#!/usr/bin/env bash
set -euo pipefail

echo "━━━ SpaceEye Bootstrap ━━━"
echo ""

# ── Find uv (handles Nix/non-standard paths) ──
UV=""
for candidate in "$(command -v uv 2>/dev/null)" "$(which uv 2>/dev/null)" /nix/store/*/bin/uv; do
  if [ -x "$candidate" ]; then
    UV="$candidate"
    break
  fi
done

if [ -z "$UV" ]; then
  echo "! 'uv' not found on PATH. Falling back to pip."
  echo "  (Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh)"
  PYTHON=$(command -v python3)
  if [ -z "$PYTHON" ]; then
    echo "ERROR: 'python3' not found either. Install Python 3.12+."
    exit 1
  fi
  PIP_INSTALL="$PYTHON -m pip install"
else
  echo "→ Using $UV"
  UV_SYNC="$UV sync"
fi

# ── Check other prerequisites ──
command -v docker >/dev/null 2>&1 || echo "! 'docker' not found. Install Docker first."
command -v node >/dev/null 2>&1 || { echo "ERROR: 'node' not found. Install Node.js 20+."; exit 1; }

# ── .env ──
if [ ! -f .env ]; then
  cp .env.example .env
  echo "→ Created .env from .env.example"
  echo "  → EDIT .env and set your INPE email (email_inpe=...)"
fi

# ── Python backend ──
if [ -n "$UV" ]; then
  echo "→ Installing Python dependencies (uv)..."
  $UV sync 2>&1 | tail -3
else
  echo "→ Installing Python dependencies (pip)..."
  $PIP_INSTALL -e ".[dev]" 2>&1 | tail -3
fi

# ── Frontend ──
echo "→ Installing frontend dependencies (npm)..."
cd apps/spaceeye-web
npm install --legacy-peer-deps 2>/dev/null || npm install
cd ../..

# ── Done ──
echo ""
echo "━━━ Bootstrap complete ── run: ━━━"
echo ""
echo "  make dev-db         # Start PostGIS + Redis"
echo "  make dev-backend    # Start FastAPI (port 8000)"
echo "  make dev-worker     # Start Celery worker"
echo "  make dev-frontend   # Start Vite dev server (port 5173)"
echo ""
echo "  Then open http://localhost:5173"
