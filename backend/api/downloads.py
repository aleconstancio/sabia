import io
import logging
import os
import re
import zipfile

from celery.result import AsyncResult
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, Response

from backend.api.auth import verify_api_key
from backend.config import get_settings
from backend.models.schemas import DownloadBatchRequest
from backend.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)

router = APIRouter()

SAFE_FILENAME_RE = re.compile(r"^[a-zA-Z0-9_.-]+$")


def _validate_path_in_cache(path: str, cache_dir: str) -> None:
    """Raise HTTPException if path is outside the cache directory."""
    if not os.path.realpath(path).startswith(os.path.realpath(cache_dir)):
        raise HTTPException(status_code=403, detail="Access denied")


def _get_task_result(task_id: str) -> dict:
    """Get Celery task result or raise 404."""
    result = AsyncResult(task_id, app=celery_app)
    if result.state != "SUCCESS" or not result.result:
        raise HTTPException(status_code=404, detail="Result not found. Task may still be running.")
    return result.result


def _download_file(task_id: str, path_key: str, extension: str, media_type: str) -> FileResponse:
    """Shared helper for file download endpoints."""
    result = _get_task_result(task_id)
    path = result.get(path_key) or result.get("path", "")
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found or expired.")
    cache_dir = os.path.join(get_settings().temp_dir, "cache")
    _validate_path_in_cache(path, cache_dir)
    filename = f"spaceeye_{task_id[:8]}.{extension}"
    return FileResponse(path, filename=filename, media_type=media_type)


@router.get("/overlay/{filename}")
async def serve_overlay(filename: str):
    """Serve a processed overlay image."""
    if not SAFE_FILENAME_RE.match(filename):
        raise HTTPException(status_code=400, detail="Invalid filename")
    settings = get_settings()
    cache_dir = os.path.join(settings.temp_dir, "cache")
    path = os.path.join(cache_dir, filename)
    _validate_path_in_cache(path, cache_dir)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path, media_type="image/png")


@router.get("/download/{task_id}")
async def download_raster(task_id: str):
    """Download the processed PNG for a completed task."""
    return _download_file(task_id, "path", "png", "image/png")


@router.get("/download/{task_id}/geotiff")
async def download_geotiff(task_id: str):
    """Download the processed GeoTIFF (full resolution, with CRS)."""
    return _download_file(task_id, "geotiff_path", "tif", "image/tiff")


@router.post("/download/batch")
async def download_batch(
    req: DownloadBatchRequest,
    _auth: None = Depends(verify_api_key),
):
    """Download multiple processed results as a ZIP archive."""
    if len(req.task_ids) > 5:
        raise HTTPException(status_code=400, detail="Maximum 5 tasks per batch")

    cache_dir = os.path.join(get_settings().temp_dir, "cache")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zf:
        for tid in req.task_ids:
            result = AsyncResult(tid, app=celery_app)
            if result.state == "SUCCESS" and result.result:
                path = result.result.get("path", "")
                if path and os.path.exists(path):
                    _validate_path_in_cache(path, cache_dir)
                    zf.write(path, f"{tid[:8]}.png")
                    geotiff = result.result.get("geotiff_path", "")
                    if geotiff and os.path.exists(geotiff):
                        _validate_path_in_cache(geotiff, cache_dir)
                        zf.write(geotiff, f"{tid[:8]}.tif")

    if len(buffer.getvalue()) <= 30:
        raise HTTPException(status_code=404, detail="No completed tasks found")
    buffer.seek(0)
    return Response(
        content=buffer.getvalue(),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=spaceeye-batch.zip"},
    )
