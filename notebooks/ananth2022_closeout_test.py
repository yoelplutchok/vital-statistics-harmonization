"""Ananth 2022 close-out: reproduce Table 4 under his stated methodology only.

Bridged-INCL-Hispanic race throughout; broad filters (no residence/tabulation);
GA threshold configurable (default ≥20 wk; set ANANTH_GA_MIN_WEEKS=24 for prior run);
Poisson APC with natural cubic splines (df=10) + Holford cohort constraint.
"""

from __future__ import annotations

import json
import os
import sys
import datetime as dt
from pathlib import Path

import numpy as np
import pandas as pd
import patsy
import pyarrow.dataset as pads
import pyarrow.compute as pc
import statsmodels.api as sm

REPO_ROOT = Path(__file__).resolve().parents[1]
GA_MIN_WEEKS = int(os.environ.get("ANANTH_GA_MIN_WEEKS", "20"))
OUTDIR = REPO_ROOT / "RECEIPTS" / f"ananth2022_closeout_outputs_ge{GA_MIN_WEEKS}wk"
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
AGE_REF_PERIOD = 2020
COHORT_REF = 1980

AGE_BANDS = [
    ("<20", 11, 19, 17.5),
    ("20-24", 20, 24, 22.5),
    ("25-29", 25, 29, 27.5),
    ("30-34", 30, 34, 32.5),
    ("35-39", 35, 39, 37.5),
    ("40-44", 40, 44, 42.5),
    ("45-49", 45, 49, 47.5),
]

AGE_RECODE14_TO_BAND = {
    "01": "<20", "02": "<20", "03": "<20", "04": "<20", "05": "<20", "06": "<20",
    "07": "20-24", "08": "25-29", "09": "30-34", "10": "35-39", "11": "40-44", "12": "45-49",
}

# Ananth Table 4 reference cells (only known values)
ANANTH_PERIOD = {
    1980: {"Overall": 2.17, "White": 2.23, "Black": 2.07},
    1985: {"Overall": 1.56, "White": 1.62, "Black": 1.41},
    1990: {"Overall": 1.46, "White": 1.47, "Black": 1.48},
    1995: {"Overall": 1.26, "White": 1.29, "Black": 1.29},
    2000: {"Overall": 1.18, "White": 1.16, "Black": 1.29},
    2005: {"Overall": 0.92, "White": 0.90, "Black": 1.01},
    2010: {"Overall": 0.96, "White": 0.98, "Black": 0.99},
    2015: {"Overall": 1.03, "White": 1.02, "Black": 1.03},
    2020: {"Overall": 1.00, "White": 1.00, "Black": 1.00},
}
ANANTH_COHORT = {
    1935: {"Overall": 1.58, "White": 1.55, "Black": 1.26},
    1945: {"Overall": 1.28, "White": 1.25, "Black": 1.15},
    1955: {"Overall": 1.03, "White": 1.02, "Black": 1.06},
    1965: {"Overall": 0.98, "White": 0.98, "Black": 1.03},
    1975: {"Overall": 0.97, "White": 0.98, "Black": 0.96},
    1980: {"Overall": 1.00, "White": 1.00, "Black": 1.00},
    1985: {"Overall": 1.02, "White": 1.02, "Black": 1.01},
    1995: {"Overall": 1.08, "White": 1.07, "Black": 1.12},
    2005: {"Overall": 1.14, "White": 1.12, "Black": 1.30},
}
ANANTH_CRUDE = {
    (1980, "Overall"): 10.6, (1980, "White"): 9.2, (1980, "Black"): 17.4,
    (2020, "Overall"): 5.8, (2020, "White"): 5.0, (2020, "Black"): 10.1,
}
ANANTH_TOTALS = {"stillbirths": 710_832, "live_births": 157_192_032}

RR_TOL = 0.03
RATE_TOL = 0.5


