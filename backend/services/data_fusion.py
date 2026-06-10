import httpx
import logging
from shapely.geometry import shape

logger = logging.getLogger(__name__)


async def fetch_weather_snapshot(lat: float, lon: float) -> dict:
    """Fetch current weather from Open-Meteo."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get("https://api.open-meteo.com/v1/forecast", params={
            "latitude": lat, "longitude": lon,
            "current": ["temperature_2m", "relative_humidity_2m", "apparent_temperature",
                        "precipitation", "weather_code", "soil_moisture_0_to_7cm"],
            "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
            "timezone": "America/Sao_Paulo",
            "forecast_days": 7,
        })
        resp.raise_for_status()
        return resp.json()


async def fetch_soil_snapshot(lat: float, lon: float) -> dict:
    """Fetch soil properties from ISRIC SoilGrids."""
    async with httpx.AsyncClient(timeout=15.0) as client:
        resp = await client.get("https://rest.isric.org/soilgrids/v2.0/properties/query", params={
            "lat": lat, "lon": lon,
            "property": ["phh2o", "oc", "nitrogen", "sand", "silt", "clay"],
            "depth": "0-5cm", "value": "mean",
        })
        if resp.status_code == 200:
            return resp.json()
        return {}


async def fetch_landcover_snapshot(lat: float, lon: float) -> dict:
    """Fetch land cover from ESA WorldCover."""
    lat_band = 'N' if lat >= 0 else 'S'
    lon_band = 'E' if lon >= 0 else 'W'
    tile_x = int(abs(lat) / 10)
    tile_y = int(abs(lon) / 10)
    classes = {
        10: "Tree cover", 20: "Shrubland", 30: "Grassland",
        40: "Cropland", 50: "Built-up", 60: "Bare/sparse",
        70: "Snow/ice", 80: "Water", 90: "Wetland",
        95: "Mangroves", 100: "Moss/lichen",
    }
    return {
        "source": "ESA WorldCover 2021",
        "resolution": "10m",
        "classes": classes,
        "tile_url": f"https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/10m/{lat_band}{tile_x:02d}{lon_band}{tile_y:03d}.tif",
    }


async def fuse_region_data(polygon_coords: list[list[list[float]]]) -> dict:
    """Fetch all data sources for a polygon and return fused snapshot."""
    poly = shape({"type": "Polygon", "coordinates": polygon_coords})
    centroid = poly.centroid

    weather = await fetch_weather_snapshot(centroid.y, centroid.x)
    soil = await fetch_soil_snapshot(centroid.y, centroid.x)
    landcover = await fetch_landcover_snapshot(centroid.y, centroid.x)

    return {
        "weather": weather,
        "soil": soil,
        "landcover": landcover,
        "centroid": {"lat": centroid.y, "lon": centroid.x},
    }
