"""Air quality data from Open-Meteo Air Quality API."""

import logging

from backend.infra.http_client import get_http_client

logger = logging.getLogger(__name__)

AIR_QUALITY_URL = "https://air-quality-api.open-meteo.com/v1/air-quality"
AIR_QUALITY_TIMEOUT = 10.0


async def fetch_air_quality(lat: float, lon: float) -> dict:
    """Fetch air quality data from Open-Meteo Air Quality API.

    Args:
        lat: Latitude
        lon: Longitude

    Returns:
        Air quality data dict or error dict
    """
    try:
        client = await get_http_client()
        resp = await client.get(
            AIR_QUALITY_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "pm2_5",
                    "pm10",
                    "carbon_monoxide",
                    "nitrogen_dioxide",
                    "sulphur_dioxide",
                    "ozone",
                    "european_aqi",
                    "us_aqi",
                ],
            },
            timeout=AIR_QUALITY_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning("Failed to fetch air quality for (%s, %s): %s", lat, lon, e)
        return {"error": str(e)}
