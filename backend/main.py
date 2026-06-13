import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.api.router import router
from backend.config import get_settings
from backend.exceptions import (
    DownloadError,
    ExternalAPIError,
    NotFoundError,
    ProcessingError,
    SpaceEyeError,
    ValidationError,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.temp_dir, exist_ok=True)
    os.makedirs(os.path.join(settings.temp_dir, "downloads"), exist_ok=True)
    os.makedirs(os.path.join(settings.temp_dir, "cache"), exist=True)
    yield
    from backend.models.database import get_engine
    await get_engine().dispose()
    from backend.api.deps import close_http_client
    await close_http_client()


app = FastAPI(
    title="SpaceEye API",
    version="0.2.0",
    description="Satellite imagery search & processing for INPE catalog",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")

try:
    from prometheus_fastapi_instrumentator import Instrumentator

    Instrumentator().instrument(app).expose(app)
except ImportError:
    pass


@app.exception_handler(SpaceEyeError)
async def spaceeye_error_handler(request: Request, exc: SpaceEyeError):
    if isinstance(exc, ValidationError):
        return JSONResponse(status_code=400, content={"error": "Validation error", "detail": str(exc)})
    if isinstance(exc, NotFoundError):
        return JSONResponse(status_code=404, content={"error": "Not found", "detail": str(exc)})
    if isinstance(exc, ExternalAPIError):
        return JSONResponse(status_code=502, content={"error": "External service error", "detail": str(exc)})
    if isinstance(exc, ProcessingError):
        return JSONResponse(status_code=422, content={"error": "Processing error", "detail": str(exc)})
    if isinstance(exc, DownloadError):
        return JSONResponse(status_code=502, content={"error": "Download error", "detail": str(exc)})
    return JSONResponse(status_code=500, content={"error": "Internal error", "detail": str(exc)})


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if isinstance(exc, (HTTPException, RequestValidationError)):
        raise exc
    logger = logging.getLogger(__name__)
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error"},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Validation error", "errors": exc.errors()},
    )
