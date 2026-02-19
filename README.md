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
- `APP_ENV` (`local`/`production`; production enforces strict secret checks)
- `DATABASE_URL` (defaults to local SQLite for no-Docker startup)
- `JWT_SECRET` (**required in production**, fail-fast if unset/default)
- `JWT_ALGORITHM`
- `JWT_EXPIRY_MINUTES`
- `DEMO_MODE`
- `FAILED_BREW_SCORE`
- `LOG_LEVEL`
- `CORS_ALLOWED_ORIGINS` (comma-separated list, default empty = deny by default)
- `ENABLE_REQUEST_ID_MIDDLEWARE`
- `HASH_TIME_COST`, `HASH_MEMORY_COST`, `HASH_PARALLELISM` (Argon2 settings)
- `OPTUNA_SKIP_COMPATIBILITY_CHECK` (default `true` to tolerate existing Optuna schema-version mismatches)

### Database URL notes
- **Local without Docker**: keep `DATABASE_URL=sqlite:///./coffee.db`.
- **Local with Postgres on host**: use `postgresql+psycopg://coffee:coffee@localhost:5432/coffee`.
- **Docker Compose**: service config overrides to `postgresql+psycopg://coffee:coffee@postgres:5432/coffee` automatically.

## Production deployment checklist
- Set `APP_ENV=production`.
- Provide a strong `JWT_SECRET` (do not use `change-me` or `dev-secret`).
- Set `DATABASE_URL` to managed Postgres and run `alembic upgrade head`.
- Set explicit `CORS_ALLOWED_ORIGINS` for your frontend origins.
- Tune `LOG_LEVEL` and aggregate structured JSON logs.
- Keep request tracing enabled (`ENABLE_REQUEST_ID_MIDDLEWARE=true`).
- Review Argon2 settings (`HASH_TIME_COST`, `HASH_MEMORY_COST`, `HASH_PARALLELISM`) for your infrastructure.
- Do not use docker-compose example credentials in production.
- Configure HTTPS/TLS at ingress/load balancer.
- Auth rate limiting is not yet implemented server-side; enforce minimal rate limits at gateway/WAF/reverse proxy.

## Run Vanilla UI
```bash
cd web-vanilla
python -m http.server 5173
```
Open `http://localhost:5173`, set API base URL (default `http://localhost:8000`), and use the Backend Console tabs to exercise auth, brews, import/export, optimisation, and health/meta endpoints.

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

## Brew method profile endpoints
- `GET /api/v1/methods`: list available methods, variants, and schema versions.
- `GET /api/v1/methods/{method_id}`: return full parameter schemas for all variants under a method.
- `GET /api/v1/methods/{method_id}/{variant_id}`: return the full parameter schema for one variant.

## CLI examples
```bash
coffee db migrate
coffee user create --email me@example.com --password secret
coffee brew add --user-id <uuid> --method aeropress --brewed-at 2026-01-01T10:00:00+00:00 --parameters-json '{"grind_size":10,"water_temp":90.0,"brew_time_sec":120}'
coffee optimise suggest --user-id <uuid> --method-id aeropress --variant-id aeropress_standard
coffee import csv --user-id <uuid> --method aeropress --data ./aeropress.data.csv --meta ./aeropress.meta.csv
coffee export csv --user-id <uuid> --out ./exports
```

## Optimisation lifecycle
1. Create/ensure a deterministic `StudyContext` and key: `u:{user_id}|m:{method_id}|v:{variant_id}|b:{bean|none}|e:{equipment|none}`.
2. Request suggestion via ask flow (`study.ask` + method profile distributions) and persist identifiers (`id`, `study_key`, `trial_number`, suggested params).
3. Brew with suggested params and record a score.
4. Apply suggestion via tell flow (`study.tell`) with score validation (`0.0..10.0`) and trial/study existence checks.
5. Apply is explicitly non-idempotent: a suggestion can be applied once and subsequent applies return `suggestion_already_applied`.

## Legacy CSV import notes
- Existing files in repo (e.g. `aeropress.data.csv`) can be imported via API or CLI.
- Unknown columns are preserved in `extra_data`.
- Repeat imports are idempotent by deterministic brew hash.



### List endpoint pagination
- Supported on list endpoints (`/brews`, `/beans`, `/equipment`, `/recipes`, `/users`).
- Query params:
  - `page` (default: `1` when pagination is requested)
  - `page_size` (default: `20` when pagination is requested, max: `100`)
  - `include_total` (default: `false`)
- Backwards compatibility: if `page`/`page_size` are omitted, endpoints return the original array response.

### Brew list filtering/sorting
- `/api/v1/brews` also supports:
 - `method`
  - `variant_id`
  - `brewed_from` / `brewed_to` (ISO-8601 datetime)
  - `sort_by` (`date` or `score`)
  - `sort_order` (`asc` or `desc`)

## Quality checks
```bash
make lint
make format
make test
```

### Pre-commit
```bash
pre-commit install
pre-commit run --all-files
```

## Troubleshooting
- If `alembic upgrade head` fails with `failed to resolve host 'postgres'`, your local shell is using a Docker-only DB URL.
  - Fix by setting `DATABASE_URL=sqlite:///./coffee.db` (quickest) or `...@localhost:5432/...` for local Postgres.

- If Optuna reports schema/runtime compatibility errors, upgrade dependency (`pip install -U optuna`) and keep `OPTUNA_SKIP_COMPATIBILITY_CHECK=true` for mixed/local legacy DBs.
