.PHONY: backend-install backend-dev backend-test frontend-install frontend-dev frontend-build docker-up docker-down

DOCKER_COMPOSE := $(shell if command -v docker-compose >/dev/null 2>&1; then echo docker-compose; else echo "docker compose"; fi)

backend-install:
	cd backend && python -m pip install -e .

backend-dev:
	cd backend && python -m uvicorn app.main:app --reload --port 8000

backend-test:
	cd backend && python -m pytest

frontend-install:
	cd frontend && npm install

frontend-dev:
	cd frontend && npm run dev

frontend-build:
	cd frontend && npm run build

docker-up:
	$(DOCKER_COMPOSE) -f docker/docker-compose.yml up --build

docker-down:
	$(DOCKER_COMPOSE) -f docker/docker-compose.yml down
