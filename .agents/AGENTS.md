# Sabiá Agent Instructions

> Part of the Oficina de Dédalo suite — the spatial intelligence layer.

## Project Overview

Sabiá is the spatial intelligence layer of Oficina de Dédalo — satellite imagery search, analysis, and environmental monitoring for Brazil's INPE catalog and global Sentinel-2/Landsat constellations.

The Eye of Sabiá watches over Brazilian land — protection, health, and restoration.

## Tech Stack

- **Backend:** Python 3.12+, FastAPI, SQLAlchemy (async), Celery, Redis, PostGIS
- **Frontend:** SvelteKit 2, Svelte 5 (runes), Tailwind CSS v4, Leaflet, LayerCake
- **Database:** PostgreSQL 16 + PostGIS 3.4
- **Package Management:** uv (Python), npm (Node.js)

## Suite Integration

Sabiá provides spatial intelligence to the Oficina de Dédalo suite:

- **Vico** → property/land disputes, environmental compliance evidence
- **Polaris** → agricultural workplace safety monitoring
- **Forja** → location intelligence for SMBs
- **Maze** → ESG monitoring dashboard

## Development Commands

```bash
just setup     # Install deps, create .env, setup database
just dev       # Start all services (DB + backend + worker + frontend)
just test      # Run all tests (backend + frontend)
just test-backend   # Run backend tests (pytest)
just test-frontend  # Run frontend tests (vitest)
just lint      # Run all linters (ruff + svelte-check)
just format    # Format all code (ruff format + fix)
just migrate   # Run Alembic migrations
```

## Code Style

### Python
- **Formatter:** ruff format
- **Linter:** ruff check
- **Type hints:** Required for all function signatures
- **Async:** Use async/await for I/O, sync for CPU-bound math

### TypeScript / Svelte
- **Svelte 5 runes:** Use `$state`, `$derived`, `$effect`, `$props`
- **No `export let`:** Use `$props()` instead
- **TypeScript:** Strict mode
- **Tailwind:** Utility classes, avoid inline styles

## Testing

- **Backend:** pytest with coverage (70% threshold)
- **Frontend:** vitest
- **Coverage threshold:** 70% (enforced in CI)

## Architecture

See [docs/architecture.md](./docs/architecture.md) for detailed system design.

### Key Patterns

- **Domain-split routers:** Each data source has its own router module
- **Async tasks:** Celery handles long-running processing (band downloads, image computation)
- **PostGIS spatial queries:** GiST index for ~2ms response regardless of catalog size
- **Dashboard-first navigation:** ESG monitoring is the primary experience

## Adding New Features

### New Satellite Collection
1. Implement `Collection` in `backend/domain/catalog.py`
2. Add STAC URL + parsing in `pipeline/ingest.py`
3. Register in `_COLLECTIONS` dict
4. Add to frontend collection selector

### New Spectral Product
1. Implement `RasterProduct` in `backend/domain/products.py`
2. Register in `_PRODUCTS` dict
3. Update `schemas.py` product enum
4. Add to collection's `available_products`

### New ESG Module
1. Create backend endpoint in `backend/api/`
2. Add to `router.py` includes
3. Create module page in `src/routes/modules/<name>/+page.svelte`
4. Create module sidebar in `src/lib/components/modules/`
