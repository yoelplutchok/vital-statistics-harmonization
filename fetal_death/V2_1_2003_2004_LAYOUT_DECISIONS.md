# V2.1 Layout Decisions: 2003 + 2004 Transition Years

Companion to `V2_1992_LAYOUT_DECISIONS.md`. Documents the decisions made when adding 2003 and 2004 fetal-death coverage to the harmonized file in V2.1 (built 2026-05-12, supersedes the v2.0.0 1992–2022-with-2003/2004-gap state).

## Why 2003 + 2004 were originally deferred

The 2003 and 2004 NCHS Fetal Death public-use files are transition-year layouts that differ substantially from both the V2 uniform 1989-revision layout (1992–2002) and the V1 mixed-revision layout that stabilized in 2005. NCHS shipped a layout-changed-substantially-from-2002 notice on page 1 of the 2003 User Guide. The two files use 1351-byte and 1501-byte records (vs 1350 for 2005–2006 and 360 for 1992–2002) and have both `S` (1989-revision) and `A` (2003-revision) records mixed in single files (2003: 53,503 S + 994 A = 1.8% A; 2004: 51,321 S + 1,964 A = 3.7% A).

## What was done in V2.1

### Record count and validation

Adding 2003 + 2004 brings fetal-death coverage to **31 consecutive years (1992–2022)** with **1,741,977 total records** (was 1,634,195 in v2.0.0). The two new years contribute 54,497 + 53,285 = 107,782 raw records.

External validation against NVSR 57-08 corrected totals (after applying the B7 NCHS-errata fix, see below):

| Year | Raw (originally reported) | Corrected (B7-applied) | NVSR target | Match |
|---|---|---|---|---|
| 2003 | 25,653 | 26,004 | 26,004 | ✓ byte-exact |
| 2004 | 25,655 | 26,001 | 26,001 | ✓ byte-exact |

Counts: 31/31 byte-exact (was 29/29). Rates: 28/28 byte-exact (was 26/26). V1-era 2005–2022 validation: 55/55 still passing (unchanged from v2.0.0 — re-verified after re-derive).

### B7 — NCHS-errata TABFLG correction

Source: `raw_docs/fetal_death/fetaldeath0304problems.pdf` (NCHS errata, ~2009). Quote from page 1:

> "Due to a programming error, the Tabulation Flag variable located in position 9 is incorrect in the 2003 and 2004 fetal death data files. This variable identifies fetal deaths of stated or presumed period of gestation of either <20 weeks, or 20 weeks or more. … Due to this error, some fetal death records with not stated gestational ages that should have been included in the 20 weeks or more group were erroneously assigned to the <20 week group."

The errata's SAS correction recipe is:

```sas
IF COMBGEST=99 and XOSTATE IN (43-state list) THEN TABFLG=2;
```

The 43 states named (page 1, SAS code block) are: AL, AK, AZ, CA, CT, DE, DC, FL, ID, IL, IN, IA, KS, KY, LA, ME, MD, MA, MI, MN, MS, MO, MT, NE, NV, NH, NJ, NM, NC, ND, OH, OK, OR, SC, SD, TN, TX, UT, VT, WA, WI, WV, WY. Verified count = 43 (the text in the PDF writes `'NH' 'NJ' 'NM'` without commas, which prompts a halt-recount risk; the count is unambiguously 43 cross-checked against Tables 2/3 per-state corrections).

The harmonize-time correction lives in `fetal_death/scripts/03_harmonize/harmonize.py` under the new `era == "2003"` block; it applies to bytes `OSTATE @ 30-31` rather than `XOSTATE @ 32-33` (the parser does not extract XOSTATE, but OSTATE ≡ XOSTATE for this comparator because the 43-state list contains neither `NY` nor `YC` — the only OSTATE/XOSTATE divergence is NY-state vs NYC). Verified: post-B7 + canonical filter (TABFLG=2 AND RESTATUS!=4) yields 26,004 (2003) and 26,001 (2004) byte-exact against the NCHS errata.

For 2003: 351 records re-flagged from TABFLG=1 to TABFLG=2 (out of 699 records meeting the COMBGEST=99 AND OSTATE-in-43 condition; the other 348 were already TABFLG=2).
For 2004: 349 records re-flagged (out of 690 meeting the condition).

### H8 — schema-vs-data dtype reconciliation

Source: `FIX_LOG.md` entry 2026-05-11T18:50:00Z. v2.0.0 shipped five demographic/filter columns as `object` (string) dtype despite `fetal_death/harmonized_schema.csv` declaring them as `int`. V2.1 re-derivation casts them to nullable Int (matches the schema and aligns with natality v2.7.0 dtype convention):

| Column | v2.0.0 | v2.1.0 |
|---|---|---|
| `tabulation_flag` | object | Int8 |
| `residence_status` | object | Int8 |
| `maternal_age` | object | Int16 |
| `maternal_race_bridged` | object | Int8 |
| `hispanic_origin` | object | Int8 |

