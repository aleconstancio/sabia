#!/usr/bin/env bash
set -euo pipefail

echo "━━━ SpaceEye Bootstrap ━━━"
echo ""

# ── Check prerequisites ──
command -v uv >/dev/null 2>&1 || { echo "ERROR: 'uv' not found. Install it: curl -LsSf https://astral.sh/uv/install.sh | sh"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo "ERROR: 'docker' not found. Install Docker first."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "ERROR: 'node' not found. Install Node.js 20+."; exit 1; }

# ── .env ──
if [ ! -f .env ]; then
  cp .env.example .env
  echo "→ Created .env from .env.example"
  echo "  EDIT .env and set your INPE email (email_inpe)"
fi

# ── Python backend ──
echo "→ Installing Python dependencies (uv)..."
uv sync --dev 2>/dev/null || uv sync  # --dev may not exist in older uv

# ── Frontend ──
echo "→ Installing frontend dependencies (npm)..."
cd apps/spaceeye-web
npm install --legacy-peer-deps 2>/dev/null || npm install
cd ../..

# ── Docs ──
echo ""
echo "━━━ Bootstrap complete ━━━"
echo ""
echo "Next steps:"
echo "  1. Edit .env with your INPE registered email"
echo "  2. Start PostGIS + Redis:      make dev-db"
echo "  3. Apply DB schema:            psql -h localhost -U postgres -d spaceeye -f sql/001_init.sql"
echo "  4. Start backend:              make dev-backend"
echo "  5. Start Celery worker:        make dev-worker"
echo "  6. Start frontend:             make dev-frontend"
echo "  7. Open http://localhost:5173"
