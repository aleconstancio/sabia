# Development Guide

## Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Node.js 20+ / [Bun](https://bun.sh)
- Docker + docker-compose (for PostGIS + Redis)
- Make

## Quick Start

```bash
# 1. Clone and set up
git clone https://github.com/your-org/spaceeye
cd spaceeye
cp .env.example .env

# 2. Edit .env — add your INPE registered email
#    (register at http://queimadas.dgi.inpe.br/catalogo/explore)

# 3. Start infrastructure
docker compose up -d postgres redis

# 4. Run database migration
psql -h localhost -U postgres -d spaceeye -f sql/001_init.sql

# 5. Install backend deps
uv venv
source .venv/bin/activate
uv pip install -e .

# 6. Start backend
uvicorn backend.main:app --reload --port 8000

# 7. Start Celery worker (separate terminal)
source .venv/bin/activate
celery -A backend.tasks.celery_app worker --loglevel=info --concurrency=4

# 8. Install frontend deps
cd apps/spaceeye-web
bun install

# 9. Start frontend (separate terminal)
bun run dev
```

Open `http://localhost:5173` for the app and `http://localhost:8000/docs` for API docs.

## Initial Database Population

```bash
# Full CBERS-4A catalog import (takes ~5-10 minutes)
python pipeline/ingest.py --collection cbers4a

# You can also use Docker:
docker compose exec backend python pipeline/ingest.py --collection cbers4a
```

## Makefile Targets

```bash
make dev-db         # Start PostGIS + Redis
make dev-backend    # uvicorn with hot reload
make dev-worker     # Celery worker
make dev-frontend   # Vite dev server
make lint           # Run svelte-check
make format         # Format frontend code
make test           # Run tests
make clean          # Remove build artifacts
```

## Code Style

### Python
- Python 3.12+ with type hints everywhere
- Follow PEP 8 (use `ruff` for linting)
- Import order: stdlib → third-party → local
- Async patterns: `async def` for I/O, `sync def` for CPU-bound math (inside Celery tasks)

### TypeScript / Svelte
- Svelte 5 runes only (`$state`, `$derived`, `$effect`, `$props`)
- `$bindable` for two-way binding on form components
- `createX()` composable pattern for shared state
- TypeScript strict mode
- Tailwind CSS v4 utilities, OKLCH color tokens
- No `@thoth/ui` dependency — UI components are vendored in `lib/ui/`

### Git
- Conventional commits: `feat(scope):`, `fix(scope):`, `chore:`, `docs:`
- Feature branches: `feat/my-feature`, `fix/bug-description`

## Project Structure Conventions

```
apps/spaceeye-web/src/lib/
  api/       — API client and typed endpoints
  components — SpaceEye-specific components (PascalCase.svelte)
  stores/    — Svelte 5 runes state ($state derived from user interaction)
  ui/        — Vendored design system components (do not add app logic here)

backend/
  api/       — Route handlers only (thin controllers)
  domain/    — Business logic (no infrastructure imports)
  services/  — External service integrations (download, GDAL, compression)
  repositories/ — Database access (PostGIS SQL queries)
  models/    — Pydantic schemas + SQLAlchemy setup
  tasks/     — Celery task definitions
```

## Making Changes

1. **Add a new satellite collection:**
   - Implement `Collection` in `backend/domain/catalog.py`
   - Add collection ID to ingestion script at `pipeline/ingest.py`
   - Test with `python pipeline/ingest.py --collection your_satellite`

2. **Add a new vegetation index / product:**
   - Implement `RasterProduct` in `backend/domain/products.py`
   - Register in the `_PRODUCTS` dict
   - Add the product name to the collection's `available_products`

3. **Add a new API endpoint:**
   - Define Pydantic schema in `backend/models/schemas.py`
   - Add route handler in `backend/api/router.py`
   - Document in `docs/api.md`

## Testing

```bash
# Backend (pytest — not yet configured)
pytest backend/tests/

# Frontend (vitest — not yet configured)
cd apps/spaceeye-web
bun vitest run
```

Test infrastructure is set up but no tests exist yet. Contributions welcome!
