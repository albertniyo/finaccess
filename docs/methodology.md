# Methodology

**Status:** v1.1 (7 Nov 2026). Any change that affects scores is recorded in the change log at the end.

## 1. Question and user

*With limited resources, which districts should a financial-inclusion or social-protection planner
investigate first, who would poverty-only targeting miss, and what evidence supports that?*

The output is a **ranking for investigation**, not a funding decision or an impact forecast.

## 2. Data

| Indicator | Survey | Geography | Source cell | Uncertainty |
| --- | --- | --- | --- | --- |
| Headcount poverty | EICV7 2023/24 (NISR) | district (30), province, urban/rural, national | Main Indicator tables, Table A9.23 | Published SE, 95% CI, CV, design effect |
| Extreme poverty | EICV7 2023/24 | province, national | Table 9.2 | Published |
| Households owning a mobile phone | EICV7 2023/24 | district | Table A5.18 | Published |
| Households owning a smartphone | EICV7 2023/24 | district | Table A5.19 | Published |
| Households with internet at home | EICV7 2023/24 | district | Table A5.15 | Published |
| Population with health insurance | EICV7 2023/24 | district | Table A3.7 | Published |
| Poverty 2017 (modelled) and fall to 2024 | EICV7 Poverty Profile | district (Annex B), province/national (Table 5.1) | Annex B, Table 5.1 | Model-based; no district CI |
| Access strand: banked / other formal / informal only / excluded | FinScope Rwanda 2024 (AFR/NISR) | district, province, national | Report Fig. 13 / 12 / 5 | Not published — approximated (§5) |
| Access strand by area, gender, age, disability, refugees, livelihood | FinScope Rwanda 2024 | national only | Fig. 6–11 | Whole % |
| Accounts by product; VUP beneficiaries | FinScope p.12; EICV7 Tables 10.1–10.4 | national only | — | Whole % / survey estimate |

**Score inputs are unchanged in v1.1:** only poverty and the exclusion measure enter the score. The context
indicators appear in the Explorer, the typology flags (§7) and the brief.

* EICV7 values are read programmatically from the official Excel file (`scripts/build_indicators.py`).
* FinScope publishes district values only as chart labels. They were transcribed into
  `data/manual/finscope2024_access_strand.csv`; five merged labels (Kicukiro, Gasabo, Gatsibo,
  Burera, Nyarugenge) were resolved by rendering the page at 600 dpi and are annotated in the file.
* Derived FinScope measures: *not formally served* = informal only + excluded;
  *formally served* = banked + other formal.

### Linkage policy

EICV7 and FinScope sample different households. They are **never merged at household level**.
They are compared only as **district aggregates** of separately weighted estimates. A district with
high poverty and high exclusion does not show that the same people are poor and excluded.

## 3. Validation

The pipeline is `scripts/build_data.sh`: download (checksums) → `verify_transcriptions.py` → `build_indicators.py`.
The build fails if any check fails (results in `data/provenance/validation.json`, shown in-app). **50 / 50 pass**,
in three groups:

* **Golden (37)** — processed values reproduce figures quoted in the reports.
* **Consistency (12)** — tables agree with each other: every EICV7 district estimate lies in its CI (5 tables × 30);
  strands sum to 98–101; Fig. 5 equals Fig. 10 "Total population"; bank-account uptake equals the banked strand;
  Annex B arithmetic; Annex B 2024 column vs Table A9.23 differs only for the documented districts.
