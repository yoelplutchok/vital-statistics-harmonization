# Getting Started

A quickstart guide for loading and working with the harmonized fetal death data (V2.0, 1992-2022, 1,634,195 records).

## Loading the Data

The Zenodo deposit is flat — `cd` into the directory you unpacked and load the parquet directly.

**Python (pandas):**

```python
import pandas as pd

df = pd.read_parquet("fetal_death_derived.parquet")
print(f"{len(df):,} records, {len(df.columns)} columns, years {df['data_year'].min()}-{df['data_year'].max()}")
# 1,634,195 records, 89 columns, years 1992-2022
```

**R (arrow):**

```r
library(arrow)

df <- read_parquet("fetal_death_derived.parquet")
cat(nrow(df), "records,", ncol(df), "columns\n")
```

## Key Variables

| Variable | Description |
|---|---|
| `data_year` | Report year, 1992-2022 (no 2003/2004 — deferred to V2.1) |
| `version_flag` | `'A'` (2003 revision) or `'S'` (1989 revision) — affects field availability. All V2 (1992-2002) records are `'S'` (synthesized); V1 (2005-2022) is mixed |
| `tabulation_flag` | NCHS-defined tabulated subset. `'2'` = include in NVSR tabulations (typically >=20 weeks gestation OR >=350g birthweight when GA is unknown); `'1'` = exclude. Note: ~5,400 V1 records flagged `'2'` have `gestational_age_combined < 20` (almost all in 2014+), and ~63,700 records across all 29 years flagged `'1'` have GA >= 20 (~42,200 in V1 alone) — `tabulation_flag` is NCHS's compound criterion, not a pure GA cutoff |
| `residence_status` | `'1'`-`'3'` = U.S. residents, `'4'` = foreign |
| `gestational_age_combined` | Weeks of gestation (02-47, 99=unknown) |
| `birthweight` | Grams (0001-8165, 9999=unknown) |
| `fetal_sex` | M/F/U (V2 1/2/9 normalized to V1 M/F/U by harmonize) |
| `cause_icd10` | ICD-10 cause-of-death code (2014+ only, blank for 1992-2013) |

## Common Filtering Patterns

Standard >=20 week analysis:

```python
gte20 = df[df['tabulation_flag'] == '2']
```

Exclude foreign residents:

```python
us_res = df[df['residence_status'] != '4']
```

NVSR-comparable subset (both filters combined — matches published NVSR figures exactly):

```python
nvsr = df[(df['tabulation_flag'] == '2') & (df['residence_status'] != '4')]
```

A-version only (required for revised fields like education, BMI, ICD-10 cause):

```python
a_only = df[df['version_flag'] == 'A']  # excludes all V2 (which is 100% S) and V1 S-version records
```

V2 era only (1989-revision uniform):

```python
v2 = df[df['data_year'].between(1992, 2002)]
```

V1 era only (2003-revision transition):

```python
v1 = df[df['data_year'] >= 2005]
```

## Derived Variables

The derived file adds several pre-computed analytic flags:

| Variable | Definition |
|---|---|
| `ga_gte20wks`, `ga_gte28wks` | Gestational age threshold flags |
| `preterm`, `very_preterm`, `extremely_preterm` | <37, <32, <28 weeks |
| `lbw`, `vlbw` | Low birthweight (<2500g), very low birthweight (<1500g) |
| `singleton` | Singleton delivery |
| `meets_who_stillbirth` | WHO stillbirth definition (>=28 weeks OR >=1000g) |
| `cause_group` | Broad cause-of-death grouping (2014+ only — blank for 1992-2013) |
| `education_cat4` | 4-level education category (blank for 1992-2002 because V2 uses years-of-school instead of revised categorical scale) |

These are string-valued columns holding `"1"` (condition met), `"0"` (condition not met), or `""` (unknown / not derivable). Filter with explicit equality: `df[df['preterm'] == '1']`. The full list of all 16 derived variables is in CODEBOOK.md.

## Sample Analysis

