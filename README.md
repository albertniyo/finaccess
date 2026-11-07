# FinAccess Compass Rwanda

Decision support for financial-inclusion and social-protection planners, built for the
**NISR 2026 Big Data Hackathon** (Track 2 — Financial Inclusion & Poverty Reduction).

> With limited resources, where should we investigate or intervene first, who is being missed, and
> what evidence supports that decision?

**Live:** https://finaccessrw.vercel.app

## Features

1. **Intervention Gap Explorer** — map, scatter plot and table comparing EICV7 poverty with the
   FinScope 2024 access strand for all 30 districts, with context indicators (poverty trend, digital
   channels, health insurance) and a national breakdown of who is excluded. Every number shows its
   source, definition and 95% interval.
2. **Explainable Priority Analysis** — a transparent weighted score compared against poverty-only
   targeting, with per-indicator contributions, Monte Carlo rank uncertainty, sensitivity to weights
   and to the exclusion definition, and hypothetical budget scenarios.
3. **Policy Brief Generator** — a district brief that labels every statement as observed, estimate,
   recommendation or scenario; prints to PDF and exports Markdown.

**Finding.** At equal weights, poverty-only targeting misses 4 of the 10 districts the combined score
prioritises — Ngoma, Ngororero, Gakenke and Kayonza, whose financial exclusion is among the highest in
Rwanda — while the poorest district, Nyamagabe (51.4%), has only 1% of adults excluded. The ranking is
weight-sensitive: only Nyaruguru stays in the top 5 under every mixed weighting, and the app says so.
See [`docs/methodology.md`](docs/methodology.md) §8.

## Data

Published aggregates only; no microdata and no generated numbers.

| Source | Used for |
| --- | --- |
| NISR **EICV7 2023/24** Main Indicator tables (Excel) | District poverty with SE and 95% CI; mobile phone, smartphone, internet and health-insurance coverage; extreme poverty and VUP (national) |
| NISR **EICV7 Poverty Profile** | 2017 (modelled) district poverty and the fall to 2024 |
| AFR / NISR **FinScope Rwanda 2024** report | Access strand by district, province and population group; account uptake by product |
| **geoBoundaries** ADM2 | District outlines |

The two surveys are compared only as district aggregates and are never linked at household level.
Values that exist only in PDFs are transcribed into [`data/manual/`](data/manual) and re-checked
against the PDF text layer. The build runs 50 checks — figures quoted in the reports, agreement
between tables, and the transcriptions — and fails if any of them fail. Sources considered and
rejected are listed in the [data dictionary](docs/data-dictionary.md#sources-considered-and-not-used).

## Repository

```text
apps/web/          React + TypeScript single-page app
backend/app/       FastAPI routes
backend/compass/   Scoring, uncertainty, typology, scenarios and briefs
backend/tests/     Data, scoring and API tests
data/manual/       Transcriptions of PDF-only figures
data/processed/    Build output served by the API
data/provenance/   Download checksums and check results
scripts/           Download, transcription check and build
docs/              Methodology, data dictionary, demo script, AI disclosure
```

## Getting started

Requires [uv](https://docs.astral.sh/uv/), Node 20+ and, to rebuild data, `pdftotext` (poppler).

```bash
# API — http://localhost:8000/docs
cd backend
uv sync
uv run uvicorn app.main:app --reload

# Web — http://localhost:5173, proxies /api to the API
cd apps/web
npm install
npm run dev
```

Processed data is committed. To rebuild it from the official sources:

```bash
scripts/build_data.sh
```

### Tests

```bash
cd backend && uv run pytest && uv run ruff check . ../scripts
cd apps/web && npm run lint && npm run build
```

CI runs both on every push. Its manual `data-pipeline` job re-downloads the sources and fails if the
committed data would change.

## Deployment

### API (Docker)

The image bundles `data/processed`, so build from the repository root:

```bash
docker build -f backend/Dockerfile -t finaccess-api .
docker run -d --name finaccess-api -p 8000:8000 --restart unless-stopped finaccess-api
```

The container runs as a non-root user and reports health through Docker's `HEALTHCHECK` (`GET /health`).

| Variable | Default | Purpose |
| --- | --- | --- |
| `PORT` | `8000` | Listen port |
| `WEB_CONCURRENCY` | `2` | Uvicorn worker processes |
| `CORS_ORIGINS` | — | Extra allowed origins, comma-separated |
| `CORS_ORIGIN_REGEX` | `https://finaccessrw(-[a-z0-9-]+)?\.vercel\.app` | Allowed origin pattern (production and preview deployments) |

`https://finaccessrw.vercel.app` and localhost are always allowed.

### Web (Vercel)

Set the project root to `apps/web` and `VITE_API_BASE` to the API origin (no trailing slash), then
redeploy; Vite inlines the value at build time. `vercel.json` handles deep links, security headers and
long-lived caching of hashed assets.

## API

| Endpoint | Returns |
| --- | --- |
| `GET /health` | Version, data and check status |
| `GET /indicators?province=` | Indicator catalogue and national, province and district series |
| `GET /geo/districts` | District GeoJSON |
| `GET /priorities?povertyWeight=&exclusionWeight=&measure=` | Rankings, contributions, baseline comparison, uncertainty and sensitivity |
| `POST /scenarios` | Budget allocation under three targeting rules |
| `POST /briefs` | District brief |
| `GET /meta/sources` · `/meta/validation` · `/meta/method` | Citations and checksums, check results, method parameters |

Invalid input returns `422`, unknown districts `404`, and missing data `503`.

## Limitations

The surveys are cross-sectional and sampled separately. FinScope district shares are rounded whole
percentages from about 400 adults per district, so their intervals are approximations. Weights are a
policy choice. A priority score says where to look first, not what an intervention will achieve, and
scenarios use no costs, populations or causal effects. See [`docs/methodology.md`](docs/methodology.md) §10.

## Documentation

- [Methodology](docs/methodology.md)
- [Data dictionary](docs/data-dictionary.md)
- [Demo script](docs/demo-script.md)
- [AI disclosure](docs/ai-disclosure.md)

## AI disclosure

We used AI assistants to brainstorm and to understand the challenge, and as coding assistants while
building. Every statistic comes from the official sources above and is checked automatically. Details
in [`docs/ai-disclosure.md`](docs/ai-disclosure.md).

## License

GPL-3.0 — see [`LICENSE`](LICENSE). No endorsement by NISR or AFR is implied.
