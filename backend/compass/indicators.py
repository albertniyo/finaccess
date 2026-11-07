"""Indicator catalogue and district series for the Intervention Gap Explorer."""

from __future__ import annotations

from compass import data, typology, uncertainty

EICV7_SOURCE = "eicv7-tables"
FINSCOPE_SOURCE = "finscope-2024"

CATALOGUE: list[dict] = [
    {
        "id": "poverty_rate",
        "label": "Headcount poverty",
        "unit": "% of population",
        "definition": (
            "Share of individuals living in households whose consumption per adult equivalent "
            "is below the EICV7 national poverty line."
        ),
        "survey": "EICV7 2023/24",
        "source": EICV7_SOURCE,
        "reference": "Table A9.23 (district), Table 9.1",
        "geo_levels": ["national", "area", "province", "district"],
        "higher_is_worse": True,
        "kind": "observed",
        "uncertainty": "Published design-based SE and 95% CI",
    },
    {
        "id": "excluded",
        "label": "Financially excluded adults",
        "unit": "% of adults 16+",
        "definition": (
            "Adults who use no formal or informal financial product or mechanism; they save at "
            "home and borrow from family or friends (FinScope access strand)."
        ),
        "survey": "FinScope Rwanda 2024",
        "source": FINSCOPE_SOURCE,
        "reference": "Figure 13 (district), Figure 12 (province), Figure 5 (national)",
        "geo_levels": ["national", "province", "district"],
        "higher_is_worse": True,
        "kind": "observed",
        "uncertainty": "Published as whole %; interval is our approximation (n≈400, deff 1.5)",
    },
    {
        "id": "not_formally_served",
        "label": "Not formally served",
        "unit": "% of adults 16+",
        "definition": (
            "Adults with no bank or other formal (e.g. mobile money, SACCO, MFI, insurance) "
            "product: informal-only plus excluded segments of the access strand."
        ),
        "survey": "FinScope Rwanda 2024",
        "source": FINSCOPE_SOURCE,
        "reference": "Figure 13 (sum of Informal ONLY and Excluded)",
        "geo_levels": ["national", "province", "district"],
        "higher_is_worse": True,
        "kind": "observed",
        "uncertainty": "Sum of two rounded labels (±1 pp rounding); interval approximated",
    },
    {
        "id": "informal_only",
        "label": "Informal only",
        "unit": "% of adults 16+",
        "definition": "Adults using only informal mechanisms (e.g. savings groups), no formal product.",
        "survey": "FinScope Rwanda 2024",
        "source": FINSCOPE_SOURCE,
        "reference": "Figure 13",
        "geo_levels": ["national", "province", "district"],
        "higher_is_worse": True,
        "kind": "observed",
        "uncertainty": "Published as whole %; interval approximated",
    },
    {
        "id": "banked",
        "label": "Banked",
        "unit": "% of adults 16+",
        "definition": "Adults with a product or service from a commercial bank.",
        "survey": "FinScope Rwanda 2024",
        "source": FINSCOPE_SOURCE,
        "reference": "Figure 13",
        "geo_levels": ["national", "province", "district"],
        "higher_is_worse": False,
        "kind": "observed",
        "uncertainty": "Published as whole %; interval approximated",
    },
    {
        "id": "poverty_decrease",
        "label": "Poverty reduction 2017–2024",
        "unit": "percentage points",
        "definition": (
            "Fall in headcount poverty from 2017 (EICV5, modelled by NISR on the EICV7 basis) to "
            "2023/24. Smaller falls flag districts where poverty is persistent."
        ),
        "survey": "EICV7 Poverty Profile 2023/24",
        "source": "eicv7-poverty-profile",
        "reference": "Annex B (district), Table 5.1 (province, national)",
        "geo_levels": ["national", "province", "district"],
        "higher_is_worse": False,
        "kind": "observed",
        "uncertainty": "2017 values are model predictions; no district CI published",
        "group": "context",
    },
    {
        "id": "mobile_phone_households",
        "label": "Households owning a mobile phone",
        "unit": "% of households",
        "definition": (
            "Households owning at least one mobile phone — context for mobile-money delivery "
            "channels (not a measure of financial inclusion)."
        ),
        "survey": "EICV7 2023/24",
        "source": EICV7_SOURCE,
        "reference": "Table A5.18",
        "geo_levels": ["national", "province", "district"],
        "higher_is_worse": False,
        "kind": "observed",
        "uncertainty": "Published design-based SE and 95% CI",
        "group": "context",
    },
    {
        "id": "smartphone_households",
        "label": "Households owning a smartphone",
        "unit": "% of households",
        "definition": (
            "Households owning at least one smartphone — readiness for app-based digital financial "
            "services beyond USSD mobile money."
        ),
        "survey": "EICV7 2023/24",
        "source": EICV7_SOURCE,
        "reference": "Table A5.19",
        "geo_levels": ["national", "area", "province", "district"],
        "higher_is_worse": False,
        "kind": "observed",
        "uncertainty": "Published design-based SE and 95% CI",
        "group": "context",
    },
    {
        "id": "internet_households",
        "label": "Households with internet at home",
        "unit": "% of households",
        "definition": "Households with internet access at home, including through mobile phones.",
        "survey": "EICV7 2023/24",
        "source": EICV7_SOURCE,
        "reference": "Table A5.15",
        "geo_levels": ["national", "area", "province", "district"],
        "higher_is_worse": False,
        "kind": "observed",
        "uncertainty": "Published design-based SE and 95% CI",
        "group": "context",
    },
    {
        "id": "health_insurance",
        "label": "Population with health insurance",
        "unit": "% of population",
        "definition": (
            "Individuals covered by any health insurance (93% of them via community-based Mutuelle) — "
            "a proxy for social-protection and risk-pooling reach."
        ),
        "survey": "EICV7 2023/24",
        "source": EICV7_SOURCE,
        "reference": "Table A3.7",
        "geo_levels": ["national", "area", "province", "district"],
        "higher_is_worse": False,
        "kind": "observed",
        "uncertainty": "Published design-based SE and 95% CI",
        "group": "context",
    },
]
for _c in CATALOGUE:
    _c.setdefault("group", "core")
