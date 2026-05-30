import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import get_settings
from backend.api.router import router

settings = get_settings()

app = FastAPI(
    title="SpaceEye API",
    version="0.2.0",
    description="Satellite imagery search & processing for INPE catalog",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.on_event("startup")
async def startup():
    os.makedirs(settings.temp_dir, exist_ok=True)
    os.makedirs(os.path.join(settings.temp_dir, "downloads"), exist_ok=True)
    os.makedirs(os.path.join(settings.temp_dir, "cache"), exist_ok=True)
    os.makedirs(os.path.join(settings.temp_dir, "masks"), exist_ok=True)
