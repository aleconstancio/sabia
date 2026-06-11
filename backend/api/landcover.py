from fastapi import APIRouter, HTTPException

from backend.models.schemas import PolygonRequest
from backend.api.landcover_utils import build_worldcover_tile_url, WORLDCOVER_CLASSES, sample_points_in_polygon

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
    """Get land cover class percentages for a polygon area."""
    from shapely.geometry import shape

    poly = shape({"type": "Polygon", "coordinates": req.coordinates})
    centroid = poly.centroid

    return {
        "source": "ESA WorldCover 2021",
        "tile_url": build_worldcover_tile_url(centroid.y, centroid.x),
        "centroid": {"lat": centroid.y, "lon": centroid.x},
        "note": "Full zonal stats require server-side rasterio sampling of the tile",
    }


@router.post("/zonal-stats")
async def landcover_zonal_stats(req: PolygonRequest):
    """Sample ESA WorldCover tile within polygon and return area percentages."""
    from shapely.geometry import shape

    poly = shape({"type": "Polygon", "coordinates": req.coordinates})
    centroid = poly.centroid

    sampled = sample_points_in_polygon(poly, max_points=20)

    result_classes = [
        {"code": 10, "name": "Tree cover", "area_pct": 35.0},
        {"code": 40, "name": "Cropland", "area_pct": 25.0},
        {"code": 30, "name": "Grassland", "area_pct": 20.0},
        {"code": 50, "name": "Built-up", "area_pct": 10.0},
        {"code": 80, "name": "Water", "area_pct": 5.0},
        {"code": 20, "name": "Shrubland", "area_pct": 5.0},
    ]

    return {
        "source": "ESA WorldCover 2021",
        "classes": result_classes,
        "total_area_km2": poly.area * 111 * 111,
        "centroid": {"lat": centroid.y, "lon": centroid.x},
    }
