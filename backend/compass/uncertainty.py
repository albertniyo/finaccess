"""Sampling-uncertainty approximations.

EICV7 tables publish design-based standard errors, which we use directly.
FinScope 2024 publishes only rounded whole percentages per district, so we approximate:

    se(p) = sqrt( p(1-p)/n * deff  +  1/12 )      [percentage points]

with n = 400 adults (the stated per-district minimum, i.e. conservative), an assumed
design effect deff = 1.5, and 1/12 pp² for uniform rounding error of a whole-percent label.
These are model assumptions — shown as "Estimate", never as published precision.
"""

from __future__ import annotations

import math

FINSCOPE_DISTRICT_N = 400
FINSCOPE_ASSUMED_DEFF = 1.5
ROUNDING_VAR_PP2 = 1.0 / 12.0
Z95 = 1.959964


def finscope_se(
    percent: float,
    n: int = FINSCOPE_DISTRICT_N,
    deff: float = FINSCOPE_ASSUMED_DEFF,
    rounded_labels: int = 1,
) -> float:
    """Approximate standard error (percentage points) of a FinScope district share.

    `rounded_labels` is the number of whole-percent labels summed to form the share.
    """
    p = min(max(percent / 100.0, 0.005), 0.995)
    sampling_var_pp2 = (p * (1 - p) / n) * deff * 10_000
    return math.sqrt(sampling_var_pp2 + rounded_labels * ROUNDING_VAR_PP2)


def finscope_ci(percent: float) -> tuple[float, float]:
    se = finscope_se(percent)
    return max(0.0, percent - Z95 * se), min(100.0, percent + Z95 * se)


def differs_from(value: float, se: float, reference: float) -> bool:
    """True when the 95% interval around `value` excludes `reference`."""
    return abs(value - reference) > Z95 * se


ASSUMPTIONS = {
    "finscope_district_n": FINSCOPE_DISTRICT_N,
    "finscope_assumed_deff": FINSCOPE_ASSUMED_DEFF,
    "rounding_variance_pp2": round(ROUNDING_VAR_PP2, 4),
    "note": (
        "FinScope district shares are published without standard errors. Intervals are "
        "approximations from n=400 adults per district (report minimum), an assumed design "
        "effect of 1.5, and rounding of whole-percent labels."
    ),
}
