# Architecture

## Overview

SpaceEye is a single-page application with a Python backend and SvelteKit frontend. The distinguishing architectural choice is that **all geospatial processing happens server-side** (the browser only displays results), while **all map interaction happens client-side** (no server-rendered maps).

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

## Directory Structure

```
apps/spaceeye-web/          # SvelteKit SPA
├── src/
│   ├── lib/
│   │   ├── api/            # Typed API client (createApiClient)
│   │   ├── components/     # SpaceEye components (SearchMenu, ImageGallery)
│   │   ├── stores/         # Svelte 5 runes state
│   │   └── ui/             # Vendored design system (Button, Card, etc.)
│   └── routes/
│       └── +page.svelte    # Main map page

backend/                    # FastAPI + Celery
├── api/                    # Route handlers (thin)
│   ├── router.py           # All endpoints
│   └── deps.py             # Dependency injection
├── domain/                 # Business logic
│   ├── catalog.py          # STAC collection abstraction
│   ├── products.py         # NDVI/TCI/NDWI product registry
│   └── processing.py       # Processing orchestrator
├── services/               # Infrastructure services
│   ├── downloader.py       # Async band downloader
│   ├── raster_processor.py # Crop/reproject helpers
│   └── compressor.py       # GeoTIFF → PNG
├── repositories/           # Database access
│   └── images.py           # PostGIS spatial queries
├── models/                 # Data models
│   ├── database.py         # SQLAlchemy async setup
│   └── schemas.py          # Pydantic request/response
├── tasks/                  # Celery task definitions
│   ├── celery_app.py
│   └── processing.py
├── config.py               # Typed settings (pydantic-settings)
└── main.py                 # FastAPI app

pipeline/                   # Data pipeline scripts
├── ingest.py               # STAC → PostGIS ingestion
└── cleanup.py              # TTL-based cache cleanup

sql/
└── 001_init.sql            # PostGIS schema + indexes
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

## Why PostGIS Instead of Python Filtering?

The old code loaded every image from the `images` table, parsed its coordinates JSON, converted it to a Shapely polygon, and checked `contains_properly` in Python. For 1,000 images this is ~100ms. For 100,000 (CBERS-4A catalog) it's several seconds.

PostGIS `ST_Intersects` uses a GiST index — the R-tree index prunes non-overlapping geometries in logarithmic time. Same query: ~2ms regardless of catalog size.

## Why Async Tasks Instead of Sync?

Downloading 4 spectral bands at ~200MB each takes 30-120 seconds. In the old code, Flask's single thread was blocked for the entire duration, meaning one user could block all others.

Celery workers handle this asynchronously: the HTTP endpoint returns a task ID immediately, and the frontend polls for progress. Multiple users can process images concurrently, and the worker pool limits resource usage.
