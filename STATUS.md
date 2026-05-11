# STATUS — last updated 2026-05-11T19:26:28Z

> **Append-only.** To update: add a new dated section at the top. Do not edit earlier sections. Each session reads the most recent section as the authoritative current state and writes its own session-end section above it.

---

## 2026-05-11T19:26:28Z — Task 4 complete: paper companion notebook shipped (5 precision-edit candidates surfaced for Task 5)

### Current phase

Phase A continuing — paper companion notebook shipped. §17 readiness checklist now has **1 ⏳ item remaining** for manuscript submission (was 2 at end of Task 2): **Task 5** (manuscript trim + admin sections). Tasks 3, 7, 8, 9, 10 also remain but Task 3 is "ideally pre-submission, not blocking"; Tasks 7 is post-submission; 8/9/10 are not on the critical path.

### Current task

**Awaiting task selection.** Task 4 (paper_companion notebook) is now ✅ complete. The only manuscript-submission critical-path item left is:

- **Task 5** — Manuscript trim + admin sections. Now unblocked by Task 4's five precision-edit candidates (inlined in `paper/README.md` and `RECEIPTS/task4_paper_companion_2026-05-11T19-26-28Z.md`). Estimated effort: ~one session.

Alternative pick if not Task 5:
- **Task 3** — V2.1 fetal-death (2003+2004; ~one to two sessions; "ideally pre-submission, not blocking"). Would naturally bundle the H8 schema-doc reconciliation (FIX_LOG 2026-05-11) since V2.1 re-derives the parquet under corrected dtype.

### Last completed step

**Task 4 — Paper companion notebook shipped.** Three new artifacts (`notebooks/paper_companion.ipynb`, `notebooks/_build_paper_companion.py`, `notebooks/paper_companion_results.csv`); three edits (`notebooks/README.md` status; `paper/README.md` outstanding-work resolution with 5 precision-edit candidates inlined; `NEXT_STEPS.md` §17 item 7). Receipt at `RECEIPTS/task4_paper_companion_2026-05-11T19-26-28Z.md`. New DECISION_LOG entry recording the Section B 2017 race-stratified NVSR re-deferral choice.

The notebook enumerates 55 numeric claims from `paper/draft_v2_hmd_styled.md` (cataloged C01–C55 in the PRE-FLIGHT Field-value snapshot), recomputes each from parquets / schema CSVs / validation CSVs, and emits a pass/fail synthesis CSV. Final counts: **25 PASS, 20 CITE-ONLY** (citations / benchmarks not parquet-derivable), **4 L11** (wording-precision findings: C29 eras-vs-boundaries, C33 line-60 "three within_era" scope-restrictive, C47/C48/C49 line-104 raw-NCHS-field-name italicization), **1 DIFF** (C04 line-7 "approximately 3.5 million live births / year" — actual 1990–2024 mean is 3,966,275).

Five Task-5 precision-edit candidates surfaced and inlined in `paper/README.md` for the Task 5 author:
- **C04 line 7**: "approximately 3.5 million" → consider "approximately 3.5–4 million" or "3.97M average" (1990–2024 mean is 3,966,275; range 3,605,081–4,324,008).
- **C29 line 23**: "two within fetal death" boundary count requires reader arithmetic against Table 1's three fetal-death eras; consider "three eras with two era-to-era transitions" wording.
- **C33 line 60**: "Three fetal-death columns are tagged within_era" is scope-restrictive (schema has 24); consider "Three of the within_era fetal-death columns carry irreducibly incompatible..."
- **C47/C48/C49 line 104**: italicized `maternal_education`, `paternal_age_combined`, `maternal_education_unrevised` are raw NCHS field names (MEDUC, FAGECOMB, MEDUC_REC), not harmonized columns; clarify the referent.

§15 Task 4's secondary scope ("absorbs Section B NVSR cell-level validation deferred from Task 2") was re-deferred at PRE-FLIGHT per Convention 3: the L9 cheap-check confirmed `fetal_death/external_validation_targets.csv` ships no 2017 race-stratified targets, so the absorption would require fresh PDF transcription with the same L9 risk that motivated Task 2's original deferral. DECISION_LOG entry 2026-05-11T19:26:28Z records the choice; receipt Forward-looking HALT 3 flags it.

Convention 3 (Field-value snapshot) was load-bearing this task on FOUR axes:
- (a) **PRE-FLIGHT**: §15 Task 4 absorption-of-Section-B vs. no-pre-encoded-targets-in-CSV divergence → re-deferred.
- (b) **PRE-FLIGHT**: C29 framing decision (eras vs boundaries) made at the cheap-check moment.
- (c) **PRE-FLIGHT**: C33 framing decision (line-60 scope-restrictive reading) made at the cheap-check moment.
- (d) **DO**: C44/C45/C47–C49 detection-logic / interpretation bugs discovered and corrected mid-DO; the in-DO corrections were author-side issues in the notebook code that the snapshot helped surface quickly (not manuscript-side errors). One was reinterpreted as a manuscript-side L11 (C47–C49).

### What was done this session

