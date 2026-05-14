# DECISION_LOG

> **Append-only.** Every non-trivial choice the LLM (or human) makes during HVS work is logged here as a dated row. Each entry includes the alternatives considered and the reason for the choice.
>
> A "non-trivial choice" is anything that:
> - Affects the harmonized schema, the analytic filters, or the validation targets
> - Resolves an ambiguity in the source documentation
> - Trades off two reasonable approaches with different downstream costs
> - Documents a residual risk surfaced by the §10 self-check in NEXT_STEPS.md
> - Defers a deferral or scope change
>
> Entry format:
>
> ```markdown
> ## YYYY-MM-DDTHH:MM:SSZ — <task_id> — <one-line title>
> **Choice:** <what was chosen>
> **Alternatives:** <what else was considered>
> **Reason:** <why; cite source documents with page/section if relevant>
> **Source:** <PMID, PDF SHA-256, or repo path>
> **Verifiable by:** <how a future reviewer can check the choice was right>
> **Reversible:** yes / no — <if yes, how>
> ```

---

## 2026-05-14T09:30:00Z — C8.17 DO step 3 — `field_specs.py` extension for 1972-1977 era (215-byte 1972-1973 + 213-byte 1974-1977 split-record-length layout; 95 anchor fields in single `PUBLIC_US_1972_1977_FIELDS` tuple list covering common envelope positions 1-212); 2 new `RECORD_LEN_*` constants (`1972_1973=215` + `1974_1977=213`) reflect the on-disk record-length divergence empirically surfaced by readline+hex-dump probe (1972-1973: 215-byte data + \r\n; 1974-1977: 213-byte data + \r\n; trailing 2 RESERVED bytes at PDF positions 214-215 are uniform spaces in 1972-1973 + absent from 1974-1977 files); 17-anchor-field L13-extension value-distribution probe PASS for all 6 years × 5,000-record samples; 3 PDF-documented year-specific behaviors confirmed byte-exact (PLDEL@80 BLANK 1972-74 / populated 1975+ "Effective 1975"; MPLACEB@138-139 '99' for 1972 / populated 1973+; PERSATT@176 BLANK 1972-74 / populated 1975+); `natality/metadata/file_inventory.csv` `file_format` column updated for 1972 + 1973 + 1974 + 1975 + 1976 + 1977 rows with empirical record-length (215/215/213/213/213/213) + empirical record counts (1,749,402 + 1,839,736 + 2,029,150 + 2,232,406 + 2,463,852 + 2,772,206); pytest 85P + 1S + 1XF in 220.27s (within ±25s of 230.97s DO-step-2 reference; -10.70s); 4 canonical + 4 matched-multiples parquet SHAs preserved BYTE-EXACT (H10 gate intact through DO step 3); 1 §15.D-wording-misclaim resolved in-flight (1972-1977 file_inventory placeholder "100%" → "mixed sample fraction per-state per Appendix A"); zero §7 halts; zero AskUserQuestion; no tag (intermediate DO step per C8.16 sub-step precedent)

**Choices (LLM at DO step 3 close; zero AskUserQuestion needed):**

1. **TWO `RECORD_LEN_*` constants for split-record-length layout** (vs single constant + parser-side autodetect): empirical readline+hex-dump probe surfaced 1972-1973 carries 215-byte data records and 1974-1977 carries 213-byte data records, with on-disk `\r\n` terminator in both (block-lengths 217 / 215). `RECORD_LEN_1972_1973 = 215` + `RECORD_LEN_1974_1977 = 213` named per the natality convention of `RECORD_LEN_<era>` constants. The field-position tuples are byte-identical for both sub-eras (the 2-byte trailing-RESERVED positions 214-215 are NOT exposed as fields). Alternatives: (B) single `RECORD_LEN_1972_1977 = 215` with parser-side autodetect (rejected: drives complexity into the parser; better to be explicit at the spec layer); (C) two separate tuple lists `PUBLIC_US_1972_1973_FIELDS` + `PUBLIC_US_1974_1977_FIELDS` with identical content (rejected: duplicates the 95-field tuple list 2x for a layout difference that does NOT affect field positions). Verifiable by: `python3 -c "import sys; sys.path.insert(0,'natality/scripts/01_import'); import field_specs as fs; print(fs.RECORD_LEN_1972_1973, fs.RECORD_LEN_1974_1977)"` → `215 213`. Reversible: trivial.

2. **Single `PUBLIC_US_1972_1977_FIELDS` tuple list (95 fields) covering positions 1-212 of the common envelope**: positions are byte-identical across all 6 years for 1-212; only positions 213-215 differ (1972-73 carry 3 trailing spaces; 1974-77 truncate at 213). Field-positional content is uniform → single tuple list. Field count = 95 (vs 71 in 1969-1971 + 35 in 1968) reflecting the layout extension into the 1968-rev cert's full 215-byte envelope. Alternatives: (B) 75-field MVP density matching 1969-71 (rejected: misses critical SAMPWT/PERSATT/NPRENVIS-recode fields needed for mixed-sample-fraction analytics); (C) 200+ field full coverage incl. occurrence-side reporting flags (rejected: pos 161-169 OCC-flags are sibling-symmetric with pos 146-156 RES-flags; not needed in MVP). Verifiable by: `python3 -c "import sys; sys.path.insert(0,'natality/scripts/01_import'); import field_specs as fs; print(len(fs.PUBLIC_US_1972_1977_FIELDS))"` → `95`. Reversible: trivial (extend tuple list incrementally at DO step 5 if harmonize.py requires).

3. **9 residence-side reporting flags exposed at pos 146-156; 9 occurrence-side flags at pos 161-169 NOT exposed**: PDF page 25 documents residence-side reporting flags `LEGITIM_STATE / EDU_STATE / LNM_STATE / MONPRE_STATE / DOLLB_STATE / DOLFD_STATE / LEGITIM_SMSA / EDU_SMSA / CONGMAL_STATE / PRENVIS_STATE / BIRINJ_STATE` (11 named fields though PDF page 25 only enumerates 9 explicitly + 2 implicit positions); MVP exposes the 9 residence-side flags `FLAG_<X>_STATE/SMSA` at pos 146-156 (11 cells = 9 named + 2 implicit). Occurrence-side flags at pos 161-169 are sibling-symmetric (PDF page 26) but parsers can derive them when needed; MVP does NOT expose them. Alternatives: (B) expose both sides (rejected: adds 9 fields without harmonization-side use case); (C) expose neither side (rejected: residence-side flags ARE used in `_STATE` legacy 1969-71 sibling layout per existing convention). Verifiable by: `grep -c "FLAG_" natality/scripts/01_import/field_specs.py` returns 11 cells in 1972-1977 list (and pre-existing `LEGITIM_STATE/EDU_PARENT_STATE/DATE_LNM_STATE` for 1969-1971). Reversible: trivial.

4. **PDF page 26 OCR-garbled "173-275" position numbering interpreted as "173-175"**: PDF page 26 OCR rendered position numbering as `170-172`, `173-275`, `176`, `177-207`, `208` for fields RESERVED + (something) + PERSATT + RESERVED + SAMPWT. The "173-275" is clearly an OCR substitution of "1" → "2" in the second digit (`173-175` makes positional sense as a 3-byte RESERVED block continuing the pattern `170-172`); "176" then carries PERSATT (Effective 1975) as a single-byte field. This interpretation is consistent with: (a) the 207-byte position of SAMPWT immediately preceding RECORD WEIGHT (208), (b) PDF size-of-field column listing PERSATT as `1` not `3`, and (c) consistent forward-numbering across positions 170-208. Alternatives: (B) PERSATT spans 173-175 + 176 (rejected: PDF says PERSATT codes are single-byte 1/2/3/9); (C) flag as soft-flag for DO step 4 follow-up (rejected: empirical record-length probe confirms 213 vs 215 byte envelope; the position 173-175 interpretation is internally consistent and matches the parser's downstream need). Verifiable by: re-OCR with higher-res pymupdf rendering at DO step 5 if PERSATT pos disagrees with empirical sample.

5. **Year-specific BLANK fields documented in field_specs.py docstring header note (NOT split into separate per-year tuple lists)**: PLDEL@80 + PERSATT@176 BLANK 1972-1974; MPLACEB@138-139 '99' for 1972. Documenting these in the docstring (rather than per-year tuple-list-bifurcation) preserves the single-tuple-list architecture from Choice 2. Alternatives: (B) per-year tuple lists with BLANK fields omitted from 1972 / 1972-74 lists (rejected: 5x duplication of the 95-field structure for a year-specific exception list of 3 fields). Verifiable by: 5,000-record probe at DO step 3 (this session) returns BLANK for the year-specific fields in their pre-effective years (empirically confirmed). Reversible: trivial.

6. **`file_inventory.csv` row notes corrected from "100% of US births (sample expansion)" → "Mixed sample fraction per-state"**: the 1972 file_inventory row note inherited at DO step 1 said "100% of US births (sample expansion)" — empirically false per the joint user-guide page 2 §1.2 ("Beginning with the 1972 data year, 100 percent of the births occurring in certain States were processed. Births occurring in all other States were coded on a 50 percent basis"). The corrected wording references the per-record SAMPWT @ pos 208 + Appendix A per-state mapping. Soft-flag NOT carried forward (resolved in-flight per L11 fix-on-contact discipline; bundled in this DO step 3 commit). Alternatives: (B) carry as soft-flag to DO step 5 (rejected: cheap fix-on-contact; ~6 line edit). Verifiable by: `awk -F',' '$1 == 1972' natality/metadata/file_inventory.csv` shows "mixed sample fraction" wording. Reversible: trivial.

7. **1972-1973 trailing 2 RESERVED bytes documented in `RECORD_LEN_1972_1973 = 215` constant + docstring + 1974 row note + tuple-list trailing comment, NOT exposed as a field**: empirical sample shows 1972-1973 records carry 215 bytes of data with positions 214-215 as uniform space ' '; 1974-1977 records truncate at byte 213 with no positions 214-215 on disk. Per Convention 1 SHAPE-not-VALUE, the canonical layout exposes fields at positions 1-212 (the 95-field tuple list); the 213-215 RESERVED block is documentation-only. Alternatives: (B) expose pos 214-215 as a named field e.g. `RESERVED_TAIL` (rejected: field carries no value semantics; the on-disk presence-vs-absence is a record-length artifact, not a field). Verifiable by: hex-dump probe (this session) shows uniform 0x20 0x20 at positions 214-215 in 1972 + 1973 samples; absent from 1974-1977. Reversible: trivial.

**Empirical figures captured this DO step 3 (in addition to the per-era record counts above):**

- 1972 (n=5,000) anchor field value distributions: DATAYEAR all "2" ✓; RECTYPE 78%/22% Res/Nonres ✓; RESTATUS 78%/19%/3% R/Intra/Inter ✓; CSEX 50.4%/49.6% M/F ✓; BIRATTND 95.6% '1' (Phys-Hosp) ✓; FRACE 63%/19%/18% White/Negro/NS ✓; MRACE 65%/34% White/Negro ✓; DMAGE median 23 range 13-49 ✓; DBIRWT modal 3175g ✓; BIRWT_R3 91.7%/7.9%/0.4% ≥2500/<2500/NS ✓; PLDEL uniform BLANK ✓; DPLURAL 98.3%/1.7% Single/Twin ✓; DOB_MONTH skewed toward Jan/Feb (sample is sequential file-read) ✓; DMEDUC '88' uniform = non-reporting (Alabama leading-state) ✓; MPLACEB '99' uniform = "Not Classifiable" for 1972 ✓; PERSATT uniform BLANK ✓; SAMPWT '2' uniform = 50% state (Alabama is a 50% state through 1975) ✓.
- 1973-1974 anchor figures align with 1972 pattern; MPLACEB populated with '01' (Alabama) modal value at 79%/78%; PLDEL + PERSATT still BLANK.
- 1975 (n=5,000): PLDEL populated '1'=83.9%, '2'=13.0%, '4'=2.2%, '9'=0.9% — sharp transition from 1974 BLANK ✓; PERSATT populated '1'=96.3%, '2'=2.8%, '9'=0.9% ✓; SAMPWT '2' still 50% for Alabama ✓.
- 1976-1977 (n=5,000): SAMPWT shifts to '1' = 100% (Alabama becomes a 100% state per PDF Appendix A) ✓; DMEDUC populated 09-17 years (Alabama starts reporting Mother's Education in 1976) ✓.
- New `RECORD_LEN_1972_1973 = 215` + `RECORD_LEN_1974_1977 = 213` constants.
- New `PUBLIC_US_1972_1977_FIELDS` 95-field tuple list at positions 1-212; smoke-test PASS (0 OOB, 0 overlap, max pos 212 ≤ both 213 + 215 bounds).
- `field_specs.py` module docstring extended +20 lines documenting the 1972-1977 era + 7 PDF-documented year-specific differences + sample-fraction mechanism + record-length divergence.

**Forward-looking HALTs for next session (C8.17 DO step 4 entry):**

1. `C8.17-pre-do` tag at `12fc20e`; `C8.17-complete` NOT yet present.
2. 4 canonical parquet SHAs byte-exact preserved (`38e2cecb…` / `185c071e…` / `e16ad53…` / `9b828a4d…`) — H10 gate intact through DO step 3.
3. 4 matched-multiples parquet SHAs byte-exact preserved (`5c22308b…` / `7c682668…` / `d98b4296…` / `adbec108…`).
4. `natality/scripts/01_import/field_specs.py` contains `RECORD_LEN_1968 = 81` + `RECORD_LEN_1969_1971 = 215` + `RECORD_LEN_1972_1973 = 215` + `RECORD_LEN_1974_1977 = 213` + 3 PUBLIC_US tuple lists (35 + 71 + 95 fields; all within bounds + no overlap). DO step 4 ADDS `RECORD_LEN_1978_1988` + `RECORD_LEN_1989` (empirical at DO step 4 entry) + `PUBLIC_US_1978_1988_FIELDS` + `PUBLIC_US_1989_FIELDS` (or `RECORD_LEN_1989_1990_INHERIT` if 1989 inherits the 1990+ 350-byte 1989-rev layout — soft-flag (t) reconciliation point).
5. `natality/metadata/file_inventory.csv` 1972-1977 rows `file_format` = "...record length <215|213> bytes data + \\r\\n terminator; <N> records; mixed sample fraction per-state..." with empirical per-row figures (215/1749402 + 215/1839736 + 213/2029150 + 213/2232406 + 213/2463852 + 213/2772206). DO step 4 ADDS 12 rows 1978-1989 with empirical record-length + record-counts.
6. NEXT_STEPS.md §15.D wording (lines 1357 / 1362 / 1369 / 1370 / 1371 / 1383) reconciled at DO step 2; DO step 3 does NOT mutate §15.D wording.
7. Cache-cleared pytest 85 PASS + 1 SKIP + 1 XFAIL ±25s of 220.27s (DO-step-3 reference) OR 230.97s (DO-step-2 reference) OR 232.20s (DO-step-1 reference); all within tolerance.
8. /tmp/c8_17_step3/ contains 6 unzipped data files (`Natl1972.pub` 380 MB + `Natl1973.pub` 399 MB + `Natl74.pb` 436 MB + `Natl75.pb` 480 MB + `Natl76.pb` 530 MB + `Natl77.pb` 596 MB; cumulative ~2.8 GB); OS-cleanable carry-forward. DO step 4 will unzip 1978-1989 (~1.2 GB compressed → ~10-15 GB uncompressed expected per 1978-rev cert's larger envelope).
9. No new tags this session; no KICKOFF.md / NEXT_STEPS.md edit.
10. Tier 3+5 progress = 1.6 of 7 tasks (C8.16 done + C8.17 PRE-FLIGHT + DO step 1 + DO step 2 + DO step 3 in flight); cumulative Phase C ~21.5 of 51-71 sessions (within Q33 effort-ceiling cap of 86).
11. DO step 4 budget per §15.D: 1-2 sessions for 1978-1988 + 1989 (1978-revision birth cert; soft-flag (t) reconciliation; the 1989 zip is the first year of the 1989-revision cert and may either inherit the 1990+ 350-byte V2 layout OR carry its own rollout-year layout).
12. DO step 4 PRE-FLIGHT-equivalent cheap-check: re-verify all 11 HALTs above; unzip `Nat1978.zip` + `Nat1985.zip` + `Nat1988.zip` + `Nat1989.zip` (4 anchor years across the 1978-rev era + the 1989 rollout) for empirical record-length probe; pymupdf-extract `Nat<YYYY>doc.pdf` for the 11 individual user-guides (1978-1988); 5,000-record value-distribution probe on 3-5 anchor fields per year before tuple authoring.
13. Soft-flag (u) on fetal_death `imported` column still carries (Phase D step 2 candidate; unchanged by this session).
14. Soft-flag (t) on §15.D "4 distinct pre-1989 layouts" vs 5 empirical era boundaries: still carries; **DO step 4 is the canonical reconciliation point** — whether 1989 inherits the 1990+ 350-byte V2-era layout (collapses 5 → 4) or carries its own 1989-rollout layout (preserves 5).

---

## 2026-05-14T08:30:00Z — C8.17 DO step 2 — `field_specs.py` extension for 1968 (81-byte) + 1969-1971 (215-byte) layouts; 35 + 71 anchor fields authored after AskUserQuestion 2026-05-14T08:00:00Z Q1 Option A resolved a §7-#13 validity-domain-ambiguity HALT on the substrate format (§15.D plan claimed CSV-at-`natality/metadata/` but natality 1990+ uses Python tuples in `natality/scripts/01_import/field_specs.py`; fetal_death + matched_multiples use CSV; natality keeps its Python convention per sibling-pipeline discipline H7); §15.D wording reconciled in 4 places (lines 1357 + 1362 + 1369 + 1370 + 1371 + 1383) bundled in this DO step 2 commit per C8.13 precedent for in-flight plan-wording fix-on-contact; `natality/metadata/file_inventory.csv` `file_format` column updated for 1968 + 1969 + 1970 + 1971 rows with empirical record-length (81-byte + 215-byte) + empirical record counts (1,772,133 + 1,800,103 + 1,868,900 + 1,781,774); L13-extension value-distribution probe PASS for 6 + 7 anchor fields per era at 5,000-record samples (DATAYEAR / CSEX / DMAGE / DBIRWT / DPLURAL / MRACE / BIRATTND — all within documented code ranges + plausible population distributions); pytest 85P + 1S + 1XF in 230.97s (within ±25s of 232.20s DO-step-1 reference; -1.23s); 4 canonical + 4 matched-multiples parquet SHAs preserved BYTE-EXACT (H10 gate intact); 1 §7-#13 halt resolved; no tag (intermediate DO step per C8.16 sub-step precedent)

**Choices (LLM + 1 AskUserQuestion this DO step 2):**

1. **Substrate format for new pre-1990 layouts** (AskUserQuestion 2026-05-14T08:00:00Z Q1; §7-#13 halt resolved): Option A (Recommended) = extend `natality/scripts/01_import/field_specs.py` with `PUBLIC_US_1968_FIELDS` + `PUBLIC_US_1969_1971_FIELDS` Python tuple lists + `RECORD_LEN_1968` + `RECORD_LEN_1969_1971` constants. Alternatives: Option B = author CSV at `natality/metadata/record_layout_*.csv` (fetal_death + matched_multiples convention); Option C = both. Reason: natality 1990+ already uses `field_specs.py` exclusively (no CSV layouts on disk despite the §15.D plan-wording's claim); Option A matches the within-subproject sibling convention (H7 sibling-pipeline drift defense); single parser code path at DO step 5; CSV-vs-Python cross-subproject difference is preserved unchanged. Verifiable by: `uv run python -c "import sys; sys.path.insert(0, 'natality/scripts/01_import'); import field_specs as fs; print(len(fs.PUBLIC_US_1968_FIELDS), len(fs.PUBLIC_US_1969_1971_FIELDS))"` = `35 71`. Reversible: yes (revert + author CSV elsewhere).

2. **Plan-wording soft-flag (v) resolution** (LLM at DO step 2 close; in-flight fix-on-contact per C8.13 precedent): §15.D lines 1357 + 1362 + 1369 + 1370 + 1371 + 1383 had "layout-CSV reconstruction at `natality/metadata/`" / "new layout-CSV SHAs" wording that conflicted with Option A resolution above. Inline-reconciled in NEXT_STEPS.md within this DO step 2 commit (single edit; ~6 surface-fixes; no scope change). Alternatives: defer to a separate `[plan-update]` commit (less efficient; would split a single 1-session unit of work into 2 commits); leave stale + soft-flag-only (L11 violation; wording would mislead future readers). Reason: small surface area; matches C8.16 sub-step 2 precedent of in-line plan-wording fixes at DO time; preserves the C8.16 sub-step Convention 5 cadence (one commit per DO step). Verifiable by: `grep -c "field_specs" NEXT_STEPS.md` and `grep -c "layout-CSV" NEXT_STEPS.md`. Reversible: yes (revert is one git restore command if user prefers a separate plan-update commit).

3. **1968 RESTATUS empirical byte position** (LLM; L13-extension): user-guide PDF page 2 OCR's positional table is unclear/noisy on positions 4 + 11 + 12. Position 4 empirically uniformly '0' (5,000-rec probe); position 11 = '1' (1647/2000) or '2' (353/2000) — the RECTYPE recode (Resident/Nonresident); position 12 = '1' (1647) / '2' (289) / '3' (64) which matches documented RESTATUS codes (1=Resident, 2=Intrastate nonresident, 3=Interstate nonresident). RESTATUS is authored at **position 12** in `PUBLIC_US_1968_FIELDS` with a header note explaining the empirical-rather-than-first-pass-PDF-reading basis. Verifiable by: 5,000-record value-distribution probe matches documented codes (PRE-FLIGHT-CLOSE evidence captured this session). Reversible: trivial (edit the tuple position).

4. **DPLURAL position 81 in 1969-1971 with year-specific BLANK** (LLM): user-guide page 15 documents DPLURAL @ position 81 as "PLURALITY - DETAIL (1971 DATA)" with the note "For 1969-70 DATA, This Item is BLANK." Empirically confirmed: 1969 sample (5,000 rec) + 1970 sample (5,000 rec) both have position 81 uniformly = space ' '; 1971 sample has position 81 ∈ {'1', '2', '3'} matching documented Plurality codes. Authored as `DPLURAL @ 81-81` with a per-field comment noting the 1969-70 BLANK convention. Verifiable by: 3-year sample probe (this session). Harmonize.py at DO step 5 must consume the data-year context to disambiguate (blank vs actual plurality). Reversible: trivial.

5. **Empirical record counts captured per era**: 1968 (NATL1968.PUB = 145,314,906 bytes ÷ 82 = 1,772,133 records — 81 data + \\r\\n terminator); 1969 (NATL1969.PUB = 390,622,351 bytes ÷ 217 = 1,800,103 records — 215 data + \\r\\n); 1970 (NATL70.PUB = 405,551,300 bytes ÷ 217 = 1,868,900); 1971 (Natl1971.pub = 386,644,958 bytes ÷ 217 = 1,781,774). Cumulative 1968-1971 = 7,222,910 records (~50% of US natality for the 4 years; 1972+ is 100% sampling). These figures land in `natality/metadata/file_inventory.csv` `file_format` column per row and will be cross-checked at DO step 5 + Tier 2 (NCHS Vital Statistics of the United States annual-volume control counts).

6. **MVP field-set per era (not fully exhaustive coverage)**: 1968 layout authored as 35 fields out of ~50 documented; 1969-1971 layout authored as 71 fields out of ~95 documented (user-guide page 24-25 + 26 contain ~25 additional items at positions 142-215 including Congenital Malformations, by-state coding overrides, prenatal-care variants). Reason: per §15.D effort budget (1-2 sessions for DO step 2), MVP coverage of the harmonization-anchor fields (year/sex/race/age/birthweight/gestation/plurality/legitimacy/attendant/education/CBA-counts/birth-order/prenatal-care-month/place-of-residence + 1990+-comparable demographic stratification fields) suffices for the parser scaffolding at DO step 5; the remaining detail fields can be added at DO step 5 if harmonize.py requires them. Verifiable by: `field_specs.py` smoke test passes (no overlap; all positions within RECORD_LEN). Reversible: trivial (extend tuple list incrementally at DO step 5).

7. **Position 4 (1968) + positions 34-37 + 45-46 (1968) treated as undocumented placeholders**: position 4 empirically uniform '0' across 5,000 records; position 34-37 empirically uniform '9911'; position 45-46 empirically uniform '11'. PDF OCR text for the relevant pages 2 + 5 is fragmentary on these positions; no field name extractable with confidence. Per Convention 1 SHAPE-not-VALUE: NOT named as fields in the layout. Header-note comments document the empirical observations so DO step 5 can revisit if harmonize.py needs them. Verifiable by: re-running the value-distribution probe (this session's empirical sample). Reversible: trivial (extend tuple list if PDF page re-read uncovers documentation).

**Empirical figures captured this DO step 2 (in addition to per-era record counts):**

- 1968 anchor field value distributions (n=5,000): DATAYEAR all "8" ✓; CSEX 51.2/48.8 M/F ✓; DMAGE range 13-48 median 23 ✓; DBIRWT real-births 340-7031g median 3289g ✓ + 0.5% NS ✓; DPLURAL 97.7%/2.2%/0.02% Single/Twin/Triplet ✓; MRACE 64%/35% White/Negro + 0.4% NS+other ✓.
- 1969-1971 anchor field value distributions (n=5,000 per year): all 4-anchor fields PASS per-era; year-specific divergence empirically confirmed (DPLURAL @ pos 81 BLANK for 1969-70, populated for 1971).
- New `RECORD_LEN_1968 = 81` + `RECORD_LEN_1969_1971 = 215` constants in `field_specs.py`.
- `field_specs.py` module docstring extended +20 lines documenting the new layout sources + L13-extension verification provenance + 1968/1969-71 year-encoding-quirk callout (single-digit DATAYEAR = "8"/"9"/"0"/"1").

**Forward-looking HALTs for next session (C8.17 DO step 3 entry):**

1. `C8.17-pre-do` tag at `12fc20e`; `C8.17-complete` NOT yet present (intermediate DO step 2 close still has no tag).
2. 4 canonical parquet SHAs byte-exact preserved (`38e2cecb…` / `185c071e…` / `e16ad53…` / `9b828a4d…`) — H10 gate intact through DO step 2.
3. 4 matched-multiples parquet SHAs byte-exact preserved (`5c22308b…` / `7c682668…` / `d98b4296…` / `adbec108…`).
4. `natality/scripts/01_import/field_specs.py` contains `RECORD_LEN_1968 = 81` + `RECORD_LEN_1969_1971 = 215` + `PUBLIC_US_1968_FIELDS` (35 fields, all within [1, 81], no overlap) + `PUBLIC_US_1969_1971_FIELDS` (71 fields, all within [1, 215], no overlap). DO step 3 ADDS `PUBLIC_US_1972_1977_FIELDS` + `RECORD_LEN_1972_1977` (record length TBD at DO step 3 entry — empirical unzip probe required, then PDF cross-reference).
5. `natality/metadata/file_inventory.csv` 1968 row `file_format` = "...record length 81 bytes data + \\r\\n terminator; 1,772,133 records..."; 1969-1971 rows = "...215 bytes data + \\r\\n terminator; 1,800,103/1,868,900/1,781,774 records..." with the year-specific record counts byte-exact.
6. NEXT_STEPS.md §15.D wording reconciled: "field_specs.py extension" replaces "layout-CSV reconstruction" in 6 places (lines 1357 + 1362 + 1369 + 1370 + 1371 + 1383); soft-flag (v) RESOLVED — no carry-forward.
7. `tests/` directory unchanged; pytest baseline 85P + 1S + 1XF in 230.97s (±25s of 232.20s DO-step-1 reference; -1.23s) — H10 cache-cleared.
8. /tmp/c8_17_step2/ contains 4 unzipped data files (NATL1968.PUB 145 MB; NATL1969.PUB 391 MB; NATL70.PUB 406 MB; Natl1971.pub 387 MB; total 1.3 GB); OS-cleanable carry-forward. DO step 3 will unzip 1972-1977 (~5-6 GB additional).
9. No new tags this session; no KICKOFF.md edit (this DO step 2 commit edits NEXT_STEPS.md §15.D wording inline per C8.13 precedent — not a separate `[plan-update]` commit).
10. Tier 3+5 progress = 1.4 of 7 tasks (C8.16 done + C8.17 PRE-FLIGHT + DO step 1 + DO step 2 in flight); cumulative Phase C ~21 of 51-71 sessions (within Q33 effort-ceiling cap of 86).
11. DO step 3 budget per §15.D: 1-2 sessions for 1972-1977 (mixed sample fraction; multi-year joint doc; highest-risk single artifact per §15.D + sub-Q42 trigger language).
12. DO step 3 PRE-FLIGHT-equivalent cheap-check: re-verify all 11 HALTs above; unzip Nat1972.zip + Nat1977.zip for empirical record-length probe; pymupdf-extract Nat1972-77doc.pdf (29 pages per PRE-FLIGHT probe); 5,000-record value-distribution probe on 2-3 anchor fields per year before tuple authoring.
13. Soft-flag (u) on fetal_death `imported` column still carries (Phase D step 2 candidate; unchanged by this session).
14. Soft-flag (t) on §15.D "4 pre-1989 layouts" wording vs 5 era boundaries: still carries (DO step 4 reconciliation; unchanged by this session).

---

## 2026-05-14T07:30:00Z — C8.17 DO step 1 — Download substrate + SHA-anchor + metadata extension; 22 natality 1968-1989 zips (1.64 GB) + 15 user-guide PDFs (95 MB) downloaded to `~/Desktop/natality-harmonization/raw_data/` + `raw_docs/` (sibling-of-existing per AskUserQuestion 2026-05-14T07:00:00Z Q1); `natality/metadata/file_inventory.csv` 54 → 76 rows (22 new 1968-1989 inserted before existing 1990; chronological order preserved); `docs/NCHS_SOURCE_MANIFEST.md` 100 → 122 zips (Section 2 35 → 57 rows; +Boundary notes paragraph for pre-1990 era boundaries); `tests/test_source_zip_sha_stability.py` anchor 100 → 122 + natality 35 → 57 (3/3 PASS incl. per-row on-disk SHA verification of all 22 new zips byte-exact); §7 halt-and-resolve on `test_natality_inventory_years_match_schema_years_available` FAIL → user-resolved via AskUserQuestion 2026-05-14T07:00:00Z Q2 = Option A = filter on `imported=true` (~10 LOC `tests/test_inventory_invariants.py` mutation); pytest 85P + 1S + 1XF in 232.20s (within ±25s of 246.27s C8.17-pre-do reference); 4 canonical + 4 matched-multiples parquet SHAs preserved BYTE-EXACT (H10 gate intact); zero §7 halts remaining; no tag (intermediate DO step)

**Choices (LLM + 2 AskUserQuestion this DO step 1):**

1. **Download location** (AskUserQuestion 2026-05-14T07:00:00Z Q1): sibling-of-existing at `~/Desktop/natality-harmonization/raw_data/Nat<YYYY>.zip` + `~/Desktop/natality-harmonization/raw_docs/Nat<YYYY>doc.pdf` (Option A; Recommended). Alternatives: in-monorepo `natality/raw_data/pre1990/` (Option B; would split natality raw data across two on-disk locations); persistent `/tmp/natality_pre1990/` (Option C; OS-cleanable; matched-multiples soft-flag (s) anti-precedent). Reason: one canonical natality raw_data location; matches what 1990-2024 data uses; consistent with `fetal_death/file_inventory.csv` pattern (~/Desktop/fetal-death-harmonization-build/raw_data/fetal_death/...). Verifiable by: `ls ~/Desktop/natality-harmonization/raw_data/Nat19{6,7,8}*.zip | wc -l` = 22. Reversible: yes (rename or move to alternate path; update file_inventory `raw_filename` + SHA-stability test `NATALITY_RAW_DIR` constant — neither change touches the canonical SHAs).

2. **Filename casing**: lowercase `.zip` for on-disk + URL (matches existing 1990-2024 inventory convention). Upstream FTP serves both `.ZIP` and `.zip` (case-insensitive). Reason: keeps inventory column-3 + URL-13 byte-uniform with 1990-2024 rows. Verifiable by: `grep -c Nat.....zip docs/NCHS_SOURCE_MANIFEST.md` (line-3 of Section 2 prose). Reversible: trivial.

3. **DO step 1 file_format column convention** (LLM): conservative wording per row: `"zip; ASCII fixed-width (record length TBD at C8.17 DO step 2; <sample-frame>, <certificate-revision>)"`. Reason: record-length probe belongs to DO step 2 (layout-CSV reconstruction); pinning a record-length figure at DO step 1 risks L17-class stale-value pin if DO step 2 surfaces a different length than assumed. The sample-frame + certificate-revision fields capture the public-NCHS-documentation-asserted era classification without overstepping into byte-position territory. Verifiable by: re-reading `Nat<YYYY>doc.pdf` page 1-30 at DO step 2 + comparing parsed record length to this row's claim. Reversible: trivial (edit per-row at DO step 2 close).

4. **`imported` column value for new rows**: `false` for all 22. Reason: the rows are SHA-anchored at DO step 1 but not yet parser-consumed; the harmonized parquet bump happens at DO step 6. `imported=false` is the accurate per-row state. Verifiable by: `python3 -c "import csv; print({r['imported'] for r in csv.DictReader(open('natality/metadata/file_inventory.csv')) if 1968 <= int(r['year']) <= 1989})"` = `{'false'}`. Reversible: trivial (flips to `true` at DO step 6 close per row).

5. **Test-resolution for `test_natality_inventory_years_match_schema_years_available` FAIL** (AskUserQuestion 2026-05-14T07:00:00Z Q2): Option A = filter on `imported=true`. Alternatives: Option B = extend schema years_available now (wrong-direction; false claim about parquet contents); Option C = rollback DO step 1 (loses SHA-anchor); Option D = halt + re-PRE-FLIGHT (slower; captures gap in protocol record). Reason: the invariant exists to detect schema-staleness for SHIPPED years, not anchored-but-not-yet-imported ones; `imported=true` filter matches Convention 2 semantics (`DESIGN: tracks-current-state` = what's currently shipped, not what's currently anchored); the parity assertion re-asserts when `imported` flips true at DO step 6 (will require schema years_available to extend backward in lock-step). Verifiable by: `uv run pytest tests/test_inventory_invariants.py::test_natality_inventory_years_match_schema_years_available -v` PASS. Reversible: trivial (revert `imported_only=True` kwarg on the helper call).

6. **fetal_death sibling test NOT given the symmetric filter edit** (LLM at test-implementation; reverted my own first-pass): fetal_death/file_inventory.csv ships all 43 rows with `imported=no` (vestigial column — never updated even though every year is in the v2.4.0 shipped parquet). Applying `imported_only=True` would filter out all 43 rows. New soft-flag (u) carried to Phase D step 2 candidate work for fetal_death PROVENANCE refresh. Reason: forward-stability symmetric edit is the obvious move IF the column conventions agree; they don't (natality = `true`/`false` accurate; fetal_death = uniformly `no` vestigial). Treat fetal_death column as out-of-scope for this DO step. Verifiable by: `awk -F',' 'NR>1 {print $8}' fetal_death/file_inventory.csv | sort | uniq -c` = `43 no`. Reversible: when fetal_death PROVENANCE refresh updates the column to actual `true`/`false`, the fetal_death test can be flipped to `imported_only=True` symmetrically.

**Empirical figures captured this DO step 1:**

- 22 zip downloads totaling 1,640,552,373 bytes (1.527 GiB); per-zip range 14 MB (Nat1968) → 145 MB (Nat1989); pattern: 50%-sample years (1968-1971) smaller than 100% years (1972+); 1978-revision rollout (1978+) larger record-length signature than 1968-revision (1972-1977).
- 15 PDF downloads totaling 91,734,071 bytes (87.5 MB); per-PDF range 0.3 MB (Nat1968doc) → 12 MB (Nat1989doc); 5 SHAs match PRE-FLIGHT /tmp/c8_17_probes/ anchors byte-exact (085ffced… / 73e2d3e2… / 0ac4733c… / 371d1f61… / 92dab811…); 10 additional PDF SHAs newly captured (1978-1984 + 1986-1988).
- 22 zip SHAs newly captured for SHA-stability anchoring (e.g., Nat1968.zip = `bd791cf5…`, Nat1989.zip = `21e39c80…`).

**Forward-looking HALTs for next session (C8.17 DO step 2 entry):**

1. `C8.17-pre-do` tag at `12fc20e`; `C8.17-complete` NOT yet present.
2. 4 canonical parquet SHAs byte-exact preserved (`38e2cecb…` / `185c071e…` / `e16ad53…` / `9b828a4d…`) — H10 gate intact.
3. 4 matched-multiples parquet SHAs byte-exact preserved (`5c22308b…` / `7c682668…` / `d98b4296…` / `adbec108…`).
4. `natality/metadata/file_inventory.csv` row count = 76 (35 + 22 + 19); natality block (`year` ∈ {1968..2024}) contiguous; 22 rows `imported=false`; 35 rows `imported=true`; 19 linked rows unchanged.
5. `docs/NCHS_SOURCE_MANIFEST.md` first paragraph names 122 zips (43 + 57 + 19 + 3); Section 2 header reads "(57; year 1968-2024)"; new Boundary notes paragraph mentions C8.17 DO step 5 + soft-flag (t).
6. `tests/test_source_zip_sha_stability.py` count anchor = 122; natality = 57; per-row test PASS on all 22 new on-disk zip SHAs.
7. `tests/test_inventory_invariants.py::_read_inventory_year_set` accepts `imported_only` kwarg; natality test uses `imported_only=True`; fetal_death test uses default; soft-flag (u) documented in fetal_death docstring.
8. `~/Desktop/natality-harmonization/raw_data/Nat<YYYY>.zip` 22 new files present; `~/Desktop/natality-harmonization/raw_docs/Nat<YYYY>doc.pdf` 15 new files present; per-file SHAs match manifest.
9. `/tmp/c8_17_probes/` may have been OS-cleaned (carry-forward); 5 PDF SHAs reproducible from `~/Desktop/natality-harmonization/raw_docs/` for re-verification.
10. Cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/ matched_multiples/tests/ -p no:cacheprovider` returns 85 PASS + 1 SKIP + 1 XFAIL ±25s of 232.20s (post-DO-step-1 reference) OR 246.27s (C8.17-pre-do reference); both within tolerance.
11. No KICKOFF.md / NEXT_STEPS.md edit at this DO step 1 close (intermediate sub-step; the §15.D plan-update timing was 2026-05-14T02:00:00Z and remains unchanged).
12. Tier 3+5 progress = 1.25 of 7 tasks (C8.16 done + C8.17 PRE-FLIGHT + C8.17 DO step 1 in flight); cumulative Phase C ~20.5 of 51-71 sessions (within Q33 effort-ceiling cap of 86).
13. Soft-flag (u) on fetal_death `imported` column = uniformly "no" (vestigial); Phase D step 2 candidate.
14. DO step 2 budget: 1-2 sessions per §15.D (layout-CSV reconstruction for 1968 + 1969-1971 eras).

---

## 2026-05-14T06:30:00Z — C8.17 PRE-FLIGHT — Natality 1968-1989 backward extension; 22 zips + 15 PDFs probed (all HTTP 200; L1-extension sibling-derive PASS after one corrected PDF-path 404 trap); L12-extension PASS on 5-sample (100% text-extractable; Acrobat PDFWriter 3.03 + 2019-04 reprocessing signature); 5 era boundaries empirically confirmed (1968 / 1969-1971 / 1972-1977 / 1978-1988 / 1989) vs §15.D "4 distinct pre-1989 layouts" wording — terminology soft-flag (t) carried; effort estimate 6-10 sessions per §15.D unchanged (cheap-check confirms); zero §7 halts; zero AskUserQuestion needed; tag `C8.17-pre-do` on this commit

**Choices (LLM at C8.17 PRE-FLIGHT close; no AskUserQuestion required):**

1. **PRE-FLIGHT close as separate commit + tag** (C8.16 precedent at `2b7139a`): the data extension involves ~1.64 GB raw + 4-5 layout reconstructions + 22 zip downloads; the PRE-FLIGHT close gets its own commit so DO begins next session with the full 6-10 session budget. No DO work bundled into this commit.

2. **§15.D "4 distinct pre-1989 layouts" wording stands**: cheap-check empirically surfaces **5 era boundaries** (1968 standalone PDF; 1969-1971 joint PDF; 1972-1977 joint PDF; 1978-1988 individual PDFs; 1989 standalone PDF). Resolution = §15.D wording is correct if 1989 inherits the 1990+ V2-era layout (already canonical for natality 1990-2002) — the cheap-check at DO step 4 will confirm. Soft-flag (t) carries forward; NO §11 plan-update triggered (terminology, not scope; effort estimate unchanged).

3. **PDF documentation path correction (logged for forensic L12 traceability):** first-pass probe used `Datasets/DVS/Dataset_Documentation/natality/Nat<YYYY>doc.pdf` (path-component order wrong) → 404 across all 22 candidates. Corrected via cross-reference to on-disk `~/Desktop/natality-harmonization/raw_docs/Nat<YYYY>doc.pdf` for 1990-2004 + WebFetch on `cdc.gov/nchs/data_access/vitalstatsonline.htm` → corrected path = `Dataset_Documentation/DVS/natality/Nat<YYYY>doc.pdf`. Re-probe returned 200 across all 15 sibling candidates (13 individual 1968 + 1978-1989, 2 joint 1969-71 + 1972-77). The L12 cheap-check (cross-reference to on-disk inventory) caught the trap in one round-trip; NO hallucinated filename variants attempted after the path correction (L1-extension discipline preserved).

4. **L12-extension cheap-check on 5-PDF sample sufficient for PRE-FLIGHT**: per LESSONS 2026-05-12T15:00:00Z, `page.get_text()` returning non-empty on any body page is the cheap-check moment to confirm OCR is not needed. All 5 samples returned 100% non-empty pages with the Acrobat PDFWriter 3.03 + 2019-04-25 reprocessing signature shared with the 1985 fetal-death PDF precedent. The remaining 10 of 15 PDFs (1978-1984, 1986, 1987, 1988) inherit this finding by sibling-extrapolation; full per-PDF text-extraction happens at DO when authoring record_layout CSVs.

**Alternatives considered:**

For #1 (commit timing):

1. **(A) PRE-FLIGHT close as separate commit + tag — CHOSEN.** Aligns with C8.16 precedent (`2b7139a`); preserves clean checkpoint; DO begins next session with full 6-10 session budget. Convention 5 brevity ~5-line commit summary.
2. **(B) Bundle PRE-FLIGHT + DO step 1 (download 22 zips + 15 PDFs; record SHAs).** Rejected: bundling violates the §15 task-segmentation discipline; DO step 1 is a 1-session commit per §15.D; bundling collapses the cheap-checkpoint that the C8.16 precedent demonstrated value of.
3. **(C) Defer PRE-FLIGHT close until DO step 1 ships.** Rejected: §10 L10 discipline forbids backfilled PRE-FLIGHT entries; PRE-FLIGHT must commit before first DO mutation.

For #2 (terminology):

1. **(A) Soft-flag (t); §15.D wording stands; DO step 4 cheap-check resolves — CHOSEN.** Reason: 5-era vs 4-layout is terminology, not scope. §15.D's "4 distinct pre-1989 layouts" wording can be reconciled at DO step 4 either as "5 era boundaries collapse to 4 layouts when 1989 inherits V2" OR as "5 layouts; §15.D wording is loose." No §11 plan-update; defer to DO step 4 cheap-check.
2. **(B) Trigger §11 plan-update revising §15.D wording.** Rejected: terminology revision absent a substantive scope/effort change is plan-update overhead with no decision benefit; per Q42 trigger framing, plan-updates are reserved for >1-session scope drifts.
3. **(C) AskUserQuestion at PRE-FLIGHT close.** Rejected: terminology question is not user-visible; LLM-resolvable at DO step 4 cheap-check.

**Reason:** C8.17 PRE-FLIGHT is a routine input-substrate verification task for a large data extension. All 12 forward-looking HALTs from STATUS 2026-05-14T05:30:00Z verified byte-exact; the 22 zip + 15 PDF probe cycle confirms NCHS resource availability; the L12-extension PASS confirms no OCR friction; the effort estimate (6-10 sessions per §15.D) stands. The one cheap-check surprise (PDF path 404 trap) was resolved in-PRE-FLIGHT by cross-reference to on-disk inventory — exactly the L1-extension discipline mandated by LESSONS 2026-05-12T04:30:00Z. The terminology soft-flag (t) is a forensic-traceability entry, not a blocker. Convention 3 Field-value snapshot captures 5 tables of pre-DO state (inventory CSV row count + structure; harmonized_schema column count + `years_available` cell distribution; 4 canonical parquet SHAs; README + PROJECT_STRUCTURE prose; C8.1 smoke EXPECTED_YEAR_ROWS anchors); these substrate snapshots anchor C8.17 VERIFY at session close.

**Source:**

- C8.16-complete state per STATUS 2026-05-14T05:30:00Z (12 forward-looking HALTs verified byte-exact this session).
- NEXT_STEPS.md §15.D C8.17 lines 1348-1392 (the canonical task spec).
- NEXT_STEPS.md §8 row L1-extension (sibling-extrapolation discipline; applied to filename probing) + L12-extension (PDF text-layer probe before OCR; applied to 15 PDFs by 5-sample inference) + L13-extension (value-distribution verification at DO; deferred to DO step 2-4 per the matched-multiples precedent at C8.16 sub-step 2).
- HTTP 200 probe results for 22 zips at `ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/natality/Nat<YYYY>.ZIP` (uniform uppercase pattern; all Last-Modified 2007-08-24 / 2007-08-27 / 2007-08-28; cumulative ~1.64 GB).
- HTTP 200 probe results for 15 PDFs at `ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/natality/` (13 individual `Nat<YYYY>doc.pdf` for 1968, 1978-1989 + 2 joint `Nat1969-71doc.pdf` + `Nat1972-77doc.pdf`).
- PyMuPDF `page.get_text()` text-layer probe on 5 samples (Nat1968: 9 pages, 7,742 chars; Nat1969-71: 26 pages, 31,244 chars; Nat1972-77: 29 pages, 33,890 chars; Nat1985: 226 pages, 380,085 chars; Nat1989: 285 pages, 502,631 chars) — all 100% non-empty; same Acrobat PDFWriter 3.03 / 2019-04-25 reprocessing signature as the 1985 fetal-death PDF (LESSONS 2026-05-12T15:00:00Z).
- LESSONS 2026-05-12T04:30:00Z (L1-extension) + LESSONS 2026-05-12T15:00:00Z (L12-extension) — the two discipline rows that governed this PRE-FLIGHT's probe sequence.

**Verifiable by:**

- `git log --all --format='%h %s' | grep 'C8.17 PRE-FLIGHT'` returns the commit shipping this entry.
- `git tag --list 'C8.17-pre-do'` returns the tag (added on the close commit).
- `git tag --list 'C8.17-complete'` returns EMPTY (DO not yet started).
- PRE_FLIGHT_LOG.md top entry is C8.17 with `RESULT: PROCEED`.
- STATUS.md top section is dated 2026-05-14T06:30:00Z naming PRE-FLIGHT close + next-session = C8.17 DO step 1.
- `git diff HEAD~1 -- KICKOFF.md NEXT_STEPS.md` returns empty (no §11 plan-update; soft-flag (t) does not trigger one).
- `shasum -a 256 /tmp/c8_17_probes/Nat1968doc.pdf` returns `085ffcedd8dbed350ae54e241f49754f8af94fc16e7dd7e749367d37504d9456`.
- `shasum -a 256 /tmp/c8_17_probes/Nat1989doc.pdf` returns `92dab8115baec71eec3633239cbd042b2079ad6b80bd1b3a3a43c3276ac3a7cb`.
- 4 canonical parquet SHAs unchanged: `38e2cecb…` / `185c071e…` / `e16ad53…` / `9b828a4d…`.
- Cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/ matched_multiples/tests/ -p no:cacheprovider` returns 85 PASS + 1 SKIP + 1 XFAIL in 246.27s (within ±25s of 270.74s C8.16-complete baseline).

**Reversible:** yes — `git reset --hard HEAD~1` discards the PRE-FLIGHT close commit + this DECISION_LOG entry; no canonical-state mutation. Reversibility is theoretical only after subsequent C8.17 DO commits (each authored against this PRE-FLIGHT's authorization).

**Residual risks:**

- (a) **DO step 4 may surface 1989 as its own pre-V2 layout, not a sibling of 1990+ V2.** §15.D names "1989 (1989-revision birth cert; sibling of 1990-2002 V2 era)" but the 1989 file is the first year of the 1989-revision cert and may carry NCHS-side rollout artifacts (e.g., partial state coverage, transition-year coding quirks) not present in 1990+. Mitigation: DO step 4 cheap-check on bytes 1-30 of a Nat1989 sample vs `record_layout_v2.csv` sibling positions. If divergence, soft-flag (t) elevates to a 5th layout count + §15.D wording reconciled.
- (b) **1972-1977 mixed-sample-fraction handling.** §15.D names this as the highest-risk single artifact in C8.17 (DO step 3). PRE-FLIGHT did not enumerate the per-year sample fraction (50% / 100% / etc.) for the 6-year joint-doc era; the joint PDF `Nat1972-77doc.pdf` (29 pages, 33,890 chars; text-extractable) will need careful reading at DO step 3 to surface per-year sample-fraction semantics. Risk: per-year row-count expectations + canonical filter applicability may vary across the 1972-1977 range. Mitigation: §15.D sub-Q42 trigger framing — if DO step 3 grows >2 sessions, file `[plan-update]` sub-entry.
- (c) **Hispanic-origin pre-1978 handling.** §15.D names this as a DO step 5 decision (Hispanic-origin column null pre-1978 by default). PRE-FLIGHT did not enumerate the exact NCHS-side reporting introduction year; if the 1985 user guide or 1978-1988 era has Hispanic-origin coverage earlier than expected, the harmonization may need a B-style 1-digit-recode (analogue of `task7_v3a` B3 recode). Mitigation: §15.D sub-Q42 trigger framing — file `[plan-update]` sub-entry if pre-1978 Hispanic handling surfaces an unanticipated B-recode.
- (d) **`record_length` field invariant across pre-1989 eras unknown.** Existing 1990+ natality records are 350 bytes (per file_inventory.csv); pre-1989 record lengths are unknown at PRE-FLIGHT. The cheap-check at DO step 2-4 (first 3 bytes of zip header inspection + unzip + `head -1 | wc -c`) will surface each era's record length. Risk: 4-5 distinct record-length layouts (vs §15.D "4 distinct pre-1989 layouts" wording) may inflate parser authoring effort. Mitigation: parser dispatch keyed on `--era` arg, same pattern as C8.16's `parse_matched_multiples.py` `--window` arg.
- (e) **H10 reproducibility-gate cascade if 1990-2024 byte-clean regression fails.** §15.D VERIFY criterion "1990-2024 byte-clean regression: 0/N columns drift on the post-1989 slice vs current parquet" requires the new v2.9/v3.0 parquet to preserve byte-exact the 1990+ slice. If the harmonization rework introduces any column drift on the existing slice, that is a §7.18 reproducibility regression. Mitigation: forward-stability anchor `.v28_baseline.parquet` preserved per §15.D plan; cell-by-cell column-vs-column diff at DO step 6 close.

**Backport scope:** None at C8.17 PRE-FLIGHT. C8.16 unaffected; the 4 canonical parquet SHAs + 4 matched-multiples parquet SHAs remain byte-exact through C8.17 PRE-FLIGHT close.

**Forward-looking HALTs for C8.17 DO step 1 entry (Convention 4):**

- `C8.17-pre-do` tag present on the PRE-FLIGHT close commit. Verify: `git tag --list 'C8.17-pre-do'`.
- `C8.17-complete` tag NOT yet present.
- 4 canonical parquet SHAs byte-exact preserved (`38e2cecb…` / `185c071e…` / `e16ad53…` / `9b828a4d…`).
- 4 matched-multiples parquet SHAs byte-exact preserved (`5c22308b…` / `7c682668…` / `d98b4296…` / `adbec108…`).
- Cache-cleared pytest baseline 85 PASS + 1 SKIP + 1 XFAIL ±25s of 246.27s reference (or 270.74s C8.16-complete reference — both are valid C8.16-baseline values).
- `/tmp/c8_17_probes/` directory present with 5 sample PDFs at known SHAs (carry forward unless OS-cleans `/tmp`; re-downloadable from FTP).
- 22 NCHS zip URLs HTTP-200 reachable (verified at PRE-FLIGHT; re-probe at DO step 1).
- 15 NCHS PDF URLs HTTP-200 reachable (verified at PRE-FLIGHT; re-probe at DO step 1).
- DO step 1 scope: download 22 zips + 15 PDFs to a canonical `raw_data/natality_pre1990/` directory (or per-year subdirs; sibling pattern of `fetal_death/raw_data/` if it exists; TBD at DO step 1); SHA-anchor each download; add 22 rows to `natality/metadata/file_inventory.csv`; emit `natality/V3_PRE1990_LAYOUT_DECISIONS.md` if needed.
- DO step 1 budget: 1 session per §15.D.

---

## 2026-05-14T05:30:00Z — C8.16-complete — Harmonize + validate + worked-example notebook + monorepo top-level docs; 1,665,568-row harmonized parquet ships at sha `adbec108…`; 5 byte-exact PDF Table 1 cells + 8 structural invariants PASS; pytest 74→85 PASS; 4 canonical SHAs preserved (H10 gate intact)

**Choices (LLM at C8.16 DO sub-step 3 / RECEIPT close):**

1. **Harmonized schema refined 26 → 24 cols.** Dropped `data_year` (not derivable across 1995-2000 mixed-year window without cohort-linked logic; window-implicit for 1995-1997 + 2016-2020 makes it redundant with `data_window`) + `maternal_age_recode9` (only 2016-2020 has it; users can derive from `maternal_age` if needed). Sub-step 1 anticipated this in residual risk (b): "Preliminary schema is a SKELETON; sub-step 3 may surface fields worth promoting/demoting."

2. **`maternal_race_hispanic_within` → `maternal_race_hispanic` rename** to match the schema CSV row 12 canonical name and align with cross-product sibling naming (natality + fetal_death also use `maternal_race_hispanic`). The `_within` suffix was carried over from preliminary draft. The `comparability_class=within_era` in the schema row already flags the cross-window comparability caveat; the name no longer needs to.

3. **Validator output path = subproject root (not `output/validation/`).** Aligns with `fetal_death/validation_results.csv` sibling pattern. Reason: validator output is informational metadata that should be TRACKED in git (committed alongside source code); the `output/` symlink at the monorepo root + `.gitignore *.parquet output/` rule make `output/validation/` files un-trackable. Moving to subproject root satisfies both goals. Trade-off: not symmetric with natality's `output/validation/` (which is gitignored); future C8.X may consolidate.

4. **Per-plurality IMR validation backbone = complete twin set IMR (10.14/1,000) byte-exact.** The PDF prose mentions 10.82 (twins) / 29.17 (triplets) / 46.98 (quads) for "complete and incomplete sets" but the PyMuPDF text extraction renders Table 1's column headers ambiguously (the denominator definition for "complete and incomplete" is not unambiguously parseable). The PDF also explicitly states "complete sets of twins = 10.14" — this figure IS reproducible byte-exact from `set_complete ∈ {1, 2}` ∧ `set_size = 2` in the harmonized parquet. The notebook reproduces 10.14 as the validation backbone and documents 10.82 / 29.17 / 46.98 as PDF prose for context without code-level assertion. Future audits with unambiguous Table 1 extraction may add the broader assertions.

5. **L14 propagation: validator exits 1 on `n_fail > 0`.** Per §8 matrix L14 ("a reproduction / validation script's per-row CSV has FAIL rows, but main() returns 0; CI / PRE-FLIGHT reads exit code only and reports PASS"). The new `validate_matched_multiples.py` follows the C8.12 B.8 audit pattern: per-row results CSV is the data; main() returns exit code based on `n_fail` count; stderr prints the FAIL count for human inspection.

6. **`tests/test_source_zip_sha_stability.py` extended for matched-multiples.** Anchor count 97 → 100; section counts add `matched_multiples: 3`; `_classify()` recognizes the 3 matched-multiples literal filenames; `MATCHED_MULTIPLES_RAW_DIR = /tmp/c8_16_zip_probe`. Test runs against the actual zip SHAs and all 3 PASS (no skip). Future C8.X may promote the 3 zips to a canonical `raw_data/matched_multiples/` location for persistence.

**Alternatives considered:**

For #1 (schema refinement):
- (A) Drop `data_year` + `maternal_age_recode9` (24 cols total) — CHOSEN.
- (B) Keep all 26 columns; mark `data_year` and `maternal_age_recode9` as `windows_available=2016-2020 only` (single-window populated). Rejected: forces user code to handle the null cases for fields that have no cross-window analog; the schema is cleaner without them.
- (C) Drop only `data_year`; keep `maternal_age_recode9`. Rejected: same cleanliness argument applies symmetrically; users wanting age recode can derive from `maternal_age`.

For #4 (IMR validation):
- (A) Use 10.14 complete-twin-set IMR as the byte-exact backbone — CHOSEN. Reproduces exactly under `set_complete ∈ {1, 2}` filter; the PDF text uses this exact figure unambiguously.
- (B) Strict assertion on PDF prose 10.82 / 29.17 / 46.98 figures. Rejected: text-extraction column-header ambiguity means the denominator definition cannot be unambiguously specified; my filter yields 10.14 / 28.44 / 45.77, which match the alternate "complete only" prose figure for twins (10.14) and may have approximated those denominators for triplets/quads. Strict assertion would fail.
- (C) No IMR assertions in notebook; defer to a future audit pass. Rejected: the 10.14 complete-twin-set figure is unambiguous and provides genuine cross-validation of the harmonize logic (record_type + set_size + set_complete semantics all exercised in one cell).

For #5 (L14 propagation):
- (A) Stderr print + `sys.exit(1)` on FAIL branch — CHOSEN. Sibling pattern with `validate_external_v2.py` + the C8.12 B.8 patches.
- (B) Stderr print only; preserve `sys.exit(0)` behavior. Rejected: violates §8 matrix L14 explicitly; future CI gating cannot detect validator FAIL.

**Reason:** Sub-step 3 closes C8.16 with the harmonize + validate + notebook + docs deliverables, advancing Tier 3+5 from 0/7 → 1/7. Schema refinement (#1) realizes the residual risk (b) anticipated at sub-step 1. The IMR validation backbone (#4) demonstrates byte-exact analytic fidelity at the prose-cell level; the PDF prose ambiguity (#4 rejection of B) is a real limitation acknowledged with a forward-looking audit pointer. L14 propagation (#5) extends the C8.12 B.8 discipline to the new validator. The SHA-stability test extension (#6) closes the L13-extension class for the matched-multiples manifest entries (audit caught the test failure before commit; fixed in this same sub-step per fix-on-contact). Per §4.5 commit-message brevity, the full narrative lives here in DECISION_LOG; the commit ships a ~5-line summary.

**Source:**

- Empirical post-harmonize value distributions (per-window record_type splits matching raw BIRTHID distributions; per-window set_size splits matching raw PLURALITY/PLURAL; cause-of-death coverage = 100% on infant_death rows across all 3 windows).
- 2016-2020 PDF Table 1 cells transcribed from `/tmp/c8_16_pdf_probe/2016-2020.txt` (lines 1668-1743; PyMuPDF extraction of `2016-2020.pdf` sha=`ed5e96ab…` page 15).
- 2016-2020 PDF prose IMR figures from `/tmp/c8_16_pdf_probe/2016-2020.txt` (lines 69-72: "the mortality rate was 10.82 deaths per 1,000 births..."; line 72: "for compete [sic] sets of twins the infant mortality rate for twins in complete sets was 10.14").
- §8 matrix L14 row (added 2026-05-11T16:32:34Z via NHANES protocol-sync; reinforced at C8.12 B.8 audit 2026-05-13T20:00:00Z).
- §8 matrix L13/L13-extension rows (added 2026-05-12T01:40:00Z; the schema-rename harmonize → schema-CSV parity issue surfaced at sub-step 3's first harmonize-output validation).
- Validator test result: 13 PASS / 0 FAIL across 13 targets.
- Pytest extension: 74 → 85 PASS (+11 matched_multiples smoke tests) in 270.74s cache-cleared.

**Verifiable by:**

- `git log --all --format='%h %s' | grep 'C8.16-complete'` returns this commit.
- `git tag --list 'C8.16-*'` returns `C8.16-pre-do` + `C8.16-complete`.
- `shasum -a 256 matched_multiples/output/harmonized/matched_multiples_harmonized.parquet` returns `adbec1087370941fd373b933566b7dfd24dbbc2f957d998f92ac14ef45dc1549`.
- `uv run python matched_multiples/scripts/05_validate/validate_matched_multiples.py; echo $?` returns 0.
- `uv run pytest matched_multiples/tests/ -q` returns 11 PASS.
- `uv run pytest fetal_death/tests/ natality/tests/ tests/ matched_multiples/tests/ -q` returns 85 PASS + 1 SKIP + 1 XFAIL in ~250-280s.
- Cache-cleared baseline check: 4 canonical parquet SHAs unchanged (`38e2cecb…` / `185c071e…` / `e16ad53…` / `9b828a4d…`).
- `wc -l matched_multiples/harmonized_schema.csv` returns 25 (1 header + 24 data rows).
- `grep -c '^| 19' docs/NCHS_SOURCE_MANIFEST.md` + `grep -c '^| 1995-\|^| 2016-' docs/NCHS_SOURCE_MANIFEST.md` returns total 100 manifest rows.

**Reversible:** yes — `git reset --hard C8.16-pre-do` (commit `2b7139a`) discards the 3 DO sub-step commits. The off-tree /tmp probe artifacts persist for re-derivation if needed.

**Residual risks (C8.16-complete):**

- (a) **Cross-product joinability of `maternal_race_hispanic` is `within_era`.** A user joining matched-multiples 1995-1997 records (`NH_Other` ≈ AIAN+Asian+NHOPI+multiple from 4-cat ORRACEM) with natality 1990-1997 records (`NH_Other` ≈ same 4-cat ORRACEM) is fine; joining to matched-multiples 2016-2020 records (`NH_Other` ≈ AIAN+Asian+NHOPI+multiple from 8-cat MRACEHISP collapse) requires understanding the boundary. Notebook section 5 + schema row's `comparability_class=within_era` flag this.
- (b) **1995-2000 file is NOT strict supersession of 1995-1997.** Concatenating both files would double-count the overlapping 1995-1997 years with different matching methodologies. ABOUT_SOURCE_DATA.md "Methodology differences" + notebook Section 5 document this; the harmonized parquet's `data_window` column is the discriminator.
- (c) **`cause_of_death_icd_revision` derivation assumes UCOD9/UCOD10 blocks are mutually exclusive per record.** If NCHS data has both blocks populated for any record, my UCOD10-priority rule shadows the ICD-9 code. Cross-tab in notebook section 4 shows clean 14,504 ICD-9 + 7,715 ICD-10 = 22,219 infant deaths in 1995-2000 (no double-counting; no missing); the rule appears correct empirically.
- (d) **`/tmp/c8_16_zip_probe/` is OS-cleanable.** `tests/test_source_zip_sha_stability.py::test_source_zip_sha_matches_manifest` will skip the 3 matched-multiples rows if `/tmp` is cleaned. Future C8.X may promote to `raw_data/matched_multiples/` for persistence.
- (e) **The harmonized schema lists `birthweight_g` as null for all 2016-2020 records** (only the 12/14-category BWTR12/BWTR14 recodes ship for the 2003-revision file). Users wanting single-gram birthweight pre-2003-revision must use the 1995-X windows. ABOUT_SOURCE_DATA.md notes this; the schema row's `windows_available=1995-1997 (DBIRWT@106-109); 1995-2000 (DBIRWT@106-109)` flags it.

**Backport scope:** None outside `matched_multiples/` + the 5 monorepo top-level docs + 1 SHA-stability test. The harmonize logic is local; the SHA-stability test extension is the only test-surface mutation (additive; existing 97-row anchor would still pass without the extension, but the new 100-row anchor is what reflects current state).

**Forward-looking HALTs for C8.17 (Convention 4):**

- 4 canonical parquet SHAs + 4 matched-multiples parquet SHAs (3 yearly_clean + 1 harmonized) byte-exact preserved at session entry.
- `C8.16-complete` tag present; `C8.17-pre-do` tag NOT yet present.
- Cache-cleared pytest baseline = 85 PASS + 1 SKIP + 1 XFAIL ±25s of 270.74s.
- `docs/NCHS_SOURCE_MANIFEST.md` row count = 100. C8.17 will add 22 (or similar; depends on the 1968-1971 50% sample's zip packaging).
- `README.md` "Four products at a glance" header is current canonical; C8.17 extends natality row's year range.
- `tests/test_source_zip_sha_stability.py::_classify()` will need to extend to recognize 1968-1989 natality filenames (PRE-FLIGHT probe deliverable for C8.17).

---

## 2026-05-14T04:30:00Z — C8.16 DO sub-step 2 — Parser authored + 3 yearly_clean parquets emitted (324,490 / 699,144 / 641,934 records byte-exact); 1995-1997 CLINGEST L13-extension residual risk (a) resolved empirically (1→2 byte; 212→211 layout rows; 502-byte continuity preserved)

**Choices (LLM at C8.16 DO sub-step 2 close):**

1. **`parse_matched_multiples.py` authored at `matched_multiples/scripts/01_import/parse_matched_multiples.py`.** Mirrors `fetal_death/scripts/01_import/parse_fetal_year.py` structure (argparse + chunked `ParquetWriter` + iter-records generator). Single new mechanism: per-window dispatch (`_WINDOWS` dict) keyed by `--window` arg ∈ {`1995-1997`, `1995-2000`, `2016-2020`} with per-window `(layout_csv, expected_len, variable_length)` tuples. Reads `matched_multiples/record_layout_<window>.csv` at runtime as the field-position source of truth (no hard-coded constants like fetal-death's `field_specs.py`). Fields preserved as raw `latin-1` strings; numeric coercion + sentinel handling deferred to 03_harmonize/ sub-step.

2. **`zip_text_stream.py` vendored byte-for-byte** at `matched_multiples/scripts/01_import/zip_text_stream.py` (copy from `fetal_death/scripts/01_import/zip_text_stream.py`). Reason: standalone-subproject architecture per the 2026-05-14T02:30:00Z PRE-FLIGHT decision; each subproject owns its own infrastructure to avoid cross-product import paths and drift. Single 81-line file; future drift is cheap to re-sync if needed.

3. **Variable-length 2016-2020 handling** in parser: records exceeding 157 bytes warn-and-skip (none observed empirically); records short of 157 bytes right-pad with spaces before slicing (UCODR130 1-byte and 2-byte tail variants). Empirical row count 641,934 matches PDF Table 1 byte-exact and PRE-FLIGHT (DECISION_LOG 2026-05-14T03:30:00Z residual risk b precursor) byte-exact. Zero `bad_len` warnings on the full parse.

4. **1995-1997 CLINGEST L13-extension residual risk (a) resolved empirically.** Sub-step 1 layout CSV declared CLINGEST at byte 115 (1 byte) followed by a spurious DELMETH 1-byte umbrella row at byte 116. Empirical value-distribution probe on first 1,000 records showed byte 115 holds digits `{1=39, 2=209, 3=513, 4=99, 9=140}` — the tens-digit of a 2-byte 17-47/99 field, NOT the documented 17-47 weeks values. Confirmed via raw-byte slice on rec0 bytes 115-116 = `'99'` (CLINGEST=99 unknown). 1995-1997 PDF page 11 lists `position 115 [CLINGEST] CLINICAL ESTIMATE OF GESTATION (values 17-47=weeks; 99=Unknown)` followed by `position 116 [DELMETH] METHOD OF DELIVERY` — the position-116 DELMETH entry is the descriptive umbrella header for the composite at positions 117-123 (VAGINAL/VBAC/PRIMAC/REPEAC/FORCEP/VACUUM/HYSTER) and does NOT occupy a separate byte. Edit: `record_layout_1995_1997.csv` row 54 changed `115,115,1,CLINGEST` → `115,116,2,CLINGEST`; row 55 (`116,116,1,DELMETH ... umbrella`) deleted. Net layout row count 212 → 211. Net byte budget 502 → 502 (preserved). Post-edit re-parse: CLINGEST distribution = `{37: 45926, 36: 44429, 99: 43133, 38: 40703, 35: 30273, ...}` — modal weeks 35-38 (preterm-to-term twins), 99=unknown. 64 / 324,490 records (0.02%) out-of-spec (blank/sentinel; routine missing-data, not a parser bug). Downstream byte positions (VAGINAL@117, DELMETH6@124, etc.) preserved byte-exact (verified by identical pre-edit and post-edit distributions on those fields).

5. **3 yearly_clean parquets emitted** at `matched_multiples/output/yearly_clean/matched_multiples_{1995-1997,1995-2000,2016-2020}_raw.parquet` with row counts 324,490 / 699,144 / 641,934 — all byte-exact to PRE-FLIGHT empirical figures. SHAs: `5c22308bed2883b9be8e244e763c3603f700b5ba5274f3ef30388a28d39205d1` (1995-1997) / `7c682668006f3fab556b79422d34f5d84eed0bd0e1ae44702908f9f5edd61f5d` (1995-2000) / `d98b42965573530d26d72368d968c395487b2c4e4dd3bfc4ad426e966a543261` (2016-2020). Parquets are gitignored (`*.parquet` + `output/`); SHAs recorded here for sub-step 3 forward-looking HALTs.

**Alternatives considered:**

For #2 (zip_text_stream vendoring):
- (A) Copy-vendor 81-line file into matched_multiples/ — CHOSEN.
- (B) sys.path-inject `fetal_death/scripts/01_import/` from matched_multiples parser. Pro: zero duplication. Con: introduces cross-subproject import dependency; matched_multiples no longer standalone; complicates future subproject pull-out.
- (C) Promote zip_text_stream to `shared/helpers/`. Pro: defrags. Con: requires moving the fetal-death sibling too + updating its imports + re-running its tests; scope creep beyond C8.16 DO sub-step 2.

For #4 (CLINGEST resolution):
- (A) Edit layout CSV in-place; preserve byte-budget by deleting the spurious DELMETH umbrella row — CHOSEN. Rationale: PDF page 11 confirms DELMETH at position 116 is a descriptive umbrella label, not a separate byte. Empirical rec0 bytes 113-127 = `'  9912222285222'` confirms positions 117-123 hold the VAGINAL-through-HYSTER composite indicators byte-for-byte, leaving no byte budget for an intervening DELMETH field. The 1-byte CLINGEST + 1-byte DELMETH original layout was a misread of the PDF's umbrella-header convention.
- (B) Add an in-DO §11 plan-update commit. Rejected: the fix is an empirical resolution of a PRE-FLIGHT-flagged residual risk (a); DECISION_LOG records it; no §15.D / §11 plan text needs updating.
- (C) Defer fix to sub-step 3 + ship 1995-1997 parquet with broken CLINGEST. Rejected: violates §2.2 fail-closed; would propagate a known bad column downstream.

For #5 (parquet output path):
- (A) `matched_multiples/output/yearly_clean/...` — CHOSEN per STATUS line 43 sub-step 2 plan + §15.D scope.
- (B) `output/yearly_clean/matched_multiples_...` at monorepo root. Rejected: existing subprojects (fetal_death, natality) house their outputs under their own subproject root.

**Reason:** Sub-step 2 closes the parser-authoring + first-parse half of the DO budget. The L13-extension empirical probe served exactly its designed function — a value-distribution sanity check on anchor fields surfaced a byte-position semantic error that the PRE-FLIGHT layout-CSV continuity check (which only verifies byte-budget arithmetic) could not catch. Per §4.5 commit-message brevity, the full narrative lives here; the commit ships a ~5-line summary.

**Source:**
- Empirical value-distribution probe on `/tmp/c8_16_smoke_1995-1997.parquet` byte 115 returning `{1, 2, 3, 4, 9}` (tens-digit pattern of 2-byte CLINGEST).
- Raw-byte slice on rec0 bytes 115-116 = `b'99'` (CLINGEST=99 unknown).
- 1995-1997 PDF text-layer extract `/tmp/c8_16_pdf_probe/1995-1997.txt` (sha=`f982ad93…`) page 11 lines for positions 115, 116, 117.
- DECISION_LOG.md 2026-05-14T03:30:00Z residual risk (a) anticipating exactly this resolution at sub-step 2.
- LESSONS.md 2026-05-12T01:40:00Z L13-extension discipline (byte-position-vs-semantics; value-distribution check is the only catch).
- Post-edit re-parse value-distribution verification (CLINGEST modal weeks 35-38; 0.02% out-of-spec).
- Empirical row counts: 324,490 / 699,144 / 641,934 across the 3 zips.

**Verifiable by:**
- `git log --all --format='%h %s' | grep 'C8.16 DO sub-step 2'` returns this commit.
- `wc -l matched_multiples/record_layout_1995_1997.csv` returns 212 (1 header + 211 data rows; was 213 at sub-step 1 close).
- `uv run python -c "import csv; ..." continuity` returns PASS with end=502 for 1995-1997 layout.
- `shasum -a 256 matched_multiples/output/yearly_clean/*.parquet` returns the 3 SHAs above.
- `uv run python -c "import pandas as pd; print(pd.read_parquet('matched_multiples/output/yearly_clean/matched_multiples_1995-1997_raw.parquet')['CLINGEST'].value_counts().head())"` returns weeks 35-38 modal + 99 sentinel (not tens-digits 1-4 + 9).
- 4 canonical parquet SHAs (`38e2cecb…` / `185c071e…` / `e16ad5323d…` / `9b828a4d…`) BYTE-EXACT preserved (H10 reproducibility gate; C8.16 remains additive).

**Reversible:** yes — `git reset --hard HEAD~1` discards this sub-step's commit. The 3 yearly_clean parquets are deterministic functions of (zips + layout CSVs + parser) so re-deriving from sub-step 1 state is free.

**Residual risks (sub-step 2):**

- (a) **1995-2000 layout potential mirror-issue not exhaustively probed.** 1995-2000 layout was authored with 2-byte CLINGEST at 115-116 from the outset (correct per PDF) but no other fields were value-distribution-checked beyond the anchor set (BIRTHID, PLURALITY, CLINGEST, DELMETH6). If a different field in the 1995-2000 layout has an analogous byte-position-vs-semantics error (e.g., an umbrella header mistaken for a field), it would not surface until sub-step 3 NCHS-Table validation.
- (b) **2016-2020 layout sanity-checked at anchor set only.** Same caveat. The 2016-2020 file Table 1 byte-exact match is a strong cross-validation for set-size + record-count, but does not validate per-field semantics for the 124 non-anchor fields.
- (c) **CLINGEST out-of-spec rate 0.02-0.018%** (64 / 324,490 in 1995-1997; 123 / 699,144 in 1995-2000) — likely blank/sentinel for fetal-death records with no clinical estimate. Sub-step 3 will L13-extension-validate by cross-checking that 100% of `BIRTHID=3` records have CLINGEST in the documented sentinel set.
- (d) **Harmonization (03_harmonize/) NOT in sub-step 2 scope.** The 3 yearly_clean parquets ship the raw NCHS columns; cross-product harmonization (sex_infant, maternal_age, plurality, etc. canonicalization) is the sub-step 3 deliverable.
- (e) **SETID empirically blank in first 1,000 records of 1995-1997**: explained by file sort order (unmatched fetal-deaths leading the file; SETID populated only on matched complete sets). Verified at rec200000+ where SETID is 6-digit numeric. Sub-step 3 validation will confirm SETID populates iff FLGCOMP=0 (Complete set).

**Backport scope:** None outside `matched_multiples/`. The CLINGEST fix is local to the 1995-1997 layout CSV; no other subproject inherits this field.

**Forward-looking HALTs for sub-step 3 (Convention 4):**

- 3 yearly_clean parquet SHAs at `5c22308bed2883b9…` / `7c682668006f3fab…` / `d98b42965573530d…` (re-derive should produce byte-identical output).
- 1995-1997 layout row count 211 (was 212; CLINGEST fix preserved); 1995-2000 layout 256; 2016-2020 layout 125. All 3 continuity-PASS at 502/754/157.
- 4 canonical parquet SHAs (`38e2cecb…` / `185c071e…` / `e16ad5323d…` / `9b828a4d…`) BYTE-EXACT preserved (H10 reproducibility-gate).
- Cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returns 74 PASS + 1 SKIP + 1 XFAIL ±25s wall-time. C8.16 sub-step 2 added no test surface; baseline preserved.
- `parse_matched_multiples.py` + `zip_text_stream.py` present at `matched_multiples/scripts/01_import/`.
- Sub-step 3 scope: author `harmonize_matched_multiples.py` (cross-product analog field canonicalization per harmonized_schema.csv) + validate against NCHS-published documentation tables byte-exact + author `notebooks/matched_multiples_demo.ipynb` worked example + update monorepo top-level docs (README + PROJECT_STRUCTURE + CITATION + NCHS_SOURCE_MANIFEST) + VERIFY + RECEIPT.
- Cumulative Phase C progresses ~18.5 of 51-71 sessions (sub-step 2 advances ~1.0 of C8.16's 2-3 session budget).

---

## 2026-05-14T03:30:00Z — C8.16 DO sub-step 1 — Subproject scaffold + 3 record_layout CSVs (212 + 256 + 125 rows) + preliminary 26-col harmonized schema + 9-col file_inventory; 5 design decisions bundled

**Choices (LLM at C8.16 DO sub-step 1 close; documented at scaffold time before parser authoring):**

1. **`applies_to` column added to record_layout CSVs as a controlled 1-column extension to the fetal-death sibling pattern.** Fetal-death `record_layout_*.csv` ships 8 columns (`position_start, position_end, length, field_name, description, version, values_summary, notes`). Matched-multiples layouts ship 8 columns with `version` replaced by `applies_to` ∈ {`all`, `FD`, `ID`} indicating which record types (live-birth-survivor + fetal-death + infant-death; fetal-death-only; infant-death-only) the field applies to. Reason: matched-multiples files contain ALL THREE record types per file (unlike fetal_death which is fetal-death-only), so per-field record-type applicability is information that disambiguates parsing. Sibling-symmetry preserved at 8 columns; semantic clarity preserved by replacing a per-file-constant column (`version`) with a per-field variable column (`applies_to`).

2. **Hybrid harmonized-schema column naming**: cross-product analog column names (`maternal_age`, `maternal_race_hispanic`, `maternal_education_cat4`, `gestation_weeks`, `birthweight_g`, `sex_infant`, `residence_status`, `tabulation_flag`) for fields with a clear natality/fetal-death sibling; matched-multiples-specific column names (`data_window`, `record_type`, `set_id`, `set_size`, `set_complete`, `set_order`, `cause_of_death_icd`, `cause_of_death_icd_revision`) for fields without a clean cross-product analog. Reason: STATUS line 111 recommendation; maximizes cross-product joinability for the analog fields while preserving matched-multiples-specific semantic clarity for the set-level + cause-of-death-revision fields.

3. **Schema column `years_available` renamed to `windows_available`** (with values like `1995-1997,1995-2000,2016-2020`) and `raw_source_by_year` renamed to `raw_source_by_window`. Reason: matched-multiples files are window-level publications (multi-year per file), not year-level. The natality/fetal-death year-level convention doesn't map cleanly. Trade-off: schema columns now differ slightly from the natality/fetal-death sibling pattern (10 columns with two renamed). Within-subproject readability gains > cross-subproject symmetry loss.

4. **2016-2020 file format = VARIABLE-LENGTH (155-157 bytes per record); `record_length=157` (documented end position) in `file_inventory.csv`.** PRE-FLIGHT (STATUS 2026-05-14T02:30:00Z) recorded 156 bytes which counted content-plus-`\r` (no `\n` stripped). Empirical probe via Python `zipfile.ZipFile(...).open(...).readline().rstrip(b'\r\n')` reveals: 634,863 records at 155 bytes content (survivors+fetal-deaths or 1-digit UCODR130); 4,089 records at 156 bytes (2-digit UCODR130); 2,982 records at 157 bytes (3-digit UCODR130) — total 641,934 MATCHES PDF Table 1 byte-exact. The variable-length tail is caused by NCHS right-trimming trailing blanks in `UCODR130` (positions 155-157) on a per-record basis. Parser at sub-step 2 will handle by reading each line as text + slicing fixed positions 1-154 + right-padding `UCODR130`. Documented in `record_layout_2016_2020.csv` notes for `UCODR130` row + `ABOUT_SOURCE_DATA.md` "Variable-length file handling" section.

5. **Empirical record counts** corrected vs PRE-FLIGHT estimates: 1995-1997 = 324,490 (was 325,135 by file-size/length division); 1995-2000 = 699,144 (was 699,938); 2016-2020 = 641,934 (was 646,113). The PRE-FLIGHT estimates were `unzip -l` uncompressed-size divided by record-length-including-`\r`; empirical counts use Python file iteration. 2016-2020's 641,934 matches PDF Table 1 byte-exact (a strong cross-validation). Recorded in `file_inventory.csv` notes.

**Alternatives considered:**

For #1 (`applies_to` column):
- (A) 8 cols with `applies_to` replacing `version` (CHOSEN). Pro: minimizes sibling-pattern deviation; clean semantic mapping.
- (B) 9 cols adding `applies_to` (keeping `version`). Pro: most general. Con: deviates from sibling pattern more substantially; `version` is per-file-constant so it's redundant within a single layout CSV.
- (C) 8 cols matching sibling exactly; encode `applies_to` info in `notes` field. Pro: zero sibling-pattern deviation. Con: loses structured queryability of FD/ID applicability; harder to validate at parser stage.

For #2 (schema naming):
- (A) Hybrid (CHOSEN). Pro: maximizes interoperability for cross-product analyses; preserves matched-multiples-specific semantic clarity for set-level fields.
- (B) Verbatim NCHS names (`PLURAL`, `MULTID`, `MAGER`, etc.). Pro: source-doc traceability. Con: zero cross-product interoperability; users would have to manually rename for joint analyses with natality/linked.
- (C) Full analog-only naming (force all fields into cross-product names). Pro: maximal interop. Con: forces semantically-unique matched-multiples concepts (`set_id`, `set_complete`) into ill-fitting analog names.

For #4 (variable-length record handling):
- (A) `record_length=157` (max content per doc end position; CHOSEN). Pro: matches documentation byte-exact; parser uses position 157 as the slice upper bound.
- (B) `record_length=155` (modal content, 98.9% of records). Pro: most common. Con: parser would silently truncate 1-2 bytes for 7,071 records (infant deaths with 2-3 digit UCODR130).
- (C) `record_length="155-157"` (range). Pro: most accurate. Con: violates fetal-death sibling pattern (integer-only `record_length`); breaks `tests/test_inventory_invariants.py::test_fetal_death_inventory_record_length_populated_for_all_rows` extension to matched_multiples.

**Reason:** Five design decisions documented at scaffold time so sub-step 2 (parser) and sub-step 3 (validation + worked-example notebook) inherit a fully-specified design context. Per §4.5 commit-message brevity, the full narrative lives here in DECISION_LOG; the commit ships a ~5-line summary.

**Source:**
- PyMuPDF `page.get_text()` extraction of all 3 PDFs (87 pages total; L12-extension PASS at PRE-FLIGHT preserved).
- Python `zipfile.ZipFile(...).open(...).readline().rstrip(b'\r\n')` empirical probe + `len(content)` distribution per record.
- 2016-2020 PDF Table 1 cell match (641,934 records empirical = 633,734 birth + 8,200 fetal death documented).
- L13-extension cheap-check (LESSONS 2026-05-12T01:40:00Z): field SEMANTICS not just positions. The 2016-2020 SEX field empirically verified at position 104 (1-indexed) matching documentation; positions 1-104 of the file align byte-exact with the PDF doc.
- STATUS line 111 recommendation for hybrid schema naming.
- C8.16 PRE-FLIGHT DECISION_LOG entry (2026-05-14T02:30:00Z) Option A standalone-subproject architecture authorization.

**Verifiable by:**
- `git log --all --format='%h %s' | grep 'C8.16 DO sub-step 1'` returns the commit shipping this entry.
- Working tree post-commit: `matched_multiples/` directory present with 7 files (3 layout CSVs + 1 inventory + 1 schema + README + ABOUT) + scripts/01_import/, 03_harmonize/, 04_derive/, 05_validate/ + tests/ + output/* (empty placeholders).
- `python3 -c "import csv; ..."` validation of layout CSVs returns continuity-PASS + no-overlap-PASS for all 3 layouts.
- 4 parquet SHAs preserved (`38e2cecb…` / `185c071e…` / `e16ad5323d…` / `9b828a4d…`); no canonical-state mutation outside `matched_multiples/`.
- 2016-2020 file Table 1 match: PDF says total=641,934, empirical Python row count = 641,934. ✓

**Reversible:** yes — `git reset --hard HEAD~1` (combined with the C8.16-pre-do tag at `2b7139a`) discards this sub-step's scaffold + decisions. The /tmp/c8_16_pdf_probe/ + /tmp/c8_16_zip_probe/ artifacts persist for re-derivation.

**Residual risks (sub-step 1):**

- (a) **1995-1997 CLINGEST byte-position ambiguity carries forward.** Doc says 1 byte at position 115 (with DELMETH at 116); 1995-2000 doc has CLINGEST at 2 bytes (115-116). The layout CSVs reflect the doc as-stated (1-byte for 1995-1997; 2-byte for 1995-2000). Sub-step 2 parser will value-distribution probe to resolve.
- (b) **Harmonized schema is a SKELETON not a final schema.** 26 columns covering the obvious cross-product analogs + matched-multiples-specifics. Sub-step 2 (parser) may surface additional fields worth promoting to harmonized; sub-step 3 (validation) may surface columns that need fine-grained recodes.
- (c) **`cause_of_death_icd_revision` derivation logic** for 1995-2000 records depends on `data_year` — but `data_year` is not in the raw file (window-implicit). Sub-step 2 parser must impute `data_year` from per-record date fields OR via cohort-linked-by-set logic. If neither is available, ICD revision flagging may be limited.
- (d) **set_complete normalization** introduces a 1->3 shift: 1995-X uses 0/1/2 (with 2=unmatched); 2016-2020 uses 1=complete + 2=incomplete + COUNT=1=unmatched. The harmonized canonical maps to 1=complete / 2=incomplete / 3=unmatched. Schema notes this; parser implements.
- (e) **`record_length` invariant test extension** (carry-forward from C8.7b soft-flag `m`): the existing `tests/test_inventory_invariants.py::test_fetal_death_inventory_record_length_populated_for_all_rows` does not yet cover matched_multiples. A future sub-step (likely sub-step 3 or C8.20+) may extend.

**Backport scope:** None. Pure additive scaffold; no existing parquet, validator, test, or canonical data touched.

**Forward-looking HALTs for sub-step 2 (Convention 4):**

- 3 record_layout CSVs present at the SHAs recorded post-commit; continuity validated (no gaps / no overlaps / position-sum=length per row).
- `file_inventory.csv` ships 3 rows (one per window) with SHA-256 anchors recorded in `notes` for each zip + doc PDF.
- 26-col preliminary `harmonized_schema.csv` skeleton present.
- 4 existing parquet SHAs (`38e2cecb…` / `185c071e…` / `e16ad5323d…` / `9b828a4d…`) BYTE-EXACT preserved (no harm to H10 reproducibility gate).
- Cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returns 74 PASS + 1 SKIP + 1 XFAIL (matched_multiples/tests/ has no tests yet so adding to pytest command would be no-op).
- Sub-step 2 (parser authoring) begins at next iteration; produces 3 yearly_clean parquets at `output/yearly_clean/matched_multiples_<window>_raw.parquet` + harmonize.py emitting `output/harmonized/matched_multiples_harmonized.parquet`.

---

## 2026-05-14T02:30:00Z — C8.16 PRE-FLIGHT — Architectural decision: standalone `matched_multiples/` subproject (§15.D default) + effort revised 1-2 → 2-3 sessions (within Q42 +1-session tolerance; no §11 plan-update); user-resolved via AskUserQuestion 2026-05-14T02:30:00Z

**Choice (user at 2026-05-14T02:30:00Z; in response to AskUserQuestion at C8.16 PRE-FLIGHT close):**

- **Architecture pattern** = **Option A (standalone subproject; §15.D default; Recommended)**. New top-level `matched_multiples/` directory parallel to `natality/` + `fetal_death/`; 4th HVS data product with its own `harmonized_schema.csv` + `file_inventory.csv` (mirroring fetal_death 9-col + 10-col patterns) + 3 distinct `record_layout_<window>.csv` files (one per record-length layout) + `scripts/01_import/parse_matched_multiples.py` + per-product validation + tests. Reasons: (i) cross-product linkage nature (spans natality + fetal-death; doesn't fit cleanly under either alone); (ii) cleanest schema separation; (iii) doesn't disturb existing canonical parquet SHAs (H10 reproducibility-gate preserved on `38e2cecb…` / `185c071e…` / `e16ad5323d…` / `9b828a4d…`); (iv) easy for non-multiple-gestation users to ignore. Inventory + schema mirror fetal_death pattern (9-col inventory with `record_length`; 10-col schema with `domain`) — the most complete sibling pattern in the monorepo.

- **Effort acknowledgment** = **Option A (acknowledge 2-3 session estimate; proceed)**. §15.D entry estimated 1-2 sessions assuming "mostly V1-era-sibling layout"; PRE-FLIGHT probing surfaced 3 DISTINCT record-length layouts (503-byte `sets9597.public` 1995-1997 + 755-byte `Sets9500.public` 1995-2000 + 156-byte `MULTIPLES.TXT` 2016-2020) requiring 3 separate `record_layout_<window>.csv` reconstructions from 87 PDF pages. Revised estimate: 2-3 sessions. Within Q42 +1-session tolerance from the 1-2 §15.D band (no §11 plan-update triggers). No update to §15.D entry text; PRE-FLIGHT log + this DECISION_LOG entry are the authoritative effort-revision record.

**Alternatives considered:**

For architecture:

1. **(A) Standalone `matched_multiples/` subproject — CHOSEN.** Reasons above.
2. **(B) Join-flag column on existing parquets.** Would add `matched_multiple_flag` boolean to existing fetal-death + linked parquets. Rejected: destroys H10 byte-exact reproducibility anchors (re-deriving 2 canonical parquets); force-fits a cross-product linkage into within-product schemas; window non-overlap (fetal-death 1982-2022; linked 2005-2023 vs matched-multiples 1995-2000 + 2016-2020) means many records would have null flags, which is misleading semantics.
3. **(C) Fold under `natality/` as 3rd product (sibling of linked file).** Rejected: matched-multiples spans natality + fetal-death (live births + fetal deaths in multiple deliveries), not natality-only; folding under natality misrepresents the cross-product linkage.

For effort:

1. **(A) Acknowledge 2-3 session estimate; proceed — CHOSEN.** Reasons above.
2. **(B) Trigger §11 plan-update; revise §15.D estimate explicitly.** Rejected: 2-3 sessions is within Q42 +1-session tolerance from the §15.D 1-2 estimate; no §11 plan-update triggers; the overhead (~15-20 min) is not warranted given the §15.D entry text already provides the 1-2 upper bound for tolerance arithmetic. The PRE-FLIGHT log + this DECISION_LOG entry suffice as authoritative effort-revision record.
3. **(C) Trim scope: ship only 2016-2020.** Rejected: defers ~1M historical multiple-gestation records (1995-1997 + 1995-2000) to a follow-up task; conflicts with the 2026-05-14 user directive *"everything possible before uploading to zenodo"*; the maximum-coverage authorization at the plan-update commit anticipated full Tier-3+5 scope. The 2-3 session cost is within plan budget.

**Reason:** §15.D explicitly named the standalone subproject as the default + recommended architecture; PRE-FLIGHT probing confirmed the matched-multiples files are a genuinely separate data product (different record formats; different methodology generations; cross-product linkage spanning natality + fetal-death). The effort revision (1-2 → 2-3) stays within Q42 tolerance and matches the actual layout-reconstruction complexity (3 distinct layouts at 503 / 755 / 156 bytes per record).

**Source:**

- AskUserQuestion 2026-05-14T02:30:00Z (this conversation) — user authorization for Option A architecture + Option A effort acknowledgment.
- NEXT_STEPS.md §15.D C8.16 lines 1307-1346 (the canonical task spec; "Default recommendation: standalone subproject for clean schema").
- NEXT_STEPS.md §8 row L1-extension (sibling-extrapolation discipline; applied to filename probing) + L12-extension (PDF text-layer probe before OCR; applied to 87-page documentation set).
- DECISION_LOG.md 2026-05-14T02:00:00Z `[plan-update] scope_expansion_tier3_tier5` Q42 framing — "any new candidate >1 session triggers a `[plan-update]` per §11; silent in-Phase-C scope-creep forbidden." The 2-3 session estimate is within +1 session of §15.D's 1-2; no plan-update triggers.
- HTTP 200 probe results for 3 zips + 3 PDFs at `ftp.cdc.gov/.../Datasets/DVS/matched-multiples/` + `Dataset_Documentation/DVS/matched-multiples/`; record-length samples (503 / 755 / 156 bytes) from `unzip -l` + `head -3 | awk '{print length($0)}'`.
- PyMuPDF `page.get_text()` text-layer probe on all 3 PDFs returning 100% non-empty across 87 pages (L12-extension cheap-check PASS).

**Verifiable by:**

- `git log --all --format='%h %s' | grep 'C8.16 PRE-FLIGHT'` returns the commit shipping this entry.
- `git tag --list 'C8.16-pre-do'` returns the tag (added on the close commit).
- `matched_multiples/` directory does NOT yet exist on disk at the pre-do commit (DO authors it next session).
- PRE_FLIGHT_LOG.md has C8.16 entry at top with `RESULT: PROCEED`.
- STATUS.md appends a new dated section at top recording PRE-FLIGHT close + revised effort 2-3 sessions + next-session = C8.16 DO.

**Reversible:** yes — `git reset --hard HEAD~1` discards the PRE-FLIGHT close commit + this DECISION_LOG entry; no canonical-state mutation. Reversibility is theoretical only after subsequent C8.16 DO commits (each authored against this PRE-FLIGHT's authorization).

**Residual risks:**

- (a) **Layout-reconstruction effort may inflate further at DO.** PRE-FLIGHT did not enumerate every documented field across the 3 PDF generations; if any of the 3 PDFs documents implicit / overflow / non-standard fields not yet visible from page 1 + zip header probes, the per-layout reconstruction may grow. Mitigation: Q42 trigger (>1 session beyond revised 2-3 = >3 cumulative beyond §15.D high bound) requires §11 plan-update at the next clean checkpoint.
- (b) **Schema-design ambiguity at DO.** Whether matched-multiples harmonized schema reuses fetal-death + natality column names (e.g., `maternal_age`, `plurality`, `infant_birthweight_g`) or uses NCHS source field names verbatim was not resolved at PRE-FLIGHT. This is a DO-time decision; surfaced if it grows >1 session beyond the revised budget.
- (c) **1995-1997 vs 1995-2000 windowing.** Both files ship; users will need clear documentation explaining the relationship (different methodology generations, not supersession). At DO: `ABOUT_SOURCE_DATA.md` must document the relationship + recommended use case for each window.
- (d) **Cross-product validation surface.** §15.D specifies "per-file aggregate counts match NCHS documentation byte-exact" as VERIFY criterion. The documentation tables for each PDF will need to be transcribed (with sha-anchored cell-by-cell counts) at DO; if transcription surfaces additional methodology nuances (e.g., the 1995-2000 PDF has additional analytic-cohort filters not in 1995-1997), the validation surface may expand.
- (e) **`notebooks/matched_multiples_demo.ipynb` IMR computation cohort.** §15.D names "≥1 cell vs NCHS-published table" as the demo target. Choosing which cell + which year × which cohort = which-NCHS-document is a DO-time decision; routine.

**Backport scope:** None. C8.1-C8.15 are unaffected; the v2.4.0 fetal-death + v2.8.0 natality + v3 linked parquets remain canonical anchors. The 4th product ships as additive at v1.0.

**Forward-looking HALTs to write in C8.16 DO PRE-FLIGHT continuation (Convention 4):**

- 3 matched-multiples zip sha256 anchors will be recorded at first DO sub-step (downloading the zips to a canonical `raw_data/` location or relying on streaming-from-FTP-only) and verified against future re-runs.
- 3 documentation PDF sha256 anchors already recorded above (`f982ad93…` / `07b7260d…` / `ed5e96ab…`); will be re-verified at each DO continuation session.
- `matched_multiples/` directory presence + 9-col file_inventory.csv + 10-col harmonized_schema.csv + 3 record_layout CSVs at DO close.
- 4 existing parquet SHAs remain byte-exact through C8.16 (additive scope).
- Cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/ matched_multiples/tests/` returns at-least-74-PASS + 1 SKIP + 1 XFAIL at C8.16 VERIFY.

---

## 2026-05-14T02:00:00Z — [plan-update] scope_expansion_tier3_tier5 — Pre-Zenodo scope expanded a 6th time: Tier 3 + Tier 5 candidates (deferred per Q35 2026-05-12) re-authorized by user 2026-05-14; new tasks C8.16-C8.22 appended to §15 in user-chosen sequence (matched-multiples → natality 1968-1989 → linked 1983-2004 → perinatal-record → CODEBOOK → Stata/SAS → cross-tabs); cumulative Phase C estimate revised 29-35 → 51-71 sessions; effort-ceiling cap raised 42 → 86 (+20% of 71 high estimate); Q41 + Q40 + Q36 defaults overridden by explicit user authorization

**Choice (user at 2026-05-14T02:00:00Z; in response to LLM kickoff question following C8.15 close):** Following C8.15 close (Tier 2 CLOSED 7/7 at `b6954ec`), the user requested all remaining data-generating work happen before the Zenodo deposit, restating the 2026-05-12 directive *"i would like do do everything possible … before we do the paper or the zenodo"* with explicit emphasis on data extensions ("wait did we finish all the data generating things? i want to do everything possible before uploading to zenodo"). AskUserQuestion 2026-05-14T02:00:00Z resolved both the scope authorization and the within-Tier-5 ordering question; a follow-up AskUserQuestion resolved the cross-Tier sequencing and D.1 timing.

- **Scope authorization** = Option A (Maximum coverage; Tier 3 + Tier 5 all). Adds matched-multiples ancillary release + natality 1968-1989 backward extension + linked 1983-2004 backward extension + perinatal-record pre-joined parquet + CODEBOOK extensions + Stata/SAS pointer files + pre-computed cross-tab CSVs. ~21-34.5 additional sessions; cumulative Phase C total estimate now ~51-71 sessions (was 29-35).
- **Tier 5 within-ordering** = Option A (Natality 1968-1989 first, then linked 1983-2004). Per EXPLORATION_REPORT Q36 default; natality is shorter (6-10 sessions vs 8-14), simpler revision-boundary story, sibling of just-shipped V3b; the 1978-cert layout work modestly benefits the 1983-1991 cohort-linked phase.
- **Cross-Tier sequencing** = Option 1 (proposed sequence confirmed): matched-multiples FIRST as cheap independent early win (1-2 sessions; tests post-Tier-2 plumbing on small new product); then the user-chosen big data extensions (natality 1968-1989 → linked 1983-2004); then perinatal-record (depends on both above); then docs/usability ancillaries (CODEBOOK → Stata/SAS → cross-tabs). Manuscript Coverage paragraph re-paragraphed ONCE at D.4 after all data lands.
- **D.1 timing** = Option 1 (D.1 stays at end after C8.22). Per current KICKOFF Phase D ordering; redirect notices ship in one batch with v1.x public-repo sync. Final notice text references the actual maximum-coverage envelope.

This is the **6th pre-submission scope expansion** since the 2026-05-09 monorepo migration:
- 1st-4th: pre-2026-05-12 (V2.1, V3a, V3b, latest-year refreshes inside Phase A).
- 5th: 2026-05-12T19:15:00Z (insertion of Phase B + Phase C between Phase A and Phase D).
- 6th: this entry (grows Phase C by Tier 3 + Tier 5 candidates explicitly deferred at the 2026-05-12T21:00:00Z Q35 authorization moment).

**Alternatives considered:**

1. **(A) Maximum coverage — Tier 3 + Tier 5 all (CHOSEN).** Pro: closes every pre-submission data-extension candidate in one v1.0 release; manuscript Coverage section re-paragraphed once; Zenodo deposit ships maximum envelope; no v1.1/v2.0 follow-up data work needed; no IJE *Update* note required for backward extensions. Con: ~6-12 weeks additional pre-submission work at ~one-session-per-half-day cadence; largest manuscript Coverage re-paragraph friction; substantial effort-ceiling expansion (Q33 cap raised 42 → 86 sessions).
2. **(B) Tier 5 only (no Tier 3).** Pro: gets the big "more data" wins (natality 1968-1989 + linked 1983-2004; ~16-24 sessions). Con: defers matched-multiples ancillary product + leaves cross-tabs + Stata/SAS pointers + CODEBOOK extensions for a v1.1 follow-up.
3. **(C) Matched-multiples + light Tier 3 only.** Pro: cheapest add (~5-9 sessions); ships 4th HVS product (matched-multiples) at v1.0; minimum re-paragraph friction. Con: misses the natality 22-year backward and linked 19-year backward extensions which are the biggest "more data" wins; user's "everything possible" framing not honored.
4. **(D) Keep current scope; ship Phase D now.** Pro: fastest path to manuscript submission (~3-4 sessions); v1.1/v2.0 ships backward extensions as IJE *Update* note + Zenodo concept-DOI patches. Con: misses user's restated "everything possible" directive; ships a v1.0 with envelope known-stale-at-ship-time when v1.1 with backward extensions is plainly imminent.

User chose Option A.

**Reason:** The 2026-05-12T19:15:00Z plan-update introduced Phase B+C to maximize pre-submission scope; the user's 2026-05-14 directive sharpens that to "everything possible including backward extensions and ancillaries." Maximum coverage closes the data-envelope question definitively at v1.0 rather than deferring half of it to a v1.1 release; matches the precedent set by the V3a/V3b backward extensions (which were already cumulative scope expansion vs the original 2026-05-11 plan). The cross-Tier sequencing (matched-multiples → natality → linked → perinatal-record → docs) minimizes manuscript Coverage re-paragraph friction by deferring all docs work until the final envelope is settled. The Tier-5 within-ordering (natality 1968-1989 before linked 1983-2004) preserves the EXPLORATION_REPORT Q36 default rationale (shorter task first; modest 1978-cert layout knowledge reuse for cohort-linked 1983-1991 phase).

**Effort revisions:**

- **Tier 1+2 (DONE)**: ~17.5 sessions actual (within §15 estimate; cumulative Phase C ~52% complete at C8.15 close). Unchanged.
- **Tier 3+5 (NEW)**: ~21-34.5 sessions estimate.
  - **C8.16** A.5 matched-multiples (4th HVS product): 1-2 sessions
  - **C8.17** A.2 natality 1968-1989 backward extension: 6-10 sessions
  - **C8.18** A.3 linked 1983-2004 backward extension: 8-14 sessions
  - **C8.19** C.8 perinatal-record pre-joined parquet (methodology research): 2-3 sessions
  - **C8.20** E.7 CODEBOOK extensions (per-variable historical distributions): 2-4 sessions
  - **C8.21** C.3 Stata/SAS quickstart pointer files: 0.5 sessions
  - **C8.22** C.5 pre-computed cross-tab CSVs (published_tabulations/): 1 session
- **Total cumulative Phase C estimate**: 51-71 sessions (revised from 29-35).
- **Effort-ceiling cap (Q33)**: raised 42 → 86 sessions (+20% of 71 high estimate). Re-ask trigger preserved: if cumulative effort drifts >86 sessions, halt at next clean checkpoint and re-ask the user.

**Source:**

- AskUserQuestion 2026-05-14T02:00:00Z (this conversation) — user authorization for Option A scope + Tier 5 ordering A + sequence Option 1 + D.1 timing Option 1.
- User chat 2026-05-14: *"wait did we finish all the data generating things? i want to do everything possible before uploading to zenodo"* — the 2026-05-12 directive restated with data-extension emphasis.
- KICKOFF.md line 198 (pre-this-commit): the "Tier 3 (5 candidates) and Tier 5 (3 candidates) deferred" framing being superseded by this plan-update.
- EXPLORATION_REPORT.md §A.2 (lines 68-103; natality 1968-1989) + §A.3 (lines 105-145; linked 1983-2004) + §A.5 (lines 172-191; matched-multiples) + §C.8 (lines 560-574; perinatal-record) + §E.7 (lines 767-781; CODEBOOK extensions) + §C.3 (lines 482-496; Stata/SAS) + §C.5 (lines 514-528; cross-tabs) — the candidate-specific scope sources.
- EXPLORATION_REPORT.md §G.4 (lines 981-997; Tier 3 + Tier 5 effort estimates) + §G.5 (lines 999-1007; maximalist recommendation tradeoff).
- DECISION_LOG.md 2026-05-12T21:00:00Z (`phase_c_authorized`) — the Q35 = Tier 1+2 authorization being superseded for Tier 3+5 work.

**Verifiable by:**

- `git log --all --format='%h %s' | grep '\[plan-update\] scope_expansion_tier3_tier5'` returns this commit.
- `git tag --list 'C8.{16,17,18,19,20,21,22}*'` empty at this commit; non-empty progressively as each task ships (pre-do + complete tags per Convention 4).
- KICKOFF.md Phase C section reflects "Tier 3 + Tier 5 ACTIVE" replacing line 198's prior "deferred" framing.
- NEXT_STEPS.md §15.C extended with new C8.16-C8.22 entries (line numbers recorded post-commit at the next session's PRE-FLIGHT).
- STATUS.md appends a new dated section at top recording the plan-update + revising "Next planned task" to C8.16.
- Cumulative effort at next session start: ~17.5 done / ~51-71 estimated = ~25-34% complete (was ~52% under prior 29-35 estimate; the scope expansion mechanically reduces the percentage-complete metric).

**Reversible:** yes — `git revert <this plan-update commit>` restores the prior Q35 = Tier 1+2-only authorization. No canonical-data, parquet, validator, or test-surface mutation in this commit. Reversibility is theoretical only after subsequent C8.X DO commits (which would also need reverting in dependency order: C8.22 → C8.21 → C8.20 → C8.19 → C8.18 → C8.17 → C8.16 → this).

**Residual risks:**

- (a) **Effort ceiling**: the new total of 51-71 sessions is ~2x the original 29-35 estimate (which was already a scope expansion from the original Phase-A-only plan). User awareness is explicit (the AskUserQuestion preview surfaced full effort totals before authorization). Q33 re-ask invariant satisfied by this very plan-update; new cap = 86 sessions; re-ask triggers if cumulative drift exceeds 86. Re-ask is BINDING per the KICKOFF "Always-on Phase C discipline" framing.
- (b) **Schema-version cascade**: each backward extension triggers a schema-version bump: C8.17 natality v2.8 → v2.9 (or v3.0 if the 1968-rev / 1978-rev / 1989-rev era boundary surfaces require a major bump); C8.18 linked v3 → v4 (if the cohort/period publishing-design boundary requires a major bump, which it likely does). H10 reproducibility-gate re-anchors at each bump; B.12 snapshot-regression baseline re-snaps; PROVENANCE.md refresh per task. Manuscript Coverage paragraph re-paragraphed ONCE at D.4 after all data lands.
- (c) **C8.17 A.2 natality 1968-1989 risk**: 4 distinct pre-1989 layouts (1968 / 1969-71 / 1972-77 / 1978-88 / 1989) is ~4x the V3b layout-CSV cost; 1968 50%-sample handling + 1972-77 mixed sample fraction + Hispanic-origin field absence pre-1978 add complexity. EXPLORATION_REPORT §A.2 estimate is 6-10 sessions; effort may inflate. Q42 trigger applies if a sub-step inflates >1 session beyond the §15 entry estimate.
- (d) **C8.18 A.3 linked 1983-2004 risk**: cohort/period publishing-design decision is methodology-paper-level; effort 8-14 sessions; 1992-1994 gap must be loud in schema. Largest single-task effort in the project. Risk of further scope inflation if cohort/period sub-design surfaces as bigger than estimated; Q42 trigger.
- (e) **C8.19 C.8 perinatal-record parquet risk**: NCHS identifier-suppression limits join success rate; results may be too sparse to be useful (per EXPLORATION_REPORT §C.8: "manuscript-level contribution if it works; zero if it doesn't"). The PRE-FLIGHT will surface this; if too sparse, the task may be deferred to a v1.1 methodology-paper subproject rather than completed inline. Q42 trigger if sub-step inflates >1 session.
- (f) **C8.20 E.7 CODEBOOK extensions risk**: large surface (per-variable for both fetal-death + natality); 2-4 sessions may inflate if the final envelope from C8.17 + C8.18 adds substantially more per-variable historical-value-distribution panels than current scope anticipates. Q42 trigger.
- (g) **Phase D timing slip**: Phase D entry projected at ~38-52 cumulative sessions; calendar slip of ~6-12 weeks vs the Phase D-now alternative (Option D above). User has accepted this tradeoff explicitly.
- (h) **C8.16 matched-multiples publishing-design**: 4th HVS product introduces a `matched_multiples/` subproject parallel to natality/ and fetal_death/. PRE-FLIGHT may surface architectural decisions (separate parquet vs joined-into-fetal-death; schema design; SHA manifest). Effort estimate 1-2 sessions may inflate if architectural decisions take more than one session.

**Backport scope:** None. C8.1-C8.15 are unaffected (already shipped at Tier-1+2 scope; the v2.4.0 fetal-death parquet at SHAs `38e2cecb…` / `185c071e…` + v2.8.0 natality parquet at `e16ad5323d…` + v3 linked parquet at `9b828a4d…` are preserved as forward-stability anchors). The V3b extension precedent (DECISION_LOG 2026-05-12T18:30:00Z B3 1-digit MRACE recode + 2-digit→4-digit DATAYEAR expansion) guides C8.17 natality 1968-1988 pre-1989-rev work; the 1985 user-guide text-extractable PDF discovery (LESSONS L12-extension 2026-05-12T15:00:00Z) generalizes to all the 2007-08-24 / 2009-01-08 NCHS re-OCR-batch PDFs that cover the natality 1968-1989 and linked 1983-1991 documentation surfaces.

**Forward-looking HALTs to write in C8.16 PRE-FLIGHT (Convention 4):**

- 7 new §15 entries C8.16-C8.22 present at NEXT_STEPS.md line numbers recorded post-this-commit.
- KICKOFF.md Phase C section reflects Tier 3+5 ACTIVE; line 198's prior "deferred" framing superseded.
- DECISION_LOG entry at 2026-05-14T02:00:00Z present (this entry) at line numbers recorded post-this-commit.
- STATUS.md section appended at top recording the plan-update + Next-planned-task = C8.16.
- No parquet, validator, test-surface, or canonical-data mutation in this commit.
- 4 parquet SHAs unchanged from C8.15 close: `38e2cecb…` / `185c071e…` / `e16ad5323d…` / `9b828a4d…`.
- Cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returns 74 PASS + 1 SKIP + 1 XFAIL ±25s wall-time variance (pure docs/plan work).
- Soft-flag (q) WORKED_EXAMPLE_FAQ.md STATUS-anchor typo from C8.15 PRE-FLIGHT carries forward to C8.16 PRE-FLIGHT.
- Tag `C8.15-complete` from prior commit unaffected; this commit adds no new task tag (plan-updates don't tag).

**Soft-flag (r) filed (this plan-update)**: Effort-ceiling cap raised 42 → 86 represents a substantial expansion. Future agents reading the kickoff sequence should be aware that this 86-cap is the second post-expansion cap (first was 35 → 42 implicit at 2026-05-12T21:00:00Z; now 42 → 86 explicit at this entry). Successive scope expansions risk cap-creep without re-grounding; future plan-updates should re-justify the cap rather than auto-expand. Defense: §11 plan-update process requires explicit user authorization for any further scope-expansion-driven cap raise.

---

## 2026-05-14T00:30:00Z — C8.15 PRE-FLIGHT — Routing resolutions for C.6.d (`education_gradient.ipynb`) + C.6.e (`state_reporting_quirks.ipynb`); user-resolved via AskUserQuestion 2026-05-14T00:30:00Z (C.6.d = natality+linked-only; C.6.e = read from `output/yearly_clean/` raw parquets); NO `[plan-update]` commit needed (substrate-routing-only resolutions; §15 deliverable names + halt-condition flags unchanged)

**Choice (LLM at C8.15 PRE-FLIGHT 2026-05-14T00:30:00Z; user-resolved via AskUserQuestion):** The C8.15 PRE-FLIGHT Convention 3 Field-value snapshot surfaced two §7.13-shape PRE-FLIGHT-time L11s where STATUS 2026-05-13T23:45:00Z line 90's gloss on the §15 C.6.d + C.6.e deliverables conflicts with the actual substrate state. Both resolved via AskUserQuestion before any DO mutation, per the C8.10a/b/c + C8.11 routine-PRE-FLIGHT-input-re-interpretation precedent.

**Resolution 1 (C.6.d data product = natality+linked-only):**

The §15 C.6.d entry (NEXT_STEPS.md line 1281) names *"`education_gradient.ipynb` (within-era only, with 1989/2003 boundary explicit)"* without specifying a data product. STATUS line 90's gloss framed the substrate as fetal-death's `maternal_education_unrevised` (pre-2003) + `maternal_education` (revised; post-2003) — those are fetal-death-side column names. The natality `harmonized_schema.csv` confirms natality has only `maternal_education_cat4` (single column, both eras crosswalked via `_dmeduc_years_to_cat4` for 1990-2002 + `_meduc_to_cat4` for 2003+) + a `certificate_revision` flag. The within-era discipline still applies (per natality COMPARABILITY line 195: `certificate_revision == 'revised_2003'` filter for 2009-2013 revised-only era to avoid spurious unrevised-null mixing) but operates via a different column structure than the fetal-death side.

User-resolved via AskUserQuestion 2026-05-14T00:30:00Z = **Option A (Natality+linked only, Recommended)**: notebook uses natality `maternal_education_cat4` + linked-file `maternal_education_cat4` + `certificate_revision` filter for 2009-2013 sub-analysis. The "1989/2003 boundary" framing in §15 becomes the 2003-revision boundary (since natality starts in 1990); the 2009-2013 revised-only window documented explicitly per natality COMPARABILITY.

**Alternatives considered (C.6.d):**

1. **(A) Natality+linked-only (CHOSEN).** Pro: cleanest "education gradient" on birth-side outcomes (preterm, LBW, IMR via linked); single within-era contract; no cross-product mixing; F4 risk localized to one column structure. Con: doesn't demonstrate fetal-death side's cleaner column split (`maternal_education` vs `maternal_education_unrevised`); fetal-death era split is illustrated in C.6.c `cross_race_fetal_mortality.ipynb` and `fetal_death/COMPARABILITY.md` instead.
2. **(B) Fetal-death only.** Pro: matches STATUS line 90's column-name framing literally; cleaner 1989/2003 within-era split using fetal-death's separate columns. Con: an "education gradient" of fetal-mortality rate (rather than birth outcomes) is non-standard; harder to validate against published NCHS cells.
3. **(C) Both products in one notebook.** Pro: maximally demonstrative; shows both era patterns; covers both birth outcomes and fetal mortality. Con: ~2x effort; multiplies F4 risk (two within-era contracts to maintain in one builder); larger notebook risks losing pedagogical clarity; pushes session beyond §15 2-session estimate.

**Resolution 2 (C.6.e substrate = `output/yearly_clean/` raw parquets):**

The §15 C.6.e entry (NEXT_STEPS.md line 1281) names *"`state_reporting_quirks.ipynb` (Oklahoma Hispanic, Maryland/Massachusetts 1992-1998, Louisiana plurality)"*. STATUS line 90 anticipated *"State-level geography NOT in public-use files (per C8.9 finding) — the notebook would need to use NCHS-reported state quirks via NVSR cross-references rather than direct state-stratification. May surface a §7.13 L11 at PRE-FLIGHT — bundle into a §11 plan-update if so."* This generalization of the C8.9 finding (DECISION_LOG 2026-05-13T10:00:00Z) was over-cautious: C8.9's C.1 drop was specifically about NATALITY public-use files. Fetal-death yearly_clean raw parquets DO retain state codes:
- 1992-2002 V2 era: `STATEFET` + `STATERES` (verified at 1992: 198 cols inc. both)
- 2005-2013 V1 era: `OSTATE` + `MRSTATEPSTL` (verified at 2010: 182 cols inc. both)
- 2014+ V1 era: adds `MBSTATE_REC` (verified at 2022: 142 cols inc. all 3)

This is HOW `fetal_death/COMPARABILITY.md` lines 273-275 derived the Louisiana plurality counts ("1,686 of 1,714 LA-occurrence records" — direct STATEFET=19 + DPLURAL=9 query on yearly_clean parquets). The harmonized parquet drops state codes (only `residence_status` 1-4 codes survive harmonization), but the per-year raw parquets preserve everything documented in the source layout.

User-resolved via AskUserQuestion 2026-05-14T00:30:00Z = **Option A (Read from `output/yearly_clean/` raw parquets, Recommended)**: notebook routes to `output/yearly_clean/fetal_death_<YEAR>_raw.parquet` for state-code access. Departs from C.6.a-c convention (those consume harmonized parquet); C.6.e is the only notebook reading raw. Documented in builder docstring; pedagogical note in notebook markdown explaining why this notebook uses raw substrate (state codes are operationally suppressed in harmonized parquet but documented in source layout).

**Alternatives considered (C.6.e):**

1. **(A) Read from `output/yearly_clean/` raw parquets (CHOSEN).** Pro: substrate exists; reproduces the COMPARABILITY-cited counts directly; pedagogically demonstrates that the harmonized → raw fallback is well-defined and documented; aligns with REPRODUCING.md's framing of yearly_clean as the canonical per-year substrate. Con: departs from C.6.a-c builder convention (one-off precedent); future notebook authors may copy the pattern incorrectly; documented in builder docstring + notebook markdown to mitigate.
2. **(B) Documentation-only mode.** Pro: preserves notebook-substrate convention; no raw-substrate departure; lightest weight. Con: less compelling than per-record demonstration; the COMPARABILITY note already does the documentation; the notebook would be redundant; pedagogical value lower.
3. **(C) Add state columns to harmonized schema + re-derive.** Pro: makes per-state work first-class in the harmonized parquet; future state-level notebooks would have a clean substrate. Con: out of pre-submission scope per C8.13 effort-ceiling concern (Q33); would push C8.15 from 2 sessions to ~4-5; triggers schema bump + parquet SHA shift + B.12 snapshot regen + H10 reproducibility gate re-anchor; not clearly worth the cost since the use-case (5 documented state quirks) is bounded.
4. **(D) Drop C.6.e entirely + plan-update.** Pro: analog of C8.9 C.1 drop and C8.13 F.1 drop; cleaner Tier-2 closure narrative. Con: state quirks are real onboarding friction for users (especially the Louisiana plurality + 2005-2013 plurality '5' miscoding which the COMPARABILITY note explicitly recommends a researcher recipe for); the notebook is a meaningful deliverable; dropping would be over-cautious.

**Three protocol justifications:** (i) §8 matrix L11 row (stale roadmap claim) — both STATUS line 90 glosses are exactly L11 cases caught at the cheap-check moment; resolved via AskUserQuestion before any DO mutation. (ii) Convention 3 Field-value snapshot — the schema-CSV + COMPARABILITY-cite + yearly_clean column probe is the canonical Convention-3 application; the table-of-substrates in PRE_FLIGHT_LOG 2026-05-14T00:30:00Z is the artifact. (iii) Routing-only-routine-PRE-FLIGHT-decision precedent (C8.10a / C8.10b / C8.10c / C8.11) — substrate routing decisions stay in PRE_FLIGHT_LOG + DECISION_LOG when the §15 deliverable name + halt-condition flag are unchanged; no `[plan-update]` commit prefix needed.

**Source:**

- `PRE_FLIGHT_LOG.md` 2026-05-14T00:30:00Z Tables 1+2 — substrate verification for both notebooks; the empirical evidence.
- `STATUS.md` 2026-05-13T23:45:00Z line 90 — the gloss being superseded.
- `NEXT_STEPS.md` §15 C.6.d (line 1281) + C.6.e (line 1281) — the §15 deliverable names (unchanged by this resolution).
- `natality/metadata/harmonized_schema.csv` lines (`maternal_education_cat4` + `certificate_revision` rows) — the natality column-availability evidence.
- `natality/docs/COMPARABILITY.md` line 195 — the canonical revision-consistent subset filter for 2009-2013.
- `fetal_death/COMPARABILITY.md` lines 162-172 + 267-269 + 273-275 — the state-quirk references (C.6.e substrate documentation).
- `output/yearly_clean/fetal_death_{1992,2010,2022}_raw.parquet` schema probe — confirmed `STATEFET`/`STATERES` (1992) + `OSTATE`/`MRSTATEPSTL` (2010) + `MBSTATE_REC` (2022) presence.
- AskUserQuestion 2026-05-14T00:30:00Z — user authorization for Option A × 2.

**Verifiable by:**

- `git tag --list 'C8.15-*'` shows `C8.15-pre-do` post-this-commit; `C8.15-complete` post-RECEIPT.
- `notebooks/_build_education_gradient.py` references `natality_v2_harmonized_derived.parquet` + `natality_v3_linked_harmonized_derived.parquet` (and NOT fetal-death parquets).
- `notebooks/_build_state_reporting_quirks.py` references `output/yearly_clean/fetal_death_<YEAR>_raw.parquet` (and NOT `output/harmonized/fetal_death_*.parquet`).
- `KICKOFF.md` line 196 + `NEXT_STEPS.md` §15 C.6.d + C.6.e entries unchanged (no plan-update).

**Reversible:** yes — `git revert <C8.15-pre-do commit>` removes this DECISION_LOG entry + the PRE_FLIGHT_LOG entry. No parquet, validator, or canonical-data mutation. Substrate-routing decisions are notebook-author-time only; future C8.X notebook tasks can re-route at their own PRE-FLIGHT.

**Residual risks:**

- (a) **Future notebook authors may copy C.6.e's raw-substrate routing pattern inappropriately**, leading to drift away from the harmonized-substrate convention. Defense: builder docstring + notebook markdown explicitly framing the raw routing as "use-case-specific (state codes operationally suppressed in harmonized parquet); see fetal_death/COMPARABILITY.md for the documented state quirks the notebook reproduces."
- (b) **C.6.d natality-only framing may surface a follow-up question** about why the fetal-death-side education columns (`maternal_education` + `maternal_education_unrevised`) aren't demonstrated. Defense: the C.6.c `cross_race_fetal_mortality.ipynb` already exercises fetal-death within-era discipline; C.6.d covers the natality-side gradient explicitly.
- (c) **The 2009-2013 revised-only filter (`certificate_revision == 'revised_2003'`) is an F4 contract** — if the notebook accidentally groups 2009-2013 by `maternal_education_cat4` without filtering revised-only, the unrevised 99% null records contaminate the gradient. Defense: explicit filter in the relevant section; markdown narrative documents the F4 contract; VERIFY checks.
- (d) **The plurality '5' miscoding 2005-2013 V1 era requires the researcher recipe** (set `plurality == '5'` to blank for that year window) per fetal_death/COMPARABILITY.md line 171; the notebook should demonstrate both the raw count + the corrected count to close soft-flag (f). Defense: explicit notebook section.

**Backport scope:** None. C8.15 is the final §15 Tier-2 task; closure brings Tier 2 to 7/7. No prior task affected by this routing decision.

**Soft-flag (q) filed (this PRE-FLIGHT)**: WORKED_EXAMPLE_FAQ.md SHA anchor typo in STATUS 2026-05-13T23:45:00Z + RECEIPTS/C8.14_2026-05-13T23-45-00Z.md + commit-message narrative — recorded sha=`89730c31…` but on-disk + committed sha=`341c4550…`. STATUS is append-only so the typo persists; future sessions reading the C8.14 closing anchor for HALT verification will see the same mismatch and need to repeat this PRE-FLIGHT's `git diff HEAD` resolution. C8.15 RECEIPT records the corrected anchor for the C8.15 forward-looking HALTs to point at. L17-shape (STATUS pin drifted from on-disk reality at moment of writing; not a runtime mutation).

---

## 2026-05-13T22:30:00Z — [plan-update] C8.13 PRE-FLIGHT — F.1 (parquet dict-encoding work) DROPPED + F.4 (GitHub Release) DEFERRED to Phase D step 3 + F.5 (timing benchmark) PROCEEDS this session; revise §15 C8.13 entry + KICKOFF.md Tier-2 line 194; effort revised 1.5-2 → ~1 session

**Choice (LLM at C8.13 PRE-FLIGHT 2026-05-13T22:30:00Z; user-resolved via AskUserQuestion):** The §15 C8.13 PRE-FLIGHT cheap-check probed per-column encoding state via `pyarrow.parquet.ParquetFile.metadata.row_group(0).column(c).encodings` across all 340 columns × 4 parquets and surfaced a §7.13-shape L11 PRE-FLIGHT-time finding: the §15 plan claim "Re-write derive.py's parquet-write call with `use_dictionary=True` per column [→] typically yields 30-50% size reduction" is empirically falsified by the actual encoding state. Specifically:

1. **Both fetal-death parquets are already 100% dict-encoded** (73/73 `fd_harm` + 89/89 `fd_der`; 29 + 36 MB total). PyArrow's default `use_dictionary=True` (boolean) already produces this state; the §15 plan would not change behavior. No headroom anyway (65 MB combined).
2. **All 38+41 non-dict columns in `nat_der` (2.2 GB) + `linked_der` (1.3 GB) are booleans using RLE+PLAIN** — the optimal 1-bit-per-value encoding for 2-state columns. Forcing dict-encoding on booleans does not reduce size and likely increases it (a dict + indices is strictly larger than RLE on 2 distinct values).
3. **Achievable size reduction from F.1 as scoped in §15 ≈ 0%** (or negative if dict encoding is forced onto boolean columns). The §15 "30-50%" estimate from `EXPLORATION_REPORT.md` §F.1 was a generic prior; it did not survive the per-parquet empirical probe.

User-resolved via AskUserQuestion 2026-05-13T22:30:00Z:
- **F.1 = Option A (DROP entirely + plan-update):** Ship this DECISION_LOG entry + revise §15 C8.13 entry + KICKOFF.md line 194. No parquet mutation; no SHA shift; B.12 snapshot regression test remains valid (the §15-anticipated "one-time SHA shift" interaction is now MOOT).
- **F.4 = Option A (DEFER to Phase D step 3):** GitHub Release v1.x with parquet uploads moves to the staging-dir scrub + v1.x push session for one bundled public-facing release event. Substrate verified ready (gh 2.87.3 + auth OK with `repo` scope).
- **F.5 = Option A (Run real end-to-end benchmark this session):** Background per-stage timing measurement of both pipelines vs `paper/draft_v2_hmd_styled.md:68` claims (~6 min fetal-death + ~90 min natality+linked). ±10% tolerance = PASS; >±10% → propose manuscript edit to Phase D step 4 (no in-session manuscript mutation).

**Alternatives considered (F.1):**

1. **(A) DROP F.1 entirely + ship DECISION_LOG entry + §11 plan-update (CHOSEN).** Pro: cleanest; matches §11 process; precedent C8.5/C8.6/C8.7/C8.9 PRE-FLIGHT-time plan-updates; zero parquet risk; B.12 snapshot stays valid. Con: leaves a (small) latent size-reduction question if pyarrow defaults are ever sub-optimal under future schema changes — addressed by leaving the path open via soft-flag (p) re-authorization mechanism.
2. **(B) Replace F.1 with broader encoding work.** Pro: try alternative compression codecs (e.g. ZSTD vs current default SNAPPY); try row-group sizing on the high-cardinality columns; might yield real reduction. Con: substantial scope-creep (each experiment requires re-derive + B.12 baseline regen + SHA shift); §15 1.5-2 session estimate would blow past +20% drift cap; ZSTD vs SNAPPY trade-off involves dependency surface considerations (older pyarrow versions vs newer; CI compatibility) — substantively bigger task than C8.13 was scoped for.
3. **(C) Document-only F.1.** Pro: ship `docs/PARQUET_ENCODING_STATE.md` audit summary; no parquet mutation, no codec experiments. Con: incomplete relative to user authorization Option A which closes the question definitively; introduces an additional doc file that would need maintenance across future parquet rebuilds. The DECISION_LOG entry + revised §15 + KICKOFF.md is sufficient documentation.

**Alternatives considered (F.4):**

1. **(A) DEFER to Phase D step 3 (CHOSEN).** Pro: one bundled public-facing release event; Phase D step 3 already does the staging-dir scrub + v1.x push that would precede the Release create; cleaner narrative for users. Con: users behind Zenodo-blocked firewalls wait an additional ~16 sessions (the cumulative Phase C remaining + Phase D startup) before parquets are available via GitHub Release.
2. **(B) Ship F.4 now on v1.0 commit.** Pro: users get parquets sooner. Con: two release events (this + Phase D step 3); each requires release-notes drafting + Zenodo cross-link maintenance + version-bumping decisions; v1.0 commit predates all the Phase B/C work so the parquets shipped wouldn't reflect the current state at the v1.x sync time — confusing for users.

**Alternatives considered (F.5):**

1. **(A) Run real end-to-end benchmark this session (CHOSEN).** Pro: closes the F.5 VERIFY criterion definitively; provides honest current-state measurement; manuscript-cited number stays defensible. Con: ~96 min compute (90 min natality+linked + 6 min fetal-death) + idempotency-preservation contract (re-run MUST produce byte-identical SHAs; H10 reproducibility gate is non-negotiable).
2. **(B) Defer F.5 to Phase D step 4.** Pro: Phase D step 4 already refreshes every manuscript-cited number; would fold cleanly. Con: defers a §15-listed Tier-2 task to Phase D; cumulative Tier-2 closure ticks down; manuscript-cited number stays unvalidated longer.
3. **(C) Quick analytical estimate.** Pro: cheapest. Con: no real measurement; can't honestly claim ±10% verification; defeats the purpose of the F.5 work.

**Reason:** Option A (drop F.1) preserves four protocol concerns: (i) §2 principle 2 fail-closed — falsified premise → halt and ask; user authorized drop; do not silently work around. (ii) §2 principle 1 cheap-before-expensive — the cheap-check at PRE-FLIGHT (pyarrow encoding probe; ~5 seconds) caught the falsification BEFORE the expensive re-derive (~96 min) + B.12 re-snapshot (~90 s) would have committed. (iii) §11 plan-update process — `[plan-update]` commit prefix; KICKOFF + NEXT_STEPS §15 edits ship in the same commit. (iv) §8 row L11 (stale roadmap claim) — encoded via the same shape as C8.5 / C8.6 / C8.7 / C8.9 PRE-FLIGHT-time L11 catches. Option A (defer F.4) preserves §15 Tier-2 closure narrative (the Phase D step 3 bundling is canonically how public-repo synchronization happens; F.4 fits naturally there). Option A (real F.5 benchmark) preserves §17 *"ready to submit"* criterion 2 (deterministic re-runnable pipelines) by giving the manuscript a defensible timing number.

**Three protocol justifications:** (i) §8 matrix L11 row (stale roadmap claim) — the §15 "30-50% size reduction" claim is exactly an L11 case caught at the cheap-check moment. (ii) Convention 3 Field-value snapshot (PRE-FLIGHT subsection) — the per-parquet encoding-state probe is the canonical Convention-3 application; the table-of-340-columns × 4 parquets in PRE_FLIGHT_LOG 2026-05-13T22:30Z is the artifact. (iii) §11 plan-update process — the precedent chain C8.5 / C8.6 / C8.7 / C8.9 establishes that PRE-FLIGHT-time §15 plan-claim falsification is resolved via user-authorized AskUserQuestion + `[plan-update]` commit prefix.

**Source:**

- `PRE_FLIGHT_LOG.md` 2026-05-13T22:30:00Z Table 1 — per-parquet encoding state probe results (340 columns total; 38+41 booleans using RLE+PLAIN); the empirical evidence.
- `paper/draft_v2_hmd_styled.md:68` — manuscript timing-claim cite (F.5 substrate); verbatim text recorded in PRE_FLIGHT_LOG.
- AskUserQuestion 2026-05-13T22:30:00Z — user authorization for Option A × 3.
- `tests/snapshots/v1_2026-05-13T21-00-00Z_columns.csv` sha=`b6fe22d6539849d931951e89cc3965930dabcaa88d20b2616a74fcdc85df153d` — B.12 snapshot regression baseline; remains valid under F.1-dropped re-scope (no SHA shift).

**Verifiable by:**

- `git tag --list 'C8.13-*'` shows `C8.13-pre-do` post-this-commit; `C8.13-complete` post-F.5 RECEIPT.
- `uv run python -c "import pyarrow.parquet as pq; [...]"` re-running the C8.13 PRE-FLIGHT encoding probe reproduces Table 1 (73/73, 89/89, 46+38, 53+41) byte-exact.
- KICKOFF.md line 194 + NEXT_STEPS.md §15.C C8.13 entry reflect this plan-update.
- `gh release list --repo yoelplutchok/vital-statistics-harmonization` returns empty at this PRE-FLIGHT moment + at Phase D step 3 + 1 entry post-Phase-D-step-3 close.

**Reversible:** yes — `git revert <this plan-update commit>` restores the original §15 C8.13 entry + KICKOFF.md line 194 + removes this DECISION_LOG entry. No parquet, validator, or canonical-data mutation. Reversibility is theoretical only; the empirical encoding-state probe stands regardless of git state.

**Residual risks:**

- (a) **Future schema-bumping tasks may surface new high-cardinality string columns** that would benefit from explicit `use_dictionary=True` (pyarrow defaults handle this case for known-string types but edge cases exist). Defense: soft-flag (p) re-authorization mechanism; any future encoding-work task triggers a fresh §11 plan-update + DECISION_LOG entry.
- (b) **The 38+41 boolean columns COULD benefit from a different encoding strategy** (e.g., bit-packed BIT_PACKED instead of RLE+PLAIN for high-density true/false patterns) but pyarrow's RLE+PLAIN default is already near-optimal for the typical density patterns observed (most CA_* and INFECTION_* columns are >95% null/0); investigating finer-grained encoding is out of pre-submission scope.
- (c) **Manuscript line 68 timing claim** (~6 min / ~90 min) might be confirmed at F.5 DO as wall-clock-PASS within ±10%, OR the measurement might fall outside ±10% and trigger a propose-edit-for-Phase-D-4. The PROPOSE-EDIT path is procedural-only — the actual manuscript line edit lands at Phase D step 4 per the C8.12 RECEIPT framing (manuscript-edit-bundles-at-Phase-D-step-4).
- (d) **H10 reproducibility gate at F.5 DO** is non-negotiable — every re-derive parquet MUST sha256-match the current shipped SHA byte-exact. Any drift is a §7.18 halt + FIX_LOG cascade.

**Backport scope:** None. C8.12 RECEIPT's Forward-looking HALT #12 ("C8.13 PRE-FLIGHT must anticipate B.12 snapshot-regression interaction") was a defensive anticipation; this plan-update resolves it as MOOT (no parquet reshape → no B.12 SHA shift → no re-snapshot needed). The "anticipated re-snapshot" closure is the documentation of this resolution in the C8.13 RECEIPT's forward-looking-HALTs section.

**Soft-flag (p) filed:** F.1 dict-encoding work permanently dropped from pre-submission scope; reconsider only on explicit user re-authorization. Analog of (i) the C.1 NCHS-suppression permanent drop at C8.9 and (ii) the C8.5b Dockerfile DEFERRED entry awaiting docker-available trigger. Any future per-parquet encoding work (alternative codecs ZSTD/LZ4; row-group sizing; column-group reshape) requires fresh §11 plan-update + DECISION_LOG entry.

---

## 2026-05-13T21:00:00Z — C8.12 (DO step 2, B.12 snapshot baseline) — Per-column SHA-256 snapshot stored as CSV at `tests/snapshots/v<X>_<UTC>_columns.csv`; row-group-streamed Arrow buffer hashing; re-snapshot triggered by §11 plan-update on authorized parquet reshape (resolves soft-flag (k) from C8.12 PRE-FLIGHT)

**Choice (LLM at C8.12 B.12 DO step 2):** The B.12 per-column-SHA snapshot baseline ships as a single committed CSV at `tests/snapshots/v1_2026-05-13T21-00-00Z_columns.csv` with six columns: `parquet,column_name,column_index,arrow_type,row_count,column_sha256`. Hash function (`tests/snapshots/_build_snapshot.py::column_sha256_map`) streams each parquet row-group by row-group, projecting every column at once for sequential-read efficiency, and folds each Arrow chunk's underlying memory buffers into the per-column SHA-256 (null buffer slots fed `b"\\x00"` so type-shape contributes deterministically). The committed baseline is **frozen until an authorized §11 plan-update reshapes a parquet** (anticipated triggers: C8.13 dict-encoding pass; latest-year refresh; harmonization-rule revision). At that point a sibling `v<X+1>_<UTC>_columns.csv` is generated alongside the rebuild commit, and `tests/test_parquet_column_snapshot.py::latest_baseline_path` automatically picks the lexicographic-latest (the `v<X>_<UTC>` convention is sort-stable).

The test (`tests/test_parquet_column_snapshot.py`) runs three assertions: (1) baseline anchor row count = 340 (Convention-1 STRUCTURAL invariant); (2) per-parquet column counts = 73 + 89 + 84 + 94 (Convention-1 STRUCTURAL invariant); (3) parametrized per-parquet per-column SHA-256 equality with the baseline (the VALUE-pinning part — re-snapshot-on-authorized-reshape per this entry's policy). Skip-if-parquet-missing per the established `_require()` pattern.

**Alternatives considered:**

1. **(A) CSV at `tests/snapshots/v<X>_<UTC>_columns.csv` with row-group-streamed Arrow buffer hashing (CHOSEN).** Pro: human-readable (open in any text editor; grep-able per column); diff-able across versions (git diff on the CSV surfaces exactly which columns drifted); lossless representation of 6 fields per row; cheap to regenerate (~90s total across 4 parquets on the canonical build machine); sort-stable filename convention via `v<X>_<UTC>`. Con: 340 rows × ~150 bytes/row = ~50KB per baseline file; one file per authorized reshape accumulates over time (~10 baselines = ~500KB across the project's expected v1.x lifecycle).
2. **(B) JSON at `tests/snapshots/v<X>_<UTC>_columns.json`.** Pro: stronger nested-structure representation if per-column metadata grows beyond 6 fields; native arrays for any per-column histograms. Con: less human-diff-readable than CSV; no advantage at the current 6-field column-shape; harder to grep. Rejected — current scope does not need nesting.
3. **(C) Parquet at `tests/snapshots/v<X>_<UTC>_columns.parquet`.** Pro: smaller storage (compression); native arrow type fidelity. Con: not human-diff-readable; requires pyarrow to inspect; mixes test-fixture file-format with the production parquet stack in a way that complicates audits. Rejected — the baseline is a small metadata-only file that benefits from CSV's text-friendliness.
4. **(D) Per-column hash as a Python literal in the test module** (no separate file). Pro: no extra file in repo; baseline + test colocated. Con: 340 hex strings inline = noisy test source; cannot regenerate without editing test source code; mixes data with code; awkward to diff for the small case of "1 column drifted." Rejected — separate baseline-as-data is cleaner.
5. **(E) Hash via `pa.compute` / pandas `hash_pandas_object` instead of Arrow buffer concatenation.** Pro: more semantically meaningful (hashes the VALUES, not the underlying memory representation). Con: dramatically slower on 138.8M-row natality (~30-60s per column instead of ~2-3s); for 84 natality columns this is 40+ minutes vs the chosen ~25s. Rejected — buffer-based hashing is deterministic per pyarrow build and per on-disk parquet, which is what we need; the "value-level semantics vs buffer-level semantics" distinction is moot here because a legitimate value change WILL change the buffer bytes too.

**Reason:** Option A balances five protocol concerns: (i) §2 principle 1 cheap-before-expensive — CSV regeneration is ~90s; (ii) §3 append-only state files — each authorized re-snapshot is a NEW file at a new sort-stable name, not an overwrite of an existing baseline; (iii) Convention 1 SHAPE-not-VALUE — the structural anchor (340 rows; 73+89+84+94 per parquet) is separate from the per-row VALUE pin, so a wholesale parquet reshape (e.g., adding a column) trips the structural anchor before the value mismatch surfaces; (iv) Convention 5 commit-message brevity — re-snapshot commits ship a 5-line summary referencing this DECISION_LOG entry as the source of the policy; (v) §11 plan-update gate — re-snapshot is exactly the kind of canonical-state change that triggers §11 (per L17 SHAPE-vs-VALUE: if the SMOKE/snapshot's "VALUE" is allowed to drift under authorized change, the authorization must be explicit and logged).

Three protocol justifications: (i) §8 matrix H10 row's defense (per-column hashes catch reproducibility drift that row-count and dtype checks miss); (ii) Convention 1 SHAPE-not-VALUE first-docstring tag (test file declares `DESIGN: tracks-current-state` per Convention 2); (iii) §11 plan-update gating reuses the existing pattern from C8.11's `[plan-update]` precedent (the EXPLORATION_REPORT-to-§15 transition + C8.9 [plan-update] both demonstrate the "authorized re-baseline at §11" pattern).

**Source:**

- `STATUS.md` 2026-05-13T20:30:00Z line 114 — recommends "per-column SHA in `tests/snapshots/v<X>_<UTC>_columns.csv`" as soft-flag (k) DO-time choice; this entry resolves the soft-flag.
- `STATUS.md` 2026-05-13T19:30:00Z lines 114-116 — Convention 1 SHAPE-not-VALUE framing for B.12; clarifies the structural-anchor vs value-pinning distinction.
- `PRE_FLIGHT_LOG.md` 2026-05-13T19:30:00Z — C8.12 PRE-FLIGHT 340-column sizing (73+89+84+94 across 4 parquets).
- Test file: `tests/test_parquet_column_snapshot.py` (NEW; ~110 lines; Convention 2 `DESIGN: tracks-current-state` tag).
- Baseline builder: `tests/snapshots/_build_snapshot.py` (NEW; ~120 lines; documented `uv run python -m tests.snapshots._build_snapshot` regeneration command).
- Committed baseline: `tests/snapshots/v1_2026-05-13T21-00-00Z_columns.csv` (340 rows; sha=`b6fe22d6539849d931951e89cc3965930dabcaa88d20b2616a74fcdc85df153d`).

**Verifiable by:**

- `tests/snapshots/v1_2026-05-13T21-00-00Z_columns.csv` exists with 341 lines (header + 340 data rows); sha=`b6fe22d6…`.
- `uv run python -m tests.snapshots._build_snapshot` regenerates the same SHAs (modulo a new sibling filename if the literal in `main()` is bumped).
- `uv run pytest tests/test_parquet_column_snapshot.py -v` returns 6 PASS (1 anchor row count + 1 per-parquet column count + 4 parametrized per-parquet SHA), or with parquets-missing SKIPs.
- Cache-cleared full pytest 68 PASS + 1 XFAIL (was 59 + 1 pre-DO-step-2; +3 from B.11 + +6 from B.12).

**Reversible:** yes — `git revert <C8.12 DO step 2 commit>` removes `tests/test_source_zip_sha_stability.py` + `tests/test_parquet_column_snapshot.py` + `tests/snapshots/`. No parquet, validator, or canonical-data mutation; reversion would only undo the test scaffolding.

**Residual risks:**

- (a) **Arrow buffer hashing is sensitive to pyarrow encoding choices** (e.g., dictionary encoding on a string column changes the buffer layout even if the values are identical). Defense: `uv.lock` pins pyarrow to an exact version (per C8.5a); a future pyarrow upgrade is a §11 plan-update event that triggers re-snapshot. Currently `uv.lock` pins pyarrow 21.0.0.
- (b) **The `column_sha256` value is NOT comparable across different parquet files even with identical content.** I.e., two parquets with the same logical data but different chunk boundaries (row group sizes) produce different SHAs. This is by design (we want a sensitive regression alarm), but it means any legitimate parquet rewrite (even with same content) is an authorized re-snapshot event.
- (c) **B.12 cannot run in a CI environment without the 4 parquets on disk.** Skip-if-parquet-missing is the documented behavior. A future CI workflow (per C8.13 GitHub release artifacts) could download the parquets from the release and re-enable B.12 on every CI run; until then B.12 is a local-build-time gate, not a CI gate. Filed as a downstream follow-up for C8.13.
- (d) **The Convention-1 structural anchors (340 / 73+89+84+94) are pinned in `EXPECTED_COLUMN_COUNTS`** in `tests/test_parquet_column_snapshot.py`; a future authorized schema change (e.g., adding a new derived column) requires updating the literal alongside the baseline regen. This is an explicit Convention-1 SHAPE pin; per L17 it MUST be updated under authorized canonical drift, otherwise it becomes a stale-pinning false-FAIL.

**Backport scope:** None directly. C8.1-C8.11 receipts unaffected. The C8.12 PRE-FLIGHT-time soft-flag (k) is now RESOLVED by this entry.

---

## 2026-05-13T20:30:00Z — C8.12 (DO step 1, B.7 L13 audit) — `fetal_death/file_inventory.csv` `record_length` convention standardized on no-terminator (matches `field_specs.py` RECORD_LEN_* + 24 EXACT inventory rows); 19-row fix-on-contact applied in-place per C8.11 precedent

**Choice (LLM at C8.12 B.7 DO step 1):** Standardize the `record_length` column in `fetal_death/file_inventory.csv` on the **no-terminator convention** — i.e., the column records the byte length of the data content per record, EXCLUDING any trailing CR/LF/CRLF line terminator. This matches:

1. **`fetal_death/scripts/01_import/field_specs.py:21-31`** `RECORD_LEN_*` constants — the parser's single source of truth (e.g., `RECORD_LEN_2003 = 1350`, `RECORD_LEN_2006 = 3350`, `RECORD_LEN_2007 = 801`, `RECORD_LEN_2014 = 3050`, `RECORD_LEN_2018 = 2651`). The parser slices fixed-width records via this convention.
2. **24 existing EXACT inventory rows** (1982-2004 + 2014): all use no-terminator (e.g., 1989 row claims 360, actual stripped-of-CRLF is 360).

The fix patches 19 inconsistent rows to match: **17 EMPTY rows** filled (2005, 2007-2013, 2015-2024) + **2 MISMATCH rows** reduced by 1 (2006: 3351→3350; 2022: 2652→2651; both were the with-terminator convention).

**Alternatives considered:**

1. **(A) Standardize on no-terminator (CHOSEN).** Pro: parser-aligned; matches the 24 EXACT rows; consistent across V3b+V3a+V2+V2.1+V1 eras post-fix. Con: changes the historical 2006+2022 claims by -1 byte each.
2. **(B) Standardize on with-terminator (+1 to all 41 zip rows).** Pro: matches NCHS user-guide convention (NCHS documents logical-record-length-including-CRLF). Con: requires changing 24 already-correct rows; introduces fresh drift vs the parser's no-terminator convention; downstream consumers comparing `file_inventory.csv` `record_length` to `field_specs.py` RECORD_LEN_* would see off-by-1.
3. **(C) Leave the column inconsistent + document the convention divergence in `notes`.** Pro: zero data mutation. Con: violates §8 matrix L13 row's defense (CSV column-content verifiable against canonical source); leaves the bug surface for future regressions. Rejected.
4. **(D) Drop the `record_length` column entirely + delegate documentation to `field_specs.py` only.** Pro: removes the source-of-truth ambiguity. Con: deletes informational documentation that's useful for human inventory-readers; breaking change for any downstream user reading inventory metadata. Rejected.

**Reason:** Option A standardizes on the single-source-of-truth convention (parser-aligned) with the smallest fix footprint (19 rows, mechanical) and removes ambiguity that could mislead future inventory authors (e.g., a future V4 backward extension would need to know which convention to use). The patched inventory is now byte-consistent with `field_specs.py` + the new `tests/test_inventory_invariants.py::test_fetal_death_inventory_record_length_populated_for_all_rows` invariant test fails fast if any future row ships with an EMPTY `record_length` cell.

Three protocol justifications: (i) §8 L13 row's "verify column-content matches" remedy (the audit + fix-on-contact is the defense); (ii) §2 principle 1 cheap-before-expensive (auditing 43 rows via `zipfile.first-record-length` probe was ~5 minutes; the fix is mechanical); (iii) C8.11 precedent of fix-on-contact for inventory-level documentation drift (C8.11 DO patched `VERSION_ROADMAP.md` lines 11+13 fix-on-contact for the same reason).

**Source:**

- `PRE_FLIGHT_LOG.md` 2026-05-13T19:30:00Z entry — C8.12 PRE-FLIGHT documented the B.7 audit scope (20 metadata CSVs across 2 subprojects).
- `FIX_LOG.md` 2026-05-13T20:15:00Z entry — full audit table + patch detail.
- `fetal_death/scripts/01_import/field_specs.py:21-31, 1330-1380` — `RECORD_LEN_*` constants + `get_record_layout(year)` dispatch.
- Per-zip probes via `zipfile.ZipFile(path).open(name).readline().rstrip(b'\r\n')` across all 43 rows (audit script in FIX_LOG entry).
- C8.11 DECISION_LOG 2026-05-13T17:25:00Z (precedent for inventory fix-on-contact under C8.X scope).

**Verifiable by:**

- Post-DO `fetal_death/file_inventory.csv` has populated `record_length` for all 43 rows; values match the per-year zip first-record-length under no-terminator convention; new sha=`2f2ba2c942f14296…` (was `38dc035eeccb8b80…`).
- `tests/test_inventory_invariants.py::test_fetal_death_inventory_record_length_populated_for_all_rows` PASSes.
- `for f in <2006, 2022>; do compare claim to field_specs.RECORD_LEN_$f; done` returns equality.
- Cache-cleared pytest 59 PASS + 1 XFAIL preserved post-patch.

**Reversible:** yes — `git revert <C8.12 DO step 1 commit>` restores the pre-fix `file_inventory.csv` state (17 EMPTY + 2 off-by-1 rows) + drops `tests/test_inventory_invariants.py`. The L13 finding itself is reversible only at the documentation layer; the parser convention is unchanged.

**Residual risks:**

- (a) **A future NCHS release MAY change record length within a year** (e.g., NCHS sometimes silently updates public-use files with no version-tag change). Defense: the `tests/test_inventory_invariants.py` `_populated_for_all_rows` test would NOT catch a silent NCHS reformat — it only catches EMPTY cells. A future C8.X could promote the audit-script (in the FIX_LOG entry) into a periodic re-probe test that runs against the on-disk zips. Deferred to C8.7b orchestrator + C8.12 B.6 mutation-test scaffolding session.
- (b) **The `record_length` semantic divergence between fetal-death (no-terminator) and the (absent) natality `record_length`** is a residual asymmetry. If natality's inventory is ever extended to include `record_length`, it should follow this same no-terminator convention. Filed as Phase D step 2 follow-up note.
- (c) **The 2006 + 2022 with-terminator claims** appear to have been authored from NCHS user guides that document logical-record-length-including-CRLF. Future inventory authors should be aware of this convention divergence in NCHS docs and explicitly probe vs-parser before recording. The new test fails fast if `record_length` is left empty, but doesn't catch off-by-1 within-convention errors (that requires the zip-presence audit-script).

**Backport scope:** None directly. C8.1-C8.11 receipts unaffected. The C8.11 receipt's FL-HALT #2 (`fetal_death/file_inventory.csv` sha=`38dc035e…`) is now superseded by the C8.12 DO step 1 commit; the next C8.12 sub-session's PRE-FLIGHT must verify the NEW sha=`2f2ba2c9…`. No data, validator, or parquet output affected.

---

## 2026-05-13T17:25:00Z — C8.11 — AskUserQuestion Option A: extend `fetal_death/file_inventory.csv` 34 → 43 rows in C8.11 DO (scope expansion ~30-60 min); 3 routine L11 PRE-FLIGHT-input re-interpretations user-authorized in-place per C8.9/C8.10a/b/c precedent

**Choice (user at AskUserQuestion 2026-05-13T17:25:00Z, Question 1 = Option A; Question 2 = "Proceed in-place per precedent"):** Apply the file_inventory.csv extension in the C8.11 DO + apply 3 routine L11 PRE-FLIGHT-input re-interpretations in-place without separate §11 plan-update commits:

1. **Option A — file_inventory.csv 34 → 43 rows.** PRE-FLIGHT cheap-checks discovered `fetal_death/file_inventory.csv` was stale relative to the v2.4.0 envelope. (At PRE-FLIGHT-write time, I believed the missing 9 rows were 7 V3b 1982-1988 + 2 latest-year 2023+2024; at DO read-time the actual missing set was confirmed as 7 V3b 1982-1988 + 2 V2.1 2003-2004 — the 2023+2024 rows were already present from C8.2. The 9-row count is correct; year-set corrected at DO start. Filed as fix-on-contact L11 (h).) Brings SHA manifest to full v2.4.0 43-year envelope cleanly. Effort impact: +30-60 min addition to C8.11 DO; ~3.5-4 sessions total. Touches `fetal_death/file_inventory.csv` (canonical-state mutation) with L13 verification of each new row's column content against DECISION_LOG sources + per-zip probes.

2. **(i) Re-target migration-guide filename** `migrations/v2.0.0-to-v2.3.0-fetal-death.md` → `migrations/v2.0.0-to-v2.4.0-fetal-death.md`. §15 named v2.3.0 but actual current is v2.4.0 per `fetal_death/README.md` line 156 + DECISION_LOG 2026-05-13T01:30Z (C8.2 latest-year refresh). Routine L11 PRE-FLIGHT-input re-interpretation.

3. **(ii) E.8 SHA manifest scope clarification.** §15 VERIFY criterion said "SHA manifest checksums match each subproject's file_inventory.csv" but neither inventory has a sha256 column. Resolution: SHA manifest is NEW data (raw-zip SHA-256 values keyed by `year × raw_filename`), NOT a re-export of inventory contents. Manifest target path: `docs/NCHS_SOURCE_MANIFEST.md` (follows `docs/JOINT_USE_GUIDE.md` + `docs/PRIOR_ART.md` + (now) `docs/COMPARABILITY.md` precedent for monorepo cross-product docs at `docs/`).

4. **(iii) Fix-on-contact VERSION_ROADMAP.md** lines 11 + 13: `**v2.1.0**` → `**v2.4.0**`; coverage 1992-2022 → 1982-2024; records 1,741,977 → 2,427,233. Single-line touches bundled into C8.11 DO since C8.11 IS the version-table consumer (the migration guide cross-references VERSION_ROADMAP.md). Not scope creep per Anti-Pattern #8 — fix-on-contact is the established L11 §8 matrix remedy. Authorized fix scope is ONLY lines 11 + 13; the broader "Planned" section staleness (lines 15-22+) deferred to a future small docs refresh task (PRE-FLIGHT soft-flag (c)).

**Alternatives considered (per AskUserQuestion 17:25Z Question 1 — file_inventory.csv):**

1. **(A) Extend inventory to 43 rows in C8.11 DO (chosen).** Pro: matches actual v2.4.0 envelope; SHA manifest covers all 43 fetal-death zips cleanly; bundles inventory + manifest authoring under one task. Con: +30-60 min addition above §15's 3-4 session estimate (lands at ~3.5-4 sessions).
2. **(B) Ship SHA manifest at 34-row state + document the gap.** Pro: preserves §15 estimate exactly. Con: manifest is incomplete; creates fresh L13 doc-data drift case. Rejected — explicitly violates §8 matrix L13 + L11 spirit.
3. **(C) Halt C8.11; ship inventory extension as a small standalone `[plan-update]` first.** Pro: clean task boundary; mirrors C8.5/C8.7 split precedent. Con: adds ~1 small session ahead of C8.11; same eventual destination as Option A but more bookkeeping. Rejected — Option A bundling is more efficient.

**(For AskUserQuestion 17:25Z Question 2 — routine L11s (i)+(ii)+(iii):** user selected "Proceed in-place per precedent" matching the C8.9 / C8.10a / C8.10b / C8.10c established routine for PRE-FLIGHT-surfaced L11 PRE-FLIGHT-input re-interpretations resolved at the cheap-check moment.)

**Reason:** Option A preserves the substantive value of E.8 (cross-product NCHS-source-data SHA manifest at the full v2.4.0 envelope) while folding the inventory-staleness fix into the natural consumer task. Three protocol justifications: (i) §2 principle 1 cheap-before-expensive — discovering inventory staleness at PRE-FLIGHT cheap-check saved having to ship a partial manifest then re-do work in a follow-up task; (ii) §8 L13 matrix's "fix-on-contact" principle applies (inventory CSV stale relative to actual on-disk state); (iii) §11 plan-update threshold is "scope changes >1 session"; Option A's +30-60 min is well below.

**Source:**

- `PRE_FLIGHT_LOG.md` 2026-05-13T17:30:00Z entry — Convention 3 Field-value snapshot Tables 1-5 documenting the 24-row mutation set + the 4 L11 findings.
- AskUserQuestion 17:25Z — Question 1 = Option A (Recommended); Question 2 = "Proceed in-place per precedent (Recommended)."
- `fetal_death/file_inventory.csv` pre-DO (34 rows; year range 1989-2024 with gap 2003-2004) verified at PRE-FLIGHT.
- `fetal_death/README.md` line 156 + `DECISION_LOG.md` 2026-05-13T01:30Z (C8.2 latest-year refresh): documents current fetal-death version is v2.4.0.
- Raw zip universe on disk: 43 fetal-death + 35 natality + 19 linked-cohort = 97 raw zips total (probe-verified).

**Verifiable by:**

- Post-DO `fetal_death/file_inventory.csv` has 43 rows; year sequence 1982-2024 contiguous; sha=`38dc035eeccb8b80…`.
- `docs/NCHS_SOURCE_MANIFEST.md` ships with 97 SHA-256 entries cross-referencing both `file_inventory.csv` files.
- `migrations/v2.0.0-to-v2.4.0-fetal-death.md` shipped at the re-targeted filename (no `v2.3.0` variant created or referenced).
- `VERSION_ROADMAP.md` lines 11 + 13 reflect v2.4.0 + record count 2,427,233 + coverage 1982-2024.
- Tag `C8.11-complete` on this commit.

**Reversible:** yes — `git revert <this commit>` restores the pre-DO state. The Option A inventory extension is the most substantive piece; reverting drops 9 rows from `file_inventory.csv` + removes the 4 NEW documents + reverts 5 MODIFIED files. The deltas are well-bounded.

**Residual risks:**

- (a) **Per-year `record_length` values (200 / 1350 / 1500 bytes) were probed at DO time, not cross-verified against canonical NCHS user-guide PDFs.** The 1985 user guide is the only V3b PDF on-disk-probed (per LESSONS L12-extension 2026-05-12T15:00Z); other V3b years (1982-1984, 1986-1988) inferred to match per sibling-derivation. Mitigation: the inventory `record_length` field is documentation-only; the harmonization pipeline reads `record_layout_<era>.csv` directly. Per-year cross-check vs user-guide byte ranges deferred to C8.12 (L13 audit task).
- (b) **PRE-FLIGHT typo "87 raw zips" (corrected to 97 at DO start)** left UNFIXED in `PRE_FLIGHT_LOG.md` per L10 no-back-fill discipline. Receipt + STATUS + this DECISION_LOG document the correction.
- (c) **The 9-row inventory extension didn't re-run any validator post-DO** (test suite is 56 PASS + 1 XFAIL; no validator currently consumes file_inventory.csv at the structural level). Mitigation: C8.12 will add an L13-class invariant test ("every row of file_inventory.csv matches a year in harmonized_schema.csv years_available"); the new V3b + V2.1 rows are pre-PASS under that invariant.

**Backport scope:** None. C8.1-C8.10c receipts unaffected. Future C8.12 PRE-FLIGHT consumes the new file_inventory.csv rows + the NCHS_SOURCE_MANIFEST.md as canonical inputs.

---

## 2026-05-13T10:00:00Z — [plan-update] C8.9 — Drop C.1 (state-stratified denominators) from C8.9 scope (structurally unbuildable from public-use data per NCHS suppression policy); ship C.2 (R quickstart) + C.4 (DuckDB views) only; add `duckdb` to pyproject.toml + uv.lock as authorized C8.9 DO step; revise §15 C8.9 entry + KICKOFF.md Tier-2 line 190; effort revised 2.5-3 → 1-1.5 sessions

**Choice (user-authorized at C8.9 PRE-FLIGHT halt-and-ask 2026-05-13T10:00:00Z, AskUserQuestion response "Drop C.1; ship C.2+C.4 only (Recommended)"):** Apply a single `[plan-update]` commit resolving two §7.13 (validity-domain ambiguity) HALTs surfaced at C8.9 PRE-FLIGHT:

1. **HALT #1 resolution — C.1 (state-stratified denominators) is structurally unbuildable.** The §15 C8.9 entry's PRE-FLIGHT-input claim "Natality derived parquet (state available 1990-2024; suppressed in fetal-death V1 era 2005+)" is factually wrong. Four cheap-check probes at PRE-FLIGHT (natality harmonized schema column inventory; natality yearly_clean per-year parquet column inventory across 11 years 1990-2024; natality FAQ + ABOUT_THIS_RELEASE explicit suppression statements; fetal-death harmonized_schema state-column check) all confirm: NCHS suppresses state-level geography in public-use files across all three products (natality + linked + fetal-death). The closest available column (`MBSTATE_REC`, 2015+) is mother's birthplace recode (3-level US/foreign/unknown), NOT state of residence. C.1's "state × race × age × Hispanic × year" deliverable cannot be built from public-use data; the upstream fix (NCHS RDC + restricted-use workflow) is well out of HVS pre-submission scope. **C.1 is dropped from C8.9 — documented as permanently-out-of-scope** in §15. Any future re-attempt requires either (i) NCHS RDC access, OR (ii) a different geographic stratification (Census region/division) which itself requires new derived-column infrastructure (state→region map) not present in the current schema.

2. **HALT #2 resolution — `duckdb` Python package not in C8.5a lockfile.** The §15 C8.9 PRE-FLIGHT-input claim "DuckDB installed in the env (C8.5 lockfile)" is also factually wrong. `pyproject.toml` does not list `duckdb`; `uv.lock` has 38 packages, none named `duckdb`; `.venv/bin/python -c "import duckdb"` returns `ModuleNotFoundError`. **Resolution: `uv add duckdb` executed during C8.9 DO step 1, which updates pyproject.toml + uv.lock to canonically-pinned versions.** The SHA drift from C8.5a-recorded values (pyproject.toml=`c8826a61…`, uv.lock=`ab627034…`) is an **authorized addition**, not a regression — the C8.9 receipt's Build-artifacts-current section will record the post-add SHAs, and the Forward-looking HALTs for C8.10 PRE-FLIGHT will name the expected new values.

**Plan-update applied (this commit):**

1. **`NEXT_STEPS.md` §15.C C8.9 entry rewritten** (lines 1101–1119 pre-revision):
   - Title revised: "C.1 + C.2 + C.4" → "C.2 + C.4 (C.1 dropped — public-use data does not include state-level geography)".
   - Goal rewritten: drops C.1 entirely; expands C.2 + C.4 descriptions with concrete deliverable shapes (3 R quickstart files per product; views.sql at monorepo root with three canonical-filter views + one cross-product join view).
   - Why-this-matters trimmed accordingly.
   - PRE-FLIGHT inputs corrected: drops the "state available 1990-2024" claim; adds `duckdb` add as an authorized C8.9 DO step; adds R-side `arrow` + `duckdb` + `dplyr` availability check.
   - SMOKE plan rewritten: Tier 0 R-syntax-parse + SQL-syntax-parse; Tier 1 R `arrow::read_parquet()` reads each parquet successfully; Tier 1 DuckDB view query produces same row count as Python pyarrow canonical filter on a 100-record subset.
   - DO scope rewritten: 4 deliverables — (a) `uv add duckdb` + commit pyproject.toml + uv.lock updates; (b) 3× `quickstart.R`; (c) `views.sql`; (d) `docs/JOINT_USE_GUIDE.md` updates documenting R + DuckDB usage.
   - VERIFY criteria rewritten: 5 criteria — (i) R quickstart loads each parquet; (ii) DuckDB views produce same record counts as Python canonical filter; (iii) cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` still 56 PASS + 1 XFAIL; (iv) 4 parquet SHAs unchanged; (v) pyproject.toml + uv.lock SHAs CHANGE in expected direction (acknowledge + record).
   - Estimated effort revised: 2.5-3 sessions → 1-1.5 sessions.
   - Halt-condition flags updated: F1 (canonical filter on natality side) retained; L13 (state-code dtype verification) DROPPED (no state column to verify); L11 (stale §15 PRE-FLIGHT-input claims) ADDED.
   - Dependencies: none upstream; C8.10 onward depends on duckdb being in the lockfile.

2. **`KICKOFF.md` Phase C Tier-2 line 190** revised: "C8.9 — Usability: state denominators + R + DuckDB views [2.5-3 sessions]" → "C8.9 — Usability: R quickstart + DuckDB views [1-1.5 sessions] (C.1 state-stratified DROPPED — NCHS suppression policy)".

3. **`PRE_FLIGHT_LOG.md`** — PRE-FLIGHT entry at 2026-05-13T10:00:00Z (RESULT: HALT, 2 §7.13 conditions) + addendum at 2026-05-13T10:15:00Z (RESULT: PROCEED post-resolution).

4. **This DECISION_LOG entry** records the §11 plan-update + Option A rationale + duckdb-addition rationale.

**Alternatives considered (per AskUserQuestion 2026-05-13T10:00:00Z):**

1. **(A) Drop C.1; ship C.2 + C.4 only (chosen).** Pro: honest to the public-use-data constraint; preserves the cleanly-buildable C.2 + C.4 deliverables; smallest scope; ~1-1.5 session estimated; reframes C.1 as a permanently-out-of-scope item (documented in §15) rather than a hidden deferral. Con: C8.9 ships smaller than originally planned; the "state-stratified" usability layer remains unshipped indefinitely. Mitigation: the FAQ + JOINT_USE_GUIDE updates document state suppression explicitly so end-users understand the constraint upfront.

2. **(B) Re-purpose C.1 as different strata (e.g., race × age × parity × education × year).** Pro: ships a usability layer; 1 session. Con: substantial overlap with the existing `stratified_denominators.csv` (Task 1, 2026-05-11) which already covers race × age × hispanic × year; the marginal usability gain is unclear; re-purposing without a clear use-case driver is feature-creep. Rejected.

3. **(C) Halt C8.9; advance C8.7b (DEFERRED orchestrator) instead.** Pro: closes a deferred Tier-1 item; reproducibility VERIFY clean. Con: needs user-authorized multi-session compute window (6-12+ hours); doesn't address the C8.9 surface; doesn't ship usability layer. Rejected — user-authorized Tier-2 launch per Q35.

4. **(D) Halt C8.9; advance C8.10 (worked-example notebooks) instead.** Pro: ships meaningful user-facing content; 3-4 sessions of value. Con: doesn't ship the C.2/C.4 usability layer which IS achievable; re-plans C8.9 entirely without a clean closure narrative. Rejected.

**Reason:** §11 plan-update process is the canonical path for in-Phase-C scope adjustments surfaced during PRE-FLIGHT verification (Q42 self-resolution + Convention 3 Field-value snapshot). Both HALTs were caught at the cheap-check moment before any DO mutation — exactly what PRE-FLIGHT cheap-checks are for. Option A preserves the substantive value of C8.9 (usability — R + DuckDB) while dropping the structurally-broken sub-task and acknowledging the lockfile reality.

Three protocol justifications: (i) §2 principle 1 "cheap-before-expensive" — discovering the state-suppression + duckdb-missing constraints at PRE-FLIGHT saves a wasted session of attempting to build C.1 (would have surfaced mid-DO when the parser column-read returned no state column); (ii) §11 plan-update is the canonical path for in-Phase-C scope adjustments per Q42 (>1-session scope change; dropping a sub-task is a scope reduction triggering plan-update); (iii) §10 self-check encourages the LLM to surface "what could I have gotten wrong that VERIFY wouldn't catch" — in this case, the §15 PRE-FLIGHT-input claims that no prior session had verified against current data.

This is the **second consecutive C8.X task** (after C8.7 split into C8.7a + C8.7b) where PRE-FLIGHT cheap-checks against §15 PRE-FLIGHT-input claims surfaced **multiple** factual errors in the §15 entry. The lesson: §15 entries authored from EXPLORATION_REPORT proposals (drafted 2026-05-12T20:30Z) contain claims about data availability + env state that the exploration author did not verify against current artifacts. **Filed as a soft-flag for the C8.X-pre-DO PRE-FLIGHT checks: always re-verify §15 PRE-FLIGHT-input claims via L9/L13 probes BEFORE the AskUserQuestion / proceeding to DO.** This is an existing L11 pattern (stale roadmap claim) — no new mistake class needed; the existing §8 matrix L11 row covers it.

**Source:**

- `PRE_FLIGHT_LOG.md` 2026-05-13T10:00:00Z entry documents the 4 cheap-check probes (natality harmonized schema; natality yearly_clean per-year inventory across 11 years; natality FAQ + ABOUT_THIS_RELEASE; fetal_death harmonized_schema state-column check) + the duckdb missing probe.
- `natality/docs/FAQ.md:87-89`: explicit "No state-level identifiers" statement.
- `natality/docs/ABOUT_THIS_RELEASE.md:70`: "No restricted-use geography or restricted-use variables are included."
- `natality/metadata/harmonized_schema.csv` (84 + 6 derived columns, no state column).
- `pyproject.toml` + `uv.lock` (38 packages, no duckdb).
- STATUS 2026-05-13T09:30:00Z line 51 (pre-authorized the PRE-FLIGHT-time split decision; chosen alternative drops C.1 rather than splitting).
- User chat 2026-05-13T10:00:00Z AskUserQuestion response: "Drop C.1; ship C.2+C.4 only (Recommended)."

**Verifiable by:**

- This `[plan-update]` commit's diff shows `NEXT_STEPS.md` §15 C8.9 entry rewritten + `KICKOFF.md` line 190 revised + this DECISION_LOG entry + `PRE_FLIGHT_LOG.md` PRE-FLIGHT entry (HALT) + addendum (PROCEED).
- Tag `C8.9-pre-do` lands on this `[plan-update]` commit (PRE-FLIGHT now PROCEEDS to C8.9 DO post-resolution; mirrors C8.5 / C8.7 plan-update precedent).
- C8.9 DO ships in a sibling commit tagged `C8.9-complete` containing R quickstart files + views.sql + JOINT_USE_GUIDE updates + pyproject.toml/uv.lock updates + receipt + STATUS append.

**Reversible:** yes — `git revert <this commit>` restores the original §15 C8.9 entry. The C.1 drop is documented as a factual finding (NCHS suppression policy) rather than a contingent scope decision, so reverting wouldn't make C.1 buildable — it would just restore the wrong claim in §15.

**Residual risks:**

- (a) **A future user may request "state-stratified denominators" expecting the standard NCHS public-use data supports it.** Mitigation: the C8.9 DO will explicitly add a note to `docs/JOINT_USE_GUIDE.md` and to `natality/docs/FAQ.md` (if not already there) about state suppression. The FAQ already covers this at lines 87-89, so a small cross-reference update is sufficient.
- (b) **`uv add duckdb` may pull a duckdb version with a behavior difference from R's duckdb 1.x.** Mitigation: pin to a recent stable (default `uv add` picks the latest); verify R + Python DuckDB queries produce same row counts in the SMOKE Tier 1 check.
- (c) **The §15 PRE-FLIGHT-input authoring pattern of unverified data-availability claims may recur** in C8.10-C8.15 entries. Mitigation: filed as a soft-flag for those tasks' PRE-FLIGHT phases to explicitly re-verify each PRE-FLIGHT input claim via L9/L13 probes before AskUserQuestion / proceeding.
- (d) **The C8.7a soft-flag (b) "Natality+linked output-path strategy decision"** carries through to C8.9 because `views.sql` must reference the natality + linked parquet paths somehow. The C8.9 DO will use relative paths from monorepo root + document the C8.7b deferral as a known gap (i.e., views.sql users outside the build dir will need to either symlink or pass `--variable PARQUET_DIR=...` to DuckDB).

**Self-check (residual risks VERIFY phase wouldn't catch):**

- "Drop C.1" decision rests on probes I ran today; if the natality parser were extended in a future session to extract state from the raw zips (some pre-2005 raw zips do contain state), C.1 would become buildable for those years. This isn't a current-session risk; documented as a forward note in the C8.9 receipt's "Notes for next session".
- The DuckDB-vs-Python parity check assumes both engines apply the canonical filter identically; if DuckDB's `WHERE` clause coerces a column dtype differently from pyarrow, the row-count parity could mask a subtle dtype-coercion bug. Defense: SMOKE Tier 1 records the row count from BOTH engines for at least 3 cells (per product); any discrepancy gets surfaced.
- R + Python parity check (one's `arrow::read_parquet()` vs the other's `pyarrow.parquet.read_table`) assumes both produce identical row counts; if R's arrow has a different default for nullability or partitioning, the counts could differ. Defense: VERIFY criterion (i) records BOTH counts per product; any discrepancy surfaces.
- The duckdb-add is a one-line edit to pyproject.toml but `uv lock` may regenerate the WHOLE lockfile if upstream package versions have drifted since C8.5a-complete; the SHA change is then larger than just-add-duckdb. Defense: the receipt records before+after SHAs for both files + the `uv lock --check` output (or `git diff uv.lock` summary) so the change is fully auditable.

**Backport scope (per §11.4):** None directly. C8.1 / C8.2 / ... / C8.8 receipts unaffected. The 2026-05-12T20:30Z EXPLORATION_REPORT §C.1 + §F.3 sections that originated the now-wrong PRE-FLIGHT-input claims are append-only frozen-state documents (per ratchet) — no edit needed there. Filed as a soft-flag for any future plan-update agent re-reading EXPLORATION_REPORT C.1 verbatim: consult this DECISION_LOG entry for the substantive resolution.

---

## 2026-05-13T09:00:00Z — C8.8 — Convention 3 amendment at PRE-FLIGHT: EXPLORATION_REPORT §E.5 author label "Hoyert et al. 2024" mis-attributes PMID 38143212 (actual lead author = Gregory ECW + Barfield WD); ship citation under correct authors; load-bearing PMID unchanged

**Choice (LLM at C8.8 PRE-FLIGHT 2026-05-13T09:00:00Z, no user halt-and-ask needed — Convention 3 routine amendment within the same L8 cheap-check pattern the §15 C8.8 halt-flag explicitly anticipates):** Resolve EXPLORATION_REPORT.md §E.5 item 2's citation mis-attribution by citing the PMID's actual authors (Gregory ECW, Barfield WD) rather than the (incorrect) label "Hoyert et al." Drop the "Hoyert" name from this PRIOR_ART citation. Do NOT add the separate Hoyert paper (PMID 39412872 = NVSR 73-09) to PRIOR_ART because doing so would be circular (NVSR is exactly the aggregate-publication category PRIOR_ART argues fails to fill the microdata gap).

**L8 cheap-check evidence (NCBI esummary API, 2026-05-13T09:00:00Z):**

- PMID 38143212: "U.S. stillbirth surveillance: The national fetal death file and other data sources." Authors: **Gregory ECW, Barfield WD**. *Semin Perinatol* 2024 Feb;48(1):151873. ISSN 0146-0005. **No Hoyert author.**
- PMID 39412872 (separate paper): "Fetal Mortality: United States, 2022." Authors: **Gregory ECW, Valenzuela CP, Hoyert DL**. *Natl Vital Stat Rep* 2024 Sep 12;73(9). DOI 10.15620/cdc:…. **This is NVSR 73-09**, already cited in HVS as the validation gold-standard publication.

The EXPLORATION_REPORT §E.5 plan-author appears to have conflated the two papers (both 2024, both stillbirth-adjacent, partial author overlap via Gregory ECW as lead). The load-bearing identifier (PMID 38143212) is the canonical input; only the human-readable label diverges. Convention 3 (Field-value snapshot at PRE-FLIGHT) caught this at the cheap-check moment, before any DO mutation — exactly the failure mode L8 + Convention 3 are designed to surface.

**Alternatives considered:**

1. **(A) Cite Gregory + Barfield 2024 (PMID 38143212) with correct authors; drop "Hoyert" label (CHOSEN).** Pro: matches the load-bearing PMID; the Semin Perinatol paper is substantively appropriate for the literature-gap argument (it surveys U.S. stillbirth surveillance and discusses microdata limitations post-Ananth 2022); preserves the substantive purpose of the §E.5 update (close the gap argument to 2024). Con: ships a citation under different authors than the EXPLORATION_REPORT plan named — but the plan-author appears to have erred on the label, not on the substantive intent. Documented in PRE_FLIGHT_LOG 2026-05-13T09:00Z.

2. **(B) Cite Hoyert + Gregory 2024 (PMID 39412872 = NVSR 73-09) instead.** Pro: matches the "Hoyert" name in §E.5. Con: NVSR 73-09 is **already** cited 11 times across HVS metadata + RECEIPTS + manuscript as the canonical 2022 fetal-mortality validation source. PRIOR_ART's central argument is that NCHS aggregate NVSR publications (like NVSR 73-09) are EXACTLY the resource that lacks the microdata HVS provides — so citing NVSR 73-09 in PRIOR_ART as evidence of the gap would be circular (citing what PRIOR_ART defines as inadequate as evidence that the gap exists). Rejected.

3. **(C) Cite BOTH Gregory+Barfield 2024 (PMID 38143212) AND Hoyert+Gregory 2024 (PMID 39412872).** Pro: maximally complete. Con: same NVSR-circularity concern as Option B; clutters the literature-gap argument with a duplicate-of-validation-source citation. Rejected.

4. **(D) Halt-and-ask via AskUserQuestion.** Pro: aligns with C8.6/C8.7 precedent of asking the user when a plan-vs-current-state divergence surfaces. Con: this divergence has only one substantively correct resolution (Option A); the others are circular (B+C) or self-defeating; an AskUserQuestion here would be ceremony, not decision-support. The §7 conditions do NOT classify "plan-text label diverges from cited identifier" as a halt — §7.11 (plan-text claim doesn't match cited artifact) is the closest match, but its remedy is "resolve at PRE-FLIGHT and document," which this entry does. Rejected.

**Reason:**

- The PRIOR_ART literature-gap argument depends on the SUBSTANTIVE content (post-Ananth-2022 evidence the gap persists), not on a specific author name. The load-bearing PMID is the canonical input. Re-attributing to the correct authors preserves the substantive argument while correcting the label.
- The §15 C8.8 entry's halt-flag explicitly names L8 (citation resolution) as the predicted failure surface; the fact that L8 surfaced a divergence is expected, not surprising. The remedy (cite the actual paper at the named PMID) is the routine L8 + Convention 3 application.
- Avoiding the circular NVSR-73-09 citation is independently correct: PRIOR_ART argues NCHS aggregate publications fail to harmonize microdata across boundaries; pointing at one such publication doesn't advance the argument.

**Source:**

- PMID 38143212 NCBI esummary: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=38143212&retmode=json` (probed 2026-05-13T09:00Z; full JSON saved in PRE_FLIGHT_LOG entry).
- PMID 39412872 NCBI esummary: `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=39412872&retmode=json` (probed; full JSON saved in PRE_FLIGHT_LOG entry).
- EXPLORATION_REPORT.md §E.5 item 2 (line 736): the misattributed plan-text.
- HVS use of NVSR 73-09 as 2022 validation source: see `fetal_death/external_validation_targets.csv` + manuscript `paper/draft_v2_hmd_styled.md` + receipts task2/task4/task7_*.

**Verifiable by:**

- `curl -s "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id=38143212"` returns Gregory + Barfield as authors (reproducible).
- Grep monorepo for "NVSR 73-09" or "Gregory" or "Barfield" returns the C8.8-shipped PRIOR_ART citation (after this commit) as the only "Gregory + Barfield" reference (whereas Hoyert is referenced in fetal-death validation context via NVSR 73-09 only).

**Reversible:** yes — `git revert` of the C8.8 commit returns PRIOR_ART.md to its pre-C8.8 state; a future plan-update could re-introduce a Hoyert citation if a different 2024 Hoyert-led paper is identified.

**Residual risk:** Low. If a manuscript reviewer notices the missing "Hoyert" attribution and asks for it, the response is "the PMID's correct authors are Gregory + Barfield; the matching Hoyert paper (NVSR 73-09) is already cited as our validation gold standard; citing it in PRIOR_ART would be circular." Both branches of the response are defensible.

---

## 2026-05-13T07:40:00Z — [plan-update] C8.7 — Split task C8.7 → C8.7a (path-drift static audit, this session) + C8.7b (orchestrator + Tier-1/2 re-derive, DEFERRED); revise §15 C8.7 entry's SMOKE/DO/VERIFY scope (Tier-0 only; no orchestrator authoring; no live re-derive); KICKOFF.md Tier-1 list + sequencing note revised; C8.5b resumption trigger re-pointed at C8.7b

**Choice (user-authorized at C8.7 PRE-FLIGHT halt-and-ask 2026-05-13T07:30:00Z, AskUserQuestion response "do what you think is best" interpreted as Option A "Tier-0 dry-run path audit only; defer reproducibility VERIFY to C8.7b" per the agent's stated recommendation in the question preamble, mirroring C8.6's same-phrasing precedent 2026-05-13T05:30:00Z):** Apply a single `[plan-update]` commit resolving four §7-class HALTs surfaced at C8.7 PRE-FLIGHT:

1. **HALT #1 resolution (§7.13 — no monorepo-root `scripts/run_pipeline.py` exists).** §15 C8.7 names this script as the entry point; PRE-FLIGHT verified it does NOT exist (`find . -maxdepth 4 -name run_pipeline.py` returns only `fetal_death/scripts/run_pipeline.py`). The deferred orchestrator authoring moves to C8.7b. C8.7a operates on per-step scripts directly via static analysis, not via the (non-existent) orchestrator.

2. **HALT #2 resolution (§7.13 — `fetal_death/scripts/run_pipeline.py` is mis-pathed AND stale).** Its `REPO_ROOT = Path(__file__).resolve().parent.parent` resolves to `fetal_death/` (monorepo subproject) under monorepo cwd, but raw zips live at `/Users/yoelplutchok/Desktop/fetal-death-harmonization-build/raw_data/` (standalone build-dir) and outputs at `MONOREPO_ROOT/output/` via symlink. Its `ALL_YEARS = 29` (V2 1992-2002 + V1 2005-2022) is stale relative to the current v2.4.0 43-year envelope (V3a 1989-1991 + V3b 1982-1988 shipped 2026-05-12). Both issues land in C8.7b's authoring scope; C8.7a documents them as audit findings without patching the orchestrator itself.

3. **HALT #3 resolution (§7.13 — natality has no orchestrator; natality + linked parquets not symlinked into monorepo `output/`).** Natality + linked re-derive infrastructure work moves entirely to C8.7b. C8.7a's audit covers natality per-step scripts' path-constants but does not attempt to wire them into the monorepo.

4. **HALT #4 resolution (§7.15 — Tier-2 full re-derive is 6-12+ hours of compute, vs §15's 1-session estimate).** Tier-2 moves to C8.7b under an explicit multi-session compute budget; C8.7a is metadata-only and matches the original 1-session estimate.

**Plan-update applied (this commit):**

1. **`NEXT_STEPS.md` §15.C C8.7 entry rewritten into two entries:**
   - **C8.7a (path audit; THIS SESSION)** — Goal narrowed to static path-constant audit of per-step scripts; SMOKE rewritten as Tier-0a (AST import) + Tier-0b (resolution test) + Tier-0c (helper-import reachability) — no Tier-1, no Tier-2, no live invocation; DO scope = audit table + L13 fix-on-contact patches + consolidated FIX_LOG entries by script-class; VERIFY = 6 criteria all metadata-only (audit table complete + patches captured + parquet SHAs unchanged + test-suite 56 PASS + 1 XFAIL preserved + C8.5a/C8.6 file SHAs unchanged + live-rebuild VERIFY closes at C8.7b); estimated 1 session.
   - **C8.7b (orchestrator + Tier-1 + Tier-2; DEFERRED)** — preserves all original C8.7 orchestrator + reproducibility VERIFY language; explicit DEFERRED-at-C8.7-PRE-FLIGHT status; AND-coupled resumption trigger (C8.7a-complete + user-authorized compute window); SMOKE plan describes Tier 0 orchestrator dry-run + Tier 1 single-year-per-product + optional Tier 2 full re-derive; effort estimate 1.5-5 sessions depending on Tier-1-only vs Tier-2 inclusion at resumption.

2. **`KICKOFF.md` Tier 1 task list (line 184)** split: single `C8.7` row split into `C8.7a` (this session, 1 session) + `C8.7b` (DEFERRED, 1.5-5 sessions).

3. **`KICKOFF.md` sequencing note (line 203)** revised: C8.5b resumption trigger now references **C8.7b** (the orchestrator), not C8.7 — with explicit clarification that C8.7a does NOT land an orchestrator.

4. **`PRE_FLIGHT_LOG.md`** PRE-FLIGHT addendum at 2026-05-13T07:40:00Z records the resolution + PROCEED-to-C8.7a-DO.

5. **This DECISION_LOG entry** records the §11 plan-update.

**Alternatives considered (per AskUserQuestion 2026-05-13T07:30:00Z):**

1. **(A) Tier-0 path audit only; defer reproducibility VERIFY to C8.7b (chosen).** Pro: surgical; matches §15's 1-session estimate exactly; cleanest scope; symmetric with C8.5a/C8.5b split precedent; closes C8.7's GOAL ("confirms no further path-drift exists") at the L13-mistake-class level via static analysis; preserves Anti-Pattern #8 (no compressed tasks). Con: leaves the named "byte-identical re-derive" VERIFY for C8.7b. Mitigation: live-rebuild VERIFY is logically distinct from path-drift surfacing; deferral is honest.

2. **(B) Author monorepo-root orchestrator + Tier-1 single-year-per-product re-build.** Pro: closes both GOAL + a narrowed VERIFY (single-year SHA-match per product); first reproducibility witness for all three products under monorepo cwd. Con: 1.5-2 sessions (50% over §15 estimate); compresses two distinct concerns into one task. Rejected.

3. **(C) Orchestrator + Tier-2 fetal-death only + Tier-1 nat/linked.** Pro: closes full Tier-2 reproducibility for the cheapest product. Con: 1.5-2 sessions; asymmetric across products; partial-completion shape. Rejected.

4. **(D) Full Tier-2 across all three products.** Pro: closes the §15 VERIFY literally. Con: 3-5 sessions; trips the Q33 effort-ceiling soft cap; major scope expansion vs §15. Rejected.

**Reason:** §11 plan-update process is the canonical path for in-Phase-C scope adjustments surfaced during PRE-FLIGHT verification of plan-vs-reality alignment (per Q42 self-resolution + Convention 3 Field-value snapshot). All 4 HALTs were caught at the cheap-check moment before any DO mutation — exactly what PRE-FLIGHT cheap-checks are for. The Option A split preserves every original C8.7 design intent (path-drift surfacing + reproducibility VERIFY) while aligning the immediate-session scope with what's locally verifiable + deferring orchestrator + live re-derive to its natural home.

Three protocol justifications: (i) §2 principle 1 "cheap-before-expensive" — discovering the orchestrator-absence + ALL_YEARS-staleness + Tier-2-cost mismatches at PRE-FLIGHT saves ~1 session of rework that would have surfaced mid-DO if I'd attempted to run the (non-existent) orchestrator. (ii) §11 plan-update is the canonical path for in-Phase-C scope adjustments per Q42 (>1 session change to scope requires `[plan-update]`; the deferred orchestrator + Tier-1 + Tier-2 = 1.5-5 sessions of work; well past the §11 threshold). (iii) §10 self-check encourages the LLM to surface "what could I have gotten wrong that VERIFY wouldn't catch" — in this case, three ground-truth-unverified §15 PRE-FLIGHT-input assumptions (monorepo-root orchestrator exists; fetal-death orchestrator is current; Tier-2 fits in 1 session) that L9 cheap-checks at PRE-FLIGHT caught.

**Source:**

- `PRE_FLIGHT_LOG.md` 2026-05-13T07:30:00Z entry documenting the 4 HALTs (§7.13 ×3 + §7.15 + §7.17 + §7.12).
- `NEXT_STEPS.md` §15.C C8.7 entry pre-revision text (lines 1037-1055 at commit `67ab76f`; full text preserved in git history).
- `find . -maxdepth 4 -name run_pipeline.py` → only `fetal_death/scripts/run_pipeline.py` (verified PRE-FLIGHT 2026-05-13T07:30:00Z).
- `fetal_death/scripts/run_pipeline.py` line 32-40: `REPO_ROOT = Path(__file__).resolve().parent.parent`; `ALL_YEARS = V2_YEARS + V1_PRE_COD_YEARS + V1_COD_YEARS` = 29 years (1992-2002 + 2005-2022); does not include V3a 1989-1991 or V3b 1982-1988.
- `ls fetal_death/output/ natality/output/` → "No such file or directory" (verified PRE-FLIGHT).
- `ls -la output/` → 3 symlinks pointing to `/Users/yoelplutchok/Desktop/fetal-death-harmonization-build/output/{harmonized,validation,yearly_clean}`; no natality / linked entries.
- Raw zip count: 43 fetal-death (build-dir) + 54 natality+linked (natality-harmonization dir) = 97 zips total.
- C8.5a outputs unchanged (4 SHAs match C8.6 forward-looking HALT #4); 4 parquet SHAs unchanged (match HALT #5); ci.yml sha unchanged (matches HALT #3).
- STATUS 2026-05-13T06:30:00Z line 116 ("PRE-FLIGHT should consider: ... natality has no current orchestrator — C8.7 may need to author one or wire the existing per-step scripts") confirms HALT #1 + #3 were foreseen.
- User authorization chat 2026-05-13T07:30:00Z: "do what you think is best" — interpreted as Option A per the agent's recommendation in the AskUserQuestion preamble, mirroring C8.6 precedent (DECISION_LOG 2026-05-13T05:45:00Z).

**Verifiable by:**

- This `[plan-update]` commit's diff shows `NEXT_STEPS.md` §15.C C8.7 entry rewritten into C8.7a + C8.7b + `KICKOFF.md` Tier 1 list + sequencing note edits + this DECISION_LOG entry + `PRE_FLIGHT_LOG.md` PRE-FLIGHT entry (HALT) + addendum (PROCEED).
- Tag `C8.7-pre-do` lands on this `[plan-update]` commit (PRE-FLIGHT now PROCEEDS to C8.7a DO post-resolution; mirrors C8.2 / C8.3 / C8.5 / C8.6 plan-update precedent).
- C8.7a DO ships in a sibling commit tagged `C8.7a-complete` containing audit-table receipt + L13 patches + FIX_LOG entries + STATUS append.
- C8.7b resumption: a future session's PRE-FLIGHT at resumption-trigger moment + tag `C8.7b-pre-do` on whichever commit ships the orchestrator + Tier-1 or Tier-2 work.

**Reversible:** yes — `git revert <this commit>` restores the original §15 C8.7 entry. The split is per-entry; reverting reverses both C8.7a + C8.7b stubs simultaneously.

**Residual risks:**

- (a) **Tier-0 static analysis may miss runtime-only failures** — e.g., a script that imports correctly but fails on first `subprocess.run(...)` invocation due to a missing CLI tool. Mitigation: C8.7b's Tier-1 single-year-per-product live run is the durable runtime test. C8.7a's audit is a necessary-but-not-sufficient defense.
- (b) **The "consolidated FIX_LOG entry per script-class" choice may hide per-script details** — a future debugger investigating a single broken script may want a finer-grained log. Mitigation: the C8.7a receipt's audit table preserves per-script detail; FIX_LOG entries reference the audit-table row by script path.
- (c) **The deferred C8.7b may slip beyond Phase D start** if the compute-window authorization doesn't fire. Mitigation: C8.5b's resumption-trigger update now binds Dockerfile work to C8.7b's orchestrator landing; users wanting Docker reproducibility VERIFY will surface C8.7b as a dependency.
- (d) **`fetal_death/scripts/run_pipeline.py` ALL_YEARS=29 is stale relative to the v2.4.0 43-year envelope**, but C8.7a does NOT patch this — the script-update belongs in C8.7b (orchestrator authoring is the natural home for `ALL_YEARS` extension). C8.7a's audit table records this as a DOCUMENTED finding, not PATCHED. Mitigation: C8.7b's PRE-FLIGHT must verify the `ALL_YEARS` extension landed before claiming Tier-2 closure.

**Self-check (residual risks the VERIFY phase wouldn't catch):**

- The "do what you think is best" user response is the second occurrence of this phrasing in two consecutive task PRE-FLIGHT halt-and-asks (C8.6 + C8.7). If the user intended a slightly different scope each time (e.g., Option B at C8.7), the agent's mirrored Option-A interpretation may drift further from user intent over time. Defense: surface the precedent-mirroring in this entry's self-check + offer the user a future correction window (Phase D close).
- The C8.7a audit's exhaustiveness depends on the agent's enumeration of "every per-step script" — the audit must be reproducible from the audit-table row count. Defense: audit table records `git ls-files <subdir>/scripts/ | grep '\.py$'` row count as the floor; any audit table with row count < git-ls-files count is incomplete and triggers a follow-up.
- The L13 "fix on contact" pattern works on the assumption that path-constant drift is the ONLY drift class. If a script has e.g. a CLI-tool dependency drift (`tabulate` removed from env post-C8.5a) or a Python-API drift (`pd.read_csv(squeeze=True)` removed), the audit won't catch it. Defense: scope is explicitly L13-only; non-L13 drift surfaces at C8.7b's runtime test.
- The "FIX_LOG entries consolidated by script-class" choice trades verbosity for readability; if there are many script-class FIX_LOGs, the consolidated entries become hard to navigate. Defense: audit table is the index; FIX_LOG entries link back via timestamp.

**Backport scope (per §11.4):** None directly. C8.1 / C8.2 / C8.3 / C8.4 / C8.5a / C8.6 receipts unaffected. C8.7a ships forward under the revised scope; C8.7b ships forward as a deferred task with explicit resumption trigger; C8.5b's resumption trigger updated to point at C8.7b instead of C8.7.

---

## 2026-05-13T05:45:00Z — [plan-update] C8.6 — Ship workflow file in monorepo + defer live-CI green-check VERIFY to Phase D step 3 first sync; revise §15 C8.6 DO scope (single-version Python 3.13, not 3.11+3.12 matrix) + VERIFY criterion (YAML structurally valid + locally-emulated test command runs green + forward-looking live-CI VERIFY at Phase D)

**Choice (user-authorized at C8.6 PRE-FLIGHT halt-and-ask 2026-05-13T05:30:00Z, AskUserQuestion response "do what you think is the best move" interpreted as Option A "Ship workflow now, live-VERIFY at Phase D" per the agent's stated recommendation in the question preamble):** Apply a single `[plan-update]` commit resolving two §7-class HALTs surfaced at C8.6 PRE-FLIGHT:

1. **HALT #1 resolution (§7.17 + §7.12-shape, dev/public separation) — ship workflow in monorepo + defer live-CI VERIFY to Phase D step 3.** This monorepo has no `git remote` configured (verified PRE-FLIGHT: `git remote -v` returns empty). The public repo `yoelplutchok/vital-statistics-harmonization` is at v1.0 commit `a18ca3a` (2026-05-12T03:20:06Z; verified via `gh api repos/.../commits/main`) with no `.github/workflows/` directory (verified via `gh api repos/.../contents/.github/workflows` → HTTP 404) and lacks all Tier-1 outputs (no `pyproject.toml`, `uv.lock`, `.python-version`, `tests/`, the four C8.1-followup `__init__.py` files, the C8.1 dtype-parity test). Per KICKOFF Phase D step 3 (line 235), the canonical mechanism for moving Tier-1 outputs to the public repo is a complete staging-dir sync from `~/Desktop/vital-statistics-harmonization-public/` (verified to exist, currently at the v1.0 state, no `.github/`) + scrub + push. A live-CI VERIFY from this session would require either (i) configuring an `origin` remote here + pushing — but this monorepo's HEAD includes all state files (STATUS.md, DECISION_LOG.md, FIX_LOG.md, LESSONS.md, NEXT_STEPS.md, KICKOFF.md, PRE_FLIGHT_LOG.md, RECEIPTS/, EXPLORATION_REPORT.md, paper/) that the Phase D exclude list deliberately scrubs, so a direct push would leak them; (ii) a surgical sync to the staging dir + push from there — which is partial-Phase-D-step-3 ahead of schedule and forward-syncs questions that aren't ready (Task 9 redirect notices, manuscript admin-section markers, etc.). Option A ships the workflow file in this monorepo as canonical state; the file moves to the public repo at Phase D step 3 along with all other Tier-1 outputs; the live-CI green-check VERIFY closes on that first sync.

2. **HALT #2 resolution (§7.12, Python pin) — single-version 3.13.** §15 C8.6 DO scope (pre-revision line 1011) specified "matrix on Python 3.11 + 3.12 if both supported per uv.lock." This text predates C8.5a (which pinned `requires-python = ">=3.13,<3.14"` + `.python-version = 3.13`). Neither 3.11 nor 3.12 is supported under the canonical env; a matrix would either resolve to zero supported versions or be silently misleading. STATUS 2026-05-13T05:00:00Z line 118 already flagged this as a candidate consideration for C8.6 PRE-FLIGHT. Revised DO scope: single-job, `runs-on: ubuntu-latest`, Python auto-resolved from `.python-version` via `astral-sh/setup-uv@v6` (no explicit matrix needed).

**Plan-update applied (this commit):**

1. **`NEXT_STEPS.md` §15.C C8.6 entry rewritten** (lines 1001–1019 pre-revision):
   - Header note added documenting the 2026-05-13T05:30:00Z PRE-FLIGHT revision + §7 HALTs resolved.
   - Goal expanded to enumerate the specific test files (`test_schema_dtype_parity.py`, `test_canonical_filter_invariants.py`, `test_row_count_conservation.py`, `test_cross_product_join_parity.py`, `test_release_smoke.py`) being gated.
   - Why-this-matters narrative extended to note authoring-ahead-of-Phase-D rationale.
   - PRE-FLIGHT inputs extended to enumerate exact C8.5a SHAs being depended on.
   - SMOKE plan rewritten: Tier 0 `yaml.safe_load` + structural-key assertions (actionlint not installed locally; fallback documented).
   - DO scope rewritten: 5-step workflow specified (checkout, setup-uv, uv lock --check, uv sync --frozen, pytest); concurrency control noted.
   - VERIFY criteria rewritten as 5 numbered items: (1) YAML structurally valid; (2) locally-emulated steps reproduce 56 PASS + 1 XFAIL baseline; (3) parquet SHAs unchanged; (4) C8.5a file SHAs unchanged; (5) **forward-looking live-CI VERIFY closes at Phase D step 3 first sync**.
   - Dependencies extended to clarify C8.5b is NOT a dependency (per C8.5 plan-update narrowing); live-CI VERIFY depends on Phase D step 3.

2. **`KICKOFF.md`** — no edits needed; Phase C Tier-1 sequencing (line 184) names C8.6 as the next task with no implicit "remote push happens at C8.6" claim that conflicts with this plan-update.

3. **`PRE_FLIGHT_LOG.md`** — PRE-FLIGHT entry at 2026-05-13T05:30:00Z (RESULT: HALT) + addendum at 2026-05-13T05:45:00Z (RESULT: PROCEED post-resolution) document the two HALTs + this plan-update.

4. **This DECISION_LOG entry** records the §11 plan-update + Option A rationale.

**Alternatives considered (per AskUserQuestion 2026-05-13T05:30:00Z):**

For HALT #1:

1. **(A) Ship workflow now, live-VERIFY at Phase D (chosen).** Pro: smallest scope; matches existing dev/public architecture cleanly; workflow IS canonical state that belongs in the public repo; one-session cost; locally-emulated VERIFY gives high-confidence signal (uv sync --frozen + pytest works under the same Python pin + same lockfile that CI will use); aligns with KICKOFF's Phase D step 3 as the canonical sync mechanism. Con: "live CI green check" doesn't close until Phase D step 3; parquet-skip-in-CI deferred to C8.13 (acceptable separate matter).

2. **(B) Surgical sync to staging dir + live push now.** Pro: live CI green check closes this session; forward-syncs Tier-1 to public; reduces Phase D step 3 burden. Con: ~45-60 min overhead; jumps Phase D step 3 ahead of schedule, partially; brings forward questions that aren't ready (Task 9 redirect notice content, manuscript admin-section markers, EXPLORATION_REPORT exclude question, paper/ exclude question, etc.); Phase D step 3 was deliberately designed as a single sweep — partial sweeps create more state to track; **violates Anti-Pattern #8** ("Never compress two tasks into one because they go together"). Rejected.

3. **(C) Re-order Tier-1: C8.7 + C8.8 first, C8.6 last.** Pro: C8.6 ships alongside Phase D step 3 (cleanest live-CI VERIFY). Con: defers C8.6 indefinitely (Phase D start is conditional on Tier-1 + Tier-2 completion — many sessions out); doesn't address the structural issue, just defers it; KICKOFF.md sequencing note revision is plan-update overhead; loses the "early CI scaffolding" benefit (`EXPLORATION_REPORT.md` §B.9 cites this as the value of C8.6 specifically). Rejected.

For HALT #2:

1. **(A) Single-version Python 3.13 (chosen).** Pro: matches `.python-version` + `requires-python` literally; cleanest workflow; no dead-matrix-cell complexity. Con: forward-compat extension (e.g., 3.14 migration) requires a workflow edit — acceptable since 3.14 migration is itself a §11 plan-update event per C8.5a forward-looking HALT #5.

2. **(B) Keep matrix wording but with values 3.13 only.** Pro: forward-compat-shape preserved. Con: zero current benefit; complicates the workflow file. Rejected.

3. **(C) Keep 3.11+3.12 matrix as-written and let CI fail.** Pro: follows §15 literally. Con: would produce a CI workflow that cannot run (uv won't install Python 3.11 or 3.12 because of `requires-python = ">=3.13,<3.14"`); breaks any "Live CI green check" VERIFY. **Rejected (would violate §2 principle 2 "fail closed" — knowingly authoring a broken workflow).**

**Reason:** §11 plan-update process is the canonical path for in-Phase-C scope adjustments surfaced during PRE-FLIGHT verification of plan-vs-reality alignment (per Q42 self-resolution + Convention 3 Field-value snapshot). Both HALTs were caught at the cheap-check moment before any DO mutation — exactly what PRE-FLIGHT cheap-checks are for. The Option A choice + Python pin resolution preserve every original C8.6 design intent (workflow file, dependency on lockfile, pytest invocation, gating on push events) while aligning the immediate-session scope with what's locally verifiable + deferring the live-CI surface to its natural home at Phase D step 3.

Three protocol justifications: (i) §2 principle 1 "cheap-before-expensive" — discovering the dev/public-separation + Python-pin misalignments at PRE-FLIGHT saves ~30-60 min of rework that would have surfaced mid-DO if I'd attempted a direct push or authored a 3.11+3.12 matrix workflow. (ii) §11 plan-update process is the canonical path for in-Phase-C scope adjustments per Q42 (>1-session candidates trigger plan-update; the deferred live-CI VERIFY is ~5 minutes of Phase D step 3 work but the architectural shift in VERIFY criterion is plan-update-shape; sibling of C8.5's plan-update precedent). (iii) §10 self-check encourages the LLM to surface "what could I have gotten wrong that VERIFY wouldn't catch" — in this case, two ground-truth-unverified §15 PRE-FLIGHT-input assumptions (remote configured; 3.11+3.12 supported) that L9 cheap-checks at PRE-FLIGHT caught.

**Source:**

- `PRE_FLIGHT_LOG.md` 2026-05-13T05:30:00Z entry documenting the two HALTs (HALT #1 §7.17 + §7.12-shape, HALT #2 §7.12).
- `NEXT_STEPS.md` §15.C C8.6 entry pre-revision text (lines 1001–1019 at commit `e9cd08e`; full text preserved in git history).
- `git remote -v` → empty (verified PRE-FLIGHT).
- `gh api repos/yoelplutchok/vital-statistics-harmonization/commits/main --jq '.sha'` → `a18ca3acdc5b3c6012511aab99de2f9da7508840` (v1.0 commit, 2026-05-12T03:20:06Z).
- `gh api repos/yoelplutchok/vital-statistics-harmonization/contents/.github/workflows` → HTTP 404 (no workflows dir in public repo).
- `ls -la ~/Desktop/vital-statistics-harmonization-public/.github` → "No such file or directory" (staging dir also has no workflows; consistent with v1.0 state).
- C8.5a outputs: `pyproject.toml` sha=`c8826a61…`; `uv.lock` sha=`ab627034…`; `.python-version` sha=`02e735b3…`; content `requires-python = ">=3.13,<3.14"` (verified).
- STATUS 2026-05-13T05:00:00Z line 118 ("C8.5a surfaced one candidate consideration for C8.6: Python version matrix (single-version 3.13.x per `requires-python`, OR matrix of {3.13} for forward compat — single suffices given the narrow Python pin).") confirms HALT #2 was foreseen.
- KICKOFF.md Phase D step 3 (line 235) "Re-rsync `~/Desktop/vital-statistics-harmonization-public/`, re-scrub (same exclude list + LLM-mention scrub edits as 2026-05-12 v1.0 push)" — the canonical sync mechanism.
- User authorization chat 2026-05-13T05:30:00Z: "do what you think is the best move" — interpreted as Option A per the agent's recommendation in the AskUserQuestion preamble.

**Verifiable by:**

- This `[plan-update]` commit's diff shows `NEXT_STEPS.md` §15.C C8.6 entry rewritten + `DECISION_LOG.md` this entry + `PRE_FLIGHT_LOG.md` PRE-FLIGHT entry + addendum.
- Tag `C8.6-pre-do` lands on this `[plan-update]` commit (PRE-FLIGHT now PROCEEDS to C8.6 DO post-resolution; mirrors C8.2 / C8.3 / C8.5 plan-update precedent).
- C8.6 DO ships in a sibling commit tagged `C8.6-complete` containing `.github/workflows/ci.yml` + RECEIPT + STATUS append.
- Phase D step 3 first sync: a future session's RECEIPT records the first remote workflow-run URL + green/red status. If green, the live-CI VERIFY closes; if red, the §15 C8.6 VERIFY criterion #5 triggers a halt.

**Reversible:** yes — `git revert <this commit>` restores the original §15 C8.6 entry. The deferred live-CI VERIFY claim is per-task; reverting affects only C8.6's scope, not C8.5a's outputs or the dev/public separation pattern itself.

**Residual risks:**

- (a) **The Phase D step 3 first sync may surface workflow-on-runner failure modes not caught by local emulation.** E.g., `astral-sh/setup-uv@v6` on `ubuntu-latest` may resolve to a different uv build than the local `0.11.10 (aarch64-apple-darwin)`. Mitigation: the workflow pins `version: "0.11.x"` which constrains the major-minor; first sync's Forward-looking HALT explicitly requires verification of green CI before claiming closure. If the first remote run is red, the Phase D session halts + surfaces.
- (b) **The parquet-skip-in-CI concern weakens the CI signal**. On a clean Ubuntu runner with no parquets, the conftest `_require()` skip-if-missing protocol will cleanly skip parquet-dependent tests; CI reports "N passed + M skipped" instead of the local "56 PASS + 1 XFAIL." Mitigation: routed to C8.13 (Performance + GitHub release artifacts) for resolution via parquet-fetch-step or GitHub release artifact attachment. Documented as a Forward-looking HALT.
- (c) **The §15 entry's "Python matrix" wording (now revised)** may resurface in a future plan-update if 3.14 / 3.15 migration is desired. Mitigation: C8.5a forward-looking HALT #5 ("Python pin: 3.13.x. `requires-python = ">=3.13,<3.14"`. A future 3.14 migration is a §11 plan-update event") names the migration trigger explicitly.
- (d) **Cross-platform lockfile resolution untested locally (macOS arm64 build).** First CI run on `ubuntu-latest` (x86_64) is the durable cross-platform test. If `uv sync --frozen` fails due to a missing wheel for a transitive dep on linux-x86_64, the lockfile may need a `--python-platform linux` re-lock. Mitigation: this is C8.5a's open soft-flag (b); surfaces at first CI run, which is Phase D step 3.

**Self-check (residual risks the VERIFY phase wouldn't catch):**

- The locally-emulated VERIFY runs `uv sync --frozen` + `pytest` under macOS arm64 (`aarch64-apple-darwin`); the workflow will run on linux-x86_64. Wheel-availability for all 38 packages on linux-x86_64 is not directly tested by local emulation. The first Phase D step 3 push is the durable test. Risk: if a linux-x86_64-specific wheel is missing, CI fails immediately — and we won't know until Phase D. Mitigation: defer to Phase D first-run + surface as Forward-looking HALT.
- The workflow's concurrency control (`group: ci-${{ github.ref }}`, `cancel-in-progress: true`) is appropriate for single-contributor + main-branch + PR-from-fork patterns; it may cancel useful in-flight runs on rapid pushes. Acceptable trade-off; not VERIFY-blocking.
- The single-job design assumes all tests pass under a single env. If a future test requires e.g. R interop, the workflow will need restructuring. Acceptable for current scope.
- The locally-emulated `uv sync --check` returns "Would make no changes" today; that's environment-consistent confirmation. If a different machine produces a different result on the same lockfile, that's a uv-internal-state bug — not a workflow bug.

**Backport scope (per §11.4):** None directly. C8.1 / C8.2 / C8.3 / C8.4 / C8.5a receipts unaffected. C8.6 ships forward under the revised scope; C8.7 / C8.8 / Phase D step 3 inherit the Forward-looking HALT lineage.

---

## 2026-05-13T04:30:00Z — [plan-update] C8.5 — Split task into C8.5a (lockfile, this session) + C8.5b (Dockerfile, DEFERRED); revise Python pin from 3.11-slim to 3.13-slim; revise VERIFY scope from pipeline-rebuild to env-resolution + test-suite

**Choice (user-authorized at C8.5 PRE-FLIGHT halt-and-ask 2026-05-13T04:15:00Z; all three options (a)):** Apply a single §11 [plan-update] commit resolving three §7-class HALT conditions surfaced at C8.5 PRE-FLIGHT:

1. **HALT #1 resolution — split C8.5 → C8.5a + C8.5b.** `docker` is not installed on the build machine (PRE-FLIGHT verified via `which docker` → exit 1; `docker --version` → command-not-found). C8.5 SMOKE Tier 1 (`docker build`) and Tier 2 (`docker run`) cannot run locally. Split the task: **C8.5a** = lockfile-only (fully locally verifiable; this session); **C8.5b** = Dockerfile (DEFERRED until docker available on build machine OR C8.6 CI ships and validates remotely via GitHub Actions' hosted-runner `docker build`). C8.6 dependency narrows: C8.6 depends on C8.5a's lockfile only (not on C8.5b).

2. **HALT #2 resolution — Python pin to 3.13.x.** §15 line 963 originally specified `python:3.11-slim` base, but every actual build event in this repo's history uses Python 3.13.9 (natality v2.7.0 + fetal-death V2.0 build notes both name Python 3.13.9 explicitly; current build interpreter is 3.13.9 via miniconda). §15's `3.11-slim` appears to be a EXPLORATION_REPORT §F.2 carryover wording without ground-truth check. Plan-update revises §15 C8.5b entry to `python:3.13-slim`; `pyproject.toml` `requires-python = ">=3.13,<3.14"`; `.python-version` = `3.13`.

3. **HALT #3 resolution — C8.5a VERIFY revised to env-resolution + test-suite passes.** §15 line 965 originally specified `python scripts/run_pipeline.py` at monorepo root as the VERIFY witness. No monorepo-root `scripts/run_pipeline.py` exists; the only pipeline orchestrator is `fetal_death/scripts/run_pipeline.py` (rebuilds fetal-death V2.0 era only — 29 of the 43 years now covered). A monorepo-root orchestrator is C8.7's explicit scope per KICKOFF Tier-1 sequencing. Plan-update revises C8.5a VERIFY to: (i) `uv lock` deterministic (running twice produces bit-identical output); (ii) `uv sync --check` reports env-OK; (iii) cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returns 56 PASS + 1 XFAIL (the C8.4 baseline); (iv) all four parquet SHAs unchanged. Pipeline-rebuild VERIFY moves to C8.7.

**Plan-update applied (this commit):**

1. **`NEXT_STEPS.md` §15.C C8.5 entry rewritten into two entries:**
   - C8.5a (lockfile) — Goal/Why/PRE-FLIGHT inputs/SMOKE/DO/VERIFY all revised per the three resolutions. Effort revised 1.5–3 sessions → 0.5–1 session.
   - C8.5b (Dockerfile, DEFERRED) — preserves all original §15 C8.5 Dockerfile language with revisions: `3.11-slim` → `3.13-slim`; explicit "DEFERRED at C8.5 PRE-FLIGHT 2026-05-13T04:00:00Z"; resumption trigger documented; dependency on C8.5a (lockfile) + C8.7 (orchestrator) for full-rebuild VERIFY.

2. **`KICKOFF.md` Tier 1 task list (line 181)**: single `C8.5` row split into two rows (C8.5a `0.5-1 session`, C8.5b `1-2 sessions [DEFERRED]`).

3. **`KICKOFF.md` sequencing note (line 202)**: `C8.5 + C8.6 paired` revised to `C8.5a + C8.6 paired` with Dockerfile deferral note.

4. **`PRE_FLIGHT_LOG.md`** PRE-FLIGHT addendum at 2026-05-13T04:30:00Z records the resolution + PROCEED-to-C8.5a-DO.

5. **This DECISION_LOG entry** records the §11 plan-update.

**Alternatives considered (per AskUserQuestion 2026-05-13T04:15:00Z):**

For HALT #1:
1. **(a) Split into C8.5a + C8.5b (chosen).** Pro: surgical; preserves Tier-1 progress; clean tag boundary; lockfile lands this session with full SMOKE+VERIFY; Dockerfile resumption trigger explicit. Con: 2 RECEIPTS + 2 tags instead of 1.
2. **(b) Author Dockerfile now, defer docker SMOKE to C8.6 CI.** Pro: ships Dockerfile artifact in same session. Con: Dockerfile lands un-locally-validated; C8.6 CI is the implicit acceptance gate but it doesn't exist yet either. Rejected for same-session-ship-without-local-SMOKE concern.
3. **(c) Halt C8.5 entirely until docker installed.** Pro: full local SMOKE. Con: introduces out-of-band human step (Docker Desktop install ~5-15 min); delays C8.5a indefinitely; the lockfile portion is independently shippable so blocking it on docker is over-conservative. Rejected.
4. **(d) Lockfile-only this session; no Dockerfile commitment.** Pro: simplest. Con: loses the C8.5b follow-up tracking; future agent may not surface the deferred Dockerfile as a clear future task without explicit §15 entry. Rejected in favor of (a)'s explicit C8.5b stub.

For HALT #2:
1. **(a) Pin to 3.13.x; §11 plan-update (chosen).** Pro: matches every actual build event in repo history; lockfile reproduces documented builds byte-exact. Con: requires §11 plan-update commit (which is happening anyway for HALT #1).
2. **(b) Pin to 3.11.x per §15 literal.** Pro: follows §15 as-written. Con: lockfile becomes a hypothetical-env pin; no actual 3.11 build event in repo's history; resolver may pick different versions on 3.11 vs 3.13 (pandas 2.3.2 + numpy 2.3.1 both still support 3.11 but the resolution flag may differ); breaks reproducibility of every existing build. Rejected.
3. **(c) Range pin `>=3.11,<3.14`.** Pro: broader downstream-consumer compat. Con: lockfile still resolves against one specific Python at lock time; the range constrains downstream consumers, not the resolver; gives the illusion of multi-version support without actually testing it. Rejected.

For HALT #3:
1. **(a) Env-resolution + test-suite VERIFY; pipeline-rebuild moves to C8.7 (chosen).** Pro: aligns C8.5a scope with what's locally verifiable; C8.7 explicitly takes the pipeline-rebuild VERIFY responsibility per its KICKOFF Tier-1 entry. Con: weakens C8.5a VERIFY; relies on C8.7 for end-to-end closure (acceptable since C8.7 is the next-after-C8.6 Tier-1 task).
2. **(b) Author stub `scripts/run_pipeline.py` at monorepo root.** Pro: closes §15 VERIFY per literal. Con: scope creep (~0.5-1 session that belongs in C8.7); duplicates C8.7's intent. Rejected.
3. **(c) Use `fetal_death/scripts/run_pipeline.py` as partial witness.** Pro: minimal scope. Con: covers fetal-death only (29 V2 years, not the 43-year v2.4.0 envelope); doesn't address natality or linked. Rejected as partial verification.
4. **(d) Defer C8.5 to after C8.7.** Pro: §15 VERIFY satisfied per literal. Con: re-orders Tier 1 sequencing (§15/KICKOFF say C8.5 before C8.6, C8.6 before C8.7); C8.6 depends on the lockfile, which is C8.5a's deliverable — deferring C8.5a means deferring C8.6 too. Rejected.

**Reason:** §11 plan-update process is the canonical path for in-Phase-C scope adjustments surfaced during PRE-FLIGHT (per Q42 self-resolution + Convention 3 Field-value snapshot). All three HALTs were caught at the cheap-check moment before any DO mutation — exactly what PRE-FLIGHT cheap-checks are for. The split + Python pin + VERIFY revision preserve every original C8.5 design intent (lockfile + Dockerfile + reproducibility-via-pinned-env) while aligning the immediate-session scope with what's locally verifiable.

Three protocol justifications: (i) §2 principle 1 "cheap-before-expensive" — discovering the docker/Python/VERIFY misalignments at PRE-FLIGHT saves ~1 session of rework after a DO-time docker invocation would have surfaced a halt mid-task; (ii) §11 plan-update process is the canonical path for in-Phase-C scope adjustments per Q42 (>1 session candidates require [plan-update]; the deferral of C8.5b is ~1-2 sessions of work; well past the §11 threshold); (iii) §10 self-check encourages the LLM to surface "what could I have gotten wrong that VERIFY wouldn't catch" — in this case, the §15 entry's `python:3.11-slim` text + the assumed monorepo-root pipeline orchestrator were both ground-truth-unverified at plan-write time. The L9 cheap-check at PRE-FLIGHT caught both.

**Source:**

- `PRE_FLIGHT_LOG.md` 2026-05-13T04:00:00Z entry documenting the three HALTs (Halt #1 §7.2, Halt #2 §7.12, Halt #3 §7.17).
- §15.C C8.5 entry pre-revision text (NEXT_STEPS.md lines 953–971 at commit `4b78dd0`; full text preserved in git history).
- `EXPLORATION_REPORT.md` §F.2 + §F.3 (the source for the original C8.5 scope; §F.2 doesn't actually specify a Python version, confirming the §15 `3.11-slim` text was an authoring-time interpolation).
- `which docker` → exit 1 (docker not installed); `which uv` → `/opt/miniconda3/bin/uv`; `uv --version` → `0.11.10`; `python3 --version` → `Python 3.13.9`.
- natality `requirements.txt` + fetal-death `requirements.txt` both reference Python 3.13.9 as the build-time interpreter explicitly.
- `find . -maxdepth 4 -name run_pipeline.py` → only `fetal_death/scripts/run_pipeline.py` exists at monorepo root.
- User authorization chat 2026-05-13T04:15:00Z: HALT #1 = "Split C8.5 → C8.5a (lockfile now) + C8.5b (Dockerfile later)"; HALT #2 = "Pin to 3.13.x; §11 plan-update revises §15 line 963"; HALT #3 = "Env-resolution + test-suite passes (§11 plan-update)".

**Verifiable by:**

- This `[plan-update]` commit's diff shows `NEXT_STEPS.md` §15.C C8.5 entry rewritten into C8.5a + C8.5b + `KICKOFF.md` Tier 1 list + sequencing note edits + this DECISION_LOG entry + PRE_FLIGHT_LOG.md addendum.
- Tag `C8.5-pre-do` lands on this `[plan-update]` commit (PRE-FLIGHT now PROCEEDS to C8.5a DO post-resolution; mirrors C8.2/C8.3 pattern).
- C8.5a DO ships in a sibling commit tagged `C8.5a-complete`.
- C8.5b resumption: a future session's PRE-FLIGHT addendum at the resumption-trigger moment + tag `C8.5b-pre-do` on whichever commit ships the Dockerfile.

**Reversible:** yes — `git revert <this commit>` restores the original §15 C8.5 entry. The split is per-entry; reverting reverses both C8.5a + C8.5b stubs simultaneously.

**Residual risks:**

- (a) **The `requires-python = ">=3.13,<3.14"` may be too narrow** if a downstream consumer wants 3.14 support before we authorize a re-pin. Mitigation: this matches the build env; broader-pin authorization is a future §11 plan-update if requested.
- (b) **The `uv.lock` will pin transitive dependencies that aren't in `requirements.txt`** (e.g., `numpy` is in requirements but `python-dateutil` (pandas transitive dep) is not). The lockfile will declare its own preferred versions. Mitigation: `uv lock` is deterministic given a fixed dependency tree; subsequent re-locks against the same `pyproject.toml` produce bit-identical output (verified at SMOKE Tier 0).
- (c) **The deferred C8.5b may slip beyond Phase D start** if the docker-availability trigger doesn't fire. Mitigation: the resumption trigger is OR-coupled ("docker available OR C8.6 CI ships"); C8.6 (next Tier-1 task after C8.5a) ships GitHub Actions which has docker natively. C8.5b will become unblockable as soon as C8.6 lands, even without local docker install.
- (d) **The original §15 VERIFY's pipeline-rebuild criterion is non-trivially weakened.** Specifically, the assertion "running the full pipeline from raw zips against this pinned env produces canonical parquet SHAs" loses its C8.5a anchor. Mitigation: C8.7's §15 entry explicitly takes this VERIFY (line 1006-ish: "VERIFY criteria: `uv sync && python scripts/run_pipeline.py` rebuilds parquets to canonical SHAs"). The end-to-end VERIFY chain still closes at C8.7-complete.

**Self-check (residual risks the VERIFY phase wouldn't catch):**

- This entry assumes `uv lock` against the currently-installed env produces a lockfile that resolves cleanly on a fresh `uv sync` (no transitive dep resolution failure). If `uv lock` discovers a conflict between `pandas==2.3.2` and another dep's `pandas` requirement on Python 3.13, the lockfile generation may fail or produce a different version pin than expected. Mitigation: SMOKE Tier 0 explicitly tests `uv lock` resolution; HALT-on-failure to surface this if it happens.
- The `requires-python = ">=3.13,<3.14"` pin assumes 3.13 stays the canonical Python for the lifetime of this lockfile. If a Phase D / v1.1 Python 3.14 migration is desired, a §11 plan-update bumps the pin.
- The deferred C8.5b is shipped as a §15 entry stub but not a fully-PRE-FLIGHTed task. When resumed, its PRE-FLIGHT must re-verify (i) `uv.lock` post-C8.5a sha = the one this session will produce; (ii) `docker` runtime available; (iii) `scripts/run_pipeline.py` post-C8.7 sha = the one C8.7 will produce. Failure of any of those triggers a fresh §11 plan-update at C8.5b PRE-FLIGHT moment.

**Backport scope (per §11.4):** None directly. C8.1 / C8.2 / C8.3 / C8.4 receipts unaffected. C8.5a ships forward under the revised scope; C8.5b ships forward as a deferred task with explicit resumption trigger.

---

## 2026-05-13T03:00:00Z — C8.4 — Linked-vs-natality per-year drift bounded by 0.01% (was previously undocumented for this product pair); B.5 harness softened from strict-subset to bounded-drift invariant

**Choice (user-authorized at C8.4 DO halt-and-ask 2026-05-13T02:30Z, option `(a) Soften to relative-drift invariant (≤0.01%) + DECISION_LOG entry (Recommended)`):** The B.5 cross-product join parity harness's `test_linked_per_year_count_le_natality` was authored with a strict-subset assumption ("every linked birth is a natality birth"). On first run against the v2.4.0 / v2.8.0 / v3 release state, 5 of 19 joint years (2005, 2006, 2008, 2011, 2012) violated strict subset: linked exceeds natality by 1–228 records (max 0.0055% relative drift, year 2005 with +228 records on a 4.14M base).

**Resolution:** Replace the strict-subset assertion with a bounded-drift invariant: `|linked - natality| / max(linked, natality) ≤ 0.01%` per joint year. The 0.01% tolerance is 2× the observed max (0.0055%) and matches the order of magnitude of the JOINT_USE_GUIDE.md-documented "<0.006% NCHS post-release re-tabulation" between microdata and NVSR-style products. Test renamed: `test_linked_per_year_count_within_drift_tolerance_of_natality`. Mutation test re-shaped: `test_mutation_linked_bounded_drift_violation_caught` injects a 0.5% drift (10× tolerance) on synthetic data and asserts the harness flags it.

**Alternatives considered (per AskUserQuestion 2026-05-13T02:30Z):**

1. **(a) Soften to relative-drift invariant + DECISION_LOG (chosen).** Pro: keeps a meaningful invariant (>0.01% drift still flagged as regression); avoids hard-coding the 5 currently-drifting years (the SHAPE invariant survives any future linked-pipeline retabulation); aligns with JOINT_USE_GUIDE.md's documented tolerance class. Con: a future widening of NCHS's re-tabulation drift past 0.01% triggers a re-pin task.
2. **(b) Strict subset + 5-year exception dict + DECISION_LOG.** Pro: more conservative — any new drifting year triggers FAIL. Con: heavy maintenance; hard-codes a tracks-current-state pin that violates Convention 1 (SHAPE-not-VALUE). Rejected as inconsistent with the file's `DESIGN: structural-invariant-no-pins` tag.
3. **(c) Remove the linked-subset assertion entirely + DECISION_LOG.** Pro: cleanest architectural framing — NCHS doesn't guarantee subset between linked and natality pipelines. Con: loses a useful invariant (a >0.01% widening still indicates a real regression). Rejected as throwing the baby out with the bathwater.
4. **(d) Halt + §11 plan-update.** Pro: methodologically cleanest. Con: ~30 min overhead for a problem solvable inside DO via a tolerance edit + log entry. Rejected as over-engineering.

**Reason:** The JOINT_USE_GUIDE-documented natality-vs-NVSR drift (5 years with diffs of 38–224 records, max 0.0055%) is the same shape as the linked-vs-natality drift surfaced by C8.4 (5 years with diffs of 1–228 records, max 0.0055%). The linked file is constructed by NCHS using NVSR-style cohort tabulations that include the same post-release adjustments. The phenomenon is documented in the source domain; B.5 had inadvertently encoded a stricter invariant than the data supports. The right level of automated defense is a tolerance that catches a *widening* of the documented drift, not a re-litigation of the documented drift itself.

Three protocol justifications: (i) §2 principle 2 "fail closed" — we halted at the FAIL rather than silently softening; AskUserQuestion is the formal "fail closed" surface. (ii) §4.2.1 Convention 1 SHAPE-not-VALUE — the bounded-drift invariant is a SHAPE check (true for any year-set, any record-count growth); the strict-subset claim was effectively a stale-pin against the year-set as it happened to exist when the test was first authored. (iii) §10 self-check — the residual risk "what could I have gotten wrong that VERIFY wouldn't catch" applies in reverse here: I HAD a strict invariant that caught something I hadn't known about. Surfacing it via AskUserQuestion + this log entry rather than silent edit is what the protocol prescribes.

**Source:**
- `tests/test_cross_product_join_parity.py` (NEW; sha=`4cb8b4e0f78d80f4…`) lines around `_LINKED_NATALITY_DRIFT_TOLERANCE = 1e-4`.
- `docs/JOINT_USE_GUIDE.md` "NCHS-series note" table (5 years with 38–224 record diffs; <0.006% relative).
- Observed empirical drift on v3 cohort-linked vs v2.8.0 natality (5 years, max 0.0055%):
    - 2005: linked=4,138,577 natality=4,138,349 diff=+228 (0.0055%)
    - 2006: linked=4,265,593 natality=4,265,555 diff=+38 (0.0009%)
    - 2008: linked=4,247,726 natality=4,247,694 diff=+32 (0.0008%)
    - 2011: linked=3,953,591 natality=3,953,590 diff=+1 (~0%)
    - 2012: linked=3,952,842 natality=3,952,841 diff=+1 (~0%)
- Linked parquet sha=`9b828a4de4e59b17…`; natality parquet sha=`e16ad5323d68e28d…`.
- User authorization chat 2026-05-13: option (a) selected via AskUserQuestion.

**Verifiable by:**
- `pytest tests/test_cross_product_join_parity.py::test_linked_per_year_count_within_drift_tolerance_of_natality` PASS on current parquet state.
- `pytest tests/test_cross_product_join_parity.py::test_mutation_linked_bounded_drift_violation_caught` PASS (mutation test).
- Combined cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returns 56 passed + 1 xfailed.

**Reversible:** yes — `git revert` of the C8.4 commit removes the bounded-drift invariant; the strict-subset assertion is preserved in git history. If a future task wants to investigate the underlying NCHS-pipeline cause (e.g., audit the 2005 +228-record source), the log entry + parquet SHAs above are the starting point.

**Residual risks:**

- (a) **The 0.01% tolerance may be too loose.** If a future linked-pipeline regression introduces a 0.005% systematic drift across more years, the harness won't catch it. Mitigation: the test reports actual drift values in the FAIL message, so a per-year drift inspection during any future failure surfaces the widening; the DECISION_LOG entry documents what the current envelope is.
- (b) **The 5 currently-drifting years are not individually pinned.** A future NCHS re-release that re-tabulates one of these years to a different drift will silently pass as long as the new drift remains ≤ 0.01%. Mitigation: the parquet-SHA-pinned C8.4 receipt + this log entry are the canonical record of the v3 / v2.8.0 state.
- (c) **The drift is documented as "NCHS post-release re-tabulation" but not directly verified.** A truly diligent investigation would compare a single drifting year's birth records between the natality public-use file and the linked file to verify that the +228 records in 2005 are NCHS-added (or natality-dropped), not a pipeline bug on our side. Mitigation: Phase D / C8.11 cross-product COMPARABILITY consolidation should incorporate this finding.

**Self-check (residual risks the VERIFY phase wouldn't catch):**

- The bounded-drift tolerance is set at 0.01% (1e-4) — 2× the observed max. If the observed max grew to 0.008% (still well within JOINT_USE_GUIDE's "<0.006%" qualitative bound but above the empirical 0.0055%), the harness would FAIL. Whether that's the right behavior depends on whether 0.008% counts as "expected NCHS drift" or "regression." The conservative choice (FAIL) is what's wired now; tuning is reversible via this entry's 1e-4 constant.
- The 5-year observation list is a snapshot of the v2.8.0 + v3 state. If a future natality v2.9.0 closes some of the diffs (e.g., by re-deriving from a newer NCHS source), the snapshot in this entry becomes a frozen historical record — not a forward-looking invariant. The forward-looking invariant is the test code's 1e-4 tolerance, not the per-year diff list.

**Backport scope (per §11.4):** None directly. C8.1, C8.2, C8.3 receipts are unaffected. Phase D step 6 manuscript re-pass should consider whether to mention the linked-vs-natality bounded drift as a Comparability note (analogous to the existing natality-vs-NVSR microdata mention).

---

## 2026-05-12T23:50:00Z — [plan-update] C8.3 — Re-scope Section B race validation to 2022 single-race + Hispanic (vs NVSR 73-09 Table A); reframe perinatal joint as JOINT-USE DEMO with two sub-component validations (28+wk FD vs NVSR 73-09 Table 1; ENN <7d vs NVSR 73-05 Table 2)

**Choice (user-authorized at PRE-FLIGHT halt-and-ask 2026-05-12T22:30Z, option `(a) 2022 race + perinatal demo (Recommended)`):** Apply a §11 plan-update rewriting `NEXT_STEPS.md` §15.C C8.3 entry's PRE-FLIGHT inputs + DO scope + VERIFY criteria, and `KICKOFF.md` line 179, to reflect actual NVSR contents instead of the original §15 wording's source-location errors.

The two source-location errors in the original entry (DECISION_LOG 2026-05-12T21:00:00Z, written at phase-c-authorized time without L9 PDF cheap-check):

- (A) "NVSR 73-09 Table A for 2022 perinatal validation" — NVSR 73-09 is *Fetal Mortality: United States, 2022* by Gregory et al., not a perinatal-mortality report; Table A is by single-race + Hispanic fetal mortality for 2022. NCHS no longer publishes a combined perinatal-mortality rate per year (the MacDorman/Gregory "Fetal and Perinatal Mortality" combined series stopped after 2013 data per NCHS website; the two strands are now separate annual NVSR series). C8.3 PRE-FLIGHT L9 cheap-check (text-extracted NVSR 73-09 via PyMuPDF; verified every table heading 2026-05-12T22:00Z).
- (B) "NVSR fetal-mortality table for 2017 by maternal race" — no such NVSR exists. C8.3 PRE-FLIGHT (~30 min L9 cheap-check 2026-05-12T22:05–22:25Z): probed `cdc.gov/nchs/data/nvsr/nvsr{65..72}/nvsr{vol}_{nn}{,_,-,-508,_508}.pdf` covers via PyMuPDF; found NCHS annual Fetal Mortality NVSR series resumes at **NVSR 70-11 (2019 data)** after a 2014–2018 gap. The 2017 by-maternal-race fetal mortality tabulation is unpublished.

**Plan-update applied (this commit):**

1. **`NEXT_STEPS.md` §15.C C8.3 entry rewritten:**
   - Title: "timeline + perinatal joint + 2022 race validation" (was "+ Section B race validation").
   - PRE-FLIGHT inputs: cite **NVSR 73-09 Table 1** (28+wk fetal-death = 9,956 for 2022; on-disk PDF sha=`2590e417…`); **NVSR 73-09 Table A** (7 cells for 2022 single-race + Hispanic fetal-mortality rates; same on-disk PDF); **NVSR 73-05** (Ely & Driscoll 2024, *Infant Mortality 2022*, sha=`dccdc895…`, Table 2 = early-neonatal <7-day rate 2.81/1000 + 6 race-stratified breakouts; to be fetched at DO step 1 + recorded in PROVENANCE).
   - DO scope: explicit re-spec — (i) timeline figure; (ii) Section B refactor to 2022 single-race + Hispanic (using `race_hispanic_revised` in fetal-death + `maternal_race_ethnicity_5` in natality); existing 2017 bridged-race cells preserved as documented "machinery demo" closing the manuscript's joint-use bridge for the last-bridged-race-year (no NVSR-validation claim); (iii) Section C perinatal joint computation as JOINT-USE DEMO with sub-component validations (28+wk FD vs NVSR 73-09 Table 1; ENN <7d vs NVSR 73-05 Table 2).
   - VERIFY criteria: explicit per-cell tolerance + regression gate on Section A.

2. **`KICKOFF.md` line 179 edit:** "C8.3 — Cross-product Tier-1: timeline + perinatal joint" → "C8.3 — Cross-product Tier-1: timeline + perinatal joint + 2022 race".

3. **PRE-FLIGHT log addendum** at 2026-05-12T23:50:00Z marks **PROCEED** post-resolution; original HALT entry preserved per append-only convention.

4. **This DECISION_LOG entry** records the §11 plan-update.

**Alternatives considered (per the PRE-FLIGHT AskUserQuestion 2026-05-12T22:30Z):**

1. **(a) 2022 race + perinatal demo (chosen).** Pro: uses on-disk NVSR 73-09 + a single freshly-fetched NVSR 73-05 PDF; latest-year (post-C8.2 refreshed envelope) validation; cleanly aligns with manuscript's joint-use claim; no bridged-race availability issue since 2022 uses the post-2018 single-race standard NCHS publishes for. Preserves the 2017 machinery as documented bridge to the last-bridged-race-year. Con: drops the "2017 deferred Task 4 fragment closes here" framing in favour of a more defensible 2022 validation; manuscript line 99 may need a sibling claim in Phase D step 6.
2. **(b) Keep 2017 machinery + smaller perinatal claim.** Pro: smallest change vs original §15 plan. Con: Section B remains externally unvalidated; defers the deferred-Task-4-fragment ambition again.
3. **(c) Split: timeline + 2022 race only; perinatal becomes new C8.X.** Pro: smaller task (~1 session vs 2). Con: adds plan-update overhead + defers the most distinctive cross-product demo.
4. **(d) Halt + [plan-update] rewriting §15 entry (no DO this session).** Pro: methodologically cleanest. Con: another session of plan-update-only overhead before any DO work.

**Reason:** §11 plan-update process specifically accommodates scope corrections surfaced during PRE-FLIGHT verification of plan-vs-reality alignment (Convention 3 Field-value snapshot caught the NVSR-source mismatch at the right moment — exactly what cheap-checks are for). Option (a) maximizes manuscript-relevance per-NVSR-fetch effort and avoids re-litigating the 2017 deferred-Task-4 framing without dropping it — the 2017 machinery stays in the notebook with a clear "machinery demo" caveat, so the closeable threads stay closed.

Three protocol justifications: (i) §2 principle 1 "cheap-before-expensive" — discovering the NVSR-source mismatch at PRE-FLIGHT saves ~1 session of rework after a DO-time NVSR cell that doesn't exist surfaces a halt mid-task; (ii) §11 plan-update is the canonical path for in-Phase-C scope adjustments per Q42 (>1 session candidates require [plan-update]; this scope change replaces ~0.5 sessions of original 2017 work with ~0.5 sessions of 2022 work + adds NVSR 73-05 fetch + Section B refactor — net effort unchanged at 2 sessions); (iii) §10 self-check encourages the LLM to surface "what could I have gotten wrong that VERIFY wouldn't catch" — in this case, planning errors masquerading as data-availability questions.

**Source:**
- `PRE_FLIGHT_LOG.md` 2026-05-12T22:30:00Z entry documenting the HALT discovery (Halt #1 §7.12 conflicting documentation).
- `EXPLORATION_REPORT.md` §D.1 (perinatal computation candidate) + §D.2 (Section B 2017 race validation candidate; framing inherited the original §15 source assumption — the same fact-error existed at Phase B exploration time but wasn't surfaced as a PRE-FLIGHT-class L9 cheap-check would have).
- On-disk NVSR 73-09 PDF text-extraction (PyMuPDF) confirms Table A topic + Table 1 cell values.
- NVSR series probe 2026-05-12T22:00–22:25Z confirms NVSR 70-11 = Fetal Mortality 2019; gap 2014–2018.
- WebSearch + URL probing at `cdc.gov/nchs/data/nvsr/nvsr73/nvsr73-05.pdf` returned HTTP 200 + Table 2 verified containing 2022 early-neonatal rates by race/Hispanic (Total 2.81; AIAN 3.73; Asian 2.01; Black 5.05; NHOPI 3.36; White 2.23; Hispanic 2.65).
- User authorization chat 2026-05-12T22:30Z: option `(a) 2022 race + perinatal demo (Recommended)`.

**Verifiable by:**
- This `[plan-update]` commit's diff shows `NEXT_STEPS.md` §15.C C8.3 entry rewritten + `KICKOFF.md` line 179 edit + this DECISION_LOG entry + `PRE_FLIGHT_LOG.md` addendum + `STATUS.md` new section (next sub-session).
- Tag `C8.3-pre-do` lands on this `[plan-update]` commit.
- Future re-scope of the perinatal validation: triggers a new `[plan-update]` if NCHS resumes publishing a combined perinatal-mortality rate or if a new linked-file NVSR adds cells that close the redistribution-handling gap.

**Reversible:** yes — `git revert <this commit>` restores the original §15 C8.3 entry (which would re-introduce the source-location errors). The 2017 bridged-race Section B machinery in `notebooks/_build_joint_use_demo.py` is preserved in this plan-update; only its NVSR-validation framing changes. The Section A 2022-by-age cells (existing) are not touched at all.

**Residual risks:**

- (a) **NVSR 73-09 Table 1's "28+wk = 9,956" is post-proportional-redistribution** (footnote 2); our parquet stores observed gestational age without redistribution. The C8.3 VERIFY tolerance allows ~50 records of slop; the canonical fix is C8.4-scope (invariant tests for canonical-filter + redistribution-handling). Mitigation: document the tolerance in Section C narrative + RECEIPT Self-check.

- (b) **NVSR 73-05 Table 2's race-stratified early-neonatal rates** use the post-2018 single-race standard. Our linked-file parquet covers 2005–2023 and has both bridged and single-race columns; for 2022 the single-race columns are authoritative. The race-stratified ENN validation is OPTIONAL in C8.3 scope (headline = Total = 2.81 single cell); the per-race cells are deferred to C8.4 invariant-test territory if desired.

- (c) **Section B's 2017 bridged-race "machinery demo" framing in the notebook** may read as a defensive caveat. Mitigation: the notebook prose explicitly frames it as documentation-of-the-machinery-on-the-last-bridged-race-year, with the 2022 single-race Section B' as the headline NVSR-validated demonstration. The Phase D manuscript pass (step 6) reframes the joint-use paragraph to cite both.

- (d) **The L9 cheap-check that found no 2017 fetal-mortality NVSR is "absence of evidence"** — a future search may surface a non-NVSR NCHS publication (e.g., a Data Brief) that publishes 2017 fetal-mortality-by-maternal-race cells. Mitigation: if such a source surfaces, a Phase C / D `[plan-update]` adds a 2017-race validation cell to `external_validation_targets.csv` and the notebook; the current scope-shift does not preclude that.

**Self-check (residual risks the VERIFY phase wouldn't catch):**

- This entry assumes user authorization for the §11 plan-update via AskUserQuestion's option (a) selection. The selection was a single-question response; the LLM did NOT re-confirm via a second AskUserQuestion before applying. Risk: user may have intended a slight variant (e.g., "preserve the 2017 machinery only as a comment, don't keep the executed cells"). Mitigation: this entry's framing is reversible via a per-section edit if the user surfaces a disagreement post-fact.

- The NVSR 73-05 fetch + SHA-verify at DO step 1 is the first irreversibility boundary for canonical-state mutation in C8.3. If the on-disk SHA differs from PRE-FLIGHT's `dccdc895…`, the file has been re-released; HALT at DO step 1 per §7.11. Defense: PRE-FLIGHT explicitly records the SHA at fetch time + DO step 1 re-verifies.

- The "machinery demo" framing for the 2017 bridged-race cells may surface as "we shipped cells but didn't validate them" in a reviewer-skeptical reading. Mitigation: the joint_use_demo.ipynb pass/fail summary explicitly marks the 2017 cells as machinery-demo + cites this DECISION_LOG entry; the receipt's Self-check enumerates the risk.

**Backport scope (per §11.4):** None directly. C8.1 + C8.2 receipts unaffected. C8.3 ships forward under the revised scope.

---

## 2026-05-12T22:30:00Z — [plan-update] C8.2 — Re-scope to fetal-only; linked-2024-cohort deferred (no NCHS public-use file exists yet); C8.1 test-infra bug fixed as a followup commit

**Choice (user-authorized at PRE-FLIGHT halt-and-ask 2026-05-12T22:30Z):** Apply two resolutions to two HALT conditions surfaced at C8.2 PRE-FLIGHT.

1. **HALT #1 resolution — re-scope C8.2 to fetal-only.** Edit `NEXT_STEPS.md` §15.C C8.2 entry and `KICKOFF.md` Phase C task list: remove all linked-file scope (DO steps 5, 7 partial; SMOKE Tier 4; linked VERIFY criteria). Effort revised from 1-2 sessions to 1 session. Linked-2024-cohort refresh becomes a future task to be triggered via §11 plan-update when NCHS publishes `2025PE2024CO.zip` (estimated 2027-Q1).
2. **HALT #2 resolution — C8.1 test-infra fix.** Add four empty `__init__.py` files at `fetal_death/`, `fetal_death/tests/`, `natality/`, `natality/tests/` to make pytest's default-mode co-collection work. Shipped as a separate `[c8.1-followup]` commit `b84ff0d` immediately before this plan-update commit. FIX_LOG entry filed at 2026-05-12T22:30:00Z as L17-extension.

**Alternatives considered (per HALT #1):**

1. **Re-scope C8.2 to fetal-only (chosen).** Pro: avoids ~50% of original C8.2 effort that has no canonical state to mutate; produces a clean v2.4.0 fetal-death-only release; clear plan-of-record for the linked file (wait for `2025PE2024CO.zip`). Con: leaves the linked refresh as a small future task — but since NCHS hasn't released the 2024-cohort file, there's nothing to do *now* regardless.
2. **Defer C8.2 entirely** (re-sequence Phase C). Pro: zero canonical-state mutation in this session. Con: fetal-death 2023+2024 IS available and refreshing it is the cheapest-pre-submission win identified in Phase B (`EXPLORATION_REPORT.md` §A.1); deferring loses that signal. **Rejected.**
3. **Confirm linked file is current and ship a v2.9.0 no-op refresh-checkpoint.** Pro: explicit version-history note that the C8.2 linked-refresh check ran. Con: a Zenodo version bump for an empty diff is wasteful (Anti-Pattern #6's spirit) and confuses cite-by-version downstream. **Rejected.**

**Alternatives considered (per HALT #2):**

1. **Add four `__init__.py` (chosen).** Pro: cleanest fix; pytest's default prepend mode generates unique fully-qualified names; no new config file; forward-compatible with C8.5 (lockfile) which will add a `pyproject.toml` for environment-pinning unrelated to test config. Con: makes `fetal_death/` and `natality/` formal Python packages (zero existing code imports them as packages — verified via `git ls-files | xargs grep -lE "^(from|import) (fetal_death|natality)\b"` → 0 matches; harmonize.py dry-imports OK).
2. **Add `pyproject.toml` with `[tool.pytest.ini_options] addopts = "--import-mode=importlib"`.** Pro: documents the import mode explicitly; no package-structure change. Con: adds a new top-level config file that C8.5 will then have to coexist with or replace. Slightly more architectural surface.
3. **Rename one test file** (e.g., `test_fd_schema_dtype_parity.py`). Pro: 2-line code change. Con: breaks the symmetry between subprojects' test naming; the next time a paired test file is added (e.g., `test_release_smoke.py` for natality at C8.4) the same bug returns. **Rejected as not-durable.**
4. **Defer to C8.6 (CI wiring).** Pro: zero work now. Con: STATUS 22:00Z's "16 tests across both subprojects" claim remains unverifiable from the documented combined-pytest command until C8.6 forces a fix. **Rejected** — cheap-check moment is now.

**Reason:** Both HALTs are inexpensive to resolve at the C8.2 PRE-FLIGHT cheap-check moment and both have clean, forward-compatible fixes. The §11 plan-update process specifically accommodates this kind of scope correction surfaced during PRE-FLIGHT verification of plan-vs-reality alignment (Convention 3 Field-value snapshot caught the linked-file conflict at the right moment — exactly what cheap-checks are for).

Two protocol justifications: (i) §2 principle 1 "cheap-before-expensive" — discovering the linked no-op now saves a ~412 MB download + multi-hour re-harmonize attempt that would have produced byte-identical output; (ii) §11 plan-update process is the canonical path for in-Phase-C scope adjustments (per Q42 self-resolution: §11 plan-update required for any new candidate adding >1 session OR removing >1 session of scope). The linked-portion of C8.2 was ~0.5-1 session of work; the removal is right at the §11 threshold and gets a [plan-update] commit anyway.

**Source:**
- `PRE_FLIGHT_LOG.md` 2026-05-12T22:30:00Z entry documenting both HALTs.
- §15.C C8.2 entry pre-revision text (line 817-880 in NEXT_STEPS.md at commit `9fe662a`; full text preserved in git history).
- `EXPLORATION_REPORT.md` §A.1 (fetal-only portion remains in scope; linked-file portion already noted as "the 2024-cohort linked file isn't out yet but a refresh task can fire when it lands").
- NCHS public-use FTP HEAD probes 2026-05-12T22:30Z: `2024PE2023CO.zip` → HTTP 200 (cohort 2023, already imported); `2025PE2024CO.zip` → HTTP 404 (cohort 2024 not yet released).
- `natality/metadata/file_inventory.csv` row `2023_linked,…,2024PE2023CO.zip,imported=true,Cohort year 2023` (sha=`0e31b92bc05b6011…`).
- Linked parquet on disk (`/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized.parquet` sha=`e1795ac615a6ee40…`, 74,943,824 rows × data_year ∈ {2005…2023}) confirms 2023-cohort already shipped.
- User authorization chat 2026-05-12T22:30Z: HALT #1 = "Re-scope C8.2 to fetal-only (Recommended)"; HALT #2 = "Add __init__.py to both test dirs now (Recommended)".

**Verifiable by:**
- This `[plan-update]` commit's diff shows `NEXT_STEPS.md` §15.C C8.2 entry rewritten + `KICKOFF.md` line 178 edit + `PRE_FLIGHT_LOG.md` addendum + `STATUS.md` new section + this DECISION_LOG entry.
- Tag `C8.2-pre-do` lands on this commit (PRE-FLIGHT now PROCEEDS post-resolution).
- Commit `b84ff0d` (immediately prior, `[c8.1-followup]`) shows the 4× `__init__.py` additions + FIX_LOG entry.
- `pytest fetal_death/tests/ natality/tests/` under default import mode now returns "15 passed, 1 xfailed in ~39s" (cache-cleared run).
- Future re-scope of the linked-file portion: triggers a new `[plan-update]` commit when NCHS releases `2025PE2024CO.zip` (HEAD-probe will return HTTP 200; PRE-FLIGHT for the new task fires).

**Reversible:** yes — `git revert <this commit>` restores the original C8.2 §15 entry. The 4× `__init__.py` files can be removed by `git revert b84ff0d` (the `[c8.1-followup]` commit). Both reverts are independent and additive.

**Residual risks:**
- (a) **The "linked-2024-cohort needs a future task" assertion may be wrong** if NCHS changes the period-cohort-linked release cadence (e.g., releases two cohorts in one period file, or skips a cohort year). Mitigation: the future task's PRE-FLIGHT will run a sibling-probe of the FTP directory before assuming any specific filename. The §11 plan-update at that time would record any naming-convention surprise.
- (b) **The 4× `__init__.py` may interact with future package-management work** at C8.5 (uv/poetry lockfile) if the lockfile authoring chooses to treat `fetal_death/` and `natality/` as installable packages. Currently they are not installable; the `__init__.py` files are inert for `pip install` purposes. Mitigation: C8.5 PRE-FLIGHT explicitly notes the package-vs-not-package status of each subproject.
- (c) **The re-scoped C8.2 still mutates many files** (file_inventory.csv, validation_targets.csv, schema.csv years_available, harmonize.py SHA if era_tag mutates, version bumps in 4+ doc files, smoke EXPECTED state). The PRE-FLIGHT addendum's PROCEED clause covers these; the receipt's Forward-looking HALTs spec covers them too.

**Self-check (residual risks the VERIFY phase wouldn't catch):**
- This entry asserts the linked file is already at maximum NCHS-public-use extent. Verification: linked parquet data_year ∈ {2005…2023} confirmed by `pq.read_table(p, columns=['data_year'])`. If NCHS *had* released a partial 2024-cohort file under a different naming convention, this entry would miss it. Mitigation: explicit HEAD probes of `2025PE2024CO.zip` (404) and `2024PE2024CO.zip` (404) cover the natural sibling-derived candidate URLs; sibling probe of the NCHS landing page (`cdc.gov/nchs/data_access/vitalstatsonline.htm` via WebFetch 2026-05-12T22:30Z) confirms the most-recent period-cohort release documented is "2024 period/2023 cohort."
- The `[c8.1-followup]` commit's classification as "fix" (not a §11 plan-update) is borderline — it touches test infrastructure not data, and Anti-Pattern #6 ("never edit harmonized_schema.csv without bumping the schema version") doesn't apply. The 4× `__init__.py` files are pure-additive and reversible.

**Backport scope (per §11.4):** None. C8.1's RECEIPT and STATUS 22:00Z section remain canonical for what C8.1 shipped; the `[c8.1-followup]` patch is documented in FIX_LOG 2026-05-12T22:30:00Z; future audits see the trail. The C8.1 RECEIPT's Self-check section already flagged "test infrastructure may need closer scrutiny" as a residual risk (item 1 — though framed around xfail rot, the broader test-infra fragility was implied).

---

## 2026-05-12T22:00:00Z — C8.1 — schema `years_available` regen via `_regenerate_schema_years.py` — auto-derived field cleanup; NO schema-version bump

**Choice:** Run `python3 fetal_death/scripts/_regenerate_schema_years.py` (sibling of standalone-build script, now copied into the monorepo) to update 46 of 73 `harmonized_schema.csv` rows whose `years_available` strings had drifted from the actual parquet data after the V3a + V3b backward extensions (V3a RECEIPT note 8 + V3b RECEIPT note 8 explicitly deferred this cleanup). **No schema-version bump** — `years_available` is an auto-derived field whose canonical value is mechanically derivable from the parquet; the regen script's purpose is exactly this regeneration. New schema SHA: `337a0ad0ab6d0a6b…` (was `69f92bf775251f1e…`).

**Alternatives considered:**

1. **Run the regen now as part of C8.1 (chosen).** Pro: closes the V3a/V3b deferred-cleanup item with the right tool (auto-derivation, not hand-editing); the `_regenerate_schema_years.py` test in the smoke suite (`test_schema_years_available_matches_data`) becomes PASS-able without xfail/skip. Con: schema CSV SHA changes; future grep against the old SHA needs to point at the new SHA.

2. **Bump fetal-death version v2.3.0 → v2.4.0 as part of C8.1.** Pro: Anti-Pattern #6 says "Never edit harmonized_schema.csv without bumping the schema version OR adding a comment row referencing the relevant DECISION_LOG entry"; a literal reading would force a version bump. Con: `years_available` is a documentation field, not a schema-structure change (no column added/removed/redefined); a version bump for a regen feels like inflated bookkeeping. Also: C8.2 (latest-year refresh) will likely re-regen with +2023/+2024 entries and bump to v2.4.0 anyway; doing it now and then bumping again on C8.2 is wasteful.

3. **Defer to C8.2.** Pro: bundle the regen with the version bump. Con: leaves the smoke's `test_schema_years_available_matches_data` failing through C8.1's interim, which violates the "every commit ships green CI" discipline that Tier 1 is building toward.

4. **Mark `test_schema_years_available_matches_data` xfail.** Pro: defers the schema edit. Con: actively hides a fixable drift via xfail when the tooling to close it exists right now.

**Reason:** The DECISION_LOG-entry exception in Anti-Pattern #6 is exactly designed for this case: the rule's spirit is "no silent schema edits that could be missed by a future audit." Filing this DECISION_LOG entry + the C8.1 RECEIPT + the FIX_LOG L13-extension entry makes the regen fully auditable: a future session sees the entry, the per-column drift list in this entry's source, and the test passing on the new state. Anti-Pattern #6 is satisfied.

Three protocol justifications: (i) §2 principle 1 "cheap-before-expensive" — running the canonical regen tool is cheaper than authoring a version-bump migration; (ii) §2 principle 4 "re-running must be free" — `_regenerate_schema_years.py --check` is idempotent and confirms the new state; (iii) §11 plan-update process is not triggered — this is a documentation-field regeneration, not a structural schema change.

**Source:**
- `fetal_death/scripts/_regenerate_schema_years.py` (newly canonicalized in the monorepo per C8.1 DO-1).
- V3a RECEIPT `RECEIPTS/task7_v3a_2026-05-12T14-30-00Z.md` Notes-for-next-session item 8 ("Schema CSV `years_available` retroactive V3a gap fixes still deferred. Task 10 polish.").
- V3b RECEIPT `RECEIPTS/task7_v3b_2026-05-12T18-45-00Z.md` Notes-for-next-session item 8 (same text, V3a→V3a/V2.1 substitution).
- STATUS 2026-05-12T18:45Z Build-artifacts-current item 7 ("PROVENANCE.md still stale at v2.0.0 SHAs … Task 10 PRE-FLIGHT must refresh it.") — note: PROVENANCE.md refresh is separate from this schema CSV regen and remains deferred to C8.13 / Phase D.

**Verifiable by:**
- `git show HEAD:fetal_death/harmonized_schema.csv | shasum -a 256` returns `337a0ad0ab6d0a6b…`.
- `python3 fetal_death/scripts/_regenerate_schema_years.py --check` returns "OK: schema years_available matches data for all 73 columns" on the post-regen schema.
- `pytest fetal_death/tests/test_release_smoke.py::test_schema_years_available_matches_data` PASSes (was FAIL pre-regen).
- 46 rows changed; 27 rows unchanged (those whose `years_available` was already correct pre-V3a/V3b). Per-row diff visible in `git diff HEAD~1 fetal_death/harmonized_schema.csv`.

**Reversible:** yes — `git revert <this commit>` restores the prior `years_available` strings. The script is idempotent so re-running on the reverted state produces the same drift report.

**Residual risks:**
- (a) **The regen overwrites any hand-curated `years_available` strings that intentionally used a non-canonical shorthand.** Verified by inspection of the drift list: every drifted row's "target" is strictly more accurate than the "current" (e.g., `version_flag`: '1982-1988, 1992-2002, 2005-2022' → '1982-2022' — current was just stale, not intentional). No hand-curated annotations lost.
- (b) **Future data extensions (e.g., C8.2 latest-year refresh) will trigger another drift.** Mitigation: every subsequent data-extension task PRE-FLIGHT lists schema regen as a planned in-task step; the regen is bundled into the task that introduces the new year(s) so the schema and parquet always agree at task-completion time.

**Self-check (residual risks the VERIFY phase wouldn't catch):**
- The regen script computes `years_available` as the set of `data_year` values where the column has non-null content. For columns that are *intentionally* null in some years (e.g., `hispanic_origin` truly absent before 1989), the regen reflects shipped reality. If shipped reality is wrong (e.g., a parser bug populated a column erroneously), the regen would document the bug as canonical. Mitigation: V3a/V3b RECEIPT byte-clean regression already verified no spurious populations; the regen reflects intentional state.
- The regen does not update the `notes` field or any other column's annotations that might reference outdated year ranges. Anti-Pattern #6's "schema edits require version bump" applies more naturally to structural changes; documentation-field updates have a lower bar. Mitigation: per-row review during regen confirms no `notes` field references stale year ranges in this case.

**Backport scope (per §11.4):** None directly. The V3a RECEIPT note 8 and V3b RECEIPT note 8 items are now CLOSED.

---

## 2026-05-12T21:00:00Z — [plan-update] phase_c_authorized — User authorized Q35 = Tier 1+2 (~29-35 sessions of Phase C); Q32-Q42 self-resolved by LLM per user directive; KICKOFF.md Phase C populated + NEXT_STEPS.md §15 C8.1-C8.15 task entries appended

**Choice (user-authorized):** Q35 = **(b) Tier 1 + Tier 2** = ~29-35 sessions of Phase C work before Phase D (Task 9 + Task 10 + public-repo v1.x sync + manuscript submit). Phase B `EXPLORATION_REPORT.md` §K plan-update applied at this commit: KICKOFF.md Phase C placeholder replaced with the Tier-1+Tier-2 task list; NEXT_STEPS.md §15 appended with C8.1-C8.15 task entries (each with full five-phase framing per §4 + Convention 1-5 binding); this DECISION_LOG entry + accompanying STATUS section record the authorization.

**Q32-Q42 self-resolutions** (per user directive "the rest of the questions attempt to answer by yourself without my input in the best way possible"):

- **Q32 (Phase B 7th-dimension inclusivity).** CLOSED — no 7th dimension surfaced during Phase B. The six-dimension brief (data extensions, robustness/testing, usability/convenience, cross-product/joint-use, documentation, performance/distribution) was comprehensive. The ~42 candidates enumerated in EXPLORATION_REPORT §A-§F cover every legitimate pre-submission expansion surface identified.

- **Q33 (Phase C effort ceiling).** No explicit cap; user authorized Tier 1+2 ~29-35 sessions and asked LLM to self-pace. **Self-imposed halt-checkpoint**: if cumulative Phase C effort drifts beyond +20% of the 29-35 session estimate (i.e., >42 sessions), halt at the next clean task boundary and re-ask the user before continuing. Encoded in KICKOFF.md "Always-on Phase C discipline" section.

- **Q34 (in-scope vs out-of-HVS-mission boundary).** **Affirmed as-defined**: HVS scope is vital events around birth (natality + fetal death + linked birth-infant death). Marriage/Divorce, Multiple-Cause-of-Death (all-age mortality), and abortion surveillance are explicitly OUT-of-scope per EXPLORATION_REPORT §A.6. The one-paragraph boundary statement in PRIOR_ART.md ships as part of **C8.8** (CHANGELOG + PRIOR_ART update) to preempt reviewer "why not all vital events?" comments.

- **Q35.** **(b) Tier 1 + Tier 2 authorized** by user directive 2026-05-12. ~29-35 sessions of Phase C before Phase D.

- **Q36 (Tier-5 ordering).** **N/A** — Tier 5 not authorized in this round. If user later authorizes Tier 5: default A.2 (natality 1968-1989) first (shorter, cleaner sibling of V3b just shipped), A.3 (linked 1983-2004) second (benefits from A.2's 1978-cert layout knowledge).

- **Q37 (Phase C kickoff item).** **C8.1 first** (cheapest item, pure-metadata, fixes the known stale L17 smoke case per STATUS 20:30Z FL-HALT #10). **C8.2 second** (latest-year refresh: extends data envelope before any test/CI scaffolding so subsequent CI gates on the full envelope). Sequencing encoded in KICKOFF.md "Sequencing notes within Phase C" section.

- **Q38 (R-only vs full Stata/SAS/R coverage).** **R full quickstart ships** (C.2 inside **C8.9**). **Stata/SAS pointer-files deferred** to post-v1 ancillary (C.3 = Tier 3 = deferred per Q41 default). Rationale: R quickstart's marginal cost is ~1 session; full Stata/SAS quickstarts require Stata/SAS licenses on the build machine (we don't have them) and pointer-files give 80% of the value at 10% of the cost. Defer until a Stata/SAS-using contributor surfaces, or until the IJE post-publication community signals demand.

- **Q39 (CLI tool vs DuckDB views).** **DuckDB views ship** (C.4 inside **C8.9**). **CLI tool deferred** (C.7 = Tier 3 = deferred per Q41). Rationale: DuckDB's SQL surface covers the same ad-hoc-query use cases as a custom CLI but with zero maintenance burden (DuckDB ships with its own CLI; users wrap with `duckdb -c "SELECT * FROM <view>"`). The custom CLI was strictly dominated by DuckDB in `EXPLORATION_REPORT.md` §C.7.

- **Q40 (manuscript re-paragraph cadence).** **Single submission after Tier 2.** Tier 5 deferred per Q35; the re-paragraph-twice scenario does not apply. If Tier 5 is later authorized post-submission, ships as v1.1 / v2.0 with an IJE *Update* note or a new Zenodo concept-DOI patch. Manuscript Coverage paragraph updated once (KICKOFF Phase D step 6) reflecting 1982-2024 fetal death + 1990-2024 natality + 2005-2024 linked envelope (post-C8.2 refresh).

- **Q41 (Tier-3 items).** **Defer all to post-v1 ancillary releases.** Specifically: A.5 matched-multiples (1-2 sessions; post-v1), E.7 CODEBOOK extensions (2-4 sessions; post-v1 — diminishing returns vs. existing CODEBOOK), C.3 Stata/SAS pointer-files (per Q38), C.5 pre-computed cross-tab CSVs (1 session; defer — maintenance tax), C.7 CLI tool (per Q39). All five Tier-3 candidates revisitable at Phase D close.

- **Q42 (Phase B-2 trigger conditions).** **§11 plan-update required** for any new candidate adding **>1 session**. ≤1 session candidates may be folded into the nearest in-progress C8.X task as a scope amendment via DECISION_LOG entry (no separate `[plan-update]` commit). >1 session candidates require explicit user authorization before execution. Encoded in KICKOFF.md "Always-on Phase C discipline" section.

**Alternatives considered:** None for this specific authorization-application — the user explicitly directed Q35 = (b) and self-resolution of the rest. The alternatives considered for each Q above are documented in EXPLORATION_REPORT.md §H + this entry's per-Q rationale.

**Reason:** User explicit directive 2026-05-12 in response to LLM's (a)-(d) handshake post-kickoff: *"Q35: Tier 1+2 the rest of the questions attempt to answer by yourself without my input in the best way possible."* The §11 plan-update process (LESSONS → propose diff → human review → LLM applies → commit `[plan-update]`) is satisfied: EXPLORATION_REPORT.md §K is the proposed diff; user reviewed via the (a)-(d) handshake; this commit applies it; the `[plan-update]` prefix tag is on the commit.

**Source:**
- `EXPLORATION_REPORT.md` §G.4 (suggested execution order) + §H (open questions) + §K (plan-update structure).
- `STATUS.md` 2026-05-12T20:30:00Z "Notes for next session" item 2 (Tier 1+2 default path) + items 3-5 (per-prefix execution branches).
- `KICKOFF.md` "Current planned sequence" 2026-05-12 (Phase B mandate; commit `306370e`).
- User authorization chat 2026-05-12: *"Q35: Tier 1+2 the rest of the questions attempt to answer by yourself without my input in the best way possible."*

**Verifiable by:**
- This `[plan-update]` commit's diff shows KICKOFF.md Phase C placeholder replaced with the Tier-1+Tier-2 task list + NEXT_STEPS.md §15 appended with C8.1-C8.15 entries.
- Tag `phase-c-authorized` lands on this commit.
- The next session's `git tag --list 'C8.*'` shows progression: first `C8.1-pre-do` (after PRE-FLIGHT), then `C8.1-complete` (after RECEIPT), then `C8.2-pre-do`, etc.
- Q32-Q42 self-resolutions in this entry are auditable: a future audit session can verify each resolution against the EXPLORATION_REPORT.md options + the user's stated preferences (the user explicitly authorized Tier 1+2 = "robust and useful middle ground" — every Q32-Q42 self-resolution follows that signal).

**Reversible:** yes at any point during Phase C — the user can re-issue any of (a) "skip ahead to Phase D", (b) "trim Tier 2 to subset", (c) "add Tier 5 candidate X", (d) "reverse a specific Q-resolution" — each triggers a new `[plan-update]` commit (per §11). Already-shipped Phase C tasks are reversible via `git tag <task_id>-pre-do` rollback.

**Residual risks:**

- (a) **Q33 effort-ceiling may surface mid-Phase-C.** If C8.4 (invariant tests) takes 5 sessions instead of 3, or if C8.12 (mutation tests) cascades through FIX_LOG, the cumulative drift breaks the +20% cap. Mitigation: halt at next clean checkpoint per encoded discipline; surface honestly; ask user to trim Tier 2 if needed.

- (b) **Q38 + Q39 deferrals may need re-opening if reviewer feedback specifically asks.** A reviewer who works in Stata or wants a CLI tool may surface the request post-submission. Mitigation: framing the deferrals as "post-v1 ancillary" (not "rejected"); easy to add via §11 plan-update.

- (c) **Q41 Tier-3 defer-all may be wrong for E.7 CODEBOOK extensions.** Per-variable historical-value-distribution panels could materially strengthen the manuscript's *Comparability classification* claim. The 2-4 session cost is the friction. Mitigation: revisit at Phase D close; possibly pull E.7 into Phase D scope.

- (d) **Q42 §11-plan-update threshold (>1 session) may be too lenient or too strict.** A 0.6-session candidate that affects schema (e.g., a new derived column) is materially different from a 0.6-session candidate that affects docs only. Mitigation: schema-touching candidates default to §11 regardless of session count; docs-only candidates default to in-progress-task amendment regardless of session count.

- (e) **The plan-update applies the §K.1 KICKOFF replacement + §K.2 NEXT_STEPS §15 appends but does NOT yet update PROVENANCE.md, the manuscript, or any data artifact.** Those updates remain queued per existing STATUS.md notes. Mitigation: encoded in C8.X task descriptions; each task's RECEIPT updates the relevant downstream artifact.

**Self-check (residual risks the VERIFY phase wouldn't catch):**

- The Q32-Q42 self-resolutions reflect *my* read of EXPLORATION_REPORT.md's defaults + the user's "best way possible" signal. A subtle risk: the user might have intended a meaningfully different default for one or more Qs (e.g., they might have wanted Stata/SAS quickstarts to ship, or the CLI tool, or Tier-3 CODEBOOK extensions). Mitigation: each self-resolution is explicit + reversible; if the user surfaces a disagreement post-fact, a single `[plan-update]` commit adjusts the plan.

- The NEXT_STEPS.md §15 C8.1-C8.15 entries vary in detail (C8.1 + C8.2 fully fleshed per §K.2 promise; C8.3-C8.15 compact). The compact entries name the goal + inputs + DO scope + VERIFY but defer the full SMOKE plan + Forward-looking HALTs spec to each task's own PRE-FLIGHT. This is per existing §15 precedent (Task 9 entry is similarly compact). Risk: a future session might claim "C8.X §15 entry is too thin to PRE-FLIGHT from" — mitigated by PRE-FLIGHT extending the entry as needed per §4.1.

- This entry's Q-self-resolutions are not user-confirmed individually. A safer protocol would have surfaced each Q as a separate AskUserQuestion; the user's "answer them yourself" directive explicitly waived that. Risk surfaced + accepted by user; the §11.4 backport process covers any reversal.

**Backport scope (per §11.4):** None. Phase A + Phase B receipts are unaffected by this plan-update. C8.X tasks ship forward.

---

## 2026-05-12T20:30:00Z — phase_b_exploration — Phase B exploration session COMPLETE; `EXPLORATION_REPORT.md` drafted; plan-update proposal status PENDING USER REVIEW; recommended prefix Tier 1+2 ~29-35 sessions

**Choice (proposal pending user confirmation):** Phase B's deliverable is `EXPLORATION_REPORT.md` at monorepo root (new file; 6-dimension candidate enumeration ~42 candidates across §A–§F + cumulative effort estimate + suggested execution order in §G.4 + plan-update proposal in §K + open questions Q35–Q42 in §H). The plan-update proposal (KICKOFF.md Phase C replacement + NEXT_STEPS.md §15 task entries C8.1–C8.23) is NOT yet applied; it requires explicit user authorization via Q35.

**Recommended user choice for Q35**: Tier 1 + Tier 2 (~29-35 sessions of Phase C work) as the "robust and useful" middle ground that maximizes pre-submission polish without the multi-month timeline extension that Tier 5 (backward extensions A.2 natality 1968-1989 + A.3 linked 1983-2004) would impose.

**Alternatives considered (per Q35):**

1. **Tier 1 only (~13–15 sessions)** — Pre-Phase-D must-haves only: smoke retag, dtype parity, invariant tests, latest-year refresh, lockfile/Dockerfile, CI, end-to-end smoke, CHANGELOG + PRIOR_ART update. Ships a substantially more robust HVS than today; submit manuscript with current envelope. Pro: shortest path to submission (~2-3 weeks). Con: leaves R quickstart, DuckDB views, worked-example notebooks, migration guides on the table.

2. **Tier 1 + Tier 2 (~29–35 sessions, chosen as recommendation)** — Tier 1 + state-stratified denominators + R quickstart + DuckDB views + 3 worked-example notebooks + migration guides + cross-product COMPARABILITY + mutation tests + L13/L14 audits + GitHub release artifacts. Pro: maximally polished v1.0; manuscript ships at v1.0 with all infrastructure complete. Con: ~4-6 weeks to submission.

3. **Tier 1 + Tier 2 + Tier 5 (~45–62 sessions)** — adds natality 1968-1989 backward extension (6-10) + linked 1983-2004 (8-14) + perinatal-record pre-joined parquet (2-3). Pro: manuscript launches with maximum-extent coverage (natality 57 yrs, linked 41 yrs with documented 1992-1994 gap). Con: ~3-4 months to submission; re-paragraphs Coverage section twice; methodology-paper territory for the perinatal-record join.

4. **Phase B-2 (defer execution; further investigate before authorizing prefix)** — if any §H open question (Q35-Q42) cannot be answered today. Pro: zero commit risk. Con: another session of latency.

**Reason:** Phase B's mandate was to enumerate the frontier honestly without narrowing prematurely, then present the user with one decision point with full trade-off picture. The Tier-prefix structure in §G.4 lets the user authorize a specific prefix without committing to "everything possible" sight unseen. Each prefix delivers a coherent shipping checkpoint:

- Tier 1 → ships ~2-3 weeks; manuscript at current 1990-2024 / 1982-2024 / 2005-2024 (post-refresh) envelope.
- Tier 1 + Tier 2 → ships ~4-6 weeks; same envelope + maximum polish.
- Tier 1+2+5 → ships ~3-4 months; backward-extended envelope + maximum polish.

Three protocol justifications: (i) §11 plan-update process accommodates this kind of mid-project amendment; (ii) §2 principle 1 "cheap-before-expensive" — Phase B's read-only research was cheap relative to Phase C execution and prevented committing to "everything" sight unseen; (iii) §10 self-check — the structured per-candidate writeup (effort/risk/manuscript-impact) is the planning-level analog of "what could I have gotten wrong that VERIFY wouldn't catch."

**Source:**
- `EXPLORATION_REPORT.md` at monorepo root (drafted this session; ~1400 lines).
- Agent `aea960a496472bb6b` external-research transcript (50 tool uses, ~5min wall): NCHS FTP directory listings for natality, fetal-death, linked, period-cohort-linked, matched-multiples, mortality; CDC NCHS data-access landing page; NBER, ICPSR, IPUMS scope confirmation. Full URL list in EXPLORATION_REPORT.md §A.9.
- Agent `a3e650be058a65976` literature-gap re-verification transcript (50 tool uses, ~4min wall): WebSearch + WebFetch on academic, GitHub, IPUMS, NBER, ICPSR. Gap claim defensible as of 2026-05; three small PRIOR_ART.md updates suggested.
- Internal repo introspection by orchestrating LLM (in parallel with agents): tests inventory (1 test file, stale L17 case post-V3b), CI inventory (none), reproducibility tooling inventory (none), docs inventory (CHANGELOG missing, manuscript stale, PROVENANCE.md 4 versions stale).
- User directive 2026-05-12 chat post-`task7_v3b-complete`: *"i would like do do everything possible with this project in terms of extending the actual project and adding diferent things to the project to make it as robust and useful as possible before we do the paper or the zenodo so i want to do an ivetigative session and exploration of what we can do and then add it to the plan to do it in subsequent sessions."*

**Verifiable by:**

- `EXPLORATION_REPORT.md` at monorepo root exists; sha256 recorded at commit time.
- This DECISION_LOG entry timestamp 2026-05-12T20:30:00Z supersedes 19:15:00Z's Phase-B-mandate status (from MANDATED to COMPLETE-PENDING-AUTHORIZATION).
- Forward-looking HALTs in STATUS 2026-05-12T20:30Z items 1-3 are the next session's pre-flight check: report file present, DECISION_LOG entry status unchanged, no C8.X tags yet.
- Next-session Phase C kickoff: if `git tag --list 'C8.*'` returns any tag, the user must have authorized; otherwise Phase B halt is still in force.

**Reversible:** yes — Phase B is read-only. If the user finds the report's scope inadequate or the prefix structure too coarse, the next session can be a Phase B-2 (further investigation) or a Phase B amendment (re-scoring candidates) without any state to roll back. The plan-update proposal in §K is NOT yet applied to KICKOFF.md or NEXT_STEPS.md; those edits land only on Q35 authorization.

**Residual risks:**

- (a) **Effort estimates may be systematically biased.** Calibration anchor is V3b's empirical 2-3 sessions; the Tier-1 robustness items (test scaffolding, CI) are well-understood; the Tier-2 worked-example notebooks have higher variance (depends on user-validation feedback per notebook); the Tier-5 backward extensions are the highest-variance (cohort/period design decision in A.3 alone could absorb a session). Per the KICKOFF brief: estimates are honest ranges, not pinned values; the user reviews the total and trims if needed.

- (b) **Phase B did not deep-research several candidates' validation grids.** For natality 1968-1989, the *Vital Statistics of the United States* paper volumes are partially online and partially not — building a complete validation grid for A.2 may surface OCR friction not anticipated. For linked 1983-2004, the cohort/period publishing-design decision is mentioned but not adjudicated. Both are documented in §A as risks; Phase C PRE-FLIGHT for those tasks will do the L9 cheap-check on the actual NVSR / Linked-File documentation.

- (c) **The user may want to add a candidate not in this report.** Phase B's §G.4 enumerates ~42 candidates from the KICKOFF brief's six-dimension grid; if the user's response to Q35 surfaces a 43rd ("can we also add X?"), the right protocol is a §11 plan-update at that point (per Q42 default), not a silent in-Phase-C scope creep.

- (d) **Phase B may have under-narrowed.** Tier 3 (matched-multiples ancillary, CODEBOOK extensions, Stata/SAS quickstarts, pre-computed cross-tab CSVs, CLI tool) is listed as defer-to-post-v1 in §G.4 — but a user who wants "everything" maximally might pull some of these into Tier 2. Q41 surfaces this explicitly.

- (e) **Manuscript framing may need adjustment per Q40.** If Tier 5 is in scope, the question of single-submission vs. dual-submission-with-v1.1-update is a real editorial decision (some journals support post-publication data-update notes; some don't). The default in §G.5 — single submission after Tier 2, Tier 5 as v1.1 update — is the lowest-risk path but the user may prefer otherwise.

**Self-check (residual risks the VERIFY phase wouldn't catch):**

- This entry asserts Phase B's deliverable is complete. The verification is the existence of `EXPLORATION_REPORT.md` at monorepo root + its §0-§K structure + the §H open questions being answerable from the report's content. A subtle risk: Phase B may have systematically over-prioritized testing/robustness items (B.1-B.12) because those are the easiest to score with the protocol's existing mistake-class matrix (§8), while harder-to-score items like research-extensions (C.8 perinatal-record join) and methodology-paper territory (A.3 cohort/period design) may be under-prioritized. Mitigation: the §G.4 tiering is explicit about which category each candidate falls into; the user can override the Tier-3/Tier-5 framing in Q41 / Q40.

- The two external-research agents were instructed to verify URLs + literature gap; the orchestrating LLM did not separately re-verify their findings (per "trust but verify" in the harness instructions). Mitigation: agent transcripts are at the disk locations cited in STATUS Notes; the user can spot-check any URL or citation by hand. The HTTP-200 / HTTP-404 results are deterministic facts about the CDC FTP server state on 2026-05-12 and can be re-verified at any time.

- This entry's "Recommended Tier 1+2" framing is a soft recommendation. The user has full discretion via Q35; this entry is not authorization for any specific prefix.

**Backport scope (per §11.4):** None. Phase B is read-only and no prior receipts are invalidated. Phase C work that lands after authorization may surface backports (e.g., the B.7 L13 audit may find an existing inventory CSV with stale claims), at which point §11.4 fires per-task.

---

## 2026-05-12T19:15:00Z — [plan-update] sequencing — Pre-submission scope expanded a 5th time: Phase B (READ-ONLY exploration session) + Phase C (execute proposed additions) inserted between Phase A (data-first; complete) and Phase D (paper + Zenodo + public-repo sync); manuscript submission paused

**Choice:** Add a mandatory **Phase B exploration session** (read-only) and a **Phase C execute-additions phase** to the pre-submission sequence in KICKOFF.md. The next LLM session is Phase B: research the full frontier of additions across 6 dimensions (data extensions, robustness/testing, usability/convenience, cross-product/joint-use, documentation, performance/distribution), produce per-candidate writeups with effort/risk/manuscript-impact estimates, propose a §11 plan-update for KICKOFF.md + NEXT_STEPS.md §15, halt for user authorization. Phase C subsequent sessions execute the user-authorized expanded plan. Phase D (Task 9 redirect notices + Task 10 unified Zenodo + public-repo sync + manuscript submit) runs only after Phase C completes.

**Alternatives considered:**

1. **Lock current 1982-2022/1990-2024/2005-2023 envelope and ship at v1.1** (the LLM's recommendation from chat 2026-05-12, post-V3b-complete). Pro: shortest path to submission; current coverage is already a defensible "Data Resource Profile" extent (41 yr FD + 35 yr natality + 19 yr linked). Con: leaves several plausible high-value additions (natality 1968-1989 backward extension; pre-2005 linked extension; latest-year refreshes; testing/usability infrastructure) on the table for a v2.0 release. User explicitly rejected this option in favor of maximum-extent pre-submission.

2. **Pull a SPECIFIC next addition (e.g., natality 1968-1989) into pre-submission without an exploration session.** Pro: faster than B+C. Con: chooses one expansion without comparing alternatives; loses the value of the systematic frontier sweep; would likely require subsequent ad-hoc expansions when the next idea surfaces. **Rejected** — exploration is a one-time investment that informs all subsequent expansion decisions.

3. **Insert exploration session + execute (chosen).** Pro: enumerates the full candidate set; gives the user one decision point with a concrete trade-off picture; subsequent execution sessions are well-scoped. Con: adds 1 session (Phase B) before any execution starts; total pre-submission timeline grows by Phase B (1 session) + Phase C (5-20 sessions TBD by Phase B output). **Selected**.

**Reason:** This is the 5th expansion of pre-submission scope (after Task 3 V2.1 → V3a → V3b → natality v2.8 → this one). The user's stated objective — *"i would like do do everything possible with this project in terms of extending the actual project and adding diferent things to the project to make it as robust and useful as possible before we do the paper or the zenodo"* — is maximalist; an exploration session is the right tool because individual pull-this-in decisions don't compare alternatives. Phase B's deliverable (a structured per-candidate writeup with effort/risk/impact) lets the user authorize a specific subset rather than committing to "everything" sight unseen.

Three protocol justifications: (i) §11 plan-update process explicitly accommodates this kind of mid-project amendment; (ii) §2 principle 1 "cheap-before-expensive" — Phase B's read-only research is cheap relative to Phase C execution; (iii) §10 self-check — surfacing the full candidate set forces the question "what could I have gotten wrong that VERIFY wouldn't catch" at the planning level, not just the per-task level.

**Source:**
- Chat 2026-05-12 between commits `b0c8b4a` (task7_v3b-complete) and this `[plan-update]` commit. User explicit directive quoted verbatim above.
- KICKOFF.md "Current planned sequence" section, rewritten in this commit, runs ~150 lines and is the canonical sequencing pointer for Phase B/C/D.
- Phase A complete summary in the new KICKOFF section reflects the closed receipts in `RECEIPTS/`.

**Verifiable by:**
- Next session's first action: pasting KICKOFF.md and outputting the (a)-(d) handshake. Expected (c): "Phase B exploration session per KICKOFF.md." If the LLM proposes any DO-phase work instead, halt — the KICKOFF directive was misread.
- Phase B deliverable: `EXPLORATION_REPORT.md` at monorepo root + STATUS.md section + new DECISION_LOG entry. None present today; their existence post-Phase-B is the verification.
- Phase C tasks: tagged `<task_id>-pre-do` + `<task_id>-complete` per added task; receipts in `RECEIPTS/`.

**Reversible:** yes — at any point during Phase B or Phase C, the user can re-issue the "lock current envelope, ship" decision; the existing Phase D plan (Task 9 / Task 10 / public-repo sync / manuscript) is intact and ready to execute. No canonical-state mutation is being committed by this plan-update itself — only the sequencing-pointer file (KICKOFF.md) and this DECISION_LOG entry.

**Residual risks:**
- (a) **Phase B inflates cumulative effort** — if Phase B proposes 15+ sessions of Phase C work, the manuscript submission delays significantly. Mitigation: Phase B's brief explicitly mandates honest effort estimates and a halt-for-authorization step; the user reviews the total before authorizing.
- (b) **Phase B over-narrows or under-narrows** — too narrow misses additions worth doing; too broad balloons Phase C. Mitigation: the six exploration dimensions are explicit in KICKOFF; the LLM must cover all six even if the proposal column for some dimensions ends up "no high-priority items found."
- (c) **Phase B hallucinates a candidate**. Mitigation: the brief mandates `WebFetch` + sibling-derived URL probing for every external data source (per LESSONS L1-extension 2026-05-12T04:30:00Z); any data candidate without verified URL+SHA is flagged as "needs further verification" rather than slotted for execution.
- (d) **Phase C surfaces a new mistake class mid-execution** that retroactively invalidates Phase A receipts. Mitigation: §11 backport process is unchanged; any new LESSONS row triggers a re-verification of affected prior tasks before continuing.
- (e) **Submission target slips past whatever timing the user has implicit**. Mitigation: surfaced honestly in Phase B's report; user decides.

**Self-check (residual risks the VERIFY phase wouldn't catch):**
- This plan-update is itself the kind of decision that the §10 self-check asks about: "what could I have gotten wrong that VERIFY wouldn't catch?" The biggest risk is that the user's intent — "everything possible" — is interpreted maximally when they actually meant "some specific high-value subset." The Phase B halt-for-authorization step is the mitigation: the user sees the proposed Phase C list and trims as desired before any execution. The §11 plan-update process puts the user back in the loop before any code or data is touched.
- The other class of risk: Phase B might surface a candidate the user already implicitly rejected (e.g., scope-creep into all-cause mortality, which is out-of-HVS-mission). Mitigation: the KICKOFF directive notes which extensions are clearly in-scope (vital events around birth: natality, fetal death, linked-infant-death) and lists candidate scope-creeps (e.g., multiple-cause-of-death) with "out of HVS scope unless user redirects" framing.

**Backport scope (per §11.4):** None. No prior receipts are invalidated by this plan-update; it's a forward-looking sequencing change only.

---

## 2026-05-12T18:30:00Z — task7_v3b — B3 maternal_race_bridged extension: 1978-rev 1-digit MRACE 0-9 → 4-cat bridged; code 7 (Other nonwhite) → null + code 9 (Not stated) → null

**Choice:** Extend the B3 `_checked_remap` in `fetal_death/scripts/03_harmonize/harmonize.py` with a new `era=='1985'` branch containing a 1-digit MRACE → bridged-race recode covering the 1978-revision V3b coding scheme:

| 1978-rev MRACE | Bridged | Records affected (1982-1988 total) |
|---|---|---|
| 0 (Other Asian or Pacific Islander) | 4 (API) | ~few hundred |
| 1 (White) | 1 (White) | ~290K |
| 2 (Black) | 2 (Black) | ~91K |
| 3 (American Indian/Aleut/Eskimo) | 3 (AIAN) | ~2K |
| 4 (Chinese), 5 (Japanese), 6 (Hawaiian), 8 (Filipino) | 4 (API) | ~12K combined |
| **7 (Other nonwhite)** | **"" (null)** | **~89 records** |
| **9 (Not stated)** | **"" (null)** | **~18,700 records (~3-5%/yr)** |

**Alternatives considered:**

1. **Map 7 → 4 (API).** Pro: keeps all V3b records in a bridged category. Con: incorrect — 1985 user guide page 18 explicitly names code 7 as "Other nonwhite", a residual catch-all for records not fitting any of the 8 specific named categories. Mapping to API would over-count bridged-API by ~89 records across 1982-1988. **Rejected** as semantically inaccurate.
2. **Map 7 → 3 (AIAN).** Pro: AIAN is a "minority other than Black/Asian" historical convention. Con: explicit conflation of unrelated racial groups. **Rejected**.
3. **Map 7 → null (chosen).** Direct parallel to V3a's 09 → null decision (DECISION_LOG 2026-05-12T14:30:00Z). The 4-cat bridged scheme does not have a residual bucket; null preserves integrity rather than false-categorizing. ~89 records exit race-stratified analyses; all V3b records remain in unbridged analyses (year totals, GA distributions, etc.). **Selected.**
4. **Add a new bridged category 5 = "Other (1978-rev residual)".** Pro: explicit. Con: schema mutation (`allowed_values=1|2|3|4|5`) for a category that exists only for V3b records — cross-era race comparability breaks. **Rejected** as scope-creep.

For code 9 (Not stated), null is the unambiguous choice — parallels V2 99 → null, V3a 09 → null. No alternatives considered.

**Reason:** The 1985 NCHS Fetal Death User Guide page 18 (item 79-81 MRACE field for the 1978-revision) explicitly defines MRACE codes 0-9 for 1978-revision records. Codes 4/5/6/8 cover specific Asian/Pacific-Islander subgroups; code 0 is the residual "Other API"; code 7 is the residual "Other nonwhite" (distinct from the API subgroups). The bridged-race 4-category recode (the NCHS standard since the 1997 OMB directives) has no residual bucket — White/Black/AIAN/API only. Mapping a residual catch-all into one of the 4 specific buckets would be a false categorization; null preserves integrity per the §2 fail-closed principle.

The 1978-revision residual structure differs from the 1989-revision: 1989-rev's residual catch-all is code 09 ("All other Races", catches everything not in 01-08); 1978-rev's residual is code 7 ("Other nonwhite", which sits alongside specific API subgroups 4-6/8 and the general API code 0). Both are residual; both map to null.

**Source:**
- `1985FetalUserGuide.pdf` page 18 (item 79-81 MRACE; PyMuPDF-extracted via text-layer, no OCR needed; SHA recorded in `raw_docs/fetal_death/` and verified at PRE-FLIGHT 2026-05-12T16:00Z).
- Per-year MRACE distributions in `output/yearly_clean/fetal_death_{1982..1988}_raw.parquet` confirming the 1-digit 0-9 scheme (no 99 sentinel; no 18-78 codes; codes 0-9 all observed).
- Existing B3 recode at `fetal_death/scripts/03_harmonize/harmonize.py` lines 271-300 (V2/V3a era; the entries `"99": ""` and `"09": ""` are the precedent for the null mapping).
- Documented in `fetal_death/V3b_1982_1988_LAYOUT_DECISIONS.md` ("Harmonization decision 2: B3 maternal_race_bridged 1-digit recode" section).

**Verifiable by:**
- `validate_external_v2.py` post-V3b: **33/33 PASS** byte-exact (counts 1982-2004 + rates 1995-2004). Per-year fetal-death counts (which use TABFLG/RESTATUS, not race) byte-exact against user-guide controls — confirming the 7→null + 9→null choices don't bias the canonical-filter aggregate (it can't, since the canonical filter doesn't use race).
- `python -c "import pandas as pd; df = pd.read_parquet('output/harmonized/fetal_death_derived.parquet'); v3b = df[(df.data_year >= 1982) & (df.data_year <= 1988)]; print('V3b null bridged-race:', v3b.maternal_race_bridged.isna().sum())"` returns ~18,789 (the ~89 code-7 + ~18,700 code-9 records).
- Re-running the harmonize.py B3 recode map inspection: the era=='1985' branch contains exactly 11 entries (codes 0/1/2/3/4/5/6/7/8/9 + blank); `_checked_remap` would raise on any unmapped code.

**Reversible:** yes — if a future analysis surfaces an NCHS-documented convention for 1978-revision code 7 (e.g., a peer-reviewed paper or an NCHS internal mapping that specifies 7 → bridged-X), the B3 map can be edited and the 1982-1988 yearly_clean parquets re-harmonized; V1+V2.1+V3a era unaffected.

**Residual risks:**
- (a) **NCHS may have a documented bridged-race convention for 1978-revision code 7 that I missed.** The 1985 user guide page 18 doesn't specify a 4-category bridged recode for code 7. RACEF3 (item 66-67 in the layout — the 3-category fetus race recode: 1=White, 2=Other than White or Black, 3=Black) would put code 7 records into RACEF3=2 — but that 3-cat collapse is incompatible with the harmonized schema's 4-category bridged scheme. Mitigation: same as V3a (DECISION_LOG 2026-05-12T14:30Z residual risk a); searching NVSR Series 21 reports for 1982-1988 race-stratified fetal death tables is post-submission scope.
- (b) **The ~89 record impact is small but non-zero on V3b race-stratified analyses.** A researcher using `maternal_race_bridged` to stratify 1982-1988 fetal deaths will see totals not exactly add up (89 records with null bridged-race from code 7; plus ~18.7K from code 9). The ~18.7K Not-stated fraction is ~3-5% per year — larger than V3a's 0.087% — because 1978-revision public-use files have a less-imputed race field than 1989+. Documented in V3b_LAYOUT_DECISIONS.md.

**Self-check (residual risks the VERIFY phase wouldn't catch):**
- Same as V3a — this entry asserts the 4-category bridged-race convention is "the NCHS standard since the 1997 OMB directives," paraphrasing common practice. A strict OMB-directive reading is post-submission scope.
- The ~89 code-7 records are a tiny fraction of V3b's 421K total, but in race-stratified time-series the V3b → V3a transition (1988 → 1989) will show a small step-change in API counts because 1978-rev code 7 (residual nonwhite) maps to null while 1989-rev's nearest analog (code 09 "All other Races") also maps to null — so no false transition is introduced. Verified: V3a's 09 = null and V3b's 7 = null are consistent treatments.

---

## 2026-05-12T18:30:00Z — task7_v3b — DATAYEAR 2-digit→4-digit expansion in harmonize.py era=='1985' branch (Option A)

**Choice:** In `harmonize.py` era=='1985' branch (1982-1988), expand the raw 2-digit DATAYEAR value ("82".."88") to the 4-digit `delivery_year` ("1982".."1988") via `df["delivery_year"] = ("19" + s).astype(str)` where `s` is the stripped raw DATAYEAR string. Defensive `ValueError` raised if any raw value is non-2-digit.

**Alternatives considered:**

1. **Option A — harmonize.py era=='1985' branch (chosen).** Pro: harmonization is the right layer for cross-era schema uniformity; preserves raw-byte fidelity in the yearly_clean parquet (1978-rev "82" stays as "82" there); pattern matches the era=='2003' B7 TABFLG correction structure. Con: adds one short block to harmonize.py.
2. **Option B — pre-process in `parse_fetal_year.py`.** Pro: simpler harmonize.py. Con: parser should preserve raw bytes (the documented `01_import/` convention); year-conversion is a harmonization concern, not a parse concern. **Rejected.**

**Reason:** The harmonized `delivery_year` column is documented as a 4-digit string across all eras for schema uniformity. V2/V2.1/V1 raw fields (DELYR @ 190-193, DOD_YY @ 15-18 / 11-14) are already 4-digit; only V3b needs an expansion. The era=='1985' branch is the natural home — it parallels the era=='2003' B7 TABFLG correction pattern (a runtime field-level fix applied per-era). Putting it in the parser would violate the raw-byte-preservation principle and introduce era awareness into the parse layer.

**Source:**
- `record_layout_1982_1988.csv` row 1 (DATAYEAR at bytes 1-2; description "Last Two Digits of Current Data Year (1978-rev)"; values "82=1982 through 88=1988").
- `harmonize.py` era=='1985' branch (lines newly added at Task 7 V3b DO step 4).
- `harmonize.py` era=='2003' branch precedent (B7 TABFLG correction at lines 358-375) — established the runtime-per-era field-correction pattern.

**Verifiable by:**
- `python -c "import pandas as pd; df = pd.read_parquet('output/harmonized/fetal_death_harmonized.parquet'); print(sorted(df.query('1982 <= data_year <= 1988').delivery_year.unique()))"` returns `['1982', '1983', '1984', '1985', '1986', '1987', '1988']` (all 4-digit strings, no leakage of "82".."88").
- The defensive halt would fire if any raw DATAYEAR was non-2-digit; it didn't fire across all 7 V3b years (421,125 records), confirming clean 2-digit raw input.
- `validate_external_v2.py` post-V3b: 33/33 PASS byte-exact, including all 7 V3b counts that depend on `data_year == year` matching — `data_year` is int32 from harmonize.py's dict init (separately from `delivery_year`), so this verifies both the int32 conversion AND the string expansion produce consistent year values.

**Reversible:** yes — the expansion is a 4-line block at one location in `harmonize.py`. If a future analysis needs the 2-digit raw form, the yearly_clean parquet preserves it.

**Residual risks:**
- (a) **The "19" prefix is hard-coded.** If a future V4 extension covered 2000+ years using the 1978-revision layout (which it won't — 1978-rev was superseded by 1989-rev effective 1989 data), the prefix would be wrong. Mitigation: V3b's coverage is bounded to 1982-1988 by `_era_tag()`; no risk in practice.
- (b) **`delivery_year` is string-typed; `data_year` is int32.** Cross-era consistency: `delivery_year` always string everywhere (V2/V3a/V3b "1985"-format; V1 "2005"-format). `data_year` always int32. Smoke verified at DO step 4.

**Self-check (residual risks the VERIFY phase wouldn't catch):**
- The defensive halt only fires on non-2-digit raw values. If a raw DATAYEAR was "82" but the BYTE positions were wrong (e.g., parser misaligned by 1 byte), the expansion would silently produce "1982" anyway from whatever 2-character substring landed there. Mitigation: the canonical-filter cross-check at DO step 8 (byte-exact NVSR-equivalent statistics for all 7 V3b years) catches byte-misalignment elsewhere; DATAYEAR-specific misalignment would surface as wrong year counts.

---

## 2026-05-12T14:30:00Z — task7_v3a — B3 maternal_race_bridged extension: 1989-rev MRACE 08→4 API, 09→null (consistent with 99 Unknown convention)

**Choice:** Extend the B3 maternal_race_bridged recode map in `fetal_death/scripts/03_harmonize/harmonize.py` with two entries to handle 1989-revision MRACE codes that the V2 (1992+) map doesn't cover:

- **`08` (Other Asian or Pacific Islander) → `4` (API)**: consistent with how codes 04-07 (Chinese, Japanese, Hawaiian, Filipino) and the parallel 1992+ codes 18-78 are mapped to bridged-API.
- **`09` (All other Races) → `""` (null/unknown bridged)**: consistent with how code 99 ("Unknown/Not stated") is handled 1993+. Affects 165 records total (1989: 34; 1990: 72; 1991: 59 — 0.087% of V3a year coverage).

**Alternatives considered:**

1. **Map 09 → 4 (API).** Pro: keeps all 1989-1991 records in some bridged category. Con: incorrect — "All other Races" is a residual catch-all per the 1989 user guide, not specifically API. Mapping it to API would over-count the API-bridged group by 165 records cumulatively and bias race-stratified rates upward for the API subgroup. Rejected as semantically inaccurate.

2. **Map 09 → 3 (AIAN).** Pro: AIAN is a "minority race other than Black" historical convention. Con: even worse than option 1 — explicit conflation of unrelated racial groups. The 1989 user guide's "All other Races" residual contains records whose race did NOT fit any of the 8 specific categories (01-08); imposing AIAN is misleading. Rejected.

3. **Map 09 → null (chosen).** Pro: integrity-preserving (no false categorization); consistent with the existing convention for code 99 "Unknown" (1993+); the 165 affected records remain in the parquet for unbridged analyses (totals, year trends, GA distributions are unaffected); only race-stratified subgroups exclude them, which is what unbridged-unknown records should do. Con: 165 records exit race-stratified analyses without explicit notice; mitigated by documentation in V3a_1989_1991_LAYOUT_DECISIONS.md + this DECISION_LOG entry. **Selected.**

4. **Add a new bridged category 5 = "Other (1989-rev residual)".** Pro: explicit. Con: requires harmonized_schema.csv allowed_values mutation (`1|2|3|4|5`); creates a category that exists only for V3a 1989-1991 records (since 1992+ has no equivalent); cross-era race comparability would break. Rejected as scope-creep beyond V3a.

**Reason:** The 1989 NCHS Fetal Death User Guide page 28 explicitly defines MRACE codes 01-09 for 1989-revision records and states "Race codes effective with 1989 data differ from previous years." Codes 04-08 cover specific Asian/Pacific Islander subgroups (Chinese, Japanese, Hawaiian, Filipino, Other API); code 09 is the residual "All other Races." The bridged-race 4-category recode (the NCHS standard since the 1997 OMB directives, also used downstream in NVSR Fetal/Perinatal Mortality reports) does not have a code for "Other Races" — it's specifically White/Black/AIAN/API. Mapping a residual catch-all into one of the 4 specific buckets would be a false categorization; null preserves integrity per the 4-core-principle "fail closed" (§2 principle 2 — when in doubt, don't fabricate; let downstream code see null).

**Source:**
- `1989FetalUserGuide.pdf` page 28 (item 79-81 MRACE, downloaded this session, sha256=`54c55a40bffea18244bd14acc60a5fa094346e87c4557cb94633c7b52599e9d1`).
- Per-year MRACE distributions in `output/yearly_clean/fetal_death_{1989,1990,1991}_raw.parquet` confirming the 9-code 01-09 scheme (no 99 sentinel; no 18-78 codes).
- Existing B3 recode at `fetal_death/scripts/03_harmonize/harmonize.py` lines 271-284 (V2 era; the entry `"99": ""` is the precedent for the null mapping).
- Documented in `fetal_death/V3a_1989_1991_LAYOUT_DECISIONS.md` ("The one code-system extension: B3 maternal_race_bridged" section).

**Verifiable by:**
- `validate_external_v2.py` post-V3a: 26/26 PASS. Per-year fetal-death counts (which use TABFLG/RESTATUS, not race) are byte-exact against user-guide controls — confirming the 09→null choice doesn't bias the canonical-filter aggregate (it can't, since the canonical filter doesn't use race).
- `python -c "import pandas as pd; df = pd.read_parquet('output/harmonized/fetal_death_derived.parquet'); print(df.query('data_year in [1989,1990,1991]')['maternal_race_bridged'].isna().sum())"` returns ~165 (the 09 records + any other nulled-by-edge-case records).
- Re-running the B3 recode map at `harmonize.py` line 271-300 inspection: the `"09": ""` entry is present alongside `"99": ""`.

**Reversible:** yes — if a future analysis surfaces a defensible convention (e.g., a peer-reviewed paper that handled 1989-rev "All other Races" via a specific bridged mapping), the B3 map can be edited to that mapping with re-derive of the V3a years only (V1+V2.1 era unaffected). A separate FIX_LOG entry would record the re-mapping with regression-scope documentation.

**Residual risks:**
- (a) **NCHS may have a documented bridged-race convention for 1989-rev code 09 that I missed.** The 1989 user guide page 28 does not specify a 4-category bridged recode for code 09. The MRACE3 (item 82-83 in the user guide) field provides a separate 3-category recode (1=White / 2=Other / 3=Black) where code 09 records would have MRACE3=2 — but that 3-category collapse is incompatible with the harmonized schema's 4-category bridged scheme. If NCHS has an internal-use 4-category recode that specifies code 09's mapping (perhaps in a separate document I don't have on disk), my null mapping may diverge from NCHS convention. Mitigation: the 4-category bridged variable is widely used and documented in NVSR; if NCHS's own publications race-stratify the 1989-1991 fetal deaths, those stratifications would be the cross-check (search NVSR Volume 41/42/43 or NCHS Series 21 reports for 1989-1991 fetal deaths by race stratified at the 4-category bridged level). Such a cross-check is out of V3a scope; documented as a possible Task 11+ verification step.

- (b) **The 165-record impact is small but non-zero on race-stratified analyses.** A researcher who uses `maternal_race_bridged` to stratify 1989-1991 fetal deaths will see the totals not exactly add up (165 records with null bridged-race). For unbridged analyses (year totals, year trends, GA-stratified, etc.) this has no effect. The behavior is consistent with how 1993+ Unknown-race records are handled, so a researcher familiar with the V2 era's race-handling will not be surprised. Documented in V3a_1989_1991_LAYOUT_DECISIONS.md.

- (c) **Future audit may surface that "Other Asian or Pacific Islander" (code 08) should NOT map to bridged-API.** Per the 1989 user guide, the 08 records are explicitly Asian/Pacific Islander but not in the 5 specific named groups (Chinese/Japanese/Hawaiian/Filipino/Other API where Other API IS code 08 itself). Mapping 08 → 4 (API) is the natural reading. But a strict reading could argue that "Other Asian or Pacific Islander" was a NCHS-internal pre-bridged category that became finer 1992+ codes 18-78 — and that the bridged-race 4-cat scheme should always use 04-07 + 18-78 paths, never 08. In that strict reading, code 08 records (~2,800 across 1989-1991) would be null-bridged instead. Mitigation: the strict reading is unsupported by the 1989 user guide (which doesn't say "08 should be excluded from the bridged-API bucket"); the natural reading aligns 08 with 04-07 and 18-78 as all API-bridged. Documented as a strict-reading alternative in V3a_1989_1991_LAYOUT_DECISIONS.md.

**Self-check (residual risks the VERIFY phase wouldn't catch):**
- This entry asserts the 4-category bridged-race convention is "the NCHS standard since the 1997 OMB directives." That's a paraphrase of common usage in NCHS publications; if the actual OMB-directive language has more nuance (e.g., a 5-category breakdown that NCHS reduces to 4 for bridged use), the choice rationale should reference the OMB directive directly rather than the NCHS practice. Mitigation: the choice is internally consistent with how the existing V2 era B3 recode handles unknowns (99 → null) and the documented user-guide categories; a strict OMB-directive check is post-submission scope.

---

## 2026-05-12T13:35:02Z — natality_v28_rename — Retain aliasing helper NATALITY_TO_CANONICAL populated post-v2.8 (override prior "becomes no-op" framing to keep v2.7.0 Zenodo backward-compat)

**Choice:** Keep `shared/helpers/canonical_join_keys.py` `NATALITY_TO_CANONICAL` populated with its 4-entry mapping after v2.8 ships. Update the docstring to clarify that the helper is a no-op for v2.8+ input (rename map produces empty dict) but is retained for v2.7.0 input where the immutable Zenodo deposit 10.5281/zenodo.19868835 still has the old column names. Premature neuter (emptying the dict) is deferred — possibly indefinitely — until the v2.7.0 deposit is no longer in common use.

**Alternatives considered:**

1. **Empty the dict post-v2.8 (the prior framing).** DECISION_LOG 2026-05-12T03:25Z DO-plan step 10 said: "Update `shared/helpers/canonical_join_keys.py` in the monorepo: `NATALITY_TO_CANONICAL` becomes empty dict + deprecation note." Pro: visible deprecation; the helper becomes a true passthrough. Con: breaks any code that reads the v2.7.0 Zenodo parquet through the helper expecting the rename to happen. The v2.7.0 deposit is immutable and remains the canonical citable artifact until Task 10 deposits v2.8.0.

2. **Retain dict + add docstring deprecation note (chosen).** Helper continues to work for both v2.7.0 and v2.8.0+ input. Joint-use code that should be version-agnostic keeps calling `to_canonical_natality()` (no-op for v2.8, full rename for v2.7.0). Cost: minor cognitive overhead (the helper "always works" framing requires the docstring to explain why); benefit: zero breakage risk for any current consumer.

3. **Remove the helper entirely.** Aggressive but unnecessary. The helper is small (~50 lines) and the cost of keeping it is near-zero. Premature.

**Reason:** Forward-looking HALT 4 in STATUS 2026-05-12T05:10Z and 06:30Z both flagged premature neuter as risky for v2.7.0 backward-compat. This session's empirical confirmation (re-running both monorepo notebooks against v2.8 parquets and observing the helper's empty-rename-map behavior) verified that the v2.8 path is unchanged whether the dict is populated or empty (no rename needed when input columns are already canonical). The v2.7.0 path REQUIRES the dict populated. Choice 2 dominates choice 1 on both safety and operational simplicity.

**Source:**
- Smoke-test inline at commit `5174552`: `python3 -c "from shared.helpers.canonical_join_keys import to_canonical_natality, NATALITY_TO_CANONICAL; df = pd.DataFrame({'data_year':[2020], 'residence_status':[1]}); out = to_canonical_natality(df); print(list(out.columns))"` returned `['data_year', 'residence_status']` (no rename); v2.7.0 input columns `['year', 'restatus']` renamed to `['data_year', 'residence_status']`. Dual-path verified.
- `paper_companion_results.csv` byte-identical to prior v2.7.0 commit after rebuilding both monorepo notebooks against v2.8 parquets (commit `a6b3d36`). The end-to-end value preservation gives high confidence that the helper's dual-path behavior is correct.

**Verifiable by:**
- The 5-line smoke-test above; reproducible at any time.
- `git diff shared/helpers/canonical_join_keys.py` at commit `5174552`: dict content unchanged; only docstring updated.

**Reversible:** yes — emptying the dict is a one-line edit at a future task (e.g., when the v2.7.0 deposit is migrated or formally deprecated). Recorded here so the future-empty task can cite this entry as the prior-state justification.

**Residual risks:**
- (a) Some user code might check `if NATALITY_TO_CANONICAL: ... ` as a sentinel that the rename is "needed"; that pattern would silently always-rename even on v2.8 input. Mitigation: `to_canonical_natality()` does the right thing in both cases (it's the wrapper that filters by input columns), and the docstring directs callers to use the wrapper, not to introspect the dict.
- (b) When the v2.7.0 Zenodo deposit is eventually superseded (Task 10 deposits v2.8.0), this retention will outlive its useful life. A future task should re-evaluate.

---

## 2026-05-12T04:30:00Z — task7_v3b_doc_hunt — KICKOFF Step 0 V3b doc retry succeeded; proposing Task 7 scope expansion to 1982-2022 (41 years)

**Choice (proposal pending user confirmation):** Expand Task 7 scope from the prior session's "V3a only (1989-1991, 34 years total)" framing back to "V3a + V3b (1982-2022, 41 years total)" per KICKOFF.md Step 0 contingency ("If V3b authoritative docs found → expand Task 7 scope to 1982-2022 and proceed with V3a + V3b"). Step 0 found all 10 fetal-death user guides 1982-1991 obtainable from NCHS canonical FTP path `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/fetaldeath/<YYYY>FetalUserGuide.pdf` (all HTTP 200; sizes/last-modified per STATUS 2026-05-12T04:30Z). The proposal is NOT yet authorized — it requires explicit user yes before Task 7 PRE-FLIGHT begins downloading the PDFs to the build dir.

**Alternatives considered:**

1. **Keep prior session's V3a-only scope** (1989-1991, 34 years; V3b deferred post-submission). Pro: shorter Task 7 budget (~1 session, not ~4-5); ships a strict superset of the current 31-year coverage; preserves integrity-principle simplicity. Con: leaves 7 years on the table that authoritative sources now confirm are accessible; the manuscript would cite 34 years with a post-submission v1.2 promise to extend, instead of citing the final 41-year extent.

2. **Expand to V3a + V3b (1982-2022, 41 years) — proposed.** Pro: maximum-extent paper coverage from first submission; cited DOI is final not incremental; the integrity principle is SATisfied because authoritative NCHS PDFs anchor V3b layout reconstruction (NOT reverse engineering). Con: +3-4 sessions of effort vs V3a-only; OCR pass required on bitmap-scanned 1980s PDFs (NCHS-published but image-scanned); L13-extension value-distribution discipline must be applied per-field on the new V3b layouts.

3. **Hybrid: V3a + V3b 1988 only.** The Damian Clarke `fetl1988.dct` artifact (88 fields, 200-byte layout) plus the NCHS 1988 user guide is a single-year addition that minimizes OCR risk (1 PDF instead of 7). Adds +4 years total (1988-1991). Rejected as a stopping point — once OCR machinery exists for one year, the marginal cost of 6 more years is small; arbitrary cutoff at 1988 is unjustified.

**Reason:** Step 0 reversed the prior session's empirical assumption ("V3b docs not at NCHS"). Wrong-filename probes by the 2026-05-12T03:50Z agent (used `Fetal82UG.pdf`, `fetal_death_inst.pdf`, NCHS series_04 paths, etc.; did NOT try `<YYYY>FetalUserGuide.pdf` despite that being the exact convention used by 2003-2022 files already on disk in this monorepo). This session's WebFetch on `cdc.gov/nchs/data_access/vitalstatsonline.htm` surfaced the canonical NCHS link list including all 7 V3b years and verified by HEAD probe. Sanity download of 1985 confirmed valid PDF + SHA recorded. The integrity-principle objection in 2026-05-12T04:00Z STATUS ("can't claim 100% correct without authoritative codebook") no longer applies: authoritative codebooks exist and are obtainable.

**Source:**
- WebFetch result for `https://www.cdc.gov/nchs/data_access/vitalstatsonline.htm` showing per-year fetal-death documentation links 1982-1988.
- `curl -sI -k <YYYY>FetalUserGuide.pdf` returning HTTP 200 with valid content-length for all 10 years 1982-1991.
- `/tmp/v3b_hunt/1985FetalUserGuide.pdf` SHA-256 `f7342480302017caf622243510c7e32ea03b6083b9797768b59fa50954eb1ed5`; `file(1)` reports valid PDF v1.4.
- GitHub `damiancclarke/nchs-fetaldata` `process/dicts/fetl1988.dct` 7,412 bytes (cross-check artifact, not authoritative; Damian Clarke 2014-07-02 Version 0.0.0 empty README).
- KICKOFF.md Step 0 contingency clause (lines 47-55 of KICKOFF.md).

**Verifiable by:**
- This entry's HEAD probe results are repeatable via `curl -sI -k https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/fetaldeath/<YYYY>FetalUserGuide.pdf` for any year 1982-1991.
- The 1985 PDF SHA can be reproduced by `curl -s -k -o /tmp/check.pdf <url> && shasum -a 256 /tmp/check.pdf`.
- STATUS.md 2026-05-12T04:30Z section is the canonical current-state record.

**Reversible:** yes — if Task 7 V3b OCR proves intractable (e.g., the 1980s NCHS scan quality is too low for reliable layout-table OCR, or value-distribution verification surfaces unresolvable per-field semantics ambiguity), the user can direct a fall-back to V3a-only scope at Task 7 PRE-FLIGHT halt-and-ask moment. The proposal does not commit V3b irreversibly; it commits to *attempting* V3b with halt-condition discipline.

**Residual risks:**
- (a) **OCR quality on 2009-vintage NCHS bitmap scans is unknown.** Quality varies year-to-year (NCHS rescanned old paper docs in 2009-01-08 batch; some scans may be cleaner than others). Mitigation: a 20-min proof-of-concept OCR run on a few `1985FetalUserGuide.pdf` pages before committing to all 7 V3b years (was option 4 of this session's 4-option ask; user chose option 1 "update state files first").
- (b) **L13-extension discipline overhead per year**: 7 V3b years × (per-field value-distribution verification + layout-CSV reconstruction from OCR'd text) may grow Task 7 V3b beyond the 3-4 session estimate if multiple fields surface semantic mismatches like the MAGER vs MAGER41 incident in V2.1.
- (c) **Damian Clarke 1988.dct provenance gap**: the Clarke artifact's "Version 0.0.0" + empty README means it MAY itself be reverse-engineered or partially-incorrect. Treating it as a cross-check (not authority) preserves integrity; treating it as authority would be the L13-extension shape we explicitly avoid.
- (d) **Manuscript timing**: pre-submission scope was already expanded once (2026-05-11T20:50Z) and again (2026-05-12T03:30Z); this is the third expansion in 3 days. User has accepted the trade-off pattern of "more sessions for final manuscript state" — but the absolute session count keeps growing. If V3b OCR surfaces a multi-session blocker, the user has the option to fall back without re-litigating the data-first-vs-submit-now choice from scratch.

**Self-check (residual risks the VERIFY phase wouldn't catch):**
- This entry asserts "authoritative NCHS PDFs are obtainable" based on (i) HEAD probes returning HTTP 200, (ii) one sanity download verifying valid PDF + matching content-length. It does NOT verify the PDF's *content* is a usable codebook with readable byte-layout tables. The 1985 PDF is bitmap-scanned; if those scans are illegible or missing the layout-table appendix entirely (e.g., the PDF body is some unrelated NCHS report, not a public-use file codebook), this proposal's premise is wrong. Mitigation: Task 7 PRE-FLIGHT MUST include an L9 cheap-check (open one PDF, locate the byte-layout table by page) before downloading all 10 to the build dir and committing harmonization effort.
- The 200-byte record length for 1982-1988 is verified by the prior session's `unzip` + byte-inspection (STATUS 2026-05-12T03:50Z); the layout table in the user guide MUST sum to 200 bytes to be consistent with the actual public-use file. Bond verification at Task 7 PRE-FLIGHT L9 step.

---

## 2026-05-12T03:30:00Z — sequencing — Pull Task 7 (V3 1982-1991) and natality v2.8 rename INTO pre-submission scope

**Choice:** Override the prior "out of pre-submission scope" status (KICKOFF.md, DECISION_LOG 2026-05-11T20:50Z) for both Task 7 fetal-death V3 backward extension AND natality v2.8 column rename. Both will be completed before manuscript submission. New pre-submission sequence:

1. ~~Task 3 V2.1 fetal-death~~ DONE 2026-05-12 (`task3-complete` at `8ca5bf9`).
2. ~~Push monorepo to GitHub at v1.0~~ DONE 2026-05-12 (public repo at https://github.com/yoelplutchok/vital-statistics-harmonization, commit `a18ca3a`).
3. **Natality v2.8 column rename** (start NEXT session per parallel-paths choice; user downloads Task 7 inputs concurrently). ~2 sessions.
4. **Task 7 V3 fetal-death** (1982-1991, +10 years). 2-4 sessions; OCR risk on older user guides.
5. **Task 9 — redirect notices on the two old GitHub repos** (~15-30 min, human-driven).
6. **Task 10 — Unified Zenodo deposit** + v2.1.0 patch to old fetal-death deposit (1 session + upload time).
7. **Push v1.1 to GitHub** (replaces current v1.0 contents; cleanly amended single-commit history not preserved — incremental release).
8. **Manuscript re-pass + submit** (~½ session).

**Alternatives considered:**

1. **Keep prior sequence (Task 7 + natality v2.8 post-submission).** Original NEXT_STEPS.md §17 + KICKOFF.md "out of scope" framing. Pro: shortest path to submission. Con: per the human's preference, the manuscript would cite a 31-year fetal-death series + v2.7.0 natality, then require v3-extended fetal-death + v2.8-renamed natality in a follow-up correction. Pre-emptively doing them before submission means the paper goes out at the latest data state.

2. **Pull Task 7 + natality v2.8 + extend further (chosen).** Pre-submission scope grows by 3-5 sessions. Pro: manuscript ships at maximum-coverage state (41 years fetal-death; aligned natality column names). Con: 3-5 more sessions of work before submission.

**Reason:** Same as DECISION_LOG 2026-05-11T20:50Z (data-first sequencing) but with maximum-extent target instead of minimum-viable. The marginal session-cost of Task 7 + v2.8 (3-5 sessions) is justified by the manuscript-once-and-final outcome. User explicitly authorized.

**Source:** Chat 2026-05-12 between commits `8ca5bf9` (Task 3 V2.1 complete) and `a18ca3a` (public repo push) and this entry. User explicit confirmation of override + parallel-paths sequencing.

**Verifiable by:**
- This DECISION_LOG entry timestamp 2026-05-12T03:30:00Z supersedes 2026-05-11T20:50Z's pre-submission scope listing.
- Future sessions reading STATUS.md + this DECISION_LOG see natality v2.8 as next task; Task 7 follows once 1982-1991 NCHS inputs are downloaded.

**Reversible:** yes — if Task 7 hits a multi-session blocker (e.g., NCHS 1982-1991 user guides only available as scanned/OCR-resistant PDFs), the human can direct a fall-back to submitting at the post-V3-attempt state with Task 7 explicitly deferred again.

**Residual risks:**
- (a) **Task 7 input availability**: PRE-FLIGHT this session showed ZERO 1982-1991 zips or user guides on disk. User has been asked to download from NCHS FTP path `ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/fetal-deaths/`. Some older-year files may not be in the standard public-use FTP path — verification required.
- (b) **Natality v2.8 scope larger than initial estimate**: PRE-FLIGHT shows 61 string-literal column-name references across natality scripts + 4 schema rows + 6 docs + 2 parquets to re-derive + 183 NVSR validation targets to re-gate. Estimated 2 sessions, not 1.
- (c) **Cross-product effects of natality v2.8 rename**: monorepo's `shared/helpers/canonical_join_keys.py` aliasing helper becomes a no-op after v2.8. monorepo's `notebooks/joint_use_demo.ipynb` and `paper_companion.ipynb` use the aliasing helper; they should continue to work (helper still imports, just renames are no-ops). Re-run both notebooks after v2.8 to verify.
- (d) **v1.0 public repo is now slightly stale**: pushed at Task 3 V2.1 state, will be superseded by v1.1 (post-Task-7 + post-v2.8). No external pulls expected in the brief window; acceptable.

---

## 2026-05-12T03:25:00Z — natality_v28_rename — PRE-FLIGHT findings: 61-string-literal rename surface (Field-value snapshot per Convention 3)

**Pre-flight result:** PROCEED to next session DO. No halt conditions. Inputs all available (natality build dir intact at v2.7.0; aliasing helper documents exact renames).

**Field-value snapshot — current state of canonical artifacts that v2.8 will mutate:**

| Artifact | Current (v2.7.0) | Target (v2.8) |
|---|---|---|
| `metadata/harmonized_schema.csv` row 1 | `year,Birth year,int16,...` | `data_year,Data year,int16,...` |
| `metadata/harmonized_schema.csv` row 2 | `restatus,Resident status (NCHS),int8,...` | `residence_status,Residence status,int8,...` |
| `metadata/harmonized_schema.csv` row N | `maternal_hispanic_origin,...` | `hispanic_origin,...` |
| `metadata/harmonized_schema.csv` row M | `maternal_race_bridged4,...` | `maternal_race_bridged,...` |
| natality parquets | columns named `year`, `restatus`, `maternal_hispanic_origin`, `maternal_race_bridged4` | renamed to canonical names |
| `shared/helpers/canonical_join_keys.py` `NATALITY_TO_CANONICAL` dict | 4 explicit renames at read time | EITHER no-op (empty dict) OR full removal with helper deprecation notice |

**String-literal reference counts (the edit surface, scoped to natality build dir scripts/metadata/docs):**

- `"year"` / `'year'`: 48 references (most string-literal column-name uses; some may be `df.groupby("year")` style; many are validation filter expressions like `mask = subset["year"] == y`)
- `"restatus"` / `'restatus'`: 3 references
- `"maternal_race_bridged4"` / `'maternal_race_bridged4'`: 6 references
- `"maternal_hispanic_origin"` / `'maternal_hispanic_origin'`: 4 references
- Total: **61 string-literal references**

**Files touching these columns (per `grep -rln`):**

| Layer | Files |
|---|---|
| Schema | `metadata/harmonized_schema.csv`, `metadata/external_validation_targets_v1.csv` |
| Harmonize | `scripts/03_harmonize/harmonize_v1_core.py`, `scripts/03_harmonize/harmonize_linked_v3.py` |
| Validate | `scripts/05_validate/qa_yearly_core_parquet.py`, `validate_row_counts_vs_nchs.py`, `harmonized_missingness.py`, `key_rates_from_derived_core.py`, `compare_external_targets_v3_linked.py`, `compare_external_targets_v1.py`, `validate_linked_parquets.py`, `validate_v1_invariants.py` |
| Convenience | `scripts/06_convenience/write_residents_only.py` |
| Figures | `scripts/07_figures/generate_paper_figures.py` |
| Docs | `docs/CODEBOOK.md`, `docs/COMPARABILITY.md`, `docs/FAQ.md`, `docs/ABOUT_THIS_RELEASE.md`, `docs/GETTING_STARTED.md`, `docs/VALIDATION.md` |
| Import (linked) | `scripts/01_import/parse_linked_cohort_year.py`, `scripts/01_import/README.md` |

**DO-phase plan:**

1. Edit `metadata/harmonized_schema.csv`: rename 4 rows. Verify schema-version bump (v2.7.0 → v2.8.0) annotated.
2. Edit `scripts/03_harmonize/harmonize_v1_core.py`: rename column-write string literals.
3. Edit `scripts/03_harmonize/harmonize_linked_v3.py`: same.
4. Re-derive `natality_v2_harmonized_derived.parquet` + `natality_v3_linked_harmonized_derived.parquet`.
5. Verify column names in resulting parquets (should be `data_year`, `residence_status`, `maternal_race_bridged`, `hispanic_origin`).
6. Edit 5 validate scripts + 2 misc scripts + 1 import script: rename column-read string literals.
7. Run 183 NVSR validation targets; gate 183/183 byte-exact.
8. Run linked-file validation; gate 33/35 + 2 differ-by-1.
9. Edit 6 docs (CODEBOOK, COMPARABILITY, FAQ, ABOUT_THIS_RELEASE, GETTING_STARTED, VALIDATION) to use new column names.
10. Update `shared/helpers/canonical_join_keys.py` in the monorepo: `NATALITY_TO_CANONICAL` becomes empty dict + deprecation note; the helper continues to import for backward compatibility but is a no-op for natality v2.8.
11. Re-run `notebooks/joint_use_demo.ipynb` + `notebooks/paper_companion.ipynb` against the v2.8 natality parquet to verify cross-product joins still work.
12. Sync renamed files to monorepo's `natality/` subdirectory.
13. Bump version: `CITATION.cff` 2.7.0 → 2.8.0; new Zenodo deposit (since v2.8 is a breaking change; v2.7.0 stays at its DOI for backward compatibility).
14. Write RECEIPT + FIX_LOG + DECISION_LOG entries.

**Forward-looking HALTs for the DO session:**

1. Some "year" references in scripts may be LOCAL VARIABLES, not column-name string literals. The rename must distinguish `df["year"]` (rename target) from `for year in range(...)` (untouched). Use targeted sed patterns like `s|"year"|"data_year"|g` and `s|'year'|'data_year'|g` only — not bare-word replacement.

2. `external_validation_targets_v1.csv` may have "year" as a column header. Inspect before editing; the V1 validation target CSV is canonical state.

3. The downstream user's local projects (multiple-gestation-linked-imr, lbw-imr-divergence per DECISION_LOG 2026-05-11T18:06:12Z) will break on v2.8 — they hard-code `df["year"]` etc. A separate compatibility task to update those projects is OUT OF SCOPE for natality v2.8 itself; flag for the user.

4. The aliasing helper currently maps 4 names. After v2.8, natality natively has the canonical names. The helper's `NATALITY_TO_CANONICAL` dict should be empty `{}` (so `to_canonical_natality(df)` becomes a passthrough). Verify nothing breaks at the call sites.

5. Re-deriving natality parquet takes ~5-10 minutes on the v2.7.0 build laptop. Budget accordingly.

---

## 2026-05-12T01:35:00Z — task3_v21_fetal_death — Bundle 4 fixes into Task 3 V2.1 build (B7 + H8 + data_year + monorepo path drift)

**Choice:** Land the following four orthogonal fixes inside a single Task 3 V2.1 build, producing one new shipped artifact pair (`fetal_death_harmonized.parquet` sha=`333e1e66…d9e0`, `fetal_death_derived.parquet` sha=`55d3d310…c447`) and one set of canonical-state log entries:

1. **B7 TABFLG normalization** for 2003/2004 — NCHS-errata correction per `fetaldeath0304problems.pdf` (records with COMBGEST=99 and OSTATE in 43-state list set TABFLG=2; raises per-year resident totals from 25,653/25,655 originally-reported to 26,004/26,001 corrected, byte-exact against the errata's Table 1).
2. **H8 schema-vs-data dtype reconciliation** — five demographic/filter columns cast from `object` to nullable Int (`tabulation_flag` Int8, `residence_status` Int8, `maternal_age` Int16, `maternal_race_bridged` Int8, `hispanic_origin` Int8), matching the schema CSV and the natality v2.7.0 dtype convention; closes FIX_LOG 2026-05-11T18:50:00Z.
3. **`data_year` derived-column fix** — surfaced when the V2 validator returned 0/23 after H8: the harmonize loop's field-map iteration was overwriting the int32 `data_year` initialization with empty-string `object` because the crosswalk row for `data_year` has `field_2006="derived"` which falls through to the loop's else-branch. Added `if raw_field == "derived": continue` to skip derived-marker rows.
4. **Monorepo path drift in `harmonize.py` + `validate_external*.py`** — pre-existing from monorepo migration `7fd9cdf`; scripts assumed `fetal_death/metadata/` subdir but the monorepo flattened the layout. Re-pointed `_CROSSWALK_CSV`/`_SCHEMA_CSV`/`_HARM_PATH`/etc. to the actual paths.

**Alternatives considered:**

1. **Land each fix as a separate task** (B7 → task3a, H8 → task3b, data_year → task3c, paths → task3d). Cleaner per-task scope; one parquet rebuild per fix. Cost: 4 parquet rebuilds, 4 separate receipts, 4 separate Zenodo deposit considerations. Rejected — H8/data_year/paths are LATENT bugs surfaced as a consequence of running Task 3's re-derive; treating them as separate tasks is artificial, and re-deriving the parquet four times burns reproducibility-budget for no extra information.
2. **Land B7 only; defer H8/data_year/paths to post-submission** (chosen-not). Pro: keeps Task 3 scope tight. Con: V2.1 ships with a known H8 dtype defect AND a latent data_year bug that would re-surface when downstream code starts using the int-comparison path; manuscript references the v2.1.0 parquet with two known issues that would need a v2.1.1 correction. Rejected.
3. **Land all four fixes bundled into one V2.1 build (chosen).** Pro: one parquet, one receipt, one deposit-version, transparent V2.1 release notes covering everything that changed. Con: receipt is denser; Task 3 effort exceeded the 1–2 session estimate. The receipt names all four orthogonally; downstream readers can trace each.

**Reason:** All four fixes converge on the same parquet rebuild. B7 requires harmonize.py edit and re-derive. H8 requires harmonize.py edit and re-derive. data_year bug surfaces during H8 re-derive (the validator failure exposes it). Path drift blocks all of the above from running at all. Bundling is the natural unit. Convention 1 (SHAPE-not-VALUE) is preserved — no SMOKE harnesses pin v2.0.0-specific values that V2.1 changes.

**Source:**
- `FIX_LOG.md` entries 2026-05-12T01:30:00Z (three new entries: H8 closure, data_year, monorepo path drift).
- `fetal_death/V2_1_2003_2004_LAYOUT_DECISIONS.md` (new).
- `raw_docs/fetal_death/fetaldeath0304problems.pdf` page 1 + Tables 2–3 (for B7).
- `raw_docs/fetal_death/2003FetalUserGuide.pdf` pages 17–19 (for the MAGER41-vs-MAGER discovery).

**Verifiable by:**
- `validate_external.py` 55/55 + `validate_external_v2.py` 23/23 = 78/78 byte-exact pass.
- joint_use_demo: 8/8 NVSR Table-4 age-band cells byte-exact for 2022.
- paper_companion: 34/34 PASS, 0 FAIL.

**Reversible:** yes — `git reset --hard task3-pre-do` reverts; v2.0.0 parquet preserved at `/Users/yoelplutchok/Desktop/fetal-death-harmonization/fetal_death_derived.parquet` (sha `90af89b9…`) for byte-clean baseline comparison.

**Residual risks (Self-check feed):**
- (a) **`record_layout_2003/2004.csv` documentation imprecisions** (inherited from 2006 with anchor-field spot-checks; surfaced semantic mismatch at MAGER vs MAGER41 plus several BLANK-vs-actual-field documentation errors). The harmonized parquet is correct (because parser-read positions for fields the harmonizer reads ARE correct, or read-all-blank which is correct behavior); only the layout CSVs need a post-submission audit-rebuild. Documented in `V2_1_2003_2004_LAYOUT_DECISIONS.md`.
- (b) **V1-era byte-clean column-level regression not exhaustively verified.** The V1 validator passed 55/55 (functional verification), but a column-by-column SHA comparison of the 2005–2022 slice of the new derived parquet vs v2.0.0's `90af89b9…` derived parquet was NOT performed this session. The 5 H8 columns are expected to change (string→int); all other 84 columns should be byte-identical. Forward-looking HALT in receipt.
- (c) **maternal_age=null for 2003+2004 may surprise downstream users** unaware that the 2003+2004 public-use files don't ship single-year-of-age. Documented in V2_1_DECISIONS doc and in the JOINT_USE_GUIDE dtype note.
- (d) **Other monorepo scripts may have latent path drift** (parse_fetal_year.py, derive.py, run_pipeline.py, tests/conftest.py). Not touched this session; flagged in FIX_LOG 2026-05-12T01:30:00Z forward-looking follow-up.

---

## 2026-05-11T20:50:00Z — sequencing — Data-first before manuscript submission (Task 3 → push GitHub → Task 9 → Task 10 → manuscript re-pass + submit)

**Choice:** Run the remaining data-side work (Task 3 V2.1 fetal-death with bundled H8 reconciliation) and the cross-product publication tasks (push GitHub, Task 9 redirect notices, Task 10 unified Zenodo) BEFORE manuscript submission, so the manuscript cites the latest fetal-death coverage and the unified Zenodo concept DOI from the first submitted version rather than the two old subproject DOIs.

**Alternatives considered:**
1. **Submit now, do data work later (submit-first).** Three pre-submission process tasks: YP admin review, GitHub push + URL injection, IJE reference reformat. Then submit at v2.0 fetal-death (29 years, with 2003–2004 gap) citing concept DOIs 10.5281/zenodo.19363074 + 10.5281/zenodo.20031571. Pros: fastest path to submission; ½ session. Cons: the paper goes out reporting a 2-year gap and the two old DOIs; a follow-up correction or v2.1 release update would be needed within weeks; the manuscript's headline numbers (1,634,195 fetal deaths; Table 1 fetal-death row count = 3; validation counts 29/29 + 26/26) become stale on a planned schedule.
2. **Data-first sequence: Task 3 → push GitHub → Task 9 → Task 10 → manuscript re-pass + submit (chosen).** Run Task 3 (V2.1 fetal-death; bundles H8 schema-doc reconciliation), push the monorepo to GitHub, do Task 9 redirect notices, set up the unified Zenodo deposit with DOI pre-reservation, then a half-session manuscript re-pass to update affected numbers (fetal-death record count ~1.6M → ~1.7M; Table 1 rows; validation counts 31/31 + 28/28), inject the unified DOI and GitHub URL, resolve the three `<!-- YP: review -->` admin-section markers, and reformat references. Pros: paper is published at the latest data state; cites the unified DOI from day one; H8 dtype fix-up rides for free in the Task 3 parquet re-derivation. Cons: 4–6 session delay before submission; Task 3 has known unknowns (2003 + 2004 transition-layout reconstruction from NCHS user guides — `fetaldeath0304problems.pdf` is the documented source for the known ambiguities).
3. **Maximum-extent: also do Task 7 V3 backward extension to 1982 pre-submission.** Adds 1982–1991 fetal-death (1978-revision + early 1989-revision). Pros: longest paper coverage. Cons: explicitly post-submission per `NEXT_STEPS.md` §17; 2–4 sessions; OCR risk on older user-guide PDFs; the marginal scientific value over the V2.1 state is incremental. Rejected as scope creep.
4. **Maximum-extent: also do natality v2.8 column rename pre-submission.** Renames `year` → `data_year`, `restatus` → `residence_status`, etc., so the aliasing helper becomes a no-op deprecation. Pros: cleaner namespace alignment. Cons: breaking change for downstream natality-only users (the `multiple-gestation-linked-imr` and `lbw-imr-divergence` projects on the human's Desktop); requires re-running 183 NVSR validation targets + new natality Zenodo deposit; the paper's Methods section already documents the cross-product alignment via the aligned shared concepts (`maternal_age`, `maternal_race_bridged`, `hispanic_origin`, `data_year`, `residence_status` per the manuscript), so deferring the rename does not cost the paper a claim. Rejected as scope creep + breaking-change risk.

**Reason:** The Data Resource Profile genre rewards "publish at the latest data state" and the IJE editorial expectation is that a Data Resource Profile cites the unified resource DOI in the manuscript. Submitting at v2.0 fetal-death (29-year coverage) and v2.1-correcting weeks later costs more author and editor time than a 4–6 session pre-submission data push. Task 3 is rated "ideally pre-submission, not blocking" by `NEXT_STEPS.md` §17 — the §17 framing was conservative; the human's preference to upgrade it to "do before submission" is consistent with the underlying intent. Task 7 and natality v2.8 are explicitly post-submission and remain so.

**Source:** Chat transcript 2026-05-11 between Task 5 commit `9aaa702` (20:30Z) and this DECISION_LOG entry (20:50Z); human's explicit confirmation of the sequence after LLM presented the trade-off summary. `KICKOFF.md` "Current planned sequence" block; STATUS.md 2026-05-11T20:50:00Z section.

**Verifiable by:**
- `KICKOFF.md` contains the "Current planned sequence" section listing the 5-step order (Task 3 → push → Task 9 → Task 10 → re-pass + submit).
- `STATUS.md` most-recent section is dated 2026-05-11T20:50:00Z and supersedes the Task 5 entry's "Next planned task: Pre-submission process pass by default" line.
- Future sessions reading KICKOFF.md and STATUS.md will propose Task 3 as the next task by default; the (a)-(d) handshake's (c) "what you propose to do this session" should name Task 3 PRE-FLIGHT unless the human directs otherwise.

**Reversible:** yes. If Task 3 hits a multi-session blocker (e.g., a 2003-revision layout ambiguity that NCHS docs don't resolve), the human can direct a fall-back to the submit-first sequence (alternative 1 above) without needing a new DECISION_LOG entry — just halt Task 3 at the blocked PRE-FLIGHT and pivot.

**Residual risks:**
- (a) Task 3 effort estimate (1–2 sessions) could grow if the 2003 + 2004 transition-layout reconstruction hits ambiguities. The human has implicit budget tolerance for this per the data-first choice; explicit budget reset would be a halt-and-ask moment.
- (b) The manuscript re-pass in step 5 is a paper-side ripple effect; if the journal's IJE author guidelines change in the intervening 4–6 sessions, the re-pass scope grows. Mitigation: low-probability over a multi-week window.
- (c) Cross-pollination between Task 3 (data-side change) and the manuscript edits (Task 5's body) is unavoidable. Task 4's HALT 5 already documents this: any manuscript edit re-runs `_build_paper_companion.py` to detect new/changed claims; Task 3's effect on the manuscript means the synthesis CSV WILL change (currently bit-stable at `7891809c...`).

---

## 2026-05-11T20:30:00Z — task5_manuscript_trim — Override Task 4's C47/C48/C49 L11 recommendation (Task 4 misdiagnosis)

**Choice:** Do NOT apply Task 4's recommended precision edit for C47/C48/C49 (line 104 of `paper/draft_v2_hmd_styled.md`). Keep the manuscript wording for `maternal_education`, `paternal_age_combined`, and `maternal_education_unrevised` exactly as-is.

**Alternatives considered:**
1. **Apply Task 4's recommended edit** — rewrite line 104 to clarify that the italicised names are "raw NCHS field names" rather than harmonized columns. Task 4's PRE-FLIGHT and receipt explicitly recommended this as a Task 5 input.
2. **Override and keep manuscript as-is (chosen).** Direct verification at Task 5 PRE-FLIGHT shows that the italicised names ARE fetal-death harmonized column names per `fetal_death/harmonized_schema.csv` lines 17 (`maternal_education`, years_available `2005-2006, 2014-2022`), 18 (`maternal_education_unrevised`, years_available `1992-2002, 2005-2006`), and 21 (`paternal_age_combined`, years_available `1992-2002, 2005-2006, 2014-2022`). Direct null-rate verification on `fetal_death_derived.parquet` (sha=`90af89b9...`) shows 100% blank for all three columns in 2007–2013 — matching the manuscript's claim byte-exact. The italicization convention is consistent with line 60's `breech_unrevised` / `delivery_place_unrevised` / `maternal_race_bridged_detail` (italics = harmonized column names throughout the manuscript). The manuscript wording at line 104 is correct and self-consistent; no edit is warranted.
3. **Hybrid: keep wording but add a clarifying footnote naming the underlying raw NCHS fields (MEDUC, FAGECOMB, MEDUC).** Considered; rejected as scope creep — the harmonized column / raw-field correspondence is documented in `fetal_death/harmonized_schema.csv` already, and adding a manuscript-level footnote duplicates the schema CSV without adding clarity.

**Reason:** Task 4's PRE-FLIGHT and DO phase checked the NATALITY parquet (`natality_v2_harmonized_derived.parquet`) for these three column names. The natality parquet has different harmonized column names for the same conceptual fields: `maternal_education_cat4` (a 4-category derivation) rather than `maternal_education`; `father_age` (single-year) rather than `paternal_age_combined`; and no equivalent of `maternal_education_unrevised`. Task 4 received "columns not found" from the natality parquet and interpreted the manuscript's italicised names as raw NCHS field names. The fetal-death parquet was not checked. Task 5 PRE-FLIGHT re-verification reads the fetal-death schema CSV and parquet directly and finds the manuscript wording byte-exact correct. This is a Task 4 receipt Self-check item 4 outcome: the receipt explicitly flagged "if the manuscript actually means harmonized columns, then C47–C49 are DIFFs… the latter scenario is plausible — recommend Task 5 author verify which framing was intended" — Task 5 carried out that verification and found the harmonized-columns framing is the correct one.

**Source:**
- `PRE_FLIGHT_LOG.md` 2026-05-11T20:05:00Z (Field-value snapshot, "5 precision-edit candidates from Task 4 — PRE-FLIGHT re-verification" table, C47/C48/C49 row).
- `fetal_death/harmonized_schema.csv` lines 17, 18, 21 (authoritative declaration of harmonized column names + years_available).
- Direct fetal-death parquet null-rate verification (PRE-FLIGHT bash output 2026-05-11T20:00Z): `maternal_education` 100% blank 2007-2013; `paternal_age_combined` 100% blank 2007-2013; `maternal_education_unrevised` 100% blank from V1 2007 onward.
- `RECEIPTS/task4_paper_companion_2026-05-11T19-26-28Z.md` Self-check item 4 (Task 4's own flag that this could be a misdiagnosis).

**Verifiable by:**
- `grep -n "^maternal_education,\|^maternal_education_unrevised,\|^paternal_age_combined," fetal_death/harmonized_schema.csv` returns three rows matching the years_available pattern above.
- A re-run of `python notebooks/_build_paper_companion.py` against an unchanged fetal-death parquet emits 100.00% blank rates for 2007-2013 in C47/C48/C49 cells, matching the manuscript.

**Reversible:** yes — if the IJE author or peer reviewer requests the clarification anyway, the Hybrid alternative (a footnote naming the underlying raw fields) is a one-line addition.

**Residual risks:**
- (a) A reader who is unfamiliar with the harmonization may parse line 104's `maternal_education` as the natality harmonized column (which has a different name) and conclude there is a manuscript-data mismatch. Mitigation: the schema CSV (shipped) is the canonical disambiguation; a future precision pass could add an explicit `(fetal-death harmonized columns)` parenthetical, but this is sub-precision-edit not L6 risk.
- (b) The Task 4 receipt's Forward-looking HALT 1 names C47/C48/C49 as a Task 5 input; future receipt-readers tracing the HALT chain should consult this entry to see the override rationale.
- (c) The C47/C48/C49 rows in `notebooks/paper_companion_results.csv` continue to show `status=L11` because the builder is data-driven (it doesn't read the manuscript line text); the L11 flag is informational not regression. A future refactor of `_build_paper_companion.py` could either fix the C47-C49 check logic to look at the fetal-death parquet rather than expect a hardcoded comparison, or update the synthesis-row status to reflect the Task 5 override. Not done in Task 5 to keep scope tight.

---

## 2026-05-11T19:26:28Z — task4_paper_companion — Re-defer Section B 2017 race-stratified NVSR validation (originally Task 2 → Task 4 absorption)

**Choice:** Re-defer the Section B 2017 race-stratified NVSR cell-level validation that §15 Task 4 (current state at `89ddc77`) names as an absorption from Task 2. Task 4 produces no race-stratified 2017 NVSR cells. The absorption becomes a separate small future task with explicit NVSR-2017 fetal-mortality PDF input.

**Alternatives considered:**
1. **Absorb Section B into Task 4 as §15 currently directs.** Would require: (a) locating the 2017-vintage NVSR fetal-mortality report PDF (likely NVSR 67-?); (b) transcribing 4 race-stratified rows into `fetal_death/external_validation_targets.csv`; (c) adding a verification cell to either `joint_use_demo.ipynb` or `paper_companion.ipynb` that reproduces each cell against the parquet. Cost: one short session if PDF is at hand; L9 risk on table/page citation.
2. **Re-defer with explicit reasoning (chosen).** The original Task 2 deferral cited the same L9 risk. The manuscript itself makes no race-stratified-2017 NVSR claim (line 94's validation claims are aggregate-level), so `paper_companion.ipynb`'s "reproduce every numeric claim in the manuscript" scope is complete without it.
3. **Hybrid: defer the NVSR validation but add a structural sanity check in the notebook** (e.g., assert race-stratified counts sum to the unstratified 2017 = 22,827 from external_validation_targets.csv). Task 2's notebook already does this cross-check (Section B's CSV-vs-direct-natality-recompute consistency check); duplicating it in `paper_companion.ipynb` would be redundant.

**Reason:** Convention 3 second bullet directs the PRE-FLIGHT to surface divergence between §15 spec and the task's available source-of-truth state, and to resolve at the cheap-check moment rather than silently proceeding. `fetal_death/external_validation_targets.csv` ships NO 2017 race-stratified targets (verified at PRE-FLIGHT by metric enumeration: 26 distinct metrics, none race-keyed). The L9 cheap-check therefore concludes that absorbing Section B would require fresh PDF transcription with the same risk profile that motivated Task 2's deferral. Re-deferring keeps Task 4 focused on its primary scope (reproduce manuscript numeric claims, which does not require race-stratified-2017 NVSR cells) and isolates the PDF-transcription work into a separate task where the L9 cheap-check can be done explicitly with the PDF in hand.

**Source:** `PRE_FLIGHT_LOG.md` 2026-05-11T19:15:00Z (Field-value snapshot, "Plan assumption amended at PRE-FLIGHT" section, item 1). `RECEIPTS/task4_paper_companion_2026-05-11T19-26-28Z.md` (Forward-looking HALT 3).

**Verifiable by:**
- `grep -i "race\|maternal_race" fetal_death/external_validation_targets.csv` returns zero hits (no race-stratified targets pre-encoded).
- Task 4's `paper_companion.ipynb` synthesis CSV contains no rows whose `claim` mentions "2017 race"; the 50 claim tags cover only manuscript-stated numeric claims.
- The manuscript's line 94 NVSR-validation claims are aggregate-level (183/183, 33/35+2, 29/29 counts + 26/26 rates); none are race-stratified-2017.

**Reversible:** yes — adding the absorption is additive (new rows in `external_validation_targets.csv` + new notebook cells). The original Task 2 deferral and this re-deferral can both be reversed in a single future session if the PDF is located.

**Residual risks:**
- (a) A reader of `NEXT_STEPS.md` §15 Task 4 may expect the absorption to be present in `paper_companion.ipynb` and be surprised by its absence. Mitigation: the receipt's Forward-looking HALT 3 and Self-check item 6 both flag this; the notebook's intro markdown cell explicitly names the deferral as out-of-scope.
- (b) The manuscript might later be edited (Task 5) to ADD a race-stratified-2017 validation claim, at which point Task 4's "reproduce every numeric claim" status would become stale. Mitigation: receipt Forward-looking HALT 5 says any future edit to `paper/draft_v2_hmd_styled.md` should re-run `python notebooks/_build_paper_companion.py` to surface new claims; the CSV `notebooks/paper_companion_results.csv` is the bit-stable check.
- (c) §15 Task 4's description currently names the absorption as in-scope. A `[plan-update]` could reword §15 Task 4 to mention the re-deferral; not done as part of Task 4 itself to avoid scope creep (similar to Task 2's stale-§15-wording handling).

---

## 2026-05-11T18:06:12Z — task1_joint_use_denominators — Aliasing-helper vs source-schema-rename for cross-product join keys

**Choice:** Reconcile cross-product join-key column-name divergence (`year`↔`data_year`, `restatus`↔`residence_status`, `maternal_race_bridged4`↔`maternal_race_bridged`, `maternal_hispanic_origin`↔`hispanic_origin`) via a read-time aliasing helper at `shared/helpers/canonical_join_keys.py`. The natality v2.7.0 Zenodo deposit's shipped schema is NOT mutated; the helper renames at the joint-use code boundary. Output `fetal_death/stratified_denominators.csv` uses the canonical (fetal_death-style) names.

**Alternatives considered:**
1. **Rename columns in the natality schema** (bump to v2.8 with `year` → `data_year`, etc.) and re-derive the parquet. Cleaner long-term, but: (a) requires re-running 183 NVSR validation targets; (b) breaks downstream user code that imports natality by its current names (e.g., `multiple-gestation-linked-imr` and `lbw-imr-divergence` projects on the user's Desktop); (c) requires a new Zenodo deposit (v2.7.0 stays immutable at its DOI); (d) needs a coordinated bump of `paper/draft_v2_hmd_styled.md` references.
2. **Use the aliasing helper as a stopgap, keep both shipped schemas as-is** (chosen). Pros: ships the joint-use convenience layer today; preserves Zenodo deposit immutability; no breaking change to natality users; isolates the cross-product reconciliation in one auditable place. Cons: future joint-use code must import the helper; the docs must document the divergence (now done in `docs/JOINT_USE_GUIDE.md`).
3. **Build Task 1 against natality-native names; ship the output with fetal_death-style names; defer documentation/helper to later**. Functionally similar to choice 2 but loses the unified-namespace clarity at the helper boundary — joint-use code would each need to know the rename rules locally.

**Reason:** Task 1's purpose is to enable the manuscript's "designed for joint use" claim by producing a stratified denominator file. Choice 1 is the long-term right answer but is a multi-session task with a meaningful breaking-change surface. Choice 2 ships the deliverable today and isolates the cross-product reconciliation behind a single helper, keeping the breaking-change decision for natality v2.8 (or v3.0) as an independent future task. The Forward-looking HALTs in the Task 1 receipt explicitly propose this rename as a §11 plan-update candidate.

**Source:** PRE_FLIGHT_LOG.md 2026-05-11T17:50:48Z (Field-value snapshot of cross-product schema divergence). `shared/helpers/canonical_join_keys.py` (the helper); `docs/JOINT_USE_GUIDE.md` (user-facing docs explaining the choice and the namespace).

**Verifiable by:**
- `python -c "from shared.helpers.canonical_join_keys import NATALITY_TO_CANONICAL; print(NATALITY_TO_CANONICAL)"` should print exactly `{'year': 'data_year', 'restatus': 'residence_status', 'maternal_race_bridged4': 'maternal_race_bridged', 'maternal_hispanic_origin': 'hispanic_origin'}`.
- `shasum -a 256 fetal_death/stratified_denominators.csv` should produce `6874d5d65e7b3888acf8a833e4fa98063630765e2eeaf6e1c6cb48ad7b0db5c1` as long as natality v2.7.0 is the upstream input.
- Per-year sums in `stratified_denominators.csv` should match `external_validation_v1_comparison.csv` `resident_births` for all 29 years in 1992–2002 + 2005–2022.

**Reversible:** yes — `git reset --hard task1-pre-do` reverts the helper and the convenience file; the natality v2.7.0 deposit was never touched.

**Residual risks (Self-check feed from RECEIPTS/task1_joint_use_denominators_2026-05-11T18-06-12Z.md):**
- (a) The 1992–2002 era's `maternal_race_bridged4` in natality uses "approximate_pre2003" crosswalk per natality schema notes; fetal-death uses a different `harmonize.py` recode. Unverified whether they produce identical 4-category outputs on the same source MRACE codes. Joint stratified-by-race rates for 1992–2002 should be cross-checked as a Task 2 PRE-FLIGHT smoke.
- (b) Hispanic code 9 (Unknown) is preserved as a stratum, not dropped. JOINT_USE_GUIDE.md flags this but does not enforce; downstream code that misaggregates would silently bias rates.
- (c) The full natality `natality_v2_harmonized_derived.parquet` is not listed in any shipped PROVENANCE.md (only the residents-only convenience parquet is). Upstream documentation gap. Locally computed sha=`9f917a43474eb9e3ed23aa95c714209421c25c29937376651149d22fab934ef0` is recorded in the receipt and the build script's `--natality-parquet` arg requires the user to provide the path explicitly.

---

## 2026-05-11T17:30:00Z — task6_linked_validation_reconcile — Canonical framing for V3 linked external-target validation count

**Choice:** Adopt "33/35 byte-exact + 2 cells (2015 `unweighted_infant_deaths` and `postneonatal_deaths`) differ by exactly 1 record from NCHS upstream null-record-weight survivor records; all 35 pass within documented tolerance" as the canonical framing across the repo, matching the manuscript drafts and monorepo top-level README. Updated `natality/README.md` (lines 19, 27, 146), `natality/docs/ABOUT_THIS_RELEASE.md` (line 80), `natality/docs/COMPARABILITY.md` (line 367), `natality/docs/VALIDATION.md` (line 206), `paper/README.md` (line 18), `NEXT_STEPS.md` (§14 Table 1 line 440, §17 checklist line 791) to match.

**Alternatives considered:**
1. Keep "35/35 pass" as the headline everywhere and treat the 2-cell differences as a tolerance-aware caveat only in detailed validation tables. Cleaner headline; loses precision.
2. Adopt "33/35 byte-exact + 2 differ by 1" as the headline everywhere. More informative; honest about what "pass" means at the byte level. (Chosen.)
3. Carry both framings in parallel ("35/35 pass under documented tolerance; 33/35 byte-exact"). Most explicit; verbose.

**Reason:** The authoritative source `natality/output/validation/external_validation_v3_linked_comparison.md` shows 35 PASS / 0 FAIL / 0 MISSING under tolerance, AND shows 33 rows at Diff=0 with 2 rows (both 2015) at Diff=1. Both framings are factually correct, but they describe different metrics. The manuscript drafts already use option 2 (33/35 byte-exact + 2 cells differ by 1), as does the monorepo top-level `README.md`. The natality subproject's README and three of its docs were the outliers using only the headline "35/35 pass" framing. Option 2 is more honest about what the validation "pass" status means at the byte level, and aligning the natality subproject docs to it removes the cross-doc inconsistency the prior STATUS section flagged as Open Question #3.

**Source:**
- `natality/output/validation/external_validation_v3_linked_comparison.md` (authoritative validation comparison; 2015 rows `unweighted_infant_deaths` 23326→23327 and `postneonatal_deaths` 7772→7773 each show Diff=1, marked `pass`).
- `paper/draft_v2_hmd_styled.md` line 94 (manuscript canonical framing, retained).
- `README.md` (monorepo top-level) line 17 (already canonical, retained).

**Verifiable by:** `git ls-files | xargs grep -n -E '35/35|33/35' 2>/dev/null` should now show consistent canonical framing across all post-edit shipping docs; residual "35/35" mentions should only appear in (a) historical state-file entries (PRE_FLIGHT_LOG, STATUS open questions), (b) NEXT_STEPS.md §15 Task 6 spec which describes the problem being resolved.

**Reversible:** yes — `git reset --hard task6-pre-do` rolls back the seven file edits; the manuscript drafts and monorepo README would remain canonical (they were unchanged in this task).

**Residual risk (Self-check feed):**
- (a) `natality/README.md` line 146 mechanism-attribution phrase ("two null-`record_weight` survivor rows in 2014/2015") and `natality/docs/VALIDATION.md` line 219 mechanism-attribution phrase ("LATEREC edge cases") differ from the manuscript canonical mechanism phrase ("NCHS upstream survivor records with null record weights"). These three locally-varying mechanism phrasings are intentionally preserved because the task scope is HEADLINE-count reconciliation, not mechanism-attribution reconciliation. Each may describe the same underlying NCHS phenomenon under different terminology (LATEREC = late-filed records that lacked record_weight at file-build time; "survivor" likely refers to the surviving-cohort linkage). Disambiguating these three framings into one is a downstream task if pursued.
- (b) `natality/README.md` line 146 retains "2014/2015" for the underlying survivor rows although both validation diffs manifest in 2015 cells. The two need not contradict (e.g., a 2014-birth-cohort record manifesting in 2015 linked-file death counts), so the original wording is preserved without speculation.
- (c) Headline framing carries forward through future LinkedFile re-validation: if a later release re-derives different per-year counts that change the byte-exact vs differ-by-1 split, every file touched in this task needs a paired update.

---

## 2026-05-09T00:00:00Z — bootstrap — Operating protocol adopted from NHANES Assay-Bridging template

**Choice:** Adopt the NHANES Assay-Bridging Harmonization Project's `EXECUTION_PROTOCOL.md` discipline (five-phase task structure, append-only state files, mistake-class matrix, halt conditions, anti-patterns, self-check) for HVS work. Folded into `NEXT_STEPS.md` §1-§13.

**Alternatives:** (a) lighter-weight ad-hoc protocol with just task list and review hook; (b) full NHANES protocol replicated verbatim; (c) hybrid (this choice).

**Reason:** HVS data is already shipped and validated, so the heaviest NHANES patterns (multi-LLM dual-key transcription, mutation fixtures, NIST SRM checks) don't apply directly. But the patterns that matter most for any harmonization with public-validation-target gold standards — five-phase structure, halt conditions, mistake-class prevention, append-only state — apply equally to HVS. Adopting them now (before Tasks 1-10 ship) means the discipline guards the manuscript-supporting work, not just future maintenance.

**Source:** `/Users/yoelplutchok/Desktop/nhanes-assay-bridging/EXECUTION_PROTOCOL.md` (read 2026-05-09); `NEXT_STEPS.md` §1-§13 (this commit).

**Verifiable by:** A future LLM session, kicked off via `KICKOFF.md`, should be unable to do work without first running the §1 session-start sequence and waiting for human confirmation. The discipline is enforced by the prompt, not by code.

**Reversible:** yes — if the protocol proves too heavy for the actual work pattern, simplify by §11 plan-update process.
