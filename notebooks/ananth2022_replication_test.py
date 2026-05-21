"""Ananth et al. 2022 (Lancet Reg Health Am 16:100380) replication test.

NOTE: This is the v1 single-pass version. Memory-pressure killed it during
Step 4 on the natality DataFrame; superseded by
`ananth2022_replication_test_v2.py` which streams natality year-by-year
through pyarrow.compute filters and handles V2.1 (2003-2004) age via
`maternal_age_recode14`. Both share the same race-coding and aggregation
logic; v2 has the canonical results that the decision memo cites.



This script is the deciding empirical test for whether HVS Paper 2 should
proceed. It computes Black/White U.S. stillbirth rates 1982-2020 under
*two* race-coding methodologies:

  Naive       maternal_race_bridged 1982-2017 (NCHS shifted underlying
              bridged-INCL-Hispanic semantics to NH-only at 2014 without
              renaming the column); race_hispanic_revised 2018-2020
              (Ananth-proxy: column flips silently across the 2014
              methodology boundary).

  Bilateral   1982-2013 use maternal_race_bridged on BOTH FD numerator
              and natality denominator (bridged-INCL-Hispanic on both).
              2014-2020 use NH-only-collapsed race_hispanic_revised on
              FD and NH-only-collapsed maternal_race_ethnicity_5 on
              natality. Matches the HVS bilateral methodology already
              implemented for total FMR in
              notebooks/cross_race_fetal_mortality.ipynb Section 3.

Steps performed:
  1. Reproduce Ananth's 1980/2020 headline naive rates (Black 17.4 -> 10.1;
     White 9.2 -> 5.0 per 1,000) within tolerance.
  2. Fit an age-period (AP) Poisson model per race under naive coding;
     report year fixed effects 2013/2014/2015.
  3. Fit an age-period-cohort (APC) Poisson model per race under naive
     coding (Holford-style identifiability constraint).
  4. Repeat Steps 2 + 3 under bilateral race coding.
  5. Sensitivity: >=20wk, singleton-only, extend bilateral through 2024.
  6. Decide whether the bilateral correction shifts the 2014 period
     coefficient by >25% (PAPER 2 HAS BITE) or <10% (PAPER 1 STANDS ALONE).

Outputs:
  RECEIPTS/ananth2022_outputs/*.csv  -- per-step aggregated tables.
  RECEIPTS/ananth2022_outputs/period_effects_*.csv -- per-year FE.
  RECEIPTS/ananth2022_replication_test_<UTC>.md -- decision memo.
"""

from __future__ import annotations

import json
import os
import sys
import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTDIR = REPO_ROOT / "RECEIPTS" / "ananth2022_outputs"
OUTDIR.mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------------------------------
# Path resolution (same convention as notebooks/_paths.py)
# ----------------------------------------------------------------------------

FD_PARQUET = Path(
    os.environ.get(
        "HVS_FETAL_DERIVED",
        "/Users/yoelplutchok/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_derived.parquet",
    )
)
NAT_PARQUET = Path(
    os.environ.get(
        "HVS_NATAL_DERIVED",
        "/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet",
    )
)
assert FD_PARQUET.exists(), FD_PARQUET
assert NAT_PARQUET.exists(), NAT_PARQUET

# ----------------------------------------------------------------------------
# Universe / coding constants
# ----------------------------------------------------------------------------

YEAR_MIN_PRIMARY = 1982       # Ananth window starts 1980; HVS PUF starts 1982
YEAR_MAX_PRIMARY = 2020       # Ananth window ends 2020
YEAR_MAX_EXTENDED = 2024      # post-Ananth extension (sensitivity)
ANANTH_BOUNDARY = 2014        # NCHS race-coding semantics flip year

AGE_LO, AGE_HI = 11, 49       # Ananth maternal-age exclusion: <11 or >=50

# Age bands (NCHS-standard 7-band scheme used by Ananth)
AGE_BANDS = [
    ("<20",   11, 19),
    ("20-24", 20, 24),
    ("25-29", 25, 29),
    ("30-34", 30, 34),
    ("35-39", 35, 39),
    ("40-44", 40, 44),
    ("45-49", 45, 49),
]
AGE_BAND_MIDPOINTS = {
    "<20":   17.5,
    "20-24": 22.5,
    "25-29": 27.5,
    "30-34": 32.5,
    "35-39": 37.5,
    "40-44": 42.5,
    "45-49": 47.5,
}
AGE_REF = "25-29"  # reference for AP/APC models


def age_to_band(age_series: pd.Series) -> pd.Series:
    a = pd.to_numeric(age_series, errors="coerce")
    out = pd.Series(pd.NA, index=age_series.index, dtype="string")
    for label, lo, hi in AGE_BANDS:
        out[(a >= lo) & (a <= hi)] = label
    return out


