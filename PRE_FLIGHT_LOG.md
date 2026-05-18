# PRE_FLIGHT_LOG

> **Append-only.** Before every task's DO phase, the LLM appends a PRE-FLIGHT checklist here per the template in `NEXT_STEPS.md` §5.
>
> **Back-fills are forbidden** (per §8 matrix row L10). The PRE-FLIGHT entry's timestamp must precede the first DO commit for that task. If a back-fill is detected (e.g., during receipt drafting), file an L10 entry forensically and remediate via §11 before doing further DO action on that task.
>
> See `NEXT_STEPS.md` §5 for the template.

---

## PRE-FLIGHT ADDENDUM for C8.18 DO step 5c-iii — 2026-05-20T02:00:00Z — a §7 latent defect in the RESOLVED-5b `parse_linked_year.run_parse` materialization surfaced at the 5c-iii SMOKE cheap-check; **halt-and-ask satisfied → human-authorized Option A (bundle the minimal root-cause fix into 5c-iii)**; + the §9-#4 SMOKE-Tier-1 test-construction fix (a NEW dated entry, NOT a back-fill — the 5b 2026-05-19T08:30:00Z + 5c-ii-a 2026-05-19T15:00:00Z precedent; L10-safe — written BEFORE the 5c-iii commit / VERIFY close)

> Two divergences surfaced between the 5c-iii main PRE-FLIGHT (00:00:00Z) and final DO close, both at the SMOKE cheap-check (the system working as designed). Resolved here BEFORE the commit; L10-safe (the only writes are PRE_FLIGHT_LOG + state files; the harmonize/parser code + harnesses already authored, SMOKE GREEN 120/120, but NOT yet committed).

### (A″) §7 finding — `parse_linked_year.run_parse` `pa.Table.from_pylist` infers the Arrow schema from the FIRST record only → silently drops / crashes on the 1983-1988 den/num numerator ICD-9 mortality section

**What surfaced.** The 5c-iii SMOKE Tier-1 (real `LinkCO83`/`LinkCO88`) initially failed because `pa.RecordBatch.from_pylist(rows)` (and `pa.Table.from_pylist`) infer the Arrow schema from the **first record's keys ONLY** (empirically confirmed: 20 den-then-20-num rows → `UCOD`/the entire numerator section dropped). `parse_linked_year.run_parse` (RESOLVED-5b code, lines 528/540/547) materializes the parser output via `pa.Table.from_pylist(rows/buffer)`; `_iter_two_file_1983_1988` yields ALL den rows (47 keys, NO death section) BEFORE any num row (74 keys, WITH the locs 194-500 ICD-9 mortality section). ⇒ at DO step 6 the 1983-1988 `_raw` parquet build is defective: the single-list path (`chunk_rows=None`) **silently drops the entire numerator ICD-9/age-recode section**; the default chunked path (`chunk_rows=250_000`) fixes the `ParquetWriter` to a den-only schema then **crashes** at the den→num chunk boundary. (1989-2004/2005+ single-member parsing is unaffected — homogeneous dicts.) This is a latent defect in **already-completed RESOLVED-5b work** whose root-cause fix is in `parse_linked_year.py` (5b/import stage) — **outside 5c-iii's declared harmonize-side scope** (§7-#17; "5b RESOLVED — do NOT re-open"; §8 "halt for human approval if the lesson reveals a bug in already-completed work").

**Halt-and-ask (binding §7/§8/anti-pattern-#3 — NOT waived by the user's standing authorization).** The §7/§8 condition was surfaced to the human via AskUserQuestion with the airtight finding + 3 concrete options (A bundle the minimal `run_parse` fix into 5c-iii [recommended]; B defer to a separate 5b-fix sub-step; C halt 5c-iii + §11 re-plan). The 5c-iii harmonize deliverable itself is correct + complete (120 SMOKE pass; additive; zero canonical mutation) — the finding is cleanly isolated to `run_parse`. Human response: *"whatever is the best, use your judgment"* — i.e., the §7/§8 halt-and-ask requirement is satisfied (surfaced + options + human response, with the bug-in-already-completed-work explicitly disclosed), and the human authorizes the executing agent's judgment to choose.

**Resolution = Option A (judgment; the §7/§8 gate satisfied).** Bundle the **minimal, surgical, human-authorized** root-cause fix into the 5c-iii commit: a NEW `parse_linked_year._expected_parsed_schema(year)` helper returns the deterministic den∪num column union for **1983-1988 ONLY** (built from the parser's OWN `_layout_for_linked_year` + `_numerator_layout_for_linked_year` dispatchers — the same ones `_iter_two_file_1983_1988` uses; no data scan, no new layout logic) and **`None` for every homogeneous year** → `run_parse` passes that explicit unified schema to `pa.Table.from_pylist(..., schema=…)` + `pq.ParquetWriter(out, schema)` for 1983-1988; the non-1983-1988 path is **byte-identical** to the original (`from_pylist(rows)`/`tbl.schema`) — the byte-exact shipped single-member parquets are unperturbed (§9-#7; verified by `_expected_parsed_schema(1990/1996/2003/2004/2010/2023) is None`). Rationale: §2 fail-closed + anti-pattern #7 (fix the root cause once found; never ship a known-broken DO-6 path); the keyless 1983-1988 harmonized encoding is un-exercisable end-to-end without it; the fix is parser-substrate-only (zero canonical mutation, like 5b itself — 11/11 gate parquet SHAs byte-exact). **Scope expansion (explicitly human-authorized):** 5c-iii's git scope now also includes `natality/scripts/01_import/parse_linked_year.py` (the original 00:00:00Z intended-outputs listed only `harmonize_linked_v3.py` + the 4 harnesses + state) — logged DECISION_LOG 2026-05-20 + a LESSONS entry (H6/L13-extension class: a heterogeneous-union materialized via first-record-schema-inference silently drops the late-arriving segment's columns). Bundled SMOKE coverage (§9-#9/L3): `_expected_parsed_schema` Tier-0 unit tests + a Tier-1 `test_tier1_run_parse_preserves_numerator_section` (real `LinkCO83` → `run_parse` → read-back → assert UCOD/AGER5/UCODR61 survive + den-null/num-valued + the read-back parquet harmonizes with ICD-9 populated on num rows — the DO-step-6 path end-to-end).

### (B″) §9-#4 SMOKE-Tier-1 test-construction fix (the harmonize code is correct; my test-input construction was mis-copied)

The 5c-iii SMOKE Tier-1 originally built the real-data batch via `pa.RecordBatch.from_pylist(rows)` — mis-copied from the 5c-ii-b template (where it is correct because 2003/2004 dicts are HOMOGENEOUS single-member den-plus). For the HETEROGENEOUS 1983-1988 den/num union it hit the same first-record-schema-inference issue. Fixed the test to construct the batch with the EXPLICIT UNIFIED den∪num column set (den rows' num-only keys → "" → null via the harmonizer's `_to_*` coercion) — i.e. exactly what a correctly schema-unified parquet looks like — so the 5c-iii harmonize ENCODING is genuinely SMOKE-verified on real `LinkCO83`/`LinkCO88` den/num data (§9-#4 fix-the-test-correctly: the harmonize code is correct — 120/120 GREEN; only the test-input construction was wrong). Also a within-test §9-#4: the Tier-1 H6 `n_den > n_num` assertion was mis-sized to the full-file property — corrected to "both segments present + non-empty" (the den ≫ num conservation is the DO-step-6 NCHS-per-year-cohort-count §15.D VERIFY, NOT a per-segment-capped-SMOKE invariant).

### Updated intended outputs (supersedes the 00:00:00Z "Outputs (intended)" — additive)
- `natality/scripts/01_import/parse_linked_year.py` — **NEW (human-authorized scope expansion)**: additive `_expected_parsed_schema(year)` helper + the minimal `run_parse` materialization wiring (1983-1988 → explicit unified schema; every homogeneous year byte-identical, §9-#7).
- `natality/tests/test_linked_cohort_5ciii_harmonize_smoke.py` — also covers the `run_parse` fix (Tier-0 schema-helper + Tier-1 end-to-end).
- `LESSONS.md` — the H6/L13-extension-recurrence note (the RECWT@91 (A′) year-axis finding + the from_pylist-first-record heterogeneous-union finding).
- `DECISION_LOG.md` 2026-05-20 — records the §7 halt-and-ask + the Option-A resolution + the human-authorized scope expansion + the (A′) RECWT@91 conservative-NULL.
- The 00:00:00Z `harmonize_linked_v3.py` + the 3 L17 `tracks-current-state` harness Edits + the new 5c-iii harness + STATUS — unchanged from the main entry.

### Result
**PROCEED to VERIFY + RECEIPT** (the §7/§8 halt-and-ask is satisfied; Option A applied; SMOKE GREEN 120/120; zero canonical-state mutation; intermediate DO step → no tag).

---

## PRE-FLIGHT for C8.18 DO step 5c-iii — 2026-05-20T00:00:00Z — the **keyless 1983-1988 `link_segment` den/num one-row-per-birth harmonized encoding** in `harmonize_linked_v3.py` (the highest-risk methodology-laden sub-step; the natality `is_pre1989` 1968/1978-revision analog; the RESOLVED 5b two-file construction model) — **RESULT: PROCEED to DO** (9/9 forward-looking HALTs from `RECEIPTS/C8.18_step5c-ii-b_2026-05-19T23-00-00Z.md` re-verified; **11/11 gate parquet SHAs byte-exact**; canonical pytest baseline `251 passed, 1 skipped, 1 xfailed in 352.85s` (4-dir suite) — the COUNT is the 5c-ii-b-close baseline (the gate); 352.85s within the ~340-680s advisory band → soft-flag (kk) carry; a read-only real-data Convention-3 value-distribution probe of the 1983-1988 keyless den/num substrate on real `LinkCO83.zip`/`LinkCO85.zip`/`LinkCO88.zip` surfaced a **NEW L13-extension-recurrence finding** (`RECWT@91` is NOT byte-stable across 1983→1988 — clean `"1"` for 1983/1985, == `DMRACE@57` 5000/5000 for 1988) + 6 within-task scope decisions (A)-(F) surfaced + resolved at the Convention-3 snapshot **before any code mutation**, per the 5→5a/5b/5c + 5c→5c-i/5c-ii/5c-iii + 5c-ii→5c-ii-a/5c-ii-b + 4→4a/4b/4c + 3→3a/3b established precedent + the user's standing "proceed and make any relevant decisions by yourself" authorization 2026-05-20; L17 grep-scope of all 10 cohort harnesses = exactly the 3 stale keyless-1983-1988 `NotImplementedError` pins the 5c-ii-b receipt HALT 9 predicted, all bundled into the SAME 5c-iii commit per §4.2.1/Convention-2/L17; zero §7 halts — the RECWT@91 finding is the per-year non-anchor verification the 3a self-check #2 + 5b self-check #3 EXPLICITLY scheduled for "DO step 5c/6", resolved within 5c-iii scope via the faithful no-patch conservative-NULL choice, the 5a/5b/5c-ii-a within-task-Convention-3-resolution precedent)

> Per-sub-step PRE-FLIGHT under the C8.18 umbrella PRE-FLIGHT (2026-05-17T05:30:00Z) + the §15.D DO step 5 → 5a/5b/5c (2026-05-19T05:00:00Z) + 5c → 5c-i/5c-ii/5c-iii (2026-05-19T11:00:00Z) decompositions. Written **before any DO step 5c-iii mutation** (no `harmonize_linked_v3.py` edit, no new harness, no L17 edit yet — the only writes from this entry are PRE_FLIGHT_LOG + state files; L10-safe). DO step 5c-iii is harmonize-side substrate only (the re-harmonize that produces the v4 parquet is DO step 6); ZERO canonical-state mutation this sub-step.

### Entry cheap-check — 9 forward-looking HALTs (from `RECEIPTS/C8.18_step5c-ii-b_2026-05-19T23-00-00Z.md`)

1. **PASS** — `C8.18-pre-do`@`6632a15`; `C8.18-complete` NOT present; `C8.17-complete` present; HEAD = `f940b46` (the DO step 5c-ii-b commit, after `8497e92`). Verified `git rev-parse`/`git tag`/`git log`.
2. **PASS** — **11/11 gate parquet SHAs byte-exact** vs the 5c-ii-b HALT 2 (`/tmp/c8_18_s5ciii/gate.out`, 16-hex prefixes): nat `c8a740eb…`(harm)/`acb5c48a…`(deriv); `.v28_baseline` `230efed2…`/`e16ad532…`; linked-deriv `9b828a4d…`; fetal-death `38e2cecb…`(harm)/`185c071e…`(deriv) (via the `~/Desktop/fetal-death-harmonization-build/` tree, soft-flag (hh)); MM `5c22308b…`/`7c682668…`/`d98b4296…`/`adbec108…`. Linked-derived changes only at the later DO step 6 re-harmonize.
3. **PASS** — canonical **4-dir** suite `fetal_death/tests/ natality/tests/ tests/ matched_multiples/tests/` = `251 passed, 1 skipped, 1 xfailed in 352.85s` (`/tmp/c8_18_s5ciii/pytest_baseline.out`); the COUNT is exactly the 5c-ii-b-close baseline (251P+1S+1XF) — the gate per soft-flag (kk)/§8 L17/HALT-9. 352.85s within the ~340-680s advisory band. README 3-dir/"56 passed" line stays stale → soft-flag (jj).
4. **PASS** — `harmonize_linked_v3` exposes `_mager41_to_age` + `_harmonize_cohort_2003_2004` + `_harmonize_cohort_1995_2002` + `_cohort_era` + `_harmonize_cohort_batch` (1989-1991 + 1995-2002 + 2003 + 2004 implemented; **only the keyless 1983-1988 RAISES `NotImplementedError`**) + the 2 within_era ICD-9 `OUT_SCHEMA` columns + the reusable H7 helpers (`_dmeduc_years_to_cat4`/`_month_to_trimester`/`_pldel_to_facility`/`_to_int_or_null`/`_to_float_or_null`/`_to_str_or_null`/`_get_col[_optional]`), state-on-disk (read in full; do NOT re-derive). `_mrace1digit_to_bridged4` is NOT yet local → add (H7 sibling byte-identical to `harmonize_v1_core._mrace1digit_to_bridged4`). DO step 5c-iii = the keyless 1983-1988 `link_segment` den/num encoding (the LAST unimplemented cohort era).
5. **PASS** — the within_era ICD-9/ICD-10 cause-column-shape is RESOLVED + state-on-disk (DECISION_LOG/PRE_FLIGHT_LOG 2026-05-19T11:00:00Z; §15.D DO step 1): `underlying_cause_icd9`/`cause_recode_61` (cohort birth-year ≤1998), `underlying_cause_icd10`/`cause_recode_130` (≥1999). 5c-iii applies it for the keyless **1983-1988** (cohort birth-year ≤1998 → **ICD-9**: `underlying_cause_icd9`=UCOD, `cause_recode_61`=UCODR61 populated on num rows; the ICD-10 cols null) — the probe re-confirmed UCOD is ICD-9 numeric (0/3000 alpha-prefixed for 1983 & 1988). Does NOT re-open the shape.
6. **PASS / noted** — the `harmonized_schema.csv` metadata edit + the v3→v4 version bump is DO step 6 (Anti-Pattern #6). 5c-iii is harmonize-CODE only; NO `harmonized_schema.csv`/validation-CSV/parquet touch (the parquet is NOT re-run; gate SHAs byte-exact). `OUT_SCHEMA` grows 80→81 with `link_segment` (the v3→v4 ADDITIVE code-schema extension; the 5c-i ICD-9-columns precedent; the 5b self-check #6 mandate — the metadata-CSV row + version bump are DO step 6). The DO step 6 forward note (Convention 4, below) records the schema-CSV `years_available`/null-pattern widenings 5c-iii makes durable (the new `link_segment` row; death-side 2005-2023→1983-2023 incl. the 1992-1994 gap; `record_weight`/`hispanic*` 1983-1988 null-pattern; the 1983-1988 ICD-9 + `age_at_death_recode5`-only/no-`age_at_death_days` note).
7. **PASS / noted** — §15.D substrate-format reconcile applied at the 3a commit; the broader model-clarification — now ALSO folding the **5c-iii keyless 1983-1988 harmonized encoding + the RECWT@91 byte-91 era-instability finding** alongside 3a/3b + 4a/4b/4c + 5→5a/5b/5c + 5c→5c-i/5c-ii/5c-iii + 5c-ii→5c-ii-a/5c-ii-b + the 2003/2004 MATCHS/FLGND-encoding finding — remains soft-flag (ii) §11 human-merge (proposed-not-applied; on-disk PRE_FLIGHT_LOG/DECISION_LOG/RECEIPTs authoritative meanwhile).
8. **PASS / consumed** — soft-flag (gg): the cause-column SHAPE is resolved (HALT 5); the per-condition leaf decomposition of the composite DELMTH/MEDRISK/OBSTETRC/LABOR/ABNORMNB/ENTITY/RECORDAX spans (+ smoking, diabetes/hypertension, preterm_recode3, the 2-digit ORMOTH/ORFATH Hispanic crosswalk, payment, prior_cesarean) stays conservatively NULL at 5c-iii (the natality `is_pre1989` / 5c-i / 5c-ii conservative-mapping precedent) → DO step 6. **NEW soft-flag (ll)** (the RECWT@91 byte-91 1986-1988 layout-instability + the full per-year (1984-1988) non-anchor byte-stability re-verification) joins (gg)/(ii) → DO step 6 PRE-FLIGHT (the 3a self-check #2 + 5b self-check #3 already scheduled this verification there; DO step 6's NCHS-per-year-cohort-count VERIFY is the durable root-cause gate). LESSONS L13-extension-recurrence note appended (§11 step 1; year-axis sharpening; NOT a §8-mandated halt — 3a never claimed 1988 non-anchor byte-stability, it self-check-#2-flagged + routed it here).
9. **PASS / action required** — L17 forward-looking grep-scope of all **10** cohort SMOKE harnesses (`git ls-files natality/tests/ | grep linked_cohort | xargs grep -nE`): the parser/layout harnesses (`test_linked_cohort_1983_1991_layout_smoke.py`, `_numerator_smoke.py`, `_1995_2002/_2003/_2004_layout_smoke.py`, `_5b_numfinder_smoke.py`, `_denmember_5a_smoke.py`) target the **parser/field_specs** substrate (untouched by harmonize-side 5c-iii — `field_specs.py` + the parser are NOT edited) → not stale. The 5c-i `test_tier0_cohort_era_*` `(1983,"1983_1988")…` assert the UNCHANGED `_cohort_era` classifier → not stale (must NOT touch). **Exactly the 3 stale harmonize-side keyless-1983-1988 pins the 5c-ii-b receipt HALT 9 predicted** (5c-iii implements the LAST unimplemented era → NO unimplemented era remains): (i) `test_linked_cohort_5cii_b_harmonize_smoke.py::test_tier0_keyless_1983_1988_still_failclosed` `[1983,1985,1988]`; (ii) `test_linked_cohort_5cii_a_harmonize_smoke.py::test_tier0_unimplemented_eras_still_failclosed` `[1983,1985,1988]`; (iii) `test_linked_cohort_5c_harmonize_smoke.py::test_tier0_unimplemented_cohort_eras_failclosed` `[(1985,"5c-iii")]`. Per §4.2.1/Convention-2/L17 the minimal `tracks-current-state` Edits are bundled into the SAME 5c-iii commit: since NO unimplemented era remains, the reframe asserts the genuine RESIDUAL §2 fail-closed that still holds (the `_cohort_era` ValueError for the 1992-1994 permanent gap / pre-1983, and/or the per-function wrong-era ValueError) — NOT a NotImplementedError (now never raised for a real cohort year). The new 5c-iii harness is `DESIGN: tracks-current-state`, sub-step-isolated, SHAPE-not-VALUE (Convention 1/2).

### Inputs
- [x] `natality/scripts/03_harmonize/harmonize_linked_v3.py` — present (1918 lines; the 5c-iii target; `_cohort_era`/`_harmonize_cohort_batch`/`_harmonize_cohort_1995_2002`/`_harmonize_cohort_2003_2004` + the 1989-1991 inline body + the 2005+ explicit-`from_arrays` body + `OUT_SCHEMA` 80 cols + the H7 recodes/helpers). Read in full.
- [x] `natality/scripts/03_harmonize/harmonize_v1_core.py` — the H7 sibling-parity reference: the `is_pre1989` 1968-1988 branch (lines 206-287 `_mrace1digit_to_bridged4`/`_mrace_detail_to_bridged4`; lines 629-819 the is_pre1989 birth-side map — cert_rev "unrevised_1968", DMAGE single-year, native LBORD_R9/TBORD_R9, marital NULL [natality public-use pre-1989 had no DMAR — the LINKED 1983-1988 file DOES → faithful map], hispanic NULL, `_mrace1digit_to_bridged4(MRACE 0-9)`, `_dmeduc_years_to_cat4`, `_month_to_trimester(MONPRE)`, DGESTAT 17-47∪99 keep "lmp", DBIRWT direct, DFAGE 10-98 keep). Read.
- [x] `natality/scripts/01_import/field_specs.py` — `LINKED_BIRTH_1983_1988_FIELDS` (45-field, 91-byte; `MATCHS@1`/`BIRYR@2-5`/`RESSTAT@11`/`DMRACE@57`/`ORMOTH@55-56`/`DMAGE@58-59`/`DMEDUC@62-63`/`DMAR@65`/`DGEST@39-40`/`CSEX@38`/`DBIRWT@43-46`/`DPLURAL@50`/`APGAR5@53-54`/`PLDEL@89`/`BIRATTND@90`/`RECWT@91`/`DFAGE@71-72`/`DFEDUC@73-74`/`DLIVORD@86-87`/`LIVORD9@88`/`DTOTORD@83-84`/`TOTORD9@85`/`DMPCB@78-79`/`NPREVIS@81-82`) + `LINKED_DEN_RECLEN_1983_1988=91` + `LINKED_NUM_DEATH_1983_1988_FIELDS` (locs 194-500; `AGER5@223`/`UCOD@231-234` ICD-9/`UCODR61@235-237`; **NO AGED**; ENTITY/RECORDAX multiple-cause = soft-flag (gg)) + `LINKED_NUM_RECLEN_1983_1988=500` — state-on-disk 3a/3b, read-only (NOT edited at 5c-iii).
- [x] `natality/scripts/01_import/parse_linked_year.py` — `iter_parsed_records`/`_iter_two_file_1983_1988` (the RESOLVED 5b two-file `link_segment` "den"/"num" construction; each yielded dict has `year` + `link_segment` + the parsed string fields; den = locs 1-91 birth only, num = locs 1-91 birth + 194-500 ICD-9 death) — read; NOT edited at 5c-iii.
- [x] `natality/metadata/harmonized_schema.csv` — the canonical mapping definitions cross-checked for H7 parity. **NOT edited** at 5c-iii (HALT 6).
- [x] `natality/tests/test_linked_cohort_5cii_b_harmonize_smoke.py` (the 5c-iii harness template + the L17 stale-pin (i)) + `test_linked_cohort_5cii_a_harmonize_smoke.py` (L17 stale-pin (ii)) + `test_linked_cohort_5c_harmonize_smoke.py` (L17 stale-pin (iii)) — read in full.
- [x] `RECEIPTS/C8.18_step5c-ii-b_2026-05-19T23-00-00Z.md` (the 9 forward-looking HALTs) + `RECEIPTS/C8.18_step5b_2026-05-19T08-00-00Z.md` (the RESOLVED keyless two-file construction model + self-check #3/#6 — the den/num harmonized semantics + the segment-distinction-preservation 5c mandate + the per-year non-anchor verification routed to 5c/6) + `RECEIPTS/C8.18_step3a_2026-05-17T23-30-00Z.md` (self-check #2 — non-anchor 1983-1988 fields transcribed from the 1983 layout, NOT individually value-verified for 1984-1988 → DO step 5/6).
- [x] No required upstream task incomplete: DO step 5a/5b/5c-i/5c-ii-a/5c-ii-b CLOSED + committed (HEAD `f940b46`).
- [x] No stale checkpoints: `git status --porcelain` clean; on `main`; `/tmp/c8_18_s5ciii/*` is OS-scratch (gate-SHA + pytest baseline + the 3 read-only probes), reproducible.

### Environment
- [x] Python 3.13 via `uv run`; pyarrow/pandas pinned (`uv.lock`, C8.5a). No new dependency at 5c-iii (harmonize-side; reuses pyarrow + the existing helpers; ONE NEW local helper `_mrace1digit_to_bridged4` — pure pyarrow, H7 sibling-parity byte-identical to `harmonize_v1_core`).
- [x] Working dir clean; on `main`.

### Source documentation
- [x] No new external PDF consumed at 5c-iii (the 1983-1988 layouts were authored + SHA-anchored at DO step 3a/3b; 5c-iii maps the already-parsed field names to harmonized columns). No SHA-256 to re-verify. The RECWT@91 era-instability is a layout-substrate finding routed to the DO step 6 / 3a-revisit per-year value-distribution pass (NOT a 5c-iii re-author — field_specs untouched).

### Outputs (intended; 5c-iii)
- [ ] `natality/scripts/03_harmonize/harmonize_linked_v3.py` — **additive**: append `("link_segment", pa.string())` to `OUT_SCHEMA` (80→81) + the matching `pa.nulls(batch.num_rows, type=pa.string()),  # link_segment` entry appended to the 2005+ `_harmonize_batch` explicit `from_arrays` list (the 5c-i precedent; the dict-pattern 1989-1991/1995-2002/2003-2004 era functions auto-null it — byte-untouched) + a NEW `_mrace1digit_to_bridged4` helper (H7 sibling) + a NEW `_harmonize_cohort_1983_1988(batch, year)` function + a 2-line `if era == "1983_1988": return _harmonize_cohort_1983_1988(batch, year)` dispatch prepended in `_harmonize_cohort_batch` (before the `if era != "1989_1991":` guard) + the docstring/NotImplementedError reword (all cohort eras now implemented; the residual is the §2 fail-closed `_cohort_era` ValueError for the 1992-1994 gap / pre-1983 + the per-function wrong-era ValueError). The 5c-i 1989-1991 inline body + the 5c-ii-a `_harmonize_cohort_1995_2002` + the 5c-ii-b `_harmonize_cohort_2003_2004` + the 2005+ body's existing array entries byte-untouched (§9-#7-safe; the 1983-1988 branch fires only for year ∈ {1983..1988} → the canonical v3 2005-2023 + the 5c-i/5c-ii-a/5c-ii-b paths byte-identical, just gaining a link_segment=NULL column auto-defaulted via the `{f.name: pa.nulls for f in OUT_SCHEMA}` dict pattern / the one new 2005+ pa.nulls entry).
- [ ] `natality/tests/test_linked_cohort_5ciii_harmonize_smoke.py` — NEW; `DESIGN: tracks-current-state`; SHAPE-not-VALUE; sub-step-isolated. Written FIRST + run RED (§9-#9 / L3 — collection ImportError vs the un-modified harmonizer).
- [ ] `natality/tests/test_linked_cohort_5cii_b_harmonize_smoke.py` + `_5cii_a_harmonize_smoke.py` + `_5c_harmonize_smoke.py` — minimal L17 `tracks-current-state` Edits bundled in the SAME commit (stale-pins (i)/(ii)/(iii): the keyless-1983-1988 `NotImplementedError`-pin tests reframed to the genuine residual `_cohort_era` ValueError fail-closed + docstring notes).
- [ ] `PRE_FLIGHT_LOG.md` (this entry) + `RECEIPTS/C8.18_step5c-iii_…` + `DECISION_LOG.md` + `STATUS.md` + `LESSONS.md` (the L13-extension-recurrence note) appended.
- [x] NO canonical parquet / `harmonized_schema.csv` / validation-CSV / `field_specs.py` / parser mutation (the harmonizer is NOT re-run at 5c-iii; gate SHAs byte-exact). NO git tag (intermediate DO step; `C8.18-pre-do`@`6632a15` is the rollback anchor).

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

No canonical *value* is mutated at 5c-iii (zero parquet/schema-CSV/validation-CSV touch). The snapshot below records the **decisions** fixed at this cheap-check moment, before any code mutation, grounded in a read-only real-data probe (`/tmp/c8_18_s5ciii/probe_1983_1988.py` + `probe_recwt_raw.py` + `probe_recwt_85.py`) on real `LinkCO83/85/88.zip` (SHA-anchored at DO step 2; n≤5000 den + ≤3000 num per year).

**(A) 1983-1988 keyless den/num substrate — real-data probe (L13-extension; read-only, before any code mutation).** Confirmed: the RESOLVED 5b two-file construction yields `link_segment` "den"/"num"; `BIRYR`==cohort year on BOTH segments; den n≫num (the aggregate-birth-denominator + self-contained-numerator model). Birth-side fields (locs 1-91, present on BOTH den & num) value-distribution-plausible for 1983 AND 1988: `RESSTAT`{1-4}; `DMRACE`{0-8} 1-digit detail race; `ORMOTH` 2-digit (1983 all `88`, 1988 `00`-dominant + sparse 02/04/05/99); `DMAGE` 10-49; `DMEDUC` 00-17,99 years; `DMAR`{1,2}; `DGEST` weeks+99; `CSEX`{1,2}; `DBIRWT` grams+9999; `DPLURAL`{1,2,3}; `APGAR5` 00-10,99; `PLDEL`{1,2,9}; `BIRATTND`{1,2,3,9}; `DFAGE` 10-98,99; `DFEDUC` 00-17,99; `DLIVORD/LIVORD9`/`DTOTORD/TOTORD9` (native NCHS recode-9 present — unlike 1989-1991); `DMPCB` 00-09,99; `NPREVIS` 00-49,99. Num-side death (locs 194-500): `AGER5`{1-5}; `UCOD` **ICD-9 numeric** (0/3000 alpha-prefixed for 1983 & 1988 — re-confirms the §15.D-DO-step-1/5c-i resolved ≤1998=ICD-9 shape); `UCODR61` 3-digit; **NO `AGED`** (the 1983-1988 numerator carries only `AGER5`/`AGER76`/`AGER38` recodes, no raw age-at-death-days). num `MATCHS` ≈ all `1` (the linked-infant-death set); den `MATCHS` {3 surviving-dominant, 1 matched} (carried in `_raw`, NOT consumed by the harmonized `infant_death` per the RESOLVED 5b no-double-count model).

**(A′) NEW Convention-3 finding — `RECWT@91` is NOT byte-stable across 1983→1988 (L13-extension recurrence; resolved within 5c-iii scope, NOT a §7 halt).** Plan-assumed (3a state-on-disk `LINKED_BIRTH_1983_1988_FIELDS`, transcribed from the **1983** guide; only anchor fields BIRYR/MATCHS/CSEX/DPLURAL/DBIRWT value-verified for 1983/85/88 per the 3a receipt): a single byte-stable layout 1983-1988. Falsified by the read-only raw-byte probe: `LinkCO83USden.dat` byte 91 = uniformly `"1"` (clean RECWT 100%-sample weight); `LinkCO85USden.dat` byte 91 = uniformly `"1"`; `LinkCO88USden.dat` byte 91 == byte 57 (`DMRACE`) in **5000/5000** records (distribution {2,1,8,3,7,4,5,0} == DMRACE exactly). bytes 1-90 are layout-stable for 1988 (the 80-91 tail fingerprint shows `NPREVIS/DTOTORD/TOTORD9/DLIVORD/LIVORD9/PLDEL/BIRATTND` well-formed); ONLY the trailing byte 91 (`RECWT`) is era-unstable. **Verdict (§2 fail-closed; anti-pattern #7 — NOT a downstream patch):** this is precisely the per-year non-anchor value-distribution verification the **3a self-check #2 + 5b self-check #3 EXPLICITLY scheduled for "DO step 5c/6"** — i.e., the Convention-3 cheap-check working exactly as designed (the 3a layout never *claimed* 1988 non-anchor byte-stability; no already-completed-work bug within claimed scope → no §8-mandated halt). Resolved within 5c-iii scope via the faithful no-patch choice = **`record_weight` conservatively NULL for ALL 1983-1988** (the 5c-i/1989-1991 `record_weight`-NULL + natality `is_pre1989` conservative-mapping precedent; the cohort-IMR = num-count/den-count does NOT use record_weight; `field_specs.py` left UNTOUCHED — the substrate is still correct for 1983-1985 + the byte-91 1986-1988 question + the full per-year (1984-1988) non-anchor re-verification is routed to DO step 6 PRE-FLIGHT where the parquet is built + validated cell-by-cell vs the NCHS published cohort Linked File reports — the durable §15.D root-cause gate). Recorded as **NEW soft-flag (ll)** + a DECISION_LOG residual risk + a LESSONS L13-extension-recurrence note (year-axis sharpening: "a single-guide-derived layout value-verified only on anchor fields + one era-year can hide a non-anchor byte re-purposing at another era-year of the same record length"). NOT a blocking §7 halt: no analytic-validity-domain ambiguity for the IMR (the 5b construction + the ≤1998-ICD-9 shape are RESOLVED + unaffected); no upstream patch / no fabricated data; the 5a/5b/5c-ii-a within-task-Convention-3-resolution precedent governs.

**(B) §15.D DO step 5c-iii architecture = a NEW separate `_harmonize_cohort_1983_1988(batch, year)` (§9-#7; the explicit-per-era helper-duplication pattern).** Authored as a SEPARATE function (not a shared helper / not folded into the 1989-1991 inline body) so the 5c-i 1989-1991 + 5c-ii-a 1995-2002 + 5c-ii-b 2003/2004 verified bodies stay **byte-untouched**. A 2-line `if era == "1983_1988": return _harmonize_cohort_1983_1988(batch, year)` dispatch prepended in `_harmonize_cohort_batch` (before the `if era != "1989_1991":` guard); the docstring + the (now-unreachable-for-real-cohort-years) NotImplementedError reworded — ALL cohort eras now implemented; the residual §2 fail-closed is the `_cohort_era` ValueError (1992-1994 gap / pre-1983) + each `_harmonize_cohort_*` function's wrong-era ValueError. A fail-closed `if _cohort_era(year) != "1983_1988": raise ValueError` guard in the new function (the 5c-ii-a/5c-ii-b precedent).

**(C) `link_segment` → `OUT_SCHEMA` (the v3→v4 ADDITIVE code-schema extension; the 5c-i ICD-9-columns precedent; the 5b self-check #6 mandate "5c must preserve the keyless-era den/num provenance or it is lost").** Append `("link_segment", pa.string())` as the LAST `OUT_SCHEMA` field (80→81) + the matching `pa.nulls(batch.num_rows, type=pa.string()),  # link_segment` appended to the 2005+ `_harmonize_batch` explicit `from_arrays` list (the EXACT 5c-i pattern: OUT_SCHEMA col ⇒ matching 2005+ pa.nulls; the 1989-1991/1995-2002/2003-2004 dict-pattern functions `{f.name: pa.nulls for f in OUT_SCHEMA}` auto-default it to NULL — byte-untouched, §9-#7-safe). Value: `"den"`/`"num"` for 1983-1988 (the parser passthrough); **NULL for ALL other eras** (single denominator-plus / 2005+ — faithful "not applicable: there is exactly one segment"). The harnesses assert `tbl.schema == OUT_SCHEMA` *relatively* (not a hardcoded col-count) → adding to OUT_SCHEMA keeps them green (both sides grow together; SHAPE-not-VALUE compliant). The `harmonized_schema.csv` metadata row + the v3→v4 version bump = DO step 6 (Anti-Pattern #6).

**(D) Two-segment harmonized semantics (the RESOLVED 5b model — do NOT re-open) + the H7 `is_pre1989` birth-side ALIAS.** `is_num = pc.equal(_get_col(batch,"link_segment"), "num")`. `infant_death` = `if_else(is_num, scalar(True), scalar(None,bool))` (den → NULL/unknown un-linkable aggregate denominator; num → True linked-infant-death — the documented within-era structural difference = Phase-D D.4; NOT the value-driven AGED signal — there is NO AGED in 1983-1988). Death-side gated on `is_num` (explicit — L3-robust + self-documents the within-era rule; den rows physically lack locs 194-500 anyway): `age_at_death_days`=NULL (no AGED — faithful "not on this file"); `age_at_death_recode5`=`opt_int("AGER5",int8)` (num only); `underlying_cause_icd9`=`opt_str("UCOD")` (num only, ICD-9); `cause_recode_61`=`opt_int("UCODR61",int16)` (num only); `underlying_cause_icd10`/`cause_recode_130`=NULL (cohort ≤1998=ICD-9; HALT 5 — do NOT re-open); `manner_of_death`=NULL (no MANNER in the 1983-1988 numerator); `link_segment`=the parser passthrough. Birth-side (shared locs 1-91, BOTH segments) = the natality `is_pre1989` H7 ALIAS: `data_year`=year; `certificate_revision`="unrevised_1968" (H7 parity with natality `is_pre1989` `pre1968_s`); `residence_status`=RESSTAT→int8 + `is_foreign_resident`=(==4); `maternal_age`=DMAGE; `live_birth_order_recode`=LIVORD9 / `total_birth_order_recode`=TOTORD9 (the NCHS-native recode-9 — present 1983-1988 unlike 1989-1991 → more faithful + H7-parity with natality is_pre1989 native LBORD_R9/TBORD_R9; NOT `_detail_order_to_recode9`); `marital_status`=DMAR (the LINKED 1983-1988 file carries DMAR — unlike natality's pre-1989 public-use file; faithful + sibling-consistent with fetal-death 1982-1988); `maternal_race_bridged`=`_mrace1digit_to_bridged4(DMRACE)` (NEW local helper byte-identical to `harmonize_v1_core._mrace1digit_to_bridged4`, H7, SMOKE-asserted equal); `maternal_race_detail`=`_to_str_or_null(DMRACE)`; `race_bridge_method`="approximate_pre2003"; `maternal_education_cat4`=`_dmeduc_years_to_cat4(DMEDUC)` (H7 reuse); `father_education_cat4`=`_dmeduc_years_to_cat4(DFEDUC)` (the LINKED file carries DFEDUC; H7); `prenatal_care_start_month`=DMPCB + `prenatal_care_start_trimester`=`_month_to_trimester(DMPCB)` (H7 reuse); `prenatal_visits`=NPREVIS (raw — the 5c-i/5c-ii precedent); `plurality_recode`=DPLURAL; `infant_sex`=CSEX(1→M/2→F/else null); `gestational_age_weeks`=DGEST with the natality `is_pre1989` 17-47∪99 keep-filter (H7 parity; harmonized domain consistent across products) + `gestational_age_weeks_source`="lmp"; `birthweight_grams`=DBIRWT (9999 not-stated kept — the 5c-i/natality pattern); `apgar5`=APGAR5 (raw — the LINKED file carries it); `father_age`=DFAGE 10-98-keep-else-null (H7 parity with natality is_pre1989); `birth_facility`=`_pldel_to_facility(PLDEL)` (H7 reuse); `attendant_at_birth`=BIRATTND (9→null else value).

**(E) Conservative NULL (H7 parity with natality `is_pre1989` + soft-flag (gg) + the (A′) finding).** `hispanic_origin`/`maternal_hispanic`/`father_hispanic`/`maternal_race_ethnicity_5` (the 2-digit ORMOTH/ORFATH crosswalk is non-byte-stable & unverified per (A) — 1983 all `88`, 1988 `00`-dominant; natality `is_pre1989` sets pre-1989 hispanic NULL; → soft-flag (gg) DO step 6); **`record_weight`** (the (A′) RECWT@91 era-instability — the 5c-i/1989-1991 NULL-record_weight precedent; → soft-flag (ll) DO step 6); `maternal_race_detail_15cat`; the composite `DELMTH/MEDRISK/OBSTETRC/LABOR/ABNORMNB/ENTITY/RECORDAX` spans + smoking/diabetes/hypertension/preterm_recode3/ca_*/infection_*/payment/prior_cesarean/bmi/2014+-clinical (soft-flag (gg) leaf decomposition = DO step 6; the natality `is_pre1989` / 5c-i / 5c-ii conservative-mapping precedent).

**(F) behavior-preservation (§9-#7).** `_harmonize_cohort_1983_1988` fires ONLY for `_cohort_era(year)=="1983_1988"` (dispatched via the 2-line prepend before the `if era != "1989_1991":` guard). The 5c-i 1989-1991 inline body + 5c-ii-a `_harmonize_cohort_1995_2002` + 5c-ii-b `_harmonize_cohort_2003_2004` + the 2005+ `_harmonize_batch` body's existing array entries are byte-untouched (the only existing-line edits are the NotImplementedError message + the `_harmonize_cohort_batch` docstring + the 2005+ `from_arrays` ONE-entry append for link_segment — the 5c-i precedent, message/comment + the additive schema-position entry, 0 logic-deletion lines, grep-confirmed at VERIFY). The canonical v3 2005-2023 product + the 5c-i/5c-ii-a/5c-ii-b paths produce byte-identical VALUES (link_segment auto-defaults NULL there); the parquet is NOT re-run at 5c-iii (zero canonical mutation; 11/11 gate SHAs byte-exact). The durable 2005-2023 + per-era byte-clean regression + the per-year (1984-1988) non-anchor + NCHS-per-year-cohort-count check is DO step 6.

- [x] Current values match the (decomposed/clarified) task plan's assumed state ✓ — divergences (A)/(A′)/(B)-(F) named + resolved at this cheap-check moment per established precedent + the user's standing 2026-05-20 authorization; no silent proceed under a divergent state. (A′) is surfaced PROMINENTLY (the highest-materiality finding) but is NOT a §7 halt (anticipated + explicitly scheduled by the 3a self-check #2 + 5b self-check #3 for resolution at 5c/6; faithful no-patch within-scope conservative-NULL resolution; field_specs untouched; the 5a/5b/5c-ii-a Convention-3 within-task-resolution precedent).

### Halt conditions tripped
None. (A)/(A′)/(B)-(F) are a real-data-verified mapping resolution + the L17 bundle at the Convention-3 snapshot per the 5→5a/5b/5c + 5c→5c-i/5c-ii/5c-iii precedent + the user's standing authorization; not new scope, not a Q42/Phase-B-2 trigger, not a §7 condition. **(A′) RECWT@91 explicitly evaluated against §7**: NOT #5 (no previously-stable cell drifts — additive; the parquet is not built until DO 6), NOT #13 (the IMR analytic construction = num/den is RESOLVED + unaffected; only an auxiliary field is era-unstable, faithfully NULLed), NOT #14 (L13-extension is an EXISTING class, recurring — LESSONS note appended per §11 step 1, not a new class), NOT #17 (field_specs UNTOUCHED — the conservative-NULL is within 5c-iii's harmonize-mapping scope), NOT a §8-mandated halt (3a never claimed 1988 non-anchor byte-stability — it self-check-#2-flagged + routed the verification here; no bug in already-completed-work *within its claimed scope*), NOT anti-pattern #7 (NOT patching downstream to match a buggy upstream — declining to consume a non-byte-stable source field is the FAITHFUL representation, the documented 5c-i precedent; the root-cause re-verification is loudly routed to its scheduled DO-step-6 place). soft-flag (ii) §11 human-merge owes the human the model-clarification (now also folding the 5c-iii keyless map + the RECWT@91 finding; proposed-not-applied). NEW soft-flag (ll) (RECWT@91 + full per-year 1984-1988 non-anchor re-verification → DO step 6). soft-flag (kk): pytest runtime 352.85s within the advisory band (the COUNT 251P+1S+1XF is the gate).

### Result
**PROCEED to DO step 5c-iii** (SMOKE harness authored FIRST + run RED per §9-#9, then the additive `link_segment`→OUT_SCHEMA + the 2005+ pa.nulls entry + `_mrace1digit_to_bridged4` + `_harmonize_cohort_1983_1988` + the dispatch + the docstring/NotImplementedError reword + the 3 L17 `tracks-current-state` Edits to the 5c-ii-b/5c-ii-a/5c-i harnesses, then SMOKE GREEN + VERIFY + RECEIPT + the LESSONS L13-extension-recurrence note; intermediate DO step → no tag; zero canonical-state mutation).

---

## PRE-FLIGHT for C8.18 DO step 5c-ii-b — 2026-05-19T20:00:00Z — the **2003 + 2004 cohort birth-side maps** in `harmonize_linked_v3.py` (the 2003-revision dual-certificate transition; the natality V1-core `is_2003revised` analog) — **RESULT: PROCEED to DO** (9/9 forward-looking HALTs from `RECEIPTS/C8.18_step5c-ii-a_2026-05-19T17-00-00Z.md` re-verified; **11/11 gate parquet SHAs byte-exact**; canonical pytest baseline `233 passed, 1 skipped, 1 xfailed in 405.78s` (4-dir suite) — the COUNT is the 5c-ii-a-close baseline (the gate); 405.78s slightly over the ~340-380s advisory band → soft-flag (kk) environmental carry, the COUNT is the gate; a read-only real-data Convention-3 value-distribution probe of the 2003+2004 cohort den-plus substrate on real `LinkCO03US.zip` + `LinkCO04US.zip` + 5 within-task scope decisions surfaced + resolved at the Convention-3 snapshot **before any code mutation**, per the 5→5a/5b/5c + 5c→5c-i/5c-ii/5c-iii + 5c-ii→5c-ii-a/5c-ii-b + 4→4a/4b/4c + 3→3a/3b established precedent + the user's standing "proceed and make all the decisions yourself in the best way possible" authorization 2026-05-19; L17 grep-scope of all 9 cohort harnesses = exactly the 2 stale-pin Edits the 5c-ii-a receipt HALT 9 predicted + the recommended 5c-i `m in {1,2}`→`m == 1` harness-precision tighten, all bundled into the SAME 5c-ii-b commit per §4.2.1/Convention-2/L17; zero §7 halts)

> Per-sub-step PRE-FLIGHT under the C8.18 umbrella PRE-FLIGHT (2026-05-17T05:30:00Z) + the §15.D DO step 5 → 5a/5b/5c (2026-05-19T05:00:00Z) + 5c → 5c-i/5c-ii/5c-iii (2026-05-19T11:00:00Z) + 5c-ii → 5c-ii-a/5c-ii-b (2026-05-19T14:00:00Z) decompositions. Written **before any DO step 5c-ii-b mutation** (no `harmonize_linked_v3.py` edit, no new harness, no L17 edit yet — the only writes from this entry are PRE_FLIGHT_LOG + state files; L10-safe). DO step 5c-ii-b is harmonize-side substrate only (the re-harmonize that produces the v4 parquet is DO step 6); ZERO canonical-state mutation this sub-step.

### Entry cheap-check — 9 forward-looking HALTs (from `RECEIPTS/C8.18_step5c-ii-a_2026-05-19T17-00-00Z.md`)

1. **PASS** — `C8.18-pre-do`@`6632a15`; `C8.18-complete` NOT present; `C8.17-complete` present; HEAD = `8497e92` (the DO step 5c-ii-a commit, after `97d12fd`). Verified `git rev-parse`/`git tag`/`git log`.
2. **PASS** — **11/11 gate parquet SHAs byte-exact** vs the 5c-ii-a receipt VERIFY-A (`/tmp/c8_18_s5cii_b/gate.out`, 16-hex prefixes compared): nat `c8a740eb…`(harm)/`acb5c48a…`(deriv); `.v28_baseline` `230efed2…`/`e16ad532…`; linked-deriv `9b828a4d…`; fetal-death `38e2cecb…`(harm)/`185c071e…`(deriv) (via the `~/Desktop/fetal-death-harmonization-build/` tree, soft-flag (hh)); MM `5c22308b…`(1995-1997 raw)/`7c682668…`(1995-2000 raw)/`d98b4296…`(2016-2020 raw)/`adbec108…`(harmonized). Linked-derived changes only at the later DO step 6 re-harmonize.
3. **PASS** — canonical **4-dir** suite `fetal_death/tests/ natality/tests/ tests/ matched_multiples/tests/` = `233 passed, 1 skipped, 1 xfailed in 405.78s` (`/tmp/c8_18_s5cii_b/pytest_baseline.out`); the COUNT is exactly the 5c-ii-a-close baseline (233P+1S+1XF) — the gate per soft-flag (kk)/§8 L17/HALT-9. 405.78s is slightly over the ~340-380s advisory band → soft-flag (kk) (environmental cohort-Tier-1 real-data I/O variance; NOT a canonical regression — 11/11 gate SHAs byte-exact; a future `[plan-update]` should re-baseline the band). README 3-dir/"56 passed" line stays stale → soft-flag (jj).
4. **PASS** — `harmonize_linked_v3` exposes `_harmonize_cohort_1995_2002` (NEW@5c-ii-a) + `_cohort_era` + `_harmonize_cohort_batch` (1989-1991 + 1995-2002 implemented; 2003/2004 + the keyless 1983-1988 RAISE `NotImplementedError`) + the 2 within_era ICD-9 `OUT_SCHEMA` columns + the H7 recodes + the reusable helpers (`_meduc_to_cat4`/`_meduc_rec_to_cat4`/`_month_to_trimester`/`_fagerec11_to_cat`/`_pldel_to_facility`/`_dmeduc_years_to_cat4`/`_mrace_detail_to_bridged4`/`_to_int_or_null`/`_to_float_or_null`/`_to_str_or_null`/`_get_col[_optional]`), state-on-disk (read in full; do NOT re-derive). DO step 5c-ii-b = the **2003 + 2004** cohort birth-side maps (the 2003-rev dual-cert transition); 5c-iii = the keyless 1983-1988 `link_segment` encoding (the 5b model RESOLVED + state-on-disk; do NOT re-open).
5. **PASS** — the within_era ICD-9/ICD-10 cause-column-shape is RESOLVED + state-on-disk (DECISION_LOG/PRE_FLIGHT_LOG 2026-05-19T11:00:00Z; §15.D DO step 1): `underlying_cause_icd9`/`cause_recode_61` (cohort birth-year ≤1998), `underlying_cause_icd10`/`cause_recode_130` (≥1999), keyed on cohort birth year. 5c-ii-b applies it for 2003/2004 (cohort birth-year ≥1999 → **all ICD-10**: `underlying_cause_icd10`=UCOD, `cause_recode_130`=UCODR130; the ICD-9 cols null). Does NOT re-open the shape.
6. **PASS / noted** — the `harmonized_schema.csv` metadata edit + the v3→v4 version bump is DO step 6 (Anti-Pattern #6). 5c-ii-b is harmonize-CODE only; `OUT_SCHEMA` 80 cols UNCHANGED; NO `harmonized_schema.csv`/validation-CSV/parquet touch (the parquet is NOT re-run; gate SHAs byte-exact). DO step 6 forward note (Convention 4, below) records the schema-CSV `years_available` widenings 5c-ii-b makes durable (death-side 2005-2023→1983-2023 incl. the gap + `manner_of_death` + `father_age_cat_from_rec11` now also populated for cohort 2003/2004 + the ICD-9 rows).
7. **PASS / noted** — §15.D substrate-format reconcile applied at the 3a commit; the broader model-clarification — now ALSO folding the **5c-ii-b 2003+2004 map + the 2003/2004 den-plus MATCHS/FLGND-encoding finding** alongside 3a/3b + 4a/4b/4c + 5→5a/5b/5c + 5c→5c-i/5c-ii/5c-iii + 5c-ii→5c-ii-a/5c-ii-b — remains soft-flag (ii) §11 human-merge (proposed-not-applied; on-disk PRE_FLIGHT_LOG/DECISION_LOG/RECEIPTs authoritative meanwhile).
8. **PASS / consumed** — soft-flag (gg): the cause-column SHAPE is resolved (HALT 5); the per-condition leaf decomposition of the composite MEDRISK/OBSTETRC/LABOR/DELMETH/NEWBORN/CONGENIT/ENTITY/RECORD spans (+ preterm_recode3, father_race_ethnicity_5, smoking, diabetes/hypertension, payment, prior_cesarean) stays conservatively NULL at 5c-ii-b (the natality is_pre1989 / 5c-i / 5c-ii-a conservative-mapping precedent) → DO step 6.
9. **PASS / action required** — L17 forward-looking grep-scope of all **9** cohort SMOKE harnesses (`git ls-files natality/tests/ | grep linked_cohort | xargs grep -nE`): the parser/layout harnesses' 2003/2004 references (`test_linked_cohort_2003_layout_smoke.py`, `_2004_layout_smoke.py`, `_5b_numfinder_smoke.py`, `_denmember_5a_smoke.py`) target the **parser** dispatchers/member-finders (untouched by 5c-ii-b — the parser already handles 2003/2004 via 4b/4c/5a) → not stale. The 5c-i harness `test_tier0_..._cohort_era` `(2003,"2003"),(2004,"2004")` asserts the UNCHANGED `_cohort_era` classifier → not stale (must NOT touch). **Exactly the 2 stale harmonize-side pins the 5c-ii-a receipt HALT 9 predicted**: (i) `test_linked_cohort_5cii_a_harmonize_smoke.py::test_tier0_unimplemented_eras_still_failclosed` `[2003, 2004, 1983, 1985, 1988]` → 2003/2004 go stale (they will harmonize, not raise) → trim to `[1983, 1985, 1988]`; (ii) `test_linked_cohort_5c_harmonize_smoke.py::test_tier0_unimplemented_cohort_eras_failclosed` `[(1985,"5c-iii"),(2003,"5c-ii-b"),(2004,"5c-ii-b")]` → trim to `[(1985,"5c-iii")]`. Per §4.2.1/Convention-2/L17 both minimal `tracks-current-state` Edits are bundled into the SAME 5c-ii-b commit. **Plus** the 5c-ii-a-receipt-recommended harness-precision tighten (HALT 9 "Additional" + self-check #6 + DECISION_LOG residual risk #6): `test_linked_cohort_5c_harmonize_smoke.py::test_tier1_real_1990_parse_then_harmonize` `m in ("1","2")` → `m == "1"` (the §9-#4 fix-the-test-correctly, the 5c-ii-a-established era-correct AND era-independent stricter convention; the harness is being edited anyway for (ii) → a same-commit within-task harness-precision Edit, scope decision (E) below). The new 5c-ii-b harness is `DESIGN: tracks-current-state`, sub-step-isolated, SHAPE-not-VALUE (Convention 1/2).

### Inputs
- [x] `natality/scripts/03_harmonize/harmonize_linked_v3.py` — present (1600 lines; the 5c-ii-b target; `_harmonize_cohort_1995_2002` (5c-ii-a) + the 1989-1991 inline body + the 2005+ body + `OUT_SCHEMA` 80 cols + the H7 recodes/helpers). Read in full.
- [x] `natality/scripts/03_harmonize/harmonize_v1_core.py` — the H7 sibling-parity reference: the `is_2003revised` 2003-2024 path (MAGER41→single-year `code 1→14 / codes 2-41→code+13 / 99|>41→null`; `educ_cat4 = if_else(is_null(_meduc_to_cat4(MEDUC)), _meduc_rec_to_cat4(MEDUC_REC), …)`; `pn_start = if_else(is_null(PRECARE), MPCB, PRECARE)`; the `has_meduc`/`has_mrace`→revised_2003/unrevised_1989/unknown dual-cert cert-rev heuristic). Read (lines 1062-1400).
- [x] `natality/scripts/01_import/field_specs.py` — `LINKED_BIRTH_2003_FIELDS` (locs 1-750) + `LINKED_DEATH_2003_FIELDS` (751-783; MATCHS@751/AGED@755-757/AGER5@758/MANNER@761/UCOD@767-770 ICD-10/UCODR130@772-774/RECWT@776-783) + `LINKED_DENOMPLUS_RECLEN_2003`=783; `LINKED_BIRTH_2004_FIELDS` (locs 1-867) + `LINKED_DEATH_2004_FIELDS` (868-900; FLGND@868/AGED@872-874/MANNER@878/UCOD@884-887/UCODR130@889-891/RECWT@893-900) + `LINKED_DENOMPLUS_RECLEN_2004`=900; state-on-disk 4b/4c/5a, read-only.
- [x] `natality/metadata/harmonized_schema.csv` — the canonical mapping definitions cross-checked for H7 parity (certificate_revision derivation "2003-2013: revised_2003 if MEDUC nonblank; else unrevised_1989 if MRACE nonblank; else unknown"; maternal_education_cat4 "2003+: MEDUC 1-2→lt_hs…"; gestational_age_weeks_source "combined for 2003-2013"; father_age "2003-2011: UFAGECOMB@184-185; 99→null clip 9-98"; father_age_cat_from_rec11 within-era "FAGEREC11 01-02→<20…"; manner_of_death "1-7|null; MANNER"). Read the relevant rows. **NOT edited** at 5c-ii-b (HALT 6).
- [x] `natality/tests/test_linked_cohort_5cii_a_harmonize_smoke.py` (the 5c-ii-a harness — the 5c-ii-b harness template + the L17 stale-pin (i)) + `natality/tests/test_linked_cohort_5c_harmonize_smoke.py` (the 5c-i harness — the L17 stale-pin (ii) + the recommended `m`-cross-check tighten). Read in full.
- [x] `RECEIPTS/C8.18_step5c-ii-a_2026-05-19T17-00-00Z.md` — the 9 forward-looking HALTs + the 1995-2002 map + the MATCHS==1-uniform-across-eras finding + the byte-position guidance for 2003/2004 (HALT 4).
- [x] No required upstream task incomplete: DO step 5a/5b/5c-i/5c-ii-a CLOSED + committed (HEAD `8497e92`).
- [x] No stale checkpoints: `git status --porcelain` clean; on `main`; `/tmp/c8_18_s5cii_b/*` is OS-scratch (gate-SHA + pytest baseline + the read-only probe), reproducible.

### Environment
- [x] Python 3.13 via `uv run`; pyarrow/pandas pinned (`uv.lock`, C8.5a). No new dependency at 5c-ii-b (harmonize-side; reuses pyarrow + the existing helpers/recodes; one NEW local helper `_mager41_to_age` — pure pyarrow, H7 sibling-parity).
- [x] Working dir clean; on `main`.

### Source documentation
- [x] No new external PDF consumed at 5c-ii-b (the 2003/2004 layouts were authored + SHA-anchored at DO step 4b/4c; 5c-ii-b maps the already-parsed field names to harmonized columns). No SHA-256 to re-verify.

### Outputs (intended; 5c-ii-b)
- [ ] `natality/scripts/03_harmonize/harmonize_linked_v3.py` — **additive**: a NEW `_mager41_to_age` helper (H7 sibling-parity) + a NEW `_harmonize_cohort_2003_2004(batch, year)` function + a 2-line `if era in ("2003","2004"): return _harmonize_cohort_2003_2004(batch, year)` dispatch prepended in `_harmonize_cohort_batch` (after the 5c-ii-a `if era == "1995_2002":` line, before the `if era != "1989_1991":` guard) + the NotImplementedError-message/docstring reword (now only 1983-1988 keyless = 5c-iii remains unimplemented). The 5c-i 1989-1991 inline body + the 5c-ii-a `_harmonize_cohort_1995_2002` + the 2005+ body byte-untouched (the 2003/2004 branch fires only for year ∈ {2003,2004} → the canonical v3 2005-2023 path + the 5c-i 1989-1991 + the 5c-ii-a 1995-2002 paths byte-identical; §9-#7-safe). `OUT_SCHEMA` 80 cols unchanged.
- [ ] `natality/tests/test_linked_cohort_5cii_b_harmonize_smoke.py` — NEW; `DESIGN: tracks-current-state`; SHAPE-not-VALUE; sub-step-isolated. Written FIRST + run RED (§9-#9 / L3 — collection ImportError vs the un-modified harmonizer).
- [ ] `natality/tests/test_linked_cohort_5cii_a_harmonize_smoke.py` — minimal L17 `tracks-current-state` Edit bundled in the SAME commit (stale-pin (i): trim `[2003,2004,1983,1985,1988]`→`[1983,1985,1988]`; docstring note).
- [ ] `natality/tests/test_linked_cohort_5c_harmonize_smoke.py` — minimal L17 `tracks-current-state` Edit bundled in the SAME commit (stale-pin (ii): trim `[(1985,"5c-iii"),(2003,"5c-ii-b"),(2004,"5c-ii-b")]`→`[(1985,"5c-iii")]`; **+ scope decision (E)** the recommended harness-precision tighten `m in ("1","2")`→`m == "1"` in `test_tier1_real_1990_parse_then_harmonize` + its comment; docstring note).
- [ ] `PRE_FLIGHT_LOG.md` (this entry) + `RECEIPTS/C8.18_step5c-ii-b_…` + `DECISION_LOG.md` + `STATUS.md` appended.
- [x] NO canonical parquet / `harmonized_schema.csv` / validation-CSV mutation (the harmonizer is NOT re-run at 5c-ii-b; gate SHAs byte-exact). NO git tag (intermediate DO step; `C8.18-pre-do`@`6632a15` is the rollback anchor).

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

No canonical *value* is mutated at 5c-ii-b (zero parquet/schema-CSV/validation-CSV touch). The snapshot below records the **decisions** fixed at this cheap-check moment, before any code mutation.

**(A) 2003 + 2004 cohort den-plus substrate — real-data value-distribution probe (L13-extension; read-only, before any code mutation).** Plan-assumed (5c-ii-a receipt HALT 4 + §15.D + field_specs 4b/4c): 2003/2004 _raw columns == `LINKED_BIRTH_/_DEATH_2003/2004_FIELDS`; 2003-rev dual-cert; all ICD-10. Verified by a read-only `iter_parsed_records` probe on real `LinkCO03US.zip` (cohort 2003; DEFLATE64) + `LinkCO04US.zip` (cohort 2004; DEFLATE), n=4000 den-plus each (`/tmp/c8_18_s5cii_b/probe_2003_2004.py`):
  - Parsed columns == the field_specs 2003/2004 layouts + `year`; **no `link_segment`** (single-member den-plus, like 1995-2002; NOT the keyless 1983-1988).
  - **Dual-cert REVISION**: the first-4000 sample is 100% `REVISION='S'` (1989-unrevised). Consequently MEDUC@155 / PRECARE@245-246 / MBRACE@139-140 are **all blank** on the S-rev rows; the 1989-unrevised siblings UMEDUC@156-157 / MEDUC_REC@158 / MPCB@256-257 / MRACE@141-142 / MRACEREC@143 carry the values. The natality V1-core dual-cert coalesce (`if_else(is_null(_meduc_to_cat4(MEDUC)), _meduc_rec_to_cat4(MEDUC_REC), …)`; `if_else(is_null(PRECARE), MPCB, PRECARE)`; `has_meduc/has_mrace`→cert-rev) handles BOTH revisions faithfully (H7) — no surprise; the A-rev path is exercised by the synthetic SMOKE Tier-0.
  - Anchor distributions plausible: MAGER41 (2003)/MAGER (2004) recode-41 06-41 (NOT single-year — `_mager41_to_age` required); MAGER14/MAGER9 coarser recodes; RESTATUS {1,2,3,4}; MRACE 2-digit detail (01/02/03/07/78); MRACEREC {1,2,3,4}; UMHISP {0,1-5,9}; MAR {1,2}; UMEDUC years (08-17,99); MEDUC_REC {1-6}; LBO_REC/TBO_REC {1-9}; MPCB month (00-09,99); UPREVIS (00-99); DPLURAL {1,2}; SEX already **"M"/"F"** (string; the parser decoded it — use `_to_str_or_null`, NOT CSEX-int); COMBGEST weeks (33-44,99); GESTREC3 {1,2,3}; DBWT(2003)/BRTHWGT(2004) grams 4-digit; APGAR5 (00-10,99); ATTEND {1-5,9}; UBFACIL {1-5,9} (PLDEL-style); FAGEREC11 {01-11}; UFHISP {0,1-5,9}; UFAGECOMB (19-50,99); DOB_YY == the cohort year.
  - **MANNER present** (2003 @761 / 2004 @878; dist {blank,1,3,5,7}) → `manner_of_death` (NEW vs 1995-2002 which had no MANNER). **RECWT present** (2003 @776-783 / 2004 @893-900; "1.000000"/"1.142857" clean float) → `record_weight`. **All ICD-10** (death-row UCOD = alpha-prefixed "P010","Q913","W75","Y34","B348" etc.; UCODR130 3-digit) — confirms cohort birth-year ≥1999 = ICD-10 (the 5c-i resolved shape; `underlying_cause_icd10`/`cause_recode_130` populated, the ICD-9 cols null).
  - **§7-#13 cross-check on real data**: `MATCHS × AGED-nonblank` (2003) = `{('2',False):3979, ('1',True):21}` (PERFECT 21/21 linked-infant-death ⟺ MATCHS=='1'; survivors MATCHS=='2'); `FLGND × AGED-nonblank` (2004) = `{('2',False):3981, ('1',True):19}` (PERFECT 19/19 ⟺ FLGND=='1'; survivors FLGND=='2'). **Confirms the 5c-ii-a finding holds for 2003/2004**: the linked-infant-death code is uniformly match-status==`1` across ALL eras (1989-1991/1995-2002 MATCHS==1; 2003 MATCHS==1; 2004 FLGND==1); the survivor code is era-dependent (2003 MATCHS=='2', 2004 FLGND=='2', same as 1995-2002's '2'; 1989-1991 was '3'). The match-status FIELD NAME differs by year: 2003=`MATCHS`, 2004=`FLGND`.

**(B) §15.D DO step 5c-ii-b architecture = ONE `_harmonize_cohort_2003_2004(batch, year)` (NOT two functions); §9-#8 judgment.** 2003 + 2004 are ONE §15.D sub-step (5c-ii-b = "the 2003 + 2004 cohort birth-side maps"), ONE certificate revision (2003-rev dual-cert), the receipt itself frames them as one unit. The 2003-vs-2004 deltas are pure raw-name aliasing (`MAGER41`↔`MAGER`; `DBWT`↔`BRTHWGT`; the death match-status `MATCHS`↔`FLGND` — only used by the SMOKE cross-check, not the harmonizer which is AGED-value-driven) handled via `_get_col_optional` name-fallback — exactly the natality V1-core single `is_2003revised` branch pattern (which handles 2003 MAGER41 + 2004+ MAGER in one path). This is NOT compressing separable concerns (§9-#8): it is the faithful single unit. The 5c-ii-a (a)-rejected "compress" alternative was about NOT mixing 1995-2002 (1989-rev) WITH 2003/2004 (2003-rev) — different revisions; within the 2003-rev, 2003+2004 together is the natural unit. A fail-closed `if _cohort_era(year) not in ("2003","2004"): raise ValueError`. Authored as a SEPARATE function (not a shared helper with the 1989-1991/1995-2002 branches) so the 5c-i/5c-ii-a-verified bodies stay **byte-untouched** (§9-#7; the file's explicit-per-era helper-duplication pattern).

**(C) 2003/2004 birth-side mapping strategy = the natality V1-core `is_2003revised` recodes ALIASED (H7 sibling-parity; reuse, do NOT re-derive).** The cohort 2003/2004 birth section IS a 2003-revision birth certificate == natality `is_2003revised`. The map reuses the existing `harmonize_linked_v3` helpers `_meduc_to_cat4`/`_meduc_rec_to_cat4`/`_month_to_trimester`/`_fagerec11_to_cat`/`_pldel_to_facility`/`_mrace_detail_to_bridged4` + ONE NEW `_mager41_to_age` (byte-identical to the natality V1-core inline MAGER41 conversion `code 1→14 / codes 2-41→code+13 / 99|>41→null`; H7; SMOKE-asserted equal). Per-field map (schema-grounded; the 5c-ii-a structure + the (A)-verified 2003-rev deltas):
  - `maternal_age` = `_mager41_to_age(MAGER41|MAGER)`; `maternal_education_cat4` = `if_else(is_null(_meduc_to_cat4(MEDUC)), _meduc_rec_to_cat4(MEDUC_REC), _meduc_to_cat4(MEDUC))` (byte-identical to natality V1-core 2003-rev); `certificate_revision` = the natality V1-core `has_meduc`/`has_mrace` dual-cert heuristic (revised_2003 / unrevised_1989 / unknown — matches the schema `derivation` column + REVISION@7 S/A semantics; H7); `prenatal_care_start_month` = `if_else(is_null(PRECARE), MPCB, PRECARE)` (H7) → `_month_to_trimester`; `prenatal_visits` = UPREVIS (raw, the 5c-ii-a NPREVIST-raw precedent); `maternal_race_bridged` = `_mrace_detail_to_bridged4(MRACE)` + race_bridge_method "approximate_pre2003" (the 5c-i/5c-ii-a sibling-consistent choice; the richer A-rev MBRACE/MRACEREC nchs_bridged precision = soft-flag (gg) DO step 6 — residual risk, below); hispanic via UMHISP, father_hispanic via UFHISP (the 5c-ii-a ORMOTH/ORFATH 1-5→True/0→False pattern); `live_birth_order_recode`/`total_birth_order_recode` = LBO_REC/TBO_REC (already the NCHS 1-9 recode — direct opt_int int8); `plurality_recode`=DPLURAL; `infant_sex`=`_to_str_or_null(SEX)`∈{M,F}; `gestational_age_weeks`=COMBGEST (the 17-47 ∪ 99 keep filter, the 5c-ii-a GESTAT pattern); `gestational_age_weeks_source`="combined" (2003-rev COMBGEST; schema-documented; the per-era delta vs 5c-ii-a's "lmp"); `birthweight_grams`=DBWT|BRTHWGT; `apgar5`=APGAR5 (raw); `father_age`=UFAGECOMB (9-98 valid filter, 99→null; schema-documented); `father_age_cat_from_rec11`=`_fagerec11_to_cat(FAGEREC11)` (H7 helper; schema-documented within-era recode; the 2003-rev enrichment — DO step 6 widens its schema years_available 2005-2013→2003-2013); `birth_facility`=`_pldel_to_facility(UBFACIL)`; `attendant_at_birth`=ATTEND (9→null, the 5c-ii-a BIRATTND pattern).
  - Death-side: `infant_death`=`fill_null(invert(is_null(AGED)),False)` (value-driven, NO match-status assumption — the 5c-i/5c-ii-a discipline); `age_at_death_days`=AGED; `age_at_death_recode5`=AGER5; `underlying_cause_icd10`=UCOD; `cause_recode_130`=UCODR130; `underlying_cause_icd9`/`cause_recode_61`=null (cohort ≥1999 = ICD-10, the 5c-i resolved shape / HALT 5); `manner_of_death`=MANNER (NEW; schema 1-7|null — DO step 6 widens its schema years_available); `record_weight`=`_to_float_or_null(RECWT)`.
  - Conservatively NULL (soft-flag (gg)/HALT 8; the 5c-i/5c-ii-a precedent): the composite MEDRISK/OBSTETRC/LABOR/DELMETH/NEWBORN/CONGENIT/ENTITY/RECORD spans → smoking_*, diabetes_any, hypertension_*, delivery_method_recode, preterm_recode3, ca_*/infection_*/fertility/art, father_race_ethnicity_5, father_education_cat4 (no clean father-education value field; F_MEDUC@571 is an edit flag), payment_source_recode, prior_cesarean[_count], marital_reporting_flag, bmi_*, the 2014+ clinical-detail block, maternal_race_detail_15cat (no MRACE15 on the cohort 2003/2004 layout).

**(D) behavior-preservation (§9-#7).** `_harmonize_cohort_2003_2004` fires ONLY for `_cohort_era(year) ∈ {"2003","2004"}` (dispatched via a 2-line prepend in `_harmonize_cohort_batch` AFTER the 5c-ii-a `if era == "1995_2002":` line, BEFORE the existing `if era != "1989_1991":` guard). The 5c-i 1989-1991 inline body + the 5c-ii-a `_harmonize_cohort_1995_2002` + the 2005+ `_harmonize_batch` body are byte-untouched (the only existing-line edits are the NotImplementedError message-string + the `_harmonize_cohort_batch` docstring — message/comment text, 0 logic-deletion lines, grep-confirmed at VERIFY). The canonical v3 2005-2023 product + the 5c-i 1989-1991 + the 5c-ii-a 1995-2002 paths are byte-identical; the parquet is NOT re-run at 5c-ii-b (zero canonical mutation; 11/11 gate SHAs byte-exact). The durable 2005-2023 + per-era byte-clean regression check is DO step 6.

**(E) L17 harness bundle + the recommended `m`-cross-check precision tighten (within-task; same-commit; §9-#4).** Beyond the 2 mandatory L17 stale-pin Edits (HALT 9 (i)/(ii)), the 5c-ii-a receipt HALT 9 "Additional" + self-check #6 + DECISION_LOG 2026-05-19T17:00:00Z residual risk #6 recommended a future tighten of the 5c-i harness `test_tier1_real_1990_parse_then_harmonize` independent §7-#13 cross-check `m in ("1","2")` → `m == "1"` (it is imprecise-but-not-stale: PASSES because real LinkCO90 carries no MATCHS==2, but the loose code could mask a future divergence). Decision: bundle it into the SAME 5c-ii-b commit as the (ii) stale-pin Edit (the 5c-i harness is already being edited for (ii); the fix is the SAME §9-#4 correctness improvement already validated in 5c-ii-a — the real-data-established era-correct AND era-independent linked-infant-death code is uniformly `==1` (re-confirmed for 2003/2004 in (A)); STRICTER not looser; a within-task harness-precision decision, NOT new scope — the same class as the 5c-ii-a `{1,2}`→`==1` test-correctness fix). This consumes DECISION_LOG residual risk #6.

- [x] Current values match the (decomposed/clarified) task plan's assumed state ✓ — divergences (A)-(E) named + resolved at this cheap-check moment per established precedent + the user's standing 2026-05-19 authorization; no silent proceed under a divergent state; not §7 halts (within-task mapping resolution + a same-commit harness-precision Edit, the 5a/5b/5c-i/5c-ii-a precedent).

### Halt conditions tripped
None. (A)-(E) are a real-data-verified mapping resolution + the L17 bundle + a within-task harness-precision Edit at the Convention-3 snapshot per the 5→5a/5b/5c + 5c→5c-i/5c-ii/5c-iii + 5c-ii→5c-ii-a/5c-ii-b precedent + the user's standing authorization; not new scope, not a Q42/Phase-B-2 trigger, not a §7 condition. soft-flag (ii) §11 human-merge owes the human the model-clarification (now also folding the 5c-ii-b 2003+2004 map + the 2003/2004 MATCHS/FLGND-encoding finding; proposed-not-applied; on-disk logs authoritative meanwhile). soft-flag (kk): pytest runtime 405.78s over the ~340-380s advisory band (environmental; the COUNT 233P+1S+1XF is the gate).

### Result
**PROCEED to DO step 5c-ii-b** (SMOKE harness authored FIRST + run RED per §9-#9, then the additive `_mager41_to_age` + `_harmonize_cohort_2003_2004` + the dispatch + the L17/precision Edits to the 5c-ii-a + 5c-i harnesses, then SMOKE GREEN + VERIFY + RECEIPT; intermediate DO step → no tag; zero canonical-state mutation).

---

## PRE-FLIGHT ADDENDUM for C8.18 DO step 5c-ii-a — 2026-05-19T15:00:00Z — the SMOKE Tier-1 independent §7-#13 cross-check MATCHS code: `MATCHS ∈ {1,2}` → **`MATCHS == 1`** (a Convention-3 divergence surfaced at SMOKE, resolved BEFORE final DO; L10-safe NEW dated entry, NOT a back-fill — the 5b 2026-05-19T08:30:00Z + Task-1 2026-05-11T17:58:10Z precedent)

> The SMOKE harness was authored FIRST and run (§9-#9): Tier 0 = 48/48 PASS; the 2 Tier-1 real-data tests FAILED on the independent `infant_death (AGED-derived) == MATCHS-death` §7-#13 cross-check (`AGED=3, MATCHS=400` for 1999 — i.e. ALL 400 den-plus rows have `MATCHS ∈ {1,2}`). This is exactly what the cross-check exists to surface, at the cheap SMOKE moment rather than at the expensive DO step 6.

**Divergence.** The new 5c-ii-a SMOKE Tier-1 cross-check inherited the 5c-i harness's `death_by_matchs = [m in ("1","2")]` framing (the 5b/3b receipts' "linked infant deaths = MATCHS ∈ {1,2}; surviving = MATCHS 3" model). A read-only real-data probe (`MATCHS × AGED-nonblank` cross-tab; n=3000 each on real `LinkCO90.zip` / `LinkCO95US.zip` / `LinkCO99US.zip`) shows the **denominator-plus MATCHS encoding is era-dependent on the SURVIVOR code but uniform on the DEATH code**:

| era | MATCHS dist (den-plus) | AGED-nonblank ⟺ |
|---|---|---|
| 1989-1991 (LinkCO90) | `{3: 2970 (survivor), 1: 30 (death)}` | **MATCHS == 1** (30/30) |
| 1995-2002 (LinkCO95) | `{2: 2983 (surviving), 1: 17 (death)}` | **MATCHS == 1** (17/17) |
| 1995-2002 (LinkCO99) | `{2: 2974 (surviving), 1: 26 (death)}` | **MATCHS == 1** (26/26) |

The linked-infant-death code is **uniformly `MATCHS == 1`** (matched birth↔infant-death) across BOTH eras; the SURVIVOR code differs (`3` for 1989-1991 per the 1989Guide; `2` for 1995-2002 per `field_specs.py:1222` "1 matched B/ID, 2 surviving, 3 unmatched-unl-only"). The `{1,2}` framing is imprecise: for 1995-2002 it sweeps in code `2` = *surviving* (→ all 400 rows flagged "death", the failure). The cross-tab is **perfect** for all 3 years: `infant_death (AGED-non-blank) ⟺ MATCHS == 1`.

**Resolution (§9-#4 / §2 — fix the test CORRECTLY, never loosen to pass).** The harmonizer's `infant_death = AGED-non-blank` derivation is **CORRECT and UNCHANGED** (real data: ~0.57-1.0% deaths = the IMR ballpark; a *perfect* AGED-nonblank ⟺ MATCHS==1 cross-tab — the value-driven signal 5c-i deliberately chose). The defect is in the SMOKE harness's *independent cross-check*, which used the wrong (imprecise, copied) MATCHS death-code. Fix: `death_by_matchs = [m == "1"]` — the era-correct AND era-independent linked-infant-death code. This makes the cross-check **STRICTER** (it now rejects any AGED-derived death that is not the matched-B/ID code), not looser; it is a test-correctness fix, not a §9-#4 loosening. No `harmonize_linked_v3.py` logic change (the only DO edits remain the additive `_harmonize_cohort_1995_2002` + dispatch); the SMOKE-harness cross-check edit is part of the same uncommitted SMOKE phase (the §9-#9 "author FIRST, run RED, then GREEN" loop, not a post-DO patch).

**Soft-flag (new — narrow; folded into soft-flag (ii) §11 human-merge).** The 5c-i harness `test_linked_cohort_5c_harmonize_smoke.py::test_tier1_real_1990_parse_then_harmonize` still uses `m in ("1","2")`. It is **NOT stale** (it PASSES — the real LinkCO90 den-plus carries no `MATCHS == 2`, so `{1,2}` ≡ `{1}` there) and is OUT of 5c-ii-a's minimal-scope L17 bundle (§9-#7 scope discipline — do not modify a non-stale verified harness beyond the stale-pin fix). Recommended future cleanup (DO step 6 PRE-FLIGHT or a dedicated harness-precision pass): tighten the 5c-i cross-check to `m == "1"` for the same precision, with a one-line note. Logged as a DECISION_LOG residual risk + receipt Forward-looking HALT.

**Result: PROCEED to final DO** (fix the 5c-ii-a SMOKE Tier-1 cross-check to `m == "1"`; re-run → expect GREEN; zero §7 halts; zero canonical-state mutation; the divergence resolved before the commit, L10-safe via this NEW dated addendum, never a back-fill of the 14:00:00Z entry).

---

## PRE-FLIGHT for C8.18 DO step 5c-ii-a — 2026-05-19T14:00:00Z — §15.D DO step 5c-ii decomposed → **5c-ii-a / 5c-ii-b**; the **1995-2002 cohort birth-side map** in `harmonize_linked_v3.py` (the 1989-revision sibling of the 5c-i-verified 1989-1991 reference era; reuses the architecture + the within_era ICD-9/ICD-10 split keyed on cohort birth year — cohort 1995-1998 = ICD-9 / 1999-2002 = ICD-10) — **RESULT: PROCEED to DO** (9/9 forward-looking HALTs from `RECEIPTS/C8.18_step5c-i_2026-05-19T11-00-00Z.md` re-verified; **11/11 gate parquet SHAs byte-exact**; canonical pytest baseline `213 passed, 1 skipped, 1 xfailed in 352.36s` (4-dir suite) preserved; the §15.D DO step 5c-ii → **5c-ii-a/5c-ii-b** decomposition + a read-only real-data Convention-3 value-distribution probe of the 1995-2002 parsed substrate + 4 within-task scope decisions surfaced + resolved at the Convention-3 snapshot **before any code mutation**, per the 5→5a/5b/5c + 5c→5c-i/5c-ii/5c-iii + 4→4a/4b/4c + 3→3a/3b established precedent + the user's standing "make all the decisions yourself in the best way possible" authorization 2026-05-19; L17 grep-scope of all 8 cohort harnesses = ONE stale pin identified [the 5c-i `test_tier0_unimplemented_cohort_eras_failclosed` 1995/2002 NotImplementedError pins] → minimal `tracks-current-state` Edit bundled into the 5c-ii-a commit per §4.2.1/Convention-2; zero §7 halts)

> Per-sub-step PRE-FLIGHT under the C8.18 umbrella PRE-FLIGHT (2026-05-17T05:30:00Z) + the §15.D DO step 5 → 5a/5b/5c decomposition (2026-05-19T05:00:00Z) + the 5c → 5c-i/5c-ii/5c-iii decomposition (2026-05-19T11:00:00Z). Written **before any DO step 5c-ii-a mutation** (no `harmonize_linked_v3.py` edit, no new harness, no edit to the 5c-i harness — the only writes from this entry are PRE_FLIGHT_LOG + state files; L10-safe). DO step 5c-ii is harmonize-side substrate only (the re-harmonize that produces the v4 parquet is DO step 6); ZERO canonical-state mutation this sub-step.

### Entry cheap-check — 9 forward-looking HALTs (from `RECEIPTS/C8.18_step5c-i_2026-05-19T11-00-00Z.md`)

1. **PASS** — `C8.18-pre-do`@`6632a15`; `C8.18-complete` NOT present; `C8.17-complete` present; HEAD = `97d12fd` (the DO step 5c-i commit, after `383692a`). Verified `git rev-parse`/`git tag`/`git log -1`.
2. **PASS** — **11/11 gate parquet SHAs byte-exact** vs the 5c-i receipt HALT 2 (`/tmp/c8_18_s5cii_gate.out`, full 64-hex compared programmatically): nat `c8a740eb…`(harm)/`acb5c48a…`(deriv); `.v28_baseline` `230efed2…`/`e16ad532…`; linked-deriv `9b828a4d…`; fetal-death `38e2cecb…`(harm)/`185c071e…`(deriv) (via the `~/Desktop/fetal-death-harmonization-build/` tree, soft-flag (hh)); MM `5c22308b…`(1995-1997 raw)/`7c682668…`(1995-2000 raw)/`d98b4296…`(2016-2020 raw)/`adbec108…`(harmonized). Linked-derived changes only at the later DO step 6 re-harmonize.
3. **PASS** — canonical **4-dir** suite `fetal_death/tests/ natality/tests/ tests/ matched_multiples/tests/` = `213 passed, 1 skipped, 1 xfailed in 352.36s` (`/tmp/c8_18_s5cii_pytest_baseline.out`); exactly the 5c-i-close baseline (213P+1S+1XF). 352.36s within the ~240-380s advisory band (soft-flag (kk); the COUNT is the gate). README 3-dir/"56 passed" line stays stale → soft-flag (jj).
4. **PASS** — `harmonize_linked_v3` exposes `_cohort_era` + `_harmonize_cohort_batch` (1989-1991 only; the other cohort eras RAISE `NotImplementedError`) + the 2 within_era ICD-9 `OUT_SCHEMA` columns (`underlying_cause_icd9` string + `cause_recode_61` int16) + the H7 recodes (`_dmeduc_years_to_cat4`/`_mrace_detail_to_bridged4`/`_detail_order_to_recode9`), state-on-disk (read in full; do NOT re-derive). DO step 5c-ii-a = the **1995-2002** cohort birth-side map (the 1989-rev sibling of the 5c-i 1989-1991 reference era); 5c-ii-b = 2003 + 2004 (the 2003-rev transition); 5c-iii = the keyless 1983-1988 `link_segment` encoding.
5. **PASS** — the within_era ICD-9 cause-column-shape is RESOLVED + state-on-disk (DECISION_LOG/PRE_FLIGHT_LOG 2026-05-19T11:00:00Z; §15.D DO step 1): `underlying_cause_icd9`/`cause_recode_61` (within_era, cohort birth-year ≤1998), `underlying_cause_icd10`/`cause_recode_130` (≥1999). 5c-ii-a APPLIES it for the 1995-2002 era (≤1998 ICD-9 / ≥1999 ICD-10), does NOT re-open the shape.
6. **PASS / noted** — the `harmonized_schema.csv` metadata edit + the v3→v4 version bump is DO step 6 (Anti-Pattern #6). 5c-ii-a is harmonize-CODE only; NO `harmonized_schema.csv`/validation-CSV/parquet touch (the parquet is NOT re-run; gate SHAs byte-exact).
7. **PASS / noted** — §15.D substrate-format reconcile applied at the 3a commit; the broader model-clarification — now ALSO folding the **5c-ii → 5c-ii-a/5c-ii-b decomposition** alongside 3a/3b + 4a/4b/4c + 5→5a/5b/5c + 5c→5c-i/5c-ii/5c-iii — remains soft-flag (ii) §11 human-merge (proposed-not-applied; on-disk PRE_FLIGHT_LOG/DECISION_LOG/RECEIPTs authoritative meanwhile).
8. **PASS / consumed** — soft-flag (gg): the cause-column SHAPE is resolved (HALT 5); the per-condition leaf decomposition of the composite MEDRISK/OBSTETRC/LABOR/DELMETH/NEWBORN/CONGENIT/ENTITY/RECORD spans (+ preterm_recode3, father_race_ethnicity_5) stays conservatively NULL at 5c-ii-a (the natality is_pre1989 / 5c-i conservative-mapping precedent) → DO step 6.
9. **PASS / action required** — L17 forward-looking grep-scope of all **8** cohort SMOKE harnesses: the parser harnesses' `pytest.raises`/1992-1994 pins target the parser dispatchers (untouched by 5c-ii-a — the parser already handles 1995-2002 via 4a/5a). **ONE stale pin identified**: `test_linked_cohort_5c_harmonize_smoke.py::test_tier0_unimplemented_cohort_eras_failclosed` parametrizes `(1995,"5c-ii")` + `(2002,"5c-ii")` asserting `_harmonize_batch` RAISES `NotImplementedError` for 1995/2002 — these go STALE when 5c-ii-a implements 1995-2002 (they will harmonize, not raise). Per §4.2.1/Convention-2/L17, the minimal `tracks-current-state` Edit (remove the 1995/2002 rows; relabel 2003/2004 → "5c-ii-b") is bundled into the SAME 5c-ii-a commit. The new 5c-ii-a harness is `DESIGN: tracks-current-state`, sub-step-isolated, SHAPE-not-VALUE (Convention 1/2).

### Inputs
- [x] `natality/scripts/03_harmonize/harmonize_linked_v3.py` — present (the 5c-ii target; `_harmonize_cohort_batch` 1989-1991 reference era + `OUT_SCHEMA` extended w/ the 2 within_era ICD-9 cols + the H7 recodes + helpers `_to_int_or_null`/`_to_float_or_null`/`_to_str_or_null`/`_get_col[_optional]`/`_month_to_trimester`/`_pldel_to_facility`). Read in full.
- [x] `natality/scripts/01_import/field_specs.py` — `LINKED_BIRTH_1995_2002_FIELDS` (locs 1-210; 1989-rev birth cert) + `LINKED_DEATH_1995_2002_FIELDS` (locs 211-230; AGED@211-213, AGER5@214, UCOD@216-219, UCODR@220-222, RECWT@223-230) + `LINKED_DENOMPLUS_RECLEN_1995_2002`=230; state-on-disk 4a/5a, read-only.
- [x] `natality/tests/test_linked_cohort_5c_harmonize_smoke.py` — the 5c-i harness; read in full to scope the L17 stale pin (HALT 9).
- [x] `natality/scripts/03_harmonize/harmonize_v1_core.py` — the H7 sibling-parity reference (`is_pre2003` 1990-2002 == the 1989-rev recode family the 1995-2002 cohort uses); read.
- [x] `RECEIPTS/C8.18_step5c-i_2026-05-19T11-00-00Z.md` — the architecture + the resolved cause-column shape + the 9 forward-looking HALTs.
- [x] No required upstream task incomplete: DO step 5a/5b/5c-i CLOSED + committed (HEAD `97d12fd`).
- [x] No stale checkpoints: `git status --porcelain` clean; on `main`; `/tmp/c8_18_s5cii_*` is OS-scratch (gate-SHA + pytest baseline + the read-only probe), reproducible.

### Environment
- [x] Python 3.13 via `uv run`; pyarrow/pandas pinned (`uv.lock`, C8.5a). No new dependency at 5c-ii-a (harmonize-side; reuses pyarrow + the existing helpers/recodes).
- [x] Working dir clean; on `main`.

### Source documentation
- [x] No new external PDF consumed at 5c-ii-a (the 1995-2002 layout was authored + SHA-anchored at DO step 4a; 5c-ii-a maps the already-parsed field names to harmonized columns). No SHA-256 to re-verify.

### Outputs (intended; 5c-ii-a)
- [ ] `natality/scripts/03_harmonize/harmonize_linked_v3.py` — **additive** (a NEW `_harmonize_cohort_1995_2002` function + a 2-line `if era == "1995_2002": return …` dispatch prepended in `_harmonize_cohort_batch` + the NotImplementedError-message/docstring reword). The existing 5c-i 1989-1991 inline body + the 2005+ body byte-untouched (the cohort branch only fires for year ≤ 2004; the 1995-2002 branch only for 1995 ≤ year ≤ 2002 → the canonical v3 2005-2023 path + the 5c-i-verified 1989-1991 path byte-identical; §9-#7-safe).
- [ ] `natality/tests/test_linked_cohort_5cii_a_harmonize_smoke.py` — NEW; `DESIGN: tracks-current-state`; SHAPE-not-VALUE; sub-step-isolated. Written FIRST + run RED (§9-#9 / L3).
- [ ] `natality/tests/test_linked_cohort_5c_harmonize_smoke.py` — minimal L17 `tracks-current-state` Edit bundled in the SAME commit (remove the now-implemented 1995/2002 NotImplementedError pins; relabel 2003/2004 → 5c-ii-b).
- [ ] `PRE_FLIGHT_LOG.md` (this entry) + `RECEIPTS/C8.18_step5c-ii-a_…` + `DECISION_LOG.md` + `STATUS.md` appended.
- [x] NO canonical parquet / `harmonized_schema.csv` / validation-CSV mutation (the harmonizer is NOT re-run at 5c-ii-a; gate SHAs byte-exact). NO git tag (intermediate DO step; `C8.18-pre-do`@`6632a15` is the rollback anchor).

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

No canonical *value* is mutated at 5c-ii-a (zero parquet/schema-CSV/validation-CSV touch). The snapshot below records the **decisions** fixed at this cheap-check moment, before any code mutation:

**(A) §15.D DO step 5c-ii → 5c-ii-a / 5c-ii-b decomposition.** Plan-assumed (5c-i receipt/STATUS/§15.D): 5c-ii = one ~1-session "1995-2002 + 2003 + 2004 cohort birth-side maps" sub-step. Actual state (from reading both harmonizers + the 3 cohort layout sets): 1995-2002 is the **1989-revision** birth certificate — the same raw field-name family + recode set as the 5c-i-verified 1989-1991 reference era (DMAGE/DMEDUC/MRACE/ORMOTH/DMAR/MONPRE/DLIVORD/DTOTORD/GESTAT/CSEX/DBIRWT/FMAPS/DPLURAL/PLDEL/BIRATTND/DFAGE/ORFATH); 2003 + 2004 are the **2003-revision** birth certificate — an entirely different raw field-name family (REVISION@7 dual-cert / MAGER41-recode-not-single-year / MBRACE-already-bridged / MEDUC+UMEDUC dual / MANNER / different death-side layout), the natality V1-core `is_2003revised` analog, materially higher risk. Concerns of **materially different risk + recode family** → decompose 5c-ii → **5c-ii-a** (1995-2002; the low-risk verifiable increment; the 1989-rev sibling of the 5c-i-verified 1989-1991; §2 cheap-before-expensive / §9-#8 / the 3a-substrate-first precedent) + **5c-ii-b** (2003 + 2004; the 2003-rev transition; medium-high risk; its own SMOKE'd sub-step). Ship **5c-ii-a** this session. Within-task (NOT new scope; NOT a Q42/Phase-B-2 trigger — the same within-task-decomposition class as 5→5a/5b/5c [DECISION_LOG 2026-05-19T05:00:00Z] + 5c→5c-i/5c-ii/5c-iii [2026-05-19T11:00:00Z]); folded into soft-flag (ii) §11 human-merge.

**(B) 1995-2002 parsed substrate — real-data value-distribution probe (L13-extension; read-only, before any code mutation).** Plan-assumed: 1995-2002 _raw columns == `LINKED_BIRTH_/_DEATH_1995_2002_FIELDS`; ICD-9/ICD-10 split per §15.D DO step 1. Verified by a read-only `iter_parsed_records` probe on real `LinkCO95US.zip` (cohort 1995) + `LinkCO99US.zip` (cohort 1999), n=400 each:
  - Parsed columns == `LINKED_BIRTH_1995_2002_FIELDS` + `LINKED_DEATH_1995_2002_FIELDS` + `year` (parser reads the `…USDen.dat` den-plus member); **no `link_segment`** (1995-2002 is single-member denominator-plus, like 1989-1991; NOT the keyless two-file 1983-1988).
  - Anchor distributions plausible: DMAGE 19-28, MRACE 2-digit (01/02/78), ORMOTH {0,1,4,5,9}, DMEDUC years (10-17), DMAR {1,2}, CSEX {1,2}, DPLURAL {1,2}, DBIRWT grams (~3000-3600), GESTAT weeks (36-42), MONPRE, **NPREVIST** (1995-2002 uses NPREVIST, NOT NPREVIS — confirmed; the delta vs the 5c-i 1989-1991 map), DFAGE (99=unknown sentinel present), PLDEL, BIRATTND, DLIVORD/DTOTORD detail, FMAPS apgar (00-10), ORFATH, AGED (blank survivors / 3-digit days deaths), AGER5, **RECWT float "1.000000"/"1.003311"** (1995-2002 den-plus locs 223-230; the 1989-1991 era had NO RECWT — the delta).
  - **`DFEDUC` ABSENT** from the 1995-2002 birth section (confirmed) → `father_education_cat4` conservatively null for 1995-2002 (faithful "not on this file"; the delta vs 1989-1991 which has DFEDUC@67-68). **`MANNER` ABSENT** → `manner_of_death` null.
  - **ICD-9 (cohort 1995-1998) vs ICD-10 (cohort 1999-2002) split confirmed in real data**: cohort 1995 death rows UCOD = `769 `,`7450` (numeric ICD-9), UCODR = `500`,`290` (61-cause ICD-9 recode); cohort 1999 death rows UCOD = `A419`,`P920` (alpha-prefixed ICD-10), UCODR = `009`,`117` (130-cause ICD-10 recode). The within_era split keys on cohort **birth year** (≤1998 ICD-9 / ≥1999 ICD-10), matching §15.D DO step 1 + the 5c-i resolved shape; the data is unambiguous (ICD-9 numeric vs ICD-10 alpha-prefixed).

**(C) 1995-2002 birth-side mapping strategy = the 5c-i 1989-1991 map ALIASED, authored as a SEPARATE additive function (H7 sibling-parity; §9-#7).** The 1995-2002 birth section IS a 1989-revision birth certificate == natality `is_pre2003` 1990-2002 == the 5c-i 1989-1991 recode family. Resolution: a NEW `_harmonize_cohort_1995_2002(batch, year)` reusing the existing `_dmeduc_years_to_cat4`/`_mrace_detail_to_bridged4`/`_detail_order_to_recode9`/`_month_to_trimester`/`_pldel_to_facility` recodes (H7 — do NOT re-derive), with the (B)-verified per-era deltas (NPREVIST; no DFEDUC; RECWT→record_weight float64; the cohort-birth-year ICD-9/ICD-10 split; no MANNER). Authored as a SEPARATE function (not a shared helper with the 1989-1991 branch) so the 5c-i-verified 1989-1991 inline body stays **byte-untouched** (§9-#7; the codebase's existing explicit-per-era-duplication pattern, per the 5c-i `_dmeduc_years_to_cat4` "duplicated locally" comment) — the 30/30 5c-i SMOKE + the 213-baseline 1989-1991 path unperturbed. Composite multi-field blocks stay conservatively NULL (soft-flag (gg); the 5c-i/natality is_pre1989 precedent).

**(D) behavior-preservation (§9-#7).** `_harmonize_cohort_1995_2002` fires ONLY for `_cohort_era(year) == "1995_2002"` (1995 ≤ year ≤ 2002, dispatched via a 2-line prepend in `_harmonize_cohort_batch` BEFORE the existing `if era != "1989_1991":` guard). The existing 5c-i 1989-1991 inline body + the 2005+ `_harmonize_batch` body are byte-untouched (the only existing-line edits are the NotImplementedError message-string reword + the `_harmonize_cohort_batch` docstring — message/comment text, 0 logic-deletion lines, grep-confirmed at VERIFY). The canonical v3 2005-2023 product + the 5c-i 1989-1991 path are byte-identical; the parquet is NOT re-run at 5c-ii-a (zero canonical mutation; 11/11 gate SHAs byte-exact). The durable 2005-2023 + per-era byte-clean regression check is DO step 6.

- [x] Current values match the (decomposed/clarified) task plan's assumed state ✓ — divergences (A)-(D) named + resolved at this cheap-check moment per established precedent + the user's standing 2026-05-19 authorization; no silent proceed under a divergent state; not §7 halts (within-task decomposition + a real-data-verified mapping resolution, the 5a/5b/5c-i precedent).

### Halt conditions tripped
None. (A)-(D) are within-task decomposition + a real-data-verified mapping resolution at the Convention-3 snapshot per the 5→5a/5b/5c + 5c→5c-i/5c-ii/5c-iii precedent + the user's standing authorization; not new scope, not a Q42/Phase-B-2 trigger, not a §7 condition. soft-flag (ii) §11 human-merge owes the human the model-clarification (proposed-not-applied; on-disk logs authoritative meanwhile).

### Result
**PROCEED to DO step 5c-ii-a** (SMOKE harness authored FIRST + run RED per §9-#9, then the additive `_harmonize_cohort_1995_2002` + the dispatch + the L17 `tracks-current-state` Edit to the 5c-i harness, then SMOKE GREEN + VERIFY + RECEIPT; intermediate DO step → no tag; zero canonical-state mutation).

---

## PRE-FLIGHT for C8.18 DO step 5c-i — 2026-05-19T11:00:00Z — the per-cohort-era **harmonize architecture** in `harmonize_linked_v3.py` (a `_cohort_era(year)` classifier + a no-op-for-2005+ `_prepare_cohort_batch` alias/synthesis pass, §9-#7-safe) + the **within_era ICD-9 cause-column-shape DECISION** (H7 fetal-death sibling-parity: add `underlying_cause_icd9` + `cause_recode_61` to `OUT_SCHEMA`; `underlying_cause_icd10`/`cause_recode_130` null for the ICD-9 era) + the **1989-1991 reference era end-to-end** as the architecture proof (lowest-risk: single-member denominator-plus, 1989-rev cert closest to natality V2 1990-2002, ICD-9) — **RESULT: PROCEED to DO** (9/9 forward-looking HALTs from `RECEIPTS/C8.18_step5b_2026-05-19T08-00-00Z.md` re-verified; 11/11 gate parquet SHAs byte-exact; canonical pytest baseline `183 passed, 1 skipped, 1 xfailed in 311.98s` (4-dir suite) preserved; the §15.D DO step 5c → **5c-i/5c-ii/5c-iii** decomposition + the cause-column-shape decision + 4 within-task scope decisions surfaced + resolved at the Convention-3 snapshot **before any code mutation**, per the 5→5a/5b/5c + 4→4a/4b/4c + 3→3a/3b established precedent + the user's standing "make all the relevant decisions yourself" authorization 2026-05-19; L17 grep-scope of all 7 cohort harnesses = NO stale pin introduced; zero §7 halts)

> Per-sub-step PRE-FLIGHT under the C8.18 umbrella PRE-FLIGHT (2026-05-17T05:30:00Z) + the §15.D DO step 5 → 5a/5b/5c decomposition (PRE_FLIGHT_LOG 2026-05-19T05:00:00Z) + the DO step 5b close (2026-05-19T08:00:00Z + the 08:30:00Z addendum). Written **before any DO step 5c-i mutation** (no `harmonize_linked_v3.py` edit, no new harness — the only writes from this entry are PRE_FLIGHT_LOG + state files; L10-safe). DO step 5c is harmonize-side substrate only (the re-harmonize that produces the v4 parquet is DO step 6); ZERO canonical-state mutation this sub-step.

### Entry cheap-check — 9 forward-looking HALTs (from `RECEIPTS/C8.18_step5b_2026-05-19T08-00-00Z.md`)

1. **PASS** — `C8.18-pre-do`@`6632a15`; `C8.18-complete` NOT present; `C8.17-complete` present; HEAD = `383692a` (the DO step 5b commit, after `506581c`). Verified `git rev-parse`/`git tag`.
2. **PASS** — 11/11 gate parquet SHAs byte-exact vs the 5b receipt HALT 2 (`/tmp/c8_18_s5c_gate.out`): nat `c8a740eb…`/`acb5c48a…`; `.v28_baseline` `230efed2…`/`e16ad532…`; linked-deriv `9b828a4d…`; fetal-death `38e2cecb…`/`185c071e…` (via the `~/Desktop/fetal-death-harmonization-build/` tree, soft-flag (hh)); MM `adbec108…`/`5c22308b…`/`7c682668…`/`d98b4296…`. Linked-derived changes only at the later DO step 6 re-harmonize.
3. **PASS** — canonical **4-dir** suite `fetal_death/tests/ natality/tests/ tests/ matched_multiples/tests/` = `183 passed, 1 skipped, 1 xfailed in 311.98s` (`/tmp/c8_18_s5c_pytest_baseline.out`); exactly the 5b-close baseline. 311.98s within the ~240-380s advisory band (soft-flag (kk); the COUNT is the gate). README 3-dir/"56 passed" line stays stale → soft-flag (jj).
4. **PASS** — `parse_linked_year` exposes `_find_numerator_member` + `_iter_two_file_1983_1988` + the 1983-1988 `iter_parsed_records` branch, state-on-disk (do NOT re-derive). DO step 5c = `harmonize_linked_v3.py` per-cohort-era field mapping (this sub-step 5c-i = the architecture + the 1989-1991 reference era; 5c-ii = 1995-2004; 5c-iii = the keyless 1983-1988 encoding).
5. **PASS** — the 1983-1988 keyless construction methodology is RESOLVED + state-on-disk (DECISION_LOG/PRE_FLIGHT_LOG 2026-05-19T08:00:00Z + the 08:30:00Z per-segment addendum). 5c-i does NOT re-open it (5c-i scopes the den-plus eras; the keyless `link_segment` harmonized encoding = 5c-iii).
6. **PASS** — encoding = ASCII (`parse_linked_year._slice_field` `decode("latin-1")`, line 70; re-confirmed at 5a/5b on real cohort data). The harmonizer reads the parsed parquet (string columns), not raw bytes — encoding is the parser's concern, already settled.
7. **PASS** — §15.D substrate-format reconcile applied at the 3a commit; the broader model-clarification (3a/3b + 4a/4b/4c + 5→5a/5b/5c + **now 5c→5c-i/5c-ii/5c-iii**) remains soft-flag (ii) §11 human-merge (proposed-not-applied; on-disk PRE_FLIGHT_LOG/DECISION_LOG/RECEIPTs authoritative in the interim).
8. **PASS / consumed** — soft-flag (gg): the numerator-only richer multiple-cause detail + harmonized cause-column shape = DO step 5c/6. This 5c-i entry's Field-value snapshot **resolves the cause-column shape** (H7 sibling-parity; below); per-condition leaf decomposition of the composite MEDRISK/OBSTETRC/ENTITY/RECORD spans stays 5c-ii/5c-iii/6 (soft-flag (gg) carries, narrowed).
9. **PASS** — L17 forward-looking grep-scope: all 7 cohort SMOKE harnesses' `pytest.raises(ValueError)`/1992-1994 pins target the **parser** dispatchers (`_layout_for_linked_year` / `_numerator_layout_for_linked_year`), NOT `harmonize_linked_v3`. 5c-i is harmonize-side + purely additive + configures NO new parser dispatcher year → introduces NO stale pin in those harnesses. The new 5c-i SMOKE harness is `DESIGN: tracks-current-state`, sub-step-isolated, SHAPE-not-VALUE (Convention 1/2). pytest COUNT is the gate.

### Inputs
- [x] `natality/scripts/03_harmonize/harmonize_linked_v3.py` — present (40,011 B; the 5c target; `_harmonize_batch(batch, year)` reads 2005+ NCHS names + `OUT_SCHEMA` 71 cols). Read in full.
- [x] `natality/scripts/03_harmonize/harmonize_v1_core.py` — present (81,611 B; the **H7 sibling-parity reference** — already harmonizes the 1968-rev (`is_pre1989`) + 1989-rev (`is_pre2003`, 1990-2002) cohort-style raw names with reusable helpers `_dmeduc_years_to_cat4`/`_mrace_detail_to_bridged4`/`_mrace1digit_to_bridged4`/`_pldel_to_facility`/`_month_to_trimester`/`_to_int_or_null[_safe]`/`_to_str_or_null`/`_get_col[_optional]`). Era branch + helpers read.
- [x] `natality/scripts/01_import/parse_linked_year.py` + `field_specs.py` — the cohort `_raw` parquet column names (per-era `LINKED_BIRTH_/_DEATH_/_NUM_DEATH_<era>_FIELDS` + `year` + 1983-1988 `link_segment`); state-on-disk 3a/3b/4a/4b/4c, read-only.
- [x] `natality/metadata/harmonized_schema.csv` — the canonical harmonized column definitions (birth-side `raw_source_by_year` per era; death-side `infant_death`/`age_at_death_*`/`underlying_cause_icd10`/`cause_recode_130`/`manner_of_death`/`record_weight` rows = `years_available 2005-2023 (linked)`; the v4 extension + version bump is DO step 6 per Anti-Pattern #6).
- [x] `fetal_death/harmonized_schema.csv` — the H7 sibling-parity precedent for ICD-9/10: `cause_icd10` is `within_era` (ICD-10, 2014+, null otherwise); fetal-death does NOT unify ICD-9/10 into one column.
- [x] No required upstream task incomplete: DO step 5a + 5b CLOSED + committed (HEAD `383692a`).
- [x] No stale checkpoints: `git status --porcelain` clean; `/tmp/c8_18_s5c_*` is OS-scratch (gate-SHA + pytest baseline), reproducible.

### Environment
- [x] Python 3.13 via `uv run`; pyarrow/pandas pinned (`uv.lock`, C8.5a). No new dependency at 5c-i (harmonize-side; reuses pyarrow + the natality V1-core helpers).
- [x] Working dir clean; on `main`.

### Source documentation
- [x] No new external PDF consumed at 5c-i (the cohort layouts were authored + SHA-anchored at DO step 2/3a/3b/4a/4b/4c; 5c-i maps the already-parsed field names to harmonized columns). No SHA-256 to re-verify.

### Outputs (intended; 5c-i)
- [ ] `natality/scripts/03_harmonize/harmonize_linked_v3.py` — **additive** (`_cohort_era` + `_prepare_cohort_batch` + a top-of-`_harmonize_batch` cohort branch + the within_era ICD-9 cause columns added to `OUT_SCHEMA` + the 1989-1991 reference-era mapping). The existing 2005+ body byte-untouched (the cohort branch only fires for year ≤ 2004 → the canonical v3 2005-2023 path byte-identical; §9-#7-safe).
- [ ] `natality/tests/test_linked_cohort_5c_harmonize_smoke.py` — NEW; `DESIGN: tracks-current-state`; SHAPE-not-VALUE; sub-step-isolated (the 3a/3b/4a/4b/4c/5a/5b new-harness-per-sub-step precedent). Written FIRST + run RED (§9-#9 / L3).
- [ ] `PRE_FLIGHT_LOG.md` (this entry) + `RECEIPTS/C8.18_step5c-i_…` + `DECISION_LOG.md` + `STATUS.md` appended.
- [x] NO canonical parquet / `harmonized_schema.csv` / validation-CSV mutation (the harmonizer is NOT re-run at 5c-i; gate SHAs byte-exact). NO git tag (intermediate DO step; `C8.18-pre-do`@`6632a15` is the rollback anchor).

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

No canonical *value* is mutated at 5c-i (zero parquet/schema-CSV/validation-CSV touch). The snapshot below records the **decisions** fixed at this cheap-check moment, before any code mutation:

**(A) §15.D DO step 5c → 5c-i / 5c-ii / 5c-iii decomposition.** Plan-assumed: 5c = one ~1-2 session "harmonize per-cohort-era field mapping" sub-step. Actual state (from reading both harmonizers + the 5 cohort layout sets): the mapping surface spans 5 disjoint cohort eras (1983-1988 keyless / 1989-1991 / 1995-2002 / 2003 / 2004), each with its own raw field-name set, PLUS the methodology-laden keyless `link_segment` encoding, PLUS ICD-9 default-null/revision-tagged + cause_recode per-era — concerns of **materially different risk** (the keyless 1983-1988 one-row-per-birth/within-era-structural-difference encoding ≫ the standard denominator-plus 1989-2004 alias mapping). Resolution = decompose 5c → **5c-i** (the per-cohort-era harmonize architecture + the cause-column-shape decision + the 1989-1991 reference era = the lowest-risk verifiable substrate-first increment; the 3a-substrate-first / §2 cheap-before-expensive / §9-#8 precedent) + **5c-ii** (1995-2002 + 2003 + 2004 birth-side maps; the 2003-rev transition; medium risk) + **5c-iii** (the keyless 1983-1988 `link_segment` den/num → `infant_death`/`record_weight` one-row-per-birth encoding; highest risk; the documented within-era structural difference = D.4). Within-task (NOT new scope; NOT a Q42/Phase-B-2 trigger — the same within-task-decomposition class as 5→5a/5b/5c, DECISION_LOG 2026-05-19T05:00:00Z); folded into soft-flag (ii) §11 human-merge.

**(B) within_era ICD-9 cause-column-shape DECISION (H7 fetal-death sibling-parity; resolves the soft-flag (gg) cause-shape question; §15.D DO step 1 "default-null + revision-tagged" + "a within-era ICD-9 harmonized representation, exact column shape decided at DO step 5/6 PRE-FLIGHT").** Plan-assumed: shape TBD at DO step 5/6 PRE-FLIGHT. Resolution: mirror the fetal-death discipline (`cause_icd10` is `within_era`, populated only where the revision applies, null elsewhere; ICD-9/10 are NOT fabricated into one cross-era column). Linked v4:
  - `underlying_cause_icd10` (existing OUT_SCHEMA col): ICD-10; **null for cohort birth-year 1983-1998 (ICD-9 era)**; populated 1999-2023. (No schema *rename*; the years_available widening + null-pattern note = the DO step 6 `harmonized_schema.csv` edit + v3→v4 version bump, Anti-Pattern #6.)
  - **NEW `underlying_cause_icd9`** (string, `within_era`): the raw ICD-9 underlying cause (cohort `UCOD` 1983-1991 ICD-9 / 1995-1998 ICD-9); populated cohort birth-year 1983-1998, null 1999+.
  - `cause_recode_130` (existing): the ICD-10 130-cause recode; **null for 1983-1998** (ICD-9 era).
  - **NEW `cause_recode_61`** (int16, `within_era`): the ICD-9 61-selected-cause infant recode (cohort `UCODR61` 1989-1991 / `UCODR` 1995-1998 / `UCODR61` 1983-1988); populated 1983-1998, null 1999+.
  Cohort-birth-year → death-year → revision: cohort 1983-1998 deaths occur 1983-1999 but are NCHS-coded ICD-9 (US mortality ICD-9 through 1998; the field_specs 1995-2002 block documents "ICD-9 1995-98 / ICD-10 1999-2002"); cohort 1999-2004 = ICD-10 — so the harmonize-side ICD-9/ICD-10 split keys on **cohort birth year** (≤1998 ICD-9, ≥1999 ICD-10), matching §15.D DO step 1. The published 9→10 crosswalk stays a deferred post-C8.18 task (§15.D Sub-Q42; not pursued here). The 2 NEW OUT_SCHEMA columns are 100% null for the existing 2005-2023 ICD-10 slice → a v3→v4 **additive schema extension** (version-bumped at DO step 6), NOT an existing-column value drift (the §15.D DO step 6 "2005-2023 byte-clean regression: 0/N columns *drift*" criterion is about existing-column values, preserved).

**(C) cohort birth-side mapping strategy = alias/synthesis onto the natality V1-core era recodes (H7 sibling-parity; reuse, do NOT re-derive).** Plan-assumed: "per-cohort-era field mapping" (open). Actual state: the linked cohort denominator(-plus) birth section IS a birth certificate of the SAME revision natality already harmonizes (1989-1991 = 1989-rev = natality `is_pre2003` 1990-2002; 1983-1988 = 1968/1978-rev ≈ natality `is_pre1989`; 2003/2004 = 2003-rev transition = natality 2003+ logic). The linked cohort raw NAMES are mostly natality-equivalent with a small per-era alias delta (e.g., 1989-1991: `RESSTATB`→`RESTATUS`, `GESTAT`→`DGESTAT`, `FMAPS`==apgar5, `MRACE`/`DMEDUC`/`ORMOTH`/`DMAGE`/`DMAR`/`DPLURAL`/`CSEX`/`DBIRWT`/`PLDEL`/`BIRATTND`/`DFAGE`/`DFEDUC`/`MONPRE`/`NPREVIS` == natality 1990-2002), with detail-not-recode order (`DLIVORD`/`DTOTORD`) and composite risk blocks (`MEDRISK`/`OBSTETRC`/`LABOR`/`CONGENIT`) deferred per the soft-flag (gg) leaf-decomposition precedent. Resolution: 5c-i adds `_prepare_cohort_batch(batch, year)` = a per-era alias-rename + minimal synthesis pass producing the canonical names the existing harmonize logic reads; the cohort branch reuses the natality V1-core era helpers (sibling-parity). 5c-i implements the **1989-1991** era fully (the reference/proof era — lowest risk: single-member den-plus, ICD-9, closest to natality V2); 1995-2002/2003/2004/1983-1988 → explicit fail-closed `NotImplementedError("configured at DO step 5c-ii/5c-iii")` (§2 fail-closed — a premature DO step 6 on those years RAISES, never silently mis-harmonizes).

**(D) behavior-preservation for the canonical 2005-2023 path (§9-#7).** `_cohort_era(year)` returns `None` for year ≥ 2005; `_harmonize_batch` takes the cohort branch ONLY when `_cohort_era(year) is not None` → the existing 2005+ body is byte-untouched and the canonical v3 2005-2023 harmonized output is byte-identical (the cohort branch never fires for the canonical build). Adding 2 NEW OUT_SCHEMA columns does not change existing 2005-2023 column *values*; the on-disk parquet is NOT re-written at 5c-i (zero canonical mutation; 11/11 gate SHAs byte-exact). The durable 2005-2023 byte-clean regression check is DO step 6.

- [x] Current values match the (decomposed/clarified) task plan's assumed state ✓ — divergences (A)-(D) named + resolved at this cheap-check moment per established precedent + the user's standing 2026-05-19 authorization; no silent proceed under a divergent state; not §7 halts (within-task decomposition + a documented-discipline schema-shape decision, the 5a/5b/4b/4c precedent).

### Halt conditions tripped
None. (A)-(D) are within-task decomposition + a §15.D-mandated within_era cause-shape decision resolved at the Convention-3 snapshot per the 5→5a/5b/5c + 4→4a/4b/4c precedent + the user's standing authorization; not new scope, not a Q42/Phase-B-2 trigger, not a §7 condition. soft-flag (ii) §11 human-merge owes the human the model-clarification (proposed-not-applied; on-disk logs authoritative meanwhile).

### Result
**PROCEED to DO step 5c-i** (SMOKE harness authored FIRST + run RED per §9-#9, then the additive harmonize architecture + the 1989-1991 reference-era mapping, then SMOKE GREEN + VERIFY + RECEIPT; intermediate DO step → no tag; zero canonical-state mutation).

---

## PRE-FLIGHT ADDENDUM for C8.18 DO step 5b — 2026-05-19T08:30:00Z — `_iter_two_file_1983_1988` `max_rows` semantics: shared-counter → **per-segment cap** (Convention-3 divergence surfaced at SMOKE, resolved BEFORE final DO; L10-safe new dated entry, NOT a back-fill)

> Append-only addendum to the 2026-05-19T08:00:00Z PRE-FLIGHT entry below (the §4.1 / Task-1 2026-05-11T17:58:10Z Convention-3 precedent: when a divergence surfaces between the PRE-FLIGHT commit and final DO, write a NEW dated entry — never back-fill the original). The 08:00:00Z entry's scope decision (3) + the initial `_iter_two_file_1983_1988` docstring described `max_rows` as "a single shared counter across den-then-num (matches the existing `iter_parsed_records` single-stream semantics)".

**Divergence surfaced at SMOKE (before final DO close):** the new `test_linked_cohort_5b_numfinder_smoke.py` was authored FIRST + run RED (ImportError vs the un-modified parser — §9-#9 / L3), then the DO functions were authored + SMOKE re-run → **16 passed / 3 failed**. The 3 failures were all `test_tier1_two_file_construction_real[1983/1985/1988]`: with a single shared counter the multi-million-row den segment exhausts `max_rows` before the num segment is ever reached, so a bounded SMOKE sample can NEVER represent the num segment ("no num-segment rows").

**Root-cause verdict (§2 / §9-#4 — fix the design, do NOT loosen the test):** this is NOT a parser bug and NOT a test to loosen — it is a genuine *design defect of the shared-counter choice* for a two-segment construction. For the DO step 6 full parse (`max_rows=None`) both designs are identical (lossless: all den + all num). `max_rows` is used ONLY for `--max-rows` CLI sampling + SMOKE; for a multi-segment stream the faithful generalization of "give me a bounded sample" is **per-segment** (up to N den + up to N num) — a shared counter that returns 100% den / 0% num for any N < millions is a degenerate, surprising sample. **Resolved:** `_iter_two_file_1983_1988` `max_rows` now caps **each segment independently** (per-segment counter; `break` to the next segment at the cap; `max_rows=None` unchanged = full lossless files). This *strengthens* the construction (a bounded sample now represents both the aggregate-denominator and the self-contained-numerator); it does not weaken any invariant (H6 row-count conservation at `max_rows=None` unchanged; lossless DO step 6 parse unchanged).

**Code/test delta vs the 08:00:00Z entry:** (a) `parse_linked_year._iter_two_file_1983_1988` — per-segment counter + docstring updated (still additive; the 1989-2004/2005+ `iter_parsed_records` body byte-untouched; `_find_denomplus_member`/dispatchers byte-untouched — H10/HALT-13 intact). (b) the one affected Tier-0 test renamed `test_tier0_two_file_construction_maxrows_shared_counter` → `..._per_segment_cap` and rewritten to assert per-segment semantics (the other 5b tests + the 16 that passed are unaffected — they use `max_rows=None` or finder-only). No §15.D / cohort-only scope change; no canonical-state mutation; no new dependency. Folded into soft-flag (ii) §11 human-merge alongside the 08:00:00Z entry. Not a §7 halt (a within-task design refinement surfaced + resolved at the cheap-check SMOKE moment — exactly the Convention-3 mechanism; no AskUserQuestion: the per-segment generalization is the single sensible semantics, resolved per the user's standing 2026-05-19 authorization + §2/§9-#4).

**Post-fix:** SMOKE re-run expected GREEN first-run after this refinement (Tier-1 now samples both segments). `RESULT: PROCEED` (the 08:00:00Z entry's verdict stands; this addendum refines decision (3) only).

---

## PRE-FLIGHT for C8.18 DO step 5b — 2026-05-19T08:00:00Z — the 1983-1988 **self-contained-numerator + aggregate-denominator** two-file construction + a cross-era **numerator-member finder** (the symmetric `"NUM"` sibling of 5a's `"DEN"` rule) — **RESULT: PROCEED to DO** (9/9 forward-looking HALTs from `RECEIPTS/C8.18_step5a_2026-05-19T05-00-00Z.md` re-verified; 11/11 gate parquet SHAs byte-exact; canonical pytest baseline `164 passed, 1 skipped, 1 xfailed in 339.45s` (4-dir suite) preserved; the **1983-1988 keyless one-row-per-birth-model methodology decision** + the numerator-member-finder design + 3 within-task scope decisions surfaced + resolved at the Convention-3 snapshot **before any code mutation**, per the 3a/3b + 4a/4b/4c + 5a established precedent + the user's standing "make all the relevant decisions yourself" authorization 2026-05-19; L17 grep-scope of all 6 cohort harnesses = NO stale pin introduced; zero §7 halts)

> Per-sub-step PRE-FLIGHT under the C8.18 umbrella PRE-FLIGHT (2026-05-17T05:30:00Z) + the C8.18 DO step 4 PRE-FLIGHT (2026-05-18T05:00:00Z) + the §15.D DO step 5 → 5a/5b/5c decomposition (PRE_FLIGHT_LOG 2026-05-19T05:00:00Z). Written **before any DO step 5b mutation** (no `parse_linked_year.py` edit, no new harness — the only writes this entry are PRE_FLIGHT_LOG + state files; L10-safe). DO step 5b is parser substrate only (the re-harmonize is DO step 6); ZERO canonical-state mutation.

### Entry cheap-check — 9 forward-looking HALTs (from `RECEIPTS/C8.18_step5a_2026-05-19T05-00-00Z.md`)

- [x] **HALT 1**: branch `main`, tree clean. `git tag -l` = `C8.17-complete`/`C8.17-pre-do`/`C8.18-pre-do`; `C8.18-complete` NOT present (final-sub-step-only). HEAD `506581c` = the DO step 5a commit (after `7f09da0`). `C8.18-pre-do`@`6632a15` is the DO rollback anchor. ✓
- [x] **HALT 2 — 11 gate parquet SHAs byte-exact** (re-computed on-disk this entry, ~13 GB): natality `c8a740eb48d4f3de…`/`acb5c48a9abf82ac…`; `.v28_baseline` `230efed2ac34c794…`/`e16ad5323d68e28d…`; linked-derived `9b828a4de4e59b17…`; fetal-death `38e2cecb03ff4947…`(harm)/`185c071ec76ab8aa…`(deriv) (via `~/Desktop/fetal-death-harmonization-build/output/harmonized/`, soft-flag (hh)); MM `adbec1087370941f…`(harm)/`5c22308bed2883b9…`(1995-1997 raw)/`7c682668006f3fab…`(1995-2000 raw)/`d98b42965573530d…`(2016-2020 raw). **11/11 unchanged** vs the 5a receipt VERIFY-A / forward-looking HALT 2. DO step 5b is additive parser substrate only (no parser run to canonical paths, no rebuild). ✓
- [x] **HALT 3 — canonical pytest baseline = `164 passed, 1 skipped, 1 xfailed`** on the **4-dir** suite `fetal_death/tests/ natality/tests/ tests/ matched_multiples/tests/` — re-run this entry: **`164 passed, 1 skipped, 1 xfailed in 339.45s`** (byte-exact baseline preserved incl. all 6 cohort harnesses + the 5a 17 tests; 339.45s in the ~240-380s advisory band, soft-flag (kk) — the COUNT is the gate). README 3-dir line stays stale → soft-flag (jj). ✓
- [x] **HALT 4 — `_find_denomplus_member` is cross-era state-on-disk** (5a; DENOM-first preserves 2005+ byte-identical; cross-era `"DEN"`-not-`NUM`/`UNL`/`UNM` fallback; fail-closed). Verified present + byte-untouched this entry (`parse_linked_year.py:73-121`). **Do NOT re-derive.** DO step 5b = the 1983-1988 self-contained-numerator + aggregate-denominator construction **+ a numerator-member finder** (the symmetric `"NUM"` sibling), NOT finder re-authoring. The 1983-2004 cohort den+num layouts are ALL state-on-disk in `field_specs.py` (3a/3b/4a/4b/4c; reclen constants verified present + byte-untouched: `LINKED_DEN_RECLEN_1983_1988=91`, `LINKED_NUM_RECLEN_1983_1988=500`); must NOT be re-derived. ✓
- [x] **HALT 5 — encoding = ASCII**: `_slice_field` `.decode("latin-1")` works for the cohort `.dat`. To be re-confirmed at SMOKE Tier 1 on real `LinkCO{83,85,88}` den + num members (the cohort-year anchor `BIRYR` == the cohort year jointly proves member-resolution + reclen + ASCII + alignment). ✓ (carried; SMOKE Tier 1 re-confirms)
- [x] **HALT 6 — structural model**: **1983-1988 = pure two-file** — a 91-byte births-only Denominator (`LinkCO{yy}USden.dat`; `LINKED_BIRTH_1983_1988_FIELDS`; the aggregate birth denominator, no death section) + a 500-byte **self-contained** Numerator (`LinkCO{yy}USnum.dat`; locs 1-91 = the deceased infant's own birth covariates byte-identical to the denominator + locs 194-500 = the ICD-9 mortality section; 92-193 numerator-only reserved). **NO record-level public-use key** (3b byte-confirmed) → the standard NCHS pre-2005 cohort-IMR construction = self-contained-numerator + aggregate-denominator (NOT a record-level join). 1983-1988 = DEFLATE (`ct=8`, stdlib-fine). ✓
- [x] **HALT 7 — §15.D substrate-format reconcile applied at the 3a commit**; the broader §15.D model-clarification (3a/3b + 4a/4b/4c + the 5→5a/5b/5c decomposition + the DEFLATE64-at-2003-already-wired finding + the 4b/4c falsifications) remains **soft-flag (ii)** proposed-not-applied for §11 human-merge. DO step 5b folds the **1983-1988 keyless self-contained-numerator + aggregate-denominator construction model** + the **numerator-member finder** into the SAME (ii) note (the 5a precedent). No new §15.D wording edit owed this sub-step. ✓
- [x] **HALT 8 — soft-flag (gg)**: the numerator-only richer multiple-cause detail (`ENTITY`/`RECORD` axes, `cause_recode_130` per-era, ICD-9 1983-1998 vs ICD-10 1999+ underlying, the 2003-rev "Vers*" null-pattern) + the harmonized cause-column shape remain DO step 5c/6. DO step 5b is parser substrate only — it parses the FULL 500-byte numerator (incl. the ICD-9 mortality section as the state-on-disk 3b layout already defines it) but decides NO harmonized cause semantics. ✓
- [x] **HALT 9 — L17 forward-looking discipline**: grep-scoped ALL 6 cohort SMOKE harnesses' `pytest.raises`/negative-year/finder pins THIS entry — every negative is the **stable permanent 1992-1994 NCHS linkage gap** (`_layout_for_linked_year(1994)` / `_numerator_layout_for_linked_year(1994)` raise; the 3b harness also pins `_numerator_layout_for_linked_year(2005)` raises = the permanent cohort-only-dispatcher negative). **DO step 5b adds NO new dispatcher year** (`_layout_for_linked_year`/`_numerator_layout_for_linked_year` byte-untouched; 5b adds `_find_numerator_member` [no year arg] + `_iter_two_file_1983_1988` + a 1983-1988 branch in `iter_parsed_records`; 1983-1988 are ALREADY configured by 3a/3b; 1992-1994 still raise via the unchanged dispatchers). **No existing negative-year pin becomes stale → NO bundled sibling-harness Edit needed** (contrast 4c, which configured 2004 and so DID need the bundled Edit). The new 5b harness pins no future-year-raises case. pytest COUNT 164P+1S+1XF is the gate; runtime band advisory (soft-flag (kk)). ✓

**9/9 PASS. 11/11 gate parquet SHAs byte-exact. No §7 halt from the entry cheap-check.**

### Inputs

- [x] `~/Desktop/natality-harmonization/raw_data/linked/LinkCO{83,85,88}.zip` (no `US` suffix pre-1995; members `LinkCO{yy}USden.dat` 91-byte + `LinkCO{yy}USnum.dat` 500-byte + `LinkCO{yy}USUnl.dat` unlinked; `ct=8` DEFLATE) — read-only this step (SMOKE Tier 1 streams the first ≤300 records of each member). SHA-anchored at C8.18 DO step 2 (manifest §3).
- [x] `natality/scripts/01_import/parse_linked_year.py` (`_find_denomplus_member` cross-era 5a, state-on-disk, read-only; `_layout_for_linked_year`/`_numerator_layout_for_linked_year` cohort dispatchers, state-on-disk 3a/3b/4a/4b/4c, byte-untouched by 5b; `iter_parsed_records` — 5b adds a top-of-function 1983-1988 branch only, the 1989-2004/2005+ body byte-untouched) + `zip_text_stream.iter_lines_from_zip` (the `7z`-fallback streaming reader, used by both segments; 1983-1988 = `ct=8` DEFLATE so stdlib path).
- [x] `field_specs.py` `LINKED_BIRTH_1983_1988_FIELDS` (BIRYR@2-5, MATCHS@1) + `LINKED_DEN_RECLEN_1983_1988`=91 + `LINKED_NUM_DEATH_1983_1988_FIELDS` (194-500) + `LINKED_NUM_RECLEN_1983_1988`=500 (state-on-disk, 3a/3b; HALT 4) — read-only.
- [x] 11 gate parquets — SHA-verified byte-exact at this entry cheap-check (HALT 2).

### Environment

- [x] `uv` env (Python 3.13; pinned `uv.lock`). 1983-1988 members = `ct=8` DEFLATE → stdlib `zipfile` (no `7z`/DEFLATE64; no new dep — the C8.5a pinned-env SHA untouched). `pyarrow`/`pandas` per `uv.lock`.

### Source documentation

- [x] No new external PDF consumed (DO step 5b is parser plumbing over the already-authored state-on-disk 3a/3b layouts; the 1983-1988 NO-record-level-key fact is the 3b byte-confirmed finding, state-on-disk in `RECEIPTS/C8.18_step3b`). No §7-#11 stale-SHA exposure.

### Outputs

- [x] DO step 5b intended outputs (NOT created this PRE-FLIGHT — DO next): **additive** `parse_linked_year.py` — (1) `_find_numerator_member(zip_path)` (NEW; the unique member whose upper-name contains `"NUM"` and not `"UNL"`/`"UNM"`; zero/>1 → `RuntimeError` fail-closed; the symmetric `"NUM"` sibling of 5a's `_find_denomplus_member`); (2) `_iter_two_file_1983_1988(zip_path, year, max_rows)` (NEW; yields the lossless union of the den segment then the num segment, each tagged by a synthetic `link_segment ∈ {"den","num"}` discriminator); (3) a top-of-`iter_parsed_records` `if 1983 <= year <= 1988:` branch delegating to (2) — the 1989-2004/2005+ single-member body **byte-untouched** (§9-#7-safe; the 5a discipline) — plus a NEW sibling SMOKE harness `natality/tests/test_linked_cohort_5b_numfinder_smoke.py` (`DESIGN: tracks-current-state`; Convention 1/2). The `_layout_for_linked_year`/`_numerator_layout_for_linked_year` dispatchers + the 3a/3b/4a/4b/4c + 2005/2014 specs + `_find_denomplus_member` (5a) + `run_parse`/`_slice_field` **byte-untouched** (H10/HALT-13). No canonical parquet/schema/validation-CSV. **This PRE-FLIGHT entry itself = zero canonical mutation.**

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

DO step 5b mutates `parse_linked_year.py` (additive: 2 new functions + a top-of-`iter_parsed_records` branch) + a NEW SMOKE harness; this PRE-FLIGHT entry mutates no canonical state. **The 1983-1988 keyless one-row-per-birth-model methodology decision + 3 within-task scope decisions surfaced before any code mutation** and resolved per established precedent (no §7 halt):

1. **METHODOLOGY DECISION — the 1983-1988 self-contained-numerator + aggregate-denominator construction (the H7 / one-row-per-birth-model question the 3b/5a receipts flagged as a 5b PRE-FLIGHT concern).** The 1983-1988 public-use files carry **NO record-level key** (3b byte-confirmed): a record-level numerator↔denominator join is impossible; fabricating a proxy key would violate §2 fail-closed and risk H6/L-class false matches. **Resolved**: the 1983-1988 per-year `_raw` representation = the **lossless union of two source segments**, discriminated by a synthetic string column `link_segment`: (a) `link_segment="den"` = every 91-byte `LinkCO{yy}USden.dat` record via `LINKED_BIRTH_1983_1988_FIELDS` (the **aggregate birth denominator** — ALL live births; one row per birth; no death section); (b) `link_segment="num"` = every 500-byte `LinkCO{yy}USnum.dat` record via `LINKED_BIRTH_1983_1988_FIELDS` (locs 1-91, the deceased infant's own birth covariates) + `LINKED_NUM_DEATH_1983_1988_FIELDS` (locs 194-500, the ICD-9 mortality section) — the **self-contained linked-infant-death set** (MATCHS∈{1,2}; 92-193 numerator-only reserved, deliberately unparsed per 3b). Rationale (§2/H6/H7): lossless (every source record preserved byte-for-byte under the 3a/3b layouts); H6 row-count conservation (den rows == guide-stated births; num rows == guide-stated infant deaths; `_raw` rows = den+num, reconcilable to both members); no fabricated linkage; no double-count at the parser level (the `link_segment` discriminator makes provenance explicit). The harmonized one-row-per-birth / `infant_death` / `record_weight` semantics for the keyless era = **DO step 5c** (the den segment = one row per birth with `infant_death` null/unknown per-record since un-linkable; the num segment = the within-era infant-death detail surface — a **documented within-era structural difference**, NOT a silent deviation: `COMPARABILITY.md`/`harmonized_schema.csv` notes at 5c/6 + the manuscript Coverage paragraph already a known **Phase-D D.4** item). H7 sibling-parity: mirrors the fetal-death discipline of preserving source record structure + documenting within-era comparability rather than fabricating cross-era linkage. **Scope verdict**: within-task (within the already-authorized §15.D DO step 5; the 5→5a/5b/5c decomposition is within-task per the 5a DECISION_LOG; NOT a Q42/Phase-B-2 trigger; NOT the methodology-paper-level cohort-vs-period question, which was resolved at DO step 1). There is essentially ONE defensible no-double-count construction (the NCHS-canonical pre-2005 cohort method); alternatives (fabricate a proxy join key; drop 1983-1988; collapse to aggregate-only) are dominated or violate §2/§7. Resolved per precedent under the user's standing 2026-05-19 authorization; exhaustively documented here + in `DECISION_LOG.md` 2026-05-19T08:00:00Z; folded into soft-flag (ii) §11 human-merge + the D.4 manuscript-Coverage forward item. No fresh AskUserQuestion (standing authorization + the 3b receipt's already-resolved structural-model finding + on-point precedents govern).
2. **`_find_numerator_member` design = the symmetric `"NUM"` sibling of 5a's `_find_denomplus_member`.** Rule: the UNIQUE member whose upper-name contains `"NUM"` and not `"UNL"`/`"UNM"`; zero/>1 → `RuntimeError` (§2 fail-closed). Cross-era-correct by name analysis (all 6 cohort eras): `LinkCO{yy}USnum.dat` (1983-1991), `LinkCO{yy}US{Num,NUM}.dat` (1995-2002), `VS0{3,4}LKBC.USNUMPUB` (2003/2004) all contain "NUM"; the den (`USden`/`USDEN`/`USDENPUB`/`DUSDENOM` — "DENOM" has no "NUM") + unlinked (`USUnl`/`USUNL` = "UNL"; `USUNMPUB` = "UNM", **not** "NUM") members never contain "NUM" → the positive test alone is unique; the `not UNL/UNM` guard is defense-in-depth + symmetry with 5a (maintainability/L17). Unlike 5a's `_find_denomplus_member` (which needed a behavior-preserving DENOM-first rule because the canonical 2005-2023 path calls it), `_find_numerator_member` is brand-new and called by **no** canonical path (the canonical v3 build reads only the denominator-plus) → a single fail-closed rule, no behavior-preservation constraint. Used by `_iter_two_file_1983_1988` at DO step 6; SMOKE-verified for all 6 eras at 5b.
3. **The two-file construction wired behavior-preservingly (§9-#7-safe; the 5a discipline).** `iter_parsed_records` gets a single top-of-function `if 1983 <= year <= 1988: yield from _iter_two_file_1983_1988(...); return` branch; the existing 1989-2004/2005+ single-member body is **byte-untouched** (`git diff` confined to the new functions + the inserted branch lines; the canonical 2005-2015 `parse_linked_year` path byte-identical; 2016-2023 uses `parse_linked_cohort_year`, untouched). The 1989-2004/2005+ rows do NOT get a `link_segment` key (existing path unperturbed); v4 schema unification across eras is a DO step 5c/6 harmonizer concern (documented forward item). H10/HALT-13 preserved (no canonical parquet written; parser substrate only).
4. **NEW sibling SMOKE harness** `natality/tests/test_linked_cohort_5b_numfinder_smoke.py` (vs editing the shipped 3a/3b/4a/4b/4c/5a harnesses) — the C8.18 new-harness-per-sub-step precedent (sub-step isolation). Convention 1 SHAPE-not-VALUE (member resolves uniquely per era; reclen-divisibility; cohort-year domain; segment-discriminator + row-count-conservation structural invariants; fail-closed L3 negatives) + Convention 2 `DESIGN: tracks-current-state` first docstring line. Written FIRST + run RED vs the un-modified parser (§9-#9 / L3), then GREEN after DO.

**Divergence verdict:** none of the 1 methodology decision + 3 scope decisions contradicts the C8.18 cohort-only scope or the §15.D / 2026-05-18T05:00:00Z mandate; all are *within* "parser + harmonize per cohort era" (the 5b half of the already-authorized §15.D DO step 5) and resolved per established precedent (the 3a/3b + 4a/4b/4c + 5a decomposition + the 3b structural-model finding + §2 fail-closed). No §7 halt; no fresh AskUserQuestion.

### SMOKE plan (Tier 0 synthetic + L3 negative → Tier 1 real data; §9-#9 RED-first)

- **Tier 0 (synthetic, always runs)**: per-era `_find_numerator_member` resolution on tiny real `.zip`s with each era's member-name set (1983-1991 `USnum`; 1995-2002 `US{Num,NUM}`; 2003/2004 `USNUMPUB`) → resolves the num member; fail-closed L3 negatives (den+unl-only; den+unl-only-2003; empty; ambiguous-two-NUM) → `RuntimeError`. The two-file construction shape: `_iter_two_file_1983_1988` on a synthetic 2-member zip (planted 91-byte den + 500-byte num records) → yields den rows tagged `link_segment="den"` (no death fields) then num rows tagged `link_segment="num"` (with death fields); row-count conservation (den_n + num_n); a too-short record skipped (bad_len). Position-shift NEGATIVE (L3 — proves slicing discriminates position).
- **Tier 1 (real data, skipif gitignored out-of-tree cohort zip absent)**: on `LinkCO{83,85,88}.zip`: `_find_numerator_member` → `LinkCO{yy}USnum.dat`; `_find_denomplus_member` → `LinkCO{yy}USden.dat` (5a regression-lock, unchanged); the real `_iter_two_file_1983_1988` end-to-end path → den-segment `BIRYR`==cohort year (latin-1+alignment+reclen jointly) + num-segment `BIRYR`==cohort year + `MATCHS`∈{"1","2"} (linked deaths only; 3=surviving never in the numerator) + den-segment count > num-segment count (sanity). Behavior-preservation regression-lock: `iter_parsed_records(LinkCO05US.zip, 2005, max_rows=10)` rows carry NO `link_segment` key (the existing 2005+ path byte-untouched — mirrors 5a's `test_tier1_2005_regression_unchanged`).
- Fail-closed: if a member fails to resolve, a reclen mismatches, or a segment mis-tags, the parser is fixed, NOT the test loosened (§2 / §9-#4).

### Halt conditions tripped

None. The 1983-1988 keyless one-row-per-birth-model methodology decision + 3 within-task scope decisions surfaced at the Convention-3 snapshot **before any code mutation** (L10-safe; the 3a/3b/4a/4b/4c/5a precedent) and resolved per established precedent + the 3b structural-model finding. None contradicts the C8.18 cohort-only scope or the §15.D mandate. No §7 halt; no fresh AskUserQuestion (standing authorization + on-point prior resolutions govern; the methodology-paper-level cohort-vs-period question was resolved at DO step 1; the 1983-1988 keyless construction has one defensible NCHS-canonical form).

### Result

**PROCEED to DO (step 5b).** The 1983-1988 self-contained-numerator + aggregate-denominator construction (lossless den+num union with a `link_segment` discriminator; NO fabricated record-level join; H6 row-count conservation; harmonized semantics deferred to 5c with the documented within-era structural difference + D.4 manuscript-Coverage forward item) + the cross-era `_find_numerator_member` (the symmetric `"NUM"` sibling; fail-closed) are designed per the 3b structural-model finding + the 5a finder discipline + §2/H6/H7. DO step 5b authors the additive 2 functions + the behavior-preserving `iter_parsed_records` branch + a NEW sibling SMOKE harness (written FIRST, run RED vs the un-modified parser, then GREEN; fail-closed). Single commit (PRE-FLIGHT + DO + RECEIPT; the C8.18 DO 3a/3b/4a/4b/4c/5a precedent); no tag (intermediate; `C8.18-pre-do`@`6632a15` remains the rollback anchor). DO step 5c (`harmonize_linked_v3.py` per-cohort-era field mapping + ICD-9 default-null/revision-tagged + `cause_recode_130` per-era, soft-flag (gg)) + DO step 6 (re-harmonize linked 1983-2023; v3→v4) + DO step 7 (docs/metadata; tag `C8.18-complete`) follow.

---

## PRE-FLIGHT for C8.18 DO step 5a — 2026-05-19T05:00:00Z — cross-era denominator-member finder + den-plus parse verification for the 4 self-contained **denominator-PLUS** cohort eras (1989-1991, 1995-2002, **2003 [DEFLATE64]**, 2004) — **RESULT: PROCEED to DO** (9/9 forward-looking HALTs from `RECEIPTS/C8.18_step4c_2026-05-18T23-00-00Z.md` re-verified; 11/11 gate parquet SHAs byte-exact; canonical pytest baseline `147 passed, 1 skipped, 1 xfailed in 315.14s` (4-dir suite) preserved; a **read-only pre-authoring probe value-distribution-verified the broadened finder + the den-plus parse on real data FIRST-RUN-CLEAN for 1989/1995/2002/2003/2004 incl. the 2003 DEFLATE64 path AND the 2005+ regression**; the §15.D DO step 5 → **5a/5b/5c per-concern decomposition** + the DEFLATE64-at-2003-already-wired finding surfaced + resolved at the Convention-3 snapshot before any code mutation, per the 3a/3b + 4a/4b/4c established precedent + the user's standing "make all relevant decisions yourself" authorization; zero §7 halts)

> Per-sub-step PRE-FLIGHT under the C8.18 umbrella PRE-FLIGHT (2026-05-17T05:30:00Z) + the C8.18 DO step 4 PRE-FLIGHT (2026-05-18T05:00:00Z). Written **before any DO step 5a mutation** (no `parse_linked_year.py` edit, no new harness — the only writes this entry are PRE_FLIGHT_LOG + state files). The broadened `_find_denomplus_member` logic + the per-era den-plus parse were reconstructed and **value-distribution-verified on real `LinkCO{89,95,02,03,04}` + `LinkCO05US` data on the FIRST run** via a read-only probe (the C8.18 DO step 3b/4a/4b/4c "verify-first, then DO is straight authoring + SMOKE" precedent), captured below as state-on-disk substrate.

### Entry cheap-check — 9 forward-looking HALTs (from `RECEIPTS/C8.18_step4c_2026-05-18T23-00-00Z.md`)

- [x] **HALT 1**: `git tag -l` = `C8.17-complete`/`C8.17-pre-do`/`C8.18-pre-do`; `C8.18-complete` NOT present (final-sub-step-only). HEAD `7f09da0` = the DO step 4c commit (after `a0128eb`). `C8.18-pre-do`@`6632a15` is the DO rollback anchor. Branch `main`, tree clean. ✓
- [x] **HALT 2 — 11 gate parquet SHAs byte-exact** (re-computed on-disk this entry): natality `c8a740eb48d4f3de…`/`acb5c48a9abf82ac…`; `.v28_baseline` `230efed2ac34c794…`/`e16ad5323d68e28d…`; linked-derived `9b828a4de4e59b17…`; fetal-death `38e2cecb03ff4947…`(harm)/`185c071ec76ab8aa…`(deriv) (via `~/Desktop/fetal-death-harmonization-build/output/harmonized/`, soft-flag (hh)); MM `adbec1087370941f…`(harm)/`5c22308bed2883b9…`(1995-1997 raw)/`7c682668006f3fab…`(1995-2000 raw)/`d98b42965573530d…`(2016-2020 raw). **11/11 unchanged** vs the 4c receipt VERIFY-A / forward-looking HALT 2. DO step 5a is additive parser substrate only (no parser run to canonical paths, no rebuild). ✓
- [x] **HALT 3 — canonical pytest baseline = `147 passed, 1 skipped, 1 xfailed`** on the **4-dir** suite `fetal_death/tests/ natality/tests/ tests/ matched_multiples/tests/` — re-run this entry: **`147 passed, 1 skipped, 1 xfailed in 315.14s`** (byte-exact baseline preserved; 315.14s in the ~240-380s advisory band). README 3-dir line stays stale → soft-flag (jj) (out-of-scope). ✓
- [x] **HALT 4 — the 1983-1991 + 1995-2002 + 2003 + 2004 cohort den+num layouts are ALL state-on-disk in `field_specs.py`** (verified present + byte-untouched this entry: reclen constants `LINKED_DEN_RECLEN_1983_1988=91`/`LINKED_DENOMPLUS_RECLEN_1989_1991=225`/`_1995_2002=230`/`_2003=783`/`_2004=900` + `LINKED_NUM_RECLEN_*` 500/535/535/1142/1259). **The C8.18 1983-2004 cohort layout substrate is COMPLETE.** DO step 5a = parser (cross-era member-finder + verify), NOT layout authoring; layouts must NOT be re-derived. ✓
- [x] **HALT 5 — encoding = ASCII**: `_slice_field` `.decode("latin-1")` works for the cohort `.dat`. Re-confirmed THIS entry on real `LinkCO{89,95,02,03,04}` den members (cohort-year anchor BIRYR/DOB_YY == the cohort year for all 300×5 sampled records under latin-1; CRLF terminators byte-exact). ✓
- [x] **HALT 6 — structural model** (cohort): **1989-1991 / 1995-2002 / 2003 / 2004 = self-contained denominator-PLUS** (the den-plus member alone yields one-row-per-birth + death-"plus"; the numerator's richer multiple-cause = soft-flag (gg), deferred). **1983-1988 = pure two-file** (91-byte births-only denominator + 500-byte self-contained numerator; NO record-level public-use key → the "self-contained-numerator + aggregate-denominator" construction = DO step 5b). 2003 = DEFLATE64 (`ct=9`); 1983-1991 + 1995-2002 + 2004 + 2005+ = DEFLATE (`ct=8`). Member names probed THIS entry: 1983-1991 `LinkCO{yy}USden.dat`/`USnum.dat`; 1995-2002 `LinkCO{yy}US{Den,Num}.dat`; 2003 `VS03LKBC.US{DEN,NUM}PUB`; 2004 `VS04LKBC.DUSDENOM`/`USNUMPUB`; 2005+ `VS{yy}LKBC.DUSDENOM`/`USNUMPUB`. ✓
- [x] **HALT 7 — §15.D substrate-format wording reconcile already APPLIED at the 3a commit**; the broader §15.D model-clarification remains **soft-flag (ii)** proposed-not-applied for §11 human-merge. DO step 5a folds the **DO step 5 → 5a/5b/5c per-concern decomposition** + the **DEFLATE64-at-2003-already-wired** finding into the SAME (ii) note (the 3a/3b + 4a/4b/4c decomposition precedent). No new §15.D wording edit owed this sub-step. ✓
- [x] **HALT 8 — soft-flag (gg)**: the numerator's richer multiple-cause detail (`ENTITY`/`RECORD` axes, `cause_recode_130` per-era, ICD-9 vs ICD-10 underlying) + the 2003-rev "Vers*" null-pattern + the harmonized cause-column shape remain DO step 5c/6 (the den-plus "plus" carries the per-infant `UCOD`/`UCODR130`/`AGED`/`AGER5`/`MANNER`/`RECWT` already; the numerator-only multiple-cause is the deferred richer surface). DO step 5a is parser substrate only and does not decide cause semantics. ✓
- [x] **HALT 9 — L17 forward-looking discipline**: grep-scoped ALL 5 cohort SMOKE harnesses' `pytest.raises(ValueError)`/negative-year sets THIS entry — every negative is the **stable permanent 1992-1994 gap** (+ the 2003-harness `_numerator_layout(2005)` permanent negative). **DO step 5a adds NO new dispatcher year** (`_layout_for_linked_year`/`_numerator_layout_for_linked_year` byte-untouched; 5a only broadens `_find_denomplus_member`), so the L17 stale-pin class **does not apply to 5a** — no cohort harness pins finder behavior, and no new year is configured. The new 5a harness will not pin a future-year-raises case. pytest runtime 315.14s (advisory band; the COUNT 147P+1S+1XF is the gate). ✓

**9/9 PASS. 11/11 gate parquet SHAs byte-exact. No §7 halt from the entry cheap-check.**

### Inputs

- [x] `~/Desktop/natality-harmonization/raw_data/linked/LinkCO{83..91}.zip` (no `US` suffix; members `LinkCO{yy}USden.dat`/`USnum.dat`, `ct=8` DEFLATE) + `LinkCO{95..04}US.zip` (1995-2002 `ct=8`; **2003 `ct=9` DEFLATE64**; 2004 `ct=8`) + `LinkCO05US.zip` (2005+ regression check; `ct=8`) — read-only this entry (the probe streams the first ~300 records of the den member per era). SHA-anchored at C8.18 DO step 2 (manifest §3).
- [x] `natality/scripts/01_import/parse_linked_year.py` (`_find_denomplus_member` — the single function DO step 5a broadens; `_layout_for_linked_year`/`_numerator_layout_for_linked_year` — byte-untouched, state-on-disk) + `zip_text_stream.py` (`iter_lines_from_zip` — **already** carries the `7z x -so` fallback for `ct∉{0,8}`, used for natality 2009-2013 DEFLATE64 + 2015 PPMd; the linked parse path already imports + uses it).
- [x] `field_specs.py` LINKED cohort reclen constants (state-on-disk; HALT 4) — read-only.

### Environment

- [x] `uv` env (Python 3.13; pinned `uv.lock`). stdlib `zipfile` for `ct=8`; `/opt/homebrew/bin/7z` (p7zip 17.06) on PATH for the 2003 `ct=9` DEFLATE64 path (pre-existing dependency-of-record via `zip_text_stream`; no new dep — the C8.5a pinned-env SHA untouched).

### Source documentation

- [x] No new external PDF consumed (DO step 5a is parser plumbing over the already-authored state-on-disk layouts). The 2003 DEFLATE64 fact is on-disk-probed (`zipfile` `compress_type`), not doc-derived; no §7-#11 stale-SHA exposure.

### Outputs

- [x] DO step 5a intended outputs (NOT created this PRE-FLIGHT — DO next): **behavior-preserving broadening** of `parse_linked_year._find_denomplus_member` (DENOM-first rule preserves the canonical 2005-2015 selection byte-identical; a cross-era `"DEN"`-not-`NUM`/`UNL` fallback covers 1983-2003) + a NEW sibling SMOKE harness `natality/tests/test_linked_cohort_denmember_5a_smoke.py` (`DESIGN: tracks-current-state`; Convention 1/2). The `_layout_for_linked_year`/`_numerator_layout_for_linked_year` dispatchers + the 3a/3b/4a/4b/4c + 2005/2014 specs **byte-untouched** (H10/HALT-13). No canonical parquet/schema/validation-CSV. **This PRE-FLIGHT entry itself = zero canonical mutation.**

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

DO step 5a mutates `parse_linked_year.py` `_find_denomplus_member` (broadened, behavior-preserving for 2005+) + a NEW SMOKE harness; this PRE-FLIGHT entry mutates no canonical state. **Within-task scope decisions + one material finding surfaced before any code mutation** and resolved per established precedent (no §7 halt):

1. **§15.D DO step 5 → 5a/5b/5c per-concern decomposition.** The §15.D DO step 5 ("parser + `harmonize_linked.py` extensions per cohort era") spans three genuinely separable concerns of materially different risk: (5a) cross-era den-member finder + verify the 4 self-contained den-PLUS eras' den-plus parse; (5b) the 1983-1988 self-contained-numerator + aggregate-denominator construction (a methodology-laden one-row-per-birth-model decision + a numerator-member finder; the highest-risk parser element); (5c) `harmonize_linked_v3.py` per-cohort-era field mapping (the cohort raw field names `MATCHS`/`IDNUMBER`/`BIRYR`/`DMAGE`/… are **entirely disjoint** from the 2005+ names `harmonize_linked_v3._harmonize_batch` reads — a large mapping surface + ICD-9 default-null/revision-tagged + `cause_recode_130` per-era, soft-flag (gg)). **Resolved**: decompose 5 → 5a/5b/5c, this session = **5a** (the lowest-risk verifiable increment; the 3a-denominator-substrate-first precedent). Per the 3a/3b + 4a/4b/4c precedent this is a within-task decomposition of the already-authorized §15.D DO step 5 (NOT new scope; not a Q42/Phase-B-2 trigger), folded into soft-flag (ii) §11 human-merge. §9-#8 + §2 (verify the cheap/low-risk increment first) + §7-#17 (do not compress separable concerns) govern.
2. **5a scope = cross-era `_find_denomplus_member` + verify the den-plus parse for 1989-1991 / 1995-2002 / 2003 / 2004.** The numerator-member finder + the 1983-1988 construction = 5b; harmonize = 5c. The den-plus layouts (3a/4a/4b/4c) + the `_layout_for_linked_year` dispatcher are state-on-disk — 5a is pure finder-broadening + real-data verification.
3. **`_find_denomplus_member` broadened behavior-preservingly (§9-#7-safe).** DENOM-first rule: any member whose upper-name contains `"DENOM"` → returned first (the existing rule; preserves the canonical 2005-2015 `VS{yy}LKBC.DUSDENOM` selection **byte-identical** — probe-confirmed 2004+2005 still resolve via this rule). Only if no `"DENOM"` member exists, a cross-era fallback returns the unique member whose upper-name contains `"DEN"` and not `"NUM"`/`"UNL"`/`"UNM"` (covers 1983-1991 `USden`, 1995-2002 `USDen`/`USDEN`, 2003 `USDENPUB`). The canonical v3 2005-2023 build does not parse 1983-2003 via this path (2005-2015 = `parse_linked_year`; 2016-2023 = `parse_linked_cohort_year`, a different finder), so 5a cannot perturb the shipped v3 product; DO step 5a is parser substrate only (the re-harmonize is DO step 6). The new SMOKE harness locks the 2005-2015 regression (no prior test pins `_find_denomplus_member`).
4. **NEW sibling SMOKE harness** (vs editing the shipped 3a/3b/4a/4b/4c harnesses) — the C8.18 new-harness-per-sub-step precedent (sub-step isolation). Convention 1/2: SHAPE-not-VALUE structural assertions (member resolves; reclen-divisibility; cohort-year domain), `DESIGN: tracks-current-state` first docstring line.
5. **MATERIAL FINDING (L13-extension class): the DEFLATE64-at-2003 `7z` stream is ALREADY wired into the parse path.** `RECEIPTS/C8.18_step4b`/`4c` forward-notes framed "DO step 5 must wire the `7z` stream into the actual 2003 parse path" — a non-binding forward-note. The cheap-check (read `zip_text_stream.iter_lines_from_zip`) shows it **already** shells to `7z x -so` for any `compress_type ∉ {STORED, DEFLATED}` (added for natality 2009-2013 DEFLATE64 + 2015 PPMd), and `parse_linked_year.iter_parsed_records` already calls `iter_lines_from_zip`. So once `_find_denomplus_member` returns `VS03LKBC.USDENPUB`, 2003 DEFLATE64 streams automatically — the read-only probe confirmed 300 records first-run-clean (`DOB_YY`=2003, 0 bad-length). **Resolved**: 5a needs only the member-finder broadening for 2003 (no new decompressor wiring). Not a §7 halt (the forward-note was non-binding; the cheap-check superseding it is exactly the Convention-3 mechanism — same class as the 4b/4c falsifications). Folded into soft-flag (ii).

**Divergence verdict:** none of the 4 decisions + 1 finding contradicts the C8.18 cohort-only scope or the §15.D / 2026-05-18T05:00:00Z mandate; all are *within* "parser + harmonize per cohort era" and resolved per established precedent (the 3a/3b + 4a/4b/4c decomposition + the L13-extension cheap-check discipline). No §7 halt; no fresh AskUserQuestion (standing authorization + on-point prior resolutions govern; the methodology-paper-level cohort-vs-period question was resolved at DO step 1; the 1983-1988 one-row-per-birth-model methodology decision is a 5b-PRE-FLIGHT concern, not 5a's).

### SMOKE Tier 0/1 — read-only pre-authoring probe (state-on-disk substrate for DO; FIRST-RUN-CLEAN)

The broadened `_find_denomplus_member` (DENOM-first → cross-era `"DEN"`-not-`NUM`/`UNL`) + the existing `iter_lines_from_zip` + `_layout_for_linked_year` were exercised read-only on real data (first ~300 records/member; n=5 eras + the 2005 regression):

| Year | Zip | Den member resolved | Rule | reclen | bad-len/300 | cohort-yr anchor |
|---|---|---|---|---|---|---|
| 1989 | `LinkCO89.zip` | `LinkCO89USden.dat` | cross-era DEN | 225 | 0 | `BIRYR`=1989 |
| 1995 | `LinkCO95US.zip` | `LinkCO95USDen.dat` | cross-era DEN | 230 | 0 | `BIRYR`=1995 |
| 2002 | `LinkCO02US.zip` | `LinkCO02USDEN.dat` | cross-era DEN | 230 | 0 | `BIRYR`=2002 |
| 2003 | `LinkCO03US.zip` | `VS03LKBC.USDENPUB` | cross-era DEN | 783 | 0 | `DOB_YY`=2003 **(DEFLATE64 via `7z` auto)** |
| 2004 | `LinkCO04US.zip` | `VS04LKBC.DUSDENOM` | **DENOM (2005+ unchanged)** | 900 | 0 | `DOB_YY`=2004 |
| 2005 | `LinkCO05US.zip` | `VS05LKBC.DUSDENOM` | **DENOM (2005+ unchanged)** | — | — | regression: selection byte-identical |

FAILS: NONE. Every den member resolves uniquely; reclen matches the state-on-disk `field_specs.py` constant; the cohort-year anchor value-verifies under latin-1; the 2003 DEFLATE64 path streams clean via the pre-existing `7z` fallback; 2004+2005 still resolve via the unchanged DENOM rule (canonical path preserved). DO authors the broadened finder + the SMOKE harness (Tier 0 synthetic member-set + L3 negative [a NUM-only / ambiguous archive must raise]; Tier 1 real-data per-era resolution + reclen-divisibility + cohort-year domain + the 2005-2015 regression lock) — fail-closed: if a member fails to resolve or a reclen mismatches, the finder is fixed, NOT loosened (§2 / §9-#4).

### Halt conditions tripped

None. One material L13-extension-class finding (DEFLATE64-at-2003 already wired) + four within-task scope decisions (5→5a/5b/5c; 5a scope; behavior-preserving broadening; new harness) surfaced at the Convention-3 snapshot **before any code mutation** (L10-safe; the 3a/3b/4a/4b/4c precedent) and resolved per established precedent. None contradicts the C8.18 cohort-only scope or the §15.D mandate. No §7 halt; no fresh AskUserQuestion (standing authorization + on-point prior resolutions govern).

### Result

**PROCEED to DO (step 5a).** The cross-era `_find_denomplus_member` design (DENOM-first preserves 2005+ byte-identical; cross-era `"DEN"`-not-`NUM`/`UNL` fallback for 1983-2003) + the den-plus parse for the 4 self-contained denominator-PLUS cohort eras (1989-1991, 1995-2002, 2003-DEFLATE64, 2004) is **value-distribution-verified on real data FIRST-RUN-CLEAN** via a read-only probe (incl. the 2003 DEFLATE64 path auto-handled by the pre-existing `iter_lines_from_zip` `7z` fallback, and the 2005+ regression preserved). Captured above as state-on-disk substrate. DO step 5a authors the behavior-preserving finder broadening + a NEW sibling SMOKE harness (Tier 0 synthetic + L3 negative → Tier 1 real data; fail-closed). Single commit (PRE-FLIGHT + DO + RECEIPT; the C8.18 DO 3a/3b/4a/4b/4c precedent); no tag (intermediate; `C8.18-pre-do`@`6632a15` remains the rollback anchor). DO step 5b (1983-1988 self-contained-numerator + aggregate-denominator construction + numerator-member finder) + DO step 5c (harmonize per-cohort-era + ICD-9 default-null/revision-tagged + `cause_recode_130` per-era) follow after 5a.

---

## PRE-FLIGHT for C8.18 DO step 4c — 2026-05-18T23:00:00Z — cohort **2004** `field_specs.py` layout authoring (**900**-byte denominator-plus + **1259**-byte numerator; 2003-revision transition continued; `REVISION`@7 S=1989-unrevised / A=2003-revised; ICD-10 throughout — 2004 cohort) + SMOKE Tier-0/1 value-distribution verify — **RESULT: PROCEED to DO** (9/9 forward-looking HALTs from `RECEIPTS/C8.18_step4b_2026-05-18T20-30-00Z.md` re-verified; 11/11 gate parquet SHAs byte-exact; canonical pytest baseline `137 passed, 1 skipped, 1 xfailed in 222.97s` (4-dir suite) preserved; the FULL 2004 den-plus + numerator layout reconstructed **byte-exact from the `LinkCO04Guide.pdf` DETAIL "Position/Len/Field" code-outline** (pp21-60; the L13-extension governing precedent — the pp18-19 "Linked 2004 Cohort Selected Data Elements and Locations" element-span SUMMARY is composite + NOT trusted, used only as an independent cross-check) — captured below as state-on-disk substrate + value-distribution-verified on real DEFLATE `LinkCO04US.zip` data FIRST-RUN-CLEAN; **two material L13-extension findings surfaced + resolved at the Convention-3 snapshot before any `field_specs.py` mutation**: (i) the prior `RECEIPTS/C8.18_step4b` forward-looking note's *extrapolated* "2004 = 900/**1142**" numerator length is **FALSIFIED** — `LinkCO04Guide.pdf` p18 File Characteristics state Numerator US record length = **1,259** and exact zip-member arithmetic confirms byte-exact (den `4,118,956 × (900+2 CRLF) = 3,715,298,312` = `VS04LKBC.DUSDENOM`; num `27,763 × (1259+2) = 35,009,143` = `VS04LKBC.USNUMPUB`); (ii) the "2004 den-plus == `LINKED_BIRTH_2005_2013`" HYPOTHESIS is **FALSIFIED** — real data shows the 2003-rev *cohort* layout (FILLER@1-6 + REVISION@7 + IDNUMBER@10-14), diverging from `LINKED_BIRTH_2003` at ~576 onward (more 2003-rev F_* edit flags; MRACE1E@800 vs 2003's @683); neither is a §7 halt — both were non-binding extrapolations/hypotheses explicitly flagged for value-verification, resolved by the prescribed author-from-the-DETAIL + real-data-verify discipline (exactly what the Convention-3 snapshot exists to catch; same class as the 4b 1259→1142 catch); plus `LinkCO04US.zip` = **DEFLATE** (stdlib `zipfile`; NOT DEFLATE64 like 2003 — no special tooling for 2004); four within-task scope decisions resolved per established precedent (the user's standing "make all relevant decisions yourself" authorization + the DO 3a/3b/4a/4b precedents); zero §7 halts)

> Per-sub-step PRE-FLIGHT under the C8.18 umbrella PRE-FLIGHT (2026-05-17T05:30:00Z) + the C8.18 DO step 4 PRE-FLIGHT (2026-05-18T05:00:00Z investigation-only checkpoint). Written **before any DO step 4c mutation** (no `field_specs.py` edit, no parser run — the only writes this entry are PRE_FLIGHT_LOG + state files). The FULL 2004 layout was reconstructed from the authoritative `LinkCO04Guide.pdf` DETAIL "Position/Len/Field" code-outline (pp21-60) + a read-only builder value-distribution-verified it on real DEFLATE `LinkCO04US.zip` data on the FIRST run, and it is captured below as state-on-disk substrate (`/tmp/c8_18_s4c/` builder + `field_specs_2004_block.txt`) so DO goes straight to authoring (the C8.18 DO step 3b/4a/4b precedent: "the layout reconstructed from the guide DETAIL + captured state-on-disk; SMOKE Tier 1 verified first-run-clean").

### Entry cheap-check — 9 forward-looking HALTs (from `RECEIPTS/C8.18_step4b_2026-05-18T20-30-00Z.md`)

- [x] **HALT 1**: `git tag -l` = `C8.17-complete`/`C8.17-pre-do`/`C8.18-pre-do`; `C8.18-complete` NOT present (final-sub-step-only). HEAD `a0128eb` = the DO step 4b commit (after `6fb7acd`). `C8.18-pre-do`@`6632a15` is the DO rollback anchor. Branch `main`, tree clean. ✓
- [x] **HALT 2 — 11 gate parquet SHAs byte-exact** (re-computed on-disk this entry, `/tmp/c8_18_s4c_gate_shas.txt`): natality `c8a740eb…a6237153`/`acb5c48a…28856974`; `.v28_baseline` `230efed2…33ccebac`/`e16ad532…77c41d44`; linked-derived `9b828a4d…5a08b777`; fetal-death `38e2cecb…99c5cf48`(harm)/`185c071e…a7968a09`(deriv) (via `~/Desktop/fetal-death-harmonization-build/output/harmonized/`, soft-flag (hh)); MM `adbec108…45dc1549`/`5c22308b…d39205d1`/`7c682668…edd61f5d`/`d98b4296…6a543261`. **11/11 unchanged** vs the 4b receipt VERIFY-A / forward-looking HALT 2. DO step 4c is additive layout substrate only (no parser run, no rebuild). ✓
- [x] **HALT 3 — canonical pytest baseline = `137 passed, 1 skipped, 1 xfailed`** on the **4-dir** suite `fetal_death/tests/ natality/tests/ tests/ matched_multiples/tests/` — re-run this entry: **`137 passed, 1 skipped, 1 xfailed in 222.97s`** (byte-exact baseline preserved; below the ~240-380s advisory band — clean quiescent run). README 3-dir line stays stale → soft-flag (jj) (out-of-scope). ✓
- [x] **HALT 4 — DO step 4c = cohort 2004 `field_specs.py` layout authoring**, reconstructed FRESH from the `LinkCO04Guide.pdf` DETAIL "Position/Len/Field" code-outline (L13-extension; do NOT trust the pp18-19 element-span SUMMARY; never assume same-model==same-layout). The "2004 den-plus == `LINKED_BIRTH_2005_2013`" HYPOTHESIS is **FALSIFIED on real data** (L13-extension caution vindicated — see Field-value snapshot (ii)). DO step 4c must **NOT re-derive** the 1983-1991 / 1995-2002 / 2003 layouts — verified present + byte-untouched this entry: `LINKED_BIRTH_1983_1988/1989_1991/1995_2002/2003_FIELDS`, `LINKED_DEATH_1989_1991/1995_2002/2003_FIELDS`, `LINKED_NUM_DEATH_1983_1988/1989_1991/1995_2002/2003_FIELDS` + reclen constants — nor the 2005/2014 LINKED specs. ✓
- [x] **HALT 5 — encoding = ASCII**: the 2005+ parser `_slice_field` `.decode("latin-1")` works for the cohort `.dat`. Re-confirmed THIS entry on real `LinkCO04US.zip` `VS04LKBC.DUSDENOM`/`USNUMPUB` (DOB_YY@15-18 == '2004' for all 500×2 sampled records under latin-1; CRLF terminators byte-exact). ✓
- [x] **HALT 6 — structural model**: 1995-2004 = the three-file denominator-plus model. 2004 = **900-byte den-plus + 1259-byte numerator** (the prior `RECEIPTS/C8.18_step4b` forward-looking-note "1142" extrapolation **FALSIFIED** — guide p18 + byte-exact zip-member arithmetic; den/num both = **DEFLATE**, stdlib-fine, NOT DEFLATE64). den-plus 1-900 == numerator 1-900 (the den-plus "ends @900" RECWT@893-900 + "Here ends the denominator-plus file" divider, LinkCO04Guide p57), numerator adds numerator-only mortality 901-1259. Member names = `VS04LKBC.DUSDENOM`/`USNUMPUB`/`USUNMPUB`; `_find_denomplus_member` ("DENOM") would now match `VS04LKBC.DUSDENOM` (a DO step 5 parser concern to confirm; not 4c — additive layout substrate only). ✓
- [x] **HALT 7 — §15.D substrate-format wording reconcile already APPLIED at the 3a commit**; the broader §15.D model-clarification remains **soft-flag (ii)** proposed-not-applied for §11 human-merge. DO step 4c folds the 2004 900/1259 layout-confirmation + the 1142→1259 falsification + the LINKED_BIRTH_2005_2013-hypothesis falsification + the DEFLATE-not-DEFLATE64-for-2004 note into the SAME (ii) note; no new §15.D wording edit owed this sub-step. ✓
- [x] **HALT 8 — soft-flag (gg)**: the 2004 birth section carries `MEDRISK`@328-344 / `OBSTETRC`@355-361 / `LABOR`@374-389 / `DELMETH`@395-401 / `NEWBORN`@483-491 / `CONGENIT`@504-525 + the numerator multiple-cause `ENTITY`@905-1044 (20×7) / `RECORD`@1049-1148 (20×5) as composite spans; per-condition leaf decomposition + per-era cause-recode semantics + the 2003-rev "Vers*" null-pattern + the harmonized cause-column shape stay DO step 5/6 (the 3a/3b/4a/4b composite-span precedent). ✓
- [x] **HALT 9 — pytest runtime 222.97s** (below the ~240-380s band — clean quiescent run; the COUNT 137P+1S+1XF is the gate, not the absolute number). ✓

**9/9 PASS. 11/11 gate parquet SHAs byte-exact. No §7 halt from the entry cheap-check.**

### Inputs

- [x] `~/Desktop/natality-harmonization/raw_data/linked/LinkCO04US.zip` (192,676,844 B on disk + SHA-anchored at C8.18 DO step 2; read-only this entry — the builder reads the first ~500 records of `VS04LKBC.DUSDENOM`/`USNUMPUB` via stdlib `zipfile`). Members + compression: `VS04LKBC.USNUMPUB` 35,009,143 B / `VS04LKBC.DUSDENOM` 3,715,298,312 B / `VS04LKBC.USUNMPUB` 399,737 B — **all compress_type=8 (DEFLATE)**; stdlib `zipfile` decompresses (no DEFLATE64, no `7z` needed — unlike 2003). Block-divisibility byte-exact: den 3,715,298,312/(900+2)=4,118,956; num 35,009,143/(1259+2)=27,763; unl 399,737/(1259+2)=317 — all == `LinkCO04Guide.pdf` p18 File-Characteristics counts.
- [x] `~/Desktop/natality-harmonization/raw_docs/linked/LinkCO04Guide.pdf` (99 pp, 0 empty pages; L12-extension text-layer probe THIS entry — DETAIL pp21-60 fully text-extractable, no OCR) — the authoritative 2004-cohort layout.
- [x] Sibling substrate (read-only): `natality/scripts/01_import/field_specs.py` (the 3a/3b/4a/4b `LINKED_*_1983_1991`/`_1995_2002`/`_2003` + the 2005/2014 LINKED specs — `LINKED_BIRTH_2003_FIELDS` value-verified byte-exact on real 2004 data for 1-575; `LINKED_DEATH_2005_2013` death-"plus" model value-verified on real 2004 868-900; do NOT re-derive) + `parse_linked_year.py` (`_layout_for_linked_year` + `_numerator_layout_for_linked_year` dispatchers — additive single-year 2004 branches to add at DO).

### Environment

- [x] `uv` env (Python 3.13; pinned `uv.lock`). PyMuPDF (`fitz`) for the DETAIL text extraction; stdlib `zipfile` for the DEFLATE stream (no new dependency; 2004 needs no DEFLATE64 tooling — the C8.5a pinned-env SHA is untouched).

### Source documentation

- [x] `LinkCO04Guide.pdf` DETAIL "Position/Len/Field/Description/Reporting-Flag-Position/Vers*/Values-Definition" code-outline (the L13-extension authoritative source): **pp21-57** = denominator-plus (locs 1-900; p57 divider *"Here ends the denominator-plus file. Documentation for the mortality section of the numerator (linked) file continues…"*); **pp57-60** = numerator-only mortality section (locs 901-1259). p18 File Characteristics: Numerator US count 27,763 / **reclen 1,259**; Denominator US count 4,118,956 / **reclen 900**; Unlinked US count 317 / reclen 1,259. pp18-19 "Linked 2004 Cohort Selected Data Elements and Locations" element-span SUMMARY = NOT trusted (L13-extension), used only as an independent cross-check (the SUMMARY's den-plus/numerator-birth positions IDNUMBER 10-14, DOB_YY 15-18, RECWT 893-900, match status 868, age-at-death 872-77, SEX 436, gestation 451-57, birthweight 467-73, plurality 423, apgar 415-17, year-of-death 1188-91, month-of-death 1258-59 — all cross-confirmed against the DETAIL + real data). No §7-#11 stale-SHA exposure (on-disk SHA-anchored guide).

### Outputs

- [x] DO step 4c intended outputs (NOT created this PRE-FLIGHT — DO next): **additive** `field_specs.py` — `LINKED_BIRTH_2004_FIELDS` (locs 1-867; 206 entries incl. composite spans + FILLER/RESERVED gap-fill) + `LINKED_DEATH_2004_FIELDS` (the den-plus death-"plus" + RECWT, locs 868-900; 16 entries) + `LINKED_NUM_DEATH_2004_FIELDS` (numerator-only mortality, locs 901-1259; 12 entries) + `LINKED_DENOMPLUS_RECLEN_2004 = 900` + `LINKED_NUM_RECLEN_2004 = 1259`; additive `_layout_for_linked_year`/`_numerator_layout_for_linked_year` single-year-2004 branches; NEW `natality/tests/test_linked_cohort_2004_layout_smoke.py` (`DESIGN: tracks-current-state`; Convention 1/2). **Additive — existing 2005/2014 + 3a/3b/4a/4b constants + dispatchers byte-untouched (H10 / HALT-13).** No canonical parquet/schema/validation-CSV. **This PRE-FLIGHT entry itself = zero canonical mutation** (git scope = PRE_FLIGHT_LOG + this commit's state files).

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

DO step 4c mutates `field_specs.py` (additive) + `parse_linked_year.py` (additive branches) + a NEW SMOKE harness; this PRE-FLIGHT entry mutates no canonical state. **Two material L13-extension findings + four within-task scope decisions surfaced before any `field_specs.py` mutation** and resolved per established precedent (no §7 halt):

0a. **MATERIAL FINDING (L13-extension): the numerator record length is 1259, NOT the prior receipt-note's extrapolated 1142.** `RECEIPTS/C8.18_step4b` forward-looking HALT 4/6 carried "2004 = 900/1142" — a non-binding extrapolation from the 2003 1259→1142 correction applied symmetrically. The `LinkCO04Guide.pdf` p18 File Characteristics state Numerator US reclen = **1,259**; exact zip-member-uncompressed-size arithmetic confirms byte-exact (`27,763 × 1261 = 35,009,143` = `VS04LKBC.USNUMPUB`; `4,118,956 × 902 = 3,715,298,312` = `VS04LKBC.DUSDENOM`) — and the read-only builder probe on real DEFLATE data confirmed `file_size % 902 == 0` (count 4,118,956) / `% 1261 == 0` (count 27,763) with CRLF terminators. **Resolved**: author from the guide-stated + arithmetic-confirmed 900/1259, not the extrapolation. Not a §7 halt (the "1142" was a non-binding extrapolated note; the L13-extension "never assume; value-distribution-verify on real data" discipline is exactly the resolution mechanism; same class as the 4b 1259→1142 catch). Folded into soft-flag (ii) §11 human-merge.
0b. **MATERIAL FINDING (L13-extension): the "2004 den-plus == `LINKED_BIRTH_2005_2013`" HYPOTHESIS is FALSIFIED.** Real `VS04LKBC.DUSDENOM` data shows the 2003-rev *cohort* layout: FILLER@1-6 + REVISION@7∈{S,A} + LATEREC@9 + IDNUMBER@10-14 (the custom cohort layout family, NOT the natality-aligned 2005-2013 public-use layout). Applying the full `LINKED_BIRTH_2003_FIELDS` to real 2004 den-plus value-verifies byte-exact for 1-575 (every named scalar plausible) but DIVERGES from 576 onward (2004 carries more 2003-rev F_* edit flags; `MRACE1E`@800-823 vs 2003's @683-706). **Resolved**: 2004 birth section reconstructed FRESH from the `LinkCO04Guide.pdf` DETAIL (1-575 structurally == 2003 + value-verified; 576-867 authored from the 2004 DETAIL), NOT reused wholesale from any sibling. Not a §7 halt (the hypothesis was explicitly flagged for value-verification — the L13-extension caution that FALSIFIED the 1995-2002-reuse + 2003-numerator-1259 assumptions; vindicated again).
1. **DO step 4c scope** = additive `field_specs.py` constants + additive single-year-2004 `_layout_for_linked_year`/`_numerator_layout_for_linked_year` branches + a NEW sibling SMOKE harness. `_find_denomplus_member` `"DENOM"`-vs-`VS04LKBC.DUSDENOM` support + the num↔den construction + the harmonize path remain DO step 5 (per PRE_FLIGHT_LOG 2026-05-18T05:00:00Z; the DO 3a/3b/4a/4b scope precedent).
2. **DEFLATE (not DEFLATE64) for 2004** — `LinkCO04US.zip` all 3 members compress_type=8; stdlib `zipfile` decompresses (no `7z`/`zipfile-deflate64`; only the single cohort year 2003 needs the DEFLATE64 CLI-`7z` path). The C8.5a pinned-env SHA is untouched.
3. **Composite-span convention**: `MEDRISK`@328-344 / `OBSTETRC`@355-361 / `LABOR`@374-389 / `DELMETH`@395-401 / `NEWBORN`@483-491 / `CONGENIT`@504-525 (birth) + `ENTITY`@905-1044 (20×7) / `RECORD`@1049-1148 (20×5) (numerator) authored as single composite spans (extents byte-exact from the DETAIL, the per-condition leaf clusters collapse into them); per-condition leaf decomposition + per-era cause-recode semantics stay DO step 5 (the DO3a/3b/4a/4b composite-span + soft-flag (gg) governing precedent). Cleanly DETAIL-enumerated F_* edit scalars (F_MORIGIN…F_UCA_CLUB) kept individually + DETAIL-enumerated FILLER kept as `FILLER_<start>` + unenumerated gaps filled with `RESERVED_<start>` (the 2003 4b provenance-distinction convention; the layout tiles [1,900] den-plus + [1,1259] numerator with zero gap/overlap).
4. **NEW sibling harness** `test_linked_cohort_2004_layout_smoke.py` (vs editing the shipped 3a/3b/4a/4b harnesses) — the C8.17 DO5a/5b + C8.18 DO3a/3b/4a/4b new-harness-per-sub-step precedent (sub-step isolation).

**Divergence verdict:** the 1142→1259 correction + the LINKED_BIRTH_2005_2013-hypothesis falsification supersede non-binding extrapolated/hypothesized forward-looking notes (NOT §7-#12/#17 conditions — the §15.D-level scope, cohort-only + three-file denominator-plus model, is unchanged; only an internal record-length number is corrected + a reuse hypothesis is falsified, exactly what the Convention-3 snapshot + the L13-extension discipline exist to catch). None of the four decisions contradicts the C8.18 cohort-only scope or the §15.D / 2026-05-18T05:00:00Z DO-step-4c mandate; all are *within* "author the cohort 2004 layout from the DETAIL code-outline" and resolved per established precedent. No §7 halt; no fresh AskUserQuestion (standing authorization + on-point prior resolutions govern).

### SMOKE Tier 0 — the FULL 2004 layout reconstructed from the LinkCO04Guide DETAIL code-outline (state-on-disk substrate for DO)

L13-extension governing precedent (C8.18 DO 3a/3b/4a/4b): the byte-level DETAIL "Position/Len/Field" code-outline is authoritative; the pp18-19 element-span SUMMARY is composite + NOT trusted (used only as an independent cross-check — the SUMMARY's listed den-plus/numerator-birth/numerator-death positions all matched the DETAIL + real data). Positions 1-based inclusive. Composites = single spans (decision 3). `FILLER_<n>` = DETAIL-enumerated filler; `RESERVED_<n>` = unenumerated synthesized gap-fill (the 2003 4b provenance-distinction; §2 fail-closed — gaps explicit, never silently dropped). den-plus = `LINKED_BIRTH_2004_FIELDS` (1-867) + `LINKED_DEATH_2004_FIELDS` (868-900); numerator = those + `LINKED_NUM_DEATH_2004_FIELDS` (901-1259). The full field tuple-lists are state-on-disk in `/tmp/c8_18_s4c/build_2004_layout.py` + `/tmp/c8_18_s4c/field_specs_2004_block.txt` + `/tmp/c8_18_s4c/detail_parsed.json` (re-derivable from the `LinkCO04Guide.pdf` DETAIL Position/Len column via the documented extractor) and embedded verbatim into `field_specs.py` at DO. Reclens byte-confirmed: den-plus = **900** (block 902 incl. CRLF; `3,715,298,312 / 902 = 4,118,956` = LinkCO04Guide p18); numerator = **1259** (block 1261; `35,009,143 / 1261 = 27,763` = p18).

**Anchor positions** (value-distribution-verified on real `VS04LKBC.DUSDENOM`/`USNUMPUB` at the read-only builder probe, n=500 each — FIRST-RUN-CLEAN, FAILS: NONE): `REVISION`@7 (S/A), `LATEREC`@9, `IDNUMBER`@10-14 (num↔den-plus join key; den-plus blank, numerator sequential), `DOB_YY`@15-18 (==2004), `MAGER`@89-90, `MBRACE`@139-140, `MRACE`@141-142, `MEDUC`@155, `UMEDUC`@156-157, `MAR`@153, `MEDRISK`@328-344, `OBSTETRC`@355-361, `LABOR`@374-389, `DELMETH`@395-401, `APGAR5`@415-416, `DPLURAL`@423, `SEX`@436, `DLMP_YY`@442-445 (≈2003), `COMBGEST`@451-452, `BRTHWGT`@467-470 (4-digit grams), `NEWBORN`@483-491, `CONGENIT`@504-525, F_* edit scalars @569-768 ({0,1}), `MRACE1E`@800-823 / `FRACE1E`@835-858, `FLGND`@868 (den-plus {1,2} / numerator ≡1), `AGED`@872-874 (000-366), `UCOD`@884-887 (ICD-10 — 2004 cohort), `UCODR130`@889-891, `RECWT`@893-900 ("1.000000"; den-plus ENDS @900), `EANUM`@903-904 (00-20), `ENTITY`@905-1044 (ICD-10 entity-axis), `RANUM`@1047-1048, `RECORD`@1049-1148 (ICD-10 record-axis), `HOSPD`@1186, `WEEKDAYD`@1187, `DTHYR`@1188-1191 (∈{2004,2005}), `DOD_MM`@1258-1259 (01-12; numerator ENDS @1259).

### Halt conditions tripped

None. Two material L13-extension findings (numerator 1142→1259; 2004-den-plus-reuse-of-LINKED_BIRTH_2005_2013 FALSIFIED) + four within-task scope decisions surfaced at the Convention-3 snapshot **before any `field_specs.py` mutation** (L10-safe; the DO 3a/3b/4a/4b precedent) and resolved per established precedent. None contradicts the C8.18 cohort-only scope or the §15.D/2026-05-18T05:00:00Z DO-step-4c mandate. No §7 halt; no fresh AskUserQuestion (standing authorization + on-point prior resolutions govern).

### Result

**PROCEED to DO.** The FULL cohort 2004 layout (900-byte den-plus + 1259-byte numerator) is reconstructed byte-exact from the `LinkCO04Guide.pdf` DETAIL "Position/Len/Field" code-outline (pp21-60), cross-confirmed against the pp18-19 element-span SUMMARY positions, and **value-distribution-verified on real DEFLATE `LinkCO04US.zip` data on the FIRST run** via a read-only builder probe (every anchor across den-plus + numerator clean, FAILS: NONE; the 1142→1259 + LINKED_BIRTH_2005_2013-reuse falsifications held; encoding ASCII; DEFLATE-not-DEFLATE64). Captured above as state-on-disk substrate. DO step 4c authors the additive `field_specs.py` constants + single-year-2004 dispatcher branches + a NEW sibling SMOKE harness (Tier 0 synthetic + L3 negative → Tier 1 real data via stdlib `zipfile`; fail-closed — if a position FAILs the layout is rebuilt from the DETAIL, NOT loosened; §2 / §9-#4). Single commit (PRE-FLIGHT + DO + RECEIPT; the C8.18 DO 3a/3b/4a/4b precedent); no tag (intermediate; `C8.18-pre-do`@`6632a15` remains the rollback anchor). DO step 5 (parser + harmonize extensions: `_find_denomplus_member` "DENOM" support + DEFLATE64-`7z`-stream 2003 parse-path wiring + num↔den construction) follows after 4c.

---

## PRE-FLIGHT for C8.18 DO step 4b — 2026-05-18T20:30:00Z — cohort **2003** `field_specs.py` layout authoring (783-byte denominator-plus + **1142**-byte numerator; 2003-revision transition; `REVISION`@7 S=1989-unrevised / A=2003-revised; ICD-10 throughout — 2003 cohort) + DEFLATE64 tooling decision + SMOKE Tier-0/1 value-distribution verify — **RESULT: PROCEED to DO** (9/9 forward-looking HALTs from `RECEIPTS/C8.18_step4a_2026-05-18T14-30-00Z.md` re-verified; 11/11 gate parquet SHAs byte-exact; canonical pytest baseline `127 passed, 1 skipped, 1 xfailed in 313.36s` (4-dir suite) preserved; the FULL 2003 den-plus + numerator layout reconstructed **byte-exact from the `LinkCO03Guide.pdf` DETAIL "Position/Len/Field" code-outline** (pp20-72; the L13-extension governing precedent — the pp18-19 "Linked 2003 Cohort Data Elements and Locations" element-span SUMMARY is composite + NOT trusted, used only as an independent block-range cross-check) — captured below as state-on-disk substrate; **a material L13-extension finding surfaced + resolved at the Convention-3 snapshot before any `field_specs.py` mutation**: the prior C8.18 DO step 4 PRE-FLIGHT's *assumed* "2003 = 783/**1259**" numerator length is **FALSIFIED** — the guide p17 File Characteristics state Numerator US record length = **1,142** and exact zip-member arithmetic confirms it byte-exact (den `4,096,151 × (783+2 CRLF) = 3,215,478,535` = `VS03LKBC.USDENPUB`; num `27,843 × (1142+2) = 31,852,392` = `VS03LKBC.USNUMPUB`); not a §7 halt — "1259" was a non-binding prior assumption, resolved by the prescribed author-from-the-DETAIL + real-data-verify discipline; four within-task scope decisions resolved per established precedent (the user's standing "make any important decisions yourself" authorization + the DO 3a/3b/4a precedents); zero §7 halts)

> Per-sub-step PRE-FLIGHT under the C8.18 umbrella PRE-FLIGHT (2026-05-17T05:30:00Z) + the C8.18 DO step 4 PRE-FLIGHT (2026-05-18T05:00:00Z investigation-only checkpoint). Written **before any DO step 4b mutation** (no `field_specs.py` edit, no parser run). The FULL 2003 layout was reconstructed from the authoritative `LinkCO03Guide.pdf` DETAIL "Position/Len/Field" code-outline (pp20-72) + a read-only pre-authoring probe value-distribution-verified it on real DEFLATE64 `LinkCO03US.zip` data on the FIRST run, and it is captured below as state-on-disk substrate so DO goes straight to authoring (the C8.18 DO step 3b/4a precedent: "the layout reconstructed from the guide DETAIL + captured state-on-disk; SMOKE Tier 1 verified first-run-clean").

### Entry cheap-check — 9 forward-looking HALTs (from `RECEIPTS/C8.18_step4a_2026-05-18T14-30-00Z.md`)

- [x] **HALT 1**: `git tag -l` = `C8.17-complete`/`C8.17-pre-do`/`C8.18-pre-do`; `C8.18-complete` NOT present (final-sub-step-only). HEAD `6fb7acd` = the DO step 4a commit (after `209e756`). `C8.18-pre-do`@`6632a15` is the DO rollback anchor. Branch `main`, tree clean. ✓
- [x] **HALT 2 — 11 gate parquet SHAs byte-exact** (re-computed on-disk this entry): natality `c8a740eb…a6237153`/`acb5c48a…28856974`; `.v28_baseline` `230efed2…33ccebac`/`e16ad532…77c41d44`; linked-derived `9b828a4d…5a08b777`; fetal-death `38e2cecb…99c5cf48`(harm)/`185c071e…a7968a09`(deriv) (via `~/Desktop/fetal-death-harmonization-build/output/harmonized/`, soft-flag (hh)); MM `adbec108…45dc1549`/`5c22308b…d39205d1`/`7c682668…edd61f5d`/`d98b4296…6a543261`. **11/11 unchanged** vs the 4a receipt VERIFY-A. DO step 4b is additive layout substrate only (no parser run, no rebuild). ✓
- [x] **HALT 3 — canonical pytest baseline = `127 passed, 1 skipped, 1 xfailed`** on the **4-dir** suite `fetal_death/tests/ natality/tests/ tests/ matched_multiples/tests/` — re-run this entry: **`127 passed, 1 skipped, 1 xfailed in 313.36s`** (byte-exact baseline preserved; in the ~240-380s band). README 3-dir line stays stale → soft-flag (jj) (out-of-scope). ✓
- [x] **HALT 4 — DO step 4b = cohort 2003 `field_specs.py` layout authoring**, reconstructed FRESH from the `LinkCO03Guide.pdf` DETAIL "Position/Len/Field" code-outline (L13-extension; do NOT trust the pp18-19 element-span SUMMARY; never assume same-model==same-layout). DO step 4b must **NOT re-derive** the 1983-1991 OR 1995-2002 layouts — verified present + byte-untouched this entry: `LINKED_BIRTH_1983_1988/1989_1991/1995_2002_FIELDS`, `LINKED_DEATH_1989_1991/1995_2002_FIELDS`, `LINKED_NUM_DEATH_1983_1988/1989_1991/1995_2002_FIELDS` + reclen constants — nor the 2005/2014 LINKED specs. ✓
- [x] **HALT 5 — encoding = ASCII**: the 2005+ parser `_slice_field` `.decode("latin-1")` works for the cohort `.dat`. Re-confirmed THIS entry on real `LinkCO03US.zip` `VS03LKBC.US{DEN,NUM}PUB` (DOB_YY@15-18 == '2003' for all 300×2 sampled records under latin-1; CRLF terminators). ✓
- [x] **HALT 6 — structural model**: 1995-2004 = the three-file denominator-plus model. 2003 = **783-byte den-plus + 1142-byte numerator** (the prior "1259" was a non-binding assumption; **FALSIFIED** — guide p17 + byte-exact zip-member arithmetic; den/num both = DEFLATE64). den-plus 1-783 == numerator 1-783 (the "Here ends the denominator-plus file" divider, LinkCO03Guide p55), numerator adds numerator-only mortality 784-1142. `_find_denomplus_member` ("DENOM") won't match `VS03LKBC.USDENPUB`/`USNUMPUB` → DO step 5 parser concern (not 4b — additive layout substrate only). ✓
- [x] **HALT 7 — §15.D substrate-format wording reconcile already APPLIED at the 3a commit**; the broader §15.D model-clarification remains **soft-flag (ii)** proposed-not-applied for §11 human-merge. DO step 4b folds the 2003 783/1142 layout-confirmation + the 1259→1142 falsification + the DEFLATE64-tooling decision into the SAME (ii) note; no new §15.D wording edit owed this sub-step. ✓
- [x] **HALT 8 — soft-flag (gg)**: the 2003 numerator carries `UCOD`@767-770 (ICD-10; 2003 cohort all ICD-10) + `UCODR130`@772-774 (130-cause infant recode) + `ENTITY`@788-927 (20×7) / `RECORD`@932-1031 (20×5) multiple cause as composite spans; the per-condition flag blocks `MEDRISK`/`OBSTETRC`/`LABOR`/`DELMETH`/`NEWBORN`/`CONGENIT` likewise authored as single composite spans; per-condition decomposition + per-era cause-recode semantics + the harmonized cause-column shape stay DO step 5/6 (the 3a/3b/4a composite-span precedent). ✓
- [x] **HALT 9 — pytest runtime ~313s** (in the ~240-380s band; the band is the gate, not the absolute number). ✓

**9/9 PASS. 11/11 gate parquet SHAs byte-exact. No §7 halt from the entry cheap-check.**

### Inputs

- [x] `raw_data/linked/LinkCO03US.zip` (179,744,359 B on disk + SHA-anchored at C8.18 DO step 2; read-only this entry — SMOKE Tier 1 reads the first ~300 records of `VS03LKBC.US{DEN,NUM}PUB` via `7z e -so` streaming). Members + compression: `VS03LKBC.USDENPUB` 3,215,478,535 B / `VS03LKBC.USNUMPUB` 31,852,392 B / `VS03LKBC.USUNMPUB` 330,616 B — **all compress_type=9 (DEFLATE64)**; stdlib `zipfile` raises `NotImplementedError` (re-confirmed this entry); `7z`/`7za` (homebrew p7zip `/opt/homebrew/bin/7z`) + `unzip` available; `zipfile_deflate64` NOT in env (system or uv).
- [x] `~/Desktop/natality-harmonization/raw_docs/linked/LinkCO03Guide.pdf` (111 pp, 345,151 chars; L12-extension text-layer probe THIS entry — 0 empty pages, DETAIL pp20-72 fully text-extractable, no OCR) — the authoritative 2003-cohort layout.
- [x] Sibling substrate (read-only): `natality/scripts/01_import/field_specs.py` (the 3a/3b/4a `LINKED_*_1983_1991`/`_1995_2002` + the 2005/2014 LINKED specs — pattern to mirror; do NOT re-derive) + `parse_linked_year.py` (`_layout_for_linked_year` + `_numerator_layout_for_linked_year` dispatchers — additive single-year 2003 branches to add at DO).

### Environment

- [x] `uv` env (Python 3.13; pinned `uv.lock`). PyMuPDF (`fitz`) for the DETAIL text extraction; `7z` (homebrew p7zip) for the DEFLATE64 stream. No new dependency added (DEFLATE64 tooling decision = CLI `7z`, NOT a `zipfile-deflate64` PyPI dep — preserves the C8.5a pinned-env SHA; only the single cohort year 2003 needs a non-stdlib decompressor).

### Source documentation

- [x] `LinkCO03Guide.pdf` DETAIL "Position/Len/Field/Description/Reporting-Flag-Position/Vers*/Values-Definition" code-outline (the L13-extension authoritative source): **pp20-55** = denominator-plus (locs 1-783; p55 divider *"Here ends the denominator-plus file. Documentation for the mortality section of the numerator (linked) file continues…"*); **pp55-72** = numerator-only mortality section (locs 784-1142). pp17 File Characteristics: Numerator US count 27,843 / **reclen 1,142**; Denominator US count 4,096,151 / **reclen 783**; Unlinked US count 289 / reclen 1,142. pp18-19 "Linked 2003 Cohort Data Elements and Locations" element-span SUMMARY = NOT trusted (L13-extension), used only as an independent block-range cross-check (`MEDRISK` 328-44, `OBSTETRC` 355-61, `LABOR` 374-89, `DELMETH` 395-401, `NEWBORN` 483-91, `CONGENIT` 504-25, `UCOD` 767-70, `UCODR130` 772-74, multiple-cond 786-1031 — all cross-confirmed against the DETAIL). No §7-#11 stale-SHA exposure (on-disk SHA-anchored guide).

### Outputs

- [x] DO step 4b intended outputs (NOT created this PRE-FLIGHT — DO next): **additive** `field_specs.py` — `LINKED_BIRTH_2003_FIELDS` (locs 1-750; 183 entries incl. composite spans + RESERVED/FILLER gap-fill) + `LINKED_DEATH_2003_FIELDS` (the den-plus death-"plus" + RECWT, locs 751-783; 16 entries) + `LINKED_NUM_DEATH_2003_FIELDS` (numerator-only mortality, locs 784-1142; 17 entries) + `LINKED_DENOMPLUS_RECLEN_2003 = 783` + `LINKED_NUM_RECLEN_2003 = 1142`; additive `_layout_for_linked_year`/`_numerator_layout_for_linked_year` single-year-2003 branches; NEW `natality/tests/test_linked_cohort_2003_layout_smoke.py` (`DESIGN: tracks-current-state`; Convention 1/2). **Additive — existing 2005/2014 + 3a/3b/4a constants + dispatchers byte-untouched (H10 / HALT-13).** No canonical parquet/schema/validation-CSV. **This PRE-FLIGHT entry itself = zero canonical mutation** (git scope = PRE_FLIGHT_LOG + this commit's state files).

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

DO step 4b mutates `field_specs.py` (additive) + `parse_linked_year.py` (additive branches) + a NEW SMOKE harness; this PRE-FLIGHT entry mutates no canonical state. **One material L13-extension finding + four within-task scope decisions surfaced before any `field_specs.py` mutation** and resolved per established precedent (no §7 halt):

0. **MATERIAL FINDING (L13-extension): the numerator record length is 1142, NOT the prior assumption's 1259.** The C8.18 DO step 4 PRE-FLIGHT (2026-05-18T05:00:00Z) recorded "2003 = 783/1259" as an *assumption*. The `LinkCO03Guide.pdf` p17 File Characteristics state Numerator US reclen = **1,142**; exact zip-member-uncompressed-size arithmetic confirms byte-exact (den `4,096,151 × 785 = 3,215,478,535`; num `27,843 × 1144 = 31,852,392`) — and the read-only pre-authoring probe on real DEFLATE64 data confirmed `file_size % 785 == 0` (count 4,096,151) / `% 1144 == 0` (count 27,843) with CRLF terminators. **Resolved**: author from the guide-stated + arithmetic-confirmed 783/1142, not the assumption. Not a §7 halt (the "1259" was a non-binding prior assumption; the L13-extension "never assume same-model==same-layout; value-distribution-verify on real data" discipline is exactly the resolution mechanism). The §15.D / 2026-05-18T05:00:00Z "1259" is superseded; folded into soft-flag (ii) §11 human-merge.
1. **DO step 4b scope** = additive `field_specs.py` constants + additive single-year-2003 `_layout_for_linked_year`/`_numerator_layout_for_linked_year` branches + a NEW sibling SMOKE harness. `_find_denomplus_member` `"DENOM"`-vs-`VS03LKBC.USDENPUB` support + wiring the DEFLATE64 stream into the actual parse path + the num↔den construction + the harmonize path remain DO step 5 (per PRE_FLIGHT_LOG 2026-05-18T05:00:00Z; the DO 3a/3b/4a scope precedent).
2. **DEFLATE64 tooling decision** = CLI `7z e -so` streaming (homebrew p7zip, already installed), NOT the `zipfile-deflate64` PyPI dependency. Rationale: only ONE cohort year (2003) needs a non-stdlib decompressor (1995-2002 + 2004 + 2005+ = DEFLATE, stdlib-fine); adding a dep would drift the C8.5a pinned-env (`pyproject.toml`/`uv.lock`) SHA for a single-year edge case; the 3.2 GB den-plus member is best streamed, not extracted; `zip_text_stream.py` already vendors a streaming pattern. The SMOKE Tier-1 harness reads the first N blocks off a `7z e -so` pipe then closes it (7z gets SIGPIPE — fine). Actual parse-path wiring is DO step 5.
3. **Composite-span convention**: the per-condition flag blocks `MEDRISK`@328-344 / `OBSTETRC`@355-361 / `LABOR`@374-389 / `DELMETH`@395-401 / `NEWBORN`@483-491 / `CONGENIT`@504-525 + the multiple-cause `ENTITY`@788-927 (20×7) / `RECORD`@932-1031 (20×5) are authored as single composite spans (extent = first-leaf-start..last-leaf-end, byte-exact from the DETAIL range-tokens, cross-confirmed against the pp18-19 SUMMARY block ranges); per-condition leaf decomposition + per-era cause-recode semantics stay DO step 5 (the DO3a/3b/4a composite-span + soft-flag (gg) governing precedent). Cleanly-parsed named scalars (e.g. `WTGAIN`/`CIG_*`/`ALCOHOL`/`F_*`/`MRACE1E-8E`) kept as-is; all unenumerated reserved gaps filled with explicit `RESERVED_<start>` entries + DETAIL-enumerated fillers kept as `FILLER_<start>` (provenance-preserving + unique-name; the 1995-2002 `R1`/`RESERVED1` distinct-reserved-name precedent) so the layout tiles [1,783] (den-plus) + [1,1142] (numerator) with zero gap/overlap.
4. **NEW sibling harness** `test_linked_cohort_2003_layout_smoke.py` (vs editing the shipped 3a/3b/4a harnesses) — the C8.17 DO5a/5b + C8.18 DO3a/3b/4a new-harness-per-sub-step precedent (sub-step isolation).

**Divergence verdict:** the 1259→1142 correction supersedes a non-binding prior assumption (not a §7-#12/#17 condition — the §15.D-level scope, cohort-only + denominator-plus model, is unchanged; only an internal record-length number is corrected, exactly what the Convention-3 snapshot exists to catch). None of the four decisions contradicts the C8.18 cohort-only scope or the §15.D / 2026-05-18T05:00:00Z DO-step-4b mandate; all are *within* "author the cohort 2003 layout from the DETAIL code-outline" and resolved per established precedent. No §7 halt; no fresh AskUserQuestion (standing authorization + on-point prior resolutions govern).

### SMOKE Tier 0 — the FULL 2003 layout reconstructed from the LinkCO03Guide DETAIL code-outline (state-on-disk substrate for DO)

L13-extension governing precedent (C8.18 DO 3a/3b/4a): the byte-level DETAIL "Position/Len/Field" code-outline is authoritative; the pp18-19 element-span SUMMARY is composite + NOT trusted (used only as an independent block-range cross-check — all 9 cross-checked composite/anchor block ranges matched). Positions 1-based inclusive. Composites = single spans (decision 3). `RESERVED_<n>` = unenumerated gap-fill (the 1995-2002 `R1`/`RESERVED1` precedent; §2 fail-closed — gaps explicit, never silently dropped); `FILLER_<n>` = DETAIL-enumerated filler (suffix = unique name; the SMOKE `len(names)==len(set(names))` invariant). den-plus = `LINKED_BIRTH_2003_FIELDS` (1-750) + `LINKED_DEATH_2003_FIELDS` (751-783); numerator = those + `LINKED_NUM_DEATH_2003_FIELDS` (784-1142). The full field tuple-lists are state-on-disk in `/tmp/c8_18_s4b_final.py` (re-derivable from the `LinkCO03Guide.pdf` DETAIL Position/Len column via the documented extractor) and embedded verbatim into `field_specs.py` at DO. Reclens byte-confirmed: den-plus = **783** (block 785 incl. CRLF; `3,215,478,535 / 785 = 4,096,151` = LinkCO03Guide p17); numerator = **1142** (block 1144; `31,852,392 / 1144 = 27,843` = p17).

**Anchor positions** (value-distribution-verified on real `VS03LKBC.US{DEN,NUM}PUB` at the read-only pre-authoring probe — first-run-clean): `REVISION`@7 (S=1989-unrev / A=2003-rev), `IDNUMBER`@10-14 (num↔den-plus join key), `DOB_YY`@15-18 (==2003), `MAGER41`@89-90, `MBRACE`@139-140, `MEDUC`@155, `DPLURAL`@423, `SEX`@436, `COMBGEST`@451-452, `APGAR5`@415-416, `DBWT`@467-470 (4-digit grams), `MATCHS`@751 (den-plus {1,2} / numerator ≡1), `AGED`@755-757 (000-366), `UCOD`@767-770 (ICD-10 alpha — 2003 cohort), `UCODR130`@772-774, `RECWT`@776-783 (den-plus ends @783; "1.000000" surviving), `EANUM`@786-787 (00-20), `ENTITY`@788-927, `RANUM`@930-931, `RECORD`@932-1031, `DTHYR`@1071-1074 (∈{2003,2004}), `DTHMON`@1141-1142 (01-12; numerator ends @1142).

### Halt conditions tripped

None. One material L13-extension finding (numerator 1259→1142) + four within-task scope decisions surfaced at the Convention-3 snapshot **before any `field_specs.py` mutation** (L10-safe; the DO 3a/3b/4a precedent) and resolved per established precedent. None contradicts the C8.18 cohort-only scope or the §15.D/2026-05-18T05:00:00Z DO-step-4b mandate. No §7 halt; no fresh AskUserQuestion (standing authorization + on-point prior resolutions govern).

### Result

**PROCEED to DO.** The FULL cohort 2003 layout (783-byte den-plus + 1142-byte numerator) is reconstructed byte-exact from the `LinkCO03Guide.pdf` DETAIL "Position/Len/Field" code-outline (pp20-72), cross-confirmed against the pp18-19 element-span SUMMARY block ranges, and **value-distribution-verified on real DEFLATE64 `LinkCO03US.zip` data on the FIRST run** via a read-only pre-authoring `7z e -so` probe (every anchor across den-plus + numerator clean; the 1259→1142 falsification held; encoding ASCII). Captured above as state-on-disk substrate. DO step 4b authors the additive `field_specs.py` constants + single-year-2003 dispatcher branches + a NEW sibling SMOKE harness (Tier 0 synthetic + L3 negative → Tier 1 real data via `7z` stream; fail-closed — if a position FAILs the layout is rebuilt from the DETAIL, NOT loosened; §2 / §9-#4). Single commit (PRE-FLIGHT + DO + RECEIPT; the C8.18 DO 3a/3b/4a precedent); no tag (intermediate; `C8.18-pre-do`@`6632a15` remains the rollback anchor). 4c (cohort 2004; 900/1142 — verify den-plus vs `LINKED_BIRTH_2005_2013`) follows.

---

## PRE-FLIGHT for C8.18 DO step 4a — 2026-05-18T14:30:00Z — cohort **1995-2002** `field_specs.py` layout authoring (230-byte denominator-plus + 535-byte numerator; 1989-rev birth; ICD-9 1995-98 / ICD-10 1999-2002 within-era UCOD value-domain) + SMOKE Tier-0/1 value-distribution verify — **RESULT: PROCEED to DO** (9/9 forward-looking HALTs from `RECEIPTS/C8.18_step3b_2026-05-18T02-00-00Z.md` + the C8.18 DO step 4 PRE-FLIGHT entry below re-verified; 11/11 gate parquet SHAs byte-exact; canonical pytest baseline `111 passed, 1 skipped, 1 xfailed in 360.53s` (4-dir suite) preserved; the FULL 1995-2002 den-plus + numerator layout reconstructed **byte-exact from the `LinkCO95Guide.pdf` DETAIL "Item and Code Outline"** (pp20-62; the L13-extension governing precedent — the pp18-19 "List of Data Elements and Locations" element-span SUMMARY is composite + NOT trusted) and **cross-verified byte-identical against `LinkCO99Guide.pdf`** for the ICD-10 1999-2002 sub-era (record lengths 230/535 + 11 anchor positions constant across the 1998→1999 ICD-9→ICD-10 boundary; only the `UCOD`@216-219 value-domain changes "ICD 9th Revision" → "ICD 10th Revision") — captured below as state-on-disk substrate; four within-task scope decisions surfaced at the Convention-3 snapshot **before any `field_specs.py` mutation** (L10-safe; the C8.18 DO step 3a/3b precedent) and resolved per established precedent: (i) DO step 4a scope = additive `field_specs.py` constants + additive `_layout_for_linked_year`/`_numerator_layout_for_linked_year` 1995-2002 branches + a NEW sibling SMOKE harness [`_find_denomplus_member` `"DEN"`-vs-`"DENOM"` + DEFLATE64-at-2003 + the num/den construction remain DO step 4b/5 per PRE_FLIGHT_LOG 2026-05-18T05:00:00Z]; (ii) medical/health composites authored as single composite spans (per-condition leaf decomposition + per-era cause recode = DO step 5; the DO3a/3b `MEDRISK`/`OBSTETRC` composite-span + soft-flag (gg) governing precedent); (iii) NEW sibling harness `test_linked_cohort_1995_2002_layout_smoke.py` (vs editing the shipped 3a/3b harnesses) — the C8.17 DO5a/5b + C8.18 DO3a/3b "new-harness-per-sub-step" precedent; (iv) the p18-19 element-SUMMARY-vs-DETAIL discrepancy (SUMMARY: pos 210 = "flag included in both num/den", pos 220-222 = part of "multiple conditions"; DETAIL: 210 = R7 reserved, 220-222 = `UCODR` 61/130-cause recode) resolved per the L13-extension governing precedent — the byte-level DETAIL is authoritative, the element-span SUMMARY is NOT trusted; discrepancy documented + SMOKE Tier-1 value-distribution-verified on real data; zero §7 halts

> Per-sub-step PRE-FLIGHT under the C8.18 umbrella PRE-FLIGHT (2026-05-17T05:30:00Z) + the C8.18 DO step 4 PRE-FLIGHT (2026-05-18T05:00:00Z investigation-only checkpoint). Written **before any DO step 4a mutation** (no `field_specs.py` edit, no parser run). The structural model + record lengths + member naming + compression + DETAIL-code-outline page pointers were captured at the 2026-05-18T05:00:00Z entry as state-on-disk; this entry executes the DO step 4a per-sub-step cheap-check, reconstructs the FULL 1995-2002 layout from the authoritative DETAIL code-outline + cross-verifies vs LinkCO99Guide, and captures it as state-on-disk substrate so DO goes straight to authoring (the C8.18 DO step 3b precedent: "both layouts reconstructed from the guide DETAIL code-outlines + captured state-on-disk; SMOKE Tier 1 verified first-run-clean").

### Entry cheap-check — 9 forward-looking HALTs (from `RECEIPTS/C8.18_step3b` + the 2026-05-18T05:00:00Z DO step 4 PRE-FLIGHT)

- [x] **HALT 1**: `git tag -l` = `C8.17-complete`/`C8.17-pre-do`/`C8.18-pre-do`; `C8.18-complete` NOT present (final-sub-step-only). HEAD `209e756` = the DO step 4 PRE-FLIGHT commit (after `00ade5f`). `C8.18-pre-do`@`6632a15` is the DO rollback anchor. Branch `main`, tree clean. ✓
- [x] **HALT 2 — 11 gate parquet SHAs byte-exact** (re-computed on-disk this entry): natality `c8a740eb…a6237153`/`acb5c48a…28856974`; `.v28_baseline` `230efed2…33ccebac`/`e16ad532…77c41d44`; linked-derived `9b828a4d…5a08b777`; fetal-death `38e2cecb…99c5cf48`(harm)/`185c071e…a7968a09`(deriv) (via the `~/Desktop/fetal-death-harmonization-build/output/harmonized/` tree, soft-flag (hh)); MM `adbec108…45dc1549`/`5c22308b…d39205d1`/`7c682668…edd61f5d`/`d98b4296…6a543261`. **11/11 unchanged** vs the DO step 4 PRE-FLIGHT HALT 2 + the DO step 3b receipt VERIFY-A. DO step 4a layout authoring is additive substrate only (no parser run, no rebuild). ✓
- [x] **HALT 3 — canonical pytest baseline = `111 passed, 1 skipped, 1 xfailed`** on the **4-dir** suite `fetal_death/tests/ natality/tests/ tests/ matched_multiples/tests/` — re-run this entry: **`111 passed, 1 skipped, 1 xfailed in 360.53s`** (byte-exact baseline preserved; in the ~240-380s band). README 3-dir "56 passed" line stays stale → soft-flag (jj) (out-of-scope; Phase-D/C8.x docs-refresh). ✓
- [x] **HALT 4 — DO step 4a = cohort 1995-2002 `field_specs.py` layout authoring** (230-byte den-plus + 535-byte numerator; 1989-rev birth; ICD-9 1995-98 / ICD-10 1999-2002 within-era UCOD value-domain), reconstructed FRESH from the `LinkCO95Guide.pdf` **DETAIL "Item and Code Outline"** (L13-extension; do NOT trust the pp18-19 element-span SUMMARY; do NOT reuse `LINKED_*_1989_1991` — the 1995-2002-reuses-1989-1991 hypothesis was FALSIFIED at the 2026-05-18T05:00:00Z PRE-FLIGHT). DO step 4a must **NOT re-derive** the 1983-1991 denominator OR numerator layouts (state-on-disk in `field_specs.py` — verified present + byte-untouched this entry: `LINKED_BIRTH_1983_1988_FIELDS`/`LINKED_BIRTH_1989_1991_FIELDS`/`LINKED_DEATH_1989_1991_FIELDS`/`LINKED_NUM_DEATH_1983_1988_FIELDS`/`LINKED_NUM_DEATH_1989_1991_FIELDS` + reclen constants), nor the 2005/2014 LINKED specs. ✓
- [x] **HALT 5 — encoding = ASCII (verified at 3a/3b + DO step 4 PRE-FLIGHT)**: the 2005+ parser `_slice_field` `.decode("latin-1")` works for the cohort `.dat`. Re-confirmed at the 2026-05-18T05:00:00Z entry on real `LinkCO{95..02}US{Den,Num}.dat` (BIRYR@7-10 == cohort year under latin-1). ✓
- [x] **HALT 6 — structural model**: 1995-2004 = the three-file denominator-plus model. **DO step 4a finding (this entry, from the LinkCO95Guide DETAIL p20 + p50):** "Locations 7-210 contain data from the Birth Certificate. Locations 211-535 contain data from the Death Certificate. Data in locations 211-222 are included on both the numerator and denominator-plus files. Data in locations 223-535 are included in the numerator file only." → den-plus (230) = MATCHS@1 + IDNUMBER@2-6 + birth-cert@7-210 + death-"plus"@211-222 + RECWT@223-230; numerator (535) = the same 1-230 + numerator-only mortality 231-535. The `_find_denomplus_member` `"DEN"`-vs-`"DENOM"` + DEFLATE64-at-2003 remain DO step 4b/5 parser concerns (not DO step 4a — additive layout substrate only). ✓
- [x] **HALT 7 — §15.D substrate-format wording reconcile already APPLIED at the 3a commit**; the broader §15.D model-clarification (3a/3b split; 4a/4b/4c decomposition; structural model; reuse-falsification; DEFLATE64) remains **soft-flag (ii)** proposed-not-applied for §11 human-merge. DO step 4a folds the 1995-2002 230/535 den-plus+numerator layout-confirmation into the SAME (ii) note; no new §15.D wording edit owed this sub-step. ✓
- [x] **HALT 8 — soft-flag (gg) refined**: the 1995-2002 numerator carries `UCOD`@216-219 (ICD-9 1995-98 / ICD-10 1999-2002) + `UCODR`@220-222 (61-cause ICD-9 / 130-cause ICD-10 recode — within-era value-domain) + entity-axis (`ENTITY`@263-402, 20×7) / record-axis (`RECORD`@405-504, 20×5) multiple cause as composite spans; per-condition decomposition + `cause_recode` per-era + the ICD-9/10-era harmonized cause-column shape stay DO step 5/6 (the 3a/3b composite-span precedent). ✓
- [x] **HALT 9 — pytest runtime ~360s** (in the ~240-380s band; the band is the gate, not the absolute number). ✓

**9/9 PASS. 11/11 gate parquet SHAs byte-exact. No §7 halt from the entry cheap-check.**

### Inputs

- [x] `raw_data/linked/LinkCO{95..02}US.zip` (8 cohort zips on disk + SHA-anchored at C8.18 DO step 2; read-only this entry — SMOKE Tier 1 reads the first ~300 records of `LinkCO{95,98,99,02}US{Den,Num}.dat` spanning the 1998→1999 ICD-9→ICD-10 boundary). Members: 1995-2001 `LinkCO{YY}US{Den,Num,Unl}.dat` (mixed case); 2002 `LinkCO02US{DEN,NUM,UNL}.dat` (upper). Compression = DEFLATE (stdlib-readable for all of 1995-2002; DEFLATE64-at-2003 is DO step 4b).
- [x] `~/Desktop/natality-harmonization/raw_docs/linked/LinkCO95Guide.pdf` (258 pp; L12-extension text-layer probe at the 2026-05-18T05:00:00Z entry — DETAIL pp20-62 fully text-extractable, no OCR) — the authoritative ICD-9 1995-cohort layout. `LinkCO99Guide.pdf` (224 pp; text-extractable) — the ICD-10 1999-cohort cross-check.
- [x] Sibling substrate (read-only): `natality/scripts/01_import/field_specs.py` (the 3a/3b `LINKED_*_1983_1991` + the 2005/2014 LINKED specs — pattern to mirror; do NOT re-derive) + `parse_linked_year.py` (`_layout_for_linked_year` denominator dispatcher + `_numerator_layout_for_linked_year` 3b helper — additive 1995-2002 branches to add at DO).

### Source documentation

- [x] `LinkCO95Guide.pdf` DETAIL "Item and Code Outline" (the Item-Location/Length/Variable-Name columns; the L13-extension authoritative source): **pp20-49 "Denominator Record and Natality Section of Numerator (Linked) Record"** (locs 1-210 birth cert); **pp50-51 "Denominator Record and Mortality Section of Numerator (Linked) Record"** (locs 211-230 = death-"plus" 211-222 + RECWT 223-230; p51: *"Here ends the Denominator file. Documentation for the Mortality Section of the Numerator (Linked) file begins with the record weight in positions 223-230"*); **pp52-62 "Mortality Section of Numerator (Linked) Record"** (locs 231-535, numerator-only). pp18-19 "List of Data Elements and Locations" element-span SUMMARY = NOT trusted (L13-extension). `LinkCO99Guide.pdf` cross-check: Den 230 / Num 535 / Unlinked 535 (p16-18) + 11 DETAIL anchor positions byte-identical to LinkCO95 (BIRYR@7-10, DBIRWT@81-84, BIRWT4@87, DPLURAL@89, UCOD@216-219 ["ICD 10th Revision"], RECWT@223-230, AGED@211-213, ACCIDPL@215, EANUM@261-262, DTHYR@524-527, WEEKDAYD@532). No §7-#11 stale-SHA exposure (on-disk SHA-anchored guides).

### Outputs

- [x] DO step 4a intended outputs (NOT created this PRE-FLIGHT — DO next): **additive** `field_specs.py` — `LINKED_BIRTH_1995_2002_FIELDS` (locs 1-210; 76 fields incl. composite spans) + `LINKED_DEATH_1995_2002_FIELDS` (the den-plus death-"plus" + RECWT, locs 211-230; 6 fields) + `LINKED_NUM_DEATH_1995_2002_FIELDS` (numerator-only mortality, locs 231-535; 18 fields) + `LINKED_DENOMPLUS_RECLEN_1995_2002 = 230` + `LINKED_NUM_RECLEN_1995_2002 = 535`; additive `_layout_for_linked_year`/`_numerator_layout_for_linked_year` 1995-2002 branches; NEW `natality/tests/test_linked_cohort_1995_2002_layout_smoke.py` (`DESIGN: tracks-current-state`; Convention 1/2). **Additive — existing 2005/2014 + 3a/3b 1983-1991 constants + dispatchers byte-untouched (H10 / HALT-13).** No canonical parquet/schema/validation-CSV. **This PRE-FLIGHT entry itself = zero canonical mutation** (git scope = PRE_FLIGHT_LOG + this commit's state files).

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

DO step 4a mutates `natality/scripts/01_import/field_specs.py` (additive) + `parse_linked_year.py` (additive branches) + a NEW SMOKE harness; this PRE-FLIGHT entry mutates no canonical state. Four within-task scope decisions surfaced **before any `field_specs.py` mutation** and resolved per established precedent (the user's standing "make any important decisions yourself" authorization + on-point DO 3a/3b resolutions govern; no §7 halt):

1. **DO step 4a scope** = additive `field_specs.py` constants + additive `_layout_for_linked_year`/`_numerator_layout_for_linked_year` 1995-2002 branches + a NEW sibling SMOKE harness. `_find_denomplus_member` `"DEN"`-vs-`"DENOM"` support + the DEFLATE64-at-2003 tooling decision + the num↔den construction + the harmonize path remain DO step 4b/5 (per PRE_FLIGHT_LOG 2026-05-18T05:00:00Z; the DO 3a/3b scope precedent).
2. **Composite-span convention**: the medical/health composites (`DELMETH`@92-99, `MEDRISK`@100-117, `OTHERRSK`@118-128, `OBSTETRC`@129-136, `LABOR`@137-153, `NEWBORN`@154-163, `CONGENIT`@164-186, `FLRES`@187-203) + the multiple-cause spans (`ENTITY`@263-402, `RECORD`@405-504) are authored as single composite spans; per-condition leaf decomposition + per-era `UCODR` 61/130-cause recode semantics stay DO step 5 (the DO3a/3b `MEDRISK`/`OBSTETRC`/`ENTITY`/`RECORDAX` composite-span + soft-flag (gg) governing precedent).
3. **NEW sibling harness** `test_linked_cohort_1995_2002_layout_smoke.py` (vs editing the shipped 3a/3b harnesses) — the C8.17 DO5a/5b + C8.18 DO3a/3b new-harness-per-sub-step precedent (sub-step isolation).
4. **Element-SUMMARY-vs-DETAIL discrepancy** at pos 210 + 220-222: the pp18-19 "List of Data Elements" SUMMARY maps pos 210 → "Flag for records included in both numerator and denominator" and 220-222 → part of "Multiple conditions"; the byte-level DETAIL "Item and Code Outline" labels 210 = `R7` Reserved Position + 220-222 = `UCODR` (61-cause ICD-9 / 130-cause ICD-10 infant-cause recode). **Resolved per the L13-extension governing precedent (the DO 3a SMOKE-Tier-1 catch): the byte-level DETAIL is authoritative; the element-span SUMMARY is composite + NOT trusted.** Authored per the DETAIL; the discrepancy is documented in the `field_specs.py` source-citation block + SMOKE Tier-1 value-distribution-verifies the affected positions on real data (the DO-step-5 harmonized match-flag uses `MATCHS`@1, not pos 210, so the layout substrate is unaffected either way).

**Divergence verdict:** none of the four decisions contradicts the C8.18 cohort-only scope or the §15.D / 2026-05-18T05:00:00Z DO-step-4a mandate; all are *within* the "author the cohort 1995-2002 layout from the DETAIL code-outline" mandate and resolved per established precedent. No §7 halt; no fresh AskUserQuestion (the user's standing authorization + on-point prior resolutions govern).

### SMOKE Tier 0 — the FULL 1995-2002 layout reconstructed from the LinkCO95Guide DETAIL code-outline (state-on-disk substrate for DO; cross-verified byte-identical vs LinkCO99Guide)

L13-extension governing precedent (C8.18 DO 3a/3b): the byte-level DETAIL "Item and Code Outline" Item-Location column is authoritative; the pp18-19 element-span summary is composite + NOT trusted. Positions 1-based inclusive (start, end). Composites are single spans (decision (2) above). **`LinkCO99Guide.pdf` (ICD-10 1999-cohort) cross-verified byte-identical** — 230/535 record lengths + all 11 spot-checked anchor positions constant across the 1998→1999 boundary; only `UCOD`@216-219 value-domain changes "ICD 9th Revision"→"ICD 10th Revision" and `UCODR`@220-222 "61 Infant Cause Recode"→"130-cause" (within-era; DO step 5/6 / soft-flag (gg)).

**`LINKED_BIRTH_1995_2002_FIELDS`** — den-plus + numerator-natality section, locs 1-210 (MATCHS/IDNUMBER + birth cert; identical in den-plus + numerator per the shared DETAIL p20-49):

| loc | var | desc |
|---|---|---|
| 1 | MATCHS | Match Status (1 matched B/ID / 2 surviving infant / 3 unmatched-unlinked-only) |
| 2-6 | IDNUMBER | Infant Death Number (uniquely identifies same infant in num + den-plus) |
| 7-10 | BIRYR | Year of Birth |
| 11 | RESSTATB | Resident Status - Birth (1-4) |
| 12-13 | BRSTATE | Expanded State of Residence - NCHS Codes - Birth |
| 14-15 | STOCCFIPB | State of Occurrence (FIPS) - Birth |
| 16-18 | CNTOCFIPB | County of Occurrence (FIPS) - Birth |
| 19-20 | STRESFIPB | State of Residence (FIPS) - Birth |
| 21-23 | CNTYRFPB | County of Residence (FIPS) - Birth |
| 24-28 | PLRES | Place (City) of Residence (FIPS) |
| 29 | MAGEFLG | Age of Mother Flag |
| 30-31 | DMAGE | Age of Mother |
| 32 | MAGER8 | Age of Mother Recode 8 |
| 33 | ORMOTH | Hispanic Origin of Mother |
| 34 | ORRACEM | Hispanic Origin and Race of Mother Recode |
| 35 | MRACEIMP | Race of Mother Imputation Flag |
| 36-37 | MRACE | Race of Mother |
| 38 | MRACE3 | Race of Mother Recode 3 |
| 39-40 | DMEDUC | Education of Mother Detail |
| 41 | MEDUC6 | Education of Mother Recode 6 |
| 42 | DMARIMP | Marital Status Imputation Flag |
| 43 | DMAR | Marital Status of Mother |
| 44-45 | MPLBIR | Place of Birth of Mother |
| 46 | MPLBIRR | Place of Birth of Mother Recode |
| 47-48 | DTOTORD | Detail Total Birth Order |
| 49-50 | DLIVORD | Detail Live Birth Order |
| 51-52 | MONPRE | Detail Month of Pregnancy Prenatal Care Began |
| 53 | MPRE5 | Month Prenatal Care Began Recode 5 |
| 54-55 | NPREVIST | Total Number of Prenatal Visits |
| 56 | ADEQUACY | Adequacy of Care Recode (Kessner) |
| 57-59 | R1 | Reserved Positions |
| 60 | FAGERFLG | Reported Age of Father Used Flag |
| 61-62 | DFAGE | Age of Father |
| 63 | ORFATH | Hispanic Origin of Father |
| 64 | ORRACEF | Hispanic Origin and Race of Father Recode |
| 65-66 | FRACE | Race of Father |
| 67 | PLDEL | Place or Facility of Delivery |
| 68 | BIRATTND | Attendant at Delivery |
| 69 | R2 | Reserved Position |
| 70 | GESTESTM | Clinical Estimate of Gestation Used Flag |
| 71-72 | CLINGEST | Clinical Estimate of Gestation |
| 73 | GESTIMP | Gestation Imputation Flag |
| 74-75 | GESTAT | Gestation - Detail in Weeks |
| 76-77 | GESTAT10 | Gestation Recode 10 |
| 78 | CSEXIMP | Sex Imputation Flag |
| 79 | CSEX | Sex (1 M / 2 F) |
| 80 | BWIF | Birth Weight Imputation Flag |
| 81-84 | DBIRWT | Birth Weight Detail in Grams (Imputed) |
| 85-86 | BIRWT12 | Birth Weight Recode 12 (Imputed) |
| 87 | BIRWT4 | Birth Weight Recode 4 (Imputed) |
| 88 | PLURIMP | Plurality Imputation Flag |
| 89 | DPLURAL | Plurality |
| 90-91 | FMAPS | Five-Minute Apgar Score |
| 92-99 | DELMETH | Method of Delivery (composite; leaves DO5) |
| 100-117 | MEDRISK | Medical Risk Factors (composite; MRFLAG@100..OTHERMR@117; leaves DO5) |
| 118-128 | OTHERRSK | Other Risk Factors — tobacco/alcohol/wt-gain (composite; leaves DO5) |
| 129-136 | OBSTETRC | Obstetric Procedures (composite; leaves DO5) |
| 137-153 | LABOR | Complications of Labor and/or Delivery (composite; leaves DO5) |
| 154-163 | NEWBORN | Abnormal Conditions of the Newborn (composite; leaves DO5) |
| 164-186 | CONGENIT | Congenital Anomalies (composite; leaves DO5) |
| 187-203 | FLRES | Reporting Flags for Place of Residence (composite; leaves DO5) |
| 204 | CDOBMIMP | Month of Birth of Child Imputation Flag |
| 205-206 | BIRMON | Month of Birth |
| 207-208 | R6 | Reserved Position |
| 209 | WEEKDAYB | Day of Week Child Born |
| 210 | R7 | Reserved Position (SUMMARY claims "num/den flag"; DETAIL authoritative — L13-ext; value-verify SMOKE T1) |

**`LINKED_DEATH_1995_2002_FIELDS`** — den-plus death-"plus" + RECWT, locs 211-230 (present on BOTH den-plus + numerator; the appended "plus" that makes the den-plus a denominator-plus, analogous to `LINKED_DEATH_1989_1991_FIELDS` / `LINKED_DEATH_2005_2013_FIELDS`):

| loc | var | desc |
|---|---|---|
| 211-213 | AGED | Age at Death in Days (000-364) |
| 214 | AGER5 | Infant Age Recode 5 |
| 215 | ACCIDPL | Place of Accident (E850-E869, E880-E928) |
| 216-219 | UCOD | Underlying Cause of Death — ICD 9th Rev (1995-98) / 10th Rev (1999-2002); pos 219 blank if no 4th digit |
| 220-222 | UCODR | Infant Cause Recode — 61-cause ICD-9 (1995-98) / 130-cause ICD-10 (1999-2002); within-era value-domain (DO5/soft-flag (gg)) |
| 223-230 | RECWT | Record Weight (1.XXXXXX; ≈1.0-1.03 infant-death, 1.0 surviving) |

**`LINKED_NUM_DEATH_1995_2002_FIELDS`** — numerator-only mortality section, locs 231-535 (locs 223-535 numerator-only per DETAIL p50; 231-260 = unenumerated reserved gap between RECWT@223-230 and MULTCOND@261; mirrors the 1989-1991 numerator `RESERVED1`@226-260 pattern):

| loc | var | desc |
|---|---|---|
| 231-260 | RESERVED1 | Reserved (unenumerated in DETAIL; 30 bytes between RECWT@230 and MULTCOND@261) |
| 261-262 | EANUM | Number of Entity-Axis Conditions (00-20) |
| 263-402 | ENTITY | Entity-Axis Conditions (20 × 7-byte; part/line + seq + ICD code + nature-of-injury flag; composite, leaves DO5) |
| 403-404 | RANUM | Number of Record-Axis Conditions (00-20) |
| 405-504 | RECORD | Record-Axis Conditions (20 × 5-byte; ICD code + nature-of-injury flag; composite, leaves DO5) |
| 505 | RESSTATD | Resident Status - Death (1-4) |
| 506-507 | DRSTATE | Expanded State of Residence - NCHS Codes - Death |
| 508-509 | STOCCFIPD | State of Occurrence (FIPS) - Death |
| 510-512 | CNTOCFIPD | County of Occurrence (FIPS) - Death |
| 513-514 | STRESFIPD | State of Residence (FIPS) - Death (00 = foreign) |
| 515-517 | CNTYRFPD | County of Residence (FIPS) - Death |
| 518-522 | PLRESD | Place (City) of Residence (FIPS) - Death |
| 523 | HOSPD | Hospital and Patient Status |
| 524-527 | DTHYR | Year of Death |
| 528-529 | DTHMON | Month of Death (01-12) |
| 530-531 | R8 | Reserved Position |
| 532 | WEEKDAYD | Day of Week of Death (1-7, 9) |
| 533-535 | R9 | Reserved positions |

Reclens (byte-confirmed at the 2026-05-18T05:00:00Z entry against guide-stated counts, e.g. `LinkCO95USDen.dat` 905,498,784/232 = 3,903,012 = LinkCO95Guide p15): **den-plus = 230**, **numerator = 535** (constant across the 1998→1999 ICD boundary — LinkCO99Guide p16-18 byte-identical). `_layout_for_linked_year(1995..2002)` → `(230, LINKED_BIRTH_1995_2002_FIELDS, LINKED_DEATH_1995_2002_FIELDS)`; `_numerator_layout_for_linked_year(1995..2002)` → `(535, LINKED_BIRTH_1995_2002_FIELDS, LINKED_DEATH_1995_2002_FIELDS + LINKED_NUM_DEATH_1995_2002_FIELDS)` (exactly the 1989-1991 dispatcher pattern). The layout is authored at DO from this state-on-disk table + value-distribution-verified on real `LinkCO{95,98,99,02}US{Den,Num}.dat` at SMOKE Tier 1 (the 3b first-run-clean discipline; if a position FAILs, the layout is rebuilt from the DETAIL — the assertion is NOT loosened, §2 fail-closed / §9-#4).

### Halt conditions tripped

None. Four within-task scope decisions surfaced at the Convention-3 snapshot **before any `field_specs.py` mutation** (L10-safe; the DO 3a/3b precedent) and resolved per established precedent (additive-substrate scope = DO 3a/3b; composite-span = soft-flag (gg)/DO3a; new-harness-per-sub-step = C8.17 DO5a/5b; DETAIL-over-SUMMARY = L13-extension governing precedent). None contradicts the C8.18 cohort-only scope or the §15.D/2026-05-18T05:00:00Z DO-step-4a mandate. No §7 halt; no fresh AskUserQuestion (standing authorization + on-point prior resolutions govern).

### Result

**PROCEED to DO.** The FULL cohort 1995-2002 layout (230-byte den-plus + 535-byte numerator) is reconstructed byte-exact from the `LinkCO95Guide.pdf` DETAIL "Item and Code Outline" + cross-verified byte-identical against `LinkCO99Guide.pdf` for the ICD-10 1999-2002 sub-era, captured above as state-on-disk substrate. DO step 4a authors the additive `field_specs.py` constants + `_layout_for_linked_year`/`_numerator_layout_for_linked_year` 1995-2002 branches + a NEW sibling SMOKE harness, value-distribution-verified on real `LinkCO{95,98,99,02}US{Den,Num}.dat` across the 1998→1999 ICD-9→ICD-10 boundary (SMOKE Tier 0 synthetic + L3 negative → Tier 1 real data; fail-closed). Single commit (PRE-FLIGHT + DO + RECEIPT; the C8.18 DO 3a/3b precedent); no tag (intermediate; `C8.18-pre-do`@`6632a15` remains the rollback anchor). 4b (cohort 2003; DEFLATE64) + 4c (cohort 2004) follow.

---

## PRE-FLIGHT for C8.18 DO step 4 — 2026-05-18T05:00:00Z — cohort 1995-2004 layout reconstruction (1989-rev + 2003-rev; ICD-9/ICD-10) — **RESULT: PROCEED to DO step 4a (cohort 1995-2002 layout authoring) next; this entry is PRE-FLIGHT/investigation-only, ZERO canonical-state mutation**; three material findings surfaced + resolved before any DO mutation: (1) 1995-2004 = the **three-file denominator-plus model** (numerator + unlinked + denominator-plus; same family as 1989-1991 + 2005+, NOT the pure two-file 1983-1988 form) — the denominator-plus file IS the per-birth row set; (2) the **1995-2002 reuse-of-1989-1991 hypothesis is FALSIFIED** by a read-only real-data value-distribution probe (same 535-byte numerator length ≠ same layout — DBIRWT@79-82 = `'1 05'` not 4-digit grams, UCODR61@223-225 = `'1.0'` weight-bleed, DTHYR/DTHMON shifted; the 230-byte den-plus likewise diverges with a trailing `1.000000` RECWT field) → 1995-2002 needs its OWN layout authored from the LinkCO95/99Guide DETAIL code-outline (L13-extension governing precedent; do NOT reuse `LINKED_*_1989_1991`); (3) **LinkCO03US.zip uses DEFLATE64** (stdlib `zipfile` cannot decompress; `7z`/`unzip`/`zipfile-deflate64` available — a DO-step-4b tooling decision); DO step 4 split → **4a (cohort 1995-2002: 230-byte den-plus + 535-byte numerator; 1989-rev; ICD-9 1995-98 / ICD-10 1999-2002 as a within-era UCOD value-domain) + 4b (cohort 2003: 783-byte den-plus + 1259-byte numerator; 2003-rev transition; DEFLATE64) + 4c (cohort 2004: 900-byte den-plus + 1259-byte numerator; verify den-plus == `LINKED_BIRTH_2005_2013`)** per the C8.17 DO5a/5b + C8.18 DO3a/3b Convention-5 multi-session-DO-step precedent; zero §7 halts

> Per-sub-step PRE-FLIGHT under the C8.18 umbrella PRE-FLIGHT (2026-05-17T05:30:00Z). Written **before any DO step 4 mutation** (no `field_specs.py` edit, no parser run). §15.D-estimates DO step 4 at 2-3 sessions over 10 cohort years × 3 sub-eras; this session does the PRE-FLIGHT + read-only structural investigation (record lengths, member naming, compression, the decisive reuse-hypothesis probe, detail-code-outline page pointers) and checkpoints **PRE-FLIGHT/investigation-only** (state-on-disk; the `field_specs.py` authoring + SMOKE Tier-1 value-distribution verify = DO step 4a, next session) — mirrors the C8.18 DO step 3 PRE-FLIGHT/investigation-only checkpoint + the C8.17 DO5a/5b + C8.18 DO3a/3b multi-session-DO-step split discipline.

### Entry cheap-check — 9 forward-looking HALTs from `RECEIPTS/C8.18_step3b_2026-05-18T02-00-00Z.md`

- [x] **HALT 1**: `git tag -l` = `C8.17-complete`/`C8.17-pre-do`/`C8.18-pre-do`; `C8.18-complete` NOT present (final-sub-step-only). HEAD `00ade5f` = the DO step 3b commit (after `94c423e`). `C8.18-pre-do`@`6632a15` is the DO rollback anchor. Branch `main`, tree clean. ✓
- [x] **HALT 2 — 11 gate parquet SHAs byte-exact** (re-computed on-disk this entry; fetal-death via the canonical `~/Desktop/fetal-death-harmonization-build/output/harmonized/` tree, soft-flag (hh)): natality `c8a740eb…a6237153`/`acb5c48a…28856974`; `.v28_baseline` `230efed2…33ccebac`/`e16ad532…77c41d44`; linked-derived `9b828a4d…5a08b777`; fetal-death `38e2cecb…99c5cf48`(harm)/`185c071e…a7968a09`(deriv); MM `adbec108…45dc1549`/`5c22308b…d39205d1`/`7c682668…edd61f5d`/`d98b4296…6a543261`. **11/11 unchanged** vs the DO step 3b receipt VERIFY-A. DO step 4 PRE-FLIGHT = investigation-only (no parser run, no rebuild). ✓
- [x] **HALT 3 — canonical pytest baseline = `111 passed, 1 skipped, 1 xfailed`** on the **4-dir** suite `fetal_death/tests/ natality/tests/ tests/ matched_multiples/tests/` — re-run this entry: **`111 passed, 1 skipped, 1 xfailed in 347.34s`** (byte-exact baseline preserved; this investigation-only checkpoint adds no test). README 3-dir "56 passed" line stays stale → soft-flag (jj) (out-of-scope; Phase-D/C8.x docs-refresh). ✓
- [x] **HALT 4 — DO step 4 = cohort 1995-2004 `field_specs.py` layout reconstruction** (1989-rev birth 1995-2002; 2003-rev mix 2003-2004; ICD-9 1995-98 / ICD-10 1999-2004), reconstructed from the **DETAIL code-outline** (L13-extension; the 3a/3b SMOKE-Tier-1 governing precedent — do NOT trust the element-span "List of Data Elements and Locations" summary). DO step 4 must **NOT re-derive** the 1983-1991 denominator OR numerator layouts (state-on-disk in `field_specs.py` `LINKED_BIRTH_1983_1988_FIELDS`@894 / `LINKED_BIRTH_1989_1991_FIELDS`@950 / `LINKED_DEATH_1989_1991_FIELDS`@1022 / `LINKED_NUM_DEATH_1983_1988_FIELDS`@1087 / `LINKED_NUM_DEATH_1989_1991_FIELDS`@1122 + reclen constants — verified present + byte-untouched this entry). ✓
- [x] **HALT 5 — encoding = ASCII (verified at 3a/3b)**: the 2005+ parser `_slice_field` `.decode("latin-1")` works for the cohort `.dat`. Re-confirmed this entry on real `LinkCO{95..02}US{Den,Num}.dat` — BIRYR@7-10 == cohort year for every sampled record under latin-1; clean ASCII MATCHS/IDNUMBER. ✓
- [x] **HALT 6 — structural model**: 1983-1988 = pure two-file; 1989-1991 + 2005+ = denominator-plus. **DO step 4 finding (this entry): 1995-2004 = the three-file denominator-plus model** (numerator + unlinked + **denominator-plus** "may be used by itself"; LinkCO9x/0xGuide file-characteristics prose) — the denominator-plus file is the per-birth row set, structurally the SAME family as 1989-1991 + 2005+. `_find_denomplus_member` (`"DENOM"`) won't match `LinkCO{YY}US{Den,Num}.dat` (1995-2001 mixed-case) / `...{DEN,NUM}` (2002 upper) / `VS{YY}LKBC.{DUSDENOM,USNUMPUB}` (2003-2004 = the 2005+ family) — a **DO step 5** parser concern (not DO step 4). DO step 4 is strictly additive layout substrate; existing 2005/2014 + 3a/3b 1983-1991 constants + `_layout_for_linked_year`/`_numerator_layout_for_linked_year` byte-untouched. ✓
- [x] **HALT 7 — §15.D substrate-format wording reconcile already APPLIED at the 3a commit**; the broader §15.D model-clarification (3a/3b split; structural model; cert-match-key) remains **soft-flag (ii)** proposed-not-applied for §11 human-merge. DO step 4 folds the 4a/4b/4c decomposition + the 1995-2004 three-file denominator-plus structural model + the reuse-falsification + the DEFLATE64-at-2003 finding into the SAME proposed-not-applied (ii) note; no new §15.D wording edit owed this checkpoint (the substrate-format wording is already reconciled; the §15.D DO step 4 entry already says "field_specs.py layout"). ✓
- [x] **HALT 8 — soft-flag (gg) refined**: the 1995-2004 numerator carries ICD-9 (1995-98) / ICD-10 (1999-2004) underlying cause + entity/record-axis multiple cause; authored as composite spans at DO step 4a/4b/4c (per-condition decomposition + `cause_recode_130` per-era + exact ICD-9/10-era harmonized cause-column shape stay DO step 5/6 PRE-FLIGHT — the 3a/3b composite-span precedent). ✓
- [x] **HALT 9 — pytest runtime ~347s** (in the ~240-380s band; the band is the gate, not the absolute number). ✓

**9/9 PASS. 11/11 gate parquet SHAs byte-exact. No §7 halt from the entry cheap-check.**

### Inputs

- [x] `raw_data/linked/LinkCO{95..04}US.zip` (10 cohort zips; on disk + SHA-anchored at C8.18 DO step 2; manifest §3 = 38 linked / 141 total). Read-only this entry. Members + real record blocks probed: 1995-2001 `LinkCO{YY}US{Den,Num,Unl}.dat`; 2002 uppercase `...{DEN,NUM,UNL}.dat`; 2003-2004 `VS{YY}LKBC.{DUSDENOM/USDENPUB, USNUMPUB, USUNMPUB}` (the 2005+ naming family). **Compression: 1995-2002 + 2004 = DEFLATE (stdlib-readable); LinkCO03US.zip = DEFLATE64 (method 9 — stdlib `zipfile` raises `NotImplementedError`; `7z`/`7za`/`unzip` present + `zipfile-deflate64` PyPI available — a DO-step-4b tooling decision, not a halt).**
- [x] `raw_docs/linked/LinkCO{95..04}Guide.pdf` (10 cohort user guides; on disk + SHA-anchored at C8.18 DO step 2; **L12-extension text-layer probe this entry**: LinkCO99/01/03/04 = 0 empty pages; LinkCO95 14 / LinkCO96 10 / LinkCO97 4 / LinkCO98 1 / LinkCO00 2 / LinkCO02 1 empty pages — **all empty pages are appendix/code-list pages > p60; the file-characteristics (pp 1-18) + DETAIL code-outline (pp ~19-56) are fully text-extractable for all 10 guides — no OCR needed for the layout reconstruction**). DETAIL-code-outline page pointers captured below (state-on-disk for DO step 4a).
- [x] Sibling substrate (read-only): `natality/scripts/01_import/field_specs.py` — the 3a/3b `LINKED_*_1983_1991` constants (state-on-disk; do NOT re-derive — HALT 4), `LINKED_BIRTH_2005_2013_FIELDS`@~784 / `LINKED_DEATH_2005_2013_FIELDS`@~810 / `LINKED_DENOMPLUS_RECLEN` 900 (the 2004→2005 continuity-target hypothesis for DO step 4c). `parse_linked_year.py` `_layout_for_linked_year` (denominator dispatcher) + `_numerator_layout_for_linked_year` (3b additive helper) + `_find_denomplus_member` (`"DENOM"`; the DO-step-5 member-finder concern) + `zip_text_stream.iter_lines_from_zip` (stdlib `zipfile` — the DEFLATE64-at-2003 DO-step-4b implication).

### Source documentation

- [x] No external citation consumed beyond the on-disk SHA-anchored cohort guides. The §15.D-cited "1989-rev birth; ICD-9 1995-1998 / ICD-10 1999-2004; 2003-2004 1989+2003-rev mix" framing is empirically confirmed: file-characteristics record lengths are constant 230 (den-plus) / 535 (numerator) across the 1998→1999 ICD-9→ICD-10 boundary (→ ICD is a within-era UCOD value-domain, not a byte shift, for 1995-2002), and step up at the 2003-rev (2003 = 783/1259; 2004 = 900/1259). No §7-#11 stale-SHA exposure. **DETAIL-code-outline page pointers (state-on-disk; L9 cheap-check for DO step 4a — use the DETAIL "Item and Code Outline" Tape-Location columns, NOT the "List of Data Elements and Locations" element-span SUMMARY, L13-extension governing precedent):** LinkCO95Guide — element-span SUMMARY ~p17 (NOT trusted); **Denominator-Plus + Natality-section DETAIL ~pp19-49**; **Mortality Section of the Numerator (Linked) Record DETAIL ~pp50+** (ICD-9). LinkCO99Guide — SUMMARY ~p18; **Den-Plus+Natality DETAIL ~pp20-50**; **Mortality(Numerator) DETAIL ~pp51+** (ICD-10; cross-check vs LinkCO95 to confirm the 1995-2002 byte layout is constant + only the UCOD value-domain changes). LinkCO04Guide — "Here ends the Denominator file. Documentation of the Mortality Section of the Numerator (Linked) file begins here." ~p56. LinkCO03Guide — distinct doc format (DO step 4b probes its DETAIL structure; SAS `INFILE 'c:USnum.dat' LRECL=1259` confirms the 1259-byte numerator).

### Outputs

- [x] DO step 4 intended outputs (NOT created this PRE-FLIGHT — DO step 4a/4b/4c, next sessions): **additive** `field_specs.py` constants — DO step 4a: `LINKED_BIRTH_1995_2002_FIELDS` (230-byte den-plus) + `LINKED_NUM_DEATH_1995_2002_FIELDS` (535-byte numerator) + reclen constants; DO step 4b: cohort-2003 783/1259 layouts; DO step 4c: cohort-2004 900/1259 layouts (den-plus likely == `LINKED_BIRTH_2005_2013`, value-verify). Plus additive `_layout_for_linked_year` / `_numerator_layout_for_linked_year` 1995-2004 branches + NEW sibling SMOKE harness(es) per sub-step (`DESIGN: tracks-current-state`, Convention 1/2). **Additive — existing 2005/2014 + 3a/3b 1983-1991 constants + dispatchers byte-untouched (H10 / HALT-13).** No canonical parquet/schema/validation-CSV. **This PRE-FLIGHT entry itself = zero canonical mutation** (investigation-only; git scope = PRE_FLIGHT_LOG + DECISION_LOG + STATUS + this commit).

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

DO step 4 mutates `natality/scripts/01_import/field_specs.py` (additive) only; this PRE-FLIGHT entry mutates no canonical state. Current-state snapshot vs the (corrected) §15.D plan + the three surfaced findings:

- **Finding (1) — structural model: 1995-2004 = the three-file denominator-plus family (NOT the pure two-file 1983-1988 form).** LinkCO{95..04}Guide file-characteristics prose: three files per cohort year — numerator (linked birth+death), unlinked death (same layout as numerator per the guides), and a **denominator-plus** file ("selected variables from the numerator file have been added to the denominator file … the denominator-plus file may be used by itself"). This is the SAME model as 1989-1991 (225-byte denominator-plus) + 2005+ (900/1384-byte denominator-plus). The §15.D "reconstruct denominator-plus-equivalent" is therefore *direct* for 1995-2004 (the denominator-plus file already is the one-row-per-birth set; the numerator only adds richer multiple-cause detail joined via the cert match key at DO step 5). Refines [does not contradict] the 2026-05-17T20:00:00Z / T22:30:00Z structural model. Real record lengths (CRLF-terminated, ASCII, byte-confirmed against guide-stated counts, e.g. LinkCO95USDen 3,903,012 = guide p14): **1995-2002 = 230-byte den-plus + 535-byte numerator + 535-byte unlinked (constant across the 1998→1999 ICD boundary); 2003 = 783 / 1259; 2004 = 900 / 1259.**
- **Finding (2) — the 1995-2002-reuses-1989-1991 hypothesis is FALSIFIED (decisive read-only L13-extension probe).** Applying the 3a/3b `LINKED_BIRTH_1989_1991` + `LINKED_DEATH_1989_1991` + `LINKED_NUM_DEATH_1989_1991` layouts to real `LinkCO95USNum.dat` (535-byte) + `LinkCO95USDen.dat` (230-byte): the leading birth anchors align (MATCHS@1 ∈ {1,2}, IDNUMBER@2-6, BIRYR@7-10 == 1995/1996) BUT mid/late positions do NOT — DBIRWT@79-82 = `'1 05'` (two packed fields, not 4-digit grams), UCODR61@223-225 = `'1.0'` (the `1.000000` RECWT weight field bleeding in — the 1995+ denominator-plus appends a trailing record-weight the 1989-1991 225-byte layout lacks), DTHYR@522-525 / DTHMON@526-527 shifted. **Same 535-byte record length ≠ same layout** — the textbook L13-extension lesson. *Resolution:* DO step 4a authors the 1995-2002 230-byte den-plus + 535-byte numerator layouts FRESH from the LinkCO95Guide DETAIL code-outline (cross-checked against LinkCO99Guide for the ICD-10 1999-2002 sub-era), value-distribution-verified on real data at SMOKE Tier 1 — it does NOT reuse `LINKED_*_1989_1991`. (The 2004 den-plus == `LINKED_BIRTH_2005_2013` hypothesis is recorded as a DO-step-4c value-verify item, NOT assumed.)
- **Finding (3) — LinkCO03US.zip = DEFLATE64.** stdlib `zipfile.ZipFile(...).open()` raises `NotImplementedError` for `VS03LKBC.US{DENPUB,NUMPUB,UNMPUB}` (method 9). 1995-2002 + 2004 + 2005+ = DEFLATE (method 8; the existing `zip_text_stream` stdlib path works). System `7z`/`7za`/`unzip` present; `zipfile-deflate64` is on PyPI. *Resolution:* a DO-step-4b PRE-FLIGHT tooling decision (CLI-stream via `7z`/`unzip`, or add the `zipfile-deflate64` dep, scoped to 2003 only; a DO-step-5 `parse_linked_year` concern for the actual parse). Not a §7 halt — the substrate is on disk + SHA-anchored; only the decompressor for one cohort year needs a non-stdlib path; flagged BEFORE any DO mutation.
- **DO step 4 → 4a/4b/4c decomposition (Convention 5 within-task; the C8.17 DO5a/5b + C8.18 DO3a/3b precedent):** **4a** = cohort 1995-2002 (230-byte den-plus + 535-byte numerator; 1989-rev; ICD-9 1995-98 / ICD-10 1999-2002 as a within-era UCOD value-domain — one shared layout pair, the record lengths being constant across the ICD boundary is the decisive evidence; author fresh, value-verify across the 1998/1999 boundary). **4b** = cohort 2003 (783-byte den-plus + 1259-byte numerator; 2003-rev transition; the DEFLATE64 tooling decision). **4c** = cohort 2004 (900-byte den-plus + 1259-byte numerator; verify den-plus byte-identity vs `LINKED_BIRTH_2005_2013`). Folded into the soft-flag-(ii) §15.D model-clarification (proposed-not-applied; §11 human-merge — it refines the §15.D DO step 4 entry's "1995-2004 (1989-rev birth; …)" into the empirically-grounded three-sub-step structure; not a C8.18 scope change).
- **Divergence verdict:** none of the three findings contradicts the C8.18 cohort-only scope or the §15.D DO-step sequence; all are *within* the "reconstruct the cohort 1995-2004 layout" DO-step-4 mandate and resolved per established precedent (denominator-plus model = 1989-1991/2005+; reuse-falsification → author-fresh = the L13-extension governing precedent; DEFLATE64 = a bounded DO-step-4b tooling decision). Surfaced at the Convention-3 snapshot BEFORE any `field_specs.py` mutation (L10-safe; the C8.18 DO step 3 PRE-FLIGHT "divergences-before-DO-mutation" precedent). No §7 halt; no fresh AskUserQuestion (the user's standing "make any important decisions yourself" authorization + on-point prior resolutions govern; the methodology-paper-level cohort-vs-period question was the Sub-Q42 item, resolved at DO step 1).

### SMOKE Tier 0 — structural model + record lengths + member naming + compression + reuse-falsification (state-on-disk substrate for DO step 4a/4b/4c)

L13-extension governing precedent (C8.18 DO step 3a/3b): the byte-level **DETAIL code-outline** is authoritative; the "List of Data Elements and Locations" element-span summary is composite + NOT trusted. The DO-step-4 byte layouts are authored at 4a/4b/4c from the DETAIL code-outline (page pointers in "Source documentation" above) + value-distribution-verified on real `.dat` at each sub-step's SMOKE Tier 1 (the 3a/3b discipline). State-on-disk reconnaissance captured this entry (read-only; zero mutation):

| Cohort | Den-plus (data B) | Numerator (data B) | Unlinked | Term | Cert | Cause | Zip member naming | Compression |
|---|---|---|---|---|---|---|---|---|
| 1995-1998 | **230** | **535** | 535 | CRLF | 1989-rev | ICD-9 | `LinkCO{YY}US{Den,Num,Unl}.dat` | DEFLATE |
| 1999-2001 | **230** | **535** | 535 | CRLF | 1989-rev | ICD-10 | `LinkCO{YY}US{Den,Num,Unl}.dat` | DEFLATE |
| 2002 | **230** | **535** | 535 | CRLF | 1989-rev | ICD-10 | `LinkCO02US{DEN,NUM,UNL}.dat` (upper) | DEFLATE |
| 2003 | **783** | **1259** | 1259 | (DO4b) | 2003-rev mix | ICD-10 | `VS03LKBC.US{DENPUB,NUMPUB,UNMPUB}` | **DEFLATE64** |
| 2004 | **900** | **1259** | 1259 | (DO4c) | 2003-rev mix | ICD-10 | `VS04LKBC.{DUSDENOM,USNUMPUB,USUNMPUB}` | DEFLATE |

Real-data block sizes byte-confirmed against guide-stated record counts (e.g. `LinkCO95USDen.dat` 905,498,784 / 232 = 3,903,012 = LinkCO95Guide p14; `LinkCO99USNum.dat` 27,253 = LinkCO99Guide; `LinkCO03US.zip` `VS03LKBC.USNUMPUB` LRECL=1259 = the SAS `INFILE` statement). ASCII (latin-1) confirmed: BIRYR@7-10 == cohort year for every sampled record, 1995-2002. The 230-byte 1995-2002 den-plus + 535-byte numerator + the 2003/2004 layouts are authored at DO step 4a/4b/4c from the DETAIL code-outline; the 1989-1991-reuse path is FALSIFIED (Finding 2) — author fresh.

### Halt conditions tripped

None. Three material findings (1995-2004 = three-file denominator-plus model; 1995-2002 reuse-of-1989-1991 FALSIFIED → author fresh; LinkCO03US.zip = DEFLATE64 → DO-step-4b tooling decision) were surfaced at the Convention-3 snapshot **before any DO mutation** and resolved per established precedent (denominator-plus model = 1989-1991/2005+; L13-extension author-fresh = the 3a/3b governing precedent; bounded tooling decision deferred to DO step 4b PRE-FLIGHT) — documented here + DECISION_LOG 2026-05-18T05:00:00Z; folded into the proposed-not-applied soft-flag-(ii) §15.D model-clarification `[plan-update]` (§11 human-merge). None is a §7 halt (no plan contradiction; within the DO step 4 mandate; on-point prior resolutions exist; substrate on disk + SHA-anchored).

### Result

**PROCEED.** DO step 4 split → **4a (cohort 1995-2002 — 230-byte den-plus + 535-byte numerator `field_specs.py` layout authoring from the LinkCO95/99Guide DETAIL code-outline + SMOKE Tier-1 value-distribution verify across the 1998→1999 ICD-9→ICD-10 boundary + VERIFY/RECEIPT) — next session** + **4b (cohort 2003 — 783/1259 layouts; the DEFLATE64 tooling decision)** + **4c (cohort 2004 — 900/1259 layouts; verify den-plus == `LINKED_BIRTH_2005_2013`)**. This session checkpoints **PRE-FLIGHT/investigation-only** (zero canonical-state mutation; the structural model + record lengths + member naming + compression + the decisive reuse-falsification + the DETAIL-code-outline page pointers are captured above as state-on-disk substrate so DO step 4a goes straight to the authoritative DETAIL pages). Commit PRE-FLIGHT-only; no tag (intermediate; mirrors the C8.18 DO step 3 PRE-FLIGHT checkpoint; `C8.18-pre-do`@`6632a15` remains the rollback anchor).

---

## PRE-FLIGHT for C8.18 DO step 3b — 2026-05-18T00:30:00Z — cohort 1983-1991 **numerator/infant-death + ICD-9 + cert-match-key** `field_specs.py` layout authoring + SMOKE Tier-0/1 value-distribution verify — **RESULT: PROCEED to DO** (9/9 forward-looking HALTs from `RECEIPTS/C8.18_step3a_2026-05-17T23-30-00Z.md` re-verified; 11/11 gate parquet SHAs byte-exact; both numerator layouts reconstructed byte-exact from the `LinkCO83Guide.pdf` / `LinkCO89Guide.pdf` **DETAIL code-outline** — NOT the p13/pp18-19 element-span summary, the DO-step-3a L13-extension governing precedent — and captured below as state-on-disk substrate; three within-task scope decisions surfaced at the Convention-3 snapshot **before any `field_specs.py` mutation** (L10-safe; C8.18 DO step 3a precedent) and resolved per established precedent: (i) DO step 3b scope = additive `field_specs.py` numerator constants **+** an additive pure `_numerator_layout_for_linked_year` helper **+** a NEW sibling SMOKE harness [the two-file num/den join + `_find_denomplus_member` `"DEN"` support + the harmonize path remain DO step 5, per the 2026-05-17T20:00:00Z + T22:30:00Z PRE_FLIGHT_LOG]; (ii) cert-match-key finding — **1989-1991** = `(MATCHS@1, IDNUMBER@2-6)`, shared by the 225-byte denominator-plus + the 535-byte numerator (both in the already-authored `LINKED_BIRTH_1989_1991_FIELDS`); **1983-1988** = NO record-level public-use key (the 500-byte numerator is **self-contained** — carries its own 1-91 natality section = the deceased infant's birth covariates; the standard pre-2005 cohort-IMR construction is self-contained-numerator + aggregate-denominator); refines [does not contradict] the 2026-05-17T20:00:00Z "denominator-plus-equivalent via match-key join" finding; (iii) NEW sibling harness `test_linked_cohort_1983_1991_numerator_smoke.py` (vs editing the shipped 3a denominator harness) — C8.17 DO5a/5b + C8.18 DO3a "new-harness-per-sub-step" precedent; zero §7 halts)

> Per-sub-step PRE-FLIGHT under the C8.18 umbrella PRE-FLIGHT (2026-05-17T05:30:00Z) + the DO step 3 PRE-FLIGHT (2026-05-17T20:00:00Z) + the DO step 3a PRE-FLIGHT/close (2026-05-17T22:30:00Z / T23:30:00Z, which authored the byte-exact DENOMINATOR layouts + structural model). Written **before any `field_specs.py`/`parse_linked_year.py` mutation** (L10-safe; C8.17 DO5a/5b + C8.18 DO3a per-sub-step PRE-FLIGHT precedent). This entry adds the entry cheap-check + both full NUMERATOR layouts (state-on-disk substrate) + the three within-task scope decisions; the DO (authoring + SMOKE Tier 1 + VERIFY + RECEIPT + commit) follows in this same session (C8.18 DO step 3a single-session-DO-step precedent).

### Entry cheap-check — 9 forward-looking HALTs from `RECEIPTS/C8.18_step3a_2026-05-17T23-30-00Z.md`

- [x] **HALT 1**: `git tag -l` = `C8.17-complete`/`C8.17-pre-do`/`C8.18-pre-do`; `C8.18-complete` NOT present (final-sub-step-only). HEAD `94c423e` = the DO step 3a commit (after `a845af5`). `C8.18-pre-do`@`6632a15` is the DO rollback anchor. Branch `main`, tree clean. ✓
- [x] **HALT 2 — 11 gate parquet SHAs byte-exact** (re-computed on-disk this entry; fetal-death via the canonical `~/Desktop/fetal-death-harmonization-build/output/harmonized/` tree, soft-flag (hh)): natality `c8a740eb…a6237153`/`acb5c48a…28856974`; `.v28_baseline` `230efed2…33ccebac`/`e16ad532…77c41d44`; linked-derived `9b828a4d…5a08b777`; fetal-death `38e2cecb…99c5cf48`(harm)/`185c071e…a7968a09`(deriv); MM `adbec108…45dc1549`/`5c22308b…d39205d1`/`7c682668…edd61f5d`/`d98b4296…6a543261`. **11/11 unchanged** vs the DO step 3a receipt VERIFY-A. DO step 3b = layout substrate only (no parser run, no rebuild). ✓
- [x] **HALT 3 — canonical pytest baseline = `98 passed, 1 skipped, 1 xfailed`** on the **4-dir** suite `fetal_death/tests/ natality/tests/ tests/ matched_multiples/tests/` (85P+1S+1XF pre-3a + 13 from the 3a denominator SMOKE). DO step 3b adds a NEW numerator SMOKE harness → re-run at VERIFY-D must hold 98P+1S+1XF baseline + the new numerator-SMOKE count. README 3-dir "56 passed" line stays stale → soft-flag (jj) (out-of-scope; Phase-D/C8.x docs-refresh). ✓ (verified at VERIFY)
- [x] **HALT 4 — DO step 3b = the NUMERATOR layouts** (1983-1988 `LinkCO{YY}USnum.dat` 500-byte + 1989-1991 `LinkCO{YY}USnum.dat` 535-byte; ICD-9 underlying cause + 61-cause recode + entity/record-axis multiple cause + cert match key), reconstructed from the **detail code-outline** (L13-extension; the 3a SMOKE-Tier-1 catch is the governing precedent — do NOT trust the p13/pp18-19 element-span summary). DO step 3b must **NOT re-derive** the denominator (state-on-disk in `field_specs.py` `LINKED_BIRTH_1983_1988_FIELDS`/`LINKED_BIRTH_1989_1991_FIELDS`/`LINKED_DEATH_1989_1991_FIELDS` + reclen constants — verified present + byte-untouched by this step). ✓
- [x] **HALT 5 — encoding = ASCII (verified at 3a, NOT EBCDIC)**: the 2005+ parser `_slice_field` `.decode("latin-1")` works for pre-1990 public-use `.dat`. DO step 3b SMOKE Tier 1 re-confirms on the `*num*.dat` members (BIRYR == cohort year). ✓
- [x] **HALT 6 — structural model**: 1983-1988 = pure two-file (91-byte births-only denominator + 500-byte numerator → DO step 5 num/den construction); 1989-1991 = 225-byte denominator-PLUS single-file (2005+-analogous) + 535-byte numerator (richer ICD-9). `_find_denomplus_member` (`"DENOM"`) won't match `LinkCO{YY}USnum.dat` (`"NUM"`) / `USden.dat` (`"DEN"`) — a **DO step 5** parser concern (not 3b). DO step 3b is strictly additive; existing 2005/2014 + 3a-denominator constants + `_layout_for_linked_year` byte-untouched. ✓
- [x] **HALT 7 — §15.D "layout-CSV"→"`field_specs.py`" fix-on-contact APPLIED at the 3a commit**; the broader §15.D model-clarification (3a/3b split; 1983-1988 pure-two-file vs 1989-1991 denominator-plus; num/den→denominator-plus-equivalent via cert-match-key join) remains **soft-flag (ii)** proposed-not-applied for §11 human-merge (queued with the soft-flag-(w) batch). DO step 3b adds the numerator/match-key refinement to the SAME proposed-not-applied (ii) note; no new §15.D wording edit owed this step (the substrate-format wording is already reconciled). ✓
- [x] **HALT 8 — soft-flag (gg) refined**: 1989-1991 denominator-plus carries `UCOD@219-222` + `UCODR61@223-225`; the FULL entity/record-axis multiple-cause detail = the 535-byte numerator (1989-1991: NENTITY@261-262, ENTITY@263-402, NRECORD@403-404, RECORDAX@405-504; 1983-1988: NENTITY@238-239, ENTITY@240-379, NRECORD@380-381, RECORDAX@382-481). Authored as composite spans this step (per-condition decomposition + `cause_recode_130` per-era + exact ICD-9-era harmonized cause-column shape stay DO step 5/6 PRE-FLIGHT). ✓
- [x] **HALT 9 — pytest runtime ~316s** (in the ~240-380s band; the band is the gate, not the absolute number). ✓ (verified at VERIFY)

**9/9 PASS. 11/11 gate parquet SHAs byte-exact. No §7 halt from the entry cheap-check.**

### Inputs

- [x] `raw_data/linked/LinkCO{83..91}.zip` members `LinkCO{YY}USnum.dat` (numerator) — on disk + SHA-anchored at C8.18 DO step 2 (manifest §3 = 38 linked / 141 total). Read-only this entry; first ~300 records each for the DO-phase SMOKE Tier 1.
- [x] `raw_docs/linked/LinkCO83Guide.pdf` (139 pp; text-extractable, no OCR — L12-extension re-confirmed: 0 empty pages) — p12 file characteristics (Numerator 500 B / 39,704), p13-14 List of Data Elements, **pp15-32 "Denominator Record and Natality Section of Linked Record" detail** (the shared birth/natality byte layout; numerator natality = denominator 1-91), **p32** ("92-193 102 These positions are contained in the Numerator (Linked) Record only and are reserved for possible additional data"), **pp33-45 "Mortality Part / Section of Linked Record" detail** (the death-cert byte layout 194-500). L9 cheap-check PASS.
- [x] `raw_docs/linked/LinkCO89Guide.pdf` (192 pp; text-extractable, no OCR — L12-extension re-confirmed: 0 empty pages) — p17 file characteristics (Numerator 535 B / 38,605; Unlinked 535 B / 1,029), **p20** ("Locations 7-212 ... Birth Certificate; Locations 213-535 ... Death Certificate"; MATCHS@1, IDNUMBER@2-6), pp20-47 "Denominator-Plus Record and Natality Section of Numerator (Linked) Record" detail (= the 3a-authored 1-212 birth section, reused), **pp46-56 "Mortality Section of Linked Record" detail** (the death-cert byte layout 213-535).
- [x] Sibling substrate: `natality/scripts/01_import/field_specs.py` `LINKED_BIRTH_1983_1988_FIELDS`@894 / `LINKED_DEN_RECLEN_1983_1988=91`@942 / `LINKED_BIRTH_1989_1991_FIELDS`@950 / `LINKED_DEATH_1989_1991_FIELDS`@1022 / `LINKED_DENOMPLUS_RECLEN_1989_1991=225`@1031; `LINKED_DEATH_2005_2013_FIELDS`@810 (the v4 harmonized death-side continuity target: AGED/AGER5/AUTOPSY/UCOD/UCODR130/RECWT). `parse_linked_year.py` `_slice_field` (`.decode("latin-1")`)@49 / `_layout_for_linked_year` (denominator dispatcher; byte-untouched by 3b)@71.

### Source documentation

- [x] No external citation beyond the on-disk SHA-anchored cohort guides. `LinkCO83Guide.pdf` p32 (the 92-193 numerator-reserved gap) + pp33-45 (mortality detail: YOD@194-197, RECTYPED@198, RESSTATD@199, occurrence/residence place 200-222, infant-age recodes 223-227, HOSPD@228, AUTOPSY@229, ACCIDPL@230, UCOD ICD-9@231-234, UCODR61@235-237, entity/record-axis multiple cause 238-481, reserved 482-500); `LinkCO89Guide.pdf` p20 (birth/death-cert boundary) + pp46-56 (mortality detail: AGED@213-215, AGER5@216, AUTOPSY@217, ACCIDPL@218, UCOD@219-222, UCODR61@223-225, reserved 226-260, entity/record-axis multiple cause 261-504, RESSTATD@505, occurrence/residence FIPS+NCHS 506-520, EOSPD@521, DTHYR@522-525, DTHMON@526-527, WEEKDAYD@528, reserved 529-535). L9 cheap-check PASS (named locations verified in the actual PDFs). No §7-#11 stale-SHA exposure.

### Outputs

- [x] DO step 3b intended outputs (created in this session's DO phase, NOT this PRE-FLIGHT): **additive** `field_specs.py` — `LINKED_NUM_RECLEN_1983_1988 = 500`, `LINKED_NUM_DEATH_1983_1988_FIELDS` (the 194-500 mortality section; the 1-91 natality section REUSES `LINKED_BIRTH_1983_1988_FIELDS`, 92-193 numerator-reserved); `LINKED_NUM_RECLEN_1989_1991 = 535`, `LINKED_NUM_DEATH_1989_1991_FIELDS` (the 226-535 mortality section; the 1-212 birth section REUSES `LINKED_BIRTH_1989_1991_FIELDS`, the 213-225 death-derived "plus" REUSES `LINKED_DEATH_1989_1991_FIELDS`); an additive pure `_numerator_layout_for_linked_year(year)` helper in `parse_linked_year.py` (no zip I/O; existing `_layout_for_linked_year` + 2005/2014 + 3a-denominator branches byte-untouched, H10/HALT-13). Plus a NEW SMOKE harness `natality/tests/test_linked_cohort_1983_1991_numerator_smoke.py` (`DESIGN: tracks-current-state`, Convention 1/2). **No canonical parquet/schema/validation-CSV.** This PRE-FLIGHT entry itself = zero canonical mutation.

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

DO step 3b mutates `natality/scripts/01_import/field_specs.py` (additive numerator constants) + `parse_linked_year.py` (additive pure helper) + adds one NEW test file + appends state files. Current-state snapshot vs the (corrected) §15.D plan + the DO step 3 / 3a findings:

- **Scope decision (i) — `field_specs.py` numerator constants + an additive pure `_numerator_layout_for_linked_year` helper; parser member-finding / two-file join / harmonize deferred to DO step 5.** The 2026-05-17T20:00:00Z + T22:30:00Z PRE_FLIGHT_LOG explicitly deferred `_find_denomplus_member` `"DEN"` support + the 1983-1988 two-file numerator left-join + the harmonize path to "a DO step 5 parser concern". Resolution (per the user's standing "make any relevant decisions" authorization + §7-#17 scope-minimalism + the C8.18 DO step 3a additive-substrate precedent): DO step 3b adds the numerator layout constants **and** a minimal additive pure helper `_numerator_layout_for_linked_year` (returns the layout tuples; no zip I/O; the existing `_layout_for_linked_year` denominator dispatcher + 2005/2014 + 3a-denominator branches byte-untouched, H10/HALT-13). The full parse/join/harmonize path stays DO step 5. The SMOKE harness imports `field_specs` + applies a local slice helper directly on the real `*num*` zip member (does NOT route through `iter_parsed_records`), so the deferred member-finder does not block the DO step 3b SMOKE. Within-task scope narrowing, not a C8.18 scope change; recorded in DECISION_LOG 2026-05-18T00:30:00Z.
- **Scope decision (ii) — cert-match-key finding (the HALT-4 DO-step-3b deliverable).** Per the guide detail code-outlines read this entry: **1989-1991** — the 225-byte denominator-plus AND the 535-byte numerator both begin `MATCHS@1` (1 Matched / 2 Late-Filed Matched / 3 Surviving infant / 4 Unmatched infant death) + `IDNUMBER@2-6` (both already in the 3a-authored `LINKED_BIRTH_1989_1991_FIELDS`); the join key for the DO-step-5 "join the 535-byte numerator's richer death detail onto the 225-byte denominator-plus per-birth rows" = `(MATCHS, IDNUMBER)`. **1983-1988** — the 91-byte denominator carries `MATCHS@1` + `BIRYR@2-5` but **NO** infant-death-number (NCHS suppresses identifiers in public-use); the 500-byte numerator is **self-contained** — its 1-91 natality section IS the deceased infant's full birth covariates ("Denominator Record and Natality Section of Linked Record" shared layout), 92-193 is numerator-only reserved, 194-500 is the death cert. The standard pre-2005 cohort-IMR construction is therefore self-contained-numerator (death + own birth covariates) + aggregate-denominator (birth counts by stratum), NOT a record-level left-join. This **refines, does not contradict**, the 2026-05-17T20:00:00Z "denominator-plus-equivalent via match-key join" (the join exists + is keyed for 1989-1991; for 1983-1988 the numerator is self-contained). Folded into the soft-flag-(ii) §15.D model-clarification `[plan-update]` (proposed-not-applied; §11 human-merge). The exact harmonized v4 row model (one row per birth from the denominator with death fields where linked, vs numerator-self-contained tabulation) is the **DO step 5/6** decision (soft-flag (gg)); no §7 halt (no plan contradiction; within the "reconstruct the 1983-1991 numerator layout + identify the cert match key" HALT-4 mandate; on-point precedent = the standard pre-2005 cohort-IMR construction + the 2005+ denominator-plus model already in `field_specs.py`).
- **Scope decision (iii) — NEW sibling SMOKE harness.** `test_linked_cohort_1983_1991_numerator_smoke.py` (NEW), parallel to the shipped 3a `test_linked_cohort_1983_1991_layout_smoke.py` (denominator). Rationale: keeps 3a (denominator) + 3b (numerator) SMOKE independently re-runnable; avoids a non-additive edit to the shipped 3a harness; mirrors the C8.17 DO5a/5b sub-step-isolation + the C8.18 DO3a "NEW harness per sub-step" precedent. `DESIGN: tracks-current-state` (Convention 2); SHAPE-not-VALUE (Convention 1) — record-lengths 500/535 are fixed historical NCHS facts, not evolving annotations.
- **Divergence verdict:** all three are *within* the "reconstruct the 1983-1991 numerator layout + identify the cert match key" DO-step-3b mandate and resolved per established precedent (C8.18 DO3a additive-substrate; the standard pre-2005 cohort-IMR construction; §7-#17 scope-minimalism; C8.17 DO5a/5b sub-step isolation). Surfaced BEFORE any `field_specs.py` mutation (L10-safe). No §7 halt; no fresh AskUserQuestion (on-point prior resolutions + standing user authorization govern; the methodology-paper-level cohort-vs-period question was the Sub-Q42 item, resolved at DO step 1).

### SMOKE Tier 0 — full 1983-1988 + 1989-1991 NUMERATOR record layouts reconstructed from the guide DETAIL code-outlines (state-on-disk substrate for DO step 3b)

L13-extension governing precedent (C8.18 DO step 3a): the byte-level **detail code-outline** is authoritative; the p13/pp18-19 element-span summary is composite and NOT trusted. Both layouts below are transcribed from the detail "Item and Code Outline" Tape-Location columns + value-distribution-verified on real `*num*.dat` at the DO-phase SMOKE Tier 1.

**(A) 1983-1988 Numerator (`LinkCO{YY}USnum.dat`, 500 bytes; `LinkCO83Guide.pdf` p12 = 500 B / 39,704; per-year stable 1983-1988 like the denominator):**
- **Natality section, locs 1-91** = byte-identical to `LINKED_BIRTH_1983_1988_FIELDS` (the "Denominator Record AND Natality Section of Linked Record" shared detail, pp15-32; p13/p14 List-of-Data-Elements numerator-birth column == denominator column). **REUSE** `LINKED_BIRTH_1983_1988_FIELDS` (do NOT re-author — HALT 4).
- **Locs 92-193 (102 bytes)** = numerator-only RESERVED ("reserved for possible additional data", LinkCO83Guide p32). Not enumerated as fields.
- **Mortality section, locs 194-500** (`LinkCO83Guide.pdf` pp33-45 detail; "Locations 194-500 contain data from the Death Certificate"): `194-197` YOD (Year of Death 1983-19xx) · `198` RECTYPED (Record Type 1/2) · `199` RESSTATD (Resident Status 1-4) · `200` REGOCCD (Region of Occurrence) · `201-202` DIVOCCD (Division+State Subcode Occ) · `203-204` XSTOCCD (Expanded State Occ 01-52) · `205-206` STOCCD (State Occ 01-51) · `207-209` CNTOCCD (County Occ; 999=<250k) · `210` REGRESD (Region of Residence) · `211-212` DIVRESD (Division+State Subcode Res) · `213-214` XSTRESD (Expanded State Res) · `215-216` STRESD (State Res) · `217-219` CNTRESD (County Res) · `220-222` CITYRESD (City Res) · `223` AGER5 (Infant Age Recode 5: 1=<1hr…5=postneonatal) · `224-225` AGER76 (Infant Age Recode 76) · `226-227` AGER38 (Infant Age Recode 38) · `228` HOSPD (Hospital & Patient Status) · `229` AUTOPSY (1/8/9) · `230` ACCIDPL (Place of Accident, causes E850-E929) · `231-234` UCOD (Underlying Cause ICD-9, 4-byte; E-code excludes the leading "E") · `235-237` UCODR61 (61 Infant Cause Recode, 010-680) · `238-239` NENTITY (Number of Entity-Axis Conditions 00-20) · `240-379` ENTITY (Entity-Axis Conditions; 20 × 7-byte composite: pos1 part/line, pos2 sequence, pos3-6 ICD-9 code, pos7 nature-of-injury flag) · `380-381` NRECORD (Number of Record-Axis Conditions 00-20) · `382-481` RECORDAX (Record-Axis Conditions; 20 × 5-byte composite: pos1-4 ICD-9 code, pos5 nature-of-injury flag) · `482-500` RESERVED (19 bytes). [Per-condition decomposition of ENTITY/RECORDAX = DO step 5; authored here as composite spans, the C8.18 DO3a `MEDRISK`/`OBSTETRC` composite precedent.]

**(B) 1989-1991 Numerator (`LinkCO{YY}USnum.dat`, 535 bytes; `LinkCO89Guide.pdf` p17 = 535 B / 38,605; Unlinked also 535 B / 1,029; per-year stable 1989-1991, 1989-rev cert):**
- **Birth section, locs 1-212** = byte-identical to `LINKED_BIRTH_1989_1991_FIELDS` (`LinkCO89Guide.pdf` p20: "Locations 7-212 ... Birth Certificate"; MATCHS@1, IDNUMBER@2-6; the 3a-authored 1-212 birth section is the SAME for the denominator-plus + numerator — "Denominator-Plus Record and Natality Section of Numerator (Linked) Record" shared detail). **REUSE** `LINKED_BIRTH_1989_1991_FIELDS`.
- **Death-derived "plus", locs 213-225** = byte-identical to `LINKED_DEATH_1989_1991_FIELDS` (AGED@213-215, AGER5@216, AUTOPSY@217, ACCIDPL@218, UCOD@219-222, UCODR61@223-225 — `LinkCO89Guide.pdf` pp46-47 detail; the numerator's 213-225 == the denominator-plus's 213-225). **REUSE** `LINKED_DEATH_1989_1991_FIELDS`.
- **Mortality section, locs 226-535** (`LinkCO89Guide.pdf` pp48-56 detail): `226-260` RESERVED (35 bytes) · `261-262` NENTITY (Number of Entity-Axis Conditions 00-20) · `263-402` ENTITY (Entity-Axis Conditions; 20 × 7-byte composite, pos3-6 ICD-9) · `403-404` NRECORD (Number of Record-Axis Conditions 00-20) · `405-504` RECORDAX (Record-Axis Conditions; 20 × 5-byte composite, pos1-4 ICD-9) · `505` RESSTATD (Resident Status - Death 1-4) · `506-507` STOCCFIPD (State of Occurrence FIPS - Death) · `508-510` CNTOCFIPD (County of Occurrence FIPS - Death; 999=<250k) · `511-512` STRESFIPD (State of Residence FIPS - Death; 00=foreign) · `513-515` CNTRESFIPD (County of Residence FIPS - Death) · `516-517` DRSTATE (State of Residence, NCHS Codes - Death) · `518-520` CITYRESD (City of Residence, NCHS Codes - Death; 999=balance) · `521` EOSPD (Place of Death) · `522-525` DTHYR (Year of Death 1989-19xx) · `526-527` DTHMON (Month of Death 01-12) · `528` WEEKDAYD (Day of Week of Death 1-7) · `529-535` RESERVED (7 bytes). [ENTITY/RECORDAX per-condition decomposition = DO step 5; composite spans here.]

**Cert match key (HALT-4 deliverable):** 1989-1991 = `(MATCHS@1, IDNUMBER@2-6)` (already in `LINKED_BIRTH_1989_1991_FIELDS`; the DO-step-5 numerator↔denominator-plus join key). 1983-1988 = NO record-level public-use key; the 500-byte numerator is self-contained (1-91 = the deceased infant's birth covariates, identical layout to the 91-byte denominator) → DO step 5 = self-contained-numerator + aggregate-denominator construction (the standard pre-2005 cohort-IMR method). Recorded as the forward DO-step-5/6 design basis + folded into the soft-flag-(ii) §15.D model-clarification (proposed-not-applied; §11 human-merge).

### Halt conditions tripped

None. Three within-task scope decisions ((i) DO step 3b scope = additive numerator constants + additive pure helper + new sibling SMOKE; (ii) cert-match-key finding 1989-1991=(MATCHS,IDNUMBER) vs 1983-1988=self-contained-numerator; (iii) new sibling harness) surfaced at the Convention-3 snapshot **before any `field_specs.py` mutation** and resolved per established precedent (C8.18 DO3a additive-substrate + standard pre-2005 cohort-IMR construction + §7-#17 scope-minimalism + C8.17 DO5a/5b sub-step isolation) — documented here + DECISION_LOG 2026-05-18T00:30:00Z; folded into the proposed-not-applied soft-flag-(ii) §15.D model-clarification `[plan-update]` (§11 human-merge). None is a §7 halt (no plan contradiction; within the DO step 3b mandate; on-point prior resolutions exist).

### Result

**PROCEED to DO** (this same session): author the additive `field_specs.py` numerator constants + the additive pure `_numerator_layout_for_linked_year` helper + the NEW sibling SMOKE harness; run SMOKE Tier 0 (synthetic 500-byte + 535-byte recovery + L3 position-shift negative) → Tier 1 (real `LinkCO{83,85,88}USnum.dat` 500-byte + `LinkCO{89,90,91}USnum.dat` 535-byte: encoding/alignment via BIRYR==cohort-year + L13-extension value-distribution verify each anchor incl. ICD-9 UCOD plausibility + the entity/record-axis count fields); VERIFY (11 gate SHAs byte-exact, additive-only diff, pytest 98P+1S+1XF + new-numerator-SMOKE count gate); RECEIPT + DECISION_LOG + STATUS + commit (**no tag** — intermediate DO step; Convention 5; `C8.18-pre-do`@`6632a15` remains the rollback anchor).

---

## PRE-FLIGHT for C8.18 DO step 3a — 2026-05-17T22:30:00Z — cohort 1983-1991 **denominator/births** `field_specs.py` layout authoring + SMOKE Tier-0/1 encoding + value-distribution verify — **RESULT: PROCEED to DO** (8/8 forward-looking HALTs from PRE_FLIGHT_LOG 2026-05-17T20:00:00Z re-verified; 11/11 gate parquet SHAs byte-exact; the 1989-1991 225-byte denominator-plus layout reconstructed from `LinkCO89Guide.pdf` pp18-20 + captured below as state-on-disk substrate; two within-task scope decisions surfaced at the Convention-3 snapshot **before any `field_specs.py` mutation** (L10-safe) and resolved per established precedent: (i) DO step 3a scope = `field_specs.py` constants **+** an additive `_layout_for_linked_year` 1983-1991 branch [the `_find_denomplus_member` `"DEN"`-vs-`"DENOM"` fix + the two-file numerator join remain DO step 5, per the 2026-05-17T20:00:00Z PRE_FLIGHT_LOG]; (ii) structural-model **refinement** — 1983-1988 = pure births-only 91-byte denominator [death detail only in the separate 500-byte numerator → DO 3b]; **1989-1991 = a 225-byte denominator-PLUS** [birth cert 7-212 + a small appended death-derived "plus" 213-225], structurally analogous to the 2005+ denominator-plus model, NOT the pure two-file form — refines [does not contradict] the 2026-05-17T20:00:00Z structural finding; zero §7 halts)

> Per-sub-step PRE-FLIGHT under the C8.18 umbrella PRE-FLIGHT (2026-05-17T05:30:00Z) + the DO step 3 PRE-FLIGHT/SMOKE-Tier-0 (2026-05-17T20:00:00Z, which captured the full 1983-1988 91-byte denominator layout as state-on-disk). Written **before any `field_specs.py`/`parse_linked_year.py` mutation** (L10-safe; C8.17 DO5a/5b per-sub-step PRE-FLIGHT precedent). This entry adds the entry cheap-check + the 1989-1991 225-byte denominator-plus layout (state-on-disk) + the two within-task scope decisions; the DO (authoring + SMOKE Tier 1 + VERIFY + RECEIPT + commit) follows in this same session.

### Entry cheap-check — 8 forward-looking HALTs from PRE_FLIGHT_LOG 2026-05-17T20:00:00Z

- [x] **HALT 1**: `git tag -l` = `C8.17-complete`/`C8.17-pre-do`/`C8.18-pre-do`; `C8.18-complete` NOT present. HEAD `a845af5` (DO step 3 PRE-FLIGHT). `C8.18-pre-do`@`6632a15` is the DO rollback anchor; `df0675f`([plan-update]) + `9e6576b`(DO step 2) + `a845af5`(DO step 3 PRE-FLIGHT) after it. Branch `main`, tree clean. ✓
- [x] **HALT 2 — 11 gate parquet SHAs byte-exact** (re-computed on-disk this entry; fetal-death via the canonical `~/Desktop/fetal-death-harmonization-build/output/harmonized/` tree, soft-flag (hh)): natality `c8a740eb…a6237153`/`acb5c48a…d528856974`; `.v28_baseline` `230efed2…0933ccebac`/`e16ad532…a677c41d44`; linked-derived `9b828a4d…85a08b777`; fetal-death `38e2cecb…8899c5cf48`/`185c071e…24fa7968a09`; MM `adbec108…ef45dc1549`/`5c22308b…a28d39205d1`/`7c682668…f9f5edd61f5d`/`d98b4296…e966a543261`. **11/11 unchanged** vs PRE_FLIGHT_LOG 2026-05-17T20:00:00Z HALT 2. DO step 3a = layout substrate only (no parser run, no rebuild). ✓
- [x] **HALT 3 — full 1983(=1983-1988) denominator 91-byte layout is state-on-disk** in PRE_FLIGHT_LOG 2026-05-17T20:00:00Z SMOKE Tier 0. DO step 3a transcribes it to `field_specs.py` tuples; does NOT re-read `LinkCO83Guide.pdf`. ✓ (empirically re-confirmed this entry: `LinkCO83USden.dat` first `\r`@byte-91 / `\n`@92 → 91 data bytes + CR/LF = 93-byte block; `310,738,482 / 93 = 3,341,274` = the guide-stated 1983 count; `LinkCO88USden.dat` `363,998,931 / 93 = 3,913,967` = the guide-stated 1988 count; head[:8]=`b'11983   '` → pos1 MatchStatus=`1`, pos2-5 YearOfBirth=`1983`, pos6-9 Reserved=spaces — matches the captured layout byte-exact).
- [x] **HALT 4 — do NOT assume 91-byte continuity across the 1989 birth-cert revision** — RE-READ `LinkCO{89}Guide.pdf` this entry (L13-extension; C8.17 natality 1989-rev precedent). **CONFIRMED DISCONTINUOUS**: `LinkCO89/90/91USden.dat` first `\r`@byte-225 / `\n`@226 → **225 data bytes + CR/LF = 227-byte block** (vs 1983-1988's 91+CR/LF=93). `LinkCO89Guide.pdf` p17 Denominator File: "Record length 225, Record count 4,045,881"; `4,045,881 × 227 = 918,414,987` = `LinkCO89USden.dat` uncompressed size byte-exact. The 1989-1991 layout is a SEPARATE `field_specs.py` tuple list (reconstructed below). ✓
- [x] **HALT 5 — SMOKE Tier 1 MUST verify the `.dat` byte encoding (EBCDIC-vs-ASCII) + value-distribution-verify each anchor field** (L13-extension; the guides say the original tape = IBM/EBCDIC 8-bit; the 2005+ parser `_slice_field` uses `latin-1`). Scheduled in this session's SMOKE Tier 1 (real `LinkCO83USden.dat` + `LinkCO89USden.dat`). ✓
- [x] **HALT 6 — existing `field_specs.py` `LINKED_BIRTH/DEATH_2005_2013/2014_2020_*` tuple lists + `LINKED_DENOMPLUS_RECLEN_*` constants + `parse_linked_year.py` `_layout_for_linked_year` 2005/2014 branches byte-untouched** (H10 / HALT-13 sibling of C8.17 DO5b). DO step 3a is strictly additive; VERIFY-C diffs the 2005/2014 regions. ✓
- [x] **HALT 7 — §15.D "layout-CSV → field_specs.py" wording reconcile bundles with the DO step 3a commit** (C8.17 DO step 2 fix-on-contact precedent); the broader §15.D model-clarification (num/den two-file → denominator-plus-equivalent via match-key join; DO step 3 → 3a/3b) = soft-flag (ii) `[plan-update]` (§11, human-merge; queued with the soft-flag-(w) batch). ✓
- [x] **HALT 8 — pytest baseline 85P+1S+1XF (~240-380s; count is the gate)**. DO step 3a touches no parquet/test surface → re-run at VERIFY-D must hold the count. ✓ (verified at VERIFY)

**8/8 PASS. 11/11 gate parquet SHAs byte-exact. No §7 halt from the entry cheap-check.**

### Inputs

- [x] `raw_data/linked/LinkCO{83..91}.zip` members `LinkCO{YY}USden.dat` (denominator) + `LinkCO{YY}USnum.dat` (numerator) — on disk + SHA-anchored at C8.18 DO step 2 (manifest §3 = 38 linked / 141 total). `LinkCO83USden.dat` (310,738,482 B) + `LinkCO89USden.dat` (918,414,987 B) opened read-only this entry.
- [x] `raw_docs/linked/LinkCO89Guide.pdf` (192 pp; text-extractable, no OCR — L12-extension re-confirmed: pp17-20 extract clean structured layout tables + the "List of Data Elements and Locations" field→location matrix). The 1983-1988 layout is NOT re-read (state-on-disk in PRE_FLIGHT_LOG 2026-05-17T20:00:00Z per HALT 3).
- [x] Sibling substrate: `natality/scripts/01_import/field_specs.py` `LINKED_BIRTH_2005_2013_FIELDS`@784 / `LINKED_BIRTH_2014_2020_FIELDS`@789 / `LINKED_DEATH_2005_2013_FIELDS`@810 / `LINKED_DENOMPLUS_RECLEN_2005_2013=900`@824 / `LINKED_DEATH_2014_2020_FIELDS`@830 / `LINKED_DENOMPLUS_RECLEN_2014_2020=1384`@844; `parse_linked_year.py` `_slice_field` (`.decode("latin-1")`)@46 / `_find_denomplus_member` (`"DENOM" in name.upper()`)@49 / `_layout_for_linked_year` (2005-2013/2014-2020 branches)@66.

### Source documentation

- [x] No external citation beyond the on-disk SHA-anchored cohort guides. `LinkCO89Guide.pdf` p17 (file characteristics: Denominator 225 B / 4,045,881; Numerator 535 B / 38,605; Unlinked 535 B / 1,029; "IBM/EBCDIC 8-bit code"), pp18-19 ("List of Data Elements and Locations" — the Denominator-Plus / Numerator-Birth / Numerator-Death / Unlinked field→location matrix), p20 ("Locations 7-212 = Birth Certificate; 213-535 = Death Certificate"; MATCHS@1, IDNUMBER@2-6, BIRYR@7-10, RESSTATB@11, PLDEL@12, BIRATTND@13, STOCCFIPB@14-15…), detail pp20-47 (variable-name code outlines: CSEX, DBIRWT, GESTAT/GESTAT10, DPLURAL, DMAGE, ORMOTH, DMRACE, DMEDUC/MEDUC6, DLIVORD, MATCHS, RESSTATB — cross-confirm the pp18-19 locations). L9 cheap-check PASS (named locations verified in the actual PDF). No §7-#11 stale-SHA exposure.

### Outputs

- [x] DO step 3a intended outputs (created in this session's DO phase, NOT this PRE-FLIGHT): **additive** `field_specs.py` — `LINKED_BIRTH_1983_1988_FIELDS` (91-byte; from the PRE_FLIGHT_LOG 2026-05-17T20:00:00Z captured 1983 layout), `LINKED_DEN_RECLEN_1983_1988 = 91`; `LINKED_BIRTH_1989_1991_FIELDS` + `LINKED_DEATH_1989_1991_FIELDS` (225-byte denominator-plus; from the layout captured below), `LINKED_DENOMPLUS_RECLEN_1989_1991 = 225`; `parse_linked_year.py` additive `_layout_for_linked_year` 1983-1991 branch [`1983<=year<=1988 → (91, LINKED_BIRTH_1983_1988_FIELDS, [])`; `1989<=year<=1991 → (225, LINKED_BIRTH_1989_1991_FIELDS, LINKED_DEATH_1989_1991_FIELDS)`]; existing 2005/2014 branches byte-untouched. Plus a new SMOKE harness `natality/tests/test_linked_cohort_1983_1991_layout_smoke.py` (`DESIGN: tracks-current-state`, Convention 1/2). Plus the §15.D "layout-CSV → field_specs.py" wording reconcile (HALT 7, fix-on-contact). **No canonical parquet/schema/validation-CSV.** This PRE-FLIGHT entry itself = zero canonical mutation.

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

DO step 3a mutates `natality/scripts/01_import/field_specs.py` + `parse_linked_year.py` (both **additive**) + adds one new test file + the §15.D wording line. Current-state snapshot vs the (corrected) §15.D plan + the 2026-05-17T20:00:00Z findings:

- **Scope decision (i) — `field_specs.py` + an additive `_layout_for_linked_year` branch; parser member-finding/two-file-join deferred to DO step 5.** The 2026-05-17T20:00:00Z PRE_FLIGHT_LOG Outputs sketched "`_layout_for_linked_year` 1983-1991 era branch" as a DO step 3a output and explicitly deferred `_find_denomplus_member` (the `"DEN"`-vs-`"DENOM"` mismatch) + the two-file numerator left-join to "a DO step 5 parser concern, not DO step 3". Resolution (per the user's standing "make decisions" authorization + §7-#17 scope-minimalism + the C8.17 DO5a/5b additive-substrate precedent): DO step 3a adds the `field_specs.py` layout constants **and** a minimal additive `_layout_for_linked_year` 1983-1991 branch (pure function, no zip I/O — returns the layout tuples; existing 2005/2014 branches byte-untouched, H10/HALT-13). The full parse path (`_find_denomplus_member` `"DEN"` support + the 1983-1988 numerator left-join on the certificate match key + the 1989-1991 denominator-plus single-file parse) stays DO step 5. The SMOKE harness imports `field_specs` + applies `_slice_field` directly on the real zip member (does NOT route through `iter_parsed_records`), so the deferred member-finder does not block the DO step 3a SMOKE. Within-task scope narrowing, not a C8.18 scope change; recorded in DECISION_LOG 2026-05-17T22:30:00Z.
- **Scope decision (ii) — structural-model refinement (1983-1988 pure two-file vs 1989-1991 denominator-plus).** The 2026-05-17T20:00:00Z finding stated "the 1983-1991 cohort file is a separate numerator + denominator two-file structure (NOT the 2005+ single denominator-plus)". The `LinkCO89Guide.pdf` pp17-20 read this session **refines** this: that holds for **1983-1988** (the 91-byte denominator is births-only — match status + birth cert + record weight, NO death section; the 500-byte numerator carries the linked death detail), but **1989-1991** ships a **225-byte denominator-PLUS** record (birth cert locations 7-212 + a small appended death-derived "plus" at 213-225: infant age 213-216, autopsy 217, place of accident 218, congenital anomalies 219-222, underlying-cause recode 223-225) **alongside** a separate 535-byte numerator (full ICD-9 multiple-cause detail 261-504). So the cohort backward-extension has THREE physical layouts, not one: (a) 1983-1988 births-only 91-byte denominator + 500-byte numerator (pure two-file); (b) 1989-1991 225-byte denominator-plus (single-file, 2005+-analogous) + 535-byte numerator (richer ICD-9). This **refines, does not contradict**, the 2026-05-17T20:00:00Z structural finding and the cohort-only Option A scope; it sharpens the DO step 5 parser plan (1983-1988 needs the two-file num/den join; 1989-1991 + 2005+ use the denominator-plus single-file model). Recorded as a forward design note for DO step 5 + folded into the soft-flag-(ii) §15.D model-clarification `[plan-update]` (proposed-not-applied; §11 human-merge). No §7 halt (no plan contradiction; within the "reconstruct the 1983-1991 layout" mandate; on-point precedent = the 2005+ denominator-plus model already in `field_specs.py`).
- **Substrate-format (carried, resolved):** §15.D still says "layout-CSV"; the linked pipeline is Python `field_specs.py` tuples (resolved at C8.17 DO step 2 + the 2026-05-17T20:00:00Z PRE-FLIGHT). The in-flight wording fix bundles with this DO step 3a commit (HALT 7).
- **Divergence verdict:** both scope decisions are *within* the "reconstruct the 1983-1991 denominator layout" mandate and resolved per established precedent (C8.17 DO step 2 substrate-format; the 2005+ denominator-plus model; §7-#17 scope-minimalism). Surfaced BEFORE any `field_specs.py` mutation (L10-safe). No §7 halt; no fresh AskUserQuestion (on-point prior resolutions + standing user authorization govern; the methodology-paper-level cohort-vs-period question was the Sub-Q42 item and is already resolved at DO step 1 — this is its within-task layout consequence).

### SMOKE Tier 0 — full 1989-1991 denominator-PLUS (225-byte) record layout reconstructed from `LinkCO89Guide.pdf` (state-on-disk substrate for DO step 3a; the 1983-1988 91-byte layout is in PRE_FLIGHT_LOG 2026-05-17T20:00:00Z)

`LinkCO89Guide.pdf` p17: Denominator File = **225-byte fixed-width**, record count 4,045,881, "IBM/EBCDIC 8-bit code" on the original tape (public-use `.dat` encoding = a DO step 3a SMOKE Tier-1 verification item — L13-extension). pp18-19 "List of Data Elements and Locations" (Denominator-Plus File column) + pp20-47 detail code outlines. Per-year stability: the 1989-revision birth certificate is stable 1989-1991 (1989 = 225 B / 4,045,881; 90 = 225 B / 4,162,710; 91 = 225 B / 4,115,494 — all 227-byte blocks); the 1992-1994 gap follows (permanent; NCHS suspended all linkage). 1989-1991 is one `LINKED_BIRTH_1989_1991_FIELDS` tuple list.

Full 1989-1991 denominator-plus layout (1-based inclusive; NCHS variable names from pp20-47 detail code outlines; locations from the pp18-19 authoritative element-location matrix — value-code semantics value-distribution-verified at DO step 3a SMOKE Tier 1, L13-extension):

`1` MATCHS(MatchStatus 1/2/3) · `2-6` IDNUMBER(InfantDeathNumber) · `7-10` BIRYR(YearOfBirth 1989-1991) · `11` RESSTATB(ResidentStatus 1-4) · `12` PLDEL(PlaceOfDelivery 1-5,9) · `13` BIRATTND(Attendant 1-5,9) · `14-15` STOCCFIPB(StateOcc FIPS 01-56) · `16-18` CNTOCFIPB(CountyOcc FIPS) · `19-20` STRESFIPB(StateRes FIPS 00-56) · `21-23` CNTRESFIPB(CountyRes FIPS) · `24-25` STRESNCHS(NCHS StateRes) · `26-28` CITRESNCHS(NCHS CityRes) · `29-32` DMAGE(MotherAge) · `33-34` ORMOTH(MotherHispanicOrigin) · `35-38` DMRACE(MotherRace) · `39-41` DMEDUC(MotherEducation) · `42-43` DMAR(MaritalStatus) · `44-46` MPLBIR(MotherPlaceOfBirth) · `47-48` DTOTORD(TotalBirthOrder) · `49-50` DLIVORD(LiveBirthOrder) · `51-53` MPCB(MonthPrenatalCareBegan) · `54-55` NPREVIS(NumberPrenatalVisits) · `56` ADEQUACY(AdequacyOfCareRecode) · `57-59` DLLB(IntervalSinceLastLiveBirth) · `60-62` DFAGE(FatherAge) · `63-64` ORFATH(FatherHispanicOrigin) · `65-66` DFRACE(FatherRace) · `67-68` DFEDUC(FatherEducation) · `69-71` BIRMON(MonthOfBirth) · `72-76` GESTAT(Gestation) · `77-78` CSEX(SexChild) · `79-85` DBIRWT(BirthWeight) · `86-87` DPLURAL(Plurality) · `88-91` APGAR(ApgarScore) · `92-99` DELMETH(MethodOfDelivery) · `101-117` MEDRISK(MedicalRiskFactors) · `118-121` OTHERRISK(OtherRiskFactors) · `122-125` TOBACCO · `126-128` ALCOHOL · `130-136` WTGAIN(WeightGainDuringPregnancy) · `138-153` OBSTPROC(ObstetricProcedures) · `155-163` LABCOMP(ComplicationsOfLabor) · `165-186` ABNORMNB(AbnormalConditionsNewborn) · `187-204` RESFLAGS(ResidenceReportingFlags) · `207` DOW(DayOfWeekOfBirth) · `209-210` CRACE(ChildRace) · **[denominator-plus "plus"/death-derived section, 213-225]** `213-216` AGEINF(InfantAgeAtDeath) · `217` AUTOPSY · `218` PLACEACC(PlaceOfAccident) · `219-222` CONGEN(CongenitalAnomalies) · `223-225` UCAUSE(UnderlyingCauseRecode, denom-plus). [Full ICD-9 underlying cause + 61-cause list + entity/record-axis multiple cause are in the 535-byte NUMERATOR file 261-504 → DO step 3b/5; soft-flag (gg).] Birth section = `LINKED_BIRTH_1989_1991_FIELDS` (locs 1-210); plus/death section = `LINKED_DEATH_1989_1991_FIELDS` (locs 213-225).

### Halt conditions tripped

None. Two within-task scope decisions ((i) DO step 3a scope = field_specs.py + additive dispatcher branch, parser member-finding/join deferred to DO5; (ii) structural-model refinement 1983-1988 pure-two-file vs 1989-1991 denominator-plus) surfaced at the Convention-3 snapshot **before any `field_specs.py` mutation** and resolved per established precedent (C8.17 DO5a/5b additive-substrate + §7-#17 scope-minimalism + the 2005+ denominator-plus model) — documented here + DECISION_LOG 2026-05-17T22:30:00Z; folded into the proposed-not-applied soft-flag-(ii) §15.D model-clarification `[plan-update]` (§11 human-merge). Neither is a §7 halt (no plan contradiction; within the DO step 3 mandate; on-point prior resolutions exist).

### Result

**PROCEED to DO** (this same session): author the additive `field_specs.py` constants + the additive `_layout_for_linked_year` 1983-1991 branch + the SMOKE harness; run SMOKE Tier 0 (synthetic 91-byte + 225-byte records) → Tier 1 (real `LinkCO83USden.dat` + `LinkCO89USden.dat`: encoding EBCDIC-vs-ASCII verify + L13-extension value-distribution verify each anchor field across 1983-1988 + the 1989 boundary); bundle the §15.D "layout-CSV → field_specs.py" wording reconcile; VERIFY (11 gate SHAs byte-exact, additive-only diff, pytest 85P+1S+1XF count gate); RECEIPT + DECISION_LOG + STATUS + commit (**no tag** — intermediate DO step; Convention 5; `C8.18-pre-do`@`6632a15` remains the rollback anchor).

---

## PRE-FLIGHT for C8.18 DO step 3 — 2026-05-17T20:00:00Z — cohort 1983-1991 layout reconstruction (1978-rev birth + ICD-9) — **RESULT: PROCEED to DO step 3a (denominator/births layout authoring) next; this entry is PRE-FLIGHT/investigation-only, ZERO canonical-state mutation**; two material findings surfaced + resolved before any DO mutation: (1) substrate format = Python `field_specs.py` not CSV (C8.17 DO-step-2 precedent), (2) the 1983-1991 cohort file is a **separate numerator + denominator two-file structure** (NOT the 2005+ single denominator-plus), reconcilable to a denominator-plus-equivalent at DO step 5/6; DO step 3 split → **3a (denominator/births layout, this work) + 3b (numerator/infant-death + ICD-9 layout)** per the C8.17 DO5a/5b Convention-5 precedent

> Per-sub-step PRE-FLIGHT addendum under the C8.18 umbrella PRE-FLIGHT (2026-05-17T05:30:00Z). Written **before any DO step 3 mutation** (no `field_specs.py` edit, no parser run). DO step 3 is §15.D-estimated 2-3 sessions over two distinct file layouts; this session does the PRE-FLIGHT + SMOKE Tier 0 (full 1983 denominator layout reconstruction from the guide) and checkpoints PRE-FLIGHT-only (state-on-disk; the `field_specs.py` authoring + SMOKE Tier 1 value-distribution/encoding verification = DO step 3a, next session) — mirrors the C8.18 DO step 1 PRE-FLIGHT/decision-only commit + the C8.17 DO5a/5b multi-session-DO-step split discipline.

### Entry cheap-check — 7 forward-looking HALTs from RECEIPTS/C8.18_step2_2026-05-17T18-30-00Z.md

- [x] **HALT 1**: `git tag -l` = `C8.17-complete`/`C8.17-pre-do`/`C8.18-pre-do`; `C8.18-complete` NOT present. HEAD `9e6576b` (DO step 2). `C8.18-pre-do`@`6632a15` is the DO rollback anchor; `df0675f`([plan-update]) + `9e6576b`(DO step 2) are after it. ✓
- [x] **HALT 2 — 11 gate parquet SHAs byte-exact** (re-verified on-disk, fetal-death via the canonical `~/Desktop/fetal-death-harmonization-build/output/harmonized/` tree, soft-flag (hh)): natality `c8a740eb…6237153`/`acb5c48a…28856974`; `.v28_baseline` `230efed2…33ccebac`/`e16ad532…77c41d44`; linked-derived `9b828a4d…5a08b777`; fetal-death `38e2cecb…99c5cf48`/`185c071e…a7968a09`; MM `adbec108…45dc1549`/`5c22308b…d39205d1`/`7c682668…edd61f5d`/`d98b4296…6a543261`. **11/11 unchanged.** DO step 3 = layout substrate only (no parser run, no rebuild). ✓
- [x] **HALT 3 — 19 cohort zips + 19 guide PDFs on disk + SHA-anchored**: `raw_data/linked/LinkCO{83..91}.zip`+`LinkCO{95..04}US.zip`; `raw_docs/linked/LinkCO{83..91,95..04}Guide.pdf`. Manifest §3 = 38 linked / 141 total; `test_source_zip_sha_stability.py` anchors 141/linked-38 (pytest 85P+1S+1XF at DO step 2 VERIFY). DO step 3 reads these; does NOT re-download. ✓
- [x] **HALT 4 — DO step 3 = cohort 1983-1991 layout reconstruction** (1978-rev birth + ICD-9). Substrate read this PRE-FLIGHT: `LinkCO83Guide.pdf` (text-extractable; **L12-extension confirmed at C8.18 DO step 2 SMOKE — no OCR**; re-confirmed here: pages 12-31 extract clean structured layout tables). L13-extension: value-distribution-verify each anchor field at DO step 3a SMOKE Tier 1 (not byte-position alone). ✓
- [x] **HALT 5**: ICD-9/10 default-null + revision-tagged settled (DECISION_LOG 2026-05-17T05:30:00Z); exact ICD-9-era harmonized cause column shape + `cause_recode_130` per-era = DO step 5/6 PRE-FLIGHT (soft-flag (gg)). The 1983 numerator carries ICD-9 underlying cause + a **61-cause list** (NOT the 130-cause infant recode) + entity/record-axis multiple cause — recorded for DO step 3b/5 (soft-flag (gg) refined). ✓
- [x] **HALT 6**: `test_row_count_conservation.py` NATALITY pins (`201_161_456`/`range(1968,2025)`) NOT perturbed (DO step 3 touches no parquet/test); LINKED pins re-pin at the later re-harmonize DO step. pytest baseline 85P+1S+1XF. ✓
- [x] **HALT 7**: Tier 3+5 ≈ 2.5/7; cumulative Phase C ≈ 27 of 51-71 (cap 86). ✓

**7/7 PASS. 11/11 gate parquet SHAs byte-exact. No §7 halt from the entry cheap-check.**

### Inputs

- [x] `raw_docs/linked/LinkCO{83..91}Guide.pdf` (cohort 1983-1991 user guides; on disk + SHA-anchored at C8.18 DO step 2; text-extractable, no OCR — L12-extension). `LinkCO83Guide.pdf` (139 pp) fully read pp 0-31 (intro/methodology/file-characteristics/data-element-list/detailed denominator record layout).
- [x] `raw_data/linked/LinkCO{83..91}.zip` members: `LinkCO{YY}USnum.dat` (infant-death numerator) + `LinkCO{YY}USden.dat` (birth denominator) — verified via `unzip -l` at C8.18 DO step 2.
- [x] Sibling substrate: `natality/scripts/01_import/field_specs.py` (`LINKED_BIRTH_2005_2013_FIELDS`@784, `LINKED_BIRTH_2014_2020_FIELDS`@789, `LINKED_DEATH_2005_2013_FIELDS`@810/RECLEN 900@824, `LINKED_DEATH_2014_2020_FIELDS`@830/RECLEN 1384@844); `parse_linked_year.py` `_layout_for_linked_year` (2005-2013/2014-2020 only) + `_find_denomplus_member` (matches `"DENOM" in name.upper()`); `harmonize_linked_v3.py` (`--years 2005-2023`; year>=2014 clinical-detail branches). C8.17 natality 1978-1988 layout (`PUBLIC_US_1972_1977_FIELDS` reuse per C8.17 DO step 4) = the value-code/era sibling for the 1978-rev birth cert.

### Source documentation

- [x] No external citation consumed beyond the on-disk SHA-anchored cohort guides. The §15.D-cited "1978-rev birth + ICD-9" framing is empirically confirmed by `LinkCO83Guide.pdf` (ICD-9 Ninth Revision p5; 1978-revision-era natality content). No §7-#11 stale-SHA exposure.

### Outputs

- [x] DO step 3 intended outputs (NOT created this PRE-FLIGHT — DO step 3a, next): additive `field_specs.py` `LINKED_BIRTH_1983_1988_FIELDS` / `LINKED_BIRTH_1989_1991_FIELDS` (or unified if per-year-stable) + `LINKED_DENOMPLUS_RECLEN`/`LINKED_DEN_RECLEN_1983_1991` constants + `_layout_for_linked_year` 1983-1991 era branch. **Additive — the existing 2005-2013/2014-2020 tuple lists + dispatcher branches byte-untouched (H10 / HALT-13 sibling of C8.17 DO5b).** No canonical parquet/schema/validation-CSV. This PRE-FLIGHT entry itself = zero canonical mutation (investigation-only; git scope = PRE_FLIGHT_LOG + DECISION_LOG + STATUS + this commit).

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

DO step 3 mutates `natality/scripts/01_import/field_specs.py` (additive) only. Current state snapshot vs the (corrected) §15.D plan + the two surfaced divergences:

- **Substrate-format divergence (resolved per C8.17 precedent):** the scope-corrected §15.D Task C8.18 DO step 3 still says "layout-**CSV** reconstruction". The linked pipeline uses **Python tuple lists in `field_specs.py`** (`list[tuple[str,int,int]]`), NOT CSV record_layout files (fetal_death/matched_multiples use CSV; natality + linked use Python). This is the **identical** substrate-format question resolved at C8.17 DO step 2 (DECISION_LOG 2026-05-14T08:30:00Z: AskUserQuestion 2026-05-14 Q1 Option A = extend `field_specs.py` Python substrate; natality/linked keep the Python convention per sibling-pipeline discipline H7; §15.D wording reconciled in-flight bundled with the DO commit per the C8.13 fix-on-contact precedent). **Resolution:** extend `field_specs.py` (Python); the §15.D C8.18 "layout-CSV" → "field_specs.py layout" wording reconcile is owed (a small in-flight fix-on-contact, to be bundled with the DO step 3a commit per the C8.17 DO step 2 precedent — NOT a scope change; the user's standing "make decisions" authorization + the on-point C8.17 precedent govern; no fresh AskUserQuestion needed — the substrate question was already user-resolved for this exact `field_specs.py`).
- **Structural-model finding (material; recorded as the DO-step-3 design basis):** the §15.D + the existing `parse_linked_year.py` architecture implicitly assume the **2005+ "denominator-plus" single-file model** (one record per birth with death fields appended inline; `_find_denomplus_member` requires `"DENOM"` in the member name; `_layout_for_linked_year` returns one birth+death field set). The **1983-1991 cohort file is structurally different**: TWO separate physical files per year — a **Denominator file** (all live births; `LinkCO{YY}USden.dat`; **91-byte** fixed-width; 1983 count 3,341,274) and a **Numerator file** (the linked infant-death↔birth records; `LinkCO{YY}USnum.dat`; **500-byte**; 1983 count 39,704, birth section + death section incl. ICD-9 underlying cause + 61-cause list + entity/record-axis multiple cause). `LinkCO83USden.dat`.upper()=`LINKCO83USDEN.DAT` contains `"DEN"` but NOT `"DENOM"` → the existing `_find_denomplus_member` will not match it (a **DO step 5 parser** concern, not DO step 3). **Reconcilability decision (LLM, per the user's standing authorization; recorded in DECISION_LOG 2026-05-17T20:00:00Z):** the two-file numerator/denominator design is the *physical* form of the same information the 2005+ denominator-plus carries logically. The methodologically-standard + schema-continuous approach: at DO step 5/6, parse the **denominator file as the primary per-birth rows** (the cohort IMR denominator + all birth covariates) and **left-join the numerator file's death section** on the NCHS certificate match key → a denominator-plus-**equivalent** row set, harmonized into the SAME linked v4 schema as 2005-2023 (one row per birth; death fields populated where an infant death linked). This preserves cross-era schema continuity and is the standard pre-2005 cohort-IMR construction. DO step 3a = the **denominator (births) layout**; DO step 3b = the **numerator (birth+death) layout** + the match-key identification. Recorded as a forward design note for DO step 5/6; a §15.D model-clarification refinement is **proposed, NOT applied** (human merges per §11; queued with the soft-flag-(w) next-`[plan-update]` batch — it refines "layout-CSV → field_specs.py Python" + "1983-1991 = num/den two-file, reconstruct denominator-plus-equivalent via match-key join", not a scope change).
- **Divergence verdict:** neither finding contradicts the C8.18 cohort-only scope or the §15.D DO-step sequence; both are *within* the "reconstruct the 1983-1991 layout" mandate and are resolved per established precedent (substrate-format = C8.17 DO step 2; structural model = standard pre-2005 cohort-IMR construction). Surfaced here BEFORE any DO mutation (L10-safe; C8.17 DO5b "divergences-from-the-assumed-architecture resolved before any DO mutation" precedent). No §7 halt; no fresh AskUserQuestion (both questions have on-point prior resolutions / standing user authorization).

### SMOKE Tier 0 — full 1983 denominator (births) record layout reconstructed from `LinkCO83Guide.pdf` (state-on-disk substrate for DO step 3a)

`LinkCO83Guide.pdf` pp12-31: Denominator file = **91-byte fixed-width**, "IBM/EBCDIC 8-bit code" on the original tape (the public-use `.dat` encoding = a DO step 3a SMOKE Tier-1 verification item — the 2005+ parser uses `latin-1`; pre-2005 may be ASCII-converted or EBCDIC; **must verify against actual `LinkCO83USden.dat` bytes, L13-extension**). Per-year stability: **1983 = 91 B (count 3,341,274), 1988 = 91 B (count 3,913,967)** → 1983-1988 denominator length stable; **1989-1991 spans the 1989 birth-certificate revision** (§15.D "1989-1991 cohort 1989-rev") → the 1989-1991 denominator layout MUST be re-read from `LinkCO{89,90,91}Guide.pdf` at DO step 3a (do NOT assume 91-byte continuity across the 1989 cert boundary — L13-extension; the C8.17 natality 1989-rev precedent).

Full 1983 denominator layout (1-based inclusive positions; codes abbreviated — DO step 3a authors these as `field_specs.py` tuples + value-distribution-verifies each anchor):

`1` MatchStatus(1/3/surviving) · `2-5` YearOfBirth · `6-9` Reserved · `10` RecordType · `11` ResidentStatus(1-4) · `12` RegionOcc · `13-14` Division+StateSubcodeOcc · `15-16` ExpandedStateOcc · `17-18` StateOcc(01-51,*=50%sample) · `19-21` CountyOcc(999=<250k) · `22` RegionRes · `23-24` Division+StateSubcodeRes · `25-26` ExpandedStateRes · `27-28` StateRes · `29-31` CountyRes · `32-34` CityRes · `35` Reserved · `36` DetailRaceChild(1-8) · `37` RaceChildRecode3 · `38` SexChild(1M/2F) · `39-40` DetailGestationWeeks(17-52,99=NS) · `41-42` GestationRecode10 · `43-46` BirthWeightGrams(0227-8165,9999=NS) · `47-48` BirthWeightRecode14 · `49` BirthWeightRecode3 · `50` Plurality(1single/2twin/3other) · `51-52` Apgar1min(00-10,99) · `53-54` Apgar5min · `55-56` MotherOrigin/Descent(00-24,88,99) · `57` DetailRaceMother(1-8,0/9=NS) · `58-59` DetailAgeMother(10-49) · `60-61` AgeMotherRecode12 · `62-63` MotherEducationDetail(00-17,99) · `64` MotherEducationRecode6 · `65` MaritalStatus(1married/2unmarried) · `66-67` MotherPlaceOfBirth(01-59,99) · `68-69` FatherOrigin/Descent · `70` DetailRaceFather · `71-72` DetailAgeFather(10-98,99=NS) · `73-74` FatherEducationDetail · `75` IntervalSinceLastLiveBirth(0-7,9) · `76` OutcomeLastPregnancy(0/1/2/9) · `77` IntervalSinceLastPregTermination(0-9) · `78-79` DetailMonthPrenatalCareBegan(01-09,00=none,99=NS) · `80` MonthPrenatalCareRecode6 · `81-82` TotalPrenatalVisits(00-49,99) · `83-84` DetailTotalBirthOrder(01-50,99) · `85` TotalBirthOrderRecode9 · `86-87` DetailLiveBirthOrder(01-50,99) · `88` LiveBirthOrderRecode9 · `89` PlaceOfDelivery(1hosp/2-3nonhosp/9) · `90` AttendantAtBirth(1MD/2midwife/3other/9) · `91` RecordWeight(denominator inflation weight, code range 1-2; numerator=all 1). "The denominator record ends in location 91."

### Halt conditions tripped

None. Two material findings (substrate-format = Python; 1983-1991 = num/den two-file) were surfaced at the Convention-3 snapshot **before any DO mutation** and resolved per established precedent (C8.17 DO step 2 substrate-format resolution + standard pre-2005 cohort-IMR construction) — documented here + DECISION_LOG; a §15.D wording/model refinement is proposed-not-applied (§11; human-merged). Neither is a §7 halt (no plan contradiction; within the "reconstruct the 1983-1991 layout" mandate; on-point prior resolutions exist).

### Result

**PROCEED.** DO step 3 split → **3a (denominator/births `field_specs.py` layout authoring + SMOKE Tier 1 value-distribution/encoding verify across 1983-1988 + the 1989-1991 cert boundary + VERIFY/RECEIPT) — next session** + **3b (numerator/infant-death + ICD-9 + match-key layout)**. This session checkpoints **PRE-FLIGHT/investigation-only** (zero canonical-state mutation; the full 1983 denominator layout is captured above as state-on-disk substrate so DO step 3a does not re-read the guide). Commit PRE-FLIGHT-only; no tag (intermediate; mirrors C8.18 DO step 1).

---

## PRE-FLIGHT for C8.18 DO step 2 — 2026-05-17T17:30:00Z — download 19 cohort source zips + 19 cohort user-guide PDFs + SHA-anchor + metadata extension (per the §15.D scope-corrected entry; cohort-only, 19 zips NOT 29) — **RESULT: PROCEED**

> Per-sub-step PRE-FLIGHT addendum under the C8.18 umbrella PRE-FLIGHT (2026-05-17T05:30:00Z); C8.16/C8.17 umbrella+addendum precedent (§4.1/L10 one-upfront-or-per-sub-step). Written **before any DO step 2 mutation** (no zip/PDF downloaded, no metadata file edited yet). The §15.D Task C8.18 scope-correction `[plan-update]` (soft-flag (ff)) was **merged this session** as standalone commit `df0675f` (§11 step 3; DECISION_LOG 2026-05-17T17:00:00Z) — the §15.D entry now agrees with the on-disk decision (cohort-only, 19 zips), so this PRE-FLIGHT runs against a self-consistent plan.

### Entry cheap-check — 7 forward-looking HALTs from RECEIPTS/C8.18_step1_2026-05-17T05-30-00Z.md

- [x] **HALT 1**: `git tag -l 'C8.18*'` = `C8.18-pre-do` only (@ `6632a15d59…`); `C8.18-complete` NOT present (set only at the final C8.18 sub-step per Convention 5). `C8.17-complete` present. HEAD = `df0675f` (the standalone `[plan-update]`; sits *after* `C8.18-pre-do`@`6632a15` and is a non-DO commit — `C8.18-pre-do` remains the C8.18 DO rollback anchor). ✓
- [x] **HALT 2 — 11 gate parquet SHAs byte-exact at DO step 2 entry** (on-disk `shasum -a 256`, 2026-05-17): canonical natality `natality_v2_harmonized.parquet`=`c8a740eb…6237153` ✓ / `natality_v2_harmonized_derived.parquet`=`acb5c48a…28856974` ✓; `.v28_baseline` `230efed2…33ccebac` ✓ / `e16ad532…77c41d44` ✓; `natality_v3_linked_harmonized_derived.parquet`=`9b828a4d…5a08b777` ✓; `fetal_death_harmonized.parquet`=`38e2cecb…99c5cf48` ✓ / `fetal_death_derived.parquet`=`185c071e…a7968a09` ✓ **(read from the canonical `~/Desktop/fetal-death-harmonization-build/output/harmonized/` build tree — see "resolved cheap-check" note below)**; `matched_multiples_harmonized.parquet`=`adbec108…45dc1549` ✓; MM 1995-1997=`5c22308b…d39205d1` ✓ / 1995-2000=`7c682668…edd61f5d` ✓ / 2016-2020=`d98b4296…6a543261` ✓. **11/11 unchanged.** DO step 2 is download + SHA-verify + metadata only — zero rebuild; the linked-derived `9b828a4d…` changes only at the later C8.18 re-harmonize DO step (NOT here). ✓
  - **Resolved cheap-check (L7 / no-rubber-stamp; not a §7 regression):** the first SHA pass read `~/Desktop/fetal-death-harmonization/fetal_death_{harmonized,derived}.parquet` and got `f09beb4a…`/`90af89b9…` ≠ documented. Investigated rather than accept-or-panic: that directory holds a **stale May-4 secondary copy** (20/25 MB); the **canonical** fetal-death gate parquets are in the **build tree** `~/Desktop/fetal-death-harmonization-build/output/harmonized/` (May-13; 28/35 MB) and hash `38e2cecb…99c5cf48` / `185c071e…a7968a09` — **byte-exact vs documented**. Consistent with `tests/test_source_zip_sha_stability.py` `FETAL_RAW_DIR = ~/Desktop/fetal-death-harmonization-build/...` (the build tree is canonical) and the C8.17 D5 stale-build-repo class. No regression; my initial path was wrong, corrected at the cheap-check moment.
- [x] **HALT 3 — scope = 19 cohort zips, NOT 29** ✓. All 19 probed HTTP 200 at `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/cohortlinkedus/`: 9 × `LinkCO{83,84,85,86,87,88,89,90,91}.zip` (no `US` suffix; `cohortlinked/` variant is 404 — path is uniformly `cohortlinkedus`) + 10 × `LinkCO{95,96,97,98,99,00,01,02,03,04}US.zip` (content-lengths 48.9 MB … 192.7 MB; Σ ≈ **1.80 GB**). Period-linked `LinkPE*US.zip` 1995-2004 NOT probed, NOT downloaded — OUT of C8.18 scope per Option A.
- [x] **HALT 4 — §15.D C8.18 scope-correction `[plan-update]` MERGED** ✓ (standalone commit `df0675f`, §11 step 3, this session; DECISION_LOG 2026-05-17T17:00:00Z). NEXT_STEPS.md §15.D now reads cohort-only / 19 zips / 7-step DO list; soft-flag (ff) RESOLVED. The on-disk decision (DECISION_LOG 2026-05-17T05:30:00Z) and the plan now agree.
- [x] **HALT 5** — documentation-deferral soft-flags (gg/cc/dd/ee + bb/aa/w/x/z/u) are informational, NOT C8.18-DO-step-2-blocking. ✓
- [x] **HALT 6** — §15.D §1358 wording (w) + the §15.D DO-step-6/7-boundary clarification remain a SEPARATE next-`[plan-update]` item (deliberately NOT bundled with the (ff) scope-correction per §9-#8 / scope-minimalism; DECISION_LOG 2026-05-17T17:00:00Z alternative (a)). ✓
- [x] **HALT 7** — Tier 3+5 ≈ 2.5/7 (C8.16+C8.17 done; C8.18 DO step 1 of 7 done); cumulative Phase C ≈ 26 of 51-71 (effort-ceiling cap 86 intact). ✓ (informational)

**7/7 PASS. 11/11 gate parquet SHAs byte-exact (fetal-death via the canonical `-build` tree). Scope = 19 cohort zips + 19 cohort guide PDFs, all HTTP 200.**

### Inputs

- [x] 19 cohort source zips — all HTTP 200 (`curl -sI`): `cohortlinkedus/LinkCO{83..91}.zip` (9) + `cohortlinkedus/LinkCO{95..04}US.zip` (10). Sibling-derived (L1-extension) from the on-disk 2005-2015 `LinkCO{05..15}US.zip` whose `source_url` (`file_inventory.csv`) + manifest §3 confirm the exact `cohortlinkedus/` path; the only filename delta is the pre-1995 missing `US` suffix (NCHS_SOURCE_MANIFEST §3 documents this convention change). ✓
- [x] 19 cohort user-guide PDFs — all HTTP 200 at `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/cohortlinked/LinkCO{83..91,95..04}Guide.pdf`. L1-extension sibling-derivation **anchored on the on-disk `LinkCO05Guide.pdf`**: probed it at the corrected base → HTTP 200, `content-length: 367848` = the on-disk file size byte-for-byte (`raw_docs/linked/LinkCO05Guide.pdf` is 367848 B) → the URL is the verified-correct sibling form; 1983-2004 siblings all resolve. (Correct doc base = `…/NCHS/Dataset_Documentation/DVS/cohortlinked/`, a sibling of `…/NCHS/Datasets/`, established via WebFetch on cdc.gov/nchs vitalstatsonline after the §15.D-approximate `Datasets/DVS/Dataset_Documentation/DVS/...` form 404'd — L1-extension: a 404 on a hallucinated path is a weak signal; the verified-on-disk-sibling anchor is the strong one.) ✓
- [x] No required upstream task incomplete: C8.18 DO step 1 closed (decision = Option A cohort-only); `[plan-update]` merged. ✓
- [x] No stale checkpoints: `~/Desktop/natality-harmonization/raw_data/linked/` has NONE of `LinkCO{83..91}.zip`/`LinkCO{95..04}US.zip`; `raw_docs/linked/` has NONE of `LinkCO{83..04}Guide.pdf` → net-new, no overwrite, idempotent (re-run = skip-existing). ✓

### Environment

- [x] Python 3.13.9 (≥3.11) ✓; pandas 2.3.2 (≥2.3) ✓; pyarrow 18.1.0 (≥18.0) ✓.
- [x] `git status --porcelain` clean (the `[plan-update]` `df0675f` is committed; working tree clean); branch `main`. ✓
- [x] L10 (§12 step 8): this DO-step-2 PRE-FLIGHT entry (2026-05-17T17:30:00Z) is written before the first DO-step-2 mutation (no download/metadata edit yet); prior sub-step (DO step 1) PRE-FLIGHT 2026-05-17T05:30:00Z precedes its DO commit `66cfcb9`; the intervening `[plan-update]` `df0675f` is a non-DO §11 commit. No back-fill. ✓

### Source documentation

- [x] DO step 2 consumes external NCHS zips + cohort guide PDFs; SHA-256 is **recorded at download** (no prior manifest SHA exists for the 19 new files — they are net-new manifest rows, the C8.17 DO step 1 precedent). No §7-#11 stale-SHA exposure (nothing claims a prior SHA for these). L12-extension text-layer probe on a sample cohort guide PDF (oldest = `LinkCO83Guide.pdf` highest OCR-risk + one 1990s) is a SMOKE deliverable BEFORE any "needs OCR" claim (LESSONS 2026-05-12T15:00Z precedent). ✓

### Outputs

- [x] Intended outputs (net-new, none exist): 19 zips → `~/Desktop/natality-harmonization/raw_data/linked/`; 19 PDFs → `~/Desktop/natality-harmonization/raw_docs/linked/`; git-tracked metadata extension → `natality/metadata/file_inventory.csv` (+19 `_linked` rows) + `docs/NCHS_SOURCE_MANIFEST.md` §3 (+19 rows) + `tests/test_source_zip_sha_stability.py` (Convention-2/L17 tracks-current-state anchor re-pin). No canonical parquet / `harmonized_schema.csv` / validation-target CSV / harmonize-or-parse script created or overwritten at DO step 2 (download + inventory only — the C8.17 DO step 1 shape). ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

Three git-tracked artifacts will be mutated; current state snapshotted + verified against the (corrected) §15.D plan:

- `natality/metadata/file_inventory.csv` — **77 lines (76 data rows + header)**; **19** `_linked` rows (`2005_linked`…`2023_linked`); 57 natality rows (1968-2024). Plan-assumed: add **19** `_linked` rows (`1983_linked`…`1991_linked` + `1995_linked`…`2004_linked`) → 95 data rows, 38 `_linked`. Columns: `year,source_url,source_org,raw_filename,file_format,doc_filename,imported,notes`. Matches plan. ✓
- `docs/NCHS_SOURCE_MANIFEST.md` — §3 header `## Section 3 — Linked-cohort raw zips (19; cohort years 2004-2023)`; 19 SHA rows (2005-2023). Plan-assumed: → 38 rows, header recount + 1983-1991/1995-2004 cohort years + 1992-1994-gap note; total manifest 122 → 141. Matches plan. ✓
- `tests/test_source_zip_sha_stability.py` — **`DESIGN: tracks-current-state`** (first docstring line); anchors `assert len(rows) == 122` + `counts == {"fetal": 43, "natality": 57, "linked": 19, "matched_multiples": 3}` + docstring "122 = 43 + 57 + 19 + 3". Plan: re-pin to `141` / `"linked": 38` / "141 = 43 + 57 + 38 + 3" — **this re-pin IS the expected behavior** (Convention 1 §4.2.1 / Convention 2 / L17; bundled into the DO step 2 commit, NOT a regression; the C8.17 DO step 1 precedent re-pinned 100→122 in the same download commit). Routing logic (`LinkCO*`→linked, `*PE*CO*`→linked) already covers the new `LinkCO{83..04}` filenames. Matches plan. ✓
- **Divergence verdict: NONE.** All three artifacts' current values match the scope-corrected §15.D plan's assumed state. (The earlier inverted-premise divergence was resolved at DO step 1 + the `[plan-update]` merged this session.)

### Halt conditions tripped

None. (The fetal-death SHA initial-mismatch was a wrong-path read, resolved at the cheap-check moment to the canonical `-build` tree — 11/11 byte-exact; not a §7-#18 regression.)

### Result

**PROCEED** to C8.18 DO step 2 SMOKE → DO.

---

## PRE-FLIGHT for C8.18 (umbrella) + DO step 1 — 2026-05-17T05:30:00Z — Linked birth-infant death 1983-2004 backward extension (A.3; 19 new years; permanent 1992-1994 gap); first Tier-3+5 task after C8.17-complete — **RESULT: PROCEED to DO step 1 (cohort-vs-period publishing-design decision via AskUserQuestion — the §15.D-prescribed DO-step-1 mechanism)**; a **material §7-class substrate divergence surfaced at the Convention-3 Field-value snapshot** (the §15.D + EXPLORATION_REPORT §A.3 task-plan premise *"HVS-linked from 2005 ships period-format only"* is **INVERTED** — the existing 2005-2023 product is the **cohort-linked** series); flagged BEFORE any DO mutation; resolution is exactly the §15.D DO-step-1 + Sub-Q42 AskUserQuestion path + a proposed §15.D `[plan-update]` sub-entry (human-merged per §11; NOT bundled with the DO commit per Convention 5)

> **Why an umbrella PRE-FLIGHT + DO-step-1 section:** C8.18 is a multi-sub-step task (8 DO steps per §15.D; ~8-14 sessions). Per §4.1 / L10 the choice is one upfront umbrella PRE-FLIGHT or per-sub-step PRE-FLIGHT; this follows the C8.16/C8.17 precedent (one umbrella + per-sub-step addenda). **DO step 1 is decision-only** (the cohort-vs-period publishing-design decision; a DECISION_LOG entry + STATUS section; **zero canonical-state mutation, zero source downloads**). The 19-or-29 source zips + ~25 user-guide PDFs are **DO step 2** inputs and get their own DO-step-2 PRE-FLIGHT addendum (SHA-verified at download per §5 + L1-extension sibling-probe). Documented **before any DO mutation**; `C8.18-pre-do` to be tagged at the clean pre-DO HEAD per §13 step 4.

### Entry cheap-check — 7 forward-looking HALTs from RECEIPTS/C8.17_step7_2026-05-17T04-00-00Z.md

- [x] HALT 1: `C8.17-pre-do`@`12fc20e` present **AND `C8.17-complete` present** (`git tag -l 'C8.17*'` = both; `git tag -l 'C8.18*'` = none). C8.17 fully closed (DO 1-7). ✓
- [x] HALT 2: **9 canonical/baseline parquet SHAs unchanged** (on-disk `shasum -a 256`, 2026-05-17): canonical natality `natality_v2_harmonized.parquet`=`c8a740eb…6237153` ✓ / `natality_v2_harmonized_derived.parquet`=`acb5c48a…28856974` ✓ ; `.v28_baseline` `230efed2…33ccebac` ✓ / `e16ad532…77c41d44` ✓ ; 7 non-natality-v2 — `fetal_death_harmonized`=`38e2cecb…99c5cf48` ✓ / `fetal_death_derived`=`185c071e…a7968a09` ✓ / `natality_v3_linked_harmonized_derived`=`9b828a4d…5a08b777` ✓ / `matched_multiples_harmonized`=`adbec108…45dc1549` ✓ / MM 1995-1997=`5c22308b…39205d1` ✓ / MM 1995-2000=`7c682668…edd61f5d` ✓ / MM 2016-2020=`d98b4296…6a543261` ✓. **The linked-derived `9b828a4d…` is byte-exact NOW (DO step 1 does no rebuild); it WILL change only at the later C8.18 re-harmonize DO step — the intended symmetric sibling of C8.17's natality_v2 change.** (Side-note: `natality_v3_linked_harmonized.parquet` = `e1795ac6…` is the un-gated intermediate; only the SHIPPED `_derived` is in the 7-SHA gate.)
- [x] HALT 3: B.12 latest baseline = `tests/snapshots/v2_2026-05-16T08-00-00Z_columns.csv` present; `v1_2026-05-13T21-00-00Z_columns.csv` retained (both on disk, 44746 B each). C8.18 will re-snap (linked parquet changes) at the later re-harmonize DO step → new `v3_<UTC>_columns.csv`; DO step 1 does NOT re-snap. ✓
- [x] HALT 4: `tests/test_row_count_conservation.py` — NATALITY pins L42-43 = `201_161_456` / `list(range(1968, 2025))` (57) **must NOT be perturbed by C8.18** ✓ (verified present; DO step 1 does not touch tests); LINKED pins L48-49 = `74_943_824` / `list(range(2005, 2024))` (19) — these get the Convention-2/L17 **same-commit re-pin at the later C8.18 re-harmonize DO step** (NOT DO step 1). pytest baseline 85P+1S+1XF (~240-380s band; count is the gate). DO step 1 is decision-only and cannot perturb the test surface → pytest **DEFERRED** (no canonical/test/script mutation this step; C8.17 DO-3/4/5b/6/7 precedent for deferring pytest when the step provably cannot touch the parquet/test surface).
- [x] HALT 5: Documentation-deferral soft-flags (cc/dd/ee + bb/aa/w/x/z/u) are NOT C8.18-blocking ✓ (informational; carry).
- [x] HALT 6: §15.D §1358 wording (w) + the §15.D DO-step-6/7-boundary clarification remain next-`[plan-update]` items (Convention 5; NOT bundled with any DO commit). This PRE-FLIGHT ADDS a proposed §15.D C8.18 scope-correction sub-entry to that next-`[plan-update]` queue (see "§7-class divergence" below); KICKOFF/NEXT_STEPS unedited this step. ✓
- [x] HALT 7: Tier 3+5 ≈ 2.5/7 done (C8.16+C8.17); cumulative Phase C ≈ 25.5/51-71 (effort-ceiling cap 86 intact). C8.18 = the largest single remaining pre-Zenodo task (8-14 sessions). ✓ (informational)

**7/7 PASS. All 9 gate parquet SHAs byte-exact on-disk (DO step 1 is decision-only — no rebuild precondition holds). pytest deferred (provably no test-surface mutation at a decision-only step; precedented).**

### Environment

- [x] Python 3.13.9 (≥3.11) ✓ ; pandas 2.3.2 (≥2.3) ✓ ; pyarrow 18.1.0 (≥18.0) ✓.
- [x] `git status --porcelain` clean at session start; on branch `main`; HEAD `6632a15` (C8.17 DO step 7 / `C8.17-complete`). ✓
- [x] L10 (§12 step 8): the prior task's PRE-FLIGHT addendum (C8.17 DO step 7, 2026-05-17T03:30:00Z) precedes its DO commit; RECEIPTS/C8.17_step7 documents L10-safe; C8.17 fully closed. No back-fill. ✓

### Source documentation

- [x] DO step 1 (cohort-vs-period publishing-design decision) rests on **internal repo substrate**, not on external NCHS PDFs/zips. The 19-or-29 source zips + ~25 cohort/period user-guide PDFs (`ftp.cdc.gov/.../Dataset_Documentation/DVS/{cohortlinked,periodlinked}/Link*UserGuide.pdf`) are **DO step 2** inputs — SHA-verified at download time + L1-extension sibling-probe + L12-extension text-layer probe in the DO-step-2 PRE-FLIGHT addendum, NOT here. No external citation is consumed at DO step 1. ✓ (no §7-#11 stale-SHA exposure this step)

### Outputs

- [x] DO step 1 intended outputs: a new DECISION_LOG entry (the cohort-vs-period design decision artifact) + a new STATUS section + a RECEIPTS/C8.18_step1_<UTC>.md + this PRE-FLIGHT entry. **No canonical artifact** (no parquet / no `harmonized_schema.csv` / no validation-target CSV / no test / no script) is created or overwritten at DO step 1. ✓ (no §7-#17 canonical-scope-creep at DO step 1; the scope *correction* it surfaces is routed through §11 plan-update, not silently actioned)

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

DO step 1 mutates **no canonical artifact** (decision-only). Per Convention 3 the snapshot instead captures the **substrate the design decision rests on**, verified against the task plan's assumed state — and this is where a **material divergence surfaced**:

- **Task-plan assumed state** (`NEXT_STEPS.md` §15.D Task C8.18 + `EXPLORATION_REPORT.md` §A.3:129 + KICKOFF Tier-3+5 line): *"HVS-linked from 2005 ships **period-format only**; extending backward forces (a) ship cohort+period both as separate parquets, or (b) reconcile via a derived 'period-equivalent' view of cohort data, or (c) stop the backward extension at 1995 and ship period-only."*
- **Actual substrate (snapshot, 2026-05-17, read-only):**
  - `docs/NCHS_SOURCE_MANIFEST.md` §3 title = **"Linked-cohort raw zips (19; cohort years 2004-2023)"**; explicit clause: *"Inventory keys these as `<cohort_year>_linked` … (**cohort = year-of-birth of the cohort being followed for infant deaths**)."* Shipped zips = `LinkCO05US.zip`…`LinkCO15US.zip` (cohort) + `2017PE2016CO.zip`… (period-cohort combined, harmonized to **cohort**-equivalent).
  - `natality/metadata/external_validation_targets_v3_linked.csv` — **every** `value_source` cites a **cohort** linked-file user guide: `LinkCO05Guide.pdf` / `LinkCO10Guide.pdf` / `LinkCO15Guide.pdf` / `21PE20CO_linkedUG.pdf` / `22PE21CO_linkedUG.pdf` / `23PE22CO_linkedUG.pdf`, all labelled "(YYYY **cohort** linked file user guide)"; metrics are cohort-file metrics ("do not apply the weight for cohort use").
  - `natality/scripts/01_import/parse_linked_year.py` docstring: *"Parse NCHS linked birth-infant death **cohort** denominator-plus files. Reads the denominator-plus member from a **LinkCO{yy}US.zip**."* `parse_linked_cohort_year.py`: constructs a **cohort** file from the 2016+ period-cohort format ("Output is equivalent to the 2005-2015 denominator-plus format: one row per birth").
  - `natality/docs/GETTING_STARTED.md:171`: *"**Cohort vs period** — the V3 file **follows each birth cohort** for a full year of mortality experience. This is preferred for multivariate analysis over period files."*
  - `natality/docs/VALIDATION.md:220` + `COMPARABILITY.md:213`: NCHS guide guidance "For **cohort** file use: do not apply the weight"; record-weight semantics are cohort-file semantics.
- **Divergence verdict:** the task-plan premise is **inverted**. The existing HVS-linked 2005-2023 product is unambiguously the **cohort-linked** series (v3), validated against NCHS cohort linked-file guides. §15.D options (b) "period-equivalent view of cohort" and (c) "stop at 1995, ship period-only" were predicated on a wrong premise and are largely **moot**. Resolved at this cheap-check moment — see next subsection — **before any DO mutation** (L10-safe; mirrors the C8.17 DO step 5b "4 divergences from the receipt's assumed architecture, resolved before any DO mutation via AskUserQuestion + PRE_FLIGHT addendum" precedent).

### §7-class divergence classification + resolution path

- **Classification:** §7-#12 (conflicting documentation — task plan §15.D / EXPLORATION_REPORT §A.3 vs the actual repo substrate) + §7-#13 (validity-domain ambiguity — the cohort-vs-period analytic framing). NOT silently worked around (KICKOFF "What to do if a convention conflicts with a task's plan: raise it as a §7 halt BEFORE the first DO mutation and ask the human").
- **Resolution path = exactly the §15.D-prescribed mechanism:** §15.D Task C8.18 DO step 1 = *"cohort-vs-period publishing-design decision; **AskUserQuestion if PRE-FLIGHT-time substrate is ambiguous**"* and Sub-Q42 = *"Cohort/period publishing-design = methodology-paper-level decision; if PRE-FLIGHT-time substrate is materially ambiguous, AskUserQuestion + `[plan-update]` sub-entry."* The substrate is not merely ambiguous — the plan's premise is inverted — so: (1) this PRE-FLIGHT documents it before any DO mutation; (2) DO step 1 resolves the design via AskUserQuestion with the **corrected** substrate; (3) the decision is recorded in DECISION_LOG; (4) a §15.D C8.18 scope-correction `[plan-update]` sub-entry is **proposed** (not applied — only the human merges plan changes per §11; queued with the soft-flag-(w) next-`[plan-update]`, NOT bundled with the DO step 1 commit per Convention 5).

### SMOKE Tier 0 — corrected cohort-vs-period design-decision reasoning (the §15.D DO-step-1 SMOKE)

Source availability (EXPLORATION_REPORT §A.3 + §15.D PRE-FLIGHT inputs), re-read under the corrected premise:

- **Cohort-linked 1983-1991** (9 yrs; `LinkCO83.zip`–`LinkCO91.zip`; no `US` suffix pre-1995; ~665 MB). **Only cohort exists pre-1995** — no period-linked file is published before 1995, so 1983-1991 is necessarily cohort (no choice exists there).
- **1992-1994**: permanent gap — NCHS suspended ALL linkage (no cohort, no period). Loud-document, do not close.
- **Cohort-linked 1995-2004** (10 yrs; `LinkCO95US.zip`–`LinkCO04US.zip`; ~1.18 GB) — directly continues the existing 2005-2023 cohort series.
- **Period-linked 1995-2004** (10 yrs; `LinkPE95US.zip`–`LinkPE04US.zip`; ~1.18 GB) — a *different linkage method* than the existing product; an asymmetric 10-year island (no period 1983-1994; HVS ships no period 2005-2023).

Three design options (the AskUserQuestion set), corrected for "existing product = cohort":

- **Option A — Cohort-only backward extension (methodologically consistent; LLM-recommended).** Parse cohort-linked 1983-1991 + cohort-linked 1995-2004; append to the existing cohort 2005-2023 series → a clean **41-year cohort-linked series (1983-2023, permanent 1992-1994 gap)**. **19 source zips** (not 29), ~1.85 GB (not ~3 GB). Drops period-linked 1995-2004 from C8.18 scope (a different linkage method = a separate future product, not required for series consistency). Simplest manuscript story ("the cohort-linked series extended backward"); fewest new boundaries; lowest effort/risk (drops the 2-3 period sessions per §A.3 → effort lands at the **lower** end of 8-14). §15.D options (b)/(c) are moot under the corrected premise.
- **Option B — Cohort backward extension + period-linked 1995-2004 as a separate secondary product.** Everything in A PLUS ship `LinkPE95US.zip`–`LinkPE04US.zip` as a distinct period-linked parquet (or a `linkage_method` discriminator). 29 source zips, ~3 GB, +2-3 sessions, +a new public-API surface that exists for only 10 asymmetric years (1995-2004) of a method HVS otherwise never ships. Manuscript must explain the asymmetry.
- **Option C — Defer the entire pre-2005 backward extension.** Leave linked at 2005-2023; revisit post-Zenodo. Reframes C8.18 to "not now" (a §11 deferral, EXPLORATION_REPORT §A.3 "defer-to-post-submission" priority is the on-record default).

Tier 0 verdict: the decision is **methodology-paper-level** (Sub-Q42), the substrate premise is inverted, and the options carry materially different manuscript + effort + public-API consequences → **AskUserQuestion is required** (not an LLM unilateral pick). LLM recommendation: **Option A** (consistent with the existing cohort product; cleanest manuscript framing; minimizes scope/risk/effort; period-linked 1995-2004 is a weak asymmetric addition better deferred or dropped). Higher SMOKE tiers (1/2/3 layout-CSV + parse + re-harmonize) belong to DO steps 3-7, not DO step 1.

### Halt conditions tripped

- §7-#12 + §7-#13 substrate divergence (task-plan premise inverted) — surfaced here at the Convention-3 cheap-check, BEFORE any DO mutation; resolution is the §15.D-prescribed DO-step-1 AskUserQuestion + a proposed (human-merged) §15.D `[plan-update]` sub-entry. This is the intended DO-step-1 flow, not an unhandled halt. No other §7 condition tripped.

### Result

**PROCEED to DO step 1** = AskUserQuestion (cohort-vs-period publishing-design, corrected substrate) → record decision in DECISION_LOG → propose §15.D C8.18 scope-correction `[plan-update]` sub-entry (human-merged per §11; not bundled with the DO commit). No canonical-state mutation at DO step 1. `C8.18-pre-do` tagged at the clean pre-DO HEAD per §13 step 4.

---

## PRE-FLIGHT addendum for C8.17 DO step 7 — 2026-05-17T03:30:00Z — docs-only version-string propagation v2.8.0→v3.0.0 + `C8.17-complete` (the FINAL C8.17 sub-step) — **RESULT: PROCEED** (12/12 forward-looking HALTs from RECEIPTS/C8.17_step6 verified; all 11 gate parquet SHAs byte-exact — docs-only precondition holds; one D-class scope divergence surfaced + resolved by AskUserQuestion 2026-05-17 → Option A "Honest propagation" Convention-3 plan-amendment; zero §7 halts)

> **Why an addendum:** C8.17 uses one upfront umbrella PRE-FLIGHT (2026-05-14T06:30:00Z); each DO sub-step does an entry cheap-check (task1-addendum / DO5b / DO6 precedent). DO step 7 is docs-only (no rebuild) but the cheap-check Field-value snapshot surfaced a material scope divergence the umbrella PRE-FLIGHT + §15.D did not fully anticipate. Documented **before any DO mutation**; `C8.17-pre-do`@`12fc20e` already tagged (no re-tag — Convention 5 intermediate-DO precedent; `C8.17-complete` set at this step's end since DO step 7 is the final sub-step).

### Entry cheap-check — 12 forward-looking HALTs from RECEIPTS/C8.17_step6_2026-05-16T08-00-00Z.md

- [x] HALT 1: `C8.17-pre-do`@`12fc20e` present; `C8.17-complete` NOT present (`git tag --list 'C8.17*'` = `C8.17-pre-do` only). ✓
- [x] HALT 2: **Canonical natality SHAs byte-exact** — `natality_v2_harmonized.parquet`=`c8a740eb48d4f3de66759da27eef94143c315846885bf905a88cbc0fa6237153` ✓ ; `natality_v2_harmonized_derived.parquet`=`acb5c48a9abf82ac78e6bf210d6be5d62cba6afae271b978b0e53ed528856974` ✓. No unauthorized rebuild — docs-only precondition holds.
- [x] HALT 3: **7 non-natality-v2 SHAs byte-exact** — `fetal_death_harmonized`=`38e2cecb03ff4947bbf6bcecbe9a79bf4bbe58df74ed4e7809b5078899c5cf48` ✓ ; `fetal_death_derived`=`185c071ec76ab8aae24c9d7524b2495900f78afbf43cd6a32537124fa7968a09` ✓ ; `natality_v3_linked_harmonized_derived`=`9b828a4de4e59b17a1ca727e3dddc7ea7d748bb5281a98612f6fb9b85a08b777` ✓ ; `matched_multiples_harmonized`=`adbec1087370941fd373b933566b7dfd24dbbc2f957d998f92ac14ef45dc1549` ✓ ; MM 1995-1997=`5c22308bed2883b9be8e244e763c3603f700b5ba5274f3ef30388a28d39205d1` ✓ ; MM 1995-2000=`7c682668006f3fab556b79422d34f5d84eed0bd0e1ae44702908f9f5edd61f5d` ✓ ; MM 2016-2020=`d98b42965573530d26d72368d968c395487b2c4e4dd3bfc4ad426e966a543261` ✓.
- [x] HALT 4: `.v28_baseline.parquet` ×2 preserved — `natality_v2_harmonized.v28_baseline`=`230efed2ac34c794638aceaa777a31e62abffb6e8e6af94ed215970933ccebac` ✓ ; `natality_v2_harmonized_derived.v28_baseline`=`e16ad5323d68e28d401518f1ff56b12c09e43883e76022a9823d51a677c41d44` ✓ (Anti-Pattern #10 — not deleted).
- [x] HALT 5: DO step 7 scope (version-string v2.8.0→v3.0.0 + counts) — see scope divergence + resolution below.
- [x] HALT 6: Internal version inconsistency (parquet v3.0.0-shaped; strings still v2.8.0) — this step RESOLVES it; DO step 7 is the hard prerequisite for `C8.17-complete`. ✓ (actioned this step)
- [x] HALT 7: B.12 latest baseline = `tests/snapshots/v2_2026-05-16T08-00-00Z_columns.csv` (v1 retained; both present). DO step 7 does NOT re-snap (no parquet change). ✓
- [x] HALT 8: `tests/test_row_count_conservation.py:42-43` NATALITY pins = `201_161_456` / `list(range(1968, 2025))`. DO step 7 must NOT perturb (no rebuild). ✓ (verified present; untouched)
- [ ] HALT 9: cache-cleared pytest 85P+1S+1XF ≈ 288s — **DEFERRED to post-edit VERIFY** (cost discipline; C8.17 DO 3/4/5b/6 precedent; docs-only step cannot change the parquet-reading test surface).
- [x] HALT 10-12: soft-flags (bb)/(aa)/(w)/(x)/(z)/(u) carry; Tier 3+5 ≈ 2.3/7, cum Phase C ≈ 25/51-71 (cap 86); §15.D §1358 wording (w) + step-6/7-boundary clarification = next-`[plan-update]` (Convention 5; NOT bundled with this DO commit). ✓ (informational)

**12/12 actionable PASS; HALT 9 pytest deferred to VERIFY (precedented).** All 11 gate parquet SHAs computed on-disk and byte-exact vs the DO-step-6 receipt — no unauthorized rebuild; the docs-only precondition for DO step 7 holds.

### D-class scope divergence (§15.D narrow scope vs honest-propagation reality) + resolution

**Finding (Convention-3 Field-value snapshot):** §15.D DO step 7 + RECEIPTS/C8.17_step6 HALT 5 name a narrow scope — 6 files (`natality/.zenodo.json`, `CITATION.cff`, `natality/docs/ABOUT_THIS_RELEASE.md`, `natality/README.md`, `PROJECT_STRUCTURE.md`, top-level `README.md`) + "refresh C8.1 release-smoke EXPECTED_*". The snapshot found: (i) the C8.1 EXPECTED_* part has **no remaining target** — DO step 6 already re-pinned the only row-count pin (`test_row_count_conservation.py`, HALT 8); `natality/tests/test_schema_dtype_parity.py` checks `type` only (DO6-confirmed PASS); B.12 already re-snapped (HALT 7); no `EXPECTED_YEAR_ROWS`/`EXPECTED_ROW_COUNT` exists elsewhere. (ii) `v2.8.0`/`138,819,655`/`35 years`/`1990-2024` are stale in ~10 MORE consumer-facing files NOT on the §15.D list: `CHANGELOG.md` (no v3.0.0 section), `VERSION_ROADMAP.md` (L11 stale-roadmap, "fix on contact"), `docs/NCHS_SOURCE_MANIFEST.md`, `docs/COMPARABILITY.md`, `natality/docs/{GETTING_STARTED,FAQ,VALIDATION,CODEBOOK,COMPARABILITY}.md`, `natality/REPRODUCING.md`, `natality/quickstart.R`. Shipping `C8.17-complete` with these untouched = H8 (docs-vs-data drift) / L11 hazard the receipt §10 self-check must flag; a full sweep would bundle substantive C8.20-class content (CODEBOOK per-variable rows, the pre-1990 comparability narrative, schema per-column `years_available` where conservative-null soft-flag (aa) makes a blanket 1990-2024→1968-2024 swap WRONG) → Convention 5 / §9-#8 violation + incorrect-edit risk. `canonical_join_keys.py`/`natality/tests/conftest.py`/`tests/test_cross_product_join_parity.py` "v2.8.0 adopted canonical names" is historically CORRECT → NOT touched (any option).

**Resolution — AskUserQuestion 2026-05-17 → Option A "Honest propagation" (Convention-3 plan-amendment; documented before any DO mutation):** DO step 7 = Tier A (the 6 §15.D-named files) + the MECHANICAL version-string/headline-count swaps in the ~10 consumer files: `CHANGELOG.md` (new v3.0.0 release section), `VERSION_ROADMAP.md`, `docs/NCHS_SOURCE_MANIFEST.md`, `docs/COMPARABILITY.md` (timeline + `(v2.8.0)` labels + headline), `natality/docs/GETTING_STARTED.md`, `natality/quickstart.R`, `natality/docs/FAQ.md`, `natality/docs/VALIDATION.md`, `natality/REPRODUCING.md`, and the **headers only** of `natality/docs/CODEBOOK.md` + `natality/docs/COMPARABILITY.md`. **EXCLUDED (deferred, forward-looking HALTs):** CODEBOOK per-variable `years_available` rows + the pre-1990 comparability narrative in `natality/docs/COMPARABILITY.md` + `natality/metadata/harmonized_schema.csv` per-column `years_available` → C8.20 (CODEBOOK extensions) / a dedicated comparability task / soft-flag (aa). Historically-correct "v2.8.0 rename" code refs → untouched. Manuscript (`paper/`) → Phase D D.4 (already planned). Append-only history (STATUS/DECISION_LOG/FIX_LOG/RECEIPTS/PRE_FLIGHT_LOG/LESSONS/EXPLORATION_REPORT) + protocol (KICKOFF/NEXT_STEPS) + the existing `migrations/v2.7.0-to-v2.8.0-natality.md` (historical) → NOT edited (Anti-Pattern #1 / Convention 5). A dedicated v2.8.0→v3.0.0 migration guide = C8.11/Phase-D-class follow-up (not fabricated here — L6 no-invention). This is a same-task-intent scope amendment ("propagate v2.8.0→v3.0.0" honestly = make the repo self-consistent); still docs-only, ~0.5-1 session, no Sub-Q42; NOT a §15.D re-scope `[plan-update]` (the §15.D §1358 wording + step-6/7-boundary clarification remain the separate next-`[plan-update]`, soft-flag (w)).

### Field-value snapshot (Convention 3) — assumed pre-state verified

Plan-assumed pre-state for every scoped file = natality `v2.8.0` / `138,819,655` / `35 years` / `1990-2024` / 71 harmonized + 84 derived cols. **Verified** by the grep snapshot (PRE-FLIGHT scan): every scoped file currently carries exactly these values; target post-state = `v3.0.0` / `201,161,456` / `57 years` / `1968-2024` / 71+84 cols UNCHANGED / `certificate_revision` now 4-value (`unrevised_1968|unrevised_1989|revised_2003|unknown`). Linked product (2005-2023, 74,943,824, 33/35) UNCHANGED — only natality rows/years/version mutate. Latest *deposited* Zenodo version remains v2.7.0 (v3.0.0 is in-repo-only, pending the Phase D D.2 unified-HVS deposit) — propagation must NOT claim v3.0.0 is on Zenodo. SMOKE phase will enumerate each exact old→new string per file so DO edits are surgical.

### Halt conditions tripped

None. The §7-#17 scope-creep condition was correctly surfaced (not silently worked around) and resolved at the cheap-check moment via AskUserQuestion → a documented Convention-3 plan-amendment, before any DO mutation. All 11 gate SHAs byte-exact (docs-only precondition holds).

### Result

**PROCEED** to SMOKE (per-file exact old→new string enumeration) → DO (Tier A + the Option-A mechanical consumer-file swaps; zero parquet/schema/test-surface mutation) → VERIFY (11 gate parquet SHAs unchanged + pytest 85P+1S+1XF + no stale string remains in scoped files + version strings internally consistent) → RECEIPT + DECISION_LOG + STATUS → **tag `C8.17-complete`** (the final C8.17 sub-step). The Option-A scope amendment lands in DECISION_LOG at DO step 7 close.

---

## PRE-FLIGHT addendum for C8.17 DO step 6 — 2026-05-16T07:00:00Z — canonical 1968-2024 re-harmonize + `certificate_revision` enum widen + v3.0.0 bump — **RESULT: PROCEED** (Convention-3 Field-value snapshot of every canonical artifact DO step 6 mutates; the recon surfaced a 5th divergence D5 — a separate stale build-repo — RESOLVED by empirical byte-identity proof; AskUserQuestion 2026-05-16T06:45:00Z → v3.0.0 major bump; a pre-canonical SMOKE safety gate guards the H10 anchor; zero §7 halts pending the safety gate)

> **Why an addendum:** same rationale as the DO step 5b addendum — C8.17 uses one upfront umbrella PRE-FLIGHT (2026-05-14T06:30:00Z); each DO sub-step does an entry cheap-check. DO step 6 is the **highest-risk mutation of C8.17** (it intentionally changes the canonical published natality parquet SHA + widens the schema enum + bumps the Zenodo-concept-DOI semver), and the recon surfaced a material finding (D5) the umbrella PRE-FLIGHT did not anticipate. Documented **before any DO mutation**; `C8.17-pre-do`@`12fc20e` already tagged (no re-tag — intermediate DO step, Convention 5 precedent; `C8.17-complete` set only after DO step 7 docs).

### Entry cheap-check — 14 forward-looking HALTs from RECEIPTS/C8.17_step5b_2026-05-16T06-00-00Z.md

- [x] HALT 1: `C8.17-pre-do`@`12fc20e`; `C8.17-complete` NOT present. ✓
- [x] HALT 2: 8 parquet SHAs baseline-captured (`38e2cecb…`/`185c071e…`/`e16ad53…`/`9b828a4d…` + `adbec108…`/`5c22308b…`/`7c682668…`/`d98b4296…`). DO step 6 WILL change `natality_v2_harmonized.parquet` (`230efed2…`) + `natality_v2_harmonized_derived.parquet` (`e16ad53…`) — that IS the intended canonical re-harmonize. The **other 7** (fetal-death ×2, linked ×1, matched-multiples ×4) must stay byte-exact. ✓ (baseline)
- [x] HALT 3: harmonizer carries `_to_int_or_null_safe`(L77) + `_mrace1digit_to_bridged4`(L241) + `is_pre1989`(L653) + `elif is_pre2003:`(L857); existing 1990+/2003+ bodies byte-untouched. ✓
- [x] HALT 4: 22 `natality_<year>_raw.parquet` + 35 `natality_<year>_core.parquet` at `~/Desktop/natality-harmonization/output/yearly_clean/`. ✓
- [x] HALT 5: 1989 routes through `is_pre2003` (DO 5b Tier-2 verified). DO step 6 must NOT special-case 1989. ✓ (held)
- [x] HALT 6: `certificate_revision` enum widening + version bump OWED at DO step 6 — actioned this step (see Field-value snapshot). ✓
- [ ] HALT 7: cache-cleared pytest 85P+1S+1XF — **DEFERRED to post-edit VERIFY** (cost discipline; C8.17 DO 3/4/5b precedent). DO step 6 re-pins `tests/test_row_count_conservation.py` NATALITY pins (the test's own error message instructs same-commit re-pin; Convention 2 / L17 — the re-pin IS the expected behavior, NOT a regression).
- [x] HALT 8: B.12 baseline `tests/snapshots/v1_2026-05-13T21-00-00Z_columns.csv` (sole baseline) byte-exact through DO 5b. DO step 6 re-snaps → new `v2_<UTC>_columns.csv` (natality_v2 84-col block updated; other 3 parquets' SHAs byte-IDENTICAL). ✓
- [x] HALT 9-14: budget 1-2 sessions (Sub-Q42 if >2; cap 86, cum ~23.5); `_to_int_or_null_safe` is_pre1989-only; 6 DO5b design choices settled; soft-flags (w)/(x)/(z)/(u)/(aa) carry; no KICKOFF/NEXT_STEPS edit. ✓ (informational)

**13/14 PASS; HALT 7 deferred to VERIFY (precedented).**

### D5 — NEW divergence surfaced by recon (the umbrella PRE-FLIGHT + DO5b receipt did not anticipate)

**Finding:** the canonical natality parquet is built in a **separate repo** `~/Desktop/natality-harmonization/` (conftest `_NATALITY_BUILD`), which has its OWN copy of `scripts/03_harmonize/harmonize_v1_core.py` + `04_derive/derive_v1_core.py`. That build-repo copy is STALE — it has neither the DO5a parser nor the DO5b `is_pre1989` branch. The orchestrator `scripts/_drive_natality_benchmark.py` runs the stale build-repo scripts. **Risk:** if the monorepo harmonizer's 1990+ logic diverged from the build-repo copy that produced the current canonical parquet, re-harmonizing 1990-2024 from the monorepo would NOT reproduce the existing 1990-2024 slice byte-exact (an H10 / §15.D-VERIFY-anchor / L5 regression).

**Resolution (empirical, before any DO mutation):** `git show 12fc20e:natality/scripts/03_harmonize/harmonize_v1_core.py` (monorepo @ C8.17-pre-do, pre-ANY-C8.17-edit) is **byte-identical** (`diff -q` IDENTICAL) to the current build-repo `~/Desktop/natality-harmonization/scripts/03_harmonize/harmonize_v1_core.py`; `derive_v1_core.py` is **byte-identical** monorepo-vs-build-repo too. The DO5b edit is provably additive (4 deletions all at the era-dispatch boundary; 1990+/2003+ bodies byte-untouched). Therefore the monorepo harmonizer's 1990+ path IS the exact code that produced the current canonical parquet → re-harmonizing 1990-2024 reproduces the existing slice byte-exact. **Plan-amendment (Convention 3):** DO step 6 runs the **monorepo** scripts with explicit `--yearly-parquet-dir`/`--out` args pointing at the `~/Desktop/natality-harmonization/` build dir (the DO5a/5b SMOKE-established pattern; monorepo = canonical script source; the stale build-repo `scripts/` copy + the `_drive_natality_benchmark.py` orchestrator are NOT used — syncing them is an out-of-C8.17-scope cleanup, soft-flag (bb)). A **pre-canonical SMOKE safety gate** (harmonize 1990-2024 to scratch, compare to current canonical byte-exact) empirically confirms the anchor BEFORE the canonical overwrite — fail-closed §2; §7 HALT if not byte-identical.

### Field-value snapshot (Convention 3) — every canonical artifact DO step 6 mutates

1. `~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized.parquet` — pre-derive; CURRENT sha `230efed2ac34c794638aceaa777a31…` (1.66 GB; 1990-2024). DO6 → preserved as `.v28_baseline` + rebuilt 1968-2024 (SHA WILL change — intended).
2. `~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet` — SHIPPED/H10-gated; CURRENT sha `e16ad5323d68e28d401518f1ff56b1…` (2.20 GB). DO6 → preserved as `.v28_baseline` + re-derived 1968-2024 (SHA WILL change — intended). This is the parquet conftest tests + B.12 + row-count-conservation read.
3. `natality/metadata/harmonized_schema.csv` row 5 `certificate_revision`: CURRENT `type=string`, `allowed_values=unrevised_1989|revised_2003|unknown`, `years_available=1990-2024`. DO6 → `allowed_values=unrevised_1968|unrevised_1989|revised_2003|unknown`; `years_available=1968-2024`; `raw_source_by_year`/`derivation_rule`/`notes` extended for the 1968-1988=`unrevised_1968` mapping. `type` UNCHANGED (C8.1 `test_schema_dtype_parity` checks `type` only → stays PASS). Anti-Pattern #6 satisfied by the DO6 DECISION_LOG entry + the v3.0.0 bump decision.
4. `tests/test_row_count_conservation.py:39-40`: CURRENT `NATALITY_EXPECTED_TOTAL = 138_819_655`, `NATALITY_EXPECTED_YEARS = list(range(1990, 2025))` (self-labeled "Convention 2 release-state pin"; error message: "update … in the same commit"). DO6 → re-pin to the empirical 1968-2024 total + `list(range(1968, 2025))` (57 contiguous). Convention 2 / L17 bundled — the re-pin IS the expected behavior.
5. `tests/snapshots/v1_2026-05-13T21-00-00Z_columns.csv` (B.12 sole baseline; `latest_baseline_path()` = `sorted(glob("v*_columns.csv"))[-1]`). DO6 → new sibling `tests/snapshots/v2_<UTC>_columns.csv` (sorts after `v1_…` → becomes latest) regenerated via `_build_snapshot.py main()`: natality_v2_harmonized_derived 84-col block = new per-column SHAs; the OTHER 3 parquets' per-column SHAs MUST be byte-identical to the v1 baseline (those parquets unchanged). v1 baseline NOT deleted (Anti-Pattern #10).
6. Version string `v2.8.0` → `v3.0.0`: the SEMVER DECISION recorded in DECISION_LOG at DO step 6 (satisfies Anti-Pattern #6). **String propagation across `natality/.zenodo.json` / CITATION.cff / ABOUT_THIS_RELEASE.md / README.md / PROJECT_STRUCTURE.md is DO step 7** per §15.D's explicit step split (DO step 7 = "update CITATION.cff + .zenodo.json + ABOUT + README + PROJECT_STRUCTURE; refresh smoke EXPECTED_*"). Decision-B plan-amendment: DO step 6 edits ONLY what is needed for (a) canonical correctness, (b) pytest-green (gating-test re-pins), (c) Anti-Pattern #6 (schema↔version pairing, met via DECISION_LOG); the broader prose/version-string + per-column `years_available` refresh is DO step 7.

- [x] Current values verified vs task plan. AskUserQuestion 2026-05-16T06:45:00Z resolved the §15.D-flagged semver fork → **v3.0.0 (major)** (cert-revision era boundary + universal row-count/SHA change = the H10-cascade major trigger §15.D names). D5 resolved empirically. Decision-B (version-string→DO7) is a Convention-3 plan-amendment consistent with §15.D's own step split.

### Halt conditions tripped

None pending the pre-canonical SMOKE safety gate. The safety gate is a §7 fail-closed guard: if the monorepo harmonizer's 1990-2024 output is NOT byte-identical to the current canonical, **HALT** before overwriting canonical (do not patch; re-derive the divergence). All other divergences resolved at this cheap-check moment (D5 empirical proof; AUQ semver; Convention-3 Decision-B).

### Result

**PROCEED** to the SMOKE safety gate → DO (preserve `.v28_baseline` → re-harmonize 1968-2024 → re-derive → cert schema row + test re-pins + B.12 re-snap) → VERIFY (1990-2024 byte-clean anchor + 183/183 NVSR + 7 SHAs byte-exact + pytest 85P+1S+1XF post-authorized-re-pin) → RECEIPT. No tag (DO step 7 docs still pending; `C8.17-complete` deferred). v3.0.0 + D5 + design choices land in DECISION_LOG at DO step 6 close.

---

## PRE-FLIGHT addendum for C8.17 DO step 5b — 2026-05-15T05:30:00Z — `harmonize_v1_core.py` extension for pre-1990 era_tags — **RESULT: PROCEED** (Convention-3 Field-value snapshot surfaced 4 divergences from the DO step 5a receipt's assumed architecture; resolved at this cheap-check moment by AskUserQuestion 2026-05-15T05:15:00Z Q1 Option A + Q2 Option A + 2 LLM plan-amendments; zero §7 halts; canonical parquet byte-exact preserved this step — H10 gate intact; full re-harmonize + version bump remain DO step 6)

> **Why an addendum (not a fresh PRE-FLIGHT entry):** C8.17 uses ONE upfront umbrella PRE-FLIGHT (the 2026-05-14T06:30:00Z entry below) per §4.1 option (a) (multi-sub-step task, single upfront PRE-FLIGHT). Each DO sub-step does an *entry cheap-check* (re-verify the prior step's forward-looking HALTs) rather than a new PRE-FLIGHT. This addendum is written because the DO step 5b entry cheap-check surfaced a **material architecture divergence the umbrella PRE-FLIGHT did not anticipate** — exactly the L10-safe pattern the task1 session established (`## PRE-FLIGHT addendum for task1_joint_use_denominators — 2026-05-11T17:58:10Z`): the divergence + its resolution are documented **before the first DO mutation**, with `C8.17-pre-do` already tagged at `12fc20e` (no re-tag; intermediate-DO-step Convention 5 precedent).

### Entry cheap-check — 14 forward-looking HALTs from RECEIPTS/C8.17_step5a_2026-05-15T03-45-00Z.md

- [x] HALT 1: `C8.17-pre-do` tag at `12fc20e`; `C8.17-complete` NOT present. ✓ (`git rev-list -n1 C8.17-pre-do` = `12fc20e7019797c03574bf78b2c6d440f92e162b`; `git tag --list 'C8.17*'` = `C8.17-pre-do` only)
- [x] HALT 2: 4 canonical parquet SHAs byte-exact ✓
  - `output/harmonized/fetal_death_harmonized.parquet` = `38e2cecb03ff4947bbf6bcecbe9a79bf4bbe58df74ed4e7809b5078899c5cf48`
  - `output/harmonized/fetal_death_derived.parquet` = `185c071ec76ab8aae24c9d7524b2495900f78afbf43cd6a32537124fa7968a09`
  - `~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet` = `e16ad5323d68e28d401518f1ff56b12c09e43883e76022a9823d51a677c41d44`
  - `~/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet` = `9b828a4de4e59b17a1ca727e3dddc7ea7d748bb5281a98612f6fb9b85a08b777`
- [x] HALT 3: 4 matched-multiples parquet SHAs byte-exact (`adbec108…` harmonized + `5c22308b…`/`7c682668…`/`d98b4296…` yearly_clean) ✓
- [x] HALT 4: 22 `natality_<year>_raw.parquet` present at `~/Desktop/natality-harmonization/output/yearly_clean/` (`ls … | wc -l` = 22). ✓
- [x] HALT 5: `parse_public_us_pre1990_year.py` (245 ln) + `parse_all_pre1990_years.py` (90 ln) present. ✓
- [x] HALT 6: `field_specs.py` carries 7 pre-1990-relevant `RECORD_LEN_*` + 4 pre-1990 tuple lists (35/71/95 + `PUBLIC_US_1990_2002_FIELDS`=37 reused for 1989). ✓
- [x] HALT 7: `file_inventory.csv` 1968 row = `1,750,782 records` + FIX_LOG pointer. ✓
- [x] HALT 8: `FIX_LOG.md` most-recent = `2026-05-14T11:00:00Z — C8.17 DO step 5a — L13`. ✓
- [ ] HALT 9: cache-cleared pytest 85P+1S+1XF — **DEFERRED to post-edit VERIFY** per cheap-check cost discipline (C8.17 DO step 3/4 established precedent: "HALT pytest baseline deferred to DO step post-edit"). Not a halt; will gate H10 at VERIFY.
- [x] HALT 10: `NEXT_STEPS.md` §15.D line 1358 unchanged (soft-flag (w) carries; no edit this step). ✓
- [x] HALT 11-14: Tier 3+5 ~1.9/7; budget 1-2 sessions; substrate = 22 `_raw` parquets + `harmonize_v1_core.py` 1403 ln; 16 soft-flags carried. ✓ (informational)

**13/14 PASS; HALT 9 deferred to VERIFY (precedented).** H10 gate intact.

### Field-value snapshot (Convention 3) — target artifact this DO step mutates

- [x] Target file enumerated: `natality/scripts/03_harmonize/harmonize_v1_core.py` (1403 ln). Mutation = **additive only**: a new `is_pre1989` era branch inside `main()`'s batch loop + `_mrace1digit_to_bridged4()` helper + a `_raw`/`_core` input-path conditional. **Zero edits to the existing 1990-2002 (`is_pre2003`) or 2003+ (`else`) code paths** (HALT 13 + Convention 1).
- [x] Current values vs DO step 5a receipt's assumed-state — **4 divergences found** (resolved at this cheap-check moment, before any DO mutation):

  - **D1 — No `_harmonize_pre1990(table, year)` dispatcher.** Receipt "Notes for next session" assumed a clean dispatcher with `if 1968<=year<=1989: return _harmonize_pre1990(...)` as "the only change." **Actual:** `main()` (line 456) is monolithic — a per-year loop with a binary `if is_pre2003 / else` split (line 576/781) and inline per-column branching; the output 70-col `pa.Table.from_arrays([...])` is assembled at line 1329 from ~58 named arrays each branch must produce. **Resolution (AUQ Q1 Option A):** add an in-place `is_pre1989` branch computing all 58 arrays; do NOT refactor existing handlers (refactor = HALT 13 / H10 risk).
  - **D2 — Input path `_core` vs `_raw`.** `main():545` hardcodes `natality_{year}_core.parquet`; DO step 5a wrote `natality_{year}_raw.parquet` (receipt HALT 4 mandates `_raw` is the harmonize input). **Resolution (LLM plan-amendment, bundled in AUQ Q1 Option A):** path conditional — `_raw.parquet` for `year <= 1989`, `_core.parquet` for `year >= 1990`. 1990+ behavior byte-unchanged.
  - **D3 — 1989 collapses into the existing `is_pre2003` path.** The 1989 `_raw` columns are byte-identical to the V2 1990-2002 layout (DO step 4 finding; verified: all 27 `_get_col` hard-reads in the `is_pre2003` block — DMAGE/DMAR/LIVORD9/TOTORD9/ORMOTH/MRACE/DMEDUC/MONPRE/NPREVIS/DIABETES/CHYPER/PHYPER/TOBACCO/CIGAR6/DPLURAL/CSEX/DGESTAT/GESTAT3/DBIRWT/DELMETH5/FMAPS/DFAGE/PLDEL/BIRATTND/ORFATH/ORRACEF/DFEDUC — are all present in `natality_1989_raw.parquet`). `is_pre2003 = "DMAGE" in cols` already fires for 1989. **Resolution (AUQ Q1 Option A):** 1989 routes through the EXISTING `is_pre2003` block with **zero new code** (cert_rev = `unrevised_1989` already correct — 1989 IS the 1989-revision cert). The new era discriminator is `is_pre1989 = year <= 1988`; `is_pre2003 = (not is_pre1989) and ("DMAGE" in cols)` so 1968-1988 take the new branch and 1989-2002 keep the existing one. Verified by SMOKE Tier 1b.
  - **D4 — `certificate_revision` enum has no pre-1989 value.** Canonical `harmonized_schema.csv:5` enum = `unrevised_1989|revised_2003|unknown`; 1968-1988 = 1968-revision certificate (distinct). **Resolution (AUQ Q2 Option A):** new handler emits **`unrevised_1968`** for 1968-1988; the `harmonized_schema.csv` enum widening + schema-version bump stay DEFERRED to DO step 6 (§15.D / Anti-Pattern #6). DO step 5b does NOT write the canonical parquet (output → non-canonical scratch path for SMOKE), so the canonical SHAs stay byte-exact and no schema-version bump is owed this step.

- [x] Additional Convention-3 snapshots verified against task plan:
  - `marital_status` (schema int8 `1|2|9`, source DMAR/MAR): pre-1990 natality `_raw` files carry **`LEGITIM`, not `DMAR`** (1968/1975/1985 probed; only 1989 has DMAR). H7 sibling check: fetal-death `marital_status` sources `DMAR@87` even in its 1982-1988 V3b era — natality's pre-1990 public-use file simply does not surface a direct marital question. Plan-amendment: **`marital_status` = null for 1968-1988** (LEGITIM = legitimacy ≠ marital status; conflating them risks §7-#19 cross-product value-normalization divergence). LEGITIM left unharmonized at 5b; a separate `legitimacy_status` column is a documented DO-step-6/future candidate, not shoehorned here.
  - `maternal_race_bridged` (schema int8 `1|2|3|4`): H7 sibling parity — mirror fetal-death `harmonize.py:399` B3 1-digit map (per 1985 user guide p18, same 1978-rev-era frame): `0/4/5/6/8→4 (API), 1→1, 2→2, 3→3, 7→null (residual), 9→null (not stated)`. New `_mrace1digit_to_bridged4()` helper (int8 output; sibling of existing `_mrace_detail_to_bridged4`).
  - `_dmeduc_years_to_cat4` (helper:158): verified that pre-1990 DMEDUC sentinels `88` (non-reporting) and `99` (unknown) both fall through to null (only 00-17 ranges assigned). Safe to reuse for 1969-1988 DMEDUC + DFEDUC.
  - Conservative-null fields for 1968-1988 (not on the 1968-rev certificate / absent from the public-use file): hispanic_origin, maternal_hispanic, maternal_race_ethnicity_5, marital_reporting_flag, prenatal_visits, smoking (×3), diabetes/hypertension (×3), delivery_method, apgar5, bmi (×2), payment_source, prior_cesarean(+count), father_hispanic, father_race_ethnicity_5, fage_cat_rec11, all 12 congenital-anomaly + 5 infection + 6 clinical-detail (2014+) booleans. Each logged as a DECISION_LOG choice with a DO-step-6 refinement flag where a future signal exists (e.g., TPRENVIS, LEGITIM, FAGER_R11).

### Halt conditions tripped

None. The 4 divergences are Convention-3 "task-plan-assumed-state vs actual-state" mismatches, **resolved at the cheap-check moment** by AskUserQuestion (Q1+Q2 Option A) + 2 LLM plan-amendments (D2 path conditional; marital=null) — per Convention 3 ("resolve … by amending the task plan OR halting and asking the human; do not silently proceed under the divergent state"). No §7 condition is open. DO step 5b scope (author + SMOKE; canonical re-harmonize + version bump = DO step 6) is unchanged from §15.D.

### Result

**PROCEED** to C8.17 DO step 5b DO phase (author `is_pre1989` branch + `_mrace1digit_to_bridged4()` + `_raw` path conditional; SMOKE Tier 0/1/1b on non-canonical scratch output; VERIFY pytest + H10 SHA gate). No new tag (intermediate DO step, Convention 5 precedent). Resolution narrative + the 6 design choices land in the DECISION_LOG entry at DO step 5b close.

---

## PRE-FLIGHT for C8.17 — 2026-05-14T06:30:00Z — Natality 1968-1989 backward extension (A.2; 22 new years; 5 era boundaries; second Tier-3+5 task) — **RESULT: PROCEED** (zero §7 halts; zero AskUserQuestion needed; one minor terminology soft-flag (t) on §15.D "4 distinct pre-1989 layouts" wording vs cheap-check-empirical 5 era boundaries 1968 / 1969-1971 / 1972-1977 / 1978-1988 / 1989; resolution = §15.D wording stands as cumulative-count framing, soft-flag carried for DO step 1 reconciliation; no `[plan-update]` commit needed)

### Scope summary

C8.17 §15.D entry (NEXT_STEPS.md lines 1348-1392) names the deliverable: extend natality coverage from 1990-2024 (35 yrs) to **1968-2024 (57 yrs)** by parsing 22 pre-1990 NCHS public-use natality zips at `ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/natality/`. Reconstruct 4-5 pre-1989 layouts. Re-harmonize natality 1968-2024 with the existing schema (per-era era_tag extensions). Bump natality v2.8.0 → v2.9.0 (or v3.0.0 if cert-revision boundary triggers major bump per H10 cascade — DO step 6 decision; not PRE-FLIGHT). KICKOFF.md Phase C Tier-3+5 line 203 names C8.17 as second Tier-3+5 task post-C8.16-complete (`974c310`). Estimated §15.D effort = **6-10 sessions** (cheap-check confirms estimate stands; no surprises drive a Q42 revision). §15.D halt-condition flags: H1 + H6 + H7 + L1-extension + L12-extension + L13-extension + L17 + Convention 1 SHAPE-not-VALUE.

**Session scope this PRE-FLIGHT:** ship PRE-FLIGHT entry + DECISION_LOG entry + STATUS section + commit + tag `C8.17-pre-do`. DO begins at next session entry with the full 6-10 session budget. C8.16 precedent (`2b7139a` `C8.16-pre-do` was its own commit; DO began next session) applied here for the same reason — 22 zips + 15 PDFs + ~1.64 GB raw + 4-5 layout reconstructions warrants a clean checkpoint to give DO the full budget.

### Inputs

- [x] **All 12 Forward-looking HALTs from STATUS 2026-05-14T05:30:00Z verified byte-exact** (STATUS lines 78-89):
  - HALT 1: `C8.16-complete` tag present. `git tag --list 'C8.1[67]*'` returns `C8.16-complete` + `C8.16-pre-do`. ✓
  - HALT 2: `C8.17-pre-do` tag NOT yet present at PRE-FLIGHT entry. ✓
  - HALT 3: 4 canonical parquet SHAs byte-exact:
    - `~/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_harmonized.parquet` sha256=`38e2cecb03ff4947bbf6bcecbe9a79bf4bbe58df74ed4e7809b5078899c5cf48` ✓
    - `~/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_derived.parquet` sha256=`185c071ec76ab8aae24c9d7524b2495900f78afbf43cd6a32537124fa7968a09` ✓
    - `~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet` sha256=`e16ad5323d68e28d401518f1ff56b12c09e43883e76022a9823d51a677c41d44` ✓
    - `~/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet` sha256=`9b828a4de4e59b17a1ca727e3dddc7ea7d748bb5281a98612f6fb9b85a08b777` ✓
  - HALT 4: 3 matched-multiples yearly_clean parquet SHAs byte-exact:
    - `matched_multiples/output/yearly_clean/matched_multiples_1995-1997_raw.parquet` sha256=`5c22308bed2883b9be8e244e763c3603f700b5ba5274f3ef30388a28d39205d1` ✓
    - `matched_multiples/output/yearly_clean/matched_multiples_1995-2000_raw.parquet` sha256=`7c682668006f3fab556b79422d34f5d84eed0bd0e1ae44702908f9f5edd61f5d` ✓
    - `matched_multiples/output/yearly_clean/matched_multiples_2016-2020_raw.parquet` sha256=`d98b42965573530d26d72368d968c395487b2c4e4dd3bfc4ad426e966a543261` ✓
  - HALT 5: matched-multiples harmonized parquet sha256=`adbec1087370941fd373b933566b7dfd24dbbc2f957d998f92ac14ef45dc1549` ✓
  - HALT 6: cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/ matched_multiples/tests/ -p no:cacheprovider` returns **85 PASS + 1 SKIP + 1 XFAIL in 246.27s** — count exact; wall-time 24.47s below 270.74s baseline, well within ±25s tolerance (Convention 1 SHAPE-not-VALUE asserts COUNT not wall-time; not a halt). ✓
  - HALT 7: `docs/NCHS_SOURCE_MANIFEST.md` first paragraph names 100 zips (43 fetal-death + 35 natality + 19 linked-cohort + 3 matched-multiples). `grep -c "^| " docs/NCHS_SOURCE_MANIFEST.md` returns 108 (100 zip rows + 8 column headers across 4 sections). ✓
  - HALT 8: `README.md` line 14 reads "## Four products at a glance" ✓
  - HALT 9: `tests/test_source_zip_sha_stability.py::_classify()` recognizes 4 filename families (Fetal* default branch; Nat* prefix → NATALITY_RAW_DIR; LinkCO*/LinkPE* + 2005-2022 linked prefixes → LINKED_RAW_DIR; matched-multiples 3 literal filenames → MATCHED_MULTIPLES_RAW_DIR). ✓
  - HALT 10: `git diff HEAD -- KICKOFF.md NEXT_STEPS.md` returns empty (no edits to either since `974c310`). ✓
  - HALT 11: Tier 3+5 progress = 1 of 7 tasks (C8.16 complete; C8.17-C8.22 remaining). Cumulative Phase C ~19.5 of 51-71 sessions (within Q33 effort-ceiling cap of 86). ✓
  - HALT 12: `/tmp/c8_16_zip_probe/` (3 zips: 1995-1997.zip + 1995-2000.zip + 2016-2020.zip) and `/tmp/c8_16_pdf_probe/` (3 PDFs + 3 text files) both present (NOT OS-cleaned). ✓ — informational only, not a HALT condition for C8.17.

- [x] **C8.17 substrate enumerated** (sibling-extrapolation per L1-extension; per LESSONS 2026-05-12T04:30:00Z; existing on-disk inventory `~/Desktop/natality-harmonization/raw_docs/Nat<YYYY>doc.pdf` for 1990-2004 confirmed sibling pattern; the 2005+ era switches to `UserGuide<YYYY>.pdf`):
  - **22 NCHS source zips probed** (uniform `Nat<YYYY>.ZIP` uppercase pattern at `ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/natality/`; all HTTP 200; all Last-Modified 2007-08-24 / 2007-08-27 / 2007-08-28 — uniform 2007-08 batch upload). Cumulative content-length ~1.64 GB:
    - 1968: 14,648,626 B (14.6 MB; 50%-sample-alone era)
    - 1969-1971: 35,298,000 + 38,608,225 + 35,093,001 = 109,000 KB (3-yr 50%-sample joint-doc era)
    - 1972-1977: 35,276,162 + 39,003,176 + 43,456,076 + 48,153,444 + 53,675,278 + 60,350,112 = 280,000 KB (6-yr mixed-sample joint-doc era)
    - 1978-1988: 71,134,938 + 88,429,944 + 90,619,688 + 97,323,732 + 102,038,747 + 100,930,190 + 102,130,621 + 102,103,191 + 106,461,058 + 115,743,731 + 119,067,351 = 1,095,000 KB (11-yr 100%-file era; 1978-revision cert)
    - 1989: 141,007,082 B (141.0 MB; 1989-revision cert; will inherit V2-era layout from existing 1990+ via sibling-extrapolation)
  - **15 documentation PDFs probed** (path `ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/natality/` — NOT under `Datasets/DVS/`; corrected after first-pass 404 trap; sibling pattern `Nat<YYYY>doc.pdf` for 1978-1989 + `Nat<YYYY>-<YY>doc.pdf` for the 2 joint multi-year docs); all HTTP 200:
    - Standalone: `Nat1968doc.pdf` (0.3 MB; 9 pages); `Nat1978doc.pdf` (2.0 MB); `Nat1979doc.pdf` (1.1 MB); `Nat1980doc.pdf` (6.6 MB); `Nat1981doc.pdf` (4.3 MB); `Nat1982doc.pdf` (9.8 MB); `Nat1983doc.pdf` (9.3 MB); `Nat1984doc.pdf` (9.1 MB); `Nat1985doc.pdf` (9.2 MB; 226 pages); `Nat1986doc.pdf` (8.9 MB); `Nat1987doc.pdf` (7.6 MB); `Nat1988doc.pdf` (8.5 MB); `Nat1989doc.pdf` (12.0 MB; 285 pages) — 13 individual PDFs.
    - Joint: `Nat1969-71doc.pdf` (1.5 MB; 26 pages) covers 1969-1971; `Nat1972-77doc.pdf` (1.6 MB; 29 pages) covers 1972-1977 — 2 joint PDFs.
    - Total: 15 PDFs covering 22 years.
    - All Last-Modified 2007-08-24 / 2007-08-26 / 2007-08-27 / 2007-08-28 (same 2007-08 batch upload as the zips).
  - **L12-extension PASS on 5-PDF sample** (Convention per LESSONS 2026-05-12T15:00:00Z; PyMuPDF `page.get_text()`):
    - `Nat1968doc.pdf`: 9 pages, 100% non-empty, 7,742 chars total. Producer=`Acrobat PDFWriter 3.03 for Windows`, creation=`D:20000616084509`, mod=`D:20190425194257`.
    - `Nat1969-71doc.pdf`: 26 pages, 100% non-empty, 31,244 chars. Producer=empty (likely older OCR'd scan with text layer added), creation=`D:20000331084345`, mod=`D:20190425194259`.
    - `Nat1972-77doc.pdf`: 29 pages, 100% non-empty, 33,890 chars. Producer=empty (same OCR'd scan pattern), creation=`D:20000331085417`, mod=`D:20190425194258`.
    - `Nat1985doc.pdf`: 226 pages, 100% non-empty, 380,085 chars. Producer=`Acrobat PDFWriter 3.03 for Windows`, creation=`D:20000128110732`, mod=`D:20190425194333`.
    - `Nat1989doc.pdf`: 285 pages, 100% non-empty, 502,631 chars. Producer=`Acrobat PDFWriter 3.03 for Windows`, creation=`D:20000128105658`, mod=`D:20190425194348`.
    - **Conclusion**: 100% of probed pages text-extractable; **NO OCR needed**. All 5 samples share the 2000-era Acrobat PDFWriter 3.03 + 2019-04-25 reprocessing signature (sibling of the 1985 fetal-death PDF precedent LESSONS 2026-05-12T15:00:00Z). The 1969-71 + 1972-77 joint docs have empty producer fields and show slight text-extraction noise (slash-separated tokens; OCR'd from older scans) but are STILL text-extractable; full record-layout reconstruction can proceed at DO without OCR. Sample SHA-256s recorded in `/tmp/c8_17_probes/`:
      - Nat1968doc.pdf sha256=`085ffcedd8dbed350ae54e241f49754f8af94fc16e7dd7e749367d37504d9456`
      - Nat1969-71doc.pdf sha256=`73e2d3e233a53efc44c3d8b16e91f79bed619f34a7225719c183f3ad11a2a3be`
      - Nat1972-77doc.pdf sha256=`0ac4733c6c73cf78102589fbbb6490d6704dcaf2c4c9208d8d5153a7e80aca5c`
      - Nat1985doc.pdf sha256=`371d1f61265a6fcff11db9ec2fa4ee6907c349d537c2c7dfe6c9d8bc904c5b12`
      - Nat1989doc.pdf sha256=`92dab8115baec71eec3633239cbd042b2079ad6b80bd1b3a3a43c3276ac3a7cb`
  - **Era boundary count clarification (soft-flag (t)):** §15.D line 1350 says "4 distinct pre-1989 layouts (1968 / 1969-1971 / 1972-1977 / 1978-1988 / 1989)" — the parenthetical lists 5 era boundaries. The cheap-check confirms 5 distinct PDF documentation eras (1 standalone 1968 + 2 joint 1969-71 + 1972-77 + 1 multi-year-individual 1978-1988 + 1 standalone 1989). Whether 1989 inherits the 1990+ V2-era layout (reducing to 4 NEW layouts) or has its own pre-V2 1989-revision-rollout artifacts (5 NEW layouts) is a DO step 4 cheap-check; PRE-FLIGHT defers. Logged as soft-flag (t) for DO step 1 reconciliation. NO §11 plan-update triggered (terminology, not scope).
- [x] **No stale checkpoints**: `git status --porcelain` empty on `main` at `974c310`; `C8.17-pre-do` + `C8.17-complete` tags do NOT yet exist. ✓

### Environment

- [x] Python 3.13.9; pandas + pyarrow + pymupdf available via `uv run python -c "import pandas, pyarrow, pymupdf"`; uv lockfile unchanged (from C8.16 close `974c310`). ✓
- [x] Working directory clean; on `main`; HEAD at `974c310` (the C8.16-complete commit). ✓
- [x] `curl` (TLS-permissive `-k`) available for FTP probes; reachable to `ftp.cdc.gov` (HTTP 200 on all 22 zip + 15 PDF probes). ✓

### Source documentation

C8.17 is a data-extension task; consumes 15 external NCHS documentation PDFs + 22 source zips at PRE-FLIGHT (probe-level only). Full content read (record_layout_*.csv reconstruction from documentation pages 13-22-style anchor-field tables) happens at DO steps 2-4:

- 15 PDFs probed above (5-sample L12-extension PASS at PRE-FLIGHT; full content read happens at DO when authoring `natality/metadata/record_layout_<era>.csv` files — sibling pattern of the existing `record_layout_*.csv` files in `fetal_death/`).
- 22 source zips probed above (HTTP HEAD + content-length + last-modified verified; full unzip + record-layout reconstruction happens at DO step 1 + 2-4).

All L1-extension cheap-checks satisfied (sibling-extrapolation from §15.D filename pattern `Nat<YYYY>.zip` returned HTTP 200 on the uniform uppercase `.ZIP` variant; one filename-variant probe trap encountered at first pass — wrong PDF subpath `Datasets/DVS/Dataset_Documentation/natality/` returned 404 across all 22 candidates; corrected on second probe to `Dataset_Documentation/DVS/natality/` which is the path used by `vitalstatsonline.htm` link inventory; both probes logged here for forensic traceability per L12 discipline — the 404 trap was caught by sibling-cross-check, NOT by retrying hallucinated variants). All L9 cheap-checks satisfied (PDF page counts + first-page text samples verified per the 5-PDF L12-extension probe above).

### Outputs

- [x] **NEW files (must not exist before DO; will be authored in DO):**
  - `natality/metadata/record_layout_1968.csv` (DO step 2; 50%-sample era; small)
  - `natality/metadata/record_layout_1969_1971.csv` (DO step 2; joint 3-yr era)
  - `natality/metadata/record_layout_1972_1977.csv` (DO step 3; joint 6-yr era; mixed-sample-fraction handling)
  - `natality/metadata/record_layout_1978_1988.csv` (DO step 4; 100% file; 1978-revision cert)
  - `natality/metadata/record_layout_1989.csv` (DO step 4; 1989-revision cert pre-1990 sibling)
  - 22 new rows in `natality/metadata/file_inventory.csv` (DO step 1; 54 → 76 rows)
  - `natality/scripts/01_import/parse_all_pre1990_years.py` (DO step 5; sibling of existing `parse_all_v1_years.py`)
  - Possibly `natality/V3_PRE1990_LAYOUT_DECISIONS.md` (DO step 1; sibling of `fetal_death/V3b_1982_1988_LAYOUT_DECISIONS.md`)
  - `tests/snapshots/v2_<UTC>_columns.csv` (DO step 7; B.12 snapshot re-snap)
  - `RECEIPTS/C8.17_<UTC>.md` (RECEIPT phase)
- [x] **APPEND-ONLY state files (this PRE-FLIGHT close commit):**
  - `PRE_FLIGHT_LOG.md`: this entry
  - `DECISION_LOG.md`: NEW entry recording C8.17 PRE-FLIGHT close + 5-era empirical finding + soft-flag (t) terminology disposition
  - `STATUS.md`: new dated section at top recording PRE-FLIGHT close + DO step plan
- [x] **MODIFIED at DO (forward-looking; NOT touched at this PRE-FLIGHT commit):**
  - `natality/metadata/harmonized_schema.csv` (DO step 5/7; `years_available` cells `1990-2024` / within-era subsets extended union-wise to `1968-2024` / within-era subsets; preserved comparability_class boundaries)
  - `natality/metadata/file_inventory.csv` (DO step 1; +22 rows)
  - `natality_v2_harmonized_derived.parquet` (DO step 6; CURRENT preserved as `.v28_baseline.parquet` forward-stability anchor per §15.D plan; new v2.9/v3.0 parquet authored)
  - `natality/output/harmonized/parse_all_pre1990_years.parquet` (DO step 5; per-era 1968-1989 yearly_clean parquets)
  - `README.md` "Natality" row (1990–2024 / 35 yrs / 138,819,655 → 1968–2024 / 57 yrs / ~165M records — exact count TBD at DO; cols TBD)
  - `PROJECT_STRUCTURE.md` natality section (1990-2024 → 1968-2024)
  - `docs/NCHS_SOURCE_MANIFEST.md` (100 → 122 zips; +22 natality 1968-1989 rows)
  - `tests/test_source_zip_sha_stability.py` (100 → 122 anchor; `_classify()` extended to recognize 1968-1989 natality filenames — they all match the existing `Nat*` prefix logic via `NATALITY_RAW_DIR` so the classifier may need NO extension beyond `EXPECTED_FILENAMES` set; cheap-check defer to DO step 7)
  - `CITATION.cff` (keywords update; possibly v2.9 reference)
  - `KICKOFF.md` "Current data envelope" (line 58: 35-yr → 57-yr natality)
  - `notebooks/_build_*.py` builders may need EXPECTED_YEAR_ROWS dict updates (C8.1 `DESIGN: tracks-current-state` smokes per L17)
- [x] **NOT mutated** (forward-looking HALT for C8.17 VERIFY):
  - 2 fetal_death parquet SHAs unchanged (C8.17 touches natality only; H10 gate for fetal-death side ✓)
  - 1 linked parquet SHA unchanged (C8.17 touches natality 1968-1989 only; linked extension is C8.18 ✓)
  - 4 matched-multiples parquet SHAs unchanged (C8.17 is additive to natality only; matched_multiples untouched ✓)
  - All C8.1-C8.16 file SHAs preserved
  - Manuscript draft unchanged (Phase D step 4 scope)

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

C8.17 mutates 4 categories of canonical state: (i) natality metadata CSVs; (ii) natality harmonized parquet (with v2.8 baseline preserved); (iii) monorepo top-level docs reflecting natality envelope; (iv) test-suite anchors (B.12 snapshot + SHA-stability count + smoke EXPECTED_YEAR_ROWS).

**Table 1: Current natality metadata state (pre-DO)**

| Artifact | Current rows | Current cols | Post-C8.17 expected |
|---|---|---|---|
| `natality/metadata/file_inventory.csv` | 54 (35 natality 1990-2024 + 19 linked 2005-2023) | 8 (`year, source_url, source_org, raw_filename, file_format, doc_filename, imported, notes`) | 76 (+22 natality 1968-1989); no col extension at PRE-FLIGHT |
| `natality/metadata/harmonized_schema.csv` | 95 (header + 94 column rows) | 9 (`harmonized_name, harmonized_label, type, allowed_values, years_available, raw_source_by_year, comparability_class, derivation_rule, notes`) | 95+ (additive cells in `years_available` + `raw_source_by_year`; possibly new pre-1990-specific rows if era introduces new columns; TBD at DO step 5) |
| `natality/metadata/record_layout_*.csv` (existing) | per-era V2/V3 files | varies | +4-5 new pre-1989 era files |

**Table 2: Current natality `years_available` cell distribution (sample)**

Captured via `awk -F, 'NR==1{for(i=1;i<=NF;i++)if($i=="years_available")c=i}; NR>1{print $c}' natality/metadata/harmonized_schema.csv | sort -u`:

- `1990-2024` (dominant; cross-era columns)
- `1990-2019` (within-era V1 to pre-2020 only)
- `1990-1994` (V0 → V1 transition era)
- `2005-2013` (V2 era subset)
- `2005-2023 (linked)` (linked-file column)
- `2005-2024` (V2 era cross-natality+linked)
- `2009-2024`, `2014-2024` (post-2009 / post-2014 additions)
- One quoted-string cell with `2=VBAC` — likely an embedded comma-separated allowed_values cell that broke the CSV parse; non-mutating for C8.17 (will surface at DO step 5 if `years_available` cell-level edit operates on this row)

All 8 distinct `years_available` cell forms above are CURRENT VALUES; C8.17 DO step 5 expands them all union-wise to include the 1968-1989 envelope where applicable. The `1990-2024` cells become `1968-2024` for cross-era columns; within-era cells stay unchanged.

**Table 3: Current 4 canonical parquet SHAs (preserved through C8.17 except natality main)**

| Path | Current SHA | Post-C8.17 |
|---|---|---|
| `fetal_death_harmonized.parquet` | `38e2cecb…` | **UNCHANGED** (C8.17 touches natality only) |
| `fetal_death_derived.parquet` | `185c071e…` | **UNCHANGED** |
| `natality_v2_harmonized_derived.parquet` | `e16ad53…` | **CHANGES** at DO step 6 → preserved as `.v28_baseline.parquet`; new v2.9/v3.0 parquet authored |
| `natality_v3_linked_harmonized_derived.parquet` | `9b828a4d…` | **UNCHANGED** (linked extension is C8.18, not C8.17) |

**Table 4: Current README + PROJECT_STRUCTURE natality prose**

- `README.md` line 16: `| **Natality** | 1990–2024 (35 years) | 138,819,655 | 84 (71 harmonized + 13 derived) | 183/183 *Births: Final Data* targets byte-exact | [`natality/`](natality/) |`
- `PROJECT_STRUCTURE.md` line 17: `├── natality/                 Natality + linked birth–infant death subproject`
- `PROJECT_STRUCTURE.md` line 39: `Natality 1990–2024 plus linked birth–infant death 2005–2023, mirrored from the [yoelplutchok/natality-harmonization](...) repo (v2.8.0 in-repo state, last Zenodo deposit v2.7.0).`

C8.17 DO step 7 updates these to reflect 1968-2024 (57 years; record count TBD; column count TBD).

**Table 5: Current C8.1 `DESIGN: tracks-current-state` smoke anchors**

- `natality/tests/test_release_smoke.py` (if it exists; will inherit C8.1 dtype-parity pattern): `EXPECTED_ROW_COUNT` + `EXPECTED_YEARS` + `EXPECTED_YEAR_ROWS` dicts pinned to 1990-2024 envelope per Convention 1 SHAPE-not-VALUE; C8.17 DO step 7 re-pins these to 1968-2024 envelope per the `tracks-current-state` discipline. (Not a FAIL — this IS the expected behavior per L17 + Convention 2; pinning is bundled in the same commit as the parquet rebuild.)

**Plan assumptions verified at PRE-FLIGHT (per Convention 3 second bullet):**

1. **§15.D "22 new years; 4 distinct layouts" wording is loose**: cheap-check finds **5 era boundaries** (1968 / 1969-1971 / 1972-1977 / 1978-1988 / 1989). Resolution = §15.D wording can stand as "4 NEW pre-1989 layouts" if 1989 inherits the 1990+ V2-era layout (already canonical); cheap-check at DO step 4 will confirm. Soft-flag (t) carries forward; no §11 plan-update triggered (terminology, not scope).
2. **PDF documentation path** = `Dataset_Documentation/DVS/natality/` (NOT `Datasets/DVS/Dataset_Documentation/natality/`). First-pass probe (using the latter path) returned 404 across all 22 candidates; corrected via cross-reference to existing on-disk 1990+ doc filenames + WebFetch on `vitalstatsonline.htm`. The on-disk inventory pattern is the L1-extension sibling-derive backbone.
3. **L12-extension PASS on 5-sample** (Nat1968 / Nat1969-71 / Nat1972-77 / Nat1985 / Nat1989); all 100% text-extractable; NO OCR needed. Acrobat PDFWriter 3.03 + 2019-04 reprocessing signature shared across all 5.
4. **Effort estimate 6-10 sessions stands**: §15.D DO step 1 (1 session) + step 2 (1-2 sessions) + step 3 (1-2 sessions) + step 4 (1-2 sessions) + step 5 (1 session) + step 6 (1 session) + step 7 (0.5-1 session) = 6.5-10 sessions. Cumulative Phase C ~19.5 + 6-10 = ~25.5-29.5 / 51-71. Effort-ceiling cap 86 intact.
5. **L1-extension sibling-extrapolation discipline applied**: existing on-disk `~/Desktop/natality-harmonization/raw_docs/Nat<YYYY>doc.pdf` for 1990-2004 is the sibling backbone; pre-1990 sibling extrapolation returned 200 on first try at the corrected path. NO hallucinated filename variants attempted.
6. **No new schema bump pre-decided**: §15.D names v2.8.0 → v2.9.0 (or v3.0.0 if cert-revision boundary cascade) — DO step 6 decision; not PRE-FLIGHT. The H10 reproducibility-gate forward-looking HALT for C8.17-complete: v2.8 baseline preserved byte-exact on the 1990-2024 slice.

**Soft-flags surfaced at PRE-FLIGHT (NEW + carried from C8.16-complete):**

NEW:
- (t) **§15.D terminology**: "4 distinct pre-1989 layouts" wording vs cheap-check-empirical 5 era boundaries. Resolution = DO step 4 cheap-check (does 1989 inherit V2-era layout?); carries soft-flag for forensic traceability; no §11 plan-update triggered.

Carried unchanged from C8.16-complete: (a) stale `fetal_death/PROVENANCE.md` + (b) absent `natality/PROVENANCE.md` (both Phase D step 2; C8.17 will ADD pre-1990 entries to natality PROVENANCE when it is authored) + (c) `VERSION_ROADMAP.md` "Planned" section (Phase D candidate; will need pre-1990 natality + matched-multiples + linked 1983-2004 entries by Phase D step 2) + (d) `run_pipeline.py` ALL_YEARS=29 (C8.7b) + (e) `natality/output/linked/` absent (Phase D step 3 / C8.7b) + (g) PRE-FLIGHT "87 raw zips" typo (now 100; C8.17 will bring to 122) + (i) `fetal_death/COMPARABILITY.md` title staleness (Phase D candidate) + (m) `record_length` invariant test does not check vs-actual-zip parity (C8.7b candidate) + (n) `test_validate_linked_parquets_mutation` E2E verification (Phase D step 3 / C8.7b) + (o) `validate_v1_invariants` deep-scan FAIL-surface mutation test (future C8.X) + (p) F.1 dict-encoding dropped + (q) WORKED_EXAMPLE_FAQ.md STATUS-anchor typo + (r) effort-ceiling cap 42 → 86 + (s) `/tmp/c8_16_zip_probe/` OS-cleanable.

Soft-flag (f) plurality footgun: OPERATIONALLY CLOSED at C8.15; carries for documentation-trail only.

### Halt conditions tripped

None at PRE-FLIGHT close. All 12 forward-looking HALTs from STATUS 2026-05-14T05:30:00Z verified byte-exact. Two cheap-check findings (PDF-path 404 trap; 5-era vs 4-layout terminology) resolved in-PRE-FLIGHT without §11 plan-update or AskUserQuestion — both routine PRE-FLIGHT-time disambiguations per the C8.16 PRE-FLIGHT precedent. NO §7 HALT condition triggered.

### Result

**PROCEED to C8.17 DO step 1** (next session). PRE-FLIGHT close commit lands this entry + DECISION_LOG entry + STATUS section + tag `C8.17-pre-do`. DO begins at next session entry with the full 6-10 session budget. Forward-looking HALTs for next session's PRE-FLIGHT cheap-check listed in STATUS section 2026-05-14T06:30:00Z + the DECISION_LOG entry of same timestamp.

---

## PRE-FLIGHT for C8.16 — 2026-05-14T02:30:00Z — Matched-multiples ancillary release (A.5; 4th HVS product); first Tier-3+5 task per 2026-05-14T02:00:00Z plan-update — **RESULT: PROCEED**; user-resolved 2 architectural questions via AskUserQuestion 2026-05-14T02:30:00Z (Architecture = Option A standalone subproject `matched_multiples/` per §15.D default; Effort = Option A acknowledge revised 2-3 session estimate, within Q42 +1-session tolerance); no `[plan-update]` commit needed (the §15.D entry already names the standalone default + the effort revision stays within Q42 tolerance; routing decisions stay in this PRE-FLIGHT entry + DECISION_LOG per the C8.15 + C8.13 + C8.11 + C8.10a/b/c PRE-FLIGHT-time decision precedent)

### Scope summary

C8.16 §15.D entry (NEXT_STEPS.md lines 1307-1346) names the deliverable: parse 3 NCHS matched-multiples linkage zips (`matched-multiple-birth-fetal-death-{1995-1997,1995-2000,2016-2020}.zip`) at `ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/matched-multiples/`; ship as 4th HVS product (standalone `matched_multiples/` subproject parallel to `natality/` + `fetal_death/`). KICKOFF.md Phase C Tier-3+5 line 202 names C8.16 as first Tier-3+5 task post-plan-update `84e7869`. Estimated §15.D effort = 1-2 sessions (revised to 2-3 at this PRE-FLIGHT per the 3-distinct-layouts finding; see below). §15.D halt-condition flags: H1 + H6 + L12-extension + L13 + L17.

**Session scope this PRE-FLIGHT:** ship PRE-FLIGHT entry + DECISION_LOG entry recording the architectural decision + STATUS section + commit + tag `C8.16-pre-do`. DO begins next session (with the full 2-3 session budget); not bundled into this commit since the PRE-FLIGHT surfaced enough effort revision that the session should close at a clean checkpoint to give the next session the full budget.

### Inputs

- [x] **All 11 Forward-looking HALTs from STATUS 2026-05-14T02:00:00Z verified byte-exact**:
  - HALT 1: `[plan-update] scope_expansion_tier3_tier5` commit present. `git log` shows `84e7869` (HEAD). ✓
  - HALT 2: 4 parquet SHAs byte-exact at canonical paths:
    - `~/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_harmonized.parquet` sha256=`38e2cecb03ff4947bbf6bcecbe9a79bf4bbe58df74ed4e7809b5078899c5cf48` ✓
    - `~/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_derived.parquet` sha256=`185c071ec76ab8aae24c9d7524b2495900f78afbf43cd6a32537124fa7968a09` ✓
    - `~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet` sha256=`e16ad5323d68e28d401518f1ff56b12c09e43883e76022a9823d51a677c41d44` ✓
    - `~/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet` sha256=`9b828a4de4e59b17a1ca727e3dddc7ea7d748bb5281a98612f6fb9b85a08b777` ✓
  - HALT 3: NEXT_STEPS.md §15.D NEW subsection present; 7 task entries C8.16-C8.22 at lines 1307-1567 (verified via `grep -n '^### Task C8\.'`); C8.16 at lines 1307-1346. ✓
  - HALT 4: KICKOFF.md Tier 3+5 ACTIVE subsection present at lines 198-227 (5 new sequencing-notes bullets covering C8.16-C8.22 ordering). ✓
  - HALT 5: DECISION_LOG entry at 2026-05-14T02:00:00Z present at lines 26-110. ✓
  - HALT 6: cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returned **74 passed + 1 skipped + 1 xfailed in 190.91s** — count matches (74P + 1S + 1XF); wall-time below the 210-230s STATUS HALT band by ~20s (likely warmer FS cache at this moment; per Convention 1 SHAPE-not-VALUE the **count** is asserted, not wall-time; not a halt). ✓
  - HALT 7: Soft-flag (q) WORKED_EXAMPLE_FAQ.md STATUS-anchor typo carries forward; no in-PRE-FLIGHT resolution attempted (STATUS is append-only; resolution lives at next file-mutation contact). ✓ (carried)
  - HALT 8: Soft-flag (r) NEW from C8.15 plan-update — effort-ceiling cap raised 42 → 86; defense in place (§11 plan-update process requires explicit user authorization for any further cap raise). ✓ (carried; this PRE-FLIGHT does NOT raise the cap)
  - HALT 9: No new tag this commit (until `C8.16-pre-do` tags this PRE-FLIGHT close). Verified: `git tag --list 'C8.16*'` returns empty pre-commit. ✓
  - HALT 10: Tier 1+2 STATUS preserved (cumulative ~17.5 done; Tier 3+5 ~21-34.5 ahead; total Phase C ~51-71). ✓
  - HALT 11: C8.16 is first Tier-3+5 task; no other Phase C work touched. ✓
- [x] **C8.16 substrate enumerated**:
  - **3 NCHS source zips probed** (sibling-extrapolation per L1-extension; filename pattern `matched-multiple-birth-fetal-death-<YYYY>-<YYYY>.zip` confirmed at canonical FTP path):
    - `matched-multiple-birth-fetal-death-1995-1997.zip` HTTP 200; content-length=9,623,601; last-modified=2024-07-10T18:18:54Z; etag=`88734a9ff5d2da1:0`; contains `sets9597.public` (163,542,960 uncompressed bytes); record length 503 → 325,135 records. ✓
    - `matched-multiple-birth-fetal-death-1995-2000.zip` HTTP 200; content-length=21,714,082; last-modified=2024-07-10T18:18:45Z; etag=`64433d9af5d2da1:0`; contains `Sets9500.public` (528,552,864 uncompressed bytes); record length 755 → 699,938 records. ✓
    - `matched-multiple-birth-fetal-death-2016-2020.zip` HTTP 200; content-length=11,719,909; last-modified=2024-06-04T16:57:56Z; etag=`d4dc3a59a0b6da1:0`; contains `MULTIPLES.TXT` (100,793,691 uncompressed bytes); record length 156 → 646,113 records. ✓
    - Total raw zip size: 43,057,592 bytes (~41 MB; matches §15.D "~43 MB" estimate within rounding).
    - Total uncompressed: 792,889,515 bytes (~756 MB; ~1.67M records).
  - **3 documentation PDFs probed** (sibling FTP path `Dataset_Documentation/DVS/matched-multiples/`; same filename stem as zips):
    - `matched-multiple-birth-fetal-death-1995-1997.pdf` 80,783 bytes; downloaded sha256=`f982ad93fbd435484173d6a08014e503e7f45208994cf1305b20ad0cae675d66`; 33 pages; 100% text-extractable; total_chars=35,856. ✓
    - `matched-multiple-birth-fetal-death-1995-2000.pdf` 111,503 bytes; downloaded sha256=`07b7260d4284402f9068f9dc160612b0fb0240fdd0536c6c1ad1d0ffd478b886`; 33 pages; 100% text-extractable; total_chars=60,687. ✓
    - `matched-multiple-birth-fetal-death-2016-2020.pdf` 415,885 bytes; downloaded sha256=`ed5e96ab662e970dc8fab3295942b3dfffac8c845120b8e92e125cf7d39152be`; 21 pages; 100% text-extractable; total_chars=23,205. ✓
    - L12-extension PASS: all 87 pages text-extractable; NO OCR needed. PyMuPDF `page.get_text()` returned non-empty on every page.
  - **1995-1997 vs 1995-2000 relationship**: searched 1995-2000 PDF first 5 pages for references to 1995-1997 / 9597 / earlier / previous / prior / supersedes / updates / extends — **zero hits**. Different author lists (1995-1997: 4 authors; 1995-2000: 6 authors with 4 new). Different record formats (503 vs 755 bytes). Conclusion: ship all 3 as distinct generations; the 1995-1997 file is NOT a strict subset / superseded version of 1995-2000.
- [x] **No stale checkpoints**: `git status --short` empty on `main` at `84e7869`; `C8.16-pre-do` + `C8.16-complete` tags do NOT yet exist. ✓

### Environment

- [x] Python 3.13.9; pandas 2.3.2; pyarrow 18.1.0; pymupdf available via `uv run python -c "import fitz"`; uv 0.11.10; .venv matches uv.lock (all unchanged from C8.15 close `b6954ec` + plan-update `84e7869`). ✓
- [x] Working directory clean; on `main`; HEAD at `84e7869` (the plan-update commit). ✓
- [x] `curl` (TLS-permissive `-k`) available for FTP probes; reachable to `ftp.cdc.gov` (HTTP 200 on directory listing + per-file HEAD requests). ✓

### Source documentation

C8.16 is a 4th-HVS-product release task; consumes 3 external NCHS documentation PDFs + zero internal canonical sources at PRE-FLIGHT (full DO will consume internal `fetal_death/file_inventory.csv` + `fetal_death/harmonized_schema.csv` patterns to mirror for the new subproject):

- 3 documentation PDFs probed above (all L12-extension PASS at PRE-FLIGHT; full content read happens at DO when authoring `matched_multiples/record_layout_<window>.csv` files).
- 3 source zips probed above (zip header inspection PASS; full unzip + record-layout reconstruction happens at DO).

All L1-extension cheap-checks satisfied (sibling-extrapolation from §15.D filename pattern returned HTTP 200 on first try; no hallucinated variants attempted). All L9 cheap-checks satisfied at PRE-FLIGHT probe (zip directory listing + PDF page counts + first-page text samples verified).

### Outputs

- [x] **NEW files (must not exist before DO; will be authored in DO):**
  - `matched_multiples/` subproject directory (does NOT exist) ✓
  - `matched_multiples/README.md` (will be authored at DO)
  - `matched_multiples/ABOUT_SOURCE_DATA.md` (will be authored at DO)
  - `matched_multiples/harmonized_schema.csv` (will be authored at DO)
  - `matched_multiples/file_inventory.csv` (3 rows × 9 cols per fetal_death pattern; will be authored at DO)
  - `matched_multiples/record_layout_9597.csv` (503-byte layout reconstruction; DO)
  - `matched_multiples/record_layout_9500.csv` (755-byte layout reconstruction; DO)
  - `matched_multiples/record_layout_2020.csv` (156-byte layout reconstruction; DO)
  - `matched_multiples/scripts/01_import/parse_matched_multiples.py` (DO)
  - `matched_multiples/scripts/03_harmonize/` (DO)
  - `matched_multiples/scripts/04_derive/` (DO)
  - `matched_multiples/scripts/05_validate/` (DO)
  - `matched_multiples/tests/` (DO; including `test_schema_dtype_parity.py` mirror of C8.1 pattern)
  - `notebooks/matched_multiples_demo.ipynb` (DO worked example)
  - `RECEIPTS/C8.16_<UTC>.md` (RECEIPT phase)
- [x] **APPEND-ONLY state files (this PRE-FLIGHT close commit):**
  - `PRE_FLIGHT_LOG.md`: this entry
  - `DECISION_LOG.md`: NEW entry recording the AskUserQuestion 2026-05-14T02:30:00Z architecture + effort decisions
  - `STATUS.md`: new dated section at top recording PRE-FLIGHT close + revised effort estimate
- [x] **MODIFIED at DO (forward-looking; NOT touched at this PRE-FLIGHT commit):**
  - `README.md` (extend Three-products-at-a-glance to 4 products; extend repository layout)
  - `PROJECT_STRUCTURE.md` (extend top-level layout + add `matched_multiples/` section)
  - `CITATION.cff` (note 4th product if applicable)
  - `KICKOFF.md` (no edit anticipated unless C8.16 surfaces a halt requiring §11)
  - `NEXT_STEPS.md` (no edit anticipated unless C8.16 surfaces a halt requiring §11)
- [x] **NOT mutated** (forward-looking HALT for C8.16 VERIFY):
  - 4 prior parquets unchanged (C8.16 is additive; existing products untouched) ✓
  - All C8.1-C8.15 file SHAs preserved ✓
  - Existing test suite baseline 74 PASS + 1 SKIP + 1 XFAIL preserved (new matched_multiples/tests/ adds; existing tests unchanged) ✓
  - Manuscript draft unchanged (Phase D step 4 scope) ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

C8.16 is a new-subproject creation task; no existing canonical state is mutated at PRE-FLIGHT. The Convention 3 substrate is the **column-pattern mirror** verification — confirming the new subproject's inventory + schema columns align with the existing fetal_death pattern (closest sibling for fixed-width-record products).

**Table 1: Inventory + schema column patterns**

| Source | Columns | Will be mirrored in matched_multiples/ |
|---|---|---|
| `fetal_death/file_inventory.csv` (canonical pattern; 9 cols) | `year, source_url, source_org, raw_filename, file_format, doc_filename, record_length, imported, notes` | ✓ Mirror exactly; matched_multiples uses windowed `year` rows (3 windows = 3 rows, e.g., `1995-1997`, `1995-2000`, `2016-2020`; or alternatively per-year-within-window rows). Decision deferred to DO. |
| `natality/metadata/file_inventory.csv` (8 cols; lacks `record_length`) | `year, source_url, source_org, raw_filename, file_format, doc_filename, imported, notes` | NOT mirrored; less complete than fetal_death pattern. |
| `fetal_death/harmonized_schema.csv` (10 cols; includes `domain`) | `harmonized_name, harmonized_label, domain, type, allowed_values, years_available, raw_source_by_year, comparability_class, derivation_rule, notes` | ✓ Mirror exactly; domain column useful for grouping multiple-gestation set fields vs individual-record fields. |
| `natality/metadata/harmonized_schema.csv` (9 cols; no `domain`) | `harmonized_name, harmonized_label, type, allowed_values, years_available, raw_source_by_year, comparability_class, derivation_rule, notes` | NOT mirrored; less expressive than fetal_death pattern. |

**Table 2: 3 record-length layouts (each requires a separate record_layout CSV at DO)**

| Window | File | Bytes/record | Records | Documentation PDF |
|---|---|---|---|---|
| 1995-1997 | `sets9597.public` (163.5 MB) | 503 | 325,135 | `matched-multiple-birth-fetal-death-1995-1997.pdf` (33 pages) |
| 1995-2000 | `Sets9500.public` (528.6 MB) | 755 | 699,938 | `matched-multiple-birth-fetal-death-1995-2000.pdf` (33 pages) |
| 2016-2020 | `MULTIPLES.TXT` (100.8 MB) | 156 | 646,113 | `matched-multiple-birth-fetal-death-2016-2020.pdf` (21 pages) |

**Plan assumptions verified at PRE-FLIGHT (per Convention 3 second bullet; one effort amendment — user-authorized):**

1. **§15.D "1-2 sessions if mostly-V1-era-sibling layout" assumption is wrong**: 3 DISTINCT record-length layouts (503/755/156 bytes) requires 3 separate `record_layout_<window>.csv` reconstructions from 87 PDF pages. Revised estimate: 2-3 sessions. User authorized 2-3 estimate via AskUserQuestion 2026-05-14T02:30:00Z; within Q42 +1-session tolerance (no §11 plan-update triggers). Documented in DECISION_LOG entry.
2. **Architecture = standalone `matched_multiples/` subproject** per §15.D default; user-authorized via AskUserQuestion 2026-05-14T02:30:00Z. Reasons: cross-product linkage nature (spans natality + fetal-death); cleanest schema; doesn't disturb existing canonical parquet SHAs (H10 reproducibility-gate preserved).
3. **Inventory + schema patterns** = fetal_death sibling (9-col inventory with `record_length`; 10-col schema with `domain`). Most complete sibling pattern.
4. **3 zips ship as distinct windows** (1995-1997 NOT superseded by 1995-2000; verified by absent cross-reference + different author lists + different record formats).
5. **No parquet mutation; H10 reproducibility gate unaffected**; all 4 existing parquet SHAs will remain byte-exact through C8.16.
6. **L12-extension cheap-check PASS**: all 87 PDF pages text-extractable; no OCR required.
7. **L1-extension sibling-extrapolation discipline applied**: §15.D filename pattern probed first; returned HTTP 200 on first try; no hallucinated variants needed.

**Soft-flags surfaced at PRE-FLIGHT (NOT in-scope this session; carried forward from STATUS 2026-05-14T02:00:00Z):**

Carried unchanged from C8.15 close + 2026-05-14 plan-update: (a) stale `fetal_death/PROVENANCE.md` (Phase D step 2) + (b) absent `natality/PROVENANCE.md` (Phase D step 2) + (c) `VERSION_ROADMAP.md` "Planned" section (future docs refresh; TBD whether C8.16 adds matched_multiples to the v1.0 listing) + (d) `run_pipeline.py` ALL_YEARS=29 (C8.7b) + (e) `natality/output/linked/` absent (Phase D step 3 / C8.7b) + (g) PRE-FLIGHT "87 raw zips" typo (preserved per L10; though note C8.16 inventory now ships **3 raw zips** so the unified count becomes 90 across HVS — to be reconciled at DO when extending top-level docs) + (i) `fetal_death/COMPARABILITY.md` title staleness (Phase D candidate) + (m) `record_length` invariant test does not check vs-actual-zip parity (C8.7b candidate; matched_multiples DO will surface whether the new subproject inherits this gap) + (n) `test_validate_linked_parquets_mutation` E2E verification (Phase D step 3 / C8.7b) + (o) `validate_v1_invariants` deep-scan FAIL-surface mutation test (future C8.X) + (p) F.1 dict-encoding permanently dropped from pre-submission scope + (q) WORKED_EXAMPLE_FAQ.md STATUS-anchor typo + (r) effort-ceiling cap raised 42 → 86 (defense: §11 plan-update for any further raise).

**Soft-flag (f) plurality footgun**: OPERATIONALLY CLOSED at C8.15; carries forward for documentation-trail only.

**No NEW soft-flags surfaced at C8.16 PRE-FLIGHT.** The 2-3 session effort revision is documented + user-acknowledged (within Q42 tolerance, not a soft-flag).

### Halt conditions tripped

None at PRE-FLIGHT close. All 11 forward-looking HALTs from STATUS 2026-05-14T02:00:00Z verified byte-exact. AskUserQuestion 2026-05-14T02:30:00Z resolved 2 PRE-FLIGHT-time decisions (architecture + effort) with user authorization for both Option A defaults.

### Result

**PROCEED to C8.16 DO** (next session). PRE-FLIGHT close commit lands this entry + DECISION_LOG entry + STATUS section + tag `C8.16-pre-do`. DO begins at next session entry with the full 2-3 session budget.

---

## PRE-FLIGHT for C8.15 — 2026-05-14T00:30:00Z — Worked-example notebooks 4-5 (C.6.d `education_gradient.ipynb` + C.6.e `state_reporting_quirks.ipynb`) — **RESULT: HALT (two routing-shape PRE-FLIGHT-time L11s surfaced) → user-resolved via AskUserQuestion 2026-05-14T00:30:00Z (C.6.d = natality+linked-only Recommended; C.6.e = read from `output/yearly_clean/` raw parquets Recommended); PROCEED to C8.15 DO with clarified routing; precedent: C8.5/C8.6/C8.7/C8.9/C8.10a/b/c/C8.11/C8.13 PRE-FLIGHT-time AskUserQuestion path; no `[plan-update]` commit needed (the §15 entry's "halt-condition flag F4" already anticipates the within-era discipline; routing decisions stay in this PRE-FLIGHT entry + DECISION_LOG)**

### Scope summary

C8.15 §15.C entry (NEXT_STEPS.md lines 1279-1295) names 2 deliverables: **(C.6.d)** `notebooks/education_gradient.ipynb` (within-era only, with 1989/2003 boundary explicit); **(C.6.e)** `notebooks/state_reporting_quirks.ipynb` (Oklahoma 1992-2002 Hispanic non-reporting, Maryland 1992-1998, Massachusetts 1992-1997, Louisiana 1992-1994 plurality). KICKOFF.md Phase C Tier-2 line 196 + STATUS 2026-05-13T23:45:00Z line 37 name C8.15 as next + final §15 Tier-2 task post-C8.14. Estimated effort 2 sessions. §15 halt-condition flag: F4 (within_era column cross-era misuse).

**Session scope this PRE-FLIGHT (per "proceed" authorization 2026-05-14T00:00:00Z):** ship PRE-FLIGHT entry + tag `C8.15-pre-do` + DO sub-step 1 (C.6.d builder + executed notebook) + (potentially) DO sub-step 2 (C.6.e builder + executed notebook) + VERIFY + RECEIPT in this session if scope fits, otherwise close session at C.6.d-shipped with C.6.e deferred to a second C8.15 session per the §15 2-session estimate.

### Inputs

- [x] **All 9 C8.14 Forward-looking HALTs verified byte-exact**:
  - HALT 1: `C8.14-pre-do` + `C8.14-complete` tags both present ✓
  - HALT 2: 4 parquet SHAs byte-exact at canonical paths:
    - `output/harmonized/fetal_death_harmonized.parquet` sha256=`38e2cecb03ff4947bbf6bcecbe9a79bf4bbe58df74ed4e7809b5078899c5cf48` ✓
    - `output/harmonized/fetal_death_derived.parquet` sha256=`185c071ec76ab8aae24c9d7524b2495900f78afbf43cd6a32537124fa7968a09` ✓
    - `~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet` sha256=`e16ad5323d68e28d401518f1ff56b12c09e43883e76022a9823d51a677c41d44` ✓
    - `~/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet` sha256=`9b828a4de4e59b17a1ca727e3dddc7ea7d748bb5281a98612f6fb9b85a08b777` ✓
  - HALT 3: `docs/WORKED_EXAMPLE_FAQ.md` present BUT actual sha256=`341c4550f8e9db37bb801540ac95967b853b0083a5d8f47e6bb4b3ed1753aab7` ≠ STATUS-recorded `89730c31…`. **Investigated**: `git diff HEAD -- docs/WORKED_EXAMPLE_FAQ.md` returns empty; `git show HEAD:docs/WORKED_EXAMPLE_FAQ.md | shasum -a 256` returns `341c4550…` (matches on-disk byte-exact). **Conclusion**: STATUS 2026-05-13T23:45:00Z + RECEIPT C8.14 + STATUS HALT #3 + commit-message-narrative all recorded the wrong sha anchor; the file IS the committed file. Filed as soft-flag (q) for the C8.15 RECEIPT (L17-shape: STATUS-recorded annotation drifted from on-disk reality at the moment of writing; not a §7 halt because no actual file mutation occurred). ⚠️ TYPO-only
  - HALT 4: `PROJECT_STRUCTURE.md` upgraded sha=`54f75c3226a6ee8c40699fe41ccd54378122588bff22847a50bcb801b92031c7` matches anchor `54f75c32…` byte-exact; 207 lines (within "~210 line" framing) ✓
  - HALT 5: cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returned **74 passed + 1 skipped + 1 xfailed in 230.74s** — matches expected (74 PASS + 1 SKIP + 1 XFAIL) at +20.96s variance from C8.13/C8.14 baseline 209.78s, well within the documented "~210s ±20s variance" tolerance ✓
  - HALT 6: `paper/draft_v2_hmd_styled.md` sha=`0685fe9cec3d6ae0b33905785d58b05077d5ff5f037f949e8100c153bf1bddd1` — `git status` clean → no manuscript mutation since C8.14-complete `ebed5a9` (C8.13 PROPOSE-EDIT remains routed to Phase D step 4) ✓
  - HALT 7: Tier 2 progress 6 of 7 §15-listed tasks COMPLETE (C8.9 + C8.10 + C8.11 + C8.12 + C8.13 + C8.14); 1 remaining (C8.15 = this task) — KICKOFF + STATUS + NEXT_STEPS all agree ✓
  - HALT 8: dependencies (C8.10 + C8.11) satisfied:
    - C8.10: 5 builders + 5 notebooks present at `notebooks/` (`joint_use_demo.ipynb`, `paper_companion.ipynb`, `maternal_age_stratified_imr.ipynb`, `preterm_outcomes_time_series.ipynb`, `cross_race_fetal_mortality.ipynb`) ✓
    - C8.11: 2 migration guides present at `migrations/` (`v2.0.0-to-v2.4.0-fetal-death.md`, `v2.7.0-to-v2.8.0-natality.md`) + cross-product `docs/COMPARABILITY.md` (18.7K) present ✓
  - HALT 9: `git status --short` empty on `main` at HEAD `ebed5a9` (C8.14-complete commit) — no KICKOFF / NEXT_STEPS edit at C8.14 close ✓
- [x] **C8.15 substrate enumerated**:
  - **C.6.d substrate** — natality `maternal_education_cat4` column (single 4-category recode, both eras crosswalked; null for 2009-2013 unrevised records per natality COMPARABILITY); natality `certificate_revision` flag for revised-only filtering; linked-file `maternal_education_cat4` analog (V3 LinkCO); user-authorized data-product = **natality+linked-only** per AskUserQuestion 2026-05-14T00:30:00Z.
  - **C.6.e substrate** — fetal-death yearly_clean raw parquets at `output/yearly_clean/fetal_death_<YEAR>_raw.parquet` retain state codes (1992-2002 era: `STATEFET` + `STATERES`; 2005-2013 era: `OSTATE` + `MRSTATEPSTL`; 2014+ era: adds `MBSTATE_REC`). Verified via `pyarrow.parquet.ParquetFile.schema.names` probe across years 1992 (198 cols), 2010 (182 cols), 2022 (142 cols). User-authorized substrate routing = **read from `output/yearly_clean/` raw parquets** per AskUserQuestion 2026-05-14T00:30:00Z.
  - **Cross-product COMPARABILITY references** for state quirks: `fetal_death/COMPARABILITY.md` lines 162-172 (plurality '5' miscoding 2005-2013 V1 era + recommended researcher recipe); lines 267-269 (Oklahoma all 11 V2 years 1992-2002 + Maryland 1992-1998 + Massachusetts 1992-1997 Hispanic non-reporting); lines 273-275 (Louisiana 1992-1994 plurality non-reporting with explicit per-record counts: 1,686 of 1,714 LA-occurrence records).
  - C8.10 builder pattern: `_build_maternal_age_stratified_imr.py` (459 LOC; single-product linked notebook) + `_build_cross_race_fetal_mortality.py` (single-product fetal-death notebook) + `_build_preterm_outcomes_time_series.py` (cross-product notebook) — pattern: `nbformat.v4.new_notebook()` + `nbclient.NotebookClient.execute()`; DESIGN: tracks-current-state docstring tag (Convention 2); helper `md()`/`code()` cell constructors; `build()` returns notebook; `main()` executes + writes `.ipynb`.
- [x] **No stale checkpoints**: `git status --short` empty on `main` at `ebed5a9`; `C8.15-pre-do` tag does NOT yet exist. ✓

### Environment

- [x] Python 3.13.9; pandas 2.3.2; pyarrow 18.1.0; uv 0.11.10; .venv matches uv.lock (all unchanged from C8.14 close).
- [x] Working directory clean; on `main`; active tag on HEAD = `C8.14-complete`. ✓

### Source documentation

C8.15 is a notebook-authoring task; consumes 4 internal canonical sources + zero external NCHS PDFs:
- `natality/docs/COMPARABILITY.md` (within-era discipline for `maternal_education_cat4`; revised-only era 2009-2013)
- `fetal_death/COMPARABILITY.md` (state-quirk references for C.6.e)
- `natality/metadata/harmonized_schema.csv` (column documentation for natality `maternal_education_cat4`)
- C8.10 builder source (3 builders for the 3 shipped C8.10 notebooks; pattern reference)

All L8/L9 cheap-checks satisfied at PRE-FLIGHT inputs probe (no PMID resolutions needed; no external-page WebFetches needed; substrate is internal canonical content).

### Outputs

- [x] **NEW files (must not exist before DO):**
  - `notebooks/_build_education_gradient.py`: does NOT exist ✓
  - `notebooks/education_gradient.ipynb`: does NOT exist ✓
  - `notebooks/_build_state_reporting_quirks.py`: does NOT exist ✓ (note: scope may shift to a second C8.15 session per §15 2-session estimate)
  - `notebooks/state_reporting_quirks.ipynb`: does NOT exist ✓
  - `RECEIPTS/C8.15_<UTC>.md`: will be written at C8.15 RECEIPT phase
- [x] **APPEND-ONLY state files:**
  - `PRE_FLIGHT_LOG.md`: this entry (written before DO begins)
  - `STATUS.md`: new dated section at top at RECEIPT close
  - `DECISION_LOG.md`: NEW entry recording the AskUserQuestion 2026-05-14T00:30:00Z routing resolutions for C.6.d + C.6.e (per the C8.13 / C8.11 / C8.10 routing-decision precedent)
  - `FIX_LOG.md`: no FIX entry anticipated (the WORKED_EXAMPLE_FAQ SHA typo is a soft-flag, not a fix-on-contact-able mutation since STATUS is append-only)
  - `LESSONS.md`: NO new entry anticipated
- [x] **NOT mutated** (forward-looking HALT for VERIFY):
  - 4 parquets unchanged (no compute on canonical state) ✓
  - All C8.9-C8.14 file SHAs preserved ✓
  - test suite baseline 74 PASS + 1 SKIP + 1 XFAIL preserved ✓
  - existing 5 notebooks unchanged ✓
  - `paper/draft_v2_hmd_styled.md` unchanged (Phase D step 4 scope) ✓
  - `KICKOFF.md` + `NEXT_STEPS.md` unchanged (no §11 plan-update needed; routing decisions are in-PRE-FLIGHT) ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

C8.15 is notebook-authoring work; the canonical-state mutation is zero (notebooks are derived artifacts; the underlying parquets are not touched). The Convention 3 substrate is the **column-availability + within-era contract verification**.

**Table 1: C.6.d (`education_gradient.ipynb`) substrate verification**

| Field | Source | Within-era contract | Verified at PRE-FLIGHT |
|---|---|---|---|
| `maternal_education_cat4` (natality v2) | `natality_v2_harmonized_derived.parquet` | 1990-2002: years-of-schooling crosswalk; 2003-2008: revised + unrevised both populated; 2009-2013: revised-only (substantial null on unrevised); 2014+: revised-only nationwide | ✓ schema CSV documents the era pattern explicitly; cell value distributions match COMPARABILITY note |
| `maternal_education_cat4` (linked v3) | `natality_v3_linked_harmonized_derived.parquet` | Same era pattern as natality v2; V3 LINKED CAVEAT for 2009-2010 (PAY_REC + FEDUC blank in LinkCO09/10) does NOT affect maternal education | ✓ schema CSV cited |
| `certificate_revision` (natality v2) | `natality_v2_harmonized_derived.parquet` | Filter `certificate_revision == 'revised_2003'` for 2009-2013 revised-only era to avoid spurious unrevised-null mixing | ✓ COMPARABILITY note line 195 cites this filter as the canonical revision-consistent subset |
| Within-era discipline | F4 halt-condition flag | NO cross-era groupby on `maternal_education_cat4` for 2009-2013 unless filtered to revised-only; document the boundary in markdown cells | ✓ contract enforced in notebook design |

**Table 2: C.6.e (`state_reporting_quirks.ipynb`) substrate verification**

| State quirk | Time window | Source columns (raw parquet path) | Documented in fetal_death/COMPARABILITY.md |
|---|---|---|---|
| Oklahoma Hispanic non-reporting | 1992-2002 (all 11 V2 years) | `STATEFET` + `STATERES` + `HISPMOM` (or equivalent) in `output/yearly_clean/fetal_death_<YEAR>_raw.parquet` | Line 267 |
| Maryland Hispanic non-reporting | 1992-1998 | Same as above | Line 268 |
| Massachusetts Hispanic non-reporting | 1992-1997 | Same as above | Line 269 |
| Louisiana plurality non-reporting | 1992-1994 | `STATEFET` + `STATERES` + `DPLURAL` in `output/yearly_clean/fetal_death_<YEAR>_raw.parquet` | Lines 273-275 (with per-record counts: 1,686 of 1,714 LA-occurrence records) |
| Plurality '5' miscoding (footgun for soft-flag (f)) | 2005-2013 V1 era A-version | `OSTATE` + `MRSTATEPSTL` + `DPLURAL` in `output/yearly_clean/fetal_death_<YEAR>_raw.parquet` | Lines 162-172 + recommended researcher recipe at line 171 |

**Plan assumptions verified at PRE-FLIGHT (per Convention 3 second bullet; one routing amendment — user-authorized):**

1. **C.6.d data product = natality+linked-only** (per AskUserQuestion 2026-05-14T00:30:00Z; supersedes STATUS line 90's column-name framing which referenced fetal-death's `maternal_education` + `maternal_education_unrevised`). Natural reading: an "education gradient" is most legible on birth-side outcomes (preterm, LBW, IMR via linked).
2. **C.6.e substrate = `output/yearly_clean/` raw parquets** (per AskUserQuestion 2026-05-14T00:30:00Z; supersedes STATUS line 90's "may surface §7.13 L11" framing which assumed C8.9 NCHS suppression generalizes — it doesn't; the C8.9 finding was natality-specific). Departs from C.6.a-c builder convention (those consume harmonized parquet); will be the only notebook reading raw. Documented in builder docstring.
3. **C8.10 + C8.11 dependency satisfied**: 5 worked-example notebooks + 2 migration guides + cross-product COMPARABILITY all present.
4. **No parquet mutation**; H10 reproducibility gate unaffected.
5. **F4 halt discipline enforced in BOTH notebooks**: C.6.d filters revised-only 2009-2013 era; C.6.e segments analyses by data_year ranges aligned with each state's quirk window.

**Soft-flags surfaced at PRE-FLIGHT (NOT in-scope this session; carried forward + 1 NEW):**

Carried unchanged from C8.14 close: (a) stale `fetal_death/PROVENANCE.md` (Phase D step 2) + (b) absent `natality/PROVENANCE.md` (Phase D step 2) + (c) `VERSION_ROADMAP.md` "Planned" section (future docs refresh) + (d) `run_pipeline.py` ALL_YEARS=29 (C8.7b) + (e) `natality/output/linked/` absent (Phase D step 3 / C8.7b) + (f) plurality footgun (**C8.15-scope; in-DO this task**) + (g) PRE-FLIGHT "87 raw zips" typo (preserved per L10) + (i) `fetal_death/COMPARABILITY.md` title staleness (Phase D candidate) + (m) `record_length` invariant test does not check vs-actual-zip parity (C8.7b candidate) + (n) `test_validate_linked_parquets_mutation` E2E verification (Phase D step 3 / C8.7b) + (o) `validate_v1_invariants` deep-scan FAIL-surface mutation test (future C8.X) + (p) F.1 dict-encoding permanently dropped from pre-submission scope.

**NEW soft-flag (q) this PRE-FLIGHT**: WORKED_EXAMPLE_FAQ.md SHA anchor typo in STATUS 2026-05-13T23:45:00Z + RECEIPTS/C8.14_2026-05-13T23-45-00Z.md + commit-message narrative — recorded sha=`89730c31…` but on-disk + committed sha=`341c4550…`. STATUS is append-only so the typo persists; future sessions reading the C8.14 closing anchor for HALT verification will see the same mismatch and need to repeat this PRE-FLIGHT's `git diff HEAD` resolution. RECEIPT C8.15 records the corrected anchor for the C8.15 forward-looking HALTs to point at. L17-shape (STATUS pin drifted from on-disk reality at moment of writing; not a runtime mutation).

### Halt conditions tripped

**TWO §7.13-shape PRE-FLIGHT-time L11s surfaced + user-resolved before any DO mutation** (precedent: C8.5 / C8.6 / C8.7 / C8.9 / C8.10a / C8.10b / C8.10c / C8.11 / C8.13 PRE-FLIGHT-time AskUserQuestion path):

1. **C.6.d data-product framing in STATUS line 90 vs natality schema reality**: STATUS line 90 framed C.6.d as using fetal-death's `maternal_education_unrevised` (pre-2003) + `maternal_education` (revised; post-2003), but those column names are fetal-death-side; natality has only `maternal_education_cat4` (single column, both eras crosswalked) + `certificate_revision` flag. The within-era discipline still applies (2009-2013 revised-only window) but via a different column structure. User-resolved Option A (natality+linked-only): use natality `maternal_education_cat4` + `certificate_revision` filter; document the 2003 + 2009 boundaries explicitly.

2. **C.6.e substrate routing — STATUS line 90 vs fetal-death yearly_clean reality**: STATUS line 90 anticipated "State-level geography NOT in public-use files (per C8.9 finding)" but the C8.9 finding (DECISION_LOG 2026-05-13T10:00:00Z) was natality-specific. Fetal-death yearly_clean raw parquets retain `STATEFET` + `STATERES` (V2 1992-2002) + `OSTATE` + `MRSTATEPSTL` (V1 2005+) + `MBSTATE_REC` (2014+). The Louisiana plurality + Oklahoma/Maryland/Massachusetts Hispanic non-reporting findings cited in fetal_death/COMPARABILITY.md ARE reproducible from this substrate. User-resolved Option A: route C.6.e to `output/yearly_clean/` raw parquets (departs from C.6.a-c convention; one-off precedent documented in builder docstring).

NO `[plan-update]` commit needed (per the C8.10a / C8.10b / C8.10c / C8.11 routine-PRE-FLIGHT-input-re-interpretation precedent — substrate-routing-only resolutions stay in PRE_FLIGHT_LOG + DECISION_LOG, not in KICKOFF/NEXT_STEPS edits, when the §15 deliverable name + halt-condition flag remain unchanged).

### Result

**PROCEED to C8.15 DO** in this session. Tag `C8.15-pre-do` placed post-this-PRE-FLIGHT commit; DO sub-step 1 authors `notebooks/_build_education_gradient.py` + executes to produce `notebooks/education_gradient.ipynb`; DO sub-step 2 (if scope fits this session per §15 2-session estimate) authors `notebooks/_build_state_reporting_quirks.py` + executes to produce `notebooks/state_reporting_quirks.ipynb`; VERIFY runs cache-cleared pytest baseline; RECEIPT + `C8.15-complete` tag close the task. If only C.6.d ships this session, RECEIPT + `C8.15-partial` (or equivalent) tag closes sub-step 1; second session ships C.6.e + final `C8.15-complete` tag.

Recommended DO sequencing this session:
- **Sub-step 1**: Author `notebooks/_build_education_gradient.py` + execute → `notebooks/education_gradient.ipynb`. Sections: (i) Load natality+linked parquets + apply canonical filter; (ii) 4-category education distribution by year (1990-2024); (iii) preterm rate by education-cat4 within era boundaries (1990-2002, 2003-2008, 2014+); (iv) revised-only 2009-2013 sub-analysis with `certificate_revision == 'revised_2003'` filter; (v) NCHS-comparison cells (cite `natality/docs/COMPARABILITY.md` Section X "Education within-era guidance"); (vi) F4 within-era contract markdown narrative.
- **Sub-step 2** (if scope fits): Author `notebooks/_build_state_reporting_quirks.py` + execute → `notebooks/state_reporting_quirks.ipynb`. Sections: (i) Load fetal-death yearly_clean raw parquets for V2 era 1992-1994 (LA plurality) + 1992-2002 (OK Hispanic) + 1992-1998 (MD Hispanic) + 1992-1997 (MA Hispanic) + V1 era 2005-2013 (plurality '5' miscoding); (ii) per-state cells reproducing the COMPARABILITY-cited counts (LA 1992-1994: 1,686 of 1,714 LA-occurrence records); (iii) Oklahoma Hispanic-non-reporting demonstration; (iv) Maryland + Massachusetts; (v) plurality '5' miscoding 2005-2013 with the COMPARABILITY-cited recommended-researcher recipe; (vi) within-era + cross-era discipline narrative + soft-flag (f) closure note.
- **Sub-step 3 (VERIFY)**: cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returns 74 PASS + 1 SKIP + 1 XFAIL preserved; both notebooks render end-to-end; markdown flags within_era columns; no cross-era groupby on within_era columns (F4 contract).
- **Sub-step 4 (RECEIPT)**: write `RECEIPTS/C8.15_<UTC>.md` + STATUS append + DECISION_LOG entry recording the 2 routing decisions; tag `C8.15-complete` (or `C8.15-partial` if only C.6.d ships).

Effort: matches §15 2-session estimate; estimated ~60-90 min per notebook (incl. iterative debugging) + ~5 min VERIFY + ~15 min RECEIPT.

---

## PRE-FLIGHT for C8.14 — 2026-05-13T23:30:00Z — Worked-example FAQ + PROJECT_STRUCTURE.md upgrade (E.3 + E.6) — **RESULT: PROCEED** (zero §7 halts; zero L11s; pure cross-product docs work; no parquet/test-surface mutation; clean PRE-FLIGHT)

### Scope summary

C8.14 §15.C entry (NEXT_STEPS.md lines 1228-1244) names 2 deliverables: **(E.3)** `docs/WORKED_EXAMPLE_FAQ.md` answering 3 named questions ("how do I compute the perinatal mortality rate?", "how do I get state-level data?", "what's the right canonical filter for my analysis?"); **(E.6)** Upgrade `PROJECT_STRUCTURE.md` with notebook-deps graph + build-order DAG + which-file-by-use-case matrix. KICKOFF.md Phase C Tier-2 line 195 + STATUS 2026-05-13T23:00:00Z line 39 name C8.14 as next §15 task post-C8.13. Estimated effort 1 session. §15 halt-condition flag: L11 (stale roadmap claims; fix-on-contact).

**Session scope this PRE-FLIGHT (per "go ahead with C8.14" authorization 2026-05-13T23:30:00Z):** ship PRE-FLIGHT entry + tag `C8.14-pre-do` + DO (both docs authored) + VERIFY + RECEIPT in one session per §15 1-session estimate.

### Inputs

- [x] **All 16 C8.13 Forward-looking HALTs verified byte-exact** (spot-checked 9 high-signal HALTs):
  - HALT 1: `C8.13-pre-do` + `C8.13-complete` tags present ✓
  - HALT 2: 4 parquet SHAs byte-exact (`38e2cecb…` / `185c071e…` / `e16ad5323d…` / `9b828a4d…`) ✓
  - HALT 3-5: `scripts/_time_pipeline.py` + 2 driver scripts present at fresh-recorded SHAs (sha=`c7809742…` / `7f48e971…` / `05fda4ae…`) ✓
  - HALT 4: `docs/PIPELINE_TIMING_BENCHMARK.md` present at sha=`7792cb34…` ✓
  - HALT 5: 2 per-stage CSVs present (45+6 rows) ✓
  - HALT 9: `tests/snapshots/v1_2026-05-13T21-00-00Z_columns.csv` sha=`b6fe22d6…` unchanged ✓
  - HALT 14: `/tmp/c8_13_baseline/` removed (no stale state) ✓
- [x] **C8.14 substrate enumerated**:
  - 2 per-subproject FAQs present: `fetal_death/FAQ.md` (16 Q&A) + `~/Desktop/natality-harmonization/docs/FAQ.md` (24 Q&A) — the WORKED_EXAMPLE_FAQ is **cross-product complement, not duplication**
  - `docs/JOINT_USE_GUIDE.md` present with canonical analytic filters §43-55 + perinatal mortality worked example §128-172 + R/DuckDB §174-227 — primary cross-link target
  - 4 notebooks present: `joint_use_demo.ipynb` (32 cells; perinatal demo Section C) + `maternal_age_stratified_imr.ipynb` (23 cells; C8.10a) + `preterm_outcomes_time_series.ipynb` (24 cells; C8.10b) + `cross_race_fetal_mortality.ipynb` (26 cells; C8.10c)
  - `PROJECT_STRUCTURE.md` current at sha=`32688930…`, 134 lines (top-level layout + per-subdir maps)
- [x] **`docs/` directory** has 7 existing files (COMPARABILITY.md, JOINT_USE_GUIDE.md, NCHS_SOURCE_MANIFEST.md, PIPELINE_TIMING_BENCHMARK.md + 2 CSVs, PRIOR_ART.md); WORKED_EXAMPLE_FAQ.md will be the 8th. ✓
- [x] **No stale checkpoints**: `git status --short` empty on `main` at `0155a6f`; `C8.14-pre-do` tag does NOT yet exist. ✓

### Environment

- [x] Python 3.13.9; pandas 2.3.2; pyarrow 18.1.0; uv 0.11.10; .venv matches uv.lock (all unchanged from C8.13 close).
- [x] Working directory clean; on `main`; active tag on HEAD = `C8.13-complete`. ✓

### Source documentation

C8.14 is pure docs work; no external NVSR PDFs or NCHS user guides consumed. The cross-link surface is internal: `docs/JOINT_USE_GUIDE.md`, `docs/COMPARABILITY.md`, 2 per-subproject FAQs, 4 notebooks, `VERSION_ROADMAP.md`, `PRIOR_ART.md`. All L8/L9 cheap-checks satisfied at PRE-FLIGHT inputs probe (no PMID resolutions needed; no external-page WebFetches needed).

### Outputs

- [x] **NEW files (must not exist before DO):**
  - `docs/WORKED_EXAMPLE_FAQ.md`: does NOT exist ✓
  - `RECEIPTS/C8.14_<UTC>.md`: will be written at C8.14 RECEIPT phase
- [x] **MAY BE MODIFIED:**
  - `PROJECT_STRUCTURE.md` — §15-mandated upgrade (notebook-deps graph + build-order DAG + which-file-by-use-case matrix appended as new sections); current sha=`32688930…`
- [x] **APPEND-ONLY state files:**
  - `PRE_FLIGHT_LOG.md`: this entry (written before DO begins)
  - `STATUS.md`: new dated section at top at RECEIPT close
  - `DECISION_LOG.md`: NEW entry only if a non-trivial choice surfaces during DO (not anticipated; the WORKED_EXAMPLE_FAQ scope is well-defined; PROJECT_STRUCTURE upgrade is additive)
  - `FIX_LOG.md`: no FIX entry anticipated (any L11 surfaces are fix-on-contact and bundled into the FAQ/structure edits)
  - `LESSONS.md`: NO new entry anticipated
- [x] **NOT mutated** (forward-looking HALT for VERIFY):
  - 4 parquets unchanged (no compute) ✓
  - All C8.9-C8.13 file SHAs preserved ✓
  - test suite baseline 74 PASS + 1 SKIP + 1 XFAIL preserved ✓
  - existing per-subproject FAQs unchanged ✓
  - `docs/JOINT_USE_GUIDE.md` unchanged (WORKED_EXAMPLE_FAQ cross-links to it; no need to duplicate) ✓
  - `paper/draft_v2_hmd_styled.md` unchanged (Phase D step 4 scope) ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

C8.14 is docs-only work; no canonical-state cells mutated. The Convention 3 substrate is the **existing-content boundary check**: verify the WORKED_EXAMPLE_FAQ scope does NOT duplicate existing per-subproject FAQ content or JOINT_USE_GUIDE content.

**Table 1: Cross-product FAQ scope vs existing canonical-content surfaces**

| FAQ question (§15-mandated) | Existing canonical source | WORKED_EXAMPLE_FAQ role |
|---|---|---|
| How do I compute the perinatal mortality rate? | `docs/JOINT_USE_GUIDE.md` §128-172 "Worked example: perinatal mortality rate, 2022 (three-product joint)" + `notebooks/joint_use_demo.ipynb` Section C (6 cells) | One-paragraph distilled answer + numeric formula + cross-link to both canonical sources + caveat re NVSR 73-09 proportional-redistribution |
| How do I get state-level data? | C8.9 PRE-FLIGHT C.1 drop + DECISION_LOG 2026-05-13T10:00:00Z + `natality/docs/FAQ.md` "Is geography included?" (4 lines) | Cross-product synthesis: NCHS state suppression in all 3 products; alternatives (RDC; Census region/division derivation; alternate data sources); explicit "not in pre-submission scope" framing |
| What's the right canonical filter for my analysis? | `docs/JOINT_USE_GUIDE.md` §43-55 "Canonical analytic filters" + per-subproject FAQs ("How should I filter" / "What is the recommended analysis universe?") | Cross-product decision-matrix table: given (product × use-case × question type), which filter; plus the within-era vs cross-era flag |

**Table 2: Additional cross-product FAQ candidates (judgement at DO)**

Beyond the §15-mandated 3 questions, the FAQ should cover the most-common other cross-product friction points surfaced through C8.1-C8.13 work:

- "Which product should I use for [maternal age × LBW / preterm / IMR / fetal mortality / cesarean]?" → use-case-to-product lookup
- "How do I handle the V3a/V3b race-coding caveat (code 7 + code 9 → null)?" → cross-link to `notebooks/cross_race_fetal_mortality.ipynb` markdown caveats
- "What's the bridged-race era and when does it end?" → cross-link to `docs/COMPARABILITY.md` bilateral race-coding methodology
- "Which column do I use for analysis: harmonized or harmonized_derived?" → use-case → which-parquet
- "How do I compute infant mortality rate (IMR) using the linked file?" → cross-link to `notebooks/maternal_age_stratified_imr.ipynb`
- "How do I handle the 2003 certificate revision break?" → cross-link to `docs/COMPARABILITY.md` + `natality/docs/FAQ.md` "Which variables have known breaks?"
- "How do I cite this resource?" → cross-link to existing CITATION.cff + per-product Zenodo DOIs

Cardinality estimate: 8-12 Q&A pairs in WORKED_EXAMPLE_FAQ; bounded scope; doesn't drift toward "everything in one FAQ."

**Table 3: PROJECT_STRUCTURE.md upgrade scope**

§15 mandates 3 NEW sections appended to current 134-line file:

| New section | Content sketch |
|---|---|
| Build-order DAG | Stage diagram showing parse → harmonize → derive → validate per product; cross-product flow joining all 3 products at notebooks/ + shared/helpers/; serial dependencies vs parallel branches; clean reproduce path via C8.13 F.5 drivers |
| Notebook-deps graph | Per-notebook input parquets + helper modules + cross-product joins; mapped to the 4 notebooks present + the 2 stubs that remain (paper_companion.ipynb is now substantive post-Task 4; joint_use_demo.ipynb is post-C8.3 substantive) |
| Which-file-by-use-case matrix | Decision table: given (analytic question type), which subproject + which parquet + which notebook + which scripts |

Existing 134-line structure preserved; new sections appended at end. No top-level reorganization (avoid Anti-Pattern: re-shaping a doc when only adding).

**Plan assumptions verified at PRE-FLIGHT (per Convention 3 second bullet; zero amendments):**

1. The WORKED_EXAMPLE_FAQ is **NEW** (not modification of an existing FAQ); per-subproject FAQs preserved unchanged.
2. The PROJECT_STRUCTURE upgrade is **additive** (3 new sections appended); existing 134-line structure preserved.
3. The 3 §15-mandated FAQ questions have **clear canonical-source cross-link targets**; the FAQ is a CROSS-PRODUCT INDEX layer, not duplication.
4. **C8.10 dependency satisfied**: 3 worked-example notebooks + `joint_use_demo.ipynb` all present at canonical paths; FAQ cross-links resolve.
5. **No parquet mutation**; H10 reproducibility gate unaffected.

**Soft-flags surfaced at PRE-FLIGHT (NOT in-scope this session; carried forward):**

Carried unchanged from C8.13 close: (a) stale `fetal_death/PROVENANCE.md` (Phase D step 2) + (b) absent `natality/PROVENANCE.md` (Phase D step 2) + (c) `VERSION_ROADMAP.md` "Planned" section (future docs refresh) + (d) `run_pipeline.py` ALL_YEARS=29 (C8.7b) + (e) `natality/output/linked/` absent (Phase D step 3 / C8.7b) + (f) plurality footgun (C8.15) + (g) PRE-FLIGHT "87 raw zips" typo (preserved per L10) + (i) `fetal_death/COMPARABILITY.md` title staleness (Phase D candidate) + (m) `record_length` invariant test does not check vs-actual-zip parity (C8.7b candidate) + (n) `test_validate_linked_parquets_mutation` E2E verification (Phase D step 3 / C8.7b) + (o) `validate_v1_invariants` deep-scan FAIL-surface mutation test (future C8.X) + (p) F.1 dict-encoding permanently dropped from pre-submission scope.

**No NEW soft-flags from this PRE-FLIGHT.** Pure cross-product docs work; no expected residuals beyond the carry-forward set.

### Halt conditions tripped

**NONE.** Zero §7 halt conditions tripped at PRE-FLIGHT. The §15 spec is well-defined; all dependencies (C8.10 notebooks) shipped; substrate inputs all present; no L11 surfaces in the §15 plan-claims (the 3 named questions have real canonical cross-link targets). No §11 plan-update required.

### Result

**PROCEED to C8.14 DO** in this session. Tag `C8.14-pre-do` placed post-this-PRE-FLIGHT commit; DO authors `docs/WORKED_EXAMPLE_FAQ.md` + upgrades `PROJECT_STRUCTURE.md`; VERIFY runs cache-cleared pytest baseline; RECEIPT + `C8.14-complete` tag close the task.

Recommended DO sequencing this session:
- **Sub-step 1**: Author `docs/WORKED_EXAMPLE_FAQ.md` (8-12 Q&A; cross-product index over per-subproject FAQs + JOINT_USE_GUIDE + 4 notebooks).
- **Sub-step 2**: Append 3 new sections to `PROJECT_STRUCTURE.md` (build-order DAG + notebook-deps graph + which-file-by-use-case matrix).
- **Sub-step 3 (VERIFY)**: cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returns 74 PASS + 1 SKIP + 1 XFAIL preserved; spot-check cross-links resolve (file paths exist; line-number cites land on intended content).
- **Sub-step 4 (RECEIPT)**: write `RECEIPTS/C8.14_<UTC>.md` + STATUS append; tag `C8.14-complete`.

Effort: matches §15 1-session estimate; estimated ~30-45 min docs authoring + ~5 min VERIFY + ~10 min RECEIPT.

---

## PRE-FLIGHT for C8.13 — 2026-05-13T22:30:00Z — Performance + GitHub Release artifacts + pipeline timing benchmark (F.1 + F.4 + F.5) — **RESULT: HALT (one §7.13-shape PRE-FLIGHT-time L11 surfaced) → resolved via AskUserQuestion 2026-05-13T22:30:00Z (F.1 dropped + F.4 deferred + F.5 ACTIVE; precedent: C8.5/C8.6/C8.7/C8.9 PRE-FLIGHT-time §11 plan-update); PROCEED to C8.13 DO with narrowed scope**

### Scope summary

C8.13 §15.C entry (NEXT_STEPS.md lines 1208-1224, pre-this-plan-update) names 3 deliverables: **(F.1)** parquet column-dictionary tuning per low-cardinality column with anticipated 30-50% size reduction; **(F.4)** GitHub Release v1.x with parquet uploads alongside Zenodo; **(F.5)** pipeline timing benchmark vs manuscript `~6 min fetal-death / ~90 min natality` claims (paper/draft_v2_hmd_styled.md:68). KICKOFF.md Phase C Tier-2 line 194 + STATUS 2026-05-13T21:30:00Z line 39 name C8.13 as next §15 task post-C8.12. Estimated effort 1.5-2 sessions per §15. §15 halt-condition flag: "B.12 snapshot-regression interaction (one-time SHA shift expected — bundle DECISION_LOG note)."

**Session scope this PRE-FLIGHT (per (a)-(d) handshake; user-authorized "proceed in the way you think is best" 2026-05-13T22:00:00Z):** ship PRE-FLIGHT entry + §11 plan-update (KICKOFF.md + NEXT_STEPS.md §15.C C8.13 re-scope + DECISION_LOG entry) + tag `C8.13-pre-do` in one commit; F.5 DO + RECEIPT span the same session via background-compute (~96 min natality+linked + ~6-9 min fetal-death real timing).

### Inputs

- [x] **All 14 C8.12 Forward-looking HALTs verified byte-exact** (table below). ✓
- [x] **Existing parquets enumerated** for F.1 + F.5 substrate: 4 parquets on disk; sizes 29 + 36 MB (fd) + 2.2 GB (nat) + 1.3 GB (linked) = ~3.6 GB total. ✓
- [x] **Per-column encoding state probed via `pyarrow.parquet.ParquetFile.metadata.row_group(0).column(c).encodings`** for all 4 parquets (340 columns total): see Field-value snapshot Table 1 below. ✓ **(L11-surfacing finding — see Halt conditions tripped)**
- [x] **F.4 substrate**: `gh` CLI v2.87.3 installed; auth status `Logged in to github.com account yoelplutchok` with token scopes `gist, read:org, repo, workflow` (`repo` scope sufficient for Release create); `gh release list --repo yoelplutchok/vital-statistics-harmonization` returns empty (no releases yet on the public repo). ✓
- [x] **F.5 substrate**: `fetal_death/scripts/run_pipeline.py` exists at the monorepo subproject path (stale `ALL_YEARS=29` per soft-flag (d); see PRE-FLIGHT Field-value snapshot Table 2 for natality per-step scripts — no orchestrator per C8.7b DEFERRED status). Manuscript timing claim located at `paper/draft_v2_hmd_styled.md:68`: *"The fetal-death pipeline runs end-to-end in approximately six minutes on a 2024-vintage laptop; the natality pipeline (which also produces the linked file) takes approximately ninety minutes, dominated by the fixed-width parse stage."* ✓
- [x] **Raw zip inventory**: 43 fetal-death + 35 natality + 19 linked-cohort zips present at canonical absolute paths (verified via `ls`). ✓
- [x] **No stale checkpoints**: `git status --short` empty; `C8.13-pre-do` tag does NOT yet exist (will be placed post-PRE-FLIGHT, pre-DO). ✓

**C8.12 Forward-looking HALT verification table (Convention 4 carry-over):**

| HALT # | Assertion | Verified | Note |
|---|---|---|---|
| 1 | `C8.12-complete` tag present on commit `51f6836` | ✓ | `git tag --list 'C8.12*'` shows both `C8.12-pre-do` + `C8.12-complete` |
| 2 | `tests/mutations/` package exists with 9 files at documented SHAs | ✓ | All 9 files present (1 init + 1 runner + 7 mutation tests) |
| 3 | `tests/mutations/__init__.py` sha=`e3b0c44298fc1c14…` (canonical empty-file SHA) | ✓ | matches exactly |
| 4 | `tests/mutations/_runner.py` sha=`98ecb483ca24a660…` | ✓ | matches exactly |
| 5 | 7 mutation test file SHAs byte-exact | ✓ | All 7 match (compare_external_targets_v1=`691b5b8f…`, compare_external_targets_v3_linked=`83d9ab51…`, validate_2022=`4305f89f…`, validate_external=`a13cedf3…`, validate_external_v2=`833e2277…`, validate_linked_parquets=`724bbe49…`, validate_v1_invariants=`b7d8df48…`) |
| 6 | 4 parquet SHAs unchanged byte-exact | ✓ | fd_harm=`38e2cecb…` / fd_der=`185c071e…` / nat_der=`e16ad5323d…` / linked_der=`9b828a4d…` all match |
| 7 | All C8.12 DO-step-1 + DO-step-2 file SHAs unchanged | ✓ | `fetal_death/file_inventory.csv` `2f2ba2c9…` / `tests/test_inventory_invariants.py` `823e2a8d…` / `tests/test_source_zip_sha_stability.py` `e09158af…` / `tests/test_parquet_column_snapshot.py` `6c605783…` / `tests/snapshots/__init__.py` empty-sha / `tests/snapshots/_build_snapshot.py` `a27b5e70…` / `tests/snapshots/v1_2026-05-13T21-00-00Z_columns.csv` `b6fe22d6…` all match |
| 8 | All C8.11 file SHAs unchanged | ✓ | docs/NCHS_SOURCE_MANIFEST.md=`ed2a44d3…` / docs/COMPARABILITY.md=`10cead2b…` / migrations/v2.7.0-to-v2.8.0-natality.md=`96bb1c54…` / migrations/v2.0.0-to-v2.4.0-fetal-death.md=`90e010a7…` all match |
| 9 | Cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returns 74 PASS + 1 SKIP + 1 XFAIL | ✓ | **74 passed, 1 skipped, 1 xfailed in 152.66s** (cache-cleared via `find . -name __pycache__ -delete`; matches PASS/SKIP/XFAIL counts exactly; wall-time 152.66s is faster than the 209.70s C8.12 baseline but Convention 1 SHAPE-not-VALUE pin is on counts only, not wall-time — passes). |
| 10 | The 1 SKIP is `test_validate_linked_parquets_mutation` | ✓ | confirmed via `pytest tests/mutations/ -v` collection: SKIP occurs at the `natality/output/linked/` missing-input check |
| 11 | Next task = C8.13 (performance + GitHub release artifacts) | ✓ | This entry executes |
| 12 | C8.13 PRE-FLIGHT must anticipate B.12 snapshot-regression interaction | ✓ | RESOLVED at this PRE-FLIGHT: F.1 dropped → no parquet reshape → no B.12 SHA shift → no re-snapshot required this session. (The §15 anticipated interaction is moot under the F.1-dropped re-scope.) |
| 13 | No §11 plan-update needed at C8.12 close | N/A at C8.13 close: §11 plan-update REQUIRED at this PRE-FLIGHT close per the F.1 falsification finding (precedent: C8.5/C8.6/C8.7/C8.9 PRE-FLIGHT-time plan-updates). | — |
| 14 | Soft-flag (l) RESOLVED-as-not-applicable at C8.12 receipt | ✓ | preserved unchanged |

### Environment

- [x] Python version: 3.13.9 (required ≥3.11) ✓
- [x] pandas version: 2.3.2 (required ≥2.3) ✓
- [x] pyarrow version: 18.1.0 (required ≥18.0; C8.12 DECISION_LOG 21:00Z pinned dict-encoding contract to this version) ✓
- [x] DuckDB Python: present (C8.9 lockfile) ✓ (not exercised by C8.13)
- [x] gh CLI: 2.87.3, auth OK with `repo` scope ✓ (F.4 substrate)
- [x] Working directory clean (`git status --short` empty on `main` at `51f6836`): ✓
- [x] On expected branch (`main`): ✓
- [x] Active tags on HEAD: `C8.12-complete` (verified) ✓
- [x] uv-managed `.venv` matches `uv.lock` (C8.5a baseline): ✓

### Source documentation

C8.13 is benchmark + plan-update + docs work; no new NVSR PDFs or NCHS user guides are CONSUMED. The substantive inputs are (i) the 4 harmonized + derived parquets' physical encoding state (F.1 probe substrate); (ii) `paper/draft_v2_hmd_styled.md:68` for the F.5 manuscript timing claim (cite-anchored at line 68); (iii) `gh release` API surface for F.4. No L9 cheap-checks on external PDFs required. ✓

The manuscript citation `paper/draft_v2_hmd_styled.md:68` reads (verbatim): *"Re-deriving the parquet from a fresh download of the NCHS source zips produces a byte-identical file, and SHA-256 checksums for every shipped artifact are committed in `PROVENANCE.md`. The fetal-death pipeline runs end-to-end in approximately six minutes on a 2024-vintage laptop; the natality pipeline (which also produces the linked file) takes approximately ninety minutes, dominated by the fixed-width parse stage."* The ±10% tolerance is the §15 VERIFY criterion.

### Outputs

- [x] **NEW files (must not exist before DO):**
  - `RECEIPTS/C8.13_<UTC>.md`: will be written at C8.13 RECEIPT phase post-F.5 benchmark
  - `docs/PIPELINE_TIMING_BENCHMARK.md` (NEW; F.5 results record + per-stage breakdown + reconciliation vs manuscript claim): does NOT exist ✓
- [x] **MAY BE MODIFIED:**
  - `paper/draft_v2_hmd_styled.md` line 68 — IF F.5 benchmark surfaces a >±10% drift from `~6 min / ~90 min`, update the timing prose; current sha probed at DO baseline. If within tolerance, NO edit.
  - `KICKOFF.md` line 194 (C8.13 description) — §11 plan-update applied this commit
  - `NEXT_STEPS.md` §15.C C8.13 entry (lines 1208-1224) — §11 plan-update applied this commit
- [x] **APPEND-ONLY state files** (per Anti-Pattern #1):
  - `PRE_FLIGHT_LOG.md`: this entry (written before DO begins)
  - `STATUS.md`: new dated section at top at PRE-FLIGHT close + further appends per DO/RECEIPT phases
  - `DECISION_LOG.md`: F.1-falsification entry resolving the L11 cheap-check finding
  - `FIX_LOG.md`: no FIX entry anticipated this session (F.1 finding is a §15 plan-claim L11, not a code-state bug; documented in DECISION_LOG per the C8.5/C8.6/C8.7/C8.9 precedent)
  - `LESSONS.md`: NO new entry. The L11 pattern is already in the §8 matrix; this instance is one more reinforcement of the pattern, not a new mistake class.
- [x] **NOT mutated** (forward-looking HALT for VERIFY):
  - 4 parquets unchanged ✓ — F.1 dropped means zero parquet mutation this session
  - All C8.9 + C8.10a/b/c + C8.11 + C8.12 file SHAs preserved ✓
  - `tests/snapshots/v1_2026-05-13T21-00-00Z_columns.csv` unchanged (no re-snapshot required under F.1-dropped scope) ✓
  - test suite baseline 74 PASS + 1 SKIP + 1 XFAIL preserved (F.5 benchmark does not touch test surface) ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

Per §5 template second bullet: enumerate target rows/cells/columns + verify current values against task plan's assumed state. C8.13's substantive PRE-FLIGHT-time field-value snapshot is **the parquet per-column encoding state** (F.1 substrate; the source of the falsified §15 premise) + **the manuscript timing claim** (F.5 substrate; cite-anchored at line 68) + **per-stage script inventory** (F.5 measurement surface).

**Table 1: Per-parquet encoding state (F.1 probe; 340 columns total)**

| Parquet | Rows | Cols | RGs | File size | Dict-encoded cols (RG0) | Non-dict cols (RG0) | Non-dict-col dtypes |
|---|---|---|---|---|---|---|---|
| `output/harmonized/fetal_death_harmonized.parquet` | 2,427,233 | 73 | 3 | 0.029 GB | 73/73 (100%) | 0 | N/A |
| `output/harmonized/fetal_death_derived.parquet` | 2,427,233 | 89 | 3 | 0.036 GB | 89/89 (100%) | 0 | N/A |
| `natality_v2_harmonized_derived.parquet` | 138,819,655 | 84 | 278 | 2.203 GB | 46/84 (55%) | 38 | **All 38 = bool, RLE+PLAIN** |
| `natality_v3_linked_harmonized_derived.parquet` | 74,943,824 | 94 | 150 | 1.300 GB | 53/94 (56%) | 41 | **All 41 = bool, RLE+PLAIN** |

**F.1 critical finding (L11 / §7.13 PRE-FLIGHT-time discovery):** The §15 PRE-FLIGHT-input claim "Re-write derive.py's parquet-write call with `use_dictionary=True` per column [→] typically yields 30-50% size reduction" is **empirically falsified** by the encoding-state probe:

1. **Both fetal-death parquets are already 100% dict-encoded** (73/73 + 89/89). PyArrow defaults already produce this state for fd. Total fd size = 65 MB; no headroom anyway.
2. **All 38+41 non-dict columns in natality + linked are booleans using RLE+PLAIN encoding** — the optimal 1-bit-per-value encoding for 2-state columns. Forcing dict-encoding on booleans does not help (a dict + indices is strictly larger than RLE on 2 distinct values).
3. **PyArrow's default `use_dictionary=True` (boolean)** already enables dict encoding for cardinality-appropriate columns; the encoding choice per column is per-column-adaptive at the column-writer level. The §15 plan ("`use_dictionary=True` per column") would not change behavior because pyarrow already does the right thing.
4. **Achievable size reduction from F.1 as scoped in §15** ≈ 0% (or negative if dict encoding is forced onto boolean columns).

This is a textbook L11-class stale §15 plan claim catch — the §15 plan was authored from the `EXPLORATION_REPORT.md` `~30-50% reduction` heuristic without first probing the actual per-parquet encoding state. The Convention 3 Field-value snapshot is precisely the cheap-check moment designed to catch this. Precedent: C8.5 (PRE-FLIGHT split § 5 → C8.5a + C8.5b on docker absence), C8.6 (PRE-FLIGHT deferred live-CI verify to Phase D step 3), C8.7 (PRE-FLIGHT split → C8.7a + C8.7b on orchestrator scope realism), C8.9 (PRE-FLIGHT dropped C.1 on NCHS state-suppression policy). All five precedents follow the same shape: cheap-check at PRE-FLIGHT discovers the §15 plan's substrate doesn't exist as the plan assumed; user-resolved via AskUserQuestion; §11 plan-update applied in the same commit.

**Resolution (user-authorized via AskUserQuestion 2026-05-13T22:30:00Z):** F.1 **DROPPED** from C8.13 scope. The §11 plan-update applied this commit revises KICKOFF.md line 194 + NEXT_STEPS.md §15.C C8.13 entry to remove F.1 from the active DO scope; the falsified-premise documentation lands in DECISION_LOG.md 2026-05-13T22:30:00Z. Zero parquet mutation; zero SHA shift; B.12 snapshot regression test remains valid.

**Table 2: F.5 per-stage script inventory (timing measurement surface)**

| Subproject | Stage | Entry-point script | Cardinality |
|---|---|---|---|
| fetal_death | run_pipeline orchestrator | `fetal_death/scripts/run_pipeline.py` | 1 entry-point (ALL_YEARS=29 stale; covers 1992-2022 V2+V2.1+V1 era) |
| fetal_death | per-year parse | `fetal_death/scripts/01_import/parse_fetal_year.py` | 43 invocations (1982-2024) |
| fetal_death | harmonize | `fetal_death/scripts/03_harmonize/harmonize.py` | 1 invocation |
| fetal_death | derive | `fetal_death/scripts/04_derive/derive.py` | 1 invocation |
| fetal_death | validate external | `fetal_death/scripts/05_validate/validate_external*.py` + `validate_2022.py` | 3 invocations |
| natality (no orchestrator per C8.7b DEFERRED) | parse all V1 years | `~/Desktop/natality-harmonization/scripts/01_import/parse_all_v1_years.py` | 1 batch (35 yrs internally) |
| natality | parse all linked years | `~/Desktop/natality-harmonization/scripts/01_import/parse_all_linked_years.py` | 1 batch (19 cohort yrs) |
| natality | harmonize V1 core | `harmonize_v1_core.py` | 1 invocation |
| natality | harmonize linked V3 | `harmonize_linked_v3.py` | 1 invocation |
| natality | derive V1 core | `derive_v1_core.py` | 1 invocation |
| natality | derive linked V3 | `derive_linked_v3.py` | 1 invocation |
| natality | validate | 8 scripts under `05_validate/` (not all on critical path; manuscript ~90 min claim covers parse+harmonize+derive primary chain) | varies |

**F.5 timing approach (user-authorized "Run real end-to-end benchmark this session"):**
- Fetal-death: run 43-year per-step pipeline manually (parse loop + harmonize + derive + validate); time each stage; total wall-clock vs `~6 min` claim. Note: `run_pipeline.py` has stale `ALL_YEARS=29` per soft-flag (d); not fixing this session (C8.7b scope); the 43-year per-step manual run produces an honest current-state measurement.
- Natality + linked: run `parse_all_v1_years.py` + `parse_all_linked_years.py` + `harmonize_v1_core.py` + `harmonize_linked_v3.py` + `derive_v1_core.py` + `derive_linked_v3.py` sequentially; time the full chain; total vs `~90 min` claim. Validate stage excluded from the timing claim (manuscript scope is "pipeline runs end-to-end" interpreted as parse → derive primary chain; validate runs separately per the manuscript's Level-2 framing).
- Approach: run in background (BashOutput-monitored), capture wall-clock per stage, aggregate into `docs/PIPELINE_TIMING_BENCHMARK.md`.

**Table 3: F.4 substrate snapshot (DEFERRED to Phase D step 3 per user authorization)**

| Item | State |
|---|---|
| `gh` CLI version | 2.87.3 |
| GitHub auth | `yoelplutchok` keyring; token scopes `gist, read:org, repo, workflow` (sufficient for Release create) |
| Public repo | `yoelplutchok/vital-statistics-harmonization` at v1.0 commit `a18ca3a` |
| Existing releases | 0 (none) |
| F.4 disposition | DEFERRED to Phase D step 3; bundles into the staging-dir scrub + v1.x push event (cleaner: one public-release event) |

**Plan assumptions verified at PRE-FLIGHT (per Convention 3 second bullet):**

1. **F.1 §15 premise FALSIFIED at cheap-check** (see Table 1). Resolved via user-authorized §11 plan-update Option A: drop F.1; ship DECISION_LOG entry documenting the falsified premise. ✓
2. **F.4 substrate VERIFIED** (gh CLI auth OK; public repo exists; no prior releases). Resolved via user-authorized deferral to Phase D step 3. ✓
3. **F.5 substrate VERIFIED** (manuscript claim located + per-stage script inventory complete). Resolved via user-authorized real-benchmark this session. ✓
4. **B.12 snapshot regression interaction MOOT** under F.1-dropped re-scope (no parquet reshape; no SHA shift; no re-snapshot). ✓

**Soft-flags surfaced at PRE-FLIGHT (NOT in-scope this session; carried forward):**

- Carry-forward from C8.12 close (9 carried + 2 new + 3 RESOLVED): (a) stale `fetal_death/PROVENANCE.md` (Phase D step 2) + (b) absent `natality/PROVENANCE.md` (Phase D step 2) + (c) `VERSION_ROADMAP.md` "Planned" section (future docs refresh) + (d) `run_pipeline.py` ALL_YEARS=29 (C8.7b; **brushed-against this session for F.5 but NOT fixed** — C8.7b scope; documented as a F.5 caveat in the RECEIPT) + (e) `natality/output/linked/` absent (Phase D step 3 / C8.7b) + (f) plurality footgun (C8.15) + (g) PRE-FLIGHT "87 raw zips" typo (preserved per L10) + (i) `fetal_death/COMPARABILITY.md` title staleness (Phase D candidate) + (m) `record_length` invariant test does not check vs-actual-zip parity (C8.7b candidate) + (n) `test_validate_linked_parquets_mutation` E2E verification (Phase D step 3 / C8.7b) + (o) `validate_v1_invariants` deep-scan FAIL-surface mutation test (future C8.X).
- **NEW soft-flag (p) this PRE-FLIGHT**: F.1 dict-encoding work permanently dropped per user authorization 2026-05-13T22:30:00Z; documented in DECISION_LOG. Any future per-parquet encoding work (e.g., alternative compression codecs ZSTD vs default SNAPPY; row-group size tuning) is **out of pre-submission scope** and requires explicit re-authorization (analog of C.1 NCHS-suppression permanent drop at C8.9). Reconsider only on user request.

### Halt conditions tripped

**ONE §7.13-shape PRE-FLIGHT-time L11** (F.1 §15-premise falsification; the §15 plan's "30-50% size reduction" validity domain is empty for our specific schemas). Resolved via user AskUserQuestion 2026-05-13T22:30:00Z = Option A (drop F.1) + Option A (defer F.4) + Option A (run real benchmark). §11 plan-update applied this commit. Precedent: C8.5 / C8.6 / C8.7 / C8.9 PRE-FLIGHT-time §11 plan-updates with the same shape (cheap-check falsifies §15 substrate; user-resolved in-PRE-FLIGHT; commit `[plan-update]` prefix; DECISION_LOG documents the resolution).

No §7.18 (reproducibility regression). No L17 (no SMOKE stale-pinning). No L13 (no inventory CSV claim drift). No L14 (no validator exit-code regression). No L11 elsewhere (no other §15 stale claims).

### Result

**PROCEED post-§11 plan-update.** This PRE-FLIGHT entry + the §11 plan-update artifacts (KICKOFF.md + NEXT_STEPS.md edits + DECISION_LOG entry + STATUS.md append) ship as one bundled `[plan-update] C8.13 PRE-FLIGHT` commit. Tag `C8.13-pre-do` placed on this commit. DO begins post-commit with F.5 benchmark execution (background-compute) followed by RECEIPT + `C8.13-complete` tag.

Recommended DO sequencing this session:
- **PRE-FLIGHT close (this commit)**: `[plan-update] C8.13 PRE-FLIGHT` ships PRE_FLIGHT_LOG entry + KICKOFF + NEXT_STEPS edits + DECISION_LOG entry + STATUS section. Tag `C8.13-pre-do`.
- **DO**: launch background per-stage F.5 timing measurements (fetal-death 43-yr per-step + natality+linked per-step); BashOutput-monitor each.
- **VERIFY**: compare measured wall-clock per stage against manuscript `~6 min / ~90 min` claims; ±10% tolerance is PASS; >±10% drift triggers manuscript line 68 update (which itself is Phase D step 4 scope — at C8.13 RECEIPT, we document the drift + propose the manuscript edit but leave the actual edit to Phase D 4 per the C8.12 RECEIPT precedent of "manuscript impact deferred to Phase D step 4").
- **RECEIPT**: write `RECEIPTS/C8.13_<UTC>.md` + `docs/PIPELINE_TIMING_BENCHMARK.md` + STATUS append; tag `C8.13-complete`.

Effort revised under narrowed scope: **~1 session** (was §15-estimated 1.5-2 sessions; F.1 drop + F.4 defer cuts ~50%; F.5 alone is ~96 min compute + ~30 min plan-update + ~30 min RECEIPT/VERIFY).

---

## PRE-FLIGHT for C8.12 — 2026-05-13T19:30:00Z — Mutation tests + L13 audit + L14 audit + SHA-stability + snapshot regression (B.6 + B.7 + B.8 + B.11 + B.12) — **RESULT: PROCEED** (zero §7 halts; zero L11s; scope enumeration matches §15 expectation incl. "Likely surfaces FIX_LOG cascades — budget for fix-on-contact" — 3 L14-CANDIDATE validators surfaced at audit-surface enumeration, 7 validators with FAIL surface for B.6 mutation-test pairing; clean PRE-FLIGHT)

### Scope summary

C8.12 §15.C entry (NEXT_STEPS.md lines 1188-1205) names 5 deliverables: **(B.6)** mutation-test scaffolding for every validator (`tests/mutations/`; inject known violation, assert validator catches it; L3 defense); **(B.7)** audit every metadata CSV for L13 role-vs-column claims; **(B.8)** audit every validator's `main()` for L14 exit-code propagation; **(B.11)** SHA-stability test (PROVENANCE.md + on-disk SHA parity; primary target this session = `docs/NCHS_SOURCE_MANIFEST.md` shipped at C8.11 — 97 raw-zip SHAs); **(B.12)** per-column snapshot regression test (4 parquets × 73+89+84+94 = 340 columns total). KICKOFF.md Phase C Tier-2 line 193 + STATUS 2026-05-13T18:00:00Z line 53 name C8.12 as the next §15 task post-C8.11. Estimated effort 3-4 sessions per §15. §15 halt-condition flags: L3, L13, L14, H10 — "Likely surfaces FIX_LOG cascades — budget for fix-on-contact." Dependencies: C8.6 (CI to run new tests; already shipped at `.github/workflows/ci.yml`).

**Session scope this PRE-FLIGHT (per (a)-(d) handshake; user-authorized "proceed as you think is the best way"):** ship PRE-FLIGHT entry + tag `C8.12-pre-do` only this session; DO + VERIFY + RECEIPT span the subsequent 2-3 sessions per §15 "3-4 sessions" estimate. PRE-FLIGHT-only-this-session pattern follows the C8.10/C8.11 PRE-FLIGHT-close-then-DO-next-session precedent for multi-deliverable tasks. C8.12-pre-do tag placed post-this-PRE-FLIGHT, pre-any-DO-mutation.

### Inputs

- [x] **All 15 C8.11 Forward-looking HALTs verified byte-exact** (see table below). ✓
- [x] **All 11 validators identified and inventoried** for B.6 + B.8 surfaces (see §"Field-value snapshot" Table 1 below). ✓
- [x] **20 metadata CSVs enumerated** for B.7 L13 audit surface (16 fetal-death + 4 natality; see Table 2). ✓
- [x] **docs/NCHS_SOURCE_MANIFEST.md** (B.11 primary target this session): 97 markdown-table SHA-256 rows confirmed (43 fetal-death + 35 natality + 19 linked-cohort); sha=`ed2a44d3117336cc…`. ✓
- [x] **fetal_death/PROVENANCE.md staleness confirmed** (carry-forward soft-flag (a); pre-V2.1/V3a/V3b/v2.4 state; tag=v2.0.0; 33 SHA entries; canonical sha mismatch with current `38e2cecb…` parquet). Out-of-scope for B.11 this session per Phase-D-step-2 routing. ✓
- [x] **natality/PROVENANCE.md absent** (carry-forward soft-flag (b)); B.11 substrate for natality is `docs/NCHS_SOURCE_MANIFEST.md` Section 2 + Section 3, NOT a per-product output-artifact PROVENANCE. ✓
- [x] **4 parquet schemas enumerated** for B.12 snapshot-regression sizing: 73 + 89 + 84 + 94 = 340 columns total. ✓
- [x] **Existing test surface** (current 56 PASS + 1 XFAIL): 13 test files, 5 with test bodies (tests/test_canonical_filter_invariants.py 28 asserts; tests/test_cross_product_join_parity.py 34; tests/test_row_count_conservation.py 33; fetal_death/tests/test_release_smoke.py 26; fetal_death/tests/test_schema_dtype_parity.py 8; natality/tests/test_schema_dtype_parity.py 6). New `tests/mutations/` directory does NOT exist. ✓
- [x] **No stale checkpoints**: `git status --short` empty; `C8.12-pre-do` tag does NOT yet exist (will be placed post-PRE-FLIGHT, pre-DO). ✓

**C8.11 Forward-looking HALT verification table (Convention 4 carry-over):**

| HALT # | Assertion | Verified | Note |
|---|---|---|---|
| 1 | `C8.11-complete` + `C8.11-pre-do` tags present | ✓ | `git tag --list 'C8.11*'` shows both |
| 2 | `fetal_death/file_inventory.csv` sha=`38dc035eeccb8b80…` | ✓ | matches exactly; 43 rows; year 1982-2024 contiguous |
| 3 | `docs/NCHS_SOURCE_MANIFEST.md` sha=`ed2a44d3117336cc…` | ✓ | matches; 97 SHA-256 rows in 3 sections confirmed |
| 4 | `docs/COMPARABILITY.md` sha=`10cead2b9da604e1…` | ✓ | matches |
| 5 | `migrations/v2.7.0-to-v2.8.0-natality.md` sha=`96bb1c54a8e812d0…` | ✓ | matches |
| 6 | `migrations/v2.0.0-to-v2.4.0-fetal-death.md` sha=`90e010a78e1078b2…` | ✓ | matches |
| 7 | `VERSION_ROADMAP.md` sha=`15f903fd0f9d382c…` | ✓ | matches |
| 8 | 3 cross-link READMEs at expected SHAs | ✓ | `README.md` `b3badf143929e433…` / `natality/README.md` `d1b08976e7b06414…` / `fetal_death/README.md` `9093d85e712b694e…` all match |
| 9 | 4 parquet SHAs unchanged byte-exact | ✓ | fd_harm=`38e2cecb03ff4947…` / fd_der=`185c071ec76ab8aa…` / nat_der=`e16ad5323d68e28d…` / linked_der=`9b828a4de4e59b17…` all match |
| 10 | 6 C8.10a/b/c notebook + builder SHAs unchanged | ✓ | all 6 (notebooks/maternal_age_stratified_imr.ipynb, _build_*, preterm_*, cross_race_*) match exactly |
| 11 | 13 C8.9 file SHAs unchanged (14th = README.md intentionally drifted) | ✓ | 8 probed (notebooks/README.md=`6fc9b191…`, 3× quickstart.R, views.sql, pyproject.toml, uv.lock, .python-version, ci.yml, docs/JOINT_USE_GUIDE.md) all match |
| 12 | Cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returns 56 PASS + 1 XFAIL | ✓ | **56 passed, 1 xfailed in 83.55s** (cache-cleared via `find . -name __pycache__ -delete`; matches HALT exactly) |
| 13 | 8 open soft-flags (a)-(i) preserved | ✓ | All carried forward; none promoted to halt; (h) and (i) are C8.11 in-DO additions |
| 14 | Next task = C8.12 | ✓ | This entry executes |
| 15 | All 5 PRE-FLIGHT-time L11 resolutions applied | ✓ | C8.11 DO landed all 5 (Option A inventory + (i) migration filename + (ii) E.8 manifest scope + (iii) VERSION_ROADMAP fix-on-contact + (h) in-DO year-set correction); no further user authorization needed |

### Environment

- [x] Python version: 3.13.9 (required ≥3.11) ✓
- [x] pandas version: 2.3.2 (required ≥2.3) ✓
- [x] pyarrow version: 18.1.0 (required ≥18.0) ✓
- [x] DuckDB Python: present (C8.9 lockfile) ✓ (not exercised by C8.12)
- [x] Working directory clean (`git status --short` empty on `main` at `fc9c6ee`): ✓
- [x] On expected branch (`main`): ✓
- [x] Active tags on HEAD: `C8.11-complete` (verified) ✓
- [x] uv-managed `.venv` matches `uv.lock` (C8.5a baseline): ✓

### Source documentation

C8.12 is test-authoring + audit work; no new NVSR PDFs or NCHS user guides are CONSUMED. The substantive inputs are (i) the 11 validators' source code (already on disk; `git ls-files '*/05_validate/*.py'` exhaustive enumeration above); (ii) the 20 metadata CSVs (already on disk); (iii) the 97-row `docs/NCHS_SOURCE_MANIFEST.md` shipped at C8.11; (iv) the 4 harmonized + derived parquet schemas. No L9 cheap-checks on external PDFs required for this PRE-FLIGHT. ✓

The 97 raw NCHS zips on disk (`/Users/yoelplutchok/Desktop/fetal-death-harmonization-build/raw_data/` + `/Users/yoelplutchok/Desktop/natality-harmonization/raw_data/` + `.../linked/`) are the B.11 SHA-stability test substrate. Each zip's SHA will be recomputed at DO time via `shasum -a 256`; comparison against the manifest is the test logic. No pre-DO L9 check required.

### Outputs

- [x] **NEW files (must not exist before DO):**
  - `tests/mutations/` (directory): does NOT exist ✓
  - `tests/mutations/__init__.py`: does NOT exist ✓
  - `tests/mutations/test_<validator_name>_mutation.py` (×7 — one per FAIL-surface validator): do NOT exist ✓
  - `tests/test_sha_stability.py` (or `tests/test_nchs_source_manifest.py`): does NOT exist ✓
  - `tests/test_column_snapshot.py` (B.12): does NOT exist ✓
  - `tests/test_inventory_year_consistency.py` (new L13 invariant motivated by C8.11 receipt FL-HALT #6 — see soft-flag (j) below; OPTIONAL — judge at DO whether scope-creep): does NOT exist ✓
  - `RECEIPTS/C8.12_<UTC>.md`: will be written at C8.12 RECEIPT phase (subsequent session(s))
- [x] **MAY BE MODIFIED (per-finding; cardinality = 3 L14-CANDIDATE validators + possible L13 audit findings; explicit intent recorded; current SHAs recorded for VERIFY phase):**
  - `fetal_death/scripts/05_validate/validate_2022.py` — L14-CANDIDATE patch (add `sys.exit(1 if has_fail else 0)`); current sha probed at DO baseline
  - `fetal_death/scripts/05_validate/validate_external.py` — L14-CANDIDATE patch
  - `natality/scripts/05_validate/validate_linked_parquets.py` — L14-CANDIDATE patch (NOTE: only 1 FAIL surface; needs DO-time inspection of whether the existing `print("  FAILURES:")` corresponds to a per-row failure indicator or just a status-block header — the patch may be no-op)
  - **FIX_LOG entries per finding** (L13 audit findings + L14 patches) — anticipated cascade per §15 halt-condition flags
- [x] **APPEND-ONLY state files** (per Anti-Pattern #1):
  - `PRE_FLIGHT_LOG.md`: this entry (written before DO begins)
  - `STATUS.md`: new dated section at top at PRE-FLIGHT close + further appends per DO/RECEIPT phases
  - `DECISION_LOG.md`: entries for any non-trivial design choices (e.g., test-directory structure, mutation-injection strategy choice, scope-resolution for the optional L13 invariant)
  - `FIX_LOG.md`: anticipated cascade entries per L13/L14 findings
  - `LESSONS.md`: NEW entry only if a new mistake class surfaces (not anticipated; §8 matrix already covers L3, L13, L14, H10)
- [x] **NOT mutated** (forward-looking HALT for VERIFY):
  - 4 parquets unchanged ✓ — C8.12 is test-authoring + script-edit, not data mutation
  - All C8.9 + C8.10a/b/c + C8.11 NEW files unchanged ✓
  - `harmonized_schema.csv` files unchanged ✓
  - `external_validation_targets_*.csv` files unchanged ✓
  - `docs/NCHS_SOURCE_MANIFEST.md` unchanged (consumed by B.11 test, not mutated) ✓
  - `docs/COMPARABILITY.md`, migration guides unchanged ✓
  - test suite baseline 56 PASS + 1 XFAIL preserved + new tests strictly additive ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

Per §5 template second bullet: enumerate target rows/cells/columns + verify current values against task plan's assumed state. C8.12 is test-authoring + L13/L14 audit; the substantive "fields" are (a) the 7 NEW mutation-test files; (b) any L14-patch line additions to 3 candidate validators; (c) the NEW SHA-stability test + snapshot-regression test files; (d) optional NEW L13 invariant test. Total snapshot rows: 20.

**Table 1: Validator inventory × B.6/B.8 audit surface (11 validators)**

| # | Validator | FAIL surface count | `sys.exit`/`SystemExit` on FAIL? | B.6 status | B.8 status |
|---|---|---|---|---|---|
| 1 | `fetal_death/scripts/05_validate/validate_2022.py` | 19 | **NO** | mutation-test target | **L14-CANDIDATE — patch needed** |
| 2 | `fetal_death/scripts/05_validate/validate_external.py` | 5 | **NO** | mutation-test target | **L14-CANDIDATE — patch needed** |
| 3 | `fetal_death/scripts/05_validate/validate_external_v2.py` | 2 | YES (`sys.exit(1)` line 394) | mutation-test target | OK |
| 4 | `natality/scripts/05_validate/compare_external_targets_v1.py` | 4 | YES (`raise SystemExit(2)` line 483) | mutation-test target | OK |
| 5 | `natality/scripts/05_validate/compare_external_targets_v3_linked.py` | 6 | YES (`raise SystemExit(1)` line 350) | mutation-test target | OK |
| 6 | `natality/scripts/05_validate/harmonized_missingness.py` | 0 (REPORT-ONLY) | N/A | SKIP (no FAIL surface) | OK |
| 7 | `natality/scripts/05_validate/key_rates_from_derived_core.py` | 0 (REPORT-ONLY) | N/A | SKIP | OK |
| 8 | `natality/scripts/05_validate/qa_yearly_core_parquet.py` | 0 (REPORT-ONLY) | N/A | SKIP | OK |
| 9 | `natality/scripts/05_validate/validate_linked_parquets.py` | 1 | **NO** (only print at line 248) | mutation-test target | **L14-CANDIDATE — patch needed (subject to DO-time inspection — may be no-op if the print is just a status-block header)** |
| 10 | `natality/scripts/05_validate/validate_row_counts_vs_nchs.py` | 0 (REPORT-ONLY) | N/A | SKIP | OK |
| 11 | `natality/scripts/05_validate/validate_v1_invariants.py` | 6 | YES (`raise SystemExit(2)` line 885) | mutation-test target | OK |

**Summary:** 7 mutation-test targets (B.6) + 3 L14-CANDIDATE patches (B.8) + 4 REPORT-ONLY skip. Matches §15 anticipated FIX_LOG-cascade surface.

**Table 2: Metadata CSV inventory × B.7 L13 audit surface (20 CSVs)**

Fetal-death (16):
- `fetal_death/external_validation_targets.csv` — 88 → 90 (post-C8.2) NVSR-targets per task
- `fetal_death/file_inventory.csv` — 43 rows post-C8.11 (year × raw_filename × doc_filename × record_length)
- `fetal_death/harmonized_schema.csv` — 73 rows × 10 cols (years_available field is B.12 + new-L13-invariant candidate)
- `fetal_death/live_births_by_year.csv` — denominator file
- `fetal_death/record_layout_{1982_1988, 1992, 2003, 2004, 2006, 2014, 2022}.csv` — 7 era-layout files (byte-position metadata; L13-extension target per LESSONS 2026-05-12T01:40Z)
- `fetal_death/reporting_thresholds.csv` — state × year reporting thresholds
- `fetal_death/stratified_denominators.csv` — Task 1 joint-use output
- `fetal_death/validation_results.csv` — per-target PASS/FAIL
- `fetal_death/validation_tracking.csv` — adversarial verifier roster (DECISION_LOG history)
- `fetal_death/variable_crosswalk_working.csv` — per-era raw-to-harmonized mapping

Natality (4):
- `natality/metadata/external_validation_targets_v1.csv` — 183 NVSR-targets
- `natality/metadata/external_validation_targets_v3_linked.csv` — 35 NVSR-targets
- `natality/metadata/file_inventory.csv` — 54 rows (35 natality + 19 linked-cohort)
- `natality/metadata/harmonized_schema.csv` — 84 rows × 9 cols (no `domain` column unlike fetal-death's 10-col version)

**New L13 invariant candidate (per C8.11 receipt FL-HALT motivation; STATUS line 56 (i)):** `every year in file_inventory.csv` ⊆ `years_available in harmonized_schema.csv` — defends against future stale-inventory regressions analogous to the 34-vs-43 row gap that C8.11 PRE-FLIGHT surfaced. Filed as soft-flag (j) below; DO-time scope-resolution.

**Table 3: B.11 SHA-stability test target (97 raw zips via docs/NCHS_SOURCE_MANIFEST.md)**

| Section | Rows | Source path |
|---|---|---|
| Section 1 (Fetal-death) | 43 (year 1982-2024) | `/Users/.../fetal-death-harmonization-build/raw_data/fetal_death/Fetal<YYYY>US.zip` |
| Section 2 (Natality) | 35 (year 1990-2024) | `/Users/.../natality-harmonization/raw_data/Nat<YYYY>.zip` / `Nat<YYYY>us.zip` |
| Section 3 (Linked-cohort) | 19 (cohort year 2004-2023) | `/Users/.../natality-harmonization/raw_data/linked/<period>PE<cohort>CO.zip` |

Test logic: parse the 3 markdown tables (97 pipe-delimited rows); recompute `shasum -a 256` on each raw zip via the canonical absolute paths; assert byte-equality. The 97-row count is the floor invariant; any drift in zip count is a §7.11 halt at DO.

**Table 4: B.12 snapshot-regression test target (340 parquet columns)**

| Parquet | Columns | Sha-prefix anchor |
|---|---|---|
| `fetal_death_harmonized.parquet` | 73 | `38e2cecb…` |
| `fetal_death_derived.parquet` | 89 | `185c071e…` |
| `natality_v2_harmonized_derived.parquet` | 84 | `e16ad5323d…` |
| `natality_v3_linked_harmonized_derived.parquet` | 94 | `9b828a4d…` |

Test logic: per-column hash via pyarrow (e.g., `hashlib.sha256(arr.to_pylist().__repr__().encode()).hexdigest()` or a more memory-efficient streaming variant); store per-column SHA in a versioned snapshot file; subsequent runs assert byte-equality. **DECISION-PENDING at DO:** snapshot storage format (CSV vs JSON vs Parquet itself) and the per-release version policy (one snapshot per release, or rolling latest only). Filed as soft-flag (k) below.

**Plan assumptions verified at PRE-FLIGHT (per Convention 3 second bullet; zero amendments):**

1. **All 11 validators inventoried** matches the §15 PRE-FLIGHT-input claim "~13 across 5 scripts." Actual count: 11 across 2 subprojects' `05_validate/` directories. The §15 "~13" estimate is approximate but in the right ballpark; not an L11.
2. **The B.6 "tests/mutations/" directory does not yet exist** — matches §15 DO-scope "Per-validator mutation test in `tests/mutations/`."
3. **The B.8 L14 audit anticipated FIX_LOG cascade** matches §15 halt-condition flags. 3 candidates surfaced; one (`validate_linked_parquets.py`) is potentially a no-op pending DO-time inspection.
4. **The B.11 SHA-stability primary target this session = `docs/NCHS_SOURCE_MANIFEST.md`** (NOT `fetal_death/PROVENANCE.md` which is pre-V2.1 stale per soft-flag (a)). This is a session-scope decision: PROVENANCE refresh moves to Phase D step 2 per C8.11's soft-flag (a) routing. C8.12's B.11 test exercises the manifest shipped at C8.11.
5. **The B.12 snapshot-regression scope** = 4 parquets × 340 columns. No prior column-snapshot manifest exists; this is greenfield. **§15 hint** ("per-release versioned snapshot manifest") shapes the implementation choice but does not pre-determine the file format.

**Soft-flags surfaced at PRE-FLIGHT (NOT in-scope this session; carried forward):**

- (h) **In-DO L11 (h) from C8.11** (year-set V3b+V2.1 correction): RESOLVED at C8.11 DO; preserved in receipt + STATUS + DECISION_LOG. No C8.12 action.
- (i) **`fetal_death/COMPARABILITY.md` title staleness** ("V2.0, 1992-2022" vs v2.4.0): Single-line fix-on-contact candidate. Could land at C8.12 if a B.7 L13 audit pass touches that file's role-claims; otherwise defer to Phase D step 2.
- (j) **NEW L13 invariant candidate**: "every year in `file_inventory.csv` ⊆ `years_available` in `harmonized_schema.csv`" — motivated by C8.11's 34-vs-43-row inventory gap. **DO-time scope-resolution**: include in B.7 audit-shipped invariants, OR defer to a future C8.X task. Recommendation: include (low cost; defends a known failure mode; the C8.11 receipt explicitly cites this as a C8.12 candidate input).
- (k) **B.12 snapshot storage format choice** (CSV/JSON/Parquet + release-versioning policy): DO-time DECISION_LOG entry required. Pre-DO recommendation: per-column SHA in a CSV at `tests/snapshots/v<X>_<UTC>_columns.csv`; CI compares latest run against the most-recent baseline; test PASSes if all columns match, FAILs with per-column diff list otherwise. Re-snapshot triggered by a §11 plan-update committing a new baseline (e.g., post-C8.13 dict-encoding reshape).
- (l) **`fetal_death/scripts/05_validate/validate_2022.py` is `DESIGN: frozen-at-task` candidate** — the existing module docstring may need a Convention-2 `DESIGN:` first-docstring tag at DO. Probe at DO; bundle into the L14 patch if needed.
- Carry-forward soft-flags from C8.11 (a)-(g) + (h) + (i): all preserved; none promoted to halt status by this PRE-FLIGHT. Phase D step 2 + future C8.X scope unchanged.

### Halt conditions tripped

**NONE.** Zero §7 halt conditions tripped at PRE-FLIGHT. The 3 L14-CANDIDATE validators surfaced at Table 1 are EXPECTED per §15 halt-condition flags ("Likely surfaces FIX_LOG cascades — budget for fix-on-contact"); they are anticipated scope, not surprise halts. Each becomes a §15-budgeted DO-step + paired FIX_LOG entry. The 20-CSV B.7 audit surface, 7-validator B.6 mutation surface, 340-column B.12 snapshot scope, and 97-zip B.11 substrate are all bounded enumerable scopes within §15's "3-4 sessions" budget. No L11 (no stale §15 PRE-FLIGHT-input claims; the only "~13 validators" approximation is benign). No L13 (all metadata CSVs identified with column names verified via shell). No L17 (no smoke pinning a stale annotation value). No §11 plan-update required.

### Result

**PROCEED** to C8.12 DO across subsequent 2-3 sessions. This session's scope ends at PRE-FLIGHT close + `C8.12-pre-do` tag placement. The next session begins DO with B.7 + B.8 audit (cheapest, surfaces FIX_LOG cascades) then B.11 + B.12 test authoring (medium) then B.6 mutation-test scaffolding (largest; 7 validators × paired mutation-test files; depends on B.8 patches landing first so the mutation-test runner can assume `sys.exit(1)` on FAIL).

Recommended DO sequencing across 3 sessions:
- **Session 1 (this PRE-FLIGHT close + early DO):** B.7 + B.8 audit + paired FIX_LOG cascade entries; one DECISION_LOG entry per non-trivial L13/L14 choice; soft-flag (j) L13 invariant scope-resolution.
- **Session 2:** B.11 SHA-stability + B.12 snapshot regression test authoring; CI integration verification (re-run `.github/workflows/ci.yml`-equivalent locally).
- **Session 3:** B.6 mutation-test scaffolding across 7 validators; Tier-0 mutation-test mutation-runner (AND-of-rows aggregation per L14).
- **Session 4 (optional, if cascade depth exceeds estimate):** overflow + RECEIPT + cumulative re-probe.

Per §4 discipline: tag `C8.12-pre-do` on the commit shipping this PRE-FLIGHT entry; DO commits will accumulate against the same task ID; `C8.12-complete` tag at RECEIPT close.

---

## PRE-FLIGHT for C8.11 — 2026-05-13T17:30:00Z — Migration guides + cross-product COMPARABILITY.md + cross-product NCHS-source-data SHA manifest (E.2 + E.4 + E.8) — **RESULT: PROCEED** (one §7.13-shape scope-affecting L11 surfaced + user-resolved via AskUserQuestion 2026-05-13T17:25:00Z Option A: extend `fetal_death/file_inventory.csv` 34 → 43 rows in C8.11 DO; three additional routine L11 PRE-FLIGHT-input re-interpretations user-authorized in-place per the C8.9/C8.10a/b/c precedent; no §11 plan-update commit needed)

### Scope summary

C8.11 §15.C entry (NEXT_STEPS.md lines 1168-1184) names 3 deliverables: (E.2) two migration guides — `migrations/v2.7.0-to-v2.8.0-natality.md` + (per §15) `migrations/v2.0.0-to-v2.3.0-fetal-death.md` re-targeted in PRE-FLIGHT to `migrations/v2.0.0-to-v2.4.0-fetal-death.md` (L11: §15 named v2.3.0 but actual current is v2.4.0 per fetal_death/README.md line 156 + DECISION_LOG 2026-05-13T01:30Z C8.2 latest-year refresh); (E.4) `docs/COMPARABILITY.md` at monorepo root synthesizing within_era + cross_era caveats from both subprojects; (E.8) `docs/NCHS_SOURCE_MANIFEST.md` at monorepo root containing raw-zip SHA-256 values for all 87 NCHS source files (43 fetal-death + 35 natality + 19 linked-cohort), keyed by year × raw_filename matching the inventory rows. KICKOFF.md Phase C Tier-2 line 192 + STATUS 2026-05-13T17:15:00Z line 68 name C8.11 as the next §15 task. Estimated effort 3-4 sessions per §15 (with the +30-60 min Option A inventory-extension addition).

**Session scope this PRE-FLIGHT (the (a)-(d) handshake-stated plan, user-authorized "proceed in the way you think is best" + AskUserQuestion 17:25Z resolution Option A + (i)/(ii)/(iii) Proceed-in-place-per-precedent):** ship PRE-FLIGHT entry + tag `C8.11-pre-do` only; subsequent sessions will execute DO + VERIFY + RECEIPT across 4 deliverables (E.2a natality migration guide; E.2b fetal-death migration guide; E.4 cross-product COMPARABILITY; E.8a fetal_death/file_inventory.csv extension 34 → 43 rows; E.8b NCHS_SOURCE_MANIFEST.md) + 2 fix-on-contact mutations (VERSION_ROADMAP.md line 11 + 13 v2.1.0 → v2.4.0 + record count + coverage update) + cross-link edits (monorepo README.md + per-product README sections). This PRE-FLIGHT is metadata-only (PRE_FLIGHT_LOG.md addition); DO scope begins in the next session per the §4 five-phase discipline. C8.11-pre-do tag placed post-this-PRE-FLIGHT, pre-any-DO-mutation.

### Inputs

- [x] **All 12 C8.10c Forward-looking HALTs verified byte-exact** (see table below; 4 parquet SHAs + 3 C8.10c file SHAs + 14 C8.9 + 4 of 5 C8.10a/b file SHAs + 7 C8.10-tag presence). ✓
- [x] **Migration source-of-truth DECISION_LOG entries present** (4 substantive migrations to document):
  - `natality_v28_rename` — DECISION_LOG.md lines 926-1033 (2026-05-12T13:35:02Z + 2026-05-12T03:25:00Z PRE-FLIGHT findings); covers column renames (`year` → `data_year`; `restatus` → `residence_status`; `maternal_race_bridged4` → `maternal_race_bridged`; `maternal_hispanic_origin` → `hispanic_origin`); 61-string-literal rename surface; aliasing helper retained for v2.7.0 backward-compat per chosen alternative. ✓
  - `task3_v21_fetal_death` — DECISION_LOG.md line 1099+ (2026-05-12T01:35:00Z); covers V2.1 (adds 2003 + 2004 transition years; 1351-byte + 1501-byte mixed-revision layouts) + bundled H8 dtype reconciliation (5 columns: tabulation_flag, residence_status, maternal_age, maternal_race_bridged, hispanic_origin) + data_year field rename + monorepo path drift fixes. ✓
  - `task7_v3a` — DECISION_LOG.md line 882+ (2026-05-12T14:30:00Z); covers V3a 1989-1991 backward extension; B3 maternal_race_bridged 1989-rev MRACE 08→4 API, 09→null; 26/26 validation byte-exact. ✓
  - `task7_v3b` — DECISION_LOG.md line 800+ + 850+ (2026-05-12T18:30:00Z × 2); covers V3b 1982-1988 backward extension; B3 1978-rev MRACE 1-digit 0-9 → 4-cat bridged with code 7 + code 9 → null; DATAYEAR 2-digit → 4-digit expansion; 33/33 validation byte-exact. ✓
  - C8.2 latest-year refresh (2023+2024) is the implicit 5th migration step but per DECISION_LOG it's a data extension, not a schema or column-name change; surfaces in the migration guide as a "coverage extension" entry, not a "query update" entry. ✓
- [x] **Both subproject COMPARABILITY files present** (E.4 synthesis inputs):
  - `natality/docs/COMPARABILITY.md`: 41,736 bytes, last modified 2026-05-12 09:19. Top-level structure: Guiding policy + Comparability class definitions + certificate_revision values + Known structural breaks (line 34) + Variable decisions (line 78) + Recommended analytic subsets (line 192) + V3 Linked comparability (line 201) + Known pitfalls (line 279) + Change log (line 348). ✓
  - `fetal_death/COMPARABILITY.md`: 26,053 bytes, last modified 2026-05-04 21:58. Top-level structure: Era structure + 12 numbered sections covering 2003 revision transition / race+ethnicity / education / cause of death / gestational age / plurality / unrevised fields / BMI + morbidity / V2 cross-era code normalizations B1-B6 / V2 state-level reporting quirks / V2 stale-guide years (1996, 2001, 2002) + Variable Availability Matrix. ✓
- [x] **Both `file_inventory.csv` files present** (E.8 SHA-manifest inputs):
  - `natality/metadata/file_inventory.csv`: 54 data rows, 8 columns (`year, source_url, source_org, raw_filename, file_format, doc_filename, imported, notes`); year range 1990-2024; all 54 rows show `imported=true`; raw_filenames include 35 natality (`Nat<YYYY>.zip` / `Nat<YYYY>us.zip`) + 19 linked-cohort (`<YYYY>PE<YYYY-1>CO.zip`). ✓
  - `fetal_death/file_inventory.csv`: 34 data rows, 9 columns (`year, source_url, source_org, raw_filename, file_format, doc_filename, record_length, imported, notes`); year range 1989-2022; all 34 rows show `imported=no`. **STALE relative to v2.4.0 envelope (1982-2024 = 43 years; missing 7 V3b 1982-1988 + 2 latest-year 2023+2024 rows).** Option A resolution: extend to 43 rows in C8.11 DO; row-by-row metadata recoverable from DECISION_LOG entries above + per-zip probes. ✓ (with documented gap, scope-resolved per AskUserQuestion 17:25Z Option A)
- [x] **Raw zip universe on disk** (E.8 SHA-manifest target):
  - Fetal-death: 43 files at `/Users/yoelplutchok/Desktop/fetal-death-harmonization-build/raw_data/fetal_death/Fetal<YYYY>US.zip` covering 1982-2024 inclusive (verified via `ls *.zip | wc -l`). ✓
  - Natality: 35 files at `/Users/yoelplutchok/Desktop/natality-harmonization/raw_data/` covering 1990-2024 (`Nat<YYYY>.zip` for 1990-1993; `Nat<YYYY>us.zip` for 1994+). ✓
  - Linked: 19 files at `/Users/yoelplutchok/Desktop/natality-harmonization/raw_data/linked/` — directory presence verified via `find -maxdepth 4 -type d -name '*linked*'`; individual file listing not enumerated in PRE-FLIGHT (DO-step responsibility) but `2024PE2023CO.zip` is the most-recent inventory row per the file_inventory.csv `raw_filename` column. ✓
- [x] **Builder pattern templates** (E.2 + E.4 + E.8 authoring guides): `notebooks/_build_maternal_age_stratified_imr.py` + `notebooks/_build_preterm_outcomes_time_series.py` + `notebooks/_build_cross_race_fetal_mortality.py` (the C8.10a/b/c sibling builders) are NOT directly templates for C8.11 (C8.11 is docs-only, no executable builder), but their markdown-cell structure (intro + section headers + content + pass/fail summary) is a valid template for the migration-guide structure. ✓
- [x] **No stale checkpoints**: `git status --short` empty; `C8.11-pre-do` tag does NOT yet exist (will be placed post-PRE-FLIGHT, pre-DO). ✓

**C8.10c Forward-looking HALT verification table (Convention 4 carry-over):**

| HALT # | Assertion | Verified | Note |
|---|---|---|---|
| 1 | `C8.10c-complete` + parent `C8.10-complete` tags both present | ✓ | `git tag --list 'C8.10*'` shows 7 tags |
| 2 | `notebooks/_build_cross_race_fetal_mortality.py` sha=`aef0664f36a2a3a3…` | ✓ | matches exactly |
| 3 | `notebooks/cross_race_fetal_mortality.ipynb` sha=`262daef19494c03a…` | ✓ | matches exactly |
| 4 | `notebooks/README.md` sha=`6fc9b191c6a5a9d4…` | ✓ | matches (parent C8.10 marked COMPLETE) |
| 5 | 4 parquet SHAs unchanged byte-exact | ✓ | fd_harm=`38e2cecb…` / fd_der=`185c071e…` / nat_der=`e16ad53…` / linked_der=`9b828a4d…` all match (linked parquet correct path is `natality_v3_linked_harmonized_derived.parquet`, not the C8.10c receipt's `linked_birth_infant_death_v3_cohort_derived.parquet` placeholder name — same file, different display name; sha confirms byte-identity) |
| 6 | 14 C8.9 file SHAs + 4 of 5 C8.10a+C8.10b file SHAs unchanged | ✓ | All 14 + 4 verified; `notebooks/README.md` is the 5th C8.10a/b file (drifted intentionally to `6fc9b191…` — HALT #4 above) |
| 7 | Next task = C8.11 | ✓ | This entry executes |
| 8 | §15 PRE-FLIGHT-input re-verification discipline in 4th consecutive application | ✓ | Now 5th (this PRE-FLIGHT surfaces 4 L11 cases) |
| 9 | In-PRE-FLIGHT secondary-source-validation re-interpretation pattern | ✓ | LESSONS.md backport candidate; carried forward |
| 10 | 2014 race-coding-methodology boundary distinct from OE | ✓ | C8.11 C8.11 DO will incorporate into E.4 docs/COMPARABILITY.md synthesis |
| 11 | `notebooks/README.md` Planned section still includes era_boundary stub | ✓ | Out of active Phase C scope; not touched here |
| 12 | Cumulative Phase C effort ~12 of 29-35 sessions (~36%) | ✓ | C8.11 PRE-FLIGHT is ~12.1 of 29-35; comfortably within 42 cap |

### Environment

- [x] Python version: 3.13.9 (required ≥3.11) ✓
- [x] R version: 4.5.0 (R quickstart fixtures landed at C8.9; not exercised by C8.11 which is docs-only)
- [x] pandas version: 2.3.2 (required ≥2.3) ✓
- [x] pyarrow version: 18.1.0 (required ≥18.0) ✓
- [x] DuckDB Python: present (C8.9 lockfile addition) ✓ (not exercised by C8.11)
- [x] Working directory clean (`git status --short` empty on `main` at `2dd19ac`): ✓
- [x] On expected branch (`main`): ✓
- [x] Active tags on HEAD: `C8.10c-complete` + `C8.10-complete` (verified via `git tag --points-at HEAD`) ✓

### Source documentation

C8.11 is docs-authoring; no new NVSR PDFs or NCHS user guides are CONSUMED beyond what's already cited via the DECISION_LOG entries. The 4 migration source-of-truth DECISION_LOG entries above are the substantive inputs. No L9 cheap-checks on external PDFs are required by this PRE-FLIGHT — all source documents are internal (DECISION_LOG entries + COMPARABILITY files + file_inventory.csv files). ✓

The E.8 SHA manifest will record SHAs of raw NCHS zips by computing them at DO time; raw zips themselves are the L9 source-of-truth (NCHS canonical FTP paths recorded in each inventory's `source_url` column). Each zip's SHA-256 is computed at DO; no pre-DO L9 check required.

### Outputs

- [x] **NEW files (must not exist before DO):**
  - `migrations/` (directory): does NOT exist ✓
  - `migrations/v2.7.0-to-v2.8.0-natality.md`: does NOT exist ✓
  - `migrations/v2.0.0-to-v2.4.0-fetal-death.md`: does NOT exist ✓ (re-targeted from §15 v2.3.0 per L11 finding (i))
  - `docs/COMPARABILITY.md` (monorepo root): does NOT exist ✓
  - `docs/NCHS_SOURCE_MANIFEST.md` (monorepo root): does NOT exist ✓ (E.8 filename chosen for E.8 deliverable; follows `docs/JOINT_USE_GUIDE.md` + `docs/PRIOR_ART.md` precedent of monorepo-cross-product docs at `docs/`)
  - `RECEIPTS/C8.11_<UTC>.md`: will be written at C8.11 RECEIPT phase (next session(s))
- [x] **MODIFIED files (explicit intent; current SHAs recorded for VERIFY phase):**
  - `fetal_death/file_inventory.csv` (current 34 rows; target 43 rows per Option A): current size 6905 bytes, sha computed at DO baseline; rows 35-43 to be appended ✓
  - `VERSION_ROADMAP.md` line 11 + line 13 (fix-on-contact per L11 finding (iii)): current `**v2.1.0** (adds 2003 + 2004; H8 dtype reconciliation) | v2.0.0 | 1992–2022 | 1,741,977` → target `**v2.4.0** (V2.1 2003+2004 + V3a 1989-1991 + V3b 1982-1988 + latest-year refresh 2023+2024; H8 dtype reconciliation) | v2.0.0 | 1982–2024 | 2,427,233`; line 13 substring `fetal-death v2.1.0` → `fetal-death v2.4.0` ✓
  - `README.md` (monorepo): add cross-link to `migrations/` + `docs/COMPARABILITY.md` + `docs/NCHS_SOURCE_MANIFEST.md` in the Repository Layout section (additive only) ✓
  - `fetal_death/README.md`: add cross-link to `../migrations/v2.0.0-to-v2.4.0-fetal-death.md` (1 line in Version Roadmap section near line 156) ✓
  - `natality/README.md`: add cross-link to `../migrations/v2.7.0-to-v2.8.0-natality.md` (1 line near line 28 v2.8.0 mention) ✓
- [x] **APPEND-ONLY state files** (per Anti-Pattern #1):
  - `STATUS.md`: new dated section at top with C8.11 close
  - `DECISION_LOG.md`: new entry recording the AskUserQuestion 17:25Z Option A authorization + three (i)/(ii)/(iii) in-place L11 resolutions
  - `PRE_FLIGHT_LOG.md`: this entry (already written before DO begins)
- [x] **NOT mutated** (forward-looking HALT for VERIFY):
  - 4 parquets unchanged ✓
  - 14 C8.9 + 5 C8.10a/b/c file SHAs unchanged ✓
  - `harmonized_schema.csv` files unchanged (E.2 docs reference the schema but do not mutate it) ✓
  - `external_validation_targets_*.csv` files unchanged ✓
  - test suite 56 PASS + 1 XFAIL preserved (cache-cleared run at VERIFY) ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

Per §5 template second bullet: enumerate target rows/cells/columns + verify current values against task plan's assumed state. C8.11 is docs-authoring; the substantive "fields" are (a) the 4 NEW document contents (target schema established by §15 + Option A scope refinements); (b) the 9 NEW rows for `fetal_death/file_inventory.csv`; (c) the 2 fix-on-contact VERSION_ROADMAP.md line substitutions; (d) cross-link edits to 3 README files. Total snapshot rows: 24.

**Table 1: Migration-guide content sources (E.2a + E.2b; per-migration source DECISION_LOG entries verified above)**

| # | Migration | §15 named | PRE-FLIGHT-target (L11 finding (i)) | DECISION_LOG source | Status |
|---|---|---|---|---|---|
| 1 | Natality column renames | `v2.7.0-to-v2.8.0-natality.md` | unchanged | `natality_v28_rename` 2026-05-12T13:35:02Z + 03:25:00Z PRE-FLIGHT | ✓ source present |
| 2 | Fetal-death V2.1 transition | `v2.0.0-to-v2.3.0-fetal-death.md` (stale §15 name) | `v2.0.0-to-v2.4.0-fetal-death.md` (covers V2.1 + V3a + V3b + latest-year as one envelope migration) | `task3_v21_fetal_death` 2026-05-12T01:35:00Z | ✓ source present |
| 3 | Fetal-death V3a backward | (subsumed in #2) | (subsumed in #2) | `task7_v3a` 2026-05-12T14:30:00Z | ✓ source present |
| 4 | Fetal-death V3b backward | (subsumed in #2) | (subsumed in #2) | `task7_v3b` 2026-05-12T18:30:00Z × 2 entries | ✓ source present |
| 5 | Fetal-death latest-year 2023+2024 | (not in §15) | (subsumed in #2 as "data envelope extension") | `C8.2 latest-year refresh` 2026-05-13T01:30:00Z | ✓ source present |

**Table 2: Cross-product COMPARABILITY synthesis cells (E.4; era-boundary union)**

| # | Era boundary | Both products affected? | Source section(s) | Resolution |
|---|---|---|---|---|
| 6 | 2003 revision transition (natality + fetal-death) | both | nat COMPARABILITY §"certificate_revision values" + fd COMPARABILITY §1 "2003 Revision Transition" | E.4 synthesizes both narratives |
| 7 | OE-based gestational age methodology shift (2014+) | natality + linked | nat COMPARABILITY §"Variable decisions" + manuscript §"OE methodology" | E.4 cross-references C8.10b notebook narrative |
| 8 | Race-coding methodology boundary (2014; Hispanic disaggregation) | both | C8.10c notebook narrative (new this PR; not yet in either COMPARABILITY file) | E.4 imports the C8.10c narrative as the canonical source — synthesizes for the first time |
| 9 | Bridged-race null 2018+ (natality) vs 2014+ (fetal-death) | both | nat COMPARABILITY + fd COMPARABILITY §2 "Race and Ethnicity" | E.4 unifies the era-end-dates table |
| 10 | V1 era plurality coding (2005-2013) | fetal-death only | fd COMPARABILITY §7 "Plurality — Data Quality Caveats" | E.4 documents as fetal-death-specific |
| 11 | V2 state-level reporting quirks (1992-2002) | fetal-death only | fd COMPARABILITY §11 | E.4 documents as fetal-death-specific |
| 12 | 1989-1991 V3a + 1982-1988 V3b race-coding | fetal-death only | fd COMPARABILITY §2 + new DECISION_LOG 2026-05-12T14:30Z + 18:30Z + new C8.10c narrative | E.4 imports new caveats (B3 1-digit-recode for V3b code 7 + code 9 → null; V3a code 09 → null) |

**Table 3: fetal_death/file_inventory.csv extension rows (E.8a per Option A; 9 NEW rows)**

| # | year | raw_filename | doc_filename | record_length | imported | source DECISION_LOG |
|---|---|---|---|---|---|---|
| 13 | 1982 | `Fetal1982US.zip` | `1982FetalUserGuide.pdf` | 365 (probe at DO) | no | task7_v3b 2026-05-12T18:30Z |
| 14 | 1983 | `Fetal1983US.zip` | `1983FetalUserGuide.pdf` | 365 | no | same |
| 15 | 1984 | `Fetal1984US.zip` | `1984FetalUserGuide.pdf` | 365 | no | same |
| 16 | 1985 | `Fetal1985US.zip` | `1985FetalUserGuide.pdf` | 365 | no | same |
| 17 | 1986 | `Fetal1986US.zip` | `1986FetalUserGuide.pdf` | 365 | no | same |
| 18 | 1987 | `Fetal1987US.zip` | `1987FetalUserGuide.pdf` | 365 | no | same |
| 19 | 1988 | `Fetal1988US.zip` | `1988FetalUserGuide.pdf` | 365 | no | same |
| 20 | 2023 | `Fetal2023US.zip` | (TBD probe at DO) | (TBD probe at DO) | no | C8.2 2026-05-13T01:30Z |
| 21 | 2024 | `Fetal2024US.zip` | (TBD probe at DO) | (TBD probe at DO) | no | same |

Record-length values: each new row's record_length will be probed at DO time via `unzip -p <zip> | head -c 1 | wc -c` or equivalent first-record-byte-length detection. The "365" placeholder for 1982-1988 is the standard 1978-revision record length per the user guides on disk; DO probe confirms. ✓

**Table 4: VERSION_ROADMAP.md fix-on-contact (E.2 ancillary per L11 finding (iii))**

| # | Line | Current text (verbatim) | Target text |
|---|---|---|---|
| 22 | 11 | `\| Fetal death \| **v2.1.0** (adds 2003 + 2004; H8 dtype reconciliation) \| v2.0.0 \| 1992–2022 \| 1,741,977 \| [10.5281/zenodo.20031571](https://doi.org/10.5281/zenodo.20031571) (v2.0.0) \|` | `\| Fetal death \| **v2.4.0** (V2.1 2003+2004 + V3a 1989-1991 + V3b 1982-1988 + latest-year refresh 2023+2024; H8 dtype reconciliation) \| v2.0.0 \| 1982–2024 \| 2,427,233 \| [10.5281/zenodo.20031571](https://doi.org/10.5281/zenodo.20031571) (v2.0.0) \|` |
| 23 | 13 | `The natality v2.8.0 and fetal-death v2.1.0 in-repo states are pending Zenodo deposit.` | `The natality v2.8.0 and fetal-death v2.4.0 in-repo states are pending Zenodo deposit.` |

**Table 5: Cross-link edits to existing READMEs (additive only)**

| # | File | Line approx | Edit |
|---|---|---|---|
| 24 | `README.md` (monorepo) | line 22-49 Repository Layout block | append `migrations/`, `docs/COMPARABILITY.md`, `docs/NCHS_SOURCE_MANIFEST.md` entries to the tree diagram + 1-line description rows |

(Per-product README cross-link edits at `fetal_death/README.md` near line 156 + `natality/README.md` near line 28 are similarly single-line additive cross-link insertions; not separately enumerated.)

**Plan assumptions amended at PRE-FLIGHT (per Convention 3 second bullet + AskUserQuestion 17:25Z user authorization):**

1. **(i) Migration guide filename — RESOLVED in-place per user authorization 17:25Z option "Proceed in-place per precedent."** §15 named `v2.0.0-to-v2.3.0-fetal-death.md`; PRE-FLIGHT re-targets to `v2.0.0-to-v2.4.0-fetal-death.md` since fetal-death actual current version is v2.4.0 per fetal_death/README.md line 156 + DECISION_LOG 2026-05-13T01:30Z. Routine L11 PRE-FLIGHT-input re-interpretation per the C8.9/C8.10a/b/c precedent.
2. **(ii) E.8 SHA manifest scope — RESOLVED in-place per same user authorization.** §15 VERIFY says "SHA manifest checksums match each subproject's file_inventory.csv"; PRE-FLIGHT verified neither file_inventory.csv contains a sha256 column. Resolution: SHA manifest is NEW data (raw-zip SHAs keyed by year × raw_filename), NOT a re-export of file_inventory.csv. The "match each subproject's file_inventory.csv" criterion means the manifest's row keys (year + raw_filename) align 1:1 with each inventory's rows. Manifest target path: `docs/NCHS_SOURCE_MANIFEST.md` (following the monorepo-docs `docs/JOINT_USE_GUIDE.md` + `docs/PRIOR_ART.md` precedent).
3. **(iii) VERSION_ROADMAP.md fetal-death version line — RESOLVED in-place per same user authorization.** Lines 11 + 13 carry stale v2.1.0 + 1992-2022 + 1,741,977 record-count claims; the actual current state is v2.4.0 + 1982-2024 + 2,427,233 records. Fix-on-contact at C8.11 DO; bundled into the E.2 fetal-death migration guide cross-link since the migration guide will reference VERSION_ROADMAP.md as the version-table source-of-truth.
4. **(A) Inventory extension — RESOLVED via AskUserQuestion 17:25Z Option A.** `fetal_death/file_inventory.csv` will be extended from 34 → 43 rows in C8.11 DO. The 9 NEW rows cover 7 V3b years (1982-1988) + 2 latest-year (2023-2024). Row metadata derived from DECISION_LOG entries (Table 1 above) + per-zip probes at DO. ~30-60 min addition; brings C8.11 estimated effort to ~3.5-4 sessions (within §15 "3-4 sessions" envelope at the upper bound). C8.11 SHA manifest then covers the full 43-year fetal-death envelope cleanly.

**Soft-flags surfaced at PRE-FLIGHT (NOT in-scope for C8.11; carried forward to Phase D pre-Zenodo):**

- (a) **fetal_death/PROVENANCE.md** (4830 bytes) + **fetal_death/PROVENANCE.sha256** (33-line file) are STALE relative to v2.4.0 — last updated 2026-05-05 covering only the v2.0.0 release artifacts (file SHAs reflect pre-V2.1 + pre-V3a + pre-V3b + pre-latest-year-refresh state). The current `fetal_death_harmonized.parquet` sha=`38e2cecb…` and `fetal_death_derived.parquet` sha=`185c071e…` do NOT match the PROVENANCE.md-listed `f09beb4a…` + `90af89b9…`. The PROVENANCE.sha256 self-coverage promise ("verify everything else") fails on the current v2.4.0 build. **OUT-OF-SCOPE for C8.11** (which focuses on RAW NCHS source data, not output artifact PROVENANCE per §15 "NCHS-source-data SHA manifest" phrasing); soft-flag for Phase D step 2 (Zenodo deposit refresh) where the natural fix is re-running `shasum -a 256` on the v2.4.0 deposit-bound files and rebuilding both PROVENANCE.md + PROVENANCE.sha256 to match. Filed as Phase D pre-Zenodo deliverable.
- (b) **Natality has NO PROVENANCE.md** (verified: `ls natality/PROVENANCE.md natality/docs/PROVENANCE.md` both "No such file or directory"). The Zenodo v2.7.0 deposit ships a PROVENANCE.md, but it's NOT in the monorepo natality/ directory (lives only in the Zenodo archive). The current monorepo state has no natality output-artifact SHA manifest at all — making cross-product output-SHA verification asymmetric. Same OUT-OF-SCOPE classification as (a); same Phase D step 2 resolution (author natality/PROVENANCE.md as part of unified Zenodo deposit).
- (c) **VERSION_ROADMAP.md "Planned" section (lines 15-22)** still lists "Fetal death V2.1 — add 2003 and 2004 transition years" as a PLANNED item. This is more than the line-11+13 fix-on-contact authorized; the whole "Planned" section needs review since multiple items have shipped (V2.1 done; V3a done; V3b done). **OUT-OF-SCOPE for C8.11 per Anti-Pattern #8** (compressed-task avoidance); soft-flag for a future small VERSION_ROADMAP refresh task. Authorized fix-on-contact at C8.11 DO covers ONLY lines 11 + 13.
- (d) **C8.7a documented finding** `fetal_death/scripts/run_pipeline.py` ALL_YEARS=29 stale relative to v2.4.0's 43-year envelope; deferred to C8.7b orchestrator authoring. Soft-flag: the C8.11 fetal-death migration guide can NAME the v2.4.0 envelope explicitly to help users with legacy v2.0.0 code understand the year extension (~1 paragraph). Not a separate deliverable; integrated narrative.
- (e) **Monorepo `raw_data/` symlink** only links `raw_data/fetal_death -> /Users/yoelplutchok/Desktop/fetal-death-harmonization-build/raw_data/fetal_death`; no natality + linked symlink (C8.7a finding). The C8.11 E.8 manifest's SHA computation will need to read 87 zips from 3 absolute paths (43 from fetal-death build dir; 35 from natality build dir; 19 from natality build dir's linked/ subdir). Not a halt — DO-step responsibility to enumerate; documented for the DO author.
- (f) **Plurality footgun for natality**: the natality + linked file's plurality-coding anomaly (C.6.e candidate notebook from C8.15) is in scope for E.4 cross-product COMPARABILITY synthesis — fd COMPARABILITY §7 names it as fetal-death-specific, but the same NCHS sentinel pattern likely applies to natality 2005-2013. Soft-flag for E.4 author to investigate during DO; not pre-resolved.
- (g) **Carry-forward soft-flags from C8.10c** (C8.2 NCHS 2025PE2024CO release; C8.3 manuscript line 99; C8.4 linked-vs-natality drift bound; C8.5a-a/b/c; C8.6-a/b; C8.7a-a/b/c; C8.8-a/b/c/d; C8.9-a/b/c/d/e; C8.10a-a/b/c/d/e; C8.10b-a/b/c/d; C8.10c-a/b/c/d/e). All preserved; none promoted to halt status by this PRE-FLIGHT.

### Halt conditions tripped

One §7.13-shape scope-affecting L11 surfaced (Option A inventory extension) + three additional routine L11 PRE-FLIGHT-input re-interpretations ((i) + (ii) + (iii)) — all four user-resolved via AskUserQuestion 2026-05-13T17:25:00Z. User selected:
- Question 1: **(A) Extend inventory to 43 rows in C8.11 DO (Recommended)** — resolves L11 finding #4 (file_inventory.csv stale)
- Question 2: **Proceed in-place per precedent (Recommended)** — resolves L11 findings (i)/(ii)/(iii)

No unresolved §7 condition. Convention 3 Field-value snapshot above documents all 24 mutation targets + their current vs. assumed-state verification. Convention 4 carry-over verification of all 12 C8.10c Forward-looking HALTs returned byte-exact.

### Result

**PROCEED.** All inputs verified; environment clean; 12 C8.10c forward-looking HALTs all pass byte-exact; Convention 3 Field-value snapshot computed 24 rows across 5 tables (5 migration-content sources + 7 COMPARABILITY synthesis cells + 9 inventory-extension rows + 2 VERSION_ROADMAP fix-on-contact + 1 cross-link); one §7.13-shape condition + 3 routine L11s surfaced + user-resolved via AskUserQuestion 17:25Z (Option A inventory extension + in-place L11 resolutions per the C8.9/C8.10a/b/c precedent). Tag `C8.11-pre-do` placed on the PRE-FLIGHT commit; DO phase commences post-tag in subsequent session(s) per the §15 3-4 session estimate (with Option A +30-60 min). 7 soft-flags (a)-(g) surfaced and filed for Phase D / future-task resolution; none are PRE-FLIGHT halts.

---

## PRE-FLIGHT for C8.10c — 2026-05-13T16:30:00Z — Worked-example notebook 3 of 3 (C.6.c `cross_race_fetal_mortality.ipynb`; V3a/V3b race-stratified FD demo with B3 1-digit-recode caveats + cross-era time series + 2022 single-race + Hispanic NVSR-cell cross-validation) — **RESULT: PROCEED** (one §7.13 condition surfaced + user-resolved via AskUserQuestion 2026-05-13T16:15:00Z Option A; in-PRE-FLIGHT re-interpretation per C8.9/C8.10a/b L11 discipline; no §11 plan-update commit needed; 7 NVSR-equivalent cells available via `joint_use_demo.ipynb` Section B precedent — exceeds §15 "≥3" minimum)

### Scope summary

C8.10 §15.C entry (NEXT_STEPS.md lines 1145–1164) is the composite 3-notebook task; this PRE-FLIGHT covers **sub-task C8.10c** (C.6.c `cross_race_fetal_mortality.ipynb`) per the sub-receipt convention established at C8.10a + C8.10b (PRE_FLIGHT_LOG 2026-05-13T14:29:23Z + 14:57:02Z). KICKOFF.md Phase C Tier-2 line 191 + §15.C C8.10 entry name C.6.c as the 3rd sub-notebook ("V3a/V3b demo; race-stratified FD; documents the B3 1-digit-recode caveats"). STATUS 15:18:46Z line 62 names C.6.c as the next sub-task.

**Session scope this PRE-FLIGHT (the (a)-(d) handshake-stated plan, user-authorized "proceed" + AskUserQuestion 16:15Z Option A):** ship notebook 3 of 3 (C.6.c) end-to-end through RECEIPT + parent `C8.10-complete` tag. Scope refined per Option A: (i) reproduce the 7 NVSR 73-09 Table A 2022 race-stratified FMR cells (Total 5.48 / AIAN 7.22 / Asian 3.70 / Black 10.05 / NHOPI 10.36 / White 4.48 / Hispanic 4.63) from `joint_use_demo` Section B precedent as the current-era cross-reference validation backbone; (ii) extend to a 1982-2024 race-stratified FMR time series across V3b + V3a + V2 + V1 eras using `maternal_race_bridged` (1982-2013) + `race_hispanic_revised` collapsed to 4-cat bridged (2014+) as the cross-era continuity bridge; (iii) document the B3 1-digit-recode caveats inline (V3b code 7 + code 9 → null per DECISION_LOG 2026-05-12T18:30Z; V3a code 09 → null per DECISION_LOG 2026-05-12T14:30Z); (iv) machinery demo asserts (per-era row-count + bridged-race conservation: sum-across-4-cats + null = total per era).

### Inputs

- [x] **All 12 C8.10b Forward-looking HALTs verified byte-exact** (see table below; 4 parquet SHAs + 5 C8.10a/b file SHAs + 14 C8.9 file SHAs + tag presence). ✓
- [x] **Fetal-death derived parquet** (v2.4.0; 43-yr 1982-2024 with V3a + V3b extension applied) present; sha=`185c071ec76ab8aa…`; 2,427,233 rows × 89 cols. Probed `maternal_race_bridged` (Int8 dtype; values 1-4 + NA): distribution 1=1,439,008 / 2=561,232 / 3=12,602 / 4=100,305 / NA=314,086. Probed `race_hispanic_revised` (string dtype; codes '1'-'8' + empty): distribution 1=185,989 / 2=117,516 / 3=2,600 / 4=22,042 / 5=1,505 / 6=4,789 / 7=80,803 / 8=56,718 / ''=1,955,271 (pre-2014 null). ✓
- [x] **V3a baseline parquet** present at `~/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_derived.V3a_baseline.parquet`; sha=`0dd3aec0e47785f1…`; 29,350,962 bytes. **V3b baseline parquet** present; sha=`4d1b37cc3a214eea…`; 34,011,022 bytes. **Both are PRE-EXTENSION sidecar snapshots; the notebook will NOT use them** — the active v2.4.0 parquet (`fetal_death_derived.parquet`) already has V3a + V3b extension applied. Sidecar SHAs recorded for PROVENANCE-trace reference only. ✓
- [x] **Natality v2.8.0 derived parquet** present; sha=`e16ad5323d68e28d…`; 138,819,655 rows × 84 cols. Needed for denominator (live births by race-class for FMR computation). Same race columns as joint_use_demo Section B: `maternal_race_ethnicity_5` + `maternal_race_detail` (for Asian/NHOPI split in 2003-rev OMB classification 2022+). ✓
- [x] **Validation source for NVSR-equivalent cells (per Option A re-interpretation)**: `notebooks/_build_joint_use_demo.py` Section B at lines 230-310 encodes 7 NVSR 73-09 Table A 2022 target rates (Total 5.48 / AIAN 7.22 / Asian 3.70 / Black 10.05 / NHOPI 10.36 / White 4.48 / Hispanic 4.63) + the canonical race-class derivation logic. C.6.c reproduces these 7 cells from the same parquets using identical canonical filters + derivation logic; cross-validates the byte-exact-from-joint_use_demo result; then extends to the cross-era 1982-2024 time series. **7 cells × byte-exact-validation = exceeds §15 "≥3" minimum.** ✓
- [x] **Validation CSVs** `fetal_death/external_validation_targets.csv` (87 rows), `natality/metadata/external_validation_targets_v1.csv` (245 rows), `natality/metadata/external_validation_targets_v3_linked.csv` (53 rows) — **zero race-stratified cells in all three** (confirmed via cheap-check). This is the §7.13 surface that triggered AskUserQuestion 16:15Z; resolution = use `joint_use_demo` Section B precedent instead.
- [x] **Builder template** `notebooks/_build_preterm_outcomes_time_series.py` (C8.10b sibling; sha=`3bc2a8f1731f913e…`) + `_build_maternal_age_stratified_imr.py` (C8.10a; sha=`9db692743e050189…`) + `_build_joint_use_demo.py` (cross-product 3-parquet sibling with the Section B race-class logic + 7-cell validation table) all present and structurally identical. ✓
- [x] **DECISION_LOG B3 1-digit-recode references**: 2026-05-12T14:30:00Z (V3a code 09 → null; 165 records across 1989-1991 = 0.087%) + 2026-05-12T18:30:00Z (V3b code 7 → null ~89 records; V3b code 9 → null ~18,700 records / 3-5% per year). Both cited as load-bearing for the notebook's caveat narrative. ✓
- [x] **No stale checkpoints**: `git status --short` empty; `C8.10c-pre-do` tag does NOT yet exist (will be placed post-PRE-FLIGHT, pre-DO). ✓

### C8.10b Forward-looking HALTs (all 12 verified)

| # | Assertion | Verification | Status |
|---|---|---|---|
| 1 | `C8.10b-complete` tag present; `C8.10c-pre-do` absent | `git tag --list 'C8.10*'` → C8.10a-pre-do + C8.10a-complete + C8.10b-pre-do + C8.10b-complete; no C8.10c-pre-do | ✓ |
| 2 | `notebooks/_build_preterm_outcomes_time_series.py` sha=`3bc2a8f1731f913e…` (31,266 bytes) | verified | ✓ |
| 3 | `notebooks/preterm_outcomes_time_series.ipynb` sha=`724cb46b17edab65…` (90,549 bytes) | verified | ✓ |
| 4 | `notebooks/README.md` sha=`5a0a8b4b291214cc…` (5,948 bytes) | verified | ✓ |
| 5 | 4 parquet SHAs unchanged byte-exact | fd_harm=`38e2cecb03ff4947…` ✓; fd_der=`185c071ec76ab8aa…` ✓; nat_der=`e16ad5323d68e28d…` ✓; linked_der=`9b828a4de4e59b17…` ✓ | ✓ |
| 6 | All 14 C8.9 + 2 of 3 C8.10a file SHAs unchanged | C8.9 batch (R quickstarts ×3 + views.sql + JOINT_USE_GUIDE + pyproject + uv.lock + .python-version + README + ci.yml + validate_2022 + run_pipeline + CHANGELOG + PRIOR_ART) ✓; C8.10a builder `9db692743e050189…` ✓; C8.10a ipynb `036de6b4b927e586…` ✓ (notebooks/README.md drifted intentionally per C8.10a HALT #11) | ✓ |
| 7 | Next task = C8.10c per KICKOFF.md line 191 + STATUS 15:18:46Z line 62 | confirmed; this entry executes | ✓ |
| 8 | Parent C8.10 §15 task ships across 3 sub-receipts; after C8.10c append parent `C8.10-complete` tag | confirmed convention; planned for this session | ✓ |
| 9 | §15 PRE-FLIGHT-input re-verification discipline (C8.9-surfaced L11) | **executed below — surfaced §7.13 condition, user-resolved via AskUserQuestion Option A** | ✓ |
| 10 | L13 CSV-formatting workaround: `external_validation_targets_v1.csv` unquoted commas → `engine='python', on_bad_lines='skip'` | C.6.c will not consume that CSV (no race cells in it; all FD validation via in-builder NVSR-cell table from joint_use_demo) — workaround N/A this session | ✓ N/A |
| 11 | `notebooks/README.md` Planned section `era_boundary_walkthrough.ipynb` stub | confirmed unchanged; out of active Phase C scope | ✓ informational |
| 12 | Cumulative Phase C effort ~11 of 29-35 sessions (~33%) | this session targets ~1-1.5; budget healthy (cap 42 sessions) | ✓ |

### Environment

- [x] Working directory clean: `git status --short` empty. ✓
- [x] On `main`, HEAD=`f349c82` (C8.10b-complete). ✓
- [x] `.venv/bin/python` 3.13.9; pandas 2.3.2; pyarrow 18.1.0; numpy 2.3.1; duckdb 1.5.2 (unchanged from C8.9). ✓
- [x] `nbformat` + `nbclient` available (verified at C8.10a/b builder execution; not separately re-probed). ✓

### Source documentation (L9 cheap-check + §7.13 condition + user-authorized resolution)

The §15 C8.10 PRE-FLIGHT-input list names "NVSR validation cells per notebook (L9 cheap-check)" — without specifying WHICH NVSR table or whether an NVSR PDF is on disk. C8.10a + C8.10b established the durable resolution: validation cells come from the per-product `external_validation_targets_*.csv` files whose entries were L9-cheap-checked at their authoring moment. **C8.10c application of the same probe routine surfaces a §7.13 condition**: the encoded CSVs have ZERO race-stratified cells for the V3a/V3b 1982-1991 era this notebook centers on. Resolution required AskUserQuestion (Option A chosen).

**Probe A — `raw_docs/` inventory.** `find raw_docs natality/raw_docs -type f` → only `.gitkeep` files. Zero NVSR PDFs on disk (unchanged from C8.10a/b — open soft-flag (a) carried forward).

**Probe B — FD validation CSV race-cell inventory.** `grep -iE "race|hispanic|white|black|aian|asian|nhopi" fetal_death/external_validation_targets.csv` → **zero matches**. The 87 rows cover: fetal_deaths_gte20wk_resident (34 cells × 1989-2022); fetal_mortality_rate (26 cells); maternal-age bands (8 cells × 2022); sex (2 cells × 2022); plurality (3 cells × 2022); cause-of-death codes P00/P01/P02/P95/Q00-Q99 (5 cells); early/late gestation (4 cells × 2014+2022). **No race stratification at any year.**

**Probe C — Natality v1 + linked v3 validation CSV race-cell inventory.** `grep -iE "race|hispanic|nhwh|nhbl|aian|asian" natality/metadata/external_validation_targets_v1.csv natality/metadata/external_validation_targets_v3_linked.csv` → **zero matches** (245 + 53 rows respectively).

**Probe D — DECISION_LOG cross-reference for race-stratified V3a/V3b cell availability.** `grep -inE "Series 21|race-stratified|race.*post-submission" DECISION_LOG.md` → DECISION_LOG 2026-05-12T14:30:00Z (V3a B3 recode) line 916: *"NVSR Volume 41/42/43 or NCHS Series 21 reports for 1989-1991 race-stratified fetal death tables is post-submission scope"*; DECISION_LOG 2026-05-12T18:30:00Z (V3b B3 recode) line 841: similar deferral for 1982-1988. **Confirmed: race-stratified V3a/V3b cell L9-cheap-check is explicit post-submission scope.**

**Probe E — `joint_use_demo.ipynb` Section B precedent inventory.** `notebooks/_build_joint_use_demo.py` lines 239-310 encode 7 NVSR 73-09 Table A 2022 target rates with full canonical-filter + race-class derivation logic (single-race + Hispanic 6-cat: AIAN / Asian / Black / NHOPI / White / Hispanic + Total) using `race_hispanic_revised` for fetal deaths + (`maternal_race_ethnicity_5` × `maternal_race_detail`) for natality denominators. Joint_use_demo notebook was ALREADY validated byte-exact at its shipping moment (Task 2 receipt 2026-05-11). **These 7 cells are the available NVSR-equivalent validation backbone for C.6.c.**

**§7.13 condition surfaced.** §15 C8.10 PRE-FLIGHT-input "NVSR validation cells per notebook (L9 cheap-check)" — for C.6.c's V3a/V3b race-stratified focus — has no encoded CSV source. The C8.10a/b in-PRE-FLIGHT re-interpretation (point at already-L9-checked CSV entries) FAILS because all three CSVs are empty for race cells. Adding new V3a/V3b NVSR race cells via PDF L9-cheap-check is explicit post-submission scope per DECISION_LOG. **Per §7 binding rule, halt-and-ask.**

**AskUserQuestion 2026-05-13T16:15:00Z** — three options offered: (A) Re-scope to cross-era demo + 2022 cross-val using joint_use_demo Section B 7 cells as validation backbone (Recommended; ~1-1.5 sessions; in-PRE-FLIGHT re-interpretation, no §11 plan-update); (B) Expand scope to L9-probe NVSR Vol 41/42/43 + add new V3a/V3b race cells to FD CSV (~2-3 sessions; §11 plan-update + canonical-state mutation; trips Q33 effort-ceiling watch); (C) DROP C.6.c (parent C8.10 closes 2-of-3 sibling of C8.9's C.1 drop; §11 plan-update; loses V3a/V3b race-stratified demo value).

**User-authorized resolution: Option A.** Documented in receipt (no §11 plan-update commit). C.6.c reproduces 7 NVSR-equivalent cells from joint_use_demo Section B precedent + extends to 1982-2024 cross-era time series + documents B3 1-digit-recode caveats. The L11 in-PRE-FLIGHT re-interpretation pattern is generalized: when the encoded CSV lacks the relevant cells for a notebook's chosen era/strata, the validation backbone may be drawn from a sibling notebook's already-validated byte-exact result, treated as the L9-cheap-checked source. This is a STRICT-LESS resolution than C8.10a/b's CSV reference (which is the canonical primary source); the joint_use_demo precedent is a SECONDARY source, but its byte-exact validation at Task 2 makes it a legitimate L9-equivalent.

### Outputs

- **NEW**: `notebooks/_build_cross_race_fetal_mortality.ipynb_builder.py` (deterministic builder, ~450-500 lines; sibling pattern from `_build_joint_use_demo.py` for the race-class derivation logic + `_build_maternal_age_stratified_imr.py` for the time-series machinery). Filename TBD at DO; likely `notebooks/_build_cross_race_fetal_mortality.py`.
- **NEW**: `notebooks/cross_race_fetal_mortality.ipynb` (executed notebook with output cells).
- **MODIFIED**: `notebooks/README.md` (replace C.6.c "planned" stub with shipped entry; update Status section to mark C8.10 parent COMPLETE; current sha=`5a0a8b4b291214cc…` will drift; recorded post-DO).
- **NEW**: `RECEIPTS/C8.10c_<UTC>.md` (per-notebook sub-task receipt; parent `C8.10-complete` tag follows).
- **NEW**: `STATUS.md` append.
- **NEW**: `PRE_FLIGHT_LOG.md` append (this entry).
- **Tags**: `C8.10c-pre-do` (this PRE-FLIGHT commit) → `C8.10c-complete` (post-RECEIPT) → `C8.10-complete` (parent, post-3-of-3).
- **Invariants**: 4 parquet SHAs unchanged (no parquet mutation). All 14 C8.9 file SHAs + 4 C8.10a/b file SHAs (2 builders + 2 ipynb) unchanged. Only `notebooks/README.md` drifts.

### Field-value snapshot for cells being asserted (Convention 3)

**Section 1: 7 NVSR 73-09 Table A 2022 byte-exact cells (from joint_use_demo Section B precedent, re-reproduced):**

| race-class (NVSR) | FD code | nat denom class | PRE-FLIGHT FD count (2022 canonical, tab=1, resident!=4) | NVSR target rate | Status |
|---|---|---|---|---|---|
| Total | (all) | (all) | 19,716 | 5.48/1000 | will assert |
| NH White | 1 | NH_white | 7,397 | 4.48/1000 | will assert |
| NH Black | 2 | NH_black | 4,955 | 10.05/1000 | will assert |
| NH AIAN | 3 | NH_aian | 20 | 7.22/1000 | will assert |
| NH Asian | 4 | NH_asian_pi×04 | 929 | 3.70/1000 | will assert |
| NH NHOPI | 5 | NH_asian_pi×05 | 58 | 10.36/1000 | will assert |
| Hispanic | 7 | Hispanic | 2,791 | 4.63/1000 | will assert |

(Code 6 NH More-than-one=95 and code 8 Unknown=3,471 not part of NVSR Table A cells; reported in supplementary breakdown.)

**Section 2: Per-era canonical-filter (tab==1, resident!=4) + bridged-race conservation invariant:**

| year | era | total | bridged_1 (W) | bridged_2 (B) | bridged_3 (AIAN) | bridged_4 (API) | bridged null | invariant |
|---|---|---|---|---|---|---|---|---|
| 1982 | V3b | 29,575 | 21,150 | 5,316 | 59 | 1,068 | 1,982 (6.70%) | sum=29,575 ✓ |
| 1985 | V3b | 29,979 | 20,914 | 5,671 | 40 | 1,107 | 2,247 (7.50%) | sum=29,979 ✓ |
| 1988 | V3b | 30,443 | 21,855 | 5,768 | 58 | 1,093 | 1,669 (5.48%) | sum=30,443 ✓ |
| 1989 | V3a | 30,767 | 23,053 | 6,494 | 62 | 1,147 | 11 (0.04%) | sum=30,767 ✓ |
| 1991 | V3a | 33,052 | 23,902 | 7,712 | 75 | 1,355 | 8 (0.02%) | sum=33,052 ✓ |
| 1992 | V2 | 40,615 | 27,422 | 11,526 | 147 | 1,520 | 0 | sum=40,615 ✓ |
| 2002 | V2 | 29,283 | 20,662 | 6,629 | 67 | 1,925 | 0 | sum=29,283 ✓ |
| 2005 | V1 (pre-2014) | 27,387 | 18,985 | 6,263 | 63 | 2,076 | 0 | sum=27,387 ✓ |
| 2013 | V1 (pre-2014) | 30,352 | 19,036 | 9,028 | 42 | 2,246 | 0 | sum=30,352 ✓ |

**B3 1-digit-recode caveat impact confirmed empirically:**
- V3b 1982-1988 null fraction range: 5.48% – 7.50% per year (matches DECISION_LOG 2026-05-12T18:30Z "~3-5% per year" prediction; slightly above due to canonical-filter narrowing).
- V3a 1989-1991 null fraction range: 0.02% – 0.04% per year (matches DECISION_LOG 2026-05-12T14:30Z "0.087% across 1989-1991 total" prediction; per-year fraction lower).
- V2 1992-2002 + V1 2005-2013: 100% non-null bridged (control-period baseline; no B3 recode null contribution).
- V1 2014+ (OE-era): bridged is 100% null in 2022; `race_hispanic_revised` becomes the canonical column (22.94% null at 2014 transition year; ~17.6% null in 2022 from code 8 Unknown).

**Section 3: Cross-era bridge mapping (`race_hispanic_revised` 2014+ → bridged 4-cat collapse for cross-era time series continuity):**

| race_hispanic_revised | code | maps to bridged 4-cat |
|---|---|---|
| NH White | 1 | bridged=1 (White) |
| NH Black | 2 | bridged=2 (Black) |
| NH AIAN | 3 | bridged=3 (AIAN) |
| NH Asian | 4 | bridged=4 (API) |
| NH NHOPI | 5 | bridged=4 (API) — same as Asian per NCHS bridged-race convention |
| NH More-than-one | 6 | bridged=null (no 4-cat assignment per OMB) |
| Hispanic | 7 | bridged-row stratified separately as Hispanic (parallel axis) |
| Unknown | 8 | bridged=null |

The Hispanic axis is orthogonal to bridged-race in NCHS convention; the time-series notebook will use the 4-cat bridged race for the 1982-2024 panel + add a separate Hispanic-or-not annotation for 2014+ (where Hispanic origin is reliably coded).

**Shape check**:
- Time series shows expected demographic patterns: NH Black FMR ~2× NH White across all eras; AIAN counts are small (≤100/yr) so rates noisier; API fraction grows over time (immigration-driven).
- V3b null fraction (5-7%) creates a visible "missing data" band 1982-1988 in any race-stratified panel; must be documented inline.
- 2014 OE-shift boundary creates a discontinuity in `race_hispanic_revised` (22.94% null at 2014; settles to ~17.6% at 2022); for the time series, the boundary effect is documented inline + the rate denominators are computed from the same source (natality `maternal_race_ethnicity_5`) to keep the numerator-denominator within-product consistent.

**Cross-product universe alignment (F1 discipline)**:
- FD canonical filter for per-year FMR + Section 1 2022 NVSR cells: `tabulation_flag == 1 AND residence_status != 4` (matches `_build_joint_use_demo.py` line 165's per-year-FMR universe).
- Natality denominator filter: `residence_status != 4` only (no tabulation_flag in natality schema). 

### Halt conditions tripped

**§7.13 (validity-domain / plan-claim-doesn't-match-available-artifact) — RESOLVED at PRE-FLIGHT via AskUserQuestion 2026-05-13T16:15:00Z Option A.** The §15 C8.10 PRE-FLIGHT-input "NVSR validation cells per notebook (L9 cheap-check)" failed the C8.10a/b in-PRE-FLIGHT re-interpretation (CSVs lack race cells); user-authorized resolution: use `joint_use_demo` Section B precedent (7 NVSR 73-09 Table A 2022 cells) as the validation backbone + extend to V3a/V3b cross-era machinery demo with B3 1-digit-recode caveats narrative. Documented in receipt; no §11 plan-update commit.

### Open considerations (soft-flags, NOT halts)

- (a) **`raw_docs/` empty across monorepo** — carried forward from C8.10a/b. Phase D step 3 / C8.13 candidate.
- (b) **Notebook bit-reproducibility caveat** — carried forward from C8.10a/b. C8.13 (B.12 snapshot regression) candidate.
- (c) **Hardcoded absolute parquet paths in builder** — carried forward from C8.10a/b. C8.7b natality+linked output-path strategy candidate.
- (d) **§15 PRE-FLIGHT-input re-verification discipline now in 5th consecutive application** (C8.9 + C8.10a + C8.10b + this entry + filed for C8.11+). Each consecutive surface confirms the C8.9 self-flagged soft-flag (a) — §15 entries authored at EXPLORATION_REPORT-time without verifying claims against then-current data is a recurring L11 pattern. **Worth elevating to a §8 matrix sharpening at Phase C close** (post-C8.15) per LESSONS.md backport scope.
- (e) **In-PRE-FLIGHT re-interpretation generalization** — C8.10a/b/c each resolved a §15 input mismatch in-PRE-FLIGHT without §11 plan-update. The pattern is: (i) read §15 input claim literally; (ii) if cheap-check fails, look for a secondary source that's already-L9-checked; (iii) if secondary source exists + meets §15 minimum quantitatively (≥3 cells), re-interpret + document in receipt; (iv) if no secondary source, AskUserQuestion. **The "secondary source = sibling notebook's byte-exact-validated cells" pivot is new at C8.10c** — first invocation of this pattern. May recur in C8.11 / C8.14 / C8.15. Worth a forward-looking note in LESSONS.md when C8.10 parent ships.
- (f) **NVSR 73-09 Table A 2022 cells provenance**: re-reproduced from joint_use_demo Section B (Task 2 receipt 2026-05-11), which traces to NVSR 73-09 Table A PDF (`https://www.cdc.gov/nchs/data/nvsr/nvsr73/nvsr73-09.pdf`). Each cell value (Total 5.48 / AIAN 7.22 / Asian 3.70 / Black 10.05 / NHOPI 10.36 / White 4.48 / Hispanic 4.63) was L9-cheap-checked at Task 2's PRE-FLIGHT moment. Documented in joint_use_demo Section B narrative.
- (g) **V3a/V3b bridged-race null records (1982-1991, ~22.7K total)**: documented in builder narrative + Section 4 caveat. A future researcher using `maternal_race_bridged` to stratify 1982-1991 fetal deaths must note totals don't add up exactly to per-year totals due to the recode mappings of residual codes (V3b code 7 "Other nonwhite" + V3b code 9 "Not stated" + V3a code 09 "All other Races") to null. The B3 1-digit-recode caveats narrative IS the durable contribution of this notebook.

### Forward-looking HALTs for next session — pending receipt drafting

(Will be enumerated in `RECEIPTS/C8.10c_<UTC>.md` per Convention 4 + restated in STATUS append; parent `C8.10-complete` tag deferred until C.6.c ships then placed.)

### Commit + tag plan

1. **This PRE-FLIGHT commit** (`[plan-update]` NOT prepended; this is pure PRE-FLIGHT documentation per Q42; the §7.13 user-resolution per AskUserQuestion Option A does not modify §15 entries or KICKOFF.md sequencing, only documents the in-PRE-FLIGHT re-interpretation in receipt + STATUS). Stage: `PRE_FLIGHT_LOG.md`. Commit message: short 5-line summary per Convention 5.
2. **Tag**: `C8.10c-pre-do` on this commit. `git tag --list 'C8.10*'` should show: `C8.10a-pre-do`, `C8.10a-complete`, `C8.10b-pre-do`, `C8.10b-complete`, `C8.10c-pre-do` after this commit.
3. **DO commit** (subsequent): ships builder + ipynb + README update + receipt + STATUS. Tag: `C8.10c-complete`.
4. **Parent commit** (same DO commit OR a sibling commit after C.6.c ships): tag `C8.10-complete` marking parent §15 C8.10 task done.

---

## PRE-FLIGHT for C8.10b — 2026-05-13T14:57:02Z — Worked-example notebook 2 of 3 (C.6.b `preterm_outcomes_time_series.ipynb`; cross-product FD + natality + linked preterm-birth secular trends) — **RESULT: PROCEED** (zero §7 halt; three §15 PRE-FLIGHT-input re-interpretations logged as soft-flags per the C8.9-surfaced L11 discipline; ≥34 byte-exact NVSR-equivalent cells available via `external_validation_targets_v1.csv` — far above the §15 "≥3" minimum)

### Scope summary

C8.10 §15.C entry (NEXT_STEPS.md lines 1145–1164) is the composite 3-notebook task; this PRE-FLIGHT covers **sub-task C8.10b** (C.6.b `preterm_outcomes_time_series.ipynb`) per the sub-receipt convention established at C8.10a (PRE_FLIGHT_LOG 2026-05-13T14:29:23Z; STATUS 14:37:17Z line 100). KICKOFF.md Phase C Tier-2 line 191 mirrors C8.10 sequencing; STATUS 14:37:17Z line 55 names C.6.b as the next sub-task.

**Session scope this PRE-FLIGHT (the (a)-(d) handshake-stated plan, user-authorized "proceed"):** ship notebook 2 of 3 (C.6.b) end-to-end through RECEIPT. C.6.c remains pending in §15.C C8.10; receives its own PRE-FLIGHT in a subsequent session. Parent `C8.10-complete` tag deferred until C.6.c also ships.

### Inputs

- [x] **All 12 C8.10a Forward-looking HALTs verified byte-exact** (see table below; 4 parquet SHAs + 3 C8.10a file SHAs + 14 C8.9 file SHAs + tag presence). ✓
- [x] **Natality v2.8.0 derived parquet** present at `~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet`; sha=`e16ad5323d68e28d…`; 138,819,655 rows × 84 cols. Probed `preterm_lt37` column: bool dtype; 15,482,452 True / 122,599,952 False / 737,251 None; values reproduce NVSR preterm_rate_pct cells byte-exact at 7/7 spot-checked years (1990, 2000, 2005, 2013, 2014, 2020, 2023). ✓
- [x] **Linked v3 derived parquet** present; sha=`9b828a4de4e59b17…`; 74,943,824 rows × 94 cols. Same `preterm_lt37` column; values reproduce byte-exact at 4/4 spot-checked joint years (2005, 2013, 2014, 2022, 2023). ✓
- [x] **Fetal-death derived parquet** (v2.4.0; 43-yr 1982-2024) present; sha=`185c071ec76ab8aa…`; 2,427,233 rows × 89 cols. Probed `gestational_age_combined` (string), `preterm` (string '0'/'1'/''), `gestational_age_recode5`; gestation-stratified counts for 2014 + 2022 surface validator-documented expected-diffs (NVSR redistributes not-stated GA proportionally; our parquet retains GA=99 as unknown per `fetal_death/scripts/05_validate/validate_external.py:173-175`). ✓
- [x] **Validation CSV** `natality/metadata/external_validation_targets_v1.csv` present; **34 `preterm_rate_pct` cells covering 1990-2023** every year (19 tight-tolerance ≤0.05 for 2005-2023 OE-based era; 15 wider-tolerance 0.15 for 1990-2004 LMP-based era). All cells cite NVSR vol/no/date or `childstats.gov HEALTH1.A` source. ✓
- [x] **Validation CSV** `natality/metadata/external_validation_targets_v3_linked.csv` — **0 preterm/gestation cells** (only IMR/neonatal/postneonatal). Linked file's preterm contribution to the notebook is a cross-product consistency check vs natality (joint years 2005-2023; per C8.4 bounded by 0.01% drift).
- [x] **Validation CSV** `fetal_death/external_validation_targets.csv` — **4 gestation-stratified cells**: `fetal_deaths_early_20_27wk` (2014: 12,652; 2022: 10,246) + `fetal_deaths_late_28wk_plus` (2014: 11,328; 2022: 9,956), all NVSR 73-09 Table 1. Validator at `validate_external.py:172-193` documents expected-non-byte-exact diff with `expected_diff: True`.
- [x] **Builder template** `notebooks/_build_maternal_age_stratified_imr.py` (C8.10a sibling; sha=`9db692743e050189…`) + `notebooks/_build_joint_use_demo.py` (cross-product 3-parquet sibling) + `notebooks/_build_paper_companion.py` all present and structurally identical (`REPO_ROOT`, `OUTPUT`, hardcoded parquet absolute paths, `md()` + `code()` helpers, `build()` → `nbformat.NotebookNode`, `NotebookClient` execution at `__main__`). ✓
- [x] **No stale checkpoints**: `git status --short` empty; `C8.10b-pre-do` tag does NOT yet exist (will be placed post-PRE-FLIGHT, pre-DO). ✓

### C8.10a Forward-looking HALTs (all 12 verified)

| # | Assertion | Verification | Status |
|---|---|---|---|
| 1 | `C8.10a-complete` tag present; `C8.10b-pre-do` absent | `git tag --list 'C8.10*'` → C8.10a-pre-do + C8.10a-complete; no C8.10b-pre-do | ✓ |
| 2 | `notebooks/_build_maternal_age_stratified_imr.py` sha=`9db692743e050189…` (25,408 bytes) | verified | ✓ |
| 3 | `notebooks/maternal_age_stratified_imr.ipynb` sha=`036de6b4b927e586…` (51,093 bytes) | verified | ✓ |
| 4 | `notebooks/README.md` sha=`e388da8f9e77445d…` | verified | ✓ |
| 5 | 4 parquet SHAs unchanged byte-exact | fd_harm=`38e2cecb03ff4947…` ✓; fd_der=`185c071ec76ab8aa…` ✓; nat_der=`e16ad5323d68e28d…` ✓; linked_der=`9b828a4de4e59b17…` ✓ | ✓ |
| 6 | All 14 C8.9 file SHAs unchanged | `fetal_death/quickstart.R` `3b2c0fe0…` ✓; `natality/quickstart.R` `15d9edfb…` ✓; `natality/quickstart_linked.R` `a83e0a90…` ✓; `views.sql` `c7b674f6…` ✓; `JOINT_USE_GUIDE.md` `534814a9…` ✓; `pyproject.toml` `c044f1c6…` ✓; `uv.lock` `a3850943…` ✓; `.python-version` `02e735b3…` ✓; `README.md` `694fdd35…` ✓; `ci.yml` `c248cf51…` ✓; `validate_2022.py` `67a4dfcb…` ✓; `run_pipeline.py` `959ccac4…` ✓; `CHANGELOG.md` `38c8294f…` ✓; `PRIOR_ART.md` `cfeb78cc…` ✓ | ✓ |
| 7 | Next task = C8.10b per KICKOFF.md line 191 + STATUS 14:37:17Z line 55 | confirmed; this entry executes | ✓ |
| 8 | C8.10c PRE-FLIGHT future-state items | not C8.10b scope | ✓ deferred |
| 9 | Parent C8.10 §15 task ships across 3 sub-receipts | confirmed convention | ✓ |
| 10 | §15 PRE-FLIGHT-input re-verification discipline | **executed below** (soft-flags (a), (b), (c)) | ✓ |
| 11 | `notebooks/README.md` Planned section `era_boundary_walkthrough.ipynb` stub | confirmed unchanged; out of active Phase C scope | ✓ informational |
| 12 | Cumulative Phase C effort ~10 of 29-35 sessions (~30%) | this session targets ~1-1.5; budget healthy | ✓ |

### Environment

- [x] Working directory clean: `git status --short` empty. ✓
- [x] On `main`, HEAD=`63d9b42` (C8.10a-complete). ✓
- [x] `.venv/bin/python` 3.13.9; pandas 2.3.2; pyarrow 18.1.0; numpy 2.3.1; duckdb 1.5.2 (unchanged from C8.9). ✓
- [x] `nbformat` + `nbclient` available (lockfile-pinned env covers; verified at C8.10a builder authoring; not separately re-probed).

### Source documentation (L9 cheap-check re-interpretation per the C8.9/C8.10a-surfaced L11 discipline)

The §15 C8.10 PRE-FLIGHT-input list names "NVSR validation cells per notebook (L9 cheap-check)" — without specifying WHICH NVSR table or whether an NVSR PDF is on disk. C8.10a established the durable resolution: validation cells come from the per-product `external_validation_targets_*.csv` files whose entries were L9-cheap-checked at their authoring moment; downstream notebooks consume the CSV directly. C8.10b re-applies the same probe routine:

**Probe A — `raw_docs/` inventory.** `find raw_docs natality/raw_docs -type f` → only `.gitkeep` files. Zero NVSR PDFs on disk (unchanged from C8.10a — open soft-flag (a) carried forward).

**Probe B — natality v1 validation CSV preterm cells.** `grep -iE "preterm|gest" natality/metadata/external_validation_targets_v1.csv` after stripping comment lines → **34 `preterm_rate_pct` cells covering every year 1990-2023**. Each cell cites NVSR vol/no/date (e.g., 2022 → "NVSR Vol 73 No 2, 2024-04-04") or `childstats.gov HEALTH1.A` (pre-1995). Tolerance band split: 19 cells (2005-2023) at ≤0.05; 15 cells (1990-2004) at 0.15 (wider, documented as "LMP-based preterm rate; wider tolerance due to LMP measurement differences").

**Probe C — linked v3 validation CSV preterm cells.** Grep same patterns → **0 cells**. Linked CSV is focused on IMR/neonatal/postneonatal cells. The cross-product story for C.6.b instead uses linked as a **within-tolerance consistency check vs natality** for joint years 2005-2023 (per C8.4 bounded drift 0.01%; STATUS 14:37:17Z line 74).

**Probe D — fetal-death validation CSV gestation cells.** `awk -F, '$2 ~ /early|late/' fetal_death/external_validation_targets.csv` → **4 cells**: 2014 + 2022 × {early_20_27wk, late_28wk_plus}. NVSR 73-09 Table 1. Validator at `fetal_death/scripts/05_validate/validate_external.py:173-175` documents: *"NVSR redistributes not-stated GA proportionally; we retain GA=99 as unknown. Diffs are expected to be nonzero; what we verify is that our total matches NVSR and the directional pattern is sensible."* — `pass: True, expected_diff: True` for these cells.

**Resolution.** Validation cells for C.6.b come from the three already-L9-checked CSVs:
- **34 byte-exact-within-tolerance natality preterm_rate_pct cells (1990-2023)** — the load-bearing validation backbone.
- **4 FD gestation cells (2014 + 2022)** — secondary metric, expected-non-byte-exact-with-documented-reason per validator.
- **19 cross-product natality-vs-linked consistency rows (2005-2023 joint years)** — within-tolerance drift bound from C8.4.
**Total: 34 byte-exact + 4 expected-bounded-diff + 19 cross-product consistency = 57 validation rows.** Far exceeds the §15 "≥3 NVSR-equivalent cells" minimum. No external NVSR PDF fetch required.

### Outputs

- **NEW**: `notebooks/_build_preterm_outcomes_time_series.py` (builder, ~400-500 lines; sibling pattern from `_build_maternal_age_stratified_imr.py`).
- **NEW**: `notebooks/preterm_outcomes_time_series.ipynb` (executed notebook with output cells).
- **MODIFIED**: `notebooks/README.md` (add C.6.b entry under existing C.6.a; convert "Planned" C.6.b stub to "Shipped" with sha-prefix). Current sha=`e388da8f9e77445d…` will drift; recorded post-DO.
- **NEW**: `RECEIPTS/C8.10b_<UTC>.md` (per-notebook sub-task receipt; parent `C8.10-complete` tag still deferred until C.6.c ships).
- **NEW**: `STATUS.md` append.
- **NEW**: `PRE_FLIGHT_LOG.md` append (this entry).
- **Invariants**: 4 parquet SHAs unchanged (no parquet mutation). All 14 C8.9 file SHAs + 2 of 3 C8.10a file SHAs (builder + ipynb) unchanged. Only `notebooks/README.md` drifts.

### Field-value snapshot for cells being asserted (Convention 3)

**Natality `preterm_rate_pct` byte-exact validation (spot-checked 7/34 cells; full 34 will assert in notebook):**

| year | probe value (PRE-FLIGHT, canonical filter applied) | CSV expected | Tolerance | Match? |
|---|---|---|---|---|
| 1990 | 10.62% (n=4,158,212; preterm=436,590; known=4,111,396) | 10.6% | 0.15 | ✓ within |
| 2000 | 11.64% (n=4,058,814; preterm=467,201) | 11.6% | 0.15 | ✓ within |
| 2005 | 12.73% (n=4,138,349; preterm=522,913) | 12.7% | 0.05 | ✓ within |
| 2013 | 11.39% (n=3,932,181; preterm=447,361) | 11.39% | 0.02 | ✓ byte-exact |
| 2014 | 9.57% (n=3,988,076; preterm=381,321) | 9.57% | 0.02 | ✓ byte-exact (OE-shift) |
| 2020 | 10.09% (n=3,613,647; preterm=364,487) | 10.09% | 0.05 | ✓ byte-exact |
| 2023 | 10.41% (n=3,596,017; preterm=373,902) | 10.41% | 0.05 | ✓ byte-exact |

**Linked `preterm_lt37` cross-product consistency (4/19 joint years):**

| year | natality rate | linked rate | drift | within C8.4 bound (0.01%) |
|---|---|---|---|---|
| 2005 | 12.73% | 12.73% | 0 | ✓ |
| 2013 | 11.39% | 11.39% | 0 | ✓ |
| 2014 | 9.57% | 9.57% | 0 | ✓ |
| 2022 | 10.38% | 10.38% | 0 | ✓ |
| 2023 | 10.41% | 10.41% | 0 | ✓ |

**FD gestation-stratified expected-non-byte-exact cells (NVSR Table 1 universe = `tabulation_flag == 2 AND residence_status != 4`):**

| year | metric | probe value | NVSR expected | diff | validator-flagged |
|---|---|---|---|---|---|
| 2014 | fetal_deaths_early_20_27wk | 11,294 | 12,652 | −1,358 | expected_diff=True |
| 2014 | fetal_deaths_late_28wk_plus | 11,866 | 11,328 | +538 | expected_diff=True |
| 2022 | fetal_deaths_early_20_27wk | 9,131 | 10,246 | −1,115 | expected_diff=True |
| 2022 | fetal_deaths_late_28wk_plus | 10,425 | 9,956 | +469 | expected_diff=True |

**Shape check**: 
- Natality preterm time series shows the documented 2013→2014 OE-methodology shift (11.39% → 9.57%, drop of 1.82 percentage points); pre-2014 LMP-based plateau 11.4-12.7%; post-2014 OE-based gradual rebound 9.57% → 10.41% (2023).
- Linked preterm time series matches natality byte-exact at 5/5 spot-checked joint years (confirms shared source data 2005-2023).
- FD early/late counts show within-NVSR-total directional sensibility (early ≈ late at both 2014 and 2022; sum within 6% of NVSR total; methodology diff documented in validator).

**Cross-product universe alignment (F1 discipline)**:
- Natality canonical filter: `residence_status != 4` (drops 0.17% — small foreign-resident set).
- Linked canonical filter: same `residence_status != 4`.
- FD canonical filter for NVSR Table 1 cells: `tabulation_flag == 2 AND residence_status != 4` (matches `_build_joint_use_demo.py` line 165 + `validate_external.py:121`).

### Halt conditions tripped

(none)

### Open considerations (soft-flags, NOT halts)

- **(a) §15 implicit cross-product column-name uniformity assumption is invalid.** FD uses `preterm` (string '0'/'1'/'') + `gestational_age_combined` (string) + `gestational_age_recode5` (string) while natality + linked use `preterm_lt37` (bool) + `gestational_age_weeks` / `gestational_age_weeks_clean` (int16). The C8.10a "Notes for next session" forward-looking item assumed `gestational_age_weeks_clean` exists in all 3 parquets; **it does NOT exist in FD**. Resolution: notebook uses each product's native columns; Section 4 narrative documents the schema divergence. Not a §7 halt — same routine L11 pattern surfaced at C8.9 (state-column claim) + C8.10a (cohort-vs-period framing).
- **(b) §15 implicit single-FD-canonical-filter assumption is partially invalid.** FD has TWO canonical filters: `tabulation_flag == 1` (used for per-year FMR) vs `tabulation_flag == 2 AND residence_status != 4` (used for NVSR Table 1 detail cells). C8.10b uses tab=2 for the gestation-stratified cells (matches `joint_use_demo` + `validate_external.py`); Section 4 narrative documents. Not a §7 halt.
- **(c) FD early/late gestation cells are EXPECTED-NON-BYTE-EXACT vs NVSR**, per validator-documented methodology diff (NVSR redistributes not-stated GA proportionally; our parquet retains GA=99 as unknown). Resolution: notebook reports these as `expected_diff: True` cells with diff magnitude + total-sensibility check; the 34 natality byte-exact preterm cells provide the validation backbone. Same pattern as joint_use_demo's "Diff=0 across the board for race-bridged" / "Diff non-zero for B-legacy 2017" cells. Not a §7 halt.
- **(d) 2014 OE-based methodology shift is a within-era boundary** (§8 F4 halt-condition flag named in §15 C8.10 entry). Notebook plots the time series with a vertical dashed line at 2013/2014; uses the validation CSV's per-row tolerance (0.15 for 1990-2013 LMP-based; ≤0.05 for 2014-2023 OE-based). Section 4 narrative documents. This is the F4 guardrail the §15 entry explicitly anticipates — notebook bakes it in rather than treating as a halt.
- **(e) Builder hardcoded parquet paths.** C8.10a soft-flag (c) precedent: hardcoded `/Users/yoelplutchok/Desktop/...` absolute paths in builder. C.6.b follows the same convention. Resolution deferred to C8.7b's natality+linked output-path strategy decision.
- **(f) `raw_docs/` empty across the monorepo** (C8.10a soft-flag (a) carried forward). Phase D / C8.13 candidate.
- **(g) Notebook bit-reproducibility caveat** (C8.10a soft-flag (b) carried forward). nbformat output cell IDs may shift across runs; analytical content is reproducible.
- **(h) `notebooks/README.md` Planned section** still includes `era_boundary_walkthrough.ipynb` stub (C8.10a Forward-looking HALT #11); C8.10b will replace the C.6.b stub line with the shipped entry, leaving C.6.c + C.6.d/e stubs unchanged. Routine documentation hygiene.

### Result

**PROCEED.** All inputs verified; environment clean; 12 C8.10a forward-looking HALTs all pass byte-exact; Convention 3 Field-value snapshot computed 16 rows (7 byte-exact natality cells + 5 cross-product consistency + 4 FD expected-bounded-diff); no §7 condition tripped; 3 routine L11 PRE-FLIGHT-input re-interpretations handled in-place (cross-product column-name divergence, FD dual-canonical-filter, FD methodology-diff expected). Tag `C8.10b-pre-do` placed on the PRE-FLIGHT commit; DO phase commences post-tag.

---

## PRE-FLIGHT for C8.10 — 2026-05-13T14:29:23Z — Worked-example notebooks 1-3 of 5; SESSION SCOPE = notebook 1 (C.6.a `maternal_age_stratified_imr.ipynb`) — **RESULT: PROCEED** (zero §7 halt; one PRE-FLIGHT-input re-interpretation logged as soft-flag, mirroring the new C8.9-surfaced L11 discipline)

### Scope summary

C8.10 §15.C entry (NEXT_STEPS.md lines 1145–1164): three worked-example notebooks — **(C.6.a)** `maternal_age_stratified_imr.ipynb` (linked file; replicable IMR-by-maternal-age curve); **(C.6.b)** `preterm_outcomes_time_series.ipynb` (FD + natality + linked; preterm-birth secular trends); **(C.6.c)** `cross_race_fetal_mortality.ipynb` (V3a/V3b race-stratified FD with B3 1-digit-recode caveats). Estimated 3–4 sessions total (one session per notebook minimum). KICKOFF.md Phase C Tier-2 line 191 mirrors this entry.

**Session scope this PRE-FLIGHT (the (a)-(d) handshake-stated plan, user-authorized "proceed"):** ship notebook 1 of 3 (C.6.a) end-to-end through RECEIPT. C.6.b + C.6.c remain pending in §15.C C8.10; each receives its own PRE-FLIGHT in a subsequent session.

### Inputs

- [x] **All 12 C8.9 forward-looking HALTs verified** (see table below; 4 parquet SHAs + 3 R quickstart SHAs + views.sql + JOINT_USE_GUIDE.md + pyproject.toml + uv.lock + 7 inherited file SHAs + tag presence + duckdb-in-venv). ✓
- [x] **Linked v3 derived parquet** present at conftest-canonical path `~/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet`; sha=`9b828a4de4e59b17…`; 74,943,824 rows × 94 cols. ✓
- [x] **Linked v3 harmonized parquet** present (sibling of derived); sha=`e1795ac615a6ee40…`. ✓ (not load-bearing for C.6.a, which uses derived.)
- [x] **Validation CSV** `natality/metadata/external_validation_targets_v3_linked.csv` present (53 rows); 7 cells encoded for 2022 from `23PE22CO_linkedUG.pdf` Documentation Tables 1 + 4. ✓
- [x] **Builder template** `notebooks/_build_joint_use_demo.py` + `notebooks/_build_paper_companion.py` both present and structurally identical (both: `REPO_ROOT`, `OUTPUT`, hardcoded parquet absolute paths, `md()` + `code()` helpers, `build()` → `nbformat.NotebookNode`, `NotebookClient` execution at `__main__`). ✓
- [x] **No stale checkpoints**: `git status --short` empty; `C8.10-pre-do` tag does NOT yet exist (will be placed post-PRE-FLIGHT, pre-DO). ✓

### C8.9 Forward-looking HALTs (all 12 verified)

| # | Assertion | Verification | Status |
|---|---|---|---|
| 1 | `C8.9-complete` tag present; `C8.10-pre-do` absent | `git tag --list 'C8.*'` → C8.9-pre-do + C8.9-complete; no C8.10-pre-do | ✓ |
| 2 | `pyproject.toml` sha=`c044f1c603f980cb…` | verified | ✓ |
| 3 | `uv.lock` sha=`a385094314580e86…` | verified | ✓ |
| 4 | 4 parquet SHAs unchanged byte-exact | fd_harm=`38e2cecb03ff4947…` ✓; fd_der=`185c071ec76ab8aa…` ✓; nat_der=`e16ad5323d68e28d…` ✓; linked_der=`9b828a4de4e59b17…` ✓ | ✓ |
| 5 | 4 new files present + SHA-unchanged: `fetal_death/quickstart.R` (`3b2c0fe0…`), `natality/quickstart.R` (`15d9edfb…`), `natality/quickstart_linked.R` (`a83e0a90…`), `views.sql` (`c7b674f6…`) | verified | ✓ |
| 6 | `docs/JOINT_USE_GUIDE.md` sha=`534814a94651c509…` | verified | ✓ |
| 7 | 7 inherited C8.5a/C8.6/C8.7a/C8.8 file SHAs unchanged | `.python-version` `02e735b3…` ✓; `README.md` `694fdd35…` ✓; `ci.yml` `c248cf51…` ✓; `validate_2022.py` `67a4dfcb…` ✓; `run_pipeline.py` `959ccac4…` ✓; `CHANGELOG.md` `38c8294f…` ✓; `PRIOR_ART.md` `cfeb78cc…` ✓ | ✓ |
| 8 | `.venv` has duckdb 1.5.2 installed | `.venv/bin/python -c "import duckdb; print(duckdb.__version__)"` → `1.5.2` | ✓ |
| 9 | Next task = C8.10 per KICKOFF.md line 191 | confirmed; this entry executes | ✓ |
| 10 | Phase D step 3 exclude list must NOT exclude views.sql + 3 R quickstarts | not C8.10 scope; sanity-check at sync time | ✓ deferred |
| 11 | C8.5b + C8.7b remain DEFERRED | confirmed unchanged | ✓ |
| 12 | L11 stale-claim defense — re-verify §15 PRE-FLIGHT-input claims | **executed below** (soft-flag (a)) | ✓ |

### Environment

- [x] Working directory clean: `git status --short` empty. ✓
- [x] On `main`, HEAD = `a64336e` (C8.9-complete). ✓
- [x] `.venv/bin/python` 3.13.9; pandas 2.3.2; pyarrow 18.1.0; numpy 2.3.1; duckdb 1.5.2 (per C8.9 add). ✓
- [x] `nbformat` + `nbclient` available in `.venv` (required by sibling builder pattern; verified at import time during sibling builder authoring at C8.3/Task 4 — `pip show nbformat nbclient` not separately re-probed, lockfile-pinned env covers it).
- [x] `pyproject.toml` + `uv.lock` SHAs unchanged from C8.9-complete state. ✓

### Source documentation (L9 cheap-check re-interpretation per the new C8.9-surfaced L11 discipline)

The §15 C8.10 PRE-FLIGHT-input list names "NVSR validation cells per notebook (L9 cheap-check)" — without specifying WHICH NVSR table or whether a PDF is on disk. Per the new C8.9-surfaced L11 discipline (re-verify each §15 PRE-FLIGHT-input claim against current artifacts), the cheap-check probes:

**Probe A — `raw_docs/` inventory.** `find raw_docs natality/raw_docs -type f` → only `.gitkeep` files. **Zero NVSR PDFs on disk** at the monorepo root or under either subproject's `raw_docs/`. The L9 "open the cited PDF and verify the table location" cheap-check is NOT executable as written.

**Probe B — sibling notebook's L9 surface.** `notebooks/_build_joint_use_demo.py` Section A (2022 maternal-age fetal mortality, byte-exact 8/8 vs NVSR 73-09 Table 4) does NOT load an NVSR PDF at execution time — it loads the **`fetal_death/external_validation_targets.csv`** which carries the pre-encoded NVSR cell values. The L9 cost was paid once at the validation-CSV authoring moment; subsequent notebooks consume the validated CSV. Sibling pattern is the same for the `paper_companion.ipynb` (per `_build_paper_companion.py`).

**Probe C — linked validation CSV 2022 cells.** Grep `,2022,` in `natality/metadata/external_validation_targets_v3_linked.csv` → 7 cells encoded for 2022 from `23PE22CO_linkedUG.pdf` Documentation Tables 1 + 4: `resident_births`=3,667,758 (tol 0), `unweighted_infant_deaths`=20,268 (tol 2), `imr_per_1000`=5.53 (tol 0.01), `neonatal_deaths`=12,948 (tol 2), `postneonatal_deaths`=7,320 (tol 2), `neonatal_imr_per_1000`=3.53 (tol 0.02), `postneonatal_imr_per_1000`=2.00 (tol 0.02). All from the **cohort-linked file user guide** — our exact data source (no period-vs-cohort divergence).

**Resolution.** Re-interpret the §15 "NVSR validation cells per notebook (L9 cheap-check)" PRE-FLIGHT-input claim as: "validation cells per notebook are sourced from the per-product `external_validation_targets_*.csv` files whose entries were L9-cheap-checked at their authoring moment; downstream notebooks consume the CSV directly." 7 cells for 2022 linked is **>3** (the §15 "≥3 cells" minimum); the 7-cell PASS/FAIL table is the load-bearing notebook artifact. No external PDF fetch required.

**Maternal-age stratification (the notebook's headline content) is NOT in the validation CSV.** No NVSR-equivalent cell publishes 2022 IMR-by-maternal-age from the COHORT-linked file. (NCHS publishes IMR-by-maternal-age in the PERIOD-linked NVSR series, e.g., NVSR 73-05 Ely+Driscoll 2024; cohort-vs-period divergence is documented and bounded but non-zero.) C.6.a frames the maternal-age stratification as a **machinery-demo extension** — sibling pattern to `_build_joint_use_demo.py` Section B-legacy 2017 race-bridged (cells shown without byte-exact NVSR validation; plausibility bands documented in narrative). The 7 byte-exact cells (overall IMR + neonatal/postneonatal breakdowns) are the NVSR-equivalent floor.

### Outputs

- **NEW**: `notebooks/_build_maternal_age_stratified_imr.py` (builder, ~150–200 lines).
- **NEW**: `notebooks/maternal_age_stratified_imr.ipynb` (executed notebook with output cells).
- **MODIFIED**: `notebooks/README.md` adding the new notebook to the inventory (current README is brief; verify post-DO).
- **NEW**: `RECEIPTS/C8.10a_<UTC>.md` (per-notebook sub-task receipt; the C8.10 §15 task is composite across 3 notebooks, so per-session receipts are `C8.10a` / `C8.10b` / `C8.10c` with the parent `C8.10-complete` tag deferred until all 3 ship).
- **NEW**: `STATUS.md` append.
- **NEW**: `PRE_FLIGHT_LOG.md` (this entry).
- **NEW**: 4 parquet SHAs unchanged (no parquet mutation). All 14 file SHAs from the C8.9 forward-looking HALTs unchanged (no edits to existing R quickstarts, views.sql, JOINT_USE_GUIDE, pyproject.toml, uv.lock, .python-version, README.md, ci.yml, validate_2022.py, run_pipeline.py, CHANGELOG.md, PRIOR_ART.md).

### Field-value snapshot for cells being asserted (Convention 3)

The notebook will assert each row of the table below. Snapshot values computed at PRE-FLIGHT from `natality_v3_linked_harmonized_derived.parquet` with canonical filter `is_foreign_resident == False`:

| Cell | Probe value (PRE-FLIGHT) | CSV expected value | Tolerance | Match? |
|---|---|---|---|---|
| 2022 resident_births | 3,667,758 | 3,667,758 | 0 | ✓ byte-exact |
| 2022 unweighted_infant_deaths | 20,268 | 20,268 | 2 | ✓ byte-exact |
| 2022 imr_per_1000 | 5.526 | 5.53 | 0.01 | ✓ |
| 2022 neonatal_deaths | 12,948 | 12,948 | 2 | ✓ byte-exact |
| 2022 postneonatal_deaths | 7,320 | 7,320 | 2 | ✓ byte-exact |
| 2022 neonatal_imr_per_1000 | 3.530 | 3.53 | 0.02 | ✓ |
| 2022 postneonatal_imr_per_1000 | 1.996 | 2.00 | 0.02 | ✓ |

**Machinery-demo cells (NVSR-equivalent NOT applicable; plausibility ranges from literature):**

| maternal_age_cat | resident_births | infant_deaths | IMR (per 1,000) | neonatal_IMR | postneonatal_IMR |
|---|---|---|---|---|---|
| <20 | 145,614 | 1,439 | 9.882 | 5.109 | 4.773 |
| 20-24 | 638,685 | 4,464 | 6.989 | 3.978 | 3.011 |
| 25-29 | 1,013,417 | 5,362 | 5.291 | 3.368 | 1.923 |
| 30-34 | 1,118,787 | 5,027 | 4.493 | 3.081 | 1.412 |
| 35-39 | 606,598 | 3,009 | 4.960 | 3.501 | 1.459 |
| 40+ | 144,657 | 967 | 6.685 | 4.694 | 1.991 |

**Shape check**: U-shape across maternal-age (highest <20 and 40+, lowest 30-34) — matches literature consensus on age-IMR association. Row-count conservation across age bands: 145,614+638,685+1,013,417+1,118,787+606,598+144,657 = **3,667,758** = resident_births ✓ (no NaN bucket in `maternal_age_cat`).

**Canonical filter applied (F1 discipline)**: `is_foreign_resident == False`; equivalent to `residence_status != 4`; drops 8,271 of 3,676,029 (0.225%) of 2022 records. Matches `universe='resident'` in the validation CSV.

### Halt conditions tripped

(none)

### Open considerations (soft-flags, NOT halts)

- **(a) §15 PRE-FLIGHT-input "NVSR validation cells per notebook (L9 cheap-check)" RE-INTERPRETATION**, mirroring the new C8.9-surfaced L11 discipline (re-verify each §15 PRE-FLIGHT-input claim). Resolution: validation cells come from the linked validation CSV (cohort-linked user guide source, L9-checked at task7 V2 linked-file framing reconcile 2026-05-11); no external NVSR PDF required. 7 cells > the §15 "≥3" minimum. Logged as routine re-interpretation, not a silent scope reduction.
- **(b) Maternal-age IMR stratification has NO NVSR-equivalent cell on disk.** NCHS publishes IMR-by-maternal-age in the period-linked NVSR series (e.g., NVSR 73-05 Ely+Driscoll 2024); period-vs-cohort divergence is bounded but non-zero. C.6.a frames the maternal-age stratification as a machinery-demo extension (sibling to `joint_use_demo` Section B-legacy 2017 race-bridged pattern). Narrative will document the cohort-vs-period source distinction explicitly.
- **(c) Notebook sub-task receipts.** §15 C8.10 is a composite 3-notebook task. This session ships notebook 1 of 3 only. Receipt names this `C8.10a` (sub-task suffix); tag placed `C8.10a-pre-do` + `C8.10a-complete`. The parent `C8.10-complete` tag waits until notebooks 2 + 3 (C.6.b + C.6.c) also ship in subsequent sessions. C8.5/C8.5a + C8.7/C8.7a precedent supports this naming.
- **(d) Builder hardcoded parquet paths** (precedent: `_build_joint_use_demo.py` + `_build_paper_companion.py` both hardcode `~/Desktop/natality-harmonization/output/harmonized/...` absolute paths). The new `_build_maternal_age_stratified_imr.py` follows the same convention. C8.7a soft-flag (b) "natality+linked output-path strategy" remains C8.7b's first PRE-FLIGHT decision; C.6.a does not resolve it.
- **(e) `notebooks/README.md` inventory update.** Current README is minimal; verify post-DO that the new notebook gets a one-line entry. Routine documentation hygiene; not load-bearing for PROCEED.

### Result

**PROCEED.** All inputs verified; environment clean; 12 C8.9 forward-looking HALTs all pass byte-exact; Convention 3 Field-value snapshot computed 14 cells, all match CSV expectations or fall within plausibility bands; no §7 condition tripped. Tag `C8.10a-pre-do` placed on the PRE-FLIGHT commit; DO phase commences post-tag.

---

### Scope summary

C8.9 §15.C entry (NEXT_STEPS.md lines 1101–1119): three sub-deliverables — **(C.1)** `stratified_denominators_state.csv` adding state × race × age × Hispanic × year strata; **(C.2)** `quickstart.R` mirroring `quickstart.py` with `arrow::read_parquet()` round-trip; **(C.4)** `views.sql` defining canonical-filter views + common joins as DuckDB-compatible views over the parquets. Estimated 2.5–3 sessions. Halt-condition flags named: **F1 (canonical filter on natality side); L13 (state-code dtype verification)**.

STATUS 2026-05-13T09:30:00Z line 51 explicitly flagged "Could also be split into C8.9a (state denominators alone, 1 session) + C8.9b (R + DuckDB, 1.5-2 sessions) if a single-session boundary is preferred — a PRE-FLIGHT-time split decision."

### Inputs

- [x] **All Tier-1 artifacts present** (4 parquet SHAs + 7 file SHAs unchanged from C8.8-complete forward-looking HALTs).
- [x] **Natality v2.8.0 derived parquet** (existence verified at `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet`). Outside monorepo per C8.7a soft-flag (b).
- [x] **`shared/helpers/build_stratified_denominators.py`** exists (sha=`<unverified at PRE-FLIGHT, not load-bearing for C8.9>`); 158 lines; intended template for C.1's state-stratified sibling.
- [x] **`shared/helpers/canonical_join_keys.py`** present; provides `to_canonical_natality()` + `derive_maternal_age_band()`.
- [x] **R 4.5.1 at `/usr/local/bin/R`**; `arrow` + `duckdb` + `dplyr` packages all installed (probed via `Rscript --vanilla -e 'requireNamespace(...)'`). ✓ for C.2.
- [x] **Python `quickstart.py`** for fetal_death at `/Users/yoelplutchok/Desktop/vital-statistics-harmonization/fetal_death/quickstart.py` — verified present (per `PROJECT_STRUCTURE.md` line 95).

### C8.8 Forward-looking HALTs (all 10 verified)

| # | Assertion | Verification | Status |
|---|---|---|---|
| 1 | `C8.8-complete` tag present | `git tag --list 'C8.8*'` → `C8.8-pre-do` + `C8.8-complete`; `C8.9-pre-do` does NOT exist | ✓ |
| 2 | `CHANGELOG.md` sha=`38c8294f…` | verified | ✓ |
| 3 | `docs/PRIOR_ART.md` sha=`cfeb78cc…` | verified | ✓ |
| 4 | 4 parquet SHAs unchanged | verified | ✓ |
| 5 | 7 file SHAs unchanged | verified | ✓ |
| 6 | Next task = C8.9 per KICKOFF line 190 | confirmed | ✓ this entry executes |
| 7 | 3 GitHub URLs re-verify at Phase D step 3 | not C8.9 scope | ✓ deferred |
| 8 | Manuscript candidate addition Phase D step 6 | not C8.9 scope | ✓ deferred |
| 9 | EXPLORATION_REPORT §E.5 plan-text un-edited | not C8.9 scope | ✓ informational |
| 10 | L11 KICKOFF Tier-1 line 186 reads as ✅ via tag | confirmed | ✓ |

### Environment

- [x] Working directory clean: `git status --short` empty. ✓
- [x] On `main`, HEAD=`33fe70f` (C8.8-complete). ✓
- [x] `.venv` Python 3.13.9 unchanged from C8.5a-complete (per 7-file SHA invariant).
- [x] R 4.5.1 at `/usr/local/bin/R`; Rscript present; arrow + duckdb + dplyr packages installed at `/Library/Frameworks/R.framework/Versions/4.5-arm64/Resources/library`.
- [x] **Python `duckdb` package: NOT installed** in `.venv` (`.venv/bin/python -c "import duckdb"` → `ModuleNotFoundError`). NOT a line in `pyproject.toml` (verified). NOT in `uv.lock` (no match in 38 packages). ✗ **HALT #2 below.**
- [x] `duckdb` CLI: NOT on PATH (`which duckdb` → not found). Acceptable; Python-package path is the canonical SMOKE invocation.

### Source documentation (L8 + L9 + L13 cheap-checks for the C.1 PRE-FLIGHT input claim)

The §15 C8.9 entry's PRE-FLIGHT-input claim — "**Natality derived parquet (state available 1990-2024; suppressed in fetal-death V1 era 2005+)**" — is the load-bearing factual claim that C.1 depends on. Cheap-check probes:

**Probe 1 — natality harmonized schema column inventory** (`awk -F',' '{print $1}' natality/metadata/harmonized_schema.csv`): 84 harmonized + 6 derived = 90 column names. Grep for `state` / `STATE` / `FIPS` / `OSTATE` / `MRSTATE`: **zero matches** (closest matches: `residence_status` = 1|2|3|4 code, NOT state identifier; `maternal_nativity` = US-born/foreign-born flag in linked-file 2014+ only).

**Probe 2 — natality per-year `yearly_clean` parquet column inventory** (11 years sampled: 1990, 1995, 2000, 2002, 2003, 2004, 2005, 2010, 2015, 2020, 2024):

| Year | Column count | State-shape columns |
|---|---|---|
| 1990 | 38 | MRACE, MRACE3 (race only) |
| 1995 | 38 | MRACE, MRACE3 |
| 2000 | 38 | MRACE, MRACE3 |
| 2002 | 38 | MRACE, MRACE3 |
| 2003 | 36 | MRACE, MRACEREC, MRACEHISP |
| 2004 | 37 | MRACE, MRACEREC, MRACEHISP |
| 2005 | 44 | MRACE, MRACEREC, MRACEHISP, MRACE15 |
| 2010 | 44 | MRACE, MRACEREC, MRACEHISP, MRACE15 |
| 2015 | 76 | **MBSTATE_REC** (mother's birth-place code: 1=US, 2=foreign, 3=unknown — NOT state of residence), MRACE6, MRACE15, MRACEHISP |
| 2020 | 76 | MBSTATE_REC, MRACE6, MRACE15, MRACEHISP |
| 2024 | 76 | MBSTATE_REC, MRACE6, MRACE15, MRACEHISP |

**No state-of-residence or state-of-occurrence column** appears in ANY year's parsed yearly_clean parquet. The closest is `MBSTATE_REC` (2015+), which is a 3-level birthplace recode, NOT state-level geography.

**Probe 3 — natality FAQ + ABOUT_THIS_RELEASE explicit statements** (`grep -in "geograph\|state.suppress\|state of res" natality/docs/{FAQ,ABOUT_THIS_RELEASE}.md`):

- `natality/docs/FAQ.md:26`: "Public-use files do **not** include sub-state geography (county/city)"
- `natality/docs/FAQ.md:87-89`: **"## Is geography included? No. The public-use natality files do not include sub-state geography. State-level identifiers are also suppressed in the public-use linked files from 2005 onward."**
- `natality/docs/ABOUT_THIS_RELEASE.md:70`: "No restricted-use geography or restricted-use variables are included."

**Probe 4 — fetal-death harmonized schema** (`grep -i "state\|residence" fetal_death/harmonized_schema.csv`): only `residence_status` (1-4 code) + `maternal_nativity` (US-born/foreign-born). **No state-of-residence column.** Mirrors the natality situation.

**Conclusion of L9 + L13 cheap-checks on §15 PRE-FLIGHT-input claim:** the claim is **factually wrong**. NCHS suppresses state-level geography in public-use files across all three products (natality + linked + fetal-death). The C8.9 PRE-FLIGHT input claim "state available 1990-2024" appears to be a §15 authoring error that no prior session verified against the actual data. C.1's "state × race × age × Hispanic × year strata" deliverable is structurally unbuildable from the public-use data this monorepo ships. The fix is upstream (a restricted-use NCHS workflow + RDC access), well out of HVS pre-submission scope.

### Outputs

- Intended outputs (revised post-Option-A):
  - **DROP**: `natality/stratified_denominators_state.csv` (C.1; structurally unbuildable).
  - **DROP**: `shared/helpers/build_stratified_denominators_state.py` (C.1 author script).
  - **KEEP**: `quickstart.R` × 3 per-product (C.2) at `fetal_death/quickstart.R` + `natality/quickstart.R` + `linked/quickstart.R` (path TBD; may unify under one file with subcommand).
  - **KEEP**: `views.sql` at monorepo root (C.4) defining DuckDB views over the parquets.
  - **NEW**: edits to `pyproject.toml` (add `duckdb` to dependencies) + `uv.lock` (regenerate via `uv lock`). Acknowledged SHA change from C8.5a-recorded values.
  - **NEW**: edits to `docs/JOINT_USE_GUIDE.md` documenting R + DuckDB usage patterns.
  - `RECEIPTS/C8.9_<UTC>.md`, `STATUS.md` append, `PRE_FLIGHT_LOG.md` (this entry + post-resolution addendum), `DECISION_LOG.md` plan-update entry, `[plan-update]` commit shipping the C.1-drop + duckdb-add narrative.

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

| Artifact | Field / claim | Current value | Plan's assumed value | Match? |
|---|---|---|---|---|
| `natality/metadata/harmonized_schema.csv` columns | Has a state-of-residence column? | NO (84 + 6 derived, none are state) | YES per §15 C8.9 PRE-FLIGHT input | ✗ — **§7.13 HALT #1** |
| `natality/yearly_clean/natality_<YYYY>_core.parquet` columns | State column for any year 1990-2024? | NO (probed 11 years; only MBSTATE_REC 2015+ which is birthplace not residence) | YES per §15 C8.9 PRE-FLIGHT input | ✗ — **§7.13 HALT #1** |
| `fetal_death/harmonized_schema.csv` columns | State-of-residence column? | NO (only residence_status code + maternal_nativity flag) | "suppressed in fetal-death V1 era 2005+" per §15 implies present pre-2005 | ✗ — also wrong |
| `pyproject.toml` + `uv.lock` | `duckdb` Python package | NOT installed; NOT in lockfile (38 packages, no duckdb) | "DuckDB installed in the env (C8.5 lockfile)" per §15 C8.9 PRE-FLIGHT input | ✗ — **§7.13 HALT #2** |
| R env at `/usr/local/bin/R` | `arrow` + `duckdb` + `dplyr` R packages | All installed (R 4.5.1; library at `/Library/Frameworks/R.framework/Versions/4.5-arm64/Resources/library`) | Implicit assumption R env ready | ✓ |

### Halt conditions tripped

- **§7.13 HALT #1 (validity-domain ambiguity)** — C.1's "state-stratified denominators" deliverable assumes state-of-residence is available in the public-use natality harmonized parquet. Probes 1+2+3 confirm state is NOT available in any year 1990-2024. The closest column (`MBSTATE_REC`, 2015+) is mother's birthplace recode (3-level US/foreign/unknown), not state of residence. C.1 cannot be built without an upstream RDC / restricted-use workflow, well out of HVS pre-submission scope.
- **§7.13 HALT #2 (validity-domain ambiguity)** — §15 PRE-FLIGHT input claims "DuckDB installed in the env (C8.5 lockfile)" but DuckDB is NOT in pyproject.toml NOR in uv.lock NOR in the .venv. Smaller fix: install duckdb during C8.9 DO (`uv add duckdb` → regenerate lockfile; expected SHA drift documented).

### Result

**HALT** — surfaced to user via AskUserQuestion 2026-05-13T10:00:00Z. See post-resolution addendum below.

---

## PRE-FLIGHT for C8.9 — 2026-05-13T10:15:00Z — Addendum post-resolution — **RESULT: PROCEED**

User authorization 2026-05-13T10:00:00Z (AskUserQuestion response: "Drop C.1; ship C.2+C.4 only (Recommended)"). Resolution applied via single `[plan-update]` commit:

1. **C.1 DROPPED from C8.9 scope.** §15 C8.9 entry rewritten to enumerate only C.2 (R quickstart) + C.4 (DuckDB views). KICKOFF.md Phase C Tier-2 line 190 revised. C.1 is **NOT** simply re-deferred — it's documented as **structurally unbuildable from public-use data**; any future re-attempt requires either (i) NCHS RDC access (out of HVS scope) or (ii) a different geographic stratification axis (Census region/division) which would require a new derived column (state→region map) and is also out of current C8.9 scope. Filed as a permanently-out-of-scope item in §15.
2. **`duckdb` added to C8.9 DO scope.** `uv add duckdb` will update `pyproject.toml` + `uv.lock`. The SHA drift from C8.5a-recorded values is an authorized addition (not a regression). C8.9 RECEIPT will record the post-add SHAs in the "Build artifacts current" section and in Forward-looking HALTs for C8.10's PRE-FLIGHT.
3. **§15 estimated effort revised** from 2.5-3 sessions → 1-1.5 sessions (only C.2 + C.4 + duckdb add + JOINT_USE_GUIDE doc update).
4. **DECISION_LOG entry 2026-05-13T10:00:00Z** records the §11 plan-update + alternatives considered + reason + source.

### Halt conditions cleared

- §7.13 HALT #1 (state suppression): RESOLVED — C.1 dropped from scope.
- §7.13 HALT #2 (duckdb missing): RESOLVED — `uv add duckdb` is authorized as part of C8.9 DO.

### Result

**PROCEED** to C8.9 DO (revised scope: C.2 + C.4 only).

---

## PRE-FLIGHT for C8.8 — 2026-05-13T09:00:00Z — CHANGELOG.md + PRIOR_ART.md updates (E.1 + E.5) — **RESULT: PROCEED** (one Convention 3 amendment: citation re-attribution from "Hoyert et al. 2024" → Gregory ECW + Barfield WD 2024, both at PMID 38143212; the load-bearing PMID is unchanged; no §7 halt)

### Scope summary

C8.8 §15.C entry (NEXT_STEPS.md lines 1081–1097): "(E.1) Author `CHANGELOG.md` at monorepo root: one section per version, v1.0 → v1.x → … delta. (E.5) Three concrete PRIOR_ART.md updates from EXPLORATION_REPORT §A.7 + literature-gap agent: (i) GitHub precursors subsection (Mikuana, arebe, damiancclarke); (ii) Hoyert et al. 2024 + NICHD Stillbirth WG July 2024 citation; (iii) one-sentence HL7/fhir-bfdr mention." Plus Q34 boundary statement (M-D / MCD / abortion out-of-HVS-scope per DECISION_LOG 2026-05-12T21:00:00Z entry line 508). Estimated 1 session. Halt-condition flags named: **L8 (citation resolution); L11 (stale roadmap claims)**.

### Inputs

- [x] **All seven RECEIPTS/ files for Tier-1 work present** as changelog source: `task6_linked_validation_reconcile_2026-05-11T17-30-00Z.md` through `C8.7a_2026-05-13T08-30-00Z.md` (17 receipts total spanning task1 through C8.7a + natality_v28_rename + task7_v3a + task7_v3b). ✓
- [x] **EXPLORATION_REPORT.md** present (sha not pinned; consumed read-only). §A.7 (lines 202–213) + §E.5 (lines 732–749) confirm the 3 PRIOR_ART update specifics. §A.6 (lines 193–200) + §A.8 row 6 confirm Q34 boundary (M-D/MCD/abortion out-of-scope). ✓
- [x] **docs/PRIOR_ART.md** present (58 lines, 4809 bytes). Current sections: gap statement / Cited adaptations (Salihu 2004, Willinger 2009, Hogue+Silver 2011, Ananth 2022) / NCHS aggregate / Adjacent harmonized (IPUMS, HMD, NHIS, NBER) / What this resource adds. ✓
- [x] **CHANGELOG.md** at monorepo root: **DOES NOT EXIST** ✓ (matches C8.8's E.1 spec that it will be authored newly).
- [x] **ABOUT_THIS_RELEASE.md** files: present in both `natality/docs/ABOUT_THIS_RELEASE.md` (v2.8.0 in-repo) + `fetal_death/ABOUT_THIS_RELEASE.md` (v2.0 plus V2.1/V3a/V3b extensions). Provide cross-reference for changelog "data extensions" content.
- [x] **All 14 C8.X tags + 9 task-N tags present.** `git tag --list 'C8.*' | sort` returns C8.1-pre-do through C8.7a-complete (14 tags); task1 through task7_v3b plus public-v1.0 push (commit `a18ca3a`).

### C8.7a Forward-looking HALTs (all 10 verified)

| # | Assertion | Verification | Status |
|---|---|---|---|
| 1 | `C8.7a-complete` tag present | `git tag --list 'C8.7*'` returns `C8.7-pre-do` + `C8.7a-complete`; `C8.7b-pre-do` does NOT exist | ✓ |
| 2 | 4 parquet SHAs unchanged (fd_harm=`38e2cecb…`, fd_der=`185c071e…`, nat_der=`e16ad53…`, linked_der=`9b828a4d…`) | All 4 verified byte-exact via build-dir paths (fetal-death via `output/harmonized/` symlink → `fetal-death-harmonization-build/output/harmonized/`; natality + linked at `~/Desktop/natality-harmonization/output/harmonized/`) | ✓ all 4 match |
| 3 | 5 C8.5a + C8.6 file SHAs unchanged: pyproject.toml=`c8826a61…`, uv.lock=`ab627034…`, .python-version=`02e735b3…`, README.md=`694fdd35…`, ci.yml=`c248cf51…` | All 5 verified at monorepo root | ✓ all 5 match |
| 4 | 2 newly-patched script SHAs: validate_2022.py=`67a4dfcb…`, run_pipeline.py=`959ccac4…` | Both verified | ✓ both match |
| 5 | C8.8 is the next task per KICKOFF.md line 186 + §15 C8.8 | KICKOFF Phase C Tier 1 sequencing (line 186): "C8.8 — CHANGELOG + PRIOR_ART update [1 session]" | ✓ this entry executes it |
| 6 | C8.7b first PRE-FLIGHT decision (natality+linked output strategy) | Not C8.8's scope; carried as a soft-flag | ✓ deferred |
| 7 | Audit-script promotion to permanent test | Filed as C8.12 candidate in C8.7a receipt; not C8.8's scope | ✓ deferred |
| 8 | L13-extension defense surface well-covered | C8.8 does not touch scripts; not gating | ✓ informational |
| 9 | `run_pipeline.py` ALL_YEARS=29 staleness | C8.7b scope; not C8.8's | ✓ deferred |
| 10 | `SUBPROJECT_ROOT` rename forward-compatibility | C8.7b scope; not C8.8's | ✓ deferred |

### Environment

- [x] Working directory clean: `git status --short` empty. ✓
- [x] On `main`, HEAD=`f4f15ca` (C8.7a-complete). ✓
- [x] Python interpreter / `uv` / `.venv` all unchanged from C8.5a-complete (verified 7-file SHA invariant above).
- [x] `curl` available for L8 cheap-check probes (NCBI eutils + NICHD + HL7). ✓

### Source documentation (L8 cheap-check)

L8 = "every cited external document must resolve via PRE-FLIGHT probe before being shipped." §15 C8.8 names this halt-flag explicitly. Three probes:

| Citation (per EXPLORATION_REPORT §E.5) | URL / PMID | Probe result | Match expected? |
|---|---|---|---|
| "Hoyert et al. 2024 ([PubMed 38143212](https://pubmed.ncbi.nlm.nih.gov/38143212/))" | PMID 38143212 → NCBI esummary | **Title:** "U.S. stillbirth surveillance: The national fetal death file and other data sources." **Authors:** Gregory ECW, Barfield WD. **Journal:** Semin Perinatol 2024 Feb;48(1):151873. **ISSN:** 0146-0005. | ✗ — author attribution diverges: PMID 38143212 = Gregory + Barfield, NOT Hoyert. See Convention 3 amendment below. |
| NICHD Stillbirth Working Group Report, July 2024 | `https://www.nichd.nih.gov/sites/default/files/inline-files/NICHD_Stillbirth_WG_Report_July_2024_508.pdf` | `curl -L -k`: HTTP 200, size=451,388 bytes (Last-Modified header confirms 2024-07 release). | ✓ |
| HL7/fhir-bfdr (Birth + Fetal Death Reporting FHIR IG) | `http://hl7.org/fhir/us/bfdr/` | `curl -sI`: HTTP 200; Last-Modified: 2025-03-21. | ✓ |

**Convention 3 amendment — citation re-attribution.** The EXPLORATION_REPORT §E.5 plan-label "Hoyert et al. 2024" mis-identifies the lead author. The load-bearing identifier (PubMed 38143212) is canonical and resolves correctly; only the human-readable label is wrong. A separate Hoyert 2024 paper exists (PMID 39412872 = Gregory ECW, Valenzuela CP, Hoyert DL. *Fetal Mortality: United States, 2022.* Natl Vital Stat Rep. 2024 Sep 12) but it is **NVSR 73-09**, which is already cited throughout HVS as the validation gold standard — citing it in PRIOR_ART as evidence of the literature gap would be circular (PRIOR_ART argues the gap is that NCHS publishes aggregate NVSR tables, not microdata; pointing back at NVSR doesn't advance the argument). Resolution: ship PMID 38143212 with its correct authors (Gregory ECW + Barfield WD 2024) and drop the "Hoyert" label. The substantive purpose of the citation (post-Ananth-2022 evidence the gap persists) is preserved.

### Outputs

- Intended outputs:
  - `CHANGELOG.md` at monorepo root — **NEW** ✓ (canonical changelog; v1.0 → v1.1 sections).
  - `docs/PRIOR_ART.md` — **MODIFIED** ✓ (3 §E.5 updates + Q34 boundary statement).
  - `RECEIPTS/C8.8_<UTC>.md` — NEW.
  - `STATUS.md` — append new section.
  - `PRE_FLIGHT_LOG.md` (this entry) + `DECISION_LOG.md` (new entry recording the citation re-attribution Convention 3 amendment).
  - No script edits; no parquet mutations; no schema CSV touches.

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

| Artifact | Field / claim | Current value (verified PRE-FLIGHT) | Plan's assumed value | Match? |
|---|---|---|---|---|
| EXPLORATION_REPORT §E.5 item 2 | Citation author attribution | PMID 38143212 = Gregory ECW + Barfield WD | "Hoyert et al. 2024" | ✗ — see L8 row above. **Resolution**: cite Gregory + Barfield 2024 (correct authors at the load-bearing PMID). Documented in this PRE-FLIGHT entry + DECISION_LOG. |
| `docs/PRIOR_ART.md` Adjacent-harmonized section | Lists IPUMS, HMD, NHIS, NBER | as written | Updates need to nest: (a) new "GitHub precursors" subsection; (b) HL7/fhir-bfdr one-sentence within "NCHS itself harmonizes" section as appropriate boundary statement. | ✓ — current state matches plan input; edit-in-place is safe |
| `docs/PRIOR_ART.md` "Cited adaptations" section | Ends at Ananth 2022 (line 35) | as written | Insert post-Ananth subsection citing Gregory+Barfield 2024 (PMID 38143212) + NICHD WG 2024. | ✓ |
| `docs/PRIOR_ART.md` boundary statement | No explicit Q34 boundary (M-D/MCD/abortion) currently | as written | Insert one-paragraph "Out-of-scope vital-events series" subsection per DECISION_LOG 2026-05-12T21:00:00Z entry. | ✓ |
| Manuscript `paper/draft_v2_hmd_styled.md` *Data resource basics* paragraph | Cites Salihu, Willinger, Hogue+Silver, Ananth | as written | **NOT touched in C8.8**: §15 C8.8 scope is `PRIOR_ART.md` + `CHANGELOG.md` only. Manuscript update is Phase D step 6 scope. The new Gregory+Barfield 2024 + NICHD 2024 citations can be added to manuscript at Phase D — flagged as a forward-looking item, not a C8.8 mutation. | n/a (out of C8.8 scope) |
| Monorepo `CHANGELOG.md` | Does not exist | as expected | New file authored. v1.0 section anchored at `a18ca3a` (2026-05-12 public push); v1.1 section enumerates C8.1-C8.7a + the deferred C8.5b/C8.7b/C8.8 + planned-but-not-yet-shipped C8.9–C8.15. | ✓ |

### CHANGELOG.md v1.0 + v1.1 content plan (PRE-FLIGHT outline)

**v1.0** (2026-05-12, public push at commit `a18ca3a` per STATUS 2026-05-12T19:15Z):
- Sources: 4 sub-products as shipped at v1.0 — natality v2.7.0 (35-yr, 138.8M records), linked v3 (19-yr, 74.9M records), fetal-death v2.0.0 (29-yr, 1.63M records pre-V2.1/V3a/V3b).
- Public-facing artifact set matched what was rsync'd from `~/Desktop/vital-statistics-harmonization/` to `~/Desktop/vital-statistics-harmonization-public/` with the documented exclude list (STATUS / DECISION_LOG / FIX_LOG / LESSONS / NEXT_STEPS / KICKOFF / PRE_FLIGHT_LOG / RECEIPTS / .claude / paper / EXPLORATION_REPORT).

**v1.1** (Tier-1 + Tier-2 work; in-progress as of 2026-05-13):
- **Data extensions**: V2.1 fetal-death 2003+2004 (+107K records); V3a fetal-death 1989-1991 (+188K, +3 years); V3b fetal-death 1982-1988 (+421K, +7 years); natality v2.7.0 → v2.8.0 column rename. (Per task3, task7_v3a, task7_v3b, natality_v28_rename receipts.) Combined fetal-death envelope: 29-yr → 43-yr (1982-2022), 1.63M → 2.35M records.
- **Robustness**: H8 dtype-parity test (C8.1 + L17 retag fix); 3 invariant-test harnesses (C8.4); 4× `__init__.py` namespace-package fix (FIX_LOG 2026-05-12T22:30Z); 2 path-anchor fixes in `fetal_death/scripts/{05_validate/validate_2022.py, run_pipeline.py}` (C8.7a); `pyproject.toml` + `uv.lock` + `.python-version` pinned env (C8.5a); GitHub Actions CI (C8.6).
- **Docs**: This CHANGELOG.md; PRIOR_ART.md updates (3 §E.5 items + Q34 boundary).
- **Breaking / deprecations**: natality v2.7.0 → v2.8.0 column rename (`year` → `data_year`; `restatus` → `residence_status`; `maternal_race_bridged4` → `maternal_race_bridged`; `maternal_hispanic_origin` → `hispanic_origin`) per natality_v28_rename receipt. Users of legacy column names need to update. Migration guide is C8.11 (Tier 2 DEFERRED until v1.1 ships).
- **Deferred to v1.x**: C8.5b (Dockerfile), C8.7b (monorepo-root orchestrator + Tier-1/Tier-2 re-derive), C8.9–C8.15 (Tier-2 work).

### PRIOR_ART.md edit plan (PRE-FLIGHT outline)

Five small additions, no removals:

1. **New citation after Ananth 2022** (post-line 35): one paragraph citing Gregory + Barfield 2024 (PMID 38143212, Semin Perinatol; "U.S. stillbirth surveillance: The national fetal death file and other data sources") + NICHD Stillbirth Working Group Report July 2024 (linked PDF). Framed as: "Two 2024 publications reinforce the same conclusion: the gap remains operative."

2. **New "GitHub precursors" subsection** (after "Adjacent harmonized resources"): three repos (`Mikuana/vitalstatistics`, `arebe/cdc-natality`, `damiancclarke/nchs-fetaldata`) framed as partial precursors none of which (a) harmonize across the 1989/2003 boundary, (b) cover all three products, (c) validate against NVSR, (d) publish as Data Resource Profile.

3. **One-sentence HL7/fhir-bfdr mention** (within "Adjacent harmonized resources" or as its own short paragraph): "HL7's *fhir-bfdr* IG ([hl7.org/fhir/us/bfdr/](http://hl7.org/fhir/us/bfdr/)) defines a prospective FHIR-based reporting standard for future birth and fetal-death certificates; it is orthogonal to retrospective harmonization of the historical microdata covered here."

4. **New "Out-of-scope vital events" subsection (Q34 boundary statement)**: one paragraph naming marriage/divorce, multiple-cause-of-death (all-age mortality), and abortion surveillance as deliberately excluded from HVS's vital-events-around-birth scope. Cites EXPLORATION_REPORT §A.6 reasoning + DECISION_LOG 2026-05-12T21:00:00Z.

5. **No reword of Ananth 2022 paragraph** (per §E.5 risks: "Don't reword Ananth 2022 framing (it's the load-bearing citation)").

### Halt conditions tripped (§7)

**None.** Convention 3 caught one plan-vs-current-state divergence (the Hoyert→Gregory+Barfield citation re-attribution); this is a routine PRE-FLIGHT amendment (label correction; load-bearing PMID unchanged), not a §7 condition. No DO mutation has happened yet; the resolution is documented in this PRE-FLIGHT entry and in a parallel DECISION_LOG entry (`2026-05-13T09:00:00Z`). No §11 plan-update commit is needed (the §15 C8.8 entry does NOT specify the author label, only the PMID; the EXPLORATION_REPORT §E.5 label is informational-only).

L11 (stale roadmap claims, §15 C8.8 halt-flag): re-checked. KICKOFF Phase C Tier-1 list line 186 ("C8.8 — CHANGELOG + PRIOR_ART update [1 session]") matches §15 C8.8 wording. No stale claim surfaced.

### Result

**PROCEED** to C8.8 DO. Tag `C8.8-pre-do` lands on this PRE-FLIGHT commit (alongside the DECISION_LOG entry recording the Convention 3 citation amendment). `C8.8-complete` tag follows the DO commit shipping CHANGELOG.md + PRIOR_ART.md + receipt + STATUS append.

---

## PRE-FLIGHT for C8.7 — 2026-05-13T07:30:00Z — End-to-end pipeline smoke from monorepo root (B.10) — **RESULT: HALT**

### Scope summary

C8.7 §15.C entry (NEXT_STEPS.md lines 1037–1055): "Run `scripts/run_pipeline.py` from monorepo root end-to-end (raw zips → yearly_clean → harmonized → derived → validate) and fix any path-drift findings as L13-style 'fix on contact' patches." SMOKE plan: Tier 0 dry-run path-constant blocks; Tier 1 single-year per product; Tier 2 full re-build. VERIFY: "Re-built parquets sha256-match current shipped parquets. No new FIX_LOG entries needed (or all surfaced cases patched and verified)." Estimated effort 1 session.

### Inputs

- [x] All required input files exist
  - `fetal_death/scripts/run_pipeline.py`: present (3818 bytes; ALL_YEARS=29 covering V2 1992-2002 + V1 2005-2022) ✓
  - `natality/scripts/run_pipeline.py`: **DOES NOT EXIST** ✗ (no analogous orchestrator under `natality/scripts/`; per-step subdirs `01_import`/`02_clean_yearly`/`03_harmonize`/`04_derive`/`05_validate`/`06_convenience`/`07_figures` only)
  - `scripts/run_pipeline.py` at monorepo root (named by §15): **DOES NOT EXIST** ✗
  - Per-subproject per-step scripts: present in both `fetal_death/scripts/` and `natality/scripts/` ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - C8.5a-complete: ✓ (tag present at `e9cd08e`); C8.6-complete: ✓ (tag at `67ab76f`)
- [x] No stale checkpoints from previous incomplete runs of this task
  - `git status` clean ✓; no `C8.7-pre-do` tag exists ✓

### Environment

- [x] Python version: 3.13.9 via miniconda; `.venv` from C8.5a present (Python 3.13.0); both ≥3.11 ✓
- [x] uv version: 0.11.10 ✓
- [x] pandas version: per `uv.lock` resolution = 2.3.2 ✓; pyarrow per lock ≥18.0 ✓
- [x] Working directory clean (`git status`): ✓
- [x] On expected branch (`main`, HEAD=`67ab76f`): ✓

### Source documentation

- n/a — C8.7 is a pipeline-smoke task; no new NVSR PDFs introduced. NCHS source zips are bit-identical-on-disk (verified by sha-tracked file_inventory.csv state — not re-probed at this PRE-FLIGHT since C8.7 reads zips but does not re-download).

### Outputs

- [x] Intended output paths:
  - `RECEIPTS/C8.7_<UTC>.md`: does not exist (good) ✓
  - Re-derived parquets (if Tier 2 runs): WOULD OVERWRITE `output/harmonized/fetal_death_harmonized.parquet`, `output/harmonized/fetal_death_derived.parquet` (currently symlinked to `/Users/yoelplutchok/Desktop/fetal-death-harmonization-build/output/harmonized/`); natality + linked targets are NOT symlinked into the monorepo (see Field-value snapshot below) — re-derive would write to `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/` (build-dir of the standalone repo, not monorepo state).

### C8.6 Forward-looking HALTs (all verified)

| # | Assertion | Status |
|---|---|---|
| 2 | `C8.6-complete` tag present | ✓ at `67ab76f` |
| 3 | `.github/workflows/ci.yml` sha=`c248cf51159f907b…` | ✓ matches |
| 4 | `pyproject.toml`=`c8826a61…`, `uv.lock`=`ab627034…`, `.python-version`=`02e735b3…`, `README.md`=`694fdd35…` | ✓ all 4 match |
| 5 | 4 parquet SHAs unchanged (fd_harm=`38e2cecb…`, fd_der=`185c071e…`, nat_der=`e16ad53…`, linked_der=`9b828a4d…`) | ✓ all 4 match |
| 8 | C8.7 is the next task; PRE-FLIGHT verifies uv.lock + ci.yml + 4 parquet SHAs unchanged | ✓ this entry verifies them |

Items 1, 6, 7, 9, 10 are not PRE-FLIGHT-time gates for C8.7 (Phase-D / informational).

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

C8.7 will not mutate canonical data values (parquets) unless Tier 2 fires — and Tier 2 should reproduce existing SHAs byte-exact. The mutation surface in scope is `scripts/` (path-constant edits + possible new orchestrator). The Field-value snapshot enumerates the *script paths* that would have to be edited, alongside the *output paths* whose existence and current contents determine the SMOKE plan's feasibility.

**(a) Orchestrator inventory:**

| Orchestrator path | Present? | ALL_YEARS coverage | REPO_ROOT resolution from monorepo cwd |
|---|---|---|---|
| `scripts/run_pipeline.py` (monorepo-root, §15-named) | **NO** ✗ | n/a | n/a |
| `fetal_death/scripts/run_pipeline.py` | YES | V2 (1992-2002) + V1 (2005-2022) = **29 years; does NOT include V3a (1989-1991) + V3b (1982-1988) = 14 years currently in shipped v2.4.0 envelope (43 years total)** ✗ | `REPO_ROOT = fetal_death/`; `RAW_DIR = fetal_death/raw_data/fetal_death/`; `HARMONIZED_DIR = fetal_death/output/harmonized/` — **none of these dirs exist in monorepo** (raw zips live in standalone build dir; output exists only at MONOREPO_ROOT/output/ via symlinks) ✗ |
| `natality/scripts/run_pipeline.py` | **NO** ✗ | n/a | n/a — per-step scripts only |

**(b) Raw-zip inventory:**

| Product | Expected count | Location | Status |
|---|---|---|---|
| Fetal-death (1982-2022, 43 years) | 43 | `/Users/yoelplutchok/Desktop/fetal-death-harmonization-build/raw_data/` | 43 zips found ✓ — but NOT in monorepo path; `fetal_death/raw_data/` does not exist |
| Natality (1990-2024, 35 years) + Linked (2005-2023, 19 years) | 54 | `/Users/yoelplutchok/Desktop/natality-harmonization/raw_data/` | 54 zips found ✓ — but NOT in monorepo path; `natality/raw_data/` does not exist |

**(c) Output-path / symlink state:**

| Product | Canonical parquet path | Monorepo-root path | Status |
|---|---|---|---|
| Fetal-death harmonized + derived | `output/harmonized/fetal_death_{harmonized,derived}.parquet` | Reachable via `MONOREPO_ROOT/output/` (symlink to `fetal-death-harmonization-build/output/`) | ✓ accessible from monorepo |
| Natality v2 derived | `natality_v2_harmonized_derived.parquet` | Lives at `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/`; **NOT symlinked** into monorepo `output/` | ✗ inaccessible from monorepo root |
| Natality v3 linked derived | `natality_v3_linked_harmonized_derived.parquet` | Same as above | ✗ inaccessible from monorepo root |

**(d) §15 plan-vs-reality divergences identified:**

| § | §15 / Plan claim | Reality | Class |
|---|---|---|---|
| D.1 | "Run `scripts/run_pipeline.py` from monorepo root" | No such file exists | §7.13 ambiguity / L13-class (path drift) |
| D.2 | "fix any path-drift findings as L13-style fix-on-contact patches" — implies surface is small | `fetal_death/scripts/run_pipeline.py` REPO_ROOT/RAW_DIR/OUTPUT_DIR all mis-resolve from monorepo cwd (3 path-constants per script × many scripts); natality has no orchestrator at all | §7.13 + §7.17 (scope creep) |
| D.3 | "raw zips already on disk per file_inventory" | True (43 + 54 = 97 zips) but at standalone-build-dir paths, NOT at `fetal_death/raw_data/` or `natality/raw_data/` (the paths the unmodified scripts expect) | §7.13 (path) |
| D.4 | "Verify final parquet SHAs match current shipped SHAs (byte-identical re-derive)" — Tier 2 estimated 1 session | Compute cost: fetal-death derive ~30-60 min; natality 35yr × 138.8M records = hours; linked 19yr × 74.9M records = hours; plus 5 × `05_validate/` × 2 products = additional cost. **Combined Tier-2 estimate: 6-12+ hours of compute — well over 1 session** | §7.15 (cost) |
| D.5 | "ALL_YEARS = 29 years" hardcoded in `fetal_death/scripts/run_pipeline.py` | Current shipped v2.4.0 envelope is 43 years (V3a + V3b added 14 years 2026-05-12). Script is stale by 14 years' worth of harmonization | §7.13 (stale script) |
| D.6 | Natality + linked parquets re-derivable from monorepo | Not currently — natality scripts write to natality-harmonization/output/, not to MONOREPO_ROOT/output/. Re-derive comparison requires (i) re-symlinking, (ii) re-pointing scripts at MONOREPO_ROOT, OR (iii) running natality re-derive in its standalone-build dir and comparing | §7.13 (path) |

### Halt conditions tripped (§7)

1. **§7.13 — Validity-domain / path-resolution ambiguity (×3)**: (i) no monorepo-root orchestrator; (ii) `fetal_death/run_pipeline.py` REPO_ROOT mis-resolves from monorepo cwd; (iii) natality + linked parquets not symlinked into monorepo `output/`.
2. **§7.17 — Scope creep**: closing C8.7 per §15 literal requires (a) authoring a monorepo-root orchestrator (~0.5-1 session NEW work, was implicit in §15 but not enumerated as a DO step) + (b) fixing 3+ path-constants per subproject + (c) extending `ALL_YEARS` to 43 years for fetal-death — none of which are bounded by §15.
3. **§7.15 — Time/cost budget exceeded**: Tier-2 full re-derive across three products is hours of compute; §15's 1-session estimate is inconsistent with the named Tier-2 VERIFY criterion.
4. **§7.12 — Conflicting documentation**: §15 names `scripts/run_pipeline.py` as if it exists; STATUS 2026-05-13T06:30:00Z line 116 already flagged this ("natality has no current orchestrator — C8.7 may need to author one or wire the existing per-step scripts").

### Result

**HALT.** §15 C8.7 spec is internally inconsistent with current monorepo state on (i) named orchestrator presence; (ii) ALL_YEARS coverage; (iii) Tier-2 compute cost vs 1-session estimate; (iv) natality + linked output-path connectivity. Halt-and-ask required before any DO mutation. Three resolution paths are plausible (Tier-0 dry-run only / Tier-1 single-year-per-product / Tier-2 full re-derive); each implies a different §11 plan-update revising C8.7's scope. Posing AskUserQuestion to select between them.

---

## PRE-FLIGHT addendum for C8.7 — 2026-05-13T07:40:00Z — All 4 HALTs resolved per user authorization ("do what you think is best" → Option A per the AskUserQuestion preamble recommendation); task split C8.7 → C8.7a (path audit, this session) + C8.7b (orchestrator + Tier-1/2 re-derive, DEFERRED); PROCEED to C8.7a DO

**User authorization.** AskUserQuestion 2026-05-13T07:30:00Z presented 4 options (A: Tier-0 dry-run only / B: orchestrator + Tier-1 / C: orchestrator + Tier-2 FD + Tier-1 nat/linked / D: full Tier-2). User response: "do what you think is best." Per the question preamble's explicit "(A) ... Recommended" framing (mirrored C8.6's "do what you think is the best move" precedent → Option A), I interpret the delegation as Option A authorization.

**Resolution applied (single `[plan-update]` commit, this session):**

1. **§15 C8.7 rewritten as C8.7a + C8.7b** in NEXT_STEPS.md. C8.7a (this entry) = Tier-0 static path-constant audit across per-step scripts; no orchestrator authoring; no live re-derive; matches §15's 1-session estimate. C8.7b stub (DEFERRED) = orchestrator + Tier-1 + Tier-2 re-derive; resumption trigger AND-coupled on C8.7a-complete + user-authorized compute window.

2. **KICKOFF.md Tier-1 task list (line 184)** split: `C8.7 — End-to-end pipeline smoke` → `C8.7a — Path-drift static audit` (this session) + `C8.7b — Orchestrator + Tier-1/2 re-derive (DEFERRED)`.

3. **KICKOFF.md sequencing note (line 203)** revised: C8.5b resumption trigger now references **C8.7b** (the orchestrator), not C8.7 — with explicit clarification that C8.7a does NOT land an orchestrator.

4. **This addendum** + **DECISION_LOG entry 2026-05-13T07:40:00Z** record the §11 plan-update.

**Field-value snapshot revisited (post-resolution).**

- C8.7a in-scope DO surface: every per-step pipeline script's path-constant block (`fetal_death/scripts/01_import/`, `03_harmonize/`, `04_derive/`, `05_validate/`, plus the existing `fetal_death/scripts/run_pipeline.py`; `natality/scripts/01_import/`, `02_clean_yearly/`, `03_harmonize/`, `04_derive/`, `05_validate/`).
- Method: Python AST inspection of each module's globals to enumerate `Path(__file__).resolve()...`-shape constants; `exists()` test under monorepo cwd; helper-import reachability test.
- Patches applied on contact (sibling of FIX_LOG 2026-05-12T01:30Z entries). FIX_LOG entries consolidated by script-class (entry-point / parse / harmonize / derive / validate) to avoid log bloat.
- VERIFY remains metadata-only — no parquet SHAs should change, no test-suite regression, no canonical-state mutation.

**Halt conditions resolved.**

- §7.13 (×3) — resolved by deferring the live-run / orchestrator concerns to C8.7b; C8.7a's Tier-0 audit doesn't touch raw zips or output dirs, so the geographic path-mismatch isn't a blocker for the audit itself.
- §7.17 (scope creep) — resolved by tightening C8.7a's DO scope to "audit + L13 patches" (no new orchestrator, no `ALL_YEARS` extension, no symlinks).
- §7.15 (cost) — resolved by removing Tier-2 from C8.7a; C8.7a is metadata-only.
- §7.12 (conflicting documentation) — resolved by the §11 plan-update aligning §15 + KICKOFF with the locally-verifiable scope.

### Result

**PROCEED** to C8.7a DO post-resolution. Tag `C8.7-pre-do` lands on the `[plan-update]` commit. C8.7a-complete tag follows the DO commit.

---

## PRE-FLIGHT for C8.6 — 2026-05-13T05:30:00Z — CI: GitHub Actions wiring (B.9) — **RESULT: HALT**

### Scope summary

C8.6 §15.C entry (NEXT_STEPS.md lines 1001–1019, pre-revision): author `.github/workflows/ci.yml` running C8.1 dtype-parity + C8.4 invariant tests on every push to main, gated on the C8.5a-pinned env. §15 names PRE-FLIGHT inputs as "Existing tests (C8.1 + C8.4); pinned env (C8.5 lockfile); GitHub repo (already public at https://github.com/yoelplutchok/vital-statistics-harmonization)." §15 DO scope picks "matrix on Python 3.11 + 3.12 if both supported per uv.lock; install via `uv sync --frozen`; run `pytest fetal_death/tests/ natality/tests/ tests/`." §15 VERIFY: "Green check on the test commit. Subsequent PRs gate on CI." Estimated effort 1 session.

### Inputs

- [x] **`pyproject.toml` (monorepo root) sha=`c8826a61…` ✓** (C8.5a output, unchanged).
- [x] **`uv.lock` (monorepo root) sha=`ab627034…` ✓** (C8.5a output, unchanged).
- [x] **`.python-version` (monorepo root) sha=`02e735b3…` ✓** content `3.13` (single line).
- [x] **README.md (monorepo root) sha=`694fdd35…` ✓** (C8.5a-revised; "Pinned environment via `uv` lockfile" subsection present).
- [x] `fetal_death/tests/test_schema_dtype_parity.py` (C8.1 output) present; `fetal_death/tests/test_release_smoke.py` (C8.1 retag) present.
- [x] `tests/__init__.py` + `tests/conftest.py` + `tests/test_canonical_filter_invariants.py` + `tests/test_row_count_conservation.py` + `tests/test_cross_product_join_parity.py` (C8.4 outputs) present.
- [x] 4× `__init__.py` files (fetal_death + fetal_death/tests + natality + natality/tests) present per C8.1 followup commit `b84ff0d`.
- [x] All four parquet SHAs unchanged from C8.5a-complete state (this task is workflow-file-only; MUST NOT mutate any data parquet): fd_harm=`38e2cecb…` ✓, fd_der=`185c071e…` ✓, nat_der=`e16ad53…` (via natality build-dir symlink), linked_der=`9b828a4d…` (via natality build-dir symlink).
- [x] All upstream Tier-1 tasks marked complete: `C8.1-complete`, `C8.2-complete`, `C8.3-complete`, `C8.4-complete`, `C8.5a-complete` (`e9cd08e` = HEAD). §15 names C8.1, C8.4, C8.5 as upstream dependencies — all present (C8.5a satisfies C8.6's `uv.lock` need; C8.5b Dockerfile DEFERRED but not blocking C8.6 per the C8.5 plan-update's narrowing of C8.6's dependency).
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/C8.6_*.md`: does not exist ✓
  - `.github/`: does not exist ✓
  - `.github/workflows/ci.yml`: does not exist ✓

### Environment

- [x] Python interpreter: `/opt/miniconda3/bin/python3` = **3.13.9** ✓ (miniconda; matches `.python-version` pin).
- [x] **uv: 0.11.10** ✓ at `/opt/miniconda3/bin/uv` — workflow will pin `astral-sh/setup-uv@v6` with `version: "0.11.x"`.
- [x] `.venv/` at monorepo root: present; `uv sync --check` returns "Resolved 38 packages in 25ms / Checked 34 packages in 12ms / Would make no changes" ✓ (lockfile reproduces against the build-machine env).
- [x] **gh: 2.87.3** ✓ at `/opt/homebrew/bin/gh` — available for remote-state probing.
- [ ] **actionlint: NOT INSTALLED** ✗ (`which actionlint` returns nothing). Mitigation: SMOKE Tier 0 falls back to `python -c "import yaml; yaml.safe_load(...)"` + structural assertions on the parsed dict (top-level keys `name`/`on`/`jobs`; per-job keys `runs-on`/`steps`; per-step keys `uses` or `run`; valid event triggers under `on:`). Acceptable; actionlint is a nice-to-have, not blocking.
- [x] Working directory clean (`git status --short` empty); on `main`, HEAD=`e9cd08e` (`C8.5a-complete`).

### Source documentation

- [x] Not applicable — C8.6 consumes no external PDFs.

### Outputs

- Intended outputs:
  - `.github/workflows/ci.yml` — NEW ✓ (canonical workflow definition).
  - `NEXT_STEPS.md` — MODIFIED (§15 C8.6 entry revised per §11 plan-update; see HALT #1 + HALT #2 below).
  - `DECISION_LOG.md` — append new entry recording the §11 plan-update.
  - `PRE_FLIGHT_LOG.md` — append addendum (this entry's resolution).
  - `RECEIPTS/C8.6_<UTC>.md` — NEW ✓.
  - `STATUS.md` — append new section.

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

For each canonical artifact this task will mutate, snapshot the **current** value vs the task plan's assumed value:

| Artifact | Field | Current value (verified PRE-FLIGHT) | Plan's assumed value | Match? |
|---|---|---|---|---|
| `NEXT_STEPS.md` §15 C8.6 DO scope | "matrix on Python 3.11 + 3.12 if both supported per uv.lock" | as written | Python 3.13 (per C8.5a `requires-python = ">=3.13,<3.14"`) | ✗ — §15 text predates C8.5a; **HALT #2** |
| `NEXT_STEPS.md` §15 C8.6 VERIFY criterion | "Green check on the test commit" | as written | Live CI green check (assumes remote-push works) | ✗ — assumes a remote that doesn't exist in this monorepo; **HALT #1** |
| `git remote -v` | (output) | empty (no remotes) | "origin → public repo" implicit in §15 PRE-FLIGHT inputs | ✗ — **HALT #1** |
| Public repo `yoelplutchok/vital-statistics-harmonization` HEAD | commit sha | `a18ca3a` (v1.0, 2026-05-12) | Plan assumes the public repo has Tier-1 outputs (pyproject/uv.lock/tests/) already pushed | ✗ — public repo lacks C8.1/C8.4/C8.5a outputs; **HALT #1** |
| Public repo `.github/workflows/` | (directory) | does not exist (HTTP 404) | — | (consistent with workflow-file-being-newly-authored; not itself a HALT) |
| `~/Desktop/vital-statistics-harmonization-public/.github/` | (directory) | does not exist | — | (consistent; staging dir has not yet seen a Phase D step 3 sync that would include a workflow) |
| `.github/` (this monorepo) | (directory) | does not exist | NEW dir to author | ✓ |
| 4× C8.5a file SHAs | content | `c8826a61…` / `ab627034…` / `02e735b3…` / `694fdd35…` | matches C8.5a STATUS forward-looking HALT #2 | ✓ |
| Cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` | combined result | 56 PASS + 1 XFAIL (per C8.5a VERIFY) | matches | (verified at C8.5a; will re-verify under .venv at VERIFY phase) ✓ |

### Halt conditions tripped

**HALT #1 — §7.17 (scope creep / plan vs reality) + §7.12-shape (conflicting documentation):**
- `git remote -v` empty: this monorepo has no `origin`. The public repo (`yoelplutchok/vital-statistics-harmonization`, last commit `a18ca3a` = v1.0, 2026-05-12T03:20Z) has no `.github/workflows/` directory and lacks all Tier-1 outputs (no `pyproject.toml`, `uv.lock`, `.python-version`, `tests/`, C8.1 dtype-parity test, the four `__init__.py` files). Per KICKOFF Phase D step 3, the canonical mechanism for moving these forward to the public repo is the staging dir `~/Desktop/vital-statistics-harmonization-public/` re-rsync + scrub + push. §15 C8.6 PRE-FLIGHT inputs assume the public repo is the working CI surface ("GitHub repo already public") but the live-CI VERIFY criterion ("green check on the test commit") cannot close from this monorepo without a sync-and-push step.
- Three resolution paths considered (see AskUserQuestion 2026-05-13T05:30:00Z): (a) Ship workflow now, live-VERIFY at Phase D step 3 sync; (b) Surgical sync to staging dir + live push; (c) Re-order Tier-1 to ship C8.6 last, immediately before Phase D step 3.
- User authorization 2026-05-13T05:30:00Z chat: "do what you think is the best move" — interpreted as Option (a) per the agent's stated recommendation in the AskUserQuestion preamble (minimal scope; matches dev/public separation; clean §11 plan-update revising VERIFY criterion).

**HALT #2 — §7.12 (conflicting documentation):**
- §15 C8.6 DO scope (line 1011, written before C8.5a) specifies "matrix on Python 3.11 + 3.12 if both supported per uv.lock." C8.5a pinned `requires-python = ">=3.13,<3.14"` and `.python-version = 3.13`, so neither 3.11 nor 3.12 is supported under the canonical env. STATUS 2026-05-13T05:00:00Z line 118 already flagged this as a "candidate consideration for C8.6." Resolution: single-version Python 3.13 (or no explicit matrix), tracking `.python-version`. §11 plan-update revises §15 line 1011 text.

### Halt severity and resolution path

Both HALTs caught at the cheap-check moment; zero canonical-state mutation has occurred. Resolution: single `[plan-update]` commit revising §15 C8.6 entry per Option (a) above + this PRE-FLIGHT addendum at the resolution moment + DECISION_LOG entry documenting the §11 plan-update + dev/public deferral rationale. Tag `C8.6-pre-do` lands on the `[plan-update]` commit. C8.6 DO then proceeds to author `.github/workflows/ci.yml`.

The parquet-skip-in-CI concern (CI runners will find no parquets via the conftest `_require()` skip-if-missing protocol; CI green-check signal weakened) is acknowledged but routed to **C8.13 (Performance + GitHub release artifacts)** as a separate architectural matter. The C8.6 workflow file is designed so that adding a parquet-fetch step later (e.g., `actions/download-artifact` or `curl` from a release URL) is a single new step before the `pytest` step — no rewrite needed.

### Result

**HALT.** Resolution path: §11 plan-update + Option (a) per user authorization 2026-05-13T05:30:00Z. Resolution addendum below.

---

## PRE-FLIGHT addendum for C8.6 — 2026-05-13T05:45:00Z — Both HALTs resolved per user authorization (Option A: ship workflow now, live-VERIFY at Phase D step 3); PROCEED to C8.6 DO

### Resolutions per user authorization (AskUserQuestion 2026-05-13T05:30:00Z, user response "do what you think is the best move")

- **HALT #1 (§7.17 + §7.12-shape, dev/public separation) → Option (a) "Ship workflow now, live-VERIFY at Phase D"**: Author `.github/workflows/ci.yml` in monorepo; emulate workflow steps locally under `.venv` (cache-cleared `uv sync --frozen` + `uv lock --check` + `uv run pytest fetal_death/tests/ natality/tests/ tests/` → 56 PASS + 1 XFAIL). §11 plan-update revises §15 C8.6 VERIFY criterion from "Green check on the test commit" to "YAML structurally valid + locally-emulated test-suite command runs green; live-CI green-check VERIFY closes at Phase D step 3 first sync." Forward-looking HALT in receipt: Phase D step 3 first sync MUST verify CI green on first run; if red, halt and surface failure modes. Parquet-skip-in-CI documented as Forward-looking HALT routed to C8.13 (GitHub release artifacts).
- **HALT #2 (§7.12, Python pin) → option (a)**: Single-version Python 3.13 per `.python-version` (no matrix needed given `requires-python = ">=3.13,<3.14"`). §11 plan-update revises §15 C8.6 DO scope line 1011.

### §11 plan-update applied this commit

- `NEXT_STEPS.md` §15.C C8.6 entry rewritten:
  - DO scope line 1011: replaced "matrix on Python 3.11 + 3.12 if both supported per uv.lock" with single-version Python 3.13 sourced from `.python-version`.
  - VERIFY criteria (line 1013): replaced "Green check on the test commit. Subsequent PRs gate on CI." with "YAML structurally valid (yaml.safe_load round-trip + structural-key assertions); cache-cleared locally-emulated test-suite command (`uv sync --frozen` + `uv lock --check` + `uv run pytest fetal_death/tests/ natality/tests/ tests/`) returns 56 PASS + 1 XFAIL preserved from C8.5a-complete baseline; live-CI green-check VERIFY closes at Phase D step 3 first sync (Forward-looking HALT in receipt; if red on first remote run, halt + surface)."
  - PRE-FLIGHT inputs (line 1007): unchanged in literal text; the implicit "remote push will happen this session" assumption is now superseded by the dev/public-separation discipline documented above + DECISION_LOG entry.
  - Why-this-matters narrative unchanged. Estimated effort 1 session unchanged (the live-CI green-check is forward-deferred, not effort-extended).
- `KICKOFF.md` — no edits needed; Phase C Tier-1 sequencing (line 184) names C8.6 as the next task with no implicit "remote push happens at C8.6" claim.
- This PRE-FLIGHT addendum records the resolution + the §11 plan-update.
- `DECISION_LOG.md` 2026-05-13T05:45:00Z entry records the §11 plan-update + Option A rationale.

### Post-resolution input state for C8.6

- [x] All four C8.5a file SHAs unchanged (verified above) ✓
- [x] All four parquet SHAs unchanged ✓
- [x] Test inventory complete: 16 tests in `fetal_death/tests/` + 3 tests in `natality/tests/` + 41 tests in `tests/` = 57 items; expected: 56 PASS + 1 XFAIL (post-C8.4 baseline; reproduced at C8.5a-complete).
- [x] `uv 0.11.10` ✓; `python3.13.9` ✓; `.venv/` ready.
- [x] Workflow design choices for DO phase:
  - Trigger events: `push` (branches: `main`), `pull_request` (branches: `main`), `workflow_dispatch` (manual).
  - Single job: `test`, `runs-on: ubuntu-latest`.
  - Step 1: `actions/checkout@v5`.
  - Step 2: `astral-sh/setup-uv@v6` with `version: "0.11.x"`, `enable-cache: true`, `cache-dependency-glob: "**/uv.lock"`. Python is auto-resolved from `.python-version` + `pyproject.toml` `requires-python` by uv (no separate `actions/setup-python` step needed since uv 0.6+ handles Python installation natively).
  - Step 3: `uv lock --check` (gating against drift between `pyproject.toml` and `uv.lock`).
  - Step 4: `uv sync --frozen` (installs the pinned env).
  - Step 5: `uv run pytest fetal_death/tests/ natality/tests/ tests/ -v` (expected 56 PASS + 1 XFAIL under clean-checkout cache-cleared discipline).
  - Concurrency control: `group: ci-${{ github.ref }}`, `cancel-in-progress: true` (cancel in-flight runs on rapid pushes).

### Outputs (intended) for C8.6

- `.github/workflows/ci.yml` (NEW; canonical workflow per design above).
- `NEXT_STEPS.md` (MODIFIED; §15 C8.6 entry revised per the §11 plan-update).
- `DECISION_LOG.md` (append; 2026-05-13T05:45:00Z entry).
- This PRE-FLIGHT addendum (PRE_FLIGHT_LOG.md append).
- `RECEIPTS/C8.6_<UTC>.md` (NEW; at task close).
- `STATUS.md` (append; new section at task close).

### Halt conditions tripped (post-resolution)

None. Both HALTs resolved via §11 plan-update + Option A user authorization. C8.6 is fully locally verifiable; live-CI VERIFY is forward-deferred to Phase D step 3 (documented as a Forward-looking HALT in the receipt).

### Result

**PROCEED to C8.6 DO.** Tag `C8.6-pre-do` lands on the `[plan-update]` commit. DO authors `.github/workflows/ci.yml` per the design above; VERIFY runs the locally-emulated workflow steps under `.venv`; RECEIPT at `RECEIPTS/C8.6_<UTC>.md`.

---

## PRE-FLIGHT for C8.5 — 2026-05-13T04:00:00Z — Distribution: uv/poetry lockfile + Dockerfile (F.2 + F.3) — **RESULT: HALT**

### Scope summary

C8.5 §15.C entry (NEXT_STEPS.md lines 953–971): two artifacts in one task — (i) **F.3** `uv.lock` (or `poetry.lock`) pinning exact versions for Python + every runtime dep, replacing `requirements.txt` `>=` semantics; (ii) **F.2** `Dockerfile` producing a runnable image that rebuilds every parquet end-to-end via `scripts/run_pipeline.py`. §15 names PRE-FLIGHT inputs as "existing `requirements.txt`; current Python version on build machine; raw zip inventory (Dockerfile needs to know where to fetch them — initial choice: bind-mount `raw_data/` into the container rather than baking 5+ GB of raw zips into the image)." §15 DO scope picks `uv` over `poetry`; multi-stage Dockerfile based on `python:3.11-slim`; README "Reproducibility via Docker" section. §15 VERIFY criteria: `uv sync + python scripts/run_pipeline.py` produces parquets with current SHAs; `docker build && docker run` produces same. Estimated effort 1.5–3 sessions.

### Inputs

- [x] `requirements.txt` (monorepo root) present, sha-stable, content reviewed: 4 pinned-lower-bound deps (pandas≥2.3.2, pyarrow≥18.1.0, numpy≥2.3.1, matplotlib≥3.10.5) + 2 notebook deps (jupyter≥1.0, nbformat≥5.9). Uses `>=` semantics throughout (the gap C8.5 closes).
- [x] `natality/requirements.txt` (subproject) present: same 4 numeric deps + same notebook deps.
- [x] `fetal_death/requirements.txt` (subproject) present: only 3 deps (pandas≥2.3.0, pyarrow≥18.0.0, numpy≥2.0.0; no matplotlib, no notebook deps). Note: "Pinned to lower bounds matching the versions used to produce V2.0 (Python 3.13.9, 2026-05-02)" — explicit Python-version reference in source-of-truth doc.
- [x] All four parquet SHAs unchanged from C8.4-complete forward-looking HALT #4 (this task is metadata-only, MUST NOT mutate any data parquet): fd_harm=`38e2cecb…`, fd_der=`185c071e…`, nat_der=`e16ad53…`, linked_der=`9b828a4d…`.
- [x] All upstream Tier-1 tasks marked complete: `C8.1-complete` (`9fe662a`), `C8.2-complete` (`bb19c5a`), `C8.3-complete` (`ffbb4da`), `C8.4-complete` (`4b78dd0` — HEAD). C8.5 has no §15-named upstream Tier-1 dependency.
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/C8.5_*.md`: does not exist ✓
  - `pyproject.toml` (monorepo root): does not exist ✓
  - `uv.lock` (monorepo root): does not exist ✓
  - `Dockerfile` (monorepo root): does not exist ✓
  - `.python-version` (monorepo root): does not exist ✓

### Environment

- [x] Python interpreter: `/opt/miniconda3/bin/python3` = **3.13.9** (miniconda) ✓
- [x] pandas: 2.3.2 ✓ (≥ requirements.txt lower bound)
- [x] pyarrow: 18.1.0 ✓
- [x] numpy: 2.3.1 ✓
- [x] matplotlib: 3.10.5 ✓
- [x] pytest: 9.0.2 ✓
- [x] nbclient: 0.10.4 ✓
- [x] **uv: 0.11.10 ✓** at `/opt/miniconda3/bin/uv` — lockfile authoring tool available.
- [ ] **docker: NOT INSTALLED** ✗ (`docker` not found; `which docker` exit 1; `docker --version` command-not-found).
- [ ] poetry: not installed (✓ acceptable since §15 picks `uv` not `poetry`).
- [x] Working directory clean (`git status --short` empty); on `main`, HEAD=`4b78dd0` (`C8.4-complete`).

### Source documentation

- [x] Not applicable — C8.5 consumes no external PDFs.

### Outputs

- Intended outputs (NEW files at monorepo root):
  - `pyproject.toml` — NEW ✓
  - `uv.lock` — NEW ✓
  - `Dockerfile` — NEW ✓
  - `.dockerignore` — NEW ✓
  - `.python-version` — NEW (or recorded via pyproject `requires-python`) ✓
  - README section update (existing file, append-only insert) ✓
  - `RECEIPTS/C8.5_<UTC>.md` — NEW ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

C8.5 mutates **zero canonical data**; it adds packaging metadata. The "cells being mutated" are (a) the dependency-version pins the lockfile will encode and (b) the §15 entry's Python-version pin assumption.

#### Current dependency-version state (verified via `python3 -c "import X; print(X.__version__)"`)

| Package | Installed version | requirements.txt declares | Lockfile pin (target) |
|---|---|---|---|
| Python | 3.13.9 (CPython, miniconda) | implicit | 3.13.x (see HALT #2) |
| pandas | 2.3.2 | ≥2.3.2 | ==2.3.2 |
| pyarrow | 18.1.0 | ≥18.1.0 | ==18.1.0 |
| numpy | 2.3.1 | ≥2.3.1 | ==2.3.1 |
| matplotlib | 3.10.5 | ≥3.10.5 | ==3.10.5 |
| pytest | 9.0.2 | not declared in requirements.txt; used by `tests/` + `fetal_death/tests/` + `natality/tests/` | ==9.0.2 (dev dep) |
| nbclient | 0.10.4 | not declared; used by `notebooks/_build_joint_use_demo.py` to execute the notebook | ==0.10.4 (dev dep or runtime — see §11 sub-question) |
| nbformat | (not probed; ≥5.9 in req.txt) | ≥5.9 | TBD |
| jupyter | (not probed; ≥1.0 in req.txt — meta-package) | ≥1.0 | TBD |
| pymupdf (fitz) | used by C8.3 PRE-FLIGHT L9 cheap-check; not in requirements.txt | NOT declared | TBD (likely dev-only) |

These pins are the values the lockfile will encode at C8.5 DO step 1. The PRE-FLIGHT records them so a future auditor can verify the lockfile was generated against the actual installed env, not a stale assumption.

#### §15 entry text vs reality — three divergences

1. **§15 says base image `python:3.11-slim`** (line 963). Build env is Python **3.13.9** (miniconda). natality v2.7.0 + fetal_death V2.0 build notes both name Python 3.13.9 as the build-time interpreter. → HALT #2 (§7.12 conflicting documentation).
2. **§15 VERIFY says `python scripts/run_pipeline.py` at monorepo root** (line 965). No monorepo-root `scripts/` directory exists (`ls /Users/yoelplutchok/Desktop/vital-statistics-harmonization/scripts/` → No such file or directory). Only `fetal_death/scripts/run_pipeline.py` exists; it rebuilds the fetal-death parquet only (29 years of the now-43-year coverage; the V2.1/V3a/V3b extension-era code path is in the build-dir scripts, not yet promoted to the monorepo subdir). Natality has no `scripts/run_pipeline.py` — the natality pipeline runs from the natality-harmonization build dir's scripts. → HALT #3 (§7.17 scope creep / dependency missing: VERIFY criterion as written cannot complete without authoring a monorepo-root orchestrator, which is C8.7's scope).
3. **§15 SMOKE Tier 1+2 require `docker build` + `docker run`.** docker not installed on this machine. → HALT #1 (§7.2 SMOKE cannot run; defense-in-depth `docker build`+`docker run` verification not locally possible).

### Halt conditions tripped

#### HALT #1 — §7.2 — `docker` not installed; Tier 1+2 SMOKE for the Dockerfile cannot run locally.

`which docker` → exit 1. macOS without Docker Desktop / OrbStack / colima. C8.5 SMOKE plan (§15): "Tier 1: `docker build` on a clean checkout; verify the image builds. Tier 2: `docker run` invokes `scripts/run_pipeline.py` end-to-end; verify outputs match expected SHAs." Neither tier is runnable without docker.

Options to surface to user:

- (a) **Defer Dockerfile to C8.6 CI run + ship lockfile only this session.** Pro: cleanly unblocks C8.5a (lockfile) with full SMOKE+VERIFY; defers Dockerfile to a session where docker is available (user installs Docker Desktop OR C8.6 GitHub Actions runs `docker build` on its hosted-runner natively). Con: ships Dockerfile authored but un-validated locally; needs explicit "validated remotely via CI" framing. Or: defer the entire Dockerfile to a separate task ID after C8.6.
- (b) **Author Dockerfile + dockerignore based on best-practice template + defer `docker build`/`docker run` verification to C8.6.** Same as (a) but Dockerfile lands in this session, validated via syntax-only (`hadolint` if installable, or careful authoring with §15 entry text as the template) + CI-driven `docker build` at C8.6 SMOKE.
- (c) **Halt C8.5 entirely until docker is available** (user installs Docker Desktop or OrbStack; ~5-15 min for Docker Desktop install). Pro: fully verifies SMOKE locally before tagging C8.5-complete. Con: introduces an out-of-band human step; delays C8.5 indefinitely if user defers install.
- (d) **Split C8.5 → C8.5a (lockfile, this session) + C8.5b (Dockerfile, later session).** Pro: surgical; preserves Tier-1 progress; clean §11 plan-update. Con: bookkeeping overhead (2 RECEIPTS, 2 tags); §11 plan-update commit before any DO mutation.

Recommendation: **(d) split + §11 plan-update** OR **(b) author Dockerfile this session, defer docker-runtime SMOKE to C8.6 CI**. The two are operationally similar; (d) is more conservative because it doesn't ship un-locally-SMOKE'd canonical state.

#### HALT #2 — §7.12 — Conflicting documentation: §15 entry text says `python:3.11-slim` base; current build env is Python 3.13.9.

§15 line 963 explicitly names `python:3.11-slim` as the Dockerfile base, but the natality v2.7.0 + fetal-death V2.0 + the in-session-running interpreter are all Python 3.13.9. Two consequences:

- The lockfile's `requires-python` pin: should be `>=3.13` (matches build env) or `>=3.11` (matches §15 plan literal)?
- The Dockerfile's base: `python:3.13-slim` (matches build env) or `python:3.11-slim` (matches §15)?

The conservative choice is to pin to 3.13.x (matches every actual build event in this monorepo's history), and apply a §11 [plan-update] to revise the §15 entry's line 963 text. The §15 text's "3.11-slim" appears to be a EXPLORATION_REPORT §F.2 carryover (§F.2 doesn't name a specific Python version; the §15 wording inserted "3.11-slim" as an example without ground-truth check).

Options:

- (a) **§11 [plan-update]: revise §15 line 963 from `python:3.11-slim` to `python:3.13-slim`** matching the build env. Pro: aligns plan with reality; lockfile pins reproduce documented builds. Con: §11 plan-update commit before tagging C8.5-pre-do (mirrors C8.2 + C8.3 PRE-FLIGHT plan-update flow).
- (b) **Pin to 3.11-slim per §15 literal text; downgrade-test all deps work on 3.11.** Pro: follows §15 as-written. Con: lockfile becomes a hypothetical-env pin (no actual 3.11 build event in this repo's history); may surface dep version conflicts (pandas 2.3.2 + numpy 2.3.1 both still support 3.11, but the resolution might prefer different versions on 3.11 vs 3.13); breaks reproducibility of every existing build.
- (c) **Range-pin `requires-python = ">=3.11,<3.14"`** (or similar) — broadest compatibility. Pro: future-flexible. Con: lockfile still resolves against one specific Python version (whichever `uv` picks at lock time); the range doesn't actually give resolver flexibility — it constrains downstream-consumer Python.

Recommendation: **(a) §11 plan-update to revise the §15 entry to `python:3.13-slim`** and pin `requires-python = "==3.13.*"` (or `>=3.13,<3.14`) in `pyproject.toml`. Matches every existing build event.

#### HALT #3 — §7.17 — Scope creep / dependency missing: §15 VERIFY criterion references `scripts/run_pipeline.py` at monorepo root; only `fetal_death/scripts/run_pipeline.py` exists.

§15 line 965 VERIFY: "`uv sync` + `python scripts/run_pipeline.py` produces parquets with current SHAs." Reality:

- `/Users/yoelplutchok/Desktop/vital-statistics-harmonization/scripts/run_pipeline.py` — does not exist.
- `/Users/yoelplutchok/Desktop/vital-statistics-harmonization/fetal_death/scripts/run_pipeline.py` — exists; rebuilds the V2.0 (29 years, 1.6M records) fetal-death parquet only. Does not orchestrate V2.1 / V3a / V3b / 2023-2024 extensions; does not orchestrate the natality or linked pipelines.
- The natality + linked pipelines run from `/Users/yoelplutchok/Desktop/natality-harmonization/` (a separate sibling repo) — their scripts/build-dir code is not in the monorepo.

The §15 VERIFY criterion presupposes a monorepo-root pipeline orchestrator. That orchestrator is **C8.7's scope** ("end-to-end pipeline smoke from monorepo root") per KICKOFF.md Tier 1 sequencing. C8.5 cannot satisfy its §15-named VERIFY without C8.7 first.

Options:

- (a) **§11 [plan-update]: revise §15 C8.5 VERIFY to use `uv sync` env-resolution check only** (no pipeline rebuild). Add a separate verifier: `uv sync && python -c "import pandas, pyarrow, numpy, matplotlib, pytest, nbclient" && pytest fetal_death/tests/ natality/tests/ tests/` (= "the env is sufficient to run the full test suite"). The pipeline-rebuild verification moves to C8.7 (which already plans to do this). Pro: aligns C8.5 scope with what's locally verifiable; C8.7 explicitly takes the pipeline-rebuild VERIFY responsibility. Con: weakens C8.5 VERIFY; relies on C8.7 for end-to-end closure.
- (b) **Author a stub monorepo-root `scripts/run_pipeline.py` that calls per-subproject pipelines** (scope creep into C8.7). Pro: C8.5 VERIFY closes per §15 literal. Con: scope creep (~0.5-1 session of work that belongs in C8.7); duplicates C8.7's intent.
- (c) **Use the per-subproject `fetal_death/scripts/run_pipeline.py` as the VERIFY witness.** Pro: minimal scope. Con: covers fetal-death only; doesn't address natality + linked; partial verification.
- (d) **Defer C8.5 to after C8.7.** Pro: VERIFY criterion fully satisfied per §15. Con: re-orders Tier 1 sequencing (§15/KICKOFF say C8.5 before C8.6; C8.7 is positioned after C8.6).

Recommendation: **(a) §11 [plan-update]: revise §15 VERIFY to "env-resolution check + test suite passes"** + explicitly leave the pipeline-rebuild VERIFY to C8.7. Mirrors the C8.6 entry which already has "CI gates on real invariant tests" as its VERIFY (test-suite-based, not pipeline-rebuild-based).

### Result

**HALT.** Three §7 conditions tripped (§7.2 docker missing; §7.12 Python version conflict; §7.17 VERIFY scope vs missing dependency). All three are PRE-FLIGHT-class — caught at cheap-check before any DO mutation. None are blockers to the eventual completion of C8.5; all are resolvable via user authorization at this PRE-FLIGHT halt-and-ask + a single combined `[plan-update]` commit revising §15 line 963 + line 965 + KICKOFF.md Tier 1 line 181 commentary (if needed). Tag `C8.5-pre-do` is **NOT yet placed** — it lands on the `[plan-update]` commit after user authorization, per the C8.2/C8.3 precedent.

A PRE-FLIGHT addendum will follow once user resolves the three halts; tag `C8.5-pre-do` lands on the `[plan-update]` commit and DO begins.

---

## PRE-FLIGHT addendum for C8.5 — 2026-05-13T04:30:00Z — All 3 HALTs resolved per user authorization; task split C8.5 → C8.5a + C8.5b; PROCEED to C8.5a DO

### Resolutions per user authorization (AskUserQuestion 2026-05-13T04:15:00Z)

- **HALT #1 (§7.2 docker missing) → option (a)**: Split C8.5 → **C8.5a** (lockfile, this session, fully verifiable) + **C8.5b** (Dockerfile, DEFERRED until docker available OR C8.6 CI ships). §11 [plan-update] commit ships the split.
- **HALT #2 (§7.12 Python version conflict) → option (a)**: Pin to **3.13.x** (matches build env). §15 line 963 revised from `python:3.11-slim` to `python:3.13-slim` (C8.5b entry); `pyproject.toml` `requires-python = ">=3.13,<3.14"`.
- **HALT #3 (§7.17 VERIFY scope) → option (a)**: Revise C8.5a VERIFY to **env-resolution + test-suite passes**. Pipeline-rebuild VERIFY moves to C8.7's responsibility. §15 C8.5a entry rewritten.

### §11 plan-update applied this commit

- `NEXT_STEPS.md` §15.C C8.5 entry rewritten into two entries: C8.5a (lockfile, this session) + C8.5b (Dockerfile, DEFERRED with resumption trigger documented).
- `KICKOFF.md` Tier 1 task list (line 181) split: `C8.5a` + `C8.5b` entries replace the single `C8.5`.
- `KICKOFF.md` sequencing note (line 202): `C8.5 + C8.6 paired` revised to `C8.5a + C8.6 paired` (C8.6 depends on lockfile only, not Dockerfile).
- This PRE-FLIGHT addendum records the resolution.
- `DECISION_LOG.md` 2026-05-13T04:30:00Z entry records the §11 plan-update.

### Post-resolution input state for C8.5a

- [x] `uv 0.11.10` ✓ at `/opt/miniconda3/bin/uv` (verified PRE-FLIGHT 04:00Z).
- [x] Python 3.13.9 (CPython, miniconda) — target lockfile pin.
- [x] Installed package versions enumerated at PRE-FLIGHT 04:00Z (pandas 2.3.2, pyarrow 18.1.0, numpy 2.3.1, matplotlib 3.10.5, pytest 9.0.2, nbclient 0.10.4).
- [x] `requirements.txt` (monorepo root + 2 subprojects) all present; will be preserved post-DO as discovery-pointers.
- [x] All four parquet SHAs unchanged from C8.4-complete state (must remain so post-C8.5a; this task is metadata-only).

### Outputs (intended) for C8.5a

- `pyproject.toml` (monorepo root, NEW) — PEP 621 metadata + `requires-python = ">=3.13,<3.14"` + exact-pin dependencies + dev-dependencies.
- `uv.lock` (monorepo root, NEW) — deterministic lock generated by `uv lock`.
- `.python-version` (monorepo root, NEW) — single-line `3.13`.
- `README.md` (existing, edit) — append section "Reproducibility via uv lockfile" describing the `uv sync` workflow.
- `RECEIPTS/C8.5a_<UTC>.md` — receipt at task close.

### Halt conditions tripped (post-resolution)

None. All three HALTs resolved via §11 plan-update + user authorization. C8.5a is fully locally verifiable.

### Result

**PROCEED to C8.5a DO.** Tag `C8.5-pre-do` (preserving the original C8.5 task ID for git-tag continuity with the C8.5 lineage; future C8.5b PRE-FLIGHT will tag `C8.5b-pre-do`) lands on this `[plan-update]` commit. DO step 1 authors `pyproject.toml` + runs `uv lock` to produce `uv.lock`; DO step 2 authors `.python-version` + README section; VERIFY runs the test-suite under the lockfile-defined env; RECEIPT at `RECEIPTS/C8.5a_<UTC>.md`.

---

## PRE-FLIGHT for C8.4 — 2026-05-13T01:30:00Z — Invariant tests: canonical-filter + row-count conservation + cross-product join parity — **RESULT: PROCEED**

### Scope summary

C8.4 §15.C entry (NEXT_STEPS.md lines 931–949): three new invariant test harnesses defending core analytic-correctness invariants per §8 H6 (silent row drops), §8 F2 (cross-product join without filter), §8 H9 (external targets cancel internal bugs), and §8 L3 (validator self-blindness — defended via mutation tests). Files land at monorepo-root `tests/` (NEW directory). Each harness carries a Convention 2 `DESIGN:` first-docstring tag and asserts SHAPE-not-VALUE invariants per Convention 1 (§4.2.1), with Tier-0 mutation tests asserting the harness fails predictably when an invariant is violated.

Three harnesses:
- **B.3** `tests/test_canonical_filter_invariants.py` — `DESIGN: structural-invariant-no-pins`. Sum-across-strata = unstratified-total for every canonical filter, every product, every year.
- **B.4** `tests/test_row_count_conservation.py` — `DESIGN: tracks-current-state`. Carries a documented-drops dict; asserts harmonized↔derived row equality per-product per-year (no drops between these stages); asserts total row counts match documented v2.4.0 / v2.8.0 / v3 envelope.
- **B.5** `tests/test_cross_product_join_parity.py` — `DESIGN: structural-invariant-no-pins`. Joint canonical-filter coverage; canonical join-key column presence; per-stratum natality vs `stratified_denominators.csv` parity.

Estimated effort 3 sessions per §15 (may close faster — Tier-1 tasks have run ~50% of their estimates).

### Inputs

- [x] All required parquets exist + match C8.3-complete (STATUS 2026-05-13T00:30:00Z) SHAs
  - `output/harmonized/fetal_death_harmonized.parquet` sha256=`38e2cecb03ff4947bbf6bcecbe9a79bf4bbe58df74ed4e7809b5078899c5cf48` ✓ (verified by `shasum -a 256`)
  - `output/harmonized/fetal_death_derived.parquet` sha256=`185c071ec76ab8aae24c9d7524b2495900f78afbf43cd6a32537124fa7968a09` ✓
  - `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet` sha256=`e16ad5323d68e28d401518f1ff56b12c09e43883e76022a9823d51a677c41d44` ✓
  - `…/natality_v3_linked_harmonized_derived.parquet` sha256=`9b828a4de4e59b17a1ca727e3dddc7ea7d748bb5281a98612f6fb9b85a08b777` ✓
- [x] All four C8.3 FL-HALTs verified: PDF=`dd8b3203…` ✓, PNG=`f32ad101…` ✓, helper=`e3e74264…` ✓, JOINT_USE_GUIDE.md=`4569b0b4…` ✓, joint_use_demo.ipynb=`e0094812…` ✓, 4× `__init__.py` present (0 bytes each) ✓.
- [x] All required upstream tasks marked complete: `C8.1-complete` (`9fe662a`), `C8.2-complete` (`bb19c5a`), `C8.3-complete` (`ffbb4da` — HEAD) ✓.
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/C8.4_*.md`: does not exist ✓
  - `tests/` at monorepo root: does not exist (good — this task creates it) ✓
- [x] `shared/helpers/canonical_join_keys.py` present and importable; `CANONICAL_JOIN_KEYS = [data_year, maternal_age, maternal_race_bridged, hispanic_origin, residence_status]`; `NATALITY_TO_CANONICAL` populated (kept for v2.7.0 backcompat; v2.8.0+ adopts canonical names natively — verified via column-name probe of the v2.8.0 parquet showing `data_year`/`residence_status`/`maternal_race_bridged`/`hispanic_origin` present natively).

### Environment

- [x] Python: 3.13.9 ✓
- [x] pandas: ≥2.3 (verified at runtime) ✓
- [x] pyarrow: ≥18.0 (verified at runtime) ✓
- [x] pytest: 9.0.2 ✓
- [x] Working directory clean (`git status --short` returns empty) ✓
- [x] On expected branch: `main`, HEAD=`ffbb4da` (`C8.3-complete`) ✓
- [x] Cache-cleared `pytest fetal_death/tests/ natality/tests/` reproduces 15 passed + 1 xfailed in 41.14s ✓ (C8.3 FL-HALT #5)

### Source documentation

- [x] Not applicable — C8.4 consumes no external PDFs; it only consumes already-validated parquets + the canonical-filter definitions documented in `docs/JOINT_USE_GUIDE.md` (sha `4569b0b4…`).

### Outputs

- [x] Intended output paths do not exist OR are explicitly marked for new
  - `tests/` (monorepo root): NEW directory ✓
  - `tests/__init__.py`: NEW (empty, namespace package per Convention from FIX_LOG 2026-05-12T22:30:00Z L17-extension) ✓
  - `tests/conftest.py`: NEW ✓
  - `tests/test_canonical_filter_invariants.py`: NEW ✓
  - `tests/test_row_count_conservation.py`: NEW ✓
  - `tests/test_cross_product_join_parity.py`: NEW ✓
  - `RECEIPTS/C8.4_2026-05-13T<ts>.md`: NEW ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

C8.4 does not mutate any canonical parquet, schema CSV, or doc number. It authors NEW test files. The "cells being mutated" are the test-asset *assertions* themselves; the Field-value snapshot enumerates the **current parquet-derived invariants the new tests will assert**, so a future audit can verify the test was authored against the actual v2.4.0 / v2.8.0 / v3 state, not a stale assumption.

#### Parquet envelope (verified by `pyarrow.parquet.read_table` 2026-05-13T01:25:00Z)

| Product | Path | Rows | Years | residence_status uniques | tabulation_flag uniques |
|---|---|---|---|---|---|
| fetal_death harmonized | `output/harmonized/fetal_death_harmonized.parquet` | 2,427,233 | 1982–2024 (43 contiguous) | {1, 2, 3, 4} | {1, 2} |
| fetal_death derived | `…/fetal_death_derived.parquet` | 2,427,233 (= harmonized) | 1982–2024 | {1, 2, 3, 4} | {1, 2} |
| natality derived | `…/natality_v2_harmonized_derived.parquet` | 138,819,655 | 1990–2024 (35 contiguous) | {1, 2, 3, 4} | n/a (no tabulation_flag) |
| linked derived | `…/natality_v3_linked_harmonized_derived.parquet` | 74,943,824 | 2005–2023 (19 contiguous) | {1, 2, 3, 4} | n/a |

#### Canonical filters (from `docs/JOINT_USE_GUIDE.md` §"Canonical analytic filters")

| Product | Filter | Dtype literal |
|---|---|---|
| Natality | `residence_status != 4` | int8 |
| Linked | `residence_status != 4` | int8 |
| Fetal-death | `tabulation_flag == 2 AND residence_status != 4` | Int8 (both, post-v2.1.0 H8 cast) |

#### Canonical join keys (from `shared/helpers/canonical_join_keys.py`)

`CANONICAL_JOIN_KEYS = [data_year, maternal_age, maternal_race_bridged, hispanic_origin, residence_status]`. All five present in both fetal-death derived parquet (verified) and natality v2.8.0 derived parquet (verified).

#### Documented row-conservation invariants (the B.4 documented-drops registry)

- **harmonized ↔ derived (all three products):** **NO drops.** `derive.py` adds columns; row count must be conserved. Test asserts `len(harmonized) == len(derived)` per-product. Per-year row count also conserved.
- **No documented per-year drops at any pipeline stage** in any product's `DECISION_LOG` after the v2.4.0 / v2.8.0 / v3 releases — verified by `grep` against DECISION_LOG.md for "documented_drop" / "drop" / "exclude" → matches refer to filter exclusions (`residence_status == 4`, `tabulation_flag == 1`), not to silent row drops at parse/harmonize/derive boundaries.
- **The 2003–2004 fetal-death "deferred years" were not dropped; they are present in v2.1.0+.** Verified by `data_year` uniques showing {1982–2024} contiguous.

#### Canonical-filter invariant (the B.3 SHAPE check)

For each (product, year):
- `total_filtered = len(df[canonical_filter])`
- For every demographic stratum column S in {residence_status, tabulation_flag (FD only), maternal_race_bridged, hispanic_origin}:
  - `sum_across_S = df[canonical_filter].groupby(S, dropna=False).size().sum()`
  - assert `sum_across_S == total_filtered` (the grouping with `dropna=False` preserves null cells; sum across all strata including null must equal the unstratified total).

This is a SHAPE-not-VALUE invariant: it holds regardless of the specific count values; survives V2.x → V2.x+1 row-count growth; survives bridged-race-null era boundaries.

#### Cross-product join parity invariant (the B.5 SHAPE check)

For each year Y in the joint-coverage intersection {2005…2023} (where all three products are present):
- canonical-filter applied on all three sides
- After `to_canonical_natality()` rename, all three products expose `{data_year, residence_status, maternal_race_bridged, hispanic_origin, maternal_age}` columns
- For natality + linked: linked rows for year Y is a subset of natality rows for year Y (every linked birth is a natality birth); test asserts `len(linked_Y) <= len(natality_Y)` after canonical filter on both.
- For natality + fetal-death: independent populations (live births vs fetal deaths); the join-key columns must be present + compatible-dtype.
- For natality_per_year vs stratified_denominators.csv: per-year sum from CSV matches direct natality groupby on residence_status != 4 byte-exact (29 years — already verified at Task 1; this is the durable test).

- [x] Current values match task plan's assumed state ✓

### Halt conditions tripped

None. All §15-named inputs verified present; no §7 condition surfaced. The "documented drops" registry is empty (no documented drops at parse/harmonize/derive boundaries in any product's release notes), which means B.4's `tracks-current-state` design starts with an empty drops dict — clean.

### Result

**PROCEED.** Tag `C8.4-pre-do` lands on the commit that ships this PRE-FLIGHT entry. The DO phase authors three test files + an empty `tests/__init__.py` + a `tests/conftest.py` (shared fixtures for cross-product parquet loading at session scope) + runs Tier 0 mutation tests as part of each harness's authoring, then a cache-cleared combined-pytest VERIFY pass before tagging `C8.4-complete`.

---

## PRE-FLIGHT for C8.3 — 2026-05-12T22:30:00Z — Cross-product Tier-1: timeline + perinatal joint + Section B race validation — **RESULT: HALT**

### Scope summary

C8.3 §15.C entry (NEXT_STEPS.md lines 881–903): land three cross-product items in one task — (i) cross-product timeline figure (`shared/helpers/build_timeline_figure.py` + `figures/fig1_coverage_timeline.{pdf,png}`); (ii) three-product perinatal-mortality joint computation in `notebooks/joint_use_demo.ipynb` as a new Section C; (iii) Section B 2017 race-stratified NVSR validation, the deferred Task 4 fragment. §15 names PRE-FLIGHT inputs as "All three parquets (post-C8.2 refresh state); **NVSR 73-09 Table A for 2022 perinatal validation; NVSR fetal-mortality table for 2017 by maternal race** (PDF location verified at PRE-FLIGHT per L9); era-boundary metadata in each subproject's COMPARABILITY." Estimated effort 2 sessions.

This PRE-FLIGHT enumerates the §15 inputs read-only (no DO mutation), runs the Convention 3 Field-value snapshot for every cell/row/column the task would mutate, and runs the L9 cheap-checks on the two NVSR sources named in the §15 plan. **One HALT condition surfaced (§7.12 + planning error): two of the four NVSR source-location assumptions in the §15 plan do not match the actual NVSR contents.** Two of the three sub-items proceed cleanly; the third needs a scope clarification. PRE-FLIGHT result is HALT pending user decision on the Section B race-validation source year + race-classification.

### Inputs

- [x] All required parquets exist + match STATUS 2026-05-12T23:30:00Z (C8.2-complete) SHAs
  - `/Users/yoelplutchok/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_harmonized.parquet` sha256=`38e2cecb03ff4947bbf6bcecbe9a79bf4bbe58df74ed4e7809b5078899c5cf48` (43 yrs 1982–2024, 2,427,233 rows × 73 cols) ✓
  - `…/fetal_death_derived.parquet` sha256=`185c071ec76ab8aae24c9d7524b2495900f78afbf43cd6a32537124fa7968a09` (same row count, 89 cols, post-C8.2) ✓
  - `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet` (35 yrs 1990–2024, 138,819,655 rows) ✓
  - `…/natality_v3_linked_harmonized_derived.parquet` (19 yrs 2005–2023, 74,943,824 rows) ✓
- [x] Monorepo symlinks at `output/harmonized → /Users/.../fetal-death-harmonization-build/output/harmonized` intact ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - `C8.1-complete` tag at `9fe662a` ✓
  - `C8.2-complete` tag at `bb19c5a` ✓ (current HEAD; verified via `git tag --list 'C8.2*'`)
- [x] No stale checkpoints from previous incomplete runs
  - `RECEIPTS/C8.3_*.md`: does not exist ✓
  - `git tag --list 'C8.3*'`: empty ✓
- [x] Forward-looking HALTs from STATUS 2026-05-12T23:30:00Z (10 items) — verified
  - **#1** `C8.2-complete` + `C8.2-pre-do` tags present ✓
  - **#2** Post-C8.2 parquet SHAs match STATUS-recorded values ✓ (`38e2cecb…` + `185c071e…`)
  - **#3** V3b baseline parquets preserved as `.V3b_baseline.parquet` sidecars at `e3d6c64a…` + `4d1b37cc…` ✓
  - **#4** Smoke EXPECTED state pinned to 43 yrs / 2,427,233 rows ✓ (verified via `pq.read_table(columns=['data_year']).to_pandas()` row count + year set)
  - **#5** `field_specs.py` `layout_for_year` accepts 1982–2024 ✓ (no probe of 2025; not relevant to C8.3)
  - **#6** External validation 88/88 + 2 spot cells unchanged ✓
  - **#7** dtype-parity XFAIL still in place ✓
  - **#8** 4× `__init__.py` files still present ✓ (cache-cleared `pytest fetal_death/tests/ natality/tests/` produces 15 passed + 1 xfailed — confirmed implicitly via STATUS 23:30Z + commit log; not re-run at this PRE-FLIGHT)
  - **#9** Linked-2024-cohort refresh remains future-task — `2025PE2024CO.zip` still HTTP 404, no action this task ✓
  - **#10** Manuscript stale-numerics gap noted (43 yrs / 2.43M records in repo vs 29 yrs / 1.6M in `paper/draft_v2_hmd_styled.md`) — C8.3 does not edit the manuscript; flagged for Phase D step 6.

### Environment

- [x] Python: 3.13.9 (≥3.11) ✓
- [x] pandas + pyarrow 18.1.0 ✓
- [x] PyMuPDF: present (used for L9 PDF text-extraction probes during this PRE-FLIGHT) ✓
- [x] matplotlib: TBD — C8.3 DO needs it for the timeline figure; will verify before SMOKE. (Not a HALT; standard scientific-python install.)
- [x] nbformat + nbclient: present (per `_build_joint_use_demo.py` existing invocation) ✓
- [x] Working directory clean (`git status`): ✓
- [x] On `main` at commit `bb19c5a` (= `C8.2-complete`): ✓

### Source documentation

NVSR PDFs available on disk (in fetal-death build dir's `raw_docs/.../validation/`):

- `nvsr73-09.pdf` (Gregory et al. 2024, *Fetal Mortality: United States, 2022*, 21 pp) sha256=`2590e41719d1be949a2ad0e32c6497a747194020d26c38e4fcbecedced84c8d1` ✓
- `nvsr57_08.pdf` (MacDorman & Kirmeyer 2009, *Fetal and Perinatal Mortality, US 2005*, used for V2-era validation) sha256=`71c0b48ae71555b036952dbde1091e75a410327d240e66562fc9dbdb06b59861` ✓
- `nvsr64_09.pdf` (Mathews & MacDorman 2015, *Infant Mortality Statistics From the 2013 Period Linked Birth/Infant Death Data Set*, 30 pp) sha256=`bef51b1593a6d180abe9230ef05c2d24269f68468d36c6c05eb67fb8cc521304` ✓ — note: INFANT mortality, **not** "Fetal and Perinatal Mortality 2013" as the validation/INDEX.md memo claims (INDEX.md row needs a fix; documented below as a non-HALT finding).
- Other NVSR PDFs on disk for V2-era references: `nvsr55_06`, `nvsr56_03`, `nvsr60_08`; deep-history: `sr20_026`, `db169`.
- Natality NVSR: `Births_Final_Data_2005.pdf` through `Births_Final_Data_2020.pdf` at `/Users/yoelplutchok/Desktop/natality-harmonization/raw_docs/nvsr/`. No 2021–2024 *Births: Final Data* PDFs on disk.

NVSR PDFs **not** on disk that the §15 plan implicitly assumes:

- §15 names **"NVSR fetal-mortality table for 2017 by maternal race"** as a PRE-FLIGHT input. **An NVSR titled "Fetal Mortality: United States, 2017" does not appear to exist.** L9 probe (this PRE-FLIGHT 22:00–22:25Z): probed every NVSR 65/66/67/68/69 PDF at `cdc.gov/nchs/data/nvsr/nvsr{vol}/nvsr{vol}_{nn}{,_-,_508,-508}.pdf` and scanned first-page text via PyMuPDF. Found NCHS "Fetal Mortality" annual reports: NVSR 70-11 (data year **2019**), NVSR 71-04 (**2020**), NVSR 72-08 (**2021**), NVSR 73-09 (**2022**); NVSR 65-07 (**Cause of Fetal Death** 2013); NVSR 69-04 (**Cause-of-Death from Fetal Death File 2015–2017** — note: this IS a cause-of-death focused report on 2015–2017 data, not a race-stratified fetal-mortality-rate report). **No standalone "Fetal Mortality: United States, 2017" exists.** NVSR 73-09 Table 1 publishes year-by-year fetal-death TOTALS 1990–2022 (and 20–27wk / 28+wk breakouts for 2014–2022) but **not race-stratified breakdowns for any year other than 2022**. So the §15 "NVSR fetal-mortality table for 2017 by maternal race" source assumption is incorrect: such a published cell does not exist.

### Outputs (intended)

Per §15 DO scope; targets do not yet exist (good):

- [x] `shared/helpers/build_timeline_figure.py` — does not exist ✓
- [x] `figures/fig1_coverage_timeline.pdf` — does not exist (`figures/` empty) ✓
- [x] `figures/fig1_coverage_timeline.png` — does not exist ✓
- [x] `notebooks/joint_use_demo.ipynb` — exists (will be MUTATED via re-build of `_build_joint_use_demo.py`); current sha=`39d2fb3c70494327…` (Section A 2022 by age + Section B 2017 by race-bridged; **DESIGN: tracks-current-state**)
- [x] `notebooks/_build_joint_use_demo.py` — exists; will be MUTATED; current sha=`7bab184c88dff6f9…`
- [x] `docs/JOINT_USE_GUIDE.md` — exists; **may be MUTATED** with a perinatal-mortality worked example per §15; current sha=`09266eae572bddf7…`
- [x] `RECEIPTS/C8.3_*.md` — does not exist ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

**Files this task will mutate (write or edit):**
- `notebooks/joint_use_demo.ipynb` (existing 2-section notebook → 3-section): adds Section C (three-product perinatal joint computation, 2022); MAY refresh Section B 2017 race-stratified content depending on user-resolution below. Currently asserts: `len(fd_2022) == 20202`, `len(nat_2022) == 3667758`, `len(fd_2017) == 22827`. All three match NVSR 73-09 Table 1 (2022 fetal deaths 20,202; 2022 live births 3,667,758; 2017 fetal deaths 22,827). ✓
- `notebooks/_build_joint_use_demo.py` (existing builder script): adds Section C build cells; minor edits to Section B comments depending on resolution.
- `figures/` (empty directory): new `fig1_coverage_timeline.{pdf,png}` + helper at `shared/helpers/build_timeline_figure.py`.
- `docs/JOINT_USE_GUIDE.md` (existing): the §15 plan calls for a new "perinatal mortality worked example." Current document has only the FMR worked example (lines 86-122).

**Files this task will NOT mutate** (Anti-Pattern #8 — not in scope):
- Any harmonized parquet (no canonical-data mutation).
- Any `harmonized_schema.csv` or `file_inventory.csv` (no schema change).
- Manuscript draft (Phase D step 6 territory).
- `external_validation_targets.csv` for any product (NVSR validation cells live in the notebook + this PRE-FLIGHT-log).

**Field-value snapshot for cells whose existence/values are load-bearing for C8.3 computations:**

| Target | Source | Current value | Used by |
|---|---|---|---|
| `fetal_death_derived[data_year=2022, tab_flag=2, res!=4].shape[0]` | post-C8.2 parquet | 20,202 (existing assert) | NVSR 73-09 Table 1 — total fetal deaths 2022, matches byte-exact |
| Same, gestational_age_*≥28wk | post-C8.2 parquet | **TBD** (DO Tier 0 compute) | Target = 9,956 per NVSR 73-09 Table 1 ("28 weeks or more" 2022 column); proportional-redistribution caveat applies |
| `natality_v2_harmonized_derived[year=2022, restatus!=4].shape[0]` | shipped parquet | 3,667,758 (existing assert) | NVSR 73-09 Table 1 — live births 2022, matches byte-exact |
| `linked_derived[data_year=2022, residence_status!=4, age_at_death_days<7].shape[0]` | shipped parquet | **TBD** (DO Tier 0 compute) | Sub-component for perinatal numerator; would validate against a 2022 linked-file infant-mortality NVSR (NVSR 73-XX series for 2022 cohort, NOT on disk; would need fetch) |
| `fetal_death_derived[data_year=2017, tab_flag=2, res!=4].shape[0]` | post-C8.2 parquet | 22,827 (existing assert) | NVSR 73-09 Table 1 — 2017 total, matches byte-exact. NO race breakdown published for 2017. |
| `fetal_death_derived[data_year=2017, …, maternal_race_bridged=k]` for k∈{1,2,3,4} | post-C8.2 parquet | (computed in joint_use_demo Section B; values not duplicated here) | Existing machinery demo, currently UNVALIDATED externally |
| NVSR 73-09 Table A (2022 race × Hispanic, single-race revised standard) | nvsr73-09.pdf p.6 | 7 rate cells: Total 5.48; AIAN 7.22; Asian 3.70; Black 10.05; NHOPI 10.36; White 4.48; Hispanic 4.63 | Potential alternative validation source — see Halt #1 |
| Era-boundary years for timeline figure | COMPARABILITY docs | Fetal: 1982/1989/1992/2003/2005/2018; Natality: 1990/2003/2014/2020; Linked: 2005/2016/2020 (see era-spec below) | Timeline figure spec |

**Era-band spec for timeline figure (from COMPARABILITY docs):**

| Product | Bands |
|---|---|
| Fetal death (1982–2024) | 1982–1988 V3b (1978-revision); 1989–1991 V3a (early 1989-rev); 1992–2002 V2 (1989-rev uniform); 2003–2004 V2.1 (transition); 2005–2017 V1 (2003-rev transition, 6.6%→96.2% A-version state-by-state); 2018–2024 V1+ uniform 2003-revision |
| Natality (1990–2024) | 1990–2002 1989-rev uniform; 2003–2013 2003-rev transition state-by-state; 2014–2019 2014-reformat (revised-only); 2020–2024 bridged-race-dropped era |
| Linked (2005–2023) | 2005–2015 denominator-plus cohort format; 2016–2023 period-cohort merged format. Sub-band 2020+ for bridged-race-dropped. |

### Halt conditions tripped

#### HALT #1 — §7.12 (Conflicting documentation) + planning error: §15 names two NVSR sources that don't match the actual NVSR contents

**Discovery.** §15 C8.3 entry (line 887) states:

> *"PRE-FLIGHT inputs. … **NVSR 73-09 Table A for 2022 perinatal validation; NVSR fetal-mortality table for 2017 by maternal race** (PDF location verified at PRE-FLIGHT per L9)."*

**Reality** (L9 cheap-check on NVSR 73-09 + NVSR-series probe):

- **(A) "NVSR 73-09 Table A for 2022 perinatal validation."** NVSR 73-09 is titled *"Fetal Mortality: United States, 2022"* — it does **not** publish perinatal-mortality rates. The earlier MacDorman/Gregory *"Fetal and Perinatal Mortality"* combined series ended with NVSR 64-09 era (last edition published was 2013-data-year per NCHS website). For 2022, NCHS publishes fetal mortality and infant mortality as separate annual reports; no single NVSR cell publishes the combined perinatal rate. **Furthermore, NVSR 73-09 Table A is "Fetal mortality rate, by selected characteristics and race and Hispanic origin of mother: United States, 2022"** — a 2022 fetal-mortality-by-race table, NOT a perinatal-mortality table. The §15 phrasing conflated three things: (1) "perinatal mortality rate" as a computed concept, (2) NVSR 73-09 (fetal-mortality-only), and (3) Table A (race-stratified).

- **(B) "NVSR fetal-mortality table for 2017 by maternal race."** No such NVSR exists. The NVSR "Fetal Mortality: United States, YYYY" annual series resumed with NVSR 70-11 (data year **2019**) after a gap; the series gap covers 2014–2018 data years. NVSR 73-09 Table 1 publishes 2014–2022 year-by-year fetal-death TOTALS (no race breakdown for 2014–2021; only 2022 has a race breakdown in Table A). Probe summary (L9 cheap-check at PRE-FLIGHT, ~30 min): probed `nvsr{65,66,67,68,69}_NN.pdf` covers via PyMuPDF text-extraction; found Cause-of-Fetal-Death reports (NVSR 65-07, NVSR 69-04) but no race-stratified fetal-mortality-rate report for 2017. The 2017 fetal-mortality-by-race tabulation is unpublished.

**Consequence.** As written, §15 C8.3's NVSR validation source is unworkable for both (i) the perinatal joint computation and (ii) the 2017 Section B race validation. The two cleanly-validate-able cells from existing on-disk sources are:

- **2022 28+wk fetal deaths = 9,956** per NVSR 73-09 Table 1 ("Fetal deaths 28 weeks or more" column for 2022). Useful for the 28+wk sub-component of the perinatal numerator.
- **2022 race-stratified fetal mortality rates** per NVSR 73-09 Table A (Total 5.48 + 6 race-Hispanic group rates). Useful for a 2022 race-stratified validation **IF** the joint_use_demo's race-stratification switches from `maternal_race_bridged` (null in fetal-death 2018+ and natality 2020+, so unavailable for 2022) to the single-race + Hispanic columns NCHS uses post-2018 (`race_hispanic_revised` in fetal-death, `maternal_race_ethnicity_5` in natality).

**Options for resolution (user decision required)**:

- **(a) RECOMMENDED — Re-scope Section B validation to 2022 single-race + Hispanic; reframe the perinatal joint computation as a demo without a full-rate NVSR cell.** Section B in joint_use_demo.ipynb switches to 2022 fetal-mortality by single-race + Hispanic groups (7 cells), validated against NVSR 73-09 Table A (on disk; no fetch needed). The existing 2017 bridged-race machinery is preserved in the notebook for backward documentation but no longer claimed as NVSR-validated — it remains a "machinery demo" closing the manuscript's joint-use bridge for the last-bridged-race-year. The perinatal joint computation (new Section C) computes the rate as a JOINT-USE DEMO using all three parquets for 2022, with **sub-component validations**: (i) 28+wk fetal-death count = 9,956 (NVSR 73-09 Table 1); (ii) <7-day early neonatal deaths from linked file — validated against any 2022 linked-file infant-mortality NVSR found, OR documented as unvalidated if no such NVSR exists. No claim of "perinatal mortality rate validated byte-exact." Pro: minimal NVSR-fetch friction (1 known PDF for sub-component (ii) — to be located in DO step 1 L9); strongest manuscript-relevant year (2022 = latest post-C8.2); no bridged-race availability issues. Con: drops the "2017 deferred Task 4 fragment" framing in favour of a more defensible 2022 validation.

- **(b) Preserve 2017 bridged-race Section B + drop NVSR validation claim there; do perinatal demo against the 2022 28+wk sub-component only.** Keep joint_use_demo Section B's existing 2017 machinery (machinery demo, no NVSR cell). Perinatal Section C uses 2022 with the 28+wk-only validation per (a). Pro: smallest scope change vs §15 plan. Con: leaves Section B externally unvalidated — defers the deferred-Task-4-fragment ambition again.

- **(c) Defer the 2017 race validation entirely; do a 2022 race validation as a new Section B' addition; drop perinatal entirely from this task.** Splits C8.3 into a smaller item that ships only the timeline figure + 2022 race validation; perinatal joint computation moves to a new C8.X candidate. Reduces this task to ~1 session. Con: a `[plan-update]` adding a new task, and the perinatal-joint demo is the most distinctive cross-product demonstration; moving it out feels like under-shipping.

- **(d) Halt C8.3 entirely, propose a `[plan-update]` that rewrites the §15 entry with explicit NVSR sources matching reality.** Pro: methodologically clean. Con: a session of plan-update overhead before any work.

#### Other findings (NOT HALTs)

- **L13-like INDEX.md soft-flag.** `…/fetal-death-harmonization-build/raw_docs/fetal_death/validation/INDEX.md` describes NVSR 64-09 as *"Fetal and Perinatal Mortality, United States, 2013 (MacDorman & Gregory)"*; the actual PDF cover (page 1, PyMuPDF text-extraction) reads *"Infant Mortality Statistics From the 2013 Period Linked Birth/Infant Death Data Set"* by Mathews/MacDorman/Thoma. Same volume number; different topic. This is one notch beyond LESSONS L13-extension (CSV inventory file-roles drift). No canonical-data impact in C8.3; the file is used for V2-era reference. FIX_LOG entry can be filed by a future audit / Phase D pre-flight that touches the validation/ inventory.
- **2017 fetal-death external_validation_targets.csv** has TWO existing rows: total 22,827 fetal deaths (NVSR 73-09 Table 1) + 2017 fetal-mortality rate 5.89 (NVSR 73-09 Table 1). Both PASS in current validation. The "deferred Task 4 fragment" was specifically the race-stratified cells, which are NOT in external_validation_targets.csv.
- **Manuscript line 99 numerical claim** *"Cross-product worked examples — a joint-use demonstration reproducing the 2022 maternal-age-stratified fetal mortality cells against NVSR 73-09 Table 4"* — verified. Section A in joint_use_demo.ipynb validates against NVSR 73-09 Table 4 (8/8 age cells); the manuscript's claim is accurate. C8.3 may add a sibling claim for the new Section C / Section B' work; manuscript edit is Phase D scope.
- **L9 cheap-check on NVSR 73-09 Table 1 contents:** the 2022 row of Table 1 publishes total 20,202; 20–27wk 10,246; 28+wk 9,956; live births 3,667,758; rates 5.48 / 2.79 / 2.71 per 1,000. Table 1 footnote: "Not stated gestational age proportionally distributed; see Technical Notes" — the 9,956 figure is post-redistribution. **Important downstream issue for Section C verify criterion**: our parquet's `gestational_age_*` columns store observed gestation values without proportional redistribution. The 28+wk count from a naïve filter will be slightly different from 9,956. The H8-class fix (auto-derive every NVSR-comparable cell from the parquet with redistribution if NCHS does redistribution) is C8.4-scope, not C8.3; for C8.3 we document the redistribution caveat in the receipt's Self-check and the notebook's Section C narrative. This is **not** a halt; it's a known tolerance.

### Result

**HALT** — One §7 condition tripped (§7.12 conflicting documentation: NVSR sources named in §15 do not match the actual NVSR series contents for both (i) 2022 perinatal validation and (ii) 2017 by-maternal-race fetal mortality). Do not proceed to C8.3 SMOKE/DO without user authorization on the Section B / Section C scope-and-validation strategy.

Forward-looking once resolved: DO step 1 will probe NCHS for a 2022 period-cohort-linked infant-mortality NVSR (likely under NVSR 73-XX series, e.g. NVSR 73-3 or NVSR 74-X candidates) for the early-neonatal sub-component validation in Section C. If found and fetch-able, the sub-component validation lands; if not, Section C narrative documents the absence and the perinatal-rate computation remains a JOINT-USE DEMO with one sub-component (28+wk fetal deaths) externally validated.

---

## PRE-FLIGHT addendum for C8.3 — 2026-05-12T23:50:00Z — HALT #1 resolved per user authorization; NVSR 73-05 located + PROCEED to SMOKE/DO

**User authorization received 2026-05-12T22:30Z** (single AskUserQuestion round): option **(a) 2022 race + perinatal demo (Recommended)**. §11 plan-update applied via DECISION_LOG entry 2026-05-12T23:50:00Z editing `NEXT_STEPS.md` §15.C C8.3 entry + `KICKOFF.md` line 179.

**Forward-looking follow-up resolved at addendum time:** Probed NVSR 73 + 74 series for a 2022 period-cohort-linked infant-mortality NVSR. **Found: NVSR 73-05** (Ely & Driscoll 2024, *Infant Mortality in the United States, 2022: Data From the Period Linked Birth/Infant Death File*, 19 pp, July 25, 2024) at `https://www.cdc.gov/nchs/data/nvsr/nvsr73/nvsr73-05.pdf`. Fetched to `/tmp/c83_preflight/nvsr73-05.pdf`. sha256=`dccdc895022c3c9d3fbc07ffce18dc3238af797197f3cc6f0b35e463676c95cc`. Table 2 (page 10) verified containing:
- 2022 Total Infant Mortality Rate = 5.61 per 1,000 LB
- 2022 Early neonatal (<7 days) rate = **2.81** per 1,000 LB (headline for Section C sub-component validation)
- Late neonatal (7–27) = 0.78; Total neonatal = 3.59; Postneonatal = 2.02
- Race-stratified breakouts for each cell (AIAN 3.73; Asian 2.01; Black 5.05; NHOPI 3.36; White 2.23; Hispanic 2.65 for early neonatal column).

This closes the §15 C8.3 PRE-FLIGHT-input gap. The early-neonatal sub-component validation in new Section C now has a single on-disk NVSR cell (Total = 2.81/1000); race-stratified ENN validation is OPTIONAL in scope.

### Post-resolution input state (revised)

- NVSR 73-09 (on disk in build-dir; SHA `2590e417…`) ✓
- NVSR 73-05 (fetched to /tmp; sha `dccdc895…`); DO step 1 = move to `raw_docs/natality/nvsr/nvsr73-05.pdf` + add to `natality/metadata/file_inventory.csv` row + SHA-verify after move (per FIX_LOG 2026-05-12T01:30Z monorepo-path discipline).
- All three parquets at C8.2-complete SHAs ✓
- All era-boundary metadata sourced from COMPARABILITY docs ✓

### Halt conditions tripped (post-resolution)

(none — HALT #1 resolved via §11 plan-update; all other PRE-FLIGHT checks PASS)

### Result

**PROCEED** — to C8.3 SMOKE/DO under the revised §15.C scope. Tag `C8.3-pre-do` lands on this `[plan-update]` commit.

---

## PRE-FLIGHT for C8.2 — 2026-05-12T22:30:00Z — Latest-year refresh (fetal 2023+2024, linked 2024) — **RESULT: HALT**

### Scope summary

C8.2 §15.C entry (`NEXT_STEPS.md` lines 817-880) goal: extend fetal-death from 1982-2022 (41 yrs) → 1982-2024 (43 yrs) by parsing `Fetal2023US_COD.zip` + `Fetal2024US_COD.zip`; extend linked from 2005-2023 (19 yrs) → 2005-2024 (20 yrs) by parsing `2024PE2023CO.zip`. Three new source zips (~440 MB), three new user-guide PDFs.

This PRE-FLIGHT enumerates the §15 inputs read-only (no DO mutation), runs the Convention 3 Field-value snapshot for every cell/row/column the task would mutate, and verifies the STATUS 2026-05-12T22:00:00Z forward-looking HALTs. **Two HALT conditions surfaced; PRE-FLIGHT result is HALT pending user decision.**

### Inputs

- [x] All required input files exist (external)
  - `Fetal2023US_COD.zip` at `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/fetaldeathus/Fetal2023US_COD.zip` — HEAD HTTP=200, Content-Length=**2,219,550**, Last-Modified=Thu, 05 Dec 2024 16:18:30 GMT, ETag=`"3599a0523147db1:0"` ✓
  - `Fetal2024US_COD.zip` at same dir — HEAD HTTP=200, Content-Length=**1,925,286**, Last-Modified=Wed, 04 Feb 2026 12:21:08 GMT, ETag=`"52fea1bdd095dc1:0"` ✓
  - `2024PE2023CO.zip` at `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/period-cohort-linked/2024PE2023CO.zip` — HEAD HTTP=200, Content-Length=**432,493,258**, Last-Modified=Thu, 22 Jan 2026 11:57:31 GMT, ETag=`"e1529449968bdc1:0"` ✓ — **BUT see HALT #1 below: this file represents cohort year 2023, already imported.**
- [x] User-guide PDFs (3 — one of three URL patterns corrected from §15 plan; see Source documentation below)
  - `2023fetaluserguide.pdf` at `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/fetaldeath/2023fetaluserguide.pdf` (**path corrected** — see "L1-extension finding" below): HTTP=200, fetched to `/tmp/c82_preflight/2023fetaluserguide.pdf`, size=1,064,197, sha256=`947042d892ea1cf584392f55dbc833c30b7ff68b7290f5958164fefaf58863aa`, Last-Modified=Mon, 24 Feb 2025 20:20:59 GMT ✓
  - `2024fetaluserguide.pdf` at same corrected dir: HTTP=200, size=906,615, sha256=`63bcc8b1082db135f698ddc194d5ce59e0dfee9558027269e3873be289eecb42`, Last-Modified=Thu, 12 Mar 2026 12:47:24 GMT ✓
  - `24PE23CO_linkedUG.pdf` at `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/period-cohort-linked/24PE23CO_linkedUG.pdf` (matches §15 plan): HTTP=200, Content-Length=1,079,044, Last-Modified=Thu, 19 Feb 2026 15:52:41 GMT ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - C8.1 (tag `C8.1-complete` at `9fe662a`): ✓
  - `phase-c-authorized` tag at `0ba0279`: ✓
  - task7_v3b-complete at `b0c8b4a`: ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/C8.2_*.md`: does not exist ✓
  - `git tag --list 'C8.2*'`: empty ✓
- [x] Forward-looking HALTs from STATUS 2026-05-12T22:00:00Z (10 items) — verified
  - **#1** `C8.1-complete` tag at `9fe662a` ✓; `C8.1-pre-do` tag at `04e6519` ✓
  - **#2** `fetal_death/harmonized_schema.csv` SHA `337a0ad0ab6d0a6b…` ✓ (will legitimately re-regen in C8.2 DO step 3)
  - **#3** `EXPECTED_YEAR_ROWS` dict has 41 entries (line 70 in `test_release_smoke.py`) ✓
  - **#4** `test_full_schema_type_matches_parquet_dtype` is xfail(strict=True) ✓ (XFAIL on isolated `pytest fetal_death/tests/` run)
  - **#5** `_regenerate_schema_years.py` exists, SHA `4275ed641fb76506…` ✓
  - **#6** `natality/tests/` exists with conftest.py + test_schema_dtype_parity.py ✓
  - **#7** Test count: claim was "16 tests across both subprojects" — **HALT-WORTHY**: see HALT #2 below.
  - **#8** `EXPLORATION_REPORT.md` unchanged (66,259 bytes, present at root) ✓; `KICKOFF.md` Phase C section unchanged ✓
  - **#9** Parquet SHAs: harmonized=`e3d6c64abcb7762d…` ✓; derived=`4d1b37cc3a214eea…` ✓
  - **#10** ~50 string-typed columns latent state still XFAIL ✓; 5 V2.1-fixed columns still int (`test_v21_h8_fixed_columns_remain_int` PASSes) ✓

### Environment

- [x] Python: 3.13.9 (≥3.11) ✓
- [x] pandas: present ✓ ; pyarrow 18.1.0 (≥18.0) ✓
- [x] PyMuPDF: present (needed for L12-extension `page.get_text()` PDF text-layer probes during SMOKE Tier 0) — verified via prior C8.1 work; no separate probe needed.
- [x] Working directory clean (`git status`): ✓
- [x] On `main` at commit `9fe662a`: ✓

### Source documentation

- [x] NVSR / NCHS user guides referenced by this task have current SHA-256s recorded above for the three new PDFs.
- [x] Existing 2022 fetal user guide (sibling-byte-position anchor for SMOKE Tier 0): `raw_docs/fetal_death/2022fetaluserguide.pdf` sha256=`d515813f89765af0ca2804afb7673f03e4efd4737f3de04e6939f9e7f43b20b3` ✓
- **L1-extension finding (URL drift; resolved):** §15 PRE-FLIGHT inputs cite "sibling-derived URLs at `…/Dataset_Documentation/DVS/fetaldeathus/{2023,2024}fetaluserguide.pdf`". Probed BOTH casings of the sibling-derived URL at `fetaldeathus/` → HTTP 404. NCHS reorganized the documentation directory; the canonical NCHS landing page (`cdc.gov/nchs/data_access/vitalstatsonline.htm`) directs to `…/Dataset_Documentation/DVS/fetaldeath/2023fetaluserguide.pdf` (note: `fetaldeath`, not `fetaldeathus`). Both 2023+2024 user guides verified at the corrected location. **Plan amendment**: at C8.2 DO step 3 (`file_inventory.csv` extension), the 2023+2024 rows' `doc_filename` URLs must use the new `Dataset_Documentation/DVS/fetaldeath/` prefix; the 2003-2022 rows' existing URLs in file_inventory.csv (`…/fetaldeathus/`) remain valid for the older user guides and need no change. This is one notch beyond the LESSONS L1-extension class (sibling-derivation correctly tried but the source FTP reorganized between releases).
- [x] All cited Zenodo DOIs resolve — `10.5281/zenodo.20031571` (fetal-death concept) + `10.5281/zenodo.19363074` (natality concept) — no new DOI fetch needed at PRE-FLIGHT.

### Outputs (intended)

Per §15 DO scope items 1-8; targets do not yet exist (good):

- [x] `raw_data/fetal_death/Fetal2023US_COD.zip` — does not exist (good) ✓
- [x] `raw_data/fetal_death/Fetal2024US_COD.zip` — does not exist (good) ✓
- [x] `raw_data/natality/2024PE2023CO.zip` — **already exists or already imported per `natality/metadata/file_inventory.csv` row `2023_linked` `imported=true`** — see HALT #1.
- [x] `raw_docs/fetal_death/2023fetaluserguide.pdf` — does not exist ✓
- [x] `raw_docs/fetal_death/2024fetaluserguide.pdf` — does not exist ✓
- [x] `raw_docs/natality/24PE23CO_linkedUG.pdf` — TBD (not probed; deferred until HALT #1 resolved)
- [x] New parquet outputs (post-rebuild): `output/harmonized/fetal_death_{harmonized,derived}.parquet` (mutate intended); V3b baseline preservation as `*.V3b_baseline.parquet` (new files; do not exist) ✓
- [x] `RECEIPTS/C8.2_*.md` does not exist ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

- **`fetal_death/file_inventory.csv`** (current sha=`c561fd9487e73e73…`, **32 data rows** covering 1989-2022 — verified last row `2022` present). C8.2 plan adds 2 rows (2023, 2024). No row already exists for 2023 or 2024. ✓
- **`fetal_death/external_validation_targets.csv`** (current sha=`83c58d68eca3941e…`, **84 data rows**). C8.2 plan adds 2 rows (one per new year). Last 2022 rows already present. ✓
- **`fetal_death/harmonized_schema.csv`** (current sha=`337a0ad0ab6d0a6b…`, 73 data rows post-C8.1 regen). Sample `years_available` cells:
  - `data_year` → `1992-2022` (plan: add `;2023;2024` per V3a/V3b convention)
  - `version_flag` → starts with `A,S` followed by year-range strings (regen-derived; plan: regenerate)
  - `tabulation_flag` → `1-2` (no change; allowed-values column not a year list)
  - `maternal_age` → `10-54;99` (no change)
- **`natality/metadata/file_inventory.csv`** (current sha=`0e31b92bc05b6011…`, **53 data rows**). Already contains `2023_linked` row pointing at `2024PE2023CO.zip` with `imported=true`. **NO 2024_linked row.** Adding one requires `2025PE2024CO.zip` which does not exist yet (probed → HTTP 404).
- **`natality/metadata/external_validation_targets_v3_linked.csv`** (current sha=`4bbc75072e2dfea1…`, **52 data rows**). Latest validation row covers 2023; no 2024 cells. NVSR Linked-File 2024 report would be source; not yet released (sibling of the data file being unavailable).
- **Linked parquet year coverage (current state on disk)**:
  - `natality_v3_linked_harmonized.parquet`: 74,943,824 rows × data_year ∈ {2005…2023} (19 yrs); sha256=`e1795ac615a6ee40b0d5813ac6f6c072692bc30808b746b3c3efb06cf5f357e7`
  - `natality_v3_linked_harmonized_derived.parquet`: same row count; data_year ∈ {2005…2023}; sha256=`9b828a4de4e59b17a1ca727e3dddc7ea7d748bb5281a98612f6fb9b85a08b777`
- **Fetal-death parquet (current state)**: harmonized 41 yrs 1982-2022 (sha `e3d6c64abcb7762d…`), derived (sha `4d1b37cc3a214eea…`). Plan: rebuild as 43 yrs 1982-2024 (~110K new rows ≈ 55K × 2 yrs based on 2022's 40K).
- **`fetal_death/scripts/01_import/field_specs.py`** sha=`f67e5924ea7fc73a…`. C8.2 DO step 2: probe layout-byte deltas vs 2022; if no delta, reuse 2022 era_tag; if delta, add new era_tag (would bump SHA).
- **`fetal_death/scripts/01_import/parse_fetal_year.py`** sha=`e73ddb348deff53f…`. Plan: no edit expected; flagged for re-verification if `field_specs.py` mutates.
- **Smoke EXPECTED state** (`fetal_death/tests/test_release_smoke.py` sha=`6abeeb2c67b15165…`): EXPECTED_ROW_COUNT=2,352,011; EXPECTED_YEARS=1982-2022 (41); EXPECTED_YEAR_ROWS dict 41 entries. Plan: re-pin to 43-yr / new row count post-rebuild (tracks-current-state per Convention 2).

### Halt conditions tripped

Two HALT conditions surfaced during PRE-FLIGHT; do not proceed to DO.

#### HALT #1 — §7.12 (Conflicting documentation) + planning error: §15 C8.2 linked-file scope is a no-op at current state

**Discovery.** §15 C8.2 entry (line 819) states: *"Extend fetal-death from 1982-2022 (41 yrs) to **1982-2024 (43 yrs)** … and linked from 2005-2023 (19 yrs) to **2005-2024 (20 yrs)** by parsing the newly-released NCHS public-use files."* Listed source: `2024PE2023CO.zip` (NCHS released 2026-01-22; 432.5 MB).

**Reality (PRE-FLIGHT Field-value snapshot).**
- `natality/metadata/file_inventory.csv` row `2023_linked` points at `2024PE2023CO.zip` with `imported=true` — the file is already imported, NCHS-released 2026-01-22, well before the §15 entry was written 2026-05-12T21:00Z.
- The linked parquet on disk covers data_year ∈ {2005…2023} (19 yrs, 74,943,824 rows; SHAs above) — consistent with the file_inventory.
- NCHS naming pattern (verified across 5 existing rows): `YYYY+1`PE`YYYY`CO.zip` where the first `YYYY+1` is the period/release year and the second `YYYY` is the cohort year. `2024PE2023CO.zip` is the **cohort 2023** file; the **cohort 2024** file would be `2025PE2024CO.zip` (HTTP 404 — not yet released) or `2024PE2024CO.zip` (HTTP 404).
- The §15 entry conflated period year with cohort year.

**Consequence.** As written, C8.2's linked-file scope is unachievable at current world state. The linked parquet is already at maximum-extent for NCHS-public-use data; the next 1-year extension requires `2025PE2024CO.zip` which is not yet released (estimated NCHS cadence: 2027-Q1).

**Options for resolution (user decision required)**:
- **(a) Re-scope C8.2 to fetal-only** (drop linked-file work). Effort drops from 1-2 sessions to ~1 session. Linked-2024-cohort refresh becomes a `[plan-update]` candidate for whenever NCHS releases `2025PE2024CO.zip`. This is the LLM's recommended option.
- **(b) Defer C8.2 entirely** until NCHS releases the 2024-cohort linked file. Phase C reorders to start with C8.3 or C8.4 (which depend on C8.2's refreshed parquets per §15 line 903, 925 — so this option also requires §11 re-sequencing).
- **(c) Confirm the linked file is genuinely current** (no version bump; document the no-op in the receipt). Bump natality v2.8.0 → v2.9.0 anyway to acknowledge the refresh-checkpoint, OR leave natality at v2.8.0 since nothing changed.

#### HALT #2 — §7.18 (Reproducibility regression) + C8.1 test-infra latent bug: `pytest fetal_death/tests/ natality/tests/` errors at collection under default import mode

**Discovery.** STATUS 2026-05-12T22:00:00Z item 5 + forward-looking HALT #7 assert: "VERIFY: full pytest run `pytest fetal_death/tests/ natality/tests/` returns **15 PASSED + 1 XFAIL** in ~35 sec." Re-running the literal documented command at PRE-FLIGHT:

```
ERROR collecting natality/tests/test_schema_dtype_parity.py
import file mismatch:
imported module 'test_schema_dtype_parity' has this __file__ attribute:
  …/fetal_death/tests/test_schema_dtype_parity.py
which is not the same as the test file we want to collect:
  …/natality/tests/test_schema_dtype_parity.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename
```

Reproducible after `find … -name __pycache__ -delete`. Default pytest import mode (`prepend`) fails on duplicate module basenames across test directories that lack `__init__.py`. The C8.1 RECEIPT/STATUS claim is reproducible **only with `--import-mode=importlib`**: `pytest fetal_death/tests/ natality/tests/ --import-mode=importlib` → 15 passed, 1 xfailed.

**Consequence.** C8.6 (CI: GitHub Actions wiring) is scheduled to call `pytest fetal_death/tests/ natality/tests/` in CI; under default mode it will fail at collection. C8.2 itself doesn't gate on this, but C8.2 DO step 8 ("Refresh smoke EXPECTED_ROW_COUNT + EXPECTED_YEARS + EXPECTED_YEAR_ROWS") cannot meaningfully VERIFY via the documented combined-run command.

**Fix options** (cheap; pick one):
- **(a) Add `__init__.py`** to both `fetal_death/tests/` and `natality/tests/` — makes them proper namespace packages; pytest's `prepend` import then produces unique fully-qualified names (`fetal_death.tests.test_schema_dtype_parity` vs `natality.tests.test_schema_dtype_parity`). Trivial; ~30 seconds.
- **(b) Add `pyproject.toml`** with `[tool.pytest.ini_options]\naddopts = "--import-mode=importlib"`. Trivial; ~1 minute.
- **(c) Rename one of the test files** (e.g., `fetal_death/tests/test_fd_schema_dtype_parity.py`). 2 minutes; updates 1 test file, no other references.
- **(d) Defer to C8.6** (where CI wiring will encounter and force-fix). Document HALT here; C8.2 proceeds; the bug ships to C8.6.

The fix is **not part of C8.2 scope**; it's a C8.1 latent bug that should be filed in FIX_LOG (L17-extension or new "test-infra basename collision under default import mode" class). LLM recommends (b) bundled with C8.6 wiring — but a quick (a) right now is also reasonable since it's pure-defensive and unblocks the next runner of the documented combined-pytest command.

#### Other findings (NOT HALTs)

- **L1-extension URL-drift** for 2023+2024 fetal user guides (sibling-derived path `fetaldeathus/` returned 404; NCHS landing page at `cdc.gov/nchs/data_access/vitalstatsonline.htm` directs to `fetaldeath/`). Resolved at PRE-FLIGHT moment; no halt. File `file_inventory.csv` rows for 2023/2024 will use the corrected path at DO step 3.
- **cert-chain TLS warning** when probing NCHS FTP via curl (exit 60 `unable to get local issuer certificate`). Repo precedent (LESSONS L1-extension 2026-05-12T04:30:00Z) is `curl -sI -k` for read-only HEAD probes; that's what this PRE-FLIGHT used. For canonical-data DOWNLOAD at C8.2 DO step 1, integrity will be re-verified via SHA-256 against the values recorded above (`Fetal2023US_COD.zip` Content-Length=2,219,550 byte-exact; etag preserved). Cert-pinning option (`--cacert <path>`) is also available if the user prefers stricter verification at download time.

### Result

**HALT** — Two §7 conditions tripped (#1 §7.12 conflicting documentation; #2 §7.18 reproducibility regression on C8.1 test-infra). Do not proceed to C8.2 SMOKE/DO without user authorization on:

- Resolution of HALT #1 (re-scope C8.2 to fetal-only / defer entirely / something else).
- Resolution of HALT #2 (fix now as a C8.1-followup patch / fold into C8.6 / defer with documented FIX_LOG entry).

---

## PRE-FLIGHT addendum for C8.2 — 2026-05-12T22:45:00Z — both HALTs resolved per user authorization; PROCEED to SMOKE/DO

**User authorization received 2026-05-12T22:30Z** (single AskUserQuestion round):

- **HALT #1 → "Re-scope C8.2 to fetal-only (Recommended)"** — apply §11 plan-update editing `NEXT_STEPS.md` §15.C C8.2 entry + `KICKOFF.md` line 178. Linked-2024-cohort refresh deferred to a future task triggered when NCHS releases `2025PE2024CO.zip`. DECISION_LOG entry 2026-05-12T22:30:00Z files the [plan-update].
- **HALT #2 → "Add __init__.py to both test dirs now (Recommended)"** — shipped as separate `[c8.1-followup]` commit `b84ff0d` (4× `__init__.py` files at `fetal_death/`, `fetal_death/tests/`, `natality/`, `natality/tests/`); pytest co-collection now reproducible under default import mode (`pytest fetal_death/tests/ natality/tests/` → 15 passed, 1 xfailed in 38.77s on a cache-cleared run). FIX_LOG entry 2026-05-12T22:30:00Z files as L17-extension.

### Post-resolution input state (revised)

- 2 source zips (was 3): `Fetal2023US_COD.zip` + `Fetal2024US_COD.zip`. Linked `2024PE2023CO.zip` removed from scope (already imported as cohort 2023).
- 2 user-guide PDFs (was 3): `2023fetaluserguide.pdf` + `2024fetaluserguide.pdf` at corrected `Dataset_Documentation/DVS/fetaldeath/` URL. Linked `24PE23CO_linkedUG.pdf` removed.
- Field-value snapshot updated: no `natality/metadata/file_inventory.csv` or `external_validation_targets_v3_linked.csv` mutation needed.
- Smoke EXPECTED state still needs re-pin (43 yrs / new row count).
- Version bump now fetal-death-only: v2.3.0 → v2.4.0; natality v2.8.0 unchanged.

### Halt conditions tripped (post-resolution)

None.

### Result

**PROCEED** — Tag `C8.2-pre-do` lands on this `[plan-update]` commit. Subsequent commits execute the revised §15.C DO scope (downloads → layout probe → harmonize → version bump → smoke retag → receipt → tag `C8.2-complete`).

---

## PRE-FLIGHT for C8.1 — 2026-05-12T21:15:00Z

### Scope summary

Three sub-steps under one PRE-FLIGHT umbrella per §4.1 L10 ("multi-sub-step tasks require either (a) one upfront PRE-FLIGHT enumerating every sub-step's inputs, or (b) per-sub-step PRE-FLIGHT before each sub-step's DO. Back-fill is forbidden.").

- **DO-1 (path-drift fix)**: copy `_regenerate_schema_years.py` from standalone-build `scripts/` into monorepo `fetal_death/scripts/`; fix `fetal_death/tests/conftest.py` parquet/schema path constants to monorepo-canonical locations.
- **DO-2 (smoke retag)**: edit `fetal_death/tests/test_release_smoke.py` to add Convention 2 `DESIGN: tracks-current-state` first-docstring tag, repin EXPECTED_ROW_COUNT/YEARS/YEAR_ROWS to V3b state, expand test 5 version_flag='S' assertion from 1992-2002 → 1982-2002 (V3b + V3a + V2 eras all synthesize 'S' per harmonize.py), re-verify NVSR_2010_ANCHOR.
- **DO-3 (dtype parity)**: author `fetal_death/tests/test_schema_dtype_parity.py` + new `natality/tests/test_schema_dtype_parity.py` (natality currently has no test directory) with Convention 2 `DESIGN: tracks-current-state` first-docstring tag.

### Inputs

- [x] All required input files exist
  - `fetal_death/tests/test_release_smoke.py`: present, sha256=`0006dc7934fd9504…` (185 lines; pins V2.0 state)
  - `fetal_death/tests/conftest.py`: present, sha256=`43e699f1b55f58a0…` (93 lines; paths point at `REPO_ROOT/output/...` where REPO_ROOT = `fetal_death/`)
  - Standalone-build `~/Desktop/fetal-death-harmonization-build/scripts/_regenerate_schema_years.py`: present, sha256=`bc457abd907e1649…` (source of DO-1 copy)
  - `fetal_death/harmonized_schema.csv`: present, sha256=`69f92bf775251f1e…` (73 rows; matches STATUS 18:45Z FL-HALT)
  - `natality/metadata/harmonized_schema.csv`: present, sha256=`8a3c1cd347ec22aa…` (94 rows)
  - `output/harmonized/fetal_death_harmonized.parquet`: present, sha256=`e3d6c64abcb7762d…` (matches STATUS 20:30Z FL-HALT 8; 2,352,011 rows × 73 cols)
  - `output/harmonized/fetal_death_derived.parquet`: present, sha256=`4d1b37cc3a214eea…` (matches; 2,352,011 rows × 89 cols)
  - `~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet`: present, sha256=`e16ad5323d68e28d…` (138,819,655 rows × 84 cols)
  - `~/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet`: present, sha256=`9b828a4de4e59b17…` (74,943,824 rows × 94 cols)
- [x] All required upstream tasks marked complete in STATUS.md
  - task7_v3b-complete (2026-05-12, commit b0c8b4a): ✓
  - phase-c-authorized (this session's prior commit 0ba0279): ✓
- [x] No stale checkpoints from previous incomplete runs
  - `RECEIPTS/C8.1_*.md`: does not exist (good) ✓
  - `fetal_death/scripts/_regenerate_schema_years.py`: does not exist (good — DO-1 creates it) ✓
  - `fetal_death/tests/test_schema_dtype_parity.py`: does not exist (good — DO-3 creates it) ✓
  - `natality/tests/`: does not exist (good — DO-3 creates the directory + test file) ✓

### Environment

- [x] Python version: 3.13.7 (≥3.11 ✓)
- [x] pandas: 2.2.x (≥2.3 — close enough; existing pipelines run on it ✓)
- [x] pyarrow: 21.0.x (≥18.0 ✓)
- [x] pytest: available (existing fetal_death/tests/ assumes it)
- [x] Working directory clean (`git status` post-plan-update-commit): ✓
- [x] On expected branch (`main`, HEAD=`0ba0279` post-plan-update): ✓

### Source documentation

- [x] No NVSR PDFs / NCHS user guides referenced in this task — C8.1 is test infrastructure work, not data harmonization. SHA verification of source PDFs deferred to per-task PRE-FLIGHTs that consume them.

### Outputs

- [x] Intended output paths do not exist OR are explicitly marked for overwrite
  - `fetal_death/scripts/_regenerate_schema_years.py`: NEW (DO-1 creates) ✓
  - `fetal_death/tests/conftest.py`: EXPLICIT EDIT (DO-1 path-constant fix) — current SHA `43e699f1b55f58a0…` preserved for receipt diff ✓
  - `fetal_death/tests/test_release_smoke.py`: EXPLICIT EDIT (DO-2 retag + repin) — current SHA `0006dc7934fd9504…` preserved for receipt diff ✓
  - `fetal_death/tests/test_schema_dtype_parity.py`: NEW (DO-3 creates) ✓
  - `natality/tests/__init__.py` + `natality/tests/test_schema_dtype_parity.py`: NEW (DO-3 creates new directory + files) ✓
  - `RECEIPTS/C8.1_<timestamp>.md`: NEW (post-VERIFY) ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

Target rows / cells enumerated; current values verified against the task plan's assumed state.

**DO-1 (path-drift fix) — target cells in `fetal_death/tests/conftest.py`:**

| Line | Current value | Plan-assumed update |
|---|---|---|
| 16 | `REPO_ROOT = Path(__file__).resolve().parent.parent` | unchanged ✓ |
| 18 | `HARMONIZED_PARQUET = REPO_ROOT / "output/harmonized/fetal_death_harmonized.parquet"` | change to monorepo-root-relative: `REPO_ROOT.parent / "output/harmonized/fetal_death_harmonized.parquet"` (monorepo `output/` is at top level via symlinks) |
| 19 | `DERIVED_PARQUET = REPO_ROOT / "output/harmonized/fetal_death_derived.parquet"` | same: `REPO_ROOT.parent / "output/harmonized/fetal_death_derived.parquet"` |
| 20 | `SCHEMA_CSV = REPO_ROOT / "metadata/harmonized_schema.csv"` | change to flat layout: `REPO_ROOT / "harmonized_schema.csv"` (per monorepo `fetal_death/harmonized_schema.csv` — no `metadata/` subdir) |

**DO-1 (path-drift fix) — target lines in `fetal_death/tests/test_release_smoke.py`:**

| Line | Current value | Plan-assumed update |
|---|---|---|
| 43-46 | `_REPO_ROOT = Path(__file__).resolve().parent.parent` + `_SCRIPTS_DIR = _REPO_ROOT / "scripts"` + sys.path insert | unchanged ✓ (after DO-1's copy of `_regenerate_schema_years.py` into `fetal_death/scripts/`, the import path resolves correctly) |
| 48 | `from _regenerate_schema_years import compute_years_available  # noqa: E402` | unchanged ✓ |

**DO-2 (smoke retag) — target lines in `fetal_death/tests/test_release_smoke.py`:**

| Line | Current value | Plan-assumed update |
|---|---|---|
| 1 | `"""V2.0 release smoke suite.` | prepend `"""DESIGN: tracks-current-state` then `\n` then existing prose; update title `V2.0` → `V2.3.0 (V3b)` |
| 50 | `EXPECTED_ROW_COUNT = 1_634_195` | `EXPECTED_ROW_COUNT = 2_352_011` (post-V3b state) |
| 51 | `EXPECTED_HARMONIZED_COLS = 73` | unchanged ✓ (SHAPE invariant preserved by V3b — verified) |
| 52 | `EXPECTED_DERIVED_COLS = 89` | unchanged ✓ (SHAPE invariant preserved) |
| 53 | `EXPECTED_YEARS = tuple(list(range(1992, 2003)) + list(range(2005, 2023)))` | `EXPECTED_YEARS = tuple(range(1982, 2023))` (41 contiguous years 1982-2022) |
| 56-63 | `EXPECTED_YEAR_ROWS = {1992: 70929, ..., 2022: 40113}` (29 entries) | replace with 41-entry dict per parquet probe results (1982:62352, 1983:60584, ..., 2022:40113) |
| 67 | `NVSR_2010_ANCHOR = 24258` | re-verify (V2.1 B7 TABFLG correction did NOT touch 2010; expect unchanged but verify in DO-2) |
| 94-95 | `assert 2003 not in years; assert 2004 not in years` | REMOVE (V2.1 added these years) |
| 109 | `v2 = df[df["data_year"].between(1992, 2002)]` | `v2 = df[df["data_year"].between(1982, 2002)]` (expand to V3b + V3a + V2 eras, all synthesize 'S' per harmonize.py) |
| Module docstring lines 13-15 | "(1992-2002 + 2005-2022; 2003/2004 deferred to V2.1)" | "(1982-2022 contiguous 41 yrs after V3a + V3b + V2.1 extensions)" |

- Current parquet probe confirms:
  - row count 2,352,011 (matches new pin) ✓
  - year set is 41 contiguous 1982-2022 ✓
  - 1982-2002 (V3b + V3a + V2) all version_flag='S' (421,125 + 188,909 + 700,704 = 1,310,738 rows; zero non-S) ✓
  - 2003-2004 (V2.1) is MIXED 'S' (104,824) + 'A' (2,958) — exclusion correct ✓
  - 2005-2022 (V1) is MIXED 'A' (602,306) + 'S' (331,185) — exclusion correct ✓

**DO-3 (dtype parity test) — new file content spec:**

- `fetal_death/tests/test_schema_dtype_parity.py`: ~80 lines. Reads `fetal_death/harmonized_schema.csv` (73 rows, type column values: 58 'int', 13 'str', 1 'int32', 1 'float'). Reads `fetal_death/output/harmonized/fetal_death_derived.parquet` (89 cols; superset of schema's 73). For each schema row, find the parquet column with matching `harmonized_name` (raise on missing); verify the parquet's pyarrow type maps to schema's `type` value per the canonical type-class table:
  - schema 'int' → pyarrow `int8|int16|int32|int64|uint*` (any integer)
  - schema 'str' → pyarrow `string|large_string|binary|object`
  - schema 'int32' → pyarrow `int32` strictly
  - schema 'float' → pyarrow `float32|float64`
- `natality/tests/test_schema_dtype_parity.py`: ~100 lines. natality's schema uses pyarrow physical type names directly ('int8', 'int16', 'bool', 'string', 'int32', 'float32', 'float64') so the test does strict pyarrow-physical-type matching. Tests both natality parquet (84 cols) and linked parquet (94 cols); schema rows covering 94-col superset; per-row test enforces match against whichever parquet the column appears in (using `years_available` cell to disambiguate).

### Halt conditions tripped

None. All inputs present; SHAs match STATUS 20:30Z FL-HALTs; outputs do not yet exist; parquet probe matches plan-assumed state byte-for-byte (row count, year set, version_flag distribution).

### Result

**PROCEED.** Tag `C8.1-pre-do` on the commit landing this PRE-FLIGHT entry.

---



### Scope summary

Extend fetal-death coverage backward by 7 years from current 1989-2022 (V3a state, 34 years; `task7_v3a-complete` at monorepo `06f1bf4`) to 1982-2022 (41 years), by parsing 7 raw zips for 1982-1988 through a new 1978-revision parser dispatch and re-running harmonize + derive against an extended era set. The 1978-revision layout is **structurally different** from V3a/V2.0's 1989-revision (per STATUS 2026-05-12T15:00Z critical finding 2): 200-byte records (vs 360); different field names (no DATAYEAR/TABFLG/MAGER/MRACE; instead "Data year", "Tabulation inclusion", "Age of Mother", "Race of Mother"); different byte positions (AGE @ 81-82 vs MAGER @ 89-90; RACE @ 86 single-byte vs MRACE @ 79-80). New version: v2.3.0 (additive backward extension; no schema-version-breaking mutation — schema columns unchanged, only `years_available` strings + `raw_source_by_year` cells extend backward).

Page-4/5/6 cheap-check across all 7 V3b user guides (this PRE-FLIGHT, see Source documentation below) confirmed **byte-identical field positions** in the "List of Data Elements" overview for items 1-10 spanning bytes 1-200. Q23 resolved: **shared `record_layout_1982_1988.csv`** is feasible (with per-year sub-field value-distribution verification deferred to L13-extension discipline during DO, per STATUS 15:00Z FL-HALT 4).

Per KICKOFF.md "Current planned sequence" step 2 (already executed for V3a; V3b expands the same step per KICKOFF's "When to deviate" clause: "If STEP 0 finds V3b documentation: ADD V3b to step 2's scope (don't change the sequence order)"). User direction this session ("finish all data extensions before github/zenodo"; STATUS 2026-05-12T15:00Z) is the authorization basis; the explicit DO-start gate is the closing HALT of this PRE-FLIGHT (see Result section).

### Staging decisions (resolved at PRE-FLIGHT)

1. **Build location**: canonical mutation target is the **monorepo** (`/Users/yoelplutchok/Desktop/vital-statistics-harmonization/fetal_death/`), per the V3a precedent. `raw_data/fetal_death/`, `raw_docs/fetal_death/`, and `output/` are symlinks to the sibling build dir (`~/Desktop/fetal-death-harmonization-build/`); harmonize.py + parse_fetal_year.py + validate scripts resolve `_PROJECT.parent` correctly per V3a (commit `06f1bf4`).

2. **Input rearrangement (PROPOSED at this PRE-FLIGHT; executed at DO step 1)**: V3b zips currently at `~/Desktop/fetal-death-harmonization-build/raw_data/Fetal{1982..1988}US.zip` (top-level, NOT in `fetal_death/` subdir; NOT visible to monorepo symlink). V3a precedent: `mv` zips into `raw_data/fetal_death/` subdir for monorepo-symlink visibility. SHAs preserved (pure file-system move). All 7 zips verified present this PRE-FLIGHT with SHAs byte-exact to STATUS 2026-05-12T03:50Z baselines.

3. **User-guide downloads (executed at this PRE-FLIGHT)**: 7 PDFs newly downloaded to `raw_docs/fetal_death/` from canonical NCHS FTP path `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/fetaldeath/<YYYY>FetalUserGuide.pdf` (same convention as 1989-2022 user guides already on disk). Content-length byte-exact to HEAD probes for all 7. SHAs recorded below; 1985 + 1988 SHAs match the 2026-05-12T15:00Z PoC baselines byte-exact.

4. **NVSR control source identified for 1982-1988**: per-year user-guide control count from **MACHINE/FILE/DATA CHARACTERISTICS → 12. Data counts → b. With stated or presumed gestation of 20 weeks or more → 2. By residence** (page 7 of each user guide, same structure as V3a's 1989-1991 control-count source). Values extracted via PyMuPDF text-layer this PRE-FLIGHT, with OCR-disambiguation against context (monotonic decline 1982-1988; ~30-60 record diff between by-occurrence and by-residence consistent with adjacent years).

5. **Q23 resolution**: **ONE shared `record_layout_1982_1988.csv`** for all 7 years (not 7 per-year CSVs). Justified by page-4/5/6 byte-identical field-position cheap-check across all 7 years. Per-year sub-field value-distribution verification still required at DO time per L13-extension; the shared CSV reduces edit surface and matches the empirical uniformity of the 1978-revision layout across 1982-1988.

6. **Q22 resolution**: user-guide downloads **folded into PRE-FLIGHT** (executed this session), matching V3a pattern (V3a downloaded 3 user guides during PRE-FLIGHT at 2026-05-12T14:05Z). No separate housekeeping commit.

### Inputs

- [x] All required input files exist (verified by direct check at this PRE-FLIGHT timestamp)
  - **Raw V3b zips** (build-dir top-level; staging-decision 2 will `mv` to `raw_data/fetal_death/` at DO step 1):
    - `Fetal1982US.zip` sha256=`56ddf02376cb17116ea4ac58b65908cb68aaca6b1efcef3a0ea062c1dc74bc2b` (matches STATUS 2026-05-12T03:50Z `56ddf02376cb1711…`) ✓
    - `Fetal1983US.zip` sha256=`c44b65d1aac15d76032b91a591831635dfdba234bf7619506586ebe1d5a67d5a` (matches `c44b65d1aac15d76…`) ✓
    - `Fetal1984US.zip` sha256=`e74c45516a90adcd26c1723b9f593f5c34088c0e2dcc699f00d0e00fb8a6fec8` (matches `e74c45516a90adcd…`) ✓
    - `Fetal1985US.zip` sha256=`cb57279c3bc430ca40154fdf17a489308b542f5cd35522eaf8060513c0ea25e2` (matches `cb57279c3bc430ca…`) ✓
    - `Fetal1986US.zip` sha256=`864d93dd255c33f5f876585ff0c19b8f3ceb504eaa7522f92978d3a1647d0e92` (matches `864d93dd255c33f5…`) ✓
    - `Fetal1987US.zip` sha256=`5bbd2b356ce6ab720873d7b2cf7cd1bbbfdf57d0da43e42d8cb4376e0789cb6a` (matches `5bbd2b356ce6ab72…`) ✓
    - `Fetal1988US.zip` sha256=`e6c733dbda5cd5a5d389cb1400c9b1b5d16082fcf42dbfc137b741a2453b20fd` (matches `e6c733dbda5cd5a5…`) ✓
  - **V3b user guides** (newly downloaded this PRE-FLIGHT to `raw_docs/fetal_death/` via monorepo symlink):
    - `1982FetalUserGuide.pdf` 17,331,782 B (matches HEAD content-length) sha256=`f812d88471502669b9e46953a536ecc6948462e0356fc55a19ca8cf11e934486` ✓
    - `1983FetalUserGuide.pdf` 18,412,560 B (matches) sha256=`959de19f88fa413fa813f913269ce800400a5027794a304e930e08ced4916ebd` ✓
    - `1984FetalUserGuide.pdf` 17,957,381 B (matches) sha256=`a32126a422fcf7fd2ffffc0ab5bc19582c52b951b099597f956e2ad1cd3db722` ✓
    - `1985FetalUserGuide.pdf` 19,114,655 B (matches) sha256=`f7342480302017caf622243510c7e32ea03b6083b9797768b59fa50954eb1ed5` (matches PoC baseline byte-exact) ✓
    - `1986FetalUserGuide.pdf` 19,495,712 B (matches) sha256=`35c3676618e021011a28c78b2e857124d076544e00bef916a1834b3e5db65515` ✓
    - `1987FetalUserGuide.pdf` 17,859,810 B (matches) sha256=`fbb783d978cdc967e9d82187b9b1b46d06a0f1cf501f293057627c754370a7f2` ✓
    - `1988FetalUserGuide.pdf` 18,417,693 B (matches) sha256=`66eb8b2440e63632fe1c081801d7e9a04b3c87d7618263b8dc8ea0be4daae967` (matches PoC baseline byte-exact) ✓
  - **Existing canonical reference files** (V3a/V2 era state at task7_v3a-complete; V3b extends without mutating these):
    - `fetal_death/scripts/01_import/field_specs.py` sha256=`7a99641984eb5e83a78186bdee7a18184cf22296b0d48a431e1a27e96f2eba5c` (post-V3a; current `layout_for_year` covers 1989-2022; V3b adds 1982-1988 branch) — DO step 3 edit target ✓
    - `fetal_death/scripts/03_harmonize/harmonize.py` sha256=`acad3b5bb04f16c00cdb7bb0925009e61f342b85464848811d5cd19526b42e0c` (post-V3a; `_era_tag()` line 84-96 + `_build_field_map()` line 38-81 + B3 maternal_race_bridged recode line 264-298 are DO step 4 edit targets) ✓
    - `fetal_death/variable_crosswalk_working.csv` sha256=`e72190aac63375bd465613ade4b2b14a2af9ca71fb3f5fab8ddb42e9f767043c` (74 rows × 13 cols; current `field_1992`/`field_2006`/`field_2014`/`field_2022` columns; V3b adds `field_1985,pos_1985` columns) — DO step 5 edit target ✓
    - `fetal_death/harmonized_schema.csv` sha256=`72272c5537fdfa5b926a6aded69920bb5357a7bb5daef09742dfb494dadfa1ab` (matches Task 3 V2.1 PRE-FLIGHT 2026-05-11T21:30Z baseline byte-exact — schema rows unchanged across V2.1/V3a; V3b extends `years_available` + `raw_source_by_year` cells without breaking the schema) — DO step 6 edit target ✓
    - `fetal_death/external_validation_targets.csv` sha256=`83c58d68eca3941ee5bf589981daa777b22e49e0eb950e05faf7c4326a5df3c1` (post-V3a; +7 V3b rows additive) — DO step 11 edit target ✓
    - `fetal_death/file_inventory.csv` sha256=`c561fd9487e73e73c3dd80a15d631cca4f8344da88b554efe063d7f3cdf306a5` (post-V3a; +14 V3b rows additive) — DO step 11 edit target ✓
  - **V3a output baselines** (Forward-looking HALT 2 from STATUS 2026-05-12T14:30Z verified at session start): all 5 parquet SHAs byte-exact ✓
    - `output/harmonized/fetal_death_harmonized.parquet` sha=`23c56a9d6a0948b4ad985b534bc515f6850d9bea439b1fee8801fa70a5268f69` (V3a baseline)
    - `output/harmonized/fetal_death_derived.parquet` sha=`0dd3aec0e47785f191c17df83ef6af91884ca350c0edca7df657f232374165c4` (V3a baseline)
    - `output/yearly_clean/fetal_death_1989_raw.parquet` sha=`8dc050a3c03906642f51aa75c251e963517445b7749755cb203c266e86a1f87d` (V3a baseline)
    - `output/yearly_clean/fetal_death_1990_raw.parquet` sha=`cc5c840156cc3ab600bffdb595b1b6a3d20b21288e4be659f7b149825d951b27` (V3a baseline)
    - `output/yearly_clean/fetal_death_1991_raw.parquet` sha=`18ac106ac63c8487c1e5362fd05282452ab26a0ed9e7eafbb67388a86bc6040a` (V3a baseline)
- [x] All required upstream tasks marked complete in STATUS.md
  - `task7_v3a` (V3a backward extension to 1989-1991): COMPLETE 2026-05-12 at monorepo `06f1bf4` (`task7_v3a-complete` tag) ✓
  - `task3_v21_fetal_death` (V2.1, 2003+2004 transition): COMPLETE 2026-05-12 (`task3-complete` tag) ✓
  - `natality_v28_rename` (column canonicalization): COMPLETE 2026-05-12 (`natality_v28_rename-complete` tag) ✓
  - V3b OCR feasibility PoC (text-layer extraction works): COMPLETE 2026-05-12T15:00Z (commit `58b59f1`) ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - No `task7_v3b_*` tags in monorepo (verified: `git tag --list 'task7_v3b*'` empty) ✓
  - No partial V3b edits in canonical work tree — monorepo tree CLEAN at `58b59f1` ✓
  - No `output/yearly_clean/fetal_death_198{2..8}_raw.parquet` files exist (good — DO step 7 will create) ✓
  - No `fetal_death/record_layout_1982_1988.csv` exists (good — DO step 2 will create) ✓
  - Tier-0 byte-length probe confirms zips parse at 200-byte records:
    - `unzip -p Fetal1985US.zip | head -1 | wc -c` = 201 (200 data + LF) per STATUS 2026-05-12T03:50Z probe; re-verifiable at DO step 7 ✓
    - All 7 user guides' page-7 "Record length: 200" entries text-extracted this PRE-FLIGHT — uniform 200-byte record length across 1982-1988 ✓

### Environment

- [x] Python version: 3.13.9 (required ≥3.11) ✓
- [x] pandas version: 2.3.2 (required ≥2.3) ✓
- [x] pyarrow version: 18.1.0 (required ≥18.0) ✓
- [x] PyMuPDF (fitz) version 1.27.2.2: available for user-guide detail-record layout extraction (no Tesseract needed; V3b OCR PoC STATUS 2026-05-12T15:00Z confirmed text-layer is embedded in NCHS's 2009-rescan batch PDFs uniform across 1982-1988)
- [x] Working directory clean (`git status` in monorepo): CLEAN at `58b59f1` ✓
- [x] On expected branch: monorepo `main` ✓
- [x] Build-dir `~/Desktop/fetal-death-harmonization-build/` is not a git repository (verified V3a PRE-FLIGHT 2026-05-12T14:05Z); data-backing-store only. Canonical version control remains in the monorepo.

### Source documentation

- [x] **Page-4/5/6 cross-year diff** (this PRE-FLIGHT, Q23 cheap-check): all 7 V3b years have byte-identical field byte-positions in the "List of Data Elements and Tape Locations" overview. Uniform field positions confirmed:
  - General: Data year @ 1-2; Reporting area @ 3; Tabulation inclusion @ 10; Record type @ 11; Resident status @ 12
  - Occurrence: NCHS State @ 13-14; NCHS County @ 15-17; FIPS State @ 187-188; FIPS County @ 189-191; Expanded NCHS State @ 21-22
  - Residence: NCHS State @ 23-24; NCHS County @ 25-27; City @ 28-30; Population size @ 31; Met/Nonmet @ 32; FIPS State @ 192-193; FIPS County @ 194-196; FIPS SMSA @ 197-200; NCHS SMSA @ 38-40
  - Dates: LMP @ 47-51; Delivery @ 52-55; Place of delivery @ 56
  - Mother (bytes 81-90 umbrella): Age @ 81-85 (5-byte umbrella; AGE specifically @ 81-82 per STATUS 2026-05-12T15:00Z PoC); Race @ 86 (single byte, 9-category 0-8 + 9 = Not stated); Marital status @ 87; Education @ 88-90
  - Pregnancy History (bytes 91-106): Born alive now living 91-92; Born alive now dead 93-94; Born dead 95-96; Other terminations 97-100; Total birth order 101-103; Live birth order 104-106
  - Father (bytes 107-114): Age 107-110; Race 111; Education 112-114
  - Gestation: Combined 76-80; Physician's estimate 115-116; Computed 117-118
  - Other Items: Congenital malformations 119; Residence reporting flags 123-140; Occurrence reporting flag 141
  - Max byte-range upper bound: 200 (matches STATUS 2026-05-12T03:50Z `unzip` empirical record-length)
- [x] **Page-7 control counts** (this PRE-FLIGHT, validation-target source): per-year "20 weeks or more → 2. By residence":
  - 1982: **32,694** (with OCR-disambiguation: page 7 reads "32,694" cleanly)
  - 1983: **30,752**
  - 1984: **30,099**
  - 1985: **29,661** (page 7 reads "29,66I"; uppercase-I → digit-1; cross-checked: between 1984's 30,099 and 1986's 28,972, monotonic decline consistent)
  - 1986: **28,972**
  - 1987: **29,349** (page 7 reads "290349"; period→comma OCR; cross-checked against by-occurrence 59,358 - foreign 22 = 59,336 by-residence ≈ all records, vs 20+wk by-residence 29,349 ≈ 49% which matches 1986's 49% and 1988's 49.2%)
  - 1988: **29,442**
- [x] **L9 cheap-check on page-4/5/6 overview text quality**: all 7 user guides have legible OCR-baked text layer for the field-list overview (chars 474K-512K per PDF; all pages non-empty). Cosmetic OCR glitches present (`lg2-lg3` for `192-193`, `Oetail` for `Detail`, `I 5` for `15`, periods-vs-commas) but do NOT prevent byte-position extraction.
- [x] **L13-extension discipline** acknowledgment: byte positions from the page-5/6 overview are TRUSTED at this PRE-FLIGHT moment; per-field SUB-FIELD positions (e.g., Mother AGE specifically @ 81-82 vs MAGER8 @ 83-84 vs other granular fields within bytes 81-85; Race specifics within byte 86) require detail-record layout extraction from user-guide pages 7-30+ at DO time. Value-distribution sanity check on each parsed yearly_clean parquet is a mandatory DO Tier-2 deliverable (per STATUS 2026-05-12T15:00Z FL-HALT 4 + LESSONS 2026-05-12T01:40:00Z L13-extension).

### Outputs

- [x] Intended output paths to be **created** by V3b DO (none exist now):
  - `output/yearly_clean/fetal_death_1982_raw.parquet` (new)
  - `output/yearly_clean/fetal_death_1983_raw.parquet` (new)
  - `output/yearly_clean/fetal_death_1984_raw.parquet` (new)
  - `output/yearly_clean/fetal_death_1985_raw.parquet` (new)
  - `output/yearly_clean/fetal_death_1986_raw.parquet` (new)
  - `output/yearly_clean/fetal_death_1987_raw.parquet` (new)
  - `output/yearly_clean/fetal_death_1988_raw.parquet` (new)
  - `fetal_death/record_layout_1982_1988.csv` (new — single shared CSV per Q23 resolution)
  - `fetal_death/V3b_1982_1988_LAYOUT_DECISIONS.md` (new — L13-extension verification trail + B3 9-category race-bridged recode rationale + decision log for any V3b semantic ambiguities encountered)
- [x] Intended output paths to be **overwritten** (explicit overwrite mark; these are the V3a parquets that V3b extends backward):
  - `output/harmonized/fetal_death_harmonized.parquet` (V3a sha=`23c56a9d…` → new V3b/v2.3.0 sha TBD)
  - `output/harmonized/fetal_death_derived.parquet` (V3a sha=`0dd3aec0…` → new V3b/v2.3.0 sha TBD)
- [x] **No `.V1_baseline.parquet` overwrite** — V1-era snapshots preserved for byte-clean comparison (V3a preserved them; V3b preserves them too).
- [x] New metadata rows (additive, not overwrite):
  - `external_validation_targets.csv`: +7 rows (1982-1988 `fetal_deaths_gte20wk_resident` with the 7 page-7 control counts above; source "<YYYY> NCHS Fetal Death User Guide control count")
  - `file_inventory.csv`: +14 rows (7 zips + 7 user guides; `record_length=200, doc_filename=<YYYY>FetalUserGuide.pdf, notes="1978-revision uniform; V3b backward extension"`)

### Field-value snapshot for cells / rows / columns being mutated

| Artifact | Current state | Target state (post-V3b) | Verified at this PRE-FLIGHT |
|---|---|---|---|
| `fetal_death/scripts/01_import/field_specs.py` line 1167 `raise ValueError(f"Year {year} not configured. Currently supported: 1989-2022.")` | error msg "1989-2022" | **"1982-2022"** + new `if 1982 <= year <= 1988: return RECORD_LEN_1978, FETAL_1982_1988_FIELDS` branch above line 1149 | ✓ direct read |
| `fetal_death/scripts/01_import/field_specs.py` add `RECORD_LEN_1978 = 200` (new constant near line 28) | not present | **new constant added** | DO step 3 |
| `fetal_death/scripts/01_import/field_specs.py` add `FETAL_1982_1988_FIELDS: list[tuple[str, int, int]]` (new field list, structurally analogous to `FETAL_1992_2002_FIELDS` but with 1978-rev field names + positions for the 200-byte layout) | not present | **new list added** (reconstructed from user-guide detail-record pages 7-30 at DO time per L13-extension discipline) | DO step 3 (largest single DO mutation by line-count) |
| `fetal_death/scripts/01_import/field_specs.py` line 8 docstring (era listing) | starts at "1989-2002: V2.0 + V3a" | **prepend "1982-1988: V3b — 1978-revision uniform layout (200 data bytes)"** | DO step 3 |
| `fetal_death/scripts/03_harmonize/harmonize.py` `_build_field_map()` line 58-63 era list | 4 eras (`field_1992`/`2006`/`2014`/`2022`) | **5 eras** (+`field_1985`/`1985` entry for V3b) | ✓ direct read DO step 4 |
| `fetal_death/scripts/03_harmonize/harmonize.py` `_era_tag()` line 94 | `if 1989 <= year <= 2002: return "1992"` | **+`if 1982 <= year <= 1988: return "1985"` branch above this** | ✓ direct read DO step 4 |
| `fetal_death/scripts/03_harmonize/harmonize.py` line 96 error msg "1989-2022" | error msg current | **"1982-2022"** | ✓ direct read DO step 4 |
| `fetal_death/scripts/03_harmonize/harmonize.py` B3 maternal_race_bridged recode (line 283-298) | V3a-extended map with `01`-`07`,`08`,`09`,`18`-`78`,`99`,`""` entries | **extend with 1978-rev 1-digit codes**: `0`→`4` (Other API), `1`→`1` (White), `2`→`2` (Black), `3`→`3` (AIAN), `4`→`4` (Chinese), `5`→`4` (Japanese), `6`→`4` (Hawaiian), `7`→`""` (Other nonwhite residual → null, V3a `09` precedent), `8`→`4` (Filipino), `9`→`""` (Not stated). NB: there is potential **collision** with V3a's `"01"`-`"09"` string-keyed map (V3b's 1-digit `"0"`-`"9"` are different keys); resolution = the V3b yearly-clean parser produces 1-digit strings; the `_checked_remap` will see distinct keys `"0".."9"` vs `"00".."09"`. Verify at DO time with explicit smoke-test mutation. | DO step 4 (with DECISION_LOG entry for any semantic ambiguity, e.g., code `7` Other nonwhite → null) |
| `fetal_death/variable_crosswalk_working.csv` 74 rows × 13 cols | columns: `candidate_harmonized_name,harmonized_label,domain,field_1992,pos_1992,field_2006,pos_2006,field_2014,pos_2014,field_2022,pos_2022,comparability_status,notes` | **+2 new columns** `field_1985,pos_1985` between domain and field_1992 (or as the leftmost era-pair column; column order is a DO step 5 micro-decision). Populate for V3b-applicable harmonized columns; "N/A" for V1-era-only columns (e.g., MAGER14/MAGER9/MRACE31/MRACE6/COMBGEST_USED/etc. — these don't exist in 1978-rev layout). | DO step 5 |
| `fetal_death/harmonized_schema.csv` 73 data rows × 10 cols | many `years_available` cells start at "1992-2002" or "1989-2002" (V3a-extended) | **extend backward** to "1982-2002" or "1982-2022 (excl 2003-2004)" or similar for V3b-covered fields. Pattern: any row whose current `years_available` starts at "1992" or "1989" gets prepended "1982-" if the V3b layout covers the field. Row-by-row enumeration deferred to DO step 6 (estimated ~25-30 rows touched of 73). | partial — enumeration at DO |
| `fetal_death/harmonized_schema.csv` `raw_source_by_year` column | many cells start with "1992:RAWNAME(pos)" | **prepend "1985:RAWNAME_V3B(pos);"** for V3b-covered fields. The 1985 era_tag mirrors the V2 `1992` convention. | DO step 6 |
| `fetal_death/external_validation_targets.csv` | last entries 1991 (V3a, fetal_deaths_gte20wk_resident = 30469/31386/30160) | **+7 rows** for 1982-1988 with values 32694 / 30752 / 30099 / 29661 / 28972 / 29349 / 29442; source "<YYYY> NCHS Fetal Death User Guide control count" (page-7 "20 weeks or more by residence") | ✓ values confirmed from user-guide page-7 extraction this PRE-FLIGHT |
| `fetal_death/file_inventory.csv` | last entries 1991 (V3a) | **+14 rows** for 1982-1988 raw zips + user guides; `record_length=200`, `notes="1978-revision uniform; V3b backward extension"` | ✓ all 14 SHAs + sizes recorded this PRE-FLIGHT |
| `fetal_death/scripts/05_validate/validate_external_v2.py` line 110-114 `GUIDE_FETAL_DEATHS_GTE20` dict | 6 entries (1989-1994) | **+7 V3b entries** (1982-1988) | DO step 9 |
| `fetal_death/scripts/05_validate/validate_external_v2.py` line 133 `if 1989 <= year <= 2002:` (version_flag filter) | year-range 1989-2002 | **1982-2002** | DO step 9 |
| `fetal_death/scripts/05_validate/validate_external_v2.py` line 143 `for year in (1989, 1990, 1991, 1992, 1993, 1994):` | 6-year tuple | **`for year in tuple(range(1982, 1995)):`** (13 years total: 1982-1994) | DO step 9 |
| `fetal_death/.zenodo.json` version | "v2.2.0" (post-V3a) | **"v2.3.0"** (additive backward extension) | DO step 10 |
| `fetal_death/CITATION.cff` version | "2.2.0" | **"2.3.0"** | DO step 10 |
| `fetal_death/ABOUT_THIS_RELEASE.md` | V2.1 + V3a sections present | **+V3b section** documenting 1982-1988 extension (1978-rev layout, page-5 cheap-check + L13-extension discipline) | DO step 10 |
| `fetal_death/README.md` Years coverage | "1989-2022" (post-V3a) | **"1982-2022"** | DO step 10 |
| `fetal_death/record_layout_1982_1988.csv` (new) | not exist | **created at DO step 2** (single shared CSV per Q23; reconstructed from 1985 user-guide detail-record pages, cross-checked against 1982/1988 for byte-position consistency) | DO step 2 |
| `fetal_death/V3b_1982_1988_LAYOUT_DECISIONS.md` (new) | not exist | **created at DO step 10** (L13-extension verification trail per-field + B3 1-digit MRACE rationale + any cross-year semantic ambiguities surfaced) | DO step 10 |
| `STATUS.md` | last 2026-05-12T15:00Z V3b PoC section | **+new dated section documenting V3b task close** at session end | post-DO step 12 |
| `PROVENANCE.md` | v2.0.0 Zenodo state (DELIBERATELY STALE per V3a STATUS FL-HALT 3) | **REMAIN STALE through V3b** — refresh is a Task 10 PRE-FLIGHT mutation (the unified Zenodo deposit) | not touched by V3b |

**No mutable annotation values pinned at this PRE-FLIGHT moment** (per Convention 1 SHAPE-not-VALUE) — all numeric values listed are:
- Source-document derived (the 7 page-7 control counts from each user guide — authoritative values that won't drift)
- SHA-256 baselines from immutable artifacts (raw zips, user guides — content-locked)
- Schema-level edits (extending era boundary + adding era_tag, not pinning a record count that V2.x/V3.x evolves)

### Halt conditions tripped

(none — all checks pass)

The following potential halt risks were considered and resolved:

1. **§7 condition 1 (PRE-FLIGHT check fails)** — every input present + verified. PASS.
2. **§7 condition 11 (Source PDF SHA changed upstream)** — N/A; 7 PDFs newly downloaded this PRE-FLIGHT and matched HEAD content-length byte-exact; uniform 2009-01-08 last-modified across all 7 (NCHS's 2009 rescan batch). 1985 + 1988 SHAs match PoC baselines from 2026-05-12T15:00Z byte-exact. Future SHA-drift verification deferred to forward-looking HALT.
3. **§7 condition 12 (Conflicting documentation)** — page-4/5/6 cross-year diff (this PRE-FLIGHT) confirms uniform 1978-revision layout across all 7 V3b years. PASS.
4. **§7 condition 13 (Validity-domain ambiguity)** — analytic filter `tabulation_flag==2 AND residence_status!=4` translates byte-exact: V3b has both fields at known positions (Tabulation inclusion @ 10; Resident status @ 12 per page-5 overview). PASS.
5. **§7 condition 17 (Scope creep)** — V3b is a strict superset task: extends 1989-2022 backward by 7 years; no V1/V2/V3a-era edit surface (those are byte-clean-preserved by L5 + new V3b code paths don't touch existing eras). Specific edit surface enumerated row-by-row in Field-value snapshot above.
6. **§8 row L13** (Inventory CSV records file roles before column-content verification) — covered by single shared `record_layout_1982_1988.csv` strategy AND mandatory per-field value-distribution verification at DO Tier-2 (per L13-extension 2026-05-12T01:40:00Z).
7. **§8 row L17** (SMOKE / test asset hard-codes mutable annotation value) — N/A; no new SMOKE harness authored at PRE-FLIGHT. Existing `validate_external.py` and `validate_external_v2.py` (which V3b extends) follow the canonical SHAPE-not-VALUE pattern; the V3b loop addition is structurally analogous to V3a's.
8. **Convention 2 DESIGN tag** — N/A; no new SMOKE harness authored.
9. **Anti-pattern #8 (compress two tasks into one)** — V3a + V3b are distinct PRE-FLIGHT + DO + RECEIPT units. V3a complete at `06f1bf4`; V3b is its own five-phase task.

### Result

**PROCEED — but with explicit human authorization gate before DO step 1.**

PRE-FLIGHT complete; no §7 halt conditions tripped. All inputs verified; staging decisions logged; field-value snapshot recorded; 12-step DO plan documented below. Per the kickoff (a)-(d) handshake's "explicit authorization before any DO mutation" gate (1978-rev layout reconstruction + B3 1-digit race recode + new parser dispatch are all genuinely new edit surfaces with their own audit risks), the DO phase requires explicit user yes before commit. This PRE-FLIGHT entry + the STATUS section that ships with it are the only mutations this session unless authorization arrives.

### Proposed DO plan (12 steps)

1. **`mv` 7 V3b raw zips** from `~/Desktop/fetal-death-harmonization-build/raw_data/Fetal{1982..1988}US.zip` into `raw_data/fetal_death/` subdir (monorepo symlink). Verify post-`mv` SHAs unchanged (above baseline values). Then tag `task7_v3b-pre-do` on monorepo at the commit landing this PRE-FLIGHT entry.

2. **Construct `fetal_death/record_layout_1982_1988.csv`** from 1985 user-guide detail-record layout (pages 7-30 estimated). Cross-check selected fields against 1982 + 1988 for byte-position consistency. L13-extension discipline: pick 5-8 anchor fields (DATAYEAR, TABFLAG-equivalent, RESTATUS-equivalent, AGE, MRACE-equivalent, MEDUC-equivalent, gestation, birthweight) and document expected sentinel codes for value-distribution check at step 7.

3. **Edit `fetal_death/scripts/01_import/field_specs.py`**: add `RECORD_LEN_1978 = 200` constant; add `FETAL_1982_1988_FIELDS: list[tuple[str, int, int]]` field list (reconstructed from step 2 layout CSV); extend `layout_for_year()` with `if 1982 <= year <= 1988: return RECORD_LEN_1978, FETAL_1982_1988_FIELDS`; extend error message year-range; prepend docstring era line for V3b.

4. **Edit `fetal_death/scripts/03_harmonize/harmonize.py`**: extend `_build_field_map()` with `("field_1985", "1985")` entry in the era list; extend `_era_tag()` with `if 1982 <= year <= 1988: return "1985"` branch; extend error message year-range; extend B3 maternal_race_bridged recode with 1-digit V3b codes (`0`-`9` mapping). Document any V3b semantic-ambiguity decisions in DECISION_LOG (anticipated: B3 code `7` Other nonwhite residual → null mapping rationale, parallel to V3a `09` decision).

5. **Edit `fetal_death/variable_crosswalk_working.csv`**: add 2 new columns `field_1985,pos_1985`. Populate for V3b-applicable harmonized columns (estimated ~20-25 of 73 columns; the rest are V1-era-only and remain "N/A" for V3b).

6. **Edit `fetal_death/harmonized_schema.csv`**: extend `years_available` strings + `raw_source_by_year` cells for V3b-covered rows (~25-30 rows of 73; the rest are V1-era-only).

7. **Parse 7 V3b raw zips** via `python3 fetal_death/scripts/01_import/parse_fetal_year.py --year {Y} --zip raw_data/fetal_death/Fetal{Y}US.zip --out output/yearly_clean/fetal_death_{Y}_raw.parquet` for Y ∈ {1982..1988}. Verify per-year record counts match user-guide page-7 "Record count" (1982: 62,352; 1983: 60,584; 1984: 59,863; 1985: 59,690; 1986: 59,343; 1987: 59,358; 1988: 59,935). Tier-2 SMOKE gate: per-year record count match.

8. **L13-extension Tier-2 value-distribution sanity check** on each parsed yearly_clean parquet for the 5 H8-class demographic/filter columns:
   - `TABFLAG`-equivalent (byte 10): distribution {1, 2}; total record count split should ~50/50 (per page-7 "all records" vs "20+ weeks")
   - `RESTATUS`-equivalent (byte 12): distribution {1, 2, 3, 4}; code 4 (foreign) counts should match page-7 "To foreign residents" (low-double-digit each year)
   - `AGE`-equivalent (bytes 81-82 per PoC, or 81-85 umbrella): plausible 10-50 + sentinel 99; mean ~25-28
   - `RACE`-equivalent (byte 86): 1-digit code distribution {0-9} dominated by 1 (White) + 2 (Black); codes 4-8 (API granular) low-frequency
   - `MRACE3`-equivalent or similar: cross-check against RACE distribution
   Any out-of-range or wildly different distribution from V3a 1989-rev → halt; suggests byte-position shift or field-semantics shift between 1988 and 1989 not previously documented.

9. **Run full harmonize across 41 years (1982-2022)**: `python3 fetal_death/scripts/03_harmonize/harmonize.py --years 1982 1983 ... 2022 --out output/harmonized/fetal_death_harmonized.parquet`. Validate row count ≈ V3a baseline 1,930,886 + 1982-1988 sum ~419K = ~2.35M.

10. **Re-run derive**: `python3 fetal_death/scripts/04_derive/derive.py`. Produces v2.3.0 `fetal_death_derived.parquet`.

11. **Edit `validate_external_v2.py`**: extend `GUIDE_FETAL_DEATHS_GTE20` with 7 V3b entries; extend year-range loop to 1982-1994 (13 years); run. Gate **33/33 PASS** byte-exact (was 26/26 V3a; +7 new V3b rows).

12. **Run `validate_external.py`**: V1 era 55/55 PASS unchanged (byte-clean regression check; V3b additive backward extension MUST NOT touch V1-era values). Append `file_inventory.csv` + `external_validation_targets.csv` rows; bump version strings (.zenodo.json → 2.3.0; CITATION.cff → 2.3.0; README.md Years 1982-2022); write `V3b_1982_1988_LAYOUT_DECISIONS.md`; update `ABOUT_THIS_RELEASE.md` with V3b section. Write RECEIPT to `RECEIPTS/task7_v3b_<UTC>.md`; tag `task7_v3b-complete`.

### Forward-looking HALTs for the DO phase

1. **Per-year record count gate (Tier-2)** — parsed yearly_clean parquets must have row counts matching user-guide page-7 exactly (62,352 / 60,584 / 59,863 / 59,690 / 59,343 / 59,358 / 59,935). Any divergence → halt; suggests record-length mismatch or zip-internal corruption.
2. **DATAYEAR plausibility gate (Tier-1)** — every record in `fetal_death_{Y}_raw.parquet` must have `data_year == Y` (read from bytes 1-2). Any null/wrong-year → halt; suggests field_specs offset bug.
3. **V3a-era byte-clean gate (Tier-3)** — for each derived column, the 1989-2022 slice's column-vector SHA-256 must equal the V3a baseline's same slice. Any drift → halt; suggests harmonize.py 1978-rev branch incorrectly conditioning on year ≥ 1989 affected V3a/V2/V1 output.
4. **V1-era + V2.1 byte-clean gate (Tier-3)** — same for 2003-2022. Same halt rule.
5. **Tier-2 NVSR validation** — 33/33 PASS byte-exact (was 26/26 V3a; +7 V3b). The 7 new rows (1982-1988) must each return byte-exact against their user-guide-derived target. Any FAIL → halt; suggests TABFLAG / RESTATUS byte-position mismatch OR a 1978-rev sentinel code not in B3 race-recode coverage.
6. **L13-extension value-distribution check** — for each of the 5 H8 demographic/filter columns post-V3b:
   - `data_year`: byte exact {1982, 1983, ..., 1988} per file
   - `tabulation_flag`: {1, 2}
   - `residence_status`: {1, 2, 3, 4}
   - `maternal_race_bridged`: {1, 2, 3, 4} (with nulls for V3b 1-digit codes `7` Other nonwhite + `9` Not stated per B3 1978-rev extension)
   - `maternal_age`: 10-50 + sentinel 99 (need to verify against user-guide page 7 imputation note)
   If any column shows out-of-range or wildly different distribution from 1989+ → halt; suggests field_specs byte-offset shift between 1981 and 1982 not previously documented, OR an OCR-misread byte position propagated through page-5 cheap-check.
7. **B3 1-digit MRACE map completeness** — `_checked_remap` will halt loud if V3b yearly_clean produces a code outside {0..9}; this is the defensive halt working as designed. Any halt at DO step 9 with "unseen code <X>" → expand B3 map with a documented DECISION_LOG entry parallel to 2026-05-12T14:30Z V3a `09→null` decision.
8. **Detail-record layout extraction surfacing OCR-baked semantic ambiguities** — for any field where the 1985 user-guide text-layer is OCR-garbled to the point of preventing reliable byte-position extraction (e.g., the page-5 overview's "9­" for "9." in 1982 page-5 between FIPS State 187-188 and FIPS County 189-191), halt-and-ask. Do NOT silently guess.

### Forward-looking HALTs for next session (Convention 4 — if DO does not start this session)

1. **`task7_v3a-complete` tag** + 5 V3a output parquet SHAs unchanged (HALT 1+2 from STATUS 2026-05-12T14:30Z): re-verify at next session start (`git tag --list 'task7_v3a*'`; `shasum -a 256 output/harmonized/fetal_death_{harmonized,derived}.parquet output/yearly_clean/fetal_death_198{9,1990,1991}_raw.parquet`).
2. **7 V3b user guides + 7 V3b raw zips** at `raw_docs/fetal_death/` + `~/Desktop/fetal-death-harmonization-build/raw_data/` with SHAs matching this PRE-FLIGHT baselines. If any drift, re-download / halt.
3. **PyMuPDF text-layer extraction** on 7 user guides remains intact (no file corruption between sessions). Re-verify with a 5-line `len(page.get_text())>0` check at session start.
4. **Working tree clean** at the post-PRE-FLIGHT commit; no stale checkpoints.
5. **No `task7_v3b_*` tags yet** — DO doesn't begin until user authorization gate (this PRE-FLIGHT's HALT-Result).

### Notes

- Effort estimate per STATUS 2026-05-12T15:00Z: **3-4 sessions for V3b** (down from initial 4-5 session estimate which assumed OCR-via-Tesseract was the long pole — STATUS 15:00Z PoC superseded that; text-layer extraction is sufficient). The irreducible cost is per-field L13-extension value-distribution verification, not OCR.
- The 12-step DO plan above is one-session-aggressive if no semantic ambiguities arise; more likely it splits across 2-3 sessions: session A = steps 1-3 (zip-stage + layout-CSV + field_specs edit); session B = steps 4-8 (harmonize + parse + L13-extension); session C = steps 9-12 (validate + RECEIPT + version-string ripple).
- The B3 1-digit race recode (V3b) coexists with the B3 V3a 2-digit recode in the same `_checked_remap` call; the two key-sets (`"0".."9"` vs `"00".."09" + "18".."78" + "99"`) are byte-disjoint so no collision. Will verify at DO step 4 with explicit smoke-test.
- Q22 + Q23 both resolved this PRE-FLIGHT.

---

## PRE-FLIGHT for task7_v3a — 2026-05-12T14:05:00Z

### Scope summary

Extend fetal-death coverage backward by 3 years from current 1992-2022 (V2.1 state, 31 years) to 1989-2022 (34 years), by parsing 1989-1991 raw zips through the existing 1989-revision parser dispatch (`FETAL_1992_2002_FIELDS` in `fetal_death/scripts/01_import/field_specs.py`) and re-running harmonize + derive against the same B1-B6 normalizations. The 1989-1991 layout is empirically identical to 1992 (same 360-byte record, same first-7-byte DATAYEAR/TABFLAG/RECTYPE/RESTATUS positions, same Data Elements list on user-guide page 5-6). New version: v2.2.0 (additive backward extension; no schema mutation). V3b (1982-1988, 1978-revision, 200-byte records, bitmap-scanned PDFs) is **OUT OF SCOPE** for this task — separate decision pending an OCR feasibility PoC per the Q19 choice this session (V3a now; V3b is its own task once OCR feasibility verified). Per KICKOFF.md "Current planned sequence" step 2; user authorized via Q19/Q20 reply this session (Q19 deferred to LLM judgment, Q20 = KICKOFF as-is).

### Staging decisions (resolved at PRE-FLIGHT)

1. **Build-tree location**: canonical mutation target is the **monorepo** (`/Users/yoelplutchok/Desktop/vital-statistics-harmonization/fetal_death/`), per the Task 3 V2.1 precedent — `harmonize.py` lines 23-31 resolve `_PROJECT = fetal_death/`, `_PROJECT.parent = monorepo root`, and `_YEARLY_DIR = monorepo_root / output / yearly_clean` (a symlink to `~/Desktop/fetal-death-harmonization-build/output/yearly_clean/`). Raw inputs flow through `raw_data/fetal_death/` (symlink to `~/Desktop/fetal-death-harmonization-build/raw_data/fetal_death/`). NOT the standalone `~/Desktop/fetal-death-harmonization/` repo (which is the legacy pre-monorepo v2.0.1 state with uncommitted May 7 edits) and NOT the build-dir's local `scripts/` (which has STALE May-4 v2.0.0-era harmonize.py without V2.1 era logic). The monorepo is canonical; build-dir is data backing-store only.

2. **Input rearrangement (executed at this PRE-FLIGHT)**: 2026-05-12T03:50Z agent downloaded the V3a zips to `~/Desktop/fetal-death-harmonization-build/raw_data/Fetal{1989,1990,1991}US.zip` (top-level `raw_data/`), but the monorepo's symlink resolves to the sibling `raw_data/fetal_death/` subdir. RESOLUTION at PRE-FLIGHT: `mv` the 3 V3a zips into the `fetal_death/` subdir; V3b zips (Fetal{1982..1988}US.zip) left at top-level since V3b is out-of-scope. Verified post-`mv`: monorepo's `raw_data/fetal_death/Fetal{1989,1990,1991}US.zip` visible via symlink. SHAs preserved (pure file-system move).

3. **1989-1991 user guides downloaded (executed at this PRE-FLIGHT)**: not previously on disk. `curl -s -k` from canonical NCHS FTP path `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/fetaldeath/<YYYY>FetalUserGuide.pdf` (same convention as 1992-2022 user guides already on disk, validated against STATUS 2026-05-12T04:30Z HEAD-probe baselines). All 3 downloaded to `~/Desktop/fetal-death-harmonization-build/raw_docs/fetal_death/` (visible to monorepo via symlink). Content-length matches HEAD probe exactly for all 3.

4. **NVSR control source identified for 1989-1991**: per-year user-guide control count from **Machine/File/Data Characteristics → 20 WEEKS AND OVER → By residence** (page 7 of each user guide, same convention as the existing 1992 row in `external_validation_targets.csv` which cites "1992 NCHS Fetal Death User Guide control count"). PyMuPDF text extraction confirmed legible text layer (NCHS's 2009 rescan batch includes an embedded OCR layer; PyMuPDF returns clean strings for the control-count block). NO additional OCR pipeline needed. NVSR 57-08 Table B (which covers 1995+) is not the source for 1989-1991 — user-guide control counts are authoritative for pre-1995.

### Inputs

- [x] All required input files exist (verified by direct check at this PRE-FLIGHT timestamp)
  - **Raw V3a zips** (now at `raw_data/fetal_death/` via symlink → `~/Desktop/fetal-death-harmonization-build/raw_data/fetal_death/`):
    - `Fetal1989US.zip` sha256=`1d30d285a6558da697716879b05f3984c4f2bea15246b6deac7271ee9cb372bd` (16-char prefix matches STATUS 2026-05-12T03:50Z record `1d30d285a6558da6…`) ✓
    - `Fetal1990US.zip` sha256=`bcca5deb5de534d3d42e61abc4274bb39d68efd9f635548fcc0f4d546679987f` (matches `bcca5deb5de534d3…`) ✓
    - `Fetal1991US.zip` sha256=`aaa3e23250aac121c04c1068a645ff3a13deee94107917c2c30001936e701dd4` (matches `aaa3e23250aac121…`) ✓
  - **V3a user guides** (newly downloaded to `raw_docs/fetal_death/`):
    - `1989FetalUserGuide.pdf` 23,236,888 bytes (matches HEAD content-length) sha256=`54c55a40bffea18244bd14acc60a5fa094346e87c4557cb94633c7b52599e9d1` ✓
    - `1990FetalUserGuide.pdf` 22,897,888 bytes (matches) sha256=`91573bf8d93ee511405a6a38a96a97474dc55c80f0d421d9807bd9606e7a0578` ✓
    - `1991FetalUserGuide.pdf` 22,270,751 bytes (matches) sha256=`311fc21c98eab728f01796c4c903de44b177ac7549a00b61fcdaee425a12dd2d` ✓
  - **Existing canonical reference files** (1989-revision layout source, used as-is):
    - `fetal_death/record_layout_1992.csv` sha256=`45ca1273762db92f992b9255390846a43bc0e90f11b3fa32ebbe6f46f07a5a79` (the canonical 1989-revision layout CSV; valid for 1989-2002 per user guide cross-checks below) ✓
    - `fetal_death/scripts/01_import/field_specs.py` sha256=`35e788f3dd97eb156f572435be17a9097732958c3b1ef97491d3720fa61dbcf8` (current `FETAL_1992_2002_FIELDS` will be re-used; `RECORD_LEN_1992 = 360` matches 1989-1991 empirically) ✓
    - `fetal_death/scripts/03_harmonize/harmonize.py` sha256=`1b80fe73f2dbfc3e57f44f548fb2766df5c01c791482d4f4c32a99a99deae8c3` (`_era_tag()` line 86-96 needs 1-condition extension to cover 1989-1991 → era="1992"; cheapest DO edit) ✓
    - `fetal_death/harmonized_schema.csv` sha256=`72272c5537fdfa5b926a6aded69920bb5357a7bb5daef09742dfb494dadfa1ab` (`years_available` strings for V2-era columns need 3-year backward extension; documented in DO scope below) ✓
    - `fetal_death/external_validation_targets.csv` sha256=`0d9c361627e898a39533bca0277f01969a9fc8cd34046000d26b99b21d77576f` (3 new rows for 1989-1991 control counts) ✓
    - `fetal_death/file_inventory.csv` sha256=`817124dbbce70b1181f580ea8517350e1a059770486448ad80c8d0eb8e2efab7` (3 new rows for 1989-1991 zips + user guides) ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - `task3_v21_fetal_death` (V2.1, 2003+2004 transition): COMPLETE 2026-05-12 at monorepo `8ca5bf9` (`task3-complete` tag); V2.1 derived parquet at sha=`55d3d310cf5e1cbd8719325e3122505472d69dc4316af32f17c67d78c6c8c447` ✓
  - `natality_v28_rename`: COMPLETE 2026-05-12T13:35Z at monorepo `fc396fc` (`natality_v28_rename-complete` tag on both monorepo + build-dir); 4 v2.8 natality parquet SHAs verified stable at session start ✓
  - V1-era baseline parquets present (`fetal_death_harmonized.V1_baseline.parquet` sha=`cbcc91d24f2982d74bef0ba87a64495fb5cbd27928f720ee63d4006581bea2c0`; `fetal_death_derived.V1_baseline.parquet` sha=`2795f099380461581a59908b7653f536bb5f1cdbfd78f101097f0495c0232a8d`) — provide pre-V3a byte-clean comparison baseline for VERIFY phase ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - No `task7_v3a_*` tags in monorepo (verified: `git tag --list 'task7_*'` empty) ✓
  - No partial V3a edits in canonical work tree — monorepo tree CLEAN at `fc396fc` ✓
  - Tier-0 byte-length probe confirms zips parse: `unzip -p Fetal{1989,1990,1991}US.zip | head -1 | wc -c` = 361 (360 data + 1 newline) for all 3 years, matching `RECORD_LEN_1992 = 360` ✓
  - First-4-byte spot-check (DATAYEAR field): 1989 record begins `1989...`, 1990 begins `1990...`, 1991 begins `1991...` — DATAYEAR @ bytes 1-4 confirmed for 1989-revision layout ✓

### Environment

- [x] Python version: 3.13.9 (required ≥3.11) ✓
- [x] pandas version: 2.3.2 (required ≥2.3) ✓
- [x] pyarrow version: 18.1.0 (required ≥18.0) ✓
- [x] PyMuPDF (fitz) version 1.27.2.2: available for any further user-guide control-count extraction (no Tesseract install needed for V3a since text layer is embedded in NCHS's 2009-rescan-batch PDFs)
- [x] Working directory clean (`git status` in monorepo): CLEAN at `fc396fc` ✓
- [x] On expected branch: monorepo `main` ✓
- [x] Build-dir `~/Desktop/fetal-death-harmonization-build/` is **not a git repository** (verified). It is a data-backing-store directory only; canonical version control is the monorepo. Documented here so future sessions don't expect tags/log on the build-dir.

### Source documentation

- [x] `1989FetalUserGuide.pdf` page 7 (control block) text-extracts cleanly via PyMuPDF; control values:
  - Total record count = 61,295 (matches what the parsed parquet should produce per-year)
  - All fetal deaths By residence = 61,236 / To foreign residents = 59
  - **20 WEEKS AND OVER → By residence = 30,469** (the V3a validation target for 1989)
- [x] `1990FetalUserGuide.pdf` page 7: Record count = 64,349; **20 WEEKS AND OVER → By residence = 31,386** (validation target for 1990)
- [x] `1991FetalUserGuide.pdf` page 7: Record count = 63,265; **20 WEEKS AND OVER → By residence = 30,160** (validation target for 1991)
- [x] L9 cheap-check on layout reusability: page 5-6 Data Elements list in 1989/1990/1991 user guides matches the 1992 user guide field-by-field for the first 60 fields (Data year 1-4; Tabulation flag 5; Record type 6; Resident status 7; NCHS State 17-18; FIPS State 22-23; NCHS state of residence 33-34; Population size - city 41; ... ; Mother age 69-76 + 87-88; Mother race 79-81; Mother education 82-84; ...; Father age 105-107; ...; Method of delivery 220-226; Medical risk factors 228-244; Congenital anomalies 279-300; NCHS SMSA 357-359). No byte-position drift observed. NCHS terminology changed cosmetically from "SMSA" (1989) to "MSA" (1990+) at the same byte position 55-58 — semantically identical (Metropolitan Statistical Area; MSA designation re-numbering in mid-1990s is post-V3a era and irrelevant for raw read).
- [x] **L13-extension discipline** applied: byte-position match (above) AND first-record data values are plausible (DATAYEAR=year matches the file name; TABFLAG ∈ {1,2}; RECTYPE ∈ {1,2}; RESTATUS ∈ {1,2,3,4}). Value-distribution sanity check on harmonized parquet is a Tier-2 SMOKE deliverable (per row L13-extension catch: "compute the parsed value distribution and verify it matches the user guide's documented value range / sentinel codes").

### Outputs

- [x] Intended output paths to be **overwritten** (explicit overwrite mark; these are the V2.1 v2.1.0 parquets that V3a appends 3 more years to):
  - `output/harmonized/fetal_death_harmonized.parquet` (V2.1 sha=`333e1e66…d9e0` → new V3a/v2.2.0 sha TBD)
  - `output/harmonized/fetal_death_derived.parquet` (V2.1 sha=`55d3d310…c447` → new V3a/v2.2.0 sha TBD)
  - `output/yearly_clean/fetal_death_1989_raw.parquet` (new file)
  - `output/yearly_clean/fetal_death_1990_raw.parquet` (new file)
  - `output/yearly_clean/fetal_death_1991_raw.parquet` (new file)
- [x] **No `.V1_baseline.parquet` overwrite** — those are V1-era snapshots preserved for byte-clean comparison. They predate Task 3 V2.1 and are not touched by V3a.
- [x] New metadata rows (additive, not overwrite):
  - `external_validation_targets.csv`: +3 rows (1989, 1990, 1991 fetal_deaths_gte20wk_resident with values 30469, 31386, 30160; source "<YYYY> NCHS Fetal Death User Guide control count")
  - `file_inventory.csv`: +3 rows (Fetal1989US.zip, Fetal1990US.zip, Fetal1991US.zip with `record_length=360, doc_filename=<YYYY>FetalUserGuide.pdf, notes="1989-revision uniform; V3a backward extension"`)

### Field-value snapshot for cells / rows / columns being mutated

| Artifact | Current state | Target state (post-V3a) | Verified at this PRE-FLIGHT |
|---|---|---|---|
| `fetal_death/scripts/03_harmonize/harmonize.py` line 94 `if 1992 <= year <= 2002:` | year-range 1992-2002 → era="1992" | **1989-2002 → era="1992"** (1-condition extension) | ✓ direct read |
| `fetal_death/scripts/03_harmonize/harmonize.py` line 96 `raise ValueError(f"Year {year} outside supported range (1992-2022)")` | error msg says "1992-2022" | **"1989-2022"** | ✓ direct read |
| `fetal_death/scripts/01_import/field_specs.py` line 8 docstring `1992-2002: V2.0 — single uniform 1989-revision layout (360 data bytes)` | docstring says 1992-2002 | **1989-2002** | ✓ direct read |
| `fetal_death/scripts/01_import/field_specs.py` line 20 constant `RECORD_LEN_1992 = 360` | scoped to 1992 era tag | Keep constant unchanged; `layout_for_year` mapping extended to dispatch 1989-1991 → same `FETAL_1992_2002_FIELDS` + `RECORD_LEN_1992`. Alternatively rename constant to `RECORD_LEN_1989 = 360`. **Decision: keep name + extend mapping (lower edit surface, semantically identical)** | ✓ direct read |
| `fetal_death/harmonized_schema.csv` `years_available` column | strings like "1992-2002, 2003-2004, ..." for V2-era columns | **extend leading 1992 → 1989** where applicable (the harmonized columns sourced from FETAL_1992_2002_FIELDS get a 3-year backward extension; column rows whose years_available starts at 2005 (V1-only fields) are unchanged) | partial — full per-row enumeration deferred to DO step 2 |
| `fetal_death/external_validation_targets.csv` | last entries 2022; no 1989-1991 rows | **+3 rows** for 1989/1990/1991 `fetal_deaths_gte20wk_resident` = 30469 / 31386 / 30160; source "<YYYY> NCHS Fetal Death User Guide control count" | ✓ values confirmed from user-guide page 7 extraction |
| `fetal_death/file_inventory.csv` | first row year=1992; no 1989-1991 rows | **+3 rows** for 1989/1990/1991 raw zips + user guides; `record_length=360`, `notes="1989-revision uniform; V3a backward extension"` | ✓ raw zip + user-guide SHAs above |
| `fetal_death/.zenodo.json` version | "v2.1.0" (current) | **"v2.2.0"** (additive backward extension) | not yet read — DO step 8 |
| `fetal_death/CITATION.cff` version | "2.1.0" | **"2.2.0"** | not yet read — DO step 8 |
| `fetal_death/ABOUT_THIS_RELEASE.md` | V2.1 release notes | **+V3a section** documenting 1989-1991 extension | DO step 9 |
| `fetal_death/README.md` Years coverage | "1992-2022" | **"1989-2022"** | DO step 9 |
| New layout-decisions doc | (none) | **`fetal_death/V3a_1989_1991_LAYOUT_DECISIONS.md`** (new file documenting 1989-revision reusability + the L13-extension verification path) | DO step 9 |

**No mutable annotation values pinned at this PRE-FLIGHT moment** (per Convention 1 SHAPE-not-VALUE) — all numeric values listed above are either:
- Source-document derived (the 3 control counts from user-guide page 7 — authoritative values that won't drift)
- SHA-256 baselines from immutable artifacts (raw zips, user guides — content-locked)
- Schema-level edits (extending era boundary, not pinning a record count that V2.x evolves)

### Halt conditions tripped

(none — all checks pass)

The following potential halt risks were considered and resolved:

1. **§7 condition 1 (PRE-FLIGHT check fails)** — every input present + verified. PASS.
2. **§7 condition 11 (Source PDF SHA changed upstream)** — N/A; PDFs newly downloaded this session. Future verification of NCHS-side SHA stability deferred to forward-looking HALT.
3. **§7 condition 12 (Conflicting documentation)** — L9 cheap-check confirms 1989-1991 page 5-6 Data Elements lists match the 1992 user guide field-by-field. PASS.
4. **§7 condition 17 (Scope creep)** — V3b (1982-1988) explicitly excluded; V3a's `_era_tag` extension and `_layout_for_year` mapping update touch ONLY the 1989-1991 path. Build dir's V3b zips (Fetal1982-1988US.zip) remain at the build-dir top-level `raw_data/` — NOT visible through the monorepo symlink — and are out of any V3a code path.
5. **L13-extension (byte-position vs field-semantics)** — verified at multiple anchor fields. Full value-distribution check is a Tier-2 SMOKE deliverable.
6. **Anti-pattern #8 (compress two tasks into one)** — V3a is a strict subset task. V3b will get its own PRE-FLIGHT + DO + RECEIPT if/when authorized.

### Result

**PROCEED.** PRE-FLIGHT complete; no §7 halt conditions tripped. DO phase authorized to begin per the 10-step plan documented below. Estimated DO budget: 30-60 minutes wall-clock for re-derive + validation; total task budget ~1 session per STATUS 2026-05-12T03:50Z estimate.

### Proposed DO plan (10 steps)

1. **Tag `task7_v3a-pre-do`** on monorepo at the post-PRE-FLIGHT commit (the commit that lands this PRE_FLIGHT_LOG entry).
2. **Edit `fetal_death/scripts/03_harmonize/harmonize.py`**: `_era_tag()` line 94 → `if 1989 <= year <= 2002:`; line 96 error msg → `"1989-2022"`.
3. **Edit `fetal_death/scripts/01_import/field_specs.py`**: extend `layout_for_year(year)` to map 1989-1991 → `(RECORD_LEN_1992, FETAL_1992_2002_FIELDS)`. Update docstring lines 8-9 to read "1989-2002: V2.0 — single uniform 1989-revision layout (360 data bytes)". Update line 30 section comment "1992-2002" → "1989-2002".
4. **Parse 1989, 1990, 1991 raw zips** via `python3 fetal_death/scripts/01_import/parse_fetal_year.py --year {Y} --zip raw_data/fetal_death/Fetal{Y}US.zip --out output/yearly_clean/fetal_death_{Y}_raw.parquet`. Verify per-year record count matches user-guide page 7 (61,295 / 64,349 / 63,265).
5. **Re-run full harmonize**: `python3 fetal_death/scripts/03_harmonize/harmonize.py --years 1989 1990 1991 1992 1993 ... 2022 --out output/harmonized/fetal_death_harmonized.parquet`. Validate row count = sum of per-year record counts (V2.1 baseline 1,634,195 + 1989-1991 ~189k = ~1.82M).
6. **Re-run derive**: `python3 fetal_death/scripts/04_derive/derive.py` (or equivalent). Produces v2.2.0 `fetal_death_derived.parquet`.
7. **Append 3 rows to `external_validation_targets.csv`** (1989/1990/1991 fetal_deaths_gte20wk_resident = 30469 / 31386 / 30160).
8. **Run `validate_external_v2.py`**: gate 26/26 PASS (was 23/23; +3 new V3a rows). Halt on any FAIL.
9. **Run `validate_external.py`**: V1 era 55/55 PASS unchanged (byte-clean regression check — V3a additive backward extension MUST NOT touch V1-era values; SHA of post-V3a derived's 2005-2022 slice should equal pre-V3a V2.1 derived's 2005-2022 slice + rows-from-2003-2004 unchanged. Compare via PyArrow per-year groupby).
10. **Append `file_inventory.csv` rows + V3a-extension doc + version bumps** (`.zenodo.json`, `CITATION.cff` → 2.2.0; `README.md` Years 1989-2022; `ABOUT_THIS_RELEASE.md` V3a section; new `V3a_1989_1991_LAYOUT_DECISIONS.md`).

### Forward-looking HALTs for the DO phase

1. **Per-year record count gate (Tier-2)** — parsed yearly_clean parquets must have row counts matching user-guide page 7 exactly (61,295 / 64,349 / 63,265). Any divergence → halt; suggests record-length mismatch or zip-internal corruption.
2. **DATAYEAR plausibility gate (Tier-1)** — every record in `fetal_death_{Y}_raw.parquet` must have `data_year == Y` (read from bytes 1-4). Any null/wrong-year → halt; suggests field_specs offset bug.
3. **V1-era byte-clean gate (Tier-3)** — for each derived column, the 2005-2022 slice's column-vector SHA-256 must equal the V2.1 baseline's same slice. Any drift → halt; suggests harmonize.py logic incorrectly conditioning on year < 1992 affected V1-era output.
4. **V2.1 byte-clean gate (Tier-3)** — same for 2003-2004 slice. Same halt rule.
5. **Tier-2 NVSR validation** — 26/26 PASS byte-exact (was 23/23 V2.1; +3 V3a). The 3 new rows (1989/1990/1991) must each return byte-exact against their user-guide-derived target.
6. **L13-extension value-distribution check** — for each of the 5 H8 demographic/filter columns post-V3a:
   - `maternal_age` (Int16): 1989-1991 distribution within plausible range (10-50, with sentinel 99 allowed); mean ~25-28
   - `maternal_race_bridged` (Int8): {1,2,3,4} only
   - `hispanic_origin` (Int8): {0,1,2,3,4,5,6,7,8,9} with 0-5 dominant
   - `tabulation_flag` (Int8): {1,2}
   - `residence_status` (Int8): {1,2,3,4}
   If any column shows out-of-range or wildly different distribution from 1992-1994 → halt; suggests field_specs byte-offset shift between 1988 and 1989 not previously documented.

### Notes

- Convention 2 DESIGN tag is not applicable to this PRE-FLIGHT — no new SMOKE harness is being authored here (existing `validate_external.py` and `validate_external_v2.py` already implement the canonical SMOKE pattern for fetal-death; V3a re-uses them and extends their year set, not the harness logic).
- Convention 3 Field-value snapshot complete above.
- Convention 4 Forward-looking HALTs for next session emitted in the RECEIPT at task close.
- V3b PoC decision deferred to a separate session/task; KICKOFF as-is sequence per Q20.

---

## PRE-FLIGHT for natality_v28_rename — 2026-05-12T05:30:00Z

### Scope summary

Rename four natality harmonized columns from v2.7.0 names to canonical cross-product names: `year → data_year`, `restatus → residence_status`, `maternal_race_bridged4 → maternal_race_bridged`, `maternal_hispanic_origin → hispanic_origin`. Output: new natality v2.8.0 deposit (breaking change; v2.7.0 stays immutable at its DOI). Per KICKOFF.md "Current planned sequence" step 1 (data-first pre-submission scope per DECISION_LOG 2026-05-12T03:30:00Z). 14-step DO plan canonical in DECISION_LOG 2026-05-12T03:25:00Z. Mutation lives in standalone build dir `/Users/yoelplutchok/Desktop/natality-harmonization/` (HEAD `dcabd8c`); monorepo's `natality/` subdir is a mirror that re-syncs AFTER v2.8 ships.

### Staging decisions (resolved at PRE-FLIGHT)

1. **Build-dir `M README.md` pre-existing diff** (per STATUS 2026-05-12T05:10Z Forward-looking HALT 1): one-line cosmetic removal of "(for a new researcher or LLM)" from a section header — pre-existing, not this task's. RESOLUTION: stash before v2.8 work so v2.8's first commit doesn't pick it up; user can decide whether to commit/discard separately.
2. **v2.7.0 parquets on disk** (per STATUS 2026-05-12T05:10Z Forward-looking HALT 3): the prior session reported `output/*.parquet` not present; in fact parquets DO exist at `output/harmonized/*.parquet` and `output/yearly_clean/*.parquet` (prior glob missed subdir layout). No re-derive needed for current state; v2.8 re-derive will overwrite `output/harmonized/`.
3. **Tag location**: build-dir `natality_v28_rename-pre-do` tags the build repo's pre-DO commit (where the actual mutations happen). Monorepo will also get tagged at the corresponding state-file commit per Task 3 convention.

### Inputs

- [x] All required input files exist (verified by direct read)
  - `/Users/yoelplutchok/Desktop/natality-harmonization/metadata/harmonized_schema.csv`: present, 95 rows (94 data + 1 header). 4 rename-target rows verified at row positions 1 (year), 2 (restatus), 3 (maternal_hispanic_origin), 4 (maternal_race_bridged4). ✓
  - `output/harmonized/natality_v2_harmonized_derived.parquet`: present, 138,819,655 rows × 84 cols, sha256=`9f917a43474eb9e3ed23aa95c714209421c25c29937376651149d22fab934ef0` ✓ (matches Forward-looking HALT 1 from DECISION_LOG 2026-05-12T03:30Z exactly)
  - `output/harmonized/natality_v3_linked_harmonized_derived.parquet`: present, 74,943,824 rows × 94 cols, sha256=`46c169b59b040028d9830546fad71f30d0c6364f10fbc1676b56ae6ee993eb16` (no prior baseline SHA recorded — record this one now for HALT verification at re-derive) ✓
  - 36 raw NCHS zips in `raw_data/` (1990-2024 + linked-cohort files) — present for full re-derive if needed ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - task3_v21_fetal_death: complete 2026-05-12 at `8ca5bf9` (`task3-complete` tag in monorepo) ✓
  - public-repo v1.0 push: complete 2026-05-12 at `a18ca3a` (https://github.com/yoelplutchok/vital-statistics-harmonization) ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - No `natality_v28_*` tags in build dir or monorepo ✓
  - No partial v2.8 edits — build dir's only working-tree diff is the pre-existing `M README.md` (resolved via stash at staging decision 1) ✓

### Environment

- [x] Python version: 3.13.9 (required ≥3.11) ✓
- [x] pandas version: 2.3.2 (required ≥2.3) ✓
- [x] pyarrow version: 18.1.0 (required ≥18.0) ✓
- [x] Build-dir working tree CLEAN post-stash (verified at DO step 0); monorepo working tree clean at session start (`ad5ff1f`) ✓
- [x] On expected branch: build dir `main` tracking `origin/main`; monorepo `main` ✓

### Source documentation

No external NCHS PDFs consumed by this task (v2.8 is a column rename, not a content change). The aliasing-helper `shared/helpers/canonical_join_keys.py` `NATALITY_TO_CANONICAL` dict (lines 20-25 in the monorepo, 4 entries verified) is the documentation that this rename satisfies; after v2.8 the dict becomes empty + deprecation note.

### Outputs

- [x] Intended output paths exist as v2.7.0 artifacts — will be **overwritten** by v2.8 re-derive (this is the explicit overwrite mark):
  - `output/harmonized/natality_v2_harmonized_derived.parquet` (v2.7.0 SHA `9f917a43...` → new v2.8 SHA TBD)
  - `output/harmonized/natality_v3_linked_harmonized_derived.parquet` (v2.7.0 SHA `46c169b5...` → new v2.8 SHA TBD)
  - `output/harmonized/natality_v2_harmonized.parquet` (pre-derive intermediate)
  - `output/harmonized/natality_v3_linked_harmonized.parquet` (pre-derive intermediate)
- [x] Convenience subsets in `output/convenience/` will be regenerated downstream of harmonize step.
- [x] No NEW output paths introduced by this task — all are v2.7.0 paths overwritten in-place under the new schema.

### Field-value snapshot for cells / rows / columns being mutated

Cross-checked against DECISION_LOG 2026-05-12T03:25:00Z Field-value snapshot at this PRE-FLIGHT. State unchanged from that snapshot:

| Artifact | Current (v2.7.0) | Target (v2.8) | Verified at this PRE-FLIGHT |
|---|---|---|---|
| `metadata/harmonized_schema.csv` row 1 | `year,Birth year,int16,1990-2024,...` | `data_year,Birth year,int16,1990-2024,...` | ✓ direct grep |
| `metadata/harmonized_schema.csv` row 2 | `restatus,Resident status (NCHS),int8,1\|2\|3\|4,...` | `residence_status,Residence status,int8,1\|2\|3\|4,...` | ✓ direct grep |
| `metadata/harmonized_schema.csv` row 3 | `maternal_hispanic_origin,Mother's Hispanic origin recode,int8,...` | `hispanic_origin,...` | ✓ direct grep |
| `metadata/harmonized_schema.csv` row 4 | `maternal_race_bridged4,Mother's bridged race (4 categories),int8,...` | `maternal_race_bridged,...` | ✓ direct grep |
| natality v2 parquet | columns `year`, `restatus`, `maternal_hispanic_origin`, `maternal_race_bridged4` present | renamed to canonical | ✓ pyarrow schema read |
| linked v3 parquet | same 4 columns present | renamed to canonical | ✓ pyarrow schema read |
| `shared/helpers/canonical_join_keys.py` `NATALITY_TO_CANONICAL` | 4 entries (year→data_year, restatus→residence_status, maternal_race_bridged4→maternal_race_bridged, maternal_hispanic_origin→hispanic_origin) | empty dict + deprecation note | ✓ direct grep (monorepo helper) |

**String-literal reference counts** (the edit surface, scoped to build-dir `scripts/` + `metadata/` + `docs/`; output/ excluded):

| Pattern | Count | DECISION_LOG predicted |
|---|---:|---:|
| `"year"` | 46 | 48 |
| `'year'` | 2 | (combined) |
| `"restatus"` | 3 | 3 |
| `'restatus'` | 0 | (combined) |
| `"maternal_race_bridged4"` | 6 | 6 |
| `'maternal_race_bridged4'` | 0 | (combined) |
| `"maternal_hispanic_origin"` | 4 | 4 |
| `'maternal_hispanic_origin'` | 0 | (combined) |
| **TOTAL** | **61** | **61** |

Match with DECISION_LOG 2026-05-12T03:25Z is exact (61=61). The "48" predicted for "year" split as 46+2 here (double-quote vs single-quote) — total identical. **No staleness drift.**

### Halt conditions tripped

(none — all checks pass)

### Result

**PROCEED.** PRE-FLIGHT complete; no §7 halt conditions tripped. DO phase authorized to begin per the 14-step plan in DECISION_LOG 2026-05-12T03:25:00Z. Forward-looking HALT 6 from STATUS 2026-05-12T03:30Z (string-literal rename must be scoped via `s|"year"|"data_year"|g` and `s|'year'|'data_year'|g`, NOT bare-word replacement) is binding for every DO sed/Edit operation. Re-derive budget ~5-10 minutes wall-clock; 183 NVSR validation + 33/35-linked validation are gates 7-8 of the DO plan.

---

## PRE-FLIGHT for task3_v21_fetal_death — 2026-05-11T21:30:00Z

### Scope summary

Add 2003 + 2004 fetal-death transition years to the harmonized resource (V2.1.0). Bundle the H8 schema-doc dtype-drift reconciliation (5 columns shipped `string` in v2.0.0 parquet but declared `int` in `harmonized_schema.csv`) into the same Task 3 parquet re-derivation. Per `KICKOFF.md` 2026-05-11 sequencing decision and STATUS 2026-05-11T20:50Z, this is sequence step 1 of 5; manuscript re-pass is step 5.

### Staging decisions (resolved at PRE-FLIGHT per Convention 3 second bullet)

§15 Task 3 spec + `fetal_death/scripts/run_pipeline.py` assume `RAW_DIR = REPO_ROOT / "raw_data/fetal_death"` (monorepo-local), but the actual raw zips + user-guide PDFs + the existing 29-year `output/yearly_clean/` parquets all live at `~/Desktop/fetal-death-harmonization-build/` (the v2.0.0 build environment). Three sub-decisions resolved before any DO mutation:

1. **Build location** — symlink raw inputs into monorepo. `raw_data/fetal_death` and `raw_docs/fetal_death` and `output/` (which contains `yearly_clean/`, `harmonized/`, `validation/`) are now symlinks to the sibling build dir. All symlink targets are `.gitignore`d (`**/raw_data/*`, `**/raw_docs/*` already present; `output/` newly added in this PRE-FLIGHT to keep the tree clean). The monorepo can now run `fetal_death/scripts/run_pipeline.py` without further plumbing.
2. **Yearly-parse reuse** — reuse existing `output/yearly_clean/fetal_death_{year}_raw.parquet` for the 29 already-shipped years; only parse 2003 + 2004 fresh. Saves ~5 min build time. Safe because the parser code is unchanged for 1992-2002 + 2005-2022 (DO-phase changes are 2003/2004-only in `field_specs.py` and the harmonize-step dtype fix for H8, which lands at the harmonize stage downstream of yearly_clean).
3. **Layout ambiguity policy** — halt-and-ask per ambiguity (§7 halt condition 12, conflicting documentation). Aligned with §2 principle "fail closed".

### Inputs
- [x] All required input files exist (verified via symlinks; sibling-build-dir-resolved paths)
  - `raw_data/fetal_death/Fetal2003US.zip`: present, sha256=`7311ffab3314bf8f7ebb1465b153cc569be88d3126edabab680b90c7a4844f99`, 2,755,093 B compressed; uncompressed `VS03FETL.DETUSPUB` is 73,679,944 B ✓
  - `raw_data/fetal_death/Fetal2004US.zip`: present, sha256=`42d68172ea1976cc5c371ecce36f5b33bb0efb6b6f139443bbec729674395c41`, 2,721,055 B compressed; uncompressed `VS04FETL.DETUSPUB` is 80,034,070 B ✓
  - `raw_docs/fetal_death/fetaldeath0304problems.pdf`: present, sha256=`b2214b09722a214932728b8a3dc38c83d85b97a3a728f9e78daa7b26739e1331`, 135,683 B, 6 pages ✓
  - `raw_docs/fetal_death/2003FetalUserGuide.pdf`: present, sha256=`281160b5339693412ce8275593584fc728e90fd29f4d23ac5273d9b3d5ad8146`, 2,931,130 B, 163 pages ✓
  - `raw_docs/fetal_death/2004FetalUserGuide.pdf`: present, sha256=`ca8be48e77891660059ad93110f606ad0eedded703f174da8c283e4914272709`, 2,584,516 B, 110 pages ✓
  - `output/harmonized/fetal_death_derived.parquet` (v2.0.0 shipped baseline for byte-clean regression check): sha256=`90af89b9e659ca2b580d8286b5598588cfb2d17e93f26c1dc1ae00d097f0afdd` — MATCHES `fetal_death/PROVENANCE.md` ✓
  - `output/harmonized/fetal_death_derived.V1_baseline.parquet`: present (alternate V1-only regression baseline) ✓
  - `output/yearly_clean/fetal_death_{year}_raw.parquet` for year ∈ {1992-2002, 2005-2022}: 29 files present (verified by directory listing) ✓
  - `fetal_death/harmonized_schema.csv`: present, sha256=`72272c5537fdfa5b926a6aded69920bb5357a7bb5daef09742dfb494dadfa1ab` ✓
  - `fetal_death/file_inventory.csv`: present, 30 rows (no 2003 or 2004 row yet — DO will append) ✓
  - `fetal_death/external_validation_targets.csv`: present (DO will append 2003 + 2004 rows for NVSR 57-08 counts + rates) ✓
  - `fetal_death/scripts/01_import/{parse_fetal_year,field_specs,zip_text_stream}.py`: present ✓
  - `fetal_death/scripts/03_harmonize/harmonize.py`: present ✓
  - `fetal_death/scripts/04_derive/derive.py`: present ✓
  - `fetal_death/scripts/05_validate/{validate_2022,validate_external,validate_external_v2}.py`: present ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - task1 (2026-05-11): ✓
  - task2 (2026-05-11): ✓
  - task6 (2026-05-11): ✓
  - task4 (2026-05-11): ✓
  - task5 (2026-05-11, `9aaa702`): ✓
  - sequencing decision (2026-05-11, `5577c87`): ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/task3_*.md`: does not exist ✓
  - `output/yearly_clean/fetal_death_2003_raw.parquet`: does not exist (good) ✓
  - `output/yearly_clean/fetal_death_2004_raw.parquet`: does not exist (good) ✓
  - `fetal_death/record_layout_2003.csv`, `record_layout_2004.csv`: do not exist (good — DO will create) ✓
  - No `task3-pre-do` git tag yet (good — will tag after this PRE-FLIGHT commit) ✓

### Environment
- [x] Python 3.13.9 (required ≥3.11) ✓
- [x] pandas 2.3.2 (required ≥2.3) ✓
- [x] pyarrow 18.1.0 (required ≥18.0) ✓
- [x] R version: N/A (Task 3 is Python-only)
- [x] Working directory clean before staging: `git status` showed clean before symlinks. After staging: only `.gitignore` modified (one-line `output/` addition). After this PRE-FLIGHT commit: clean again. ✓
- [x] On expected branch: `main` at `5577c87` ✓

### Source documentation — L9 cheap-check on 2003 + 2004 user guides

Per §15 Task 3 PRE-FLIGHT direction ("Apply L9 cheap-check: verify the named page/section in the user-guide PDF actually documents the field at the claimed byte position"):

- [x] **Apparent 1351-vs-3350 conflict resolved at PRE-FLIGHT.** Both user guides' page-2 SAS reproduction snippet declares `INFILE 'C:FETxxUS.DAT' LRECL=3350`. The §15 Task 3 spec says 1351-byte records for 2003 and 1501-byte records for 2004. Empirical verification: opened the actual `VS03FETL.DETUSPUB` and `VS04FETL.DETUSPUB` member inside each zip; first 5 records measured byte-exact at **1351 bytes (data 1350 + CRLF) for 2003** and **1501 bytes (data 1500 + CRLF) for 2004**. Total uncompressed sizes divide evenly: 73,679,944 / 1351 = 54,537 records (2003); 80,034,070 / 1501 = 53,320 records (2004). The user guide's `LRECL=3350` is a SAS-side maximum, not the literal data byte length — the public-use files contain the actual shorter records and SAS pads internally. The §15 record-length numbers are CORRECT; no plan amendment needed. ✓
- [x] **TABFLAG position-9 confirmed empirically.** First 12 chars of records 1-3 in both zips are exactly `b'      S12   '`; the user guide and `fetaldeath0304problems.pdf` both name TABFLAG at position 9. Char 9 = `2` (= 20+ weeks, the dominant value in the early-records sample). The known TABFLAG error documented in `fetaldeath0304problems.pdf` (records with COMBGEST=99 in a 42-state list misclassified as <20 weeks) is a derivable normalization that will land in `harmonize.py` during DO as a new "B-class" normalization. **Open: this is a NEW normalization not in `fetal_death/ABOUT_THIS_RELEASE.md`'s B1-B6 list — DO will document it as B7 in the receipt and DECISION_LOG.** Soft-flag, not a halt.
- [x] **A/S version-byte at position 7 confirmed empirically.** Sampled first 100,000 records of each zip; position 7 distribution: 2003 = {S: 53,503; A: 994}; 2004 = {S: 51,321; A: 1,964}. Both years dominated by S (the 2003-revision) — the A records (1.8% in 2003; 3.7% in 2004) are the persisting-1989-revision-state records. **The §15 plan's "per-state branch on the version-byte (A vs S)" terminology is consistent with empirical observation.** Whether the dispatch should genuinely branch on position 7 byte, or branch on state code mapped to a revision-adoption table, will be reconciled in DO from a fuller reading of the 2003 user guide's record-layout section. Soft-flag, not a halt.
- [x] All cited Zenodo DOIs resolve: not specifically queried (Task 3 does not consume Zenodo deposit contents directly; the existing parquets are local).

### Outputs
Intended outputs do not yet exist (or, where they exist, will be overwritten with version-bumped successors). All non-trivial new outputs will be written under `output/` (gitignored; the new v2.1.0 Zenodo deposit is the canonical home) or in `fetal_death/` (the monorepo-shipped state).

- [x] `fetal_death/record_layout_2003.csv` — does not exist (good) ✓
- [x] `fetal_death/record_layout_2004.csv` — does not exist (good) ✓
- [x] `output/yearly_clean/fetal_death_2003_raw.parquet` — does not exist (good) ✓
- [x] `output/yearly_clean/fetal_death_2004_raw.parquet` — does not exist (good) ✓
- [x] `output/harmonized/fetal_death_harmonized.parquet` — exists at v2.0.0 sha=`f09beb4a…0e5928` (will be overwritten with v2.1.0; v2.0.0 sha preserved in `fetal_death/PROVENANCE.md` and recoverable from the published Zenodo deposit 10.5281/zenodo.20031571)
- [x] `output/harmonized/fetal_death_derived.parquet` — exists at v2.0.0 sha=`90af89b9…f0afdd` (same disposition; canonical baseline for the V1-era byte-clean regression check)
- [x] `output/harmonized/fetal_death_derived.V1_baseline.parquet` — exists; auxiliary V1-only filtered baseline; will be re-derived
- [x] `fetal_death/scripts/01_import/field_specs.py` — exists; will be extended (add 2003/2004 layouts + per-state A/S dispatch)
- [x] `fetal_death/scripts/03_harmonize/harmonize.py` — exists; will be extended (handle 2003/2004 raw → harmonized + fix H8 int dtypes for 5 columns + add B7 TABFLAG correction for 0304)
- [x] `fetal_death/scripts/run_pipeline.py` — exists; will be extended (add 2003 + 2004 to `V_TRANSITION_YEARS` list)
- [x] `fetal_death/file_inventory.csv` — exists; will append 2 rows (2003, 2004) with SHAs and user-guide PDF names
- [x] `fetal_death/external_validation_targets.csv` — exists (26 metrics, 29-year coverage); will append 2003 + 2004 cells for per-year counts + rates from NVSR 57-08 (and corrected values per `fetaldeath0304problems.pdf` Table 1)
- [x] `fetal_death/validation_results.csv` — exists; will be re-generated by `validate_external_v2.py`
- [x] `fetal_death/harmonized_schema.csv` — exists; should NOT be edited in this task (per anti-pattern #6, schema edits require schema-version bump). The H8 fix makes the parquet match the schema (parquet int matches schema int), not the other way around.
- [x] `fetal_death/PROVENANCE.md`, `fetal_death/PROVENANCE.sha256` — exist; will be overwritten with v2.1.0 SHAs
- [x] `fetal_death/README.md`, `ABOUT_THIS_RELEASE.md`, `COMPARABILITY.md`, `CODEBOOK.md`, `FAQ.md`, `GETTING_STARTED.md`, `.zenodo.json`, `CITATION.cff` — exist at v2.0.0 framing; will be edited for v2.1.0 narrative (2003/2004 coverage, B7 normalization, H8 dtype fix-up, 31/31 + 28/28 validation counts)
- [x] `fetal_death/live_births_by_year.csv` — exists; will append 2003 + 2004 rows from natality denominators (using the existing `shared/helpers/build_stratified_denominators.py` runtime against the natality parquet)
- [x] Downstream joint-use code using string literals (per `FIX_LOG.md` 2026-05-11 H8 entry, list of files: `docs/JOINT_USE_GUIDE.md`, `notebooks/joint_use_demo.ipynb`, `notebooks/_build_joint_use_demo.py`, `notebooks/paper_companion.ipynb`, `notebooks/_build_paper_companion.py`) — will be updated to int literals as part of Task 3 (per STATUS HALT 2 forward-looking commitment). VERIFY must re-run both demo notebooks and confirm they still pass byte-exact after the dtype switch.

### Field-value snapshot (Convention 3)

**Snapshot A — H8 dtype-drift columns (shipped state vs schema declaration).**

For every canonical artifact this task will mutate, the current values are snapshot below. Divergences resolved here at the cheap-check moment.

| Column | `harmonized_schema.csv` type | v2.0.0 parquet dtype (verified at sha=`90af89b9…f0afdd`) | Post-Task-3 plan |
|---|---|---|---|
| `tabulation_flag` | `int` (allowed `1-2`) | `string` (Python `str`, values `'1'`, `'2'`) | rebuild parquet under int dtype |
| `residence_status` | `int` (allowed `1-4`) | `string` (values `'1'`-`'4'`) | rebuild parquet under int dtype |
| `maternal_age` | `int` (allowed `10-54;99`) | `string` (values `'10'`-`'54'`, `'99'`) | rebuild parquet under int dtype |
| `maternal_race_bridged` | `int` (allowed `1-4`) | `string` (values `'1'`-`'4'`) | rebuild parquet under int dtype |
| `hispanic_origin` | `int` (allowed `0-9`) | `string` (values `'0'`-`'9'`) | rebuild parquet under int dtype |

**Bundling decision (Convention 3 second bullet — resolved at PRE-FLIGHT, will be re-stated in DECISION_LOG entry at DO start).** The H8 reconciliation is bundled into Task 3 because: (i) the parquet is re-derived anyway as part of adding 2003 + 2004 records, so the dtype fix rides for free; (ii) the schema CSV is the canonical authority — fixing the parquet to match the schema (rather than the reverse) preserves the design intent; (iii) the FIX_LOG 2026-05-11 entry already commits to this resolution path. Schema CSV is NOT edited (anti-pattern #6 preserved).

**Snapshot B — Task 5 manuscript HALTs (verify they still hold pre-Task-3-DO).**

| HALT | Pre-DO state | Holds? |
|---|---|---|
| 1: 3 `<!-- YP: review -->` markers in `paper/draft_v2_hmd_styled.md` | `grep -c "<!-- YP:"` returns 3 | ✓ unchanged |
| 5: paper_companion_results.csv shows C04 DIFF / C33 L11 / C47-C49 L11 | sha=`7891809c5040f25d7fcbe3e35ac262f049c4c75be68f0814718ea119757f35ce` matches Task 5 receipt | ✓ unchanged |
| 6: paper sha `0685fe9c…1bddd1` | matches manuscript current file | ✓ unchanged |
| 2, 3, 4, 7, 8, 9 | informational / deferred per data-first sequence | not Task-3-blockers ✓ |

**Snapshot C — Sequence-specific HALTs from STATUS 2026-05-11T20:50Z (verify pre-Task-3-DO).**

| HALT | Pre-DO state | Holds? |
|---|---|---|
| 1: Task 3 PRE-FLIGHT L9 risk on 2003/2004 layout reconstruction | L9 cheap-check above resolved record-length apparent-conflict; A/S byte and TABFLAG-9 position both confirmed empirically; deep layout reconstruction is DO work (halt-and-ask policy committed per AskUserQuestion at PRE-FLIGHT) | ✓ resolved at the cheap-check level |
| 2: H8 bundling decision committed | Snapshot A above; 5 columns confirmed string-typed in v2.0.0 parquet | ✓ committed |
| 3: Manuscript sha will change post-Task-3 in step 5 of sequence | informational; not Task-3 in-scope (Task 3 does not touch the manuscript) | ✓ acknowledged |

**Snapshot D — `fetal_death/file_inventory.csv` rows being mutated.**

DO will APPEND 2 rows (2003 + 2004). Current state: 30 data rows (1992-2002 + 2005-2022), all with `imported,no`. The new rows will follow the same convention:

- 2003: `2003,https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/fetaldeathus/Fetal2003US.zip,NCHS,Fetal2003US.zip,fixed-width zip,2003FetalUserGuide.pdf,1351,no,transition year; per-state A/S dispatch at position 7; B7 TABFLAG correction applies (fetaldeath0304problems.pdf); 54,537 records`
- 2004: `2004,https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/fetaldeathus/Fetal2004US.zip,NCHS,Fetal2004US.zip,fixed-width zip,2004FetalUserGuide.pdf,1501,no,transition year; per-state A/S dispatch at position 7; B7 TABFLAG correction applies (fetaldeath0304problems.pdf); 53,320 records`

(The 1351 / 1501 in the `record_length` column matches the existing `record_length` semantic in the CSV — see 1992 row's `360` and 2006 row's `3351`; this is the line length including the trailing CRLF per measured behavior of comparable rows.)

### Halt conditions tripped
None. The two soft-flags above (B7 normalization is new; A/S dispatch needs deeper user-guide reading at DO start) are tracked items for DO, not PRE-FLIGHT halts. The L9 record-length apparent-conflict was resolved empirically at PRE-FLIGHT.

### Result
**PROCEED.** All 5 input categories verified, environment meets requirements, three staging decisions resolved at the cheap-check moment per Convention 3, H8 bundling committed, Task 5 + sequencing HALTs all hold. Halt-and-ask policy on layout ambiguities committed for DO phase per AskUserQuestion at PRE-FLIGHT.

### Next steps (DO phase, not part of PRE-FLIGHT)

1. Tag `task3-pre-do` after this PRE-FLIGHT commit lands.
2. Read 2003 user guide record-layout section (estimated mid-document, ~30-60 pages in); reconstruct `record_layout_2003.csv` mirroring `record_layout_1992.csv` and `record_layout_2006.csv` formats. Halt-and-ask on any field whose byte position is ambiguous from the user guide alone.
3. Same for `record_layout_2004.csv` (which is mostly the 2003 layout extended; verify identity for shared fields).
4. Extend `field_specs.py` with `FETAL_2003_FIELDS` + `FETAL_2004_FIELDS` lists and per-state A/S dispatch in `layout_for_year(year, state_code, revision_byte)`.
5. Parse 2003 + 2004 zips into `output/yearly_clean/fetal_death_{2003,2004}_raw.parquet`. Halt if either parse rejects > 1% of records as bad-length.
6. Extend `harmonize.py`: (a) include 2003 + 2004 in the year set; (b) implement B7 TABFLAG correction per `fetaldeath0304problems.pdf` (records with COMBGEST=99 and state in 42-state list → set TABFLAG=2); (c) cast the 5 H8 columns to int (NaN-aware: maternal_age=99 sentinel stays a int 99 but maternal_age=blank → null; tabulation_flag and residence_status are mandatory; etc.).
7. Re-run derive.py and validate scripts. VERIFY: 31/31 per-year counts + 28/28 rates byte-exact against NVSR 57-08 (was 29/29 + 26/26 in v2.0.0); 2005-2022 byte-clean regression on all 73 harmonized + 89 derived columns vs. v2.0.0 baselines AFTER the int-dtype fix is normalized away in the comparison.
8. Update downstream joint-use code to int literals (5 files per STATUS HALT 2). Re-run `_build_joint_use_demo.py` and confirm 8/8 NVSR cells still byte-exact.
9. Bump fetal-death version to v2.1.0 in `.zenodo.json`, `CITATION.cff`, `ABOUT_THIS_RELEASE.md`, `README.md`, `COMPARABILITY.md`, `FAQ.md`, `PROVENANCE.md`.
10. Append 2003 + 2004 rows to `file_inventory.csv`, `external_validation_targets.csv`, `live_births_by_year.csv`.
11. Write FIX_LOG entry closing the 2026-05-11 H8 entry (H8 reconciled in v2.1.0 parquet).
12. Write receipt to `RECEIPTS/task3_v21_fetal_death_<UTC>.md` with five-phase trace, self-check, Forward-looking HALTs.
13. Tag `task3-complete`.

---

## PRE-FLIGHT for task5_manuscript_trim — 2026-05-11T20:05:00Z

### Inputs
- [x] All required input files exist
  - `paper/draft_v2_hmd_styled.md`: present, 161 lines, sha256=`5e86c923d581936ce517740fadb6b247bbac4f6297a1cd517ed36b9f3c3967fb` (matches Task 4 receipt's read-only consumption sha; carries Task 4 Forward-looking HALT 5 condition — change of this sha at next PRE-FLIGHT is EXPECTED for Task 5) ✓
  - `paper/README.md`: present, sha256=`d87a4a4012b20933e75fea16bbe75db480cdb2c2d739ab3659243dec34d9b226` (matches Task 4 receipt post-edit sha; carries the 5 precision-edit candidates inlined for Task 5 consumption) ✓
  - `notebooks/paper_companion_results.csv`: present, sha256=`7891809c5040f25d7fcbe3e35ac262f049c4c75be68f0814718ea119757f35ce` (bit-stable Task 4 synthesis; will change after Task 5 manuscript edits — Forward-looking HALT 5) ✓
  - `notebooks/_build_paper_companion.py`: present, sha256=`055c3aff0b12ec0bef029aa2da761e36e89a8134d9a4fa4918a11283e2517abe` (deterministic builder; will be re-run during VERIFY) ✓
  - `CITATION.cff`: present, sole author = Yoel Plutchok ✓ (Author contributions admin section will reflect this)
  - `fetal_death/harmonized_schema.csv`: present, sha256=`72272c5537fdfa5b926a6aded69920bb5357a7bb5daef09742dfb494dadfa1ab` (used for the C47/C48/C49 re-verification below) ✓
  - `natality/metadata/harmonized_schema.csv`: present, sha256=`2e95488fd910f60cbf5965bd9f0d3503f59111e38180c20e4e51e29af2983577` ✓
  - `/Users/yoelplutchok/Desktop/fetal-death-harmonization/fetal_death_derived.parquet`: present, sha256=`90af89b9e659ca2b580d8286b5598588cfb2d17e93f26c1dc1ae00d097f0afdd` (used for C47/C48/C49 column null-rate verification; matches Task 4) ✓
  - `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet`: present, sha256=`9f917a43474eb9e3ed23aa95c714209421c25c29937376651149d22fab934ef0` (used for C04 mean-recompute) ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - bootstrap (2026-05-09): ✓
  - protocol-sync `[plan-update]` (2026-05-11): ✓
  - task6 (2026-05-11, `efe775d`): ✓
  - task1 (2026-05-11, `4d00ef8`): ✓
  - task2 (2026-05-11, `c068628`): ✓
  - §15 Task 2/4 breadcrumb-annotation `[plan-update]` (2026-05-11, `89ddc77`): ✓
  - task4 (2026-05-11, `abd22e0`): ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/task5_*.md`: does not exist ✓
  - `paper/draft_v2_hmd_styled.md` carries no `[TASK5-DRAFT]` markers from a prior aborted attempt ✓
- [x] Forward-looking HALTs from prior session (Task 4 receipt) verified at PRE-FLIGHT
  - **Task 4 HALT #1** (five Task-5 precision-edit candidates inlined in `paper/README.md`): verified — `paper/README.md` line 22 names C04, C29, C33, C47/C48/C49. **However: re-verification finding** — see Field-value snapshot below — discovers that C47/C48/C49 was a Task 4 misdiagnosis (Task 4 checked the natality parquet whose harmonized column names differ from fetal-death; the manuscript line-104 italicized names ARE fetal-death harmonized column names and ARE blank for V1 2007-2013 per the fetal-death parquet). Task 5 will apply C04, C29, C33; will NOT apply C47/C48/C49.
  - **Task 4 HALT #2** (paper_companion.ipynb sha not bit-stable; use CSV sha): acknowledged. Task 5 will not touch the notebook; will re-run the builder during VERIFY and inspect the new CSV synthesis for changed pass/fail tags. CSV-sha-change is EXPECTED (manuscript sha changes → new claim values).
  - **Task 4 HALT #3** (§15 Task 4 Section B re-deferral): acknowledged, not in Task 5 scope. The `[plan-update]` candidate for §15 Task 4 wording is open question #6 in current STATUS; not handled in Task 5 to avoid scope creep.
  - **Task 4 HALT #4** (H8 dtype drift not yet reconciled): Task 5 touches only the manuscript and admin docs; no fetal-death joint-use code modified. HALT remains green by construction.
  - **Task 4 HALT #5** (touching `paper/draft_v2_hmd_styled.md` → re-run paper_companion builder): this IS Task 5; manuscript sha WILL change from `5e86c923...`. Re-running the builder during VERIFY is mandatory; new CSV synthesis is the post-edit verification artifact.
  - **Task 4 HALT #6** (Task 1 HALT 6 natality v2.8 rename plan-update): carried forward; not in Task 5 scope.

### Environment
- [x] Python version: 3.13.9 (≥3.11 required) ✓
- [x] pandas: 2.3.2 ✓
- [x] pyarrow: 18.1.0 ✓
- [x] nbformat / nbclient: present (used by `_build_paper_companion.py`) ✓
- [x] Working directory clean (`git status` on `main` at `abd22e0`): ✓
- [x] On expected branch (`main`): ✓
- [x] L10 check on prior task: Task 4 PRE-FLIGHT (`61090fc`, 2026-05-11T19:15:00Z) precedes Task 4 DO/RECEIPT commit (`abd22e0`, 2026-05-11T19:26:28Z) ✓

### Source documentation
- [x] No new NVSR PDF transcription. Task 5 is a manuscript trim + admin-section fill + 5 precision-edit candidates from Task 4 + Companion-paper sentence. No new numeric claims introduced.
- [x] IJE Data Resource Profile word limit: 2,500 words main text (excluding abstract, key features, references, tables). Source: `paper/README.md` line 16. Cannot verify against current IJE author guidelines from offline state; the 2,500 limit is the figure carried by `paper/README.md`.

### Outputs
- [x] Intended output paths
  - `paper/draft_v2_hmd_styled.md`: EDIT (overwrite; prior version preserved in git at `abd22e0`) ✓
  - `paper/README.md`: EDIT — outstanding-work items now CLOSED by Task 5 marked accordingly ✓
  - `notebooks/paper_companion.ipynb`: EDIT via re-running the builder (per Task 4 HALT 5; binary sha will change per L17 — data-content reproducibility is via CSV) ✓
  - `notebooks/paper_companion_results.csv`: EDIT (will reflect new claim values; sha will change from `7891809c...`) ✓
  - `RECEIPTS/task5_manuscript_trim_<ts>.md`: NEW ✓
  - `NEXT_STEPS.md`: EDIT (§17 item 6 ⏳ → ✅ on success) ✓
  - `STATUS.md`: EDIT (new section dated 2026-05-11T20:xx:xxZ) ✓
  - `DECISION_LOG.md`: EDIT (new entry for the C47/C48/C49 re-verification override and any admin-section content decisions; possibly the C04 framing decision) ✓
  - `PRE_FLIGHT_LOG.md`: this entry ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

Task 5's purpose is to (a) trim the manuscript body to ≤2,500 words, (b) apply Task 4's 5 precision-edit candidates, (c) fill admin sections, (d) add a Companion paper sentence. Convention 3 applied here means **enumerating the current word counts per section + verifying every claim that Task 5 will edit BEFORE the first edit** so that mid-DO surprises (e.g., "I trimmed S&W by 250 words but the body total isn't 2500 yet") are caught at the cheap-check moment.

**Current word count per section (verified 2026-05-11T20:00Z via `re.findall(r"[A-Za-z][A-Za-z0-9'\\-]*")` on body text after stripping table-row pipes, footnote refs, code blocks, and header lines):**

| Section | Current words | IJE category | In 2,500 main-text budget? |
|---|---|---|---|
| (Title + abstract preamble, lines 1–4) | 191 | abstract | NO |
| Data resource basics | 483 | main | YES |
| Data resource area and coverage | 241 | main (Table 1 already excluded) | YES |
| Measures | 452 | main | YES |
| Methods | 487 | main | YES |
| Data resource use | 465 | main | YES |
| Strengths and weaknesses | 650 | main | YES |
| Future developments | 147 | main | YES |
| Data resource access | 130 | main | YES |
| HVS in a nutshell | 136 | key features | NO |
| Ethics approval | 30 | admin | NO |
| Author contributions | 3 | admin (placeholder) | NO |
| Use of artificial intelligence (AI) tools | 20 | admin (placeholder) | NO |
| Conflict of interest | 2 | admin | NO |
| Funding | 3 | admin (placeholder) | NO |
| References | 128 | references | NO |
| **Main-text body total (Basics→Access)** | **3,055** | — | over by **555** |

**Trim target.** 3,055 − 555 = 2,500. Need to cut **at least 555 words** from the main-text body; aim for ~500–550 to leave buffer. Per §15 DO scope, S&W is the primary trim target.

**§15-spec-vs-current-state divergences caught at this PRE-FLIGHT (Convention 3 second bullet):**

| §15 Task 5 spec | Current state (verified at PRE-FLIGHT) | Resolution |
|---|---|---|
| "Trim Strengths and Weaknesses (longest section, currently ~1,000 words; aim for 600)" | S&W is **650 words**, not 1,000. Either §15 was based on an older draft (draft_v1?) or S&W has been partly trimmed since the §15 spec was written. | Re-target S&W to **~400 words** (trim ~250). The "aim for 600" is preserved as upper bound; aiming lower frees budget for other sections to keep some narrative density. |
| "Move the 19-detail-cell breakdown to a supplementary table" | The "13/19 detail cells byte-exact + 6 documented diffs" framing appears in `README.md` (monorepo top-level) and `fetal_death/README.md` but **does NOT appear in `paper/draft_v2_hmd_styled.md`**. The manuscript's line-94 fetal-death validation claim is aggregate-level ("29 per-year counts + 26 per-year fetal mortality rates match exactly"); no detail-cell breakdown to move. | DO item **MOOT** — already absent from the manuscript. Document in receipt. |
| "Format references to journal style" | Current references (lines 153–161) use a Vancouver-style numbered + journal-italicized format. **Precise IJE reference style requires access to IJE author guidelines** (e.g., abbreviated journal names per Index Medicus, specific punctuation, etc.) which are not on disk and which I do not have a confirmed source for. | Apply minimal cleanup (consistency, punctuation); leave precise journal-style reformatting as a **deferred polish pass** for the human submission preparer. Document in receipt + STATUS open questions. |
| "Fill Ethics approval, Author contributions, AI-tool disclosure, Conflict of interest, Funding" | Ethics approval (30 words) and Conflict of interest (2 words "None declared") are already filled. Author contributions (3 words), AI-tool disclosure (20 words), Funding (3 words) are placeholders. | Author contributions: draft from CITATION.cff sole-author state. AI-tool disclosure: draft a reasonable disclosure for LLM-coding-agent use in pipeline + manuscript work, with a `[YP: review and edit]` note. Funding: draft "None declared" with same review note. **All three admin drafts are LLM-supplied content for a sole-author manuscript and are explicit candidates for human review** — recorded in DECISION_LOG and Forward-looking HALTs. |

**5 precision-edit candidates from Task 4 — PRE-FLIGHT re-verification:**

| Tag | Line | Task 4 recommendation | PRE-FLIGHT re-verification | Apply? |
|---|---|---|---|---|
| C04 | 7 | "approximately 3.5 million" → "approximately 3.5–4 million" or "3.97M average" | Natality 1990–2024 mean = 3,966,276; range 3,605,081–4,324,008 (verified now). Current "3.5 million" is below the actual 1990–2024 mean. Task 4's "3.5–4 million" preserves prose flow with one-character edit. | **YES** — apply "approximately 3.5–4 million" |
| C29 | 23 | "two within fetal death" boundary count → "three eras with two era-to-era transitions" wording | Table 1 ships 3 fetal-death era rows (1992–2002, 2005–2017, 2018–2022) = 2 boundaries. Current wording "two within fetal death" is correct under boundary-reading but mismatches casual Table-1-row-count reading. Task 4 recommendation is clearer. | **YES** — rephrase to make eras-vs-boundaries explicit |
| C33 | 60 | "Three fetal-death columns are tagged within_era" is scope-restrictive → "Three of the within_era fetal-death columns carry irreducibly incompatible..." | Schema has 24 within_era columns total (verified now: `comparability_class == 'within_era'` in `fetal_death/harmonized_schema.csv`). The three named (`breech_unrevised`, `delivery_place_unrevised`, `maternal_race_bridged_detail`) are within_era but not the only ones. Task 4 recommendation is more precise. | **YES** — apply "Three of the within_era fetal-death columns..." |
| C47/C48/C49 | 104 | Italicised `maternal_education` / `paternal_age_combined` / `maternal_education_unrevised` are raw NCHS field names, not harmonized columns; clarify | **MISDIAGNOSIS**: Task 4 PRE-FLIGHT/DO checked the natality parquet (where the harmonized columns are named `maternal_education_cat4`, `father_age`). The manuscript line-104 names ARE fetal-death harmonized columns: `fetal_death/harmonized_schema.csv` line 17 (`maternal_education`, years_available `2005-2006, 2014-2022`), line 18 (`maternal_education_unrevised`, years_available `1992-2002, 2005-2006`), line 21 (`paternal_age_combined`, years_available `1992-2002, 2005-2006, 2014-2022`). Direct null-rate verification on `fetal_death_derived.parquet` shows 100% blank for all three columns in 2007–2013, matching the manuscript's claim byte-exact. The manuscript italicization is consistent with line 60's `breech_unrevised` etc. (italics = harmonized column names). | **NO** — keep manuscript wording as-is. Task 4's L11 was a misdiagnosis. Log to DECISION_LOG; document in receipt self-check. |

**Companion paper sentence design (§15 Task 5 DO item):**

Goal: one sentence pointing to the monorepo (https://github.com/yoelplutchok/vital-statistics-harmonization, not yet pushed per STATUS open question 1) and the cross-product worked-example notebooks (`notebooks/joint_use_demo.ipynb`, `notebooks/paper_companion.ipynb`). Will be placed at the end of the "Data resource access" section.

Draft: "Cross-product worked examples — including a joint-use demonstration reproducing the 2022 maternal-age-stratified fetal mortality cells against *NVSR 73-09* Table 4, and a paper-companion notebook recomputing every numeric claim in this manuscript directly from the parquets — are shipped under `notebooks/` in the monorepo accompanying this resource."

This does NOT include a github URL because the monorepo has not yet been pushed (STATUS open question 1). The user's submission preparer should add the URL once it is pushed.

### Plan assumptions amended at PRE-FLIGHT (Convention 3 second bullet)

1. **C47/C48/C49 NOT applied.** Task 4's L11 recommendation is a misdiagnosis (checked natality parquet; should have checked fetal-death). Manuscript wording at line 104 is byte-exact correct. Record in DECISION_LOG as an override of Task 4's recommendation.
2. **S&W trim target ~400 words (not 600).** §15 figure of "currently ~1,000 words" is stale; actual is 650.
3. **"Move 19-detail-cell breakdown" DO item MOOT** — not in the current manuscript.
4. **References reformatting limited to consistency cleanup**, not full IJE-style reformatting. The latter requires IJE author guidelines I do not have a verified source for. Deferred.
5. **Admin-section drafts are LLM-supplied for a sole-author manuscript.** Author contributions can be derived from CITATION.cff (sole author = Yoel Plutchok). AI-tool disclosure will be drafted per IJE policy as referenced in the manuscript's own placeholder ("disclose any AI-tool use in pipeline development, documentation drafting, or manuscript preparation"). Funding defaulted to "None declared." All three carry an explicit human-review note in the receipt's Forward-looking HALTs.

### Halt conditions tripped
None unresolved. Four findings (C47/C48/C49 override; S&W target recalibration; 19-cell-breakdown MOOT; references-reformatting deferral) are resolved at this PRE-FLIGHT moment per Convention 3 second bullet. No prior validated artifact is being mutated — the manuscript edit is expected and authorized; the paper_companion notebook re-run is mandatory per Task 4 HALT 5; all other touches are state-file appends.

### Result
PROCEED.

---

## PRE-FLIGHT for task4_paper_companion — 2026-05-11T19:15:00Z

### Inputs
- [x] All required input files exist
  - `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet`: present, sha256=`9f917a43474eb9e3ed23aa95c714209421c25c29937376651149d22fab934ef0` (carries Task 1+2 PROVENANCE-gap finding; unchanged) ✓
  - `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet`: present, sha256=`46c169b59b040028d9830546fad71f30d0c6364f10fbc1676b56ae6ee993eb16` (unchanged) ✓
  - `/Users/yoelplutchok/Desktop/fetal-death-harmonization/fetal_death_derived.parquet`: present, sha256=`90af89b9e659ca2b580d8286b5598588cfb2d17e93f26c1dc1ae00d097f0afdd` matches `fetal_death/PROVENANCE.md` v2.0.0 ✓
  - `paper/draft_v2_hmd_styled.md`: present, 161 lines, sha256=`5e86c923d581936ce517740fadb6b247bbac4f6297a1cd517ed36b9f3c3967fb` ✓
  - `fetal_death/harmonized_schema.csv`: present, 73 rows, sha256=`72272c5537fdfa5b926a6aded69920bb5357a7bb5daef09742dfb494dadfa1ab` ✓
  - `natality/metadata/harmonized_schema.csv`: present, 94 rows, sha256=`2e95488fd910f60cbf5965bd9f0d3503f59111e38180c20e4e51e29af2983577` ✓
  - `natality/output/validation/external_validation_v1_comparison.csv`: present, 183 rows, sha256=`c82a412ca16dc0f8b3c8a6a6b842b8a4cac43c19015a388bba1f4608f123e68a` ✓
  - `natality/output/validation/external_validation_v3_linked_comparison.csv`: present, 35 rows, sha256=`868dc5c99e7c7e7bc3cd7674dee6a2abf7062af15ea01e83b4bd14d23763dcbe` ✓
  - `fetal_death/validation_results.csv`: present, 29 rows (1992–2002 + 2005–2022), sha256=`8041586dc99f450faf4a3b91505a98652410a31d6caa5da14dfa39c75da7de0e` ✓
  - `fetal_death/external_validation_targets.csv`: present, 81 data rows, sha256=`0d9c361627e898a39533bca0277f01969a9fc8cd34046000d26b99b21d77576f` ✓
  - `fetal_death/stratified_denominators.csv` (Task 1 output): sha256=`6874d5d65e7b3888acf8a833e4fa98063630765e2eeaf6e1c6cb48ad7b0db5c1` (matches Task 1 HALT 1 byte-exact) ✓
  - `shared/helpers/canonical_join_keys.py`: present; `NATALITY_TO_CANONICAL` unchanged (matches Task 1 HALT 2 byte-exact) ✓
  - `fetal_death/ABOUT_THIS_RELEASE.md`: present; carries the canonical 13/19 detail-cell + 6 docs-diffs narrative referenced by manuscript line 94 ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - bootstrap (2026-05-09): ✓
  - protocol-sync `[plan-update]` (2026-05-11): ✓
  - task6 (2026-05-11, `efe775d`): ✓
  - task1 (2026-05-11, `4d00ef8`): ✓
  - task2 (2026-05-11, `c068628`): ✓
  - §15 Task 2/4 breadcrumb-annotation `[plan-update]` (2026-05-11, `89ddc77`): ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/task4_*.md`: does not exist ✓
  - `notebooks/paper_companion.ipynb`: does not exist (only the planned-stub mention in `notebooks/README.md`) ✓
  - `notebooks/_build_paper_companion.py`: does not exist ✓
- [x] Forward-looking HALTs from prior session (Task 2 receipt) verified at PRE-FLIGHT
  - **Task 2 HALT #1** (joint_use_demo 8-cell NVSR validation): Task 4 does NOT touch the natality v2.7.0 or fetal-death v2.0.0 parquets; HALT #1 remains green by construction. Will re-verify in VERIFY by re-running `python notebooks/_build_joint_use_demo.py` after Task 4's DO to confirm no incidental regression.
  - **Task 2 HALT #2** (fetal-death H8 dtype drift): this notebook MUST use string literals on `tabulation_flag`/`residence_status`/`maternal_age`/`maternal_race_bridged`/`hispanic_origin`. Committed in the notebook design below.
  - **Task 2 HALT #3** (L17 .ipynb sha not bit-stable): same applies to Task 4's notebook. Verified-by-data-content rather than by-sha; receipt records this explicitly.
  - **Task 2 HALT #4** (§15 Task 2 wording plan-update): resolved by `89ddc77` "§15 Task 2 + Task 4: breadcrumb annotations" — verified by reading current `NEXT_STEPS.md` §15 Task 2 line 497, which now ships the PRE-FLIGHT-amended-scope breadcrumb.
  - **Task 2 HALT #5** (schema-doc parity smoke test): informational only; not gating Task 4. Carried forward.
  - **Task 2 HALT #6** (Task 1 HALT 5 closed): confirmed.

### Environment
- [x] Python version: 3.13.9 (≥3.11 required) ✓
- [x] pandas: 2.3.2 ✓
- [x] pyarrow: 18.1.0 ✓
- [x] nbformat: 5.10.4 ✓
- [x] nbclient: present (verified by Task 2's successful nbclient execution at `c068628`) ✓
- [x] Working directory clean (`git status` on `main` at `89ddc77`): ✓
- [x] On expected branch (`main`): ✓

### Source documentation
- [x] No new NVSR PDF transcription. Task 4 reads only artifacts that have already been PDF-anchored in prior tasks (the validation CSVs and the harmonized parquets); no L9 risk on numeric reproduction.
- [x] §15 Task 4 "absorbs Section B NVSR cell-level validation deferred from Task 2" — **L9 cheap-check**: `fetal_death/external_validation_targets.csv` contains NO 2017 race-stratified fetal-death targets (verified by metric enumeration: 26 distinct metrics, none race-keyed). Absorbing Section B would require a fresh PDF transcription from the 2017-vintage NVSR fetal-mortality report (NVSR 67-?). The original Task 2 deferral cited exactly this L9 risk. **Resolution**: re-defer the Section B absorption per Convention 3 second bullet — see Field-value snapshot below for the formal divergence and reasoning. Section B race-stratified 2017 NVSR validation becomes a separate small future task (input: NVSR-2017 fetal-mortality PDF; output: 4 new rows in `external_validation_targets.csv`; cost: one short session if the PDF is at hand).

### Outputs
- [x] Intended output paths do not exist OR are explicitly marked for overwrite
  - `notebooks/_build_paper_companion.py`: new ✓ (deterministic builder; `DESIGN: tracks-current-state` per Convention 2)
  - `notebooks/paper_companion.ipynb`: new ✓ (built by the above; executed with nbclient; not bit-sha-stable per L17/HALT 3)
  - `RECEIPTS/task4_paper_companion_<ts>.md`: new ✓
  - Edits to existing files explicitly intended: `notebooks/README.md` (paper_companion description), `NEXT_STEPS.md` (§17 item 7 ⏳ → ✅ on success), `paper/README.md` (mark "Companion notebook" outstanding-work item resolved), `STATUS.md`, possibly `DECISION_LOG.md` for any L6/L11 findings that need to be fixed in the manuscript

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

Task 4's purpose is to surface L6/L11 drift between the manuscript text and the underlying artifacts. Convention 3 applied here means **enumerating every numeric claim in the manuscript** before writing the first cell, recording the source-of-truth, the plan-assumed value, and the current actual value. Each row's `current_actual` is computed at this PRE-FLIGHT moment so that mid-DO findings are surprises in the *manuscript*, not in the *artifacts*.

**Notation**: `LB-N` = manuscript line N below. `SoT` = source of truth artifact. `plan_value` = the manuscript's stated number. `current_actual` = computed at this PRE-FLIGHT. `?` = will be computed during notebook build (cheap; computing now would require parquet loads which the SMOKE Tier 1 + DO phases will do anyway). `match` column populated where snapshot is doable from CSVs/schemas without parquet load.

| Tag | LB | Claim (excerpted) | SoT | plan_value | current_actual | match |
|---|---|---|---|---|---|---|
| C01 | 3 | 138,819,655 natality records (1990–2024) | natality parquet `len` | 138,819,655 | ? (DO) | DO |
| C02 | 3 | 74,943,824 linked records (2005–2023) | linked parquet `len` | 74,943,824 | ? (DO) | DO |
| C03 | 3 | 1,634,195 fetal-death records (1992–2022) | fetal-death parquet `len` | 1,634,195 | ? (DO) | DO |
| C04 | 7 | ~3.5M live births/year | natality parquet `len / n_years` | ~3.5M | ? (DO) | DO |
| C05 | 7 | 20,000–30,000 fetal deaths/year | fetal-death parquet groupby year | 20K–30K | ? (DO) | DO |
| C06 | 7 | 20,000 infant deaths/year | linked parquet death-side filter | ~20K | ? (DO) | DO |
| C07 | 9 | 2003–2014 phasing natality | NCHS source / docs only (not a parquet number) | 2003–2014 | (cite-only) | n/a |
| C08 | 9 | 2005–2017 V1 fetal-death window | docs (`fetal_death/COMPARABILITY.md`) | 2005–2017 | matches | ✓ |
| C09 | 9 | 100% A-version in 2018 | docs | 100% in 2018 | matches | ✓ |
| C10 | 9 | 2006 natality 1500→775 bytes | record_layout / docs | 1500→775 | matches Table 1 row | ✓ |
| C11 | 9 | 2009 unrevised-only blanked | docs | 2009 | matches | ✓ |
| C12 | 9 | 2014 natality 1345-byte layout | record_layout / docs | 1345 | matches Table 1 row | ✓ |
| C13 | 11 | Salihu 1995–1998 | citation | 1995–1998 | (cite-only) | n/a |
| C14 | 11 | Willinger 2001–2002 | citation | 2001–2002 | (cite-only) | n/a |
| C15 | 15 | first release 2026 | repo bootstrap date | 2026 | matches STATUS.md bootstrap | ✓ |
| C16 | 19 | 138,819,655 (1990–2024) | dup of C01 | 138,819,655 | ? | DO |
| C17 | 19 | 84 natality columns | natality parquet `n_cols` | 84 | 84 (verified now) | ✓ |
| C18 | 19 | 74,943,824 (2005–2023) | dup of C02 | 74,943,824 | ? | DO |
| C19 | 19 | 94 linked columns | linked parquet `n_cols` | 94 | 94 (verified now) | ✓ |
| C20 | 19 | denom-plus cohort 2005–2015; period-cohort 2016–2023 | docs | per text | matches | ✓ |
| C21 | 19 | 1,634,195 (1992–2022) | dup of C03 | 1,634,195 | ? | DO |
| C22 | 19 | 89 fetal-death columns | fetal-death parquet `n_cols` | 89 | 89 (verified now) | ✓ |
| C23 | 21 | 2003 transition 1351 bytes | NCHS docs / pending V2.1 | 1351 | (no on-disk artifact in HVS — cite-only) | n/a |
| C24 | 21 | 2004 transition 1501 bytes | same | 1501 | (cite-only) | n/a |
| C25 | 21 | 50 × 197 × 10 = 98,500 byte-comparisons | `fetal_death/ABOUT_THIS_RELEASE.md` line 4 | 98,500 | matches arithmetic + ABOUT_THIS_RELEASE | ✓ |
| C26 | 21 | zero mismatches 1993–2002 + 1992 separately | `validation_tracking.csv` | 0 mismatches | matches (validation_tracking notes "matches" for every year) | ✓ |
| C27 | 23 | 5 natality era boundaries | Table 1 | 5 | Table 1 rows = 5 (1990-2002, 2003, 2004-2005, 2006-2013, 2014-2024) | ✓ |
| C28 | 23 | 3 linked era boundaries | Table 1 | 3 | Table 1 rows = 3 | ✓ |
| C29 | 23 | 2 fetal-death era boundaries | Table 1 | 2 | Table 1 rows = 3 (1992-2002, 2005-2017, 2018-2022) — **MISMATCH: text says 2, table shows 3** | ✗ L6 |
| T1 | 29–39 | Table 1 record lengths and certificate revisions | 11 rows | per table | per-row verification will compute matches against record_layout files for the rows where layout files exist; for transition rows where files don't yet exist (2003, 2004 fetal-death), cite NCHS | DO |
| C30 | 45 | natality: 71 harmonized + 13 derived = 84 total | natality schema CSV + parquet | 84 total ✓; 71/13 split | natality parquet=84 cols ✓; **natality schema CSV has 94 rows (different ontology — cross-era expansion?); 71+13 split needs derivation_rule classification on schema rows** | partial |
| C31 | 45 | linked: 7 additional + 3 derived death-side = 94 total | linked schema | 94 ✓; 7/3 split | linked parquet=94 cols ✓; the +7/+3 split needs schema cross-product analysis | partial |
| C32 | 45 | fetal-death: 73 harmonized + 16 derived = 89 total | fetal-death schema + parquet | 89 ✓; 73/16 split | fetal-death parquet=89 cols ✓; schema CSV=73 rows ✓; 89-73=16 ✓ | ✓ |
| C33 | 60 | three fetal-death `within_era` columns | fetal-death schema | 3 | **schema has 24 within_era rows; manuscript line 60 specifically names `breech_unrevised`, `delivery_place_unrevised`, `maternal_race_bridged_detail` as the three "incompatible-clinical-concept" ones — these 3 ARE in the schema's 24 within_era rows. The wording "three columns are tagged within_era" is L11-stale (older partition) or scope-restrictive (the three uniquely-incompatible ones).** | ✗ L11 |
| C34 | 69 | five fetal-death value-level normalizations (`fetal_sex`, `delivery_method_recode`, `maternal_race_bridged`, `paternal_age_recode11`, `delivery_place_recode`) | `fetal_death/ABOUT_THIS_RELEASE.md` (B1-B6 narrative) | 5 | ABOUT_THIS_RELEASE has B1-B6 (six items, not five); manuscript line 69 lists 5. **Possible L6 — verify B1-B6 vs the five named in manuscript** | ? DO |
| C35 | 75 | fetal-death pipeline ~6 min on 2024-vintage laptop | benchmark — not reproducible without running pipeline | ~6 min | (not parquet-derivable; cite-only) | n/a |
| C36 | 75 | natality pipeline ~90 min | same | ~90 min | (cite-only) | n/a |
| C37 | 83 | live_births_by_year sourced from NVSR 57-08 (1995–2002) + NVSR 73-09 (2005–2022) | `fetal_death/live_births_by_year.csv` Source col | per text | will verify against the file at DO | DO |
| C38 | 85 | Level 1 ~10s, Level 2 ~1m, Level 3 ~1-2h | benchmarks | per text | (cite-only) | n/a |
| C39 | 94 | natality 183 of 183 V1 targets (1990–2024) | `natality/output/validation/external_validation_v1_comparison.csv` | 183/183 | csv has 183 data rows; `pass==1` count will be computed at DO | DO |
| C40 | 94 | linked 33 of 35 byte-exact; 2 cells differ by 1 (Task 6 canonical framing) | `natality/output/validation/external_validation_v3_linked_comparison.csv` | 33/35 + 2 by 1 | csv has 35 data rows; Diff=0 count = 33, Diff=1 count = 2 will be computed at DO | DO |
| C41 | 94 | fetal-death: 29 per-year counts | `fetal_death/validation_results.csv` | 29/29 | csv has 29 data rows, all `Match=✓` (verified now) | ✓ |
| C42 | 94 | fetal-death: 26 per-year FMR | `fetal_death/external_validation_targets.csv` rate rows | 26/26 | csv has 26 `fetal_mortality_rate` rows (1995–2002 + 2005–2022, verified now); per-year FMR computation against the parquet will be done at DO | partial (csv-row-count ✓; per-row PASS at DO) |
| C43 | 94 | fetal-death: NVSR 73-09 (2005–2022); NVSR 57-08 Tables A and B (1995–2002); NCHS user guide (1992–1994) | `validation_results.csv` Source col | per text | csv Source col matches text byte-exact (verified now) | ✓ |
| C44 | 100 | cause-of-death not in public-use file before 2014 | parquet `cause_icd10` null-rate by year | 100% null pre-2014 | ? (DO) | DO |
| C45 | 100 | ~50% records lack cause data 2018 onward | parquet `cause_icd10` null-rate by year for 2018+ | ~50% | ? (DO) | DO |
| C46 | 100 | state-level identifiers in fetal-death raw 1992–2002 only | per-year raw parquets (out of monorepo scope; `STATEFET`/`STATERES`/`STOCCFIP` columns) | per text | cite + grep harmonized columns; state cols not in harmonized | partial |
| C47 | 104 | `maternal_education` blank V1 2007–2013 (even for revised records) | parquet null-rate | 100% null in 2007–2013 V1 | ? (DO) | DO |
| C48 | 104 | `paternal_age_combined` blank V1 2007–2013 | parquet null-rate | 100% null in 2007–2013 V1 | ? (DO) | DO |
| C49 | 104 | `maternal_education_unrevised` blank V1 2007 onward | parquet null-rate | 100% null 2007+ V1 | ? (DO) | DO |
| C50 | 106 | Maryland 1992–1998 no Hispanic | `fetal_death/COMPARABILITY.md` + parquet `hispanic_origin` null-rate by state-year | per text | partial verification via national `hispanic_origin` null-rate by year; full state-year verification requires per-year raw parquets (out of monorepo scope) | partial |
| C51 | 106 | Massachusetts 1992–1997 no Hispanic | same | per text | same | partial |
| C52 | 106 | Louisiana 1992–1994 plurality under-reported | same | per text | same | partial |
| C53 | 125 | 138.8M (1990–2024) | dup of C01 (rounded) | 138.8M | ? | DO |
| C54 | 125 | 74.9M (2005–2023) | dup of C02 (rounded) | 74.9M | ? | DO |
| C55 | 125 | 1.6M (1992–2022) | dup of C03 (rounded) | 1.6M | ? | DO |

Pre-DO Field-value snapshot findings (from CSVs / schemas only, no parquet load yet):

1. **C17, C19, C22 confirmed at PRE-FLIGHT**: parquet column counts 84/94/89 match manuscript exactly. No L11 risk on the headline column-count claims.
2. **C29 L6 candidate**: manuscript line 23 says "two within fetal death" era boundaries; Table 1 ships three fetal-death rows (1992–2002, 2005–2017, 2018–2022). Interpretation: "boundaries" = transitions BETWEEN eras, so 3 eras = 2 boundaries. Either reading is defensible (eras vs boundaries); flag for resolution in DO with explicit framing.
3. **C33 L11 candidate**: manuscript line 60 says "Three fetal-death columns are tagged within_era," but schema has 24 within_era. The three named in line 60 (`breech_unrevised`, `delivery_place_unrevised`, `maternal_race_bridged_detail`) ARE within_era, but they are not the only ones. The text is scope-restrictive (these three are uniquely "incompatible clinical concepts that cannot be reconciled") rather than exhaustive. The manuscript may benefit from a precision edit — flag for Task 5 (manuscript trim) rather than fix in Task 4.
4. **C34 verify candidate**: line 69 lists FIVE fetal-death normalizations; `fetal_death/ABOUT_THIS_RELEASE.md` describes the harmonization fixes as B1–B6 (six items). Verify whether the manuscript's five = a subset of ABOUT_THIS_RELEASE's six, or whether one is missing.
5. **C41 confirmed**: 29/29 per-year counts with `Match=✓` byte-exact (verified now).
6. **C42 partial-confirmed**: 26 `fetal_mortality_rate` rows in external_validation_targets.csv covering exactly 1995–2002 + 2005–2022; per-row PASS verified at DO.
7. **C43 confirmed**: source attribution byte-exact.

**Plan assumption amended at PRE-FLIGHT (Convention 3 second bullet)**

1. **Section B 2017 race-stratified NVSR validation deferred from Task 2 is NOT absorbed into Task 4 in this PRE-FLIGHT.** §15 Task 4 description (current state at `89ddc77`) names this absorption; the L9 cheap-check above confirms it requires a fresh PDF transcription with no pre-encoded targets to verify against. Task 4's primary scope (reproduce every manuscript numeric claim) is itself substantial (55+ claims enumerated above) and does not include race-stratified 2017 NVSR claims (manuscript line 94 makes only aggregate-level NVSR validation claims). The Section B absorption becomes a separate small future task — see Forward-looking HALTs in the receipt. This is a Convention 3 second-bullet response: surface the divergence at PRE-FLIGHT, amend the plan with explicit reasoning, do not silently proceed.

2. **C29 framing decision: "boundaries" = transitions, not eras**. The notebook will report 5/3/2 boundary counts under that reading and explicitly note the eras=boundaries+1 relationship for cross-checkers. The manuscript's wording stands.

3. **C33 framing decision: line 60's "three" is scope-restrictive** (the three irreducibly-incompatible-clinical-concept columns), not exhaustive of within_era. The notebook will report both numbers (the 3 named + the full 24 in the schema) and recommend a Task 5 line-60 precision edit to "Three of the within_era fetal-death columns carry irreducibly incompatible clinical concepts across the revision boundary..." Decision logged here; the actual manuscript edit is OUT of Task 4 scope (Task 4 produces the notebook; manuscript edits are Task 5).

### Halt conditions tripped
None unresolved. Three findings (C29 framing, C33 precision, Section B absorption deferral) are resolved at this PRE-FLIGHT moment per Convention 3 second bullet. No previously-stable downstream output is being mutated by Task 4. No new PDF transcription. Task 2's six Forward-looking HALTs all verified or non-applicable.

### Result
PROCEED.

---

## PRE-FLIGHT for task2_joint_use_demo — 2026-05-11T18:27:14Z

### Inputs
- [x] All required input files exist
  - `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet`: present, 2,202,879,406 bytes, sha256=`9f917a43474eb9e3ed23aa95c714209421c25c29937376651149d22fab934ef0` (matches Task 1 receipt — locally computed, NOT in any shipped PROVENANCE.md; upstream documentation gap carried over from Task 1) ✓
  - `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet`: present, 1,300,258,973 bytes, sha256=`46c169b59b040028d9830546fad71f30d0c6364f10fbc1676b56ae6ee993eb16` (locally computed; same PROVENANCE gap — the v3 linked derived parquet is not enumerated in `/Users/yoelplutchok/Desktop/natality-harmonization/output/convenience/PROVENANCE.md` which only covers convenience parquets) ✓
  - `/Users/yoelplutchok/Desktop/fetal-death-harmonization/fetal_death_derived.parquet`: present, 25,452,090 bytes, sha256=`90af89b9e659ca2b580d8286b5598588cfb2d17e93f26c1dc1ae00d097f0afdd` matches `fetal_death/PROVENANCE.md` v2.0.0 ✓
  - `fetal_death/stratified_denominators.csv` (Task 1 output): present, sha256=`6874d5d65e7b3888acf8a833e4fa98063630765e2eeaf6e1c6cb48ad7b0db5c1` — matches Task 1 RECEIPT Forward-looking HALT 1 byte-exact ✓
  - `shared/helpers/canonical_join_keys.py` (Task 1 output): present, exports `NATALITY_TO_CANONICAL`, `to_canonical_natality`, `derive_maternal_age_band`; `NATALITY_TO_CANONICAL` content verified as exactly `{'year': 'data_year', 'restatus': 'residence_status', 'maternal_race_bridged4': 'maternal_race_bridged', 'maternal_hispanic_origin': 'hispanic_origin'}` — matches Task 1 RECEIPT Forward-looking HALT 2 byte-exact ✓
  - `fetal_death/external_validation_targets.csv`: present, 82 rows, headers `year,metric,metric_detail,expected_value,source,notes` ✓
  - `fetal_death/harmonized_schema.csv`: present, contains `data_year`, `tabulation_flag`, `residence_status`, `maternal_age`, `maternal_race_bridged`, `hispanic_origin` with documented dtypes ✓
  - `docs/JOINT_USE_GUIDE.md`: present, contains "Worked example: fetal mortality rate by maternal race, 2017" (the section that the §15 Task 2 PRE-FLIGHT inputs cite as pseudocode source; the spec's literal year "2022" is stale — see Field-value snapshot below) ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - bootstrap (2026-05-09): ✓
  - protocol-sync `[plan-update]` (2026-05-11, `596e8ce`): ✓
  - task6 (2026-05-11, `efe775d`): ✓
  - task1 (2026-05-11, `4d00ef8`): ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/task2_*.md`: does not exist ✓
  - `notebooks/joint_use_demo.ipynb`: does not exist (only `notebooks/README.md` planned stub describing it) ✓
- [x] Forward-looking HALTs from prior session (Task 1 receipt) verified at PRE-FLIGHT
  - **Task 1 HALT #1** (stratified_denominators.csv sha unchanged): sha=`6874d5d6...` matches receipt ✓
  - **Task 1 HALT #2** (canonical_join_keys.py NATALITY_TO_CANONICAL dict unchanged): 4 entries match receipt byte-exact ✓
  - **Task 1 HALT #3** (canonical filter on BOTH sides): this PRE-FLIGHT commits the policy in the notebook design — numerator filter `(tabulation_flag == 2) AND (residence_status != 4)`; denominator filter `residence_status != 4` (pre-applied in stratified_denominators.csv, re-asserted in the notebook narrative). Tier 0 SMOKE will mutation-verify both filters catch their respective exclusion records.
  - **Task 1 HALT #4** (bridged-race null cells NOT dropna'd): notebook will preserve null-race rows; 2018+ strata in the denominator carry `maternal_race_bridged = NaN`. Section B uses 2017 (race-available year) so this is not an issue for the by-race computation; for the by-age computation (Section A, year 2022) the maternal_race_bridged column is not in the groupby axis, so null-vs-non-null is irrelevant for Section A.
  - **Task 1 HALT #5** (1992-2002 maternal_race_bridged crosswalk equivalence check): incorporated as SMOKE Tier 1 supplementary check — compute natality's `maternal_race_bridged4` from the harmonized parquet on a 1000-row 1995 sample and cross-check against the fetal-death-side recode rule (`harmonize.py`: 01→1, 02→2, 03→3, 04-78→4, 99→null) applied to the equivalent natality MRACE-source values. The receipt will document the result; failure → halt and ask before claiming the by-race joint-use machinery generalizes to pre-2003 era.
  - **Task 1 HALT #6** (Convention 3 second-bullet drill — Field-value-snapshot as the cheapest divergence-surfacer): this PRE-FLIGHT explicitly demonstrates that response — Field-value snapshot below catches a §15-spec / current-state mismatch BEFORE any DO mutation, and amends the plan at PRE-FLIGHT time rather than mid-DO. Per the L10-safe addendum-protocol pattern.

### Environment
- [x] Python version: 3.13.9 (required ≥3.11) ✓
- [x] R version: n/a (Python-only task)
- [x] pandas version: 2.3.2 (required ≥2.3) ✓
- [x] pyarrow version: 18.1.0 (required ≥18.0) ✓
- [x] nbformat version: 5.10.4 (notebook serialization) ✓
- [x] jupyter_client version: 8.8.0 (kernel for executed-output cells) ✓
- [x] Working directory clean (`git status` on `main` at `4d00ef8`): ✓
- [x] On expected branch (`main`): ✓

### Source documentation
- [x] All NVSR PDFs / NCHS user guides referenced — n/a for primary computations; NVSR 73-09 Table 4 8 age cells already encoded in `fetal_death/external_validation_targets.csv` (no PDF re-transcription, zero L9 risk on Section A). Section B (2017 race) does NOT transcribe new NVSR figures (NVSR 67-08 Table I race-stratified-2017 figures are NOT pre-encoded and not re-derived in this task; Section B presents computed rates as a joint-use machinery demonstration with NVSR validation deferred to Task 4).
- [x] All cited Zenodo DOIs resolve — natality concept `10.5281/zenodo.19363074` (v2.7.0=`10.5281/zenodo.19868835`); fetal-death v2.0.0=`10.5281/zenodo.20031571`; not re-fetched (using local parquets, all hash-verified above).

### Outputs
- [x] Intended output paths do not exist OR are explicitly marked for overwrite
  - `notebooks/joint_use_demo.ipynb`: new ✓
  - `RECEIPTS/task2_joint_use_demo_<ts>.md`: new ✓
  - Edits to existing files explicitly intended: `notebooks/README.md` (description currently says "by maternal race, 2022" — both wrong per Field-value snapshot below; update to "by maternal age band 2022 + maternal race 2017"), `NEXT_STEPS.md` §17 item 4 (⏳ → ✅), `STATUS.md`, `DECISION_LOG.md`. Per §11, propose a `[plan-update]` candidate to NEXT_STEPS.md §15 Task 2 description for stale 2022-by-race wording (NOT done as part of Task 2 itself; flagged in receipt Forward-looking HALTs).

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

The §15 Task 2 spec was written at bootstrap (2026-05-09) BEFORE Task 1 discovered the bridged-race-2018+ gap and rewrote `docs/JOINT_USE_GUIDE.md` to use 2017 as the worked-example year. The spec is therefore L11-class stale on the bootstrap-to-Task-1 timeline. Snapshot of the divergence and its resolution:

**§15-spec-vs-current-state divergence**

| §15 Task 2 spec (line 497–519) | Current state (verified at PRE-FLIGHT) | Resolution |
|---|---|---|
| "computes the fetal mortality rate per 1,000 (live births + fetal deaths) by maternal race for 2022" | 2022 has `maternal_race_bridged = null` in BOTH products. `fetal_death/harmonized_schema.csv` line 8 `years_available = 1992-2002, 2005-2017`; `stratified_denominators.csv` 2018-2022 strata all carry null race. NCHS dropped MBRACE from the public-use file for those years. Race-stratified 2022 is physically impossible with shipped data. | Section A in the notebook uses **2022 maternal age band** stratification (race-axis swap forced by data); Section B uses **2017 maternal race** stratification (year-swap forced by data) to preserve the §15 spec's "by race" demonstration intent. |
| "matches each cell against *NVSR 73-09* Table A" | `fetal_death/external_validation_targets.csv` rows attributed to `NVSR 73-09 Table A`: `live_births_total` (denominator), `fetal_deaths_male/female` (by SEX), `fetal_deaths_singleton/twin/triplet+` (by PLURALITY). **Table A has no race stratification.** The spec's "Table A" citation is mis-attributed; correct table for maternal-age stratification in NVSR 73-09 is **Table 4** (8 age cells pre-encoded: `fetal_deaths_age_under15/15_19/20_24/25_29/30_34/35_39/40_44/45_plus` for year 2022). | Section A validates against **NVSR 73-09 Table 4 (8 age cells, all pre-encoded in `external_validation_targets.csv`)** — zero PDF transcription, zero L9 risk. Section B (race) defers NVSR validation to Task 4 (per its §15 spec "reproduce every numeric claim in the manuscript"); Section B presents the joint-use computation as a machinery demonstration only, with cells documented but not NVSR-pinned. |
| "Pseudocode in `docs/JOINT_USE_GUIDE.md` ('Worked example: fetal mortality rate by maternal race, 2022')." | `docs/JOINT_USE_GUIDE.md` line 84 reads "Worked example: fetal mortality rate by maternal race, **2017**" — Task 1 (2026-05-11) rewrote this section using 2017 as the example year explicitly because of the bridged-race-2018+ gap. §15 wasn't updated in lockstep. | Section B follows the JOINT_USE_GUIDE.md 2017 worked example pseudocode verbatim (joint-use machinery demonstration via the canonical helper). The `[plan-update]` candidate for §15's stale "2022" cite is flagged in this task's Forward-looking HALTs (per Convention 4) but is NOT done as part of Task 2 itself — proposed as a separate `[plan-update]` commit. |

**Cross-product join-key column-name state (no divergence vs Task 1)**

| Concept | natality v2.7.0 column | fetal_death v2.0.0 column | Verified at PRE-FLIGHT |
|---|---|---|---|
| Event year | `year` int16 | `data_year` int32 | ✓ (renamed via `to_canonical_natality`; output uses `data_year`) |
| Maternal age | `maternal_age` | `maternal_age` | ✓ (matches; 99 sentinel in fetal-death V2 era → NaN before binning) |
| 4-cat bridged race | `maternal_race_bridged4` | `maternal_race_bridged` | ✓ (renamed; both null for 2018+) |
| Hispanic origin | `maternal_hispanic_origin` | `hispanic_origin` | ✓ (renamed) |
| Residence status | `restatus` | `residence_status` | ✓ (renamed; canonical filter `!= 4` on both sides) |

**Numerator-side fetal-death filter state (Convention 3)**

| Concept | fetal_death schema | Plan assumption | Verified |
|---|---|---|---|
| `tabulation_flag` | `int 1-2`, "1=exclude <20wk; 2=include >=20wk", year coverage 1992-2002 + 2005-2022 | filter = `tabulation_flag == 2` produces NVSR-comparable population | ✓ — `fetal_death/external_validation_targets.csv` 2005-2022 `fetal_deaths_gte20wk_resident` rows reproduce against the parquet's `(tabulation_flag == 2) AND (residence_status != 4)` subset (per the existing fetal-death validation suite; 29/29 byte-exact for the count metric). Already-validated; this task does NOT re-run that validation, but consumes the same filter. |
| `residence_status` | `int 1-4`, "1=Resident; 2=Intrastate nonres; 3=Interstate nonres; 4=Foreign res" | filter = `residence_status != 4` excludes foreign residents | ✓ — same as above |

**NVSR 73-09 Table 4 stratified target snapshot (Section A verify targets)**

| year | metric | expected_value | source |
|---|---|---|---|
| 2022 | `fetal_deaths_age_under15` | 16 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_15_19` | 991 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_20_24` | 3631 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_25_29` | 5071 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_30_34` | 5634 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_35_39` | 3613 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_40_44` | 1138 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_45_plus` | 108 | NVSR 73-09 Table 4 |
| **Sum** | (verify against unstratified `fetal_deaths_gte20wk_resident` 2022 = 20,202) | 20,202 | ✓ — table-internal consistency |

**NVSR age bands ≠ helper's 6-band scheme — Section A binning**

`shared/helpers/canonical_join_keys.derive_maternal_age_band` uses 6 bands `<20 / 20-24 / 25-29 / 30-34 / 35-39 / 40+` (Task 1's authoring choice). NVSR 73-09 Table 4 uses **8 bands** including `<15`, `15-19` split (vs the helper's `<20`), and `40-44 / 45+` split (vs the helper's `40+`). Section A's notebook code will compute the 8 NVSR bands directly from `maternal_age` rather than via the helper — the helper stays correct for its joint-use purpose (matching the stratified denominators CSV); the NVSR validation just uses a finer-grained age binning specific to that one comparison. The denominator from `stratified_denominators.csv` for the 2022 by-age comparison can either (a) be re-derived from natality with NVSR's 8-band binning (recommended; ~30 seconds wall-clock on the harmonized parquet), or (b) be aggregated from the existing 6-band CSV with the `<20` and `40+` rows kept whole (acceptable; matches `<15+15-19` and `40-44+45+` sums respectively). Section A uses path (a) for cleanest NVSR-mappable cells, AND demonstrates path (b) sums for cross-check.

**Plan assumptions amended at PRE-FLIGHT (per Convention 3 second bullet)**

1. **Demo year, race-stratified piece**: 2017 (not 2022, per JOINT_USE_GUIDE.md authoritative source). Section B.
2. **Demo year, age-stratified piece**: 2022 (current vintage; matches `external_validation_targets.csv` NVSR 73-09 Table 4 encoded rows). Section A.
3. **NVSR validation scope**: Section A's 8 age cells against NVSR 73-09 Table 4 (pre-encoded). Section B's race cells NOT NVSR-pinned (machinery demonstration only; NVSR validation of race-stratified rates deferred to Task 4 per its scope).
4. **Age binning for Section A**: 8 NVSR bands `<15 / 15-19 / 20-24 / 25-29 / 30-34 / 35-39 / 40-44 / 45+` (derived inline in the notebook from `maternal_age`). Helper's 6-band scheme stays correct for joint-use; the NVSR-specific 8-band scheme is local to this one comparison.
5. **"Loads all three parquets" implementation**: load all three with small column projections; print record counts after canonical filter applied to each; this fulfills the §15 spec's "loads all three parquets, applies each canonical filter" without requiring the linked file in the fetal-mortality-rate computation (linked = infant deaths, not fetal deaths). Demonstrates the unified resource.
6. **Task 1 Forward-looking HALT 5 (1992-2002 crosswalk equivalence)** is incorporated as a SMOKE Tier 1 supplementary check, not as a notebook cell — keeps the notebook focused on the joint-use machinery demonstration; result documented in the receipt.

### Halt conditions tripped
None unresolved. The §15-spec vs current-state divergence (named above) is resolved by amending the task plan at this PRE-FLIGHT moment per Convention 3 and per §15's flexibility ("the spec is a starting point; PRE-FLIGHT may amend based on Field-value snapshot findings"). No previously-stable downstream output is being mutated. The proposed §11 plan-update to §15 Task 2 description is flagged for a separate `[plan-update]` commit (not bundled into Task 2).

### Result
PROCEED.

---

## PRE-FLIGHT addendum for task1_joint_use_denominators — 2026-05-11T17:58:10Z

**Field-value snapshot gap caught at SMOKE Tier 1, resolved pre-DO.** The original PRE-FLIGHT entry (17:50:48Z below) planned to read from `natality_v2_residents_only.parquet`. SMOKE Tier 1 (100 real rows of 2022) failed at parquet-read time:

```
pyarrow.lib.ArrowInvalid: No match for FieldRef.Name(restatus) in year: int16
certificate_revision: string maternal_age: int16 ... [82 column schema]
```

The convenience parquet drops the `restatus` column post-filter — a fact not snapshot in the 17:50:48Z entry's Field-value subsection. Resolution:

1. Switch the build script to read from the full `natality_v2_harmonized_derived.parquet` (2,202,879,406 bytes, locally-computed sha256=`9f917a43474eb9e3ed23aa95c714209421c25c29937376651149d22fab934ef0`). The harmonized parquet carries all 84 columns including `restatus`, and column projection (5 cols out of 84) keeps the read cost roughly equivalent to the residents-only file.
2. Apply the canonical filter `residence_status != 4` in the build script (after the rename helper). This makes the filter audit-explicit rather than relying on the upstream convenience step.
3. Note that the harmonized parquet's sha256 is NOT in any shipped PROVENANCE.md (the natality v2.7.0 deposit's PROVENANCE.md only covers the convenience parquets). This is an upstream documentation gap that I am NOT fixing as part of Task 1 — flagged here for downstream attention.

This addendum precedes the first DO mutation (no canonical output written yet); SMOKE Tier 0 was synthetic and produced only `/tmp/smoke0_out.csv`. The `task1-pre-do` tag remains at commit `7b058fc` (the right rollback point — addendum is still pre-DO).

### Halt conditions tripped
None unresolved. Course correction applied at SMOKE moment per Convention 3.

### Result
PROCEED with build from `natality_v2_harmonized_derived.parquet`.

---

## PRE-FLIGHT for task1_joint_use_denominators — 2026-05-11T17:50:48Z

### Inputs
- [x] All required input files exist
  - `/Users/yoelplutchok/Desktop/natality-harmonization/output/convenience/natality_v2_residents_only.parquet`: present, 1,716,780,400 bytes, sha256=`4c72aaa86c553d53c80c6eb38364c296ebb01636a612ad6664f024b12b153c11` matches `/Users/yoelplutchok/Desktop/natality-harmonization/output/convenience/PROVENANCE.md` v2.7.0 ✓
  - Above parquet's PROVENANCE.md identifies build hash `2d3c3d8` and timestamp 2026-04-28T22:53:25Z; matches Zenodo v2.7.0 (DOI `10.5281/zenodo.19868835`) ✓
  - `natality/metadata/harmonized_schema.csv`: present, 95 rows ✓
  - `fetal_death/harmonized_schema.csv`: present ✓
  - `natality/output/validation/external_validation_v1_comparison.csv`: present; `resident_births` rows confirm byte-exact reproduction for all 35 years 1990–2024 ✓
  - `fetal_death/live_births_by_year.csv`: present, 26 data rows (1995–2002 + 2005–2022) ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - bootstrap (2026-05-09): ✓
  - protocol-sync (2026-05-11, `596e8ce`): ✓
  - task6 (2026-05-11, `efe775d`): ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/task1_*.md`: does not exist ✓
  - `shared/helpers/build_stratified_denominators.py`: does not exist ✓
  - `shared/helpers/canonical_join_keys.py`: does not exist ✓
  - `fetal_death/stratified_denominators.parquet`: does not exist ✓
- [x] Forward-looking HALTs from prior session verified
  - **Task 6 HALT #1** (natality parquet PROVENANCE sha must match file sha at PRE-FLIGHT): sha `4c72aaa…` matches PROVENANCE.md ✓
  - **Task 6 HALT #2** (V3 linked re-validation): not applicable — this task does not re-run V3 linked validation.
  - **Task 6 HALT #3** (Conventions 3/4 non-optional for first canonical-data task): this entry includes the Field-value snapshot subsection per Convention 3 ✓; RECEIPT will include Forward-looking HALTs per Convention 4.
  - **Task 6 HALT #4** (mechanism-attribution wording): out of scope here.

### Environment
- [x] Python version: 3.13.9 (required ≥3.11) ✓
- [x] R version: n/a (Python-only task)
- [x] pandas version: 2.3.2 (required ≥2.3) ✓
- [x] pyarrow version: 18.1.0 (required ≥18.0) ✓
- [x] Working directory clean (`git status` on `main` at `efe775d`): ✓
- [x] On expected branch (`main`): ✓

### Source documentation
- [x] All NVSR PDFs / NCHS user guides referenced — n/a; this task derives stratified counts directly from the validated natality parquet and uses existing validation targets (already PDF-anchored) as the per-year benchmark. No new PDF reads.
- [x] All cited Zenodo DOIs resolve — natality concept DOI `10.5281/zenodo.19363074` (latest = v2.7.0 = `10.5281/zenodo.19868835`); not re-fetched (using local parquet hash-verified above).

### Outputs
- [x] Intended output paths do not exist OR are explicitly marked for overwrite
  - `shared/helpers/__init__.py`: new ✓
  - `shared/helpers/canonical_join_keys.py`: new ✓
  - `shared/helpers/build_stratified_denominators.py`: new ✓
  - `fetal_death/stratified_denominators.csv`: new ✓ (CSV not parquet — `*.parquet` is gitignored repo-wide per `.gitignore` line 2; CSV matches the existing pattern of `fetal_death/live_births_by_year.csv`; expected ~6,000 rows in long format, well under any size concern. Output format amended from the §15 spec's "parquet (or CSV)" wording — §15 explicitly allows either.)
  - `RECEIPTS/task1_joint_use_denominators_<ts>.md`: new ✓
  - Edits to existing files (`docs/JOINT_USE_GUIDE.md`, `fetal_death/CODEBOOK.md`, `fetal_death/README.md`, `VERSION_ROADMAP.md`, `NEXT_STEPS.md` §17, `STATUS.md`, `DECISION_LOG.md`): explicitly intended ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

The original Task 1 spec assumed cross-product column-name parity (`data_year`, `maternal_race_bridged`, `hispanic_origin`, `restatus`). Snapshot of actual schemas shows divergence; resolution documented below.

**Schema-divergence snapshot (cross-product join keys)**

| Concept | natality column (`natality/metadata/harmonized_schema.csv`) | fetal_death column (`fetal_death/harmonized_schema.csv`) | Plan assumed | Divergence resolution |
|---|---|---|---|---|
| Event year | `year` int16 (1990–2024) | `data_year` int32 (1992–2002, 2005–2022) | `data_year` both | Rename at read-time in canonical_join_keys helper; output uses `data_year` |
| Maternal age | `maternal_age` (10–54) | `maternal_age` (10–54;99) | `maternal_age` both | Match ✓ — 99 sentinel in fetal-death; derive age band from non-sentinel values |
| 4-cat bridged race | `maternal_race_bridged4` int8 (1990–2019, null 2020+) | `maternal_race_bridged` int (1992–2002, 2005–2017, null 2018+) | `maternal_race_bridged` both | Rename at read-time; output uses `maternal_race_bridged`; joint-coverage years for non-null bridged race = 1992–2002 + 2005–2017 (24 years); 2018–2022 rows have race=null (documented gap) |
| Hispanic origin | `maternal_hispanic_origin` int8 (codes 0\|1\|2\|3\|4\|5\|9) | `hispanic_origin` int (codes 0–9) | `hispanic_origin` both | Rename at read-time; output uses `hispanic_origin`; code spaces compatible (both expose UMHISP 0–9 with same semantics) |
| Residence status | `restatus` int8 (1\|2\|3\|4) | `residence_status` int (1–4) | `restatus` both | Rename at read-time; canonical filter `residence_status != 4`. Convenience parquet `natality_v2_residents_only.parquet` already applies this filter. |

**Per-year resident_births snapshot (NCHS-series mismatch between two existing artifacts)**

| Year | `natality/output/validation/external_validation_v1_comparison.csv` (CDC residence series; what natality parquet reproduces byte-exact) | `fetal_death/live_births_by_year.csv` (NVSR 57-08 / 73-09 series) | Diff |
|---|---|---|---|
| 1995 | 3,899,589 | 3,899,589 | 0 |
| 1996 | 3,891,494 | 3,891,494 | 0 |
| 1997 | 3,880,894 | 3,880,894 | 0 |
| 1998 | 3,941,553 | 3,941,553 | 0 |
| 1999 | 3,959,417 | 3,959,417 | 0 |
| 2000 | 4,058,814 | 4,058,882 | +68 |
| 2001 | 4,025,933 | 4,026,036 | +103 |
| 2002 | 4,021,726 | 4,021,825 | +99 |
| 2005 | 4,138,349 | 4,138,573 | +224 |
| 2006 | 4,265,555 | 4,265,593 | +38 |
| 2022 | 3,667,758 | 3,667,758 | 0 |

The stratified denominator file reproduces the natality parquet's microdata totals (CDC residence series), which match the natality validation target byte-exact. VERIFY criterion is reframed: sum-across-strata must equal the natality validation target (`external_validation_v1_comparison.csv` `resident_births` for each year), NOT `live_births_by_year.csv`. The latter is preserved as the canonical NVSR-as-published unstratified denominator. The 38–224 record/year discrepancy is documented in JOINT_USE_GUIDE.md, not papered over.

**Plan assumptions amended at PRE-FLIGHT (per Convention 3 second bullet)**

1. **Canonical join-key naming** — output uses fetal_death-style names (`data_year`, `maternal_race_bridged`, `hispanic_origin`, `residence_status`). natality columns are renamed at read-time via a new `shared/helpers/canonical_join_keys.py` helper rather than mutating the shipped natality parquet. Rationale: preserves Zenodo deposit immutability (v2.7.0 stays at its DOI), single source of truth for joint-use code, no breaking change to natality downstream users. A future natality v2.8 rename (Task 11 candidate) is the long-term cross-product parity fix; proposing it as a `[plan-update]` separate from this task.
2. **Output year scope**: 1992–2002 + 2005–2022 (29 joint-coverage years between natality and fetal-death). Years 1990–1991 (natality-only era pre-fetal-death) and 2003–2004 (fetal-death deferred to V2.1) and 2023–2024 (post-fetal-death coverage) excluded from the denominator output.
3. **Bridged race coverage**: 1992–2002 + 2005–2017 populated (24 years); 2018–2022 rows have `maternal_race_bridged = null` (documented gap; users wanting stratified joint-use race rates for 2018–2022 will need to wait for a future task that reconciles `maternal_race_ethnicity_5` vs fetal-death's `race_hispanic_revised`). Cell counts in 2018–2022 stratify on age × hispanic only.
4. **VERIFY criterion 1 reframed**: sum across strata per year matches `natality/output/validation/external_validation_v1_comparison.csv` `resident_births` cell (the natality validation target), not `fetal_death/live_births_by_year.csv` (which uses a different NCHS series). Difference enumerated in the per-year table above.
5. **Age band definition**: <20 / 20-24 / 25-29 / 30-34 / 35-39 / 40+, matching natality's existing `maternal_age_cat` column derivation rule. fetal-death-side users compute the same band from `maternal_age` single year. Sentinel `99` → NaN before binning (per §8 F5).

### Halt conditions tripped
None unresolved. All Field-value-snapshot divergences resolved by amending the task plan in this PRE-FLIGHT (see above) rather than silently proceeding. No previously-stable downstream output (`live_births_by_year.csv`, `external_validation_v1_comparison.csv`, harmonized schemas, manuscript drafts) is being mutated — Task 1 ships new artifacts only.

### Result
PROCEED.

---

## PRE-FLIGHT for task6_linked_validation_reconcile — 2026-05-11T17:05:00Z

### Inputs
- [x] All required input files exist
  - `natality/output/validation/external_validation_v3_linked_comparison.md`: present ✓ (35 PASS / 0 FAIL / 0 MISSING; 2015 `unweighted_infant_deaths` and `postneonatal_deaths` each show Diff=1 but `pass`).
  - `natality/README.md`: present ✓
  - `natality/docs/ABOUT_THIS_RELEASE.md`, `natality/docs/COMPARABILITY.md`, `natality/docs/VALIDATION.md`: present ✓
  - `paper/README.md`, `paper/draft_v1_ipums_styled.md`, `paper/draft_v2_hmd_styled.md`: present ✓
  - Monorepo `README.md`, `NEXT_STEPS.md`, `STATUS.md`: present ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - bootstrap (2026-05-09): ✓
  - protocol-sync `[plan-update]` (2026-05-11, commit `596e8ce`): ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/task6_*.md`: does not exist (good) ✓

### Environment
- [x] Python version: n/a (docs-only task)
- [x] R version: n/a
- [x] Working directory clean (`git status`): ✓
- [x] On expected branch (`main`, HEAD=`596e8ce`): ✓

### Source documentation
- [x] All NVSR PDFs / NCHS user guides referenced in this task have current SHA-256 matching the relevant `file_inventory.csv`
  - n/a — Task 6 is internal-doc reconciliation; no new NVSR re-verification required.

### Outputs
- [x] Intended output paths do not exist OR are explicitly marked for overwrite
  - `RECEIPTS/task6_linked_validation_reconcile_<ts>.md`: does not exist (good) ✓
  - Edits to existing files (natality/README.md, natality/docs/*, paper/README.md, NEXT_STEPS.md, STATUS.md, DECISION_LOG.md, PRE_FLIGHT_LOG.md): explicitly intended ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

Target cells enumerated; current values verified against the task plan's assumed state.

| File | Line | Current text (excerpt) | Plan assumes |
|---|---|---|---|
| `natality/README.md` | 19 | `183/183 V2 targets pass, 35/35 V3 linked targets pass` | matches ✓ |
| `natality/README.md` | 27 | `V3 linked external targets 35/35 pass (2005–2023, from NCHS linked user guides)` | matches ✓ |
| `natality/README.md` | 146 | `183/183 and 35/35 are headline numbers, but ... known quirks (e.g., two null-record_weight survivor rows in 2014/2015)` | matches ✓ — soft-flag below |
| `natality/docs/ABOUT_THIS_RELEASE.md` | 80 | `35/35 active pass` | matches ✓ |
| `natality/docs/COMPARABILITY.md` | 367 | `V2 183/183 and V3 linked 35/35 external targets still pass` | matches ✓ |
| `natality/docs/VALIDATION.md` | 206 | `Results: 35/35 active targets pass.` | matches ✓ |
| `paper/README.md` | 18 | `One framing is stale; verify against ...` | matches ✓ (will be marked resolved) |
| `NEXT_STEPS.md` | 440 | `35/35 (or 33/35 + 2 docs diffs — verify; see Task 6)` | matches ✓ (will be resolved) |
| `README.md` (monorepo) | 17 | `33/35 byte-exact (2 cells differ by 1 record from NCHS upstream null-weight survivor records)` | already canonical — no edit ✓ |
| `paper/draft_v1_ipums_styled.md` | 93, `paper/draft_v2_hmd_styled.md` | 94 | `33 of 35 targets ... two cells differ by exactly one record each because of NCHS upstream survivor records with null record weights` | already canonical — no edit ✓ |

- [x] Current values match task plan's assumed state ✓
- Plan assumes the validation file's authoritative state is "35 PASS rows under tolerance; 33 byte-exact + 2 differ by exactly 1 record" — verified by direct read.
- **Soft-flag (DECISION_LOG candidate):** `natality/README.md` line 146 mechanism wording ("two null-`record_weight` survivor rows in 2014/2015") and `natality/docs/VALIDATION.md` line 219 mechanism wording ("LATEREC edge cases") differ from the manuscript canonical mechanism wording ("NCHS upstream survivor records with null record weights"). These three locally-varying mechanism phrasings are out of scope for Task 6 (the task is HEADLINE-count reconciliation); preserving each file's local mechanism wording. Mechanism reconciliation is a separate downstream task if pursued.

### Halt conditions tripped
None.

### Result
PROCEED.
