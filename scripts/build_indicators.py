#!/usr/bin/env python3
"""Build district aggregates from data/raw → data/processed.

Inputs (run scripts/download_sources.py first):
  - EICV7 Main Indicator Report tables (A2), estimate / SE / 95% CI sheets:
      Table A9.23 poverty · Table 9.2 extreme poverty · Table A5.18 mobile phone ·
      Table A5.19 smartphone · Table A5.15 internet at home · Table A3.7 health insurance ·
      Tables 10.1 / 10.2 / 10.4 VUP (national context)
  - EICV7 Poverty Profile tables (A3b): Table 5.1 (2017 modelled poverty by province)
  - Hand transcriptions in data/manual/ (verified by scripts/verify_transcriptions.py):
      finscope2024_access_strand.csv (Fig. 5, 12, 13) · finscope2024_access_strand_groups.csv
      (Fig. 5–11) · finscope2024_products.csv (p.12) · eicv7_poverty_profile_annex_b.csv
  - geoBoundaries RWA ADM2 simplified GeoJSON

Outputs:
  - data/processed/districts.json     app contract (published values only)
  - data/processed/districts.geojson  district outlines for the choropleth
  - data/provenance/validation.json   golden + consistency checks against the published reports

Usage (from repo root, using the backend environment for openpyxl):
    cd backend && uv run python ../scripts/build_indicators.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import sys
from pathlib import Path

import openpyxl

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MANUAL = ROOT / "data" / "manual"
PROCESSED = ROOT / "data" / "processed"
PROVENANCE = ROOT / "data" / "provenance"

EICV7_TABLES = RAW / "eicv7" / "EICV7_Tables_MainIndicatorReport.xlsx"
POVERTY_PROFILE_TABLES = RAW / "eicv7" / "EICV7_Tables_Rwanda_Poverty_Profile.xlsx"
FINSCOPE_CSV = MANUAL / "finscope2024_access_strand.csv"
FINSCOPE_GROUPS_CSV = MANUAL / "finscope2024_access_strand_groups.csv"
FINSCOPE_PRODUCTS_CSV = MANUAL / "finscope2024_products.csv"
ANNEX_B_CSV = MANUAL / "eicv7_poverty_profile_annex_b.csv"
GEOJSON = RAW / "geo" / "geoBoundaries-RWA-ADM2_simplified.geojson"
TRANSCRIPTION_CHECK = PROVENANCE / "transcription_check.json"

PROVINCE_OF = {
    "City of Kigali": ["Nyarugenge", "Gasabo", "Kicukiro"],
    "Southern": ["Nyanza", "Gisagara", "Nyaruguru", "Huye", "Nyamagabe", "Ruhango", "Muhanga", "Kamonyi"],
    "Western": ["Karongi", "Rutsiro", "Rubavu", "Nyabihu", "Ngororero", "Rusizi", "Nyamasheke"],
    "Northern": ["Rulindo", "Gakenke", "Musanze", "Burera", "Gicumbi"],
    "Eastern": ["Rwamagana", "Nyagatare", "Gatsibo", "Kayonza", "Kirehe", "Ngoma", "Bugesera"],
}
DISTRICT_PROVINCE = {d: p for p, ds in PROVINCE_OF.items() for d in ds}
PROVINCES = list(PROVINCE_OF)
POVERTY_PROFILE_PROVINCE = {"Kigali City": "City of Kigali", "South": "Southern", "West": "Western",
                            "North": "Northern", "East": "Eastern"}

# EICV7 estimate sheets with district rows: output key → (sheet, citation)
EICV_DISTRICT_SHEETS = {
    "poverty_rate": ("Table A9.23", "EICV7 Main Indicator Report tables, Table A9.23"),
    "mobile_phone_households": ("Table A5.18", "EICV7 Main Indicator Report tables, Table A5.18"),
    "smartphone_households": ("Table A5.19", "EICV7 Main Indicator Report tables, Table A5.19"),
    "internet_households": ("Table A5.15", "EICV7 Main Indicator Report tables, Table A5.15"),
    "health_insurance": ("Table A3.7", "EICV7 Main Indicator Report tables, Table A3.7"),
}

# Published figures quoted in report text/annexes, used to validate the ETL.
GOLDEN_POVERTY = {
    ("national", "Rwanda"): 27.4,
    ("area", "Urban"): 16.7,
    ("area", "Rural"): 31.6,
    ("province", "Western"): 37.4,
    ("province", "Southern"): 34.7,
    ("province", "Eastern"): 26.8,
    ("province", "Northern"): 20.2,
    ("province", "City of Kigali"): 9.1,
    ("district", "Nyamagabe"): 51.4,
    ("district", "Gisagara"): 45.6,
    ("district", "Rusizi"): 44.2,
    ("district", "Nyanza"): 43.3,
    ("district", "Nyamasheke"): 42.7,
    ("district", "Nyarugenge"): 6.8,
    ("district", "Kicukiro"): 6.9,
    ("district", "Gasabo"): 11.1,
}
GOLDEN_EXTREME_NATIONAL = 5.4
# (indicator, expected national value, tolerance, reference)
GOLDEN_NATIONAL_CONTEXT = [
    ("health_insurance", 85.3, 0.06, "EICV7 Main Indicators Report, key findings: 'Health insurance coverage expanded to 85.3%'"),
    ("internet_households", 29.8, 0.06, "EICV7 Main Indicators Report, key indicators table row 26 (29.8)"),
    ("smartphone_households", 34.0, 0.5, "EICV7 Main Indicators Report summary: 'smartphones (34%)'"),
    ("mobile_phone_households", 85.0, 0.5, "EICV7 Main Indicators Report summary: 'mobile phones (85% vs 67%)' — EICV7 vs EICV5"),
]
GOLDEN_AREA_CONTEXT = [
    ("internet_households", "Urban", 57.0, "EICV7 Main Indicators Report summary: 'In urban areas, 57% of the households'"),
    ("internet_households", "Rural", 19.0, "EICV7 Main Indicators Report summary: 'compared to 19% in rural areas'"),
]
# FinScope narrative claims about the demographic strands (Figures 6–10)
GOLDEN_GROUP_INCLUDED = [
    ("area", "Urban", 97, "FinScope 2024 p.27: '97% of the urban population'"),
    ("area", "Rural", 96, "FinScope 2024 p.27: 'About 96% of the rural populace'"),
    ("gender", "Male", 97, "FinScope 2024 p.28: '97% of males'"),
    ("gender", "Female", 96, "FinScope 2024 p.28: '96% of females are financially included'"),
    ("disability", "Adults with disabilities", 93, "FinScope 2024 p.29: 'About 93% of people with disabilities'"),
]
GOLDEN_GROUP_FORMAL = [
    ("gender", "Male", 94, "FinScope 2024 p.28: 'formally served males (94%)'"),
    ("gender", "Female", 90, "FinScope 2024 p.28: 'versus females (90%)'"),
]
# Annex B (PDF) vs Table A9.23 (Excel) differences beyond rounding, documented in methodology.
ANNEX_B_KNOWN_DIFFERENCES = {"Burera", "Nyabihu", "Nyamasheke", "Rwamagana"}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def r(value: float, digits: int = 2) -> float:
    return round(float(value), digits)


def read_estimate_table(ws) -> dict[tuple[str, str], dict]:
    """Parse an EICV7 'estimate / SE / CI / CV / deff' sheet into {(level, name): estimate}."""
    rows: dict[tuple[str, str], dict] = {}
    section = "national"
    for row in ws.iter_rows(min_row=3, values_only=True):
        label = row[0]
        if not isinstance(label, str):
            continue
        label = label.strip()
        if row[1] is None:
            lowered = label.lower()
            if "district" in lowered:
                section = "district"
            elif "province" in lowered:
                section = "province"
            elif "area" in lowered:
                section = "area"
            else:
                section = "other"
            continue
        if label in {"Poverty Rate", "Rwanda"}:
            level, name = "national", "Rwanda"
        elif label in {"Urban", "Rural"}:
            level, name = "area", label
        elif label in DISTRICT_PROVINCE:
            level, name = "district", label
        elif label in PROVINCE_OF:
            level, name = "province", label
        else:
            level, name = section, label
        rows[(level, name)] = {
            "value": r(row[1]),
            "se": r(row[2], 3),
            "ci_low": r(row[3]),
            "ci_high": r(row[4]),
            "cv": r(row[5]),
            "deff": r(row[6], 3),
        }
    return rows


def read_province_2017(ws) -> dict[str, dict]:
    """Poverty Profile Table 5.1: EICV5 (2017, modelled) poverty and printed change, by province + national."""
    out = {}
    for row in ws.iter_rows(values_only=True):
        label = row[0].strip() if isinstance(row[0], str) else None
        name = "Rwanda" if label == "Rwanda" else POVERTY_PROFILE_PROVINCE.get(label or "")
        if name:
            out[name] = {"poverty_2017_modelled": float(row[3]), "decrease_pp": r(-float(row[5]), 1)}
    return out


def read_vup(wb) -> dict:
    """VUP social-protection context (national only): Tables 10.1, 10.2, 10.4."""
    t101 = next(wb["Table 10.1"].iter_rows(min_row=4, max_row=4, values_only=True))
    t102 = list(wb["Table 10.2"].iter_rows(min_row=3, max_row=4, values_only=True))
    t104 = next(wb["Table 10.4"].iter_rows(min_row=5, max_row=5, values_only=True))
    components = dict(zip(t102[0][2:7], t102[1][2:7], strict=True))
    return {
        "beneficiaries_thousands": r(t101[3], 1),
        "population_thousands": r(t101[1], 1),
        "poverty_rate_beneficiaries": r(t104[2], 1),
        "poverty_rate_all": r(t104[1], 1),
        "component_shares": {k.strip(): r(v, 1) for k, v in components.items()},
        "reference": "EICV7 Main Indicator Report tables, Tables 10.1, 10.2, 10.4 (EICV7 cross-section + VUP survey)",
    }


def strand(rec: dict) -> dict:
    banked, other = int(rec["banked"]), int(rec["other_formal"])
    informal, excluded = int(rec["informal_only"]), int(rec["excluded"])
    return {
        "banked": banked,
        "other_formal": other,
        "informal_only": informal,
        "excluded": excluded,
        "formally_served": banked + other,
        "not_formally_served": informal + excluded,
        "strand_sum": banked + other + informal + excluded,
    }


def load_finscope() -> dict[tuple[str, str], dict]:
    out = {}
    with FINSCOPE_CSV.open(newline="") as fh:
        for rec in csv.DictReader(fh):
            out[(rec["level"], rec["name"])] = {
                **strand(rec),
                "source_figure": rec["source_figure"],
                "transcription_note": rec["transcription_note"] or None,
            }
    return out


def load_finscope_groups() -> list[dict]:
    with FINSCOPE_GROUPS_CSV.open(newline="") as fh:
        return [
            {"dimension": rec["dimension"], "group": rec["group"], "year": int(rec["year"]), **strand(rec),
             "source_figure": rec["source_figure"], "transcription_note": rec["transcription_note"] or None}
            for rec in csv.DictReader(fh)
        ]


def load_products() -> list[dict]:
    with FINSCOPE_PRODUCTS_CSV.open(newline="") as fh:
        return [{"product": rec["product"], "percent_adults": int(rec["percent_adults"]),
                 "source": rec["source"], "note": rec["note"] or None} for rec in csv.DictReader(fh)]


def load_annex_b() -> dict[str, dict]:
    with ANNEX_B_CSV.open(newline="") as fh:
        return {
            rec["district"]: {"poverty_2017_modelled": float(rec["eicv5_2017_modelled"]),
                              "poverty_2024_annex": float(rec["eicv7_2024"]),
                              "decrease_pp": float(rec["decrease_pp"]),
                              "note": rec["note"] or None}
            for rec in csv.DictReader(fh)
        }


def simplify_geojson() -> dict:
    data = json.loads(GEOJSON.read_text())

    def round_coords(coords):
        if isinstance(coords[0], (int, float)):
            return [round(coords[0], 4), round(coords[1], 4)]
        return [round_coords(c) for c in coords]

    features = []
    for feat in data["features"]:
        name = feat["properties"]["shapeName"].strip()
        if name not in DISTRICT_PROVINCE:
            raise SystemExit(f"GeoJSON district not in crosswalk: {name!r}")
        geom = feat["geometry"]
        features.append(
            {
                "type": "Feature",
                "properties": {"district": name, "province": DISTRICT_PROVINCE[name]},
                "geometry": {"type": geom["type"], "coordinates": round_coords(geom["coordinates"])},
            }
        )
    return {"type": "FeatureCollection", "features": features}


class Checks:
    def __init__(self) -> None:
        self.items: list[dict] = []

    def add(self, name: str, expected, observed, passed: bool, ref: str, tolerance: float = 0,
            group: str = "golden") -> None:
        self.items.append({"check": name, "group": group, "expected": expected, "observed": observed,
                           "tolerance": tolerance, "pass": bool(passed), "reference": ref})

    def near(self, name: str, expected: float, observed: float, tolerance: float, ref: str,
             group: str = "golden") -> None:
        self.add(name, expected, observed, abs(float(observed) - float(expected)) <= tolerance, ref,
                 tolerance, group)

    @property
    def failed(self) -> list[dict]:
        return [c for c in self.items if not c["pass"]]


def main() -> int:
    inputs = (EICV7_TABLES, POVERTY_PROFILE_TABLES, FINSCOPE_CSV, FINSCOPE_GROUPS_CSV,
              FINSCOPE_PRODUCTS_CSV, ANNEX_B_CSV, GEOJSON)
    for path in inputs:
        if not path.exists():
            print(f"Missing input: {path.relative_to(ROOT)} — run scripts/download_sources.py", file=sys.stderr)
            return 1

    wb = openpyxl.load_workbook(EICV7_TABLES, read_only=True, data_only=True)
    eicv = {key: read_estimate_table(wb[sheet]) for key, (sheet, _) in EICV_DISTRICT_SHEETS.items()}
    extreme = read_estimate_table(wb["Table 9.2"])
    vup = read_vup(wb)
    pp_wb = openpyxl.load_workbook(POVERTY_PROFILE_TABLES, read_only=True, data_only=True)
    province_2017 = read_province_2017(pp_wb["Table 5.1."])
    finscope = load_finscope()
    groups = load_finscope_groups()
    products = load_products()
    annex_b = load_annex_b()
    poverty = eicv["poverty_rate"]

    def eicv_block(level: str, name: str) -> dict:
        return {key: table[(level, name)] for key, table in eicv.items()}

    districts = []
    for province, names in PROVINCE_OF.items():
        for name in names:
            fs = finscope.get(("district", name))
            missing = [k for k, t in eicv.items() if ("district", name) not in t]
            if missing or fs is None or name not in annex_b:
                raise SystemExit(f"Missing district row for {name}: {missing or 'finscope/annex B'}")
            trend = annex_b[name]
            districts.append(
                {
                    "district": name,
                    "province": province,
                    **eicv_block("district", name),
                    "poverty_trend": {
                        "poverty_2017_modelled": trend["poverty_2017_modelled"],
                        "decrease_pp": trend["decrease_pp"],
                        "annex_note": trend["note"],
                    },
                    "finscope": fs,
                }
            )

    provinces = []
    for name in PROVINCES:
        provinces.append(
            {
                "province": name,
                **eicv_block("province", name),
                "extreme_poverty_rate": extreme[("province", name)],
                "poverty_trend": province_2017[name],
                "finscope": finscope[("province", name)],
            }
        )

    national = {
        **eicv_block("national", "Rwanda"),
        "extreme_poverty_rate": extreme[("national", "Rwanda")],
        "urban_poverty_rate": poverty[("area", "Urban")],
        "rural_poverty_rate": poverty[("area", "Rural")],
        "by_area": {key: {a: table[("area", a)] for a in ("Urban", "Rural")} for key, table in eicv.items()},
        "poverty_trend": province_2017["Rwanda"],
        "finscope": finscope[("national", "Rwanda")],
        "finscope_groups": groups,
        "finscope_products": products,
        "vup": vup,
    }

    checks = Checks()
    for (level, name), expected in GOLDEN_POVERTY.items():
        checks.near(f"Poverty headcount — {name}", expected, poverty[(level, name)]["value"], 0.06,
                    "EICV7 Main Indicators Report text / Poverty Profile Annex B")
    checks.near("Extreme poverty — Rwanda", GOLDEN_EXTREME_NATIONAL, extreme[("national", "Rwanda")]["value"],
                0.06, "EICV7 Main Indicators Report")
    for key, expected, tol, ref in GOLDEN_NATIONAL_CONTEXT:
        checks.near(f"{key} — Rwanda", expected, eicv[key][("national", "Rwanda")]["value"], tol, ref)
    for key, area, expected, ref in GOLDEN_AREA_CONTEXT:
        checks.near(f"{key} — {area}", expected, eicv[key][("area", area)]["value"], 0.5, ref)
    for key, (sheet, _) in EICV_DISTRICT_SHEETS.items():
        rows = [v for (lvl, _), v in eicv[key].items() if lvl == "district"]
        checks.add(f"{sheet}: 30 districts, every estimate inside its 95% CI", 30, len(rows),
                   len(rows) == 30 and all(v["ci_low"] <= v["value"] <= v["ci_high"] for v in rows),
                   f"Excel sheet '{sheet}'", group="consistency")

    fs_nat = finscope[("national", "Rwanda")]
    checks.add("FinScope financially included — Rwanda", 96, 100 - fs_nat["excluded"],
               100 - fs_nat["excluded"] == 96, "FinScope 2024 §2.1")
    checks.add("FinScope formally served — Rwanda", 92, fs_nat["formally_served"],
               fs_nat["formally_served"] == 92, "FinScope 2024 §2.1")
    checks.add("FinScope banked — Rwanda", 22, fs_nat["banked"], fs_nat["banked"] == 22, "FinScope 2024 §2.3")
    above = sum(1 for d in districts if d["finscope"]["excluded"] > fs_nat["excluded"])
    checks.add("Districts with exclusion above national 4%", 12, above, above == 12,
               "FinScope 2024 p.30: 'Twelve districts have higher levels of financial exclusion'")
    top_informal = max(districts, key=lambda d: d["finscope"]["informal_only"])["district"]
    checks.add("Highest informal-only reliance", "Gicumbi", top_informal, top_informal == "Gicumbi",
               "FinScope 2024 p.30")
    sums = sorted({d["finscope"]["strand_sum"] for d in districts} | {g["strand_sum"] for g in groups})
    checks.add("All access strands (district + group) sum to 98–101", "98–101", sums,
               all(98 <= s <= 101 for s in sums), "Rounded figure labels", group="consistency")

    by_group = {(g["dimension"], g["group"]): g for g in groups if g["year"] == 2024}
    for dim, grp, expected, ref in GOLDEN_GROUP_INCLUDED:
        observed = 100 - by_group[(dim, grp)]["excluded"]
        checks.add(f"FinScope included — {grp}", expected, observed, observed == expected, ref)
    for dim, grp, expected, ref in GOLDEN_GROUP_FORMAL:
        observed = by_group[(dim, grp)]["formally_served"]
        checks.add(f"FinScope formally served — {grp}", expected, observed, observed == expected, ref)
    refugees = by_group[("refugee", "Refugees")]
    checks.add("FinScope refugees banked", 37, refugees["banked"], refugees["banked"] == 37,
               "FinScope 2024 p.29: '37% of refugees have bank accounts'")
    nat_2024 = by_group[("national", "All adults")]
    checks.add("Group file national strand equals district file national strand",
               [fs_nat[k] for k in ("banked", "other_formal", "informal_only", "excluded")],
               [nat_2024[k] for k in ("banked", "other_formal", "informal_only", "excluded")],
               all(nat_2024[k] == fs_nat[k] for k in ("banked", "other_formal", "informal_only", "excluded")),
               "Figure 5 vs Figure 10 'Total Population'", group="consistency")
    bank_product = next(p for p in products if p["product"] == "Bank")["percent_adults"]
    checks.add("Bank account uptake equals banked strand", fs_nat["banked"], bank_product,
               bank_product == fs_nat["banked"], "FinScope 2024 p.12 vs Figure 5", group="consistency")

    checks.near("Poverty 2017 (modelled) — Rwanda, Annex B vs Table 5.1", 39.8,
                province_2017["Rwanda"]["poverty_2017_modelled"], 0.06,
                "EICV7 Poverty Profile Annex B ('Rwanda 39.8') vs Excel Table 5.1")
    checks.near("Poverty decrease 2017–2024 — Rwanda", 12.4, province_2017["Rwanda"]["decrease_pp"], 0.06,
                "EICV7 Poverty Profile Annex B ('12.4') vs Excel Table 5.1", group="consistency")
    arithmetic_ok = [abs(t["poverty_2017_modelled"] - t["poverty_2024_annex"] - t["decrease_pp"]) <= 0.15
                     for t in annex_b.values()]
    checks.add("Annex B: decrease = 2017 − 2024 (±0.15 rounding) for all 30 districts", 30, sum(arithmetic_ok),
               all(arithmetic_ok), "EICV7 Poverty Profile Annex B", group="consistency")
    differing = sorted(n for n, t in annex_b.items()
                       if abs(t["poverty_2024_annex"] - poverty[("district", n)]["value"]) > 0.051)
    checks.add("Annex B 2024 column vs Excel Table A9.23: only documented differences",
               sorted(ANNEX_B_KNOWN_DIFFERENCES), differing, set(differing) == ANNEX_B_KNOWN_DIFFERENCES,
               "EICV7 Poverty Profile Annex B vs Main Indicator tables A9.23", group="consistency")
    checks.near("VUP beneficiaries (thousands)", 410.4, vup["beneficiaries_thousands"], 0.1,
                "EICV7 Table 10.1", group="consistency")

    transcription = json.loads(TRANSCRIPTION_CHECK.read_text()) if TRANSCRIPTION_CHECK.exists() else None
    if transcription is not None:
        checks.add("Hand transcriptions match PDF text layer (scripts/verify_transcriptions.py)",
                   transcription["passed"] + transcription["failed"], transcription["passed"],
                   transcription["failed"] == 0, "data/provenance/transcription_check.json", group="transcription")

    failed = checks.failed

    known_discrepancies = [
        {
            "item": "Gisagara headcount poverty",
            "detail": (
                "EICV7 Main Indicators Report narrative (§9) quotes 46.6%; the report's own district "
                "figure, Poverty Profile Annex B and Excel Table A9.23 all give 45.6%. We use 45.6%."
            ),
        },
        {
            "item": "Annex B vs Table A9.23 (2024 poverty)",
            "detail": (
                "Poverty Profile Annex B prints Burera 22.0 (Excel 21.8), Nyabihu 20.2 (Excel 20.4), "
                "Nyamasheke 42.8 (Excel 42.7) and Rwamagana 23.8 (Excel 23.9). We use the Excel values for "
                "2024 and Annex B only for the 2017 modelled values and the printed decrease."
            ),
        },
        {
            "item": "2017 district poverty is modelled",
            "detail": (
                "EICV5 (2017) district rates in Annex B are NISR model predictions on the EICV7 "
                "consumption basis, not EICV5 published rates; province CIs (Table 5.1) are model-dependent."
            ),
        },
    ]

    def ref(path: Path) -> dict:
        return {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)}

    meta = {
        "generated_by": "scripts/build_indicators.py",
        "geo_level": "district",
        "n_districts": len(districts),
        "inputs": [ref(p) for p in inputs],
        "references": {
            **{k: cite for k, (_, cite) in EICV_DISTRICT_SHEETS.items()},
            "extreme_poverty_rate": "EICV7 Main Indicator Report tables, Table 9.2",
            "poverty_trend": "EICV7 Poverty Profile, Annex B (district, PDF) and Table 5.1 (province/national, Excel)",
            "finscope": (
                "FinScope Rwanda 2024 Report (AFR/NISR), Figure 13 (district access strand), "
                "Figure 12 (province), Figure 5 (national); transcribed from figure labels"
            ),
            "finscope_groups": "FinScope Rwanda 2024 Report, Figures 5–11 (access strand by group)",
            "finscope_products": "FinScope Rwanda 2024 Report, p.12 (accounts in own name)",
            "vup": vup["reference"],
        },
        "units": "percent",
        "eicv7": {
            "survey": "EICV7 2023/24",
            "population": "Individuals (poverty, health insurance); households (phones, internet)",
            "design": "Stratified two-stage sample; estimates carry published SE and 95% CI",
        },
        "finscope": {
            "survey": "FinScope Rwanda 2024",
            "population": "Adults aged 16+",
            "design": "Stratified three-stage cluster sample, ~400–440 adults in most districts",
            "precision": "Published as whole percentages without standard errors",
        },
        "known_discrepancies": known_discrepancies,
        "transcription_check": (
            {"passed": transcription["passed"], "failed": transcription["failed"]} if transcription else None
        ),
    }

    PROCESSED.mkdir(parents=True, exist_ok=True)
    PROVENANCE.mkdir(parents=True, exist_ok=True)
    (PROCESSED / "districts.json").write_text(
        json.dumps({"meta": meta, "national": national, "provinces": provinces, "districts": districts},
                   indent=2) + "\n"
    )
    (PROCESSED / "districts.geojson").write_text(json.dumps(simplify_geojson(), separators=(",", ":")))
    (PROVENANCE / "validation.json").write_text(
        json.dumps({"passed": len(checks.items) - len(failed), "failed": len(failed), "checks": checks.items,
                    "known_discrepancies": known_discrepancies}, indent=2) + "\n"
    )

    print(f"Wrote {len(districts)} districts, {len(provinces)} provinces, {len(groups)} FinScope groups → data/processed/")
    print(f"Validation: {len(checks.items) - len(failed)} passed, {len(failed)} failed")
    if transcription is None:
        print("  note: run scripts/verify_transcriptions.py (needs pdftotext) to include the transcription check")
    for c in failed:
        print(f"  FAIL {c['check']}: expected {c['expected']}, observed {c['observed']}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
