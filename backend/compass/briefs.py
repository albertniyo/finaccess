"""Policy brief payload builder.

Every statement carries a `kind` so the UI can badge it:
observed (published statistic) · estimate (our calculation) · recommendation · scenario.
"""

from __future__ import annotations

from datetime import date

from compass import data, scenarios, scoring, sources, typology, uncertainty

NEXT_STEPS_BY_TYPE = {
    "compound_gap": [
        "Map which sectors combine high poverty with weak agent / mobile-money coverage.",
        (
            "Check whether social-protection (e.g. VUP) payments in the district reach beneficiaries "
            "through accounts or wallets, and where they do not."
        ),
        "Design any programme as a joint poverty + access response, then pilot with a comparison group.",
    ],
    "poverty_led": [
        (
            "Basic access is broadly in place: investigate depth of use (savings, credit, insurance) "
            "rather than new account-opening campaigns."
        ),
        "Review livelihood and graduation programmes; financial products alone are unlikely to be the constraint.",
        "Request EICV7 microdata to test whether poor households in this district use credit and savings.",
    ],
    "access_gap": [
        "This district would be deprioritised by poverty-only targeting — review it explicitly.",
        (
            "Identify who the excluded adults are (dependants, older adults, remote cells) using "
            "FinScope microdata before choosing a channel."
        ),
        "Audit agent, SACCO and mobile-money coverage in the most remote sectors.",
    ],
    "lower_relative_need": [
        "Lower relative priority on these two indicators; monitor in the next survey round.",
        "Check sub-district pockets of need that district averages may hide.",
    ],
}


NEXT_STEPS_BY_FLAG = {
    "slow_poverty_reduction": (
        "Poverty has fallen much more slowly than nationally since 2017: review why existing programmes "
        "have had limited reach before adding new ones."
    ),
    "low_digital_readiness": (
        "Few households own smartphones: favour USSD mobile money, agents and SACCO branches over "
        "app-only products."
    ),
    "informal_reliance": (
        "Many adults rely only on savings groups: explore linking groups to SACCOs or mobile wallets."
    ),
}


def _stmt(text: str, kind: str, source: str | None = None) -> dict:
    return {"text": text, "kind": kind, "source": source}


def _fmt_ci(est: dict) -> str:
    return f"95% CI {est['ci_low']:.1f}–{est['ci_high']:.1f}"


