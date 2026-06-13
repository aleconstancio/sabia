# Deployment Guide

> Production deployment, configuration, and operations for SpaceEye.

## Docker Deployment (Recommended)

### Prerequisites

- Docker 24+ and docker compose v2
- [INPE registered email](http://queimadas.dgi.inpe.br/catalogo/explore) (for satellite data access)

### Quick Deploy

```bash
# 1. Clone and configure
git clone https://github.com/your-org/spaceeye
cd spaceeye
cp .env.example .env

# 2. Edit .env with production values
#    - EMAIL_INPE: your registered email
#    - DATABASE_URL: production database URL
#    - CORS_ORIGINS: your domain(s)
#    - Strong database passwords

# 3. Start services
docker compose up -d --build

# 4. Initialize database
docker compose --profile setup run --rm seed

# 5. Run migrations
docker compose exec backend alembic upgrade head

# 6. Open
# Frontend: http://localhost
# API docs: http://localhost:8000/docs
```

### Services

| Service | Port | Description |
|---------|------|-------------|
| `frontend` (NGINX) | 80 | SvelteKit SPA |
| `backend` (FastAPI) | 8000 | API + Swagger docs |
| `worker` (Celery) | — | Background processing |
| `postgres` (PostGIS) | 5432 | Spatial database |
| `redis` | 6379 | Task queue broker |

### Seeding Additional Collections

```bash
docker compose exec backend python pipeline/ingest.py --collection sentinel2
docker compose exec backend python pipeline/ingest.py --collection landsat8
docker compose exec backend python pipeline/ingest.py --collection landsat9
```

### Updating

```bash
git pull
docker compose up -d --build
docker compose exec backend alembic upgrade head
```

## Environment Variables

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection (async) | `postgresql+asyncpg://user:pass@host:5432/spaceeye` |
| `REDIS_URL` | Redis connection | `redis://localhost:6379/0` |
| `CELERY_BROKER_URL` | Celery broker | `redis://localhost:6379/0` |
| `CELERY_RESULT_BACKEND` | Celery result store | `redis://localhost:6379/0` |
| `CORS_ORIGINS` | Allowed origins (JSON array) | `["http://localhost:5173"]` |
| `EMAIL_INPE` | INPE registered email | `user@example.com` |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `VITE_API_URL` | `http://localhost:8000/api` | Frontend API base URL |
| `TEMP_DIR` | `/tmp/spaceeye` | Temporary file storage |
| `CACHE_TTL_DAYS` | `7` | Days to keep processed rasters |

### Frontend Variables

| Variable | Description |
|----------|-------------|
| `VITE_API_URL` | Backend API URL (must be accessible from browser) |

## Manual Deployment (No Docker)

### Backend

```bash
# Prerequisites: Python 3.12+, PostgreSQL 16+PostGIS, Redis 7+, uv

# Install dependencies
uv sync --prod

# Database setup
createdb spaceeye
psql spaceeye -c "CREATE EXTENSION postgis"
uv run alembic upgrade head

# Run API server
uv run uvicorn backend.main:app \
  --host 0.0.0.0 \
  --port 8000 \
  --workers 4

# Run Celery worker
uv run celery -A backend.tasks.celery_app worker \
  --concurrency=4 \
  --loglevel=info
```

### Frontend

```bash
cd apps/spaceeye-web

# Build
bun install --frozen-lockfile
bun run build

# Serve with any static server
bunx serve build -p 80
# or
bunx vite preview --port 80
```

### NGINX Configuration

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # Frontend
    location / {
        root /path/to/apps/spaceeye-web/build;
        try_files $uri $uri/ /index.html;
    }

    # API proxy
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket support
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

## Database Migrations

### Alembic Setup

SpaceEye uses Alembic for schema management:

```bash
# Run all pending migrations
uv run alembic upgrade head

# Check current version
uv run alembic current

# Rollback one step
uv run alembic downgrade -1

# Create new migration
uv run alembic revision --autogenerate -m "add feature X"
```

### SQL Init vs Alembic

The project has two ways to create the initial schema — each for a different scenario:

- **SQL init files** (`sql/*.sql`): Mounted into the Postgres container at startup via `docker-entrypoint-initdb.d`. These run **only when the database is first created** (empty `pgdata` volume). Use these for fresh Docker deployments.
- **Alembic migrations** (`alembic/`): For **existing databases**. Run `alembic upgrade head` to apply the initial schema and any future migrations. Do not use SQL init files on an already-initialized database — they will not run.

### Initial Schema

For fresh databases, the migration `001_initial_schema` creates:
- `images` table with PostGIS spatial index
- `analyses` table with foreign key to images
- `region_profiles` table
- `processing_tasks` table
- `metric_timeseries` table
- `alert_rules` table
- `update_timestamp()` trigger function

## Backup and Restore

### Database Backup

```bash
# Docker
docker compose exec postgres pg_dump -U postgres spaceeye > backup_$(date +%Y%m%d).sql

# Manual
pg_dump -U postgres spaceeye > backup_$(date +%Y%m%d).sql
```

### Database Restore

```bash
# Docker
cat backup_20250101.sql | docker compose exec -T postgres psql -U postgres spaceeye

# Manual
psql -U postgres spaceeye < backup_20250101.sql
```

### Automated Backups

Add to crontab (daily at 3 AM):

```cron
0 3 * * * cd /opt/spaceeye && docker compose exec -T postgres pg_dump -U postgres spaceeye | gzip > /backups/spaceeye_$(date +\%Y\%m\%d).sql.gz
```

## Data Ingestion

### Initial Catalog Population

```bash
# CBERS-4A (Brazilian satellites)
docker compose exec backend python pipeline/ingest.py --collection cbers4a

# Sentinel-2 (Global)
docker compose exec backend python pipeline/ingest.py --collection sentinel2

# Landsat 8/9 (Global)
docker compose exec backend python pipeline/ingest.py --collection landsat8
docker compose exec backend python pipeline/ingest.py --collection landsat9
```

### Scheduled Ingestion

Add to crontab (daily at 2 AM):

```cron
0 2 * * * cd /opt/spaceeye && docker compose exec -T backend python pipeline/ingest.py --collection cbers4a >> /var/log/spaceeye-ingest.log 2>&1
```

### Cache Cleanup

Processed rasters are cached with a 7-day TTL. Run cleanup daily:

```cron
0 4 * * * cd /opt/spaceeye && docker compose exec -T backend python pipeline/cleanup.py >> /var/log/spaceeye-cleanup.log 2>&1
```

## Resource Requirements

### Minimum (1-2 concurrent users)

- 2 CPU cores, 4 GB RAM
- 10 GB disk (for cached rasters)

### Recommended (10+ concurrent users)

- 4 CPU cores, 8 GB RAM
- 50 GB SSD (for cached rasters)
- Celery workers scaled to 8-16

### Production (50+ concurrent users)

- 8+ CPU cores, 16+ GB RAM
- 200+ GB SSD
- Dedicated PostgreSQL server
- Redis on separate machine
- Celery workers: 16-32
- Load balancer in front of API servers

## Monitoring

### Health Checks

```bash
# API health
curl http://localhost:8000/api/health

# Database check
docker compose exec postgres pg_isready
```

### Logs

```bash
# All services
docker compose logs -f

# Specific service
docker compose logs -f backend
docker compose logs -f worker

# Last 100 lines
docker compose logs --tail 100 backend
```

### Celery Flower (Queue Monitoring)

```bash
docker compose exec backend celery -A backend.tasks.celery_app flower --port=5555
```

Access at http://localhost:5555

### Metrics

- FastAPI OpenAPI spec at `/openapi.json`
- Prometheus metrics can be added via `prometheus-fastapi-instrumentator`

## Security

### Production Checklist

- [ ] Strong database passwords (not `postgres:postgres`)
- [ ] `.env` not in version control
- [ ] CORS restricted to your domain
- [ ] HTTPS enabled (via reverse proxy)
- [ ] Rate limiting on API endpoints
- [ ] Authentication enabled (when implemented)
- [ ] Regular database backups
- [ ] Log monitoring

### SSL/TLS

Use a reverse proxy (NGINX, Caddy, Traefik) for TLS termination:

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # ... proxy configuration
}
```

## Troubleshooting

### "Connection refused" on database

```bash
# Check if PostgreSQL is running
docker compose ps postgres

# Check logs
docker compose logs postgres

# Verify connection
docker compose exec postgres psql -U postgres -d spaceeye -c "SELECT 1;"
```

### "Worker not processing tasks"

```bash
# Check worker status
docker compose ps worker

# Check worker logs
docker compose logs worker

# Restart worker
docker compose restart worker
```

### "Disk space exhausted"

```bash
# Check cache size
docker compose exec backend du -sh /tmp/spaceeye/cache/

# Clean old files
docker compose exec backend python pipeline/cleanup.py

# Remove old Docker images
docker system prune -f
```

### "Out of memory"

```bash
# Check worker concurrency
docker compose exec backend celery -A backend.tasks.celery_app inspect stats

# Reduce concurrency
# Edit docker-compose.yml: --concurrency=2
```
