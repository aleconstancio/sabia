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
    except Exception as exc:
        raise self.retry(exc=exc)
