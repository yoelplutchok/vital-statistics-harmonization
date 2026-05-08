# FAQ

## What years are covered?

- **V2 Natality**: 1990-2024 (35 years, 138.8 million birth records)
- **V3 Linked birth-infant death**: 2005-2023 (19 years, 74.9 million birth records with linked infant death data)

## What is the difference between V2 and V3?

**V2 Natality** contains birth records only — maternal demographics, prenatal care, birth outcomes. It covers the longest time span (1990-2024).

**V3 Linked** contains birth records linked to infant death certificates. It includes all the V2 birth-side columns plus death-side columns (cause of death, age at death, neonatal/postneonatal classification). Use V3 for infant mortality research. V3 starts at 2005 because that is when NCHS began releasing public-use cohort linked files in the current format.

## Which file should I use?

- For **birth outcome research** (LBW, preterm, demographic trends): use `output/convenience/natality_v2_residents_only.parquet` (pre-filtered to residents, 82 columns)
- For **infant mortality research** (IMR, cause-specific mortality, neonatal vs postneonatal): use `output/convenience/natality_v3_linked_residents_only.parquet` (pre-filtered to residents, 92 columns)
- For analyses that need **foreign residents** or the `restatus` column: use the full `natality_v2_harmonized_derived.parquet` (84 columns) or `natality_v3_linked_harmonized_derived.parquet` (94 columns)
- For **auditing or debugging**: use the yearly `output/yearly_clean/` or `output/linked/` files

## Are these data nationally representative?

Yes. These are the **NCHS national public-use natality files** — essentially a census of all registered births in the United States for each year. However:

- Some variables are not fully comparable across years and certificate revisions (see `docs/COMPARABILITY.md`)
- Public-use files do **not** include sub-state geography (county/city)
- 1990-1993 files use `Nat{year}.zip` (without "us" suffix); they still contain a small foreign-resident tail (~0.1% per year, identifiable via `RESTATUS == 4` / `is_foreign_resident == True`)

## What is the recommended analysis universe?

Use **resident births** by default:

```python
df_res = df[df["is_foreign_resident"] == False]
```

This matches the residence-based tabulations used in all NCHS publications and in our validation.

## Which variables are fully comparable across all years?

See `docs/COMPARABILITY.md` for the full list. Variables with **full** comparability (trend-safe 1990-2024):

- `year`, `restatus`, `is_foreign_resident`, `certificate_revision`
- `live_birth_order_recode`, `total_birth_order_recode`
- `plurality_recode`, `infant_sex`, `birthweight_grams`, `apgar5`
- Derived: `birthweight_grams_clean`, `apgar5_clean`, `low_birthweight`, `very_low_birthweight`, `singleton`, `maternal_age_cat`

## Which variables have known breaks?

Key breaks:

- **Gestation/preterm**: three eras with different measurement methods (LMP → combined → obstetric estimate). Series breaks at 2003 and 2014.
- **Education/prenatal care/smoking**: effectively revised-only in 2009-2013 public-use files (use `certificate_revision == 'revised_2003'` for consistent analysis).
- **Race bridging**: approximate for 1990-2002; official NCHS bridged race 2003-2019; reconstructed from MRACE6 detail codes 2020-2024 (multiracial ~3% → null). See `race_bridge_method`.
- **Maternal age**: 2003 uses an approximate recode from `MAGER41`.
- **Father education**: null for 1995-2008 (field dropped from public-use files); partial coverage 2009-2010 (2003-revision states only).
- **Father race/ethnicity**: `NH_other` category only exists for 1990-2002 (code 8 semantic shift).
- **Payment source**: available 2009+ (partial 2009-2010); null for 1990-2008.

## Why are some fields missing in some years?

Common reasons:

- **Not on that certificate revision** (e.g., pre-pregnancy smoking, congenital anomalies, infections, and fertility treatment fields are only available 2014+)
- **Structural coverage differences** between revised and unrevised certificates
- **Public-use blanking** of unrevised-only fields in 2009-2013; father education dropped from public-use 1995-2008
- **Sentinel codes** (`99` for gestation, `9999` for birthweight) treated as missing in derived `_clean` fields
- **"Not applicable" codes** (e.g., `RF_FEDRG` X code for births without fertility treatment → null)

## Should I apply the record weight in the linked file?

**No, for cohort analyses.** The NCHS user guides explicitly state: "For cohort file use: do not apply the weight." The weight is designed for period (cross-sectional) analyses only. All validation in this project uses unweighted cohort data.

## What is the difference between the 2005-2015 and 2016-2023 linked files?

The underlying data format changed:

