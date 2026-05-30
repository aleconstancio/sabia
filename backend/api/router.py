import json
import os

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db
from backend.models.schemas import PolygonRequest, ProcessRequest
from backend.config import get_settings

router = APIRouter()

_datasets_path = os.path.join(os.path.dirname(__file__), "..", "datasets", "cidades_brasileiras.json")
with open(_datasets_path, "r", encoding="utf-8") as f:
    _cidades_data = json.load(f)


@router.get("/health")
async def health():
    return {"status": "ok"}


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

    images, total = await find_images_by_polygon(db, req.coordinates, req.collections, req.limit, req.offset)
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


@router.get("/overlay/{filename}")
async def serve_overlay(filename: str):
    path = os.path.join(get_settings().temp_dir, "cache", filename)
    if not os.path.exists(path):
        raise HTTPException(404, "Overlay not found")
    return FileResponse(path, media_type="image/png")


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
    async with httpx.AsyncClient() as client:
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
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, params=params)
        if resp.status_code == 200:
            return resp.json()
        return {}


@router.get("/landcover/{lat}/{lon}")
async def get_landcover(lat: float, lon: float):
    """Get land cover classification for a point using open data."""
    classes = {
        10: "Tree cover", 20: "Shrubland", 30: "Grassland",
        40: "Cropland", 50: "Built-up", 60: "Bare/sparse",
        70: "Snow/ice", 80: "Water", 90: "Wetland",
        95: "Mangroves", 100: "Moss/lichen",
    }

    return {
        "source": "ESA WorldCover 2020",
        "resolution": "10m",
        "classes": {k: v for k, v in classes.items()},
        "note": "Full raster sampling requires downloading the tile via S3",
    }


@router.post("/export/pdf")
async def export_pdf(data: dict):
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
    c.drawString(50, y, f"Imagem: {data.get('image_id', 'N/A')}")
    c.drawString(50, y - 20, f"Produto: {data.get('product', 'N/A')}")
    c.drawString(50, y - 40, f"Data: {data.get('date', 'N/A')}")

    cc = data.get('cloud_cover')
    if cc is not None:
        c.drawString(50, y - 60, f"Nuvem: {cc:.1f}%")

    # Embed processed image overlay if available
    overlay_path = data.get('overlay_path', '')
    overlay_y = y - 80
    if overlay_path and os.path.exists(overlay_path):
        try:
            from reportlab.lib.utils import ImageReader
            img = ImageReader(overlay_path)
            c.drawImage(img, 50, y - 260, width=400, height=200, preserveAspectRatio=True)
            overlay_y = y - 280
        except Exception:
            c.drawString(50, overlay_y, "(Imagem overlay não disponível)")
            overlay_y -= 20

    weather = data.get('weather')
    if weather:
        weather_y = overlay_y
        c.drawString(50, weather_y, "Clima:")
        c.drawString(70, weather_y - 20, f"Temperatura: {weather.get('temperature', 'N/A')}°C")
        c.drawString(70, weather_y - 40, f"Umidade: {weather.get('humidity', 'N/A')}%")
        c.drawString(70, weather_y - 60, f"Precipitação: {weather.get('precipitation', 'N/A')} mm")

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


@router.post("/process/batch")
async def process_batch(req: dict):
    """Process multiple images for the same polygon and return task IDs."""
    image_ids = req.get("image_ids", [])
    coordinates = req.get("coordinates")
    product = req.get("product", "NDVI")

    from backend.tasks.processing import process_image_task

    task_ids = []
    for img_id in image_ids:
        task = process_image_task.delay(
            image_id=img_id,
            polygon_coords=coordinates,
            product=product,
            band_urls={},
        )
        task_ids.append({"image_id": img_id, "task_id": task.id})

    return {"tasks": task_ids}


@router.post("/difference")
async def compute_difference(req: dict):
    """Compute NDVI difference between two processed images."""
    task_id_a = req.get("task_id_a")
    task_id_b = req.get("task_id_b")

    from backend.tasks.processing import compute_difference_task

    task = compute_difference_task.delay(
        task_id_a=task_id_a,
        task_id_b=task_id_b,
    )
    return {"task_id": task.id}


@router.get("/download/{task_id}")
async def download_result(task_id: str):
    """Download the processed raster (PNG) for a completed task."""
    from celery.result import AsyncResult
    from backend.tasks.celery_app import celery_app

    result = AsyncResult(task_id, app=celery_app)
    if result.state != "SUCCESS":
        raise HTTPException(404, "Task not found or not yet complete")

    path = result.result.get("path", "")
    if not path or not os.path.exists(path):
        raise HTTPException(404, "Result file not found")

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
