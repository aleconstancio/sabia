# Architecture

> *This document reflects the current codebase state. Last updated: June 2026.*

## Overview

SpaceEye is a single-page application with a Python backend and SvelteKit frontend. The distinguishing architectural choices are:

1. **All geospatial processing happens server-side** — the browser only displays results
2. **All map interaction happens client-side** — no server-rendered maps
3. **Dashboard-first navigation** — ESG monitoring is the primary experience
4. **Domain-split backend** — each data source has its own router module

## Data Flow

```
1. User draws polygon on Leaflet map
           │
2. POST /api/images/search { coordinates }
           │
3. FastAPI calls PostGIS ST_Intersects
           │
4. Returns matching images (id, cloud_cover, thumbnail, acquired_at)
           │
5. User selects an image + product (NDVI/TCI/NDWI)
           │
6. POST /api/process { image_id, coordinates, product }
           │
7. Returns { task_id } immediately
           │
8. Frontend polls GET /api/tasks/{task_id} (or WebSocket)
           │
9. Celery worker:
   a. Downloads spectral band GeoTIFFs from INPE (aiohttp, 4 concurrent)
   b. Crops bands to user's polygon (rasterio.mask)
   c. Computes product (NDVI = (NIR-RED)/(NIR+RED), etc.)
   d. Compresses result to PNG with colormap + WGS84 bounds
           │
10. Frontend receives overlay URL + bounds → displays on map via L.imageOverlay
```

### ESG Data Flow

```
1. User selects a region (or loads a saved profile)
           │
2. Frontend fetches multi-source data in parallel:
   ├── GET /api/weather/{lat}/{lon}     → Open-Meteo API
   ├── GET /api/soil/zonal              → ISRIC SoilGrids
   ├── GET /api/landcover/zonal-stats   → ESA WorldCover
   ├── POST /api/carbon-stock           → SOC + NDVI proxy
   └── POST /api/fire-risk              → NBR + weather factors
           │
3. Results displayed in module sidebar with charts and KPIs
           │
4. User can set alert thresholds per region
           │
5. Export to PDF/CSV/JSON for ESG reporting
```

## Directory Structure

### Backend (`backend/`)

```
backend/
├── api/                          # Route handlers (domain-split)
│   ├── router.py                 # Core: images, process, geocode, download
│   ├── weather.py                # /weather/{lat}/{lon}
│   ├── soil.py                   # /soil/{lat}/{lon}, /soil/zonal
│   ├── landcover.py              # /landcover, /landcover/zonal, /landcover/zonal-stats
│   ├── esg.py                    # /carbon-stock, /fire-risk, /export/*
│   ├── tasks_api.py              # /tasks/{id}, /tasks/{id}/ws
│   ├── analyses.py               # CRUD for analysis records
│   ├── profiles.py               # CRUD for region profiles
│   ├── health.py                 # Health checks
│   ├── deps.py                   # Dependency injection (DB, HTTP client)
│   └── landcover_utils.py        # Shared land cover utilities
├── domain/                       # Business logic
│   ├── catalog.py                # STAC collection abstraction
│   ├── products.py               # Spectral product registry (NDVI, TCI, etc.)
│   └── processing.py             # Image processing orchestrator
├── services/                     # Infrastructure services
│   ├── downloader.py             # Async band downloader
│   ├── compressor.py             # GeoTIFF → PNG conversion
│   └── data_fusion.py            # Multi-source data fusion
├── repositories/                 # Database access
│   └── images.py                 # PostGIS spatial queries
├── models/                       # Data models
│   ├── database.py               # SQLAlchemy async setup
│   └── schemas.py                # Pydantic request/response schemas
├── tasks/                        # Celery task definitions
│   ├── celery_app.py
│   └── processing.py
├── config.py                     # Typed settings (pydantic-settings)
├── main.py                       # FastAPI app with lifespan
└── exceptions.py                 # Custom exception hierarchy
```

### Frontend (`apps/spaceeye-web/`)

