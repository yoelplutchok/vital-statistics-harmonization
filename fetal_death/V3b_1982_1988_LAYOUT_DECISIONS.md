# V3b Layout Decisions: 1982-1988 Backward Extension

This document records the 1978-revision layout reconstruction and the two harmonization decisions the V3b backward extension required. V3b brings fetal-death coverage from 1989-2022 (34 years; V2.0 + V2.1 + V3a) to **1982-2022 (41 years)** by parsing the seven 1978-revision years that predate the 1989-revision V2 era.

V3b is **structurally distinct** from V2/V3a: the 1978-revision Standard Report of Fetal Death uses a 200-byte record layout with different field names, different byte positions, and different value-code schemes than the 1989-revision (e.g., 1-digit MRACE 0-9 vs 2-digit 01-99; AGE umbrella at bytes 81-85 vs 71-76; no Hispanic-origin field). A new layout CSV (`record_layout_1982_1988.csv`) and a new parser field list (`FETAL_1982_1988_FIELDS` in `field_specs.py`) were authored from `1985FetalUserGuide.pdf` pages 8-26 and validated against empirical anchor-field probes on 1982/1983/1985/1988 raw zips.

## Empirical layout reusability evidence

Three independent verifications confirm 1982-1988 are byte-position-uniform under the 1978-revision layout:

1. **Record length**: `unzip -p Fetal{1982..1988}US.zip | head -1 | wc -c` returns 202 bytes (200 data + CR+LF) for all seven years, matching `RECORD_LEN_1978 = 200`.

2. **Page 4/5/6 Data Elements list cross-year diff** (L9 cheap-check): the "List of Data Elements and Tape Locations" overview tables in `198{2..8}FetalUserGuide.pdf` are byte-identical across all seven years per the user-guide-text diff at PRE-FLIGHT 2026-05-12T15:45Z. NCHS's 2009-01-08 bulk re-OCR batch produced PDFs with embedded text layers; PyMuPDF extracts the layout tables cleanly without OCR pass. Anchor fields verified at every byte position in `record_layout_1982_1988.csv`.

3. **Per-year record-count parity with user-guide page-7 "Record count" block** (Tier-2 SMOKE pass): parser-produced row counts equal NCHS user-guide page-7 control byte-exact for all seven years:

   | Year | Parsed records | User-guide page 7 "Record count" | Match |
   |---|---:|---:|---|
   | 1982 | 62,352 | 62,352 | ✓ |
   | 1983 | 60,584 | 60,584 | ✓ |
   | 1984 | 59,863 | 59,863 | ✓ |
   | 1985 | 59,690 | 59,690 | ✓ |
   | 1986 | 59,343 | 59,343 | ✓ |
   | 1987 | 59,358 | 59,358 | ✓ |
   | 1988 | 59,935 | 59,935 | ✓ |
   | **Total V3b** | **421,125** | **421,125** | **✓** |

4. **Canonical-filter aggregate parity** (Tier-3 SMOKE pass): `TABFLAG=='2' AND RESTATUS!='4'` count from the parsed yearly_clean parquet equals the user-guide page-7 "20 WEEKS OR MORE: By residence" figure byte-exact for all seven years. The 1985 user guide's OCR-ambiguous `29,66I` was resolved empirically to `29,661`:

   | Year | Computed (filter) | User-guide control | Match |
   |---|---:|---:|---|
   | 1982 | 32,694 | 32,694 | ✓ |
   | 1983 | 30,752 | 30,752 | ✓ |
   | 1984 | 30,099 | 30,099 | ✓ |
   | 1985 | 29,661 | 29,661 | ✓ (OCR `29,66I` → digit-1 confirmed) |
   | 1986 | 28,972 | 28,972 | ✓ |
   | 1987 | 29,349 | 29,349 | ✓ |
   | 1988 | 29,442 | 29,442 | ✓ |
   | **Total V3b (resident, 20+wk)** | **210,969** | **210,969** | **✓** |

Two independent NVSR-equivalent statistics (record count + by-residence-20wk count) match byte-exact for all seven years. This is strong evidence that the 200-byte record length, TABFLAG byte 10, RESTATUS byte 12, and the underlying byte-position assignments are all correct. Layout reconstruction is empirically valid.

## Harmonization decision 1: DATAYEAR 2-digit → 4-digit expansion

1978-revision DATAYEAR (bytes 1-2) is a **2-digit string** ("82".."88" for data years 1982..1988); 1989-revision DATAYEAR (bytes 1-4) is a 4-digit string. The harmonized `delivery_year` column carries 4-digit strings across all eras for schema uniformity.

