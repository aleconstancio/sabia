import numpy as np
import pytest

from backend.domain.products import (
    ColorInfraredProduct,
    EviProduct,
    MndwiProduct,
    Msavi2Product,
    NbrProduct,
    NdmiProduct,
    NdviProduct,
    SaviProduct,
    TciProduct,
    VariProduct,
    get_product,
)
from backend.exceptions import ProcessingError


class TestProductRegistry:
    def test_all_products_registered(self):
        """All 11 products must be registered and retrievable."""
        expected = {
            "NDVI",
            "TCI",
            "NDWI",
            "SAVI",
            "EVI",
            "MSAVI2",
            "VARI",
            "MNDWI",
            "CIR",
            "NBR",
            "NDMI",
        }
        for name in expected:
            product = get_product(name)
            assert product is not None, f"{name} not registered"
            assert product.name == name, f"{name} has wrong name"

    def test_invalid_product_raises_error(self):
        with pytest.raises(ValueError, match="Unknown product"):
            get_product("INVALID")


class TestNdviProduct:
    def test_compute_returns_clipped_values(self, sample_raster_bands):
        product = NdviProduct()
        result = product.compute(sample_raster_bands)
        assert result.shape == (10, 10)
        assert result.dtype == np.float32
        assert np.all(result >= -1.0) and np.all(result <= 1.0)

    def test_ndvi_positive_for_vegetation(self):
        """NDVI should be positive when NIR > Red (healthy vegetation)."""
        bands = {
            "nir": np.ones((5, 5), dtype=np.float32) * 0.8,
            "red": np.ones((5, 5), dtype=np.float32) * 0.2,
        }
        result = NdviProduct().compute(bands)
        assert np.all(result > 0), "NDVI should be positive for NIR > Red"

    def test_ndvi_negative_for_non_vegetation(self):
        """NDVI should be negative when Red > NIR (bare soil/water)."""
        bands = {
            "nir": np.ones((5, 5), dtype=np.float32) * 0.2,
            "red": np.ones((5, 5), dtype=np.float32) * 0.8,
        }
        result = NdviProduct().compute(bands)
        assert np.all(result < 0), "NDVI should be negative for Red > NIR"

    def test_ndvi_zero_for_equal_bands(self):
        bands = {
            "nir": np.ones((5, 5), dtype=np.float32) * 0.5,
            "red": np.ones((5, 5), dtype=np.float32) * 0.5,
        }
        result = NdviProduct().compute(bands)
        assert np.allclose(result, 0), "NDVI should be 0 when NIR == Red"


class TestTciProduct:
    def test_compute_returns_uint8_rgb(self, sample_raster_bands):
        result = TciProduct().compute(sample_raster_bands)
        assert result.shape == (10, 10, 3)
        assert result.dtype == np.uint8

    def test_compute_raises_on_all_invalid(self):
        bands = {
            "red": np.zeros((5, 5), dtype=np.float32),
            "green": np.zeros((5, 5), dtype=np.float32),
            "blue": np.zeros((5, 5), dtype=np.float32),
        }
        with pytest.raises(ProcessingError, match="No valid pixels"):
            TciProduct().compute(bands)


class TestSaviProduct:
    def test_compute_returns_valid(self, sample_raster_bands):
        result = SaviProduct().compute(sample_raster_bands)
        assert result.shape == (10, 10)
        assert np.all(result >= -1.0) and np.all(result <= 1.0)

    def test_savi_lower_than_ndvi_for_sparse_vegetation(self):
        """SAVI should be slightly lower than NDVI in sparse vegetation due to soil adjustment."""
        bands = {
            "nir": np.ones((5, 5), dtype=np.float32) * 0.4,
            "red": np.ones((5, 5), dtype=np.float32) * 0.3,
        }
        ndvi = NdviProduct().compute(bands)
        savi = SaviProduct().compute(bands)
        assert np.all(savi <= ndvi), "SAVI should be <= NDVI (soil adjustment)"


class TestEviProduct:
    def test_compute_requires_blue_band(self):
        bands = {
            "nir": np.ones((5, 5), dtype=np.float32) * 0.8,
            "red": np.ones((5, 5), dtype=np.float32) * 0.2,
            "blue": np.ones((5, 5), dtype=np.float32) * 0.1,
        }
        result = EviProduct().compute(bands)
        assert result.shape == (5, 5)
        assert np.all(np.isfinite(result))


class TestMsavi2Product:
    def test_compute_returns_valid(self, sample_raster_bands):
        result = Msavi2Product().compute(sample_raster_bands)
        assert result.shape == (10, 10)
        assert np.all(np.isfinite(result))


class TestVariProduct:
    def test_compute_visible_only(self):
        """VARI should work with only visible bands (no NIR needed)."""
        bands = {
            "green": np.ones((5, 5), dtype=np.float32) * 0.3,
            "red": np.ones((5, 5), dtype=np.float32) * 0.2,
            "blue": np.ones((5, 5), dtype=np.float32) * 0.1,
        }
        result = VariProduct().compute(bands)
        assert result.shape == (5, 5)
        assert np.all(np.isfinite(result))


class TestMndwiProduct:
    def test_compute_requires_swir_bands(self):
        """MNDWI should raise when SWIR bands are unavailable."""
        bands = {
            "green": np.ones((5, 5), dtype=np.float32) * 0.3,
            "nir": np.ones((5, 5), dtype=np.float32) * 0.1,
        }
        with pytest.raises(ProcessingError, match="MNDWI requires green and SWIR"):
            MndwiProduct().compute(bands)

    def test_compute_with_swir(self):
        """MNDWI should work with green and SWIR1 bands."""
        bands = {
            "green": np.ones((5, 5), dtype=np.float32) * 0.3,
            "swir1": np.ones((5, 5), dtype=np.float32) * 0.1,
        }
        result = MndwiProduct().compute(bands)
        assert result.shape == (5, 5)
        assert np.all(result >= -1.0) and np.all(result <= 1.0)


class TestColorInfraredProduct:
    def test_compute_returns_uint8_rgb(self, sample_raster_bands):
        result = ColorInfraredProduct().compute(sample_raster_bands)
        assert result.shape == (10, 10, 3)
        assert result.dtype == np.uint8
        assert result.max() <= 255
        assert result.min() >= 0


class TestNbrProduct:
    def test_compute_requires_swir_bands(self):
        """NBR should raise when SWIR bands are unavailable."""
        bands = {
            "nir": np.ones((5, 5), dtype=np.float32) * 0.6,
            "red": np.ones((5, 5), dtype=np.float32) * 0.2,
        }
        with pytest.raises(ProcessingError, match="NBR requires NIR and SWIR"):
            NbrProduct().compute(bands)

    def test_compute_with_swir(self):
        """NBR should work with NIR and SWIR2 bands."""
        bands = {
            "nir": np.ones((5, 5), dtype=np.float32) * 0.6,
            "swir2": np.ones((5, 5), dtype=np.float32) * 0.2,
        }
        result = NbrProduct().compute(bands)
        assert result.shape == (5, 5)
        assert np.all(np.isfinite(result))


class TestNdmiProduct:
    def test_compute_returns_valid(self):
        """NDMI should work with NIR and SWIR1 bands."""
        bands = {
            "nir": np.ones((5, 5), dtype=np.float32) * 0.6,
            "swir1": np.ones((5, 5), dtype=np.float32) * 0.3,
        }
        result = NdmiProduct().compute(bands)
        assert result.shape == (5, 5)
        assert np.all(result >= -1.0) and np.all(result <= 1.0)
