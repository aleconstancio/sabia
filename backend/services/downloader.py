import os
import asyncio
import aiohttp
from backend.exceptions import DownloadError


async def download_bands(
    image_id: str,
    bands: dict[str, str],
    temp_dir: str,
) -> dict[str, str | None]:
    download_dir = os.path.join(temp_dir, "downloads", image_id)
    os.makedirs(download_dir, exist_ok=True)

    filepaths: dict[str, str | None] = {}
    for band_name, url in bands.items():
        if url:
            filepaths[band_name] = os.path.join(download_dir, f"{band_name}_{image_id}.tif")
        else:
            filepaths[band_name] = None

    connector = aiohttp.TCPConnector(limit=4)
    timeout = aiohttp.ClientTimeout(total=600)

    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as session:
        tasks = []
        for band_name, url in bands.items():
            if url:
                tasks.append(_download_one(session, url, filepaths[band_name], band_name))

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, Exception):
                raise DownloadError(f"Band download failed: {result}")

    for band_name, filepath in filepaths.items():
        if filepath is None:
            continue
        if not os.path.exists(filepath) or os.path.getsize(filepath) < 1024:
            raise DownloadError(f"Missing or truncated file for band {band_name}: {filepath}")

    return filepaths


async def _download_one(
    session: aiohttp.ClientSession,
    url: str,
    filepath: str | None,
    band_name: str,
):
    if filepath is None:
        return

    temp_path = f"{filepath}.part"

    if os.path.exists(temp_path):
        os.remove(temp_path)
    if os.path.exists(filepath) and os.path.getsize(filepath) > 0:
        return

    async with session.get(url) as resp:
        resp.raise_for_status()
        with open(temp_path, "wb") as f:
            async for chunk in resp.content.iter_chunked(1024 * 1024):
                f.write(chunk)
            f.flush()
            os.fsync(f.fileno())

    os.replace(temp_path, filepath)
