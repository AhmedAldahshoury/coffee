# Backend

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
python -m uvicorn app.main:app --reload --port 8000
```

## Notes
- Package discovery is explicitly scoped to `app*`; `data/` is runtime data, not a Python package.

API docs: `http://localhost:8000/api/v1/docs`
