"""Ananth 2022 replication test — memory-efficient v2.

Aggregates natality year-by-year via pyarrow filtered scans, so we never
hold more than one year's natality rows in memory (~3-4M rows / year).
All other analysis runs on the small (year x age_band x race) aggregated
panels.

Also fixes V2.1 (2003-2004) maternal-age handling: those years' FD records
have null `maternal_age` but a valid `maternal_age_recode14` that maps to
the standard age bands.
"""

from __future__ import annotations
import json
import os
import sys
import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow.dataset as pads
import pyarrow.compute as pc
import statsmodels.api as sm

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTDIR = REPO_ROOT / "RECEIPTS" / "ananth2022_outputs"
OUTDIR.mkdir(parents=True, exist_ok=True)

FD_PARQUET = Path(os.environ.get(
    "HVS_FETAL_DERIVED",
    "/Users/yoelplutchok/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_derived.parquet"))
NAT_PARQUET = Path(os.environ.get(
    "HVS_NATAL_DERIVED",
    "/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet"))
assert FD_PARQUET.exists() and NAT_PARQUET.exists()

YEAR_MIN = 1982
YEAR_MAX_PRIMARY = 2020
YEAR_MAX_EXT = 2024

AGE_BANDS = [
    ("<20",   11, 19),
    ("20-24", 20, 24),
    ("25-29", 25, 29),
    ("30-34", 30, 34),
    ("35-39", 35, 39),
    ("40-44", 40, 44),
    ("45-49", 45, 49),
]
AGE_BAND_MIDPOINTS = {"<20": 17.5, "20-24": 22.5, "25-29": 27.5, "30-34": 32.5,
                       "35-39": 37.5, "40-44": 42.5, "45-49": 47.5}
AGE_REF = "25-29"

# maternal_age_recode14 mapping (NCHS standard 14-band recode):
#  01=<15, 02=15, 03=16, 04=17, 05=18, 06=19, 07=20-24, 08=25-29, 09=30-34,
#  10=35-39, 11=40-44, 12=45-49, 13=50+, 14=Not stated
AGE_RECODE14_TO_BAND = {
    "01": "<20", "02": "<20", "03": "<20", "04": "<20", "05": "<20", "06": "<20",
    "07": "20-24", "08": "25-29", "09": "30-34",
    "10": "35-39", "11": "40-44", "12": "45-49",
    # "13": "50+" excluded by Ananth's <50 filter; "14"=Not stated → null
}


def age_to_band(age: pd.Series) -> pd.Series:
    a = pd.to_numeric(age, errors="coerce")
    out = pd.Series(pd.NA, index=age.index, dtype="string")
    for label, lo, hi in AGE_BANDS:
        out[(a >= lo) & (a <= hi)] = label
    return out


def cohort_5yr(period: pd.Series, age_band: pd.Series) -> pd.Series:
    midp = age_band.map(AGE_BAND_MIDPOINTS)
    c = period - midp
    bin_lo = (np.floor(c / 5) * 5).astype(int)
    return bin_lo.astype(str) + "-" + (bin_lo + 4).astype(str)


# ---------------------------------------------------------------------------
# FD aggregation (small file ~2.4M rows fits in memory)
# ---------------------------------------------------------------------------


