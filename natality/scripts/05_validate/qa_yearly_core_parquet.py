#!/usr/bin/env python3
"""
QA for yearly *core* Parquet outputs (2005–2015).

Produces:
- Missingness (blank/whitespace-only) rates per column per year
- Frequency tables for a small set of low-cardinality columns

Outputs are written to `output/validation/`.
"""

from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--yearly-parquet-dir",
        type=Path,
        default=repo_root / "output" / "yearly_clean",
        help="Directory containing natality_{year}_core.parquet",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=repo_root / "output" / "validation",
        help="Directory to write QA outputs",
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
        default=250_000,
        help="Rows per Parquet batch scan (memory/perf tradeoff)",
    )
    return p.parse_args()


def _parse_years(spec: str) -> list[int]:
    spec = spec.strip()
    if "-" in spec and "," not in spec:
        a, b = spec.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in spec.split(",") if x.strip()]


def _trim(arr: pa.Array | pa.ChunkedArray) -> pa.Array | pa.ChunkedArray:
    return pc.utf8_trim_whitespace(arr)


def _blank_count(arr: pa.Array | pa.ChunkedArray) -> int:
    trimmed = _trim(arr)
    is_blank = pc.equal(trimmed, "")
    s = pc.sum(is_blank)
    return int(s.as_py() or 0)


def _value_counts_small(arr: pa.Array | pa.ChunkedArray) -> Counter[str]:
    """
    Return counts of trimmed string values for low-cardinality columns.
    Blank values are counted as "".
    """
    trimmed = _trim(arr)
    # Replace nulls with empty string just in case (works for Array and ChunkedArray).
    trimmed = pc.fill_null(trimmed, "")
    vc = pc.value_counts(trimmed)
    out: Counter[str] = Counter()
    # vc is a StructArray with fields "values" and "counts"
    values = vc.field("values")
    counts = vc.field("counts")
    for v, c in zip(values.to_pylist(), counts.to_pylist(), strict=False):
        out[str(v)] += int(c)
    return out


def _write_missingness_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["year", "column", "n_rows", "blank_count", "blank_pct"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _write_freq_csv(path: Path, rows: list[dict[str, object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["year", "column", "value", "count", "pct"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def _write_md(path: Path, *, missingness_csv: Path, freq_csv: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "\n".join(
            [
                "# QA: yearly core Parquet",
                "",
                "## Outputs",
                "",
                f"- Missingness (blank/whitespace-only): `{missingness_csv}`",
                f"- Frequencies (selected low-cardinality columns): `{freq_csv}`",
                "",
                "## Notes",
                "",
                "- These Parquet files store **raw fixed-width substrings**. Missingness here is defined as a field being blank after whitespace trimming.",
                "- Some blanks are expected due to nonreporting areas and certificate revision differences (see NCHS user guides).",
                "",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    args = parse_args()
    years = _parse_years(args.years)
    if not years:
        raise ValueError("No years specified")
    min_year = min(years)
    max_year = max(years)
    suffix = f"{min_year}_{max_year}" if min_year != max_year else f"{min_year}"

    missingness_rows: list[dict[str, object]] = []
    freq_rows: list[dict[str, object]] = []

    # Only compute frequencies for a small set of columns that are expected to be low-cardinality.
    freq_columns = {
        "DOB_YY",
        "DOB_MM",
        "RESTATUS",
        "SEX",
        "CSEX",          # 1990–2002 sex field
        "DPLURAL",
        "GESTREC3",
        "GESTAT3",        # 1990–2002 preterm recode
        "OEGEST_R3",
        "MRACEHISP",
        "MAR",
        "DMAR",
        "RECTYPE",        # 1990–2002 US/territory indicator
        "TOBACCO",        # 1990–2002 smoking flag
        "MRACE3",         # 1990–2002 race recode
        "DELMETH5",       # 1990–2002 delivery method
    }

    for year in years:
        pq_path = args.yearly_parquet_dir / f"natality_{year}_core.parquet"
        if not pq_path.is_file():
            raise FileNotFoundError(pq_path)

        pf = pq.ParquetFile(pq_path)
        n_rows = int(pf.metadata.num_rows)
        schema = pf.schema_arrow
        col_names = [f.name for f in schema]

        # Track blanks per column across batches.
        blank_counts: dict[str, int] = {c: 0 for c in col_names if c != "year"}
        freq_acc: dict[str, Counter[str]] = {
            c: Counter() for c in col_names if c in freq_columns
        }

        for batch in pf.iter_batches(batch_size=args.batch_rows):
            for c in blank_counts.keys():
                arr = batch.column(batch.schema.get_field_index(c))
                blank_counts[c] += _blank_count(arr)

            for c in freq_acc.keys():
                arr = batch.column(batch.schema.get_field_index(c))
                freq_acc[c].update(_value_counts_small(arr))

        for c, blanks in sorted(blank_counts.items()):
            missingness_rows.append(
                {
                    "year": year,
                    "column": c,
                    "n_rows": n_rows,
                    "blank_count": blanks,
                    "blank_pct": round(blanks / n_rows * 100.0, 6) if n_rows else 0.0,
                }
            )

        for c, ctr in sorted(freq_acc.items()):
            total = sum(ctr.values())
            if total == 0:
                continue
            # Sort by descending count.
            for v, cnt in ctr.most_common():
                freq_rows.append(
                    {
                        "year": year,
                        "column": c,
                        "value": v,
                        "count": cnt,
                        "pct": round(cnt / total * 100.0, 6),
                    }
                )

    out_missing = args.out_dir / f"qa_missingness_core_{suffix}.csv"
    out_freq = args.out_dir / f"qa_frequencies_core_{suffix}.csv"
    out_md = args.out_dir / f"qa_core_{suffix}.md"

    _write_missingness_csv(out_missing, missingness_rows)
    _write_freq_csv(out_freq, freq_rows)
    _write_md(out_md, missingness_csv=out_missing, freq_csv=out_freq)

    print(f"Wrote {out_missing}")
    print(f"Wrote {out_freq}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()

