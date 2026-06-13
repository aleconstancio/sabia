#!/usr/bin/env bash
export LD_LIBRARY_PATH="/nix/store/chqq8mpmpyfi9kgsngya71akv5xicn03-gcc-15.2.0-lib/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"
exec uv run celery -A backend.tasks.celery_app worker --loglevel=info --concurrency=4
