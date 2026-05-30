.PHONY: dev-backend dev-frontend dev-worker dev-db lint check test clean

dev-db:
	docker compose up -d postgres redis

dev-backend:
	uvicorn backend.main:app --reload --port 8000

dev-worker:
	celery -A backend.tasks.celery_app worker --loglevel=info --concurrency=4

dev-frontend:
	cd apps/spaceeye-web && npm run dev

lint:
	cd apps/spaceeye-web && npx svelte-check --tsconfig ./tsconfig.json

check: lint

test:
	cd apps/spaceeye-web && npm run check || true

clean:
	rm -rf apps/spaceeye-web/build
	rm -rf apps/spaceeye-web/.svelte-kit
	rm -rf apps/spaceeye-web/node_modules
