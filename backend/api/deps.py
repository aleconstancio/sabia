import asyncio

import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from backend.models.database import get_db as _get_db

_http_client: httpx.AsyncClient | None = None
_http_client_lock = asyncio.Lock()


async def get_db() -> AsyncSession:
    async for session in _get_db():
        yield session


async def get_http_client() -> httpx.AsyncClient:
    global _http_client
    async with _http_client_lock:
        if _http_client is None or _http_client.is_closed:
            _http_client = httpx.AsyncClient(timeout=30.0)
        return _http_client


async def close_http_client() -> None:
    global _http_client
    async with _http_client_lock:
        if _http_client is not None and not _http_client.is_closed:
            await _http_client.aclose()
        _http_client = None
