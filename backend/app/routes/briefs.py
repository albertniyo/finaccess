"""Policy brief payloads for print/export."""

from typing import Literal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, ConfigDict, Field

from compass import briefs as brief_logic

router = APIRouter()


class BriefRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    geo: str = Field(..., min_length=1, max_length=64, description="District name")
    poverty_weight: float = Field(default=0.5, ge=0.0, le=1.0, alias="povertyWeight")
    exclusion_weight: float = Field(default=0.5, ge=0.0, le=1.0, alias="exclusionWeight")
    measure: Literal["excluded", "not_formally_served"] = "excluded"


@router.post("")
def create_brief(body: BriefRequest) -> dict:
    """Structured brief JSON: findings, interpretation, next steps, limitations, sources."""
    try:
        return brief_logic.generate_brief(
            geo=body.geo,
            poverty_weight=body.poverty_weight,
            exclusion_weight=body.exclusion_weight,
            measure=body.measure,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
