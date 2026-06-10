# Deployment Guide

## Docker (Recommended)

### Prerequisites
- Docker 24+ and docker-compose v2
- An INPE-registered email (http://queimadas.dgi.inpe.br/catalogo/explore)

### Production Deploy

```bash
# 1. Clone & configure
git clone https://github.com/your-org/spaceeye
cd spaceeye
cp .env.example .env
# Edit .env: set EMAIL_INPE, CORS_ORIGINS, database passwords

# 2. Start everything (includes catalog seeding)
docker compose up -d --build
docker compose --profile setup run --rm seed

# 3. Open
# Frontend: http://localhost
# API docs: http://localhost:8000/docs
```

To seed additional collections:
```bash
docker compose exec backend python pipeline/ingest.py --collection sentinel2
docker compose exec backend python pipeline/ingest.py --collection landsat8
```

### Services

| Service | Port | Notes |
|---------|------|-------|
| `frontend` (NGINX) | 80 | Serves SvelteKit SPA |
| `backend` (FastAPI) | 8000 | API + Swagger docs |
| `worker` (Celery) | — | Background processing |
| `postgres` (PostGIS) | 5432 | Spatial database |
| `redis` | 6379 | Task queue broker |

### Updating

```bash
git pull
docker compose up -d --build
```

### Backup

```bash
# Database
docker compose exec postgres pg_dump -U postgres spaceeye > backup_$(date +%Y%m%d).sql

# Restore
cat backup_20250101.sql | docker compose exec -T postgres psql -U postgres spaceeye
```

### Scheduling Ingestion

Add to your host's crontab (runs daily at 2 AM):

```cron
0 2 * * * cd /opt/spaceeye && docker compose exec -T backend python pipeline/ingest.py --collection cbers4a >> /var/log/spaceeye-ingest.log 2>&1
```

## Manual (No Docker)

### Backend

```bash
# Prerequisites: Python 3.12+, PostgreSQL 16+PostGIS, Redis 7+, uv
uv sync --dev

# Database
createdb spaceeye
psql spaceeye -c "CREATE EXTENSION postgis"
psql spaceeye -f sql/001_init.sql

# Run
uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --workers 4

# Worker
uv run celery -A backend.tasks.celery_app worker --concurrency=4 --loglevel=info

# Scheduler (runs once, add to cron)
uv run python pipeline/ingest.py --collection cbers4a
```

### Frontend

```bash
cd apps/spaceeye-web
npm ci
npm run build

# Serve with any static server
npx serve build -p 80
```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `DATABASE_URL` | ✅ | `postgresql+asyncpg://postgres:postgres@localhost:5432/spaceeye` | Async database connection |
| `REDIS_URL` | ✅ | `redis://localhost:6379/0` | Redis connection |
| `CELERY_BROKER_URL` | ✅ | `redis://localhost:6379/0` | Celery broker |
| `CELERY_RESULT_BACKEND` | ✅ | `redis://localhost:6379/0` | Celery result store |
| `CORS_ORIGINS` | ✅ | `["http://localhost:5173","http://localhost:4173","http://localhost:80"]` | Allowed CORS origins (JSON array) |
| `email_inpe` | ⚠️ | — | INPE registered email (required for band downloads) |
| `VITE_API_URL` | ✅ | `http://localhost:8000/api` | Frontend-side API base URL |

## Resource Requirements

### Minimum (1-2 concurrent users)
- 2 CPU cores, 4 GB RAM
- 10 GB disk (for cached rasters)

### Recommended (10+ concurrent users)
- 4 CPU cores, 8 GB RAM
- 50 GB disk (SSD preferred)
- Celery workers scaled to 8-16

### Cache Behavior
- Processed rasters are stored in `/tmp/spaceeye/cache/` (or `TEMP_DIR`) with a 7-day TTL
- The cleanup script removes files older than the TTL
- Create a cron/systemd timer to run `python pipeline/cleanup.py` daily

## Monitoring

- FastAPI exposes `/docs` (Swagger) and `/openapi.json`
- Celery flower can be added for queue monitoring:
  ```bash
  docker compose exec flower celery -A backend.tasks.celery_app flower --port=5555
  ```
- Application logs go to stdout (docker-friendly)
