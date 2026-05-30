from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PolygonRequest(BaseModel):
    coordinates: list[list[list[float]]]
    collections: Optional[list[str]] = None
    date_from: Optional[str] = None
    date_to: Optional[str] = None
    max_cloud: Optional[float] = Field(default=None, ge=0, le=100)
    sort_by: str = Field(default="acquired_at", pattern="^(acquired_at|cloud_cover)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    limit: int = Field(default=50, le=100)
    offset: int = Field(default=0, ge=0)


class ImageResponse(BaseModel):
    id: str
    collection: str
    cloud_cover: Optional[float] = None
    acquired_at: datetime
    thumbnail_url: Optional[str] = None
    footprint: dict


class ImageSearchResponse(BaseModel):
    images: list[ImageResponse]
    total: int


class ProcessRequest(BaseModel):
    image_id: str
    coordinates: list[list[list[float]]]
    product: str = Field(pattern="^(NDVI|TCI|NDWI|SAVI|EVI|MSAVI2|VARI|MNDWI|CIR|NBR|NDMI)$")


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int = Field(default=0, ge=0, le=100)
    phase: str = ""
    result: Optional[dict] = None
    error: Optional[str] = None


class UfResponse(BaseModel):
    sigla: str


class CityResponse(BaseModel):
    nome: str
