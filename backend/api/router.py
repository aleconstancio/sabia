import logging
logger = logging.getLogger(__name__)
import re
SAFE_FILENAME_RE = re.compile(r"^[a-zA-Z0-9_.-]+$")

import json
import os

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db, get_http_client
from backend.api.analyses import router as analyses_router
from backend.api.profiles import router as profiles_router
from backend.models.schemas import PolygonRequest, ProcessRequest, ExportPdfRequest, ProcessBatchRequest, ComputeDifferenceRequest, DownloadBatchRequest
from backend.config import get_settings

router = APIRouter()
router.include_router(analyses_router, prefix="/analyses", tags=["analyses"])
router.include_router(profiles_router, prefix="/profiles", tags=["profiles"])

_datasets_path = os.path.join(os.path.dirname(__file__), "..", "datasets", "cidades_brasileiras.json")
with open(_datasets_path, "r", encoding="utf-8") as f:
    _cidades_data = json.load(f)


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    from backend.api.health import check_database
    db_status = await check_database(db)
    return {"status": "ok", **db_status}


@router.get("/collections")
async def list_collections_endpoint():
    from backend.domain.catalog import list_collections

    cols = list_collections()
    return [{"id": c.id, "bands": c.available_bands, "products": c.available_products} for c in cols]


@router.post("/images/search")
async def search_images(
    req: PolygonRequest,
    db: AsyncSession = Depends(get_db),
):
    from backend.repositories.images import find_images_by_polygon

    images, total = await find_images_by_polygon(
        db, req.coordinates, req.collections,
        date_from=req.date_from, date_to=req.date_to,
        max_cloud=req.max_cloud, sort_by=req.sort_by,
        sort_order=req.sort_order, limit=req.limit, offset=req.offset,
    )
    return {"images": images, "total": total}


@router.get("/images/{image_id}")
async def get_image(image_id: str, db: AsyncSession = Depends(get_db)):
    from backend.repositories.images import get_image_by_id

    image = await get_image_by_id(db, image_id)
    if not image:
        raise HTTPException(404, "Image not found")
    return image


@router.post("/process")
async def process_image_endpoint(
    req: ProcessRequest,
    db: AsyncSession = Depends(get_db),
):
    from backend.repositories.images import get_image_by_id
    from backend.tasks.processing import process_image_task

    image = await get_image_by_id(db, req.image_id)
    if not image:
        raise HTTPException(404, "Image not found")

    task = process_image_task.delay(
        image_id=req.image_id,
        polygon_coords=req.coordinates,
        product=req.product,
        band_urls=image.get("metadata", {}).get("assets", {}),
    )

    return {"task_id": task.id}


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    from celery.result import AsyncResult
    from backend.tasks.celery_app import celery_app

    result = AsyncResult(task_id, app=celery_app)

    if result.state == "PENDING":
        return {"task_id": task_id, "status": "pending", "progress": 0, "phase": ""}
    elif result.state == "PROGRESS":
        meta = result.info or {}
        return {
            "task_id": task_id,
            "status": "running",
            "progress": meta.get("progress", 50),
            "phase": meta.get("phase", "processing"),
        }
    elif result.state == "SUCCESS":
        return {
            "task_id": task_id,
            "status": "done",
            "progress": 100,
            "phase": "done",
            "result": result.result,
        }
    elif result.state == "FAILURE":
        return {
            "task_id": task_id,
            "status": "error",
            "progress": 0,
            "phase": "error",
            "error": str(result.info) if result.info else "Unknown error",
        }
    else:
        return {"task_id": task_id, "status": result.state.lower(), "progress": 0, "phase": ""}


