import httpx
import pytest
import respx
from httpx import ASGITransport, AsyncClient

from backend.api import geocoding
from backend.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    c = AsyncClient(transport=transport, base_url="http://test")
    geocoding._geocode_last_request = 0.0
    return c


@respx.mock
@pytest.mark.asyncio
async def test_reverse_geocode_valid(client):
    respx.get("https://nominatim.openstreetmap.org/reverse").mock(
        return_value=httpx.Response(
            200,
            json={
                "display_name": "São Paulo, São Paulo, Brazil",
                "lat": "-23.5505",
                "lon": "-46.6333",
            },
        )
    )
    resp = await client.get("/api/geocode/reverse?lat=-23.5505&lon=-46.6333")
    assert resp.status_code == 200
    data = resp.json()
    assert "display_name" in data
    assert data["display_name"] == "São Paulo, São Paulo, Brazil"


@pytest.mark.asyncio
async def test_reverse_geocode_invalid_lat(client):
    resp = await client.get("/api/geocode/reverse?lat=91.0&lon=-46.6333")
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_reverse_geocode_invalid_lon(client):
    resp = await client.get("/api/geocode/reverse?lat=-23.5505&lon=181.0")
    assert resp.status_code == 400


@respx.mock
@pytest.mark.asyncio
async def test_reverse_geocode_rate_limit(client):
    # First request succeeds
    respx.get("https://nominatim.openstreetmap.org/reverse").mock(
        return_value=httpx.Response(
            200,
            json={"display_name": "Test", "lat": "0", "lon": "0"},
        )
    )
    await client.get("/api/geocode/reverse?lat=0&lon=0")
    # Second immediate request hits rate limit
    resp = await client.get("/api/geocode/reverse?lat=0&lon=0")
    assert resp.status_code == 429


@pytest.mark.asyncio
async def test_reverse_geocode_missing_params(client):
    resp = await client.get("/api/geocode/reverse")
    assert resp.status_code == 422


@respx.mock
@pytest.mark.asyncio
async def test_reverse_geocode_upstream_error(client):
    respx.get("https://nominatim.openstreetmap.org/reverse").mock(
        return_value=httpx.Response(502, text="Bad Gateway")
    )
    resp = await client.get("/api/geocode/reverse?lat=-23.5505&lon=-46.6333")
    assert resp.status_code == 502
    assert resp.json()["detail"] == "Upstream geocoding service error"
