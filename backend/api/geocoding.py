import asyncio
import json
import logging
import os
import time as _time

from fastapi import APIRouter, HTTPException

from backend.api.deps import get_http_client

logger = logging.getLogger(__name__)

router = APIRouter()

_geocode_last_request: float = 0.0


def _check_rate_limit():
    global _geocode_last_request
    now = _time.monotonic()
    if now - _geocode_last_request < 1.0:
        raise HTTPException(status_code=429, detail="Rate limit: 1 request per second")
    _geocode_last_request = now

_cidades_data: dict = {}
_cidades_loaded = False


def _load_cidades_sync():
    global _cidades_data, _cidades_loaded
    if _cidades_loaded:
        return
    _cidades_loaded = True
    datasets_path = os.path.join(
        os.path.dirname(__file__), "..", "datasets", "cidades_brasileiras.json"
    )
    try:
        with open(datasets_path, encoding="utf-8") as f:
            _cidades_data = json.load(f)
    except Exception as exc:
        logger.warning("Failed to load %s: %s — using empty dataset", datasets_path, exc)


async def _load_cidades():
    await asyncio.to_thread(_load_cidades_sync)


@router.get("/ibge/uf")
async def list_ufs():
    await _load_cidades()
    return list(_cidades_data.keys())


@router.get("/ibge/cidades/{uf}")
async def list_cidades(uf: str):
    await _load_cidades()
    return list(_cidades_data.get(uf.upper(), []))


@router.get("/geocode")
async def geocode(q: str):
    """Proxy for Nominatim geocoding to avoid direct client requests."""
    if not q or not q.strip():
        raise HTTPException(status_code=400, detail="Query parameter 'q' must not be empty")
    if len(q) > 200:
        raise HTTPException(
            status_code=400, detail="Query parameter 'q' must not exceed 200 characters"
        )
    _check_rate_limit()

    client = await get_http_client()
    resp = await client.get(
        "https://nominatim.openstreetmap.org/search",
        params={"format": "json", "q": q, "limit": 1},
        headers={"User-Agent": "SpaceEye/0.2.0"},
    )
    return resp.json()


@router.get("/geocode/reverse")
async def reverse_geocode(lat: float, lon: float):
    """Reverse geocode coordinates to place name via Nominatim."""
    if not (-90 <= lat <= 90):
        raise HTTPException(status_code=400, detail="Latitude must be between -90 and 90")
    if not (-180 <= lon <= 180):
        raise HTTPException(status_code=400, detail="Longitude must be between -180 and 180")

    _check_rate_limit()

    client = await get_http_client()
    resp = await client.get(
        "https://nominatim.openstreetmap.org/reverse",
        params={"format": "json", "lat": lat, "lon": lon},
        headers={"User-Agent": "SpaceEye/0.2.0"},
    )
    if resp.status_code != 200:
        raise HTTPException(status_code=502, detail="Upstream geocoding service error")
    data = resp.json()
    return {
        "display_name": data.get("display_name", ""),
        "lat": str(lat),
        "lon": str(lon),
    }
