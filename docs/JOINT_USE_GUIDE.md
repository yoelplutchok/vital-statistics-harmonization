# Joint-use guide: computing rates that need numerator and denominator

The three U.S. Harmonized Vital Statistics products are designed to be used jointly. Several headline rates in U.S. perinatal epidemiology cannot be computed from any single product alone:

- **Fetal mortality rate** = fetal deaths / (live births + fetal deaths)
- **Perinatal mortality rate** = (fetal deaths + early neonatal deaths) / (live births + fetal deaths)
- **Neonatal mortality rate** = neonatal deaths / live births
- **Infant mortality rate** = infant deaths / live births

The first two require the fetal-death numerator and the natality denominator. The third and fourth require the linked-file numerator and the natality denominator. All four require the demographic stratification on numerator and denominator to align exactly, otherwise the resulting rate is biased.

This guide describes the canonical join keys, aligned strata, and analytic filters.

## Canonical join keys

All three products share these column names with identical dtypes and code spaces (see each subproject's `harmonized_schema.csv`):

| Column | Description | All three products |
|---|---|---|
| `data_year` | Calendar year of event | ✓ |
| `maternal_age` | Maternal age at event (years) | ✓ |
| `maternal_race_bridged` | 4-category bridged race | ✓ |
| `hispanic_origin` | Hispanic origin recode | ✓ |
| `residence_status` | U.S. resident vs non-resident | ✓ |

Joining on `data_year` and any subset of these demographic columns produces numerator and denominator with consistent semantics.

## Canonical analytic filters

Each product has one filter that reproduces the population on which NCHS computes its published rates. **These filters MUST be applied before computing any rate** if the result is to be comparable to published NVSR figures.

| Product | Filter | Rationale |
|---|---|---|
| Natality | `restatus != '4'` | U.S. residents only |
| Linked birth–infant death | `restatus != '4'` (on the birth side) | U.S. residents only |
| Fetal death | `tabulation_flag == '2' AND residence_status != '4'` | NVSR-comparable subset of resident fetal deaths whose gestational age and birth-weight criteria meet NCHS's tabulation rule |

Applying the filter is the difference between reproducing NCHS's published per-year rates exactly and producing systematically biased counts.

## Worked example: fetal mortality rate by maternal race, 2022

Pseudocode (the worked notebook lives at [`notebooks/joint_use_demo.ipynb`](../notebooks/joint_use_demo.ipynb), to be filled in):

```python
import pandas as pd

# Numerator: fetal deaths
fd = pd.read_parquet("fetal_death/fetal_death_derived.parquet")
fd_2022 = fd[
    (fd["data_year"] == 2022)
    & (fd["tabulation_flag"] == "2")
    & (fd["residence_status"] != "4")
]
fd_by_race = fd_2022.groupby("maternal_race_bridged").size()

# Denominator: live births + fetal deaths (in same race stratum)
nat = pd.read_parquet("natality/.../natality_derived.parquet")
nat_2022 = nat[
    (nat["data_year"] == 2022)
    & (nat["restatus"] != "4")
]
births_by_race = nat_2022.groupby("maternal_race_bridged").size()

# Fetal mortality rate per 1,000 (live births + fetal deaths)
fmr = 1000 * fd_by_race / (births_by_race + fd_by_race)
print(fmr)
```

The cross-product validation notebook will compare these cell-by-cell against *NVSR 73-09* Table A.

## Convenience: the `live_births_by_year.csv` shortcut

For unstratified denominators, the fetal-death deposit ships [`fetal_death/live_births_by_year.csv`](../fetal_death/live_births_by_year.csv), sourced from NVSR 57-08 (1995–2002) and NVSR 73-09 (2005–2022). This file is appropriate when:

- You want a national fetal mortality rate without demographic stratification.
- You don't want to load the 138.8M-row natality file.

It is **not** appropriate when:

- You need stratified rates (race, age, ethnicity) — those require a join to the natality file.
- You need fetal-death years 1992–1994 or 2003–2004 — these are absent from the NVSR Fetal & Perinatal Mortality series and the convenience CSV.

A planned [stratified denominator file](../VERSION_ROADMAP.md#joint-use-convenience-layer) will close this gap.

## Caveats

1. **Era-specific reporting quirks.** Several states had incomplete reporting of Hispanic origin or plurality during 1992–2002 (see `fetal_death/COMPARABILITY.md`). Joint analyses on those strata in those years should restrict to states with complete reporting.
2. **Within-era columns.** Three fetal-death columns are tagged `within_era` because they carry incompatible content across the 1989/2003 revision boundary (`breech_unrevised`, `delivery_place_unrevised`, `maternal_race_bridged_detail`). Cross-era groupby on these is unsafe; see `fetal_death/COMPARABILITY.md`.
3. **Linked-file weighting.** The linked file's `recwt` (record weight) is the NCHS-assigned weight needed for unbiased period rates. Joint analyses involving the linked file should respect it.