def aggregate_fd() -> pd.DataFrame:
    """Return long-form FD count panel keyed by:

    data_year, age_band, race_naive_W, race_naive_B,
    race_bilateral_W, race_bilateral_B, ga_threshold (20 or 24), is_singleton.

    Counts are: fd_count for the cell.
    """
    cols = ["data_year", "tabulation_flag", "residence_status",
            "maternal_age", "maternal_age_recode14",
            "gestational_age_combined", "plurality",
            "maternal_race_bridged", "race_hispanic_revised"]
    fd = pd.read_parquet(FD_PARQUET, columns=cols)
    fd = fd[(fd["tabulation_flag"] == 2) & (fd["residence_status"] != 4)].copy()
    fd["ga"] = pd.to_numeric(fd["gestational_age_combined"], errors="coerce")
    fd = fd[fd["ga"].notna() & (fd["ga"] != 99)].copy()
    # Build age_band: prefer maternal_age, fall back to maternal_age_recode14
    # (only matters for V2.1 2003-2004; maternal_age is null there).
    age_band = age_to_band(fd["maternal_age"])
    needs_fallback = age_band.isna() & fd["maternal_age_recode14"].notna()
    age_band[needs_fallback] = fd.loc[needs_fallback, "maternal_age_recode14"].map(AGE_RECODE14_TO_BAND)
    fd["age_band"] = age_band
    fd = fd[fd["age_band"].notna()].copy()
    # Naive race coding: bridged 1982-2017, race_hispanic_revised codes '1'/'2' 2018+
    pre = fd["data_year"] <= 2017
    post = fd["data_year"] >= 2018
    fd["race_naive"] = pd.Series(pd.NA, index=fd.index, dtype="string")
    fd.loc[pre & (fd["maternal_race_bridged"] == 1), "race_naive"] = "White"
    fd.loc[pre & (fd["maternal_race_bridged"] == 2), "race_naive"] = "Black"
    fd.loc[post & (fd["race_hispanic_revised"] == "1"), "race_naive"] = "White"
    fd.loc[post & (fd["race_hispanic_revised"] == "2"), "race_naive"] = "Black"
    # Bilateral: bridged 1982-2013, race_hispanic_revised collapsed NH-only 2014+
    pre_b = fd["data_year"] <= 2013
    post_b = fd["data_year"] >= 2014
    fd["race_bilateral"] = pd.Series(pd.NA, index=fd.index, dtype="string")
    fd.loc[pre_b & (fd["maternal_race_bridged"] == 1), "race_bilateral"] = "White"
    fd.loc[pre_b & (fd["maternal_race_bridged"] == 2), "race_bilateral"] = "Black"
    fd.loc[post_b & (fd["race_hispanic_revised"] == "1"), "race_bilateral"] = "White"  # NH White
    fd.loc[post_b & (fd["race_hispanic_revised"] == "2"), "race_bilateral"] = "Black"  # NH Black
    fd["is_singleton"] = fd["plurality"].astype(str) == "1"

    # Tag GA tiers: 20+ vs 24+
    fd["ga_ge20"] = fd["ga"] >= 20
    fd["ga_ge24"] = fd["ga"] >= 24
    # Aggregate twice (naive + bilateral) for each scheme x GA threshold x singleton flag
    parts = []
    for scheme, col in (("naive", "race_naive"), ("bilateral", "race_bilateral")):
        for ga_label, mask in (("ge20wk", fd["ga_ge20"]), ("ge24wk", fd["ga_ge24"])):
            for sing_label, sing_mask in (("all", pd.Series(True, index=fd.index)),
                                           ("singleton", fd["is_singleton"])):
                sub = fd[mask & sing_mask & fd[col].notna()]
                g = (sub.groupby(["data_year", "age_band", col], observed=True)
                     .size().reset_index(name="fd_count")
                     .rename(columns={col: "race"}))
                g["scheme"] = scheme
                g["ga_threshold"] = ga_label
                g["plurality_filter"] = sing_label
                parts.append(g)
    out = pd.concat(parts, ignore_index=True)
    return out


# ---------------------------------------------------------------------------
# NAT aggregation: streamed year-by-year via pyarrow
# ---------------------------------------------------------------------------


