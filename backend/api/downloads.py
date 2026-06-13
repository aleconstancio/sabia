import logging
import os
import re

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse, Response

from backend.config import get_settings
from backend.models.schemas import DownloadBatchRequest

logger = logging.getLogger(__name__)

router = APIRouter()

SAFE_FILENAME_RE = re.compile(r"^[a-zA-Z0-9_.-]+$")


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

    path = result.result.get("geotiff_path") or result.result.get("path", "")
    if not path or not os.path.exists(path):
        raise HTTPException(404, "File not found or expired.")

    cache_dir = os.path.join(get_settings().temp_dir, "cache")
    if not os.path.realpath(path).startswith(os.path.realpath(cache_dir)):
        raise HTTPException(403, "Access denied")

    filename = f"spaceeye_{task_id[:8]}.tif"
    return FileResponse(path, filename=filename, media_type="image/tiff")


@router.post("/download/batch")
async def download_batch(req: DownloadBatchRequest):
    """Download multiple processed results as a ZIP archive."""
    # TODO: Add API key authentication before production use
    if len(req.task_ids) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 tasks per batch")
    import io
    import zipfile

    from celery.result import AsyncResult

    from backend.tasks.celery_app import celery_app

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for tid in req.task_ids:
            result = AsyncResult(tid, app=celery_app)
            if result.state == "SUCCESS" and result.result:
                path = result.result.get("path", "")
                if path and os.path.exists(path):
                    name = f"{tid[:8]}.png"
                    zf.write(path, name)
                    geotiff = result.result.get("geotiff_path", "")
                    if geotiff and os.path.exists(geotiff):
                        zf.write(geotiff, f"{tid[:8]}.tif")

    if len(buffer.getvalue()) <= 30:
        raise HTTPException(status_code=404, detail="No completed tasks found")
    buffer.seek(0)
    return Response(
        content=buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=spaceeye-batch.zip"}
    )
