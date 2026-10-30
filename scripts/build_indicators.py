#!/usr/bin/env python3
"""Build district aggregates from data/raw → data/processed.

Stub: implement after Excel inspection and indicator freeze.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
PROVENANCE = ROOT / "data" / "provenance"


def main() -> None:
    PROCESSED.mkdir(parents=True, exist_ok=True)
    PROVENANCE.mkdir(parents=True, exist_ok=True)
    print(f"Raw: {RAW}")
    print(f"Processed: {PROCESSED}")

if __name__ == "__main__":
    main()