"""Intervention Gap Explorer indicator series."""

from fastapi import APIRouter, Query

from compass import indicators as indicator_logic

router = APIRouter()


@router.get("")
def get_indicators(
    geo: str | None = Query(default=None, description="Province or district filter"),
    urban_rural: str | None = Query(default=None, alias="urbanRural"),
) -> dict:
    """District (or other supported unit) indicator series for the Gap Explorer."""
    return indicator_logic.get_indicators(geo=geo, urban_rural=urban_rural)