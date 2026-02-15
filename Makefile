.PHONY: backend-install backend-dev backend-test frontend-install frontend-dev frontend-build docker-up docker-down

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
	@set -e; \
	if docker compose version >/dev/null 2>&1; then \
		docker compose -f docker/docker-compose.yml up --build; \
	elif command -v docker-compose >/dev/null 2>&1; then \
		docker-compose -f docker/docker-compose.yml up --build; \
	else \
		echo "Error: neither 'docker compose' nor 'docker-compose' is available."; \
		exit 1; \
	fi

docker-down:
	@set -e; \
	if docker compose version >/dev/null 2>&1; then \
		docker compose -f docker/docker-compose.yml down; \
	elif command -v docker-compose >/dev/null 2>&1; then \
		docker-compose -f docker/docker-compose.yml down; \
	else \
		echo "Error: neither 'docker compose' nor 'docker-compose' is available."; \
		exit 1; \
	fi
