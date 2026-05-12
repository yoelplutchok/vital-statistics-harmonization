#!/usr/bin/env python3
"""
Quickstart: U.S. Fetal Death Harmonized Dataset (V2.0, 1992-2022)

This script demonstrates basic loading and analysis of the harmonized
fetal death dataset across the full 29-year V2.0 release.

Run from the directory containing the unpacked Zenodo deposit (the directory
that holds fetal_death_derived.parquet and live_births_by_year.csv).
"""

import pandas as pd
import numpy as np

# ============================================================
# 1. Load the data
# ============================================================

df = pd.read_parquet("fetal_death_derived.parquet")
print(f"Loaded {len(df):,} records, {len(df.columns)} columns")
print(f"Years: {df['data_year'].min()}-{df['data_year'].max()} "
      f"({df['data_year'].nunique()} distinct years; 2003 and 2004 deferred to V2.1)")
print()

# ============================================================
# 2. Standard analytic subset (NVSR-comparable)
# ============================================================
# Filter to >=20 weeks gestation, U.S. residents only.
# This subset matches NVSR 57-08 (1995-2002), NVSR 73-09 (2005-2022),
# and the 1992-1994 user guide control counts exactly.
gte20 = df[(df["tabulation_flag"] == 2) & (df["residence_status"] != 4)]
print(f">=20 week, U.S. resident subset: {len(gte20):,} records")
print()

# ============================================================
# 3. Fetal death counts by year
# ============================================================
print("Fetal deaths >=20 weeks (resident) by year:")
counts = gte20.groupby("data_year").size()
for year, count in counts.items():
    print(f"  {year}: {count:,}")
print()

# ============================================================
# 4. Fetal mortality rate trend (using published live birth counts)
# ============================================================
# 1995-2002 denominators from NVSR 57-08 Table B.
# 2005-2022 denominators from NVSR 73-09 / NCHS Vital Statistics.
# 1992-1994 live birth counts are not in the NVSR Fetal & Perinatal Mortality
# series (gap), so rates for those years are skipped here.
LIVE_BIRTHS = (
    pd.read_csv("live_births_by_year.csv")
    .set_index("year")["live_births"]
    .to_dict()
)

print("Fetal mortality rate (per 1,000 live births + fetal deaths):")
for year, fd_count in counts.items():
    if year not in LIVE_BIRTHS:
        print(f"  {year}: (skipped — NVSR live-birth denominator not available)")
        continue
    lb = LIVE_BIRTHS[year]
    rate = fd_count / (lb + fd_count) * 1000
    print(f"  {year}: {rate:.2f}")
print()

# ============================================================
# 5. Sex distribution among >=20 week deaths
# ============================================================
# fetal_sex is M/F/U across all eras after the V2 B1 normalization
# (V2 raw 1/2/9 -> M/F/U).
known_sex = gte20[gte20["fetal_sex"].isin(["M", "F"])]
male_pct = (known_sex["fetal_sex"] == "M").mean() * 100
print(f"Male % among known-sex fetal deaths >=20wk (1992-2022): {male_pct:.1f}%")
print()

# ============================================================
# 6. Cause-of-death analysis (2014+ only)
# ============================================================
# cause_group is blank for 1992-2013 (no ICD-10 in pre-2014 public-use files).
print("Top 5 causes of fetal death (2014-2022, >=20wk resident):")
cod_subset = gte20[(gte20["data_year"] >= 2014) & (gte20["cause_group"] != "")]
top_causes = cod_subset["cause_group"].value_counts()
for cause, count in top_causes.head(5).items():
    pct = count / len(cod_subset) * 100
    print(f"  {cause}: {count:,} ({pct:.1f}%)")
print()

# ============================================================
# 7. Version A transition
# ============================================================
# All V2 (1992-2002) records are version_flag='S' (synthesized).
# V1 era (2005-2022) shows the staggered 2003-revision adoption.
print("Revision adoption (% A-version by year):")
for year in sorted(df["data_year"].unique()):
    yr = df[df["data_year"] == year]
    a_pct = (yr["version_flag"] == "A").mean() * 100
    print(f"  {year}: {a_pct:.1f}%")
print()

# ============================================================
# 8. Preterm and birthweight among >=20 week deaths
# ============================================================
known_preterm = gte20[gte20["preterm"].isin(["0", "1"])]
preterm_pct = (known_preterm["preterm"] == "1").mean() * 100
print(f"Preterm (<37wk) among >=20wk deaths with known GA: {preterm_pct:.1f}%")

known_lbw = gte20[gte20["lbw"].isin(["0", "1"])]
lbw_pct = (known_lbw["lbw"] == "1").mean() * 100
print(f"Low birthweight (<2500g) among >=20wk deaths with known BW: {lbw_pct:.1f}%")
print()

# ============================================================
# 9. V2-era data quirks worth respecting
# ============================================================
# Louisiana plurality non-reporting 1992-1994: ~99% of LA resident records
# have plurality=9. The derived `singleton` correctly returns '' for these.
la_92_94 = df[(df["data_year"].between(1992, 1994))]
la_unknown_singleton = (la_92_94["singleton"] == "").sum()
print(f"V2 1992-1994 records with unknown singleton (mostly LA non-reporters): "
      f"{la_unknown_singleton:,}")

# Oklahoma 100% Hispanic-origin unknown for all V2 years; MD 1992-1998; MA 1992-1997.
# Check Hispanic-origin known rate for V2 vs V1.
# Use isin() of the known codes (0-5) so blanks aren't counted as "known".
KNOWN_HISP = {"0", "1", "2", "3", "4", "5"}
v2 = df[df["data_year"].between(1992, 2002)]
v1 = df[df["data_year"] >= 2005]
v2_hisp_known = v2["hispanic_origin"].isin(KNOWN_HISP).mean() * 100
v1_hisp_known = v1["hispanic_origin"].isin(KNOWN_HISP).mean() * 100
print(f"Hispanic-origin known rate: V2 (1992-2002) {v2_hisp_known:.1f}% vs "
      f"V1 (2005-2022) {v1_hisp_known:.1f}%")
print("  (V2 lower because OK reports 100% unknown all years, plus MD 1992-98 and MA 1992-97)")
print()

print("Done. See COMPARABILITY.md for full cross-era guidance, including "
      "the three within_era columns to avoid in cross-era groupby.")