1. Session start: read STATUS.md, NEXT_STEPS.md, README.md, PROJECT_STRUCTURE.md, DECISION_LOG.md (2 entries), FIX_LOG.md (1 entry), LESSONS.md (1 entry) per §1. Confirmed `89ddc77` was a post-Task-2 follow-up resolving STATUS Open Question 4.
2. Selected Task 4 (vs Task 5 STATUS default) with reasoning: Task 4 has clearer five-phase structure than Task 5, absorbs deferred Section B work (deferred again at PRE-FLIGHT), informs Task 5 by enumerating which numbers are parquet-anchored.
3. Verified all six Task 2 Forward-looking HALTs pre-DO: parquet shas unchanged; H8 dtype-drift caveat carried (string literals used on fetal-death side); L17 risk acknowledged for Task 4's notebook; §15 Task 2 wording already resolved by `89ddc77`; schema-doc parity test follow-up informational; Task 1 HALT 5 closed.
4. Wrote PRE-FLIGHT entry to `PRE_FLIGHT_LOG.md` (2026-05-11T19:15:00Z) with Convention 3 Field-value snapshot enumerating all 55 manuscript numeric claims (C01–C55) with source-of-truth artifacts. Three plan amendments resolved at PRE-FLIGHT: (Section B) NVSR-2017 race absorption re-deferred; (C29) eras-vs-boundaries framing; (C33) line-60 scope-restrictive reading.
5. Committed PRE-FLIGHT (`61090fc`); tagged `task4-pre-do`.
6. SMOKE Tier 0/1: PASS — 3 record counts (138,819,655 / 74,943,824 / 1,634,195) byte-exact; 3 validation-CSV row counts (183 / 35 / 29) byte-exact.
7. Wrote `notebooks/_build_paper_companion.py` (~370 lines; `DESIGN: tracks-current-state` per Convention 2). 38 cells (15 markdown, 23 code) across 14 section headers.
8. Built and executed `notebooks/paper_companion.ipynb` via `nbclient`. Initial run surfaced two author-side detection-logic bugs (C44/C45 used `.isna()` but cause_icd10 is empty-string; C34 regex didn't match B-blocks in markdown table) and one author-side interpretation bug (C47–C49 manuscript names raw NCHS field names not harmonized columns). All three corrected; re-ran builder; final synthesis: 25 PASS / 20 CITE-ONLY / 4 L11 / 1 DIFF.
9. VERIFY: Criterion A (notebook end-to-end no errors) PASS; Criterion B (every claim has a recompute or CITE-ONLY tag with documented source-of-truth) PASS-with-findings (5 precision-edit candidates for Task 5); Criterion C (Task 2 HALT 1 regression check) PASS via re-running `_build_joint_use_demo.py` — 8/8 NVSR cells still byte-exact. Task 2's notebook reverted post-re-run to preserve canonical artifact unmodified (L17 metadata churn, not a regression signal).
10. Edits to `notebooks/README.md` (paper_companion description rewritten + status table updated), `paper/README.md` (Companion notebook outstanding-work item marked RESOLVED with 5 precision-edit candidates inlined), `NEXT_STEPS.md` §17 item 7 ⏳ → ✅.
11. Wrote receipt to `RECEIPTS/task4_paper_companion_2026-05-11T19-26-28Z.md` with five-phase trace, three verify criteria, seven-item self-check, six Forward-looking HALTs.
12. Wrote DECISION_LOG entry recording the Section B re-deferral choice (3 alternatives considered, 3 residual risks documented).
13. Updating this STATUS.md section.
14. Pending: task commit + tag `task4-complete`.

### In-progress

(none)

### Blocked

(none)

### Next planned task

**Task 5 (manuscript trim + admin sections)** by default — it is the last critical-path item before manuscript submission, and Task 4's findings make it concrete (five enumerated precision-edit candidates to address during the trim). Alternative: Task 3 (V2.1 fetal-death) if the user wants to bundle H8 schema-doc reconciliation before submission.

### Open questions for human

Carried forward from prior STATUS, with open question 4 confirmed-resolved (89ddc77):

1. **Push the monorepo to GitHub now**, or wait until Task 5 ships? (Unblocks Task 9 redirect notices.)
2. **Natality v2.8 schema rename** (Task 1 Forward-looking HALT 6) — bundle with Task 3 (V2.1 fetal-death), or dedicated session?
3. **Schema-doc reconciliation for the H8 dtype drift** (FIX_LOG 2026-05-11): bundle into Task 3 (V2.1 = fetal-death rebuild) or do as a dedicated `[plan-update]` + schema-version bump task before Task 3?
4. ~~**`[plan-update]` candidate for §15 Task 2 wording**~~ **RESOLVED 2026-05-11 by `89ddc77` "§15 Task 2 + Task 4: breadcrumb annotations".**
5. **Section B 2017 race-stratified NVSR validation** — re-deferred by Task 4 per Convention 3 (no pre-encoded targets; L9 PDF-transcription risk). Should this be packaged as a small future task before manuscript submission (input: NVSR-2017 fetal-mortality PDF), or left as a post-submission enhancement? If the manuscript Task 5 trim does NOT add race-stratified-2017 NVSR claims, the absorption is not on the critical path.
6. **§15 Task 4 wording `[plan-update]` candidate** — analogous to the Task 2 case: §15 Task 4 description names the Section B absorption as in-scope but Task 4 re-deferred it. A future `[plan-update]` could add a breadcrumb annotation similar to the `89ddc77` pattern. Not done as part of Task 4 itself to avoid scope creep.

### Forward-looking HALTs for next session

Per Convention 4 (§6 receipt template). These are PRE-FLIGHT assertions the next session must verify; halt and ask the human if any fails. (Full list — six items — is in `RECEIPTS/task4_paper_companion_2026-05-11T19-26-28Z.md`; restated here at session level for cheap-check access at next session start.)

1. **Five Task-5 precision-edit candidates inlined in `paper/README.md`** (C04, C29, C33, C47/C48/C49) are the primary Task 4 → Task 5 handoff. If Task 5 runs, consume these as input.
2. **`notebooks/paper_companion.ipynb` binary sha = `dde922d1...` is NOT bit-stable across re-executions** (L17 / Task 2 HALT 3 carry-over). Use `paper_companion_results.csv` sha=`7891809c5040f25d7fcbe3e35ac262f049c4c75be68f0814718ea119757f35ce` as the bit-stable verification artifact.
3. **§15 Task 4's Section B absorption re-deferred** per Convention 3 (L9 risk; no pre-encoded targets). DECISION_LOG entry 2026-05-11T19:26:28Z and receipt Forward-looking HALT 3 carry the rationale. If the human disagrees, the absorption is a separate small future task (input: NVSR-2017 fetal-mortality PDF).
4. **`fetal_death/harmonized_schema.csv` H8 dtype drift remains NOT YET RECONCILED** (Task 2 HALT 2 carry-over). All future fetal-death joint-use code must continue to use string literals on `tabulation_flag`/`residence_status`/`maternal_age`/`maternal_race_bridged`/`hispanic_origin` until the schema-version bump task lands. Task 4's notebook follows this pattern.
5. **If a future task touches `paper/draft_v2_hmd_styled.md` (e.g., Task 5 trim)**, manuscript sha changes from `5e86c923...` — re-run `python notebooks/_build_paper_companion.py` to confirm whether the edit added/removed numeric claims. If `paper_companion_results.csv` sha changes, inspect the new synthesis for tags that need attention. Task 5 SHOULD touch the manuscript by design; treat the CSV-sha change as expected and use the new synthesis as the post-Task-5 verification.
6. **Task 1 Forward-looking HALT 6 (natality v2.8 rename plan-update)** remains open. Carried forward.

### Build artifacts current

- `natality/`: unchanged from prior STATUS (v2.7.0 mirror).
- `fetal_death/`: unchanged from prior STATUS (v2.0.0 mirror + Task 1's stratified_denominators.csv).
- `shared/helpers/`: unchanged.
- `paper/draft_v2_hmd_styled.md`: unchanged.
- `paper/README.md`: edited — Companion notebook outstanding-work item marked RESOLVED with 5 precision-edit candidates inlined. Post-edit sha=`d87a4a40...`.
- `notebooks/`: now contains **`paper_companion.ipynb`** (new, sha=`dde922d1...`, NOT bit-stable), **`_build_paper_companion.py`** (new, sha=`055c3aff...`, deterministic), **`paper_companion_results.csv`** (new, sha=`7891809c...`, bit-stable). README updated.
- `docs/JOINT_USE_GUIDE.md`: unchanged from Task 2.
- `FIX_LOG.md`: unchanged (no new entries this task).
- `DECISION_LOG.md`: new Task 4 entry recording Section B re-deferral.
- `figures/`: empty.

### Notes for next session

- Task 4 commit ships a ~5-line summary per Convention 5; full narrative in receipt + DECISION_LOG entry + this STATUS section.
- `task4-pre-do` set at `61090fc`; `task4-complete` to be set after the task commit lands.
- Field-value snapshot (Convention 3) caught FOUR divergences this task — two pre-DO (Section B deferral + C29/C33 framing decisions) and two in-DO (C44/C45 detection-logic bug; C47–C49 interpretation reframing). The in-DO findings were author-side bugs surfaced by the notebook's actual execution; documented in the receipt's DO trace.
- Task 4 is the second-largest task this project so far in terms of source-of-truth coverage — 55 enumerated manuscript claims is the densest mapping between text and shipped artifacts the resource will produce. Future manuscript edits should re-run the builder to refresh the synthesis.
- The 1 DIFF + 4 L11 findings are all manuscript-precision improvements rather than data-side bugs. Task 5 is well-positioned to absorb them all in a single edit pass.

---

## 2026-05-11T18:51:59Z — Task 2 complete: joint-use demo notebook shipped (+ first FIX_LOG entry)

### Current phase

Phase A continuing — joint-use demo notebook shipped. §17 readiness checklist now has **2 ⏳ items remaining** for manuscript submission (was 3 at end of Task 1): Task 4 (paper companion notebook) and Task 5 (manuscript trim + admin sections). Tasks 3, 7, 8, 9, 10 also remain but Tasks 7 is post-submission; Task 3 is "ideally before submission, not blocking"; Tasks 8/9/10 are not on the critical path.

### Current task

**Awaiting task selection.** Task 2 (joint_use_demo notebook) is now ✅ complete. Recommended next picks from `NEXT_STEPS.md` §15 in priority order:

- **Task 5** — Manuscript trim + admin sections (~one session; unblocks Task 4 cleanly because Task 4 wants the manuscript stable).
- **Task 4** — `notebooks/paper_companion.ipynb` (~one session; depends on Task 5 ideally precedes; would also naturally absorb the Section B NVSR validation deferred from Task 2).
- **Task 3** — V2.1 fetal-death (2003+2004 transition years; ~one to two sessions; "ideally before submission, not blocking").

### Last completed step

**Task 2 — Joint-use demo notebook shipped.** Two new artifacts (`notebooks/joint_use_demo.ipynb` + companion deterministic builder `notebooks/_build_joint_use_demo.py`); two edits (JOINT_USE_GUIDE.md filter-syntax fix + dtype caveat; notebooks/README.md description update); one §17 ✅; one new FIX_LOG entry (H8 fetal-death dtype drift — first FIX_LOG entry in the repo). Receipt at `RECEIPTS/task2_joint_use_demo_2026-05-11T18-51-59Z.md`.

The notebook ships two integrated demonstrations:
- **Section A** — 2022 fetal mortality rate by maternal age band, validated byte-exact against *NVSR 73-09* Table 4 (8 cells, all PASS, sum=20,202 matches unstratified target; aggregate FMR 5.4778 matches NVSR-published 5.48 within rounding).
- **Section B** — 2017 fetal mortality rate by maternal race (last bridged-race-available year), joint-use machinery demonstration with both denominator paths (pre-built CSV vs direct natality recompute) cross-verifying byte-exact. NVSR cell-level validation deferred to Task 4 per PRE-FLIGHT amendment.

Convention 3 (Field-value snapshot) was load-bearing this task on TWO axes:
- (a) **PRE-FLIGHT-discovered §15-vs-current state divergence**: §15 said "by maternal race, 2022, vs NVSR 73-09 Table A" but (i) 2022 has null `maternal_race_bridged` (NCHS dropped MBRACE post-2017); (ii) Table A is sex/plurality, not race. Plan amended at PRE-FLIGHT (Section A axis swap; Section B year swap; NVSR validation for Section B deferred to Task 4 to avoid L9 PDF-transcription risk).
- (b) **SMOKE-Tier-1-discovered H8 dtype drift**: `fetal_death/harmonized_schema.csv` documents 5 demographic/filter columns as `int` but the parquet ships them as `object`/string. Filter `(fd["tabulation_flag"] == 2)` silently produces 0 rows. Fixed in scope (JOINT_USE_GUIDE.md + notebook) with FIX_LOG entry; schema-doc reconciliation deferred to a future schema-version-bump task.

Task 1 Forward-looking HALT 5 (1992-2002 maternal_race_bridged crosswalk equivalence) was executed as SMOKE Tier 1 supplementary check: PASS — both products partition 1995 into the same `{1, 2, 3, 4}` bridged-race categories (structural equivalence). HALT 5 is now CLOSED.

### What was done this session

1. Session start: read STATUS.md, NEXT_STEPS.md, README.md, PROJECT_STRUCTURE.md, DECISION_LOG.md (3 entries), FIX_LOG.md (0 entries), LESSONS.md (1 entry) per §1.
2. Verified all 6 Task 1 Forward-looking HALTs pre-DO: stratified_denominators.csv sha matches; canonical_join_keys.py NATALITY_TO_CANONICAL content matches; filter-on-both-sides policy committed in notebook design; bridged-race-null preservation committed; 1992-2002 crosswalk-equivalence smoke deferred to Task 2 SMOKE Tier 1; Convention 3 second-bullet drill applied.
3. Wrote PRE-FLIGHT entry to `PRE_FLIGHT_LOG.md` (2026-05-11T18:27:14Z) with Convention 3 Field-value snapshot enumerating §15-spec-vs-current-state divergences on race-availability and NVSR-table mis-cite. Resolution: plan amended at PRE-FLIGHT (Section A 2022 by age + Section B 2017 by race).
4. Committed PRE-FLIGHT (`da5d407`); tagged `task2-pre-do`.
5. SMOKE Tier 0 (synthetic 10-row fixture): PASS — combined filter retains expected subset; mutation tests on each filter clause independently; race groupby; age=99 sentinel preserved.
6. SMOKE Tier 1 attempt 1: FAIL — `tabulation_flag == 2` (int) produces 0 rows. Diagnosed: fetal-death parquet stores `tabulation_flag` and `residence_status` as `object`/string dtype despite schema doc saying `int`. H8 doc-vs-data drift extends to 5 columns total (tabulation_flag, residence_status, maternal_age, maternal_race_bridged, hispanic_origin).
7. SMOKE Tier 1 retry with string-literal filter: PASS — 2017 NVSR-pop = 22,827 byte-exact against pre-encoded NVSR target. Task 1 HALT 5 crosswalk equivalence: PASS — both products partition 1995 into the same `{1, 2, 3, 4}` bridged-race categories.
8. SMOKE Tier 4 (full 2022 cross-product): PASS — 8/8 NVSR 73-09 Table 4 age cells byte-exact; aggregate FMR 5.4778 ≈ NVSR-published 5.48; row-count conservation on both numerator (sum-of-bands=20,202) and denominator (sum-of-bands=3,667,758) sides.
9. Wrote `notebooks/_build_joint_use_demo.py` (deterministic notebook builder; 199 lines; `DESIGN: tracks-current-state` per Convention 2).
10. Built and executed `notebooks/joint_use_demo.ipynb` via `nbclient`: 19 cells (8 markdown, 11 code), 0 errors, all assertions PASS.
11. Bundled docs-data drift fixes into Task 2 scope: JOINT_USE_GUIDE.md filter table line 51 + new dtype-caveat paragraph + worked-example code lines 92-95 string-literal fix; notebooks/README.md description rewritten.
12. Filed FIX_LOG entry for H8 (first FIX_LOG entry in repo) documenting fetal-death dtype drift across 5 columns + recommended schema-doc reconciliation + dtype-parity smoke-test follow-up.
13. Updated NEXT_STEPS.md §17 item 4 → ✅.
14. Wrote receipt to `RECEIPTS/task2_joint_use_demo_2026-05-11T18-51-59Z.md` with five-phase trace, three verify criteria, seven-item self-check, six Forward-looking HALTs.
15. Updating this STATUS.md section.
16. Pending: task commit + tag `task2-complete`.

### In-progress

(none)

### Blocked

(none)

### Next planned task

Task 5 (manuscript trim) by default — unblocks Task 4 cleanly and is the highest-leverage item on the §17 critical path after Task 2. Alternative: Task 4 directly (paper companion notebook) if you'd rather do it before manuscript trim; would naturally absorb Section B's NVSR validation deferred from Task 2.

### Open questions for human

Carried forward from prior STATUS:

1. **Push the monorepo to GitHub now**, or wait until Task 4/5 ships? (Unblocks Task 9 redirect notices.)
2. **Should the future natality v2.8 schema rename** (Task 1 Forward-looking HALT 5/6) be packaged with Task 3 (V2.1 fetal-death), or as a dedicated session?
3. **Schema-doc reconciliation for the H8 dtype drift** (FIX_LOG 2026-05-11): bundle into Task 3 (V2.1 = fetal-death rebuild) which would naturally re-derive the parquet under the corrected dtype, or do as a dedicated `[plan-update]` + schema-version bump task before Task 3?
4. **`[plan-update]` candidate for §15 Task 2 wording**: the §15 spec still says "by maternal race, 2022, matches NVSR 73-09 Table A" — both axes stale. The plan was amended at this task's PRE-FLIGHT. Should I write a `[plan-update]` commit to reword §15 to match what shipped?

### Forward-looking HALTs for next session

Per Convention 4 (§6 receipt template). These are PRE-FLIGHT assertions the next session must verify; halt and ask the human if any fails. (Full list — six items — is in `RECEIPTS/task2_joint_use_demo_2026-05-11T18-51-59Z.md`; restated here at session level for cheap-check access at next session start.)

1. **joint_use_demo.ipynb 2022 8-cell NVSR validation must remain all PASS.** If any future change touches natality v2.7.0 or fetal-death v2.0.0 parquets, re-run `python notebooks/_build_joint_use_demo.py` and inspect Section A's pass/fail table. Any DIFF row that wasn't there before is a regression — halt and ask.
2. **`fetal_death/harmonized_schema.csv` H8 dtype drift NOT YET RECONCILED.** ALL fetal-death joint-use code MUST use string literals on `tabulation_flag`/`residence_status`/`maternal_age`/`maternal_race_bridged`/`hispanic_origin` (or coerce with `pd.to_numeric`). Editing the schema CSV requires a schema-version bump per anti-pattern #6 — see open question #3.
3. **L17 risk: notebook .ipynb sha=`ff563e10...` is NOT bit-stable across re-executions** (Jupyter execution metadata). Receipt records as snapshot, not contract. Verify data-content reproducibility by re-running the builder and inspecting cell outputs, NOT by hashing the .ipynb file.
4. **Plan-update candidate for §15 Task 2 wording** (carried from PRE-FLIGHT amendment): reword the §15 Task 2 description to match what shipped (Section A age 2022 + Section B race 2017). Open question #4 for human.
5. **Schema-doc parity smoke test (FIX_LOG follow-up)**: add `fetal_death/tests/test_schema_dtype_parity.py` to prevent H8 recurrence. Bundle with the schema-version bump task.
6. **Task 1 Forward-looking HALT 5 (1992-2002 crosswalk equivalence) is CLOSED** by Task 2 SMOKE Tier 1's structural-equivalence check. Future receipt-readers tracing the HALT chain should consider this resolved at the 4-category-code level.

### Build artifacts current

- `natality/`: unchanged from prior STATUS (v2.7.0 mirror).
- `fetal_death/`: unchanged from prior STATUS (v2.0.0 mirror + stratified_denominators.csv shipped in Task 1).
- `shared/helpers/`: unchanged (3 files from Task 1).
- `paper/draft_v2_hmd_styled.md`: unchanged.
- `notebooks/`: now contains **`joint_use_demo.ipynb`** (new, sha=`ff563e10...`; NOT bit-stable) and **`_build_joint_use_demo.py`** (new, sha=`1f5952d4...`; deterministic). README updated.
- `docs/JOINT_USE_GUIDE.md`: edited (filter-table syntax fix + dtype-caveat paragraph + worked-example code string-literal fix). New sha=`cd68eba0...`.
- `FIX_LOG.md`: first entry filed (H8 fetal-death dtype drift, 2026-05-11).
- `figures/`: empty.

### Notes for next session

- Task 2 commit ships a ~5-line summary per Convention 5; full narrative in receipt + FIX_LOG entry + this STATUS section.
- `task2-pre-do` set at `da5d407`; `task2-complete` to be set after the task commit lands.
- Field-value snapshot (Convention 3) caught two real divergences this session — one at PRE-FLIGHT (§15-vs-current state on race availability and NVSR table) and one at SMOKE Tier 1 (H8 dtype drift on 5 fetal-death columns). The addendum-protocol pattern (write a new dated PRE-FLIGHT entry) was not needed because the SMOKE Tier 1 dtype finding was a bug-class addressable within DO scope (fix the filter literal, file FIX_LOG) rather than a plan-amendment-requiring divergence.
- The notebook's .ipynb file ships executed outputs; users running it via `jupyter nbconvert --execute` or `Run All` in Jupyter will reproduce identical data outputs (deterministic) but a different binary sha (Jupyter metadata).
- Section B's race-stratified NVSR validation was deferred to Task 4 (paper companion notebook); Task 4 should absorb that scope.

---

## 2026-05-11T18:06:12Z — Task 1 complete: joint-use stratified denominators shipped

### Current phase

Phase A — joint-use convenience layer shipped. §17 readiness checklist now has 3 ⏳ items remaining for manuscript submission (was 4 at end of Task 6): Task 2 (joint-use demo notebook), Task 4 (paper companion notebook), Task 5 (manuscript trim + admin sections). Tasks 3, 7, 8, 9, 10 also remain but are not on the manuscript-submission critical path or are post-submission.

### Current task

**Awaiting task selection.** Task 1 (joint-use convenience layer) is now ✅ complete. Recommended next picks from `NEXT_STEPS.md` §15 in priority order:

- **Task 2** — `notebooks/joint_use_demo.ipynb` (immediate downstream consumer of Task 1's output; ~half a session).
- **Task 5** — Manuscript trim and admin sections (no parquet dependency; ~one session).
- **Task 4** — `notebooks/paper_companion.ipynb` (depends on Task 5 ideally precedes; ~one session).

### Last completed step

**Task 1 — Joint-use convenience layer shipped.** Three new code artifacts (`shared/helpers/__init__.py`, `shared/helpers/canonical_join_keys.py`, `shared/helpers/build_stratified_denominators.py`) and one new data artifact (`fetal_death/stratified_denominators.csv`: 4,906 strata × 29 joint-coverage years, 114,886,832 total live births). All 29 per-year sums match `natality/output/validation/external_validation_v1_comparison.csv resident_births` byte-exact. Receipt at `RECEIPTS/task1_joint_use_denominators_2026-05-11T18-06-12Z.md`. DECISION_LOG entry records the aliasing-helper-vs-source-schema-rename choice and three residual risks. `NEXT_STEPS.md` §17 checklist item 3 marked ✅. Stale-on-contact fetal-death README "V4: Natality companion product" entry replaced with the joint-use-layer-shipped note (per §16). The natality v2.7.0 Zenodo deposit was NOT mutated; this is a purely additive layer over the existing deposits.

Convention 3 (PRE-FLIGHT Field-value snapshot) and Convention 4 (RECEIPT Forward-looking HALTs) both load-bearing this task:

- Convention 3 surfaced two divergences at the cheap-check window. (a) PRE-FLIGHT: all four non-age join keys diverge between the two product schemas; resolved by aliasing helper. (b) SMOKE Tier 1: the `natality_v2_residents_only.parquet` convenience file drops `restatus` post-filter, breaking the planned read path; resolved by a pre-DO addendum to PRE_FLIGHT_LOG.md (timestamp 2026-05-11T17:58:10Z) switching the input to the full harmonized parquet with the canonical filter applied audit-explicit in the build script. Both resolutions were documented BEFORE the first DO mutation.
- Convention 4: receipt enumerates six Forward-looking HALTs (sha-pin on the convenience CSV; canonical_join_keys dict-content check; filter-on-both-sides reminder for downstream notebooks; bridged-race-null-handling reminder; natality v2.8 rename plan-update candidate; documentation of when Field-value snapshot caught what).

### What was done this session

1. Session start: read STATUS.md, NEXT_STEPS.md, README.md, PROJECT_STRUCTURE.md, DECISION_LOG.md, FIX_LOG.md (no entries), LESSONS.md per §1.
2. Verified Task 6 Forward-looking HALTs (natality PROVENANCE sha matches local file sha; no V3 re-validation; Convention 3/4 templates applied to this task; mechanism-attribution wording preserved as Task 6 set).
3. Wrote PRE-FLIGHT entry to `PRE_FLIGHT_LOG.md` with Convention 3 Field-value snapshot enumerating all 5 join-key concepts; surfaced 4 column-name divergences; documented per-year `live_births` mismatch between `external_validation_v1_comparison.csv` (CDC residence series) and `live_births_by_year.csv` (NVSR series).
4. Committed PRE-FLIGHT (`7b058fc`); tagged `task1-pre-do`.
5. Wrote `shared/helpers/__init__.py`, `shared/helpers/canonical_join_keys.py`, `shared/helpers/build_stratified_denominators.py`. Build script supports `--tier 0/1/2/full` for SMOKE laddering.
6. SMOKE Tier 0 (synthetic 8-row fixture): PASS. 6 strata, sum=7, restatus=4 excluded, age=99 → null band, race=NaN preserved.
7. SMOKE Tier 1 (100 real 2022 rows): FAIL with `pyarrow.lib.ArrowInvalid: No match for FieldRef.Name(restatus)` — `natality_v2_residents_only.parquet` drops the column.
8. Wrote PRE-FLIGHT addendum at PRE_FLIGHT_LOG.md (timestamp 17:58:10Z) per Convention 3; switched build script to read from the full `natality_v2_harmonized_derived.parquet` (sha=`9f917a43...`, locally computed; no upstream PROVENANCE.md ships it).
9. Re-ran SMOKE Tier 0 (sha unchanged ✓), Tier 1 (100 rows, 16 strata, all-null race for 2022 per NCHS source change ✓), Tier 2 (full 2022, 3,667,758 total = natality validation target byte-exact ✓).
10. DO: full build for 1992-2002 + 2005-2022; output sha=`6874d5d65e7b3888acf8a833e4fa98063630765e2eeaf6e1c6cb48ad7b0db5c1`; 4,906 strata; 114,886,832 total.
11. VERIFY A (per-year sum matches natality target): 29/29 byte-exact ✓.
12. VERIFY B (bit-identical re-run): ✓ (sha unchanged across two consecutive `--tier full` invocations).
13. VERIFY C (race × year independent cross-check via direct natality groupby): 18/18 cells ✓ across years {2000, 2010, 2015, 2017}.
14. Rewrote `docs/JOINT_USE_GUIDE.md` end-to-end; replaced incorrect cross-product column-name claim with actual schema divergence table + helper reference + bridged-race-gap caveat + NCHS-series mismatch table + worked example for 2017 fetal mortality rate.
15. Updated `fetal_death/README.md` (companion-project section + version-roadmap stale-on-contact V4 entry) and `VERSION_ROADMAP.md` (joint-use section → ✅ shipped).
16. Marked `NEXT_STEPS.md` §17 item 3 → ✅.
17. Wrote receipt to `RECEIPTS/task1_joint_use_denominators_2026-05-11T18-06-12Z.md` with five-phase trace, verify results, six-item self-check, six Forward-looking HALTs.
18. Wrote DECISION_LOG entry recording the aliasing-helper choice and three residual risks.
19. Updating this STATUS.md section.
20. Pending: task commit + tag `task1-complete`.

### In-progress

(none)

### Blocked

(none)

### Next planned task

Task 2 (joint_use_demo.ipynb) by default — immediate downstream consumer of the new convenience CSV. Alternative: Task 5 (manuscript trim) if you prefer to push the manuscript forward before more code work.

### Open questions for human

Carried forward from prior STATUS, with #2 now consumed by completing Task 1:

1. **Push the monorepo to GitHub now**, or wait until Task 2/Task 5 ships? (Unblocks Task 9 redirect notices on the old repos.)
2. ~~**Task 1 next**, or another priority?~~ **RESOLVED 2026-05-11 (Task 1 complete).**
3. **Should the future natality v2.8 schema rename** (Forward-looking HALT 5 in the Task 1 receipt) be packaged with Task 3 (V2.1 fetal-death), or as a dedicated session? It requires re-running 183 NVSR targets and a new Zenodo deposit; bundling with Task 3 amortizes the validation re-run.
4. **Convention 3 second-bullet drill** — task 1 was the first session that triggered an addendum-protocol response (write a new dated PRE-FLIGHT entry rather than back-fill the original). Was the timestamp ordering (`task1-pre-do` tagged BEFORE the addendum) the right call? Self-check item 5 in the receipt documents the trade-off; if a different convention is preferred (e.g., re-tag after addendum), propose a §11 plan-update.

### Forward-looking HALTs for next session

Per Convention 4 (§6 receipt template). These are PRE-FLIGHT assertions the next session must verify; halt and ask the human if any fails. (Full forward-looking HALTs list — six items — is in `RECEIPTS/task1_joint_use_denominators_2026-05-11T18-06-12Z.md`; restated here at session level for cheap-check access at next session start.)

1. **stratified_denominators.csv sha256**: `6874d5d65e7b3888acf8a833e4fa98063630765e2eeaf6e1c6cb48ad7b0db5c1`. If different at next PRE-FLIGHT, the file has been re-derived or edited — halt and verify authorization (could indicate natality v2.8 rename landed, or an unauthorized edit).
2. **canonical_join_keys.py NATALITY_TO_CANONICAL mapping**: 4 entries `year:data_year, restatus:residence_status, maternal_race_bridged4:maternal_race_bridged, maternal_hispanic_origin:hispanic_origin`. If a future natality v2.8 lands these renames natively, this dict's content must change (become empty) and the receipt's invariants update.
3. **Joint-use code in Task 2 notebook MUST apply canonical filters on BOTH sides**: numerator `tabulation_flag == 2 AND residence_status != 4`; denominator `residence_status != 4` (already applied in the CSV).
4. **bridged-race null cells in 2018-2022 must NOT be dropna'd**. JOINT_USE_GUIDE.md caveat 4 documents this; a downstream `.dropna(subset=['maternal_race_bridged'])` would undercount the joint denominator by ~17M records.
5. **1992-2002 maternal_race_bridged equivalence cross-check** (Self-check residual risk 3): a 5-minute Task 2 PRE-FLIGHT smoke comparing natality's "approximate_pre2003" crosswalk to fetal-death's `harmonize.py` 4-category recode on a 1000-row MRACE sample would close this. Recommend doing it before any 1992-2002 stratified-by-race joint-use computation.
6. **natality v2.8 rename plan-update**: a future §11 proposal would rename natality's join-key columns to fetal_death-style names natively, making `canonical_join_keys.py` a no-op deprecation. This is a substantive task (re-run 183 NVSR targets, new Zenodo deposit, breaking-change communication); recommend a dedicated session or bundle with Task 3 (V2.1).

### Build artifacts current

- `natality/`: unchanged from prior STATUS (v2.7.0 mirror, parquets in Zenodo + on local Desktop).
- `fetal_death/`: now ships **`fetal_death/stratified_denominators.csv`** (4,906 rows, sha=`6874d5d6...`). All other artifacts unchanged.
- `shared/helpers/`: now contains three new files (`__init__.py`, `canonical_join_keys.py`, `build_stratified_denominators.py`). Was empty.
- `paper/draft_v2_hmd_styled.md`: unchanged.
- `notebooks/`: stub README unchanged; three planned notebooks (`joint_use_demo`, `paper_companion`, `era_boundary_walkthrough`) still not built. Task 2 (joint_use_demo) is unblocked by this STATUS section.
- `docs/JOINT_USE_GUIDE.md`: rewritten end-to-end with accurate cross-product naming, NCHS-series caveat, bridged-race-gap caveat, and 2017-vintage worked example.
- `figures/`: empty.

### Notes for next session

- Task 1 commit ships a ~5-line summary per Convention 5; full narrative in receipt + DECISION_LOG + this STATUS entry.
- `task1-pre-do` set at `7b058fc`; `task1-complete` to be set after the task commit lands.
- Field-value snapshot (Convention 3) caught two real divergences this session, both pre-DO. The protocol works; the addendum response pattern (write new dated PRE-FLIGHT entry; don't back-fill) is the L10-safe response when divergence surfaces between PRE-FLIGHT commit and DO mutation.
- The natality v2.7.0 full harmonized parquet's sha256 (`9f917a43...`) is NOT in any shipped PROVENANCE.md; it lives only in this receipt + PRE-FLIGHT entry. Upstream natality docs gap — flagged but not fixed in this task.

---

## 2026-05-11T17:30:00Z — Task 6 complete: V3 linked validation framing reconciled

### Current phase

Phase 0 — Monorepo bootstrap + protocol baseline + Task 6 done. Ready to begin Phase A (joint-use convenience layer + paper-supporting work). Task 6 was a small docs-only task; the first canonical-data mutation has not yet happened.

### Current task

**Awaiting task selection.** Task 6 (linked-file validation framing reconciliation) is now ✅ complete. The next session should pick from `NEXT_STEPS.md` §15 in priority order:

- **Task 1** — Joint-use convenience layer (stratified live-birth denominators). Highest leverage for the manuscript's "designed for joint use" claim.
- **Task 2** — `notebooks/joint_use_demo.ipynb`. Depends on Task 1 being helpful but not required.

### Last completed step

**Task 6 — V3 linked validation framing reconciled.** Adopted "33/35 byte-exact + 2 cells (2015 `unweighted_infant_deaths` and `postneonatal_deaths`) differ by exactly 1 record from NCHS upstream null-record-weight survivor records; all 35 pass within documented tolerance" as canonical, matching the framing already in the manuscript drafts and monorepo top-level README. Six files updated; manuscript drafts and monorepo top-level README unchanged (already canonical). Receipt at `RECEIPTS/task6_linked_validation_reconcile_2026-05-11T17-30-00Z.md`; DECISION_LOG entry records the canonical-framing choice. `NEXT_STEPS.md` §17 checklist item 5 marked ✅.

This was the first task to exercise Convention 3 (PRE-FLIGHT Field-value snapshot) and Convention 4 (RECEIPT Forward-looking HALTs) under the 2026-05-11 NHANES protocol-sync. Both proved useful: Convention 3 forced enumeration of every target line BEFORE any edit; Convention 4 produced four forward-looking HALTs (see receipt) that explicitly carry forward the prior session's HALT 2 plus three new task-specific halts for Task 1 / Task 2 to verify at PRE-FLIGHT time.

### What was done this session

1. Session start: read STATUS.md, NEXT_STEPS.md, README.md, PROJECT_STRUCTURE.md, DECISION_LOG.md, FIX_LOG.md, LESSONS.md per §1.
2. Verified prior session's Forward-looking HALTs (commit `596e8ce` touched expected files; no NHANES-specific items leaked into shipping content; working tree clean on `main`).
3. Wrote PRE-FLIGHT entry to `PRE_FLIGHT_LOG.md` including Convention 3 Field-value snapshot enumerating all 9 target locations (six post-edit + three already-canonical references) with current-text quoted and plan-assumption verified.
4. Tagged `task6-pre-do` at `596e8ce` before any DO edit.
5. DO: edited 7 files (6 content + §17 checklist update) to adopt canonical framing.
6. VERIFY: re-grepped 35/35|33/35 patterns; confirmed canonical framing consistent across the four scoped artifacts (natality README, monorepo README, manuscript drafts, validation MD) plus four additional fix-on-contact docs.
7. Wrote DECISION_LOG entry recording the canonical-framing choice, alternatives, reasons, residual risks.
8. Wrote RECEIPT to `RECEIPTS/task6_linked_validation_reconcile_2026-05-11T17-30-00Z.md` with five-phase trace, verify results, self-check, and Forward-looking HALTs (Convention 4).
9. Updating this STATUS.md section.
10. Pending: task commit + tag `task6-complete`.

### In-progress

(none)

### Blocked

(none)

### Next planned task

Task 1 (joint-use convenience layer) by default — highest leverage for the manuscript. Task 2 alternative if Task 1 turns out to be blocked by parquet-download cost.

### Open questions for human

Carried forward from prior STATUS, with #3 now resolved:

1. **Push the monorepo to GitHub now**, or wait until Task 1 ships?
2. **Task 1 next**, or another priority?
3. ~~**Linked-file validation framing.**~~ **RESOLVED 2026-05-11 (Task 6).**

### Forward-looking HALTs for next session

Per Convention 4 (§6 receipt template). These are PRE-FLIGHT assertions the next session must verify; halt and ask the human if any fails. (Full forward-looking HALTs list is in `RECEIPTS/task6_linked_validation_reconcile_2026-05-11T17-30-00Z.md`; restated here at session level for cheap-check access at next session start.)

1. **If next session is Task 1**: the natality parquet's PROVENANCE.md sha256 must match the file's current sha256 at PRE-FLIGHT time. If the parquet has been re-derived since v2.7.0, the V3 linked validation count may have shifted from 33/35 byte-exact + 2 differ-by-1, invalidating the canonical framing established in Task 6. Halt and re-validate before stratifying.
2. **If next session re-runs `compare_external_targets_v3_linked.py`** and the resulting split differs from 33 Diff=0 / 2 Diff=1, then the canonical framing established in Task 6 is stale. All six post-edit shipping docs plus the manuscript drafts and the monorepo top-level README need paired updates. Halt and re-derive.
3. **Convention 3 / Convention 4 templates are non-optional for the next task that mutates a canonical artifact** (parquet, harmonized_schema.csv, validation-target CSV, doc numeric). Task 6 demonstrated them on a docs-only reconciliation; the next task is the first canonical-data exercise. If the PRE-FLIGHT lacks the Field-value snapshot subsection or the RECEIPT lacks the Forward-looking HALTs subsection, that is an L10-class back-fill risk and a regression on the protocol-sync convention adoption.
4. **Mechanism-attribution wording across `natality/README.md` line 146 vs `natality/docs/VALIDATION.md` line 219 vs the manuscript drafts** intentionally remains varied after Task 6 (out of scope; preserved as DECISION_LOG residual-risk (a)). If a future task disambiguates them, propose a §11 plan-update that touches all three locations together so the wording converges atomically.

### Build artifacts current

Unchanged from prior STATUS. No parquets, schemas, or validation CSVs were touched in this session — Task 6 was a docs-only reconciliation. Validation MD `external_validation_v3_linked_comparison.md` remains the unmodified authoritative source for the V3 linked target outcomes.

### Notes for next session

- Task 6 commit ships a ~5-line summary per Convention 5 (commit-message brevity); full narrative lives in the receipt and DECISION_LOG entry. Commit pending at this STATUS write.
- `task6-pre-do` tag set at `596e8ce`; `task6-complete` tag will be set after the task commit lands.
- §17 readiness checklist now has 4 ⏳ items remaining for manuscript submission (was 5; Task 6 → ✅): Task 1 (joint-use layer), Task 2 (joint-use demo), Task 4 (paper companion), Task 5 (manuscript trim + admin sections). Tasks 3, 7, 8, 9, 10 are post-submission.
- The new PRE-FLIGHT template's Field-value snapshot subsection (Convention 3) is the first cheap-check that surfaces drift between task-plan-assumed state and actual file state. Worked well here for headline-count enumeration; the next task using it on canonical-data mutation will be a stronger test.

---

## 2026-05-11T16:32:34Z — `[plan-update]` Protocol sync from upstream NHANES (conventions 1-5 + L13/L14/L17)

### Current phase

Phase 0 — Monorepo bootstrap + protocol baseline. Still ready to begin Phase A (joint-use convenience layer + paper-supporting work). No canonical-data mutation has happened yet; this session was a `[plan-update]` only.

### Current task

**Awaiting task selection.** No data/code task is currently in flight. The next session should pick from `NEXT_STEPS.md` §15 in priority order, applying the new conventions starting from PRE-FLIGHT of whichever task is chosen:

- **Task 1** — Joint-use convenience layer (stratified live-birth denominators).
- **Task 6** — Reconcile linked-file validation framing (15-30 min).
- **Task 2** — `notebooks/joint_use_demo.ipynb`.

### Last completed step

**Protocol sync from upstream NHANES.** `KICKOFF.md` and `NEXT_STEPS.md` updated to incorporate five generalizable conventions (SHAPE-not-VALUE smoke; FROZEN-AT-TASK docstring tag; Field-value snapshot in PRE-FLIGHT template; Forward-looking HALTs in RECEIPT template; commit-message brevity) and three new mistake-class matrix rows (L13 inventory file-roles vs columns; L14 exit-code propagation on per-row failures; L17 SMOKE pinning stale annotation values). `LESSONS.md` has the full rationale entry under 2026-05-11T16:32:34Z. NHANES-specific items (cross-family dual-key, `halt_c_reprobe.sh`, schema `$schema_version`, V1.9-folate task block) explicitly NOT ported.

### What was done this session

1. Read NHANES `KICKOFF.md`, `EXECUTION_PROTOCOL.md`, `HARMONIZATION_LESSONS.md` end-to-end and identified five generalizable conventions and three new mistake-class matrix rows since the HVS protocol was forked.
2. Categorized each as HVS-portable vs NHANES-specific; presented the categorized list to the human; received approval to apply all six generalizable updates as a single `[plan-update]` commit.
3. Edited `NEXT_STEPS.md` §4.2.1 (SHAPE-not-VALUE + DESIGN docstring tag), §4.5 (commit-message brevity), §5 PRE-FLIGHT template (Field-value snapshot subsection), §6 RECEIPT template (Forward-looking HALTs subsection), §8 mistake-class matrix (L13, L14, L17).
4. Edited `KICKOFF.md` to add the "Conventions in effect" block summarizing Conventions 1-5; refined audit-session framing to include L17 in the "look for these specifically" list and point findings at `AUDITS/`.
5. Appended rationale entry to `LESSONS.md` under 2026-05-11T16:32:34Z.
6. Updating this `STATUS.md` section.
7. Pending: `[plan-update]` commit of all five edits.

### In-progress

(none)

### Blocked

(none)

### Next planned task

Same as before: Task 1 (joint-use convenience layer) or Task 6 (linked-validation reconciliation) per user direction.

### Open questions for human

Carried over from the prior STATUS section, unchanged by this `[plan-update]`:

1. **Which task to start first** — Task 1 (~half a session) or Task 6 (~30 min)?
2. **Should the monorepo be pushed to GitHub now**, or wait until Task 1 ships?
3. **Linked-file validation framing** (Task 6 input): 35/35 vs 33/35 + 2 docs framing. The authoritative source is `natality/output/validation/external_validation_v3_linked_comparison.md`.

### Forward-looking HALTs for next session

Per the new Convention 4 (and §6 receipt template), this protocol-sync flags the following for the next session's PRE-FLIGHT to verify:

1. **KICKOFF.md, NEXT_STEPS.md §4.2.1 / §4.5 / §5 / §6 / §8, LESSONS.md, STATUS.md sha256s all changed** in the protocol-sync commit. If `git show <commit>` shows fewer files touched than these six, the commit is incomplete. Halt and re-derive.
2. **NHANES-specific items not leaked.** Grep the HVS tree for `dual_key_match_exception`, `halt_c_reprobe`, `bridges_schema.json`, `$schema_version`, `V1.9-folate` — all should return zero hits. Any hit means an NHANES-specific item was accidentally ported. Halt and remove.
3. **First post-protocol-sync task** (Task 1 or Task 6 — whichever the human picks next) must use the new PRE-FLIGHT template (with Field-value snapshot subsection) and the new RECEIPT template (with Forward-looking HALTs subsection). If the first post-sync receipt is missing either subsection, that's an L10-class back-fill risk; halt and re-template before continuing.

### Build artifacts current

Unchanged from the prior STATUS section. No data or code touched in this session.

### Notes for next session

- The `[plan-update]` commit message follows new Convention 5 (~5-line summary; full rationale lives in `LESSONS.md` 2026-05-11T16:32:34Z entry).
- The first task that mutates a canonical artifact (parquet, harmonized_schema.csv, validation-target CSV, doc number) is the first real exercise of the new PRE-FLIGHT and RECEIPT templates. The new subsections are non-optional — see §5 and §6 templates.
- New `AUDITS/` directory referenced in the updated `KICKOFF.md` audit-session framing does not yet exist; it will be created the first time an audit session writes findings, not pre-emptively.

---

## 2026-05-09T00:00:00Z — Bootstrap: monorepo migration + operating protocol installed

### Current phase

Phase 0 — Monorepo bootstrap complete. Ready to begin Phase A (joint-use convenience layer + paper-supporting work).

### Current task

**Awaiting task selection.** No task is currently in flight. The next session should pick from `NEXT_STEPS.md` §15 in priority order:

- **Task 1** — Joint-use convenience layer (stratified live-birth denominators). Highest leverage for the manuscript's "designed for joint use" claim.
- **Task 6** — Reconcile linked-file validation framing. 15-30 minute task; should be done early to unblock Task 5.
- **Task 2** — `notebooks/joint_use_demo.ipynb`. Depends on Task 1 being helpful but not required.

### Last completed step

**Bootstrap.** This monorepo was created from the previously separate `natality-harmonization` and `fetal-death-harmonization` repos, with unified top-level docs and the operating-protocol scaffolding now in place.

### What was done in bootstrap

1. Created `/Users/yoelplutchok/Desktop/vital-statistics-harmonization/`.
2. Imported `natality/` from yoelplutchok/natality-harmonization v2.7.0 (no .git history, code + docs + metadata only; large parquets and raw zips are .gitignored and live on Zenodo).
3. Imported `fetal_death/` from local /Users/yoelplutchok/Desktop/fetal-death-harmonization v2.0.1 (same exclusions).
4. Wrote unified top-level docs: `README.md`, `PROJECT_STRUCTURE.md`, `VERSION_ROADMAP.md`, `LICENSE`, `CITATION.cff`, `requirements.txt`, `.gitignore`.
5. Wrote cross-product docs: `docs/JOINT_USE_GUIDE.md`, `docs/PRIOR_ART.md`.
6. Moved manuscript drafts to `paper/` with clearer names (`draft_v1_ipums_styled.md`, `draft_v2_hmd_styled.md`); the original drafts in the fetal-death repo are unchanged.
7. Wrote `notebooks/README.md` describing planned cross-product worked examples.
8. Initial monorepo commit at `7fd9cdf`.
9. Wrote `NEXT_STEPS.md` with detailed handoff plan for fresh sessions; commit `79b3072`.
10. Folded the NHANES-Assay-Bridging operating protocol (five-phase structure, halt conditions, mistake-class matrix, anti-patterns, self-check) into `NEXT_STEPS.md` §1-§13; created supporting state files: `KICKOFF.md`, this `STATUS.md`, append-only logs (`DECISION_LOG.md`, `FIX_LOG.md`, `LESSONS.md`, `PRE_FLIGHT_LOG.md`), and `RECEIPTS/README.md`.

### In-progress

(none)

### Blocked

(none)

### Next planned task

Begin Task 1 (joint-use convenience layer) or Task 6 (reconcile linked validation framing) per user direction. See `NEXT_STEPS.md` §15.

### Open questions for human

1. **Which task to start first** — Task 1 (joint-use layer; ~half a session) or Task 6 (validation reconciliation; ~30 min)? Task 6 is shorter and unblocks Task 5; Task 1 is higher leverage for the manuscript.
2. **Should the new monorepo be pushed to GitHub now**, or wait until at least Task 1 has shipped? Task 9 (redirect notices on the old repos) depends on the monorepo being on GitHub.
3. **Linked file validation framing** (Task 6 input): the natality README says "35/35 linked targets pass" but the manuscript drafts say "33/35 byte-exact + 2 cells differ by one record each from null-weight survivor records." Need to know which is canonical. The authoritative source is `natality/output/validation/external_validation_v3_linked_comparison.md`.

### Build artifacts current

- `natality/`: full v2.7.0 mirror minus parquets (138.8M natality records and 74.9M linked records live in Zenodo concept DOI 10.5281/zenodo.19363074, latest version v2.7.0 = 10.5281/zenodo.19868835).
- `fetal_death/`: full v2.0.1 mirror minus parquets and raw zip (1.6M fetal-death records live in Zenodo DOI 10.5281/zenodo.20031571).
- `paper/draft_v2_hmd_styled.md`: current preferred manuscript draft (~3,500 words, modeled on HMD IJE 2015; see `paper/README.md` for outstanding work).
- `paper/draft_v1_ipums_styled.md`: superseded.
- `notebooks/`: stub README only; three planned notebooks (`joint_use_demo`, `paper_companion`, `era_boundary_walkthrough`) not yet built.
- `figures/`: empty; cross-product figures planned in Task 8.
- `shared/helpers/`: empty.

### Notes for next session

- The operating protocol in `NEXT_STEPS.md` §1-§13 is binding. Read `KICKOFF.md` for the canonical session-start prompt.
- The mistake-class matrix in `NEXT_STEPS.md` §8 is informed by the natality `HARMONIZATION_LESSONS.md` and the NHANES Assay-Bridging project's `EXECUTION_PROTOCOL.md`. New mistake classes encountered during HVS work should be appended to `LESSONS.md` and a new matrix row proposed via §11.
- This is the very first STATUS entry. There are no prior receipts, fixes, lessons, or decisions logged yet. Session-end discipline starts now.
