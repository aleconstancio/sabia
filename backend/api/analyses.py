import json
import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("")
async def create_analysis(data: dict, db: AsyncSession = Depends(get_db)):
    """Save a completed analysis record."""
    required = ["image_id", "collection", "product", "polygon"]
    missing = [f for f in required if f not in data]
    if missing:
        raise HTTPException(422, f"Missing fields: {', '.join(missing)}")

    result = await db.execute(
        text("""
            INSERT INTO analyses (image_id, collection, product, polygon, centroid, statistics, overlay_path, acquired_at, cloud_cover, weather)
            VALUES (:image_id, :collection, :product, :polygon, :centroid, :statistics, :overlay_path, :acquired_at, :cloud_cover, :weather)
            RETURNING id
        """),
        {
            "image_id": data["image_id"],
            "collection": data["collection"],
            "product": data["product"],
            "polygon": json.dumps(data["polygon"])
            if isinstance(data["polygon"], dict)
            else data["polygon"],
            "centroid": json.dumps(data["centroid"])
            if isinstance(data.get("centroid"), dict)
            else data.get("centroid"),
            "statistics": json.dumps(data["statistics"])
            if isinstance(data.get("statistics"), dict)
            else data.get("statistics"),
            "overlay_path": data.get("overlay_path"),
            "acquired_at": data.get("acquired_at"),
            "cloud_cover": data.get("cloud_cover"),
            "weather": json.dumps(data["weather"])
            if isinstance(data.get("weather"), dict)
            else data.get("weather"),
        },
    )
    await db.commit()
    row = result.fetchone()
    return {"id": str(row[0])}


@router.get("")
async def list_analyses(
    product: str = None,
    collection: str = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List saved analyses with optional filters."""
    limit = min(limit, 200)
    conditions = []
    params = {"limit": limit, "offset": offset}
    if product:
        conditions.append("product = :product")
        params["product"] = product
    if collection:
        conditions.append("collection = :collection")
        params["collection"] = collection

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

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
                "centroid": r["centroid"],
                "statistics": r["statistics"],
                "acquired_at": r["acquired_at"].isoformat() if r["acquired_at"] else None,
                "cloud_cover": r["cloud_cover"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
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
