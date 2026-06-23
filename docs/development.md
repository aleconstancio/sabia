# Development Guide

> Setting up, running, and contributing to Sabiá locally.

## Prerequisites

- Python 3.12+ with [uv](https://docs.astral.sh/uv/)
- Node.js 20+ with [bun](https://bun.sh/)
- Docker + docker compose
- PostgreSQL 16+PostGIS (or use Docker)
- Redis 7+ (or use Docker)

## Quick Start

```bash
# 1. Clone and bootstrap
git clone https://github.com/oficina-de-dedalo/sabia && cd sabia
cp .env.example .env
just setup

# 2. Configure
# Edit .env — set EMAIL_INPE (required for satellite data downloads)

# 3. Start everything
just dev
```

**Services started by `just dev`:**

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | SvelteKit dev server |
| Backend | http://localhost:8000 | FastAPI with hot reload |
| API Docs | http://localhost:8000/docs | Swagger UI |
| PostGIS | localhost:5432 | PostgreSQL + PostGIS |
| Redis | localhost:6379 | Task queue broker |

## Justfile Targets

| Target | Description |
|--------|-------------|
| `just setup` | Full bootstrap (deps + .env + DB) |
| `just dev` | Start all services (single terminal) |
| `just dev-db` | Start PostGIS + Redis only |
| `just dev-backend` | FastAPI with hot reload |
| `just dev-worker` | Celery worker |
| `just dev-frontend` | Vite dev server |
| `just test` | Run all tests |
| `just test-backend` | Python tests (pytest) |
| `just test-frontend` | Frontend tests (vitest) |
| `just format` | Format Python (ruff) |
| `just lint` | Type-check frontend (svelte-check) |
| `just migrate` | Run Alembic migrations |
| `just clean` | Remove build artifacts |

## Project Structure

```
sabia/
├── apps/sabia-web/          # SvelteKit SPA
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
cd apps/sabia-web

# Install dependencies
bun install

# Add a dependency
bun add some-package

# Add dev dependency
bun add -D some-package
```

## Running Tests

```bash
# All tests
just test

# Backend only
just test-backend
# or
uv run pytest backend/tests/ -v

# Frontend only
just test-frontend
# or
cd apps/sabia-web && bun run test

# With coverage
uv run pytest backend/tests/ --cov=backend --cov-report=term-missing
```

## Database Migrations

Sabiá uses [Alembic](https://alembic.sqlalchemy.org/) for database migrations.

```bash
# Run all pending migrations
just migrate

# Create a new migration
uv run alembic revision --autogenerate -m "description"

# Rollback one migration
uv run alembic downgrade -1

# Check current version
uv run alembic current
```

### Initial Setup

For fresh databases, migrations run automatically during `just setup`. For existing databases:

```bash
uv run alembic upgrade head
```

## Code Style

### Python

- **Formatter**: `ruff format` (run via `just format`)
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
5. Test: `just test-backend`

## Adding a New Spectral Product

1. Implement `RasterProduct` in `backend/domain/products.py`
2. Register in `_PRODUCTS` dict
3. Update `schemas.py` product enum
4. Add to collection's `available_products`
5. Add to frontend product dropdown in `lib/constants.ts`
6. Test: `just test-backend`

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
cd apps/sabia-web
bun run dev --inspect

# Chrome DevTools
# Open chrome://inspect and find the Node.js process
```

### Database

```bash
# Connect directly
psql postgresql://postgres:postgres@localhost:5432/sabia

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
docker compose exec postgres psql -U postgres -d sabia -c "CREATE EXTENSION IF NOT EXISTS postgis;"
```

### "Celery worker not processing"

Check Redis connection and worker logs:
```bash
docker compose logs worker
```

### Frontend build fails

Clear node_modules and reinstall:
```bash
cd apps/sabia-web
rm -rf node_modules .svelte-kit
bun install
bun run build
```
