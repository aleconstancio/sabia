import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.mark.asyncio
async def test_health_endpoint(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_collections_endpoint(client):
    resp = await client.get("/api/collections")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 5  # 5 collections
    ids = [c["id"] for c in data]
    assert "cbers4a" in ids
    assert "sentinel2" in ids
    assert "landsat8" in ids


@pytest.mark.asyncio
async def test_ibge_uf_endpoint(client):
    resp = await client.get("/api/ibge/uf")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "SP" in data or "AC" in data or "RJ" in data


@pytest.mark.asyncio
async def test_images_search_invalid_polygon(client):
    resp = await client.post("/api/images/search", json={"coordinates": [[[0, 0]]]})
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_images_search_valid_polygon(client):
    poly = [[[-35.2, -5.8], [-35.1, -5.8], [-35.1, -5.7], [-35.2, -5.7], [-35.2, -5.8]]]
    resp = await client.post("/api/images/search", json={"coordinates": poly, "limit": 5})
    assert resp.status_code == 200
    data = resp.json()
    assert "images" in data
    assert "total" in data


@pytest.mark.asyncio
async def test_get_nonexistent_image(client):
    resp = await client.get("/api/images/nonexistent_id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_weather_endpoint(client):
    resp = await client.get("/api/weather/-23.55/-46.63")
    assert resp.status_code == 200
    data = resp.json()
    assert "current" in data or "daily" in data


@pytest.mark.asyncio
async def test_geocode_endpoint(client):
    resp = await client.get("/api/geocode?q=S%C3%A3o%20Paulo-SP")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_soil_endpoint(client):
    resp = await client.get("/api/soil/-23.55/-46.63")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_landcover_endpoint(client):
    resp = await client.get("/api/landcover/-23.55/-46.63")
    assert resp.status_code == 200
    data = resp.json()
    assert "classes" in data
