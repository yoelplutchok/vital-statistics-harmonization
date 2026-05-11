# STATUS — last updated 2026-05-11T18:06:12Z

> **Append-only.** To update: add a new dated section at the top. Do not edit earlier sections. Each session reads the most recent section as the authoritative current state and writes its own session-end section above it.

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
