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
async def test_weather_valid_coordinates(client):
    respx.get("https://api.open-meteo.com/v1/forecast").mock(
        return_value=httpx.Response(
            200,
            json={
                "current": {
                    "temperature_2m": 25.0,
                    "relative_humidity_2m": 60,
                    "apparent_temperature": 26.5,
                    "precipitation": 0.0,
                    "weather_code": 1,
                    "soil_moisture_0_to_7cm": 0.2,
                },
                "daily": {
                    "temperature_2m_max": [28.0, 27.5, 29.0, 26.0, 28.5, 30.0, 27.0],
                    "temperature_2m_min": [18.0, 17.5, 19.0, 17.0, 18.5, 20.0, 18.0],
                    "precipitation_sum": [0.0, 2.5, 0.0, 5.0, 0.0, 0.0, 1.0],
                    "precipitation_hours": [0, 3, 0, 6, 0, 0, 2],
                },
            },
        )
    )
    resp = await client.get("/api/weather/-23.55/-46.63")
    assert resp.status_code == 200
    data = resp.json()
    assert "current" in data
    assert data["current"]["temperature_2m"] == 25.0


@respx.mock
@pytest.mark.asyncio
async def test_weather_invalid_latitude(client):
    resp = await client.get("/api/weather/91.0/-46.63")
    assert resp.status_code == 400


@respx.mock
@pytest.mark.asyncio
async def test_weather_invalid_longitude(client):
    resp = await client.get("/api/weather/-23.55/181.0")
    assert resp.status_code == 400