**Decision (Q28, 2026-05-12)**: expand in `harmonize.py` era=='1985' branch via `df["delivery_year"] = ("19" + s).astype(str)` where `s` is the 2-digit raw string. The crosswalk maps `delivery_year` → `field_1985=DATAYEAR (1-2)` directly; the expansion is a harmonization-step concern, not a parse-step concern. Defensive halt: if any raw DATAYEAR value is non-2-digit, `harmonize.py` raises `ValueError` listing the offending sample. (Option B — pre-process in `parse_fetal_year.py` — was rejected at PRE-FLIGHT because parse should preserve raw bytes; year-conversion is a harmonization concern.)

Verified post-DO: `delivery_year` column for V3b records contains exactly "1982".."1988" (no leakage of "82".."88" strings; no nulls; no non-numeric values).

## Harmonization decision 2: B3 maternal_race_bridged 1-digit recode

The 1978-revision MRACE field (byte 86, **1-digit code 0-9**) uses a different categorization scheme than the 1989-revision (bytes 79-80, 2-digit code 01-99). Per 1985 NCHS Fetal Death User Guide page 18 (MRACE field documentation):

| 1978-rev MRACE code | Definition |
|---|---|
| 0 | Other Asian or Pacific Islander |
| 1 | White |
| 2 | Black |
| 3 | American Indian / Aleut / Eskimo |
| 4 | Chinese |
| 5 | Japanese |
| 6 | Hawaiian |
| 7 | Other nonwhite |
| 8 | Filipino |
| 9 | Not stated |

**Decision (Q29, 2026-05-12)**: extend the B3 `_checked_remap` in `harmonize.py` era=='1985' branch with the following 1-digit-to-bridged mapping:

| 1978-rev MRACE | Bridged-race (4-cat) | Rationale |
|---|---|---|
| 1 | 1 (White) | Direct |
| 2 | 2 (Black) | Direct |
| 3 | 3 (AIAN) | Direct |
| 0, 4, 5, 6, 8 | 4 (API) | All API subgroups collapse into bridged-API (parallels V2 codes 18-78 → 4 mapping) |
| **7** | **null** | "Other nonwhite" is a 1978-rev residual catch-all that doesn't fit any 4-cat bridged bucket. **Parallels V3a's 09 → null choice** (DECISION_LOG 2026-05-12T14:30Z). Mapping to any specific category would be false categorization. |
| **9** | **null** | Not stated → null (same convention as V2 99 → null) |

**Cross-product effect of the null-mappings**: ~89 records across 1982-1988 are code 7 (per V3b yearly_clean Tier-2 value-distribution check); ~18,700 records are code 9 (~3.0-5.4% per year). All 18,789 records receive null `maternal_race_bridged` but are otherwise preserved in the parquet for unbridged analyses (year totals, GA distributions, plurality stratifications are unaffected; only race-stratified subgroups exclude them). This is consistent with how V2/V3a Unknown-race records are handled.

Verified post-DO: `maternal_race_bridged` value counts for V3b years contain exactly {1, 2, 3, 4, NaN}; no raw 0-9 codes leak through; `_checked_remap` would have raised if any code were unmapped.

## Other 1978-revision field divergences (not bridged)

For other harmonized fields, the V3b row in `variable_crosswalk_working.csv` points to the V3b raw field directly (no recode needed). Edge cases:

- **`plurality`**: V3b NUMDEL (1=Single; 2=Twin; 3=Triplet or higher) is **partial** vs V1 DPLURAL (1-5 with separate Triplet/Quadruplet/Quintuplet+). V3b code 3 conflates V1 codes 3-5 (~107 V3b records per year). Schema row already marks `plurality` as `partial`; V3b coverage adds a third reason for the partial label.
- **`live_birth_order`**: V3b LIVORD10 (10-cat with 0=No children) is byte-identical to V1 LBO_REC (10-cat 0-9). Direct wiring.
- **`paternal_age_recode11`**: V3b FAGE12 has the same 12-category structure as V2 FAGE11 (despite the V2 legacy name); same B4 collapse applies (10/11→10, 12→11).
- **`fetal_sex`**: V3b FSEX (1/2/9) → M/F/U via the same B1 recode as V2.
- **`delivery_place_recode`**: V3b PLDEL (1=Hospital; 2=Doctor/home/public; 3=En route; 9=Not classifiable) uses the same B6 recode as V2 to derive the V1 3-bucket scheme.

## Fields with no V3b counterpart (left null)

