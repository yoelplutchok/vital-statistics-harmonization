# Ananth 2022 close-out — ≥20 wk sensitivity

**Verdict: FAILED** — 19/60 cells pass (31.7%). Up from 16/60 at the mistaken ≥24 run (filter bug left GA≥24 hardcoded).

Script: `notebooks/ananth2022_closeout_test.py` (default `ANANTH_GA_MIN_WEEKS=20`)  
Outputs: `RECEIPTS/ananth2022_closeout_outputs_ge20wk/`

## TL;DR

Switching GA from ≥24 to **≥20 wk** (everything else fixed: Ananth bridged-INCL-Hispanic race, broad filters, same APC splines) **restores Table 2 crude rates at 2020** (3/3 race columns within ±0.5/1,000). Period and cohort Table 4 cells remain largely off — cohort extraction still collapses toward 1.0. **GA threshold was the main blocker for crude rates, not race coding.**

## Crude rates (Table 2) — ≥20 wk vs ≥24 wk

| Cell | Ananth | HVS ≥24 (buggy run) | HVS ≥20 |
|------|-------:|--------------------:|--------:|
| 2020 Overall | 5.8 | 3.94 | **5.76** ✓ |
| 2020 White | 5.0 | 3.45 | **5.00** ✓ |
| 2020 Black | 10.1 | 7.10 | **10.49** ✓ |
| 1982 Overall (vs 1980) | 10.6 | 6.74 | 8.29 (still fails — PUF floor) |

## Period RR (selected)

| Year | Ananth Overall | HVS ≥20 |
|------|---------------:|--------:|
| 1980 | 2.17 | 1.80 |
| 2005 | 0.92 | 1.04 |
| 2015 | 1.03 | 1.04 ✓ |
| 2020 | 1.00 | 1.00 ✓ |

2020 White period cells largely track; Black 1980 period RR still low (1.51 vs 2.07).

## Totals (1982–2020, broad filters)

| | HVS ≥20 wk | Ananth |
|--|----------:|-------:|
| Fetal deaths | 1,020,470 | 710,832 |
| Live births | 153,590,744 | 157,192,032 |

HVS stillbirth count exceeds Ananth (broader inclusion / PUF years); LB count still ~2.3% low.

## Unchanged vs ≥24 run

- Cohort RR: still ~1.0 for most cells → APC spline reporting issue, not GA.
- Period RR: modest improvement, still below 80% pass rate overall.

## Implication

Ananth’s published **headline rates align with HVS at ≥20 wk** under his stated race semantics. Table 4 **APC** cells are not reproduced with this Python spline implementation; follow-up should target R `apc`/`mgcv` parity, not bilateral race correction.
