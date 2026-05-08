#!/usr/bin/env python3
"""
External row-count validation for yearly core parses.

Compares:
- Parsed Parquet row counts in `output/yearly_clean/natality_{year}_core.parquet`
- The implied record count from the raw zip member size + (record_len + newline_len)
- NCHS published annual births (resident births) from CDC Open Data:
  https://data.cdc.gov/NCHS/NCHS-Births-and-General-Fertility-Rates-United-Sta/e6fc-ccez

Notes:
- The natality public-use microdata include births to U.S. residents and nonresidents.
  NCHS residence-based tabulations exclude births to nonresidents (see UserGuide2015.pdf).
"""

from __future__ import annotations

import argparse
import csv
import sys
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path

import pandas as pd
import pyarrow.compute as pc
import pyarrow.parquet as pq


@dataclass(frozen=True)
class YearRowCountCheck:
    year: int
    parquet_path: str
    parquet_rows: int
    foreign_resident_rows_restatus4: int | None
    resident_rows_excluding_foreign: int | None
    resident_rows_match_nchs: bool | None
    nchs_birth_number_residence: int | None
    nonresident_births_estimate: int | None
    zip_path: str
    zip_member: str
    zip_compress_type: int
    zip_member_size_bytes: int
    record_len_expected: int
    newline_len_detected: int
    expected_rows_from_size: int
    size_divides_evenly: bool
    size_rows_match_parquet: bool


def _method_name(code: int) -> str:
    mapping = {
        0: "stored",
        8: "deflate",
        9: "deflate64",
        98: "ppmd",
    }
    return mapping.get(code, f"code_{code}")


def _record_len_for_year(year: int) -> int:
    if 1990 <= year <= 2002:
        return 350
    if year == 2003:
        return 1350
    if year == 2004 or year == 2005:
        return 1500
    if 2006 <= year <= 2013:
        return 775
    if 2014 <= year <= 2024:
        return 1345
    raise ValueError(f"Unsupported year: {year}")


def _zip_first_member_info(zip_path: Path) -> tuple[str, int, int]:
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
        if not names:
            raise RuntimeError(f"No members in {zip_path}")
        member = names[0]
        info = zf.getinfo(member)
        return member, int(info.compress_type), int(info.file_size)


def _detect_newline_len(zip_path: Path, *, max_bytes: int = 8192) -> int:
    """
    Detect whether records end with \\r\\n (2) or \\n (1) by reading the first line.
    Uses the existing zip streaming helper (7z fallback when needed).
    """
    repo_root = Path(__file__).resolve().parents[2]
    import_dir = repo_root / "scripts" / "01_import"
    if str(import_dir) not in sys.path:
        sys.path.insert(0, str(import_dir))
    from zip_text_stream import iter_lines_from_zip  # type: ignore

    it = iter_lines_from_zip(zip_path)
    try:
        line = next(it)
        line = line[:max_bytes]
    finally:
        it.close()

    stripped = line.rstrip(b"\r\n")
    return max(0, len(line) - len(stripped))


def _parquet_row_count(path: Path) -> int:
    pf = pq.ParquetFile(path)
    return int(pf.metadata.num_rows)


def _count_foreign_residents_restatus4(path: Path, *, batch_rows: int = 500_000) -> int | None:
    """
    Count births to foreign residents using the RESTATUS code '4' when the column exists.
    Returns None if RESTATUS is not present in the Parquet.
    """
    pf = pq.ParquetFile(path)
    schema = pf.schema_arrow
    if "RESTATUS" not in [f.name for f in schema]:
        return None

    total = 0
    for batch in pf.iter_batches(columns=["RESTATUS"], batch_size=batch_rows):
        arr = batch.column(0)
        trimmed = pc.utf8_trim_whitespace(arr)
        is_foreign = pc.equal(trimmed, "4")
        total += int(pc.sum(is_foreign).as_py() or 0)
    return total


