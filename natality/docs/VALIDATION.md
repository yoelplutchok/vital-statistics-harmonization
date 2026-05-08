# Validation

## Row counts (external + internal)

- `output/validation/row_count_validation_nchs_1994_2024.md` — **unified 1994–2024** Parquet rows vs zip size-implied counts (all years match); resident rows match NCHS residence totals exactly for 1994–2018 (2019–2024 not yet in CDC Open Data API but validated via NVSR targets)
- `output/validation/row_count_validation_nchs_1994_2004.md` — 1994–2004 subset (legacy)
- `output/validation/row_count_validation_nchs_2005_2015.md` — 2005–2015 subset (original V1 baseline)
- The script (`scripts/05_validate/validate_row_counts_vs_nchs.py`) also fetches NCHS published annual births (**residence-based**) from `data.cdc.gov` (`e6fc-ccez`) and uses `RESTATUS` (code `4` = foreign resident) to reproduce the NCHS residence totals exactly.
- Note: 1990–1993 zips (`Nat{year}.zip`) lack the `us` suffix used from 1994 on, but still contain a small share of foreign-resident records (~0.10–0.11% of rows; 4,283–4,705 per year). The parser reads all 350-byte records; `RESTATUS == 4` correctly distinguishes them so the residents-only convenience file and the `is_foreign_resident` flag work for these years.

## Missingness + frequency QA (raw core extracts)

Legacy per-era QA on the **raw** (pre-harmonization) yearly Parquet extracts. These check blank/whitespace rates on the NCHS field names, not the harmonized column names. For harmonized-level null rates, see the "Harmonized missingness diagnostics" section below.

- Summary pointer: `output/validation/qa_core_2005_2015.md` (V1 baseline)
- Missingness (blank/whitespace-only) by year/column: `output/validation/qa_missingness_core_2005_2015.csv`
- Frequencies (selected low-cardinality columns): `output/validation/qa_frequencies_core_2005_2015.csv`

## Harmonized missingness diagnostics

Per-variable per-year null rates across all harmonized variables, with structural break detection.

Run:

```bash
python scripts/05_validate/harmonized_missingness.py
```

Outputs:

- `output/validation/harmonized_missingness_by_year.csv` — null rate for every harmonized variable by year (columns: `year`, `variable`, `n_total`, `n_null`, `null_pct`)
- `output/validation/harmonized_missingness_breaks.csv` — any variable where the null rate changes by >5 percentage points between adjacent years

This is the recommended first check before any multi-year analysis. Known structural breaks include:

| Variable | Break year | Mechanism |
|----------|-----------|-----------|
| `marital_status` | 2017 | California stopped reporting (~11–12% null) |
| `smoking_any_during_pregnancy` | 2009, 2014 | Revised-only in 2009–2013; all states revised by 2014 |
| `maternal_education_cat4` | 2009 | Same revised-only mechanism as smoking |
| `maternal_race_bridged4` | 2020 | NCHS dropped bridged race (100% null) |
| `maternal_race_ethnicity_5` | 2020 | Multiracial ~3% cannot be bridged (now reconstructed from MRACE6) |
| `father_education_cat4` | 1995, 2009 | Dropped from public-use 1995–2008; partially restored 2009+ |

## Key derived rates (resident-only)

- By-year resident-only LBW + preterm rates:
  - `output/validation/key_rates_core_1990_2024.csv` (full range)
  - `output/validation/key_rates_core_1990_2024.md`

Reproduce:

```bash
python scripts/03_harmonize/harmonize_v1_core.py --years 1990-2024 --out output/harmonized/natality_v2_harmonized.parquet
python scripts/04_derive/derive_v1_core.py --in output/harmonized/natality_v2_harmonized.parquet --out output/harmonized/natality_v2_harmonized_derived.parquet
python scripts/05_validate/key_rates_from_derived_core.py --in output/harmonized/natality_v2_harmonized_derived.parquet --years 1990-2024
```

