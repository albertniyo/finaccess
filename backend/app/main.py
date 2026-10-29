"""FinAccess Compass API entrypoint."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import briefs, health, indicators, meta, priorities, scenarios

app = FastAPI(
    title="FinAccess Compass Rwanda",
    description=(
        "Decision-support API for financial inclusion and poverty prioritisation. "
        "Calculation logic lives in the `compass` package — not in the UI."
    ),
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(meta.router, prefix="/meta", tags=["meta"])
app.include_router(indicators.router, prefix="/indicators", tags=["indicators"])
app.include_router(priorities.router, prefix="/priorities", tags=["priorities"])
app.include_router(scenarios.router, prefix="/scenarios", tags=["scenarios"])
app.include_router(briefs.router, prefix="/briefs", tags=["briefs"])