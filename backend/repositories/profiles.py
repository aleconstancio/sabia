from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def create_profile(
    db: AsyncSession,
    name: str | None,
    polygon: dict,
    centroid: dict | None,
    weather_summary: dict | None,
    soil_summary: dict | None,
    landcover_summary: dict | None,
    satellite_data: dict | None,
    notes: str | None = None,
) -> str | None:
    result = await db.execute(
        text("""
            INSERT INTO region_profiles (name, polygon, centroid, weather_data, soil_data, landcover_data, satellite_data, notes)
            VALUES (:name, :polygon, :centroid, :weather_data, :soil_data, :landcover_data, :satellite_data, :notes)
            RETURNING id
        """),
        {
            "name": name,
            "polygon": polygon,
            "centroid": centroid,
            "weather_data": weather_summary,
            "soil_data": soil_summary,
            "landcover_data": landcover_summary,
            "satellite_data": satellite_data,
            "notes": notes,
        },
    )
    await db.commit()
    row = result.fetchone()
    return str(row[0]) if row else None


async def list_profiles(
    db: AsyncSession,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict], int]:
    result = await db.execute(
        text("SELECT * FROM region_profiles ORDER BY created_at DESC LIMIT :limit OFFSET :offset"),
        {"limit": limit, "offset": offset},
    )
    rows = result.mappings().all()
    count = (await db.execute(text("SELECT COUNT(*) FROM region_profiles"))).scalar() or 0

    profiles = []
    for r in rows:
        profiles.append(
            {
                "id": str(r["id"]),
                "name": r["name"],
                "polygon": r["polygon"],
                "centroid": r["centroid"],
                "weather_summary": r["weather_data"],
                "soil_summary": r["soil_data"],
                "landcover_summary": r["landcover_data"],
                "satellite_data": r["satellite_data"],
                "created_at": r["created_at"].isoformat() if r["created_at"] else None,
            }
        )

    return profiles, count


async def get_profile(db: AsyncSession, profile_id: str) -> dict | None:
    result = await db.execute(
        text("SELECT * FROM region_profiles WHERE id = :id"), {"id": profile_id}
    )
    row = result.mappings().fetchone()
    if not row:
        return None
    return dict(row)


async def get_profile_polygon(db: AsyncSession, profile_id: str) -> dict | None:
    result = await db.execute(
        text("SELECT polygon FROM region_profiles WHERE id = :id"), {"id": profile_id}
    )
    row = result.fetchone()
    if not row:
        return None
    polygon: dict = row[0]
    return polygon


async def refresh_profile(
    db: AsyncSession,
    profile_id: str,
    centroid: dict,
    weather_summary: dict,
    soil_summary: dict,
    landcover_summary: dict,
) -> None:
    await db.execute(
        text("""
            UPDATE region_profiles
            SET weather_data = :weather_data, soil_data = :soil_data, landcover_data = :landcover_data,
                centroid = :centroid, updated_at = now()
            WHERE id = :id
        """),
        {
            "weather_data": weather_summary,
            "soil_data": soil_summary,
            "landcover_data": landcover_summary,
            "centroid": centroid,
            "id": profile_id,
        },
    )
    await db.commit()


async def delete_profile(db: AsyncSession, profile_id: str) -> bool:
    result = await db.execute(
        text("DELETE FROM region_profiles WHERE id = :id RETURNING id"), {"id": profile_id}
    )
    await db.commit()
    return result.fetchone() is not None
