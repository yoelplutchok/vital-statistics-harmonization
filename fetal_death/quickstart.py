#!/usr/bin/env python3
"""
Quickstart: U.S. Fetal Death Harmonized Dataset (v2.4.0, 1982-2024)

Demonstrates basic loading and analysis of the harmonized fetal-death
microdata across the full 43-year in-repo envelope (V2.1 + V3a + V3b + 2023-2024).

Run from the directory containing the unpacked deposit (the directory that
holds fetal_death_derived.parquet and live_births_by_year.csv), or pass the
parquet path as argv[1].
"""

import sys

import pandas as pd

PARQUET = sys.argv[1] if len(sys.argv) > 1 else "fetal_death_derived.parquet"

# ============================================================
# 1. Load the data
# ============================================================

df = pd.read_parquet(PARQUET)
print(f"Loaded {len(df):,} records, {len(df.columns)} columns")
print(
    f"Years: {df['data_year'].min()}-{df['data_year'].max()} "
    f"({df['data_year'].nunique()} distinct years; v2.4.0 envelope 1982-2024)"
)
print()

# ============================================================
# 2. Standard analytic subset (NVSR-comparable)
# ============================================================
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
# 4. Fetal mortality rate trend (published live-birth denominators)
# ============================================================
# live_births_by_year.csv covers 1995-2002 + 2005-2022 (NVSR series).
# For 2023-2024 or 1992-1994, recompute denominators from natality (JOINT_USE_GUIDE).
LIVE_BIRTHS_PATH = "live_births_by_year.csv"
try:
    LIVE_BIRTHS = (
        pd.read_csv(LIVE_BIRTHS_PATH)
        .set_index("year")["live_births"]
        .to_dict()
    )
except FileNotFoundError:
    LIVE_BIRTHS = {}

print("Fetal mortality rate (per 1,000 live births + fetal deaths):")
for year, fd_count in counts.items():
    if year not in LIVE_BIRTHS:
        print(f"  {year}: (skipped — no entry in {LIVE_BIRTHS_PATH})")
        continue
    lb = LIVE_BIRTHS[year]
    rate = fd_count / (lb + fd_count) * 1000
    print(f"  {year}: {rate:.2f}")
print()

# ============================================================
# 5. Sex distribution among >=20 week deaths
# ============================================================
known_sex = gte20[gte20["fetal_sex"].isin(["M", "F"])]
male_pct = (known_sex["fetal_sex"] == "M").mean() * 100
print(f"Male % among known-sex fetal deaths >=20wk (1982-2024): {male_pct:.1f}%")
print()

# ============================================================
# 6. Cause-of-death analysis (2014+ only)
# ============================================================
print("Top 5 causes of fetal death (2014-2024, >=20wk resident):")
cod_subset = gte20[(gte20["data_year"] >= 2014) & (gte20["cause_group"] != "")]
top_causes = cod_subset["cause_group"].value_counts()
for cause, count in top_causes.head(5).items():
    pct = count / len(cod_subset) * 100
    print(f"  {cause}: {count:,} ({pct:.1f}%)")
print()

# ============================================================
# 7. Version A transition
# ============================================================
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

print("Done. See COMPARABILITY.md for cross-era guidance.")
