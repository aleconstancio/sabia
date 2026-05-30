from abc import ABC, abstractmethod
import numpy as np


class RasterProduct(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def compute(self, bands: dict[str, np.ndarray]) -> np.ndarray:
        ...


class NdviProduct(RasterProduct):
    name = "NDVI"

    def compute(self, bands: dict[str, np.ndarray]) -> np.ndarray:
        nir = bands["nir"].astype(np.float32)
        red = bands["red"].astype(np.float32)
        denominator = nir + red
        mask = denominator != 0
        ndvi = np.full_like(denominator, np.nan, dtype=np.float32)
        ndvi[mask] = (nir[mask] - red[mask]) / denominator[mask]
        return np.clip(ndvi, -1, 1)


class TciProduct(RasterProduct):
    name = "TCI"

    def compute(self, bands: dict[str, np.ndarray]) -> np.ndarray:
        red = bands["red"].astype(np.float32)
        green = bands["green"].astype(np.float32)
        blue = bands["blue"].astype(np.float32)

        invalid = (red <= 0) | (green <= 0) | (blue <= 0) | ~np.isfinite(red) | ~np.isfinite(green) | ~np.isfinite(blue)

        r = np.where(invalid, np.nan, red * 1.10)
        g = np.where(invalid, np.nan, green * 0.95)
        b = np.where(invalid, np.nan, blue * 0.55)

        rgb = np.stack([r, g, b], axis=-1)
        valid = rgb[np.isfinite(rgb)]

        if valid.size == 0:
            raise RuntimeError("No valid pixels in TCI computation")

        p2, p98 = np.percentile(valid, 2), np.percentile(valid, 98)
        rgb = np.clip(rgb, p2, p98)
        rgb = (rgb - p2) / max(p98 - p2, 1e-10)
        rgb = np.power(rgb, 1 / 1.8)
        rgb = np.nan_to_num(rgb)
        return (rgb * 255).astype(np.uint8)


class NdwiProduct(RasterProduct):
    name = "NDWI"

    def compute(self, bands: dict[str, np.ndarray]) -> np.ndarray:
        green = bands["green"].astype(np.float32)
        nir = bands["nir"].astype(np.float32)
        denominator = green + nir
        mask = denominator != 0
        ndwi = np.full_like(denominator, np.nan, dtype=np.float32)
        ndwi[mask] = (green[mask] - nir[mask]) / denominator[mask]
        return np.clip(ndwi, -1, 1)


_PRODUCTS: dict[str, RasterProduct] = {
    "NDVI": NdviProduct(),
    "TCI": TciProduct(),
    "NDWI": NdwiProduct(),
}


def get_product(name: str) -> RasterProduct:
    if name not in _PRODUCTS:
        raise ValueError(f"Unknown product: {name}. Available: {list(_PRODUCTS.keys())}")
    return _PRODUCTS[name]
