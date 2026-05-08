#!/usr/bin/env python3
"""
Compare V3 linked birth-infant death metrics to externally-sourced targets.

Targets:
- metadata/external_validation_targets_v3_linked.csv

Outputs:
- output/validation/external_validation_v3_linked_comparison.csv
- output/validation/external_validation_v3_linked_comparison.md

Computes resident-only birth counts, weighted/unweighted infant death counts,
IMR, neonatal/postneonatal deaths from the V3 linked derived Parquet and
compares them to user guide values.

Uses batch streaming to avoid loading the full ~64M-row table into memory.
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass, field
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq


@dataclass(frozen=True)
class Target:
    metric_id: str
    year: int
    universe: str
    expected_value: float | None
    tolerance_abs: float | None
    value_source: str
    notes: str


SUPPORTED_METRICS: set[str] = {
    "resident_births",
    "weighted_infant_deaths",
    "unweighted_infant_deaths",
    "imr_per_1000",
    "neonatal_deaths",
    "postneonatal_deaths",
    "neonatal_imr_per_1000",
    "postneonatal_imr_per_1000",
}


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--in",
        dest="in_path",
        type=Path,
        default=repo_root / "output" / "harmonized" / "natality_v3_linked_harmonized_derived.parquet",
        help="Input V3 linked derived Parquet path",
    )
    p.add_argument(
        "--targets",
        type=Path,
        default=repo_root / "metadata" / "external_validation_targets_v3_linked.csv",
        help="CSV of external target values",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=repo_root / "output" / "validation",
        help="Directory to write outputs",
    )
    p.add_argument(
        "--batch-rows",
        type=int,
        default=750_000,
        help="Rows per Parquet batch scan",
    )
    return p.parse_args()


def _parse_float(s: str) -> float | None:
    s = (s or "").strip()
    if not s:
        return None
    return float(s)


def load_targets(path: Path) -> list[Target]:
    if not path.is_file():
        raise FileNotFoundError(path)

    targets: list[Target] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        rows = (line for line in f if not line.lstrip().startswith("#") and line.strip())
        r = csv.DictReader(rows)
        for row in r:
            metric_id = (row.get("metric_id") or "").strip()
            universe = (row.get("universe") or "").strip()
            year_s = (row.get("year") or "").strip()

            if not metric_id or not universe or not year_s:
                continue
            if metric_id not in SUPPORTED_METRICS:
                raise ValueError(f"Unsupported metric_id={metric_id!r}. Supported: {sorted(SUPPORTED_METRICS)}")

            targets.append(
                Target(
                    metric_id=metric_id,
                    year=int(year_s),
                    universe=universe,
                    expected_value=_parse_float(row.get("expected_value", "")),
                    tolerance_abs=_parse_float(row.get("tolerance_abs", "")),
                    value_source=(row.get("value_source") or "").strip(),
                    notes=(row.get("notes") or "").strip(),
                )
            )
    return targets


@dataclass
class YearAccum:
    births: int = 0
    deaths_unw: int = 0
    deaths_w: float = 0.0
    neonatal: int = 0
    postneonatal: int = 0


def main() -> None:
    args = parse_args()
    targets = load_targets(args.targets)
    if not targets:
        raise RuntimeError(f"No targets found in {args.targets}")

    if not args.in_path.is_file():
        raise FileNotFoundError(args.in_path)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    pf = pq.ParquetFile(args.in_path)
    print(f"Reading {args.in_path} ...")
    print(f"  {pf.metadata.num_rows:,} rows, {len(pf.schema_arrow.names)} columns")

    # Accumulate per-year stats in a streaming pass
    accum: dict[int, YearAccum] = {}

    for batch in pf.iter_batches(
        batch_size=args.batch_rows,
        columns=[
            "year",
            "is_foreign_resident",
            "infant_death",
            "record_weight",
            "neonatal_death",
            "postneonatal_death",
        ],
    ):
        year_arr = batch.column(0)
        foreign = batch.column(1)
        infant_death = batch.column(2)
        recwt = batch.column(3)
        neo_death = batch.column(4)
        pneo_death = batch.column(5)

        # Resident mask
        res_mask = pc.fill_null(pc.and_(pc.is_valid(foreign), pc.invert(foreign)), False)

        for yr in pc.unique(year_arr).to_pylist():
            if yr is None:
                continue
            yr = int(yr)
            if yr not in accum:
                accum[yr] = YearAccum()
            a = accum[yr]

            is_y = pc.equal(year_arr, yr)
            m_res = pc.fill_null(pc.and_(res_mask, is_y), False)

            # Births
            a.births += int(pc.sum(pc.cast(m_res, pa.int64())).as_py() or 0)

            # Deaths (unweighted)
            death_mask = pc.and_(m_res, pc.fill_null(pc.equal(infant_death, True), False))
            n_deaths = int(pc.sum(pc.cast(death_mask, pa.int64())).as_py() or 0)
            a.deaths_unw += n_deaths

            # Deaths (weighted)
            wt_filtered = pc.filter(recwt, death_mask)
            a.deaths_w += float(pc.sum(wt_filtered).as_py() or 0.0)

            # Neonatal
            neo_mask = pc.and_(m_res, pc.fill_null(pc.equal(neo_death, True), False))
            a.neonatal += int(pc.sum(pc.cast(neo_mask, pa.int64())).as_py() or 0)

            # Postneonatal
            pneo_mask = pc.and_(m_res, pc.fill_null(pc.equal(pneo_death, True), False))
            a.postneonatal += int(pc.sum(pc.cast(pneo_mask, pa.int64())).as_py() or 0)

    # Build metrics dict
    metrics: dict[tuple[str, int], float] = {}
    for yr, a in accum.items():
        metrics[("resident_births", yr)] = a.births
        metrics[("unweighted_infant_deaths", yr)] = a.deaths_unw
        metrics[("weighted_infant_deaths", yr)] = round(a.deaths_w)
        if a.births > 0:
            metrics[("imr_per_1000", yr)] = round(a.deaths_unw / a.births * 1000, 2)
        metrics[("neonatal_deaths", yr)] = a.neonatal
        metrics[("postneonatal_deaths", yr)] = a.postneonatal
        if a.births > 0:
            metrics[("neonatal_imr_per_1000", yr)] = round(a.neonatal / a.births * 1000, 2)
            metrics[("postneonatal_imr_per_1000", yr)] = round(a.postneonatal / a.births * 1000, 2)

    # Compare targets
    out_csv = args.out_dir / "external_validation_v3_linked_comparison.csv"
    out_md = args.out_dir / "external_validation_v3_linked_comparison.md"

    rows_out: list[dict[str, str]] = []
    n_pass = 0
    n_fail = 0
    n_missing = 0

    for t in targets:
        actual = metrics.get((t.metric_id, t.year))
        is_rate = t.metric_id in ("imr_per_1000", "neonatal_imr_per_1000", "postneonatal_imr_per_1000")
        actual_s = "" if actual is None else (f"{actual:.2f}" if is_rate else str(int(actual)))

        expected_s = "" if t.expected_value is None else (
            f"{t.expected_value:.2f}" if is_rate else str(int(t.expected_value))
        )
        tol_s = "" if t.tolerance_abs is None else f"{t.tolerance_abs}"

        status = "missing"
        diff_s = ""
        pass_s = ""

        if t.expected_value is None or actual is None:
            n_missing += 1
        else:
            diff = float(actual) - float(t.expected_value)
            diff_s = f"{diff:.2f}" if is_rate else str(int(round(diff)))
            tol = t.tolerance_abs if t.tolerance_abs is not None else 0.0
            ok = abs(diff) <= tol
            status = "pass" if ok else "fail"
            pass_s = "1" if ok else "0"
            if ok:
                n_pass += 1
            else:
                n_fail += 1

        rows_out.append({
            "metric_id": t.metric_id,
            "year": str(t.year),
            "universe": t.universe,
            "actual_value": actual_s,
            "expected_value": expected_s,
            "tolerance_abs": tol_s,
            "diff": diff_s,
            "status": status,
            "pass": pass_s,
            "value_source": t.value_source,
            "notes": t.notes,
        })

    # Write CSV
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "metric_id", "year", "universe", "actual_value", "expected_value",
            "tolerance_abs", "diff", "status", "pass", "value_source", "notes",
        ])
        w.writeheader()
        w.writerows(rows_out)

    # Write MD with trend table
    all_years = sorted(accum.keys())
    trend_rows: list[dict] = []
    for yr in all_years:
        a = accum[yr]
        imr_unw = round(a.deaths_unw / a.births * 1000, 2) if a.births else 0
        imr_w = round(round(a.deaths_w) / a.births * 1000, 2) if a.births else 0
        trend_rows.append({
            "year": yr,
            "births": a.births,
            "deaths_unweighted": a.deaths_unw,
            "deaths_weighted": round(a.deaths_w),
            "imr_unweighted": imr_unw,
            "imr_weighted": imr_w,
            "neonatal": a.neonatal,
            "postneonatal": a.postneonatal,
        })

    md_lines = [
        "# External validation comparison (V3 linked birth-infant death)",
        "",
        f"Computed from `{args.in_path.name}` (resident-only: `is_foreign_resident == false`).",
        "",
        f"- Targets: `{args.targets}`",
        f"- Output CSV: `{out_csv.name}`",
        "",
        "## Summary",
        "",
        f"- **Pass**: {n_pass}",
        f"- **Fail**: {n_fail}",
        f"- **Missing**: {n_missing}",
        "",
        "## Target comparison",
        "",
        "| Metric | Year | Expected | Actual | Diff | Status |",
        "|--------|------|----------|--------|------|--------|",
    ]
    for r in rows_out:
        md_lines.append(
            f"| {r['metric_id']} | {r['year']} | {r['expected_value']} | {r['actual_value']} | {r['diff']} | {r['status']} |"
        )

    md_lines += [
        "",
        "## IMR trend (all years, residents only)",
        "",
        "| Year | Births | Deaths (unw) | Deaths (w) | IMR (unw) | IMR (w) | Neonatal | Postneonatal |",
        "|------|--------|-------------|------------|-----------|---------|----------|--------------|",
    ]
    for tr in trend_rows:
        md_lines.append(
            f"| {tr['year']} | {tr['births']:,} | {tr['deaths_unweighted']:,} | {tr['deaths_weighted']:,} "
            f"| {tr['imr_unweighted']:.2f} | {tr['imr_weighted']:.2f} | {tr['neonatal']:,} | {tr['postneonatal']:,} |"
        )

    md_lines += [
        "",
        "## Notes",
        "",
        "- 2005 and 2010 user guides report **weighted** infant death counts in documentation tables.",
        "- 2015 user guide reports **unweighted** counts (explicitly labeled).",
        "- 2015 and 2020 guides: 'For cohort file use: do not apply the weight.'",
        "- Small differences (1-2 records) expected due to LATEREC (late-filed births) edge cases.",
        "",
    ]

    out_md.write_text("\n".join(md_lines) + "\n", encoding="utf-8")

    print(f"\nWrote {out_csv}")
    print(f"Wrote {out_md}")
    print(f"\nResults: {n_pass} pass, {n_fail} fail, {n_missing} missing")

    if n_fail > 0:
        print("\n*** FAILURES DETECTED — review comparison CSV ***")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
