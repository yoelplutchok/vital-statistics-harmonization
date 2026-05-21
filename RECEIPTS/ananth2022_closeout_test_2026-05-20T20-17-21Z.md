# Ananth 2022 close-out test

**Verdict: FAILED** — 16/60 cells pass (26.7%). Well below the 80% CONFIRMED threshold.

Script: `notebooks/ananth2022_closeout_test.py`  
Outputs: `RECEIPTS/ananth2022_closeout_outputs/` (`comparison_table.csv`, `results.json`)

## TL;DR

Under Ananth’s **stated** bridged-INCL-Hispanic race coding (held constant 1982–2020) and his **inferred broad filters** (no residence/tabulation restrictions, GA≥24, age 11–49), HVS **does not** reproduce Table 4 within ±0.03 for most cells. The prior “Paper 2 correction-of-Ananth” story remains **invalid as a critique of Ananth’s analysis** — it compared NH-only vs bridged-INCL-Hispanic semantics — but this close-out also shows **full Table 4 reproduction is not achieved** on public HVS PUF alone with the spec as implemented (crude rates, cohort splines, and/or GA definition are the main gaps).

## Methodology (single scheme — Ananth only)

| Component | Implementation |
|-----------|----------------|
| Filters | No `residence_status` / `tabulation_flag`; GA≥24 (drop 99); age 11–49; V2.1 age via `maternal_age_recode14` |
| Race | Bridged-INCL-Hispanic: `maternal_race_bridged` through 2017 (FD) / 2019 (nat); 2018–20 FD via `race_hispanic_revised` + `maternal_race_recode6` (100% agreement vs bridged in 2017); 2020 nat via `maternal_race_ethnicity_5` + `maternal_race_detail` for Hispanic |
| APC | Poisson, offset log(LB+FD); `cr(·, df=10)` splines on age / period / cohort; Holford constraint (first two cohort basis terms equal); period ref 2020, cohort ref 1980 |

## Totals vs Ananth (1982–2020)

| | HVS | Ananth (paper) |
|---|---:|---:|
| Stillbirths (≥24 wk) | 742,411 | 710,832 |
| Live births | 153,590,744 | 157,192,032 |

HVS counts **more** fetal deaths but **fewer** live births (−2.3%), producing systematically **lower** crude rates than Table 2.

## 2018–2020 reconstruction diagnostics

| Transition | Side | Δ count |
|------------|------|--------:|
| 2017→2018 | FD White | −4.6% |
| 2017→2018 | FD Black | +0.3% |
| 2019→2020 | Nat White LB | **−6.0%** |
| 2019→2020 | Nat Black LB | **−8.7%** |

FD reconstruction is smooth; **2020 natality** shows a large LB drop when switching from `maternal_race_bridged` to `eth5+detail` reconstruction — flag this boundary in any follow-up.

## What passed (16/60)

- **Reference cells** (by construction): period 2020 and cohort 1980 for all three race columns (6 cells).
- **Period RR** (non-ref): 1980 Overall (2.19 vs 2.17); 2015 Overall; 2015 White — close but most other period years fail by 0.06–0.34.
- **Cohort RR**: Many HVS values collapsed toward **1.00** (spline + extraction issue); a few near-ref cohorts pass by being within tolerance of 1.0.

## What failed systematically

1. **Crude rates (0/6 pass):** 2020 Overall 3.94 vs 5.8; Black 7.10 vs 10.1; White 3.45 vs 5.0. Prior headline replication showed Ananth’s 2020 cells match HVS at **≥20 wk**, not ≥24 wk — Table 2 likely reflects a different GA operationalization than the paper’s inferred ≥24 filter.
2. **Period RR (~3/27 non-ref pass):** Shape is directionally similar (high 1980s, dip mid-2000s) but magnitudes off, especially Black 1980 (1.73 vs 2.07).
3. **Cohort RR (~4/27 meaningful pass):** Gradient (youngest cohorts elevated) **not recovered**; many HVS cohort RRs ≈ 1.0 → APC spline marginalization / software mismatch vs Ananth’s R `apc` pipeline is the prime suspect.

## Implications for Paper 2 framing

| Framing | Status after close-out |
|---------|------------------------|
| “Correct Ananth’s undisclosed 2014 race break” (bilateral) | **Dead** — Ananth holds bridged-INCL-Hispanic constant; prior bite was a cross-definition comparison |
| “Replicate Ananth Table 4 exactly on HVS PUF” | **Not achieved** (FAILED) |
| “Complementary extension” (2014+ Hispanic disaggregation, 2021–24, open code) | **Still viable** |

## Recommended follow-ups (hypotheses — not run here)

1. **GA threshold:** Re-run crude + APC at ≥20 wk only (headline check from prior replication) while holding Ananth race coding — tests whether Table 2 GA definition is the crude-rate blocker.
2. **APC software:** Replicate Table 4 in R `apc`/`mgcv` with the same spline spec (10 knots, Holford) — Python patsy + constrained GLM may not match published extraction.
3. **2020 denominator:** Investigate natality 2020 reconstruction loss (−6–9% LB) vs keeping bridged through 2019 only for a sensitivity.
