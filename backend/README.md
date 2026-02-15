# Backend

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
uvicorn app.main:app --reload --port 8000
```

API docs: `http://localhost:8000/api/v1/docs`
