# Vanilla Backend Console

Simple static UI for exercising the Coffee Optimiser backend end-to-end.

## Run backend

From repo root:

```bash
cp .env.example .env
alembic upgrade head
coffee api run
```

Backend default URL: `http://localhost:8000`

## Run UI

From repo root:

```bash
cd web-vanilla
python -m http.server 5173
```

Then open `http://localhost:5173`.

## Tested flows

- Ping `/health` and inspect API log.
- Register user, login, fetch `/api/v1/auth/me`, logout.
- Create brew with parameters JSON, list brews, fetch brew by id.
- Import CSV via file upload (`/api/v1/import/csv/upload`).
- Export CSV download (`/api/v1/export/csv/download`).
- Create/load optimisation study, ask suggestion, apply suggestion with score/failed.
- Fetch `/openapi.json` and open `/docs` link.
