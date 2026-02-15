# Coffee Optimizer Platform

Interactive coffee optimization platform for AeroPress brewing with FastAPI + React.

## Features
- Legacy recommendation endpoint (`/api/v1/optimizer/recommendation`) preserved.
- Interactive human-in-the-loop Optuna runs.
- JWT authentication (`/auth/register`, `/auth/login`).
- PostgreSQL persistence via SQLAlchemy + Alembic.
- SSE run event stream (`/optimizer/runs/{run_id}/events`).
- Leaderboard with filtering, sort, and pagination.

## Local setup

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

## Interactive optimization flow
1. Register/login and keep the JWT in localStorage.
2. Start run: `POST /api/v1/optimizer/runs/start`.
3. Read latest suggested trial parameters.
4. Submit score: `POST /api/v1/optimizer/runs/{run_id}/submit_score`.
5. Observe progress stream from SSE endpoint.

## SSE payload
Each event includes:
- `trial_number`
- `best_score`
- `best_parameters`
- `last_trial_parameters`
- `last_trial_score`
- `run_status`

## Docker
```bash
make docker-up
```
If your Docker installation does not include the `docker compose` plugin, the Makefile automatically falls back to `docker-compose`.

This starts PostgreSQL, backend (with DB readiness wait + Alembic migration on startup), and frontend.
