from fastapi import APIRouter, HTTPException

from backend.services.deforestation import fetch_deforestation_alerts

router = APIRouter()


@router.get("/{lat}/{lon}")
async def get_deforestation_alerts(lat: float, lon: float):
    """Fetch nearby deforestation alerts from INPE DETER (free, no API key needed)."""
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(400, "Latitude must be in [-90, 90], longitude in [-180, 180]")

    result = await fetch_deforestation_alerts(lat, lon)

    if "error" in result:
        raise HTTPException(
            status_code=502, detail=f"Upstream deforestation service error: {result['error']}"
        )

    return result
