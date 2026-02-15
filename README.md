# Coffee Optimizer Platform

This repository is now organized as a production-ready full-stack platform.

## Structure

- `backend/` FastAPI REST API and business services.
- `frontend/` React + TypeScript web UI.
- `docker/` Full-stack compose deployment.
- `docs/` Architecture and migration documentation.

## Quick start

### Backend
```bash
cp backend/.env.example backend/.env
make backend-install
make backend-dev
# or: cd backend && python -m pip install -r requirements.txt
```

### Frontend
```bash
cp frontend/.env.example frontend/.env
make frontend-install
make frontend-dev
```

If the UI shows network/CORS errors while backend is running, ensure `backend/.env` includes both `http://localhost:5173` and `http://127.0.0.1:5173` in `CORS_ORIGINS`.

### Full stack via Docker
```bash
make docker-up
```

## API docs
After backend startup, OpenAPI docs are available at:

- `http://localhost:8000/api/v1/docs`

## Migration notes
Legacy CLI entrypoints were removed and replaced with a service-driven API architecture.
Business logic is now isolated in `backend/app/services/optimizer_service.py` and consumed through REST.
The frontend consumes this API through a typed client layer.
