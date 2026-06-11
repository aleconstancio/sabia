UV := $(shell command -v uv 2>/dev/null || which uv 2>/dev/null || echo "")
NPM := npm

# Find libstdc++.so.6 for greenlet (needed on NixOS and some systems)
LIBSTDCXX_PATH := $(shell find /nix/store -maxdepth 4 -path '*/gcc-*-lib/lib/libstdc++.so.6' 2>/dev/null | head -1)
ifneq ($(LIBSTDCXX_PATH),)
LIBSTDCXX_DIR := $(dir $(LIBSTDCXX_PATH))
# Export LD_LIBRARY_PATH with the libstdc++ directory prepended
export LD_LIBRARY_PATH
endif
LD_LIBRARY_PATH := $(LIBSTDCXX_DIR)$(LD_LIBRARY_PATH)

# Fallback: use pip+python if uv not available
ifeq ($(UV),)
PYTHON := python3
PIP := $(PYTHON) -m pip
RUN :=
else
PYTHON := $(shell $(UV) run -- python3 -c "import sys; print(sys.executable)" 2>/dev/null || echo ".venv/bin/python")
RUN := $(UV) run
endif

.PHONY: setup dev dev-db dev-backend dev-worker dev-frontend lint check test test-backend test-frontend clean format help migrate docker-build docker-up docker-down docker-logs

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Full bootstrap (deps + config)
	@bash scripts/bootstrap.sh

dev: ## Start all dev services in one terminal
	@echo "━━━ Starting SpaceEye dev environment ━━━"
	@echo ""
	@trap 'echo ""; echo "→ Stopping..."; kill $$BACKEND_PID $$WORKER_PID 2>/dev/null; pkill -f "postgres.*5432" 2>/dev/null; pkill -f "redis.*6379" 2>/dev/null; exit 0' INT TERM; \
	bash scripts/start-db.sh; \
	echo "→ Databases ready"; \
	$(RUN) uvicorn backend.main:app --reload --port 8000 &
	BACKEND_PID=$$!; \
	sleep 2; \
	$(RUN) celery -A backend.tasks.celery_app worker --loglevel=info --concurrency=4 &
	WORKER_PID=$$!; \
	sleep 1; \
	echo "→ Backend (PID $$BACKEND_PID) + Worker (PID $$WORKER_PID) started"; \
	echo "→ Starting Vite..."; \
	echo ""; \
	cd apps/spaceeye-web && $(NPM) run dev; \
	STATUS=$$?; \
	echo "→ Stopping..."; \
	kill $$BACKEND_PID $$WORKER_PID 2>/dev/null; \
	pkill -f "postgres.*5432" 2>/dev/null; \
	pkill -f "redis.*6379" 2>/dev/null; \
	exit $$STATUS

dev-db: ## Start Postgres + Redis (no Docker needed)
	@bash scripts/start-db.sh

dev-backend: ## Start FastAPI dev server with hot reload
	$(RUN) uvicorn backend.main:app --reload --port 8000

dev-worker: ## Start Celery worker
	$(RUN) celery -A backend.tasks.celery_app worker --loglevel=info --concurrency=4

dev-frontend: ## Start Vite dev server
	cd apps/spaceeye-web && $(NPM) run dev

lint: ## Run all linters
	@echo "==> Python linting..."
	uv run ruff check .
	uv run ruff format --check .
	@echo "==> Frontend type checking..."
	cd apps/spaceeye-web && npm run check

check: lint ## Alias for lint

test: test-backend test-frontend ## Run all tests

test-backend: ## Run Python tests
	$(RUN) pytest backend/tests/ -v -x

test-frontend: ## Run frontend tests
	cd apps/spaceeye-web && $(NPM) run test -- --run

test-frontend-watch: ## Run frontend tests in watch mode
	cd apps/spaceeye-web && $(NPM) run test

format: ## Format all code
	@echo "==> Python formatting..."
	uv run ruff format .
	uv run ruff check --fix .

clean: ## Remove build artifacts
	rm -rf apps/spaceeye-web/build
	rm -rf apps/spaceeye-web/.svelte-kit
	rm -rf apps/spaceeye-web/node_modules
	rm -rf .venv
	rm -rf __pycache__ backend/__pycache__ pipeline/__pycache__
	find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true

migrate: ## Run database migrations
	uv run alembic upgrade head

docker-build: ## Build Docker images
	docker compose build

docker-up: ## Start Docker services
	docker compose up -d

docker-down: ## Stop Docker services
	docker compose down

docker-logs: ## View Docker logs
	docker compose logs -f
