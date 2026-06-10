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


# --- Analysis CRUD tests ---

@pytest.fixture
def client_with_analyses_db():
    """Mock DB that handles analyses CRUD operations."""
    mock_session = AsyncMock()

    from datetime import datetime, timezone

    analyses_store = []
    next_id = 1

    async def mock_execute(query, params=None):
        nonlocal next_id
        query_str = str(query) if hasattr(query, '__str__') else query

        if 'INSERT INTO analyses' in query_str:
            uid = f"test-uuid-{next_id:04d}"
            next_id += 1
            analyses_store.append({
                "id": uid,
                "image_id": params["image_id"],
                "collection": params["collection"],
                "product": params["product"],
                "polygon": params.get("polygon"),
                "centroid": params.get("centroid"),
                "statistics": params.get("statistics"),
                "acquired_at": None,
                "cloud_cover": params.get("cloud_cover"),
                "created_at": datetime(2025, 1, 1, tzinfo=timezone.utc),
            })
            result = MagicMock()
            result.fetchone.return_value = [uid]
            return result

        elif 'SELECT * FROM analyses' in query_str:
            filtered = list(analyses_store)
            if params:
                if 'product' in params and params['product']:
                    filtered = [a for a in filtered if a.get('product') == params['product']]
                if 'collection' in params and params['collection']:
                    filtered = [a for a in filtered if a.get('collection') == params['collection']]
            filtered.sort(key=lambda a: a.get('created_at') or datetime.min.replace(tzinfo=timezone.utc), reverse=True)
            limit = params.get('limit', 50) if params else 50
            offset = params.get('offset', 0) if params else 0
            filtered = filtered[offset:offset+limit]
            result = MagicMock()
            result.mappings.return_value.all.return_value = filtered
            return result

        elif 'SELECT COUNT(*) FROM analyses' in query_str:
            filtered = list(analyses_store)
            if params:
                if 'product' in params and params['product']:
                    filtered = [a for a in filtered if a.get('product') == params['product']]
                if 'collection' in params and params['collection']:
                    filtered = [a for a in filtered if a.get('collection') == params['collection']]
            result = MagicMock()
            result.scalar.return_value = len(filtered)
            return result

        elif 'DELETE FROM analyses' in query_str:
            aid = params.get('id') if params else None
            found = any(a.get('id') == aid for a in analyses_store)
            analyses_store[:] = [a for a in analyses_store if a.get('id') != aid]
            result = MagicMock()
            result.fetchone.return_value = [aid] if found else None
            return result

        return MagicMock()

    # Patch execute and commit
    mock_session.execute = mock_execute
    mock_session.commit = AsyncMock()

    # Store reference for test assertions
    mock_session._analyses_store = analyses_store
    mock_session._next_id_ref = lambda: next_id

    async def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    c = AsyncClient(transport=transport, base_url="http://test")
    yield c, analyses_store
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_and_list_analyses(client_with_analyses_db):
    client, store = client_with_analyses_db
    # Create
    payload = {
        "image_id": "test-image-001",
        "collection": "cbers4a",
        "product": "NDVI",
        "polygon": {"type": "Polygon", "coordinates": [[[-35.9, -5.8], [-35.8, -5.8], [-35.8, -5.7], [-35.9, -5.7], [-35.9, -5.8]]]},
        "centroid": {"lat": -5.75, "lon": -35.85},
        "statistics": {"mean": 0.45, "std": 0.12},
    }
    resp = await client.post("/api/analyses", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data

    # List
    resp = await client.get("/api/analyses")
    assert resp.status_code == 200
    analyses = resp.json()["analyses"]
    assert len(analyses) >= 1
    assert analyses[0]["image_id"] == "test-image-001"


@pytest.mark.asyncio
async def test_create_analysis_validation(client_with_analyses_db):
    client, store = client_with_analyses_db
    payload = {"image_id": "x"}  # missing required fields
    resp = await client.post("/api/analyses", json=payload)
    assert resp.status_code == 422
