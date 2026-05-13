#!/usr/bin/env python3
"""C8.13 F.5 timer wrapper: runs a list of (label, argv, cwd) stages and
records per-stage wall-clock to a CSV. Not an orchestrator; no skip-if-done
logic; no per-product subcommands (those are C8.7b scope).

Usage from a driver script:
    from scripts._time_pipeline import run_stages
    run_stages(stages=[(label, argv, cwd), ...], log_csv=Path("path/to/log.csv"))
"""

from __future__ import annotations

import csv
import subprocess
import sys
import time
from pathlib import Path
from datetime import datetime, timezone


def run_stages(stages: list[tuple[str, list[str], Path]], log_csv: Path) -> list[dict]:
    log_csv.parent.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    with log_csv.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=[
            "stage", "start_utc", "end_utc", "duration_seconds", "returncode", "cwd",
        ])
        w.writeheader()
        for label, argv, cwd in stages:
            start = time.monotonic()
            start_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
            print(f"\n[F.5] BEGIN {label!r} cwd={cwd}", flush=True)
            print(f"[F.5]   argv={argv}", flush=True)
            try:
                cp = subprocess.run(argv, cwd=str(cwd), check=False)
                rc = cp.returncode
            except FileNotFoundError as e:
                print(f"[F.5]   FileNotFoundError: {e}", flush=True)
                rc = 127
            end = time.monotonic()
            end_utc = datetime.now(timezone.utc).isoformat(timespec="seconds")
            dur = end - start
            row = {
                "stage": label,
                "start_utc": start_utc,
                "end_utc": end_utc,
                "duration_seconds": f"{dur:.2f}",
                "returncode": rc,
                "cwd": str(cwd),
            }
            results.append(row)
            w.writerow(row)
            f.flush()
            print(f"[F.5] END   {label!r} dur={dur:.2f}s rc={rc}", flush=True)
            if rc != 0:
                print(f"[F.5] HALT: non-zero exit code from {label!r}; aborting subsequent stages", flush=True)
                break
    return results


if __name__ == "__main__":
    sys.exit("not invoked directly; import run_stages from a driver script")
