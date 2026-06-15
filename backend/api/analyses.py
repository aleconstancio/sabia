import json

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.auth import verify_api_key
from backend.api.deps import get_db
from backend.repositories.analyses import (
    create_analysis,
    delete_analysis,
    list_analyses,
)

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
async def create_analysis_endpoint(data: CreateAnalysisRequest, db: AsyncSession = Depends(get_db)):
    """Save a completed analysis record."""
    statistics = (
        json.dumps(data.statistics) if isinstance(data.statistics, dict) else data.statistics
    )
    weather = json.dumps(data.weather) if isinstance(data.weather, dict) else data.weather

    analysis_id = await create_analysis(
        db,
        image_id=data.image_id,
        collection=data.collection,
        product=data.product,
        polygon=data.polygon,
        statistics=statistics,
        overlay_path=data.overlay_path,
        weather=weather,
        centroid=data.centroid,
    )
    if not analysis_id:
        raise HTTPException(409, "Analysis already exists")
    return {"id": analysis_id}


@router.get("")
async def list_analyses_endpoint(
    product: str | None = None,
    collection: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List saved analyses with optional filters."""
    analyses, total = await list_analyses(
        db, product=product, collection=collection, limit=limit, offset=offset
    )
    return {"analyses": analyses, "total": total}


@router.delete("/{analysis_id}")
async def delete_analysis_endpoint(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
):
    """Delete a saved analysis."""
    deleted = await delete_analysis(db, analysis_id)
    if not deleted:
        raise HTTPException(404, "Analysis not found")
    return {"deleted": True}