Spot-checks: LBW 6.97% (1990), 7.32% (1995), 7.57% (2000), 8.07% (2015), 8.24% (2020) — all match NCHS published values. Preterm rates show expected series breaks at 2003 (LMP→combined) and 2014 (combined→obstetric estimate).

## External validation (V2 natality)

**Results: 183/183 targets pass.** Validated against NCHS “Births: Final Data” NVSR reports, CDC Data API, and NCHS Data Briefs covering resident birth counts, LBW%, preterm%, twin/triplet+ rates, cesarean%, singleton%, male%, smoking%, and Medicaid% across 1990-2024.

> **2024 coverage caveat**: the NVSR "Births: Final Data for 2024" report was not yet published at this release. The targets CSV currently contains only **one 2024 target** — `cesarean_rate_pct`, sourced to VSRR No. 38 (*Births: Provisional Data for 2024*). Other 2024 metrics (LBW%, preterm%, smoking%, Medicaid%, etc.) have no external validation yet. When the 2024 NVSR Final Data report publishes, those targets will be backfilled to match the 5–8 targets per year density used for 1990–2023.

### Playbook

Goal: for a small set of **gold** outcomes/distributions, reproduce published NCHS residence-based values and record the comparison in a **machine-readable** way.

### Step 1: Define the validation universe(s)

- **resident**: exclude foreign residents (`is_foreign_resident == false`)
- **resident_revised**: resident births **and** `certificate_revision == 'revised_2003'`
  - Use this universe for domains that are effectively revised-only in 2009–2013 public-use files (education, prenatal care initiation, smoking).

### Step 2: Pick official targets (recommended minimum)

For benchmark years (e.g., **1995**, **2000**, **2005**, **2010**, **2015**, **2020**), pull values from NCHS “Births: Final Data” (or equivalent official natality report) for:

- resident births (count)
- low birthweight % (<2500g)
- preterm % (<37 weeks)
- (recommended) twin birth rate (per 1,000 births) and triplet+ birth rate (per 100,000 births)
- (optional) singleton % / plurality distribution
- (optional) male % (sex ratio)

For education / smoking / prenatal-care initiation, either:

- validate only **2014+** (near-national revised coverage), or
- validate within a **revised-only reporting area** if the official table defines one (then use `resident_revised`).

### Step 3: Record targets in a CSV (auditable)

Edit:

- `metadata/external_validation_targets_v1.csv`

Fill in `expected_value`, `tolerance_abs`, and a precise `value_source` (table name/number + publication).

### Step 4: Run the comparison script

```bash
python scripts/05_validate/compare_external_targets_v1.py
```

Outputs:

- `output/validation/external_validation_v1_comparison.csv`
- `output/validation/external_validation_v1_comparison.md`

### Step 5: Treat failures as actionable bugs or documented differences

If a comparison fails:

- confirm universe alignment (resident vs occurrence, resident-only vs all births)
- confirm definition alignment (gestation source break at 2014; sentinel codes; category mappings)
- if still failing, either fix the pipeline/metadata or document the reason as a V1 limitation (with a clear “do not use for trend” note in `docs/COMPARABILITY.md` and `metadata/harmonized_schema.csv`).

## Internal invariants (regression checks)

Deterministic internal invariants scan that should always pass unless a regression is introduced.

Run:

```bash
python scripts/05_validate/validate_v1_invariants.py \
  --in output/harmonized/natality_v2_harmonized_derived.parquet --years 1990-2024
```

Outputs:

- `output/validation/invariants_report_v2_1990_2024.md` (V2 natality)
- `output/validation/invariants_year_summary_v2_1990_2024.csv` (V2 natality)
- `output/validation/invariants_report_v3_linked_2005_2023.md` (V3 linked)
- `output/validation/invariants_year_summary_v3_linked_2005_2023.csv` (V3 linked)

