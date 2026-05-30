# API Reference

Base URL: `http://localhost:8000/api`

Interactive docs: `http://localhost:8000/docs` (Swagger UI)

---

## `GET /api/health`

Health check.

**Response 200:**
```json
{ "status": "ok" }
```

---

## `GET /api/collections`

List supported satellite collections and their capabilities.

**Response 200:**
```json
[
  {
    "id": "cbers4a",
    "bands": ["pan", "red", "green", "blue", "nir"],
    "products": ["NDVI", "TCI"]
  },
  {
    "id": "amazonia1",
    "bands": ["red", "green", "blue", "nir"],
    "products": ["TCI", "NDVI"]
  }
]
```

---

## `POST /api/images/search`

Search for satellite images whose footprint intersects a given polygon.

**Request Body:**
```json
{
  "coordinates": [[[-50.0, -20.0], [-49.0, -20.0], [-49.0, -19.0], [-50.0, -19.0], [-50.0, -20.0]]],
  "collections": ["cbers4a"],
  "limit": 50,
  "offset": 0
}
```

| Field | Type | Required | Default | Description |
|-------|------|----------|---------|-------------|
| `coordinates` | `[[[lon, lat]]]` | ✅ | — | GeoJSON Polygon coordinates (exterior ring) |
| `collections` | `string[]` | ❌ | `null` (all) | Filter by collection(s) |
| `limit` | `int` | ❌ | `50` | Max results (max 100) |
| `offset` | `int` | ❌ | `0` | Pagination offset |

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

---

## `GET /api/images/{image_id}`

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

---

## `POST /api/process`

Submit an image for async processing. Returns a task ID immediately. The frontend polls `/api/tasks/{task_id}` for completion.

**Request Body:**
```json
{
  "image_id": "CBERS4A_WPM_20250101_123_456_L4_DN",
  "coordinates": [[[-50.0, -20.0], [-49.0, -20.0], ...]],
  "product": "NDVI"
}
```

`product` must be one of: `NDVI`, `TCI`, `NDWI`, `NDDI`

**Response 200:**
```json
{ "task_id": "8f7a2b1c-3d4e-5f6a-7b8c-9d0e1f2a3b4c" }
```

---

## `GET /api/tasks/{task_id}`

Poll the status of an async processing task.

**Response (pending):**
```json
{ "task_id": "...", "status": "pending", "progress": 0, "phase": "" }
```

**Response (running):**
```json
{ "task_id": "...", "status": "running", "progress": 60, "phase": "generating_ndvi" }
```

Phases: `downloading`, `cropping`, `generating_{product}`, `compressing`, `done`

**Response (done):**
```json
{
  "task_id": "...",
  "status": "done",
  "progress": 100,
  "phase": "done",
  "result": {
    "bounds": [[-20.5, -50.5], [-19.5, -49.5]],
    "path": "/tmp/spaceeye/cache/NDVI_CBERS4A_2025...png"
  }
}
```

The `bounds` are `[[south, west], [north, east]]` for use with Leaflet's `L.imageOverlay`.

**Response (error):**
```json
{ "task_id": "...", "status": "error", "progress": 0, "phase": "error", "error": "Download failed: Connection timeout" }
```

---

## `WS /api/tasks/{task_id}/ws`

WebSocket endpoint that streams task progress as server-sent events (through WebSocket frames). Same payload format as the polling endpoint, but pushed in real-time.

Messages are JSON, sent approximately every second while the task is `PROGRESS`. The connection closes when the task reaches `SUCCESS` or `FAILURE`.

---

## `GET /api/ibge/uf`

List Brazilian states (UF).

**Response 200:**
```json
["AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", ...]
```

---

## `GET /api/ibge/cidades/{uf}`

List cities for a given state.

**Response 200:**
```json
["Acrelândia", "Assis Brasil", "Brasiléia", "Bujari", ...]
```

**Response 404:** Returns empty array for invalid UF.

---

## Error Responses

All errors follow the format:

```json
{
  "detail": "Human-readable error message"
}
```

HTTP status codes:
- `400` — Invalid input (malformed polygon, invalid product name)
- `404` — Image or resource not found
- `500` — Internal server error (processing failure, database error)

---

## `POST /api/process/batch`

Process multiple images for the same polygon. Returns task IDs for each.

**Request Body:**
```json
{
  "image_ids": ["CBERS4A_...", "CBERS4A_..."],
  "coordinates": [[[-50.0, -20.0], ...]],
  "product": "NDVI"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `image_ids` | `string[]` | ✅ | Image IDs to process |
| `coordinates` | `[[[lon, lat]]]` | ✅ | GeoJSON Polygon coordinates |
| `product` | `string` | ❌ | Product name (default: `NDVI`) |

**Response 200:**
```json
{
  "tasks": [
    {"image_id": "CBERS4A_...", "task_id": "8f7a2b1c-..."},
    {"image_id": "CBERS4A_...", "task_id": "9a8b7c6d-..."}
  ]
}
```

---

## `POST /api/difference`

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

Poll `/api/tasks/{task_id}` for completion. The result contains `type: "diff"` with bounds and overlay path.

---

## `GET /api/download/{task_id}`

Download the processed raster (PNG) for a completed task.

**Response 200:** PNG file download
**Response 404:** Task not found or not yet complete

---

## `GET /api/geocode`

Proxy for Nominatim geocoding. Search for a location by text.

**Query Parameters:**
| Param | Type | Required | Description |
|-------|------|----------|-------------|
| `q` | string | ✅ | Search query (e.g., "São Paulo-SP") |

**Response 200:** Array of geocoding results (Nominatim format)