* **Transcription (1)** — all 90 hand-entered rows match the PDF text layer (`verify_transcriptions.py`; compares the
  digit string of each row's printed labels, so merged labels such as "22" are covered).

Golden checks include:

* Poverty: national 27.4%, urban 16.7%, rural 31.6%, all 5 provinces, 8 named districts
  (Nyamagabe 51.4, Gisagara 45.6, Rusizi 44.2, Nyanza 43.3, Nyamasheke 42.7, Nyarugenge 6.8,
  Kicukiro 6.9, Gasabo 11.1); extreme poverty 5.4%.
* FinScope: included 96%, formally served 92%, banked 22%; "twelve districts" above the 4%
  national exclusion rate; Gicumbi has the highest informal-only reliance; every district strand
  sums to 98–101 (rounding).
* Context: health insurance 85.3%, internet at home 29.8% (urban 57%, rural 19%), smartphone 34%,
  mobile phone 85%; 2017 modelled poverty 39.8% and fall of 12.4 points; FinScope groups — urban 97% /
  rural 96% / male 97% / female 96% / disabled 93% included, male 94% / female 90% formally served,
  refugees 37% banked.

Known source discrepancies (documented, not silently fixed):

* **Gisagara** — Main Indicators Report narrative says 46.6%; the report's own figure, Poverty
  Profile Annex B and Excel Table A9.23 all say 45.6%. We use 45.6%.
* **Annex B vs Table A9.23** — Annex B prints Burera 22.0 (Excel 21.8), Nyabihu 20.2 (Excel 20.4),
  Nyamasheke 42.8 (Excel 42.7), Rwamagana 23.8 (Excel 23.9). We use Excel for 2024 and Annex B only for
  the 2017 modelled value and printed fall.
* **2017 district poverty is modelled** — NISR predictions on the EICV7 consumption basis, not EICV5
  published rates.

## 4. Priority score

```text
score_d = w_p · minmax(poverty_d) + w_e · minmax(exclusion_d)        w_p + w_e = 1
minmax(x_d) = (x_d − min x) / (max x − min x)   across the 30 districts
```

* `exclusion` is either **financially excluded** (default) or **not formally served** (robustness).
* Contributions `w·minmax(x)` are additive and shown per district.
* Weights are **normative**. Default 50/50 is a neutral starting point, not a recommendation.
* **Baseline:** ranking by poverty alone (`w_p = 1`).
* Ties (common with whole-percent FinScope labels) are broken by the higher poverty rate.
* Implemented in `backend/compass/scoring.py`; an independent pure-Python recalculation is in
  `backend/tests/test_scoring.py`.

## 5. Uncertainty

* **Poverty:** published design-based standard errors.
* **FinScope exclusion:** no SEs are published. We approximate

  ```text
  se(p) = sqrt( p(1−p)/n · deff + k/12 )      [percentage points]
  ```

  with n = 400 adults (stated per-district minimum, so conservative), assumed deff = 1.5, and
  k/12 pp² for rounding of k whole-percent labels (k = 1 for excluded, 2 for not formally served).
  At 4% this gives ≈ ±2.4 pp (95%) — so 1–2 point differences between districts are noise.
* **Rank uncertainty:** 2,000 Monte Carlo draws of both indicators (fixed seed 20261030); we report
  P(top 5), P(top 10) and the 5th–95th percentile rank.
* **Classification confidence:** each district's poverty and exclusion are flagged "clear" only if
  the 95% interval excludes the national value.

## 6. Sensitivity

Top 5 is reported under poverty weights 1.0 / 0.75 / 0.5 / 0.25 / 0 and under the alternative
exclusion definition. For every district we report the range of poverty weights (0–1 sweep in
0.05 steps) at which it is in the top 5. A district is "robust" if it is in the top 5 at 75/25,
50/50 and 25/75.

## 7. Typology (aggregate exclusion patterns)

| Profile | Rule | Suggested line of enquiry |
| --- | --- | --- |
| High poverty + exclusion gap | poverty > national and excluded > national | Joint poverty + access responses; transfer-to-account channels |
| Poverty-led, access largely in place | poverty > national, excluded ≤ national | Depth of use, livelihoods — not account campaigns |
| Exclusion gap outside poverty hotspots | poverty ≤ national, excluded > national | Who is excluded; agent / channel coverage. Missed by poverty-only targeting |
| Lower relative need on both | both ≤ national | Monitor |

Flags (each flags exactly 3 districts with current data):

| Flag | Rule | Districts |
| --- | --- | --- |
| High informal-only reliance | informal-only ≥ 2× national (FinScope) | Gisagara, Gicumbi, Kayonza |
| Bank-led inclusion | banked ≥ 50% | Nyarugenge, Gasabo, Kicukiro |
| Slow poverty reduction | relative fall 2017→2024 < ½ the national relative fall (31%) | Nyanza, Burera, Ngoma |
| Low smartphone ownership | smartphone 95% CI entirely below the national *rural* rate (22.9%) | Gisagara, Nyaruguru, Nyamagabe |

Thresholds were chosen to discriminate: comparing smartphone ownership with the national rate (pulled up by
Kigali's 69%) flagged 19 of 30 districts, and an absolute poverty-fall rule flagged Kigali districts that simply
started low — both rejected.

## 8. Proof-of-value experiment

Default weights 50/50, measure = financially excluded.

1. **Poverty-only top 5:** Nyamagabe, Gisagara, Rusizi, Nyanza, Nyamasheke.
2. **Combined top 5:** Nyaruguru, Rusizi, Nyamasheke, Ngoma, Rutsiro.
3. **Movers (top 10):** Ngoma (#13 → #4), Ngororero (#14 → #7), Gakenke (#15 → #8) and Kayonza
   (#11 → #10) enter; Nyamagabe (#1 → #13), Kamonyi, Rubavu and Karongi drop out.
4. **Why:** Ngoma and Gakenke have 8% excluded (joint 2nd highest of 30), twice the national 4%;
   Nyamagabe — the poorest district — has 1% excluded (access is broadly reached; the problem is
   poverty, not access).
5. **Decision implication:** poverty-only targeting of financial-inclusion resources would skip
   districts with the highest exclusion. Five districts (Rulindo, Nyabihu, Gakenke, Gicumbi, Huye)
   have above-national exclusion *and* at-or-below-national poverty.
6. **Sensitivity:** a modest change (50/50 → 75/25) swaps 2 of the top 5 (Ngoma and Rutsiro out,
   Nyamagabe and Gisagara back in). Only **Nyaruguru** is robust across mixed weightings
   (P(top 5) ≈ 98%). Switching to "not formally served" brings Gisagara and Kayonza (high
   informal-only reliance) into the top 5. The tool therefore presents the ranking *with* its
   sensitivity, and the brief states the weight range in which each district is a top-5 priority.

## 9. Scenario planner

A hypothetical budget is split (equally or proportionally) across the top-N districts under three
rules — poverty only, exclusion gap, combined score — and the rules are compared by budget share
reaching above-national-poverty, above-national-exclusion and "exclusion gap" districts. **No
population, unit costs or causal effects are used; outputs are labelled Scenario and never claim
poverty exits.**

## 10. Limitations

1. Cross-sectional surveys; no causal effects of programmes.
2. Aggregate overlays ≠ individual "poor and excluded" households.
3. FinScope district shares are rounded, from ~400 adults; intervals are approximations.
4. Different reference periods (EICV7 2023/24, FinScope 2024) and populations (all individuals vs
   adults 16+).
5. District averages hide sector / cell pockets; no sex, age or urban/rural split at district level.
6. Priority score ≠ guaranteed impact; weights are normative.
7. Scenario allocations are hypothetical; population size is not used.

## 11. Impact framework

| Measure | Now | Future pilot (goal, not achieved) |
| --- | --- | --- |
| Data coverage | 30 districts, 2 official surveys, 10 district indicators, national group breakdowns | Add sector-level microdata estimates |
| Analytical reliability | 50 automated checks, Monte Carlo ranks, sensitivity | Replicate with microdata and replicate weights |
| Decision usefulness | Worked example above | Share of flagged districts confirmed by district officers |
| Reach | — | Change in excluded adults at next FinScope round vs comparison districts |
| Adoption | — | Briefs used in district planning (DDS / Imihigo) meetings |

## Change log

| Date | Change |
| --- | --- |
| 2026-10-29 | Skeleton created with scaffold |
| 2026-11-07 | v1: indicators, min–max weighted score, poverty-only baseline, Monte Carlo uncertainty, sensitivity, typology, scenarios, golden checks |
| 2026-11-07 | v1.1: context data (health insurance, smartphone, internet, 2017→2024 poverty, FinScope group strands, product uptake, VUP), two typology flags, transcription verification, 50 checks. Score inputs and rankings unchanged. |
