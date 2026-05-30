import json

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional


async def _has_postgis(db: AsyncSession) -> bool:
    """Check if the PostGIS column 'footprint' exists."""
    try:
        row = await db.execute(
            text("SELECT 1 FROM pg_extension WHERE extname = 'postgis'")
        )
        return row.scalar() is not None
    except Exception:
        return False


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
    has_gis = await _has_postgis(db)
    geojson_str = json.dumps({"type": "Polygon", "coordinates": polygon_coords})

    # Build WHERE conditions (same for both modes)
    conditions = []
    params: dict = {}

    if has_gis:
        conditions.append(
            "ST_Intersects(footprint, ST_SetSRID(ST_GeomFromGeoJSON(:geom), 4326))"
        )
        params["geom"] = geojson_str
    # Non-PostGIS fallback: no spatial filter — return all images

    if collections:
        placeholders = [f":col_{i}" for i in range(len(collections))]
        conditions.append(f"collection IN ({','.join(placeholders)})")
        for i, c in enumerate(collections):
            params[f"col_{i}"] = c

    if date_from:
        conditions.append("acquired_at >= :date_from")
        params["date_from"] = date_from
    if date_to:
        conditions.append("acquired_at <= :date_to")
        params["date_to"] = date_to
    if max_cloud is not None:
        conditions.append("(cloud_cover IS NULL OR cloud_cover <= :max_cloud)")
        params["max_cloud"] = max_cloud

    where_clause = " AND ".join(conditions) if conditions else "TRUE"
    order = "DESC" if sort_order == "desc" else "ASC"
    sort_col = "cloud_cover" if sort_by == "cloud_cover" else "acquired_at"

    count_query = text(f"SELECT COUNT(*) FROM images WHERE {where_clause}")
    total = (await db.execute(count_query, params)).scalar() or 0

    if has_gis:
        select_cols = "id, collection, ST_AsGeoJSON(footprint) as footprint_json, cloud_cover, acquired_at, thumbnail_url"
    else:
        select_cols = "id, collection, footprint_geojson as footprint_json, cloud_cover, acquired_at, thumbnail_url"

    data_query = text(f"""
        SELECT {select_cols}
        FROM images WHERE {where_clause}
        ORDER BY {sort_col} {order}
        LIMIT :limit OFFSET :offset
    """)
    params["limit"] = limit
    params["offset"] = offset
    rows = (await db.execute(data_query, params)).fetchall()

    images = []
    for row in rows:
        fp = row.footprint_json
        if isinstance(fp, str):
            try:
                fp = json.loads(fp)
            except (json.JSONDecodeError, TypeError):
                fp = None
        elif hasattr(fp, '__str__'):
            try:
                fp = json.loads(str(fp))
            except (json.JSONDecodeError, TypeError):
                fp = None

        images.append({
            "id": row.id,
            "collection": row.collection,
            "footprint": fp,
            "cloud_cover": row.cloud_cover,
            "acquired_at": row.acquired_at.isoformat() if row.acquired_at else None,
            "thumbnail_url": row.thumbnail_url,
        })

    return images, total


async def get_image_by_id(db: AsyncSession, image_id: str) -> Optional[dict]:
    has_gis = await _has_postgis(db)
    if has_gis:
        select_cols = "id, collection, ST_AsGeoJSON(footprint) as footprint_json, cloud_cover, acquired_at, thumbnail_url, metadata"
    else:
        select_cols = "id, collection, footprint_geojson as footprint_json, cloud_cover, acquired_at, thumbnail_url, metadata"

    query = text(f"SELECT {select_cols} FROM images WHERE id = :id")
    row = (await db.execute(query, {"id": image_id})).fetchone()
    if not row:
        return None

    fp = row.footprint_json
    if isinstance(fp, str):
        try:
            fp = json.loads(fp)
        except (json.JSONDecodeError, TypeError):
            fp = None

    return {
        "id": row.id,
        "collection": row.collection,
        "footprint": fp,
        "cloud_cover": row.cloud_cover,
        "acquired_at": row.acquired_at.isoformat() if row.acquired_at else None,
        "thumbnail_url": row.thumbnail_url,
        "metadata": row.metadata if hasattr(row, 'metadata') else {},
    }
