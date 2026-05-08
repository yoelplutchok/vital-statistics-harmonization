# Getting started

## Prerequisites

```bash
pip install -r requirements.txt
brew install p7zip   # needed for deflate64 (2009-2013, 2016-2017, 2020) and PPMd (2015) zips
```

## Quick start: load harmonized data

If the pipeline has already been run, you can immediately load the outputs:

```python
import pandas as pd

# V2 Natality: 138.8M births, 1990-2024 (84 columns)
df = pd.read_parquet("output/harmonized/natality_v2_harmonized_derived.parquet")

# Filter to residents (standard NCHS analysis universe)
df_res = df[df["is_foreign_resident"] == False]

# Or use the pre-filtered convenience file (recommended for most analyses):
df_res = pd.read_parquet("output/convenience/natality_v2_residents_only.parquet")

# V3 Linked: 74.9M births with infant death data, 2005-2023 (94 columns)
linked = pd.read_parquet("output/harmonized/natality_v3_linked_harmonized_derived.parquet")
linked_res = linked[linked["is_foreign_resident"] == False]

# Or use the pre-filtered convenience file:
linked_res = pd.read_parquet("output/convenience/natality_v3_linked_residents_only.parquet")
```

## Available output files

### V2 Natality (1990-2024)

| File | Rows | Columns | Use case |
|------|------|---------|----------|
| `output/convenience/natality_v2_residents_only.parquet` | 138,582,904 | 82 | **Recommended** — residents only, derived indicators included |
| `output/harmonized/natality_v2_harmonized_derived.parquet` | 138,819,655 | 84 | Full file with foreign residents + restatus columns |
| `output/harmonized/natality_v2_harmonized.parquet` | 138,819,655 | 71 | Harmonized only (no derived indicators) |
| `output/yearly_clean/natality_{year}_core.parquet` | varies | varies | Raw NCHS substrings (audit/debug only) |

### V3 Linked birth-infant death (2005-2023)

| File | Rows | Columns | Use case |
|------|------|---------|----------|
| `output/convenience/natality_v3_linked_residents_only.parquet` | 74,785,708 | 92 | **Recommended** — residents only, derived indicators included |
| `output/harmonized/natality_v3_linked_harmonized_derived.parquet` | 74,943,824 | 94 | Full file with foreign residents + restatus columns |
| `output/harmonized/natality_v3_linked_harmonized.parquet` | 74,943,824 | 78 | Harmonized only (no derived indicators) |
| `output/linked/linked_{year}_denomplus.parquet` | varies | 55–87 (layout-dependent) | Raw parsed linked records (audit/debug only; 55 cols for 2005–2013, 87 cols for 2014–2023) |

## Example analyses

### Low birthweight rate by year (residents)

```python
res = df[df["is_foreign_resident"] == False]
lbw = res.groupby("year").apply(
    lambda g: (g["low_birthweight"].sum() / g["low_birthweight"].notna().sum()) * 100
)
print(lbw)  # LBW% from ~7.0% (1990) to ~8.2% (2020)
```

### Infant mortality rate by year (residents)

```python
res = linked[linked["is_foreign_resident"] == False]
imr = res.groupby("year").apply(
    lambda g: g["infant_death"].sum() / len(g) * 1000
)
print(imr)  # IMR from 6.74 (2005) to 5.49 (2023)
```

### Cause-specific infant mortality

```python
deaths = linked_res[linked_res["infant_death"] == True]
# Top 5 underlying causes of death (ICD-10) in 2020
deaths_2020 = deaths[deaths["year"] == 2020]
deaths_2020["underlying_cause_icd10"].value_counts().head(10)
```

### Neonatal vs postneonatal mortality trend

```python
trend = linked_res.groupby("year").agg(
    births=("infant_death", "count"),
    neonatal=("neonatal_death", "sum"),
    postneonatal=("postneonatal_death", "sum"),
)
trend["neo_imr"] = trend["neonatal"] / trend["births"] * 1000
trend["post_imr"] = trend["postneonatal"] / trend["births"] * 1000
```

## Rebuilding from source

### V2 Natality

```bash
python scripts/01_import/parse_all_v1_years.py --years 1990-2024
python scripts/03_harmonize/harmonize_v1_core.py --years 1990-2024 \
  --out output/harmonized/natality_v2_harmonized.parquet
python scripts/04_derive/derive_v1_core.py \
  --in output/harmonized/natality_v2_harmonized.parquet \
  --out output/harmonized/natality_v2_harmonized_derived.parquet
```

### V3 Linked

```bash
# 2005-2015 (denominator-plus format)
python scripts/01_import/parse_all_linked_years.py --years 2005-2015

# 2016-2023 (period-cohort format)
for cohort_year in 2016 2017 2018 2019 2020 2021 2022 2023; do
  period_year=$((cohort_year + 1))
  python scripts/01_import/parse_linked_cohort_year.py \
    --zip "raw_data/linked/${period_year}PE${cohort_year}CO.zip" \
    --year "$cohort_year" \
    --out "output/linked/linked_${cohort_year}_denomplus.parquet"
done

# Harmonize + derive
python scripts/03_harmonize/harmonize_linked_v3.py --years 2005-2023
python scripts/04_derive/derive_linked_v3.py
```

### Convenience: residents-only subsets (optional)

```bash
python scripts/06_convenience/write_residents_only.py
```

## Critical caveats (read before trend work)

### For all analyses

1. **Residents-only is the default analytic universe** — use `is_foreign_resident == false` (or `restatus != 4`) to match NCHS residence-based tabulations.

