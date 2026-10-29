"""Policy brief payload builder."""

from __future__ import annotations

from compass import scoring, sources


def generate_brief(
    geo: str,
    poverty_weight: float = 0.5,
    exclusion_weight: float = 0.5,
) -> dict:
    """Structured brief for print/export.

    Distinguishes observed findings · interpretation · recommendations · scenarios.
    """
    priority = scoring.rank_priorities(
        poverty_weight=poverty_weight,
        exclusion_weight=exclusion_weight,
    )
    meta = sources.list_sources()

    return {
        "status": "awaiting_processed_data",
        "geo": geo,
        "sections": {
            "key_findings": [],
            "supporting_statistics": [],
            "priority_explanation": {
                "weights": priority["weights"],
                "baseline": priority["baseline"],
                "rankings": priority["rankings"],
            },
            "next_steps": [
                "Confirm indicator definitions against published EICV7 / FinScope tables.",
                "Investigate local delivery constraints before reallocating programmes.",
                "Treat combined priority as a hypothesis for further investigation.",
            ],
            "methodology_notes": [
                "No household-level merge of EICV7 and FinScope.",
                "Weights are normative assumptions.",
            ],
            "limitations": priority["provenance"]["limitations"],
            "sources": meta["sources"],
        },
        "provenance": {
            "kind": "estimate",
            "note": "Brief content will fill once processed aggregates are available.",
        },
    }