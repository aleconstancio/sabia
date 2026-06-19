from fastapi import APIRouter, HTTPException

from backend.services.disasters import fetch_disaster_alerts

router = APIRouter()


@router.get("/{lat}/{lon}")
async def get_disaster_alerts(lat: float, lon: float):
    """Fetch nearby disaster alerts from NASA EONET (free, no API key needed)."""
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(400, "Latitude must be in [-90, 90], longitude in [-180, 180]")

    result = await fetch_disaster_alerts(lat, lon)

    if "error" in result:
        raise HTTPException(
            status_code=502, detail=f"Upstream disaster service error: {result['error']}"
        )

    return result
