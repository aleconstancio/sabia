# Development Guide

## Prerequisites

- Python 3.12+ with [uv](https://docs.astral.sh/uv/)
- Node.js 20+ with npm
- Docker + docker-compose

## Quick Start

```bash
# 1. Bootstrap (installs all deps, creates .env)
make setup

# 2. Edit .env with your INPE registered email
#    (register at http://queimadas.dgi.inpe.br/catalogo/explore)

# 3. Apply database migration (first time only)
psql -h localhost -U postgres -d spaceeye -f sql/001_init.sql

# 4. Start everything in one terminal
make dev
```

`make dev` starts PostGIS, Redis, the FastAPI backend, Celery worker, and Vite dev server in a single terminal. Press Ctrl+C to stop all services.

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make setup` | Full bootstrap (deps + .env) |
| `make dev` | Start all services (single terminal) |
| `make dev-db` | Start PostGIS + Redis |
| `make dev-backend` | FastAPI with hot reload |
| `make dev-worker` | Celery worker |
| `make dev-frontend` | Vite dev server |
| `make test` | Run all tests |
| `make test-backend` | Run Python tests |
| `make test-frontend` | Run frontend tests |
| `make format` | Format Python with ruff |
| `make lint` | Svelte type-check |
| `make clean` | Remove build artifacts |

## Python Package Management

This project uses `uv` for dependency management:

```bash
uv sync --dev          # Install all deps (including dev)
uv add some-package    # Add a new dependency
uv run python ...      # Run with correct venv
uv run pytest ...      # Run tests
```

The `uv.lock` file is committed for reproducible builds.

## Running Tests

```bash
# Backend (pytest)
make test-backend

# Frontend (vitest)
make test-frontend

# Both
make test
```

## Project Structure

```
apps/spaceeye-web/       # SvelteKit SPA
├── src/lib/
│   ├── api/             # Typed API client
│   ├── components/      # SpaceEye components
│   ├── stores/          # Svelte 5 runes stores
│   └── ui/              # Vendored design system
├── src/routes/
│   └── +page.svelte     # Main map page

backend/                 # FastAPI + Celery
├── api/                 # Route handlers
├── domain/              # Business logic
├── services/            # Download, process, compress
├── repositories/        # PostGIS queries
├── models/              # Pydantic + SQLAlchemy
├── tasks/               # Celery task defs
├── config.py            # Settings
└── main.py              # FastAPI app

pipeline/                # Data ingestion
├── ingest.py            # STAC → PostGIS
└── cleanup.py           # TTL cache cleanup

sql/                     # Database migrations
docs/                    # Documentation
scripts/                 # Bootstrap helpers
```

## Code Style

### Python
- Format with `ruff`: `make format`
- Python 3.12+ with type hints
- Async for I/O, sync for CPU-bound math
- Import order: stdlib → third-party → local

### TypeScript / Svelte
- Svelte 5 runes: `$state`, `$derived`, `$effect`, `$props`, `$bindable`
- No `export let` — use `$props()` instead
- TypeScript strict mode
- Tailwind CSS v4 utilities

## Adding a New Satellite Collection

1. Implement `Collection` in `backend/domain/catalog.py`
2. Add STAC URL + parsing in `pipeline/ingest.py`
3. Register in `_COLLECTIONS` dict
4. Test with `make test-backend`

## Adding a New Spectral Product

1. Implement `RasterProduct` in `backend/domain/products.py`
2. Register in the `_PRODUCTS` dict
3. Update `schemas.py` product regex
4. Add to collection's `available_products`
5. Update frontend product dropdown
6. Test with `make test-backend`
