#!/usr/bin/env python3
"""C8.13 F.5 driver: time the natality + linked end-to-end pipeline.

Routes around the absent monorepo-root orchestrator (C8.7b DEFERRED) by
invoking each natality-side script in sequence with cwd set to the natality
build directory. Per-stage wall-clock is logged to
docs/PIPELINE_TIMING_BENCHMARK_natality_raw.csv.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts._time_pipeline import run_stages  # noqa: E402

NAT_ROOT = Path("/Users/yoelplutchok/Desktop/natality-harmonization")
NAT_SCRIPTS = NAT_ROOT / "scripts"

# 35-year V1 envelope + 19-year linked envelope (cf. STATUS 2026-05-13T22:30:00Z)
V1_YEARS = "1990-2024"
LINKED_YEARS = "2005-2023"


def main() -> int:
    stages: list[tuple[str, list[str], Path]] = [
        ("parse_all_v1_years",
         [sys.executable, str(NAT_SCRIPTS / "01_import/parse_all_v1_years.py"),
          "--years", V1_YEARS],
         NAT_ROOT),
        ("parse_all_linked_years",
         [sys.executable, str(NAT_SCRIPTS / "01_import/parse_all_linked_years.py"),
          "--years", LINKED_YEARS],
         NAT_ROOT),
        ("harmonize_v1_core",
         [sys.executable, str(NAT_SCRIPTS / "03_harmonize/harmonize_v1_core.py"),
          "--years", V1_YEARS],
         NAT_ROOT),
        ("harmonize_linked_v3",
         [sys.executable, str(NAT_SCRIPTS / "03_harmonize/harmonize_linked_v3.py"),
          "--years", LINKED_YEARS],
         NAT_ROOT),
        ("derive_v1_core",
         [sys.executable, str(NAT_SCRIPTS / "04_derive/derive_v1_core.py")],
         NAT_ROOT),
        ("derive_linked_v3",
         [sys.executable, str(NAT_SCRIPTS / "04_derive/derive_linked_v3.py")],
         NAT_ROOT),
    ]

    log_csv = REPO_ROOT / "docs/PIPELINE_TIMING_BENCHMARK_natality_raw.csv"
    results = run_stages(stages, log_csv)
    failed = [r for r in results if int(r["returncode"]) != 0]
    if failed:
        print(f"\n[F.5 natality] FAILED at: {[r['stage'] for r in failed]}", flush=True)
        return 1
    print(f"\n[F.5 natality] PASS: {len(results)} stages; total = "
          f"{sum(float(r['duration_seconds']) for r in results):.2f}s", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
