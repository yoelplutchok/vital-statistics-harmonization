# Pre-computed published tabulations (C8.22)

Top NVSR-cited cross-tabulations of the HVS harmonized microdata, pre-computed
so you can cite HVS figures **without loading the multi-GB parquets**. Every
cell is auto-derived by the deterministic builder
[`scripts/_build_published_tabulations.py`](../../scripts/_build_published_tabulations.py)
from the gate-verified derived parquets — re-running the builder reproduces
every CSV byte-identically.

## Canonical filter applied (every tabulation)

| Product | Canonical filter (applied on every side, incl. cross-product joins) |
|---|---|
| Natality | `residence_status != 4` (U.S. residents; ≡ `is_foreign_resident == False`) |
| Fetal death | `tabulation_flag == 2 AND residence_status != 4` (+ `version_flag == 'S'` for 1982–2002) — the NVSR-comparable ≥20-week subset |
| Linked birth–infant death | `residence_status != 4`; IMR is **unweighted** `infant_death`/`births` (the `compare_external_targets_v3_linked.py` definition) |

Each metric mirrors the exact definition of the canonical NVSR validator that
owns it (`natality/scripts/05_validate/compare_external_targets_v1.py`,
`compare_external_targets_v3_linked.py`,
`fetal_death/scripts/05_validate/validate_external_v2.py`); rate denominators
are the **known (non-null)** subset. Where a cell overlaps an NVSR-validated
target the `reconciliation` column reports the comparison; within-tolerance
differences are documented, never hidden.

## No state / sub-national geography

NCHS **suppresses all sub-national geography in the public-use natality,
fetal-death, and linked files**. There is therefore **no per-state (or county
/ region) tabulation** — it is structurally impossible from public-use data,
not an omission. The per-state slice of the original task spec is substituted
by the maternal-race and maternal-age stratifications below (both more highly
NVSR-cited). For state-level vital statistics use the NCHS Restricted Data
Center or CDC WONDER (see `docs/WORKED_EXAMPLE_FAQ.md` → "How do I get
state-level data?").

## Bridged-race discontinuity (read before using the `*_x_maternal_race` tabs)

`maternal_race_bridged` = {1 White, 2 Black, 3 AIAN, 4 Asian or Pacific
Islander}. NULL is surfaced as an explicit **"Not stated / not bridged"**
row (never dropped — every stratified breakdown sums back to the year total).
NCHS discontinued the bridged-race recode at different times per product:

- **Natality / linked**: populated through **2019**; **100% NULL from 2020**
  (use `maternal_race_ethnicity_5` for 2020+). 1990–2002 natality bridged race
  is an *approximate* crosswalk, not the official NCHS bridged-race recode.
- **Fetal death**: populated through **2017**; **100% NULL from 2018**.

So race-stratified fetal mortality is informative 1990–2017; race-stratified
IMR 2005–2019. Later years are present but fall into "Not stated / not
bridged".

## The 10 tabulations

| File | Rows | NVSR reconciliation |
|---|---|---|
| `natality_births_by_year.csv` | resident live births, 1968–2024 | `resident_births` v1 targets, 1990–2024 (pre-1990 derived; NVSR-benchmarking planned) |
| `natality_births_by_year_x_maternal_race.csv` | × bridged race + Not stated | H6 conserves to the by-year total |
| `natality_births_by_year_x_maternal_age.csv` | × NCHS age band + Not stated | H6 conserves to the by-year total |
| `natality_rates_lbw_preterm_singleton_by_year.csv` | LBW% / preterm% / singleton% (known denominator) | `lbw_rate_pct`, `preterm_rate_pct` v1 targets |
| `natality_rates_cesarean_multiple_by_year.csv` | cesarean% (era crosswalk) / twin/1000 / triplet+/100k | `cesarean_rate_pct`, `twin_rate_per_1000`, `triplet_plus_rate_per_100000` |
| `fetal_death_counts_by_year.csv` | ≥20-wk resident fetal deaths, 1982–2024 | `fetal_deaths_gte20wk_resident` (+ validator NVSR 57-08 / guide controls) |
| `fetal_mortality_rate_by_year.csv` | FMR /1000 (live births + fetal deaths), joint fetal+natality | `fetal_mortality_rate` targets, 1995–2024 |
| `fetal_mortality_rate_by_year_x_maternal_race.csv` | FMR × bridged race (both sides canonical-filtered) | H6 conserves the fetal numerator |
| `linked_imr_by_year.csv` | IMR / neonatal / postneonatal /1000, 2005–2023 | `imr_per_1000`, `neonatal_imr_per_1000`, `postneonatal_imr_per_1000` |
| `linked_imr_by_year_x_maternal_race.csv` | IMR × bridged race, 2005–2023 | H6 conserves to the by-year total |

The linked IMR tabs cover **2005–2023** (the unweighted, NVSR-reconcilable,
canonical-validator-owned surface). Pre-2005 cohort-linked IMR (1983–2004)
**is in the parquet** but its published-comparable computation needs the
cohort-specific RECWT weighting (1983–1984) + `link_segment` den/num ratio
(1983–1988) methodology — validated separately at C8.18 via
`natality/metadata/external_validation_targets_v3_linked.csv` and documented
in `natality/docs/COMPARABILITY.md` § "Pre-2005 cohort backward extension".
The permanent 1992–1994 NCHS-linkage gap applies to all linked tabs.

## Reproducing

```bash
uv run python scripts/_build_published_tabulations.py          # (re)build
uv run python scripts/_build_published_tabulations.py --check   # assert byte-identical
```
