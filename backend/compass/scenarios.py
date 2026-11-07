"""Hypothetical budget scenarios — not causal impact claims.

A strategy picks the top-N districts by its targeting indicator and splits a hypothetical
budget among them (equally, or proportionally to the indicator). We report *where money
would go* under each strategy and how the strategies differ — never people lifted out of
poverty, because no reliable intervention costs or causal effects are available.
"""

from __future__ import annotations

from compass import data, scoring

STRATEGIES: dict[str, str] = {
    "poverty_only": "Highest headcount poverty (EICV7)",
    "exclusion_gap": "Highest financial-exclusion measure (FinScope)",
    "combined_score": "Highest combined priority score",
}
ALLOCATION_RULES = {"equal": "Equal split across selected districts",
                    "proportional": "Proportional to the strategy's indicator value"}
ALLOWED_STRATEGIES = frozenset(STRATEGIES)


def _targeting_values(priorities: dict) -> dict[str, dict[str, float]]:
    out: dict[str, dict[str, float]] = {s: {} for s in STRATEGIES}
    for r in priorities["rankings"]:
        out["poverty_only"][r["district"]] = r["inputs"]["poverty_rate"]
        out["exclusion_gap"][r["district"]] = r["inputs"]["exclusion"]
        out["combined_score"][r["district"]] = r["score"]
    return out


def _allocate(
    values: dict[str, float], poverty: dict[str, float], budget: float, top_n: int, rule: str
) -> list[dict]:
    """Ties on the targeting value (common for whole-percent FinScope labels) go to higher poverty."""
    chosen = sorted(values, key=lambda n: (-values[n], -poverty[n], n))[:top_n]
    if rule == "proportional" and sum(values[n] for n in chosen) > 0:
        total = sum(values[n] for n in chosen)
        shares = {n: values[n] / total for n in chosen}
    else:
        shares = {n: 1 / len(chosen) for n in chosen}
    return [{"district": n, "share": round(shares[n], 4), "amount": round(budget * shares[n], 2),
             "targeting_value": round(values[n], 4)} for n in chosen]


def run_scenario(
    budget: float,
    strategy: str,
    top_n: int = 10,
    allocation: str = "equal",
    poverty_weight: float = 0.5,
    exclusion_weight: float = 0.5,
    measure: str = scoring.DEFAULT_MEASURE,
) -> dict:
    if strategy not in ALLOWED_STRATEGIES:
        raise ValueError(f"Unknown strategy '{strategy}'. Allowed: {sorted(ALLOWED_STRATEGIES)}")
    if allocation not in ALLOCATION_RULES:
        raise ValueError(f"Unknown allocation '{allocation}'. Allowed: {sorted(ALLOCATION_RULES)}")
    n_districts = len(data.district_names())
    if not 1 <= top_n <= n_districts:
        raise ValueError(f"top_n must be between 1 and {n_districts}")

    priorities = scoring.rank_priorities(poverty_weight, exclusion_weight, measure, simulations=200)
    values = _targeting_values(priorities)
    by_name = {r["district"]: r for r in priorities["rankings"]}
    nat = priorities["national"]

    def summarise(allocs: list[dict]) -> dict:
        def share_where(pred) -> float:
            return round(sum(a["share"] for a in allocs if pred(by_name[a["district"]])), 4)
        return {
            "districts": [a["district"] for a in allocs],
            "budget_share_above_national_poverty": share_where(
                lambda r: r["inputs"]["poverty_rate"] > nat["poverty_rate"]),
            "budget_share_above_national_exclusion": share_where(
                lambda r: r["inputs"]["exclusion"] > nat["exclusion"]),
            "budget_share_access_gap_districts": share_where(
                lambda r: r["profile"]["type"] == "access_gap"),
        }

    all_allocs = {
        s: _allocate(values[s], values["poverty_only"], budget, top_n, allocation) for s in STRATEGIES
    }
    selected = all_allocs[strategy]
    for a in selected:
        r = by_name[a["district"]]
        a.update({"province": r["province"], "poverty_rate": r["inputs"]["poverty_rate"],
                  "exclusion": r["inputs"]["exclusion"], "profile": r["profile"]["label"]})

    selected_set = {a["district"] for a in selected}
    comparison = []
    for s, allocs in all_allocs.items():
        names = {a["district"] for a in allocs}
        comparison.append({
            "strategy": s,
            "label": STRATEGIES[s],
            **summarise(allocs),
            "overlap_with_selected": len(names & selected_set),
            "only_in_this_strategy": sorted(names - selected_set),
        })

    return {
        "status": "ok",
        "label": "scenario",
        "budget": budget,
        "strategy": strategy,
        "strategy_label": STRATEGIES[strategy],
        "top_n": top_n,
        "allocation": allocation,
        "allocation_label": ALLOCATION_RULES[allocation],
        "weights": priorities["weights"],
        "measure": priorities["measure"]["id"],
        "allocations": selected,
        "comparison": comparison,
        "strategies": STRATEGIES,
        "allocation_rules": ALLOCATION_RULES,
        "provenance": {
            "kind": "scenario",
            "warning": (
                "Hypothetical only. Shows where a budget would be directed under each targeting "
                "rule. Without reliable intervention costs and causal effects, it does not "
                "predict poverty exits or inclusion gains."
            ),
            "assumptions": [
                "District population size is not used; shares are per district, not per person.",
                "Targeting values come from the published aggregates shown in the Explorer.",
                "Combined-score strategy uses the weights and measure currently selected.",
                "Ties on the targeting value are broken by the higher poverty rate.",
            ],
        },
    }
