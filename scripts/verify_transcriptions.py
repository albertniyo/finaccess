#!/usr/bin/env python3
"""Check hand transcriptions in data/manual/ against the PDF text layer.

For every transcribed row, the figure's printed labels are re-extracted with `pdftotext -layout`
and compared with the CSV. Chart labels that touch (e.g. "2" and "2" printed as "22") cannot be
split from text alone, so the comparison is on the concatenated digit string of the non-zero
values in printed order; the split itself was resolved visually and is annotated in the CSV.

Requires poppler's `pdftotext`. Writes data/provenance/transcription_check.json.

Usage:
    python scripts/verify_transcriptions.py
"""

from __future__ import annotations

import csv
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
MANUAL = ROOT / "data" / "manual"
PROVENANCE = ROOT / "data" / "provenance"

FINSCOPE_PDF = RAW / "finscope" / "Rwanda-Finscope-2024-Report_compressed.pdf"
POVERTY_PROFILE_PDF = RAW / "eicv7" / "EICV7_Poverty_Profile.pdf"
STRAND = ("banked", "other_formal", "informal_only", "excluded")

FIGURE_PAGES = {"Figure 5": 27, "Figure 6": 28, "Figure 7": 28, "Figure 8": 29, "Figure 9": 29,
                "Figure 10": 29, "Figure 11": 30, "Figure 12": 30, "Figure 13": 31}

GROUP_LABELS = {
    ("national", "All adults", "2020"): ("Figure 5", r"^\s*2020\s"),
    ("national", "All adults", "2024"): ("Figure 5", r"^\s*2024\s"),
    ("area", "Rural", "2024"): ("Figure 6", r"^\s*Rural 2024\b"),
    ("area", "Urban", "2024"): ("Figure 6", r"^\s*Urban 2024\b"),
    ("gender", "Male", "2024"): ("Figure 7", r"^\s*Male 2024\b"),
    ("gender", "Female", "2024"): ("Figure 7", r"^\s*Female 2024\b"),
    ("age", "16-17", "2024"): ("Figure 8", r"^\s*16-17 \(2024\)"),
    ("age", "18-30", "2024"): ("Figure 8", r"^\s*18-30 \(2024\)"),
    ("age", "31-60", "2024"): ("Figure 8", r"^\s*31-60 \(2024\)"),
    ("age", "61+", "2024"): ("Figure 8", r"^\s*61\+ \(2024\)"),
    ("disability", "Adults with disabilities", "2024"): ("Figure 9", r"^\s*people \(2024\)"),
    ("refugee", "Refugees", "2024"): ("Figure 10", r"^\s*Refugees\s"),
    ("livelihood", "Formal sector", "2024"): ("Figure 11", r"^\s*Formal sector\b"),
    ("livelihood", "Self employed", "2024"): ("Figure 11", r"^\s*Self employed\b"),
    ("livelihood", "Dependents", "2024"): ("Figure 11", r"^\s*Dependents\b"),
    ("livelihood", "Informal sector", "2024"): ("Figure 11", r"^\s*Informal sector\b"),
    ("livelihood", "Farming activities", "2024"): ("Figure 11", r"^\s*Farming activities\b"),
}
PROVINCE_LABELS = {"City of Kigali": "Kigali City", "Southern": "Southern", "Northern": "Northern",
                   "Eastern": "Eastern", "Western": "Western"}
PRODUCT_PATTERNS = {
    "Mobile money": r"mobile\s+money \((\d+)%\)",
    "Umurenge SACCO": r"SACCO \((\d+)%\)",
    "Insurance": r"insurance \((\d+)%\)",
    "Pension": r"pension \((\d+)%\)",
    "Bank": r"bank \((\d+)%\)",
    "MFI": r"MFI \((\d+)%\)",
    "Any financial product account in own name": r"(\d+)% or 6\.9\s+million",
}


def page_text(pdf: Path, page: int) -> str:
    return subprocess.run(
        ["pdftotext", "-layout", "-f", str(page), "-l", str(page), str(pdf), "-"],
        check=True, capture_output=True, text=True,
    ).stdout


def after_caption(text: str, caption: str) -> list[str]:
    idx = text.find(caption + ":")
    if idx < 0:
        raise SystemExit(f"Caption '{caption}' not found in text layer")
    return text[idx:].splitlines()


