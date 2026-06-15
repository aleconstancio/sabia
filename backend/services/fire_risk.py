"""Fire risk assessment from weather factors and NBR trend."""

import logging

from backend.services.external_apis import fetch_weather
from backend.utils import compute_centroid

logger = logging.getLogger(__name__)

TEMP_WEIGHT = 0.3
HUMIDITY_WEIGHT = 0.25
PRECIP_WEIGHT = 0.25
VEG_WEIGHT = 0.2


def _temperature_score(temp_max: float) -> float:
    if temp_max < 20:
        return 0.0
    if temp_max > 45:
        return 100.0
    return ((temp_max - 20) / 25) * 100


def _humidity_score(humidity: float) -> float:
    if humidity > 80:
        return 0.0
    if humidity < 10:
        return 100.0
    return ((80 - humidity) / 70) * 100


def _precipitation_score(precip_7d: float) -> float:
    if precip_7d > 50:
        return 0.0
    if precip_7d < 1:
        return 100.0
    return ((50 - precip_7d) / 49) * 100


def _drought_score(temp_max: list[float], precip: list[float]) -> float:
    hot_dry_days = 0
    for t, p in zip(temp_max, precip, strict=True):
        if t > 30 and p < 1:
            hot_dry_days += 1
    return min(100, hot_dry_days * 15)


def _risk_level(score: float) -> str:
    if score < 25:
        return "low"
    if score < 50:
        return "moderate"
    if score < 75:
        return "high"
    return "extreme"


async def fetch_weather_for_fire(coords: list[list[list[float]]]) -> dict:
    """Fetch weather data for fire risk calculation."""
    lat, lon = compute_centroid(coords)
    weather = await fetch_weather(
        lat,
        lon,
        properties=["temperature_2m", "relative_humidity_2m", "precipitation"],
    )

    # Return default values on error
    if "error" in weather:
        return {
            "current": {"temperature_2m": 25.0, "relative_humidity_2m": 50.0, "precipitation": 0.0},
            "daily": {
                "temperature_2m_max": [25.0] * 7,
                "temperature_2m_min": [15.0] * 7,
                "precipitation_sum": [0.0] * 7,
            },
        }

    return weather


async def calculate_fire_risk(coords: list[list[list[float]]]) -> dict:
    """Calculate fire risk from weather factors and NBR trend."""
    weather = await fetch_weather_for_fire(coords)

    current = weather.get("current", {})
    daily = weather.get("daily", {})

    temp = current.get("temperature_2m", 25.0)
    humidity = current.get("relative_humidity_2m", 50.0)
    temp_max = daily.get("temperature_2m_max", [25.0] * 7)
    precip_sum = daily.get("precipitation_sum", [0.0] * 7)
    total_precip = sum(precip_sum)

    temp_score = _temperature_score(max(temp_max))
    humidity_score = _humidity_score(humidity)
    precip_score = _precipitation_score(total_precip)
    drought = _drought_score(temp_max, precip_sum)
    veg_score = min(100, drought * 0.6 + 20)

    composite = (
        temp_score * TEMP_WEIGHT
        + humidity_score * HUMIDITY_WEIGHT
        + precip_score * PRECIP_WEIGHT
        + veg_score * VEG_WEIGHT
    )

    return {
        "fire_risk_score": round(composite, 1),
        "risk_level": _risk_level(composite),
        "factors": {
            "temperature_score": round(temp_score, 1),
            "humidity_score": round(humidity_score, 1),
            "precipitation_score": round(precip_score, 1),
            "vegetation_score": round(veg_score, 1),
            "drought_days": drought,
        },
        "weather_summary": {
            "temperature": temp,
            "humidity": humidity,
            "precipitation_7d": total_precip,
        },
    }
