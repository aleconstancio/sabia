#!/usr/bin/env python3
"""
Clean up processed raster caches older than TTL days.

Usage:
    python pipeline/cleanup.py --ttl 7 --cache-dir /tmp/horus/cache
    
Run via cron/systemd timer daily.
"""

import argparse
import logging
import os
import time
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger(__name__)


def cleanup_directory(cache_dir: str, ttl_days: int):
    cutoff = time.time() - (ttl_days * 86400)
    removed = 0
    size_freed = 0
    
    for f in Path(cache_dir).rglob("*"):
        if f.is_file() and f.suffix.lower() in (".tif", ".png", ".tiff", ".part"):
            mtime = f.stat().st_mtime
            if mtime < cutoff:
                size_freed += f.stat().st_size
                try:
                    f.unlink()
                    removed += 1
                except PermissionError:
                    pass
    
    return removed, size_freed


def main():
    parser = argparse.ArgumentParser(description="Clean cached rasters")
    parser.add_argument("--ttl", type=int, default=7, help="Days to keep cached files")
    parser.add_argument("--cache-dir", default="/tmp/horus/cache", help="Cache directory")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.cache_dir):
        logger.info("Cache directory %s does not exist. Nothing to clean.", args.cache_dir)
        return
    
    removed, size_freed = cleanup_directory(args.cache_dir, args.ttl)
    
    logger.info("Removed %d files (%.2f MB freed)", removed, size_freed / 1024 / 1024)


if __name__ == "__main__":
    main()