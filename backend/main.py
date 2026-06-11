import os
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.api.router import router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    os.makedirs(settings.temp_dir, exist_ok=True)
    os.makedirs(os.path.join(settings.temp_dir, "downloads"), exist_ok=True)
    os.makedirs(os.path.join(settings.temp_dir, "cache"), exist_ok=True)
    yield
    from backend.api.deps import _http_client
    if _http_client is not None and not _http_client.is_closed:
        await _http_client.aclose()


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

from prometheus_fastapi_instrumentator import Instrumentator
Instrumentator().instrument(app).expose(app)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    import traceback
    logger = logging.getLogger(__name__)
    logger.error("Unhandled exception: %s", exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


from fastapi.exceptions import RequestValidationError


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": "Validation error", "errors": exc.errors()},
    )