def _fetch_nchs_births(min_year: int, max_year: int) -> dict[int, int]:
    # Socrata API: be careful with `$` in shell; here it's just a URL string.
    url = (
        "https://data.cdc.gov/resource/e6fc-ccez.csv"
        "?$select=year,birth_number"
        f"&$where=year%20between%20%27{min_year}%27%20and%20%27{max_year}%27"
        "&$order=year"
        "&$limit=20000"
    )
    df = pd.read_csv(url, dtype={"year": "int64", "birth_number": "int64"})
    out: dict[int, int] = {}
    for r in df.itertuples(index=False):
        out[int(r.year)] = int(r.birth_number)
    return out


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--raw-dir",
        type=Path,
        default=repo_root / "raw_data",
        help="Directory containing Nat{year}us.zip",
    )
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
        help="Directory to write validation CSV/MD",
    )
    p.add_argument(
        "--years",
        type=str,
        default="2005-2015",
        help="Comma years or range like 2005-2015",
    )
    p.add_argument(
        "--skip-nchs-fetch",
        action="store_true",
        help="Skip fetching NCHS resident births; output will omit that column.",
    )
    return p.parse_args()


def _parse_years(spec: str) -> list[int]:
    spec = spec.strip()
    if "-" in spec and "," not in spec:
        a, b = spec.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in spec.split(",") if x.strip()]