```
apps/spaceeye-web/src/
├── lib/
│   ├── api/                      # API client & processing logic
│   │   ├── client.ts             # Typed API client (createApiClient)
│   │   ├── processing.ts         # Image processing, export, polling
│   │   └── types.ts              # TypeScript interfaces
│   ├── charts/                   # LayerCake chart components
│   │   ├── AreaChart.svelte      # Time-series area charts
│   │   ├── Sparkline.svelte      # Inline trend indicators
│   │   ├── BarChart.svelte       # Bar charts
│   │   └── DonutChart.svelte     # Composition breakdown
│   ├── components/               # Feature components
│   │   ├── alerts/               # Alert notification system
│   │   │   └── AlertBell.svelte  # Notification bell with unread count
│   │   ├── dashboard/            # Dashboard cards & grid
│   │   │   ├── Scorecard.svelte  # ESG metric card with sparkline
│   │   │   └── PortfolioGrid.svelte  # Region card grid
│   │   ├── modules/              # ESG module components
│   │   │   ├── ModuleSidebar.svelte   # Domain-specific sidebar
│   │   │   ├── ModuleMapPage.svelte   # Shared map page for modules
│   │   │   ├── ModuleKPI.svelte       # KPI card with sparkline
│   │   │   └── AlertThresholds.svelte # Threshold configuration
│   │   └── sidebar/              # Map sidebar panels
│   │       ├── SearchPanel.svelte
│   │       ├── ResultsPanel.svelte
│   │       ├── AnalyticsPanel.svelte
│   │       └── HistorySidebar.svelte
│   ├── config.ts                 # API_URL singleton
│   ├── constants.ts              # SPECTRAL_PRODUCTS, shared constants
│   ├── stores/                   # Svelte 5 rune stores
│   │   ├── map.svelte.ts         # Map state (polygon, results, UI flags)
│   │   ├── dashboard.svelte.ts   # Dashboard state
│   │   ├── alerts.svelte.ts      # Alert store
│   │   ├── bookmarks.svelte.ts   # LocalStorage bookmarks
│   │   ├── history.svelte.ts     # Analysis history
│   │   └── monitors.svelte.ts    # Region monitoring
│   ├── ui/                       # Design system
│   │   ├── components/           # Button, Card, Badge, Dialog, etc.
│   │   └── styles/               # Global CSS, tokens, utilities
│   └── utils/                    # Shared utilities
│       ├── download.ts           # downloadBlob(), downloadBlobPost()
│       ├── pollTask.ts           # pollTaskStatus() for Celery tasks
│       └── map-helpers.ts        # Leaflet helper functions
└── routes/                       # SvelteKit pages
    ├── +layout.svelte            # Root layout
    ├── dashboard/                # ESG dashboard (primary landing page)
    │   └── +page.svelte
    ├── map/                      # Map analysis view
    │   └── +page.svelte
    └── modules/                  # Domain-specific modules
        ├── vegetation/
        ├── water/
        ├── fire/
        ├── soil/
        └── climate/
```

### Database (`sql/`)

```
sql/
├── 001_init.sql                  # images table + PostGIS spatial index
├── 003_analyses.sql              # analyses table + FK to images
├── 004_profiles.sql              # region_profiles table
└── 005_triggers.sql              # Triggers, processing_tasks, metric_timeseries, alert_rules
```

### Infrastructure

```
alembic/                          # Database migrations (Alembic)
pipeline/                         # Data ingestion scripts
├── ingest.py                     # STAC → PostGIS
└── cleanup.py                    # TTL-based cache cleanup
scripts/                          # Helper scripts
├── migrate.sh                    # Run Alembic migrations
└── make.sh                       # Makefile fallback
```

## Key Abstractions

### Collection (domain/catalog.py)

Each satellite is a `Collection` subclass:

```python
class Collection(ABC):
    id: str
    stac_url: str
    available_bands: list[str]
    available_products: list[str]
    get_asset_url(item_assets, band) -> str | None
```

Adding a new satellite = implementing 6 methods.

### RasterProduct (domain/products.py)

Each remote sensing index is a `RasterProduct` subclass:

```python
class RasterProduct(ABC):
    name: str
    compute(bands: dict[str, np.ndarray]) -> np.ndarray
```

Adding NDVI was 8 lines. Adding NDWI was 9 lines.

### ESG Modules

Each ESG domain (Vegetation, Water, Fire, Soil, Climate) follows the same pattern:

1. **Backend endpoint** — fetches domain-specific data (weather, soil, carbon stock, etc.)
2. **Module sidebar** — displays KPIs, charts, and alert thresholds
3. **Module map page** — shared Leaflet map with domain-specific overlay
4. **Alert rules** — configurable thresholds per region

### Shared Utilities

- **`pollTaskStatus(taskId, options)`** — unified Celery task polling (replaces 5 duplicate implementations)
- **`downloadBlob(url, filename)`** — file download via blob URL (replaces 5 duplicate patterns)
- **`API_URL`** — single config constant (was duplicated 19 times)

## Design Decisions

### Why PostGIS Instead of Python Filtering?

The old code loaded every image from the `images` table, parsed its coordinates JSON, converted it to a Shapely polygon, and checked `contains_properly` in Python. For 1,000 images this is ~100ms. For 100,000 (CBERS-4A catalog) it's several seconds.

PostGIS `ST_Intersects` uses a GiST index — the R-tree index prunes non-overlapping geometries in logarithmic time. Same query: ~2ms regardless of catalog size.

### Why Async Tasks Instead of Sync?

Downloading 4 spectral bands at ~200MB each takes 30-120 seconds. In the old code, Flask's single thread was blocked for the entire duration, meaning one user could block all others.

Celery workers handle this asynchronously: the HTTP endpoint returns a task ID immediately, and the frontend polls for progress. Multiple users can process images concurrently, and the worker pool limits resource usage.

### Why Dashboard-First?

ESG analysts need portfolio visibility — seeing all monitored regions, their health scores, and active alerts at a glance. The dashboard provides this immediately. The map page becomes the "drill-down" for deep analysis of specific regions.

### Why Domain-Split Routers?

The original `router.py` was 713 lines with 25+ endpoints. Splitting by domain (weather, soil, landcover, ESG, tasks) makes each module independently maintainable, testable, and understandable. The pattern follows the existing `analyses.py` and `profiles.py` split.

## Database Schema

### Core Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `images` | Satellite image catalog | `id`, `footprint` (PostGIS), `cloud_cover`, `acquired_at`, `metadata` |
| `analyses` | Processing results | `id`, `image_id` (FK→images), `product`, `polygon`, `statistics` |
| `region_profiles` | Saved ESG regions | `id`, `name`, `polygon`, `weather_summary`, `soil_summary`, `satellite_data` |

### ESG Tables

| Table | Purpose | Key Columns |
|-------|---------|-------------|
| `processing_tasks` | Task result persistence | `task_id`, `image_id`, `product`, `status`, `result_path`, `statistics` |
| `metric_timeseries` | Historical ESG metrics | `profile_id` (FK→profiles), `metric_name`, `value`, `recorded_at` |
| `alert_rules` | User-defined thresholds | `profile_id` (FK→profiles), `metric`, `operator`, `threshold_value` |

### Key Relationships

```
images ──< analyses (1:N, FK image_id, CASCADE DELETE)
region_profiles ──< metric_timeseries (1:N, FK profile_id, CASCADE DELETE)
region_profiles ──< alert_rules (1:N, FK profile_id, CASCADE DELETE)
```

## Error Handling

### Backend

- **HTTP exceptions** — returned as `{"detail": "message"}` with appropriate status codes
- **Global exception handler** — catches unhandled exceptions, logs them, returns generic 500
- **Health check** — returns HTTP 503 when database is disconnected
- **ESG stubs** — endpoints not yet fully implemented return HTTP 501

### Frontend

- **Toast notifications** — for user-facing errors (using `svelte-sonner`)
- **Console warnings** — for non-critical failures (background data loading)
- **Error boundaries** — for component-level error isolation

## Performance Considerations

### Spatial Queries

- PostGIS GiST index on `images.footprint` — O(log n) spatial lookup
- `ST_Intersects` with SRID 4326 — index-accelerated intersection test
- Collection filtering via parameterized `IN` clause

### Processing Pipeline

- Celery workers with configurable concurrency (default: 4)
- Band downloads use `aiohttp` with connection pooling (4 concurrent)
- Results cached on disk with 7-day TTL
- Batch processing uses single-query image lookup (`WHERE id IN (...)`)

### Frontend

- LayerCake for performant SVG charts
- Lazy image loading in gallery
- Sparkline components for inline trend indicators
- Client-side routing (SvelteKit SPA)
