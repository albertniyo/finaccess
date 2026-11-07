# Demo script

About five minutes: one story in four steps, on https://finaccessrw.vercel.app.

**Opening (20 s).** "A planner has money for financial-inclusion work in a handful of districts. The
usual shortcut is to target the poorest. We test whether that shortcut misses anyone, using only
official NISR and FinScope numbers."

## 1. Find the gap — Explore (75 s)

1. Open **Explore gaps**. The map shows headcount poverty; Nyamagabe (51.4%) is darkest.
2. Switch the indicator to **Financially excluded adults**. A different set of districts lights up:
   Nyaruguru (10%), then Ngoma, Rulindo, Nyabihu and Gakenke (8%).
3. Scroll to the scatter plot. The shaded corner is above the national rate on both measures; the
   purple points (Rulindo, Nyabihu, Gakenke, Gicumbi, Huye) have high exclusion but below-average
   poverty.
4. Scroll to **Who is excluded nationally?** 16–17-year-olds (16%), dependants (11%), adults over 60
   and adults with disabilities (7% each) are excluded well above the 4% average — the *who* behind
   the *where*.

## 2. Examine the evidence (60 s)

1. Click **Ngoma**. Poverty is 30.9% (95% CI 25.8–36.1) and 8% of adults are excluded (approx.
   4.7–11.3), with province and national comparisons alongside.
2. Point at the badges: *Observed* is published data, *Estimate* is our calculation.
3. Note the honesty: poverty is within the margin of error of the national rate; exclusion clearly is
   not. The **slow poverty reduction** flag adds that poverty fell only 3.1 points since 2017, against
   12.4 nationally.
4. Open **Data notes**: separate samples, no household linkage, and the report's Gisagara typo.

## 3. Compare priorities — Prioritise (90 s)

1. Click **See its priority rank**. Weights start at 50/50.
2. Read the callout: 4 of the combined top 10 would be missed by poverty-only targeting. Ngoma moves
   from 13th to 4th; Nyamagabe drops out because only 1% of its adults are excluded.
3. Show the contribution bars (why) and the *In top 5* and rank-range columns (how sure).
4. Drag the slider to 75% poverty: Nyamagabe and Gisagara return. In the sensitivity table only
   Nyaruguru holds its place — "the weights are a policy choice, and the tool makes that choice
   visible."
5. Optional (20 s): run a 1 billion RWF scenario for 10 districts. Under poverty-only targeting 40% of
   the budget reaches districts with above-average exclusion; under the combined score, 80%.

## 4. Produce a brief — Policy brief (45 s)

1. Click **Brief →** for Gakenke: observed findings, our interpretation (a top-5 priority only when
   the poverty weight is 0.35 or less), next steps, limitations and sources.
2. **Print / save as PDF.**

**Close (20 s).** "Every number traces to a published table or figure, 50 automated checks tie the
data back to the reports, and the tool says how sure it is. It doesn't promise impact — it shows a
planner where to look first and who poverty targeting alone would miss."

## Before presenting

- Open the API's `/health` endpoint and confirm the sidebar shows the checks passing.
- Fallback: run the API and web app locally (see the README).
