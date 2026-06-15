#!/usr/bin/env bash
exec uv run uvicorn backend.main:app --reload --port 8000
