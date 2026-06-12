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
PG_CTL=$(command -v pg_ctl)
INITDB=$(command -v initdb)
PSQL=$(command -v psql)
PG_ISREADY=$(command -v pg_isready)
REDIS_SERVER=$(command -v redis-server)

if [ -z "$PG_CTL" ] || [ -z "$PSQL" ]; then
  echo "ERROR: PostgreSQL not found. Install via your system package manager."
  exit 1
fi
if [ -z "$REDIS_SERVER" ]; then
  echo "ERROR: Redis not found. Install via your system package manager."
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
"$PG_CTL" -D "$PGDATA" -l "$DATA_DIR/pg.log" start \
  -o "-p $PGPORT -h 127.0.0.1 -k /tmp" 2>&1 | tail -3

for i in $(seq 1 10); do
  "$PG_ISREADY" -q -p "$PGPORT" 2>/dev/null && break
  sleep 0.5
done

# ── Create database + roles ──
echo "→ Creating 'postgres' role if missing..."
# Note: Passwordless superuser is intentional for local dev only
"$PSQL" -p "$PGPORT" -h 127.0.0.1 -U "$USER" -d postgres -tc \
  "SELECT 1 FROM pg_roles WHERE rolname='postgres'" | grep -q 1 || \
  "$PSQL" -p "$PGPORT" -h 127.0.0.1 -U "$USER" -d postgres -c \
  "CREATE ROLE postgres LOGIN SUPERUSER;" 2>/dev/null || true

echo "→ Creating 'spaceeye' database..."
"$PSQL" -p "$PGPORT" -h 127.0.0.1 -U "$USER" -d postgres -tc \
  "SELECT 1 FROM pg_database WHERE datname='spaceeye'" | grep -q 1 || \
  "$PSQL" -p "$PGPORT" -h 127.0.0.1 -U "$USER" -d postgres -c "CREATE DATABASE spaceeye" 2>/dev/null || true

for sql_file in "$PROJECT_ROOT"/sql/001_init.sql "$PROJECT_ROOT"/sql/003_analyses.sql "$PROJECT_ROOT"/sql/004_profiles.sql "$PROJECT_ROOT"/sql/005_triggers.sql; do
  if [ -f "$sql_file" ]; then
    echo "→ Applying $(basename "$sql_file")..."
    "$PSQL" -p "$PGPORT" -h 127.0.0.1 -U "$USER" -d spaceeye -f "$sql_file" 2>&1 | tail -1
  fi
done

# ── Start Redis ──
echo "→ Starting Redis on localhost:$REDIS_PORT..."
"$REDIS_SERVER" --port "$REDIS_PORT" --pidfile "$DATA_DIR/redis.pid" \
  --daemonize yes --logfile "$DATA_DIR/redis.log" 2>&1 | tail -1

echo ""
echo "━━━ Services ready ━━━"
echo "  Postgres: localhost:$PGPORT  (db: spaceeye, user: $USER)"
echo "  Redis:    localhost:$REDIS_PORT"
