import logging
logger = logging.getLogger(__name__)
import re
SAFE_FILENAME_RE = re.compile(r"^[a-zA-Z0-9_.-]+$")
import time as _time
_geocode_last_request: float = 0.0

import json
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db, get_http_client
from backend.api.analyses import router as analyses_router
from backend.api.profiles import router as profiles_router
from backend.api.weather import router as weather_router
from backend.api.soil import router as soil_router
from backend.api.landcover import router as landcover_router
from backend.api.esg import router as esg_router
from backend.api.tasks_api import router as tasks_router
from backend.models.schemas import PolygonRequest, ProcessRequest, ExportPdfRequest, ProcessBatchRequest, ComputeDifferenceRequest, DownloadBatchRequest
from backend.config import get_settings

router = APIRouter()
router.include_router(analyses_router, prefix="/analyses", tags=["analyses"])
router.include_router(profiles_router, prefix="/profiles", tags=["profiles"])
router.include_router(weather_router, prefix="/weather", tags=["weather"])
router.include_router(soil_router, prefix="/soil", tags=["soil"])
router.include_router(landcover_router, prefix="/landcover", tags=["landcover"])
router.include_router(esg_router, prefix="", tags=["esg"])
router.include_router(tasks_router, prefix="/tasks", tags=["tasks"])

_datasets_path = os.path.join(os.path.dirname(__file__), "..", "datasets", "cidades_brasileiras.json")
with open(_datasets_path, "r", encoding="utf-8") as f:
    _cidades_data = json.load(f)


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    from backend.api.health import check_database
    db_status = await check_database(db)
    if db_status.get("database") == "disconnected":
        return JSONResponse(status_code=503, content={"status": "error", **db_status})
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


@router.get("/ibge/uf")
async def list_ufs():
    return list(_cidades_data.keys())


@router.get("/ibge/cidades/{uf}")
async def list_cidades(uf: str):
    return list(_cidades_data.get(uf.upper(), []))


@router.get("/geocode")
async def geocode(q: str):
    """Proxy for Nominatim geocoding to avoid direct client requests."""
    global _geocode_last_request
    now = _time.monotonic()
    if now - _geocode_last_request < 1.0:
        raise HTTPException(status_code=429, detail="Rate limit: 1 request per second")
    _geocode_last_request = now

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

    cache_dir = os.path.join(get_settings().temp_dir, "cache")
    if not os.path.realpath(path).startswith(os.path.realpath(cache_dir)):
        raise HTTPException(403, "Access denied")

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

    cache_dir = os.path.join(get_settings().temp_dir, "cache")
    if not os.path.realpath(path).startswith(os.path.realpath(cache_dir)):
        raise HTTPException(403, "Access denied")

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
    from datetime import datetime as _dt
    c.drawString(50, 30, f"Gerado em: {_dt.now().strftime('%d/%m/%Y %H:%M')}")

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
    if len(req.task_ids) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 tasks per batch")
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
async def process_batch(req: ProcessBatchRequest, db: AsyncSession = Depends(get_db)):
    """Process multiple images for the same polygon and return task IDs."""
    from backend.repositories.images import get_images_by_ids
    from backend.tasks.processing import process_image_task

    images = await get_images_by_ids(db, req.image_ids)
    task_ids = []
    for img_id in req.image_ids:
        image = images.get(img_id)
        if not image:
            raise HTTPException(404, f"Image {img_id} not found")
        task = process_image_task.delay(
            image_id=img_id,
            polygon_coords=req.coordinates,
            product=req.product,
            band_urls=image.get("metadata", {}).get("assets", {}),
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
