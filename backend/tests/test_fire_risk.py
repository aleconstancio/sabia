from unittest.mock import AsyncMock, patch

import pytest

from backend.services.fire_risk import calculate_fire_risk


@pytest.mark.asyncio
async def test_calculate_fire_risk_returns_valid_structure():
    coords = [[[-46.63, -23.55], [-46.62, -23.55], [-46.62, -23.54], [-46.63, -23.54], [-46.63, -23.55]]]

    mock_weather = {
        "current": {
            "temperature_2m": 35.0,
            "relative_humidity_2m": 20.0,
            "precipitation": 0.0,
        },
        "daily": {
            "temperature_2m_max": [38.0, 36.0, 37.0, 35.0, 34.0, 33.0, 32.0],
            "temperature_2m_min": [22.0, 21.0, 23.0, 20.0, 19.0, 18.0, 17.0],
            "precipitation_sum": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        },
    }

    with patch("backend.services.fire_risk.fetch_weather_for_fire", new_callable=AsyncMock, return_value=mock_weather):
        result = await calculate_fire_risk(coords)

    assert "risk_score" in result
    assert "risk_level" in result
    assert "nbr_trend" in result
    assert "factors" in result
    assert isinstance(result["risk_score"], float)
    assert 0 <= result["risk_score"] <= 100
    assert result["risk_level"] in ("low", "moderate", "high", "extreme")


@pytest.mark.asyncio
async def test_calculate_fire_risk_high_when_hot_dry():
    coords = [[[-46.63, -23.55], [-46.62, -23.55], [-46.62, -23.54], [-46.63, -23.54], [-46.63, -23.55]]]

    mock_weather = {
        "current": {"temperature_2m": 42.0, "relative_humidity_2m": 10.0, "precipitation": 0.0},
        "daily": {
            "temperature_2m_max": [42.0] * 7,
            "temperature_2m_min": [28.0] * 7,
            "precipitation_sum": [0.0] * 7,
        },
    }

    with patch("backend.services.fire_risk.fetch_weather_for_fire", new_callable=AsyncMock, return_value=mock_weather):
        result = await calculate_fire_risk(coords)

    assert result["risk_level"] in ("high", "extreme")
    assert result["risk_score"] >= 60