The 1978-revision public-use file does **not** contain the following 1989-rev+ fields; they remain null for 1982-1988 records:

- `hispanic_origin` (Hispanic-origin collection began effective 1989)
- `maternal_age_recode14`, `maternal_age_recode9` (V3b ships MAGE12 / MAGE8 instead)
- `maternal_race_multi`, `maternal_race_recode6` (multi-race recodes are 2014+)
- `maternal_education` (revised; 2003+); `maternal_nativity` (2014+)
- `prenatal_care_month` (revised; 2003+); `prenatal_care_recode` (2003+)
- `delivery_method_recode` (DELMETH not in 1978-rev PUF)
- `prepregnancy_diabetes` / `gestational_diabetes` / etc. (all 2003+ revised risk-factor items)
- `attendant`, `gestation_imputed_flag`, `birthweight_recode4`, `breech_unrevised` (not in 1978-rev PUF or have V3b-specific siblings)
- All cause-of-death fields (2014+ only)
- All 2014+ obstetric-estimate gestation fields

A complete list is in the schema CSV's `years_available` column for each harmonized variable; rows that include "1982-1988" are V3b-covered, rows that don't are V3b-null.

## version_flag synthesis

V3b synthesizes `version_flag = 'S'` for all 1982-1988 records (per `harmonize.py` era=='1985' branch). The 1978-revision predates the 1989/2003 revision-discriminator split, so 'S' (1989-revision/pre-2003) is the inclusive default. Researchers needing the 1978-vs-1989 distinction can filter on `data_year < 1989`.

## Cross-product re-probe

After the V3b harmonize+derive+validate cycle:

- `validate_external_v2.py` (V2-era extended for V3a+V3b): **33/33 PASS** byte-exact (23 counts 1982-2004 + 10 rates 1995-2004)
- `validate_external.py` (V1-era validator): **55/55 PASS** byte-exact (unchanged from V3a baseline; V1 era is post-V3b-fence)
- **V3a/V2/V2.1/V1 baseline byte-clean regression**: 0 of 162 columns (73 harmonized + 89 derived) drifted on the 1989-2022 data slice when comparing pre-V3b baseline vs post-V3b parquet
- **Total: 88/88 external validation PASS + V3a byte-clean preserved**

## What V3b does NOT do

- **PROVENANCE.md SHA refresh**: deferred to Task 10 (Zenodo deposit prep), per V3a precedent. Current PROVENANCE.md lists v2.0.0 SHAs; user verification will FAIL against current parquet files until Task 10's batched refresh.
- **Schema CSV `years_available` retroactive V3a-gap fix**: for V3a-only columns (e.g., a column wired in 1989-2002 but not in 1982-1988), the `years_available` string still says "1992-2002, …" rather than "1989-2002, …". Only V3b-covered rows received the conservative `1982-1988, …` prepend at DO step 6. The V3a gap remains deferred per V3a RECEIPT 2026-05-12T14:30Z item 8.
- **OCR pass on the V3b user guides**: not needed. The 1985 OCR feasibility PoC at STATUS 2026-05-12T15:00:00Z confirmed PyMuPDF text-layer extraction is sufficient; no tesseract pass required. The single ambiguity (`29,66I` → `29,661`) was resolved empirically by canonical-filter cross-check rather than by OCR correction.
- **Reverse-engineered field semantics**: every harmonized column wired in the V3b crosswalk has a user-guide-documented raw field. The L13-extension value-distribution discipline (per LESSONS L13-extension 2026-05-12T01:40:00Z) was applied: TABFLAG/RECTYPE/RESTATUS/MRACE/DMAGE distributions match the user-guide-documented coding for all seven years.

## Manuscript implications

Numbers that change with V3b:

- "Fetal death coverage 1989-2022 (34 years)" → **"1982-2022 (41 years)"**
- "1,930,886 total records" → **"2,352,011 total records"** (unfiltered) / **"1,989,184 NVSR-comparable (resident, 20+wk)"** (filtered)
- "Total external validation: 81/81 PASS" → **"Total external validation: 88/88 PASS"** (+7 V3b user-guide controls)
- New ABOUT_THIS_RELEASE section: "V3b 1982-1988 backward extension" alongside V3a section
- The V3b-induced 89-record code-7 + ~18,700-record code-9 null-bridged fraction (~1% of V3b race-stratified rows) is a footnote-worthy caveat for race-stratified time-series analyses crossing the 1989 boundary

These updates are out of V3b scope; bundled into the manuscript re-pass at KICKOFF sequence step 6.
