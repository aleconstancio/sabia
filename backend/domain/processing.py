import os
import asyncio
import numpy as np
import rasterio
from rasterio.mask import mask as rio_mask
from rasterio.warp import reproject, Resampling
from shapely.geometry import mapping, shape
import geopandas as gpd
from backend.config import get_settings
from backend.services.downloader import download_bands
from backend.services.raster_processor import crop_raster_to_polygon
from backend.services.compressor import compress_to_png

from backend.exceptions import ProcessingError


async def process_image(
    image_id: str,
    polygon_coords: list[list[list[float]]],
    bands: dict[str, str],
    product_name: str,
    progress_callback=None,
) -> dict:
    settings = get_settings()

    if progress_callback:
        await progress_callback(5, "downloading")

    downloaded = await download_bands(image_id, bands, settings.temp_dir)

    if progress_callback:
        await progress_callback(30, "cropping")

    output_path = os.path.join(settings.temp_dir, "cache", f"{product_name}_{image_id}.tif")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    result_path = _compute_product(downloaded, polygon_coords, product_name, output_path)

    if progress_callback:
        await progress_callback(80, "compressing")

    overlay = compress_to_png(result_path, product_name)

    if progress_callback:
        await progress_callback(100, "done")

    return overlay


def _compute_product(
    band_paths: dict[str, str],
    polygon_coords: list[list[list[float]]],
    product_name: str,
    output_path: str,
) -> str:
    from backend.domain.products import get_product

    product = get_product(product_name)

    # Edge case detection
    poly = shape({"type": "Polygon", "coordinates": polygon_coords})
    from pyproj import Geod
    g = Geod(ellps="WGS84")
    poly_area_m2, _ = g.geometry_area_perimeter(poly)
    poly_area_km2 = abs(poly_area_m2) / 1_000_000
    if poly_area_km2 < 0.0001:
        raise ProcessingError("Polygon is too small. Minimum area: 0.0001 km²")
    if poly_area_km2 > 10000:
        raise ProcessingError("Polygon is too large. Maximum area: 10,000 km²")

    band_data = {}
    transform = None
    crs = None
    geom = None

    for band_name, filepath in band_paths.items():
        if filepath is None:
            continue
        with rasterio.open(filepath) as src:
            if transform is None:
                transform = src.transform
                crs = src.crs

            user_polygon_gdf = gpd.GeoDataFrame(
                geometry=[mapping({"type": "Polygon", "coordinates": polygon_coords})],
                crs="EPSG:4326",
            )
            if user_polygon_gdf.crs != src.crs:
                user_polygon_gdf = user_polygon_gdf.to_crs(src.crs)

            geom_mapping = mapping(user_polygon_gdf.geometry.iloc[0])
            cropped, _ = rio_mask(src, [geom_mapping], crop=True, filled=False)
            band_data[band_name] = cropped[0]
            geom = [geom_mapping]

    if geom is None:
        raise RuntimeError("No valid bands to process")

    if "pan" in band_paths:
        pan_path = band_paths["pan"]
        if pan_path and any(b in band_data for b in ("red", "nir", "green", "blue")):
            with rasterio.open(pan_path) as pan_src:
                pan_crop, _ = rio_mask(pan_src, geom, crop=True, nodata=0)
                pan_data = pan_crop[0].astype(np.float32)

            band_resampled = set()
            for band_name in ("red", "nir", "green", "blue"):
                if band_name not in band_data or band_name in band_resampled:
                    continue
                bpath = band_paths.get(band_name)
                if not bpath:
                    continue
                resampled = np.zeros_like(pan_data, dtype=np.float32)
                with rasterio.open(bpath) as src:
                    reproject(
                        source=rasterio.band(src, 1),
                        destination=resampled,
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=pan_src.transform,
                        dst_crs=pan_src.crs,
                        resampling=Resampling.bilinear,
                    )
                band_data[band_name] = resampled
                band_resampled.add(band_name)

            soma = sum(band_data[b] for b in band_data if b != "pan")
            mask_soma = soma != 0
            for bname in list(band_data.keys()):
                if bname == "pan":
                    continue
                ps = np.zeros_like(pan_data)
                ps[mask_soma] = (band_data[bname][mask_soma] / soma[mask_soma]) * pan_data[mask_soma]
                band_data[bname] = ps

    band_data_for_product = {k: v for k, v in band_data.items() if k != "pan"}

    result = product.compute(band_data_for_product)

    if result.ndim == 3:
        count = result.shape[2]
        dtype = rasterio.uint8
        height, width = result.shape[0], result.shape[1]
    else:
        count = 1
        dtype = rasterio.float32
        height, width = result.shape

    profile = {
        "driver": "GTiff",
        "dtype": dtype,
        "count": count if result.ndim == 3 else 1,
        "height": height,
        "width": width,
        "crs": crs,
        "transform": transform,
        "compress": "lzw",
    }

    with rasterio.open(output_path, "w", **profile) as dst:
        if result.ndim == 3:
            rgb_uint8 = np.moveaxis(result, -1, 0)
            dst.write(rgb_uint8)
        else:
            dst.write(result, 1)

    return output_path