def cohort_5yr(period: pd.Series, age_band: pd.Series) -> pd.Series:
    """5-year cohort label from period + age-band midpoint.

    cohort_center = period - midpoint(age_band); rounded down to 5-yr bin.
    """
    midp = age_band.map(AGE_BAND_MIDPOINTS)
    c = period - midp
    bin_lo = (np.floor(c / 5) * 5).astype(int)
    return bin_lo.astype(str) + "-" + (bin_lo + 4).astype(str)


# ----------------------------------------------------------------------------
# Filter helpers
# ----------------------------------------------------------------------------


def parse_ga(s: pd.Series) -> pd.Series:
    """gestational_age_combined parses as nullable Int16. 99 = unknown."""
    return pd.to_numeric(s, errors="coerce").astype("Int16")


def load_fd() -> pd.DataFrame:
    """Load FD with canonical filter + Ananth filters."""
    cols = [
        "data_year", "tabulation_flag", "residence_status",
        "maternal_age", "gestational_age_combined", "plurality",
        "maternal_race_bridged", "race_hispanic_revised",
    ]
    fd = pd.read_parquet(FD_PARQUET, columns=cols)
    # Canonical
    fd = fd[(fd["tabulation_flag"] == 2) & (fd["residence_status"] != 4)].copy()
    fd["ga"] = parse_ga(fd["gestational_age_combined"])
    # Drop 99 sentinel + drop rows with missing ga
    fd = fd[fd["ga"].notna() & (fd["ga"] != 99)].copy()
    # Ananth maternal-age filter
    fd = fd[(fd["maternal_age"] >= AGE_LO) & (fd["maternal_age"] <= AGE_HI)].copy()
    return fd


def load_nat() -> pd.DataFrame:
    """Load NAT with canonical filter + Ananth age filter.

    Project columns only: year, residence_status, maternal_age, plurality,
    maternal_race_bridged, maternal_race_ethnicity_5.
    """
    cols = [
        "data_year", "residence_status",
        "maternal_age", "singleton",
        "maternal_race_bridged", "maternal_race_ethnicity_5",
    ]
    nat = pd.read_parquet(NAT_PARQUET, columns=cols)
    nat = nat[nat["residence_status"] != 4].copy()
    # Restrict to the year window we use anywhere
    nat = nat[(nat["data_year"] >= YEAR_MIN_PRIMARY) & (nat["data_year"] <= YEAR_MAX_EXTENDED)].copy()
    # Ananth maternal-age filter (same on denominator)
    nat = nat[(nat["maternal_age"] >= AGE_LO) & (nat["maternal_age"] <= AGE_HI)].copy()
    return nat


# ----------------------------------------------------------------------------
# Race-coding strategies
# ----------------------------------------------------------------------------


def code_naive_fd(df: pd.DataFrame) -> pd.Series:
    """Naive Ananth proxy for FD race.

    Through 2017, use maternal_race_bridged (1=W, 2=B). For 2018-2020 (no
    bridged race in the FD PUF), fall back to race_hispanic_revised
    codes '1' (NH White) / '2' (NH Black).
    """
    race = pd.Series(pd.NA, index=df.index, dtype="string")
    pre = df["data_year"] <= 2017
    mrb = df["maternal_race_bridged"]
    race[pre & (mrb == 1)] = "White"
    race[pre & (mrb == 2)] = "Black"
    post = df["data_year"] >= 2018
    rhr = df["race_hispanic_revised"]
    race[post & (rhr == "1")] = "White"
    race[post & (rhr == "2")] = "Black"
    return race


def code_naive_nat(df: pd.DataFrame) -> pd.Series:
    """Naive Ananth proxy for natality race.

    Through 2019 (last year MRACE is populated in natality v3), use
    maternal_race_bridged. For 2020+ fall back to maternal_race_ethnicity_5
    NH_white / NH_black. Same Ananth-proxy spirit as FD side.
    """
    race = pd.Series(pd.NA, index=df.index, dtype="string")
    pre = df["data_year"] <= 2019
    mrb = df["maternal_race_bridged"]
    race[pre & (mrb == 1)] = "White"
    race[pre & (mrb == 2)] = "Black"
    post = df["data_year"] >= 2020
    eth5 = df["maternal_race_ethnicity_5"]
    race[post & (eth5 == "NH_white")] = "White"
    race[post & (eth5 == "NH_black")] = "Black"
    return race


def code_bilateral_fd(df: pd.DataFrame) -> pd.Series:
    """Bilateral race for FD.

    1982-2013 maternal_race_bridged (bridged-INCL-Hispanic).
    2014+      race_hispanic_revised collapsed to NH-only (Hispanic excluded).
    """
    race = pd.Series(pd.NA, index=df.index, dtype="string")
    pre = df["data_year"] <= 2013
    mrb = df["maternal_race_bridged"]
    race[pre & (mrb == 1)] = "White"
    race[pre & (mrb == 2)] = "Black"
    post = df["data_year"] >= 2014
    rhr = df["race_hispanic_revised"]
    race[post & (rhr == "1")] = "White"   # NH White
    race[post & (rhr == "2")] = "Black"   # NH Black
    return race


