# Coffee Optimiser Backend

Production-grade backend platform for Coffee Optimiser with REST API, persistent optimisation, database-backed storage, CLI workflows, CSV import/export, and Docker support.

## Features
- FastAPI REST API (`/api/v1`) with OpenAPI docs.
- PostgreSQL-first persistence (SQLite supported for local/dev/test).
- SQLAlchemy 2 + Alembic migrations.
- JWT authentication.
- Method-aware brew parameter validation via registry.
- Optuna ask/tell optimisation with persistent RDB storage.
- Typer CLI covering API-equivalent operations.
- CSV import/export (legacy compatibility) with idempotent import hash.
- Analytics endpoints for best brews and score trend.

## Quickstart (Docker)
```bash
docker compose up --build
```
API: `http://localhost:8000`
Docs: `http://localhost:8000/docs`

## Local setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
cp .env.example .env
# Optional: set DATABASE_URL to local Postgres if desired
alembic upgrade head
coffee api run
```

## Environment variables
See `.env.example`:
- `DATABASE_URL` (defaults to local SQLite for no-Docker startup)
- `JWT_SECRET`
- `JWT_EXPIRY_MINUTES`
- `APP_ENV`
- `DEMO_MODE`
- `FAILED_BREW_SCORE`
- `OPTUNA_SKIP_COMPATIBILITY_CHECK` (default `true` to tolerate existing Optuna schema-version mismatches)

### Database URL notes
- **Local without Docker**: keep `DATABASE_URL=sqlite:///./coffee.db`.
- **Local with Postgres on host**: use `postgresql+psycopg://coffee:coffee@localhost:5432/coffee`.
- **Docker Compose**: service config overrides to `postgresql+psycopg://coffee:coffee@postgres:5432/coffee` automatically.

## API examples
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H 'content-type: application/json' \
  -d '{"email":"me@example.com","password":"secret"}'

TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H 'content-type: application/json' \
  -d '{"email":"me@example.com","password":"secret"}' | jq -r .access_token)

curl -X POST http://localhost:8000/api/v1/brews \
  -H "Authorization: Bearer $TOKEN" \
  -H 'content-type: application/json' \
  -d '{"method":"aeropress","brewed_at":"2026-01-01T10:00:00Z","parameters":{"grind_size":10,"water_temp":91.0,"brew_time_sec":120}}'
```

## CLI examples
```bash
coffee db migrate
coffee user create --email me@example.com --password secret
coffee brew add --user-id <uuid> --method aeropress --brewed-at 2026-01-01T10:00:00+00:00 --parameters-json '{"grind_size":10,"water_temp":90.0,"brew_time_sec":120}'
coffee optimise suggest --user-id <uuid> --method aeropress
coffee import csv --user-id <uuid> --method aeropress --data ./aeropress.data.csv --meta ./aeropress.meta.csv
coffee export csv --user-id <uuid> --out ./exports
```

## Optimisation lifecycle
1. Create/ensure study scope (`user + method + optional bean/equipment/recipe`).
2. Request suggestion (`study.ask` + parameter registry distributions).
3. Brew with suggested params and record score.
4. Apply suggestion to tell Optuna trial result (`study.tell`).

## Legacy CSV import notes
- Existing files in repo (e.g. `aeropress.data.csv`) can be imported via API or CLI.
- Unknown columns are preserved in `extra_data`.
- Repeat imports are idempotent by deterministic brew hash.

## Quality checks
```bash
ruff check .
black --check .
mypy src
pytest
```

## Troubleshooting
- If `alembic upgrade head` fails with `failed to resolve host 'postgres'`, your local shell is using a Docker-only DB URL.
  - Fix by setting `DATABASE_URL=sqlite:///./coffee.db` (quickest) or `...@localhost:5432/...` for local Postgres.

- If Optuna reports schema/runtime compatibility errors, upgrade dependency (`pip install -U optuna`) and keep `OPTUNA_SKIP_COMPATIBILITY_CHECK=true` for mixed/local legacy DBs.
