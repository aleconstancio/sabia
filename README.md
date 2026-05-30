# SpaceEye

> Satellite imagery search, visualization, and processing for Brazil's Earth observation satellite fleet.

SpaceEye lets you draw a polygon on a map, search for overlapping satellite images from INPE's catalog (CBERS-4A, Amazonia-1, and more), and generate remote sensing products — NDVI, True Color, NDWI — overlaid directly on the map.

## Architecture

```
┌──────────────────────────────────────────────────┐
│                  SvelteKit SPA                    │
│  Leaflet Map  ·  Search Menu  ·  Image Gallery   │
│  Processing Viewer  ·  Progress Overlay          │
└────────────────────┬─────────────────────────────┘
                     │ REST + WebSocket
┌────────────────────▼─────────────────────────────┐
│                  FastAPI Backend                  │
│  /api/images/search  ·  /api/process  ·  /api/*  │
│  Pydantic validation  ·  CORS  ·  OpenAPI docs   │
└────────┬───────────────────────┬──────────────────┘
         │                       │
    ┌────▼────┐           ┌──────▼────────────┐
    │ PostGIS │           │   Celery Workers  │
    │  GiST   │           │ Download · Crop    │
    │ spatial │           │ NDVI · TCI · NDWI │
    │ queries │           │ Compress to PNG   │
    └─────────┘           └───────────────────┘
```

Key design decisions:
- **Direct Leaflet** — No Folium, no iframe, no `postMessage`. The map runs natively in the SPA.
- **PostGIS spatial queries** — Image footprints are stored as `GEOMETRY(POLYGON, 4326)` with a GiST index, replacing the old full-table Python scan.
- **Async background processing** — Band downloads and raster generation run in Celery workers, polled via REST or WebSocket. HTTP handlers stay fast.
- **STAC collection abstraction** — Each satellite is a `Collection` implementation (CBERS-4A, Amazonia-1, etc.) with its own band mapping and product capabilities.
- **Product registry** — NDVI, TCI, NDWI are pluggable `RasterProduct` classes. Adding a new product is one file.

## Quick Start (Docker)

```bash
cp .env.example .env
# Edit .env to add your INPE registered email

docker compose up -d
# Frontend:  http://localhost
# API:       http://localhost:8000
# API docs:  http://localhost:8000/docs
```

Then populate the database:

```bash
docker compose exec backend python pipeline/ingest.py --collection cbers4a
```

This is a one-time bulk import (~tens of thousands of images, takes a few minutes). After that, run it daily via cron to pick up new catalog items.

## Development Setup

### Backend

```bash
# Python 3.12+ with uv recommended
uv venv
source .venv/bin/activate
uv pip install -e .

# Ensure PostGIS is running
docker compose up -d postgres redis

# Start FastAPI
uvicorn backend.main:app --reload --port 8000

# Start Celery worker (separate terminal)
celery -A backend.tasks.celery_app worker --loglevel=info --concurrency=4
```

### Frontend

```bash
cd apps/spaceeye-web
bun install      # or npm install
bun dev          # Vite dev server on :5173
```

### Database

```bash
# Apply initial schema
psql -h localhost -U postgres -d spaceeye -f sql/001_init.sql
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.12+, FastAPI, SQLAlchemy (async), Celery, Redis |
| Database | PostgreSQL 16 + PostGIS |
| Frontend | Svelte 5, SvelteKit, Tailwind CSS v4, Leaflet |
| Processing | Rasterio, NumPy, Matplotlib, PyProj, aiohttp |
| Infrastructure | Docker, docker-compose, NGINX |

## Satellite Collections

| Collection | Status | Products |
|-----------|--------|----------|
| CBERS-4A (WPM) | ✅ Active | NDVI, TCI |
| Amazonia-1 (WFC) | 🔜 Planned | TCI, NDVI |
| Landsat 8/9 | 🔜 Planned | NDVI, TCI |
| Sentinel-2 | 🔜 Planned | NDVI, TCI, NDWI |

## API Overview

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |
| `/api/collections` | GET | List supported satellite collections |
| `/api/images/search` | POST | Search images by polygon intersection |
| `/api/images/{id}` | GET | Get image metadata |
| `/api/images/timeline` | POST | List images chronologically for a polygon |
| `/api/process` | POST | Submit async processing task |
| `/api/process/batch` | POST | Process multiple images for time-series |
| `/api/tasks/{id}` | GET | Poll task status + result |
| `/api/tasks/{id}/ws` | WS | Stream task progress |
| `/api/difference` | POST | Compute NDVI difference (change detection) |
| `/api/download/{id}` | GET | Download processed raster (PNG) |
| `/api/overlay/{filename}` | GET | Serve processed overlay PNG |
| `/api/export/pdf` | POST | Generate PDF analysis report |
| `/api/weather/{lat}/{lon}` | GET | Current weather + 7-day forecast |
| `/api/soil/{lat}/{lon}` | GET | Soil properties (pH, texture, CEC) |
| `/api/landcover/{lat}/{lon}` | GET | ESA WorldCover land use classes |
| `/api/geocode` | GET | Nominatim geocoding proxy |
| `/api/ibge/uf` | GET | List Brazilian states |
| `/api/ibge/cidades/{uf}` | GET | List cities in a state |

Full API documentation is available at `/docs` (Swagger UI) when the backend is running.

## License

MIT