def code_bilateral_nat(df: pd.DataFrame) -> pd.Series:
    """Bilateral race for natality.

    1982-2013 maternal_race_bridged (bridged-INCL-Hispanic).
    2014+      maternal_race_ethnicity_5 collapsed to NH-only.
    """
    race = pd.Series(pd.NA, index=df.index, dtype="string")
    pre = df["data_year"] <= 2013
    mrb = df["maternal_race_bridged"]
    race[pre & (mrb == 1)] = "White"
    race[pre & (mrb == 2)] = "Black"
    post = df["data_year"] >= 2014
    eth5 = df["maternal_race_ethnicity_5"]
    race[post & (eth5 == "NH_white")] = "White"
    race[post & (eth5 == "NH_black")] = "Black"
    return race


# ----------------------------------------------------------------------------
# Aggregation
# ----------------------------------------------------------------------------


def aggregate_panel(fd: pd.DataFrame, nat: pd.DataFrame,
                    fd_race: pd.Series, nat_race: pd.Series,
                    ga_threshold: int = 24,
                    singletons_only: bool = False,
                    year_min: int = YEAR_MIN_PRIMARY,
                    year_max: int = YEAR_MAX_PRIMARY) -> pd.DataFrame:
    """Return year x age_band x race panel with fd_count, lb_count columns."""
    # FD subset
    fd_sub = fd.copy()
    fd_sub["race"] = fd_race
    fd_sub["age_band"] = age_to_band(fd_sub["maternal_age"])
    if singletons_only:
        # plurality coded as string: '1' singleton, '2'+ multiples, '9' unknown
        fd_sub = fd_sub[fd_sub["plurality"].astype(str) == "1"]
    fd_sub = fd_sub[
        (fd_sub["data_year"] >= year_min) & (fd_sub["data_year"] <= year_max)
        & (fd_sub["ga"] >= ga_threshold)
        & fd_sub["race"].notna()
        & fd_sub["age_band"].notna()
    ]
    fd_agg = (fd_sub.groupby(["data_year", "age_band", "race"], observed=True)
              .size().rename("fd_count").reset_index())

    # NAT subset
    nat_sub = nat.copy()
    nat_sub["race"] = nat_race
    nat_sub["age_band"] = age_to_band(nat_sub["maternal_age"])
    if singletons_only:
        nat_sub = nat_sub[nat_sub["singleton"] == True]
    nat_sub = nat_sub[
        (nat_sub["data_year"] >= year_min) & (nat_sub["data_year"] <= year_max)
        & nat_sub["race"].notna()
        & nat_sub["age_band"].notna()
    ]
    nat_agg = (nat_sub.groupby(["data_year", "age_band", "race"], observed=True)
               .size().rename("lb_count").reset_index())

    panel = pd.merge(fd_agg, nat_agg, on=["data_year", "age_band", "race"], how="outer")
    panel["fd_count"] = panel["fd_count"].fillna(0).astype(int)
    panel["lb_count"] = panel["lb_count"].fillna(0).astype(int)
    panel["denom"] = panel["lb_count"] + panel["fd_count"]
    panel["fmr_per_1000"] = 1000 * panel["fd_count"] / panel["denom"]
    panel["cohort"] = cohort_5yr(panel["data_year"], panel["age_band"])
    return panel


def annual_rates(panel: pd.DataFrame) -> pd.DataFrame:
    """Crude (age-pooled) annual FMR by race."""
    g = (panel.groupby(["data_year", "race"], observed=True)
         .agg(fd=("fd_count", "sum"), lb=("lb_count", "sum"), denom=("denom", "sum"))
         .reset_index())
    g["fmr_per_1000"] = 1000 * g["fd"] / g["denom"]
    return g


# ----------------------------------------------------------------------------
# APC models (Poisson with log offset)
# ----------------------------------------------------------------------------


