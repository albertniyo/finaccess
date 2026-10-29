"""Transparent priority scoring and baseline comparison.

Weights are assumptions — never presented as objective truth.
"""

from __future__ import annotations


def rank_priorities(
    poverty_weight: float = 0.5,
    exclusion_weight: float = 0.5,
) -> dict:
    """Rank areas by combined score vs poverty-only baseline.

    Stub until processed indicators exist. Formula sketch (documented in
    docs/methodology.md once indicators are frozen):

        combined = w_p * norm(poverty) + w_e * norm(financial_exclusion)
    """
    total = poverty_weight + exclusion_weight
    if total <= 0:
        poverty_weight, exclusion_weight = 0.5, 0.5
        total = 1.0

    return {
        "status": "awaiting_processed_data",
        "weights": {
            "poverty": poverty_weight / total,
            "exclusion": exclusion_weight / total,
            "note": "Normative assumptions; use sensitivity UI before deciding.",
        },
        "baseline": "poverty_only",
        "rankings": [],
        "contributions": [],
        "provenance": {
            "kind": "estimate",
            "method": "transparent_weighted_score_v1",
            "limitations": [
                "District aggregates from EICV7 and FinScope are separate samples.",
                "Priority score ≠ guaranteed impact.",
                "Correlations ≠ causation.",
            ],
        },
    }