def aggregate_nat(year_max: int) -> pd.DataFrame:
    """Year-by-year streaming aggregation of natality counts.

    Output rows keyed by data_year, age_band, race (scheme-specific),
    scheme (naive|bilateral), plurality_filter (all|singleton).
    """
    ds = pads.dataset(str(NAT_PARQUET))
    project = ["data_year", "residence_status", "maternal_age", "singleton",
               "maternal_race_bridged", "maternal_race_ethnicity_5"]
    parts = []
    for year in range(YEAR_MIN, year_max + 1):
        flt = (pc.field("data_year") == year) & (pc.field("residence_status") != 4) \
              & (pc.field("maternal_age") >= 11) & (pc.field("maternal_age") <= 49)
        tbl = ds.to_table(columns=project, filter=flt)
        if tbl.num_rows == 0:
            continue
        df = tbl.to_pandas()
        df["age_band"] = age_to_band(df["maternal_age"])
        # Naive: bridged 1982-2019, eth5 NH 2020+
        if year <= 2019:
            mrb = df["maternal_race_bridged"]
            df["race_naive"] = pd.Series(pd.NA, index=df.index, dtype="string")
            df.loc[mrb == 1, "race_naive"] = "White"
            df.loc[mrb == 2, "race_naive"] = "Black"
        else:
            eth5 = df["maternal_race_ethnicity_5"]
            df["race_naive"] = pd.Series(pd.NA, index=df.index, dtype="string")
            df.loc[eth5 == "NH_white", "race_naive"] = "White"
            df.loc[eth5 == "NH_black", "race_naive"] = "Black"
        # Bilateral: bridged 1982-2013, eth5 NH 2014+
        if year <= 2013:
            mrb = df["maternal_race_bridged"]
            df["race_bilateral"] = pd.Series(pd.NA, index=df.index, dtype="string")
            df.loc[mrb == 1, "race_bilateral"] = "White"
            df.loc[mrb == 2, "race_bilateral"] = "Black"
        else:
            eth5 = df["maternal_race_ethnicity_5"]
            df["race_bilateral"] = pd.Series(pd.NA, index=df.index, dtype="string")
            df.loc[eth5 == "NH_white", "race_bilateral"] = "White"
            df.loc[eth5 == "NH_black", "race_bilateral"] = "Black"
        # Aggregate
        for scheme, col in (("naive", "race_naive"), ("bilateral", "race_bilateral")):
            for sing_label, sing_mask in (("all", pd.Series(True, index=df.index)),
                                          ("singleton", df["singleton"] == True)):
                sub = df[sing_mask & df[col].notna() & df["age_band"].notna()]
                g = (sub.groupby(["age_band", col], observed=True).size()
                     .reset_index(name="lb_count").rename(columns={col: "race"}))
                g["data_year"] = year
                g["scheme"] = scheme
                g["plurality_filter"] = sing_label
                parts.append(g)
        del df
        print(f"  {year}: aggregated", flush=True)
    return pd.concat(parts, ignore_index=True)


# ---------------------------------------------------------------------------
# Panel assembly + analysis
# ---------------------------------------------------------------------------


def build_panel(fd_agg: pd.DataFrame, nat_agg: pd.DataFrame,
                scheme: str, ga_threshold: str, plurality_filter: str,
                year_min: int = YEAR_MIN, year_max: int = YEAR_MAX_PRIMARY) -> pd.DataFrame:
    fd = fd_agg[(fd_agg["scheme"] == scheme) & (fd_agg["ga_threshold"] == ga_threshold)
                & (fd_agg["plurality_filter"] == plurality_filter)
                & fd_agg["data_year"].between(year_min, year_max)].copy()
    nat = nat_agg[(nat_agg["scheme"] == scheme) & (nat_agg["plurality_filter"] == plurality_filter)
                  & nat_agg["data_year"].between(year_min, year_max)].copy()
    panel = pd.merge(
        fd[["data_year", "age_band", "race", "fd_count"]],
        nat[["data_year", "age_band", "race", "lb_count"]],
        on=["data_year", "age_band", "race"], how="outer",
    )
    panel["fd_count"] = panel["fd_count"].fillna(0).astype(int)
    panel["lb_count"] = panel["lb_count"].fillna(0).astype(int)
    panel["denom"] = panel["lb_count"] + panel["fd_count"]
    panel = panel[panel["denom"] > 0].copy()
    panel["fmr_per_1000"] = 1000 * panel["fd_count"] / panel["denom"]
    panel["cohort"] = cohort_5yr(panel["data_year"], panel["age_band"])
    return panel


