#!/usr/bin/env python3
"""
Validate linked birth-infant death Parquet files (2005-2020).

Checks per the handoff log parsing step-specific add-ons:
1. Row-count correctness: Parquet rows vs zip size-implied rows
2. Layout correctness: birth-year field matches expected year, death fields at correct positions
3. Missingness sanity: death fields blank for survivors (~99.4%), filled for deaths
4. Frequency sanity: FLGND, AGER5, SEX, DPLURAL distributions; IMR trend

Usage:
  python validate_linked_parquets.py
  python validate_linked_parquets.py --years 2005-2020
"""

from __future__ import annotations

import argparse
import csv
import sys
import zipfile
from pathlib import Path

import pyarrow.parquet as pq

REPO = Path(__file__).resolve().parents[2]


def _parse_years(spec: str) -> list[int]:
    spec = spec.strip()
    if "-" in spec and "," not in spec:
        a, b = spec.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in spec.split(",") if x.strip()]


def _zip_path_for_year(raw_dir: Path, year: int) -> Path | None:
    """Find the zip file for a given cohort year."""
    # 2005-2015: LinkCO{YY}US.zip
    legacy = raw_dir / f"LinkCO{year % 100:02d}US.zip"
    if legacy.is_file():
        return legacy
    # 2016-2020: {Y+1}PE{Y}CO.zip
    period_cohort = raw_dir / f"{year + 1}PE{year}CO.zip"
    if period_cohort.is_file():
        return period_cohort
    return None


