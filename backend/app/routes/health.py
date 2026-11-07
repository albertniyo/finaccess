"""Health check."""

from fastapi import APIRouter, Request

from compass import data

router = APIRouter()


@router.get("/health")
def health(request: Request) -> dict:
    try:
        n = data.load_dataset()["meta"]["n_districts"]
        validation = data.load_validation() or {}
        data_status = {
            "data": "ok",
            "districts": n,
            "validation": {"passed": validation.get("passed"), "failed": validation.get("failed")},
        }
    except data.DataUnavailableError:
        data_status = {"data": "missing", "districts": 0}
    return {"status": "ok", "service": "finaccess-compass", "version": request.app.version, **data_status}
