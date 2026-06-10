import pytest


@pytest.fixture
def sample_raster_bands():
    """Create synthetic 10x10 raster bands for testing product computations."""
    import numpy as np
    np.random.seed(42)
    nir = np.random.uniform(0.1, 0.9, (10, 10)).astype(np.float32)
    red = np.random.uniform(0.05, 0.5, (10, 10)).astype(np.float32)
    green = np.random.uniform(0.05, 0.4, (10, 10)).astype(np.float32)
    blue = np.random.uniform(0.02, 0.3, (10, 10)).astype(np.float32)
    pan = np.random.uniform(0.1, 1.0, (10, 10)).astype(np.float32)
    return {"nir": nir, "red": red, "green": green, "blue": blue, "pan": pan}


@pytest.fixture
def sample_polygon():
    """A small polygon in Brazil (Natal area) for testing."""
    return [[[-35.2, -5.8], [-35.1, -5.8], [-35.1, -5.7], [-35.2, -5.7], [-35.2, -5.8]]]


@pytest.fixture
def mock_search_response():
    """Simulated PostGIS search response."""
    return [
        {
            "id": "CBERS4A_2025_001",
            "collection": "cbers4a",
            "cloud_cover": 12.5,
            "acquired_at": "2025-01-15T12:00:00Z",
            "thumbnail_url": "http://example.com/thumb.jpg",
            "footprint": {"type": "Polygon", "coordinates": [[[-35.0, -6.0], [-34.0, -6.0], [-34.0, -5.0], [-35.0, -5.0], [-35.0, -6.0]]]},
        },
        {
            "id": "SENTINEL2_2025_002",
            "collection": "sentinel2",
            "cloud_cover": 5.0,
            "acquired_at": "2025-01-20T12:00:00Z",
            "thumbnail_url": "http://example.com/thumb2.jpg",
            "footprint": {"type": "Polygon", "coordinates": [[[-35.0, -6.0], [-34.0, -6.0], [-34.0, -5.0], [-35.0, -5.0], [-35.0, -6.0]]]},
        },
    ]
