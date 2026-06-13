
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db, verify_api_key
from backend.services.data_fusion import fuse_region_data
from backend.utils import _summarize_soil, _summarize_weather

router = APIRouter()


class CreateProfileRequest(BaseModel):
    name: str = Field(max_length=200)
    polygon: dict
    satellite_data: dict | None = None
    notes: str | None = None


@router.post("")
async def create_profile(data: CreateProfileRequest, db: AsyncSession = Depends(get_db)):
    """Create a region profile with fused multi-source data."""
    polygon = data.polygon

    fused = await fuse_region_data(polygon["coordinates"])

    result = await db.execute(
        text("""
            INSERT INTO region_profiles (name, polygon, centroid, weather_data, soil_data, landcover_data, satellite_data, notes)
            VALUES (:name, :polygon, :centroid, :weather_data, :soil_data, :landcover_data, :satellite_data, :notes)
            RETURNING id
        """),
        {
            "name": data.name,
            "polygon": polygon,
            "centroid": fused["centroid"],
            "weather_data": fused["weather"],
            "soil_data": fused["soil"],
            "landcover_data": fused["landcover"],
            "satellite_data": data.satellite_data,
            "notes": data.notes,
        },
    )
    await db.commit()
    row = result.fetchone()
    return {"id": str(row[0])}


@router.get("")
async def list_profiles(
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    """List all region profiles."""
    result = await db.execute(
        text("SELECT * FROM region_profiles ORDER BY created_at DESC LIMIT :limit OFFSET :offset"),
        {"limit": limit, "offset": offset},
    )
    rows = result.mappings().all()
    profiles = []
    for r in rows:
        profiles.append(
            {
                "id": str(r["id"]),
                "name": r["name"],
                "polygon": r["polygon"],
                "centroid": r["centroid"],
                "weather_summary": _summarize_weather(r["weather_data"]),
                "soil_summary": _summarize_soil(r["soil_data"]),
                "landcover_summary": r["landcover_data"],
                "satellite_data": r["satellite_data"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            }
        )

    count = (await db.execute(text("SELECT COUNT(*) FROM region_profiles"))).scalar() or 0
    return {"profiles": profiles, "total": count}


@router.get("/{profile_id}")
async def get_profile(profile_id: str, db: AsyncSession = Depends(get_db)):
    """Get full profile data."""
    result = await db.execute(
        text("SELECT * FROM region_profiles WHERE id = :id"), {"id": profile_id}
    )
    row = result.mappings().fetchone()
    if not row:
        raise HTTPException(404, "Profile not found")
    return dict(row)


@router.put("/{profile_id}/refresh")
async def refresh_profile(profile_id: str, db: AsyncSession = Depends(get_db)):
    """Re-fetch all data sources for a profile."""
    result = await db.execute(
        text("SELECT polygon FROM region_profiles WHERE id = :id"), {"id": profile_id}
    )
    row = result.fetchone()
    if not row:
        raise HTTPException(404, "Profile not found")

    polygon = row[0]
    coords = polygon["coordinates"] if isinstance(polygon, dict) else polygon
    fused = await fuse_region_data(coords)

    # Map fused data keys to database column names
    column_mapping = {
        "weather": "weather_data",
        "soil": "soil_data",
        "landcover": "landcover_data",
        "centroid": "centroid",
    }
    db_params = {column_mapping.get(k, k): v for k, v in fused.items()}
    db_params["id"] = profile_id

    await db.execute(
        text("""
            UPDATE region_profiles
            SET weather_data = :weather_data, soil_data = :soil_data, landcover_data = :landcover_data,
                centroid = :centroid, updated_at = now()
            WHERE id = :id
        """),
        db_params,
    )
    await db.commit()
    return {"updated": True}


@router.delete("/{profile_id}")
async def delete_profile(
    profile_id: str,
    db: AsyncSession = Depends(get_db),
    _auth: None = Depends(verify_api_key),
):
    result = await db.execute(
        text("DELETE FROM region_profiles WHERE id = :id RETURNING id"), {"id": profile_id}
    )
    await db.commit()
    if not result.fetchone():
        raise HTTPException(404, "Profile not found")
    return {"deleted": True}



