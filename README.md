# FinAccess Compass Rwanda

Decision-support tool for the **NISR 2026 Big Data Hackathon** (Track 2: Financial Inclusion & Poverty Reduction).

Helps a policymaker answer: *With limited resources, where should we investigate or intervene first, who is being missed, and what evidence supports that decision?*

**Stack:** TypeScript (Vite + React) · Python (FastAPI + `compass` analytics) · optional C for profiled hot paths

## Monorepo layout

```text
apps/web/          Vite + React + TypeScript UI
backend/           FastAPI routes + compass scoring
data/raw|processed Provenance-aware data pipeline
docs/              Methodology, dictionary, demo, AI disclosure
scripts/           Download + ETL stubs
```

## Quick start

### Backend (uv)

```bash
cd backend
uv sync
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd apps/web
npm install
npm run dev
```

Open http://localhost:5173 — Vite proxies `/api` → `http://127.0.0.1:8000`.

### Tests

```bash
cd backend && uv run pytest
```

## Core workflow

1. **Explorer** — Intervention Gap Explorer  
2. **Priorities** — Explainable scores + poverty-only baseline + sensitivity  
3. **Brief** — Policy brief for print/export  

See `plan.md` for architecture and judging strategy; `data.md` for source status.

## Documentation

| Doc | Path |
| --- | --- |
| Execution plan | `plan.md` |
| Data inventory | `data.md` |
| Methodology | `docs/methodology.md` |
| AI disclosure | `docs/ai-disclosure.md` |

## Status

Scaffold complete. Verified district indicators require Priority A downloads + ETL (`scripts/`). No fabricated statistics in the UI.