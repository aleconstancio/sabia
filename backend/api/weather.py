from fastapi import APIRouter, HTTPException

from backend.services.external_apis import fetch_weather

router = APIRouter()


@router.get("/{lat}/{lon}")
async def get_weather(lat: float, lon: float):
    """Fetch weather data from Open-Meteo (free, no API key needed)."""
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(400, "Latitude must be in [-90, 90], longitude in [-180, 180]")

    result = await fetch_weather(
        lat,
        lon,
        properties=[
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "precipitation",
            "weather_code",
            "soil_moisture_0_to_7cm",
        ],
    )

    if "error" in result:
        raise HTTPException(
            status_code=502, detail=f"Upstream weather service error: {result['error']}"
        )

    return result
