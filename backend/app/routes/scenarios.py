"""Hypothetical resource-allocation scenarios (not causal impact claims)."""

from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from compass import scenarios as scenario_logic

router = APIRouter()


class ScenarioRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    budget: float = Field(..., gt=0, le=1e15, description="Hypothetical budget (RWF)")
    strategy: Literal["poverty_only", "exclusion_gap", "combined_score"]
    top_n: int = Field(default=10, ge=1, le=30, alias="topN")
    allocation: Literal["equal", "proportional"] = "equal"
    poverty_weight: float = Field(default=0.5, ge=0.0, le=1.0, alias="povertyWeight")
    exclusion_weight: float = Field(default=0.5, ge=0.0, le=1.0, alias="exclusionWeight")
    measure: Literal["excluded", "not_formally_served"] = "excluded"


@router.post("")
def create_scenario(body: ScenarioRequest) -> dict:
    """Compare allocation strategies under a hypothetical budget.

    Outputs are labelled scenarios, not predicted poverty exits.
    """
    try:
        return scenario_logic.run_scenario(
            budget=body.budget,
            strategy=body.strategy,
            top_n=body.top_n,
            allocation=body.allocation,
            poverty_weight=body.poverty_weight,
            exclusion_weight=body.exclusion_weight,
            measure=body.measure,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
