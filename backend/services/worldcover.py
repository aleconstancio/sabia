"""WorldCover class definitions and utilities.

Single source of truth for ESA WorldCover 2021 class definitions.
"""

# Canonical WorldCover class definitions with name and color
WORLDCOVER_CLASSES: dict[int, dict[str, str]] = {
    10: {"name": "Tree cover", "color": "#006400"},
    20: {"name": "Shrubland", "color": "#ffbb22"},
    30: {"name": "Grassland", "color": "#ffff4c"},
    40: {"name": "Cropland", "color": "#f096ff"},
    50: {"name": "Built-up", "color": "#fa0000"},
    60: {"name": "Bare / sparse vegetation", "color": "#b4b4b4"},
    70: {"name": "Snow and Ice", "color": "#f0f0f0"},
    80: {"name": "Permanent water bodies", "color": "#0064c8"},
    90: {"name": "Herbaceous wetland", "color": "#0096a0"},
    95: {"name": "Mangroves", "color": "#00cf75"},
    100: {"name": "Moss and lichen", "color": "#fae6a0"},
}


def build_worldcover_tile_url(lat: float, lon: float) -> str:
    """Build the S3 URL for a WorldCover tile."""
    lat_band = "N" if lat >= 0 else "S"
    lon_band = "E" if lon >= 0 else "W"
    tile_x = int(abs(lat) / 10)
    tile_y = int(abs(lon) / 10)
    return f"https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/10m/{lat_band}{tile_x:02d}{lon_band}{tile_y:03d}.tif"
