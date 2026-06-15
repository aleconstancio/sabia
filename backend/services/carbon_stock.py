"""Carbon stock estimation from soil organic carbon and weather-derived biomass proxy."""

import logging

from backend.services.external_apis import extract_soil_property, fetch_soil, fetch_weather
from backend.utils import compute_centroid

logger = logging.getLogger(__name__)

BIOMASS_FACTOR = 2.0


def _compute_biomass_proxy(weather: dict) -> float:
    """Estimate above-ground biomass proxy from temperature and precipitation."""
    try:
        temp = weather.get("current", {}).get("temperature_2m", 25.0)
        precip = sum(weather.get("daily", {}).get("precipitation_sum", [0.0]))
        temp_factor = max(0, min(1, (temp - 10) / 30))
        precip_factor = max(0, min(1, precip / 10.0))
        return temp_factor * precip_factor * BIOMASS_FACTOR
    except (KeyError, TypeError):
        return 1.0


async def fetch_weather_for_carbon(coords: list[list[list[float]]]) -> dict:
    """Fetch weather from Open-Meteo for polygon centroid."""
    lat, lon = compute_centroid(coords)
    return await fetch_weather(
        lat,
        lon,
        properties=["temperature_2m", "relative_humidity_2m", "precipitation"],
    )


async def fetch_soil_for_carbon(coords: list[list[list[float]]]) -> dict:
    """Fetch soil properties from ISRIC SoilGrids for polygon centroid."""
    lat, lon = compute_centroid(coords)
    return await fetch_soil(
        lat,
        lon,
        properties=["oc", "nitrogen"],
    )


async def estimate_carbon_stock(coords: list[list[list[float]]]) -> dict:
    """Estimate carbon stock from soil organic carbon and weather-derived biomass proxy."""
    weather, soil = await fetch_weather_for_carbon(coords), await fetch_soil_for_carbon(coords)

    soc_g_kg = extract_soil_property(soil, "oc")
    soc_t_ha = soc_g_kg * 0.075

    biomass = _compute_biomass_proxy(weather)
    carbon_stock = soc_t_ha + biomass

    return {
        "carbon_stock_t_ha": round(carbon_stock, 2),
        "biomass_estimate": round(biomass, 2),
        "soil_organic_carbon": round(soc_t_ha, 2),
        "ndvi_avg": 0.0,
        "weather_summary": {
            "temperature": weather.get("current", {}).get("temperature_2m"),
            "humidity": weather.get("current", {}).get("relative_humidity_2m"),
            "precipitation": weather.get("current", {}).get("precipitation"),
        },
        "soil_summary": {
            "organic_carbon_gkg": soc_g_kg,
            "nitrogen": extract_soil_property(soil, "nitrogen"),
        },
    }
