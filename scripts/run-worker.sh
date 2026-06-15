#!/usr/bin/env bash
exec uv run celery -A backend.tasks.celery_app worker --loglevel=info --concurrency=4