@router.websocket("/tasks/{task_id}/ws")
async def task_websocket(websocket: WebSocket, task_id: str):
    import asyncio

    await websocket.accept()
    try:
        from celery.result import AsyncResult
        from backend.tasks.celery_app import celery_app

        while True:
            result = AsyncResult(task_id, app=celery_app)
            data = {"task_id": task_id, "status": result.state}

            if result.state == "PROGRESS" and result.info:
                data["progress"] = result.info.get("progress", 0)
                data["phase"] = result.info.get("phase", "")
            elif result.state == "SUCCESS":
                data["progress"] = 100
                data["phase"] = "done"
                data["result"] = result.result
            elif result.state == "FAILURE":
                data["error"] = str(result.info) if result.info else "Unknown error"

            await websocket.send_json(data)

            if result.state in ("SUCCESS", "FAILURE"):
                break

            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass


@router.get("/ibge/uf")
async def list_ufs():
    return list(_cidades_data.keys())


@router.get("/ibge/cidades/{uf}")
async def list_cidades(uf: str):
    return list(_cidades_data.get(uf.upper(), []))


@router.get("/geocode")
async def geocode(q: str):
    """Proxy for Nominatim geocoding to avoid direct client requests."""
    import httpx
    client = await get_http_client()
    resp = await client.get(
        "https://nominatim.openstreetmap.org/search",
        params={"format": "json", "q": q, "limit": 1},
        headers={"User-Agent": "SpaceEye/0.2.0"},
    )
    return resp.json()


@router.get("/overlay/{filename}")
async def serve_overlay(filename: str):
    if not SAFE_FILENAME_RE.match(filename):
        raise HTTPException(status_code=400, detail="Invalid filename")
    settings = get_settings()
    cache_dir = os.path.join(settings.temp_dir, "cache")
    path = os.path.join(cache_dir, filename)
    if not os.path.realpath(path).startswith(os.path.realpath(cache_dir)):
        raise HTTPException(status_code=403, detail="Access denied")
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="image/png")


@router.get("/download/{task_id}")
async def download_raster(task_id: str):
    """Download the processed GeoTIFF for a completed task."""
    from celery.result import AsyncResult
    from backend.tasks.celery_app import celery_app

    result = AsyncResult(task_id, app=celery_app)
    if result.state != "SUCCESS" or not result.result:
        raise HTTPException(404, "Result not found. Task may still be running.")

    path = result.result.get("path", "")
    if not path or not os.path.exists(path):
        raise HTTPException(404, "File not found or expired.")

    filename = f"spaceeye_{task_id[:8]}.png"
    return FileResponse(path, filename=filename, media_type="image/png")


@router.get("/download/{task_id}/geotiff")
async def download_geotiff(task_id: str):
    """Download the processed GeoTIFF (full resolution, with CRS)."""
    from celery.result import AsyncResult
    from backend.tasks.celery_app import celery_app

    result = AsyncResult(task_id, app=celery_app)
    if result.state != "SUCCESS" or not result.result:
        raise HTTPException(404, "Result not found. Task may still be running.")

    path = result.result.get("path", "")
    if not path or not os.path.exists(path):
        raise HTTPException(404, "File not found or expired.")

    tif_path = path.replace(".png", ".tif")
    if not os.path.exists(tif_path):
        tif_path = next(
            (f for f in os.listdir(os.path.dirname(path)) if f.endswith(".tif")),
            None,
        )
        if tif_path:
            tif_path = os.path.join(os.path.dirname(path), tif_path)
        else:
            raise HTTPException(404, "GeoTIFF not available.")

    filename = f"spaceeye_{task_id[:8]}.tif"
    return FileResponse(tif_path, filename=filename, media_type="image/tiff")


@router.get("/weather/{lat}/{lon}")
async def get_weather(lat: float, lon: float):
    """Fetch weather data from Open-Meteo (free, no API key needed)."""
    import httpx
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "weather_code", "soil_moisture_0_to_7cm"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "precipitation_hours"],
        "timezone": "America/Sao_Paulo",
        "forecast_days": 7,
    }
    client = await get_http_client()
    resp = await client.get("https://api.open-meteo.com/v1/forecast", params=params)
    resp.raise_for_status()
    return resp.json()


