"""Golden tests: processed data reproduces figures published by NISR / AFR."""

import pytest

from compass import data, typology, uncertainty


@pytest.fixture(scope="module")
def dataset() -> dict:
    return data.load_dataset()


def _district(dataset: dict, name: str) -> dict:
    return next(d for d in dataset["districts"] if d["district"] == name)


def test_thirty_districts_five_provinces(dataset: dict) -> None:
    assert len(dataset["districts"]) == 30
    assert len({d["district"] for d in dataset["districts"]}) == 30
    assert [p["province"] for p in dataset["provinces"]] == [
        "City of Kigali", "Southern", "Western", "Northern", "Eastern",
    ]


@pytest.mark.parametrize(
    ("name", "expected"),
    [("Nyamagabe", 51.4), ("Gisagara", 45.6), ("Rusizi", 44.2), ("Nyarugenge", 6.8), ("Gasabo", 11.1)],
)
def test_district_poverty_golden(dataset: dict, name: str, expected: float) -> None:
    assert _district(dataset, name)["poverty_rate"]["value"] == pytest.approx(expected, abs=0.06)


def test_national_golden(dataset: dict) -> None:
    nat = dataset["national"]
    assert nat["poverty_rate"]["value"] == pytest.approx(27.4, abs=0.06)
    assert nat["extreme_poverty_rate"]["value"] == pytest.approx(5.4, abs=0.06)
    assert nat["finscope"]["excluded"] == 4
    assert nat["finscope"]["formally_served"] == 92


def test_finscope_district_claims(dataset: dict) -> None:
    above = [d["district"] for d in dataset["districts"] if d["finscope"]["excluded"] > 4]
    assert len(above) == 12
    assert {"Nyaruguru", "Ngoma", "Rulindo", "Nyabihu", "Gakenke"} <= set(above)
    assert max(dataset["districts"], key=lambda d: d["finscope"]["informal_only"])["district"] == "Gicumbi"


def test_access_strands_sum_to_about_100(dataset: dict) -> None:
    for d in dataset["districts"]:
        assert 98 <= d["finscope"]["strand_sum"] <= 101, d["district"]


def test_poverty_ci_contains_estimate(dataset: dict) -> None:
    for d in dataset["districts"]:
        p = d["poverty_rate"]
        assert p["ci_low"] < p["value"] < p["ci_high"]


def test_validation_file_all_pass() -> None:
    validation = data.load_validation()
    assert validation is not None
    assert validation["failed"] == 0


def test_finscope_se_reasonable() -> None:
    assert 1.0 < uncertainty.finscope_se(4) < 1.5
    assert uncertainty.finscope_se(10) > uncertainty.finscope_se(1)
    low, high = uncertainty.finscope_ci(1)
    assert low == 0.0 and high > 1


def test_typology(dataset: dict) -> None:
    nat = dataset["national"]
    assert typology.classify(_district(dataset, "Nyaruguru"), nat)["type"] == "compound_gap"
    assert typology.classify(_district(dataset, "Nyamagabe"), nat)["type"] == "poverty_led"
    assert typology.classify(_district(dataset, "Rulindo"), nat)["type"] == "access_gap"
    assert typology.classify(_district(dataset, "Kicukiro"), nat)["type"] == "lower_relative_need"
    flags = {f["id"] for f in typology.classify(_district(dataset, "Gicumbi"), nat)["flags"]}
    assert "informal_reliance" in flags
