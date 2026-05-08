#!/usr/bin/env python3
"""
Compute key derived rates by year from the harmonized V1 derived file.

Produces resident-only (exclude foreign residents) rates for:
- low birthweight (<2500g)
- preterm (<37 weeks; based on best-available gestation measure in harmonized file)
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import pyarrow.compute as pc
import pyarrow.parquet as pq


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--in",
        dest="in_path",
        type=Path,
        default=repo_root
        / "output"
        / "harmonized"
        / "natality_v2_harmonized_derived.parquet",
        help="Input derived Parquet path",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=repo_root / "output" / "validation",
        help="Directory to write outputs",
    )
    p.add_argument(
        "--years",
        type=str,
        default="2005-2015",
        help="Comma years or range like 2005-2015",
    )
    p.add_argument(
        "--batch-rows",
        type=int,
        default=750_000,
        help="Rows per Parquet batch scan",
    )
    return p.parse_args()


def _count_true(arr) -> int:
    return int(pc.sum(pc.cast(pc.equal(arr, True), "int64")).as_py() or 0)


def _count_not_null(arr) -> int:
    return int(pc.sum(pc.cast(pc.invert(pc.is_null(arr)), "int64")).as_py() or 0)


def _parse_years(spec: str) -> list[int]:
    spec = spec.strip()
    if "-" in spec and "," not in spec:
        a, b = spec.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in spec.split(",") if x.strip()]


def main() -> None:
    args = parse_args()
    if not args.in_path.is_file():
        raise FileNotFoundError(args.in_path)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    pf = pq.ParquetFile(args.in_path)
    cols = set(pf.schema_arrow.names)
    required = {"year", "is_foreign_resident", "low_birthweight", "preterm_lt37"}
    missing = sorted(required - cols)
    if missing:
        raise RuntimeError(f"Missing required columns: {missing}")

    years = _parse_years(args.years)
    if not years:
        raise ValueError("No years specified")
    min_year = min(years)
    max_year = max(years)
    suffix = f"{min_year}_{max_year}" if min_year != max_year else f"{min_year}"
    # Accumulators
    res_births = {y: 0 for y in years}
    lbw_den = {y: 0 for y in years}
    lbw_num = {y: 0 for y in years}
    pre_den = {y: 0 for y in years}
    pre_num = {y: 0 for y in years}

    for batch in pf.iter_batches(
        batch_size=args.batch_rows,
        columns=["year", "is_foreign_resident", "low_birthweight", "preterm_lt37"],
    ):
        year = batch.column(0)
        foreign = batch.column(1)
        lbw = batch.column(2)
        pre = batch.column(3)

        # Resident mask (boolean; treat null as nonresident if ever present)
        res_mask = pc.fill_null(pc.and_(pc.is_valid(foreign), pc.invert(foreign)), False)

        present_years = pc.unique(year).to_pylist()
        for y in present_years:
            if y is None:
                continue
            y = int(y)
            if y not in res_births:
                continue
            mask = pc.fill_null(pc.and_(res_mask, pc.equal(year, y)), False)
            res_births[y] += int(pc.sum(pc.cast(mask, "int64")).as_py() or 0)

            lbw_y = pc.filter(lbw, mask)
            lbw_den[y] += _count_not_null(lbw_y)
            lbw_num[y] += _count_true(lbw_y)

            pre_y = pc.filter(pre, mask)
            pre_den[y] += _count_not_null(pre_y)
            pre_num[y] += _count_true(pre_y)

    if suffix == "2005_2015":
        out_csv = args.out_dir / "key_rates_core_2005_2015.csv"
        out_md = args.out_dir / "key_rates_core_2005_2015.md"
    else:
        out_csv = args.out_dir / f"key_rates_core_{suffix}.csv"
        out_md = args.out_dir / f"key_rates_core_{suffix}.md"

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "year",
                "resident_births",
                "lbw_den",
                "lbw_num",
                "lbw_rate_pct",
                "preterm_den",
                "preterm_num",
                "preterm_rate_pct",
            ],
        )
        w.writeheader()
        for y in years:
            lbw_rate = (lbw_num[y] / lbw_den[y] * 100.0) if lbw_den[y] else None
            pre_rate = (pre_num[y] / pre_den[y] * 100.0) if pre_den[y] else None
            w.writerow(
                {
                    "year": y,
                    "resident_births": res_births[y],
                    "lbw_den": lbw_den[y],
                    "lbw_num": lbw_num[y],
                    "lbw_rate_pct": round(lbw_rate, 6) if lbw_rate is not None else "",
                    "preterm_den": pre_den[y],
                    "preterm_num": pre_num[y],
                    "preterm_rate_pct": round(pre_rate, 6) if pre_rate is not None else "",
                }
            )

    out_md.write_text(
        "\n".join(
            [
                "# Key rates from harmonized derived core (resident-only)",
                "",
                f"Computed from `{args.in_path}` after excluding foreign residents (`restatus=4`).",
                "",
                f"Years: {min_year}–{max_year}" if min_year != max_year else f"Years: {min_year}",
                "",
                f"- CSV: `{out_csv}`",
                "",
                "## Notes",
                "",
                "- **Low birthweight** uses `birthweight_grams_clean` (treats `9999` as missing).",
                "- **Preterm** uses the harmonized `gestational_age_weeks` field, which is **best-available by year** (combined gestation for 2005–2013; obstetric estimate for 2014+).",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()

