import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse, Response

from backend.models.schemas import PolygonRequest
from backend.services.carbon_stock import estimate_carbon_stock
from backend.services.esg_export import export_esg_csv_data, export_esg_json_data
from backend.services.fire_risk import calculate_fire_risk

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/carbon-stock")
async def carbon_stock(req: PolygonRequest):
    """Estimate carbon stock from soil organic carbon and NDVI biomass proxy."""
    try:
        result = await estimate_carbon_stock(req.coordinates)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/fire-risk")
async def fire_risk(req: PolygonRequest):
    """Calculate fire risk from NBR trend and weather data."""
    try:
        result = await calculate_fire_risk(req.coordinates)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/export/esg-csv")
async def export_esg_csv(req: PolygonRequest):
    """Export ESG data as CSV for a module."""
    try:
        csv_data = await export_esg_csv_data("esg", req.coordinates)
        return Response(
            content=csv_data,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=spaceeye-esg-export.csv"},
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@router.post("/export/esg-json")
async def export_esg_json(data: dict):
    """Export full ESG data package as JSON."""
    try:
        coordinates = data.get("coordinates", [])
        region = data.get("region", "unknown")
        result = await export_esg_json_data(region, coordinates)
        return result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
