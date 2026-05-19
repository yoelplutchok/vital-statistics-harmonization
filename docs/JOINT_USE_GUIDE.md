# Joint-use guide: computing rates that need numerator and denominator

The three U.S. Harmonized Vital Statistics products are designed to be used jointly. Several headline rates in U.S. perinatal epidemiology cannot be computed from any single product alone:

- **Fetal mortality rate** = fetal deaths / (live births + fetal deaths)
- **Perinatal mortality rate** = (fetal deaths + early neonatal deaths) / (live births + fetal deaths)
- **Neonatal mortality rate** = neonatal deaths / live births
- **Infant mortality rate** = infant deaths / live births

The first two require the fetal-death numerator and the natality denominator. The third and fourth require the linked-file numerator and the natality denominator. All four require the demographic stratification on numerator and denominator to align exactly, otherwise the resulting rate is biased.

This guide describes the canonical join keys, aligned strata, analytic filters, and the convenience denominator file that ships in the fetal-death deposit.

## Canonical join-key column names (read carefully)

The two shipped product schemas use **different column names** for the same five join concepts. natality v2.7.0 and fetal-death v2.0.0 are independently versioned releases that adopted different naming conventions at the time of their respective deposits. Joint-use code reconciles the names at read-time via [`shared/helpers/canonical_join_keys.py`](../shared/helpers/canonical_join_keys.py); a future natality v2.8 rename to adopt the fetal-death names natively is a planned plan-update.

| Concept | natality v2.7.0 column | fetal-death v2.0.0 column | Canonical (joint-use) name |
|---|---|---|---|
| Event year | `year` (int16, 1990–2024) | `data_year` (int32, 1992–2002 + 2005–2022) | **`data_year`** |
| Maternal age (single year) | `maternal_age` (10–54) | `maternal_age` (10–54; 99 = Unknown sentinel) | **`maternal_age`** |
| 4-category bridged race | `maternal_race_bridged4` (int8, 1–4; **null 2020–2024** — NCHS dropped MBRACE) | `maternal_race_bridged` (int, 1–4; **null 2018–2022**) | **`maternal_race_bridged`** |
| Hispanic origin recode | `maternal_hispanic_origin` (int8, 0\|1\|2\|3\|4\|5\|9) | `hispanic_origin` (int, 0–9) | **`hispanic_origin`** |
| Residence status | `restatus` (int8, 1\|2\|3\|4) | `residence_status` (int, 1–4) | **`residence_status`** |

The helper exposes one rename function:

```python
from shared.helpers.canonical_join_keys import to_canonical_natality

natality_df = pd.read_parquet("natality_v2_harmonized_derived.parquet")
joint_view = to_canonical_natality(natality_df)
# joint_view now has columns data_year, maternal_age, maternal_race_bridged,
# hispanic_origin, residence_status (plus the rest of the natality schema).
```

## Joint-coverage years and the bridged-race gap

Natality covers 1990–2024 (35 years); fetal-death covers 1992–2022 with 2003 and 2004 deferred (29 years). Joint coverage is the intersection: **1992–2002 + 2005–2022 = 29 years**.

For the 4-category bridged race, joint coverage shrinks further because both products have null years from NCHS source changes (natality 2020+; fetal-death 2018+). **Bridged race is jointly available for 1992–2002 + 2005–2017 (24 years).** For 2018–2022, joint stratified-by-race rate computation is not currently supported via `maternal_race_bridged`. Closing this gap (via `maternal_race_ethnicity_5` in natality joined to `race_hispanic_revised` in fetal-death, with comparability verification) is future work.

## Canonical analytic filters

Each product has one filter that reproduces the population on which NCHS computes its published rates. **These filters MUST be applied before computing any rate** if the result is to be comparable to published NVSR figures.

