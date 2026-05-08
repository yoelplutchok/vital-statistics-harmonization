#!/usr/bin/env python3
"""
Compute derived analysis-ready variables from harmonized fetal death data.

Reads the harmonized Parquet, adds derived indicator columns, and writes
the enriched file.

Usage:
  python derive.py --input ../../output/harmonized/fetal_death_harmonized.parquet \
                   --out ../../output/harmonized/fetal_death_derived.parquet
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd


def _to_numeric_or_nan(series: pd.Series) -> pd.Series:
    """Convert to numeric, coercing blanks and non-numeric to NaN."""
    return pd.to_numeric(series.replace("", np.nan), errors="coerce")


def add_derived(df: pd.DataFrame) -> pd.DataFrame:
    """Add all derived variables to the harmonized DataFrame."""

    # --- Parse numeric versions of key fields ---
    ga = _to_numeric_or_nan(df["gestational_age_combined"])
    ga = ga.where(ga != 99)  # 99 = unknown gestational age -> treat as NaN
    bw = _to_numeric_or_nan(df["birthweight"])
    age = _to_numeric_or_nan(df["maternal_age"])
    educ = df.get("maternal_education", pd.Series(dtype="object"))

    # ========================================
    # Gestational age indicators
    # ========================================

    # ga_gte20wks: gestational age >= 20 weeks (common inclusion criterion)
    df["ga_gte20wks"] = np.where(ga.isna(), "", np.where(ga >= 20, "1", "0"))

    # ga_gte28wks: gestational age >= 28 weeks (WHO stillbirth definition)
    df["ga_gte28wks"] = np.where(ga.isna(), "", np.where(ga >= 28, "1", "0"))

    # preterm: gestational age < 37 weeks
    df["preterm"] = np.where(ga.isna(), "", np.where(ga < 37, "1", "0"))

    # very_preterm: gestational age < 32 weeks
    df["very_preterm"] = np.where(ga.isna(), "", np.where(ga < 32, "1", "0"))

    # extremely_preterm: gestational age < 28 weeks
    df["extremely_preterm"] = np.where(ga.isna(), "", np.where(ga < 28, "1", "0"))

    # ========================================
    # Birthweight indicators
    # ========================================

    # Exclude 9999 (not stated) from BW indicators
    bw_valid = bw.where(bw != 9999)

    # bw_gte350g: birthweight >= 350 grams (common reporting threshold)
    df["bw_gte350g"] = np.where(bw_valid.isna(), "", np.where(bw_valid >= 350, "1", "0"))

    # bw_gte500g: birthweight >= 500 grams (common analytic threshold)
    df["bw_gte500g"] = np.where(bw_valid.isna(), "", np.where(bw_valid >= 500, "1", "0"))

    # bw_gte1000g: birthweight >= 1000 grams
    df["bw_gte1000g"] = np.where(bw_valid.isna(), "", np.where(bw_valid >= 1000, "1", "0"))

    # lbw: low birthweight (< 2500g)
    df["lbw"] = np.where(bw_valid.isna(), "", np.where(bw_valid < 2500, "1", "0"))

    # vlbw: very low birthweight (< 1500g)
    df["vlbw"] = np.where(bw_valid.isna(), "", np.where(bw_valid < 1500, "1", "0"))

    # ========================================
    # WHO stillbirth definition
    # ========================================
    # meets_who_stillbirth: >= 28 weeks OR >= 1000g
    # Three-valued OR logic: if either criterion is met -> "1";
    # if both are known and neither is met -> "0";
    # if one is unknown and the other is not met -> "" (unknown);
    # if both unknown -> "" (unknown).
    ga_known = ga.notna()
    bw_known = bw_valid.notna()
    who_ga = ga_known & (ga >= 28)
    who_bw = bw_known & (bw_valid >= 1000)
    either_met = who_ga | who_bw
    both_known_neither_met = (ga_known & bw_known) & ~either_met
    df["meets_who_stillbirth"] = np.where(
        either_met, "1",
        np.where(both_known_neither_met, "0", "")
    )

    # meets_20wk_threshold: >= 20 weeks by combined gestation
    df["meets_20wk_threshold"] = df["ga_gte20wks"]  # Same as ga_gte20wks

    # ========================================
    # Maternal age categories
    # ========================================
    bins = [0, 20, 25, 30, 35, 40, 999]
    labels = ["<20", "20-24", "25-29", "30-34", "35-39", "40+"]
    df["maternal_age_cat"] = pd.cut(age, bins=bins, labels=labels, right=False).astype(str)
    df.loc[age.isna(), "maternal_age_cat"] = ""

    # ========================================
    # Education categories (4-level)
    # ========================================
    # MEDUC coding: 1=8th grade or less, 2=9-12th no diploma, 3=HS grad/GED,
    #   4=Some college no degree, 5=Associate, 6=Bachelor's, 7=Master's,
    #   8=Doctorate/Professional, 9=Unknown
    educ_map = {
        "1": "< HS", "2": "< HS",
        "3": "HS grad",
        "4": "Some college", "5": "Some college",
        "6": "BA+", "7": "BA+", "8": "BA+",
    }
    if "maternal_education" in df.columns:
        df["education_cat4"] = df["maternal_education"].map(educ_map).fillna("")
    else:
        df["education_cat4"] = ""

    # ========================================
    # Singleton indicator
    # ========================================
    plur = df.get("plurality", pd.Series(dtype="object"))
    df["singleton"] = np.where(
        plur.isin(["", "9"]), "",
        np.where(plur == "1", "1", "0")
    )

    # ========================================
    # Cause-of-death broad grouping
    # ========================================
    icd = df.get("cause_icd10", pd.Series([""] * len(df), dtype="object"))

    def _cause_group(code: str) -> str:
        if not code or code.strip() == "":
            return ""
        c = code.strip().upper()
        if c.startswith("Q"):
            return "Congenital anomalies"
        if c.startswith("P95"):
            return "Unspecified cause"
        if c.startswith("P02"):
            return "Placenta/cord/membranes"
        if c.startswith("P01"):
            return "Pregnancy complications"
        if c.startswith("P00"):
            return "Maternal conditions"
        if c.startswith("P"):
            return "Other perinatal"
        return "Other"

    df["cause_group"] = icd.apply(_cause_group)

    return df


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True, help="Harmonized Parquet")
    p.add_argument("--out", type=Path, required=True, help="Output Parquet with derived vars")
    args = p.parse_args()

    df = pd.read_parquet(args.input)
    # Strip whitespace
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    df = add_derived(df)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(args.out, index=False)
    print(f"Wrote {len(df):,} records with {len(df.columns)} columns to {args.out}", file=sys.stderr)


if __name__ == "__main__":
    main()