def annual_rates(panel: pd.DataFrame) -> pd.DataFrame:
    g = (panel.groupby(["data_year", "race"], observed=True)
         .agg(fd=("fd_count", "sum"), lb=("lb_count", "sum"), denom=("denom", "sum"))
         .reset_index())
    g["fmr_per_1000"] = 1000 * g["fd"] / g["denom"]
    return g


def fit_ap(panel: pd.DataFrame, race: str, year_ref: int = 2000) -> dict:
    df = panel[(panel["race"] == race) & (panel["denom"] > 0)].copy()
    df["year_str"] = df["data_year"].astype(int).astype(str)
    df["age_str"] = df["age_band"].astype(str)
    age_levels = [b for b, _, _ in AGE_BANDS]
    year_levels = sorted(df["data_year"].unique().tolist())
    age_d = pd.get_dummies(df["age_str"], prefix="age").drop(columns=[f"age_{AGE_REF}"], errors="ignore")
    year_d = pd.get_dummies(df["year_str"], prefix="yr").drop(columns=[f"yr_{year_ref}"], errors="ignore")
    X = pd.concat([pd.Series(1.0, index=df.index, name="const"), age_d, year_d], axis=1).astype(float)
    y = df["fd_count"].astype(float).values
    offset = np.log(df["denom"].astype(float).values)
    res = sm.GLM(y, X, family=sm.families.Poisson(), offset=offset).fit(maxiter=200)
    coef, se = res.params, res.bse
    period = {}
    for yr in year_levels:
        if yr == year_ref:
            period[yr] = {"beta": 0.0, "se": 0.0, "rr": 1.0}
        else:
            k = f"yr_{yr}"
            if k in coef.index:
                period[yr] = {"beta": float(coef[k]), "se": float(se[k]), "rr": float(np.exp(coef[k]))}
    return {"race": race, "year_ref": year_ref, "n_obs": int(len(df)),
            "deviance": float(res.deviance), "period_effects": period,
            "intercept": float(coef["const"])}


