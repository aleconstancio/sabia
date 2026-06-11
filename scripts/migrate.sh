#!/bin/bash
# Run database migrations
set -e
cd "$(dirname "$0")/.."
.venv/bin/alembic upgrade head
echo "Migrations complete."
