#!/usr/bin/env bash
# Reproduce data/processed from official sources, in order:
#   1. download official files (checksums → data/provenance/downloads.json)
#   2. verify hand transcriptions against the PDF text layer (needs poppler's pdftotext)
#   3. build processed aggregates and run golden / consistency checks
# Any failing step stops the pipeline.
set -euo pipefail
cd "$(dirname "$0")/../backend"
uv run python ../scripts/download_sources.py
uv run python ../scripts/verify_transcriptions.py
uv run python ../scripts/build_indicators.py
