#!/usr/bin/env python3
"""Download Priority A sources listed in data.md into data/raw/.

Stub: implement URL pulls
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"


def main() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    print(f"Target directory: {RAW}")

if __name__ == "__main__":
    main()
    