| Product | Filter | Rationale |
|---|---|---|
| Natality | `restatus != 4` (int8 in parquet; renamed to `residence_status` by the helper) | U.S. residents only |
| Linked birth–infant death | `restatus != 4` (int8 in parquet; renamed to `residence_status` by the helper) | U.S. residents only |
| Fetal death | `tabulation_flag == 2 AND residence_status != 4` (both Int8 in v2.1.0 parquet) | NVSR-comparable subset: gestational age and birth-weight criteria meet NCHS's tabulation rule |

Applying the filter is the difference between reproducing NCHS's published per-year rates exactly and producing systematically biased counts.

**Dtype reconciliation (fetal-death v2.1.0).** The v2.1.0 `fetal_death_derived.parquet` stores `tabulation_flag` (Int8), `residence_status` (Int8), `maternal_age` (Int16), `maternal_race_bridged` (Int8), and `hispanic_origin` (Int8) as nullable integer dtypes, matching `fetal_death/harmonized_schema.csv` declarations and aligning with the natality v2.7.0 dtype convention. Use int literals on both sides (`tabulation_flag == 2`, `residence_status != 4`). For 2003–2004 transition records, `maternal_age` is null (the public-use file ships only the 41/14/9-category recodes); use `maternal_age_recode14` for age-stratified analyses spanning those two years.

## Convenience denominators: pick the right file

For unstratified rates → [`fetal_death/live_births_by_year.csv`](../fetal_death/live_births_by_year.csv). Lightweight, NVSR-as-published, 26 years (1995–2002 + 2005–2022). Use when you do not need demographic strata.

For stratified rates → [`fetal_death/stratified_denominators.csv`](../fetal_death/stratified_denominators.csv) (shipped in v2.1 of the joint-use layer, built by [`shared/helpers/build_stratified_denominators.py`](../shared/helpers/build_stratified_denominators.py)). Long format, one row per (`data_year`, `maternal_age_band`, `maternal_race_bridged`, `hispanic_origin`) cell with a `live_births` column. 4,906 cells across 29 joint-coverage years.

Schema:

| Column | Type | Domain |
|---|---|---|
| `data_year` | int | 1992–2002, 2005–2022 (29 years) |
| `maternal_age_band` | str | `<20`, `20-24`, `25-29`, `30-34`, `35-39`, `40+`; null when single-year age is the NCHS sentinel 99 |
| `maternal_race_bridged` | int (nullable) | 1=White, 2=Black, 3=AIAN, 4=Asian/PI; **null for 2018–2022** (NCHS source) |
| `hispanic_origin` | int | 0=non-Hispanic, 1=Mexican, 2=PR, 3=Cuban, 4=Central/South American, 5=Other Hispanic, 9=Unknown |
| `live_births` | int | Resident live births (`residence_status != 4`) in that stratum-year |

### NCHS-series note (microdata vs NVSR-as-published)

The stratified denominator is derived from the natality v2.7.0 microdata under `residence_status != 4`. Per-year totals match the CDC residence series (`e6fc-ccez`) that natality validates against byte-exact (29/29 years). For 2000–2002 and 2005–2006, those microdata totals differ from `live_births_by_year.csv`'s NVSR 57-08 / 73-09 figures by 38–224 records per year (<0.006%), because NCHS post-release re-tabulations adjust some published totals slightly. The stratified file is internally consistent (sum across strata = year total), which is the property that matters for unbiased rate computation; the two NCHS series differ by less than rounding noise at the rate level.

| Year | Stratified total (microdata) | `live_births_by_year.csv` (NVSR) | Diff |
|---|---|---|---|
| 1995–1999, 2007–2022 | identical | identical | 0 |
| 2000 | 4,058,814 | 4,058,882 | +68 |
| 2001 | 4,025,933 | 4,026,036 | +103 |
| 2002 | 4,021,726 | 4,021,825 | +99 |
| 2005 | 4,138,349 | 4,138,573 | +224 |
| 2006 | 4,265,555 | 4,265,593 | +38 |

