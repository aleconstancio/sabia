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
async def test_disasters_valid(client):
    respx.get("https://eonet.gsfc.nasa.gov/api/v3/events").mock(
        return_value=httpx.Response(
            200,
            json={
                "events": [
                    {
                        "id": "test-1",
                        "title": "Test Wildfire",
                        "categories": [{"id": "wildfires", "title": "Wildfires"}],
                        "geometry": [{"date": "2026-06-19T00:00:00Z", "type": "Point", "coordinates": [-46.63, -23.55]}],
                        "sources": [{"id": "InciWeb", "url": "http://test"}],
                    }
                ]
            },
        )
    )
    resp = await client.get("/api/disasters/-23.55/-46.63")
    assert resp.status_code == 200
    data = resp.json()
    assert "events" in data


@pytest.mark.asyncio
async def test_disasters_invalid_lat(client):
    resp = await client.get("/api/disasters/91.0/-46.63")
    assert resp.status_code == 400