def age_to_band(ages: pd.Series) -> pd.Series:
    a = pd.to_numeric(ages, errors="coerce")
    out = pd.Series(pd.NA, index=ages.index, dtype="string")
    for label, lo, hi, _ in AGE_BANDS:
        out[(a >= lo) & (a <= hi)] = label
    return out


def fd_bridged_incl_hispanic(df: pd.DataFrame) -> pd.Series:
    """Bridged-INCL-Hispanic Black/White; validated 100% vs bridged in 2017."""
    out = pd.Series(pd.NA, index=df.index, dtype="string")
    pre = df["data_year"] <= 2017
    b = df["maternal_race_bridged"]
    out[pre & (b == 1)] = "White"
    out[pre & (b == 2)] = "Black"
    post = df["data_year"] >= 2018
    rhr = df["race_hispanic_revised"].astype(str)
    m6 = pd.to_numeric(df["maternal_race_recode6"], errors="coerce")
    out[post & (rhr == "1")] = "White"
    out[post & (rhr == "2")] = "Black"
    out[post & (m6 == 1)] = "White"
    out[post & (m6 == 2)] = "Black"
    out[post & (rhr == "3")] = "Black"
    return out


def nat_bridged_incl_hispanic(df: pd.DataFrame, year: int) -> pd.Series:
    out = pd.Series(pd.NA, index=df.index, dtype="string")
    if year <= 2019:
        b = df["maternal_race_bridged"]
        out[b == 1] = "White"
        out[b == 2] = "Black"
        return out
    eth = df["maternal_race_ethnicity_5"]
    det = df["maternal_race_detail"].astype(str)
    out[eth == "NH_white"] = "White"
    out[eth == "NH_black"] = "Black"
    hisp = eth == "Hispanic"
    out[hisp & (det == "01")] = "White"
    out[hisp & (det == "02")] = "Black"
    return out


def aggregate_fd() -> pd.DataFrame:
    cols = [
        "data_year", "maternal_age", "maternal_age_recode14",
        "gestational_age_combined", "maternal_race_bridged",
        "race_hispanic_revised", "maternal_race_recode6",
    ]
    fd = pd.read_parquet(FD_PARQUET, columns=cols)
    fd["ga"] = pd.to_numeric(fd["gestational_age_combined"], errors="coerce")
    fd = fd[fd["ga"].notna() & (fd["ga"] != 99) & (fd["ga"] >= GA_MIN_WEEKS)].copy()
    band = age_to_band(fd["maternal_age"])
    fb = band.isna() & fd["maternal_age_recode14"].notna()
    band[fb] = fd.loc[fb, "maternal_age_recode14"].map(AGE_RECODE14_TO_BAND)
    fd["age_band"] = band
    fd = fd[fd["age_band"].notna()].copy()
    fd["race"] = fd_bridged_incl_hispanic(fd)
    fd["age_mid"] = fd["age_band"].map({b: m for b, _, _, m in AGE_BANDS})
    fd["cohort"] = fd["data_year"] - fd["age_mid"]
    parts = []
    for race_scope, mask in (
        ("Overall", pd.Series(True, index=fd.index)),
        ("White", fd["race"] == "White"),
        ("Black", fd["race"] == "Black"),
    ):
        sub = fd[mask]
        g = (
            sub.groupby(["data_year", "age_band", "age_mid", "cohort"], observed=True)
            .size()
            .reset_index(name="fd_count")
        )
        g["race_scope"] = race_scope
        parts.append(g)
    return pd.concat(parts, ignore_index=True)


