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

## Docker / Render

```bash
cd backend
docker build -t finaccess-api .
docker run --rm -p 8000:8000 -e PORT=8000 finaccess-api
```

On [Render](https://render.com): create a **Web Service** with Docker, Root Directory `backend`, and health check path `/health`. Render sets `PORT` automatically.

## Layout

| Path | Role |
| --- | --- |
| `app/` | FastAPI routes → JSON |
| `compass/` | Scoring, baselines, briefs (calculation logic) |
| `native/` | Optional C extensions for profiled hot paths |
| `tests/` | Unit + API contract tests |