- **2005-2015**: "denominator-plus" format — birth and death fields are appended in a single record
- **2016-2023**: "period-cohort" format — birth records (denominator) and death records (numerator) are in separate files, merged by sequence number (CO_SEQNUM)

This project handles both formats transparently. The harmonized output has the same schema regardless of source format.

## How was the age-at-death variable changed in 2019?

Starting with 2019, NCHS calculates age at death from the birth certificate's date and time of birth (instead of the death certificate). This improves accuracy for deaths in the first 24 hours but means the `<1 hour` and `1 day` age categories are not perfectly comparable with 2005-2018. The impact on total neonatal/postneonatal splits is minimal.

## Is geography included?

No. The public-use natality files do not include sub-state geography. State-level identifiers are also suppressed in the public-use linked files from 2005 onward.

## How should the data be cited?

- Cite NCHS as the source of the underlying public-use microdata
- Cite this repository/release: https://doi.org/10.5281/zenodo.19363074 (concept DOI — resolves to latest version)

Example:

> Birth and linked birth-infant death microdata from the National Center for Health Statistics (NCHS), U.S. Centers for Disease Control and Prevention. Harmonized using the U.S. Natality Harmonization Project [URL/DOI].

## Why is `marital_status` null for ~12% of births after 2017?

California stopped providing record-level marital status to NCHS in 2017 due to state statutory restrictions. The data is truly absent at the source — NCHS does not impute it. Use `marital_reporting_flag` (available 2014+) to distinguish non-reporting-state births (`false`) from reporting-state births with genuine unknown status. For trend analyses spanning 2017, either restrict to `marital_reporting_flag == true` or exclude marital status from the model.

## Why is `father_age` null for so many 2012 and 2013 births?

`father_age` (single-year integer) is populated only for revised-certificate rows in 2012 and 2013 — about 77% and 79% of those years respectively. The reason: NCHS moved the raw single-year father-age field from `UFAGECOMB` (used 2005–2011) to `FAGECOMB` across those two years, and only the revised form carries `FAGECOMB`. The unrevised-certificate rows in 2012 (~12% of births) have no raw single-year source at all.

For analyses that need father age for *every* row in 2005–2013, use **`father_age_cat_from_rec11`** (a categorical string column derived from the NCHS `FAGEREC11` recode — values `<20`, `20-24`, `25-29`, `30-34`, `35-39`, `40+`, or null). This column is populated for ~87% of rows across 2005–2013 regardless of certificate revision, because FAGEREC11 is on both forms. It is null for 1990–2002 and 2014+ (where raw single-year age is directly available in `father_age`).

## Why is `prior_cesarean` null for 1990–2004 and partly null for 2005–2013?

`prior_cesarean` is derived from `RF_CESAR`, which is a **revised-certificate-only** field. It was introduced at position 324 of the 2005–2013 record layout and appears on every revised-cert birth but no unrevised-cert births. Coverage therefore tracks state-level adoption of the 2003 revised certificate: 30.8% of rows populated in 2005, rising to 48.6% (2006), 55.0% (2007), 64.4% (2008), 67.7% (2009), 77.1% (2010), 85.4% (2011), 88.0% (2012), 90.2% (2013), and ~96–100% from 2014+ when all states had adopted the revised form.

For 1990–2004, the public-use layouts carry no Y/N/U prior-cesarean field at all. The closest tracer is `delivery_method_recode`: codes 2 (VBAC) and 4 (repeat cesarean) together identify a mother with a known prior cesarean. This tracer is only available 1990–2004 because the delivery-method coding changed at 2005 (3-category vs. 5-category).

The companion `prior_cesarean_count` column (0–30 count of prior cesareans, with 99→null) follows the same coverage pattern — 2005–2024, revised-cert-only in 2005–2013, and ~96–100% in 2014+ — but is very slightly less complete than `prior_cesarean` because some rows have a known Y/N/U flag with a blank count.

## How do I compute the cesarean rate across 1990–2024?

`delivery_method_recode` uses two different coding frames with the boundary at **2005** (not 2003). You need a year-aware rule:

- **1990–2004** (DELMETH5-style): codes 1=vaginal, 2=VBAC, 3=primary cesarean, 4=repeat cesarean, 9=not stated. Cesarean = `delivery_method_recode IN (3, 4)` among known codes 1–4.
- **2005–2024** (DMETH_REC): codes 1=vaginal, 2=cesarean, 9=not stated. Cesarean = `delivery_method_recode == 2` among known codes 1–2.

Naïvely computing `delivery_method_recode == 2` over the full range will undercount cesareans by ~15–20 percentage points for 1990–2004 rows (where `2` means VBAC, not cesarean). Example SQL / Python:

