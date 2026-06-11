# Development Guide

> Setting up, running, and contributing to SpaceEye locally.

## Prerequisites

- Python 3.12+ with [uv](https://docs.astral.sh/uv/)
- Node.js 20+ with npm
- Docker + docker-compose
- PostgreSQL 16+PostGIS (or use Docker)
- Redis 7+ (or use Docker)

## Quick Start

```bash
# 1. Clone and bootstrap
git clone https://github.com/your-org/spaceeye && cd spaceeye
cp .env.example .env
./make setup

# 2. Configure
# Edit .env — set EMAIL_INPE (required for satellite data downloads)

# 3. Start everything
./make dev
```

**Services started by `make dev`:**

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | SvelteKit dev server |
| Backend | http://localhost:8000 | FastAPI with hot reload |
| API Docs | http://localhost:8000/docs | Swagger UI |
| PostGIS | localhost:5432 | PostgreSQL + PostGIS |
| Redis | localhost:6379 | Task queue broker |

## Makefile Targets

| Target | Description |
|--------|-------------|
| `make setup` | Full bootstrap (deps + .env + DB) |
| `make dev` | Start all services (single terminal) |
| `make dev-db` | Start PostGIS + Redis only |
| `make dev-backend` | FastAPI with hot reload |
| `make dev-worker` | Celery worker |
| `make dev-frontend` | Vite dev server |
| `make test` | Run all tests |
| `make test-backend` | Python tests (pytest) |
| `make test-frontend` | Frontend tests (vitest) |
| `make format` | Format Python (ruff) |
| `make lint` | Type-check frontend (svelte-check) |
| `make migrate` | Run Alembic migrations |
| `make clean` | Remove build artifacts |

If `make` is not installed, use `./scripts/make.sh` as a drop-in replacement.

## Project Structure

```
spaceeye/
├── apps/spaceeye-web/       # SvelteKit SPA
│   └── src/
│       ├── lib/              # Reusable modules
│       │   ├── api/          # API client & processing
│       │   ├── charts/       # LayerCake chart components
│       │   ├── components/   # Feature components
│       │   ├── stores/       # Svelte 5 rune stores
│       │   ├── ui/           # Design system
│       │   └── utils/        # Shared utilities
│       └── routes/           # SvelteKit pages
│           ├── dashboard/    # ESG dashboard
│           ├── map/          # Map analysis
│           └── modules/      # ESG modules
│
├── backend/                 # FastAPI + Celery
│   ├── api/                 # Route handlers (domain-split)
│   ├── domain/              # Business logic
│   ├── services/            # Infrastructure services
│   ├── repositories/        # Database access
│   ├── models/              # Data models
│   ├── tasks/               # Celery tasks
│   ├── config.py            # Settings
│   └── main.py              # FastAPI app
│
├── alembic/                 # Database migrations
├── pipeline/                # Data ingestion
├── sql/                     # SQL schema
├── docs/                    # Documentation
└── scripts/                 # Helper scripts
```

## Python Package Management

```bash
# Install dependencies
uv sync --dev

# Add a dependency
uv add some-package

# Add dev dependency
uv add --dev some-package

# Run with correct venv
uv run python ...
uv run pytest ...
uv run ruff format .
```

The `uv.lock` file is committed for reproducible builds.

## Frontend Package Management

```bash
cd apps/spaceeye-web

# Install dependencies
npm install

# Add a dependency
npm install some-package

# Add dev dependency
npm install -D some-package
```

## Running Tests

```bash
# All tests
make test

# Backend only
make test-backend
# or
uv run pytest backend/tests/ -v

# Frontend only
make test-frontend
# or
cd apps/spaceeye-web && npm test

# With coverage
uv run pytest backend/tests/ --cov=backend --cov-report=term-missing
```

## Database Migrations

SpaceEye uses [Alembic](https://alembic.sqlalchemy.org/) for database migrations.

```bash
# Run all pending migrations
make migrate
# or
./scripts/migrate.sh

# Create a new migration
uv run alembic revision --autogenerate -m "description"

# Rollback one migration
uv run alembic downgrade -1

# Check current version
uv run alembic current
```

### Initial Setup

For fresh databases, migrations run automatically during `make setup`. For existing databases:

```bash
uv run alembic upgrade head
```

## Code Style

### Python

- **Formatter**: `ruff format` (run via `make format`)
- **Linter**: `ruff check`
- **Type hints**: Required for all function signatures
- **Async**: Use `async/await` for I/O, sync for CPU-bound math
- **Import order**: stdlib → third-party → local

```python
# Good
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db
from backend.repositories.images import find_images_by_polygon

router = APIRouter()

@router.post("/images/search")
async def search_images(
    req: PolygonRequest,
    db: AsyncSession = Depends(get_db),
):
    images, total = await find_images_by_polygon(db, req.coordinates)
    return {"images": images, "total": total}
```

### TypeScript / Svelte

- **Svelte 5 runes**: `$state`, `$derived`, `$effect`, `$props`
- **No `export let`**: Use `$props()` instead
- **TypeScript**: Strict mode
- **Tailwind CSS v4**: Utility classes, avoid inline styles

```svelte
<!-- Good -->
<script lang="ts">
  import { Sparkline } from '$lib/charts';

  let { data, color = '#10b981' }: { data: number[]; color?: string } = $props();
  let trend = $derived(data.length > 1 ? data[data.length - 1] - data[0] : 0);
</script>

<div class="flex items-center gap-2">
  <Sparkline {data} {color} />
  <span class="text-xs" class:text-green-500={trend > 0} class:text-red-500={trend < 0}>
    {trend > 0 ? '+' : ''}{(trend * 100).toFixed(1)}%
  </span>
</div>
```

## Adding a New Satellite Collection

1. Implement `Collection` in `backend/domain/catalog.py`
2. Add STAC URL + parsing in `pipeline/ingest.py`
3. Register in `_COLLECTIONS` dict
4. Add to frontend collection selector
5. Test: `make test-backend`

## Adding a New Spectral Product

1. Implement `RasterProduct` in `backend/domain/products.py`
2. Register in `_PRODUCTS` dict
3. Update `schemas.py` product enum
4. Add to collection's `available_products`
5. Add to frontend product dropdown in `lib/constants.ts`
6. Test: `make test-backend`

## Adding a New ESG Module

1. Create backend endpoint in `backend/api/`
2. Add to `router.py` includes
3. Create module page in `src/routes/modules/<name>/+page.svelte`
4. Create module sidebar in `src/lib/components/modules/`
5. Add navigation link in `Header.svelte`
6. Test both frontend and backend

## IDE Setup

### VS Code

Recommended extensions:
- `svelte.svelte-vscode` — Svelte language support
- `charliermarsh.ruff` — Python formatting/linting
- `ms-python.python` — Python language server
- `bradlc.vscode-tailwindcss` — Tailwind CSS IntelliSense

### Settings

```json
{
  "editor.formatOnSave": true,
  "editor.defaultFormatter": "charliermarsh.ruff",
  "[svelte]": {
    "editor.defaultFormatter": "svelte.svelte-vscode"
  },
  "python.analysis.typeCheckingMode": "strict"
}
```

## Debugging

### Backend

```bash
# Run with debug logging
uv run uvicorn backend.main:app --reload --log-level debug

# Attach debugger
# Use VS Code Python debugger with "FastAPI" configuration
```

### Frontend

```bash
# Run with debug
cd apps/spaceeye-web
npm run dev -- --inspect

# Chrome DevTools
# Open chrome://inspect and find the Node.js process
```

### Database

```bash
# Connect directly
psql postgresql://postgres:postgres@localhost:5432/spaceeye

# Check spatial indexes
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'images';
```

## Common Issues

### "No module named 'backend'"

Run from the project root, not from inside `backend/`:
```bash
uv run python -c "from backend.main import app; print('OK')"
```

### "PostGIS extension not found"

Ensure PostGIS is installed:
```bash
docker compose exec postgres psql -U postgres -d spaceeye -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

### "Celery worker not processing"

Check Redis connection and worker logs:
```bash
docker compose logs worker
```

### Frontend build fails

Clear node_modules and reinstall:
```bash
cd apps/spaceeye-web
rm -rf node_modules .svelte-kit
npm install
npm run build
```
