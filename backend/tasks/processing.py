import asyncio
import logging

from backend.config import get_settings
from backend.exceptions import DownloadError
from backend.services.processing import process_image
from backend.tasks.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(bind=True, max_retries=3, default_retry_delay=30)
def process_image_task(self, image_id: str, polygon_coords: list, product: str, band_urls: dict):
    async def run():
        async def update_progress(progress: int, phase: str):
            self.update_state(
                state="PROGRESS",
                meta={"progress": progress, "phase": phase},
            )

        result = await process_image(
            image_id=image_id,
            polygon_coords=polygon_coords,
            bands=band_urls,
            product_name=product,
            progress_callback=update_progress,
        )
        return result

    try:
        # Celery tasks are synchronous; asyncio.run() is the standard way
        # to bridge sync Celery workers with async application code.
        return asyncio.run(run())
    except (OSError, ConnectionError, TimeoutError, DownloadError) as exc:
        raise self.retry(exc=exc) from exc
    except Exception:
        logger.exception("Unexpected error in process_image_task")
        raise


@celery_app.task(bind=True, max_retries=2)
def compute_difference_task(self, task_id_a: str, task_id_b: str):
    """Compute NDVI difference: result_B - result_A, return colormap overlay."""
    settings = get_settings()
    import numpy as np
    import rasterio
    from celery.result import AsyncResult

    res_a = AsyncResult(task_id_a, app=celery_app)
    res_b = AsyncResult(task_id_b, app=celery_app)

    if res_a.state != "SUCCESS" or res_b.state != "SUCCESS":
        raise ValueError("Both tasks must be completed")

    path_a = res_a.result.get("geotiff_path") or res_a.result["path"]
    path_b = res_b.result.get("geotiff_path") or res_b.result["path"]

    with rasterio.open(path_a) as src_a, rasterio.open(path_b) as src_b:
        ndvi_a = src_a.read(1).astype(np.float32)
        ndvi_b = src_b.read(1).astype(np.float32)

        diff = ndvi_b - ndvi_a

        import os
        import tempfile

        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fd, out_path = tempfile.mkstemp(suffix=".png", dir=settings.temp_dir)
        os.close(fd)

        try:
            vmax = max(abs(np.nanmin(diff)), abs(np.nanmax(diff)), 0.1)
            plt.imsave(out_path, diff, cmap="RdBu_r", vmin=-vmax, vmax=vmax)

            bounds = src_b.bounds
            import pyproj

            transformer = pyproj.Transformer.from_crs(src_b.crs, "EPSG:4326", always_xy=True)
            left, bottom = transformer.transform(bounds.left, bounds.bottom)
            right, top = transformer.transform(bounds.right, bounds.top)
            wgs84_bounds = [[bottom, left], [top, right]]
        finally:
            plt.close("all")

    return {"path": out_path, "bounds": wgs84_bounds, "type": "diff"}
