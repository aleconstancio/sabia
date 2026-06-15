import logging
import os
import tempfile

from fastapi import APIRouter, HTTPException

from backend.api.deps import get_http_client
from backend.api.landcover_utils import WORLDCOVER_CLASSES, build_worldcover_tile_url
from backend.models.schemas import PolygonRequest
from backend.services.landcover_zonal import compute_landcover_zonal

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/{lat}/{lon}")
async def get_landcover(lat: float, lon: float):
    """Get land cover classification for a point using open data."""
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(400, detail="Latitude must be in [-90, 90], longitude in [-180, 180]")

    return {
        "source": "ESA WorldCover 2021",
        "resolution": "10m",
        "classes": WORLDCOVER_CLASSES,
        "tile_url": build_worldcover_tile_url(lat, lon),
    }


async def _compute_landcover_zonal(coords: list[list[list[float]]]) -> dict:
    """Shared helper for landcover zonal computations."""
    if not coords or not coords[0]:
        raise HTTPException(400, detail="Invalid coordinates")

    # Calculate centroid to determine which tile to fetch
    ring = coords[0]
    lats = [c[1] for c in ring]
    lons = [c[0] for c in ring]
    center_lat = sum(lats) / len(lats)
    center_lon = sum(lons) / len(lons)

    # Build tile URL
    tile_url = build_worldcover_tile_url(center_lat, center_lon)

    # Download tile to temporary file
    client = await get_http_client()
    with tempfile.NamedTemporaryFile(suffix=".tif", delete=False) as tmp:
        response = await client.get(tile_url, follow_redirects=True)
        if response.status_code != 200:
            raise HTTPException(
                status_code=502,
                detail=f"Failed to download WorldCover tile: {response.status_code}",
            )
        tmp.write(response.content)
        tmp_path = tmp.name

    try:
        return compute_landcover_zonal(coords, tmp_path)
    finally:
        os.unlink(tmp_path)


@router.post("/zonal")
async def landcover_zonal(req: PolygonRequest):
    """Get land cover class percentages for a polygon area."""
    try:
        result = await _compute_landcover_zonal(req.coordinates)
        return {"source": "ESA WorldCover 2021", "resolution": "10m", **result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Landcover zonal computation failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/zonal-stats")
async def landcover_zonal_stats(req: PolygonRequest):
    """Sample ESA WorldCover tile within polygon and return area percentages."""
    try:
        result = await _compute_landcover_zonal(req.coordinates)
        return {"source": "ESA WorldCover 2021", "resolution": "10m", **result}
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Landcover zonal stats computation failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e)) from e