def generate_brief(
    geo: str,
    poverty_weight: float = 0.5,
    exclusion_weight: float = 0.5,
    measure: str = scoring.DEFAULT_MEASURE,
) -> dict:
    district = data.find_district(geo)
    if district is None:
        raise LookupError(f"Unknown district '{geo}'. Allowed: {data.district_names()}")
    dataset = data.load_dataset()
    national = dataset["national"]
    province = next(p for p in dataset["provinces"] if p["province"] == district["province"])
    name = district["district"]

    priority = scoring.rank_priorities(poverty_weight, exclusion_weight, measure)
    row = next(r for r in priority["rankings"] if r["district"] == name)
    profile = typology.classify(district, national)
    fs = district["finscope"]
    pov = district["poverty_rate"]
    phone = district["mobile_phone_households"]
    smart = district["smartphone_households"]
    internet = district["internet_households"]
    health = district["health_insurance"]
    trend = district["poverty_trend"]
    measure_label = priority["measure"]["label"]
    eicv_ref = "EICV7 2023/24, Table A9.23"
    fs_ref = "FinScope Rwanda 2024, Figure 13"

    excl_lo, excl_hi = uncertainty.finscope_ci(fs["excluded"])
    findings = [
        _stmt(
            f"Headcount poverty in {name} is {pov['value']:.1f}% ({_fmt_ci(pov)}), versus "
            f"{national['poverty_rate']['value']:.1f}% nationally and "
            f"{province['poverty_rate']['value']:.1f}% in {district['province']}. "
            f"It ranks {row['baseline_rank']} of 30 districts.",
            "observed", eicv_ref,
        ),
        _stmt(
            f"{fs['excluded']}% of adults are financially excluded (national {national['finscope']['excluded']}%); "
            f"{fs['informal_only']}% rely only on informal mechanisms, {fs['other_formal']}% use other formal "
            f"(non-bank) services and {fs['banked']}% are banked.",
            "observed", fs_ref,
        ),
        _stmt(
            f"Poverty fell from {trend['poverty_2017_modelled']:.1f}% in 2017 (NISR modelled estimate) — a "
            f"{trend['decrease_pp']:.1f}-point fall versus {national['poverty_trend']['decrease_pp']:.1f} nationally.",
            "observed", "EICV7 Poverty Profile, Annex B",
        ),
        _stmt(
            f"{phone['value']:.1f}% of households own a mobile phone ({_fmt_ci(phone)}) and "
            f"{smart['value']:.1f}% a smartphone ({_fmt_ci(smart)}); national {national['mobile_phone_households']['value']:.1f}% "
            f"and {national['smartphone_households']['value']:.1f}%. {internet['value']:.1f}% have internet at home.",
            "observed", "EICV7 2023/24, Tables A5.18, A5.19, A5.15",
        ),
        _stmt(
            f"{health['value']:.1f}% of residents have health insurance ({_fmt_ci(health)}; national "
            f"{national['health_insurance']['value']:.1f}%).",
            "observed", "EICV7 2023/24, Table A3.7",
        ),
    ]

    shift = row["rank_shift"]
    shift_text = (
        f"moves up {shift} places" if shift > 0 else f"moves down {-shift} places" if shift < 0 else "keeps its position"
    )
    weights = priority["weights"]
    interpretation = [
        _stmt(
            f"Under a {weights['poverty']:.0%} poverty / {weights['exclusion']:.0%} exclusion weighting "
            f"({measure_label}), {name} ranks {row['rank']} of 30 on the combined score and {shift_text} "
            f"relative to poverty-only targeting (rank {row['baseline_rank']}).",
            "estimate", "FinAccess Compass scoring v1",
        ),
        _stmt(
            f"Profile: {profile['label']} — {typology.DEFINITIONS[profile['type']]['rule'].lower()}. "
            f"Poverty difference from national is {profile['confidence']['poverty_vs_national']}; "
            f"exclusion difference is {profile['confidence']['exclusion_vs_national']}.",
            "estimate", "District typology (aggregate)",
        ),
        _stmt(
            f"Allowing for sampling error in both surveys, {name} is in the top 5 in "
            f"{row['uncertainty']['p_top5']:.0%} of simulations and its rank lies between "
            f"{row['uncertainty']['rank_interval_90'][0]} and {row['uncertainty']['rank_interval_90'][1]} "
            f"in 90% of them. The exclusion interval is approximately {excl_lo:.1f}–{excl_hi:.1f}%.",
            "estimate", "Monte Carlo uncertainty",
        ),
    ]
    rng = row["top5_poverty_weight_range"]
    interpretation.append(_stmt(
        f"{name} enters the combined top 5 when the poverty weight is between {rng[0]:.2f} and {rng[1]:.2f}."
        if rng else f"{name} is not in the combined top 5 at any poverty weight from 0 to 1.",
        "estimate", "Weight sensitivity sweep",
    ))
    for flag in profile["flags"]:
        interpretation.append(_stmt(f"{flag['label']}: {flag['detail']}", "observed", flag["source"]))

    recommendations = [_stmt(t, "recommendation") for t in NEXT_STEPS_BY_TYPE[profile["type"]]]
    flag_ids = {f["id"] for f in profile["flags"]}
    for flag_id, text in NEXT_STEPS_BY_FLAG.items():
        if flag_id in flag_ids:
            recommendations.append(_stmt(text, "recommendation"))
    recommendations.append(_stmt(
        "Treat this ranking as a hypothesis for field verification, not a funding decision.",
        "recommendation",
    ))

    scenario_lines = []
    scen = scenarios.run_scenario(1_000_000, "combined_score", top_n=10, allocation="equal",
                                  poverty_weight=poverty_weight, exclusion_weight=exclusion_weight,
                                  measure=measure)
    for c in scen["comparison"]:
        scenario_lines.append(_stmt(
            f"{c['label']}: {name} {'is' if name in c['districts'] else 'is not'} among the 10 districts selected.",
            "scenario", "Hypothetical top-10 targeting rule",
        ))

    return {
        "status": "ok",
        "geo": name,
        "province": district["province"],
        "generated_on": date.today().isoformat(),
        "title": f"{name} District — financial inclusion & poverty priority brief",
        "weights": weights,
        "measure": priority["measure"],
        "summary": {
            "poverty_rate": pov["value"],
            "excluded": fs["excluded"],
            "rank": row["rank"],
            "baseline_rank": row["baseline_rank"],
            "rank_shift": shift,
            "profile": profile,
            "p_top5": row["uncertainty"]["p_top5"],
            "contributions": row["contributions"],
        },
        "sections": {
            "key_findings": findings,
            "interpretation": interpretation,
            "next_steps": recommendations,
            "scenario": scenario_lines,
            "methodology_notes": [
                priority["provenance"]["formula"] + " (" + priority["provenance"]["normalisation"] + ").",
                "Baseline: ranking by EICV7 headcount poverty alone.",
                "No household-level merge of EICV7 and FinScope; comparison at district aggregate only.",
                uncertainty.ASSUMPTIONS["note"],
            ],
            "limitations": priority["provenance"]["limitations"],
            "sources": sources.list_sources()["sources"],
        },
        "provenance": {
            "kind": "mixed",
            "note": "Each statement is badged observed / estimate / recommendation / scenario.",
        },
    }
