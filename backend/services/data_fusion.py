import asyncio
import logging

from shapely.geometry import shape

from backend.api.deps import get_http_client
from backend.api.landcover_utils import WORLDCOVER_CLASSES, build_worldcover_tile_url

logger = logging.getLogger(__name__)


async def fetch_weather_snapshot(lat: float, lon: float) -> dict:
    """Fetch current weather from Open-Meteo."""
    try:
        client = await get_http_client()
        resp = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": [
                    "temperature_2m",
                    "relative_humidity_2m",
                    "apparent_temperature",
                    "precipitation",
                    "weather_code",
                    "soil_moisture_0_to_7cm",
                ],
                "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
                "timezone": "America/Sao_Paulo",
                "forecast_days": 7,
            },
            timeout=10.0,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception:
        logger.warning("Failed to fetch weather snapshot for (%s, %s)", lat, lon)
        return {}


async def fetch_soil_snapshot(lat: float, lon: float) -> dict:
    """Fetch soil properties from ISRIC SoilGrids."""
    try:
        client = await get_http_client()
        resp = await client.get(
            "https://rest.isric.org/soilgrids/v2.0/properties/query",
            params={
                "lat": lat,
                "lon": lon,
                "property": ["phh2o", "oc", "nitrogen", "sand", "silt", "clay"],
                "depth": "0-5cm",
                "value": "mean",
            },
            timeout=10.0,
        )
        if resp.status_code == 200:
            return resp.json()
        return {}
    except Exception:
        logger.warning("Failed to fetch soil snapshot for (%s, %s)", lat, lon)
        return {}


async def fetch_landcover_snapshot(lat: float, lon: float) -> dict:
    """Fetch land cover from ESA WorldCover."""
    return {
        "source": "ESA WorldCover 2021",
        "resolution": "10m",
        "classes": WORLDCOVER_CLASSES,
        "tile_url": build_worldcover_tile_url(lat, lon),
    }


async def fuse_region_data(polygon_coords: list[list[list[float]]]) -> dict:
    """Fetch all data sources for a polygon and return fused snapshot."""
    poly = shape({"type": "Polygon", "coordinates": polygon_coords})
    centroid = poly.centroid

    weather, soil, landcover = await asyncio.gather(
        fetch_weather_snapshot(centroid.y, centroid.x),
        fetch_soil_snapshot(centroid.y, centroid.x),
        fetch_landcover_snapshot(centroid.y, centroid.x),
    )

    return {
        "weather": weather,
        "soil": soil,
        "landcover": landcover,
        "centroid": {"lat": centroid.y, "lon": centroid.x},
    }
