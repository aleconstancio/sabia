WORLDCOVER_CLASSES = {
    10: "Tree cover", 20: "Shrubland", 30: "Grassland",
    40: "Cropland", 50: "Built-up", 60: "Bare/sparse",
    70: "Snow/ice", 80: "Water", 90: "Wetland",
    95: "Mangroves", 100: "Moss/lichen",
}


def build_worldcover_tile_url(lat: float, lon: float) -> str:
    lat_band = "N" if lat >= 0 else "S"
    lon_band = "E" if lon >= 0 else "W"
    tile_x = int(abs(lat) / 10)
    tile_y = int(abs(lon) / 10)
    return f"https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/10m/{lat_band}{tile_x:02d}{lon_band}{tile_y:03d}.tif"


def sample_points_in_polygon(polygon, step=0.1, max_points=20):
    from shapely.geometry import shape
    import random

    bounds = polygon.bounds
    step = min(bounds[2] - bounds[0], bounds[3] - bounds[1], 0.5) or step
    points = []
    x = bounds[0]
    while x <= bounds[2]:
        y = bounds[1]
        while y <= bounds[3]:
            if polygon.contains(shape({"type": "Point", "coordinates": [x, y]})):
                points.append((y, x))
            y += max(step, 0.1)
        x += max(step, 0.1)
    return random.sample(points, min(len(points), max_points))
