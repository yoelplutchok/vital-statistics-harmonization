"""Independent replication of Ananth et al. 2022 stillbirth disparity analysis.

Streams natality year-by-year (201M rows). Aggregates FD + LB, fits Poisson AP/APC,
writes to RECEIPTS/ananth2022_outputs_independent/. Does NOT read prior outputs.

Naive Ananth-proxy variants (vs bilateral):
  naive_default       — bridged through 2017 (FD) / 2019 (nat); NH rhr/eth5 after
  naive_rhr_2014      — NH rhr/eth5 from 2014+ (earlier switch)
  naive_bridged_prefer — maternal_race_bridged whenever non-null; else NH fallback
  naive_hisp_impute   — 2014+: bridged first; Hispanic→bridged W/B when bridged set
  naive_mrace6        — 2014+: maternal_race_recode6 (MRACE6) 1/2; else bridged pre-2014
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
OUTDIR = REPO_ROOT / "RECEIPTS" / "ananth2022_outputs_independent"
OUTDIR.mkdir(parents=True, exist_ok=True)

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

YEAR_MIN = 1982
YEAR_MAX = 2020
YEAR_MAX_EXT = 2024

AGE_BANDS = [
    ("<20", 11, 19),
    ("20-24", 20, 24),
    ("25-29", 25, 29),
    ("30-34", 30, 34),
    ("35-39", 35, 39),
    ("40-44", 40, 44),
    ("45-49", 45, 49),
]
AGE_BAND_MID = {
    "<20": 17.5,
    "20-24": 22.5,
    "25-29": 27.5,
    "30-34": 32.5,
    "35-39": 37.5,
    "40-44": 42.5,
    "45-49": 47.5,
}
AGE_REF = "25-29"
YEAR_REF = 2000

AGE_RECODE14_TO_BAND = {
    "01": "<20",
    "02": "<20",
    "03": "<20",
    "04": "<20",
    "05": "<20",
    "06": "<20",
    "07": "20-24",
    "08": "25-29",
    "09": "30-34",
    "10": "35-39",
    "11": "40-44",
    "12": "45-49",
}

# Prior memo headline targets (for cell-by-cell comparison only — not inputs).
PRIOR = {
    "step1_ge20wk_2020": {"Black": 9.94, "White": 4.62},
    "step1_ge24wk_2020": {"Black": 6.79, "White": 3.28},
    "crude_ge20wk_step": {"Black": {"naive": -0.335, "bilateral": -1.418}, "White": {"naive": -0.114, "bilateral": -0.955}},
    "ap_ge20wk_rr_2014": {"Black": {"naive": 0.815, "bilateral": 0.729}, "White": {"naive": 0.921, "bilateral": 0.766}},
    "ap_pct_change_ge20wk": {"Black": 54.7, "White": 223.0},
}

NAIVE_SCHEMES = (
    "naive_default",
    "naive_rhr_2014",
    "naive_bridged_prefer",
    "naive_hisp_impute",
    "naive_mrace6",
)
ALL_SCHEMES = ("bilateral",) + NAIVE_SCHEMES


def age_to_band(ages: pd.Series) -> pd.Series:
    a = pd.to_numeric(ages, errors="coerce")
    out = pd.Series(pd.NA, index=ages.index, dtype="string")
    for label, lo, hi in AGE_BANDS:
        out[(a >= lo) & (a <= hi)] = label
    return out


def cohort_5yr(period: pd.Series, age_band: pd.Series) -> pd.Series:
    mid = age_band.map(AGE_BAND_MID)
    c = period.astype(float) - mid
    lo = (np.floor(c / 5) * 5).astype(int)
    return lo.astype(str) + "-" + (lo + 4).astype(str)


def _from_bridged(s: pd.Series) -> pd.Series:
    out = pd.Series(pd.NA, index=s.index, dtype="string")
    out[s == 1] = "White"
    out[s == 2] = "Black"
    return out


def _from_rhr(s: pd.Series) -> pd.Series:
    out = pd.Series(pd.NA, index=s.index, dtype="string")
    out[s.astype(str) == "1"] = "White"
    out[s.astype(str) == "2"] = "Black"
    return out


def _from_eth5(s: pd.Series) -> pd.Series:
    out = pd.Series(pd.NA, index=s.index, dtype="string")
    out[s == "NH_white"] = "White"
    out[s == "NH_black"] = "Black"
    return out


def _from_mrace6(s: pd.Series) -> pd.Series:
    m = pd.to_numeric(s, errors="coerce")
    out = pd.Series(pd.NA, index=s.index, dtype="string")
    out[m == 1] = "White"
    out[m == 2] = "Black"
    return out


def assign_race_fd_vectorized(df: pd.DataFrame, scheme: str) -> pd.Series:
    y = df["data_year"]
    b = df["maternal_race_bridged"]
    rhr = df["race_hispanic_revised"]
    m6 = df.get("maternal_race_recode6", pd.Series(pd.NA, index=df.index))

    if scheme == "bilateral":
        out = pd.Series(pd.NA, index=df.index, dtype="string")
        pre = y <= 2013
        out[pre] = _from_bridged(b[pre])
        out[~pre] = _from_rhr(rhr[~pre])
        return out

    if scheme == "naive_default":
        out = pd.Series(pd.NA, index=df.index, dtype="string")
        pre = y <= 2017
        out[pre] = _from_bridged(b[pre])
        out[~pre] = _from_rhr(rhr[~pre])
        return out

    if scheme == "naive_rhr_2014":
        out = pd.Series(pd.NA, index=df.index, dtype="string")
        pre = y <= 2013
        out[pre] = _from_bridged(b[pre])
        out[~pre] = _from_rhr(rhr[~pre])
        return out

    if scheme == "naive_bridged_prefer":
        out = _from_bridged(b)
        miss = out.isna()
        out[miss] = _from_rhr(rhr[miss])
        return out

    if scheme == "naive_hisp_impute":
        out = pd.Series(pd.NA, index=df.index, dtype="string")
        pre = y <= 2013
        out[pre] = _from_bridged(b[pre])
        post = ~pre
        out[post] = _from_bridged(b[post])
        miss = post & out.isna()
        out[miss] = _from_rhr(rhr[miss])
        hisp = post & (rhr.astype(str) == "7") & out.isna()
        out[hisp] = _from_bridged(b[hisp])
        return out

    if scheme == "naive_mrace6":
        out = pd.Series(pd.NA, index=df.index, dtype="string")
        pre = y < 2014
        out[pre] = _from_bridged(b[pre])
        post = y >= 2014
        out[post] = _from_mrace6(m6[post])
        miss = post & out.isna()
        out[miss] = _from_bridged(b[miss])
        return out

    raise ValueError(scheme)


def assign_race_nat_vectorized(df: pd.DataFrame, year: int, scheme: str) -> pd.Series:
    b = df["maternal_race_bridged"]
    eth = df["maternal_race_ethnicity_5"]

    if scheme == "bilateral":
        if year <= 2013:
            return _from_bridged(b)
        return _from_eth5(eth)

    if scheme == "naive_default":
        if year <= 2019:
            return _from_bridged(b)
        return _from_eth5(eth)

    if scheme == "naive_rhr_2014":
        if year <= 2013:
            return _from_bridged(b)
        return _from_eth5(eth)

    if scheme == "naive_bridged_prefer":
        out = _from_bridged(b)
        miss = out.isna()
        out[miss] = _from_eth5(eth[miss])
        return out

    if scheme == "naive_hisp_impute":
        if year <= 2013:
            return _from_bridged(b)
        out = _from_bridged(b)
        miss = out.isna()
        out[miss] = _from_eth5(eth[miss])
        hisp = (eth == "Hispanic") & out.isna()
        out[hisp] = _from_bridged(b[hisp])
        return out

    if scheme == "naive_mrace6":
        return _from_bridged(b)

    raise ValueError(scheme)


def aggregate_fetal_death() -> pd.DataFrame:
    cols = [
        "data_year",
        "tabulation_flag",
        "residence_status",
        "maternal_age",
        "maternal_age_recode14",
        "gestational_age_combined",
        "plurality",
        "maternal_race_bridged",
        "race_hispanic_revised",
        "maternal_race_recode6",
    ]
    fd = pd.read_parquet(FD_PARQUET, columns=cols)
    fd = fd[(fd["tabulation_flag"] == 2) & (fd["residence_status"] != 4)].copy()
    fd["ga"] = pd.to_numeric(fd["gestational_age_combined"], errors="coerce")
    fd = fd[fd["ga"].notna() & (fd["ga"] != 99)].copy()

    band = age_to_band(fd["maternal_age"])
    fb = band.isna() & fd["maternal_age_recode14"].notna()
    band[fb] = fd.loc[fb, "maternal_age_recode14"].map(AGE_RECODE14_TO_BAND)
    fd["age_band"] = band
    fd = fd[fd["age_band"].notna()].copy()
    fd["is_singleton"] = fd["plurality"].astype(str) == "1"
    fd["ge20"] = fd["ga"] >= 20
    fd["ge24"] = fd["ga"] >= 24

    parts: list[pd.DataFrame] = []
    for scheme in ALL_SCHEMES:
        fd["race"] = assign_race_fd_vectorized(fd, scheme)
        for ga_label, gmask in (("ge20wk", fd["ge20"]), ("ge24wk", fd["ge24"])):
            for plural_label, pmask in (("all", pd.Series(True, index=fd.index)), ("singleton", fd["is_singleton"])):
                sub = fd[gmask & pmask & fd["race"].notna()]
                g = (
                    sub.groupby(["data_year", "age_band", "race"], observed=True)
                    .size()
                    .reset_index(name="fd_count")
                )
                g["scheme"] = scheme
                g["ga_threshold"] = ga_label
                g["plurality_filter"] = plural_label
                parts.append(g)
    return pd.concat(parts, ignore_index=True)


def aggregate_natality(year_max: int) -> pd.DataFrame:
    ds = pads.dataset(str(NAT_PARQUET))
    project = [
        "data_year",
        "residence_status",
        "maternal_age",
        "singleton",
        "maternal_race_bridged",
        "maternal_race_ethnicity_5",
    ]
    parts: list[pd.DataFrame] = []
    for year in range(YEAR_MIN, year_max + 1):
        flt = (
            (pc.field("data_year") == year)
            & (pc.field("residence_status") != 4)
            & (pc.field("maternal_age") >= 11)
            & (pc.field("maternal_age") <= 49)
        )
        tbl = ds.to_table(columns=project, filter=flt)
        if tbl.num_rows == 0:
            continue
        df = tbl.to_pandas()
        df["age_band"] = age_to_band(df["maternal_age"])
        df = df[df["age_band"].notna()].copy()

        for scheme in ALL_SCHEMES:
            df["race"] = assign_race_nat_vectorized(df, year, scheme)
            for plural_label, pmask in (
                ("all", pd.Series(True, index=df.index)),
                ("singleton", df["singleton"] == True),
            ):
                sub = df[pmask & df["race"].notna()]
                g = (
                    sub.groupby(["age_band", "race"], observed=True)
                    .size()
                    .reset_index(name="lb_count")
                )
                g["data_year"] = year
                g["scheme"] = scheme
                g["plurality_filter"] = plural_label
                parts.append(g)
        del df
        print(f"  nat {year}: done", flush=True)
    return pd.concat(parts, ignore_index=True)


def build_panel(
    fd_agg: pd.DataFrame,
    nat_agg: pd.DataFrame,
    scheme: str,
    ga_threshold: str,
    plurality_filter: str,
    year_max: int = YEAR_MAX,
) -> pd.DataFrame:
    fd = fd_agg[
        (fd_agg["scheme"] == scheme)
        & (fd_agg["ga_threshold"] == ga_threshold)
        & (fd_agg["plurality_filter"] == plurality_filter)
        & fd_agg["data_year"].between(YEAR_MIN, year_max)
    ]
    nat = nat_agg[
        (nat_agg["scheme"] == scheme)
        & (nat_agg["plurality_filter"] == plurality_filter)
        & nat_agg["data_year"].between(YEAR_MIN, year_max)
    ]
    panel = pd.merge(
        fd[["data_year", "age_band", "race", "fd_count"]],
        nat[["data_year", "age_band", "race", "lb_count"]],
        on=["data_year", "age_band", "race"],
        how="outer",
    )
    panel["fd_count"] = panel["fd_count"].fillna(0).astype(np.int64)
    panel["lb_count"] = panel["lb_count"].fillna(0).astype(np.int64)
    panel["denom"] = panel["fd_count"] + panel["lb_count"]
    panel = panel[panel["denom"] > 0].copy()
    panel["fmr_per_1000"] = 1000.0 * panel["fd_count"] / panel["denom"]
    panel["cohort"] = cohort_5yr(panel["data_year"], panel["age_band"])
    return panel


def annual_rates(panel: pd.DataFrame) -> pd.DataFrame:
    g = (
        panel.groupby(["data_year", "race"], observed=True)
        .agg(fd=("fd_count", "sum"), lb=("lb_count", "sum"), denom=("denom", "sum"))
        .reset_index()
    )
    g["fmr_per_1000"] = 1000.0 * g["fd"] / g["denom"]
    return g


def fit_ap(panel: pd.DataFrame, race: str, year_ref: int = YEAR_REF) -> dict:
    df = panel[(panel["race"] == race) & (panel["denom"] > 0)].copy()
    df["year_str"] = df["data_year"].astype(int).astype(str)
    df["age_str"] = df["age_band"].astype(str)
    year_levels = sorted(df["data_year"].unique().tolist())
    age_d = pd.get_dummies(df["age_str"], prefix="age").drop(columns=[f"age_{AGE_REF}"], errors="ignore")
    year_d = pd.get_dummies(df["year_str"], prefix="yr").drop(columns=[f"yr_{year_ref}"], errors="ignore")
    x = pd.concat([pd.Series(1.0, index=df.index, name="const"), age_d, year_d], axis=1).astype(float)
    y = df["fd_count"].astype(float).values
    offset = np.log(df["denom"].astype(float).values)
    res = sm.GLM(y, x, family=sm.families.Poisson(), offset=offset).fit(maxiter=200)
    coef = res.params
    period: dict[int, dict] = {}
    for yr in year_levels:
        if yr == year_ref:
            period[yr] = {"beta": 0.0, "se": 0.0, "rr": 1.0}
        else:
            k = f"yr_{yr}"
            if k in coef.index:
                period[yr] = {"beta": float(coef[k]), "se": float(res.bse[k]), "rr": float(np.exp(coef[k]))}
    return {"race": race, "year_ref": year_ref, "n_obs": len(df), "period_effects": period}


def fit_apc(panel: pd.DataFrame, race: str, year_ref: int = YEAR_REF) -> dict:
    df = panel[(panel["race"] == race) & (panel["denom"] > 0)].copy()
    df["year_str"] = df["data_year"].astype(int).astype(str)
    df["age_str"] = df["age_band"].astype(str)
    df["cohort_str"] = df["cohort"].astype(str)
    year_levels = sorted(df["data_year"].unique().tolist())
    cohort_levels = sorted(df["cohort_str"].unique(), key=lambda s: int(s.split("-")[0]))
    cohort_ref = cohort_levels[len(cohort_levels) // 2]
    age_d = pd.get_dummies(df["age_str"], prefix="age").drop(columns=[f"age_{AGE_REF}"], errors="ignore")
    year_d = pd.get_dummies(df["year_str"], prefix="yr").drop(columns=[f"yr_{year_ref}"], errors="ignore")
    cohort_d = pd.get_dummies(df["cohort_str"], prefix="coh").drop(columns=[f"coh_{cohort_ref}"], errors="ignore")
    non_ref = [c for c in cohort_levels if c != cohort_ref]
    c1, c2 = non_ref[0], non_ref[1]
    merged = f"coh_{c1}|{c2}"
    cohort_d[merged] = cohort_d[f"coh_{c1}"] + cohort_d[f"coh_{c2}"]
    cohort_d = cohort_d.drop(columns=[f"coh_{c1}", f"coh_{c2}"])
    x = pd.concat([pd.Series(1.0, index=df.index, name="const"), age_d, year_d, cohort_d], axis=1).astype(float)
    y = df["fd_count"].astype(float).values
    offset = np.log(df["denom"].astype(float).values)
    res = sm.GLM(y, x, family=sm.families.Poisson(), offset=offset).fit(maxiter=200)
    coef = res.params
    period: dict[int, dict] = {}
    for yr in year_levels:
        if yr == year_ref:
            period[yr] = {"beta": 0.0, "rr": 1.0}
        else:
            k = f"yr_{yr}"
            if k in coef.index:
                period[yr] = {"beta": float(coef[k]), "rr": float(np.exp(coef[k]))}
    cohort: dict[str, dict] = {cohort_ref: {"beta": 0.0, "rr": 1.0}}
    for c in cohort_levels:
        if c == cohort_ref:
            continue
        if c in (c1, c2):
            if merged in coef.index:
                cohort[c] = {"beta": float(coef[merged]), "rr": float(np.exp(coef[merged]))}
            continue
        k = f"coh_{c}"
        if k in coef.index:
            cohort[c] = {"beta": float(coef[k]), "rr": float(np.exp(coef[k]))}
    return {"race": race, "cohort_ref": cohort_ref, "period_effects": period, "cohort_effects": cohort}


def boundary_shift(naive_ap: dict, bil_ap: dict, year: int = 2014) -> dict:
    bn = naive_ap["period_effects"].get(year, {}).get("beta", np.nan)
    bb = bil_ap["period_effects"].get(year, {}).get("beta", np.nan)
    pct = 100.0 * abs(bb - bn) / abs(bn) if abs(bn) > 1e-9 else np.nan
    return {
        "beta_naive": bn,
        "beta_bilateral": bb,
        "rr_naive": float(np.exp(bn)),
        "rr_bilateral": float(np.exp(bb)),
        "abs_pct_change": pct,
    }


def compare_to_prior(indep: dict) -> pd.DataFrame:
    rows = []
    for race in ("Black", "White"):
        for thr, key in (("ge20wk", "step1_ge20wk_2020"), ("ge24wk", "step1_ge24wk_2020")):
            got = indep["step1"][thr][race]
            exp = PRIOR[key][race]
            rows.append(
                {
                    "metric": f"step1_{thr}_2020_{race}",
                    "independent": got,
                    "prior_memo": exp,
                    "diff": round(got - exp, 3),
                    "pct_diff": round(100 * (got - exp) / exp, 2) if exp else np.nan,
                    "match": abs(got - exp) <= 0.05,
                }
            )
        got_n = indep["crude_step"]["ge20wk"][race]["naive"]
        got_b = indep["crude_step"]["ge20wk"][race]["bilateral"]
        rows.append(
            {
                "metric": f"crude_step_ge20wk_{race}_naive",
                "independent": got_n,
                "prior_memo": PRIOR["crude_ge20wk_step"][race]["naive"],
                "diff": round(got_n - PRIOR["crude_ge20wk_step"][race]["naive"], 3),
                "pct_diff": np.nan,
                "match": abs(got_n - PRIOR["crude_ge20wk_step"][race]["naive"]) <= 0.02,
            }
        )
        rows.append(
            {
                "metric": f"crude_step_ge20wk_{race}_bilateral",
                "independent": got_b,
                "prior_memo": PRIOR["crude_ge20wk_step"][race]["bilateral"],
                "diff": round(got_b - PRIOR["crude_ge20wk_step"][race]["bilateral"], 3),
                "pct_diff": np.nan,
                "match": abs(got_b - PRIOR["crude_ge20wk_step"][race]["bilateral"]) <= 0.02,
            }
        )
        got_rr_n = indep["ap_rr"]["ge20wk"][race]["naive"]
        got_rr_b = indep["ap_rr"]["ge20wk"][race]["bilateral"]
        rows.append(
            {
                "metric": f"ap_rr_ge20wk_2014_{race}_naive",
                "independent": got_rr_n,
                "prior_memo": PRIOR["ap_ge20wk_rr_2014"][race]["naive"],
                "diff": round(got_rr_n - PRIOR["ap_ge20wk_rr_2014"][race]["naive"], 3),
                "pct_diff": np.nan,
                "match": abs(got_rr_n - PRIOR["ap_ge20wk_rr_2014"][race]["naive"]) <= 0.01,
            }
        )
        rows.append(
            {
                "metric": f"ap_rr_ge20wk_2014_{race}_bilateral",
                "independent": got_rr_b,
                "prior_memo": PRIOR["ap_ge20wk_rr_2014"][race]["bilateral"],
                "diff": round(got_rr_b - PRIOR["ap_ge20wk_rr_2014"][race]["bilateral"], 3),
                "pct_diff": np.nan,
                "match": abs(got_rr_b - PRIOR["ap_ge20wk_rr_2014"][race]["bilateral"]) <= 0.01,
            }
        )
        pct = indep["ap_pct_change"]["ge20wk"][race]
        rows.append(
            {
                "metric": f"ap_pct_change_ge20wk_{race}",
                "independent": round(pct, 1),
                "prior_memo": PRIOR["ap_pct_change_ge20wk"][race],
                "diff": round(pct - PRIOR["ap_pct_change_ge20wk"][race], 1),
                "pct_diff": np.nan,
                "match": abs(pct - PRIOR["ap_pct_change_ge20wk"][race]) <= 2.0,
            }
        )
    return pd.DataFrame(rows)


def main() -> int:
    ts = dt.datetime.now(dt.timezone.utc).isoformat()
    print(f"=== independent ananth2022 replication === {ts}", flush=True)
    assert FD_PARQUET.exists(), FD_PARQUET
    assert NAT_PARQUET.exists(), NAT_PARQUET

    print("FD aggregation...", flush=True)
    fd_agg = aggregate_fetal_death()
    fd_agg.to_csv(OUTDIR / "fd_aggregated.csv", index=False)

    print("Natality year-by-year...", flush=True)
    nat_agg = aggregate_natality(YEAR_MAX_EXT)
    nat_agg.to_csv(OUTDIR / "nat_aggregated.csv", index=False)

    panels: dict[tuple, pd.DataFrame] = {}
    rates: dict[tuple, pd.DataFrame] = {}
    models: dict[tuple, dict] = {}

    for scheme in ALL_SCHEMES:
        for ga in ("ge20wk", "ge24wk"):
            for plural in ("all", "singleton"):
                ym_ext = YEAR_MAX_EXT if scheme == "bilateral" and plural == "all" else YEAR_MAX
                key = (scheme, ga, plural)
                panels[key] = build_panel(fd_agg, nat_agg, scheme, ga, plural, year_max=ym_ext)
                panels[key].to_csv(OUTDIR / f"panel_{scheme}_{ga}_{plural}.csv", index=False)
            p_all = panels[(scheme, ga, "all")]
            rates[(scheme, ga)] = annual_rates(p_all[p_all["data_year"] <= YEAR_MAX])
            rates[(scheme, ga)].to_csv(OUTDIR / f"annual_rates_{scheme}_{ga}.csv", index=False)

    # Step 1 (naive_default only — Ananth proxy)
    ananth = {(1980, "Black"): 17.4, (1980, "White"): 9.2, (2020, "Black"): 10.1, (2020, "White"): 5.0}
    step1_rows = []
    for ga in ("ge20wk", "ge24wk"):
        rt = rates[("naive_default", ga)]
        for yr in (1982, 1990, 2000, 2010, 2020):
            for race in ("Black", "White"):
                m = rt[(rt["data_year"] == yr) & (rt["race"] == race)]
                if m.empty:
                    continue
                hvs = round(float(m["fmr_per_1000"].iloc[0]), 2)
                row = {"scheme": "naive_default", "threshold": ga, "year": yr, "race": race, "hvs_per_1000": hvs}
                if yr == 1982:
                    t = ananth[(1980, race)]
                    row.update(
                        {
                            "ananth_year": 1980,
                            "ananth_per_1000": t,
                            "diff": round(hvs - t, 2),
                            "pass": abs(hvs - t) <= 0.5,
                        }
                    )
                elif yr == 2020:
                    t = ananth[(2020, race)]
                    row.update(
                        {
                            "ananth_year": 2020,
                            "ananth_per_1000": t,
                            "diff": round(hvs - t, 2),
                            "pass": abs(hvs - t) <= 0.5,
                        }
                    )
                step1_rows.append(row)
    step1_df = pd.DataFrame(step1_rows)
    step1_df.to_csv(OUTDIR / "step1_reproduction.csv", index=False)

    # Models: bilateral + each naive vs bilateral boundary
    print("Fitting AP/APC...", flush=True)
    for scheme in ALL_SCHEMES:
        for ga in ("ge20wk", "ge24wk"):
            p = panels[(scheme, ga, "all")]
            p = p[p["data_year"] <= YEAR_MAX].copy()
            models[(scheme, ga)] = {}
            for race in ("Black", "White"):
                models[(scheme, ga)][race] = {"ap": fit_ap(p, race), "apc": fit_apc(p, race)}

    # Boundary tables
    bd_crude = []
    bd_ap = []
    for ga in ("ge20wk", "ge24wk"):
        rn = rates[("naive_default", ga)]
        rb = rates[("bilateral", ga)]
        for race in ("Black", "White"):
            n13 = float(rn[(rn.data_year == 2013) & (rn.race == race)]["fmr_per_1000"].iloc[0])
            n14 = float(rn[(rn.data_year == 2014) & (rn.race == race)]["fmr_per_1000"].iloc[0])
            b13 = float(rb[(rb.data_year == 2013) & (rb.race == race)]["fmr_per_1000"].iloc[0])
            b14 = float(rb[(rb.data_year == 2014) & (rb.race == race)]["fmr_per_1000"].iloc[0])
            bd_crude.append(
                {
                    "threshold": ga,
                    "race": race,
                    "naive_2013": round(n13, 3),
                    "naive_2014": round(n14, 3),
                    "naive_step": round(n14 - n13, 3),
                    "bilateral_2013": round(b13, 3),
                    "bilateral_2014": round(b14, 3),
                    "bilateral_step": round(b14 - b13, 3),
                }
            )
            ch = boundary_shift(
                models[("naive_default", ga)][race]["ap"],
                models[("bilateral", ga)][race]["ap"],
            )
            ch.update({"threshold": ga, "race": race, "model": "ap"})
            bd_ap.append(ch)
    pd.DataFrame(bd_crude).to_csv(OUTDIR / "boundary_crude_steps.csv", index=False)
    pd.DataFrame(bd_ap).to_csv(OUTDIR / "boundary_ap_shift_naive_default.csv", index=False)

    # Naive variant robustness (>25% AP shift at 2014 vs bilateral)
    variant_rows = []
    for naive in NAIVE_SCHEMES:
        for ga in ("ge20wk", "ge24wk"):
            for race in ("Black", "White"):
                ch = boundary_shift(
                    models[(naive, ga)][race]["ap"],
                    models[("bilateral", ga)][race]["ap"],
                )
                variant_rows.append(
                    {
                        "naive_scheme": naive,
                        "threshold": ga,
                        "race": race,
                        "rr_naive": round(ch["rr_naive"], 4),
                        "rr_bilateral": round(ch["rr_bilateral"], 4),
                        "abs_pct_change": round(ch["abs_pct_change"], 1),
                        "meets_25pct": ch["abs_pct_change"] > 25,
                    }
                )
    variant_df = pd.DataFrame(variant_rows)
    variant_df.to_csv(OUTDIR / "naive_variant_boundary_robustness.csv", index=False)

    # Cohort youngest (naive_default vs bilateral)
    coh_rows = []
    for ga in ("ge20wk", "ge24wk"):
        for race in ("Black", "White"):
            cn = models[("naive_default", ga)][race]["apc"]["cohort_effects"]
            cb = models[("bilateral", ga)][race]["apc"]["cohort_effects"]

            def k(s: str) -> int:
                return int(s.split("-")[0])

            for c in sorted((x for x in cn if k(x) >= 1985), key=k):
                bn = cn[c].get("beta", np.nan)
                bb = cb.get(c, {}).get("beta", np.nan)
                pct = 100 * abs(bb - bn) / abs(bn) if abs(bn) > 1e-9 else np.nan
                coh_rows.append(
                    {
                        "threshold": ga,
                        "race": race,
                        "cohort": c,
                        "abs_pct_change": round(pct, 2),
                    }
                )
    pd.DataFrame(coh_rows).to_csv(OUTDIR / "cohort_youngest_shift.csv", index=False)

    bd_crude_df = pd.DataFrame(bd_crude)
    indep_summary = {"step1": {"ge20wk": {}, "ge24wk": {}}, "crude_step": {"ge20wk": {}}, "ap_rr": {"ge20wk": {}}, "ap_pct_change": {"ge20wk": {}}}
    for race in ("Black", "White"):
        for ga, slot in (("ge20wk", "ge20wk"), ("ge24wk", "ge24wk")):
            indep_summary["step1"][slot][race] = float(
                rates[("naive_default", ga)][
                    (rates[("naive_default", ga)]["data_year"] == 2020) & (rates[("naive_default", ga)]["race"] == race)
                ]["fmr_per_1000"].iloc[0]
            )
        row = bd_crude_df[(bd_crude_df["race"] == race) & (bd_crude_df["threshold"] == "ge20wk")].iloc[0]
        indep_summary["crude_step"]["ge20wk"][race] = {"naive": float(row["naive_step"]), "bilateral": float(row["bilateral_step"])}
        ch = boundary_shift(
            models[("naive_default", "ge20wk")][race]["ap"],
            models[("bilateral", "ge20wk")][race]["ap"],
        )
        indep_summary["ap_rr"]["ge20wk"][race] = {"naive": ch["rr_naive"], "bilateral": ch["rr_bilateral"]}
        indep_summary["ap_pct_change"]["ge20wk"][race] = ch["abs_pct_change"]

    cmp_df = compare_to_prior(indep_summary)
    cmp_df.to_csv(OUTDIR / "comparison_to_prior_memo.csv", index=False)

    results = {
        "timestamp_utc": ts,
        "step1": step1_df.to_dict(orient="records"),
        "boundary_crude": bd_crude,
        "boundary_ap_naive_default": bd_ap,
        "naive_variants": variant_df.to_dict(orient="records"),
        "comparison_to_prior": cmp_df.to_dict(orient="records"),
        "all_match": bool(cmp_df["match"].all()),
    }
    with (OUTDIR / "results.json").open("w") as f:
        json.dump(results, f, indent=2, default=str)

    print("\n--- Step 1 (naive_default) ---")
    print(step1_df.to_string(index=False))
    print("\n--- Boundary crude (naive_default vs bilateral) ---")
    print(pd.DataFrame(bd_crude).to_string(index=False))
    print("\n--- AP 2014 shift (naive_default vs bilateral) ---")
    print(pd.DataFrame(bd_ap).to_string(index=False))
    print("\n--- Naive variant robustness (>25%?) ---")
    print(variant_df.to_string(index=False))
    print("\n--- Comparison to prior memo ---")
    print(cmp_df.to_string(index=False))
    print(f"\nWrote {OUTDIR}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
