# About This Release: Version 2 (in-repo state: V3a)

## Overview

Version 2 of the U.S. Fetal Death Harmonization Project provides a researcher-ready, harmonized microdata file covering **1989 through 2022** — thirty-four consecutive years of NCHS fetal death records, since the V2.1 (2003+2004 transition) and V3a (1989-1991 backward extension) increments. The base V2 deposit at the v2.0.0 Zenodo DOI covers 1992-2022 with 2003/2004 deferred; the in-repo state has since landed V2.1 (2003+2004) and V3a (1989-1991) and ships from this monorepo. The release contains **~1.93M total records** with **73 harmonized variables** in the base file and **16 additional derived analysis variables** (89 columns total) in the derived file.

## V3a (2026-05-12): backward extension to 1989

V3a adds three years (1989, 1990, 1991) to the fetal-death series under the same 1989-revision uniform layout as V2.0. Records added: **188,909** (61,295 + 64,349 + 63,265). All three years are byte-position-identical to the 1992 benchmark; layout reusability verified by record-length probe + page 5-6 Data Elements cross-check + per-year record-count parity with each year's NCHS user-guide page 7 control block. The B3 maternal_race_bridged recode map was extended to handle two 1989-revision-only MRACE codes (`08` Other Asian/Pacific Islander → 4 API; `09` All other Races → null, consistent with how 1993+ Unknown is handled). All other B1/B2/B4/B6 recode maps unchanged. V3a validation gate: all 3 per-year fetal-death counts (≥20wk, residents) match each year's user-guide control-count block byte-exact (1989=30469, 1990=31386, 1991=30160). V1 era 2005-2022 byte-clean regression verified (55/55 still PASS, 0 column drift). See `V3a_1989_1991_LAYOUT_DECISIONS.md` for full layout reusability evidence, B3 extension rationale, and code-system mapping decisions.

**Total external validation post-V3a: 81/81 PASS** (V2-era 26/26 + V1-era 55/55).

## V2.1 (2026-05-12): the 2003-2004 transition years

