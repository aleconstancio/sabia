from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.database import get_db as _get_db


async def get_db() -> AsyncSession:
    async for session in _get_db():
        yield session
