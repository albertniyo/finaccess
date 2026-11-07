# Data dictionary

Values are percentages unless stated otherwise. Processed file: `data/processed/districts.json`, built
by `scripts/build_indicators.py`. API field names are in brackets.

## Observed (published) indicators

| Variable [API id] | Survey | Year | Geo | Definition | Source table / figure | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| Headcount poverty [`poverty_rate`] | EICV7 | 2023/24 | national, urban/rural, province, district | % of individuals in households whose consumption per adult equivalent is below the national poverty line | Main Indicator tables, **Table A9.23** (district), Table 9.1 | Stored with `se`, `ci_low`, `ci_high`, `cv`, `deff` as published |
| Extreme poverty [`extreme_poverty_rate`] | EICV7 | 2023/24 | national, urban/rural, province | % below the extreme (food) poverty line | **Table 9.2** | Not published by district in the tables used |
| Households with a mobile phone [`mobile_phone_households`] | EICV7 | 2023/24 | national, province, district | % of households owning ≥1 mobile phone | **Table A5.18** | Context for mobile-money channels; not an inclusion measure |
| Households with a smartphone [`smartphone_households`] | EICV7 | 2023/24 | national, urban/rural, province, district | % of households owning ≥1 smartphone | **Table A5.19** | Context: app-based channels |
| Households with internet at home [`internet_households`] | EICV7 | 2023/24 | national, urban/rural, province, district | % of households with internet at home, incl. via mobile phone | **Table A5.15** | Context |
| Population with health insurance [`health_insurance`] | EICV7 | 2023/24 | national, urban/rural, province, district | % of individuals with any health insurance | **Table A3.7** | Context: social-protection reach |
| Poverty 2017, modelled [`poverty_decrease.poverty_2017_modelled`] | EICV7 Poverty Profile | 2017 (modelled) | district, province, national | NISR prediction of 2017 headcount poverty on the EICV7 consumption basis | **Annex B** (district), **Table 5.1** (province) | Model-based, no district CI |
| Poverty reduction [`poverty_decrease`] | EICV7 Poverty Profile | 2017→2023/24 | district, province, national | Printed fall in headcount poverty, percentage points | Annex B / Table 5.1 | Uses NISR's printed change |
| Banked [`banked`] | FinScope | 2024 | national, province, district | % of adults 16+ with a commercial-bank product | Report **Fig. 13** (district), Fig. 12, Fig. 5 | Access strand segment; whole % |
| Other formal (non-bank) [`other_formal`] | FinScope | 2024 | as above | % of adults served by regulated non-bank providers (mobile money, SACCO, MFI, insurance…) but not banks | as above | |
| Informal only [`informal_only`] | FinScope | 2024 | as above | % of adults using only informal mechanisms (e.g. savings groups) | as above | Nyarugenge recorded as 0 (segment not visible; < 0.5) |
| Financially excluded [`excluded`] | FinScope | 2024 | as above | % of adults using no formal or informal product; save at home / borrow from family | as above | Default exclusion measure for scoring |

## National-only context

| Variable [API path] | Source | Notes |
| --- | --- | --- |
| Access strand by group [`who_is_excluded.groups`] | FinScope 2024 Fig. 6–11 | area, gender, age (16–17, 18–30, 31–60, 61+), disability, refugees, main income source; 2024 only |
| Access strand 2020 vs 2024 [`who_is_excluded.national_trend`] | FinScope 2024 Fig. 5 | |
| Accounts in own name by product [`who_is_excluded.products`] | FinScope 2024 p.12 | mobile money, SACCO, insurance, pension, bank, MFI, any |
| VUP beneficiaries [`who_is_excluded.vup`] | EICV7 Tables 10.1, 10.2, 10.4 | count (thousands), poverty rate among beneficiaries, component shares |

Transcription files: `data/manual/finscope2024_access_strand.csv`, `finscope2024_access_strand_groups.csv`,
`finscope2024_products.csv`, `eicv7_poverty_profile_annex_b.csv` — verified by `scripts/verify_transcriptions.py`.

## Derived (our calculation)

| Variable [API id] | Formula | Notes |
| --- | --- | --- |
| Not formally served [`not_formally_served`] | informal_only + excluded | Alternative exclusion measure for robustness |
| Formally served [`formally_served`] | banked + other_formal | Validated: national 92% |
| FinScope SE / CI | see `docs/methodology.md` §5 | **Approximate** (n = 400, deff 1.5, rounding) |
| Priority score [`score`] | w_p·minmax(poverty) + w_e·minmax(exclusion) | Estimate; weights user-set |
| Baseline rank [`baseline_rank`] | rank by poverty_rate | Poverty-only targeting |
| Rank shift [`rank_shift`] | baseline_rank − rank | Positive = moves up under combined score |
| P(top 5), rank range [`uncertainty`] | Monte Carlo, 2,000 draws | Estimate |
| Profile [`profile.type`] | typology rules, methodology §7 | Aggregate pattern, not household label |
| Flags [`profile.flags`] | informal reliance, bank-led, slow poverty reduction, low smartphone ownership — methodology §7 | Context; do not change the score |

## Geography

* Unit: the **30 districts** of Rwanda, grouped into 5 provinces (City of Kigali, Southern,
  Western, Northern, Eastern). District names in EICV7, FinScope and geoBoundaries ADM2 match
  exactly — no crosswalk edits were needed.
* Boundaries: geoBoundaries RWA ADM2 simplified (CC BY 4.0), coordinates rounded to 4 dp.

## Sources

| ID | File (data/raw) | URL |
| --- | --- | --- |
| A1 | `eicv7/EICV7_Main_Indicator_Report.pdf` | https://statistics.gov.rw/sites/default/files/documents/2025-07/EICV7_Main%20Indicator%20Report.pdf |
| A2 | `eicv7/EICV7_Tables_MainIndicatorReport.xlsx` | https://statistics.gov.rw/sites/default/files/documents/2025-04/EICV7_Tables_MainIndicatorReport.xlsx |
| A3a | `eicv7/EICV7_Poverty_Profile.pdf` | https://statistics.gov.rw/sites/default/files/documents/2025-07/EICV7_Poverty%20Profile.pdf |
| A3b | `eicv7/EICV7_Tables_Rwanda_Poverty_Profile.xlsx` | https://statistics.gov.rw/sites/default/files/documents/2025-05/EICV7_Tables_Rwanda_Poverty_Profile.xlsx |
| A4 | `finscope/Rwanda-Finscope-2024-Report_compressed.pdf` | https://statistics.gov.rw/sites/default/files/documents/2024-09/Rwanda-Finscope-2024-Report_compressed.pdf |
| C1s | `geo/geoBoundaries-RWA-ADM2_simplified.geojson` | https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/gbOpen/RWA/ADM2/geoBoundaries-RWA-ADM2_simplified.geojson |

SHA-256 checksums: `data/provenance/downloads.json`.

## Sources considered and not used

| Candidate | Reason |
| --- | --- |
| EICV7 Table A8.22, households sending transfers | Sending remittances is not an access or need indicator for this decision |
| EICV7 Table A6.20, workforce-to-population ratio | Labour-market context with a weak link to financial access |
| EICV7 Table A5.14, electricity for lighting | Infrastructure, not specific to financial inclusion |
| Extreme poverty by district | Published only by province (Table 9.2) |
| FinScope population-group strands by district | Published only nationally |
| BNR inclusion dashboard, Global Findex, IMF Financial Access Survey | Different definitions and no district-level demand-side data |
