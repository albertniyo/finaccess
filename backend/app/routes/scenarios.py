"""Hypothetical resource-allocation scenarios (not causal impact claims)."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from compass import scenarios as scenario_logic

router = APIRouter()


class ScenarioRequest(BaseModel):
    budget: float = Field(..., gt=0, description="Hypothetical budget (currency units)")
    strategy: str = Field(
        ...,
        description="poverty_only | exclusion_gap | combined_score",
    )


@router.post("")
def create_scenario(body: ScenarioRequest) -> dict:
    """Compare allocation strategies under a hypothetical budget.

    Outputs are labelled scenarios, not predicted poverty exits.
    """
    return scenario_logic.run_scenario(budget=body.budget, strategy=body.strategy)