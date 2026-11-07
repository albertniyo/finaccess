# FinAccess Compass — API

FastAPI service exposing the `compass` analytics package. Dependencies are managed with
[uv](https://docs.astral.sh/uv/).

```bash
uv sync
uv run uvicorn app.main:app --reload    # http://localhost:8000/docs
uv run pytest
uv run ruff check . ../scripts
```

Processed data is read from `../data/processed`, or from `COMPASS_DATA_DIR` when set. Rebuild it with
`../scripts/build_data.sh`.

## Docker

The `Dockerfile` is at the repository root so the image can include `data/processed`. From the root:

```bash
docker build -t finaccess-api .
docker run -d -p 8000:8000 --restart unless-stopped finaccess-api
```

| Variable | Default | Purpose |
| --- | --- | --- |
| `PORT` | `8000` | Listen port |
| `WEB_CONCURRENCY` | `2` | Uvicorn worker processes |
| `CORS_ORIGINS` | — | Extra allowed origins, comma-separated |
| `CORS_ORIGIN_REGEX` | `https://finaccessrw(-[a-z0-9-]+)?\.vercel\.app` | Allowed origin pattern |
| `COMPASS_DATA_DIR` | `/app/data/processed` | Directory containing `districts.json` |

## Layout

| Path | Contents |
| --- | --- |
| `app/` | Routes, CORS, headers, error handling |
| `compass/data.py` | Loading processed aggregates |
| `compass/indicators.py` | Indicator catalogue and Explorer payload |
| `compass/scoring.py` | Weighted score, baseline, Monte Carlo uncertainty, sensitivity |
| `compass/uncertainty.py` | FinScope standard-error approximation |
| `compass/typology.py` | District profiles and flags |
| `compass/scenarios.py` | Budget scenarios |
| `compass/briefs.py` | Policy briefs |
| `native/` | Reserved for C extensions; not needed (see its README) |
| `tests/` | Data, scoring and API tests |
