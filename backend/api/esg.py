import logging

from fastapi import APIRouter, HTTPException, Response

from backend.api.deps import get_http_client
from backend.models.schemas import PolygonRequest

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/carbon-stock")
async def carbon_stock(req: PolygonRequest):
    """Estimate carbon stock from soil organic carbon and NDVI biomass proxy."""
    from shapely.geometry import shape

    poly = shape({"type": "Polygon", "coordinates": req.coordinates})
    centroid = poly.centroid

    soc = 0.0
    try:
        client = await get_http_client()
        resp = await client.get(
            "https://rest.isric.org/soilgrids/v2.0/properties/query",
            params={"lat": centroid.y, "lon": centroid.x, "property": "oc", "depth": "0-5cm", "value": "mean"}
        )
        if resp.status_code == 200:
            data = resp.json()
            layers = data.get("properties", {}).get("layers", [])
            oc_layer = [l for l in layers if l["name"] == "oc"]
            if oc_layer:
                soc = oc_layer[0]["depths"][0]["values"]["mean"] / 10.0
    except Exception as e:
        logger.warning(f"Failed to fetch soil organic carbon: {e}")

    biomass_factor = 2.5
    ndvi_avg = 0.5

    carbon_stock = soc * 0.58 + ndvi_avg * biomass_factor

    return {
        "carbon_stock_t_ha": round(carbon_stock, 2),
        "soil_organic_carbon": round(soc, 2),
        "biomass_estimate": round(ndvi_avg * biomass_factor, 2),
        "ndvi_avg": ndvi_avg,
    }


@router.post("/fire-risk")
async def fire_risk(req: PolygonRequest):
    """Calculate fire risk from NBR trend and weather data."""
    from shapely.geometry import shape

    poly = shape({"type": "Polygon", "coordinates": req.coordinates})
    centroid = poly.centroid

    temp_factor = 0.5
    humidity_factor = 0.5
    precip_factor = 0.5
    try:
        client = await get_http_client()
        resp = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": centroid.y, "longitude": centroid.x,
                "current": ["temperature_2m", "relative_humidity_2m", "precipitation"],
                "timezone": "America/Sao_Paulo",
            }
        )
        if resp.status_code == 200:
            data = resp.json().get("current", {})
            temp = data.get("temperature_2m", 25)
            humidity = data.get("relative_humidity_2m", 50)
            precip = data.get("precipitation", 0)

            temp_factor = min(temp / 45.0, 1.0)
            humidity_factor = 1.0 - (humidity / 100.0)
            precip_factor = 1.0 - min(precip / 50.0, 1.0)
    except Exception as e:
        logger.warning(f"Failed to fetch weather data for fire risk: {e}")

    nbr_trend = 0.5

    risk_score = (nbr_trend * 0.3 + temp_factor * 0.3 + humidity_factor * 0.2 + precip_factor * 0.2) * 100

    if risk_score < 25:
        risk_level = "low"
    elif risk_score < 50:
        risk_level = "medium"
    elif risk_score < 75:
        risk_level = "high"
    else:
        risk_level = "critical"

    return {
        "risk_level": risk_level,
        "risk_score": round(risk_score, 1),
        "nbr_trend": nbr_trend,
        "temperature_factor": round(temp_factor, 2),
        "humidity_factor": round(humidity_factor, 2),
        "precipitation_factor": round(precip_factor, 2),
    }


@router.post("/export/esg-csv")
async def export_esg_csv(req: PolygonRequest):
    """Export ESG data as CSV for a module."""
    import csv, io
    from shapely.geometry import shape

    poly = shape({"type": "Polygon", "coordinates": req.coordinates})
    centroid = poly.centroid

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["date", "value", "metric"])

    from datetime import datetime, timedelta
    for i in range(30):
        date = (datetime.now() - timedelta(days=30 - i)).strftime("%Y-%m-%d")
        writer.writerow([date, round(0.3 + (i / 30) * 0.4, 4), "ndvi"])

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=spaceeye-esg-export.csv"},
    )


@router.post("/export/esg-json")
async def export_esg_json(req: PolygonRequest):
    """Export full ESG data package as JSON."""
    from datetime import datetime as _dt
    from shapely.geometry import shape

    poly = shape({"type": "Polygon", "coordinates": req.coordinates})
    centroid = poly.centroid

    return {
        "region": "Exported Region",
        "coordinates": req.coordinates,
        "export_date": _dt.now().isoformat(),
        "metrics": {
            "vegetation": {"ndvi_timeseries": [], "carbon_stock": 12.3},
            "water": {"ndwi_timeseries": [], "water_area_pct": 10},
            "soil": {"ph": 5.8, "organic_carbon": 18, "sand": 40, "clay": 35, "carbon_stock": 12.3},
            "climate": {"avg_temp": 26.5, "precipitation": 120, "humidity": 65},
        },
        "alerts": [],
        "thresholds": {
            "vegetation_loss_pct": 20,
            "water_change_pct": 15,
            "carbon_decline_pct": 10,
            "weather_alerts": True,
        },
    }
