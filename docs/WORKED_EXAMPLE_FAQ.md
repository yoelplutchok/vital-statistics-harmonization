# Worked-example FAQ (cross-product)

This file collects cross-product use-case questions — the ones that span more than one HVS product, or that require choosing between products. Single-product questions live in each subproject's own FAQ:

- Fetal-death-only: [`fetal_death/FAQ.md`](../fetal_death/FAQ.md)
- Natality + linked-only: [`natality/docs/FAQ.md`](../natality/docs/FAQ.md)

For the full mechanics of joint computation, see [`docs/JOINT_USE_GUIDE.md`](JOINT_USE_GUIDE.md). The notebooks under [`notebooks/`](../notebooks/) are runnable end-to-end against the shipped parquets.

---

## Computing rates that span products

### Q: How do I compute the perinatal mortality rate?

PMR = (fetal deaths at 28+ weeks gestation + infant deaths under 7 days) / (live births + fetal deaths at 28+ weeks) × 1000. It needs all three products at once: fetal-death parquet for the 28+ wk numerator component; linked birth–infant death parquet for the early-neonatal component; natality parquet for the live-birth denominator. Apply each product's canonical filter (`residence_status != 4` everywhere; `tabulation_flag == 2` additionally on fetal-death) before counting.

The full code is in [`docs/JOINT_USE_GUIDE.md` §128-172](JOINT_USE_GUIDE.md#worked-example-perinatal-mortality-rate-2022-three-product-joint), with caveats. The cell-by-cell version lives in [`notebooks/joint_use_demo.ipynb`](../notebooks/joint_use_demo.ipynb) Section C. NCHS does not publish a single 2022 PMR cell — the combined *Fetal and Perinatal Mortality* NVSR series ended after 2013 data — so the result is the product of HVS joint use rather than a reproduction of a published number. The sub-components match published cells (28+ wk fetal deaths within proportional-redistribution tolerance vs *NVSR 73-09*; early-neonatal cohort rate byte-exact vs the cohort-linked user-guide).

### Q: Is there a pre-joined "perinatal record" — can I link a fetal death to the same mother's later infant?

No. NCHS public-use files carry no maternal/household/pregnancy identifier and no sub-national geography, so a fetal death cannot be linked to the *same mother's* live birth or infant death at the record level — the expected unique-sibling match rate is **~0% (≤0.00118%, vs a 5% feasibility threshold)** in every year tested. This is a permanent disclosure-protection limit, not an HVS gap. The two perinatal analyses that public-use data *does* support are shipped: the aggregate **perinatal mortality rate** (the question above), and the **stillborn↔liveborn co-multiple** linkage (a multiple gestation with one stillbirth and a liveborn co-twin) in [`matched_multiples/`](../matched_multiples/). Full quantitative evidence, the four structural blockers, and the restricted-data (RDC / state vital records) path: [`docs/PERINATAL_RECORD_FEASIBILITY.md`](PERINATAL_RECORD_FEASIBILITY.md).

### Q: How do I compute the fetal mortality rate?

FMR = fetal deaths / (live births + fetal deaths) × 1000. Numerator from fetal-death; denominator from either natality (for stratified analyses; recompute from the parquet) or [`fetal_death/live_births_by_year.csv`](../fetal_death/live_births_by_year.csv) (unstratified, NVSR-as-published). Apply `tabulation_flag == 2 AND residence_status != 4` to the fetal-death side; `residence_status != 4` to the natality side.

For a race-stratified worked example, see [`docs/JOINT_USE_GUIDE.md` §90-126](JOINT_USE_GUIDE.md#worked-example-fetal-mortality-rate-by-maternal-race-2017) (2017 bridged-race demo) or [`notebooks/joint_use_demo.ipynb`](../notebooks/joint_use_demo.ipynb) Section B (2022 single-race + Hispanic, validated against *NVSR 73-09* Table A 7/7 cells). For a cross-era V3a/V3b-era race-stratified time series, see [`notebooks/cross_race_fetal_mortality.ipynb`](../notebooks/cross_race_fetal_mortality.ipynb).

### Q: How do I compute the infant mortality rate?

IMR is a single-product computation off the linked file: `linked["infant_death"] == True` per 1,000 `linked` records (with `residence_status != 4`). The maternal-age-stratified version is the headline worked example in [`notebooks/maternal_age_stratified_imr.ipynb`](../notebooks/maternal_age_stratified_imr.ipynb), validated against *NVSR* per-stratum cells.

Note: IMR is sometimes presented as `infant deaths / live births × 1000`, where the live-birth denominator comes from natality. The linked-file approach (numerator and denominator from the same file) is the canonical computation because it preserves the cohort-vs-period distinction; mixing natality live births with linked infant deaths recovers the same number within rounding but doesn't gain anything for routine IMR work.

### Q: How do I compute the preterm birth rate over time?

[`notebooks/preterm_outcomes_time_series.ipynb`](../notebooks/preterm_outcomes_time_series.ipynb) is the worked example. Use natality's `preterm_lt37` (and `very_preterm_lt32` for the severe-preterm rate). The 2014 obstetric-estimate-vs-LMP gestational-age methodology break is the headline caveat; the notebook documents which years are comparable for which gestational-age definition.

---

## Filters, products, and use-case mapping

### Q: What is the right canonical filter for my analysis?

| Product | Filter | What it does |
|---|---|---|
| Natality | `residence_status != 4` | Drops the ~0.5% of records from non-U.S.-resident births |
| Linked birth–infant death | `residence_status != 4` | Same |
| Fetal death | `tabulation_flag == 2 AND residence_status != 4` | Restricts to records meeting NCHS's gestational-age + birth-weight tabulation rule (the population NVSR rates are computed on) |

These filters reproduce the populations NCHS computes published rates on. Skipping them produces systematically biased totals (5–10% off the published cells). Apply them before any rate computation, every time. The expanded discussion is in [`docs/JOINT_USE_GUIDE.md` §43-55](JOINT_USE_GUIDE.md#canonical-analytic-filters).

### Q: Which product should I use for [X]?

| Use case | Primary product | Secondary product |
|---|---|---|
| Live-birth counts; maternal demographics; pregnancy/birth conditions | Natality | Linked (if you also need infant outcomes) |
| Infant mortality rate; cause-of-infant-death; cohort vs period mortality | Linked birth–infant death | Natality (for an alternative denominator) |
| Fetal mortality rate; stillbirth analyses; cause of fetal death (2014+) | Fetal death | Natality (for the live-birth denominator) |
| Perinatal mortality rate; stillbirth-vs-infant-death joint analyses | All three (joint use) | — |
| Pre-2005 infant mortality | (not available in HVS) | Pre-2005 linked-cohort exists at NCHS but is not yet harmonized; *NVSR* tables remain the source. |
| State-stratified anything | (not available; see geography Q below) | — |

### Q: Which column should I use — the one in `*_harmonized.parquet` or the one in `*_harmonized_derived.parquet`?

The derived parquet is a superset of the harmonized parquet: it contains every harmonized column plus the derived indicators (`low_birthweight`, `preterm_lt37`, etc.). For analysis, always read from the derived parquet. The harmonized parquet is an intermediate kept on disk for pipeline-stage isolation and re-derive determinism.

---

## Geography, race, and known breaks

### Q: How do I get state-level data?

You can't, from the public-use files. NCHS suppresses state-of-residence and state-of-occurrence geography in all three public-use products. The natality FAQ and the C8.9 PRE-FLIGHT both confirm this against the on-disk columns and against the NCHS data-access documentation.

If you need state-level vital statistics, the options are:

- **NCHS Research Data Center (RDC).** Restricted-use files with full geography. Requires a research proposal and an in-person or virtual RDC session. Not within HVS pre-submission scope.
- **CDC WONDER.** Pre-tabulated state × demographic cells with NCHS-applied disclosure protection (suppression of small cells). Useful for descriptive work; the underlying microdata is not user-accessible.
- **Census-region or Census-division derivation.** HVS does not currently ship a derived `region` column. A future task could add one by mapping state-of-residence-recoded variables that ARE in some products (e.g., `restatus`-derived foreign-vs-domestic) into a coarser geography, but the resulting strata would not be state-level.

For more on the geography limitation, see [`natality/docs/FAQ.md` "Is geography included?"](../natality/docs/FAQ.md) and the C8.9 [ 2026-05-13T10:00:00Z](../) entry.

### Q: What is the bridged-race era, and when does it end?

NCHS published a 4-category bridged-race recode (White / Black / AIAN / Asian-or-PI) for natality through 2019 and for fetal-death through 2017. Starting 2020 (natality) and 2018 (fetal-death), the bridged column is null in the public-use files. The replacement is the single-race + Hispanic representation: `maternal_race_ethnicity_5` (natality) and `race_hispanic_revised` (fetal-death). The two representations are not interchangeable — bridging combines multiple-race respondents into a single category by an NCHS-defined algorithm, while single-race uses the principal-race response. See [`docs/COMPARABILITY.md`](COMPARABILITY.md) "Bilateral race-coding methodology" for the cross-product treatment.

Joint race-stratified analyses crossing the bridged-era boundary need explicit handling. Two options: split the time series at the boundary and report each era separately; or use single-race + Hispanic for the whole span (with a noted methodology break at 2018/2020). Neither approach lets you compute a continuous bridged-race trend through 2024.

### Q: How do I handle the V3a/V3b race-coding caveats in the 1982-1991 fetal-death years?

The 1985-revision (1982-1988) and 1989-revision-early (1989-1991) fetal-death files use a 1-digit MRACE code instead of the multi-digit MRACE we get in 1992+. HVS's V3a/V3b extension maps 1-digit MRACE to the 4-category bridged race for time-series continuity, but two source codes have no bridged equivalent: code 7 (Other nonwhite) and code 9 (Not stated / Unknown). Both are mapped to **null** rather than forced into one of the four categories.

The consequence: for 1982-1991, ~10-15% of records have null `maternal_race_bridged`. Race-stratified rates for those years should be computed on the non-null subset, with the null proportion documented. The worked example in [`notebooks/cross_race_fetal_mortality.ipynb`](../notebooks/cross_race_fetal_mortality.ipynb) cells 8-12 demonstrates the pattern; the V3a/V3b [ 2026-05-12T14:30:00Z / 2026-05-12T18:30:00Z](../) entries explain the mapping choice.

### Q: How do I handle the 2003 certificate-revision break?

The 2003 certificate adds revised representations for many fields (gestational age, education, medical risk factors, etc.) but legacy and revised codes coexist during the 2003-2013 transition because states adopted the revision on a staggered schedule. Two general rules:

- Use the **`*_revised`** column for analyses spanning 2003-2024 (revised representation; null pre-2003).
- Use the **`*_unrevised`** column for analyses spanning 1990-2002 (legacy representation; null post-2003).
- A unified analysis across the 1989/2003 boundary is generally not supported because the codings differ in ways NCHS deliberately did not bridge.

The per-column comparability classification (`within_era` vs `cross_era`) is in each subproject's [`COMPARABILITY.md`](../fetal_death/COMPARABILITY.md). The cross-product synthesis is in [`docs/COMPARABILITY.md`](COMPARABILITY.md).

---

## Loading the data in R, Stata, SAS, or SQL

### Q: I don't use Python — how do I load the parquet in R, Stata, SAS, or plain SQL?

- **R:** per-product `quickstart.R` (`fetal_death/quickstart.R`, `natality/quickstart.R`, `natality/quickstart_linked.R`) using `arrow`.
- **SQL (no Python):** [`views.sql`](../views.sql) at the monorepo root defines DuckDB canonical-filter views over the parquets.
- **Stata / SAS:** see [`STATA_SAS_QUICKSTART.md`](../STATA_SAS_QUICKSTART.md). Stata/SAS base releases cannot read Parquet (native Stata `import parquet` is StataNow-only; SAS 9.4 has none — SAS Viya uses an ORC/Parquet `LIBNAME` engine), so the version-proof path is Parquet → CSV once (via `views.sql` + DuckDB, or `quickstart.py` + pandas) then `import delimited` / `PROC IMPORT DBMS=CSV`.

The full mechanics for all four languages are in [`docs/JOINT_USE_GUIDE.md`](JOINT_USE_GUIDE.md) "Cross-language access: R, DuckDB, Stata, SAS".

---

## Citing this resource

### Q: Is there a pre-computed table I can cite without loading the parquet?

Yes. [`csv/published_tabulations/`](../csv/published_tabulations/) ships ten plain-CSV cross-tabulations of the most NVSR-cited HVS figures — resident live births, fetal-death counts, fetal-mortality rate, and infant-mortality rate, each by year and (where the data supports it) by bridged race or maternal-age band. Every cell is auto-derived under the product's canonical filter by the deterministic builder `scripts/_build_published_tabulations.py`, and each NVSR-overlapping cell carries a `reconciliation` column reporting the comparison to its validated NVSR target (within-tolerance differences are shown, not hidden). Open the CSV, read the figure, cite it — no Python required. Start with [`csv/published_tabulations/README.md`](../csv/published_tabulations/README.md) for the canonical filter and the bridged-race discontinuity note. There is **no per-state** table (NCHS suppresses sub-national geography in public-use files — see "How do I get state-level data?" above); the per-state slice is substituted by the race and maternal-age stratifications.

### Q: How do I cite HVS?

The citation metadata is in [`CITATION.cff`](../CITATION.cff). Until the unified HVS Zenodo concept DOI lands at Phase D (post-Phase-C), cite the two existing product DOIs:

- Plutchok Y. *Harmonized U.S. Natality and Linked Birth–Infant Death Microdata*. Zenodo. https://doi.org/10.5281/zenodo.19363074
- Plutchok Y. *Harmonized U.S. Fetal Death Microdata, 1992–2022*. Zenodo. https://doi.org/10.5281/zenodo.20031571

The forthcoming Data Resource Profile manuscript will provide the unified citation form.