This script runs 41 deterministic invariant checks (V2 natality; V3 linked skips 3 V2-only coverage invariants and allows `record_weight_null_when_survivor ≤ 2` as a documented upstream NCHS quirk — see `docs/COMPARABILITY.md`):

- **plausible range checks**: birthweight 100–8165g after cleaning; gestation 12–47 weeks after cleaning; apgar 0–10 after cleaning; year in target range
- **internal consistency of derived fields**: LBW = (birthweight_grams_clean < 2500), preterm = (gestational_age_weeks_clean < 37), singleton = (plurality_recode == 1), each verified rowwise
- **smoking any/intensity consistency** (scoped to 2003+ where smoke_any is derived from intensity; 1990–2002 exempt because TOBACCO and CIGAR6 are independent source fields)
- **Hispanic origin ↔ bool**: hisp_origin=0 must give hispanic=False; 1–5 must give True; 9 must give null
- **race_ethnicity_5 must be "Hispanic" when hispanic=True**; and must be non-null when hispanic is known AND the detail race code is in the mappable range (catches the 2020+ reconstruction regressing)
- **race_ethnicity_5 NH mapping**: bridged4=1 ↔ NH_white, 2 ↔ NH_black, 3 ↔ NH_aian, 4 ↔ NH_asian_pi
- **gestation source rules** (no obstetric-estimate source prior to 2014)
- **certificate revision validity** (2014+ must be revised_2003; values must be one of three allowed strings; never null)
- **sentinel clean consistency**: `ga_clean`, `bw_clean`, `apgar5_clean` must be null when the raw field equals its sentinel (99, 9999, 99)
- **preservation of known structural coverage constraints**: 2009–2013 unrevised records must remain missing for revised-only domains (education, pn-month, smoke-intensity)
- **era-coverage constraints for 2014+-only variables**: congenital anomalies, infections, fertility treatment, assisted-reproductive-tech must be null pre-2014; pre_pregnancy_diabetes, gestational_diabetes, nicu_admission, weight_gain_pounds, induction_of_labor, breastfed_at_discharge null pre-2014
- **father demographics**: father_hispanic=True must imply father_race_ethnicity_5=="Hispanic"; father_education_cat4 null 1995–2008
- **payment source**: null pre-2009
- **prior_cesarean_count**: null pre-2005; never takes the sentinel 99 post-2014 (the harmonizer maps 99→null)
- **delivery_method_recode allowed-value set**: {1,2,3,4,9} for 1990–2004; {1,2,9} for 2005+ — catches any crosswalk regression
- **record_weight null only for documented survivors**: V3 linked quirk — exactly 2 survivor rows (1 in 2014, 1 in 2015) have null record_weight per upstream NCHS data
- **null-rate discontinuity detection** (informational, not hard-fail): for 18 key harmonized variables, computes per-year null rates and flags any >5 percentage-point year-over-year change. Expected breaks (marital at 2017, smoking at 2009/2014, education at 2009/2014, race_bridged4 at 2020) are catalogued in `docs/COMPARABILITY.md` §"Known pitfalls".

### Field-position provenance

Every field position in `scripts/01_import/field_specs.py` was verified against the corresponding NCHS User Guide PDF (`raw_docs/Nat{year}doc.pdf` for 1990–2004, `raw_docs/UserGuide{year}.pdf` for 2005–2024) and spot-checked byte-by-byte against the raw zips. Notable positions that differ from a naive "look up the 2005 spec and use it for everything nearby" approach:

