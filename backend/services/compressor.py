import os
import tempfile

import numpy as np
import pyproj
import rasterio
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def compress_to_png(raster_path: str, product_name: str) -> dict:
    with rasterio.open(raster_path) as img:
        bounds = img.bounds

        crs = img.crs
        if crs is None:
            crs = "EPSG:4326"

        if product_name == "NDVI":
            return _compress_ndvi(img, bounds, crs)
        elif product_name == "TCI":
            return _compress_tci(img, bounds, crs)
        elif product_name in ("NDWI", "NDDI"):
            return _compress_ndvi(img, bounds, crs)
        else:
            return _compress_tci(img, bounds, crs)


def _bounds_to_wgs84(bounds, src_crs):
    if str(src_crs).upper() == "EPSG:4326":
        return [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]

    try:
        transformer = pyproj.Transformer.from_crs(src_crs, "EPSG:4326", always_xy=True)
        left, bottom = transformer.transform(bounds.left, bounds.bottom)
        right, top = transformer.transform(bounds.right, bounds.top)
        return [[bottom, left], [top, right]]
    except Exception:
        return [[bounds.bottom, bounds.left], [bounds.top, bounds.right]]


def _compress_ndvi(img, bounds, crs):
    data = img.read(1).astype(np.float32)
    data = np.where(data == 0, np.nan, data)

    bounds2 = _bounds_to_wgs84(bounds, crs)

    fd, temp_path = tempfile.mkstemp(suffix=".png")
    os.close(fd)

    plt.imsave(temp_path, data, cmap="RdYlGn", vmin=-1, vmax=1)

    return {"bounds": bounds2, "path": temp_path}


def _compress_tci(img, bounds, crs):
    red = img.read(1).astype(np.float32)
    green = img.read(2).astype(np.float32)
    blue = img.read(3).astype(np.float32)

    rgb = np.dstack((red, green, blue))
    mask = np.all(rgb == 0, axis=-1)

    rgb_min = np.nanmin(rgb)
    rgb_max = np.nanmax(rgb)
    rgb = ((rgb - rgb_min) / max((rgb_max - rgb_min), 1e-10) * 255).astype(np.uint8)
    rgb[mask] = [255, 255, 255]

    bounds2 = _bounds_to_wgs84(bounds, crs)

    fd, temp_path = tempfile.mkstemp(suffix=".png")
    os.close(fd)

    plt.imsave(temp_path, rgb)

    return {"bounds": bounds2, "path": temp_path}
