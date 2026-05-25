# Receipt: notebook-portable-paths (D-prep.9 re-verify)

## 2026-05-25T02:30:00Z

### What was done

- **PRE-FLIGHT:** Four gate parquet SHA prefixes byte-exact (`38e2cecb…`, `185c071e…`, `acb5c48a…`, `f630d8cf…`); `_paths.py` resolves all inputs on build host.
- **Re-executed** all eight `notebooks/_build_*.py` builders on build host (post–RD.4 / C8.18 envelope).
- **Builder fixes** (notebook source only; no canonical parquet/schema mutation):
  - `_build_maternal_age_stratified_imr.py` — `infant_death` numeric coercion; cohort-era IMR validation scoped to 2015 + 2020–2023 (excludes C8.18 pre-2005 CSV rows).
  - `_build_education_gradient.py` — year-filtered / year-looped natality reads; linked 2022-only slice (OOM fix).
  - `_build_cross_race_fetal_mortality.py` — natality 2022 filter read; per-year 1990–2024 aggregation loop (OOM fix).
  - `_build_preterm_outcomes_time_series.py` — pyarrow year filters (natality 1990–2023; linked 2005–2023).

### Verify results

| Notebook | Execute |
|---|---|
| `joint_use_demo` | PASS (21/21 code cells with outputs) |
| `paper_companion` | PASS (22/23) |
| `matched_multiples_demo` | PASS (9/9) |
| `maternal_age_stratified_imr` | PASS (12/13) |
| `education_gradient` | PASS (9/9) |
| `state_reporting_quirks` | PASS (8/8) |
| `cross_race_fetal_mortality` | PASS (15/16) |
| `preterm_outcomes_time_series` | PASS (13/14) |

- SMOKE: zero `/Users/...` literals in `notebooks/*.ipynb` and `natality/notebooks/quickstart.ipynb`.
- Four gate parquet SHAs unchanged post-run.

### Self-check (§10)

What VERIFY might not catch: (a) a notebook whose last code cell is intentionally output-free looks like “missing execution” in a naive output count; (b) year-looped builder logic could diverge from whole-file `groupby` if a future pandas/pyarrow filter semantics change; (c) `paper_companion` still cites `draft_v2_hmd_styled.md` claims — manuscript not re-audited this session (D.4 gated). Residual: emitted cells embed `~/Desktop/...` fallbacks inside `_gate_parquet()` strings — portable on this machine, not path-agnostic for arbitrary clones (same as 2026-05-20 receipt).

### Forward-looking HALTs for next session

1. §15.F closure: explicit human deferral of latest-year refresh and/or RD.1b Phase C, or run those — then set STATUS “Next planned task” = **D.4**.
2. If any notebook is edited outside `_build_*.py`, re-run the matching builder before Zenodo/public push.
3. Pre-upload: re-hash four gate parquets on exact bytes in the deposit zip (KICKOFF gate SHA re-hash).