def fit_ap(panel: pd.DataFrame, race_label: str, year_ref: int = 2000,
           age_ref: str = AGE_REF) -> dict:
    """Age-period Poisson model: log mu = a_age + p_year + log(denom).

    Returns dict with fitted coefficients keyed by year, age_band, and
    overall summary.
    """
    df = panel[(panel["race"] == race_label) & (panel["denom"] > 0)].copy()
    df["year_str"] = df["data_year"].astype(int).astype(str)
    df["age_str"] = df["age_band"].astype(str)
    # Build design matrix
    age_levels = [b for b, _, _ in AGE_BANDS]
    year_levels = sorted(df["data_year"].unique().tolist())
    age_dummies = pd.get_dummies(df["age_str"], prefix="age", drop_first=False)
    age_dummies = age_dummies.drop(columns=[f"age_{age_ref}"])
    year_dummies = pd.get_dummies(df["year_str"], prefix="yr", drop_first=False)
    year_dummies = year_dummies.drop(columns=[f"yr_{year_ref}"])
    X = pd.concat([pd.Series(1.0, index=df.index, name="const"), age_dummies, year_dummies], axis=1).astype(float)
    y = df["fd_count"].astype(float).values
    offset = np.log(df["denom"].astype(float).values)
    model = sm.GLM(y, X, family=sm.families.Poisson(), offset=offset)
    res = model.fit(maxiter=200)
    coef = res.params
    se = res.bse
    period_effects = {}
    for yr in year_levels:
        if yr == year_ref:
            period_effects[yr] = {"beta": 0.0, "se": 0.0, "rr": 1.0}
        else:
            key = f"yr_{yr}"
            if key in coef.index:
                period_effects[yr] = {
                    "beta": float(coef[key]),
                    "se": float(se[key]),
                    "rr": float(np.exp(coef[key])),
                }
    age_effects = {age_ref: {"beta": 0.0, "rr": 1.0}}
    for b in age_levels:
        if b == age_ref:
            continue
        key = f"age_{b}"
        if key in coef.index:
            age_effects[b] = {"beta": float(coef[key]), "rr": float(np.exp(coef[key]))}
    return {
        "race": race_label,
        "year_ref": year_ref,
        "age_ref": age_ref,
        "period_effects": period_effects,
        "age_effects": age_effects,
        "intercept": float(coef["const"]),
        "deviance": float(res.deviance),
        "df_resid": int(res.df_resid),
        "n_obs": int(len(df)),
    }


