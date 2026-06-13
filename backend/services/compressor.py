import asyncio
import logging
import os

import matplotlib
import numpy as np
import pyproj
import rasterio

matplotlib.use("Agg")
import matplotlib.pyplot as plt

from backend.config import get_settings

logger = logging.getLogger(__name__)


def _compress_ndvi_sync(raster_path: str) -> dict:
    """Synchronous NDVI compression (runs in thread)."""
    settings = get_settings()
    with rasterio.open(raster_path) as img:
        bounds = img.bounds
        crs = img.crs or "EPSG:4326"

        data = img.read(1).astype(np.float32)
        nodata = img.nodata
        if nodata is not None:
            data = np.where(data == nodata, np.nan, data)

        if np.all(np.isnan(data)):
            data = np.zeros_like(data)

        bounds2 = _bounds_to_wgs84(bounds, crs)

        cache_dir = os.path.join(settings.temp_dir, "cache")
        os.makedirs(cache_dir, exist_ok=True)
        temp_path = os.path.join(cache_dir, f"ndvi_{os.urandom(8).hex()}.png")

        plt.imsave(temp_path, data, cmap="RdYlGn", vmin=-1, vmax=1)

        return {"bounds": bounds2, "path": temp_path}


def _compress_tci_sync(raster_path: str) -> dict:
    """Synchronous TCI compression (runs in thread)."""
    settings = get_settings()
    with rasterio.open(raster_path) as img:
        bounds = img.bounds
        crs = img.crs or "EPSG:4326"

        red = img.read(1).astype(np.float32)
        green = img.read(2).astype(np.float32)
        blue = img.read(3).astype(np.float32)

        rgb = np.dstack((red, green, blue))
        nodata = img.nodata
        if nodata is not None:
            mask = np.all(np.isnan(rgb), axis=-1) | np.all(rgb == nodata, axis=-1)
        else:
            mask = np.all(rgb == 0, axis=-1)

        rgb_min = np.nanmin(rgb)
        rgb_max = np.nanmax(rgb)
        denom = max((rgb_max - rgb_min), 1e-10)
        rgb = ((rgb - rgb_min) / denom * 255).astype(np.uint8)
        rgb[mask] = [255, 255, 255]

        bounds2 = _bounds_to_wgs84(bounds, crs)

        cache_dir = os.path.join(settings.temp_dir, "cache")
        os.makedirs(cache_dir, exist_ok=True)
        temp_path = os.path.join(cache_dir, f"tci_{os.urandom(8).hex()}.png")

        plt.imsave(temp_path, rgb)

        return {"bounds": bounds2, "path": temp_path}


def _bounds_to_wgs84(bounds, src_crs):
    if str(src_crs).upper() == "EPSG:4326":
        return [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]

    try:
        transformer = pyproj.Transformer.from_crs(src_crs, "EPSG:4326", always_xy=True)
        left, bottom = transformer.transform(bounds.left, bounds.bottom)
        right, top = transformer.transform(bounds.right, bounds.top)
        return [[bottom, left], [top, right]]
    except Exception as e:
        logger.warning("CRS transformation failed: %s", e)
        return [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]


async def compress_to_png(raster_path: str, product_name: str) -> dict:
    """Compress GeoTIFF to PNG overlay. Runs CPU-heavy work in a thread."""
    if product_name in ("NDVI", "NDWI", "SAVI", "EVI", "MSAVI2", "VARI", "NDMI", "NBR"):
        return await asyncio.to_thread(_compress_ndvi_sync, raster_path)
    else:
        return await asyncio.to_thread(_compress_tci_sync, raster_path)