## Cross-product coverage timeline

Each product covers a different range of years, with three certificate-revision / NCHS-reformat boundaries (1989, 2003, 2014, 2018). The cross-product timeline figure shipped at [`figures/fig1_coverage_timeline.pdf`](../figures/fig1_coverage_timeline.pdf) (regenerable via [`shared/helpers/build_timeline_figure.py`](../shared/helpers/build_timeline_figure.py)) visualizes each product's era-banded coverage. Joint analyses spanning a revision boundary must respect the era-comparability classifications in each subproject's `COMPARABILITY.md`.

## Worked example: fetal mortality rate by maternal race, 2017

```python
import pandas as pd
from shared.helpers.canonical_join_keys import to_canonical_natality

# Numerator: NVSR-comparable fetal deaths, 2017, by maternal race
# (fetal-death v2.1.0 stores tabulation_flag and residence_status as Int8; see dtype note above)
fd = pd.read_parquet("fetal_death/fetal_death_derived.parquet")
fd_2017 = fd[
    (fd["data_year"] == 2017)
    & (fd["tabulation_flag"] == 2)
    & (fd["residence_status"] != 4)
]
fd_by_race = fd_2017.groupby("maternal_race_bridged", dropna=False).size()

# Denominator option A — load from the stratified denominator file (~6,000 rows):
denom = pd.read_csv("fetal_death/stratified_denominators.csv")
births_by_race = (
    denom[denom["data_year"] == 2017]
    .groupby("maternal_race_bridged", dropna=False)["live_births"]
    .sum()
)

# Denominator option B — recompute from the natality parquet (~138.8M rows):
# (natality v2.7.0 stores residence_status/restatus as int8; int literals)
# nat = pd.read_parquet("natality_v2_harmonized_derived.parquet")
# nat = to_canonical_natality(nat)
# nat_2017 = nat[(nat["data_year"] == 2017) & (nat["residence_status"] != 4)]
# births_by_race = nat_2017.groupby("maternal_race_bridged", dropna=False).size()

# Fetal mortality rate per 1,000 (live births + fetal deaths)
fmr = 1000 * fd_by_race / (births_by_race + fd_by_race)
print(fmr)
```

For 2018-onward the bridged-race column is null in fetal-death (and 2020-onward in natality). Race-stratified joint analyses on 2018+ should use single-race + Hispanic origin (`race_hispanic_revised` in fetal-death, `maternal_race_ethnicity_5` + `maternal_race_detail` in natality) — see Section B of `notebooks/joint_use_demo.ipynb` for a 2022 worked example validated against *NVSR 73-09* Table A (7/7 rate cells PASS within rounding).

## Worked example: perinatal mortality rate, 2022 (three-product joint)

The perinatal mortality rate is the headline cross-product computation that requires all three HVS products simultaneously:

$$\text{PMR} = \frac{\text{FD}_{\geq 28\,\text{wk}} + \text{ENN}_{<7\,\text{d}}}{\text{LB} + \text{FD}_{\geq 28\,\text{wk}}} \times 1000$$

```python
import pandas as pd

# Numerator part 1: fetal deaths at 28+ wk gestation, 2022 (resident, NVSR-comparable)
fd = pd.read_parquet("fetal_death/fetal_death_derived.parquet")
fd_2022 = fd[
    (fd["data_year"] == 2022)
    & (fd["tabulation_flag"] == 2)
    & (fd["residence_status"] != 4)
].copy()
fd_2022["ga"] = pd.to_numeric(fd_2022["gestational_age_combined"], errors="coerce")
fd_2022["ga"] = fd_2022["ga"].where((fd_2022["ga"] >= 20) & (fd_2022["ga"] <= 46), pd.NA)
fd_28plus = int((fd_2022["ga"] >= 28).sum())          # observed 28+ wk

# Numerator part 2: early-neonatal deaths (<7 days) from cohort linked-file, 2022
linked = pd.read_parquet("natality/natality_v3_linked_harmonized_derived.parquet")
linked_2022 = linked[(linked["data_year"] == 2022) & (linked["residence_status"] != 4)]
n_enn = int(((linked_2022["infant_death"] == True) & (linked_2022["age_at_death_days"] < 7)).sum())

# Denominator: live births, 2022 (resident)
nat = pd.read_parquet("natality/natality_v2_harmonized_derived.parquet", columns=["data_year", "residence_status"])
n_lb = int(((nat["data_year"] == 2022) & (nat["residence_status"] != 4)).sum())

pmr = 1000 * (fd_28plus + n_enn) / (n_lb + fd_28plus)
print(f"2022 perinatal mortality rate: {pmr:.2f} per 1,000")
```

