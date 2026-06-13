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
