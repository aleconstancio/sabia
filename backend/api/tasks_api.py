from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()


@router.get("/{task_id}")
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
        result_data = result.result
        if isinstance(result_data, dict):
            result_data = {k: v for k, v in result_data.items() if k != "path"}
        return {
            "task_id": task_id,
            "status": "done",
            "progress": 100,
            "phase": "done",
            "result": result_data,
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


@router.websocket("/{task_id}/ws")
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
                result_data = result.result
                if isinstance(result_data, dict):
                    result_data = {k: v for k, v in result_data.items() if k != "path"}
                data["result"] = result_data
            elif result.state == "FAILURE":
                data["error"] = str(result.info) if result.info else "Unknown error"

            await websocket.send_json(data)

            if result.state in ("SUCCESS", "FAILURE"):
                break

            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