def _write_csv(path: Path, rows: list[YearRowCountCheck]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = list(asdict(rows[0]).keys()) + ["zip_compress_method"]
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        for r in rows:
            d = asdict(r)
            d["zip_compress_method"] = _method_name(r.zip_compress_type)
            w.writerow(d)


def _write_md(path: Path, rows: list[YearRowCountCheck], *, title_years: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    # Build a compact markdown table.
    lines: list[str] = []
    lines.append(f"# Row-count validation ({title_years})")
    lines.append("")
    lines.append("## What this checks")
    lines.append("")
    lines.append(
        "- **Parquet rows vs raw zip size**: verifies no records were dropped during parsing."
    )
    lines.append(
        "- **Parquet rows vs NCHS published annual births (residence-based)**: highlights that"
        " the public-use microdata include births to **U.S. residents and nonresidents**, while"
        " residence tabulations exclude nonresidents."
    )
    lines.append("")
    lines.append("## Sources")
    lines.append("")
    lines.append(
        "- NCHS annual births (resident births):"
        " `https://data.cdc.gov/NCHS/NCHS-Births-and-General-Fertility-Rates-United-Sta/e6fc-ccez`"
    )
    lines.append(
        "- Nonresident inclusion note: see `raw_docs/UserGuide2015.pdf` (Introduction)."
    )
    lines.append("")
    lines.append("## Results")
    lines.append("")

    has_nchs = any(r.nchs_birth_number_residence is not None for r in rows)
    if has_nchs:
        lines.append(
            "| year | file records | foreign residents (RESTATUS=4) | resident rows | NCHS births (residence) | match? | zip method | size-implied rows match? |"
        )
        lines.append("|---:|---:|---:|---:|---:|:---:|:---|:---:|")
        for r in rows:
            nchs = (
                f"{r.nchs_birth_number_residence:,}"
                if r.nchs_birth_number_residence is not None
                else "—"
            )
            foreign = (
                f"{r.foreign_resident_rows_restatus4:,}"
                if r.foreign_resident_rows_restatus4 is not None
                else "—"
            )
            resident = (
                f"{r.resident_rows_excluding_foreign:,}"
                if r.resident_rows_excluding_foreign is not None
                else "—"
            )
            match = (
                "yes"
                if r.resident_rows_match_nchs is True
                else ("NO" if r.resident_rows_match_nchs is False else "—")
            )
            lines.append(
                f"| {r.year} | {r.parquet_rows:,} | {foreign} | {resident} | {nchs} | {match} | {_method_name(r.zip_compress_type)} | {'yes' if r.size_rows_match_parquet else 'NO'} |"
            )
    else:
        lines.append(
            "| year | parquet rows (file records) | zip method | size-implied rows match? |"
        )
        lines.append("|---:|---:|:---|:---:|")
        for r in rows:
            lines.append(
                f"| {r.year} | {r.parquet_rows:,} | {_method_name(r.zip_compress_type)} | {'yes' if r.size_rows_match_parquet else 'NO'} |"
            )

    lines.append("")
    any_bad = any(not r.size_rows_match_parquet for r in rows)
    if any_bad:
        lines.append("**WARNING:** One or more years did not match size-implied counts. Investigate.")
    else:
        lines.append("All years matched the raw zip size-implied record counts.")
    lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    years = _parse_years(args.years)
    if not years:
        raise ValueError("No years specified")
    min_year = min(years)
    max_year = max(years)
    title_years = f"{min_year}–{max_year}" if min_year != max_year else str(min_year)

    nchs: dict[int, int] | None = None
    if not args.skip_nchs_fetch:
        try:
            nchs = _fetch_nchs_births(min_year, max_year)
        except Exception as e:
            print(f"warning: failed to fetch NCHS births series: {e}", file=sys.stderr)
            nchs = None

    rows: list[YearRowCountCheck] = []
    for year in years:
        # 1990-1993 files are combined US+territory (Nat{year}.zip); 1994+ are US-only.
        if year <= 1993:
            zip_path = args.raw_dir / f"Nat{year}.zip"
        else:
            zip_path = args.raw_dir / f"Nat{year}us.zip"
        pq_path = args.yearly_parquet_dir / f"natality_{year}_core.parquet"
        if not zip_path.is_file():
            raise FileNotFoundError(zip_path)
        if not pq_path.is_file():
            raise FileNotFoundError(pq_path)

        parquet_rows = _parquet_row_count(pq_path)
        foreign_restatus4 = _count_foreign_residents_restatus4(pq_path)
        resident_rows = (
            (parquet_rows - foreign_restatus4) if foreign_restatus4 is not None else None
        )
        record_len = _record_len_for_year(year)
        newline_len = _detect_newline_len(zip_path)

        member, compress_type, member_size = _zip_first_member_info(zip_path)
        denom = record_len + newline_len
        size_divides_evenly = (denom > 0) and (member_size % denom == 0)
        expected_rows = int(member_size // denom) if size_divides_evenly else -1
        size_rows_match = size_divides_evenly and (expected_rows == parquet_rows)

        nchs_births = nchs.get(year) if nchs else None
        diff = (parquet_rows - nchs_births) if nchs_births is not None else None
        resident_match = (
            (resident_rows == nchs_births)
            if (resident_rows is not None and nchs_births is not None)
            else None
        )

        rows.append(
            YearRowCountCheck(
                year=year,
                parquet_path=str(pq_path),
                parquet_rows=parquet_rows,
                foreign_resident_rows_restatus4=foreign_restatus4,
                resident_rows_excluding_foreign=resident_rows,
                resident_rows_match_nchs=resident_match,
                nchs_birth_number_residence=nchs_births,
                nonresident_births_estimate=diff,
                zip_path=str(zip_path),
                zip_member=member,
                zip_compress_type=compress_type,
                zip_member_size_bytes=member_size,
                record_len_expected=record_len,
                newline_len_detected=newline_len,
                expected_rows_from_size=expected_rows,
                size_divides_evenly=size_divides_evenly,
                size_rows_match_parquet=size_rows_match,
            )
        )

    suffix = f"{min_year}_{max_year}" if min_year != max_year else f"{min_year}"
    out_csv = args.out_dir / f"row_count_validation_nchs_{suffix}.csv"
    out_md = args.out_dir / f"row_count_validation_nchs_{suffix}.md"
    _write_csv(out_csv, rows)
    _write_md(out_md, rows, title_years=title_years)
    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")


if __name__ == "__main__":
    main()

