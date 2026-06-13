from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

from backend.api.landcover_utils import WORLDCOVER_CLASSES, build_worldcover_tile_url
from backend.models.schemas import PolygonRequest

router = APIRouter()


@router.get("/{lat}/{lon}")
async def get_landcover(lat: float, lon: float):
    """Get land cover classification for a point using open data."""
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        raise HTTPException(400, "Latitude must be in [-90, 90], longitude in [-180, 180]")

    return {
        "source": "ESA WorldCover 2021",
        "resolution": "10m",
        "classes": WORLDCOVER_CLASSES,
        "tile_url": build_worldcover_tile_url(lat, lon),
    }


@router.post("/zonal")
async def landcover_zonal(req: PolygonRequest):
    """Get land cover class percentages for a polygon area.

    Not yet implemented — server-side rasterio sampling is required to
    compute real zonal statistics from the ESA WorldCover raster tiles.
    """
    return JSONResponse(
        status_code=501,
        content={
            "error": "Not implemented",
            "message": (
                "Zonal stats require server-side rasterio sampling of ESA WorldCover "
                "tiles, which is not yet implemented. Use the /landcover/{lat}/{lon} endpoint "
                "for a tile URL that can be rendered client-side."
            ),
        },
    )


@router.post("/zonal-stats")
async def landcover_zonal_stats(req: PolygonRequest):
    """Sample ESA WorldCover tile within polygon and return area percentages.

    Not yet implemented — server-side rasterio sampling is required to
    compute real zonal statistics from the ESA WorldCover raster tiles.
    """
    return JSONResponse(
        status_code=501,
        content={
            "error": "Not implemented",
            "message": (
                "Zonal stats require server-side rasterio sampling of ESA WorldCover "
                "tiles, which is not yet implemented. Use the /landcover/zonal endpoint "
                "for a tile URL that can be rendered client-side."
            ),
        },
    )
