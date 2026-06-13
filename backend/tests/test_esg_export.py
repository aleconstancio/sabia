import pytest
import csv
import io
from unittest.mock import AsyncMock, patch
from backend.services.esg_export import export_esg_csv_data, export_esg_json_data


@pytest.mark.asyncio
async def test_export_esg_csv_returns_csv_string():
    coords = [[[-46.63, -23.55], [-46.62, -23.55], [-46.62, -23.54], [-46.63, -23.54], [-46.63, -23.55]]]

    mock_carbon = {
        "carbon_stock_t_ha": 45.2,
        "biomass_estimate": 2.1,
        "soil_organic_carbon": 43.1,
        "ndvi_avg": 0.45,
    }
    mock_fire = {
        "risk_score": 35.0,
        "risk_level": "moderate",
        "nbr_trend": -0.02,
        "factors": {"drought_days": 2},
    }

    with patch("backend.services.esg_export.estimate_carbon_stock", new_callable=AsyncMock, return_value=mock_carbon), \
         patch("backend.services.esg_export.calculate_fire_risk", new_callable=AsyncMock, return_value=mock_fire):
        result = await export_esg_csv_data("vegetation", coords)

    reader = csv.DictReader(io.StringIO(result))
    rows = list(reader)
    assert len(rows) > 0
    assert "module" in rows[0]
    assert rows[0]["module"] == "vegetation"


@pytest.mark.asyncio
async def test_export_esg_json_returns_dict():
    coords = [[[-46.63, -23.55], [-46.62, -23.55], [-46.62, -23.54], [-46.63, -23.54], [-46.63, -23.55]]]

    mock_carbon = {"carbon_stock_t_ha": 45.2, "biomass_estimate": 2.1, "soil_organic_carbon": 43.1, "ndvi_avg": 0.45, "weather_summary": {"temperature": 25.0, "precipitation_7d": 5.0}}
    mock_fire = {"risk_score": 35.0, "risk_level": "moderate", "nbr_trend": -0.02, "factors": {"drought_days": 2}}

    with patch("backend.services.esg_export.estimate_carbon_stock", new_callable=AsyncMock, return_value=mock_carbon), \
         patch("backend.services.esg_export.calculate_fire_risk", new_callable=AsyncMock, return_value=mock_fire):
        result = await export_esg_json_data("test-region", coords)

    assert "region" in result
    assert "modules" in result
    assert "vegetation" in result["modules"]
    assert "fire" in result["modules"]
    assert result["region"] == "test-region"
