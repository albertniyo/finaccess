"""Official source citations and provenance metadata."""

from __future__ import annotations

from compass import data

SOURCES: list[dict] = [
    {
        "id": "eicv7-tables",
        "title": "EICV7 Main Indicator Report 2023/24 — statistical tables (Excel)",
        "publisher": "National Institute of Statistics of Rwanda (NISR)",
        "year": "2023/24",
        "role": (
            "District poverty with SE and CI (Table A9.23); mobile phone, smartphone, internet and "
            "health-insurance coverage (Tables A5.18, A5.19, A5.15, A3.7); extreme poverty (Table 9.2); "
            "VUP beneficiaries (Tables 10.1–10.4)"
        ),
        "geo_level": "national, urban/rural, province, district",
        "url": "https://statistics.gov.rw/sites/default/files/documents/2025-04/EICV7_Tables_MainIndicatorReport.xlsx",
        "landing_page": (
            "https://www.statistics.gov.rw/statistical-publications/"
            "poverty-and-social-protection/eicv7-main-indicators-report-202324"
        ),
        "catalogue": "RWA-NISR-EICV7-2023-2024-v01",
        "download_id": "A2",
    },
    {
        "id": "eicv7-report",
        "title": "EICV7 Main Indicators Report 2023/24",
        "publisher": "National Institute of Statistics of Rwanda (NISR)",
        "year": "2023/24",
        "role": "Headline figures used as golden checks",
        "geo_level": "national, province, district",
        "url": "https://statistics.gov.rw/sites/default/files/documents/2025-07/EICV7_Main%20Indicator%20Report.pdf",
        "catalogue": "RWA-NISR-EICV7-2023-2024-v01",
        "download_id": "A1",
    },
    {
        "id": "eicv7-poverty-profile",
        "title": "EICV7 Poverty Profile Report 2023/24",
        "publisher": "National Institute of Statistics of Rwanda (NISR)",
        "year": "2023/24",
        "role": "2017 (modelled) district poverty and the fall to 2024 (Annex B)",
        "geo_level": "district",
        "url": "https://statistics.gov.rw/sites/default/files/documents/2025-07/EICV7_Poverty%20Profile.pdf",
        "catalogue": "RWA-NISR-EICV7-2023-2024-v01",
        "download_id": "A3a",
        "transcription": "Annex B transcribed into data/manual/eicv7_poverty_profile_annex_b.csv",
    },
    {
        "id": "eicv7-poverty-profile-tables",
        "title": "EICV7 Poverty Profile 2023/24 — statistical tables (Excel)",
        "publisher": "National Institute of Statistics of Rwanda (NISR)",
        "year": "2023/24",
        "role": "2017 (modelled) poverty and change by province and nationally (Table 5.1)",
        "geo_level": "national, province",
        "url": "https://statistics.gov.rw/sites/default/files/documents/2025-05/EICV7_Tables_Rwanda_Poverty_Profile.xlsx",
        "catalogue": "RWA-NISR-EICV7-2023-2024-v01",
        "download_id": "A3b",
    },
    {
        "id": "finscope-2024",
        "title": "FinScope Rwanda 2024 Report",
        "publisher": "Access to Finance Rwanda (AFR) / NISR",
        "year": "2024",
        "role": (
            "Access strand by district (Fig. 13), province (Fig. 12), nationally and by population group "
            "(Fig. 5–11); account uptake by product (p.12)"
        ),
        "geo_level": "national, province, district",
        "url": "https://statistics.gov.rw/sites/default/files/documents/2024-09/Rwanda-Finscope-2024-Report_compressed.pdf",
        "landing_page": "https://www.microdata.statistics.gov.rw/index.php/catalog/120",
        "catalogue": "RWA-NISR-FINSCOPE-2024-v01",
        "download_id": "A4",
        "transcription": "Transcribed from figure labels into data/manual/ and checked against the PDF text layer",
    },
    {
        "id": "geoboundaries-adm2",
        "title": "geoBoundaries — Rwanda ADM2 (districts), simplified",
        "publisher": "geoBoundaries / William & Mary geoLab (CC BY 4.0)",
        "year": "current release",
        "role": "District outlines for the map",
        "geo_level": "district",
        "url": "https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/gbOpen/RWA/ADM2/geoBoundaries-RWA-ADM2_simplified.geojson",
        "download_id": "C1s",
    },
]


def list_sources() -> dict:
    """Citeable sources; every displayed statistic traces to one of these."""
    downloads = {}
    try:
        downloads = {f["id"]: f for f in data.load_downloads()}
    except data.DataUnavailableError:
        pass
    sources = []
    for s in SOURCES:
        entry = dict(s)
        dl = downloads.get(s.get("download_id", ""))
        if dl:
            entry["sha256"] = dl["sha256"]
            entry["retrieved_at"] = dl.get("retrieved_at")
        sources.append(entry)
    return {
        "geo_level": "district",
        "country": "Rwanda",
        "note": "All statistics are published NISR / AFR aggregates; no microdata were used.",
        "sources": sources,
        "linkage_policy": (
            "EICV7 and FinScope are not merged at household/individual level. "
            "Comparisons are only at a defensible common geographic aggregate (district)."
        ),
    }
