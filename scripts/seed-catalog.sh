#!/usr/bin/env bash
# Manual seed script for users who run `docker compose up -d` and want to
# populate the catalog afterwards. If you prefer the one-command approach,
# use `docker compose --profile setup run --rm seed` instead.
set -euo pipefail

# Resolve script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

COLLECTION="${1:-cbers4a}"
BACKEND_URL="http://localhost:8000/api/health"
MAX_WAIT=30
WAIT_INTERVAL=2

echo "Waiting for backend to be ready at $BACKEND_URL..."

elapsed=0
while [ $elapsed -lt $MAX_WAIT ]; do
    if curl -sf "$BACKEND_URL" > /dev/null 2>&1; then
        echo "Backend is ready."
        break
    fi
    sleep $WAIT_INTERVAL
    elapsed=$((elapsed + WAIT_INTERVAL))
    echo "Still waiting... ($elapsed/$MAX_WAIT seconds)"
done

if [ $elapsed -ge $MAX_WAIT ]; then
    echo "ERROR: Backend did not become ready within $MAX_WAIT seconds."
    exit 1
fi

echo "Running catalog ingestion for collection: $COLLECTION"
docker compose -f "$PROJECT_ROOT/docker-compose.yml" exec backend \
    python pipeline/ingest.py --collection "$COLLECTION"

echo "Done. Catalog seeded successfully."
