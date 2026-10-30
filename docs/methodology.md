# Methodology (skeleton)

**Status:** stub — freeze indicators after Priority A Excel/PDF inspection.

## Scope

FinAccess Compass ranks geographic units for **investigation / intervention priority** using transparent weights over poverty and financial-exclusion indicators. It does **not** claim causal impact or household-level dual labels across EICV7 and FinScope.

## Linkage policy

- Default: **no microdata merge** of EICV7 and FinScope.
- Compare only at a defensible common geographic aggregate (target: **district**).
- Document definition mismatches (sample, year, coverage).

## Scoring (v1 sketch)

Pending frozen indicator set. Planned form:

```text
combined_score = w_poverty * norm(poverty) + w_exclusion * norm(financial_exclusion)
```

- `norm` — min–max or rank normalisation within the analysis set (TBD).
- Weights are **normative assumptions**, exposed in the UI with sensitivity.
- **Baseline:** poverty-only ranking vs combined ranking.

## Uncertainty & sensitivity

- Re-rank under 2–3 weight schemes.
- Flag transcription uncertainty where only charts (not Excel) exist.
- Prefer published tables; validate 2–3 figures against reports.

## Limitations (always surface in-app)

1. Cross-sectional surveys; no causal effects of programmes.
2. Aggregate overlays ≠ individual “poor and excluded” households.
3. Priority score ≠ guaranteed poverty reduction.
4. Scenario allocations are hypothetical only.

## Change log

| Date | Change |
| --- | --- |
| 2026-10-29 | Skeleton created with scaffold |