# Architecture

## Backend
- FastAPI app with modular layers: routers, services, repositories, schemas, core, config.
- Route handlers are orchestration-only.
- Service layer encapsulates all optimization business logic and Optuna orchestration.
- CSV repository abstracts data access.
- Global settings from environment via Pydantic Settings.
- Structured logging and centralized exception mapping.

## Frontend
- React + TypeScript + Vite.
- Feature-first folder structure for optimizer domain.
- API access centralized in API client modules.
- React Query handles server-state mutations.
- Zustand handles UI state (theme mode).
- Routing prepared for future feature modules.

## Deployment
- Independent Dockerfiles for backend and frontend.
- Compose stack for integrated local deployment.
