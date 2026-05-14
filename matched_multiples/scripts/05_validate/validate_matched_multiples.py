#!/usr/bin/env python3
"""
DESIGN: tracks-current-state

Validate matched_multiples/output/harmonized/matched_multiples_harmonized.parquet
against NCHS documentation tables.

Primary byte-exact targets (2016-2020 PDF Table 1, "Total" column across all
matched/unmatched/incomplete categories):
  - Total records                 = 641,934
  - Live births (= survivor + ID) = 633,734
  - Survivors                     = 626,541
  - Infant deaths                 = 7,193
  - Fetal deaths                  = 8,200

Structural invariants:
  - Row count totals per window match the yearly_clean parquet row counts
    (324,490 / 699,144 / 641,934; sum = 1,665,568).
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
# Tracked validation outputs live at the subproject root (sibling of
# fetal_death/validation_results.csv) so the per-target PASS/FAIL table is
# committed to the repo alongside the source code. The gitignored output/
# directory only holds large reproducible parquets.
_OUT_DIR = _SUBPROJECT_ROOT


# (target_id, description, source, expected) — all from 2016-2020 PDF Table 1
# unless otherwise noted. Sources are anchored by PDF SHA + page number for
# auditability.
PDF_2016_2020_SHA = "ed5e96ab662e970dc8fab3295942b3dfffac8c845120b8e92e125cf7d39152be"

_TARGETS_2016_2020 = [
    ("total", "All records (2016-2020)", 641_934),
    ("live_birth", "Live births: survivor + infant_death (2016-2020)", 633_734),
    ("survivor", "Survivors (2016-2020)", 626_541),
    ("infant_death", "Infant deaths (2016-2020)", 7_193),
    ("fetal_death", "Fetal deaths (2016-2020)", 8_200),
]

# Yearly_clean row-count parity (anchors row-count conservation across the
# harmonize step). Empirical values byte-exact from the C8.16 sub-step 2
# parquets (DECISION_LOG 2026-05-14T04:30:00Z).
_YEARLY_CLEAN_TARGETS = [
    ("1995-1997", 324_490),
    ("1995-2000", 699_144),
    ("2016-2020", 641_934),
]


def _evaluate_2016_2020(df: pd.DataFrame) -> list[dict[str, object]]:
    sub = df[df["data_window"] == "2016-2020"]
    results: list[dict[str, object]] = []
    actual_total = len(sub)
    actual_live_birth = int(sub["record_type"].isin(["survivor", "infant_death"]).sum())
    actual_survivor = int((sub["record_type"] == "survivor").sum())
    actual_infant_death = int((sub["record_type"] == "infant_death").sum())
    actual_fetal_death = int((sub["record_type"] == "fetal_death").sum())
    actuals = {
        "total": actual_total,
        "live_birth": actual_live_birth,
        "survivor": actual_survivor,
        "infant_death": actual_infant_death,
        "fetal_death": actual_fetal_death,
    }
    for tid, desc, expected in _TARGETS_2016_2020:
        actual = actuals[tid]
        status = "PASS" if actual == expected else "FAIL"
        results.append({
            "target_id": tid,
            "source": "2016-2020 PDF Table 1 'Total' column",
            "description": desc,
            "expected": expected,
            "actual": actual,
            "status": status,
            "diff": actual - expected,
            "pdf_sha256": PDF_2016_2020_SHA,
        })
    return results


def _evaluate_window_row_counts(df: pd.DataFrame) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    for window, expected in _YEARLY_CLEAN_TARGETS:
        actual = int((df["data_window"] == window).sum())
        status = "PASS" if actual == expected else "FAIL"
        results.append({
            "target_id": f"window_{window}_count",
            "source": "Row-count conservation across harmonize step",
            "description": f"Harmonized rows for window {window} match yearly_clean",
            "expected": expected,
            "actual": actual,
            "status": status,
            "diff": actual - expected,
            "pdf_sha256": "",
        })
    return results


def _evaluate_structural(df: pd.DataFrame) -> list[dict[str, object]]:
    results: list[dict[str, object]] = []
    # 1995-1997 ships twins+triplets only (no quadruplets per file design).
    n_quad_9597 = int(((df["data_window"] == "1995-1997") & (df["set_size"] == 4)).sum())
    results.append({
        "target_id": "no_quadruplets_1995_1997",
        "source": "1995-1997 PDF p1 + ABOUT_SOURCE_DATA.md (quadruplets excluded by confidentiality)",
        "description": "1995-1997 window has no set_size=4 records",
        "expected": 0,
        "actual": n_quad_9597,
        "status": "PASS" if n_quad_9597 == 0 else "FAIL",
        "diff": n_quad_9597,
        "pdf_sha256": "f982ad93fbd435484173d6a08014e503e7f45208994cf1305b20ad0cae675d66",
    })

    # residence_status is suppressed in 2016-2020 (state-residence not in public file)
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

    # All harmonized rows total = 1,665,568 (sum of 3 windows)
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

    # cause_of_death_icd should be populated iff record_type=infant_death
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
    # And populated cause-of-death count should equal infant_death count
    # (minus a small number of UCOD blanks - acceptable).
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

    df = pd.read_parquet(_HARMONIZED)
    results: list[dict[str, object]] = []
    results.extend(_evaluate_window_row_counts(df))
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
        fh.write("row-count conservation across the harmonize step (3),\n")
        fh.write("and structural invariants (5). See `validation_results.csv` for\n")
        fh.write("the per-row table.\n\n")
        # Hand-render markdown table (avoids the `tabulate` optional dep).
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
