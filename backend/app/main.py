"""FinAccess Compass API entrypoint."""

import logging
import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.routes import briefs, geo, health, indicators, meta, priorities, scenarios
from compass import data
from compass.data import DataUnavailableError

log = logging.getLogger("uvicorn.error")

DEFAULT_CORS_ORIGINS = [
    "https://finaccessrw.vercel.app",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:4173",
    "http://127.0.0.1:4173",
]
# Vercel preview deployments of the same project, e.g. finaccessrw-git-main-<team>.vercel.app
DEFAULT_CORS_ORIGIN_REGEX = r"https://finaccessrw(-[a-z0-9-]+)?\.vercel\.app"
# Processed data only changes on redeploy, so read-only GETs may be cached briefly by browsers/CDNs.
GET_CACHE_SECONDS = 300
SECURITY_HEADERS = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "geolocation=(), camera=(), microphone=()",
}


def cors_origins() -> list[str]:
    extra = os.environ.get("CORS_ORIGINS", "")
    return DEFAULT_CORS_ORIGINS + [o.strip().rstrip("/") for o in extra.split(",") if o.strip()]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    try:
        meta_info = data.load_dataset()["meta"]
        validation = data.load_validation() or {}
        log.info("Loaded %s districts from %s (validation: %s passed, %s failed)",
                 meta_info["n_districts"], data.processed_dir(), validation.get("passed"), validation.get("failed"))
    except DataUnavailableError as exc:
        log.error("Processed data unavailable — data endpoints will return 503: %s", exc)
    yield


app = FastAPI(
    title="FinAccess Compass Rwanda",
    description=(
        "Decision-support API for financial inclusion and poverty prioritisation. "
        "Calculation logic lives in the `compass` package — not in the UI."
    ),
    version="1.1.0",
    lifespan=lifespan,
)

app.add_middleware(GZipMiddleware, minimum_size=1024)
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins(),
    allow_origin_regex=os.environ.get("CORS_ORIGIN_REGEX", DEFAULT_CORS_ORIGIN_REGEX),
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    max_age=600,
)


@app.middleware("http")
async def response_headers(request: Request, call_next) -> Response:
    response = await call_next(request)
    for name, value in SECURITY_HEADERS.items():
        response.headers.setdefault(name, value)
    if request.method == "GET" and response.status_code == 200 and request.url.path != "/health":
        response.headers.setdefault("Cache-Control", f"public, max-age={GET_CACHE_SECONDS}")
    elif request.url.path == "/health":
        response.headers["Cache-Control"] = "no-store"
    return response


@app.exception_handler(DataUnavailableError)
async def data_unavailable(_: Request, exc: DataUnavailableError) -> JSONResponse:
    return JSONResponse(status_code=503, content={"status": "data_unavailable", "detail": str(exc)})


app.include_router(health.router)
app.include_router(meta.router, prefix="/meta", tags=["meta"])
app.include_router(indicators.router, prefix="/indicators", tags=["indicators"])
app.include_router(geo.router, prefix="/geo", tags=["geo"])
app.include_router(priorities.router, prefix="/priorities", tags=["priorities"])
app.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
app.include_router(briefs.router, prefix="/briefs", tags=["briefs"])