- **2004 `ATTEND`**: byte 408 (same as 2003). The 2004 file's record length matches 2005 (1500 bytes), but the ATTEND field didn't migrate to 410 until 2005.
- **`FAGECOMB` and `RF_CESAR` (unrevised/revised transition in the dual-cert era)**: both are revised-certificate-only fields that first appear at the start of the 2005–2013 layout. `RF_CESAR` at byte 324 is populated on 30.8% of 2005 births, ramping with cert adoption to 90.2% by 2013 and ~96–100% from 2014+ (see `docs/FAQ.md` "Why is `prior_cesarean` null for 1990–2004…"). `FAGECOMB` at bytes 182–183 is populated on revised-cert rows too — but while both `UFAGECOMB@184-185` (unrevised) and `FAGECOMB@182-183` (revised) coexist 2005–2011, NCHS blanked `UFAGECOMB` starting 2012, so the harmonizer switches from `UFAGECOMB` to `FAGECOMB` at that year. Raw `FAGECOMB` is 88.26% nonblank in 2012 and 90.45% in 2013 (matching that year's revised-cert share exactly); after the harmonizer maps sentinel 99→null, the resulting `father_age` column is populated on ~77% (2012) and ~79% (2013) of rows.
- **2014–2015 `URF_DIAB`/`URF_CHYPER`/`URF_PHYPER`**: bytes 1331–1333. Present only in the 2014 and 2015 User Guides; removed from 2016+ layouts (bytes 571–1330 are `FILLER_X` from 2016 onward, so the harmonizer switches to `RF_PDIAB`/`RF_GDIAB`/`RF_PHYPE`/`RF_GHYPE` at bytes 313–316 for 2016+).
- **Linked 2005–2013 `BRTHWGT`**: bytes 467–470 (vs. natality `DBWT` at 463–466). The linked files use the imputed `BRTHWGT` instead of `DBWT`.
- **Linked 2016–2023 merge key**: `(CO_SEQNUM@365-371, CO_YOD@372-375)` per the NCHS period-cohort user guide — composite, not CO_SEQNUM alone.

## V3: Linked birth-infant death validation (2005–2023)

### Row counts and parsing validation

Run:

```bash
python scripts/05_validate/validate_linked_parquets.py --years 2005-2023
```

Outputs:

- Range-labeled CSV/MD summaries under `output/validation/` (filenames reflect the year range used)
- Current full-range outputs: `linked_validation_2005_2023.csv` and `linked_validation_2005_2023.md`

This script checks:

- **Row-count correctness**: Parquet rows match zip size-implied rows across the full 2005-2023 linked scope
- **Layout correctness**: DOB_YY matches expected year at 100%; byte-level field position spot checks
- **Missingness sanity**: death fields (AGED, UCOD) blank for survivors, filled for deaths — exact alignment with FLGND
- **Frequency/IMR trend**: IMR falls from 6.74 (2005) to 5.49 (2023) in the full linked files, remaining in the expected low-5 to mid-6 range
- **Linked vs natality row counts**: exact for 14/19 years; small positive differences occur only in 2005, 2006, 2008, 2011, and 2012 due to LATEREC

### External validation (linked)

Targets: `metadata/external_validation_targets_v3_linked.csv` — 35 active targets across 2005, 2010, 2015, and 2020-2023.

Run:

```bash
python scripts/05_validate/compare_external_targets_v3_linked.py
```

Outputs:

- `output/validation/external_validation_v3_linked_comparison.csv`
- `output/validation/external_validation_v3_linked_comparison.md`

**Results: 35/35 active targets pass.** An additional 4 targets (2021 neonatal/postneonatal deaths and IMR components) are commented out in `metadata/external_validation_targets_v3_linked.csv` and not counted in the 35; see the note further down ("The 4 excluded 2021 split targets…") for the 131-death discrepancy that remains unresolved.

Cross-checked against linked file user guides (`LinkCO05Guide.pdf`, `LinkCO10Guide.pdf`, `LinkCO15Guide.pdf`, `21PE20CO_linkedUG.pdf`, `22PE21CO_linkedUG.pdf`, `23PE22CO_linkedUG.pdf`, `24PE23CO_linkedUG.pdf`):

- 2005 and 2010: resident births and weighted infant death counts match the user guides exactly.
- 2015: resident births, IMR, and neonatal deaths match exactly; unweighted infant deaths and postneonatal deaths differ by 1 record but pass within tolerance.
- 2020: all active births/deaths/IMR/neonatal/postneonatal targets match exactly.
- 2021: resident births, unweighted infant deaths, and IMR match exactly.
- 2022 and 2023: all active births/deaths/IMR/neonatal/postneonatal/neonatal-IMR/postneonatal-IMR targets match exactly.

Notes:
- 2005 and 2010 user guides report **weighted** infant death counts. 2015 and 2020-2023 user guides report **unweighted** (explicitly labeled).
- 2015 and 2020-2023 guides: "For cohort file use: do not apply the weight."
- The 1-record differences in 2015 are likely LATEREC edge cases and are not a concern.
- The 4 excluded 2021 split targets (`neonatal_deaths`, `postneonatal_deaths`, `neonatal_imr_per_1000`, `postneonatal_imr_per_1000`) remain unresolved: our data show 12,489 neonatal / 7,476 postneonatal deaths versus 12,620 / 7,345 in the user guide, while total deaths match exactly.
- 2016-2023 use period-cohort format (separate numerator/denominator files merged by CO_SEQNUM); 2005-2015 use denominator-plus format.

### IMR trend (residents, 2005–2023)

| Year | Births | Deaths | IMR | Neonatal IMR | Postneonatal IMR |
|------|--------|--------|-----|-------------|-----------------|
| 2005 | 4,138,577 | 27,893 | 6.74 | 4.47 | 2.27 |
| 2006 | 4,265,593 | 28,278 | 6.63 | 4.40 | 2.23 |
| 2007 | 4,316,233 | 28,725 | 6.66 | 4.33 | 2.32 |
| 2008 | 4,247,726 | 27,492 | 6.47 | 4.23 | 2.24 |
| 2009 | 4,130,665 | 25,793 | 6.24 | 4.11 | 2.13 |
| 2010 | 3,999,386 | 24,156 | 6.04 | 3.99 | 2.05 |
| 2011 | 3,953,591 | 23,547 | 5.96 | 4.00 | 1.95 |
| 2012 | 3,952,842 | 23,378 | 5.91 | 3.98 | 1.94 |
| 2013 | 3,932,181 | 23,142 | 5.89 | 3.99 | 1.89 |
| 2014 | 3,988,076 | 23,256 | 5.83 | 3.91 | 1.92 |
| 2015 | 3,978,497 | 23,327 | 5.86 | 3.91 | 1.95 |
| 2016 | 3,945,875 | 22,893 | 5.80 | 3.85 | 1.95 |
| 2017 | 3,855,500 | 22,167 | 5.75 | 3.84 | 1.91 |
| 2018 | 3,791,712 | 21,346 | 5.63 | 3.75 | 1.88 |
| 2019 | 3,747,540 | 20,639 | 5.51 | 3.65 | 1.85 |
| 2020 | 3,613,647 | 19,346 | 5.35 | 3.53 | 1.82 |
| 2021 | 3,664,292 | 19,965 | 5.45 | 3.41 | 2.04 |
| 2022 | 3,667,758 | 20,268 | 5.53 | 3.53 | 2.00 |
| 2023 | 3,596,017 | 19,743 | 5.49 | 3.59 | 1.91 |

The 2021 neonatal and postneonatal rates above are computed from the linked file itself; they are shown for trend context but excluded from external target validation until the 131-death split discrepancy is resolved.

### Reproduce linked harmonized + derived outputs

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

# Harmonize and derive
python scripts/03_harmonize/harmonize_linked_v3.py --years 2005-2023
python scripts/04_derive/derive_linked_v3.py

# Validate
python scripts/05_validate/validate_linked_parquets.py --years 2005-2023
python scripts/05_validate/compare_external_targets_v3_linked.py
```
