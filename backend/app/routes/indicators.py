"""Intervention Gap Explorer indicator series."""

from fastapi import APIRouter, HTTPException, Query

from compass import indicators as indicator_logic

router = APIRouter()


@router.get("")
def get_indicators(
    province: str | None = Query(default=None, description="Province filter, e.g. 'Northern'"),
) -> dict:
    """District indicator series (with national and province context) for the Gap Explorer."""
    try:
        return indicator_logic.get_indicators(province=province)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
