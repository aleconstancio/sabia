from abc import ABC, abstractmethod
from typing import Optional


class Collection(ABC):
    @property
    @abstractmethod
    def id(self) -> str:
        ...

    @property
    @abstractmethod
    def stac_url(self) -> str:
        ...

    @property
    @abstractmethod
    def available_bands(self) -> list[str]:
        ...

    @property
    @abstractmethod
    def available_products(self) -> list[str]:
        ...

    @abstractmethod
    def get_asset_url(self, item_assets: dict, band: str) -> Optional[str]:
        ...


class Cbers4ACollection(Collection):
    id = "cbers4a"
    stac_url = "http://www.dgi.inpe.br/lgi-stac/collections/CBERS4A_WPM_L4_DN/items"
    available_bands = ["pan", "red", "green", "blue", "nir"]
    available_products = ["NDVI", "TCI", "NDWI", "SAVI", "EVI", "MSAVI2", "VARI", "MNDWI", "CIR"]

    def get_asset_url(self, item_assets: dict, band: str) -> Optional[str]:
        mapping = {"pan": "pan", "red": "red", "green": "green", "blue": "blue", "nir": "nir"}
        key = mapping.get(band)
        if key and key in item_assets:
            return item_assets[key]["href"]
        return None


class Amazonia1Collection(Collection):
    id = "amazonia1"
    stac_url = ""
    available_bands = ["red", "green", "blue", "nir"]
    available_products = ["TCI", "NDVI", "SAVI", "EVI", "MSAVI2", "VARI", "MNDWI", "CIR"]

    def get_asset_url(self, item_assets: dict, band: str) -> Optional[str]:
        return None


class Sentinel2Collection(Collection):
    id = "sentinel2"
    stac_url = "https://earth-search.aws.element84.com/v1/collections/sentinel-2-l2a/items"
    available_bands = ["red", "green", "blue", "nir"]
    available_products = ["NDVI", "TCI", "NDWI", "SAVI", "EVI", "MSAVI2", "VARI", "MNDWI", "CIR"]

    def get_asset_url(self, item_assets: dict, band: str) -> Optional[str]:
        mapping = {"red": "B04", "green": "B03", "blue": "B02", "nir": "B08"}
        key = mapping.get(band)
        if key and key in item_assets:
            return item_assets[key]["href"]
        return None


class Landsat8Collection(Collection):
    id = "landsat8"
    stac_url = "https://landsatlook.usgs.gov/stac-server/collections/landsat-c2l2-sr/items"
    available_bands = ["pan", "red", "green", "blue", "nir", "swir1", "swir2"]
    available_products = ["NDVI", "TCI", "NDWI", "SAVI", "EVI", "MSAVI2", "VARI", "MNDWI", "CIR", "NBR", "NDMI"]

    def get_asset_url(self, item_assets: dict, band: str) -> Optional[str]:
        mapping = {"red": "B4", "green": "B3", "blue": "B2", "nir": "B5", "pan": "B8", "swir1": "B6", "swir2": "B7"}
        key = mapping.get(band)
        if key and key in item_assets:
            return item_assets[key]["href"]
        return None


class Landsat9Collection(Collection):
    id = "landsat9"
    stac_url = "https://landsatlook.usgs.gov/stac-server/collections/landsat-c2l2-sr/items"
    available_bands = ["pan", "red", "green", "blue", "nir", "swir1", "swir2"]
    available_products = ["NDVI", "TCI", "NDWI", "SAVI", "EVI", "MSAVI2", "VARI", "MNDWI", "CIR", "NBR", "NDMI"]

    def get_asset_url(self, item_assets: dict, band: str) -> Optional[str]:
        mapping = {"red": "B4", "green": "B3", "blue": "B2", "nir": "B5", "pan": "B8", "swir1": "B6", "swir2": "B7"}
        key = mapping.get(band)
        if key and key in item_assets:
            return item_assets[key]["href"]
        return None


_COLLECTIONS: dict[str, Collection] = {
    "cbers4a": Cbers4ACollection(),
    "amazonia1": Amazonia1Collection(),
    "sentinel2": Sentinel2Collection(),
    "landsat8": Landsat8Collection(),
    "landsat9": Landsat9Collection(),
}


def get_collection(collection_id: str) -> Optional[Collection]:
    return _COLLECTIONS.get(collection_id)


def list_collections() -> list[Collection]:
    return list(_COLLECTIONS.values())
