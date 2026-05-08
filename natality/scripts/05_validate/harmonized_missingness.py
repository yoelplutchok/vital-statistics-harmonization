#!/usr/bin/env python3
"""
Compute null rates for all harmonized variables by year and flag structural breaks.

Reads the harmonized (or derived) Parquet file and produces:
- output/validation/harmonized_missingness_by_year.csv
- output/validation/harmonized_missingness_breaks.csv  (>5 ppt year-over-year jumps)
- output/validation/harmonized_missingness_report.md
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--in",
        dest="in_path",
        type=Path,
        default=repo_root / "output" / "harmonized" / "natality_v2_harmonized_derived.parquet",
        help="Input harmonized Parquet path",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=repo_root / "output" / "validation",
        help="Directory to write outputs",
    )
    p.add_argument(
        "--break-threshold",
        type=float,
        default=5.0,
        help="Percentage-point threshold for flagging null-rate breaks (default: 5.0)",
    )
    p.add_argument(
        "--batch-rows",
        type=int,
        default=500_000,
        help="Rows per Parquet batch scan",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    if not args.in_path.is_file():
        raise FileNotFoundError(args.in_path)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    pf = pq.ParquetFile(args.in_path)
    all_cols = [f.name for f in pf.schema_arrow]

    # Accumulate per-year, per-variable counts
    # {(year, variable): [n_total, n_null]}
    counts: dict[tuple[int, str], list[int]] = {}

    for batch in pf.iter_batches(batch_size=args.batch_rows):
        year_arr = batch.column(batch.schema.get_field_index("year"))
        unique_years = pc.unique(year_arr).to_pylist()

        for y in unique_years:
            if y is None:
                continue
            mask = pc.equal(year_arr, y)
            n = int(pc.sum(pc.cast(mask, pa.int64())).as_py() or 0)

            for col_name in all_cols:
                col = batch.column(batch.schema.get_field_index(col_name))
                col_masked = pc.filter(col, mask)
                n_null = int(pc.sum(pc.cast(pc.is_null(col_masked), pa.int64())).as_py() or 0)

                key = (y, col_name)
                if key not in counts:
                    counts[key] = [0, 0]
                counts[key][0] += n
                counts[key][1] += n_null

    # Build rows sorted by variable, year
    rows = []
    for (y, var), (n_total, n_null) in sorted(counts.items(), key=lambda x: (x[0][1], x[0][0])):
        null_pct = round(n_null / n_total * 100.0, 4) if n_total else 0.0
        rows.append({
            "year": y,
            "variable": var,
            "n_total": n_total,
            "n_null": n_null,
            "null_pct": null_pct,
        })

    # Write full missingness CSV
    out_csv = args.out_dir / "harmonized_missingness_by_year.csv"
    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["year", "variable", "n_total", "n_null", "null_pct"])
        w.writeheader()
        for r in rows:
            w.writerow(r)
    print(f"Wrote {out_csv}")

    # Detect structural breaks (>threshold ppt change between adjacent years)
    # Build lookup: {variable: {year: null_pct}}
    var_year_pct: dict[str, dict[int, float]] = {}
    for r in rows:
        var_year_pct.setdefault(r["variable"], {})[r["year"]] = r["null_pct"]

    breaks = []
    for var, year_pct in sorted(var_year_pct.items()):
        years_sorted = sorted(year_pct.keys())
        for i in range(1, len(years_sorted)):
            prev_y = years_sorted[i - 1]
            curr_y = years_sorted[i]
            delta = year_pct[curr_y] - year_pct[prev_y]
            if abs(delta) > args.break_threshold:
                breaks.append({
                    "variable": var,
                    "year_from": prev_y,
                    "year_to": curr_y,
                    "null_pct_from": year_pct[prev_y],
                    "null_pct_to": year_pct[curr_y],
                    "delta_ppt": round(delta, 4),
                })

    out_breaks = args.out_dir / "harmonized_missingness_breaks.csv"
    with out_breaks.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=[
            "variable", "year_from", "year_to", "null_pct_from", "null_pct_to", "delta_ppt",
        ])
        w.writeheader()
        for r in breaks:
            w.writerow(r)
    print(f"Wrote {out_breaks}")

    # Write markdown report
    out_md = args.out_dir / "harmonized_missingness_report.md"
    lines = [
        "# Harmonized missingness report",
        "",
        f"Input: `{args.in_path}`",
        f"Break threshold: {args.break_threshold} percentage points",
        "",
    ]

    if breaks:
        lines.append(f"## Structural breaks detected ({len(breaks)} total)")
        lines.append("")
        lines.append("| Variable | Year transition | Null % (from → to) | Delta (ppt) |")
        lines.append("|----------|----------------|---------------------|-------------|")
        for b in breaks:
            lines.append(
                f"| `{b['variable']}` | {b['year_from']}→{b['year_to']} "
                f"| {b['null_pct_from']:.1f}% → {b['null_pct_to']:.1f}% "
                f"| {b['delta_ppt']:+.1f} |"
            )
        lines.append("")
    else:
        lines.append("## No structural breaks detected")
        lines.append("")

    lines.append("## Output files")
    lines.append("")
    lines.append(f"- Full missingness by year: `{out_csv}`")
    lines.append(f"- Structural breaks: `{out_breaks}`")
    lines.append("")

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {out_md}")

    if breaks:
        print(f"\nWARNING: {len(breaks)} null-rate break(s) > {args.break_threshold} ppt detected.")
        for b in breaks:
            print(f"  {b['variable']}: {b['year_from']}→{b['year_to']} "
                  f"({b['null_pct_from']:.1f}% → {b['null_pct_to']:.1f}%, "
                  f"delta={b['delta_ppt']:+.1f} ppt)")
    else:
        print("\nNo structural breaks detected.")


if __name__ == "__main__":
    main()