CATALOGUE_BY_ID = {c["id"]: c for c in CATALOGUE}
FINSCOPE_FIELDS = ("excluded", "not_formally_served", "informal_only", "banked")
EICV_FIELDS = ("poverty_rate", "mobile_phone_households", "smartphone_households", "internet_households",
               "health_insurance")


def _eicv_value(est: dict) -> dict:
    return {"value": est["value"], "se": est["se"], "ci": [est["ci_low"], est["ci_high"]],
            "cv": est["cv"], "uncertainty": "published"}


def _finscope_value(percent: float) -> dict:
    low, high = uncertainty.finscope_ci(percent)
    return {"value": percent, "se": round(uncertainty.finscope_se(percent), 2),
            "ci": [round(low, 1), round(high, 1)], "uncertainty": "approximate"}


def flatten(area: dict) -> dict:
    """One row per geography with every indicator as {value, se, ci}."""
    row: dict = {field: _eicv_value(area[field]) for field in EICV_FIELDS}
    trend = area["poverty_trend"]
    row["poverty_decrease"] = {"value": trend["decrease_pp"], "uncertainty": "modelled",
                               "poverty_2017_modelled": trend["poverty_2017_modelled"]}
    fs = area["finscope"]
    for field in FINSCOPE_FIELDS:
        row[field] = _finscope_value(fs[field])
    row["other_formal"] = {"value": fs["other_formal"], "uncertainty": "approximate"}
    row["access_strand"] = {k: fs[k] for k in ("banked", "other_formal", "informal_only", "excluded")}
    row["transcription_note"] = fs.get("transcription_note")
    return row


def district_rows() -> list[dict]:
    dataset = data.load_dataset()
    national = dataset["national"]
    rows = []
    for d in dataset["districts"]:
        row = {"district": d["district"], "province": d["province"], **flatten(d)}
        row["profile"] = typology.classify(d, national)
        rows.append(row)
    return rows


