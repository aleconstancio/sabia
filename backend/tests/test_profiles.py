from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock

import pytest
from httpx import ASGITransport, AsyncClient

from backend.api.deps import get_db
from backend.main import app


@pytest.fixture
def client_with_profiles_db():
    """Mock DB that handles profile CRUD operations."""
    mock_session = AsyncMock()

    profiles_store = []
    next_id = 1

    async def mock_execute(query, params=None):
        nonlocal next_id
        query_str = str(query) if hasattr(query, "__str__") else query

        if "INSERT INTO region_profiles" in query_str:
            uid = f"profile-{next_id:04d}"
            next_id += 1
            profiles_store.append(
                {
                    "id": uid,
                    "name": params["name"],
                    "polygon": params["polygon"],
                    "centroid": params.get("centroid"),
                    "weather_data": params.get("weather_data"),
                    "soil_data": params.get("soil_data"),
                    "landcover_data": params.get("landcover_data"),
                    "satellite_data": params.get("satellite_data"),
                    "notes": params.get("notes"),
                    "created_at": datetime(2025, 1, 1, tzinfo=UTC),
                }
            )
            result = MagicMock()
            result.fetchone.return_value = [uid]
            return result

        elif "SELECT * FROM region_profiles WHERE id" in query_str:
            pid = params.get("id") if params else None
            found = [p for p in profiles_store if p["id"] == pid]
            result = MagicMock()
            if found:
                row = dict(found[0])
                # Return a mock with mapping-style access
                mapping_mock = MagicMock()
                mapping_mock.__getitem__ = lambda self, key: row[key]
                mapping_mock.__iter__ = lambda self: iter(row.keys())
                mapping_mock.keys = lambda: row.keys()
                mapping_mock.items = lambda: row.items()
                mapping_mock.values = lambda: row.values()
                mapping_mock.__contains__ = lambda self, key: key in row
                result.mappings.return_value.fetchone.return_value = mapping_mock
            else:
                result.mappings.return_value.fetchone.return_value = None
            return result

        elif "SELECT * FROM region_profiles ORDER BY" in query_str:
            result = MagicMock()
            # Return rows as mapping objects
            rows = []
            for p in profiles_store:
                mapping_mock = MagicMock()
                mapping_mock.__getitem__ = lambda self, key, _p=p: _p[key]
                mapping_mock.__iter__ = lambda self, _p=p: iter(_p.keys())
                rows.append(mapping_mock)
            result.mappings.return_value.all.return_value = rows
            return result

        elif "SELECT COUNT(*) FROM region_profiles" in query_str:
            result = MagicMock()
            result.scalar.return_value = len(profiles_store)
            return result

        elif "DELETE FROM region_profiles" in query_str:
            pid = params.get("id") if params else None
            found = any(p["id"] == pid for p in profiles_store)
            profiles_store[:] = [p for p in profiles_store if p["id"] != pid]
            result = MagicMock()
            result.fetchone.return_value = [pid] if found else None
            return result

        return MagicMock()

    mock_session.execute = mock_execute
    mock_session.commit = AsyncMock()

    async def override_get_db():
        yield mock_session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    c = AsyncClient(transport=transport, base_url="http://test")
    yield c, profiles_store
    app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_profile(client_with_profiles_db):
    client, store = client_with_profiles_db
    payload = {
        "name": "Test Region",
        "polygon": {
            "type": "Polygon",
            "coordinates": [
                [[-35.9, -5.8], [-35.8, -5.8], [-35.8, -5.7], [-35.9, -5.7], [-35.9, -5.8]]
            ],
        },
        "notes": "Test notes",
    }
    resp = await client.post("/api/profiles", json=payload)
    assert resp.status_code == 200
    data = resp.json()
    assert "id" in data


@pytest.mark.asyncio
async def test_list_profiles(client_with_profiles_db):
    client, store = client_with_profiles_db
    resp = await client.get("/api/profiles")
    assert resp.status_code == 200
    data = resp.json()
    assert "profiles" in data
    assert "total" in data
    assert isinstance(data["profiles"], list)


@pytest.mark.asyncio
async def test_get_profile_not_found(client_with_profiles_db):
    client, store = client_with_profiles_db
    resp = await client.get("/api/profiles/nonexistent_id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_profile_not_found(client_with_profiles_db):
    client, store = client_with_profiles_db
    resp = await client.delete("/api/profiles/nonexistent_id")
    assert resp.status_code == 404