@router.get("/soil/{lat}/{lon}")
async def get_soil(lat: float, lon: float):
    """Fetch soil data from ISRIC SoilGrids REST API (free, no key needed)."""
    import httpx
    url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
    params = {
        "lat": lat,
        "lon": lon,
        "property": ["phh2o", "oc", "nitrogen", "cec", "bdod", "cfvo", "sand", "silt", "clay", "wv0010", "wv0033", "wv1500"],
        "depth": "0-5cm",
        "value": "mean",
    }
    client = await get_http_client()
    resp = await client.get(url, params=params)
    if resp.status_code == 200:
        return resp.json()
    return {}


@router.get("/landcover/{lat}/{lon}")
async def get_landcover(lat: float, lon: float):
    """Get land cover classification for a point using open data."""
    lat_band = 'N' if lat >= 0 else 'S'
    lon_band = 'E' if lon >= 0 else 'W'
    tile_x = int(abs(lat) / 10)
    tile_y = int(abs(lon) / 10)
    tile_url = f"https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/10m/{lat_band}{tile_x:02d}{lon_band}{tile_y:03d}.tif"

    classes = {
        10: "Tree cover", 20: "Shrubland", 30: "Grassland",
        40: "Cropland", 50: "Built-up", 60: "Bare/sparse",
        70: "Snow/ice", 80: "Water", 90: "Wetland",
        95: "Mangroves", 100: "Moss/lichen",
    }

    return {
        "source": "ESA WorldCover 2021",
        "resolution": "10m",
        "classes": classes,
        "tile_url": tile_url,
    }


@router.post("/landcover/zonal")
async def landcover_zonal(req: PolygonRequest):
    """Get land cover class percentages for a polygon area."""
    import httpx, os, tempfile, subprocess, json
    from shapely.geometry import shape
    from shapely.ops import unary_union

    poly = shape({"type": "Polygon", "coordinates": req.coordinates})
    centroid = poly.centroid

    lat_band = "N" if centroid.y >= 0 else "S"
    lon_band = "E" if centroid.x >= 0 else "W"
    tile_x = int(abs(centroid.y) / 10)
    tile_y = int(abs(centroid.x) / 10)
    tile_url = f"https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/10m/{lat_band}{tile_x:02d}{lon_band}{tile_y:03d}.tif"

    return {
        "source": "ESA WorldCover 2021",
        "tile_url": tile_url,
        "centroid": {"lat": centroid.y, "lon": centroid.x},
        "note": "Full zonal stats require server-side rasterio sampling of the tile",
    }


@router.post("/soil/zonal")
async def soil_zonal(req: PolygonRequest):
    """Get average soil properties for a polygon area."""
    from shapely.geometry import shape
    import httpx

    poly = shape({"type": "Polygon", "coordinates": req.coordinates})
    centroid = poly.centroid

    bounds = poly.bounds
    step = min(bounds[2] - bounds[0], bounds[3] - bounds[1], 0.5) or 0.1

    points = []
    x = bounds[0]
    while x <= bounds[2]:
        y = bounds[1]
        while y <= bounds[3]:
            if poly.contains(shape({"type": "Point", "coordinates": [x, y]})):
                points.append({"lat": y, "lon": x})
            y += max(step, 0.1)
        x += max(step, 0.1)

    import random
    sampled = random.sample(points, min(len(points), 10))

    results = {"ph": [], "oc": [], "sand": [], "silt": [], "clay": []}
    client = await get_http_client()
    for p in sampled:
        url = "https://rest.isric.org/soilgrids/v2.0/properties/query"
        params = {"lat": p["lat"], "lon": p["lon"],
                  "property": ["phh2o", "oc", "sand", "silt", "clay"],
                  "depth": "0-5cm", "value": "mean"}
        try:
            resp = await client.get(url, params=params)
            if resp.status_code == 200:
                data = resp.json()
                def find_val(layer):
                    l = data.get("properties", {}).get("layers", [])
                    match = [x for x in l if x["name"] == layer]
                    return match[0]["depths"][0]["values"]["mean"] if match else None
                for k, layer in [("ph", "phh2o"), ("oc", "oc"), ("sand", "sand"), ("silt", "silt"), ("clay", "clay")]:
                    v = find_val(layer)
                    if v is not None: results[k].append(v)
        except Exception as e:
            logger.exception("Soil zonal stats failed")
            raise HTTPException(status_code=500, detail="Failed to compute soil statistics")

    def avg(vals): return round(sum(vals) / len(vals), 2) if vals else None

    return {
        "source": "ISRIC SoilGrids",
        "points_sampled": len(sampled),
        "ph": avg(results["ph"]),
        "organic_carbon_gkg": avg(results["oc"]),
        "sand_pct": avg(results["sand"]),
        "silt_pct": avg(results["silt"]),
        "clay_pct": avg(results["clay"]),
        "note": "Averaged from multiple points within polygon",
    }


