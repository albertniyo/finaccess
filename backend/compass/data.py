"""Load processed aggregates written by scripts/build_indicators.py."""

from __future__ import annotations

import json
import os
from functools import lru_cache
from pathlib import Path


class DataUnavailableError(RuntimeError):
    """Processed aggregates have not been built (or were not shipped with the deploy)."""


def _candidate_dirs() -> list[Path]:
    env = os.environ.get("COMPASS_DATA_DIR")
    here = Path(__file__).resolve()
    candidates = [Path(env)] if env else []
    candidates += [
        here.parents[2] / "data" / "processed",  # repo checkout: finaccess/data/processed
        here.parents[1] / "data" / "processed",  # container: /app/data/processed
    ]
    return candidates


def processed_dir() -> Path:
    for path in _candidate_dirs():
        if (path / "districts.json").exists():
            return path
    raise DataUnavailableError(
        "data/processed/districts.json not found. Run scripts/download_sources.py and "
        "scripts/build_indicators.py, or set COMPASS_DATA_DIR."
    )


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text())


@lru_cache(maxsize=1)
def load_dataset() -> dict:
    return _read_json(processed_dir() / "districts.json")


@lru_cache(maxsize=1)
def load_geojson() -> dict:
    return _read_json(processed_dir() / "districts.geojson")


@lru_cache(maxsize=1)
def load_validation() -> dict | None:
    path = processed_dir().parent / "provenance" / "validation.json"
    return _read_json(path) if path.exists() else None


@lru_cache(maxsize=1)
def load_downloads() -> list[dict]:
    path = processed_dir().parent / "provenance" / "downloads.json"
    return _read_json(path)["files"] if path.exists() else []


def district_names() -> list[str]:
    return [d["district"] for d in load_dataset()["districts"]]


def province_names() -> list[str]:
    return [p["province"] for p in load_dataset()["provinces"]]


def find_district(name: str) -> dict | None:
    key = name.strip().lower()
    for d in load_dataset()["districts"]:
        if d["district"].lower() == key:
            return d
    return None
