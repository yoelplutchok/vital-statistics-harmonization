# V3a Layout Decisions: 1989-1991 Backward Extension

This document records the layout reusability verification and the single code-system extension that the V3a fetal-death backward extension required. V3a brings fetal-death coverage from 1992-2022 (31 years; V2.0 + V2.1) to **1989-2022 (34 years)** by parsing the three 1989-revision years that predate the existing 1992 benchmark.

V3a is **layout-additive**: no schema change, no new harmonized variables, no derived-variable logic change. The 1989-revision Standard Report of Fetal Death — issued by NCHS effective with 1989 data and used through the 2002 data year — is the same data dictionary already documented in `record_layout_1992.csv` and parsed by `FETAL_1992_2002_FIELDS` (now renamed in spirit to "1989-revision uniform 1989-2002 layout"; the constant name `FETAL_1992_2002_FIELDS` is preserved to minimize edit surface).

## Empirical layout reusability evidence

Three independent verifications confirm 1989-1991 are byte-position-identical to 1992-2002 under the 1989-revision uniform layout:

1. **Record length**: `unzip -p Fetal{1989,1990,1991}US.zip | head -1 | wc -c` returns 361 bytes (360 data + 1 newline) for all three years, matching `RECORD_LEN_1992 = 360`.

2. **Page 5-6 Data Elements list cross-check** (L9 cheap-check): the "List of Data Elements and Tape Locations" tables in `1989FetalUserGuide.pdf` / `1990FetalUserGuide.pdf` / `1991FetalUserGuide.pdf` enumerate fields at byte positions identical to `1992FetalUserGuide.pdf` for every comparison-eligible field. NCHS's 2009 PDF rescan batch includes an embedded OCR text layer that PyMuPDF extracts cleanly; verification was scripted, not visual. Examples:
   - Data year → bytes 1-4 (all 4 guides)
   - Tabulation flag → byte 5
   - Record type → byte 6
   - Resident status → byte 7
   - NCHS state of occurrence → bytes 17-18
   - NCHS state of residence → bytes 33-34
   - Mother age → bytes 69-76 + recode at 87-88
   - Mother race → bytes 79-81
   - Method of delivery → bytes 220-226
   - Medical risk factors → bytes 228-244
   - Congenital anomalies → bytes 279-300
   - SMSA → bytes 357-359 (NCHS terminology shift "SMSA"→"MSA" between 1989 and 1990 at the same byte position is semantic-equivalent; both denote the metropolitan statistical area code)

3. **Per-year record-count parity with user-guide control block** (Tier-2 SMOKE pass): parser-produced row counts equal NCHS user-guide page 7 "Record count" byte-exact for all three years:

   | Year | Parsed records | User-guide page 7 | Match |
   |---|---:|---:|---|
   | 1989 | 61,295 | 61,295 | ✓ |
   | 1990 | 64,349 | 64,349 | ✓ |
   | 1991 | 63,265 | 63,265 | ✓ |

4. **Canonical-filter aggregate parity** (Tier-3 SMOKE pass): `TABFLG=='2' AND RESTATUS!='4'` count from the parsed yearly_clean parquet equals the user-guide page 7 "20 WEEKS AND OVER: By residence" figure byte-exact:

   | Year | Computed (filter) | User-guide control | Match |
   |---|---:|---:|---|
   | 1989 | 30,469 | 30,469 | ✓ |
   | 1990 | 31,386 | 31,386 | ✓ |
   | 1991 | 30,160 | 30,160 | ✓ |

## The one code-system extension: B3 maternal_race_bridged

The B3 maternal_race_bridged value-level normalization required a 2-code extension to accommodate the 1989-revision MRACE coding scheme, which is the only 1989-revision field whose value codes diverge from the 1992+ scheme on this layout.

Per the 1989 NCHS Fetal Death User Guide (`1989FetalUserGuide.pdf` page 28, item 79-81), 1989-revision MRACE uses a 9-category coding:

| Code | Definition (1989-revision) |
|---|---|
| 01 | White |
| 02 | Black |
| 03 | American Indian (includes Aleuts and Eskimos) |
| 04 | Chinese |
| 05 | Japanese |
| 06 | Hawaiian (includes Part-Hawaiian) |
| 07 | Filipino |
| 08 | Other Asian or Pacific Islander |
| 09 | All other Races |

The 1989 user guide explicitly states: *"Race codes effective with 1989 data differ from previous years."* This is the canonical 1978-revision → 1989-revision API-detail expansion. The 1989-revision codes 04-08 cover specific Asian/Pacific Islander subgroups; code 09 is a residual "All other Races" catch-all.

In **1992 and later** files (also under the same 1989-revision Standard Report), NCHS introduced a parallel 2nd-digit scheme to allow finer API granularity within the same 2-byte field: 18, 28, 38, 48, 58, 68, 78 — and code 99 "Unknown/Not stated" replaced the 09 residual. The 1992+ MRACE codes are 01-07 + 18-78 + 99.

### B3 extension

