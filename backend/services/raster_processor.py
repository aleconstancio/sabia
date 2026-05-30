import numpy as np
import rasterio
from rasterio.mask import mask
from shapely.geometry import mapping
import geopandas as gpd
from typing import Optional


def crop_raster_to_polygon(
    raster_path: str,
    polygon_coords: list[list[list[float]]],
    nodata: Optional[float] = None,
) -> tuple[np.ndarray, dict]:
    with rasterio.open(raster_path) as src:
        user_gdf = gpd.GeoDataFrame(
            geometry=[mapping({"type": "Polygon", "coordinates": polygon_coords})],
            crs="EPSG:4326",
        )
        if user_gdf.crs != src.crs:
            user_gdf = user_gdf.to_crs(src.crs)

        geom = [mapping(user_gdf.geometry.iloc[0])]
        kwargs: dict = {"crop": True, "filled": False}
        if nodata is not None:
            kwargs["nodata"] = nodata

        cropped, transform = mask(src, geom, **kwargs)
        profile = src.profile.copy()
        profile.update({
            "height": cropped.shape[1],
            "width": cropped.shape[2],
            "transform": transform,
        })

        return cropped, profile
