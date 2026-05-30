import json

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional


async def find_images_by_polygon(
    db: AsyncSession,
    polygon_coords: list[list[list[float]]],
    collections: Optional[list[str]] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    max_cloud: Optional[float] = None,
    sort_by: str = "acquired_at",
    sort_order: str = "desc",
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict], int]:
    geojson_str = json.dumps({"type": "Polygon", "coordinates": polygon_coords})

    conditions = "ST_Intersects(footprint, ST_SetSRID(ST_GeomFromGeoJSON(:geom), 4326))"
    params = {"geom": geojson_str, "limit": limit, "offset": offset}

    if collections:
        placeholders = [f":col_{i}" for i in range(len(collections))]
        conditions += f" AND collection IN ({','.join(placeholders)})"
        for i, c in enumerate(collections):
            params[f"col_{i}"] = c

    if date_from:
        conditions += " AND acquired_at >= :date_from"
        params["date_from"] = date_from
    if date_to:
        conditions += " AND acquired_at <= :date_to"
        params["date_to"] = date_to
    if max_cloud is not None:
        conditions += " AND (cloud_cover IS NULL OR cloud_cover <= :max_cloud)"
        params["max_cloud"] = max_cloud

    order = "DESC" if sort_order == "desc" else "ASC"
    sort_col = "cloud_cover" if sort_by == "cloud_cover" else "acquired_at"

    count_query = text(f"SELECT COUNT(*) FROM images WHERE {conditions}")
    total = (await db.execute(count_query, params)).scalar()

    data_query = text(f"""
        SELECT id, collection, ST_AsGeoJSON(footprint) as footprint_json,
               cloud_cover, acquired_at, thumbnail_url
        FROM images WHERE {conditions}
        ORDER BY {sort_col} {order}
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
