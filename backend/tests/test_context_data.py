"""Golden + consistency tests for context data added in v1.1 (EICV7 annex tables, Annex B, FinScope groups)."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from compass import data, indicators, typology

ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def dataset() -> dict:
    return data.load_dataset()


def _district(dataset: dict, name: str) -> dict:
    return next(d for d in dataset["districts"] if d["district"] == name)


@pytest.mark.parametrize(
    ("field", "expected", "tol"),
    [("health_insurance", 85.3, 0.06), ("internet_households", 29.8, 0.06), ("smartphone_households", 34.0, 0.5)],
)
def test_national_context_golden(dataset: dict, field: str, expected: float, tol: float) -> None:
    assert dataset["national"][field]["value"] == pytest.approx(expected, abs=tol)


def test_every_district_has_context_with_ci(dataset: dict) -> None:
    for d in dataset["districts"]:
        for field in ("smartphone_households", "internet_households", "health_insurance"):
            est = d[field]
            assert est["ci_low"] <= est["value"] <= est["ci_high"], (d["district"], field)


def test_annex_b_trend(dataset: dict) -> None:
    nat = dataset["national"]["poverty_trend"]
    assert nat["poverty_2017_modelled"] == pytest.approx(39.8)
    assert nat["decrease_pp"] == pytest.approx(12.4)
    assert _district(dataset, "Nyamagabe")["poverty_trend"] == {
        "poverty_2017_modelled": 67.6, "decrease_pp": 16.2, "annex_note": None,
    }
    for d in dataset["districts"]:
        t = d["poverty_trend"]
        implied_2024 = t["poverty_2017_modelled"] - t["decrease_pp"]
        assert implied_2024 == pytest.approx(d["poverty_rate"]["value"], abs=0.35), d["district"]


def test_finscope_groups_match_narrative(dataset: dict) -> None:
    groups = {(g["dimension"], g["group"]): g for g in dataset["national"]["finscope_groups"] if g["year"] == 2024}
    assert 100 - groups[("area", "Urban")]["excluded"] == 97
    assert 100 - groups[("area", "Rural")]["excluded"] == 96
    assert groups[("gender", "Male")]["formally_served"] == 94
    assert groups[("gender", "Female")]["formally_served"] == 90
    assert groups[("age", "16-17")]["excluded"] == 16
    for g in groups.values():
        assert 98 <= g["strand_sum"] <= 101


def test_products_and_vup(dataset: dict) -> None:
    products = {p["product"]: p["percent_adults"] for p in dataset["national"]["finscope_products"]}
    assert products["Mobile money"] == 77
    assert products["Bank"] == dataset["national"]["finscope"]["banked"]
    vup = dataset["national"]["vup"]
    assert vup["poverty_rate_beneficiaries"] == pytest.approx(40.9)
    assert vup["beneficiaries_thousands"] == pytest.approx(410.4)


def test_flags_are_discriminating(dataset: dict) -> None:
    nat = dataset["national"]
    flagged = {
        fid: sorted(d["district"] for d in dataset["districts"]
                    if fid in {f["id"] for f in typology.classify(d, nat)["flags"]})
        for fid in typology.FLAG_DEFINITIONS
    }
    assert flagged["slow_poverty_reduction"] == ["Burera", "Ngoma", "Nyanza"]
    assert flagged["low_digital_readiness"] == ["Gisagara", "Nyamagabe", "Nyaruguru"]
    assert flagged["bank_led"] == ["Gasabo", "Kicukiro", "Nyarugenge"]


def test_catalogue_fields_present_on_every_row() -> None:
    rows = indicators.district_rows()
    for meta in indicators.CATALOGUE:
        for row in rows:
            assert "value" in row[meta["id"]], (row["district"], meta["id"])


def test_national_context_payload() -> None:
    ctx = indicators.national_context()
    assert len(ctx["groups"]) == 16
    assert ctx["highlights"][0].startswith("16-17")


def test_validation_covers_new_data() -> None:
    validation = data.load_validation()
    names = {c["check"] for c in validation["checks"]}
    assert validation["failed"] == 0
    assert any("Annex B" in n for n in names)
    assert any("Hand transcriptions" in n for n in names)
    assert {c["group"] for c in validation["checks"]} >= {"golden", "consistency", "transcription"}


def test_transcription_check_committed_and_passing() -> None:
    report = json.loads((ROOT / "data" / "provenance" / "transcription_check.json").read_text())
    assert report["failed"] == 0
    assert report["passed"] >= 90


@pytest.mark.skipif(
    shutil.which("pdftotext") is None
    or not (ROOT / "data" / "raw" / "finscope" / "Rwanda-Finscope-2024-Report_compressed.pdf").exists(),
    reason="needs pdftotext and raw PDFs (scripts/download_sources.py)",
)
def test_transcriptions_reverify_against_pdf() -> None:
    result = subprocess.run([sys.executable, str(ROOT / "scripts" / "verify_transcriptions.py")],
                            capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stderr
