"""Official source citations and provenance metadata."""

from __future__ import annotations


def list_sources() -> dict:
    """Return citeable sources used (or planned) for v1 indicators.

    Numbers are not inventable: every displayed statistic must trace here.
    """
    return {
        "geo_level": "district",
        "country": "Rwanda",
        "note": (
            "Processed aggregates are pending Priority A downloads. "
            "Until then, endpoints return empty series with provenance stubs."
        ),
        "sources": [
            {
                "id": "eicv7-main-indicators",
                "title": "EICV7 Main Indicators Report 2023/24",
                "publisher": "NISR",
                "year": "2023/24",
                "role": "Poverty / living-conditions indicators",
                "url": (
                    "https://www.statistics.gov.rw/statistical-publications/"
                    "poverty-and-social-protection/eicv7-main-indicators-report-202324"
                ),
                "catalogue": "RWA-NISR-EICV7-2023-2024-v01",
            },
            {
                "id": "finscope-2024",
                "title": "FinScope Rwanda 2024",
                "publisher": "Access to Finance Rwanda / NISR catalogue",
                "year": "2024",
                "role": "Financial inclusion indicators",
                "url": "https://www.microdata.statistics.gov.rw/index.php/catalog/120",
                "catalogue": "RWA-NISR-FINSCOPE-2024-v01",
            },
        ],
        "linkage_policy": (
            "EICV7 and FinScope are not merged at household/individual level. "
            "Comparisons are only at a defensible common geographic aggregate."
        ),
    }