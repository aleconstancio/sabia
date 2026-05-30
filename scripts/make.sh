#!/usr/bin/env bash
# Wrapper: finds `make` anywhere (Nix store, PATH, etc.) and runs it.
# Defaults to `dev` when no target is given.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Find make in Nix store or PATH
MAKE=""
for candidate in "$(command -v make 2>/dev/null)" /nix/store/*-gnumake-*/bin/make /nix/store/*make*/bin/make; do
  if [ -x "$candidate" ]; then
    MAKE="$candidate"
    break
  fi
done

if [ -z "$MAKE" ]; then
  echo "ERROR: 'make' not found. Install it with your package manager or:"
  echo "  nix-shell -p gnumake"
  echo "  brew install make"
  echo "  apt install make"
  exit 1
fi

# Default to 'dev' when no target specified
if [ $# -eq 0 ]; then
  echo "→ No target given. Defaulting to 'dev'. Run '$0 help' for all targets."
  exec "$MAKE" -C "$PROJECT_ROOT" dev
fi

exec "$MAKE" -C "$PROJECT_ROOT" "$@"
