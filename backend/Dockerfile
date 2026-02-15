FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml ./
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app
COPY data ./data
COPY scripts ./scripts

RUN pip install --no-cache-dir .

EXPOSE 8000
CMD ["./scripts/start.sh"]