def fit_apc(panel: pd.DataFrame, race_label: str, year_ref: int = 2000,
            age_ref: str = AGE_REF, cohort_ref: str | None = None) -> dict:
    """Age-period-cohort Poisson model with Holford identifiability constraint.

    Drops three references (intercept absorbs them):
      - age_ref
      - year_ref
      - cohort_ref (auto: middle cohort)
    AND additionally constrains the first two non-reference cohort dummies
    to be equal (Holford's classic identifiability constraint that breaks
    the exact age + period - cohort linear dependence).
    """
    df = panel[(panel["race"] == race_label) & (panel["denom"] > 0)].copy()
    df["year_str"] = df["data_year"].astype(int).astype(str)
    df["age_str"] = df["age_band"].astype(str)
    df["cohort_str"] = df["cohort"].astype(str)

    age_levels = [b for b, _, _ in AGE_BANDS]
    year_levels = sorted(df["data_year"].unique().tolist())
    cohort_levels = sorted(df["cohort_str"].unique().tolist(),
                           key=lambda s: int(s.split("-")[0]))
    if cohort_ref is None:
        cohort_ref = cohort_levels[len(cohort_levels) // 2]

    age_dummies = pd.get_dummies(df["age_str"], prefix="age").drop(columns=[f"age_{age_ref}"])
    year_dummies = pd.get_dummies(df["year_str"], prefix="yr").drop(columns=[f"yr_{year_ref}"])
    cohort_dummies = pd.get_dummies(df["cohort_str"], prefix="coh").drop(columns=[f"coh_{cohort_ref}"])

    # Holford constraint: equate first two non-reference cohorts.
    non_ref_cohorts = [c for c in cohort_levels if c != cohort_ref]
    c1, c2 = non_ref_cohorts[0], non_ref_cohorts[1]
    # Sum the two columns into one merged dummy; drop one of the originals.
    merged_name = f"coh_{c1}|{c2}"
    cohort_dummies[merged_name] = cohort_dummies[f"coh_{c1}"] + cohort_dummies[f"coh_{c2}"]
    cohort_dummies = cohort_dummies.drop(columns=[f"coh_{c1}", f"coh_{c2}"])

    X = pd.concat([
        pd.Series(1.0, index=df.index, name="const"),
        age_dummies, year_dummies, cohort_dummies,
    ], axis=1).astype(float)
    y = df["fd_count"].astype(float).values
    offset = np.log(df["denom"].astype(float).values)
    model = sm.GLM(y, X, family=sm.families.Poisson(), offset=offset)
    res = model.fit(maxiter=200)
    coef = res.params
    se = res.bse
    period_effects = {}
    for yr in year_levels:
        if yr == year_ref:
            period_effects[yr] = {"beta": 0.0, "se": 0.0, "rr": 1.0}
            continue
        key = f"yr_{yr}"
        if key in coef.index:
            period_effects[yr] = {
                "beta": float(coef[key]),
                "se": float(se[key]),
                "rr": float(np.exp(coef[key])),
            }
    cohort_effects = {cohort_ref: {"beta": 0.0, "rr": 1.0}}
    for c in cohort_levels:
        if c == cohort_ref:
            continue
        if c in (c1, c2):
            key = merged_name
            if key in coef.index:
                cohort_effects[c] = {"beta": float(coef[key]),
                                     "rr": float(np.exp(coef[key])),
                                     "constraint": "merged_with_adjacent"}
            continue
        key = f"coh_{c}"
        if key in coef.index:
            cohort_effects[c] = {"beta": float(coef[key]), "rr": float(np.exp(coef[key]))}
    return {
        "race": race_label,
        "year_ref": year_ref,
        "age_ref": age_ref,
        "cohort_ref": cohort_ref,
        "holford_merged_cohorts": [c1, c2],
        "period_effects": period_effects,
        "cohort_effects": cohort_effects,
        "intercept": float(coef["const"]),
        "deviance": float(res.deviance),
        "df_resid": int(res.df_resid),
        "n_obs": int(len(df)),
    }


# ----------------------------------------------------------------------------
# Reporting helpers
# ----------------------------------------------------------------------------


def period_effects_to_df(model: dict) -> pd.DataFrame:
    rows = []
    for yr, d in sorted(model["period_effects"].items()):
        rows.append({
            "year": yr,
            "beta": d["beta"],
            "rr": d["rr"],
            "se": d.get("se", 0.0),
        })
    return pd.DataFrame(rows)


def boundary_change(model_naive: dict, model_bilateral: dict,
                    race_label: str, year_target: int = 2014) -> dict:
    """Compute |beta_bilateral - beta_naive| / |beta_naive| at year_target."""
    bn = model_naive["period_effects"].get(year_target, {"beta": np.nan})["beta"]
    bb = model_bilateral["period_effects"].get(year_target, {"beta": np.nan})["beta"]
    if abs(bn) < 1e-9:
        pct = np.inf
    else:
        pct = 100.0 * abs(bb - bn) / abs(bn)
    return {
        "race": race_label,
        "year": year_target,
        "beta_naive": bn,
        "beta_bilateral": bb,
        "diff": bb - bn,
        "rr_naive": float(np.exp(bn)),
        "rr_bilateral": float(np.exp(bb)),
        "abs_pct_change": pct,
    }


# ----------------------------------------------------------------------------
# Main pipeline
# ----------------------------------------------------------------------------


def main() -> int:
    print(f"=== ananth2022_replication_test ===  {dt.datetime.now(dt.timezone.utc).isoformat()}")
    print(f"FD parquet: {FD_PARQUET}")
    print(f"NAT parquet: {NAT_PARQUET}")
    print()
    print("Loading FD parquet (canonical filter + ga ne 99 + age 11-49)...")
    fd = load_fd()
    print(f"  FD canonical universe: {len(fd):,} rows; years {fd['data_year'].min()}-{fd['data_year'].max()}")
    print("Loading NAT parquet (canonical filter + age 11-49)...")
    nat = load_nat()
    print(f"  NAT canonical universe: {len(nat):,} rows; years {nat['data_year'].min()}-{nat['data_year'].max()}")

    results = {
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "fd_parquet": str(FD_PARQUET),
        "nat_parquet": str(NAT_PARQUET),
        "fd_rows_canonical": int(len(fd)),
        "nat_rows_canonical": int(len(nat)),
    }

    # -------------------------------------------------------------------- Step 1
    print("\n--- Step 1: naive headline rates 1982-2020 (>=24wk, all plurality, age 11-49) ---")
    fd_naive = code_naive_fd(fd)
    nat_naive = code_naive_nat(nat)
    panel_naive = aggregate_panel(
        fd, nat, fd_naive, nat_naive,
        ga_threshold=24, singletons_only=False,
        year_min=YEAR_MIN_PRIMARY, year_max=YEAR_MAX_PRIMARY,
    )
    panel_naive.to_csv(OUTDIR / "panel_naive_24wk.csv", index=False)
    rates_naive = annual_rates(panel_naive)
    rates_naive.to_csv(OUTDIR / "annual_rates_naive_24wk.csv", index=False)
    print(rates_naive.pivot(index="data_year", columns="race", values="fmr_per_1000").round(2).head(20))

    ananth_targets = {
        # (year, race) -> rate per 1,000   (Ananth's published 1980 and 2020 cells)
        (1980, "Black"): 17.4,
        (1980, "White"): 9.2,
        (2020, "Black"): 10.1,
        (2020, "White"): 5.0,
    }
    cmp_rows = []
    for yr in (1982, 1990, 2000, 2010, 2020):
        for race in ("Black", "White"):
            hvs = rates_naive[(rates_naive["data_year"] == yr) & (rates_naive["race"] == race)]
            if hvs.empty:
                continue
            hvs_rate = float(hvs["fmr_per_1000"].iloc[0])
            row = {"year": yr, "race": race, "hvs_naive_per_1000": round(hvs_rate, 2)}
            # Match against Ananth headline if it exists (only 1980 and 2020)
            if yr == 1982 and (1980, race) in ananth_targets:
                target = ananth_targets[(1980, race)]
                row.update({"ananth_year": 1980, "ananth_per_1000": target,
                            "diff": round(hvs_rate - target, 2),
                            "tolerance_pass": abs(hvs_rate - target) <= 0.5,
                            "note": "1982 HVS vs 1980 Ananth (2-yr offset; HVS PUF floor)"})
            elif (yr, race) in ananth_targets:
                target = ananth_targets[(yr, race)]
                row.update({"ananth_year": yr, "ananth_per_1000": target,
                            "diff": round(hvs_rate - target, 2),
                            "tolerance_pass": abs(hvs_rate - target) <= 0.5,
                            "note": "direct"})
            else:
                row.update({"ananth_year": None, "ananth_per_1000": None,
                            "diff": None, "tolerance_pass": None, "note": "no Ananth headline"})
            cmp_rows.append(row)
    cmp_df = pd.DataFrame(cmp_rows)
    cmp_df.to_csv(OUTDIR / "step1_reproduction_table.csv", index=False)
    print("\nStep 1 reproduction table:")
    print(cmp_df.to_string(index=False))
    results["step1"] = {
        "reproduction": cmp_df.to_dict(orient="records"),
        "ananth_targets": {f"{y}_{r}": v for (y, r), v in ananth_targets.items()},
    }

    # -------------------------------------------------------------------- Step 2: APC naive
    print("\n--- Step 2: APC under naive race coding ---")
    naive_results = {}
    for race in ("Black", "White"):
        print(f"  Race={race}")
        ap = fit_ap(panel_naive, race)
        apc = fit_apc(panel_naive, race)
        naive_results[race] = {"ap": ap, "apc": apc}
        print(f"    AP n_obs={ap['n_obs']} deviance={ap['deviance']:.1f}")
        print(f"    APC n_obs={apc['n_obs']} deviance={apc['deviance']:.1f} cohort_ref={apc['cohort_ref']}")
        for yr in (2013, 2014, 2015):
            ap_e = ap["period_effects"][yr]
            apc_e = apc["period_effects"][yr]
            print(f"      yr={yr}: AP beta={ap_e['beta']:+.4f} RR={ap_e['rr']:.3f} | APC beta={apc_e['beta']:+.4f} RR={apc_e['rr']:.3f}")
        for m_name, m in (("ap", ap), ("apc", apc)):
            pdf = period_effects_to_df(m)
            pdf.to_csv(OUTDIR / f"period_effects_naive_{m_name}_{race}.csv", index=False)

    # -------------------------------------------------------------------- Step 3: bilateral
    print("\n--- Step 3: APC under bilateral race coding ---")
    fd_bil = code_bilateral_fd(fd)
    nat_bil = code_bilateral_nat(nat)
    panel_bil = aggregate_panel(
        fd, nat, fd_bil, nat_bil,
        ga_threshold=24, singletons_only=False,
        year_min=YEAR_MIN_PRIMARY, year_max=YEAR_MAX_PRIMARY,
    )
    panel_bil.to_csv(OUTDIR / "panel_bilateral_24wk.csv", index=False)
    rates_bil = annual_rates(panel_bil)
    rates_bil.to_csv(OUTDIR / "annual_rates_bilateral_24wk.csv", index=False)
    print("Bilateral annual crude rates 2012-2016:")
    print(rates_bil[rates_bil["data_year"].between(2012, 2016)].pivot(
        index="data_year", columns="race", values="fmr_per_1000").round(2))

    bilateral_results = {}
    for race in ("Black", "White"):
        print(f"  Race={race}")
        ap = fit_ap(panel_bil, race)
        apc = fit_apc(panel_bil, race)
        bilateral_results[race] = {"ap": ap, "apc": apc}
        print(f"    AP n_obs={ap['n_obs']} deviance={ap['deviance']:.1f}")
        print(f"    APC n_obs={apc['n_obs']} deviance={apc['deviance']:.1f} cohort_ref={apc['cohort_ref']}")
        for yr in (2013, 2014, 2015):
            ap_e = ap["period_effects"][yr]
            apc_e = apc["period_effects"][yr]
            print(f"      yr={yr}: AP beta={ap_e['beta']:+.4f} RR={ap_e['rr']:.3f} | APC beta={apc_e['beta']:+.4f} RR={apc_e['rr']:.3f}")
        for m_name, m in (("ap", ap), ("apc", apc)):
            pdf = period_effects_to_df(m)
            pdf.to_csv(OUTDIR / f"period_effects_bilateral_{m_name}_{race}.csv", index=False)

    # -------------------------------------------------------------------- Cross-check 2014 step
    print("\n--- Cross-check: 2014 boundary step in naive vs bilateral CRUDE rates ---")
    cross_check_rows = []
    for race in ("Black", "White"):
        r2013_n = float(rates_naive[(rates_naive["data_year"] == 2013) & (rates_naive["race"] == race)]["fmr_per_1000"].iloc[0])
        r2014_n = float(rates_naive[(rates_naive["data_year"] == 2014) & (rates_naive["race"] == race)]["fmr_per_1000"].iloc[0])
        r2013_b = float(rates_bil[(rates_bil["data_year"] == 2013) & (rates_bil["race"] == race)]["fmr_per_1000"].iloc[0])
        r2014_b = float(rates_bil[(rates_bil["data_year"] == 2014) & (rates_bil["race"] == race)]["fmr_per_1000"].iloc[0])
        cross_check_rows.append({
            "race": race,
            "naive_2013": round(r2013_n, 3), "naive_2014": round(r2014_n, 3),
            "naive_step_2013_to_2014": round(r2014_n - r2013_n, 3),
            "bilateral_2013": round(r2013_b, 3), "bilateral_2014": round(r2014_b, 3),
            "bilateral_step_2013_to_2014": round(r2014_b - r2013_b, 3),
            "expected_naive_artifact_per_1000": -0.87 if race == "White" else -1.09,
        })
    cc = pd.DataFrame(cross_check_rows)
    cc.to_csv(OUTDIR / "boundary_2014_crude_rate_check.csv", index=False)
    print(cc.to_string(index=False))

    # -------------------------------------------------------------------- Comparison: boundary betas
    print("\n--- Boundary comparison: 2014 period effect change naive -> bilateral ---")
    boundary_rows = []
    for race in ("Black", "White"):
        for model_name in ("ap", "apc"):
            bc = boundary_change(naive_results[race][model_name], bilateral_results[race][model_name],
                                  race, year_target=2014)
            bc["model"] = model_name
            boundary_rows.append(bc)
    bdf = pd.DataFrame(boundary_rows)
    bdf.to_csv(OUTDIR / "boundary_period_effect_change.csv", index=False)
    print(bdf.to_string(index=False))

    # -------------------------------------------------------------------- Cohort effects: youngest survival
    print("\n--- Youngest-cohort effect: naive vs bilateral (APC) ---")
    cohort_rows = []
    for race in ("Black", "White"):
        cn = naive_results[race]["apc"]["cohort_effects"]
        cb = bilateral_results[race]["apc"]["cohort_effects"]
        # Sort cohorts by lower bound year
        def k(s): return int(s.split("-")[0])
        # Identify post-1990 (youngest) cohorts
        youngest = [c for c in sorted(cn.keys(), key=k) if k(c) >= 1990]
        for c in youngest:
            beta_n = cn.get(c, {}).get("beta", np.nan)
            beta_b = cb.get(c, {}).get("beta", np.nan)
            rr_n = float(np.exp(beta_n)) if not np.isnan(beta_n) else np.nan
            rr_b = float(np.exp(beta_b)) if not np.isnan(beta_b) else np.nan
            if abs(beta_n) > 1e-6:
                pct = 100.0 * abs(beta_b - beta_n) / abs(beta_n)
            else:
                pct = np.nan
            cohort_rows.append({
                "race": race, "cohort": c,
                "beta_naive": beta_n, "rr_naive": rr_n,
                "beta_bilateral": beta_b, "rr_bilateral": rr_b,
                "abs_pct_change": pct,
            })
    cohort_df = pd.DataFrame(cohort_rows)
    cohort_df.to_csv(OUTDIR / "cohort_effects_youngest.csv", index=False)
    print(cohort_df.to_string(index=False))

    # -------------------------------------------------------------------- Step 4: sensitivity
    print("\n--- Step 4 sensitivity: >=20wk, singletons-only, 2024 extension ---")
    sens_results = {}
    # 4a. >=20wk
    panel_bil_20 = aggregate_panel(fd, nat, fd_bil, nat_bil, ga_threshold=20,
                                   singletons_only=False, year_min=YEAR_MIN_PRIMARY, year_max=YEAR_MAX_PRIMARY)
    panel_bil_20.to_csv(OUTDIR / "panel_bilateral_20wk.csv", index=False)
    ap_20 = {r: fit_ap(panel_bil_20, r) for r in ("Black", "White")}
    sens_results["20wk_AP"] = ap_20
    # 4b. singletons-only
    panel_bil_sing = aggregate_panel(fd, nat, fd_bil, nat_bil, ga_threshold=24,
                                     singletons_only=True, year_min=YEAR_MIN_PRIMARY, year_max=YEAR_MAX_PRIMARY)
    panel_bil_sing.to_csv(OUTDIR / "panel_bilateral_24wk_singleton.csv", index=False)
    ap_sing = {r: fit_ap(panel_bil_sing, r) for r in ("Black", "White")}
    sens_results["singleton_AP"] = ap_sing
    # 4c. extend to 2024
    panel_bil_ext = aggregate_panel(fd, nat, fd_bil, nat_bil, ga_threshold=24,
                                    singletons_only=False, year_min=YEAR_MIN_PRIMARY, year_max=YEAR_MAX_EXTENDED)
    panel_bil_ext.to_csv(OUTDIR / "panel_bilateral_24wk_to2024.csv", index=False)
    rates_ext = annual_rates(panel_bil_ext)
    rates_ext.to_csv(OUTDIR / "annual_rates_bilateral_24wk_to2024.csv", index=False)
    ap_ext = {r: fit_ap(panel_bil_ext, r) for r in ("Black", "White")}
    sens_results["ext2024_AP"] = ap_ext

    # Summaries: print 2014 boundary across sensitivity variants
    print("\nSensitivity period-effect summary at year=2014 (AP model):")
    sens_summary_rows = []
    for variant_name, variant in sens_results.items():
        for race in ("Black", "White"):
            e2013 = variant[race]["period_effects"][2013]
            e2014 = variant[race]["period_effects"][2014]
            e2015 = variant[race]["period_effects"][2015]
            sens_summary_rows.append({
                "variant": variant_name, "race": race,
                "beta_2013": e2013["beta"], "rr_2013": e2013["rr"],
                "beta_2014": e2014["beta"], "rr_2014": e2014["rr"],
                "beta_2015": e2015["beta"], "rr_2015": e2015["rr"],
            })
    sens_df = pd.DataFrame(sens_summary_rows)
    sens_df.to_csv(OUTDIR / "sensitivity_period_effects.csv", index=False)
    print(sens_df.to_string(index=False))

    # 2020-2024 extension period effects (bilateral)
    ext_extra = []
    for race in ("Black", "White"):
        for yr in (2020, 2021, 2022, 2023, 2024):
            e = ap_ext[race]["period_effects"][yr]
            ext_extra.append({"race": race, "year": yr, "beta": e["beta"], "rr": e["rr"]})
    ext_df = pd.DataFrame(ext_extra)
    ext_df.to_csv(OUTDIR / "extension_2020_2024_period_effects.csv", index=False)
    print("\nBilateral extension 2020-2024 period effects (AP):")
    print(ext_df.to_string(index=False))

    # -------------------------------------------------------------------- Persist results
    def trim_for_json(m):
        # statsmodels float scalars are fine; cohort dicts already simple
        return m

    serializable = {
        "step1_reproduction": cmp_df.to_dict(orient="records"),
        "boundary_2014_crude_rate_check": cc.to_dict(orient="records"),
        "boundary_period_effect_change": bdf.to_dict(orient="records"),
        "cohort_youngest": cohort_df.to_dict(orient="records"),
        "sensitivity_summary": sens_df.to_dict(orient="records"),
        "extension_2020_2024": ext_df.to_dict(orient="records"),
        "naive_AP_summary": {
            r: {y: {"beta": v["beta"], "rr": v["rr"]}
                for y, v in naive_results[r]["ap"]["period_effects"].items()}
            for r in ("Black", "White")
        },
        "bilateral_AP_summary": {
            r: {y: {"beta": v["beta"], "rr": v["rr"]}
                for y, v in bilateral_results[r]["ap"]["period_effects"].items()}
            for r in ("Black", "White")
        },
        "naive_APC_summary": {
            r: {y: {"beta": v["beta"], "rr": v["rr"]}
                for y, v in naive_results[r]["apc"]["period_effects"].items()}
            for r in ("Black", "White")
        },
        "bilateral_APC_summary": {
            r: {y: {"beta": v["beta"], "rr": v["rr"]}
                for y, v in bilateral_results[r]["apc"]["period_effects"].items()}
            for r in ("Black", "White")
        },
        "naive_APC_cohort": {
            r: {c: {"beta": v["beta"], "rr": v["rr"]}
                for c, v in naive_results[r]["apc"]["cohort_effects"].items()}
            for r in ("Black", "White")
        },
        "bilateral_APC_cohort": {
            r: {c: {"beta": v["beta"], "rr": v["rr"]}
                for c, v in bilateral_results[r]["apc"]["cohort_effects"].items()}
            for r in ("Black", "White")
        },
    }
    results.update(serializable)
    with (OUTDIR / "results.json").open("w") as f:
        json.dump(results, f, indent=2, default=str)

    print(f"\nWrote outputs to {OUTDIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
