import json
import logging
import os
import time as _time

from fastapi import APIRouter, HTTPException

from backend.api.deps import get_http_client

logger = logging.getLogger(__name__)

router = APIRouter()

_geocode_last_request: float = 0.0

_datasets_path = os.path.join(os.path.dirname(__file__), "..", "datasets", "cidades_brasileiras.json")
try:
    with open(_datasets_path, encoding="utf-8") as f:
        _cidades_data = json.load(f)
except Exception:
    logger.warning("Failed to load %s, using empty dataset", _datasets_path)
    _cidades_data = {}


@router.get("/ibge/uf")
async def list_ufs():
    return list(_cidades_data.keys())


@router.get("/ibge/cidades/{uf}")
async def list_cidades(uf: str):
    return list(_cidades_data.get(uf.upper(), []))


@router.get("/geocode")
async def geocode(q: str):
    """Proxy for Nominatim geocoding to avoid direct client requests."""
    global _geocode_last_request
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Query parameter 'q' must not be empty")
    if len(q) > 200:
        raise HTTPException(status_code=400, detail="Query parameter 'q' must not exceed 200 characters")
    now = _time.monotonic()
    if now - _geocode_last_request < 1.0:
        raise HTTPException(status_code=429, detail="Rate limit: 1 request per second")
    _geocode_last_request = now

    client = await get_http_client()
    resp = await client.get(
        "https://nominatim.openstreetmap.org/search",
        params={"format": "json", "q": q, "limit": 1},
        headers={"User-Agent": "SpaceEye/0.2.0"},
    )
    return resp.json()
