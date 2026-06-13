import logging

from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)


async def check_database(db: AsyncSession) -> dict:
    try:
        result = await db.execute(text("SELECT COUNT(*) FROM images"))
        count = result.scalar() or 0
        return {"database": "connected", "catalog_count": count}
    except SQLAlchemyError as e:
        logger.warning("Health check DB failure: %s", e)
        return {"database": "disconnected", "catalog_count": 0}
