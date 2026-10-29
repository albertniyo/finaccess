"""Scoring unit tests (expand once indicators are frozen)."""

from compass.scoring import rank_priorities


def test_weights_normalise() -> None:
    result = rank_priorities(poverty_weight=1.0, exclusion_weight=1.0)
    assert result["weights"]["poverty"] == 0.5
    assert result["weights"]["exclusion"] == 0.5


def test_zero_total_falls_back() -> None:
    result = rank_priorities(poverty_weight=0.0, exclusion_weight=0.0)
    assert result["weights"]["poverty"] == 0.5
    assert result["weights"]["exclusion"] == 0.5