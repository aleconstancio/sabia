#!/usr/bin/env bash
set -euo pipefail

# Resolve project root (script lives in scripts/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$PROJECT_ROOT"

echo "━━━ SpaceEye Bootstrap ── $PROJECT_ROOT"
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
  echo "→ Using $(basename "$UV") $(basename "$(dirname "$(dirname "$UV")")" | sed 's/.*-uv-//')"
fi

# ── Find make (handles Nix/non-standard paths) ──
MAKE=""
for candidate in "$(command -v make 2>/dev/null)" /nix/store/*-gnumake-*/bin/make /nix/store/*make*/bin/make; do
  if [ -x "$candidate" ]; then
    MAKE="$candidate"
    break
  fi
done

if [ -z "$MAKE" ]; then
  echo "! 'make' not found. Use scripts/make.sh as a drop-in replacement:"
  echo "    ./scripts/make.sh dev"
  echo "    ./scripts/make.sh setup"
  echo "  Or install make via your package manager."
  echo "  (On NixOS: nix-shell -p gnumake)"
else
  echo "→ Using $(basename "$MAKE") $("$MAKE" --version 2>&1 | head -1 | grep -oP '[\d.]+' | head -1)"
fi

# ── Check other prerequisites ──
command -v node >/dev/null 2>&1 || { echo "ERROR: 'node' not found. Install Node.js 20+."; exit 1; }

# ── .env ──
if [ ! -f .env ]; then
  cp .env.example .env
  echo "→ Created .env from .env.example"
  echo "  → EDIT .env and set your INPE email (email_inpe=...)"
fi

# ── Python backend ──
if [ -n "$UV" ]; then
  echo "→ Installing Python dependencies (uv sync)..."
  "$UV" sync 2>&1 | tail -3
  echo "→ Done. Run 'uv run python ...' to use the virtualenv."
else
  echo "→ Installing Python dependencies (pip)..."
  $PIP_INSTALL -e ".[dev]" 2>&1 | tail -3
fi

# ── Frontend ──
echo "→ Installing frontend dependencies (npm)..."
cd apps/spaceeye-web
npm install --legacy-peer-deps 2>/dev/null || npm install
cd "$PROJECT_ROOT"

# ── Done ──
echo ""
echo "━━━ Bootstrap complete ━━━"
echo ""
echo "  ./make dev    # Start everything (from project root)"
echo "  Then open  http://localhost:5173"