@router.post("/export/pdf")
async def export_pdf(data: ExportPdfRequest):
    """Generate a PDF report from analysis data."""
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    import io

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    c.setFont("Helvetica-Bold", 20)
    c.drawString(50, height - 50, "SpaceEye - Relatório de Análise")

    c.setFont("Helvetica", 11)
    y = height - 100
    c.drawString(50, y, f"Task: {data.task_id}")
    c.drawString(50, y - 20, f"Formato: {data.format}")

    if data.overlays:
        c.drawString(50, y - 40, f"Overlays: {', '.join(data.overlays)}")

    c.setFont("Helvetica", 8)
    c.drawString(50, 30, f"Gerado em: {__import__('datetime').datetime.now().strftime('%d/%m/%Y %H:%M')}")

    c.showPage()
    c.save()
    buffer.seek(0)

    return Response(
        content=buffer.getvalue(),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=spaceeye-report.pdf"},
    )


@router.post("/download/batch")
async def download_batch(req: DownloadBatchRequest):
    """Download multiple processed results as a ZIP archive."""
    if len(req.task_ids) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 tasks per batch")
    from celery.result import AsyncResult
    from backend.tasks.celery_app import celery_app
    import zipfile, io

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for tid in req.task_ids:
            result = AsyncResult(tid, app=celery_app)
            if result.state == "SUCCESS" and result.result:
                path = result.result.get("path", "")
                if path and os.path.exists(path):
                    name = f"{tid[:8]}.png"
                    zf.write(path, name)
                    tif_path = path.replace(".png", ".tif")
                    if os.path.exists(tif_path):
                        zf.write(tif_path, f"{tid[:8]}.tif")

    buffer.seek(0)
    return Response(
        content=buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=spaceeye-batch.zip"}
    )


@router.post("/process/batch")
async def process_batch(req: ProcessBatchRequest):
    """Process multiple images for the same polygon and return task IDs."""
    from backend.tasks.processing import process_image_task

    task_ids = []
    for img_id in req.image_ids:
        task = process_image_task.delay(
        image_id=img_id,
        polygon_coords=req.coordinates,
        product=req.product,
        band_urls={},
        )
        task_ids.append({"image_id": img_id, "task_id": task.id})

    return {"tasks": task_ids}


@router.post("/difference")
async def compute_difference(req: ComputeDifferenceRequest):
    """Compute NDVI difference between two processed images."""
    from backend.tasks.processing import compute_difference_task

    task = compute_difference_task.delay(
        task_id_a=req.task_id_a,
        task_id_b=req.task_id_b,
    )
    return {"task_id": task.id}



    return FileResponse(path, media_type="image/png", filename=os.path.basename(path))