2. **Three gestation measurement eras** — preterm rates shift at each boundary:
   - 1990-2002: LMP-based (`gestational_age_weeks_source == 'lmp'`)
   - 2003-2013: combined gestation (`'combined'`)
   - 2014-2024: obstetric estimate (`'obstetric_estimate'`)

3. **Certificate revision coverage matters (especially 2009-2013)** — education, prenatal care, and smoking are effectively revised-only in 2009-2013 public-use files. Use `certificate_revision == 'revised_2003'` for revision-consistent analysis.

4. **Marital status has a 2017 break** — California stopped reporting, causing ~11-12% null from 2017+. Use `marital_reporting_flag == true` (2014+) to restrict to reporting states.

5. **Race/ethnicity uses three bridge methods** — approximate pre-2003, NCHS bridged 2003-2019, reconstructed from MRACE6 detail 2020-2024 (multiracial ~3% → null). Use `race_bridge_method` to identify derivation era.

6. **Use `_bool` versions for diabetes/HTN** — the raw `diabetes_any`, `hypertension_chronic`, `hypertension_gestational` use 9=unknown which passes `IS NOT NULL`. Prefer `diabetes_any_bool`, `hypertension_chronic_bool`, `hypertension_gestational_bool` (9→null).

7. **`prior_cesarean` is revised-cert-only and starts at 2005** — `RF_CESAR` (the Y/N/U prior-cesarean field) is a revised-certificate field. Coverage tracks cert-revision adoption: 30.8% of rows populated in 2005, rising to 90.2% in 2013 and ~96-100% from 2014+. 1990-2004 have no Y/N/U prior-cesarean field at all in the public-use layouts (use `delivery_method_recode` codes 2/4 — VBAC + repeat CS — as a tracer for 1990-2004 only).

8. **`father_age` 2012-2013**: `UFAGECOMB` carries raw single-year father age through 2011, but NCHS blanked it starting in 2012 while revised-cert rows carried `FAGECOMB`. Only revised-cert rows (77-79% of births in 2012/2013) therefore contribute single-year `father_age` in those two years. For categorical (5-year bucket) father age that covers the unrevised-cert 2005-2013 rows too, use `father_age_cat_from_rec11` (derived from the `FAGEREC11` recode; populated 2005-2013 only).

9. **2003 `maternal_age` has a phantom spike at age 14** — the 2003 public-use file suppresses single-year age below 15 and exposes only the `MAGER41` recode, so all births to mothers under 15 are coded as `maternal_age == 14`. Aggregated `maternal_age_cat` buckets are correct; for single-year-age analyses that span 2003, use `maternal_age_cat` or restrict to age ≥ 15.

10. **Check missingness profiles before trend work** — run `python scripts/05_validate/harmonized_missingness.py` to see per-variable per-year null rates and flag structural breaks. See `docs/COMPARABILITY.md` "Known pitfalls" section for the full table.

11. **1990-2002 era differences**:
    - Race bridge is **approximate** (no official NCHS bridged race before 2003)
    - Education is mapped from years-of-schooling to 4-category
    - Smoking `smoking_any_during_pregnancy` and `smoking_intensity_max_recode6` come from independent source fields (so a "smoker with unknown intensity" state is possible in 1990-2002 but not 2003+)

### For linked (V3) analyses

12. **Cohort vs period** — the V3 file follows each birth cohort for a full year of mortality experience. This is preferred for multivariate analysis over period files.

13. **Record weight** — for cohort analyses, NCHS recommends **not** applying the weight variable. The unweighted data are used in all validation targets. Two survivor rows (one in 2014, one in 2015) have null `record_weight`; this is a known upstream NCHS quirk, documented in COMPARABILITY.md. If weighting matters, filter with `record_weight.fillna(1.0)` or drop those two rows.

14. **`neonatal_death` / `postneonatal_death` are three-valued** — `False` for every survivor, `True`/`False` for deaths with known `age_at_death_days`, and `null` for the rare death with unknown age (none exist in current data, but the column is typed to preserve that distinction rather than force-coding unknown-age deaths as not-neonatal).

15. **Age-at-death comparability note** — starting 2019, NCHS revised how `age_at_death_days` is calculated (using birth certificate time-of-birth instead of death certificate). This produces more accurate sub-24-hour age categorization but means the <1 day and 1-day age-at-death categories are not perfectly comparable with 2005-2018. Total neonatal/postneonatal splits are minimally affected.

16. **Bridged race dropped 2020-2023** — NCHS no longer provides bridged race in linked files from 2020+. `maternal_race_bridged4` is null for these years, but `maternal_race_ethnicity_5` is reconstructed from MRACE6 detail codes (see caveat 5 above).

17. **V3 linked schema mirrors V2** — all 71 V2 harmonized birth-side columns plus all 13 V2 derived indicators appear in V3 as well; V3 adds 7 death-side harmonized columns (`infant_death`, `age_at_death_days`, `age_at_death_recode5`, `underlying_cause_icd10`, `cause_recode_130`, `manner_of_death`, `record_weight`) and 3 death-side derived (`neonatal_death`, `postneonatal_death`, `cause_group`). Net: 78 + 16 = 94.

## Where to look next

- **Codebook**: `docs/CODEBOOK.md` — variable definitions and death-side columns
- **Comparability**: `docs/COMPARABILITY.md` — trend-safe subset guidance
- **Validation**: `docs/VALIDATION.md` — what was checked and how
- **Schema**: `metadata/harmonized_schema.csv` — machine-readable provenance (raw-field positions per era)
