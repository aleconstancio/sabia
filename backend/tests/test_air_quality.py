import httpx
import pytest
import respx
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@respx.mock
@pytest.mark.asyncio
async def test_air_quality_valid(client):
    respx.get("https://air-quality-api.open-meteo.com/v1/air-quality").mock(
        return_value=httpx.Response(
            200,
            json={
                "current": {
                    "pm2_5": 12.5,
                    "pm10": 25.0,
                    "carbon_monoxide": 200.0,
                    "nitrogen_dioxide": 15.0,
                    "sulphur_dioxide": 5.0,
                    "ozone": 80.0,
                    "european_aqi": 45,
                    "us_aqi": 42,
                }
            },
        )
    )
    resp = await client.get("/api/air-quality/-23.55/-46.63")
    assert resp.status_code == 200
    data = resp.json()
    assert "current" in data
    assert data["current"]["pm2_5"] == 12.5


@pytest.mark.asyncio
async def test_air_quality_invalid_lat(client):
    resp = await client.get("/api/air-quality/91.0/-46.63")
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_air_quality_invalid_lon(client):
    resp = await client.get("/api/air-quality/-23.55/181.0")
    assert resp.status_code == 400