DIMENSION_LABELS = {
    "national": "All adults",
    "area": "Area",
    "gender": "Gender",
    "age": "Age group",
    "disability": "Disability",
    "refugee": "Refugees",
    "livelihood": "Main income source",
}


def national_context() -> dict:
    """National FinScope breakdowns by group, product uptake and VUP — observed, national only."""
    national = data.load_dataset()["national"]
    groups = []
    for g in national["finscope_groups"]:
        if g["year"] != 2024:
            continue
        groups.append({
            "dimension": g["dimension"],
            "dimension_label": DIMENSION_LABELS[g["dimension"]],
            "group": g["group"],
            "access_strand": {k: g[k] for k in ("banked", "other_formal", "informal_only", "excluded")},
            "excluded": g["excluded"],
            "formally_served": g["formally_served"],
            "source_figure": g["source_figure"],
            "transcription_note": g["transcription_note"],
        })
    trend = [
        {"year": g["year"], "access_strand": {k: g[k] for k in ("banked", "other_formal", "informal_only", "excluded")}}
        for g in national["finscope_groups"] if g["dimension"] == "national"
    ]
    nat_excl = national["finscope"]["excluded"]
    highest = sorted((g for g in groups if g["dimension"] != "national"), key=lambda g: -g["excluded"])[:3]
    return {
        "groups": groups,
        "national_trend": trend,
        "products": national["finscope_products"],
        "vup": national["vup"],
        "highlights": [
            f"{g['group']} ({g['dimension_label'].lower()}): {g['excluded']}% excluded vs {nat_excl}% of all adults"
            for g in highest
        ],
        "provenance": {
            "kind": "observed",
            "geo_level": "national",
            "references": {
                "groups": "FinScope Rwanda 2024, Figures 5–11",
                "products": "FinScope Rwanda 2024, p.12",
                "vup": national["vup"]["reference"],
            },
            "note": (
                "Group breakdowns are national only — FinScope does not publish them by district. "
                "VUP beneficiary statistics come from a separate VUP survey and are national only."
            ),
        },
    }


def get_indicators(province: str | None = None) -> dict:
    """Explorer payload: indicator catalogue + national / province / district series."""
    dataset = data.load_dataset()
    provinces = data.province_names()
    if province is not None:
        match = next((p for p in provinces if p.lower() == province.strip().lower()), None)
        if match is None:
            raise ValueError(f"Unknown province '{province}'. Allowed: {provinces}")
        province = match

    districts = district_rows()
    if province:
        districts = [d for d in districts if d["province"] == province]

    national = dataset["national"]
    return {
        "status": "ok",
        "geo_level": "district",
        "filters": {"province": province, "available": {"province": provinces}},
        "unsupported_filters": {
            "urban_rural": "District tables are not published by urban/rural for both surveys.",
            "sex_age": "Not available at district level in the published tables used.",
        },
        "indicators": CATALOGUE,
        "national": {
            **flatten(national),
            "extreme_poverty_rate": _eicv_value(national["extreme_poverty_rate"]),
            "poverty_2017_modelled": national["poverty_trend"]["poverty_2017_modelled"],
            "urban_poverty_rate": _eicv_value(national["urban_poverty_rate"]),
            "rural_poverty_rate": _eicv_value(national["rural_poverty_rate"]),
        },
        "provinces": [
            {"province": p["province"], **flatten(p),
             "extreme_poverty_rate": _eicv_value(p["extreme_poverty_rate"])}
            for p in dataset["provinces"]
        ],
        "districts": districts,
        "who_is_excluded": national_context(),
        "typology": typology.DEFINITIONS,
        "flags": typology.FLAG_DEFINITIONS,
        "provenance": {
            "kind": "observed",
            "references": dataset["meta"]["references"],
            "uncertainty_assumptions": uncertainty.ASSUMPTIONS,
            "known_discrepancies": dataset["meta"]["known_discrepancies"],
            "linkage": "EICV7 and FinScope are separate samples; compared only as district aggregates.",
        },
    }
