# Development

set dotenv-load
set shell := ["bash", "-euo", "pipefail", "-c"]

# Full project bootstrap (deps + config + db)
setup:
    @echo "==> Installing Python dependencies..."
    uv sync --dev
    @echo "==> Installing frontend dependencies..."
    cd apps/spaceeye-web && bun install --frozen-lockfile
    @echo "==> Setting up environment..."
    test -f .env || cp .env.example .env
    @echo "==> Setting up database..."
    just dev-db
    @echo ""
    @echo "━━━ Setup complete ━━━"
    @echo "  Run 'just dev' to start all services"

# Start all dev services in one terminal
dev:
    @echo "━━━ Starting SpaceEye dev environment ━━━"
    @echo ""
    @trap 'echo ""; echo "→ Stopping..."; kill $BACKEND_PID $WORKER_PID 2>/dev/null; pkill -f "postgres.*5432" 2>/dev/null; pkill -f "redis.*6379" 2>/dev/null; exit 0' INT TERM; \
    just dev-db; \
    echo "→ Databases ready"; \
    bash scripts/run-backend.sh &  BACKEND_PID=$!; \
    sleep 2; \
    bash scripts/run-worker.sh &  WORKER_PID=$!; \
    sleep 1; \
    echo "→ Backend (PID $BACKEND_PID) + Worker (PID $WORKER_PID) started"; \
    echo "→ Starting Vite..."; \
    echo ""; \
    cd apps/spaceeye-web && bun run dev &  sleep 3 && xdg-open http://localhost:5173

# Start Postgres + Redis via Docker
dev-db:
    docker-compose up -d postgres redis

# Start FastAPI dev server with hot reload
dev-backend:
    uv run uvicorn backend.main:app --reload --port 8000

# Start Celery worker
dev-worker:
    uv run celery -A backend.tasks.celery_app worker --loglevel=info --concurrency=4

# Start Vite dev server
dev-frontend:
    cd apps/spaceeye-web && bun run dev

# Code Quality

# Run all linters
lint:
    @echo "==> Python linting..."
    uv run ruff check .
    uv run ruff format --check .
    @echo "==> Frontend type checking..."
    cd apps/spaceeye-web && bun run check

# Alias for lint
check: lint

# Format all code
format:
    @echo "==> Python formatting..."
    uv run ruff format .
    uv run ruff check --fix .

# Testing

# Run all tests
test: test-backend test-frontend

# Run Python tests
test-backend:
    uv run pytest backend/tests/ -v -x

# Run frontend tests
test-frontend:
    cd apps/spaceeye-web && bun run test -- --run

# Run frontend tests in watch mode
test-frontend-watch:
    cd apps/spaceeye-web && bun run test

# Run end-to-end tests
test-e2e:
    cd apps/spaceeye-web && bunx playwright test

# Run all tests (backend + frontend + e2e)
test-all: test-backend test-frontend test-e2e

# Database

# Run database migrations
migrate:
    uv run alembic upgrade head

# Seed the database
seed:
    docker-compose exec backend python pipeline/ingest.py --collection cbers4a

# Docker

# Build Docker images
docker-build:
    docker-compose build

# Start Docker services
docker-up:
    docker-compose up -d

# Stop Docker services
docker-down:
    docker-compose down

# View Docker logs
docker-logs:
    docker-compose logs -f

# Cleanup

# Remove build artifacts
clean:
    rm -rf apps/spaceeye-web/build
    rm -rf apps/spaceeye-web/.svelte-kit
    rm -rf apps/spaceeye-web/node_modules
    rm -rf .venv
    find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
    rm -rf .spaceeye/data

# Utilities

# Check backend health endpoint
health:
    @curl -sf http://localhost:8000/api/health || echo "Backend not running"

# Show project info
info:
    @echo "SpaceEye — Satellite imagery search & ESG monitoring"
    @echo ""
    @echo "Available commands:"
    @just --list
