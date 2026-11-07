"""Transparent priority scoring and baseline comparison.

    combined = w_p * norm(poverty_rate) + w_e * norm(exclusion_measure)

`norm` is min–max normalisation across the 30 districts (0 = lowest, 1 = highest), so each
indicator's contribution is bounded by its weight. The baseline is a poverty-only ranking.
Weights are assumptions — never presented as objective truth.
"""

from __future__ import annotations

import copy
from functools import lru_cache

import numpy as np

from compass import data, typology, uncertainty

MEASURES: dict[str, dict] = {
    "excluded": {
        "label": "Financially excluded adults (%)",
        "short": "financially excluded",
        "field": "excluded",
        "rounded_labels": 1,
    },
    "not_formally_served": {
        "label": "Adults not formally served (%) — informal-only + excluded",
        "short": "not formally served",
        "field": "not_formally_served",
        "rounded_labels": 2,
    },
}
DEFAULT_MEASURE = "excluded"
SIMULATIONS = 2000
SEED = 20261030
SWEEP_STEP = 0.05
TOP_K = (5, 10)
SCHEMES = [
    (1.0, "Poverty only (baseline)"),
    (0.75, "Poverty-leaning 75/25"),
    (0.5, "Balanced 50/50"),
    (0.25, "Exclusion-leaning 25/75"),
    (0.0, "Exclusion only"),
]

LIMITATIONS = [
    (
        "EICV7 (2023/24) and FinScope (2024) are separate samples; district scores combine "
        "aggregates, not households that are both poor and excluded."
    ),
    (
        "FinScope district shares are rounded whole percentages from ~400 adults per district; "
        "differences of 1–2 points are within sampling error."
    ),
    "Weights are normative choices. Check the sensitivity table before acting on a ranking.",
    "A priority score flags where to investigate first — it is not a predicted impact.",
    "Cross-sectional data: correlations do not show what causes poverty or exclusion.",
]


def normalise_weights(poverty_weight: float, exclusion_weight: float) -> tuple[float, float]:
    total = poverty_weight + exclusion_weight
    if total <= 0:
        return 0.5, 0.5
    return poverty_weight / total, exclusion_weight / total


def _minmax(values: np.ndarray) -> np.ndarray:
    """Min–max along the last axis; a constant row normalises to zeros."""
    lo = values.min(axis=-1, keepdims=True)
    span = values.max(axis=-1, keepdims=True) - lo
    return np.divide(values - lo, span, out=np.zeros_like(values, dtype=float), where=span > 0)


def _rank_desc(values: np.ndarray) -> np.ndarray:
    """Competition ranks (1 = highest); ties share the best rank. Works on the last axis."""
    v = np.asarray(values, dtype=float)
    return (v[..., None, :] > v[..., :, None]).sum(axis=-1) + 1


