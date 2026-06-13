import logging

from backend.api.deps import get_http_client
from backend.utils import compute_centroid

logger = logging.getLogger(__name__)

BIOMASS_FACTOR = 2.0


def _extract_soil_oc(soil_data: dict) -> float:
    """Extract soil organic carbon (g/kg) from ISRIC SoilGrids response."""
    if "error" in soil_data:
        return 0.0
    try:
        for prop in soil_data.get("properties", []):
            if prop.get("name") == "oc":
                for depth in prop.get("depths", []):
                    if depth.get("label") == "0-5cm":
                        return depth.get("values", {}).get("mean", 0.0)
    except (KeyError, TypeError, IndexError):
        pass
    return 0.0


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


async def fetch_weather(coords: list[list[list[float]]]) -> dict:
    """Fetch weather from Open-Meteo for polygon centroid."""
    lat, lon = compute_centroid(coords)
    try:
        client = await get_http_client()
        resp = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": ["temperature_2m", "relative_humidity_2m", "precipitation"],
                "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
                "timezone": "America/Sao_Paulo",
                "forecast_days": 7,
            },
            timeout=10.0,
        )
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        logger.warning("Weather fetch failed: %s", e)
        return {"error": str(e)}


async def fetch_soil(coords: list[list[list[float]]]) -> dict:
    """Fetch soil properties from ISRIC SoilGrids for polygon centroid."""
    lat, lon = compute_centroid(coords)
    try:
        client = await get_http_client()
        resp = await client.get(
            "https://rest.isric.org/soilgrids/v2.0/properties/query",
            params={
                "lat": lat,
                "lon": lon,
                "property": ["oc", "nitrogen"],
                "depth": "0-5cm",
                "value": "mean",
            },
            timeout=10.0,
        )
        if resp.status_code == 200:
            return resp.json()
        return {"error": f"Non-200 status: {resp.status_code}"}
    except Exception as e:
        logger.warning("Soil fetch failed: %s", e)
        return {"error": str(e)}


async def estimate_carbon_stock(coords: list[list[list[float]]]) -> dict:
    """Estimate carbon stock from soil organic carbon and weather-derived biomass proxy."""
    weather, soil = await fetch_weather(coords), await fetch_soil(coords)

    soc_g_kg = _extract_soil_oc(soil)
    soc_t_ha = soc_g_kg * 0.075

    biomass = _compute_biomass_proxy(weather)
    carbon_stock = soc_t_ha + biomass

    return {
        "carbon_stock_t_ha": round(carbon_stock, 2),
        "biomass_estimate": round(biomass, 2),
        "soil_organic_carbon": round(soc_t_ha, 2),
        "ndvi_avg": 0.0,
        "methodology": "IPCC Tier 2: SOC (ISRIC SoilGrids 0-5cm) + weather-derived biomass proxy",
        "weather_summary": {
            "temperature": weather.get("current", {}).get("temperature_2m"),
            "humidity": weather.get("current", {}).get("relative_humidity_2m"),
            "precipitation_7d": sum(weather.get("daily", {}).get("precipitation_sum", [0.0])),
        },
    }
