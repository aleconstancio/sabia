import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db, verify_api_key
from backend.models.schemas import (
    ComputeDifferenceRequest,
    ProcessBatchRequest,
    ProcessRequest,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/process")
async def process_image_endpoint(
    req: ProcessRequest,
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
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


@router.post("/process/batch")
async def process_batch(
    req: ProcessBatchRequest,
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
):
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
async def compute_difference(
    req: ComputeDifferenceRequest,
    _auth: None = Depends(verify_api_key),
):
    """Compute NDVI difference between two processed images."""
    from backend.tasks.processing import compute_difference_task

    task = compute_difference_task.delay(
        task_id_a=req.task_id_a,
        task_id_b=req.task_id_b,
    )
    return {"task_id": task.id}
