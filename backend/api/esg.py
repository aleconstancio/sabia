import logging

from fastapi import APIRouter
from fastapi.responses import JSONResponse

from backend.models.schemas import PolygonRequest

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/carbon-stock")
async def carbon_stock(req: PolygonRequest):
    """Estimate carbon stock from soil organic carbon and NDVI biomass proxy."""
    return JSONResponse(
        status_code=501,
        content={
            "error": "Not implemented",
            "message": (
                "Carbon stock estimation requires real NDVI data from satellite imagery, "
                "which is not yet integrated."
            ),
        },
    )


@router.post("/fire-risk")
async def fire_risk(req: PolygonRequest):
    """Calculate fire risk from NBR trend and weather data."""
    return JSONResponse(
        status_code=501,
        content={
            "error": "Not implemented",
            "message": (
                "Fire risk estimation requires real NBR (Normalized Burn Ratio) trend "
                "data from satellite imagery, which is not yet integrated."
            ),
        },
    )


@router.post("/export/esg-csv")
async def export_esg_csv(req: PolygonRequest):
    """Export ESG data as CSV for a module."""
    return JSONResponse(status_code=501, content={"error": "Not implemented", "message": "CSV export from real data not yet available"})


@router.post("/export/esg-json")
async def export_esg_json(req: PolygonRequest):
    """Export full ESG data package as JSON."""
    return JSONResponse(status_code=501, content={"error": "Not implemented", "message": "JSON export from real data not yet available"})
