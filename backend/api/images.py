from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db
from backend.models.schemas import PolygonRequest

router = APIRouter()


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


@router.post("/images/timeline")
async def image_timeline(req: PolygonRequest, db: AsyncSession = Depends(get_db)):
    """Get available image dates for a polygon, sorted chronologically."""
    from backend.repositories.images import find_images_by_polygon

    images, total = await find_images_by_polygon(
        db, req.coordinates, req.collections,
        date_from=req.date_from, date_to=req.date_to,
        max_cloud=req.max_cloud, sort_by=req.sort_by,
        sort_order=req.sort_order, limit=100, offset=0
    )
    timeline = []
    for img in images:
        timeline.append({
            "id": img["id"],
            "date": img["acquired_at"],
            "cloud_cover": img["cloud_cover"],
            "thumbnail_url": img["thumbnail_url"],
        })
    return {"timeline": timeline, "total": total}
