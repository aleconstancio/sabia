import logging

import numpy as np
import rasterio
from rasterio.features import geometry_mask
from shapely.geometry import mapping, shape

from backend.services.worldcover import WORLDCOVER_CLASSES

logger = logging.getLogger(__name__)


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
                    classes.append(
                        {
                            "id": class_id,
                            "name": WORLDCOVER_CLASSES[class_id]["name"],
                            "color": WORLDCOVER_CLASSES[class_id]["color"],
                            "pixels": count,
                            "percentage": round(count / total * 100, 1),
                        }
                    )

            return {
                "classes": classes,
                "total_pixels": int(total),
                "resolution": "10m",
                "source": "ESA WorldCover 2021",
            }
    except Exception as e:
        logger.warning("Landcover zonal computation failed: %s", e)
        return {"classes": [], "total_pixels": 0, "error": str(e)}
