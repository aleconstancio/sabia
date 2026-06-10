import asyncio

from backend.tasks.celery_app import celery_app
from backend.domain.processing import process_image


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
        return asyncio.run(run())
    except (ConnectionError, TimeoutError, IOError) as exc:
        raise self.retry(exc=exc, max_retries=3)
    except Exception:
        raise


@celery_app.task(bind=True, max_retries=2)
def compute_difference_task(self, task_id_a: str, task_id_b: str):
    """Compute NDVI difference: result_B - result_A, return colormap overlay."""
    from celery.result import AsyncResult
    from backend.tasks.celery_app import celery_app
    import rasterio
    import numpy as np

    res_a = AsyncResult(task_id_a, app=celery_app)
    res_b = AsyncResult(task_id_b, app=celery_app)

    if res_a.state != "SUCCESS" or res_b.state != "SUCCESS":
        raise ValueError("Both tasks must be completed")

    path_a = res_a.result["path"]
    path_b = res_b.result["path"]

    with rasterio.open(path_a) as src_a, rasterio.open(path_b) as src_b:
        ndvi_a = src_a.read(1).astype(np.float32)
        ndvi_b = src_b.read(1).astype(np.float32)

        diff = ndvi_b - ndvi_a

        import tempfile, os
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib.colors import TwoSlopeNorm

        fd, out_path = tempfile.mkstemp(suffix=".png")
        os.close(fd)

        vmax = max(abs(np.nanmin(diff)), abs(np.nanmax(diff)), 0.1)
        plt.imsave(out_path, diff, cmap='RdBu_r', vmin=-vmax, vmax=vmax)

        bounds = src_b.bounds
        import pyproj
        transformer = pyproj.Transformer.from_crs(src_b.crs, "EPSG:4326", always_xy=True)
        left, bottom = transformer.transform(bounds.left, bounds.bottom)
        right, top = transformer.transform(bounds.right, bounds.top)
        wgs84_bounds = [[bottom, left], [top, right]]

    return {"path": out_path, "bounds": wgs84_bounds, "type": "diff"}
