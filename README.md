# SpaceEye

> Satellite imagery search, analysis, and visualization for Brazil's INPE catalog and global Sentinel-2/Landsat constellations.

[Quick Start](#quick-start) · [Architecture](./docs/architecture.md) · [API Docs](./docs/api.md) · [Development](./docs/development.md)

## Features

- **5 satellite collections**: CBERS-4A, Amazonia-1, Sentinel-2, Landsat 8, Landsat 9
- **11 spectral products**: NDVI, TCI, NDWI, SAVI, EVI, MSAVI2, VARI, MNDWI, CIR, NBR, NDMI
- **Interactive map**: Draw polygon → search imagery → process NDVI → view overlay — all in browser
- **Analytics**: Zonal statistics, time-series charts, change detection, land cover, soil, weather
- **Advanced tools**: Side-by-side comparison, swipe overlay, timelapse animation, PDF reports, GeoTIFF download
- **Async processing**: Celery workers handle band download + computation; UI polls for progress

## Quick Start

Prerequisites: `uv` · `node` 20+ · PostgreSQL 16 (with PostGIS) · Redis 7

```bash
# One-command setup (creates .env, installs all deps)
./make setup

# Start everything (Postgres + backend + worker + frontend)
./make dev
```

`./make dev` starts local Postgres, Redis, the FastAPI backend, Celery worker, and Vite dev server in a single terminal. Press Ctrl+C to stop all services.

> **No `make` on PATH?** Use `./make` or `./scripts/make.sh` as drop-in replacements — they find GNU Make anywhere (Nix store, Homebrew, system packages).

Once running, open http://localhost:5173.

## Satellite Collections

| Collection | Resolution | Coverage | Products |
|-----------|-----------|----------|----------|
| CBERS-4A (WPM) | 8m PAN / 4m MS | Brazil | NDVI, TCI, SAVI, EVI... |
| Amazonia-1 (WFC) | 64m | Brazil | TCI, NDVI... |
| Sentinel-2 (L2A) | 10m | Global | All 11 products |
| Landsat 8 (C2 L2) | 30m (15m PAN) | Global | All 11 + SWIR-based |
| Landsat 9 (C2 L2) | 30m (15m PAN) | Global | All 11 + SWIR-based |

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12+, FastAPI, SQLAlchemy (async), Celery, Redis |
| Database | PostgreSQL 16 + PostGIS |
| Frontend | Svelte 5, SvelteKit, Tailwind CSS v4, Leaflet |
| Processing | Rasterio, NumPy, Matplotlib, aiohttp, scikit-image |
| Infrastructure | Docker, docker-compose, NGINX, UV |

## Development

See [docs/development.md](./docs/development.md) for full setup.

## API

See [docs/api.md](./docs/api.md) for endpoint reference (27 endpoints).

## License

MIT