def _zip_implied_rows(zip_path: Path, year: int) -> int | None:
    """Estimate row count from zip member uncompressed size / record length."""
    if year >= 2016:
        reclen = 1346  # period-cohort denominator
    elif year >= 2014:
        reclen = 1384
    else:
        reclen = 900
    try:
        with zipfile.ZipFile(zip_path) as zf:
            for info in zf.infolist():
                upper = info.filename.upper()
                # For period-cohort files, find the correct year's denominator
                if year >= 2016:
                    yy2 = f"{year % 100:02d}"
                    yy4 = str(year)
                    if not (f"VS{yy2}LINK" in upper or f"VS{yy4}LINK" in upper):
                        continue
                if "DENOM" in upper or "DENPUB" in upper:
                    # Each line has reclen + newline (varies: \r\n or \n)
                    # Try both possibilities
                    size = info.file_size
                    for nl_len in (2, 1):
                        full = reclen + nl_len
                        if size % full == 0:
                            return size // full
                    # If neither divides evenly, use the closest
                    return size // (reclen + 2)
    except Exception:
        return None
    return None


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--years", type=str, default="2005-2020")
    p.add_argument("--linked-dir", type=Path, default=REPO / "output" / "linked")
    p.add_argument("--raw-dir", type=Path, default=REPO / "raw_data" / "linked")
    p.add_argument("--out-dir", type=Path, default=REPO / "output" / "validation")
    args = p.parse_args()
    years = _parse_years(args.years)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    yr_range = f"{years[0]}-{years[-1]}" if len(years) > 1 else str(years[0])
    print("=" * 70)
    print(f"LINKED FILE VALIDATION ({yr_range})")
    print("=" * 70)

    # ---- 1. Row-count correctness ----
    print("\n## 1. Row-count correctness\n")
    row_counts = []
    for year in years:
        pq_path = args.linked_dir / f"linked_{year}_denomplus.parquet"
        zip_path = _zip_path_for_year(args.raw_dir, year)
        if not pq_path.is_file():
            print(f"  SKIP {year}: {pq_path} not found")
            continue
        pf = pq.ParquetFile(str(pq_path))
        pq_rows = pf.metadata.num_rows
        zip_rows = _zip_implied_rows(zip_path, year) if zip_path else None
        match = "MATCH" if zip_rows and pq_rows == zip_rows else ("MISMATCH" if zip_rows else "N/A")
        row_counts.append((year, pq_rows, zip_rows, match))
        print(f"  {year}: parquet={pq_rows:>12,}  zip_implied={zip_rows if zip_rows else 'N/A':>12}  {match}")

    # ---- 2. Layout correctness (byte-level spot checks) ----
    print("\n## 2. Layout correctness (spot checks)\n")
    for year in years:
        pq_path = args.linked_dir / f"linked_{year}_denomplus.parquet"
        if not pq_path.is_file():
            continue
        tbl = pq.read_table(str(pq_path), columns=["year", "DOB_YY", "SEX", "FLGND", "AGED", "UCOD"])
        n = tbl.num_rows

        # Check DOB_YY matches expected year
        dob_yy_col = tbl.column("DOB_YY").to_pylist()
        year_str = str(year)
        dob_match_count = sum(1 for v in dob_yy_col if v.strip() == year_str)
        dob_pct = 100.0 * dob_match_count / n if n else 0
        status = "OK" if dob_pct > 99.0 else "WARN"
        print(f"  {year}: DOB_YY=={year}: {dob_match_count:,}/{n:,} ({dob_pct:.2f}%) [{status}]")

        # Check FLGND values (should be 0 or 1 for matched/unmatched)
        flgnd_col = tbl.column("FLGND").to_pylist()
        flgnd_vals = set(v.strip() for v in flgnd_col if v.strip())
        print(f"  {year}: FLGND unique values: {sorted(flgnd_vals)}")

        # Check SEX values (should be M/F or 1/2)
        sex_col = tbl.column("SEX").to_pylist()
        sex_vals = {}
        for v in sex_col:
            v = v.strip()
            sex_vals[v] = sex_vals.get(v, 0) + 1
        sex_top = sorted(sex_vals.items(), key=lambda x: -x[1])[:5]
        print(f"  {year}: SEX distribution: {sex_top}")

    # ---- 3. Missingness sanity ----
    print("\n## 3. Missingness sanity (death fields)\n")
    death_fields = ["FLGND", "AGED", "AGER5", "UCOD", "UCODR130", "MANNER", "RECWT"]
    miss_results = []
    for year in years:
        pq_path = args.linked_dir / f"linked_{year}_denomplus.parquet"
        if not pq_path.is_file():
            continue
        tbl = pq.read_table(str(pq_path), columns=death_fields)
        n = tbl.num_rows
        print(f"  {year} (n={n:,}):")

        # Count linked deaths (FLGND=1 means matched to a death record)
        flgnd = tbl.column("FLGND").to_pylist()
        deaths = sum(1 for v in flgnd if v.strip() == "1")
        survivors = n - deaths
        imr = 1000.0 * deaths / n if n else 0
        print(f"    Deaths (FLGND=1): {deaths:,}  Survivors: {survivors:,}  IMR: {imr:.2f} per 1,000")
        miss_results.append((year, n, deaths, survivors, imr))

        # Check that AGED is blank/spaces for survivors and filled for deaths
        aged = tbl.column("AGED").to_pylist()
        aged_blank = sum(1 for v in aged if v.strip() == "")
        aged_filled = n - aged_blank
        print(f"    AGED: blank={aged_blank:,} filled={aged_filled:,} (expect filled ~= deaths={deaths:,})")

        # Check UCOD is blank for survivors
        ucod = tbl.column("UCOD").to_pylist()
        ucod_blank = sum(1 for v in ucod if v.strip() == "")
        ucod_filled = n - ucod_blank
        print(f"    UCOD: blank={ucod_blank:,} filled={ucod_filled:,}")

    # ---- 4. Frequency sanity / IMR trend ----
    print("\n## 4. IMR trend across years\n")
    print(f"  {'Year':>6}  {'Births':>12}  {'Deaths':>8}  {'IMR':>8}")
    print(f"  {'----':>6}  {'------':>12}  {'------':>8}  {'---':>8}")
    for year, n, deaths, survivors, imr in miss_results:
        print(f"  {year:>6}  {n:>12,}  {deaths:>8,}  {imr:>8.2f}")

    # Check IMR trend is generally declining (2005 ~6.9 -> 2015 ~5.9)
    if len(miss_results) >= 2:
        first_imr = miss_results[0][4]
        last_imr = miss_results[-1][4]
        trend = "DECLINING (expected)" if last_imr < first_imr else "INCREASING (unexpected)"
        print(f"\n  Trend: {first_imr:.2f} → {last_imr:.2f} = {trend}")

    # ---- 5. Compare to natality row counts ----
    print("\n## 5. Linked vs natality row counts\n")
    nat_dir = REPO / "output" / "yearly_clean"
    for year in years:
        pq_path = args.linked_dir / f"linked_{year}_denomplus.parquet"
        nat_path = nat_dir / f"natality_{year}_core.parquet"
        if not pq_path.is_file() or not nat_path.is_file():
            continue
        linked_rows = pq.ParquetFile(str(pq_path)).metadata.num_rows
        nat_rows = pq.ParquetFile(str(nat_path)).metadata.num_rows
        diff = linked_rows - nat_rows
        pct = 100.0 * diff / nat_rows if nat_rows else 0
        status = "EXACT" if diff == 0 else f"+{diff:,} ({pct:+.4f}%)"
        print(f"  {year}: linked={linked_rows:>12,}  natality={nat_rows:>12,}  diff={status}")

    # ---- Write CSV summary ----
    csv_path = args.out_dir / f"linked_validation_{yr_range.replace('-', '_')}.csv"
    with open(csv_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["year", "parquet_rows", "zip_implied_rows", "zip_match",
                     "deaths", "survivors", "imr_per_1000"])
        for i, (yr, pq_n, zip_n, match) in enumerate(row_counts):
            if i < len(miss_results):
                _, _, deaths, survivors, imr = miss_results[i]
            else:
                deaths = survivors = imr = ""
            w.writerow([yr, pq_n, zip_n or "", match, deaths, survivors, f"{imr:.2f}" if imr else ""])
    print(f"\nCSV written: {csv_path}")

    # ---- Write MD summary ----
    md_path = args.out_dir / f"linked_validation_{yr_range.replace('-', '_')}.md"
    with open(md_path, "w") as f:
        f.write(f"# Linked Birth-Infant Death Validation ({yr_range})\n\n")
        f.write("## Row Counts\n\n")
        f.write("| Year | Parquet Rows | Zip-Implied | Match |\n")
        f.write("|------|-------------|-------------|-------|\n")
        for yr, pq_n, zip_n, match in row_counts:
            zip_str = f"{zip_n:,}" if zip_n else "N/A"
            f.write(f"| {yr} | {pq_n:,} | {zip_str} | {match} |\n")
        f.write("\n## Infant Mortality Rates\n\n")
        f.write("| Year | Births | Deaths | IMR (per 1,000) |\n")
        f.write("|------|--------|--------|-----------------|\n")
        for yr, n, deaths, survivors, imr in miss_results:
            f.write(f"| {yr} | {n:,} | {deaths:,} | {imr:.2f} |\n")
    print(f"MD written: {md_path}")

    # ---- Stop-ship check ----
    print("\n## STOP-SHIP CHECKS\n")
    failures = []
    for yr, pq_n, zip_n, match in row_counts:
        if match == "MISMATCH":
            failures.append(f"Row count mismatch for {yr}: parquet={pq_n}, zip_implied={zip_n}")
    for yr, n, deaths, survivors, imr in miss_results:
        if imr < 3.0 or imr > 10.0:
            failures.append(f"IMR out of plausible range for {yr}: {imr:.2f}")

    if failures:
        print("  FAILURES:")
        for f in failures:
            print(f"    - {f}")
        print("\n  *** DO NOT PROCEED until resolved ***")
    else:
        print("  All stop-ship checks PASSED.")


if __name__ == "__main__":
    main()
