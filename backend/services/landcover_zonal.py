import logging

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from shapely.geometry import shape

logger = logging.getLogger(__name__)

WORLDCOVER_CLASSES = {
    10: {"name": "Tree cover", "color": "#006400"},
    20: {"name": "Shrubland", "color": "#ffbb22"},
    30: {"name": "Grassland", "color": "#ffff4c"},
    40: {"name": "Cropland", "color": "#f096ff"},
    50: {"name": "Built-up", "color": "#fa0000"},
    60: {"name": "Bare / sparse vegetation", "color": "#b4b4b4"},
    70: {"name": "Snow and Ice", "color": "#f0f0f0"},
    80: {"name": "Permanent water bodies", "color": "#0064c8"},
    90: {"name": "Herbaceous wetland", "color": "#0096a0"},
    95: {"name": "Mangroves", "color": "#00cf75"},
    100: {"name": "Moss and lichen", "color": "#fae6a0"},
}


def compute_landcover_zonal(coords: list[list[list[float]]], tile_path: str) -> dict:
    """Sample ESA WorldCover tile within polygon and return class percentages."""
    try:
        poly = shape({"type": "Polygon", "coordinates": coords})

        with rasterio.open(tile_path) as src:
            mask = geometry_mask(
                [mapping(poly)],
                out_shape=(src.height, src.width),
                transform=src.transform,
                invert=True,
            )

            data = src.read(1)
            masked_data = data[mask]
            valid_pixels = masked_data[masked_data != 0]

            total = len(valid_pixels)
            if total == 0:
                return {"classes": [], "total_pixels": 0}

            classes = []
            for class_id in sorted(WORLDCOVER_CLASSES.keys()):
                count = int(np.sum(valid_pixels == class_id))
                if count > 0:
                    classes.append({
                        "id": class_id,
                        "name": WORLDCOVER_CLASSES[class_id]["name"],
                        "color": WORLDCOVER_CLASSES[class_id]["color"],
                        "pixels": count,
                        "percentage": round(count / total * 100, 1),
                    })

            return {
                "classes": classes,
                "total_pixels": int(total),
                "resolution": "10m",
                "source": "ESA WorldCover 2021",
            }
    except Exception as e:
        logger.warning("Landcover zonal computation failed: %s", e)
        return {"classes": [], "total_pixels": 0, "error": str(e)}


def mapping(geom):
    """Convert shapely geometry to GeoJSON mapping."""
    from shapely.geometry import mapping as _mapping
    return _mapping(geom)
