# Getting Started

A quickstart guide for loading and working with the harmonized fetal death data (**v2.4.0, 1982-2024, 2,427,233 records**).

## Loading the Data

The Zenodo deposit is flat — `cd` into the directory you unpacked and load the parquet directly.

**Python (pandas):**

```python
import pandas as pd

df = pd.read_parquet("fetal_death_derived.parquet")
print(f"{len(df):,} records, {len(df.columns)} columns, years {df['data_year'].min()}-{df['data_year'].max()}")
# 2,427,233 records, 89 columns, years 1982-2024
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
| `data_year` | Report year, **1982-2024** (43 years) |
| `version_flag` | `'A'` (2003 revision) or `'S'` (1989 / pre-2003-revision synthesized) — see `COMPARABILITY.md` |
| `tabulation_flag` | `2` = NVSR tabulated subset; `1` = exclude. Integer dtype (v2.1+). See Appendix C8.20 for per-era GA/tab_flag cross-tabs |
| `residence_status` | `1`-`3` = U.S. residents, `4` = foreign |
| `gestational_age_combined` | Weeks of gestation (02-47, 99=unknown) |
| `birthweight` | Grams (0001-8165, 9999=unknown) |
| `fetal_sex` | M/F/U |
| `cause_icd10` | ICD-10 cause-of-death code (**2014+** only) |

## Common Filtering Patterns

Standard >=20 week analysis:

```python
gte20 = df[df['tabulation_flag'] == 2]
```

Exclude foreign residents:

```python
us_res = df[df['residence_status'] != 4]
```

NVSR-comparable subset (both filters — matches published NVSR figures):

```python
nvsr = df[(df['tabulation_flag'] == 2) & (df['residence_status'] != 4)]
```

A-version only (revised fields like education, BMI, ICD-10 cause):

```python
a_only = df[df['version_flag'] == 'A']
```

Pre-2003-revision slice (1982-2002, incl. V3b/V3a/V2):

```python
pre2003 = df[df['data_year'].between(1982, 2002)]
```

V2.1 transition years:

```python
trans = df[df['data_year'].isin([2003, 2004])]
```

V1 era (2003-revision public-use layouts, 2005+):

```python
v1 = df[df['data_year'] >= 2005]
```

## Derived Variables

The derived file adds 16 pre-computed analytic flags (`ga_gte20wks`, `preterm`, `lbw`, `singleton`, `cause_group`, etc.). These are string-valued (`"1"` / `"0"` / `""`). Filter with explicit equality: `df[df['preterm'] == '1']`. Full definitions: `CODEBOOK.md`.

## Sample Analysis

Fetal death count trend by year (NVSR-comparable subset):

```python
import pandas as pd

df = pd.read_parquet("fetal_death_derived.parquet")
nvsr = df[(df['tabulation_flag'] == 2) & (df['residence_status'] != 4)]
counts = nvsr.groupby('data_year').size()
print(counts)
```

Fetal mortality rate (divide by fetal deaths + live births per year). Denominators: `live_births_by_year.csv` where available; for joint natality denominators see [`docs/JOINT_USE_GUIDE.md`](../docs/JOINT_USE_GUIDE.md).

## Cross-Era Considerations

The dataset spans **seven file-format eras** (1982-2024). See `COMPARABILITY.md` for the era table and `CODEBOOK.md` Appendix C8.20 for per-variable per-era distributions.

**Do not cross-era groupby** on `within_era` columns: `maternal_race_bridged_detail`, `delivery_place_unrevised`, `breech_unrevised`.

For V2-specific raw fields, use per-year raw parquets:

```python
# Monorepo: output/yearly_clean/fetal_death_{year}_raw.parquet (1982-2024)
v2_breech = pd.read_parquet("fetal_death_1998_raw.parquet")['BREECH']
```

## Important Caveats

- **Version-A-only fields** blank for S-version records (incl. all pre-2003-revision eras for revised-only items).
- **Maternal education:** use `maternal_education_unrevised` for 1982-2002; revised scale gaps in V1 2007-2013.
- **Cause of death:** 2014+ only in public-use files.
- **Cross-year comparability:** report A/S mix when using version-dependent fields.
- **Reporting thresholds:** see [REPORTING_THRESHOLDS.md](REPORTING_THRESHOLDS.md).
- **V2 Hispanic / Louisiana quirks:** [COMPARABILITY.md](COMPARABILITY.md) §11.
- **V3b race recode:** 1978-revision 1-digit `MRACE`; codes 7+9 → null — see `COMPARABILITY.md` and Appendix C8.20.
