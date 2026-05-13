#!/usr/bin/env python3
"""C8.13 F.5 driver: time the 43-year fetal-death pipeline end-to-end.

Routes around the stale ALL_YEARS=29 in fetal_death/scripts/run_pipeline.py
(soft-flag (d); C8.7b scope) by enumerating all 43 years explicitly. Per-stage
wall-clock is logged to docs/PIPELINE_TIMING_BENCHMARK_fetal_raw.csv.

The 4 shipped parquet SHAs are gated by a separate post-run verifier; this
driver does not check SHAs itself (separation of concerns).
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts._time_pipeline import run_stages  # noqa: E402

FETAL_DEATH_ROOT = REPO_ROOT / "fetal_death"
RAW_DIR = REPO_ROOT / "raw_data/fetal_death"
YEARLY_DIR = REPO_ROOT / "output/yearly_clean"
HARMONIZED_DIR = REPO_ROOT / "output/harmonized"

# 43-year envelope post-V3a/V3b/V2.1/C8.2 (cf. STATUS 2026-05-13T22:30:00Z + file_inventory.csv)
ALL_YEARS = list(range(1982, 2025))  # 1982..2024 inclusive


def _zip_path(year: int) -> Path:
    suffix = "US_COD.zip" if year >= 2014 else "US.zip"
    return RAW_DIR / f"Fetal{year}{suffix}"


def main() -> int:
    YEARLY_DIR.mkdir(parents=True, exist_ok=True)
    HARMONIZED_DIR.mkdir(parents=True, exist_ok=True)

    stages: list[tuple[str, list[str], Path]] = []

    # Stage 1: parse each of 43 years
    for y in ALL_YEARS:
        zip_path = _zip_path(y)
        if not zip_path.exists():
            sys.exit(f"missing {zip_path} — abort F.5 fetal-death benchmark")
        out = YEARLY_DIR / f"fetal_death_{y}_raw.parquet"
        stages.append((
            f"parse_{y}",
            [sys.executable, "scripts/01_import/parse_fetal_year.py",
             "--zip", str(zip_path), "--year", str(y), "--out", str(out)],
            FETAL_DEATH_ROOT,
        ))

    # Stage 2: harmonize all 43 years
    stages.append((
        "harmonize",
        [sys.executable, "scripts/03_harmonize/harmonize.py",
         "--years", *map(str, ALL_YEARS),
         "--out", str(HARMONIZED_DIR / "fetal_death_harmonized.parquet")],
        FETAL_DEATH_ROOT,
    ))

    # Stage 3: derive
    stages.append((
        "derive",
        [sys.executable, "scripts/04_derive/derive.py",
         "--input", str(HARMONIZED_DIR / "fetal_death_harmonized.parquet"),
         "--out", str(HARMONIZED_DIR / "fetal_death_derived.parquet")],
        FETAL_DEATH_ROOT,
    ))

    log_csv = REPO_ROOT / "docs/PIPELINE_TIMING_BENCHMARK_fetal_raw.csv"
    results = run_stages(stages, log_csv)
    failed = [r for r in results if int(r["returncode"]) != 0]
    if failed:
        print(f"\n[F.5 fetal-death] FAILED at: {[r['stage'] for r in failed]}", flush=True)
        return 1
    print(f"\n[F.5 fetal-death] PASS: {len(results)} stages; total = "
          f"{sum(float(r['duration_seconds']) for r in results):.2f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
