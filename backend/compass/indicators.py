"""Indicator series for the Intervention Gap Explorer."""

from __future__ import annotations

from pathlib import Path

PROCESSED_DIR = Path(__file__).resolve().parents[2] / "data" / "processed"


def get_indicators(geo: str | None = None, urban_rural: str | None = None) -> dict:
    """Load processed district aggregates when available.

    Returns an empty series with provenance until ETL writes processed files.
    """
    return {
        "status": "awaiting_processed_data",
        "filters": {"geo": geo, "urbanRural": urban_rural},
        "geo_level": "district",
        "series": [],
        "provenance": {
            "kind": "observed",
            "processed_path": str(PROCESSED_DIR),
            "note": (
                "Run scripts/download_sources.py then scripts/build_indicators.py "
                "to populate data/processed/."
            ),
        },
    }