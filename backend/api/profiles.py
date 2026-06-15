from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.auth import verify_api_key
from backend.api.deps import get_db
from backend.repositories.profiles import (
    create_profile,
    delete_profile,
    get_profile,
    get_profile_polygon,
    list_profiles,
    refresh_profile,
)
from backend.services.data_fusion import fuse_region_data
from backend.utils import summarize_soil, summarize_weather

router = APIRouter()


class CreateProfileRequest(BaseModel):
    name: str = Field(max_length=200)
    polygon: dict
    satellite_data: dict | None = None
    notes: str | None = None


@router.post("")
async def create_profile_endpoint(data: CreateProfileRequest, db: AsyncSession = Depends(get_db)):
    """Create a region profile with fused multi-source data."""
    polygon = data.polygon
    fused = await fuse_region_data(polygon["coordinates"])

    profile_id = await create_profile(
        db,
        name=data.name,
        polygon=polygon,
        centroid=fused["centroid"],
        weather_summary=fused["weather"],
        soil_summary=fused["soil"],
        landcover_summary=fused["landcover"],
        satellite_data=data.satellite_data,
        notes=data.notes,
    )
    return {"id": profile_id}


@router.get("")
async def list_profiles_endpoint(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List all region profiles."""
    raw_profiles, total = await list_profiles(db, limit=limit, offset=offset)
    profiles = []
    for r in raw_profiles:
        profiles.append(
            {
                "id": r["id"],
                "name": r["name"],
                "polygon": r["polygon"],
                "centroid": r["centroid"],
                "weather_summary": summarize_weather(r["weather_summary"]),
                "soil_summary": summarize_soil(r["soil_summary"]),
                "landcover_summary": r["landcover_summary"],
                "satellite_data": r["satellite_data"],
                "created_at": r["created_at"],
            }
        )
    return {"profiles": profiles, "total": total}


@router.get("/{profile_id}")
async def get_profile_endpoint(profile_id: str, db: AsyncSession = Depends(get_db)):
    """Get full profile data."""
    profile = await get_profile(db, profile_id)
    if not profile:
        raise HTTPException(404, "Profile not found")
    return profile


@router.put("/{profile_id}/refresh")
async def refresh_profile_endpoint(profile_id: str, db: AsyncSession = Depends(get_db)):
    """Re-fetch all data sources for a profile."""
    polygon = await get_profile_polygon(db, profile_id)
    if not polygon:
        raise HTTPException(404, "Profile not found")

    coords = polygon["coordinates"] if isinstance(polygon, dict) else polygon
    fused = await fuse_region_data(coords)

    column_mapping = {
        "weather": "weather_data",
        "soil": "soil_data",
        "landcover": "landcover_data",
        "centroid": "centroid",
    }
    db_params = {column_mapping.get(k, k): v for k, v in fused.items()}

    await refresh_profile(
        db,
        profile_id=profile_id,
        centroid=db_params["centroid"],
        weather_summary=db_params["weather_data"],
        soil_summary=db_params["soil_data"],
        landcover_summary=db_params["landcover_data"],
    )
    return {"updated": True}


@router.delete("/{profile_id}")
async def delete_profile_endpoint(
    profile_id: str,
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
):
    deleted = await delete_profile(db, profile_id)
    if not deleted:
        raise HTTPException(404, "Profile not found")
    return {"deleted": True}
