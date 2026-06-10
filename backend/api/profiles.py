from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db
from backend.services.data_fusion import fuse_region_data

router = APIRouter()


@router.post("")
async def create_profile(data: dict, db: AsyncSession = Depends(get_db)):
    """Create a region profile with fused multi-source data."""
    polygon = data.get("polygon")
    if not polygon:
        raise HTTPException(422, "polygon is required")

    fused = await fuse_region_data(polygon["coordinates"])

    result = await db.execute(
        text("""
            INSERT INTO region_profiles (name, polygon, centroid, weather_data, soil_data, landcover_data, satellite_data, notes)
            VALUES (:name, :polygon, :centroid, :weather, :soil, :landcover, :satellite, :notes)
            RETURNING id
        """),
        {
            "name": data.get("name"),
            "polygon": polygon,
            "centroid": fused["centroid"],
            "weather": fused["weather"],
            "soil": fused["soil"],
            "landcover": fused["landcover"],
            "satellite": data.get("satellite_data"),
            "notes": data.get("notes"),
        },
    )
    await db.commit()
    row = result.fetchone()
    return {"id": str(row[0])}


@router.get("")
async def list_profiles(
    limit: int = 50,
    offset: int = 0,
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

    await db.execute(
        text("""
            UPDATE region_profiles
            SET weather_data = :weather, soil_data = :soil, landcover_data = :landcover,
                centroid = :centroid, updated_at = now()
            WHERE id = :id
        """),
        {"id": profile_id, **fused},
    )
    await db.commit()
    return {"updated": True}


@router.delete("/{profile_id}")
async def delete_profile(profile_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        text("DELETE FROM region_profiles WHERE id = :id RETURNING id"), {"id": profile_id}
    )
    await db.commit()
    if not result.fetchone():
        raise HTTPException(404, "Profile not found")
    return {"deleted": True}


def _summarize_weather(data: dict) -> dict | None:
    if not data:
        return None
    current = data.get("current", {})
    return {
        "temperature": current.get("temperature_2m"),
        "humidity": current.get("relative_humidity_2m"),
        "precipitation": current.get("precipitation"),
        "weather_code": current.get("weather_code"),
    }


def _summarize_soil(data: dict) -> dict | None:
    if not data:
        return None
    layers = data.get("properties", {}).get("layers", [])
    summary = {}
    for layer in layers:
        name = layer.get("name")
        if name and layer.get("depths"):
            summary[name] = layer["depths"][0].get("values", {}).get("mean")
    return summary
