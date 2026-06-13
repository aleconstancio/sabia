from datetime import datetime

from pydantic import BaseModel, Field


class PolygonRequest(BaseModel):
    coordinates: list[list[list[float]]]
    # Product/collection validation happens at the domain layer (catalog.get_collection).
    collections: list[str] | None = None
    date_from: str | None = None
    date_to: str | None = None
    max_cloud: float | None = Field(default=None, ge=0, le=100)
    sort_by: str = Field(default="acquired_at", pattern="^(acquired_at|cloud_cover)$")
    sort_order: str = Field(default="desc", pattern="^(asc|desc)$")
    limit: int = Field(default=50, le=100)
    offset: int = Field(default=0, ge=0)


class ImageResponse(BaseModel):
    id: str
    collection: str
    cloud_cover: float | None = None
    acquired_at: datetime
    thumbnail_url: str | None = None
    footprint: dict


class ImageSearchResponse(BaseModel):
    images: list[ImageResponse]
    total: int


class ProcessRequest(BaseModel):
    image_id: str
    coordinates: list[list[list[float]]]
    # Product validation (allowed values) is enforced at the domain layer via catalog.get_collection.
    product: str = Field(pattern="^(NDVI|TCI|NDWI|SAVI|EVI|MSAVI2|VARI|MNDWI|CIR|NBR|NDMI)$")


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str
    progress: int = Field(default=0, ge=0, le=100)
    phase: str = ""
    result: dict | None = None
    error: str | None = None


class UfResponse(BaseModel):
    sigla: str


class CityResponse(BaseModel):
    nome: str


class ExportPdfRequest(BaseModel):
    task_id: str = Field(min_length=1)
    format: str = Field(default="pdf", pattern="^pdf$")
    overlays: list[str] = Field(max_length=20, default=[])


class ProcessBatchRequest(BaseModel):
    image_ids: list[str] = Field(max_length=20)
    coordinates: list[list[list[float]]]
    product: str = Field(pattern="^(NDVI|TCI|NDWI|SAVI|EVI|MSAVI2|VARI|MNDWI|CIR|NBR|NDMI)$")


class ComputeDifferenceRequest(BaseModel):
    task_id_a: str
    task_id_b: str
    coordinates: list[list[list[float]]]


class DownloadBatchRequest(BaseModel):
    task_ids: list[str] = Field(max_length=5)
