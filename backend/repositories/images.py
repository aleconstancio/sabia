import json

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional


async def find_images_by_polygon(
    db: AsyncSession,
    polygon_coords: list[list[list[float]]],
    collections: Optional[list[str]] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict], int]:
    geojson_str = str({"type": "Polygon", "coordinates": polygon_coords})

    conditions = "ST_Intersects(footprint, ST_SetSRID(ST_GeomFromGeoJSON(:geom), 4326))"
    params = {"geom": geojson_str, "limit": limit, "offset": offset}

    if collections:
        placeholders = [f":col_{i}" for i in range(len(collections))]
        conditions += f" AND collection IN ({','.join(placeholders)})"
        for i, c in enumerate(collections):
            params[f"col_{i}"] = c

    count_query = text(f"SELECT COUNT(*) FROM images WHERE {conditions}")
    total = (await db.execute(count_query, params)).scalar()

    data_query = text(f"""
        SELECT id, collection, ST_AsGeoJSON(footprint) as footprint_json, 
               cloud_cover, acquired_at, thumbnail_url
        FROM images WHERE {conditions}
        ORDER BY acquired_at DESC
        LIMIT :limit OFFSET :offset
    """)
    rows = (await db.execute(data_query, params)).fetchall()

    images = []
    for row in rows:
        images.append({
            "id": row.id,
            "collection": row.collection,
            "footprint": json.loads(row.footprint_json),
            "cloud_cover": row.cloud_cover,
            "acquired_at": row.acquired_at.isoformat() if row.acquired_at else None,
            "thumbnail_url": row.thumbnail_url,
        })

    return images, total


async def get_image_by_id(db: AsyncSession, image_id: str) -> Optional[dict]:
    query = text("""
        SELECT id, collection, ST_AsGeoJSON(footprint) as footprint_json,
               cloud_cover, acquired_at, thumbnail_url, metadata
        FROM images WHERE id = :id
    """)
    row = (await db.execute(query, {"id": image_id})).fetchone()
    if not row:
        return None
    return {
        "id": row.id,
        "collection": row.collection,
        "footprint": json.loads(row.footprint_json),
        "cloud_cover": row.cloud_cover,
        "acquired_at": row.acquired_at.isoformat() if row.acquired_at else None,
        "thumbnail_url": row.thumbnail_url,
        "metadata": row.metadata if hasattr(row, 'metadata') else {},
    }
