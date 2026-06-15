# SpaceEye

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Svelte 5](https://img.shields.io/badge/svelte-5-ff3e00.svg)](https://svelte.dev)
[![PostGIS](https://img.shields.io/badge/postgis-3.4-336791.svg)](https://postgis.net/)

> Satellite imagery search, analysis, and ESG monitoring for Brazil's INPE catalog and global Sentinel-2/Landsat constellations.

[Quick Start](#quick-start) · [Architecture](./docs/architecture.md) · [API Reference](./docs/api.md) · [ESG Features](./docs/esg-features.md) · [Development](./docs/development.md) · [Deployment](./docs/deployment.md) · [Contributing](./docs/contributing.md)

---

## Features

### Core Capabilities

- **5 satellite collections**: CBERS-4A, Amazonia-1, Sentinel-2, Landsat 8, Landsat 9
- **11 spectral products**: NDVI, TCI, NDWI, SAVI, EVI, MSAVI2, VARI, MNDWI, CIR, NBR, NDMI
- **Interactive map**: Draw polygon → search imagery → process spectral index → view overlay on Leaflet map
- **Async processing**: Celery workers handle band download and computation; UI polls for real-time progress

### ESG Monitoring

- **Dashboard-first**: ESG scorecard, portfolio overview, and alert management as primary landing page
- **5 domain modules**: Vegetation, Water, Fire, Soil, Climate — each with dedicated KPIs, charts, and alert thresholds
- **Multi-source data fusion**: Satellite imagery + weather (Open-Meteo) + soil (ISRIC SoilGrids) + land cover (ESA WorldCover)
- **Carbon stock estimation**: Soil organic carbon + NDVI-derived biomass proxy
- **Fire risk scoring**: NBR trend + weather factors (temperature, humidity, precipitation)
- **Alert system**: Configurable thresholds for vegetation loss, water body change, carbon decline, weather extremes

### Analysis Tools

- **Time-series charts**: Interactive LayerCake-powered NDVI/NDWI/NBR timelines with anomaly markers
- **Change detection**: NDVI_B - NDVI_A difference overlays with diverging colormap
- **Side-by-side comparison**: Swipe and split-view image comparison
- **Timelapse animation**: Animated satellite imagery with configurable speed
- **Zonal statistics**: Soil composition, land cover percentages, weather summaries
- **Export**: Enhanced PDF reports, CSV data export, JSON full-data packages, GeoTIFF download

---

## Quick Start

### Docker (Recommended — 2 commands)

**Prerequisites**: Docker 24+ · docker compose v2 · [INPE registered email](http://queimadas.dgi.inpe.br/catalogo/explore)

```bash
git clone https://github.com/spaceeye/spaceeye && cd spaceeye
cp .env.example .env   # Set EMAIL_INPE in .env
docker compose up -d --build
docker compose --profile setup run --rm seed
```

Open **http://localhost** — you're ready to analyze satellite imagery.

### Local Development

**Prerequisites**: `uv` · `node` 20+ · PostgreSQL 16+PostGIS · Redis 7

```bash
git clone https://github.com/spaceeye/spaceeye && cd spaceeye
just setup     # Installs deps, creates .env
just dev       # Starts Postgres, Redis, backend, worker, frontend
```

Open **http://localhost:5173**. Run `python pipeline/ingest.py --collection cbers4a` to populate the catalog.

### Manual Install

See [docs/deployment.md](./docs/deployment.md) for step-by-step manual setup including environment variables, database configuration, and production deployment.

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    SpaceEye Architecture                  │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────────┐     ┌──────────────┐                 │
│  │   Frontend    │────▶│   Backend    │                 │
│  │   SvelteKit   │     │   FastAPI    │                 │
│  │   + Leaflet   │     │   + Celery   │                 │
│  └──────────────┘     └──────┬───────┘                 │
│                              │                          │
│                    ┌─────────┼─────────┐               │
│                    │         │         │               │
│               ┌────▼───┐ ┌──▼───┐ ┌──▼────┐          │
│               │PostGIS │ │Redis │ │External│          │
│               │  DB    │ │      │ │ APIs   │          │
│               └────────┘ └──────┘ └───────┘          │
│                                                         │
│  External APIs: Open-Meteo (weather), ISRIC (soil),     │
│                 ESA WorldCover (land cover), INPE (STAC) │
└─────────────────────────────────────────────────────────┘
```

**Key architectural decisions:**

- **All geospatial processing happens server-side** — the browser only displays results
- **All map interaction happens client-side** — no server-rendered maps
- **PostGIS for spatial queries** — GiST index gives ~2ms response regardless of catalog size
- **Celery for async processing** — downloading 4 spectral bands (30-120s) doesn't block the API
- **Dashboard-first navigation** — ESG monitoring is the primary experience, map is for deep analysis

For detailed architecture, see [docs/architecture.md](./docs/architecture.md).

---

## Satellite Collections

| Collection | Resolution | Coverage | Available Products |
|-----------|-----------|----------|-------------------|
| CBERS-4A (WPM) | 8m PAN / 4m MS | Brazil | NDVI, TCI, SAVI, EVI, MSAVI2, VARI |
| Amazonia-1 (WFC) | 64m | Brazil | TCI, NDVI |
| Sentinel-2 (L2A) | 10m | Global | NDVI, TCI, NDWI, SAVI, EVI, MSAVI2, VARI, MNDWI, CIR |
| Landsat 8 (C2 L2) | 30m (15m PAN) | Global | All 11 products |
| Landsat 9 (C2 L2) | 30m (15m PAN) | Global | All 11 products |

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Frontend** | SvelteKit 2, Svelte 5 (runes), Tailwind CSS v4, Leaflet, LayerCake |
| **Backend** | Python 3.12+, FastAPI, SQLAlchemy (async), Pydantic v2 |
| **Task Queue** | Celery + Redis |
| **Database** | PostgreSQL 16 + PostGIS 3.4 |
| **Processing** | Rasterio, NumPy, scikit-image, aiohttp |
| **External Data** | Open-Meteo (weather), ISRIC SoilGrids (soil), ESA WorldCover (land cover) |
| **Infrastructure** | Docker, docker compose, NGINX, Alembic (migrations) |
| **Package Mgmt** | uv (Python), bun (Node.js) |

---

## Project Structure

```
spaceeye/
├── apps/spaceeye-web/           # SvelteKit SPA
│   └── src/
│       ├── lib/
│       │   ├── api/             # API client & processing logic
│       │   ├── charts/          # LayerCake chart components
│       │   ├── components/      # Feature components
│       │   │   ├── alerts/      # Alert notification system
│       │   │   ├── dashboard/   # Dashboard cards & grid
│       │   │   ├── modules/     # ESG module components
│       │   │   ├── sidebar/     # Map sidebar panels
│       │   │   └── ui/          # shadcn-svelte components
│       │   ├── helpers/         # Download, polling, map helpers
│       │   ├── stores/          # Svelte 5 rune stores
│       │   └── utils/           # Logger, utilities
│       └── routes/              # SvelteKit pages
│           ├── dashboard/       # ESG dashboard (primary)
│           ├── map/             # Map analysis view
│           └── modules/         # Domain-specific modules
│
├── backend/                     # FastAPI + Celery
│   ├── api/                     # Route handlers (domain-split)
│   │   ├── router.py            # Main router assembly
│   │   ├── images.py            # Image catalog endpoints
│   │   ├── processing.py        # Processing endpoints
│   │   ├── downloads.py         # File download endpoints
│   │   ├── geocoding.py         # Geocoding endpoints
│   │   ├── reports.py           # PDF export endpoints
│   │   ├── weather.py           # Weather endpoint
│   │   ├── soil.py              # Soil endpoints
│   │   ├── landcover.py         # Land cover endpoints
│   │   ├── esg.py               # Carbon stock, fire risk, ESG export
│   │   ├── tasks_api.py         # Task status & WebSocket
│   │   ├── analyses.py          # Analysis CRUD
│   │   ├── profiles.py          # Region profile CRUD
│   │   ├── health.py            # Health checks
│   │   └── deps.py              # Dependency injection
│   ├── domain/                  # Business logic
│   │   ├── catalog.py           # STAC collection abstraction
│   │   └── products.py          # Spectral product registry
│   ├── services/                # Infrastructure services
│   │   ├── downloader.py        # Async band downloader
│   │   ├── compressor.py        # GeoTIFF → PNG conversion
│   │   ├── carbon_stock.py      # Carbon stock estimation
│   │   ├── fire_risk.py         # Fire risk assessment
│   │   ├── esg_export.py        # ESG CSV/JSON export
│   │   ├── landcover_zonal.py   # Landcover zonal statistics
│   │   └── data_fusion.py       # Multi-source data fusion
│   ├── repositories/            # Database access layer
│   │   └── images.py            # PostGIS spatial queries
│   ├── models/                  # Data models
│   │   ├── database.py          # SQLAlchemy async setup
│   │   └── schemas.py           # Pydantic request/response schemas
│   ├── tasks/                   # Celery task definitions
│   │   ├── celery_app.py
│   │   └── processing.py
│   ├── utils/                   # Shared utilities
│   ├── config.py                # Typed settings (pydantic-settings)
│   └── main.py                  # FastAPI app with lifespan
```

---

## Documentation

| Document | Description |
|----------|-------------|
| [Architecture](./docs/architecture.md) | System design, data flow, directory structure, key abstractions |
| [API Reference](./docs/api.md) | All 30+ endpoints with request/response examples |
| [ESG Features](./docs/esg-features.md) | ESG modules, monitoring, alerts, reporting |
| [Development](./docs/development.md) | Local setup, testing, code style, contribution workflow |
| [Deployment](./docs/deployment.md) | Docker, manual install, environment variables, production |
| [Contributing](./docs/contributing.md) | How to contribute, PR process, code standards |

---

## Development

```bash
just test          # Run all tests
just test-backend  # Backend only (pytest)
just test-frontend # Frontend only (vitest)
just format        # Format Python (ruff)
just lint          # Type-check frontend (svelte-check)
```

See [docs/development.md](./docs/development.md) for full setup and workflow.

---

## API

Interactive Swagger documentation is available at `http://localhost:8000/docs` when the backend is running.

See [docs/api.md](./docs/api.md) for the full endpoint reference.

---

## License

[MIT](LICENSE)