def fit_apc(panel: pd.DataFrame, race: str, year_ref: int = 2000,
            cohort_ref: str | None = None) -> dict:
    df = panel[(panel["race"] == race) & (panel["denom"] > 0)].copy()
    df["year_str"] = df["data_year"].astype(int).astype(str)
    df["age_str"] = df["age_band"].astype(str)
    df["cohort_str"] = df["cohort"].astype(str)
    age_levels = [b for b, _, _ in AGE_BANDS]
    year_levels = sorted(df["data_year"].unique().tolist())
    cohort_levels = sorted(df["cohort_str"].unique().tolist(), key=lambda s: int(s.split("-")[0]))
    if cohort_ref is None:
        cohort_ref = cohort_levels[len(cohort_levels) // 2]
    age_d = pd.get_dummies(df["age_str"], prefix="age").drop(columns=[f"age_{AGE_REF}"], errors="ignore")
    year_d = pd.get_dummies(df["year_str"], prefix="yr").drop(columns=[f"yr_{year_ref}"], errors="ignore")
    cohort_d = pd.get_dummies(df["cohort_str"], prefix="coh").drop(columns=[f"coh_{cohort_ref}"], errors="ignore")
    non_ref = [c for c in cohort_levels if c != cohort_ref]
    c1, c2 = non_ref[0], non_ref[1]
    merged = f"coh_{c1}|{c2}"
    cohort_d[merged] = cohort_d[f"coh_{c1}"] + cohort_d[f"coh_{c2}"]
    cohort_d = cohort_d.drop(columns=[f"coh_{c1}", f"coh_{c2}"])
    X = pd.concat([pd.Series(1.0, index=df.index, name="const"), age_d, year_d, cohort_d], axis=1).astype(float)
    y = df["fd_count"].astype(float).values
    offset = np.log(df["denom"].astype(float).values)
    res = sm.GLM(y, X, family=sm.families.Poisson(), offset=offset).fit(maxiter=200)
    coef = res.params
    period = {}
    for yr in year_levels:
        if yr == year_ref:
            period[yr] = {"beta": 0.0, "rr": 1.0}
        else:
            k = f"yr_{yr}"
            if k in coef.index:
                period[yr] = {"beta": float(coef[k]), "rr": float(np.exp(coef[k]))}
    cohort = {cohort_ref: {"beta": 0.0, "rr": 1.0}}
    for c in cohort_levels:
        if c == cohort_ref:
            continue
        if c in (c1, c2):
            if merged in coef.index:
                cohort[c] = {"beta": float(coef[merged]), "rr": float(np.exp(coef[merged])),
                              "constraint": "merged_with_adjacent"}
            continue
        k = f"coh_{c}"
        if k in coef.index:
            cohort[c] = {"beta": float(coef[k]), "rr": float(np.exp(coef[k]))}
    return {"race": race, "year_ref": year_ref, "cohort_ref": cohort_ref,
            "holford_merged_cohorts": [c1, c2],
            "n_obs": int(len(df)), "deviance": float(res.deviance),
            "period_effects": period, "cohort_effects": cohort,
            "intercept": float(coef["const"])}


def boundary_pct(naive_m: dict, bil_m: dict, yr_target: int = 2014) -> dict:
    bn = naive_m["period_effects"].get(yr_target, {}).get("beta", np.nan)
    bb = bil_m["period_effects"].get(yr_target, {}).get("beta", np.nan)
    pct = 100.0 * abs(bb - bn) / abs(bn) if abs(bn) > 1e-9 else np.inf
    return {"beta_naive": bn, "beta_bilateral": bb, "diff": bb - bn,
            "rr_naive": float(np.exp(bn)), "rr_bilateral": float(np.exp(bb)),
            "abs_pct_change": pct}


def main() -> int:
    print(f"=== ananth2022_replication_test_v2 ===  {dt.datetime.now(dt.timezone.utc).isoformat()}", flush=True)

    # ---- Aggregate FD ----
    print("Aggregating FD...", flush=True)
    fd_agg = aggregate_fd()
    fd_agg.to_csv(OUTDIR / "fd_aggregated.csv", index=False)
    print(f"  FD aggregated rows: {len(fd_agg):,}", flush=True)

    # ---- Aggregate NAT (streamed) ----
    print("Streaming-aggregating NAT 1982-2024...", flush=True)
    nat_agg = aggregate_nat(YEAR_MAX_EXT)
    nat_agg.to_csv(OUTDIR / "nat_aggregated.csv", index=False)
    print(f"  NAT aggregated rows: {len(nat_agg):,}", flush=True)

    # ---- Build panels ----
    panels = {}
    for scheme in ("naive", "bilateral"):
        for ga in ("ge20wk", "ge24wk"):
            for plural in ("all", "singleton"):
                key = (scheme, ga, plural)
                panels[key] = build_panel(fd_agg, nat_agg, scheme, ga, plural,
                                          year_min=YEAR_MIN, year_max=YEAR_MAX_PRIMARY)
        # extended-year bilateral panels
        for ga in ("ge20wk", "ge24wk"):
            key = (scheme, ga, "all_ext")
            panels[key] = build_panel(fd_agg, nat_agg, scheme, ga, "all",
                                      year_min=YEAR_MIN, year_max=YEAR_MAX_EXT)

    # Save key panels
    for (scheme, ga, plural), p in panels.items():
        p.to_csv(OUTDIR / f"panel_{scheme}_{ga}_{plural}.csv", index=False)

    # ---- Annual rates ----
    rates = {}
    for key, p in panels.items():
        rates[key] = annual_rates(p)
    rates_naive_20 = rates[("naive", "ge20wk", "all")]
    rates_naive_24 = rates[("naive", "ge24wk", "all")]
    rates_bil_20 = rates[("bilateral", "ge20wk", "all")]
    rates_bil_24 = rates[("bilateral", "ge24wk", "all")]
    rates_naive_20.to_csv(OUTDIR / "annual_rates_naive_ge20wk.csv", index=False)
    rates_naive_24.to_csv(OUTDIR / "annual_rates_naive_ge24wk.csv", index=False)
    rates_bil_20.to_csv(OUTDIR / "annual_rates_bilateral_ge20wk.csv", index=False)
    rates_bil_24.to_csv(OUTDIR / "annual_rates_bilateral_ge24wk.csv", index=False)
    rates_bil_ext20 = rates[("bilateral", "ge20wk", "all_ext")]
    rates_bil_ext20.to_csv(OUTDIR / "annual_rates_bilateral_ge20wk_to2024.csv", index=False)

    # ---- Step 1 reproduction (both thresholds) ----
    ananth_targets = {(1980, "Black"): 17.4, (1980, "White"): 9.2,
                      (2020, "Black"): 10.1, (2020, "White"): 5.0}
    cmp_rows = []
    for thr_label, rt in (("ge20wk", rates_naive_20), ("ge24wk", rates_naive_24)):
        for yr in (1982, 1990, 2000, 2010, 2020):
            for race in ("Black", "White"):
                m = rt[(rt["data_year"] == yr) & (rt["race"] == race)]
                if m.empty:
                    continue
                hvs = float(m["fmr_per_1000"].iloc[0])
                row = {"threshold": thr_label, "year": yr, "race": race,
                       "hvs_per_1000": round(hvs, 2)}
                if yr == 1982 and (1980, race) in ananth_targets:
                    t = ananth_targets[(1980, race)]
                    row.update({"ananth_year": 1980, "ananth_per_1000": t,
                                "diff": round(hvs - t, 2),
                                "tolerance_pass": abs(hvs - t) <= 0.5,
                                "note": "1982 HVS vs 1980 Ananth (HVS PUF floor)"})
                elif (yr, race) in ananth_targets:
                    t = ananth_targets[(yr, race)]
                    row.update({"ananth_year": yr, "ananth_per_1000": t,
                                "diff": round(hvs - t, 2),
                                "tolerance_pass": abs(hvs - t) <= 0.5,
                                "note": "direct"})
                else:
                    row.update({"ananth_year": None, "ananth_per_1000": None,
                                "diff": None, "tolerance_pass": None, "note": "no Ananth headline"})
                cmp_rows.append(row)
    cmp_df = pd.DataFrame(cmp_rows)
    cmp_df.to_csv(OUTDIR / "step1_reproduction_both_thresholds.csv", index=False)
    print("\nStep 1 reproduction (both thresholds):")
    print(cmp_df.to_string(index=False))

    # ---- 2014 boundary crude rate check (both thresholds) ----
    bd_all = []
    for thr_label, n, b, expected in (
        ("ge20wk", rates_naive_20, rates_bil_20, {"Black": -1.09, "White": -0.87}),
        ("ge24wk", rates_naive_24, rates_bil_24, {"Black": -1.09, "White": -0.87}),  # same docs
    ):
        for race in ("Black", "White"):
            nv13 = float(n[(n.data_year == 2013) & (n.race == race)]["fmr_per_1000"].iloc[0])
            nv14 = float(n[(n.data_year == 2014) & (n.race == race)]["fmr_per_1000"].iloc[0])
            bl13 = float(b[(b.data_year == 2013) & (b.race == race)]["fmr_per_1000"].iloc[0])
            bl14 = float(b[(b.data_year == 2014) & (b.race == race)]["fmr_per_1000"].iloc[0])
            bd_all.append({"threshold": thr_label, "race": race,
                           "naive_2013": round(nv13, 3), "naive_2014": round(nv14, 3),
                           "naive_step": round(nv14 - nv13, 3),
                           "bilateral_2013": round(bl13, 3), "bilateral_2014": round(bl14, 3),
                           "bilateral_step": round(bl14 - bl13, 3),
                           "expected_step_doc": expected[race]})
    bd_df = pd.DataFrame(bd_all)
    bd_df.to_csv(OUTDIR / "boundary_2014_crude_rate_check_both.csv", index=False)
    print("\n2014 boundary crude rates (both thresholds):")
    print(bd_df.to_string(index=False))

    # ---- APC fits ----
    print("\nFitting AP + APC models at both thresholds...", flush=True)
    models = {}
    for scheme in ("naive", "bilateral"):
        for ga in ("ge20wk", "ge24wk"):
            key = (scheme, ga)
            print(f"  {scheme} {ga}...", flush=True)
            models[key] = {}
            for race in ("Black", "White"):
                ap = fit_ap(panels[(scheme, ga, "all")], race)
                apc = fit_apc(panels[(scheme, ga, "all")], race)
                models[key][race] = {"ap": ap, "apc": apc}

    # Boundary period-effect change naive→bilateral at both thresholds
    bdy = []
    for ga in ("ge20wk", "ge24wk"):
        for race in ("Black", "White"):
            for mod in ("ap", "apc"):
                ch = boundary_pct(models[("naive", ga)][race][mod],
                                  models[("bilateral", ga)][race][mod], 2014)
                ch.update({"race": race, "model": mod, "threshold": ga, "year": 2014})
                bdy.append(ch)
    bdy_df = pd.DataFrame(bdy)
    bdy_df.to_csv(OUTDIR / "boundary_period_effect_change_both.csv", index=False)
    print("\n2014 boundary period-effect change naive->bilateral:")
    print(bdy_df.to_string(index=False))

    # Period effects across 2013/2014/2015 for narrative table
    pe_rows = []
    for ga in ("ge20wk", "ge24wk"):
        for scheme in ("naive", "bilateral"):
            for race in ("Black", "White"):
                for mod in ("ap", "apc"):
                    for yr in (2013, 2014, 2015):
                        e = models[(scheme, ga)][race][mod]["period_effects"][yr]
                        pe_rows.append({"threshold": ga, "scheme": scheme, "race": race,
                                        "model": mod, "year": yr,
                                        "beta": e["beta"], "rr": e["rr"]})
    pe_df = pd.DataFrame(pe_rows)
    pe_df.to_csv(OUTDIR / "period_effects_2013_2014_2015_both.csv", index=False)

    # Youngest-cohort effects at both thresholds
    cohort_rows = []
    for ga in ("ge20wk", "ge24wk"):
        for race in ("Black", "White"):
            cn = models[("naive", ga)][race]["apc"]["cohort_effects"]
            cb = models[("bilateral", ga)][race]["apc"]["cohort_effects"]
            def k(s): return int(s.split("-")[0])
            young = [c for c in sorted(cn.keys(), key=k) if k(c) >= 1985]
            for c in young:
                bn = cn.get(c, {}).get("beta", np.nan)
                bb = cb.get(c, {}).get("beta", np.nan)
                pct = 100.0 * abs(bb - bn) / abs(bn) if abs(bn) > 1e-9 else np.nan
                cohort_rows.append({"threshold": ga, "race": race, "cohort": c,
                                    "beta_naive": bn, "rr_naive": float(np.exp(bn)) if not np.isnan(bn) else np.nan,
                                    "beta_bilateral": bb, "rr_bilateral": float(np.exp(bb)) if not np.isnan(bb) else np.nan,
                                    "abs_pct_change": pct})
    coh_df = pd.DataFrame(cohort_rows)
    coh_df.to_csv(OUTDIR / "cohort_effects_youngest_both.csv", index=False)
    print("\nYoungest-cohort effects (post-1985 cohorts):")
    print(coh_df.to_string(index=False))

    # ---- Step 4 sensitivity: singleton + 2024 extension ----
    print("\nStep 4: singleton AP + 2024-extension AP (bilateral)...", flush=True)
    sens = {}
    for ga in ("ge20wk", "ge24wk"):
        p_sing = panels[("bilateral", ga, "singleton")]
        ap_sing = {r: fit_ap(p_sing, r) for r in ("Black", "White")}
        sens[("singleton", ga)] = ap_sing
        p_ext = panels[("bilateral", ga, "all_ext")]
        ap_ext = {r: fit_ap(p_ext, r) for r in ("Black", "White")}
        sens[("ext2024", ga)] = ap_ext

    sens_rows = []
    for ga in ("ge20wk", "ge24wk"):
        # Primary variants (year_max=2020)
        for scheme in ("naive", "bilateral"):
            for race in ("Black", "White"):
                e = models[(scheme, ga)][race]["ap"]["period_effects"]
                row = {"variant": f"{scheme}_{ga}", "race": race}
                for y in (2013, 2014, 2015):
                    row[f"beta_{y}"] = e[y]["beta"]; row[f"rr_{y}"] = e[y]["rr"]
                sens_rows.append(row)
        # Singleton
        for race in ("Black", "White"):
            e = sens[("singleton", ga)][race]["period_effects"]
            row = {"variant": f"bilateral_{ga}_singleton", "race": race}
            for y in (2013, 2014, 2015):
                row[f"beta_{y}"] = e[y]["beta"]; row[f"rr_{y}"] = e[y]["rr"]
            sens_rows.append(row)
        # 2024 extension
        for race in ("Black", "White"):
            e = sens[("ext2024", ga)][race]["period_effects"]
            row = {"variant": f"bilateral_{ga}_to2024", "race": race}
            for y in (2013, 2014, 2015, 2020, 2022, 2024):
                if y in e:
                    row[f"beta_{y}"] = e[y]["beta"]; row[f"rr_{y}"] = e[y]["rr"]
            sens_rows.append(row)
    sens_df = pd.DataFrame(sens_rows)
    sens_df.to_csv(OUTDIR / "sensitivity_period_effects_both.csv", index=False)
    print(sens_df.to_string(index=False))

    # 2020-2024 extended period effects (bilateral ge20wk)
    ext_rows = []
    for race in ("Black", "White"):
        e = sens[("ext2024", "ge20wk")][race]["period_effects"]
        r = rates_bil_ext20
        for y in (2020, 2021, 2022, 2023, 2024):
            crude = r[(r.data_year == y) & (r.race == race)]
            ext_rows.append({"race": race, "year": y,
                             "beta": e.get(y, {}).get("beta", np.nan),
                             "rr": e.get(y, {}).get("rr", np.nan),
                             "crude_fmr": float(crude["fmr_per_1000"].iloc[0]) if not crude.empty else np.nan})
    ext_df = pd.DataFrame(ext_rows)
    ext_df.to_csv(OUTDIR / "extension_2020_2024_bilateral_ge20wk.csv", index=False)
    print("\nBilateral ≥20wk extension 2020-2024 period effects + crude rates:")
    print(ext_df.to_string(index=False))

    # ---- Serialize all results ----
    serial = {
        "timestamp_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "fd_parquet": str(FD_PARQUET),
        "nat_parquet": str(NAT_PARQUET),
        "step1_reproduction": cmp_df.to_dict(orient="records"),
        "boundary_2014_crude_rates": bd_df.to_dict(orient="records"),
        "boundary_period_effect_change": bdy_df.to_dict(orient="records"),
        "period_effects_2013_2014_2015": pe_df.to_dict(orient="records"),
        "cohort_youngest": coh_df.to_dict(orient="records"),
        "sensitivity_summary": sens_df.to_dict(orient="records"),
        "extension_2020_2024_bilateral_ge20wk": ext_df.to_dict(orient="records"),
        "models_period_effects": {
            f"{scheme}_{ga}_{race}_{mod}": {y: e for y, e in models[(scheme, ga)][race][mod]["period_effects"].items()}
            for scheme in ("naive", "bilateral") for ga in ("ge20wk", "ge24wk")
            for race in ("Black", "White") for mod in ("ap", "apc")
        },
        "models_cohort_effects_apc": {
            f"{scheme}_{ga}_{race}": models[(scheme, ga)][race]["apc"]["cohort_effects"]
            for scheme in ("naive", "bilateral") for ga in ("ge20wk", "ge24wk")
            for race in ("Black", "White")
        },
    }
    with (OUTDIR / "results.json").open("w") as f:
        json.dump(serial, f, indent=2, default=str)
    print(f"\nWrote {OUTDIR / 'results.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
