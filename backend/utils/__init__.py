def compute_centroid(coords: list[list[list[float]]]) -> tuple[float, float]:
    """Compute centroid of a polygon from coordinate rings.

    Returns (latitude, longitude) tuple.
    """
    all_lons = []
    all_lats = []
    for ring in coords:
        for lon, lat in ring:
            all_lons.append(lon)
            all_lats.append(lat)
    return sum(all_lats) / len(all_lats), sum(all_lons) / len(all_lons)


def _summarize_weather(data: dict) -> dict | None:
    if not data:
        return None
    current = data.get("current", {})
    return {
        "temperature": current.get("temperature_2m"),
        "humidity": current.get("relative_humidity_2m"),
        "precipitation": current.get("precipitation"),
        "weather_code": current.get("weather_code"),
    }


def _summarize_soil(data: dict) -> dict | None:
    if not data:
        return None
    layers = data.get("properties", {}).get("layers", [])
    summary = {}
    for layer in layers:
        name = layer.get("name")
        if name and layer.get("depths"):
            summary[name] = layer["depths"][0].get("values", {}).get("mean")
    return summary
