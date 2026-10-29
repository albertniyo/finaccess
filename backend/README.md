# FinAccess Compass — Backend

FastAPI API + pure-Python `compass` analytics for FinAccess Compass Rwanda.

Managed with **[uv](https://docs.astral.sh/uv/)**.

## Setup

```bash
cd backend
uv sync
```

## Run

```bash
uv run uvicorn app.main:app --reload --port 8000
```

API docs: http://localhost:8000/docs

## Tests

```bash
uv run pytest
```

## Layout

| Path | Role |
| --- | --- |
| `app/` | FastAPI routes → JSON |
| `compass/` | Scoring, baselines, briefs (calculation logic) |
| `native/` | Optional C extensions for profiled hot paths |
| `tests/` | Unit + API contract tests |