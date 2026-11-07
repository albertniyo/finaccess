"""Explainable priority rankings."""

from typing import Annotated, Literal

from fastapi import APIRouter, Query

from compass import scoring

router = APIRouter()

Measure = Literal["excluded", "not_formally_served"]


@router.get("")
def get_priorities(
    poverty_weight: Annotated[float, Query(ge=0.0, le=1.0, alias="povertyWeight")] = 0.5,
    exclusion_weight: Annotated[float, Query(ge=0.0, le=1.0, alias="exclusionWeight")] = 0.5,
    measure: Annotated[Measure, Query()] = "excluded",
) -> dict:
    """Ranked districts with indicator contributions, baseline ranks, uncertainty and sensitivity.

    Weights are normative assumptions — not objective truth. See methodology.
    """
    return scoring.rank_priorities(
        poverty_weight=poverty_weight,
        exclusion_weight=exclusion_weight,
        measure=measure,
    )
