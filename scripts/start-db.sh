#!/usr/bin/env bash
# Starts Postgres + Redis for local development.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

DATA_DIR="$PROJECT_ROOT/.spaceeye/data"
PGDATA="$DATA_DIR/pgdata"
mkdir -p "$DATA_DIR" "$PGDATA"

PGPORT=${PGPORT:-5432}
REDIS_PORT=${REDIS_PORT:-6379}

# ── Find binaries ──
find_bin() {
  local name="$1"
  local pattern="${2:-}"
  local path
  path=$(command -v "$name" 2>/dev/null) && echo "$path" && return 0
  if [ -n "$pattern" ]; then
    path=$(ls /nix/store/*"$pattern"/bin/"$name" 2>/dev/null | head -1) && echo "$path" && return 0
  fi
  path=$(ls /nix/store/*/bin/"$name" 2>/dev/null | head -1) && echo "$path" && return 0
  return 1
}

PG_CTL=$(find_bin pg_ctl "-postgresql")
INITDB=$(find_bin initdb "-postgresql")
PSQL=$(find_bin psql "-postgresql")
PG_ISREADY=$(find_bin pg_isready "-postgresql")
REDIS_SERVER=$(find_bin redis-server "-redis")

PG_CTL=$(find_bin pg_ctl)
INITDB=$(find_bin initdb)
PSQL=$(find_bin psql)
PG_ISREADY=$(find_bin pg_isready)
REDIS_SERVER=$(find_bin redis-server)

if [ -z "$PG_CTL" ] || [ -z "$PSQL" ]; then
  echo "ERROR: PostgreSQL not found. Set up via your system package manager or nix-shell."
  echo "  nix-shell -p postgresql_16 redis"
  exit 1
fi
if [ -z "$REDIS_SERVER" ]; then
  echo "ERROR: Redis not found. Set up via your system package manager or nix-shell."
  exit 1
fi

echo "→ PostgreSQL: $PG_CTL"
echo "→ Redis:      $REDIS_SERVER"

# ── Stop existing ──
"$PG_CTL" -D "$PGDATA" stop 2>/dev/null || true
kill "$(cat "$DATA_DIR/redis.pid" 2>/dev/null)" 2>/dev/null || true
sleep 0.5

# ── Init Postgres ──
if [ ! -f "$PGDATA/PG_VERSION" ]; then
  echo "→ Initializing database..."
  "$INITDB" -D "$PGDATA" --no-locale --encoding=UTF8 2>&1 | tail -1
fi

# ── Start Postgres (TCP on localhost) ──
echo "→ Starting PostgreSQL on localhost:$PGPORT..."
# Disable unix socket (no /run/postgresql), TCP only
"$PG_CTL" -D "$PGDATA" -l "$DATA_DIR/pg.log" start \
  -o "-p $PGPORT -h 127.0.0.1 -k /tmp" 2>&1 | tail -3

for i in $(seq 1 10); do
  "$PG_ISREADY" -q -p "$PGPORT" 2>/dev/null && break
  sleep 0.5
done

# ── Create database + postgres role + extensions ──
echo "→ Creating 'postgres' role if missing..."
"$PSQL" -p "$PGPORT" -h 127.0.0.1 -U "$USER" -d postgres -tc \
  "SELECT 1 FROM pg_roles WHERE rolname='postgres'" | grep -q 1 || \
  "$PSQL" -p "$PGPORT" -h 127.0.0.1 -U "$USER" -d postgres -c \
  "CREATE ROLE postgres LOGIN SUPERUSER;" 2>/dev/null || true

echo "→ Creating 'spaceeye' database..."
"$PSQL" -p "$PGPORT" -h 127.0.0.1 -U "$USER" -d postgres -tc \
  "SELECT 1 FROM pg_database WHERE datname='spaceeye'" | grep -q 1 || \
  "$PSQL" -p "$PGPORT" -h 127.0.0.1 -U "$USER" -d postgres -c "CREATE DATABASE spaceeye" 2>/dev/null || true

if [ -f "$PROJECT_ROOT/sql/001_init.sql" ]; then
  echo "→ Applying migration..."
  "$PSQL" -p "$PGPORT" -h 127.0.0.1 -U "$USER" -d spaceeye -f "$PROJECT_ROOT/sql/001_init.sql" 2>&1 | tail -1
fi

# ── Start Redis ──
echo "→ Starting Redis on localhost:$REDIS_PORT..."
"$REDIS_SERVER" --port "$REDIS_PORT" --pidfile "$DATA_DIR/redis.pid" \
  --daemonize yes --logfile "$DATA_DIR/redis.log" 2>&1 | tail -1

echo ""
echo "━━━ Services ready ━━━"
echo "  Postgres: localhost:$PGPORT  (db: spaceeye, user: $USER)"
echo "  Redis:    localhost:$REDIS_PORT"
