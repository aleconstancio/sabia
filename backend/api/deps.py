import asyncio

import httpx
from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader
from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import get_settings
from backend.models.database import get_db as _get_db

_http_client: httpx.AsyncClient | None = None
_http_client_lock = asyncio.Lock()

_api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


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


async def verify_api_key(api_key: str | None = Security(_api_key_header)) -> None:
    """Verify API key if configured. Skipped when API_KEY env var is empty."""
    settings = get_settings()
    if not settings.api_key:
        return  # Auth disabled
    if not api_key or api_key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid or missing API key")