V2.1 adds two years (2003, 2004) that were deferred from V2.0 because of their distinct transition-year layouts (1351-byte and 1501-byte records with mixed 1989/2003-revision content). Records added: **107,782** post-canonical-filter (NCHS-errata B7 correction restoring 26,004 / 26,001 byte-exact against `fetaldeath0304problems.pdf` Table 1). Five demographic/filter columns (`tabulation_flag`, `residence_status`, `maternal_age`, `maternal_race_bridged`, `hispanic_origin`) were cast from `object` to nullable Int (closes the H8 schema-vs-data dtype drift surfaced at Task 2). The `data_year` column initialization bug was fixed (a latent crosswalk's `derived` row would silently overwrite the int32 init with empty-string object). Monorepo path drift on `harmonize.py` + `validate_external*.py` was re-pointed to the flattened layout. The 2003-revision MAGER vs MAGER41 byte-position-semantic mismatch at bytes 89-90 is documented; `maternal_age` is intentionally null for 2003+2004 records (downstream consumers should use `maternal_age_recode14` for age-stratified analyses spanning those years). See `V2_1_2003_2004_LAYOUT_DECISIONS.md` for full V2.1 details.

## V2.0 (2026-05-05): the original 11-year backward extension

V2 extends V1 (2005-2022, 933,491 records, originally completed 2026-04-19) backward by adding the eleven uniform 1989-revision years (1992-2002, 700,704 records). The same 73-column harmonized schema, the same 16 derived variables, and the same parquet file shape are preserved. V1's 2005-2022 slice is **byte-identical** to the V1 baseline (verified after every V2 fix: 0 / 73 harmonized + 0 / 89 derived columns drifted).

No comparable longitudinal product for U.S. fetal death data has previously been available in the public domain.

## What Was Done in V2

**Layout reconstruction for 1992-2002.** The eleven 1989-revision years share a uniform 360-byte fixed-width layout (362 bytes per physical line including CRLF). The layout was reconstructed from the 1992 NCHS Fetal Death User Guide (OCR-cleaned against the cleaner 1998 and 2002 guides) and verified byte-by-byte: 98,500 raw-byte-to-parquet field comparisons across 10 years × 50 records × 197 fields, with **0 mismatches**. Three known stale-guide years (1996, 2001, 2002) — where the user guide control-count blocks were copy-pasted from adjacent years — were resolved against NVSR 57-08 (which gave the authoritative published counts) and the parsed counts matched NVSR exactly.

**Cross-era V2 code-system fixes (B1-B6 plus comparability relabels).** Eight harmonized columns received V2-era updates to bridge the 1989-revision (V2) and 2003-revision (V1) coding systems. Five are **value-level normalizations** (V2 raw codes mapped to V1 codes inside `harmonize.py`); three are **comparability relabels** (column tagged `within_era` or `partial` because the underlying concepts are not 1:1 mappable):

| Fix | Type | Column | What changed |
|---|---|---|---|
| **B1** | normalization | `fetal_sex` | V2 numeric `1/2/9` recoded to V1 alphabetic `M/F/U` |
| **B2** | normalization | `delivery_method_recode` | V2 6-category DELMETH6 collapsed to V1 3-category DMETH_REC: `{1,2}→1`, `{3,4,5}→2`, `6→9`. Full 6-cat detail preserved in yearly raw parquets. |
| **B3** | normalization | `maternal_race_bridged` | Crosswalk switched from MRACE3 (3-cat, collapses AIAN+API into "Other") to MRACE (2-digit detail); harmonize recodes V2 codes 01→1 White, 02→2 Black, 03→3 AIAN, 04-78→4 API, 99→blank Unknown. |
| **B4** | normalization | `paternal_age_recode11` | V2 12-category FAGE11 (`10=55-59`, `11=60-98`, `12=Unknown`) collapsed to V1 11-category FAGEREC11 (`10=55+`, `11=Unknown`): `{10,11}→10`, `12→11`. Full 12-cat detail preserved. |
| **B5** | **relabel** (not a normalization) | `breech_unrevised` | Re-labeled `partial → within_era` because V2 BREECH = "Breech/Malpresentation" (broader concept) vs V1 ULD_BREECH = "Breech Delivery" (narrower concept). Verified in 1998 user guide p.57 + 2006 user guide p.28. Cross-era groupby on this column conflates two distinct clinical concepts. |
| **B6** | normalization | `delivery_place_recode` | V2 raw PLDEL2 only has 2 codes (Hospital / Not in hospital incl Unknown); harmonize re-derives from raw PLDEL (`{1,3}→1`, `2→2`, `9→3`) to recover V1's 3-bucket Hospital/Not/Unknown scheme. 603 V2 unknowns now in their own bucket. |
| (additional) | **relabel** | `delivery_place_unrevised` | Re-labeled `partial → within_era` because V2 PLDEL (4 categories) and V1 UBFACIL (5 categories) use incompatible place taxonomies — codes 2 and 3 mean different things across eras. |
| (additional) | **relabel** | `maternal_age` | Re-labeled `full → partial` because V2 DMAGE is exact single-year (10-54 observed) whereas V1 MAGER top/bottom-codes 50+ and 12-. 150 V2 rows fall outside the V1 boundary-coded range (108 at age 50-54; 42 at age 10-11). |

**Summary**: 5 V2 value-level normalizations (B1, B2, B3, B4, B6) + 3 comparability relabels (B5, `delivery_place_unrevised`, `maternal_age`). One additional standing `within_era` column carried unchanged — `maternal_race_bridged_detail` — was already tagged `within_era` because V2 raw 1989-rev MRACE codes vs V1 2006 raw MBRACE codes use the same numerics for different ethnic subgroups.

**version_flag synthesis.** The 1992-2002 raw files have no native VERSION field (the 1989 revision was the only revision in use at the time). Per the crosswalk's explicit instruction, harmonize.py synthesizes `version_flag = 'S'` for all 700,704 V2 records so downstream filters like `version_flag == 'S'` for NVSR-comparable subsets behave consistently across eras.

**Empty-by-design columns for V2 (37 columns).** Variables that did not exist in the 1989-revision Standard Report of Fetal Death are intentionally blank for the V2 slice: BMI, maternal nativity, prepregnancy diabetes/hypertension/eclampsia (revised), revised tobacco detail, multi-race recodes, ICD-10 cause-of-death fields, obstetric-estimate edited gestation, fetal presentation, etc. These columns remain populated for V1 records (where the underlying revised fields exist) and are documented as `within_era` in the schema.

**Derived variable behavior for V2.** All 16 derived variables compute correctly on V2 with the V2 sentinels handled appropriately. Two derived variables are intentionally blank for the V2 slice: `education_cat4` (V2 populates `maternal_education_unrevised` years-of-school instead of the revised 1-9 categorical scale that the derivation maps from) and `cause_group` (no ICD-10 cause data in V2 public-use files).

**External validation against NVSR 57-08.** The MacDorman et al. NVSR 57(8) "Fetal and Perinatal Mortality, United States, 2005" report tables A and B publish authoritative counts and rates for 1995-2005. All eight per-year V2 counts (1995-2002) and all eight per-year V2 rates match exactly. For 1992-1994 (a documented gap in the NVSR Fetal & Perinatal Mortality series), the user guide control-counts are the authoritative source and all three match exactly. **Total V2 external validation: 19/19 exact matches.**

## Key Output Files

In the Zenodo deposit these are all at the deposit root; in the GitHub source repository they live under `output/` and `metadata/` as shown in parentheses below.

| File (Zenodo flat) | GitHub path | Description |
|---|---|---|
| `fetal_death_harmonized.parquet` | `output/harmonized/` | 1,634,195 rows × 73 columns — base harmonized file (1992-2002 + 2005-2022) |
| `fetal_death_derived.parquet` | `output/harmonized/` | 1,634,195 rows × 89 columns — base + 16 derived variables |
| `fetal_death_yearly_raw_1992-2022.zip` (29 files inside) | `output/yearly_clean/` | 29 raw per-year Parquet files preserving every documented field (including the 6-category DELMETH6, 12-category FAGE11, broader "Breech/Malpresentation" BREECH, etc., for users who need the full 1989-revision detail) |
| `harmonized_schema.csv` | `metadata/` | Variable definitions with allowed_values, comparability_class, source columns by era — refreshed 2026-04-22 to reflect V2 ranges and B-fix derivations |
| `variable_crosswalk_working.csv` | `metadata/` | Raw-to-harmonized mapping across all 4 eras (1992, 2006, 2014, 2022) |
| `record_layout_1992.csv` | `metadata/` | Full 1989-revision 360-byte layout (197 data fields + 15 FILLER ranges) |
| `reporting_thresholds.csv` | `metadata/` | State-by-year reporting threshold documentation |

## Validation Summary

The shipped parquet was validated against every per-year fetal death figure NCHS has published, plus a 55-cell detail-cell sample from NVSR 73-09. All checks use the standard `tabulation_flag=='2' & residence_status!='4'` filter.

- **Per-year fetal death counts (1992-2022):** 29 of 29 reproduce the published source figures exactly. 1995-2002 against NVSR 57-08 Tables A and B; 2005-2020 against NVSR 73-09; 1992-1994 against the NCHS user-guide control-count blocks (which are the authoritative source for those three years, since the NVSR Fetal & Perinatal Mortality series begins at 1995). The three known stale-guide V2 years (1996, 2001, 2002) — where the user-guide control counts were copy-pasted from adjacent years — are resolved against NVSR 57-08, and the parsed counts match NVSR exactly.
- **Per-year fetal mortality rates (1995-2022):** 26 of 26 match the published source figures exactly.
- **NVSR 73-09 detail-cell tabulations (Tables A, 4, 8 and early/late GA from Table 1; 2014 and 2022):** 13 of 19 cells match exactly; the remaining 6 differ for documented methodological or framing reasons (4 early/late gestational-age cells where NVSR proportionally redistributes records with unknown gestational age between strata; 2 cause-of-death cells where NVSR Table 8 restricts to a 43-state reporting area while the harmonization includes all states). None are byte-level mismatches in the harmonized data.
- **V1 byte-clean regression:** the 2005-2022 slice of the harmonized parquet remained cell-identical to its V1.x baseline through the V2 backward-extension to 1992 (0 of 73 harmonized + 0 of 89 derived columns drifted), so V2 did not perturb any existing V1-era analysis.
- **Byte-level parse verification (1992-2002):** 98,500 raw-byte-to-parquet field comparisons across 10 years × 50 records × 197 fields, with 0 mismatches.

Per-target source citations are in `external_validation_targets.csv`; the per-target pass/fail table is in `validation_results.csv`. Independent verification scripts are shipped in `scripts/05_validate/`; see `README.md` §Validation for the three-level verification ladder users can run themselves.

## What Is Not in Version 2

- **2003 and 2004 transition years.** Both years have distinct, non-uniform transition layouts (1351-byte and 1501-byte records respectively, with mixed 1989/2003-revision content) that require dedicated handling. NCHS publishes a separate `fetaldeath0304problems.pdf` (downloadable from the CDC FTP server alongside the year zips) documenting their idiosyncrasies. These are deferred to V2.1.
- **Years before 1992.** 1982-1991 use earlier layouts and will be added in V3.
- **ICD-9 cause-of-death coding (1992-2013).** Cause of death is not present in the public-use fetal death files for any year before 2014. Pre-2014 ICD codes are only available through the NCHS Research Data Center (restricted-use, multi-month application). The 2006 user guide states this directly on p. 54: *"Cause-of-fetal-death data are also not currently available."* This is a structural limitation of the source data, not a pipeline gap.
- **State-level geographic identifiers.** State of occurrence and state of residence are suppressed in the V1-era public-use files (2005+) and therefore cannot be included for those years. The V2 era (1992-2002) **does** carry state codes in the raw yearly parquets (STATEFET, STATERES, STOCCFIP, etc., per the 1989-revision layout) which is how the OK/MD/MA Hispanic-non-reporting and Louisiana plurality-non-reporting quirks are documentable; users who need state-level analysis for V2 can work directly with the per-year raw parquets bundled in `fetal_death_yearly_raw_1992-2022.zip`.
- **Cross-era education bridge.** V2 populates `maternal_education_unrevised` (years-of-school 00-17) while V1 populates `maternal_education` (revised 1-8 categorical). No 1989→2003 binning bridge is currently provided, so the derived `education_cat4` is blank for V2. Building the bridge is a deliberate non-goal for V2 — the year-of-schooling and degree-level concepts are not 1:1 mappable, and any bridge would impose modeling choices best left to the analyst.
