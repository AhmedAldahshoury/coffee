#!/usr/bin/env sh
set -eu

python - <<'PY'
import os
import time
from sqlalchemy import create_engine, text

url = os.getenv('DATABASE_URL')
if not url:
    raise SystemExit('DATABASE_URL is not set')

engine = create_engine(url, future=True)
max_attempts = 30
for attempt in range(1, max_attempts + 1):
    try:
        with engine.connect() as conn:
            conn.execute(text('SELECT 1'))
        print('Database is ready')
        break
    except Exception as exc:
        if attempt == max_attempts:
            raise
        print(f'Database not ready yet (attempt {attempt}/{max_attempts}): {exc}')
        time.sleep(2)
PY

alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
