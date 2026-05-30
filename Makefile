UV := $(shell command -v uv 2>/dev/null || which uv 2>/dev/null || echo "")
NPM := npm

# Fallback: use pip+python if uv not available
ifeq ($(UV),)
PYTHON := python3
PIP := $(PYTHON) -m pip
RUN :=
else
PYTHON := $(shell $(UV) run -- python3 -c "import sys; print(sys.executable)" 2>/dev/null || echo ".venv/bin/python")
RUN := $(UV) run
endif

.PHONY: setup dev-db dev-backend dev-worker dev-frontend lint check test test-backend test-frontend clean format help

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

setup: ## Full bootstrap (deps + config)
	@bash scripts/bootstrap.sh

dev-db: ## Start PostGIS and Redis via Docker
	docker compose up -d postgres redis

dev-backend: ## Start FastAPI dev server with hot reload
	$(RUN) uvicorn backend.main:app --reload --port 8000

dev-worker: ## Start Celery worker
	$(RUN) celery -A backend.tasks.celery_app worker --loglevel=info --concurrency=4

dev-frontend: ## Start Vite dev server
	cd apps/spaceeye-web && $(NPM) run dev

lint: ## Run Svelte type-check
	cd apps/spaceeye-web && npx svelte-check --tsconfig ./tsconfig.json

check: lint ## Alias for lint

test: test-backend test-frontend ## Run all tests

test-backend: ## Run Python tests
	$(RUN) pytest backend/tests/ -v -x

test-frontend: ## Run frontend tests
	cd apps/spaceeye-web && $(NPM) run test -- --run

test-frontend-watch: ## Run frontend tests in watch mode
	cd apps/spaceeye-web && $(NPM) run test

format: ## Format Python code with ruff
	$(RUN) ruff format backend/ pipeline/

clean: ## Remove build artifacts
	rm -rf apps/spaceeye-web/build
	rm -rf apps/spaceeye-web/.svelte-kit
	rm -rf apps/spaceeye-web/node_modules
	rm -rf .venv
	rm -rf __pycache__ backend/__pycache__ pipeline/__pycache__
	find . -name __pycache__ -type d -exec rm -rf {} + 2>/dev/null || true
