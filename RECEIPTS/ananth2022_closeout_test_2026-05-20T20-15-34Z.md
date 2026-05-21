# Ananth 2022 close-out test

**Verdict: FAILED** — 9/60 cells pass (15.0%).

Script: `notebooks/ananth2022_closeout_test.py`  
Outputs: `RECEIPTS/ananth2022_closeout_outputs/`

## Methodology (Ananth stated only)

- Filters: no residence/tabulation restrictions; GA≥24; maternal age 11–49.
- Race: bridged-INCL-Hispanic throughout (FD `maternal_race_bridged` ≤2017; 2018–2020 via `race_hispanic_revised`+`maternal_race_recode6`; natality bridged ≤2019; 2020 via `maternal_race_ethnicity_5`+`maternal_race_detail` for Hispanic).
- APC: Poisson, offset log(LB+FD), natural cubic splines df=10 (age/period/cohort), Holford constraint on first two cohort basis terms, period ref 2020, cohort ref 1980.

## Totals check

| | HVS | Ananth |
|---|---:|---:|
| Stillbirths (≥24 wk) | 742,411 | 710,832 |
| Live births | 153,590,744 | 157,192,032 |

## 2018–2020 reconstruction continuity

```
side  race   y0   y1  count_y0  count_y1  pct_change
  fd White 2017 2018     10036      9573       -4.61
  fd White 2019 2020      9187      9113       -0.81
  fd Black 2017 2018      4309      4322        0.30
  fd Black 2019 2020      4204      4145       -1.40
 nat White 2017 2018   2865462   2842750       -0.79
 nat White 2019 2020   2798519   2630815       -5.99
 nat Black 2017 2018    658603    634033       -3.73
 nat Black 2019 2020    635165    580022       -8.68
```

## Comparison summary

Failures by cell type:
```
cell_type  race   
cohort_rr  Black      8
           Overall    8
           White      8
crude      Black      2
           Overall    2
           White      2
period_rr  Black      8
           Overall    6
           White      7
```

## Interpretation

Substantial mismatch under stated methodology. Do not use bilateral-correction narrative. Review reconstruction diagnostics and whether spline/Holford implementation matches Ananth's software.