def printed_digits(lines: list[str], label_re: str, expected_len: int, strip_label: bool = True) -> str | None:
    """Digits printed after the label, continuing onto following lines if the label wraps."""
    for i, line in enumerate(lines):
        m = re.search(label_re, line)
        if not m:
            continue
        rest = line[m.end():] if strip_label else line
        digits = "".join(re.findall(r"\d+", rest))
        j = i + 1
        while len(digits) < expected_len and j < min(i + 3, len(lines)):
            nxt = re.sub(r"^\s*(Province|people \(\d{4}\))", "", lines[j])
            digits += "".join(re.findall(r"\d+", nxt))
            j += 1
        return digits
    return None


def expected_digits(rec: dict) -> str:
    return "".join(str(int(rec[k])) for k in STRAND if int(rec[k]) > 0)


def main() -> int:
    if shutil.which("pdftotext") is None:
        print("pdftotext (poppler) is required for this check", file=sys.stderr)
        return 2
    for pdf in (FINSCOPE_PDF, POVERTY_PROFILE_PDF):
        if not pdf.exists():
            print(f"Missing {pdf.relative_to(ROOT)} — run scripts/download_sources.py", file=sys.stderr)
            return 1

    pages = {p: page_text(FINSCOPE_PDF, p) for p in set(FIGURE_PAGES.values())}
    results = []

    def record(file: str, row: str, expected: str, printed: str | None) -> None:
        results.append({"file": file, "row": row, "expected": expected, "printed": printed,
                        "pass": printed == expected})

    with (MANUAL / "finscope2024_access_strand.csv").open(newline="") as fh:
        for rec in csv.DictReader(fh):
            exp = expected_digits(rec)
            if rec["level"] == "district":
                lines = after_caption(pages[31], "Figure 13")
                got = printed_digits(lines, rf"^\s*{re.escape(rec['name'])}\s", len(exp))
            elif rec["level"] == "province":
                lines = after_caption(pages[30], "Figure 12")
                got = printed_digits(lines, rf"^\s*{PROVINCE_LABELS[rec['name']]}\b", len(exp))
            else:
                lines = after_caption(pages[27], "Figure 5")
                got = printed_digits(lines, r"^\s*2024\s", len(exp))
            record("finscope2024_access_strand.csv", f"{rec['level']}:{rec['name']}", exp, got)

    with (MANUAL / "finscope2024_access_strand_groups.csv").open(newline="") as fh:
        for rec in csv.DictReader(fh):
            caption, label_re = GROUP_LABELS[(rec["dimension"], rec["group"], rec["year"])]
            exp = expected_digits(rec)
            lines = after_caption(pages[FIGURE_PAGES[caption]], caption)
            got = printed_digits(lines, label_re, len(exp))
            record("finscope2024_access_strand_groups.csv", f"{rec['dimension']}:{rec['group']}:{rec['year']}",
                   exp, got)

    text12 = re.sub(r"\s+", " ", page_text(FINSCOPE_PDF, 12))
    with (MANUAL / "finscope2024_products.csv").open(newline="") as fh:
        for rec in csv.DictReader(fh):
            m = re.search(PRODUCT_PATTERNS[rec["product"]], text12)
            record("finscope2024_products.csv", rec["product"], rec["percent_adults"], m.group(1) if m else None)

    annex_page = next(
        p for p in range(40, 50)
        if "Annex B: Headcount Poverty Rate" in page_text(POVERTY_PROFILE_PDF, p)
    )
    annex = page_text(POVERTY_PROFILE_PDF, annex_page).splitlines()
    with (MANUAL / "eicv7_poverty_profile_annex_b.csv").open(newline="") as fh:
        for rec in csv.DictReader(fh):
            exp = " ".join(f"{float(rec[k]):.1f}" for k in ("eicv5_2017_modelled", "eicv7_2024", "decrease_pp"))
            got = None
            for line in annex:
                m = re.match(rf"^\s*\d+\s+{re.escape(rec['district'])}\s+([\d.]+)\s+([\d.]+)\s+([\d.]+)", line)
                if m:
                    got = " ".join(f"{float(v):.1f}" for v in m.groups())
                    break
            record("eicv7_poverty_profile_annex_b.csv", rec["district"], exp, got)

    failed = [r for r in results if not r["pass"]]
    PROVENANCE.mkdir(parents=True, exist_ok=True)
    (PROVENANCE / "transcription_check.json").write_text(
        json.dumps({"method": "pdftotext -layout digit-string comparison", "passed": len(results) - len(failed),
                    "failed": len(failed), "rows": results}, indent=2) + "\n"
    )
    print(f"Transcription check: {len(results) - len(failed)} passed, {len(failed)} failed")
    for r in failed:
        print(f"  FAIL {r['file']} {r['row']}: csv {r['expected']!r} vs pdf {r['printed']!r}", file=sys.stderr)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
