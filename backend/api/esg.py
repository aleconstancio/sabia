import logging

from fastapi import APIRouter
from fastapi.responses import Response
from pydantic import BaseModel

from backend.exceptions import ExternalAPIError
from backend.models.schemas import PolygonRequest
from backend.services.carbon_stock import estimate_carbon_stock
from backend.services.esg_export import export_esg_csv_data, export_esg_json_data
from backend.services.fire_risk import calculate_fire_risk

logger = logging.getLogger(__name__)
router = APIRouter()


class ESGExportRequest(BaseModel):
    region: str = "unknown"
    coordinates: list[list[list[float]]]


@router.post("/carbon-stock")
async def carbon_stock(req: PolygonRequest):
    """Estimate carbon stock from soil organic carbon and NDVI biomass proxy."""
    try:
        return await estimate_carbon_stock(req.coordinates)
    except Exception as e:
        logger.warning("Carbon stock estimation failed: %s", e)
        raise ExternalAPIError(f"Carbon stock estimation failed: {e}") from e


@router.post("/fire-risk")
async def fire_risk(req: PolygonRequest):
    """Calculate fire risk from NBR trend and weather data."""
    try:
        return await calculate_fire_risk(req.coordinates)
    except Exception as e:
        logger.warning("Fire risk calculation failed: %s", e)
        raise ExternalAPIError(f"Fire risk calculation failed: {e}") from e


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
        logger.warning("ESG CSV export failed: %s", e)
        raise ExternalAPIError(f"ESG CSV export failed: {e}") from e


@router.post("/export/esg-json")
async def export_esg_json(data: ESGExportRequest):
    """Export full ESG data package as JSON."""
    try:
        return await export_esg_json_data(data.region, data.coordinates)
    except Exception as e:
        logger.warning("ESG JSON export failed: %s", e)
        raise ExternalAPIError(f"ESG JSON export failed: {e}") from e
