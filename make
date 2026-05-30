#!/usr/bin/env bash
# Convenience entrypoint: maps `./make dev` to `./scripts/make.sh dev`.
# Use this if `make` isn't on your system PATH.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec bash "$SCRIPT_DIR/scripts/make.sh" "$@"
