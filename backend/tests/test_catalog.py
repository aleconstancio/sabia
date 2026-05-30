from backend.domain.catalog import get_collection, list_collections


class TestCollectionRegistry:
    def test_all_collections_registered(self):
        collections = list_collections()
        ids = {c.id for c in collections}
        expected = {"cbers4a", "amazonia1", "sentinel2", "landsat8", "landsat9"}
        assert ids == expected, f"Missing collections: {expected - ids}"

    def test_get_existing_collection(self):
        c = get_collection("cbers4a")
        assert c is not None
        assert c.id == "cbers4a"

    def test_get_nonexistent_collection(self):
        assert get_collection("nonexistent") is None

    def test_cbers4a_has_expected_products(self):
        c = get_collection("cbers4a")
        assert "NDVI" in c.available_products
        assert "TCI" in c.available_products
        assert "SAVI" in c.available_products

    def test_sentinel2_no_pan_band(self):
        c = get_collection("sentinel2")
        assert "pan" not in c.available_bands
        assert "nir" in c.available_bands

    def test_landsat8_has_swir_bands(self):
        c = get_collection("landsat8")
        assert "swir1" in c.available_bands
        assert "swir2" in c.available_bands
        assert "pan" in c.available_bands

    def test_cbers4a_asset_url(self):
        c = get_collection("cbers4a")
        assets = {"red": {"href": "http://example.com/red.tif"},
                  "nir": {"href": "http://example.com/nir.tif"}}
        assert c.get_asset_url(assets, "red") == "http://example.com/red.tif"
        assert c.get_asset_url(assets, "pan") is None