```python
import pyarrow.compute as pc
is_ces = pc.if_else(
    pc.less_equal(df["year"], 2004),
    pc.is_in(df["delivery_method_recode"], value_set=pa.array([3, 4], pa.int8())),
    pc.equal(df["delivery_method_recode"], pa.scalar(2, pa.int8())),
)
known = pc.if_else(
    pc.less_equal(df["year"], 2004),
    pc.less_equal(df["delivery_method_recode"], pa.scalar(4, pa.int8())),
    pc.less_equal(df["delivery_method_recode"], pa.scalar(2, pa.int8())),
)
```

This crosswalk is validated against NVSR published cesarean rates for every year 1990–2024 (all within 0.07 pct-pts — see `output/validation/external_validation_v1_comparison.csv`). Finer categories (primary vs repeat cesarean, VBAC) are only available for 1990–2004.

## What does the `attendant_at_birth` column cover?

`attendant_at_birth` records who attended the birth: 1=MD, 2=DO, 3=CNM, 4=other midwife, 5=other. Null rate is <0.4% in every year (typically under 0.1%; range 0.026% in 2002 to 0.389% in 1990) — this variable has the cleanest coverage in the dataset. The source field moves across three positions (`BIRATTND@10` for 1990–2002; `ATTEND@408` for 2003–2004; `ATTEND@410` for 2005–2013; `ATTEND@433` for 2014+); the harmonizer resolves this automatically.

## Why should I use `diabetes_any_bool` instead of `diabetes_any`?

The raw `diabetes_any` field uses integer coding: 1=yes, 2=no, **9=unknown**. The sentinel value 9 is not null, so `WHERE diabetes_any IS NOT NULL` silently includes unknowns in your denominator. The derived `diabetes_any_bool` maps 1→true, 2→false, 9→null, making it safe for standard `IS NOT NULL` / complete-case filtering. The same applies to `hypertension_chronic_bool` and `hypertension_gestational_bool`.

## What is `race_bridge_method` and why does it matter?

`maternal_race_ethnicity_5` uses three different derivation methods across eras:

- **1990-2002** (`approximate_pre2003`): crosswalk from MRACE detail codes — approximate, not official NCHS bridging
- **2003-2019** (`nchs_bridged`): official NCHS bridged race from MBRACE/MRACEREC
- **2020-2024** (`approximate_from_detail`): reconstructed from MRACE6 detail codes after NCHS dropped bridged race. Multiracial births (MRACE6=06, ~3%) cannot be bridged and map to null.

The `race_bridge_method` column tells you which method was used for each record, so you can document or stratify by derivation era.

## How do I check for missingness breaks before running a trend analysis?

Run `python scripts/05_validate/harmonized_missingness.py`. This produces:

- `harmonized_missingness_by_year.csv`: null rate for every variable by year
- `harmonized_missingness_breaks.csv`: any variable where the null rate changes by >5 percentage points between adjacent years

Check this before running any multi-year analysis. Known major breaks include marital status at 2017, smoking at 2009, education at 2009, and race at 2020.

## What clinical detail variables are available for 2014+?

The 2014+ revised certificate added several within-era variables not available in earlier years:

- `pre_pregnancy_diabetes`, `gestational_diabetes` (finer-grained than `diabetes_any`)
- `nicu_admission`, `induction_of_labor`, `breastfed_at_discharge`
- `weight_gain_pounds` (0-97 pounds, 99→null)
- `bmi_prepregnancy`, `bmi_prepregnancy_recode6`
- `smoking_pre_pregnancy_recode6`
- 12 congenital anomaly booleans, 5 infection booleans
- `fertility_enhancing_drugs`, `assisted_reproductive_tech`
- `payment_source_recode` (available 2009+ but full coverage only from 2014+)

All are null for pre-2014 years.

## Where do I see variable definitions and provenance?

- Machine-readable schema: `metadata/harmonized_schema.csv`
- Human-readable overview: `docs/CODEBOOK.md`
- Comparability details: `docs/COMPARABILITY.md`

## How do I validate that the pipeline matches official totals?

See `docs/VALIDATION.md`. Key artifacts:

- `output/validation/external_validation_v1_comparison.csv` (V2 natality: 183 targets)
- `output/validation/external_validation_v3_linked_comparison.csv` (V3 linked: 35 targets)
- `output/validation/invariants_report_v2_1990_2024.md` (V2 natality deterministic consistency checks + null-rate discontinuity detection)
- `output/validation/invariants_report_v3_linked_2005_2023.md` (V3 linked equivalent)
- `output/validation/harmonized_missingness_by_year.csv` (per-variable per-year null rates)
- `output/validation/harmonized_missingness_breaks.csv` (>5 ppt year-over-year jumps)