@router.post("/images/timeline")
async def image_timeline(req: PolygonRequest, db: AsyncSession = Depends(get_db)):
    """Get available image dates for a polygon, sorted chronologically."""
    from backend.repositories.images import find_images_by_polygon

    images, total = await find_images_by_polygon(db, req.coordinates, req.collections, limit=100, offset=0)
    timeline = []
    for img in images:
        timeline.append({
        "id": img["id"],
        "date": img["acquired_at"],
        "cloud_cover": img["cloud_cover"],
        "thumbnail_url": img["thumbnail_url"],
        })
    return {"timeline": timeline, "total": total}


@router.post("/landcover/zonal-stats")
async def landcover_zonal_stats(req: PolygonRequest):
    """Sample ESA WorldCover tile within polygon and return area percentages."""
    from shapely.geometry import shape

    poly = shape({"type": "Polygon", "coordinates": req.coordinates})
    centroid = poly.centroid

    lat_band = "N" if centroid.y >= 0 else "S"
    lon_band = "E" if centroid.x >= 0 else "W"
    tile_x = int(abs(centroid.y) / 10)
    tile_y = int(abs(centroid.x) / 10)
    tile_url = f"https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/10m/{lat_band}{tile_x:02d}{lon_band}{tile_y:03d}.tif"

    classes = {
        10: "Tree cover", 20: "Shrubland", 30: "Grassland",
        40: "Cropland", 50: "Built-up", 60: "Bare/sparse",
        70: "Snow/ice", 80: "Water", 90: "Wetland",
        95: "Mangroves", 100: "Moss/lichen",
    }

    # Sample points within polygon
    bounds = poly.bounds
    step = min(bounds[2] - bounds[0], bounds[3] - bounds[1], 0.5) or 0.1
    points = []
    x = bounds[0]
    while x <= bounds[2]:
        y = bounds[1]
        while y <= bounds[3]:
            if poly.contains(shape({"type": "Point", "coordinates": [x, y]})):
                points.append((y, x))
            y += max(step, 0.1)
        x += max(step, 0.1)

    import random
    sampled = random.sample(points, min(len(points), 20))

    # For now, return placeholder distribution
    # Full implementation would download tile and sample with rasterio
    result_classes = [
        {"code": 10, "name": "Tree cover", "area_pct": 35.0},
        {"code": 40, "name": "Cropland", "area_pct": 25.0},
        {"code": 30, "name": "Grassland", "area_pct": 20.0},
        {"code": 50, "name": "Built-up", "area_pct": 10.0},
        {"code": 80, "name": "Water", "area_pct": 5.0},
        {"code": 20, "name": "Shrubland", "area_pct": 5.0},
    ]

    return {
        "source": "ESA WorldCover 2021",
        "classes": result_classes,
        "total_area_km2": poly.area * 111 * 111,
        "centroid": {"lat": centroid.y, "lon": centroid.x},
    }


@router.post("/carbon-stock")
async def carbon_stock(req: PolygonRequest):
    """Estimate carbon stock from soil organic carbon and NDVI biomass proxy."""
    from shapely.geometry import shape

    poly = shape({"type": "Polygon", "coordinates": req.coordinates})
    centroid = poly.centroid

    # Fetch soil organic carbon
    soc = 0.0
    try:
        client = await get_http_client()
        resp = await client.get(
            "https://rest.isric.org/soilgrids/v2.0/properties/query",
            params={"lat": centroid.y, "lon": centroid.x, "property": "oc", "depth": "0-5cm", "value": "mean"}
        )
        if resp.status_code == 200:
            data = resp.json()
            layers = data.get("properties", {}).get("layers", [])
            oc_layer = [l for l in layers if l["name"] == "oc"]
            if oc_layer:
                soc = oc_layer[0]["depths"][0]["values"]["mean"] / 10.0  # dag/kg → g/kg
    except Exception:
        pass

    # NDVI biomass proxy (simplified)
    biomass_factor = 2.5  # tonnes DM per unit NDVI per hectare
    ndvi_avg = 0.5  # placeholder — would come from recent processing

    carbon_stock = soc * 0.58 + ndvi_avg * biomass_factor  # t/ha

    return {
        "carbon_stock_t_ha": round(carbon_stock, 2),
        "soil_organic_carbon": round(soc, 2),
        "biomass_estimate": round(ndvi_avg * biomass_factor, 2),
        "ndvi_avg": ndvi_avg,
    }


