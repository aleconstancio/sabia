"""API dependencies — database sessions and auth."""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.infra.http_client import close_http_client, get_http_client  # noqa: F401
from backend.models.database import get_db as _get_db


async def get_db() -> AsyncSession:
    async for session in _get_db():
        yield session
