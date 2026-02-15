.PHONY: backend-install backend-dev backend-test frontend-install frontend-dev frontend-build docker-up docker-down

backend-install:
	cd backend && pip install -e .

backend-dev:
	cd backend && uvicorn app.main:app --reload --port 8000

backend-test:
	cd backend && pytest

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

docker-up:
	docker compose -f docker/docker-compose.yml up --build

docker-down:
	docker compose -f docker/docker-compose.yml down
