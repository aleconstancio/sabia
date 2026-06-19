"""Disaster alerts from NASA Earth Observatory Natural Event Tracker (EONET)."""

import logging
import math

from backend.infra.http_client import get_http_client

logger = logging.getLogger(__name__)

EONET_URL = "https://eonet.gsfc.nasa.gov/api/v3/events"
EONET_TIMEOUT = 15.0


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance in km between two points using Haversine formula."""
    R = 6371.0
    lat1_r, lon1_r = math.radians(lat1), math.radians(lon1)
    lat2_r, lon2_r = math.radians(lat2), math.radians(lon2)
    dlat = lat2_r - lat1_r
    dlon = lon2_r - lon1_r
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1_r) * math.cos(lat2_r) * math.sin(dlon / 2) ** 2
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


async def fetch_disaster_alerts(
    lat: float, lon: float, radius_km: float = 100.0, limit: int = 20
) -> dict:
    """Fetch disaster alerts from NASA EONET.

    Args:
        lat: Latitude
        lon: Longitude
        radius_km: Search radius in kilometers (default: 100)
        limit: Max events to return (default: 20)

    Returns:
        Dict with 'events' list and 'nearby' count
    """
    try:
        client = await get_http_client()
        resp = await client.get(
            EONET_URL,
            params={"status": "open", "limit": 50},
            timeout=EONET_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()

        nearby_events = []
        for event in data.get("events", []):
            geometries = event.get("geometry", [])
            if not geometries:
                continue
            geom = geometries[-1]
            coords = geom.get("coordinates", [])
            if len(coords) < 2:
                continue
            event_lon, event_lat = coords[0], coords[1]
            dist = _haversine(lat, lon, event_lat, event_lon)
            if dist <= radius_km:
                category = event.get("categories", [{}])[0]
                nearby_events.append({
                    "id": event.get("id", ""),
                    "title": event.get("title", ""),
                    "category": category.get("id", "unknown"),
                    "category_title": category.get("title", "Unknown"),
                    "date": geom.get("date", ""),
                    "coordinates": [event_lat, event_lon],
                    "distance_km": round(dist, 1),
                    "sources": event.get("sources", []),
                })

        nearby_events.sort(key=lambda e: e["date"], reverse=True)
        return {
            "events": nearby_events[:limit],
            "nearby": len(nearby_events),
        }
    except Exception as e:
        logger.warning("Failed to fetch disaster alerts for (%s, %s): %s", lat, lon, e)
        return {"events": [], "nearby": 0, "error": str(e)}
