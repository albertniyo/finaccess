"""Explainable priority rankings."""

from fastapi import APIRouter, Query

from compass import scoring

router = APIRouter()


@router.get("")
def get_priorities(
    poverty_weight: float = Query(default=0.5, ge=0.0, le=1.0, alias="povertyWeight"),
    exclusion_weight: float = Query(default=0.5, ge=0.0, le=1.0, alias="exclusionWeight"),
) -> dict:
    """Ranked areas with indicator contributions and baseline ranks.

    Weights are normative assumptions — not objective truth. See methodology.
    """
    return scoring.rank_priorities(
        poverty_weight=poverty_weight,
        exclusion_weight=exclusion_weight,
    )