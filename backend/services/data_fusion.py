"""Multi-source data fusion for ESG monitoring.

Combines weather, soil, and landcover data into unified region snapshots.
"""

import asyncio
import logging

from shapely.geometry import shape

from backend.services.external_apis import fetch_soil, fetch_weather
from backend.services.worldcover import WORLDCOVER_CLASSES, build_worldcover_tile_url

logger = logging.getLogger(__name__)


async def fetch_weather_snapshot(lat: float, lon: float) -> dict:
    """Fetch current weather from Open-Meteo."""
    return await fetch_weather(lat, lon)


async def fetch_soil_snapshot(lat: float, lon: float) -> dict:
    """Fetch soil properties from ISRIC SoilGrids."""
    return await fetch_soil(lat, lon)


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
