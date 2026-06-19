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
async def test_deforestation_valid(client):
    respx.get("http://terrabrasilis.dpi.inpe.br/api/").mock(
        return_value=httpx.Response(
            200,
            json={
                "data": [
                    {
                        "lat": -23.55,
                        "lon": -46.63,
                        "areameter": 500000,
                        "municipio": "São Paulo",
                        "uf": "SP",
                        "bioma": "Mata Atlântica",
                        "class": "DESGRAMA",
                        "date": "2026-06-19",
                    }
                ]
            },
        )
    )
    resp = await client.get("/api/deforestation/-23.55/-46.63")
    assert resp.status_code == 200
    data = resp.json()
    assert "alerts" in data


@pytest.mark.asyncio
async def test_deforestation_invalid_lat(client):
    resp = await client.get("/api/deforestation/91.0/-46.63")
    assert resp.status_code == 400
