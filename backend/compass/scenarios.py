"""Hypothetical budget scenarios — not causal impact claims."""

from __future__ import annotations

ALLOWED_STRATEGIES = frozenset({"poverty_only", "exclusion_gap", "combined_score"})


def run_scenario(budget: float, strategy: str) -> dict:
    """Compare relative allocation under a stated strategy."""
    if strategy not in ALLOWED_STRATEGIES:
        return {
            "status": "error",
            "error": f"Unknown strategy '{strategy}'. Allowed: {sorted(ALLOWED_STRATEGIES)}",
            "provenance": {"kind": "scenario"},
        }

    return {
        "status": "awaiting_processed_data",
        "label": "scenario",
        "budget": budget,
        "strategy": strategy,
        "allocations": [],
        "provenance": {
            "kind": "scenario",
            "warning": (
                "Hypothetical only. Without reliable intervention costs and causal "
                "effects, do not claim poverty exits or guaranteed outcomes."
            ),
        },
    }