The B3 recode map in `fetal_death/scripts/03_harmonize/harmonize.py` (the V2 era's MRACE → maternal_race_bridged 4-category collapse) is extended for V3a with two entries:

| MRACE raw code (1989-1991) | maternal_race_bridged | Rationale |
|---|---|---|
| `08` | `4` (API) | Code 08 ("Other Asian or Pacific Islander") is unambiguously API and maps to the same bridged group as 04-07 and the 1992+ codes 18-78. |
| `09` | `""` (null/unknown) | Code 09 ("All other Races") is a residual that doesn't fit the 4-category bridged scheme (White / Black / AIAN / API). Per NCHS convention and consistent with how the 1993+ "Unknown" code 99 is handled, code 09 records receive `null` for the bridged variable. They are preserved in the parquet for unbridged-race analyses. |

### Record-count impact of the 09→null decision

| Year | Records with MRACE='09' | Fraction of year total |
|---|---:|---:|
| 1989 | 34 | 0.055% |
| 1990 | 72 | 0.112% |
| 1991 | 59 | 0.093% |
| **Total V3a** | **165** | **0.087%** |

These 165 records have `maternal_race_bridged = null` post-harmonize. Race-stratified analyses on the V3a years will exclude these records consistently with how 1993+ Unknown-race records are excluded; analyses that don't require bridged race (e.g., totals, year trends, gestational-age distributions) are unaffected.

## Other 1989-revision fields: no extension needed

The other four V2 cross-era code-system fixes (B1 fetal_sex, B2 delivery_method_recode, B4 paternal_age_recode11, B6 delivery_place_recode) read raw fields whose value distributions in 1989-1991 are byte-identical to those in 1992 (FSEX={1,2,9}; DELMETH6={1-6}; FAGE11={01-12}; PLDEL={1,2,3,9}; PLDEL2={1,2}). The existing B1/B2/B4/B6 recode maps cover all observed codes in 1989-1991. Verified by per-year distribution sanity at PRE-FLIGHT.

## Validation source for 1989-1991

The NVSR Fetal & Perinatal Mortality series (NVSR 57-08 and successors) begins at data year 1995. For 1989-1991 — a 6-year gap before NVSR series coverage — the authoritative external reference is **each year's NCHS Fetal Death User Guide control-count block on page 7** ("20 WEEKS AND OVER: By residence"), the same source used for 1992-1994 in the existing pre-V3a validation. The three V3a control counts (30,469 / 31,386 / 30,160) are recorded in `external_validation_targets.csv` and gate `validate_external_v2.py` (now 26/26 PASS, up from 23/23 at V2.1).

## Files touched by V3a

| File | Edit |
|---|---|
| `fetal_death/scripts/01_import/field_specs.py` | Extend `layout_for_year(year)` to dispatch 1989-1991 to `FETAL_1992_2002_FIELDS`; docstring + section comment year range 1992-2002 → 1989-2002. |
| `fetal_death/scripts/03_harmonize/harmonize.py` | Extend `_era_tag()` from `1992 <= year <= 2002` to `1989 <= year <= 2002`; extend B3 map with `08→4` and `09→""`; update docstrings + error messages. |
| `fetal_death/scripts/05_validate/validate_external_v2.py` | Extend `GUIDE_FETAL_DEATHS_GTE20` dict with 1989/1990/1991 control counts; extend guide-based reference loop from `(1992, 1993, 1994)` to `(1989, 1990, 1991, 1992, 1993, 1994)`; extend version_flag filter from `1992 <= year <= 2002` to `1989 <= year <= 2002`. |
| `fetal_death/external_validation_targets.csv` | +3 rows (1989/1990/1991 fetal_deaths_gte20wk_resident = 30469 / 31386 / 30160). |
| `fetal_death/file_inventory.csv` | +3 rows (Fetal{1989,1990,1991}US.zip + doc_filename {Y}FetalUserGuide.pdf). |
| `fetal_death/ABOUT_THIS_RELEASE.md` | New "V3a (2026-05-12)" section documenting the +3-year backward extension. |
| `fetal_death/README.md` | Years covered + total records updated to V3a state. |
| `fetal_death/V3a_1989_1991_LAYOUT_DECISIONS.md` | This file (new). |
| Output parquets | `output/harmonized/fetal_death_harmonized.parquet` + `fetal_death_derived.parquet` re-derived at 34-year scope; new yearly_clean parquets for 1989, 1990, 1991. |

## What V3a does NOT do

- **Version-string bump** in `.zenodo.json` and `CITATION.cff`: deferred to Task 10 (Zenodo deposit) per the V2.1 precedent. In-repo work tracks "V3a" informally; formal version strings (currently still "v2.0.0" / "2.0.0") get the full v2.2.0 ripple at Zenodo-deposit time.
- **PROVENANCE.md SHA refresh**: deferred to Task 10. PROVENANCE.md documents the immutable v2.0.0 Zenodo deposit state; refreshing it pre-deposit would create a misleading manifest.
- **V3b backward extension to 1982-1988**: out of V3a scope. V3b uses the 1978-revision layout (200-byte records, fully bitmap-scanned NCHS user guides requiring OCR). A separate PRE-FLIGHT + DO is required if/when V3b is authorized.
- **harmonized_schema.csv `years_available` column extension**: not strictly required for V3a's behavior (the years_available strings are documentation only; downstream consumers use the data_year column directly). Bulk-extension of those strings can ride with Task 10's Zenodo-deposit polish.

## Reproducibility

V3a is reproducible from the public NCHS source files using:

1. Raw zip SHAs: see `file_inventory.csv` rows for 1989-1991 (downloaded from NCHS canonical FTP).
2. User-guide PDF SHAs: see PRE_FLIGHT_LOG.md task7_v3a entry (`54c55a40...`, `91573bf8...`, `311fc21c...` for 1989, 1990, 1991 respectively).
3. Pipeline: `scripts/run_pipeline.py --years 1989 1990 1991 ... 2022` (re-runs end-to-end).
4. Validation: `validate_external_v2.py` (gate 26/26) + `validate_external.py` (gate 55/55, V1 byte-clean regression).

Total: **81/81 external validation checks pass** at V3a (was 78/78 at V2.1; +3 V3a).