def aggregate_nat() -> pd.DataFrame:
    ds = pads.dataset(str(NAT_PARQUET))
    project = [
        "data_year", "maternal_age", "maternal_race_bridged",
        "maternal_race_ethnicity_5", "maternal_race_detail",
    ]
    parts = []
    for year in range(YEAR_MIN, YEAR_MAX + 1):
        flt = (pc.field("data_year") == year) & (pc.field("maternal_age") >= 11) & (pc.field("maternal_age") <= 49)
        tbl = ds.to_table(columns=project, filter=flt)
        if tbl.num_rows == 0:
            continue
        df = tbl.to_pandas()
        df["age_band"] = age_to_band(df["maternal_age"])
        df = df[df["age_band"].notna()].copy()
        df["race"] = nat_bridged_incl_hispanic(df, year)
        df["age_mid"] = df["age_band"].map({b: m for b, _, _, m in AGE_BANDS})
        df["cohort"] = year - df["age_mid"]
        for race_scope, mask in (
            ("Overall", pd.Series(True, index=df.index)),
            ("White", df["race"] == "White"),
            ("Black", df["race"] == "Black"),
        ):
            sub = df[mask]
            g = (
                sub.groupby(["age_band", "age_mid", "cohort"], observed=True)
                .size()
                .reset_index(name="lb_count")
            )
            g["data_year"] = year
            g["race_scope"] = race_scope
            parts.append(g)
        del df
        print(f"  nat {year}", flush=True)
    return pd.concat(parts, ignore_index=True)


def build_panel(fd_agg: pd.DataFrame, nat_agg: pd.DataFrame, race_scope: str) -> pd.DataFrame:
    fd = fd_agg[fd_agg["race_scope"] == race_scope]
    nat = nat_agg[nat_agg["race_scope"] == race_scope]
    panel = pd.merge(
        fd, nat, on=["data_year", "age_band", "age_mid", "cohort", "race_scope"], how="outer",
    )
    panel["fd_count"] = panel["fd_count"].fillna(0).astype(np.int64)
    panel["lb_count"] = panel["lb_count"].fillna(0).astype(np.int64)
    panel["events"] = panel["fd_count"]
    panel["denom"] = panel["lb_count"] + panel["fd_count"]
    return panel[panel["denom"] > 0].copy()


def annual_crude(panel: pd.DataFrame) -> pd.DataFrame:
    g = (
        panel.groupby("data_year", observed=True)
        .agg(fd=("fd_count", "sum"), lb=("lb_count", "sum"), denom=("denom", "sum"))
        .reset_index()
    )
    g["rate_per_1000"] = 1000.0 * g["fd"] / g["denom"]
    return g


