#!/usr/bin/env python3
"""Download the official source files into data/raw/.

Writes data/provenance/downloads.json with URL, size, SHA-256 and retrieval time
for every file so processed numbers can be traced back to the exact bytes used.

Usage:
    python scripts/download_sources.py            # skip files already present
    python scripts/download_sources.py --force    # re-download everything
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROVENANCE = ROOT / "data" / "provenance"

SOURCES: list[dict[str, str]] = [
    {
        "id": "A1",
        "path": "eicv7/EICV7_Main_Indicator_Report.pdf",
        "title": "EICV7 Main Indicators Report 2023/24",
        "publisher": "NISR",
        "url": "https://statistics.gov.rw/sites/default/files/documents/2025-07/EICV7_Main%20Indicator%20Report.pdf",
    },
    {
        "id": "A2",
        "path": "eicv7/EICV7_Tables_MainIndicatorReport.xlsx",
        "title": "EICV7 Main Indicator Report — statistical tables",
        "publisher": "NISR",
        "url": "https://statistics.gov.rw/sites/default/files/documents/2025-04/EICV7_Tables_MainIndicatorReport.xlsx",
    },
    {
        "id": "A3a",
        "path": "eicv7/EICV7_Poverty_Profile.pdf",
        "title": "EICV7 Poverty Profile Report 2023/24",
        "publisher": "NISR",
        "url": "https://statistics.gov.rw/sites/default/files/documents/2025-07/EICV7_Poverty%20Profile.pdf",
    },
    {
        "id": "A3b",
        "path": "eicv7/EICV7_Tables_Rwanda_Poverty_Profile.xlsx",
        "title": "EICV7 Poverty Profile — statistical tables",
        "publisher": "NISR",
        "url": "https://statistics.gov.rw/sites/default/files/documents/2025-05/EICV7_Tables_Rwanda_Poverty_Profile.xlsx",
    },
    {
        "id": "A4",
        "path": "finscope/Rwanda-Finscope-2024-Report_compressed.pdf",
        "title": "FinScope Rwanda 2024 Report",
        "publisher": "Access to Finance Rwanda / NISR",
        "url": "https://statistics.gov.rw/sites/default/files/documents/2024-09/Rwanda-Finscope-2024-Report_compressed.pdf",
    },
    {
        "id": "C1",
        "path": "geo/geoBoundaries-RWA-ADM2.geojson",
        "title": "geoBoundaries Rwanda ADM2 (districts)",
        "publisher": "geoBoundaries (William & Mary geoLab)",
        "url": "https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/gbOpen/RWA/ADM2/geoBoundaries-RWA-ADM2.geojson",
    },
    {
        "id": "C1s",
        "path": "geo/geoBoundaries-RWA-ADM2_simplified.geojson",
        "title": "geoBoundaries Rwanda ADM2 (districts), simplified",
        "publisher": "geoBoundaries (William & Mary geoLab)",
        "url": "https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/gbOpen/RWA/ADM2/geoBoundaries-RWA-ADM2_simplified.geojson",
    },
]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def fetch(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    tmp = dest.with_suffix(dest.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "finaccess-compass/0.1"})
    with urllib.request.urlopen(request, timeout=180) as response, tmp.open("wb") as fh:
        while chunk := response.read(1 << 16):
            fh.write(chunk)
    tmp.replace(dest)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="re-download existing files")
    args = parser.parse_args()

    RAW.mkdir(parents=True, exist_ok=True)
    PROVENANCE.mkdir(parents=True, exist_ok=True)
    manifest_path = PROVENANCE / "downloads.json"
    previous = {}
    if manifest_path.exists():
        previous = {e["id"]: e for e in json.loads(manifest_path.read_text())["files"]}

    entries = []
    failures = 0
    for source in SOURCES:
        dest = RAW / source["path"]
        retrieved_at = previous.get(source["id"], {}).get("retrieved_at")
        if args.force or not dest.exists():
            print(f"[{source['id']}] downloading {source['url']}")
            try:
                fetch(source["url"], dest)
                retrieved_at = datetime.now(UTC).isoformat(timespec="seconds")
            except Exception as exc:  # noqa: BLE001 — report and continue with other files
                print(f"[{source['id']}] FAILED: {exc}", file=sys.stderr)
                failures += 1
                continue
        else:
            print(f"[{source['id']}] present: {dest.relative_to(ROOT)}")
            if retrieved_at is None:
                mtime = datetime.fromtimestamp(dest.stat().st_mtime, UTC)
                retrieved_at = mtime.isoformat(timespec="seconds")

        entries.append(
            {
                **source,
                "path": f"data/raw/{source['path']}",
                "bytes": dest.stat().st_size,
                "sha256": sha256(dest),
                "retrieved_at": retrieved_at,
            }
        )

    manifest_path.write_text(json.dumps({"files": entries}, indent=2) + "\n")
    print(f"Wrote {manifest_path.relative_to(ROOT)} ({len(entries)} files)")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
