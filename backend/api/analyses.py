import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


class CreateAnalysisRequest(BaseModel):
    image_id: str
    collection: str
    product: str
    polygon: list[list[list[float]]]
    statistics: dict | None = None
    overlay_path: str | None = None
    weather: dict | None = None
    centroid: dict | None = None


@router.post("")
async def create_analysis(data: CreateAnalysisRequest, db: AsyncSession = Depends(get_db)):
    """Save a completed analysis record."""
    result = await db.execute(
        text("""
            INSERT INTO analyses (image_id, collection, product, polygon, statistics, overlay_path, weather, centroid)
            VALUES (:image_id, :collection, :product, :polygon, :statistics, :overlay_path, :weather, :centroid)
            ON CONFLICT (image_id, product, (polygon::text)) DO NOTHING
            RETURNING id
        """),
        {
            "image_id": data.image_id,
            "collection": data.collection,
            "product": data.product,
            "polygon": data.polygon,
            "statistics": json.dumps(data.statistics)
            if isinstance(data.statistics, dict)
            else data.statistics,
            "overlay_path": data.overlay_path,
            "weather": json.dumps(data.weather)
            if isinstance(data.weather, dict)
            else data.weather,
            "centroid": data.centroid,
        },
    )
    await db.commit()
    row = result.fetchone()
    return {"id": str(row[0])}


@router.get("")
async def list_analyses(
    product: str = None,
    collection: str = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List saved analyses with optional filters."""
    conditions = []
    params = {"limit": limit, "offset": offset}
    if product:
        conditions.append("product = :product")
        params["product"] = product
    if collection:
        conditions.append("collection = :collection")
        params["collection"] = collection

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    # SECURITY NOTE: The `where` clause is built from fixed column names
    # (product, collection) validated above — not user-supplied free text.
    # All dynamic values use named parameters (:product, :collection) via
    # the `params` dict, so there is no SQL injection vector here.
    result = await db.execute(
        text(
            f"SELECT * FROM analyses {where} ORDER BY created_at DESC LIMIT :limit OFFSET :offset"
        ),
        params,
    )
    rows = result.mappings().all()
    analyses = []
    for r in rows:
        analyses.append(
            {
                "id": str(r["id"]),
                "image_id": r["image_id"],
                "collection": r["collection"],
                "product": r["product"],
                "polygon": r["polygon"],
                "centroid": r.get("centroid"),
                "statistics": r["statistics"],
                "acquired_at": r["acquired_at"].isoformat() if r.get("acquired_at") else None,
                "cloud_cover": r.get("cloud_cover"),
                "created_at": r["created_at"].isoformat() if r.get("created_at") else None,
            }
        )

    count_result = await db.execute(text(f"SELECT COUNT(*) FROM analyses {where}"), params)
    total = count_result.scalar() or 0

    return {"analyses": analyses, "total": total}


@router.delete("/{analysis_id}")
async def delete_analysis(analysis_id: str, db: AsyncSession = Depends(get_db)):
    """Delete a saved analysis."""
    result = await db.execute(
        text("DELETE FROM analyses WHERE id = :id RETURNING id"),
        {"id": analysis_id},
    )
    await db.commit()
    if not result.fetchone():
        raise HTTPException(404, "Analysis not found")
    return {"deleted": True}
