"""Deforestation alerts from INPE DETER (Daily Deforestation Detection in Real-Time)."""

import logging
import math

from backend.infra.http_client import get_http_client

logger = logging.getLogger(__name__)

DETER_URL = "http://terrabrasilis.dpi.inpe.br/api/"
DETER_TIMEOUT = 15.0


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two points using Haversine formula."""
    R = 6371.0
    lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
    lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


async def fetch_deforestation_alerts(
    lat: float, lon: float, radius_km: float = 50.0, limit: int = 20
) -> dict:
    """Fetch deforestation alerts from INPE DETER.

    Args:
        lat: Latitude
        lon: Longitude
        radius_km: Search radius in kilometers (default: 50)
        limit: Max alerts to return (default: 20)

    Returns:
        Dict with 'alerts' list, 'total_area_ha', and 'count'
    """
    try:
        client = await get_http_client()
        resp = await client.get(
            DETER_URL,
            params={"lat": lat, "lon": lon, "radius": radius_km},
            timeout=DETER_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        alerts = []
        total_area_ha = 0.0
        for item in data.get("data", []):
            alert_lat = item.get("lat", 0)
            alert_lon = item.get("lon", 0)
            dist = _haversine(lat, lon, alert_lat, alert_lon)
            if dist <= radius_km:
                area_m2 = item.get("areameter", 0)
                area_ha = area_m2 / 10000.0
                total_area_ha += area_ha
                alerts.append({
                    "id": f"{item.get('date', '')}-{alert_lat}-{alert_lon}",
                    "date": item.get("date", ""),
                    "area_ha": round(area_ha, 2),
                    "municipality": item.get("municipio", ""),
                    "state": item.get("uf", ""),
                    "biome": item.get("bioma", ""),
                    "class": "deforestation" if "DESGRAMA" in item.get("class", "") else "degradation",
                    "coordinates": [alert_lat, alert_lon],
                    "distance_km": round(dist, 1),
                })

        alerts.sort(key=lambda a: a["date"], reverse=True)
        return {
            "alerts": alerts[:limit],
            "total_area_ha": round(total_area_ha, 2),
            "count": len(alerts),
        }
    except Exception as e:
        logger.warning("Failed to fetch deforestation alerts for (%s, %s): %s", lat, lon, e)
        return {"alerts": [], "total_area_ha": 0, "count": 0, "error": str(e)}
