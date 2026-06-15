from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


async def create_analysis(
    db: AsyncSession,
    image_id: str,
    collection: str,
    product: str,
    polygon: list[list[list[float]]],
    statistics: str | None,
    overlay_path: str | None,
    weather: str | None,
    centroid: dict | None,
) -> str | None:
    result = await db.execute(
        text("""
            INSERT INTO analyses (image_id, collection, product, polygon, statistics, overlay_path, weather, centroid)
            VALUES (:image_id, :collection, :product, :polygon, :statistics, :overlay_path, :weather, :centroid)
            ON CONFLICT (image_id, product, (polygon::text)) DO NOTHING
            RETURNING id
        """),
        {
            "image_id": image_id,
            "collection": collection,
            "product": product,
            "polygon": polygon,
            "statistics": statistics,
            "overlay_path": overlay_path,
            "weather": weather,
            "centroid": centroid,
        },
    )
    await db.commit()
    row = result.fetchone()
    return str(row[0]) if row else None


async def list_analyses(
    db: AsyncSession,
    product: str | None = None,
    collection: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[dict], int]:
    conditions = []
    params: dict = {"limit": limit, "offset": offset}
    if product:
        conditions.append("product = :product")
        params["product"] = product
    if collection:
        conditions.append("collection = :collection")
        params["collection"] = collection

    where = f"WHERE {' AND '.join(conditions)}" if conditions else ""

    # SECURITY NOTE: The `where` clause is built from fixed column names
    # (product, collection) validated above — not user-supplied free text.
    # All dynamic values use named parameters (:product, :collection) via
    # the `params` dict, so there is no SQL injection vector here.
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
                "centroid": r.get("centroid"),
                "statistics": r["statistics"],
                "acquired_at": r["acquired_at"].isoformat() if r.get("acquired_at") else None,
                "cloud_cover": r.get("cloud_cover"),
                "created_at": r["created_at"].isoformat() if r.get("created_at") else None,
            }
        )

    count_result = await db.execute(text(f"SELECT COUNT(*) FROM analyses {where}"), params)
    total = count_result.scalar() or 0

    return analyses, total


async def delete_analysis(db: AsyncSession, analysis_id: str) -> bool:
    result = await db.execute(
        text("DELETE FROM analyses WHERE id = :id RETURNING id"),
        {"id": analysis_id},
    )
    await db.commit()
    return result.fetchone() is not None
