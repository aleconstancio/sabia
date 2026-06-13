import pytest
from unittest.mock import AsyncMock, patch
from backend.services.carbon_stock import estimate_carbon_stock


@pytest.mark.asyncio
async def test_estimate_carbon_stock_returns_valid_structure():
    coords = [[[-46.63, -23.55], [-46.62, -23.55], [-46.62, -23.54], [-46.63, -23.54], [-46.63, -23.55]]]

    mock_weather = {
        "current": {"temperature_2m": 25.0, "relative_humidity_2m": 60.0, "precipitation": 0.0},
        "daily": {"temperature_2m_max": [30.0], "temperature_2m_min": [18.0], "precipitation_sum": [0.0]},
    }
    mock_soil = {
        "properties": [
            {"name": "oc", "depths": [{"label": "0-5cm", "values": {"mean": 15.0}}]},
            {"name": "nitrogen", "depths": [{"label": "0-5cm", "values": {"mean": 1.2}}]},
        ]
    }

    with patch("backend.services.carbon_stock.fetch_weather", new_callable=AsyncMock, return_value=mock_weather), \
         patch("backend.services.carbon_stock.fetch_soil", new_callable=AsyncMock, return_value=mock_soil):
        result = await estimate_carbon_stock(coords)

    assert "carbon_stock_t_ha" in result
    assert "biomass_estimate" in result
    assert "ndvi_avg" in result
    assert "soil_organic_carbon" in result
    assert "methodology" in result
    assert isinstance(result["carbon_stock_t_ha"], float)
    assert result["carbon_stock_t_ha"] >= 0


@pytest.mark.asyncio
async def test_estimate_carbon_stock_handles_missing_soil():
    coords = [[[-46.63, -23.55], [-46.62, -23.55], [-46.62, -23.54], [-46.63, -23.54], [-46.63, -23.55]]]

    mock_weather = {
        "current": {"temperature_2m": 25.0, "relative_humidity_2m": 60.0, "precipitation": 0.0},
        "daily": {"temperature_2m_max": [30.0], "temperature_2m_min": [18.0], "precipitation_sum": [0.0]},
    }

    with patch("backend.services.carbon_stock.fetch_weather", new_callable=AsyncMock, return_value=mock_weather), \
         patch("backend.services.carbon_stock.fetch_soil", new_callable=AsyncMock, return_value={"error": "timeout"}):
        result = await estimate_carbon_stock(coords)

    assert result["carbon_stock_t_ha"] >= 0
    assert result["soil_organic_carbon"] == 0.0