def _inputs(measure: str) -> tuple[list[dict], np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    if measure not in MEASURES:
        raise ValueError(f"Unknown exclusion measure '{measure}'. Allowed: {sorted(MEASURES)}")
    spec = MEASURES[measure]
    districts = data.load_dataset()["districts"]
    pov = np.array([d["poverty_rate"]["value"] for d in districts], dtype=float)
    pov_se = np.array([d["poverty_rate"]["se"] for d in districts], dtype=float)
    exc = np.array([d["finscope"][spec["field"]] for d in districts], dtype=float)
    exc_se = np.array(
        [uncertainty.finscope_se(x, rounded_labels=spec["rounded_labels"]) for x in exc], dtype=float
    )
    return districts, pov, pov_se, exc, exc_se


def _scores(pov: np.ndarray, exc: np.ndarray, wp: float, we: float) -> np.ndarray:
    return wp * _minmax(pov) + we * _minmax(exc)


def _top(names: list[str], scores: np.ndarray, k: int, tiebreak: np.ndarray) -> list[str]:
    """Top-k names by score; ties (common with whole-percent FinScope labels) go to higher poverty."""
    order = np.lexsort((-tiebreak, -np.round(scores, 10)))
    return [names[i] for i in order[:k]]


def simulate_ranks(
    pov: np.ndarray, pov_se: np.ndarray, exc: np.ndarray, exc_se: np.ndarray,
    wp: float, we: float, simulations: int = SIMULATIONS, seed: int = SEED,
) -> np.ndarray:
    """Monte Carlo ranks (simulations × districts) under sampling uncertainty of both inputs."""
    rng = np.random.default_rng(seed)
    pov_draws = np.clip(pov + pov_se * rng.standard_normal((simulations, pov.size)), 0, 100)
    exc_draws = np.clip(exc + exc_se * rng.standard_normal((simulations, exc.size)), 0, 100)
    scores = _scores(pov_draws, exc_draws, wp, we)
    order = np.argsort(-scores, axis=1, kind="stable")
    ranks = np.empty_like(order)
    rows = np.arange(simulations)[:, None]
    ranks[rows, order] = np.arange(1, pov.size + 1)
    return ranks


def _weight_ranges(names, pov, exc, k: int) -> dict[str, list[float] | None]:
    """For each district, the poverty weights (0–1 sweep) at which it is in the top-k."""
    hits: dict[str, list[float]] = {n: [] for n in names}
    for w in np.round(np.arange(0, 1 + 1e-9, SWEEP_STEP), 2):
        for name in _top(names, _scores(pov, exc, float(w), 1 - float(w)), k, pov):
            hits[name].append(float(w))
    return {n: ([min(ws), max(ws)] if ws else None) for n, ws in hits.items()}


def rank_priorities(
    poverty_weight: float = 0.5,
    exclusion_weight: float = 0.5,
    measure: str = DEFAULT_MEASURE,
    simulations: int = SIMULATIONS,
) -> dict:
    """Rank districts by combined score vs the poverty-only baseline, with uncertainty.

    Results are deterministic (fixed seed), so identical requests are served from a cache;
    callers receive a deep copy they may mutate.
    """
    wp, we = normalise_weights(poverty_weight, exclusion_weight)
    if measure not in MEASURES:
        raise ValueError(f"Unknown exclusion measure '{measure}'. Allowed: {sorted(MEASURES)}")
    return copy.deepcopy(_rank_priorities_cached(round(wp, 6), round(we, 6), measure, simulations))


@lru_cache(maxsize=256)
def _rank_priorities_cached(wp: float, we: float, measure: str, simulations: int) -> dict:
    districts, pov, pov_se, exc, exc_se = _inputs(measure)
    names = [d["district"] for d in districts]
    national = data.load_dataset()["national"]

    norm_p, norm_e = _minmax(pov), _minmax(exc)
    score = wp * norm_p + we * norm_e
    combined_rank = _rank_desc(score)
    baseline_rank = _rank_desc(pov)
    exclusion_rank = _rank_desc(exc)

    sims = simulate_ranks(pov, pov_se, exc, exc_se, wp, we, simulations)
    p_top = {k: (sims <= k).mean(axis=0) for k in TOP_K}
    rank_lo = np.percentile(sims, 5, axis=0)
    rank_hi = np.percentile(sims, 95, axis=0)
    weight_ranges = _weight_ranges(names, pov, exc, 5)

    rankings = []
    for i, d in enumerate(districts):
        rankings.append({
            "district": d["district"],
            "province": d["province"],
            "rank": int(combined_rank[i]),
            "baseline_rank": int(baseline_rank[i]),
            "exclusion_rank": int(exclusion_rank[i]),
            "rank_shift": int(baseline_rank[i] - combined_rank[i]),
            "score": round(float(score[i]), 4),
            "inputs": {"poverty_rate": float(pov[i]), "exclusion": float(exc[i])},
            "normalised": {"poverty": round(float(norm_p[i]), 4), "exclusion": round(float(norm_e[i]), 4)},
            "contributions": {
                "poverty": round(float(wp * norm_p[i]), 4),
                "exclusion": round(float(we * norm_e[i]), 4),
            },
            "uncertainty": {
                "p_top5": round(float(p_top[5][i]), 3),
                "p_top10": round(float(p_top[10][i]), 3),
                "rank_interval_90": [int(rank_lo[i]), int(rank_hi[i])],
            },
            "top5_poverty_weight_range": weight_ranges[d["district"]],
            "profile": typology.classify(d, national),
        })
    rankings.sort(key=lambda r: (r["rank"], r["baseline_rank"]))

    sensitivity = []
    for w, label in SCHEMES:
        s = _scores(pov, exc, w, 1 - w)
        sensitivity.append({"poverty_weight": w, "label": label, "measure": measure,
                            "top5": _top(names, s, 5, pov), "top10": _top(names, s, 10, pov)})
    alt_measure = next(m for m in MEASURES if m != measure)
    _, _, _, alt_exc, _ = _inputs(alt_measure)
    alt_scores = _scores(pov, alt_exc, wp, we)
    sensitivity.append({"poverty_weight": round(wp, 2), "label": f"Same weights, {MEASURES[alt_measure]['short']}",
                        "measure": alt_measure, "top5": _top(names, alt_scores, 5, pov),
                        "top10": _top(names, alt_scores, 10, pov)})

    current_top5 = _top(names, score, 5, pov)
    robust = [n for n in current_top5 if all(n in s["top5"] for s in sensitivity[1:4])]

    comparison = {}
    by_name = {r["district"]: r for r in rankings}
    for k in TOP_K:
        base = _top(names, pov, k, pov)
        comb = _top(names, score, k, pov)
        comparison[f"top{k}"] = {
            "baseline": base,
            "combined": comb,
            "overlap": [n for n in comb if n in base],
            "entered": [_mover(by_name[n]) for n in comb if n not in base],
            "dropped": [_mover(by_name[n]) for n in base if n not in comb],
        }

    return {
        "status": "ok",
        "weights": {
            "poverty": round(wp, 4),
            "exclusion": round(we, 4),
            "note": "Normative assumptions; use the sensitivity table before deciding.",
        },
        "measure": {"id": measure, **MEASURES[measure]},
        "measures": {k: v["label"] for k, v in MEASURES.items()},
        "baseline": "poverty_only",
        "national": {"poverty_rate": national["poverty_rate"]["value"],
                     "exclusion": national["finscope"][MEASURES[measure]["field"]]},
        "rankings": rankings,
        "comparison": comparison,
        "sensitivity": {"schemes": sensitivity, "robust_top5": robust},
        "provenance": {
            "kind": "estimate",
            "method": "transparent_weighted_score_v1",
            "formula": "score = w_p·minmax(poverty_rate) + w_e·minmax(exclusion_measure)",
            "normalisation": "min–max across the 30 districts",
            "uncertainty": {
                "method": f"Monte Carlo, {simulations} draws, seed {SEED}",
                "poverty": "EICV7 published standard errors",
                "exclusion": uncertainty.ASSUMPTIONS["note"],
            },
            "limitations": LIMITATIONS,
        },
    }


def _mover(r: dict) -> dict:
    return {
        "district": r["district"],
        "rank": r["rank"],
        "baseline_rank": r["baseline_rank"],
        "poverty_rate": r["inputs"]["poverty_rate"],
        "exclusion": r["inputs"]["exclusion"],
        "exclusion_rank": r["exclusion_rank"],
        "explanation": (
            f"{r['district']}: poverty {r['inputs']['poverty_rate']:.1f}% (rank {r['baseline_rank']}/30), "
            f"exclusion measure {r['inputs']['exclusion']:.0f}% (rank {r['exclusion_rank']}/30)."
        ),
    }
