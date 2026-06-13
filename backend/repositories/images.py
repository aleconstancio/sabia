import json
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


def _sanitize_url(url: str) -> str:
    """Remove the `email` query parameter from a URL to prevent token leakage."""
    parsed = urlparse(url)
    if not parsed.query:
        return url
    params = parse_qs(parsed.query, keep_blank_values=True)
    params.pop("email", None)
    sanitized_query = urlencode(params, doseq=True) if params else ""
    return urlunparse(parsed._replace(query=sanitized_query))


def _sanitize_metadata(metadata: dict) -> dict:
    """Recursively strip email tokens from asset URLs in metadata."""
    if not metadata:
        return metadata
    sanitized = dict(metadata)
    assets = sanitized.get("assets")
    if isinstance(assets, dict):
        sanitized["assets"] = {
            k: _sanitize_url(v) if isinstance(v, str) else v
            for k, v in assets.items()
        }
    return sanitized


async def find_images_by_polygon(
    db: AsyncSession,
    polygon_coords: list[list[list[float]]],
    collections: list[str] | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    max_cloud: float | None = None,
    sort_by: str = "acquired_at",
    sort_order: str = "desc",
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict], int]:
    geojson_str = json.dumps({"type": "Polygon", "coordinates": polygon_coords})

    conditions = []
    params: dict = {}

    conditions.append(
        "ST_Intersects(footprint, ST_SetSRID(ST_GeomFromGeoJSON(:geom), 4326))"
    )
    params["geom"] = geojson_str

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

    select_cols = "id, collection, ST_AsGeoJSON(footprint) as footprint_json, cloud_cover, acquired_at, thumbnail_url"
    # Removed: PostGIS is required
    # select_cols = "id, collection, footprint_geojson as footprint_json, cloud_cover, acquired_at, thumbnail_url"

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


async def get_images_by_ids(db: AsyncSession, image_ids: list[str]) -> dict[str, dict]:
    """Fetch multiple images by IDs in a single query."""
    if not image_ids:
        return {}
    placeholders = [f":id_{i}" for i in range(len(image_ids))]
    params = {f"id_{i}": img_id for i, img_id in enumerate(image_ids)}

    query = text(f"""
        SELECT id, jsonb_build_object(
            'assets', metadata->'assets'
        ) as metadata
        FROM images
        WHERE id IN ({','.join(placeholders)})
    """)
    result = await db.execute(query, params)
    return {row[0]: _sanitize_metadata(row[1]) for row in result.fetchall()}


async def get_image_by_id(db: AsyncSession, image_id: str) -> dict | None:
    select_cols = "id, collection, ST_AsGeoJSON(footprint) as footprint_json, cloud_cover, acquired_at, thumbnail_url, metadata"
    # Removed: PostGIS is required
    # select_cols = "id, collection, footprint_geojson as footprint_json, cloud_cover, acquired_at, thumbnail_url, metadata"

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

    metadata = row.metadata if hasattr(row, 'metadata') else {}
    return {
        "id": row.id,
        "collection": row.collection,
        "footprint": fp,
        "cloud_cover": row.cloud_cover,
        "acquired_at": row.acquired_at.isoformat() if row.acquired_at else None,
        "thumbnail_url": row.thumbnail_url,
        "metadata": _sanitize_metadata(metadata),
    }
