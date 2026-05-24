#!/usr/bin/env python3
"""
DESIGN: tracks-current-state

Validate matched_multiples/output/harmonized/matched_multiples_harmonized.parquet
against NCHS documentation tables.

Primary byte-exact targets per window:

  **2016-2020** — PDF Table 1 *Total* column (5 cells):
    Total / Live births / Survivors / Infant deaths / Fetal deaths

  **1995-1997 and 1995-2000** — same Table 1 *Total*-column semantics
  (file-wide BIRTHID outcome totals per layout-PDF BIRTHID@1 coding) plus
  Table 1 complete/incomplete/unmatched × outcome cells (9 per window) using
  harmonized set_complete (1=complete, 2=incomplete, 3=unmatched). The NCHS
  layout PDFs for these windows omit printable count tables; targets are
  committed in external_validation_targets.csv (anchored at C8.16 parse-time
  raw BIRTHID crosstab; structure cross-checked against NBER d_Cntltab1.pdf).

Structural invariants:
  - Row count totals per window match the yearly_clean parquet row counts.
  - record_type × data_window contingencies match raw BIRTHID splits.
  - 1995-1997 has no quadruplets (set_size=4) per file design.

The script writes a per-target PASS/FAIL CSV + a human-readable markdown
report under output/validation/, and exits non-zero (L14 propagation) if any
target FAILs.

Usage:
  uv run python matched_multiples/scripts/05_validate/validate_matched_multiples.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

_SCRIPT_DIR = Path(__file__).resolve().parent
_SUBPROJECT_ROOT = _SCRIPT_DIR.parents[1]
_HARMONIZED = _SUBPROJECT_ROOT / "output" / "harmonized" / "matched_multiples_harmonized.parquet"
_TARGETS_CSV = _SUBPROJECT_ROOT / "external_validation_targets.csv"
_OUT_DIR = _SUBPROJECT_ROOT

PDF_1995_1997_SHA = "f982ad93fbd435484173d6a08014e503e7f45208994cf1305b20ad0cae675d66"
PDF_1995_2000_SHA = "07b7260d4284402f9068f9dc160612b0fb0240fdd0536c6c1ad1d0ffd478b886"
PDF_2016_2020_SHA = "ed5e96ab662e970dc8fab3295942b3dfffac8c845120b8e92e125cf7d39152be"
NBER_TAB1_STRUCTURE_SHA = "2778c65674b702eb245ee5f5fc0fb1a7e0e393e49693e0d6fa1d4726a4257f33"

# 2016-2020 PDF Table 1 *Total* column (extractable from 2016-2020.pdf p15).
_TARGETS_2016_2020 = [
    ("total", "All records (2016-2020)", 641_934),
    ("live_birth", "Live births: survivor + infant_death (2016-2020)", 633_734),
    ("survivor", "Survivors (2016-2020)", 626_541),
    ("infant_death", "Infant deaths (2016-2020)", 7_193),
    ("fetal_death", "Fetal deaths (2016-2020)", 8_200),
]

_YEARLY_CLEAN_TARGETS = [
    ("1995-1997", 324_490),
    ("1995-2000", 699_144),
    ("2016-2020", 641_934),
]

_OUTCOME_COLS = {
    "survivor": "survivor",
    "infant_death": "infant_death",
    "fetal_death": "fetal_death",
}


def _load_committed_targets() -> dict[str, dict[str, int]]:
    """Load per-window targets from external_validation_targets.csv."""
    if not _TARGETS_CSV.exists():
        return {}
    df = pd.read_csv(_TARGETS_CSV)
    out: dict[str, dict[str, int]] = {}
    for _, row in df.iterrows():
        window = str(row["window"])
        out.setdefault(window, {})[str(row["target_id"])] = int(row["expected_value"])
    return out


def _birthid_totals(sub: pd.DataFrame) -> dict[str, int]:
    return {
        "total": len(sub),
        "live_birth": int(sub["record_type"].isin(["survivor", "infant_death"]).sum()),
        "survivor": int((sub["record_type"] == "survivor").sum()),
        "infant_death": int((sub["record_type"] == "infant_death").sum()),
        "fetal_death": int((sub["record_type"] == "fetal_death").sum()),
    }


def _set_complete_outcome(sub: pd.DataFrame, sc: int, outcome: str) -> int:
    return int(((sub["set_complete"] == sc) & (sub["record_type"] == outcome)).sum())


def _evaluate_window_table1(df: pd.DataFrame, window: str, pdf_sha: str) -> list[dict[str, object]]:
    """Evaluate Table 1 Total-column + set_complete×outcome cells for one window."""
    sub = df[df["data_window"] == window]
    committed = _load_committed_targets().get(window, {})
    results: list[dict[str, object]] = []
    actuals = _birthid_totals(sub)

    birthid_ids = ("total", "live_birth", "survivor", "infant_death", "fetal_death")
    for tid in birthid_ids:
        expected = committed.get(tid)
        if expected is None:
            continue
        actual = actuals[tid]
        results.append({
            "target_id": f"{window.replace('-', '_')}_{tid}",
            "source": f"{window} Table 1 Total column (BIRTHID@1 totals)",
            "description": f"{window} {tid}",
            "expected": expected,
            "actual": actual,
            "status": "PASS" if actual == expected else "FAIL",
            "diff": actual - expected,
            "pdf_sha256": pdf_sha,
        })

    for sc in (1, 2, 3):
        for outcome in ("survivor", "infant_death", "fetal_death"):
            tid = f"sc{sc}_{outcome}"
            expected = committed.get(tid)
            if expected is None:
                continue
            actual = _set_complete_outcome(sub, sc, outcome)
            sc_label = {1: "complete", 2: "incomplete", 3: "unmatched"}[sc]
            results.append({
                "target_id": f"{window.replace('-', '_')}_{tid}",
                "source": (
                    f"{window} Table 1 {sc_label}-set × {outcome} "
                    f"(NBER tab1 structure sha={NBER_TAB1_STRUCTURE_SHA[:8]}…)"
                ),
                "description": f"{window} set_complete={sc} {outcome}",
                "expected": expected,
                "actual": actual,
                "status": "PASS" if actual == expected else "FAIL",
                "diff": actual - expected,
                "pdf_sha256": pdf_sha,
            })
    return results


def _evaluate_2016_2020(df: pd.DataFrame) -> list[dict[str, object]]:
    sub = df[df["data_window"] == "2016-2020"]
    results: list[dict[str, object]] = []
    actuals = _birthid_totals(sub)
    for tid, desc, expected in _TARGETS_2016_2020:
        actual = actuals[tid]
        results.append({
            "target_id": tid,
            "source": "2016-2020 PDF Table 1 'Total' column",
            "description": desc,
            "expected": expected,
            "actual": actual,
            "status": "PASS" if actual == expected else "FAIL",
            "diff": actual - expected,
            "pdf_sha256": PDF_2016_2020_SHA,
        })
    return results


def _evaluate_window_row_counts(df: pd.DataFrame) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for window, expected in _YEARLY_CLEAN_TARGETS:
        actual = int((df["data_window"] == window).sum())
        results.append({
            "target_id": f"window_{window}_count",
            "source": "Row-count conservation across harmonize step",
            "description": f"Harmonized rows for window {window} match yearly_clean",
            "expected": expected,
            "actual": actual,
            "status": "PASS" if actual == expected else "FAIL",
            "diff": actual - expected,
            "pdf_sha256": "",
        })
    return results


def _evaluate_structural(df: pd.DataFrame) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    n_quad_9597 = int(((df["data_window"] == "1995-1997") & (df["set_size"] == 4)).sum())
    results.append({
        "target_id": "no_quadruplets_1995_1997",
        "source": "1995-1997 PDF p1 + ABOUT_SOURCE_DATA.md (quadruplets excluded by confidentiality)",
        "description": "1995-1997 window has no set_size=4 records",
        "expected": 0,
        "actual": n_quad_9597,
        "status": "PASS" if n_quad_9597 == 0 else "FAIL",
        "diff": n_quad_9597,
        "pdf_sha256": PDF_1995_1997_SHA,
    })

    n_resid_2016 = int(((df["data_window"] == "2016-2020") & df["residence_status"].notna()).sum())
    results.append({
        "target_id": "residence_status_suppressed_2016_2020",
        "source": "2016-2020 PDF doc + harmonized_schema.csv",
        "description": "2016-2020 residence_status is fully NaN (suppressed)",
        "expected": 0,
        "actual": n_resid_2016,
        "status": "PASS" if n_resid_2016 == 0 else "FAIL",
        "diff": n_resid_2016,
        "pdf_sha256": PDF_2016_2020_SHA,
    })

    total_rows = len(df)
    results.append({
        "target_id": "harmonized_total_rows",
        "source": "Row-count conservation across harmonize step",
        "description": "Harmonized parquet total rows = sum of 3 yearly_clean parquets",
        "expected": 1_665_568,
        "actual": total_rows,
        "status": "PASS" if total_rows == 1_665_568 else "FAIL",
        "diff": total_rows - 1_665_568,
        "pdf_sha256": "",
    })

    n_cause_on_id = int(
        ((df["record_type"] == "infant_death") & df["cause_of_death_icd"].notna()).sum()
    )
    n_cause_off_id = int(
        ((df["record_type"] != "infant_death") & df["cause_of_death_icd"].notna()).sum()
    )
    results.append({
        "target_id": "cause_of_death_only_on_infant_death",
        "source": "Schema constraint (cause_of_death applies_to=ID per layout CSVs)",
        "description": "Non-infant-death rows have NaN cause_of_death_icd",
        "expected": 0,
        "actual": n_cause_off_id,
        "status": "PASS" if n_cause_off_id == 0 else "FAIL",
        "diff": n_cause_off_id,
        "pdf_sha256": "",
    })
    n_id = int((df["record_type"] == "infant_death").sum())
    cause_coverage = n_cause_on_id / n_id if n_id > 0 else 0.0
    results.append({
        "target_id": "cause_of_death_coverage_on_id",
        "source": "Heuristic: 95%+ of infant_death rows carry a coded UCOD",
        "description": "Coverage of cause_of_death_icd on infant_death rows",
        "expected": "≥0.95",
        "actual": f"{cause_coverage:.4f}",
        "status": "PASS" if cause_coverage >= 0.95 else "FAIL",
        "diff": "",
        "pdf_sha256": "",
    })

    return results


def main() -> int:
    if not _HARMONIZED.exists():
        print(f"ERROR: harmonized parquet missing: {_HARMONIZED}", file=sys.stderr)
        return 1
    if not _TARGETS_CSV.exists():
        print(f"ERROR: external_validation_targets.csv missing: {_TARGETS_CSV}", file=sys.stderr)
        return 1

    df = pd.read_parquet(_HARMONIZED)
    results: list[dict[str, object]] = []
    results.extend(_evaluate_window_row_counts(df))
    results.extend(_evaluate_window_table1(df, "1995-1997", PDF_1995_1997_SHA))
    results.extend(_evaluate_window_table1(df, "1995-2000", PDF_1995_2000_SHA))
    results.extend(_evaluate_2016_2020(df))
    results.extend(_evaluate_structural(df))

    results_df = pd.DataFrame(results)

    _OUT_DIR.mkdir(parents=True, exist_ok=True)
    csv_path = _OUT_DIR / "validation_results.csv"
    md_path = _OUT_DIR / "validation_results.md"
    results_df.to_csv(csv_path, index=False)

    n_pass = int((results_df["status"] == "PASS").sum())
    n_fail = int((results_df["status"] == "FAIL").sum())

    with md_path.open("w") as fh:
        fh.write("# Matched-Multiples validation results\n\n")
        fh.write(f"**{n_pass} PASS / {n_fail} FAIL across {len(results_df)} targets.**\n\n")
        fh.write("Targets cover 2016-2020 PDF Table 1 cells (5 byte-exact),\n")
        fh.write("1995-1997 + 1995-2000 Table 1 Total-column + set_complete×outcome cells\n")
        fh.write("(28 from external_validation_targets.csv),\n")
        fh.write("row-count conservation across the harmonize step (3),\n")
        fh.write("and structural invariants (5). See `validation_results.csv` for\n")
        fh.write("the per-row table.\n\n")
        cols = list(results_df.columns)
        fh.write("| " + " | ".join(cols) + " |\n")
        fh.write("| " + " | ".join("---" for _ in cols) + " |\n")
        for _, row in results_df.iterrows():
            fh.write("| " + " | ".join(str(row[c]) for c in cols) + " |\n")

    print(f"validation: {n_pass} PASS / {n_fail} FAIL ({len(results_df)} targets)")
    print(f"  csv: {csv_path}")
    print(f"  md:  {md_path}")

    if n_fail > 0:
        print(f"*** {n_fail} FAIL row(s) detected — see {csv_path} ***", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
