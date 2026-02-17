FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

COPY pyproject.toml README.md /app/
COPY src /app/src
COPY alembic.ini /app/
COPY src/coffee_backend/db/migrations /app/src/coffee_backend/db/migrations
COPY docker/entrypoint.sh /entrypoint.sh

RUN pip install --no-cache-dir .
RUN chmod +x /entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/entrypoint.sh"]
CMD ["uvicorn", "coffee_backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
