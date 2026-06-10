import respx
import httpx
import pytest
from unittest.mock import AsyncMock, MagicMock
from httpx import AsyncClient, ASGITransport
from backend.main import app
from backend.api.deps import get_db


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


@pytest.fixture
def client_with_mock_db():
    mock_session = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar.return_value = 0
    mock_session.execute.return_value = mock_result

    async def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    c = AsyncClient(transport=transport, base_url="http://test")
    yield c
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_health_endpoint(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"


@pytest.mark.asyncio
async def test_health_detailed(client_with_mock_db):
    resp = await client_with_mock_db.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert "database" in data
    assert "catalog_count" in data
    assert data["database"] in ("connected", "disconnected")
    assert data["catalog_count"] == 0


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


@respx.mock
@pytest.mark.asyncio
async def test_weather_endpoint(client):
    respx.get("https://api.open-meteo.com/v1/forecast").mock(
        return_value=httpx.Response(200, json={
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
        })
    )
    resp = await client.get("/api/weather/-23.55/-46.63")
    assert resp.status_code == 200
    data = resp.json()
    assert "current" in data or "daily" in data


@respx.mock
@pytest.mark.asyncio
async def test_geocode_endpoint(client):
    respx.get("https://nominatim.openstreetmap.org/search").mock(
        return_value=httpx.Response(200, json=[
            {
                "place_id": 123,
                "lat": "-23.5505",
                "lon": "-46.6333",
                "display_name": "São Paulo, Brasil",
                "type": "city",
                "class": "place",
            }
        ])
    )
    resp = await client.get("/api/geocode?q=S%C3%A3o%20Paulo-SP")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)


@respx.mock
@pytest.mark.asyncio
async def test_soil_endpoint(client):
    respx.get("https://rest.isric.org/soilgrids/v2.0/properties/query").mock(
        return_value=httpx.Response(200, json={
            "type": "Feature",
            "properties": {
                "layers": [
                    {
                        "name": "phh2o",
                        "depths": [{"values": {"mean": 6.5}}]
                    },
                    {
                        "name": "oc",
                        "depths": [{"values": {"mean": 15.0}}]
                    },
                    {
                        "name": "sand",
                        "depths": [{"values": {"mean": 35.0}}]
                    },
                    {
                        "name": "silt",
                        "depths": [{"values": {"mean": 40.0}}]
                    },
                    {
                        "name": "clay",
                        "depths": [{"values": {"mean": 25.0}}]
                    },
                ]
            }
        })
    )
    resp = await client.get("/api/soil/-23.55/-46.63")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_landcover_endpoint(client):
    resp = await client.get("/api/landcover/-23.55/-46.63")
    assert resp.status_code == 200
    data = resp.json()
    assert "classes" in data
