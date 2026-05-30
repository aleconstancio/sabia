#!/usr/bin/env bash
# Wrapper: finds `make` anywhere (Nix store, PATH, etc.) and runs it.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

exec "$MAKE" -C "$SCRIPT_DIR/.." "$@"
