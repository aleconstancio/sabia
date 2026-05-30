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


class SaviProduct(RasterProduct):
    """Soil-Adjusted Vegetation Index: ((NIR - Red) / (NIR + Red + L)) * (1 + L), L=0.5
    Minimizes soil brightness influence in sparse vegetation."""
    name = "SAVI"
    def compute(self, bands: dict[str, np.ndarray]) -> np.ndarray:
        nir = bands["nir"].astype(np.float32)
        red = bands["red"].astype(np.float32)
        L = 0.5
        denominator = nir + red + L
        mask = denominator != 0
        savi = np.full_like(denominator, np.nan, dtype=np.float32)
        savi[mask] = ((nir[mask] - red[mask]) / denominator[mask]) * (1 + L)
        return np.clip(savi, -1, 1)


class EviProduct(RasterProduct):
    """Enhanced Vegetation Index: 2.5 * (NIR - Red) / (NIR + 6*Red - 7.5*Blue + 1)
    Optimizes vegetation signal in high-biomass areas."""
    name = "EVI"
    def compute(self, bands: dict[str, np.ndarray]) -> np.ndarray:
        nir = bands["nir"].astype(np.float32)
        red = bands["red"].astype(np.float32)
        blue = bands["blue"].astype(np.float32)
        denominator = nir + 6 * red - 7.5 * blue + 1
        mask = denominator != 0
        evi = np.full_like(denominator, np.nan, dtype=np.float32)
        evi[mask] = 2.5 * (nir[mask] - red[mask]) / denominator[mask]
        return np.clip(evi, -1, 1)


class Msavi2Product(RasterProduct):
    """Modified Soil-Adjusted Vegetation Index 2.
    (2*NIR + 1 - sqrt((2*NIR+1)^2 - 8*(NIR-Red))) / 2
    No soil adjustment factor needed."""
    name = "MSAVI2"
    def compute(self, bands: dict[str, np.ndarray]) -> np.ndarray:
        nir = bands["nir"].astype(np.float32)
        red = bands["red"].astype(np.float32)
        inner = 2 * nir + 1
        denom = 2
        mask = ~np.isnan(inner)
        msavi = np.full_like(nir, np.nan, dtype=np.float32)
        msavi[mask] = (inner[mask] - np.sqrt(np.maximum(inner[mask]**2 - 8 * (nir[mask] - red[mask]), 0))) / denom
        return np.clip(msavi, -1, 1)


class VariProduct(RasterProduct):
    """Visible Atmosphere Resistance Index: (Green - Red) / (Green + Red - Blue)
    Uses only visible bands — works without NIR."""
    name = "VARI"
    def compute(self, bands: dict[str, np.ndarray]) -> np.ndarray:
        green = bands["green"].astype(np.float32)
        red = bands["red"].astype(np.float32)
        blue = bands["blue"].astype(np.float32)
        denominator = green + red - blue
        mask = denominator != 0
        vari = np.full_like(denominator, np.nan, dtype=np.float32)
        vari[mask] = (green[mask] - red[mask]) / denominator[mask]
        return np.clip(vari, -1, 1)


class MndwiProduct(RasterProduct):
    """Modified Normalized Difference Water Index: (Green - SWIR1) / (Green + SWIR1)
    Better than NDWI for urban water bodies and turbid water."""
    name = "MNDWI"
    def compute(self, bands: dict[str, np.ndarray]) -> np.ndarray:
        green = bands["green"].astype(np.float32)
        swir = bands.get("swir1")
        if swir is None:
            swir = bands.get("nir")
        swir = np.array(swir).astype(np.float32) if swir is not None else green
        denominator = green + swir
        mask = denominator != 0
        mndwi = np.full_like(denominator, np.nan, dtype=np.float32)
        mndwi[mask] = (green[mask] - swir[mask]) / denominator[mask]
        return np.clip(mndwi, -1, 1)


class NbrProduct(RasterProduct):
    """Normalized Burn Ratio: (NIR - SWIR2) / (NIR + SWIR2)
    Standard index for burn severity mapping."""
    name = "NBR"
    def compute(self, bands: dict[str, np.ndarray]) -> np.ndarray:
        nir = bands["nir"].astype(np.float32)
        swir = bands.get("swir2") or bands.get("swir1") or bands.get("nir")
        swir = np.array(swir).astype(np.float32)
        denominator = nir + swir
        mask = denominator != 0
        nbr = np.full_like(denominator, np.nan, dtype=np.float32)
        nbr[mask] = (nir[mask] - swir[mask]) / denominator[mask]
        return np.clip(nbr, -1, 1)


class NdmiProduct(RasterProduct):
    """Normalized Difference Moisture Index: (NIR - SWIR1) / (NIR + SWIR1)
    Vegetation moisture content and drought monitoring."""
    name = "NDMI"
    def compute(self, bands: dict[str, np.ndarray]) -> np.ndarray:
        nir = bands["nir"].astype(np.float32)
        swir = bands.get("swir1") or bands.get("nir")
        swir = np.array(swir).astype(np.float32)
        denominator = nir + swir
        mask = denominator != 0
        ndmi = np.full_like(denominator, np.nan, dtype=np.float32)
        ndmi[mask] = (nir[mask] - swir[mask]) / denominator[mask]
        return np.clip(ndmi, -1, 1)


class ColorInfraredProduct(RasterProduct):
    """False-color composite: R=NIR, G=Red, B=Green.
    Healthy vegetation appears bright red — standard for vegetation analysis."""
    name = "CIR"
    def compute(self, bands: dict[str, np.ndarray]) -> np.ndarray:
        nir = bands["nir"].astype(np.float32)
        red = bands["red"].astype(np.float32)
        green = bands["green"].astype(np.float32)
        rgb = np.dstack((nir, red, green))
        p2, p98 = np.percentile(rgb[np.isfinite(rgb)], [2, 98])
        rgb = np.clip((rgb - p2) / max(p98 - p2, 1e-10), 0, 1)
        return (rgb * 255).astype(np.uint8)


_PRODUCTS: dict[str, RasterProduct] = {
    "NDVI": NdviProduct(),
    "TCI": TciProduct(),
    "NDWI": NdwiProduct(),
    "SAVI": SaviProduct(),
    "EVI": EviProduct(),
    "MSAVI2": Msavi2Product(),
    "VARI": VariProduct(),
    "MNDWI": MndwiProduct(),
    "CIR": ColorInfraredProduct(),
    "NBR": NbrProduct(),
    "NDMI": NdmiProduct(),
}


def get_product(name: str) -> RasterProduct:
    if name not in _PRODUCTS:
        raise ValueError(f"Unknown product: {name}. Available: {list(_PRODUCTS.keys())}")
    return _PRODUCTS[name]
