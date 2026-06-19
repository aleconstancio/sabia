from fastapi import APIRouter, HTTPException

from backend.services.air_quality import fetch_air_quality

router = APIRouter()


@router.get("/{lat}/{lon}")
async def get_air_quality(lat: float, lon: float):
    """Fetch air quality data from Open-Meteo (free, no API key needed)."""
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(400, "Latitude must be in [-90, 90], longitude in [-180, 180]")

    result = await fetch_air_quality(lat, lon)

    if "error" in result:
        raise HTTPException(
            status_code=502, detail=f"Upstream air quality service error: {result['error']}"
        )

    return result