def reconstruction_diagnostics(fd_agg: pd.DataFrame, nat_agg: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for side, agg, race_col in (
        ("fd", fd_agg[fd_agg["race_scope"] == "White"], "fd_count"),
        ("fd", fd_agg[fd_agg["race_scope"] == "Black"], "fd_count"),
        ("nat", nat_agg[nat_agg["race_scope"] == "White"], "lb_count"),
        ("nat", nat_agg[nat_agg["race_scope"] == "Black"], "lb_count"),
    ):
        for y0, y1 in ((2017, 2018), (2019, 2020)):
            c0 = agg[agg["data_year"] == y0][race_col].sum()
            c1 = agg[agg["data_year"] == y1][race_col].sum()
            pct = 100.0 * (c1 - c0) / c0 if c0 else np.nan
            rows.append({"side": side, "race": agg["race_scope"].iloc[0], "y0": y0, "y1": y1, "count_y0": c0, "count_y1": c1, "pct_change": round(pct, 2)})
    return pd.DataFrame(rows)


def _prep(d: pd.DataFrame) -> pd.DataFrame:
    return d.assign(age=d["age_mid"], period=d["data_year"].astype(float), coh=d["cohort"])


def _build_design(d: pd.DataFrame) -> tuple[pd.DataFrame, object]:
    _, X = patsy.dmatrices(
        "events ~ cr(age, df=10) + cr(period, df=10) + cr(coh, df=10)",
        data=_prep(d),
        return_type="dataframe",
    )
    return X, X.design_info


def fit_apc_spline(panel: pd.DataFrame) -> tuple[object, pd.DataFrame, object]:
    """Poisson APC with cr splines (df=10) and Holford cohort constraint."""
    d = panel[(panel["data_year"] >= YEAR_MIN) & (panel["data_year"] <= YEAR_MAX)].copy()
    X, design_info = _build_design(d)
    y = d["events"].astype(float).values
    offset = np.log(d["denom"].astype(float).values)
    coh_cols = [c for c in X.columns if c.startswith("cr(coh")]
    R = np.zeros((1, X.shape[1]))
    R[0, X.columns.get_loc(coh_cols[0])] = 1.0
    R[0, X.columns.get_loc(coh_cols[1])] = -1.0
    model = sm.GLM(y, X, family=sm.families.Poisson(), offset=offset)
    res = model.fit_constrained((R, np.array([0.0])), maxiter=200)
    return res, X, design_info


def _lp_from_grid(res, design_info, grid: pd.DataFrame, weights: pd.Series) -> float:
    g = grid.assign(events=0.0)
    Xg_dm = patsy.build_design_matrices([design_info], g)[0]
    Xg = pd.DataFrame(np.asarray(Xg_dm), columns=Xg_dm.design_info.column_names)
    for c in res.params.index:
        if c not in Xg.columns:
            Xg[c] = 0.0
    Xg = Xg[list(res.params.index)]
    lps = Xg.to_numpy() @ res.params.values
    w = weights.reindex(grid["age"]).fillna(0).values
    w = w / w.sum() if w.sum() else w
    return float(np.dot(w, lps))


def extract_period_rr(res, design_info, panel: pd.DataFrame, years: list[int], ref: int = AGE_REF_PERIOD) -> dict[int, float]:
    """Period RR vs 2020: age-weighted, cohort = period − age (APC-consistent)."""
    weights = panel.groupby("age_mid", observed=True)["denom"].sum().astype(float)
    age_mids = weights.index.values

    def lp_at(period: float) -> float:
        rows = [{"age": float(am), "period": period, "coh": period - float(am)} for am in age_mids]
        return _lp_from_grid(res, design_info, pd.DataFrame(rows), weights)

    lp_ref = lp_at(float(ref))
    return {int(y): float(np.exp(lp_at(float(y)) - lp_ref)) for y in years}


def _age_mid_for_cohort(cohort: float, period: float) -> float | None:
    """Pick age-band midpoint so period − age ≈ cohort and age in [11, 49]."""
    age = period - cohort
    mids = [m for _, _, _, m in AGE_BANDS]
    if age < mids[0] or age > mids[-1]:
        return None
    for label, lo, hi, mid in AGE_BANDS:
        if lo <= age <= hi:
            return mid
    return None


def extract_cohort_rr(res, design_info, panel: pd.DataFrame, cohorts: list[int], ref: int = COHORT_REF) -> dict[int, float]:
    """Cohort RR vs 1980 at APC-consistent (age, period) support for each cohort."""

    def lp_at(cohort: float) -> float:
        # Anchor period at cohort+27.5 (25–29 band), clip to observed window
        period_val = float(np.clip(cohort + 27.5, YEAR_MIN, YEAR_MAX))
        age_val = _age_mid_for_cohort(cohort, period_val)
        if age_val is None:
            period_val = float(YEAR_MAX if cohort >= 1980 else YEAR_MIN)
            age_val = _age_mid_for_cohort(cohort, period_val)
        if age_val is None:
            return np.nan
        rows = [{"age": age_val, "period": period_val, "coh": cohort}]
        return _lp_from_grid(res, design_info, pd.DataFrame(rows), pd.Series([1.0], index=[0]))

    lp_ref = lp_at(float(ref))
    out = {}
    for c in cohorts:
        lp = lp_at(float(c))
        out[int(c)] = float(np.exp(lp - lp_ref)) if not (np.isnan(lp) or np.isnan(lp_ref)) else np.nan
    return out


def compare_cells(hvs_rr: dict, ananth_table: dict, label: str, race: str) -> list[dict]:
    rows = []
    for key, targets in ananth_table.items():
        target = targets[race]
        got = hvs_rr.get(key, np.nan)
        diff = abs(got - target) if not np.isnan(got) else np.nan
        rows.append(
            {
                "cell_type": label,
                "key": key,
                "race": race,
                "ananth": target,
                "hvs": round(got, 3) if not np.isnan(got) else np.nan,
                "abs_diff": round(diff, 3) if not np.isnan(diff) else np.nan,
                "pass": diff <= RR_TOL if not np.isnan(diff) else False,
                "flag": "1982_offset" if label == "crude" and key == 1980 else "",
            }
        )
    return rows


def main() -> int:
    ts = dt.datetime.now(dt.timezone.utc).isoformat()
    print(f"=== ananth2022_closeout_test (GA>={GA_MIN_WEEKS}wk) === {ts}", flush=True)

    fd_agg = aggregate_fd()
    fd_agg.to_csv(OUTDIR / "fd_aggregated.csv", index=False)
    print("FD done", flush=True)
    nat_agg = aggregate_nat()
    nat_agg.to_csv(OUTDIR / "nat_aggregated.csv", index=False)

    recon = reconstruction_diagnostics(fd_agg, nat_agg)
    recon.to_csv(OUTDIR / "reconstruction_2017_2020.csv", index=False)

    totals = {
        f"fd_ge{GA_MIN_WEEKS}wk": int(fd_agg[fd_agg["race_scope"] == "Overall"]["fd_count"].sum()),
        "lb": int(nat_agg[nat_agg["race_scope"] == "Overall"]["lb_count"].sum()),
    }
    totals["denom"] = totals[f"fd_ge{GA_MIN_WEEKS}wk"] + totals["lb"]
    totals["ga_min_weeks"] = GA_MIN_WEEKS
    with (OUTDIR / "totals_check.json").open("w") as f:
        json.dump({**totals, "ananth": ANANTH_TOTALS}, f, indent=2)

    cmp_rows: list[dict] = []
    model_summaries = {}

    for scope in ("Overall", "White", "Black"):
        panel = build_panel(fd_agg, nat_agg, scope)
        panel.to_csv(OUTDIR / f"panel_{scope.lower()}.csv", index=False)
        crude = annual_crude(panel)
        crude.to_csv(OUTDIR / f"crude_rates_{scope.lower()}.csv", index=False)

        # Crude comparisons (1982 as HVS stand-in for 1980)
        for yr, ananth_yr in ((1982, 1980), (2020, 2020)):
            row = crude[crude["data_year"] == yr]
            if row.empty:
                continue
            hvs_r = float(row["rate_per_1000"].iloc[0])
            ananth_r = ANANTH_CRUDE.get((ananth_yr, scope), np.nan)
            if np.isnan(ananth_r):
                continue
            diff = abs(hvs_r - ananth_r)
            cmp_rows.append(
                {
                    "cell_type": "crude",
                    "key": ananth_yr,
                    "race": scope,
                    "ananth": ananth_r,
                    "hvs": round(hvs_r, 2),
                    "abs_diff": round(diff, 3),
                    "pass": diff <= RATE_TOL if ananth_yr == 2020 else False,
                    "flag": "1982_for_1980" if ananth_yr == 1980 else "",
                }
            )

        print(f"Fitting APC splines: {scope}...", flush=True)
        res, _, design_info = fit_apc_spline(panel)
        period_rr = extract_period_rr(res, design_info, panel, list(ANANTH_PERIOD.keys()), ref=AGE_REF_PERIOD)
        cohort_rr = extract_cohort_rr(res, design_info, panel, list(ANANTH_COHORT.keys()), ref=COHORT_REF)
        model_summaries[scope] = {"period_rr": period_rr, "cohort_rr": cohort_rr, "n_obs": int(len(panel))}
        cmp_rows.extend(compare_cells(period_rr, ANANTH_PERIOD, "period_rr", scope))
        cmp_rows.extend(compare_cells(cohort_rr, ANANTH_COHORT, "cohort_rr", scope))

    cmp_df = pd.DataFrame(cmp_rows)
    cmp_df.to_csv(OUTDIR / "comparison_table.csv", index=False)

    n_pass = int(cmp_df["pass"].sum())
    n_total = len(cmp_df)
    pass_rate = 100.0 * n_pass / n_total if n_total else 0.0
    if pass_rate >= 80:
        verdict = "CONFIRMED"
    elif pass_rate >= 50:
        verdict = "INCONCLUSIVE"
    else:
        verdict = "FAILED"

    memo = f"""# Ananth 2022 close-out test

**Verdict: {verdict}** — {n_pass}/{n_total} cells pass ({pass_rate:.1f}%).

Script: `notebooks/ananth2022_closeout_test.py`  
Outputs: `RECEIPTS/ananth2022_closeout_outputs/`

## Methodology (Ananth stated only)

- Filters: no residence/tabulation restrictions; GA≥{GA_MIN_WEEKS} wk; maternal age 11–49.
- Race: bridged-INCL-Hispanic throughout (FD `maternal_race_bridged` ≤2017; 2018–2020 via `race_hispanic_revised`+`maternal_race_recode6`; natality bridged ≤2019; 2020 via `maternal_race_ethnicity_5`+`maternal_race_detail` for Hispanic).
- APC: Poisson, offset log(LB+FD), natural cubic splines df=10 (age/period/cohort), Holford constraint on first two cohort basis terms, period ref 2020, cohort ref 1980.

## Totals check

| | HVS | Ananth |
|---|---:|---:|
| Stillbirths (≥{GA_MIN_WEEKS} wk) | {totals[f'fd_ge{GA_MIN_WEEKS}wk']:,} | {ANANTH_TOTALS['stillbirths']:,} |
| Live births | {totals['lb']:,} | {ANANTH_TOTALS['live_births']:,} |

## 2018–2020 reconstruction continuity

```
{recon.to_string(index=False)}
```

## Comparison summary

Failures by cell type:
```
{cmp_df[~cmp_df['pass']].groupby(['cell_type','race']).size().to_string() if (~cmp_df['pass']).any() else 'none'}
```

## Interpretation

"""
    if verdict == "CONFIRMED":
        memo += (
            "Ananth Table 4 is reproducible under his stated bridged-INCL-Hispanic methodology "
            "and broad inclusion filters. The prior 'correction-of-Ananth' framing compared different "
            "race definitions across 2014; it does not invalidate his published results. Paper 2 should "
            "be scoped as complementary (Hispanic disaggregation 2014+, 2021–2024 extension, open reproducibility)."
        )
    elif verdict == "INCONCLUSIVE":
        memo += (
            "Partial reproduction: some Table 4 cells match but others do not. Inspect `comparison_table.csv` "
            "for systematic patterns (likely 1980/1982 period extrapolation, spline extraction, or APC identifiability)."
        )
    else:
        memo += (
            "Substantial mismatch under stated methodology. Do not use bilateral-correction narrative. "
            "Review reconstruction diagnostics and whether spline/Holford implementation matches Ananth's software."
        )

    receipt_path = REPO_ROOT / "RECEIPTS" / f"ananth2022_closeout_test_ge{GA_MIN_WEEKS}wk_{ts[:19].replace(':', '-')}Z.md"
    receipt_path.write_text(memo)
    with (OUTDIR / "results.json").open("w") as f:
        json.dump(
            {"verdict": verdict, "n_pass": n_pass, "n_total": n_total, "models": model_summaries,
             "comparison": cmp_df.to_dict(orient="records"), "reconstruction": recon.to_dict(orient="records"),
             "totals": totals},
            f, indent=2, default=str,
        )

    print(cmp_df.to_string(index=False))
    print(f"\n{verdict}: {n_pass}/{n_total} pass")
    print(f"Wrote {receipt_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