**Caveats and validations** (see `notebooks/joint_use_demo.ipynb` Section C for the cell-by-cell version):

- **No single NVSR cell publishes the 2022 perinatal mortality rate.** NCHS's combined *Fetal and Perinatal Mortality* series ended after 2013 data; for 2022, fetal mortality (*NVSR 73-09*) and infant mortality (*NVSR 73-05*) are published separately. The perinatal rate is *constructed* by joint use of all three HVS products.
- **28+ wk fetal-death sub-component** matches *NVSR 73-09* Table 1 (2022 = 9,956 published) only after proportional redistribution of records with unknown gestational age. Our parquet stores observed gestational age; the observed 28+ wk count is approximately 5% higher than the redistributed cell. Either is valid; document which methodology your analysis uses.
- **Early-neonatal (<7 days) sub-component** uses our *cohort*-linked file. *NVSR 73-05* uses the *period*-linked file; the two differ by ~2% by design (the period file includes deaths from prior-year births; the cohort file includes deaths in the year after birth). Our cohort counts match the cohort linked-file user-guide byte-exact (validated in `natality/metadata/external_validation_targets_v3_linked.csv`).
- **Live births** match both *NVSR 73-09* and *NVSR 73-05* byte-exact at the resident-filter (3,667,758 for 2022).

The cross-product validation notebook reproduces:
- **Section A**: 8/8 cells of *NVSR 73-09* Table 4 (2022 age-band fetal mortality) byte-exact.
- **Section B**: 7/7 cells of *NVSR 73-09* Table A (2022 single-race + Hispanic fetal mortality) within rounding.
- **Section B-legacy**: 2017 bridged-race joint-use machinery (no NVSR cell — no NCHS *Fetal Mortality 2017* report exists).
- **Section C**: 2022 perinatal mortality rate joint computation, sub-components validated individually.

> **Perinatal *rate* vs perinatal *record*.** The computation above is the aggregate perinatal mortality **rate** (stratum-level counts; no record linkage). A record-*level* "perinatal record" — one infant row with its same-mother fetal-death sibling joined on — is **not constructible from public-use NCHS data** (no maternal/household identifier, no sub-national geography). See [`docs/PERINATAL_RECORD_FEASIBILITY.md`](PERINATAL_RECORD_FEASIBILITY.md) for the quantitative evidence and the two perinatal analyses HVS *does* support (this rate; and the stillborn↔liveborn co-multiple linkage shipped as `matched_multiples/`).

## Cross-language access: R and DuckDB

Beyond the Python pattern shown above, HVS ships two additional access paths:

### R quickstart

Three R scripts mirror the Python `quickstart.py` for each product. Requires R packages `arrow` + `dplyr`.

- [`fetal_death/quickstart.R`](../fetal_death/quickstart.R) — uses `arrow::read_parquet()` (the 2.4M-row fetal-death parquet fits comfortably in memory).
- [`natality/quickstart.R`](../natality/quickstart.R) — uses `arrow::open_dataset()` because the 138.8M-row natality parquet exceeds R's default 16 GB memory limit; dplyr verbs are pushed down to Arrow and only the aggregated result is materialized.
- [`natality/quickstart_linked.R`](../natality/quickstart_linked.R) — same `open_dataset()` pattern for the 74.9M-row linked file; demonstrates per-year IMR computation and cause-of-death distribution.

