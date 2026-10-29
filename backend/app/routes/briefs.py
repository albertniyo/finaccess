"""Policy brief payloads for print/export."""

from fastapi import APIRouter
from pydantic import BaseModel, Field

from compass import briefs as brief_logic

router = APIRouter()


class BriefRequest(BaseModel):
    geo: str = Field(..., min_length=1, description="Selected geography (district/province)")
    poverty_weight: float = Field(default=0.5, ge=0.0, le=1.0, alias="povertyWeight")
    exclusion_weight: float = Field(default=0.5, ge=0.0, le=1.0, alias="exclusionWeight")


@router.post("")
def create_brief(body: BriefRequest) -> dict:
    """Structured brief JSON: findings, evidence, priorities, limitations, sources."""
    return brief_logic.generate_brief(
        geo=body.geo,
        poverty_weight=body.poverty_weight,
        exclusion_weight=body.exclusion_weight,
    )