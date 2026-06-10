from sqlalchemy.ext.asyncio import AsyncSession
from backend.models.database import get_db as _get_db
import httpx

_http_client: httpx.AsyncClient | None = None


async def get_db() -> AsyncSession:
    async for session in _get_db():
        yield session


async def get_http_client() -> httpx.AsyncClient:
    global _http_client
    if _http_client is None or _http_client.is_closed:
        _http_client = httpx.AsyncClient(timeout=30.0)
    return _http_client
