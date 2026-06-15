"""WorldCover utilities for the landcover API endpoints.

This module provides a simplified interface to WorldCover classes for the API layer.
"""

from backend.services.worldcover import WORLDCOVER_CLASSES, build_worldcover_tile_url

# Export the simple name mapping for backward compatibility
WORLDCOVER_CLASS_NAMES: dict[int, str] = {
    class_id: info["name"] for class_id, info in WORLDCOVER_CLASSES.items()
}

__all__ = [
    "WORLDCOVER_CLASSES",
    "WORLDCOVER_CLASS_NAMES",
    "build_worldcover_tile_url",
]