Compute a fetal death count trend by year, using the standard >=20 week / U.S. resident subset:

```python
import pandas as pd

df = pd.read_parquet("fetal_death_derived.parquet")

# Standard >=20wk, U.S. residents — exact-match against NVSR 57-08 (1995-2002) and NVSR 73-09 (2005-2022)
nvsr = df[(df['tabulation_flag'] == '2') & (df['residence_status'] != '4')]
counts = nvsr.groupby('data_year').size()
print(counts)
```

To compute a fetal mortality rate, divide these counts by `(fetal_deaths + live_births)` for each year. Live-birth denominators are shipped in `live_births_by_year.csv` (1995-2022, NVSR 57-08 + NVSR 73-09 / NCHS sources noted per row; 1992-1994 are absent because the NVSR Fetal & Perinatal Mortality series itself has a gap there):

```python
denoms = pd.read_csv("live_births_by_year.csv").set_index("year")["live_births"]
rates = (counts / (counts + denoms.reindex(counts.index))).mul(1000)  # per 1,000 total births
```

## Cross-Era Considerations

The dataset spans **four file-format eras**: 1992-2002 (1989-revision uniform), 2005-2013 (mixed), 2014-2017 (mostly 2003-revision), 2018-2022 (2003-revision only). The `version_flag` column identifies the revision per record.

For most fields, cross-era `groupby` is safe after the V2 normalization fixes (see `COMPARABILITY.md` §10). **Three columns are explicitly tagged `within_era` and should not be cross-era grouped**: `maternal_race_bridged_detail`, `delivery_place_unrevised`, `breech_unrevised`. The schema and codebook flag these with WARNINGs.

Example — what to NOT do:

```python
# DON'T do this: V2 BREECH means "Breech/Malpresentation"; V1 ULD_BREECH means "Breech Delivery" — different concepts
df.groupby(['data_year','breech_unrevised']).size()  # mixes apples and oranges
```

What to do instead:

```python
# Use yearly raw parquets if you need V2-specific BREECH detail.
# In this Zenodo deposit the per-year files are bundled in fetal_death_yearly_raw_1992-2022.zip — unzip first:
#   unzip fetal_death_yearly_raw_1992-2022.zip
v2_breech = pd.read_parquet("fetal_death_1998_raw.parquet")['BREECH']
```

## Important Caveats

- **Version-A-only fields.** Many variables — revised education, revised tobacco use, revised risk factors, BMI, cause of death — are only populated for records with `version_flag == 'A'`. S-version records (including all 700,704 V2 records) leave these blank. The share of A-version records varies by year and state.

- **Maternal education gap.** `maternal_education` (the revised 1-9 categorical) is blank for V1 2007-2013 and for all V2 records. For V2, use `maternal_education_unrevised` (years of school 00-17). The derived `education_cat4` is blank for V2.

- **Cause of death availability.** `cause_icd10` is only present for 2014 and later. Even within that range, roughly 50% of records for 2018 onward have missing cause codes. Pre-2014 ICD codes are NCHS RDC restricted-use only.

- **Cross-year comparability.** The mix of A-version and S-version records shifts over time, which can create artificial trends in version-dependent fields. See [COMPARABILITY.md](COMPARABILITY.md) for details on what can and cannot be safely compared across years.

- **Reporting thresholds.** Not all states report fetal deaths at the same gestational age cutoff. Some report only at >=20 weeks, others at lower thresholds. This affects completeness at earlier gestational ages. See [REPORTING_THRESHOLDS.md](REPORTING_THRESHOLDS.md) for the full discussion.

- **V2 state-specific Hispanic non-reporting**: Oklahoma 100% unknown all 11 V2 years; Maryland 1992-1998; Massachusetts 1992-1997. Do not over-interpret Hispanic-origin distributions for those state-years.

- **V2 Louisiana plurality non-reporting (1992-1994)**: ≈99% of LA resident records have `plurality=9` for those three years. The derived `singleton` correctly returns `''` (unknown) for these records.
