"""District exclusion-pattern typology (aggregate profiles, not household labels).

Each district is placed relative to the national poverty rate (EICV7) and the national
financial-exclusion rate (FinScope). Because the two surveys sample different households,
a "compound gap" district is one where both aggregates are high — not a count of people
who are simultaneously poor and excluded.
"""

from __future__ import annotations

from compass import uncertainty

INFORMAL_RELIANCE_MULTIPLE = 2.0
BANK_LED_THRESHOLD = 50
SLOW_REDUCTION_SHARE = 0.5

FLAG_DEFINITIONS: dict[str, dict] = {
    "informal_reliance": {
        "label": "High informal-only reliance",
        "rule": f"Informal-only share ≥ {INFORMAL_RELIANCE_MULTIPLE:g}× national (FinScope)",
    },
    "bank_led": {
        "label": "Bank-led inclusion",
        "rule": f"Banked ≥ {BANK_LED_THRESHOLD}% (FinScope)",
    },
    "slow_poverty_reduction": {
        "label": "Slow poverty reduction",
        "rule": (
            f"Relative fall in poverty 2017 (modelled) → 2024 is less than {SLOW_REDUCTION_SHARE:.0%} of the "
            "national relative fall (EICV7 Poverty Profile Annex B)"
        ),
    },
    "low_digital_readiness": {
        "label": "Low smartphone ownership",
        "rule": (
            "Household smartphone ownership 95% CI entirely below the national rural rate "
            "(EICV7 Table A5.19) — low even by rural standards"
        ),
    },
}

DEFINITIONS: dict[str, dict] = {
    "compound_gap": {
        "label": "High poverty + exclusion gap",
        "rule": "Poverty above national AND financial exclusion above national",
        "response_focus": (
            "Investigate combined responses — e.g. whether social-protection transfers can be "
            "paid into accounts/mobile wallets, and which delivery channels are missing."
        ),
    },
    "poverty_led": {
        "label": "Poverty-led, access largely in place",
        "rule": "Poverty above national, exclusion at or below national",
        "response_focus": (
            "Basic access is largely reached; investigate depth of use (savings, credit, "
            "insurance) and livelihood constraints rather than new account campaigns."
        ),
    },
    "access_gap": {
        "label": "Exclusion gap outside poverty hotspots",
        "rule": "Poverty at or below national, exclusion above national",
        "response_focus": (
            "Likely missed by poverty-only targeting. Investigate who the excluded adults are "
            "(dependants, older adults, remote cells) and agent / channel coverage."
        ),
    },
    "lower_relative_need": {
        "label": "Lower relative need on both",
        "rule": "Poverty and exclusion at or below national",
        "response_focus": "Lower relative priority on these indicators; monitor.",
    },
}


def classify(district: dict, national: dict) -> dict:
    pov = district["poverty_rate"]
    excl = district["finscope"]["excluded"]
    informal = district["finscope"]["informal_only"]
    nat_pov = national["poverty_rate"]["value"]
    nat_excl = national["finscope"]["excluded"]
    nat_informal = national["finscope"]["informal_only"]

    high_poverty = pov["value"] > nat_pov
    high_exclusion = excl > nat_excl
    if high_poverty and high_exclusion:
        key = "compound_gap"
    elif high_poverty:
        key = "poverty_led"
    elif high_exclusion:
        key = "access_gap"
    else:
        key = "lower_relative_need"

    poverty_clear = uncertainty.differs_from(pov["value"], pov["se"], nat_pov)
    exclusion_clear = uncertainty.differs_from(excl, uncertainty.finscope_se(excl), nat_excl)

    flags = []

    def flag(flag_id: str, detail: str, source: str) -> None:
        flags.append({"id": flag_id, "label": FLAG_DEFINITIONS[flag_id]["label"], "detail": detail,
                      "source": source})

    if informal >= INFORMAL_RELIANCE_MULTIPLE * nat_informal:
        flag("informal_reliance",
             f"{informal}% of adults rely only on informal mechanisms (national {nat_informal}%). "
             "Consider linking savings groups to formal providers.",
             "FinScope Rwanda 2024, Figure 13")
    if district["finscope"]["banked"] >= BANK_LED_THRESHOLD:
        flag("bank_led", f"{district['finscope']['banked']}% banked — urban, bank-led access pattern.",
             "FinScope Rwanda 2024, Figure 13")
    trend, nat_trend = district.get("poverty_trend"), national.get("poverty_trend")
    if trend and nat_trend:
        rel = trend["decrease_pp"] / trend["poverty_2017_modelled"]
        nat_rel = nat_trend["decrease_pp"] / nat_trend["poverty_2017_modelled"]
        if rel < SLOW_REDUCTION_SHARE * nat_rel:
            flag("slow_poverty_reduction",
                 f"Poverty fell only {trend['decrease_pp']:.1f} points ({rel:.0%}) from a modelled "
                 f"{trend['poverty_2017_modelled']:.1f}% in 2017, versus a {nat_rel:.0%} fall nationally — persistent poverty.",
                 "EICV7 Poverty Profile, Annex B")
    phone = district.get("smartphone_households")
    rural_phone = national.get("by_area", {}).get("smartphone_households", {}).get("Rural")
    if phone and rural_phone and phone["ci_high"] < rural_phone["value"]:
        flag("low_digital_readiness",
             f"{phone['value']:.1f}% of households own a smartphone (95% CI {phone['ci_low']:.1f}–{phone['ci_high']:.1f}), "
             f"below even the rural average of {rural_phone['value']:.1f}% — app-only channels may not reach them; "
             "USSD and agents matter.",
             "EICV7 2023/24, Table A5.19")

    return {
        "type": key,
        "label": DEFINITIONS[key]["label"],
        "confidence": {
            "poverty_vs_national": "clear" if poverty_clear else "within margin of error",
            "exclusion_vs_national": "clear" if exclusion_clear else "within margin of error (approx.)",
        },
        "flags": flags,
    }
