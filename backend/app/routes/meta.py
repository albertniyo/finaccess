"""Source citations, validation checks and method metadata."""

from fastapi import APIRouter

from compass import data, indicators, scoring, sources, typology, uncertainty

router = APIRouter()


@router.get("/sources")
def get_sources() -> dict:
    """Citations, years, and geographic levels for displayed statistics."""
    return sources.list_sources()


@router.get("/validation")
def get_validation() -> dict:
    """Golden, consistency and transcription checks run when the processed data was built."""
    validation = data.load_validation()
    if validation is None:
        return {"status": "missing", "checks": []}
    return {"status": "ok", **validation}


@router.get("/method")
def get_method() -> dict:
    """Indicator catalogue, scoring formula, uncertainty assumptions and typology rules."""
    return {
        "indicators": indicators.CATALOGUE,
        "measures": scoring.MEASURES,
        "formula": "score = w_p·minmax(poverty_rate) + w_e·minmax(exclusion_measure)",
        "schemes": [{"poverty_weight": w, "label": label} for w, label in scoring.SCHEMES],
        "uncertainty": uncertainty.ASSUMPTIONS,
        "simulations": scoring.SIMULATIONS,
        "typology": typology.DEFINITIONS,
        "limitations": scoring.LIMITATIONS,
        "known_discrepancies": data.load_dataset()["meta"]["known_discrepancies"],
    }
