import logging

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db
from backend.api.downloads import router as downloads_router
from backend.api.geocoding import router as geocoding_router
from backend.api.images import router as images_router
from backend.api.processing import router as processing_router
from backend.api.reports import router as reports_router

logger = logging.getLogger(__name__)

router = APIRouter()

router.include_router(images_router, tags=["images"])
router.include_router(processing_router, tags=["processing"])
router.include_router(downloads_router, tags=["downloads"])
router.include_router(geocoding_router, tags=["geocoding"])
router.include_router(reports_router, tags=["reports"])

router.include_router(__import__("backend.api.analyses", fromlist=["router"]).router, prefix="/analyses", tags=["analyses"])
router.include_router(__import__("backend.api.profiles", fromlist=["router"]).router, prefix="/profiles", tags=["profiles"])
router.include_router(__import__("backend.api.weather", fromlist=["router"]).router, prefix="/weather", tags=["weather"])
router.include_router(__import__("backend.api.soil", fromlist=["router"]).router, prefix="/soil", tags=["soil"])
router.include_router(__import__("backend.api.landcover", fromlist=["router"]).router, prefix="/landcover", tags=["landcover"])
router.include_router(__import__("backend.api.esg", fromlist=["router"]).router, prefix="", tags=["esg"])
router.include_router(__import__("backend.api.tasks_api", fromlist=["router"]).router, prefix="/tasks", tags=["tasks"])


@router.get("/health")
async def health(db: AsyncSession = Depends(get_db)):
    from backend.api.health import check_database
    db_status = await check_database(db)
    if db_status.get("database") == "disconnected":
        return JSONResponse(status_code=503, content={"status": "error", **db_status})
    return {"status": "ok", **db_status}
