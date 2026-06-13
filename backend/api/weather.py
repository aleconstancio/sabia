import httpx
from fastapi import APIRouter, HTTPException

from backend.api.deps import get_http_client

router = APIRouter()


@router.get("/{lat}/{lon}")
async def get_weather(lat: float, lon: float):
    """Fetch weather data from Open-Meteo (free, no API key needed)."""
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(400, "Latitude must be in [-90, 90], longitude in [-180, 180]")
    params = {
        "latitude": lat,
        "longitude": lon,
        "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "precipitation", "weather_code", "soil_moisture_0_to_7cm"],
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum", "precipitation_hours"],
        "timezone": "America/Sao_Paulo",
        "forecast_days": 7,
    }
    client = await get_http_client()
    try:
        resp = await client.get("https://api.open-meteo.com/v1/forecast", params=params)
        resp.raise_for_status()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=502,
            detail=f"Upstream weather service returned error: {e.response.status_code}"
        ) from e
    return resp.json()
