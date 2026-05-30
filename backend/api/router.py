import json
import os

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.deps import get_db
from backend.models.schemas import PolygonRequest, ProcessRequest

router = APIRouter()


@router.get("/health")
async def health():
    return {"status": "ok"}


@router.get("/collections")
async def list_collections_endpoint():
    from backend.domain.catalog import list_collections

    cols = list_collections()
    return [{"id": c.id, "bands": c.available_bands, "products": c.available_products} for c in cols]


@router.post("/images/search")
async def search_images(
    req: PolygonRequest,
    db: AsyncSession = Depends(get_db),
):
    from backend.repositories.images import find_images_by_polygon

    images, total = await find_images_by_polygon(db, req.coordinates, req.collections, req.limit, req.offset)
    return {"images": images, "total": total}


@router.get("/images/{image_id}")
async def get_image(image_id: str, db: AsyncSession = Depends(get_db)):
    from backend.repositories.images import get_image_by_id

    image = await get_image_by_id(db, image_id)
    if not image:
        raise HTTPException(404, "Image not found")
    return image


@router.post("/process")
async def process_image_endpoint(
    req: ProcessRequest,
    db: AsyncSession = Depends(get_db),
):
    from backend.repositories.images import get_image_by_id
    from backend.tasks.processing import process_image_task

    image = await get_image_by_id(db, req.image_id)
    if not image:
        raise HTTPException(404, "Image not found")

    task = process_image_task.delay(
        image_id=req.image_id,
        polygon_coords=req.coordinates,
        product=req.product,
        band_urls=image.get("metadata", {}).get("assets", {}),
    )

    return {"task_id": task.id}


@router.get("/tasks/{task_id}")
async def get_task_status(task_id: str):
    from celery.result import AsyncResult
    from backend.tasks.celery_app import celery_app

    result = AsyncResult(task_id, app=celery_app)

    if result.state == "PENDING":
        return {"task_id": task_id, "status": "pending", "progress": 0, "phase": ""}
    elif result.state == "PROGRESS":
        meta = result.info or {}
        return {
            "task_id": task_id,
            "status": "running",
            "progress": meta.get("progress", 50),
            "phase": meta.get("phase", "processing"),
        }
    elif result.state == "SUCCESS":
        return {
            "task_id": task_id,
            "status": "done",
            "progress": 100,
            "phase": "done",
            "result": result.result,
        }
    elif result.state == "FAILURE":
        return {
            "task_id": task_id,
            "status": "error",
            "progress": 0,
            "phase": "error",
            "error": str(result.info) if result.info else "Unknown error",
        }
    else:
        return {"task_id": task_id, "status": result.state.lower(), "progress": 0, "phase": ""}


@router.websocket("/tasks/{task_id}/ws")
async def task_websocket(websocket: WebSocket, task_id: str):
    import asyncio

    await websocket.accept()
    try:
        from celery.result import AsyncResult
        from backend.tasks.celery_app import celery_app

        while True:
            result = AsyncResult(task_id, app=celery_app)
            data = {"task_id": task_id, "status": result.state}

            if result.state == "PROGRESS" and result.info:
                data["progress"] = result.info.get("progress", 0)
                data["phase"] = result.info.get("phase", "")
            elif result.state == "SUCCESS":
                data["progress"] = 100
                data["phase"] = "done"
                data["result"] = result.result
            elif result.state == "FAILURE":
                data["error"] = str(result.info) if result.info else "Unknown error"

            await websocket.send_json(data)

            if result.state in ("SUCCESS", "FAILURE"):
                break

            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass


@router.get("/ibge/uf")
async def list_ufs():
    datasets_path = os.path.join(os.path.dirname(__file__), "..", "datasets", "cidades_brasileiras.json")
    with open(datasets_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return list(data.keys())


@router.get("/ibge/cidades/{uf}")
async def list_cidades(uf: str):
    datasets_path = os.path.join(os.path.dirname(__file__), "..", "datasets", "cidades_brasileiras.json")
    with open(datasets_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return list(data.get(uf.upper(), []))