Empty strings become `pd.NA` (null); sentinel integers like `maternal_age=99` are preserved as Int 99 (sentinel masking remains a separate downstream concern via `derive.py`'s sentinel handling). Downstream code that previously used string literals (`tabulation_flag == "2"`) was migrated to int literals in this release: `docs/JOINT_USE_GUIDE.md`, `notebooks/_build_joint_use_demo.py`, `notebooks/_build_paper_companion.py`, `fetal_death/quickstart.py`, `fetal_death/scripts/05_validate/validate_external.py`, `fetal_death/scripts/05_validate/validate_external_v2.py`.

### maternal_age handling for 2003+2004

The 2003 and 2004 public-use files **do not ship a single-year-of-age (`MAGER`) field**. The 2003 User Guide pages 17–19 documents bytes 89–90 as **`MAGER41` (Mother's Age Recode 41)** — a 41-category recode — not the single-year-of-age `MAGER` that appears at bytes 89–90 in the 2005–2006 layout. Bytes 91–92 hold `MAGER14` and byte 93 holds `MAGER9` in both eras.

**Consequence:** `maternal_age` is **null** for all 2003 and 2004 records in the v2.1.0 parquet. For age-stratified analysis spanning these two years, use `maternal_age_recode14` (14-category) or `maternal_age_recode9` (9-category) instead — these columns are populated from the recode fields and are valid for all 31 years.

The harmonize-time exclusion is implemented in `_build_field_map()` via `_OMIT_FROM_2003 = {"maternal_age"}`. The yearly_clean parquet's column labelled `MAGER` for 2003/2004 actually contains `MAGER41` codes (the parser dispatch inherited the 2005–2006 field list); a post-submission audit pass should rename the column for documentation correctness, but the harmonized output is correct because of the exclusion.

### Record-layout reconstruction (cheap-check note)

`record_layout_2003.csv` and `record_layout_2004.csv` shipped at v2.1.0 commit `bb01eaa` (2026-05-11) were reconstructed by inheriting bytes 1–797 from `record_layout_2006.csv` with anchor-field byte-position spot-checks against the 2003 User Guide. The spot-checks verified positions of TABFLG, DOD_YY, OSTATE, MRACEREC, F_HYSTERu — but did not value-verify field semantics. Subsequent investigation (this V2.1 build, 2026-05-12) surfaced one semantic mismatch (`MAGER` vs `MAGER41` at bytes 89–90, addressed above) and several documentation-only differences (bytes 8 = `RECWT` not BLANK; bytes 32–33 = `XOSTATE` not BLANK; bytes 96–99, 141–142, 145–147 hold actual fields in 2003 documented as BLANK in our CSV; bytes 357 = `UOB_INDUC` not `UOP_INDUC` typo). The 11 R-prefix risk-factor fields the parser reads at bytes 313–326 (`RF_DIAB`, `RF_GEST`, etc.) read all-blank for 2003/2004 in the existing yearly_clean parquet, because the 2003 layout places no documented field at those positions (it's within a BLANK filler in the 2003 user guide), and the parser-read bytes are 100% blank — so harmonized RF_* columns for 2003/2004 are correctly all-null without harmonize-time intervention.

A post-submission audit pass should rebuild `record_layout_2003.csv` and `record_layout_2004.csv` from the user guides directly (not inherited from 2006), and optionally re-parse 2003/2004 yearly_clean parquets with corrected column names. The v2.1.0 harmonized output is functionally correct because the byte positions for fields the harmonizer reads are correct (or read-blank-for-2003 and that's correct behavior); only the documentation-side `record_layout_2003/2004.csv` files have inherited-from-2006 imprecisions that should be cleaned up.

### data_year derived-column fix

A latent bug in `harmonize_year()` was surfaced and fixed during V2.1 derivation: `data_year` was being initialized as int32 in the harmonized-dict init line but then overwritten with empty-string `object` dtype when the field-map loop iterated over the crosswalk row whose `field_2006 = "derived"` (the loop's else-branch fired, since `"derived"` is not a column name in any raw parquet). The fix adds an explicit `if raw_field == "derived": continue` in the loop, preserving the int32 initialization. This bug presumably existed in v2.0.0 too; the validator at the time apparently was using a tolerant comparison or the bug was masked by something I haven't traced. v2.1.0 ships with `data_year` as int32 for all rows.

## Forward-looking caveats

- **2003 + 2004 demographic stratification**: For race × age × Hispanic-origin cross-tabulations spanning 2003–2004, use `maternal_age_recode14` or `_recode9` (NOT `maternal_age` — null for these years); `maternal_race_bridged` and `hispanic_origin` are populated from MRACEREC@143 and UMHISP@148/MRACEHISP@149 respectively (verified at byte-position level against the 2003 User Guide).

- **2003 + 2004 record_layout CSVs**: shipped as `record_layout_2003.csv` (sha `a88e1fa3…`) and `record_layout_2004.csv` (sha `f4ad74ca…`) at commit `bb01eaa`. These CSVs are documentation imprecise (inherited from 2006 with anchor-field spot-checks rather than full reconstruction). The harmonized parquet is correct; the CSVs warrant a post-submission audit-rebuild against the user guides directly.

- **B7 reapplication on re-parse**: If the yearly_clean parquets for 2003/2004 are ever re-parsed, the B7 correction will continue to apply because it is implemented in `harmonize.py` against the post-parse data, not at parse time. The TABFLG field in the yearly_clean parquet contains the originally-reported (incorrect) values; harmonize.py promotes them to the corrected values.

- **A-revision records in 2003/2004**: 1.8% (2003) and 3.7% (2004) of records are 2003-revision (`version_flag='A'`). For analyses that filter by `version_flag=='S'` (V2-era convention), these A records are excluded. The NVSR validation numbers (26,004 / 26,001) are TOTAL (S + A) by residence, so the V2.1 validator (`validate_external_v2.py`) drops the `version_flag=='S'` filter for 2003/2004 specifically.
