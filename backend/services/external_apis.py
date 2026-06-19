"""Shared external API clients for weather and soil data.

Consolidates duplicate implementations across data_fusion, carbon_stock, and fire_risk.
"""

import logging

from backend.infra.http_client import get_http_client

logger = logging.getLogger(__name__)

# Open-Meteo API configuration
OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
OPEN_METEO_TIMEOUT = 10.0

# ISRIC SoilGrids API configuration
SOILGRIDS_URL = "https://rest.isric.org/soilgrids/v2.0/properties/query"
SOILGRIDS_TIMEOUT = 10.0


async def fetch_weather(
    lat: float,
    lon: float,
    properties: list[str] | None = None,
    forecast_days: int = 7,
) -> dict:
    """Fetch weather data from Open-Meteo API.

    Args:
        lat: Latitude
        lon: Longitude
        properties: Weather properties to fetch (default: temperature, humidity, precipitation)
        forecast_days: Number of forecast days (default: 7)

    Returns:
        Weather data dict or error dict
    """
    if properties is None:
        properties = [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "weather_code",
            "soil_moisture_0_to_7cm",
            "wind_speed_10m",
            "wind_direction_10m",
            "wind_gusts_10m",
        ]

    try:
        client = await get_http_client()
        resp = await client.get(
            OPEN_METEO_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": properties,
                "daily": [
                    "temperature_2m_max",
                    "temperature_2m_min",
                    "precipitation_sum",
                    "uv_index_max",
                    "sunrise",
                    "sunset",
                    "daylight_duration",
                ],
                "timezone": "America/Sao_Paulo",
                "forecast_days": forecast_days,
            },
            timeout=OPEN_METEO_TIMEOUT,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning("Failed to fetch weather for (%s, %s): %s", lat, lon, e)
        return {"error": str(e)}


async def fetch_soil(
    lat: float,
    lon: float,
    properties: list[str] | None = None,
    depth: str = "0-5cm",
) -> dict:
    """Fetch soil properties from ISRIC SoilGrids API.

    Args:
        lat: Latitude
        lon: Longitude
        properties: Soil properties to fetch (default: phh2o, oc, nitrogen, sand, silt, clay)
        depth: Soil depth layer (default: 0-5cm)

    Returns:
        Soil data dict or error dict
    """
    if properties is None:
        properties = ["phh2o", "oc", "nitrogen", "sand", "silt", "clay"]

    try:
        client = await get_http_client()
        resp = await client.get(
            SOILGRIDS_URL,
            params={
                "lat": lat,
                "lon": lon,
                "property": properties,
                "depth": depth,
                "value": "mean",
            },
            timeout=SOILGRIDS_TIMEOUT,
        )
        if resp.status_code == 200:
            return resp.json()
        return {"error": f"Non-200 status: {resp.status_code}"}
    except Exception as e:
        logger.warning("Failed to fetch soil for (%s, %s): %s", lat, lon, e)
        return {"error": str(e)}


def extract_soil_property(soil_data: dict, property_name: str, depth: str = "0-5cm") -> float:
    """Extract a specific soil property from ISRIC SoilGrids response.

    Args:
        soil_data: Soil data response from fetch_soil
        property_name: Name of the property to extract (e.g., 'oc', 'phh2o')
        depth: Depth layer to extract (default: 0-5cm)

    Returns:
        Property value or 0.0 if not found
    """
    if "error" in soil_data:
        return 0.0
    try:
        for prop in soil_data.get("properties", []):
            if prop.get("name") == property_name:
                for d in prop.get("depths", []):
                    if d.get("label") == depth:
                        return d.get("values", {}).get("mean", 0.0)
    except (KeyError, TypeError, IndexError):
        pass
    return 0.0
