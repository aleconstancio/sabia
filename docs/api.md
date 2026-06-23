# API Reference

> Complete endpoint reference for the Horus backend. Interactive docs available at `/docs` when running.

**Base URL**: `http://localhost:8000/api`

**Interactive docs**: `http://localhost:8000/docs` (Swagger UI)

**OpenAPI spec**: `http://localhost:8000/openapi.json`

---

## Table of Contents

- [Health](#health)
- [Images](#images)
- [Processing](#processing)
- [Tasks](#tasks)
- [ESG](#esg)
- [Weather](#weather)
- [Soil](#soil)
- [Land Cover](#land-cover)
- [Analyses](#analyses)
- [Profiles](#profiles)
- [Geocoding](#geocoding)
- [IBGE](#ibge)
- [Downloads](#downloads)
- [Export](#export)

---

## Health

### `GET /api/health`

Health check endpoint. Returns HTTP 503 when database is disconnected.

**Response 200:**
```json
{ "status": "ok", "database": "connected", "catalog_count": 142 }
```

**Response 503:**
```json
{ "status": "error", "database": "disconnected", "catalog_count": 0 }
```

---

## Images

### `POST /api/images/search`

Search for satellite images whose footprint intersects a polygon.

**Request Body:**
```json
{
  "coordinates": [[[-50.0, -20.0], [-49.0, -20.0], [-49.0, -19.0], [-50.0, -19.0], [-50.0, -20.0]]],
  "collections": ["cbers4a"],
  "limit": 50,
  "offset": 0,
  "date_from": "2025-01-01",
  "date_to": "2025-12-31",
  "max_cloud": 30,
  "sort_by": "acquired_at",
  "sort_order": "desc"
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `coordinates` | `[[[lon, lat]]]` | ✅ | — | GeoJSON Polygon coordinates |
| `collections` | `string[]` | ❌ | all | Filter by collection(s) |
| `limit` | `int` | ❌ | `50` | Max results (max 100) |
| `offset` | `int` | ❌ | `0` | Pagination offset |
| `date_from` | `string` | ❌ | — | Start date (ISO 8601) |
| `date_to` | `string` | ❌ | — | End date (ISO 8601) |
| `max_cloud` | `number` | ❌ | `100` | Max cloud cover percentage |
| `sort_by` | `string` | ❌ | `acquired_at` | Sort field (`acquired_at` or `cloud_cover`) |
| `sort_order` | `string` | ❌ | `desc` | Sort order (`asc` or `desc`) |

**Response 200:**
```json
{
  "images": [
    {
      "id": "CBERS4A_WPM_20250101_123_456_L4_DN",
      "collection": "cbers4a",
      "cloud_cover": 12.5,
      "acquired_at": "2025-01-01T12:30:00Z",
      "thumbnail_url": "http://...",
      "footprint": { "type": "Polygon", "coordinates": [...] }
    }
  ],
  "total": 142
}
```

### `GET /api/images/{image_id}`

Get full metadata for a single image.

**Response 200:**
```json
{
  "id": "CBERS4A_WPM_20250101_123_456_L4_DN",
  "collection": "cbers4a",
  "footprint": { "type": "Polygon", "coordinates": [...] },
  "cloud_cover": 12.5,
  "acquired_at": "2025-01-01T12:30:00Z",
  "thumbnail_url": "http://...",
  "metadata": {
    "assets": {
      "pan": "http://...?email=user@example.com",
      "red": "http://...?email=user@example.com",
      "green": "http://...?email=user@example.com",
      "blue": "http://...?email=user@example.com",
      "nir": "http://...?email=user@example.com"
    }
  }
}
```

**Response 404:**
```json
{ "detail": "Image not found" }
```

### `POST /api/images/timeline`

Get available images for a polygon, sorted chronologically.

**Request Body:** Same as `/api/images/search`.

**Response 200:**
```json
{
  "timeline": [
    { "id": "CBERS4A_...", "date": "2025-01-01T12:00:00Z", "cloud_cover": 12.5, "thumbnail_url": "..." }
  ],
  "total": 50
}
```

---

## Processing

### `POST /api/process`

Submit an image for async processing. Returns a task ID immediately.

**Request Body:**
```json
{
  "image_id": "CBERS4A_WPM_20250101_123_456_L4_DN",
  "coordinates": [[[-50.0, -20.0], [-49.0, -20.0], ...]],
  "product": "NDVI"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image_id` | `string` | ✅ | Image to process |
| `coordinates` | `[[[lon, lat]]]` | ✅ | GeoJSON Polygon |
| `product` | `string` | ✅ | Product name (see below) |

**Available products**: `NDVI`, `TCI`, `NDWI`, `SAVI`, `EVI`, `MSAVI2`, `VARI`, `MNDWI`, `CIR`, `NBR`, `NDMI`

**Response 200:**
```json
{ "task_id": "8f7a2b1c-3d4e-5f6a-7b8c-9d0e1f2a3b4c" }
```

### `POST /api/process/batch`

Process multiple images for the same polygon.

**Request Body:**
```json
{
  "image_ids": ["CBERS4A_...", "CBERS4A_..."],
  "coordinates": [[[-50.0, -20.0], ...]],
  "product": "NDVI"
}
```

**Response 200:**
```json
{
  "tasks": [
    {"image_id": "CBERS4A_...", "task_id": "8f7a2b1c-..."},
    {"image_id": "CBERS4A_...", "task_id": "9a8b7c6d-..."}
  ]
}
```

### `POST /api/difference`

Compute NDVI difference between two processed results (result_B - result_A).

**Request Body:**
```json
{
  "task_id_a": "8f7a2b1c-...",
  "task_id_b": "9a8b7c6d-..."
}
```

**Response 200:**
```json
{ "task_id": "7e6d5c4b-..." }
```

---

## Tasks

### `GET /api/tasks/{task_id}`

Poll the status of an async processing task.

**Response (pending):**
```json
{ "task_id": "...", "status": "pending", "progress": 0, "phase": "" }
```

**Response (running):**
```json
{ "task_id": "...", "status": "running", "progress": 60, "phase": "generating_ndvi" }
```

**Phases**: `downloading`, `cropping`, `generating_{product}`, `compressing`, `done`

**Response (done):**
```json
{
  "task_id": "...",
  "status": "done",
  "progress": 100,
  "phase": "done",
  "result": {
    "bounds": [[-20.5, -50.5], [-19.5, -49.5]],
    "path": "/tmp/horus/cache/NDVI_CBERS4A_2025...png",
    "statistics": { "mean": 0.72, "std": 0.15, "min": 0.1, "max": 0.95 }
  }
}
```

**Response (error):**
```json
{ "task_id": "...", "status": "error", "progress": 0, "phase": "error", "error": "Download failed" }
```

### `WS /api/tasks/{task_id}/ws`

WebSocket endpoint that streams task progress in real-time. Same payload format as polling, pushed every second. Connection closes on completion.

---

## ESG

### `POST /api/carbon-stock`

Estimate carbon stock from soil organic carbon and NDVI biomass proxy.

**Request Body:**
```json
{
  "coordinates": [[[-50.0, -20.0], [-49.0, -20.0], ...]]
}
```

**Response 200:**
```json
{
  "carbon_stock_t_ha": 12.3,
  "soil_organic_carbon": 18.5,
  "biomass_estimate": 1.25,
  "ndvi_avg": 0.5,
  "warning": "NDVI value is estimated"
}
```

### `POST /api/fire-risk`

Calculate fire risk from weather data and NBR trend.

**Request Body:**
```json
{
  "coordinates": [[[-50.0, -20.0], [-49.0, -20.0], ...]]
}
```

**Response 200:**
```json
{
  "risk_level": "medium",
  "risk_score": 42.5,
  "nbr_trend": 0.5,
  "temperature_factor": 0.6,
  "humidity_factor": 0.4,
  "precipitation_factor": 0.3,
  "warning": "NBR trend is estimated"
}
```

---

## Weather

### `GET /api/weather/{lat}/{lon}`

Fetch weather data from Open-Meteo (free, no API key).

**Path Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `lat` | float | Latitude (-90 to 90) |
| `lon` | float | Longitude (-180 to 180) |

**Response 200:**
```json
{
  "current": {
    "temperature_2m": 27.5,
    "relative_humidity_2m": 65,
    "precipitation": 0,
    "weather_code": 1,
    "soil_moisture_0_to_7cm": 0.23
  },
  "daily": {
    "temperature_2m_max": [30.1, 29.8, ...],
    "temperature_2m_min": [22.1, 21.5, ...],
    "precipitation_sum": [2.5, 0, ...]
  }
}
```

**Response 400:** Invalid lat/lon values.

---

## Soil

### `GET /api/soil/{lat}/{lon}`

Fetch soil properties from ISRIC SoilGrids (free, no key).

**Path Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `lat` | float | Latitude (-90 to 90) |
| `lon` | float | Longitude (-180 to 180) |

**Response 200:** SoilGrids properties response with layers for pH, OC, nitrogen, CEC, sand/silt/clay.

### `POST /api/soil/zonal`

Get average soil properties for a polygon area.

**Request Body:**
```json
{
  "coordinates": [[[-50.0, -20.0], [-49.0, -20.0], ...]]
}
```

**Response 200:**
```json
{
  "source": "ISRIC SoilGrids",
  "points_sampled": 10,
  "ph": 5.8,
  "organic_carbon_gkg": 18.5,
  "sand_pct": 40.2,
  "silt_pct": 35.1,
  "clay_pct": 24.7,
  "note": "Averaged from multiple points within polygon"
}
```

---

## Land Cover

### `GET /api/landcover/{lat}/{lon}`

Get ESA WorldCover 2021 land cover classes for a point.

**Path Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `lat` | float | Latitude (-90 to 90) |
| `lon` | float | Longitude (-180 to 180) |

**Response 200:**
```json
{
  "source": "ESA WorldCover 2021",
  "resolution": "10m",
  "classes": {
    "10": "Tree cover", "20": "Shrubland", "30": "Grassland",
    "40": "Cropland", "50": "Built-up", "60": "Bare/sparse",
    "70": "Snow/ice", "80": "Water", "90": "Wetland",
    "95": "Mangroves", "100": "Moss/lichen"
  },
  "tile_url": "https://esa-worldcover.s3.eu-central-1.amazonaws.com/..."
}
```

### `POST /api/landcover/zonal`

Get land cover class percentages for a polygon area.

**Request Body:**
```json
{
  "coordinates": [[[-50.0, -20.0], [-49.0, -20.0], ...]]
}
```

**Response 200:**
```json
{
  "source": "ESA WorldCover 2021",
  "tile_url": "https://...",
  "centroid": { "lat": -19.5, "lon": -49.5 },
  "note": "Full zonal stats require server-side rasterio sampling"
}
```

---

## Profiles

### `POST /api/profiles`

Create a new region profile.

**Request Body:**
```json
{
  "name": "Amazonia Conservation Area",
  "polygon": { "type": "Polygon", "coordinates": [[[-50.0, -20.0], ...]] },
  "satellite_data": { "product": "NDVI", "stats": { "mean": 0.72 } }
}
```

**Response 200:**
```json
{ "id": "uuid-here" }
```

### `GET /api/profiles`

List region profiles.

**Query Parameters:**
| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `limit` | int | 50 | Max results (max 200) |
| `offset` | int | 0 | Pagination offset |

**Response 200:**
```json
{
  "profiles": [...],
  "total": 12
}
```

### `GET /api/profiles/{profile_id}`

Get a single region profile.

### `PUT /api/profiles/{profile_id}/refresh`

Refresh external data (weather, soil, land cover) for a profile.

### `DELETE /api/profiles/{profile_id}`

Delete a region profile.

---

## Geocoding

### `GET /api/geocode`

Proxy for Nominatim geocoding. Rate limited to 1 request/second.

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `q` | string | ✅ | Search query (e.g., "São Paulo") |

**Response 200:** Array of geocoding results (Nominatim format).

**Response 429:** Rate limit exceeded.

---

## IBGE

### `GET /api/ibge/uf`

List Brazilian states (UF).

**Response 200:**
```json
["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", ...]
```

### `GET /api/ibge/cidades/{uf}`

List cities for a given state.

**Response 200:**
```json
["Acrelândia", "Assis Brasil", "Brasiléia", "Bujari", ...]
```

**Response 404:** Empty array for invalid UF.

---

## Downloads

### `GET /api/overlay/{filename}`

Serve a processed overlay PNG. Path traversal protected.

**Response 200:** PNG image
**Response 400:** Invalid filename
**Response 403:** Path traversal attempt
**Response 404:** File not found

### `GET /api/download/{task_id}`

Download the processed raster (PNG) for a completed task. Path traversal protected.

**Response 200:** PNG file download
**Response 404:** Task not found or not complete

### `GET /api/download/{task_id}/geotiff`

Download the processed GeoTIFF (full resolution, with CRS). Path traversal protected.

**Response 200:** TIFF file download
**Response 404:** GeoTIFF not available

### `POST /api/download/batch`

Download multiple processed results as a ZIP archive.

**Request Body:**
```json
{ "task_ids": ["8f7a2b1c-...", "9a8b7c6d-..."] }
```

**Response 200:** ZIP file download
**Response 400:** Maximum 5 tasks per batch

---

## Export

### `POST /api/export/pdf`

Generate a downloadable ESG PDF report.

**Request Body:**
```json
{
  "image_id": "CBERS4A_...",
  "product": "NDVI",
  "date": "2025-01-01T00:00:00Z",
  "cloud_cover": 12.5,
  "weather": { "temperature": 27.5, "humidity": 65, "precipitation": 0 },
  "overlay_path": "/tmp/horus/cache/NDVI_CBERS4A_...png"
}
```

**Response 200:** PDF file download (`horus-esg-report.pdf`)

---

## Error Responses

All errors follow the format:

```json
{ "detail": "Human-readable error message" }
```

| Status Code | Description |
|-------------|-------------|
| `400` | Invalid input (malformed polygon, out-of-range coordinates) |
| `404` | Resource not found |
| `429` | Rate limit exceeded |
| `500` | Internal server error |
| `501` | Not implemented (stub endpoint) |
| `503` | Service unavailable (database disconnected) |
