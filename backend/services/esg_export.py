import csv
import io
import logging
from datetime import UTC, datetime

from backend.services.carbon_stock import estimate_carbon_stock
from backend.services.fire_risk import calculate_fire_risk

logger = logging.getLogger(__name__)


async def export_esg_csv_data(module: str, coordinates: list[list[list[float]]]) -> str:
    """Generate ESG CSV export for a module."""
    carbon = await estimate_carbon_stock(coordinates)
    fire = await calculate_fire_risk(coordinates)

    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["module", "metric", "value", "unit", "timestamp"])
    writer.writeheader()

    now = datetime.now(UTC).isoformat()
    metrics = [
        ("vegetation", "carbon_stock_t_ha", carbon["carbon_stock_t_ha"], "t/ha"),
        ("vegetation", "biomass_estimate", carbon["biomass_estimate"], "t/ha"),
        ("vegetation", "soil_organic_carbon", carbon["soil_organic_carbon"], "t/ha"),
        ("vegetation", "ndvi_avg", carbon["ndvi_avg"], "index"),
        ("fire", "fire_risk_score", fire["fire_risk_score"], "/100"),
        ("fire", "risk_level", fire["risk_level"], "level"),
        ("fire", "drought_days", fire["factors"]["drought_days"], "days"),
    ]

    for mod, metric, value, unit in metrics:
        writer.writerow(
            {"module": mod, "metric": metric, "value": value, "unit": unit, "timestamp": now}
        )

    return output.getvalue()


async def export_esg_json_data(region: str, coordinates: list[list[list[float]]]) -> dict:
    """Generate full ESG JSON data package."""
    carbon = await estimate_carbon_stock(coordinates)
    fire = await calculate_fire_risk(coordinates)

    return {
        "region": region,
        "generated_at": datetime.now(UTC).isoformat(),
        "coordinates": coordinates,
        "modules": {
            "vegetation": {
                "carbon_stock": carbon,
                "alerts": [],
            },
            "water": {
                "ndwi_avg": 0.0,
                "water_area_pct": 0.0,
                "alerts": [],
            },
            "fire": {
                "fire_risk": fire,
                "alerts": [],
            },
            "soil": {
                "ph": 0.0,
                "organic_carbon": carbon.get("soil_organic_carbon", 0.0),
                "alerts": [],
            },
            "climate": {
                "temperature": carbon.get("weather_summary", {}).get("temperature"),
                "precipitation": carbon.get("weather_summary", {}).get("precipitation_7d"),
                "alerts": [],
            },
        },
    }
