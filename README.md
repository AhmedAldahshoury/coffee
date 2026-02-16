# Coffee Optimizer Platform

Interactive coffee optimization platform for AeroPress brewing with FastAPI + React.

## Features
- Legacy recommendation endpoint (`/api/v1/optimizer/recommendation`) preserved.
- Interactive human-in-the-loop Optuna runs.
- JWT authentication (`/auth/register`, `/auth/login`).
- SQLite/PostgreSQL persistence via SQLAlchemy + Alembic.
- SSE run event stream (`/optimizer/runs/{run_id}/events`).
- Leaderboard with filtering, sort, and pagination.

## Local setup

### Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
VITE_API_URL=http://localhost:8000/api/v1 npm run dev
```

If `VITE_API_URL` is not set, the frontend defaults to `http://localhost:8000/api/v1`.

## API base URL configuration
The frontend uses `VITE_API_URL` for:
- all REST requests (`axios` client)
- SSE run updates (`/optimizer/runs/{id}/events`)
- top-bar health badge ping (`GET /health`)

Example:
```bash
# Linux/macOS
export VITE_API_URL=http://localhost:8000/api/v1
npm run dev

# One-liner
VITE_API_URL=http://localhost:8000/api/v1 npm run dev
```

## Interactive optimization flow
1. Register/login and keep the JWT in localStorage.
2. Start run: `POST /api/v1/optimizer/runs/start`.
3. UI shows run id, status, progress, SSE/polling state, and event log.
4. Submit score when a trial is in `suggested` state.
5. Monitor leaderboard and dataset visibility from frontend status panels.


## Guided Brew Session
- Visit `/brew` for the guided workflow: **Setup → Brew timer → Rate → Save → Learn**.
- Apply current optimiser suggestions directly into session setup when a run is active.
- Submit score back to active optimiser trial and store session notes/taste tags in localStorage.

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
