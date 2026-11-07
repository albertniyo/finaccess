"""Scoring unit tests: normalisation, baseline, independent recalculation, uncertainty."""

import numpy as np
import pytest

from compass import data, scoring
from compass.scoring import rank_priorities


def _by_name(result: dict) -> dict[str, dict]:
    return {r["district"]: r for r in result["rankings"]}


def test_weights_normalise() -> None:
    result = rank_priorities(poverty_weight=1.0, exclusion_weight=1.0, simulations=50)
    assert result["weights"]["poverty"] == 0.5
    assert result["weights"]["exclusion"] == 0.5


def test_zero_total_falls_back() -> None:
    result = rank_priorities(poverty_weight=0.0, exclusion_weight=0.0, simulations=50)
    assert result["weights"]["poverty"] == 0.5
    assert result["weights"]["exclusion"] == 0.5


def test_ranks_all_thirty_districts() -> None:
    result = rank_priorities(simulations=50)
    assert len(result["rankings"]) == 30
    assert sorted(r["baseline_rank"] for r in result["rankings"]) == list(range(1, 31))


def test_poverty_only_weight_reproduces_baseline() -> None:
    result = rank_priorities(poverty_weight=1.0, exclusion_weight=0.0, simulations=50)
    for r in result["rankings"]:
        assert r["rank"] == r["baseline_rank"]
        assert r["rank_shift"] == 0
    assert result["comparison"]["top5"]["entered"] == []


def test_baseline_top_matches_published_ranking() -> None:
    result = rank_priorities(simulations=50)
    assert result["comparison"]["top5"]["baseline"] == [
        "Nyamagabe", "Gisagara", "Rusizi", "Nyanza", "Nyamasheke",
    ]


def test_independent_recalculation_of_scores() -> None:
    """Recompute every score from the processed file with plain Python (no numpy)."""
    districts = data.load_dataset()["districts"]
    pov = {d["district"]: d["poverty_rate"]["value"] for d in districts}
    exc = {d["district"]: d["finscope"]["excluded"] for d in districts}

    def minmax(values: dict[str, float]) -> dict[str, float]:
        lo, hi = min(values.values()), max(values.values())
        return {k: (v - lo) / (hi - lo) for k, v in values.items()}

    np_, ne = minmax(pov), minmax(exc)
    result = _by_name(rank_priorities(poverty_weight=0.6, exclusion_weight=0.4, simulations=50))
    for name, r in result.items():
        expected = 0.6 * np_[name] + 0.4 * ne[name]
        assert r["score"] == pytest.approx(expected, abs=1e-4)
        assert r["contributions"]["poverty"] + r["contributions"]["exclusion"] == pytest.approx(
            r["score"], abs=2e-4
        )


def test_scores_bounded_and_sorted() -> None:
    result = rank_priorities(simulations=50)
    scores = [r["score"] for r in result["rankings"]]
    assert all(0 <= s <= 1 for s in scores)
    assert scores == sorted(scores, reverse=True)


def test_combined_surfaces_exclusion_districts_missed_by_poverty_only() -> None:
    """Proof-of-value: at 50/50, the combined top-10 includes high-exclusion districts outside the baseline top-10."""
    result = rank_priorities(simulations=50)
    entered = {m["district"] for m in result["comparison"]["top10"]["entered"]}
    assert {"Ngoma", "Gakenke"} <= entered


def test_alternative_measure() -> None:
    result = rank_priorities(measure="not_formally_served", simulations=50)
    gicumbi = _by_name(result)["Gicumbi"]
    assert gicumbi["inputs"]["exclusion"] == 18  # informal-only 11 + excluded 7


def test_unknown_measure_raises() -> None:
    with pytest.raises(ValueError):
        rank_priorities(measure="vibes")


def test_monte_carlo_is_reproducible_and_coherent() -> None:
    a = rank_priorities(simulations=300)
    b = rank_priorities(simulations=300)
    assert [r["uncertainty"] for r in a["rankings"]] == [r["uncertainty"] for r in b["rankings"]]
    for r in a["rankings"]:
        u = r["uncertainty"]
        assert 0 <= u["p_top5"] <= u["p_top10"] <= 1
        lo, hi = u["rank_interval_90"]
        assert 1 <= lo <= hi <= 30


def test_simulated_ranks_are_permutations() -> None:
    pov = np.array([10.0, 20.0, 30.0])
    se = np.array([1.0, 1.0, 1.0])
    ranks = scoring.simulate_ranks(pov, se, pov, se, 0.5, 0.5, simulations=20)
    assert (np.sort(ranks, axis=1) == np.array([1, 2, 3])).all()


def test_rank_desc_ties_share_rank() -> None:
    assert scoring._rank_desc(np.array([5.0, 8.0, 8.0, 1.0])).tolist() == [3, 1, 1, 4]


def test_sensitivity_schemes_present() -> None:
    result = rank_priorities(simulations=50)
    schemes = result["sensitivity"]["schemes"]
    assert [s["poverty_weight"] for s in schemes[:5]] == [1.0, 0.75, 0.5, 0.25, 0.0]
    assert schemes[-1]["measure"] == "not_formally_served"
    assert all(len(s["top5"]) == 5 for s in schemes)
