# FinAccess Compass — Web

React + TypeScript single-page app built with Vite. It renders results from the API and performs no
calculations of its own.

```bash
npm install
npm run dev     # http://localhost:5173, proxies /api to http://127.0.0.1:8000
npm run lint
npm run build
```

## Configuration

`VITE_API_BASE` is the API origin, without a trailing slash. Leave it unset in development. For
production builds it must be set — Vite inlines it at build time — and the API must allow the site's
origin through CORS. See `.env.example`.

## Routes

| Path | Page |
| --- | --- |
| `/` | Overview and key finding |
| `/explorer` | Intervention Gap Explorer |
| `/priorities` | Priority analysis and scenario planner |
| `/brief` | Policy brief |
| `/methodology` | Method, checks, impact framework, sources, AI disclosure |

The poverty weight (`pw`), exclusion measure (`m`) and district (`d`) are kept in the query string, so
links between pages carry the same assumptions.