Usage:

```bash
Rscript fetal_death/quickstart.R path/to/fetal_death_derived.parquet
Rscript natality/quickstart.R    path/to/natality_v2_harmonized_derived.parquet
Rscript natality/quickstart_linked.R path/to/natality_v3_linked_harmonized_derived.parquet
```

### DuckDB views

[`views.sql`](../views.sql) at the monorepo root defines four DuckDB views over the parquets. Three apply each product's canonical filter; the fourth pre-aggregates each side and joins on `data_year` to compute the per-year fetal mortality rate.

| View | Source | Filter |
|---|---|---|
| `fetal_death_canonical` | `fetal_death_derived.parquet` | `tabulation_flag = 2 AND residence_status != 4` |
| `natality_canonical` | `natality_v2_harmonized_derived.parquet` | `residence_status != 4` |
| `linked_canonical` | `natality_v3_linked_harmonized_derived.parquet` | `residence_status != 4` |
| `fetal_mortality_rate_by_year` | join of the first two | aggregated; 35 rows; FMR per 1,000 |

Usage (from a directory containing the three parquets at the unpacked Zenodo deposit layout):

```bash
# DuckDB CLI
duckdb hvs.duckdb < views.sql
duckdb hvs.duckdb -c "SELECT * FROM fetal_mortality_rate_by_year LIMIT 5"
```

```python
# Python
import duckdb
con = duckdb.connect()
con.execute(open("views.sql").read())
con.execute("SELECT * FROM fetal_mortality_rate_by_year").fetchdf()
```

```r
# R
library(duckdb)
con <- dbConnect(duckdb())
DBI::dbExecute(con, paste(readLines("views.sql"), collapse = "\n"))
DBI::dbGetQuery(con, "SELECT * FROM fetal_mortality_rate_by_year")
```

The DuckDB views' row counts are byte-exact-equivalent to applying the same filter via Python `pyarrow.compute`; verified in `RECEIPTS/C8.9_<UTC>.md`.

### Note on state-level geography

State-level identifiers (state of residence, state of occurrence) are **suppressed across all three NCHS public-use files** for confidentiality. This monorepo therefore cannot ship state-stratified denominators; any state-level analysis requires NCHS Research Data Center access. See `natality/docs/FAQ.md` for the upstream NCHS policy.

## Caveats

1. **Era-specific reporting quirks.** Several states had incomplete reporting of Hispanic origin or plurality during 1992–2002 (Oklahoma all years; Maryland 1992–1998; Massachusetts 1992–1997; Louisiana plurality 1992–1994). See [`fetal_death/COMPARABILITY.md`](../fetal_death/COMPARABILITY.md). Joint analyses on those strata in those years should restrict to states with complete reporting.
2. **Within-era columns.** Three fetal-death columns are tagged `within_era` because they carry incompatible content across the 1989/2003 revision boundary (`breech_unrevised`, `delivery_place_unrevised`, `maternal_race_bridged_detail`). Cross-era groupby on these is unsafe.
3. **Linked-file weighting.** The linked file's `recwt` (record weight) is the NCHS-assigned weight needed for unbiased period rates. Joint analyses involving the linked file should respect it.
4. **Bridged-race null years.** Both products lack 4-category bridged race for their most recent years (natality 2020+; fetal-death 2018+) because NCHS dropped MBRACE from the public-use file. Joint stratified-by-race rates are currently supported for 1992–2002 + 2005–2017.
5. **Dtype mismatch on event year.** natality `year` is `int16` and fetal-death `data_year` is `int32`. The rename helper does not coerce; cast as needed if you `merge` on year directly.