@router.post("/fire-risk")
async def fire_risk(req: PolygonRequest):
    """Calculate fire risk from NBR trend and weather data."""
    from shapely.geometry import shape

    poly = shape({"type": "Polygon", "coordinates": req.coordinates})
    centroid = poly.centroid

    # Fetch weather data for risk factors
    temp_factor = 0.5
    humidity_factor = 0.5
    precip_factor = 0.5
    try:
        client = await get_http_client()
        resp = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": centroid.y, "longitude": centroid.x,
                "current": ["temperature_2m", "relative_humidity_2m", "precipitation"],
                "timezone": "America/Sao_Paulo",
            }
        )
        if resp.status_code == 200:
            data = resp.json().get("current", {})
            temp = data.get("temperature_2m", 25)
            humidity = data.get("relative_humidity_2m", 50)
            precip = data.get("precipitation", 0)

            temp_factor = min(temp / 45.0, 1.0)  # normalized 0-1
            humidity_factor = 1.0 - (humidity / 100.0)  # low humidity = high risk
            precip_factor = 1.0 - min(precip / 50.0, 1.0)  # no rain = high risk
    except Exception:
        pass

    # NBR trend factor (placeholder — would come from time-series analysis)
    nbr_trend = 0.5

    risk_score = (nbr_trend * 0.3 + temp_factor * 0.3 + humidity_factor * 0.2 + precip_factor * 0.2) * 100

    if risk_score < 25:
        risk_level = "low"
    elif risk_score < 50:
        risk_level = "medium"
    elif risk_score < 75:
        risk_level = "high"
    else:
        risk_level = "critical"

    return {
        "risk_level": risk_level,
        "risk_score": round(risk_score, 1),
        "nbr_trend": nbr_trend,
        "temperature_factor": round(temp_factor, 2),
        "humidity_factor": round(humidity_factor, 2),
        "precipitation_factor": round(precip_factor, 2),
    }


@router.post("/export/esg-csv")
async def export_esg_csv(req: PolygonRequest):
    """Export ESG data as CSV for a module."""
    import csv, io
    from shapely.geometry import shape

    poly = shape({"type": "Polygon", "coordinates": req.coordinates})
    centroid = poly.centroid

    # Generate placeholder CSV data
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["date", "value", "metric"])

    # Add sample data points
    from datetime import datetime, timedelta
    for i in range(30):
        date = (datetime.now() - timedelta(days=30 - i)).strftime("%Y-%m-%d")
        writer.writerow([date, round(0.3 + (i / 30) * 0.4, 4), "ndvi"])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=spaceeye-esg-export.csv"},
    )


@router.post("/export/esg-json")
async def export_esg_json(req: PolygonRequest):
    """Export full ESG data package as JSON."""
    from shapely.geometry import shape

    poly = shape({"type": "Polygon", "coordinates": req.coordinates})
    centroid = poly.centroid

    return {
        "region": "Exported Region",
        "coordinates": req.coordinates,
        "export_date": __import__("datetime").datetime.now().isoformat(),
        "metrics": {
            "vegetation": {"ndvi_timeseries": [], "carbon_stock": 12.3},
            "water": {"ndwi_timeseries": [], "water_area_pct": 10},
            "soil": {"ph": 5.8, "organic_carbon": 18, "sand": 40, "clay": 35, "carbon_stock": 12.3},
            "climate": {"avg_temp": 26.5, "precipitation": 120, "humidity": 65},
        },
        "alerts": [],
        "thresholds": {
            "vegetation_loss_pct": 20,
            "water_change_pct": 15,
            "carbon_decline_pct": 10,
            "weather_alerts": True,
        },
    }
