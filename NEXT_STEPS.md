# NEXT_STEPS — work plan + operating protocol

This document is **both** the canonical work plan for the U.S. Harmonized Vital Statistics (HVS) resource and the operating discipline its LLM agents follow. It is self-contained: a fresh LLM session reading this file plus `STATUS.md` and `KICKOFF.md` has full context.

The operating discipline (sections §1–§9) is adapted from the NHANES Assay-Bridging Harmonization Project's `EXECUTION_PROTOCOL.md`, which itself was distilled from real LLM-amplifier failures during a prior natality harmonization. The disciplines exist because each one prevented a real, expensive mistake. **Do not skip them on the assumption that "this task is too small."**

**Last updated:** 2026-05-09, after monorepo-migration commit `7fd9cdf` and NEXT_STEPS-protocol-folding commit (this commit).

---

# §1. Session start — read this every time

If you are an LLM agent or new human collaborator picking this up, read these files in this exact order before doing any work:

1. **[`STATUS.md`](STATUS.md)** — the always-current project state. Tells you the current phase, current task, last completed task, in-progress items, blocks, and open questions for the human.
2. **This file (`NEXT_STEPS.md`)** — operating protocol (§1–§9) and the full task list (§10).
3. **[`README.md`](README.md)** — what the resource is, three products at a glance, where things live.
4. **[`PROJECT_STRUCTURE.md`](PROJECT_STRUCTURE.md)** — the file-by-file map. Use it when you need to find something.
5. **The last 10 entries of [`DECISION_LOG.md`](DECISION_LOG.md)** — recent non-trivial choices and why.
6. **The last 5 entries of [`FIX_LOG.md`](FIX_LOG.md)** — recent bugs and fixes.
7. **[`LESSONS.md`](LESSONS.md)** end-to-end — new mistake classes since this protocol was written.
8. **[`docs/JOINT_USE_GUIDE.md`](docs/JOINT_USE_GUIDE.md)** and **[`docs/PRIOR_ART.md`](docs/PRIOR_ART.md)** if your task touches cross-product analysis or the manuscript.
9. **The current preferred manuscript draft: [`paper/draft_v2_hmd_styled.md`](paper/draft_v2_hmd_styled.md)** if your task touches the paper.

After reading, before doing any work, tell the human:

- **(a)** the current task per `STATUS.md` (or "bootstrap, no STATUS.md state yet" if uninitialized)
- **(b)** any open questions for the human you found
- **(c)** what you propose to do this session
- **(d)** any halt condition you've already tripped from steps 1–8

Then **wait for human confirmation** before starting. The kickoff prompt in [`KICKOFF.md`](KICKOFF.md) automates this handshake.

---

# §2. The four core principles

Every operational rule in this file derives from these four. If any rule appears to conflict, the principle wins.

1. **Cheap checks before expensive ones.** Verify a SHA-256 before downloading. Verify a smoke result on 100 rows before applying to 138 million. Verify a join on 5 demographic strata before claiming the join works for all strata.
2. **Fail closed.** When in doubt, halt and ask the human. Never silently work around an inconsistency. Never patch a downstream artifact to match a buggy upstream.
3. **State on disk, never only in memory.** Every meaningful step writes a checkpoint. Every non-trivial decision is logged. The next session can resume without context.
4. **Re-running must be free.** Every operation is idempotent and reversible. If a mistake is found, the cost of recovery is "wait for the pipeline" — not "redo the past three days."

If a step would violate one of these, **stop and ask the human before proceeding.**

---

# §3. State files

Six files at the repository root, plus a `RECEIPTS/` directory. Read all relevant ones at session start. Append to them throughout the session.

| File | Read at session start | Format | Append-only |
|---|---|---|---|
| [`STATUS.md`](STATUS.md) | Always | Dated sections, newest first | Yes — new section per session |
| [`NEXT_STEPS.md`](NEXT_STEPS.md) (this file) | Always | Plan + protocol | Update task statuses; protocol changes via §9 plan-update process only |
| [`DECISION_LOG.md`](DECISION_LOG.md) | Last 10 entries | Dated rows | Yes |
| [`FIX_LOG.md`](FIX_LOG.md) | Last 5 entries | Dated rows | Yes |
| [`LESSONS.md`](LESSONS.md) | End-to-end | Dated rows | Yes |
| [`PRE_FLIGHT_LOG.md`](PRE_FLIGHT_LOG.md) | Most recent entry only | Dated checklists | Yes |
| [`RECEIPTS/`](RECEIPTS/) | None directly; use STATUS.md to locate the latest | One markdown file per completed task | Yes — never edit an existing receipt |

**Append-only means:** new content goes at the top (or in a new file under `RECEIPTS/`) with a timestamp. Earlier sections are not edited or deleted, even if they turn out to be wrong. A correction is a new dated section that supersedes the old one. This is how the next session reconstructs what happened.

---

# §4. The five-phase task structure

Every task in §10 has five phases, executed in order. Skipping a phase is a halt condition.

```
┌────────────┐   ┌───────┐   ┌────┐   ┌────────┐   ┌─────────┐
│ PRE-FLIGHT │──▶│ SMOKE │──▶│ DO │──▶│ VERIFY │──▶│ RECEIPT │
└────────────┘   └───────┘   └────┘   └────────┘   └─────────┘
       │            │          │         │             │
       ▼            ▼          ▼         ▼             ▼
   Halt if      Halt if    Run on    Halt if      Append to
   inputs       trivial    real      success      RECEIPTS/
   missing or   case       inputs    criteria     and update
   wrong        fails                not met      STATUS.md
```

## §4.1 PRE-FLIGHT — verify inputs before doing anything

Cheap. Read-only. Catches missing files, wrong inputs, mis-aligned state.

For each task in §10, run the standard checks (template in §5), append the checklist to `PRE_FLIGHT_LOG.md` **before** the DO phase, and only proceed if every check passes. Halt-and-ask on any failure.

**Do not back-fill PRE-FLIGHT entries.** Writing the PRE-FLIGHT checklist *after* DO has already started is forbidden — the cheap-check window has closed by then. If a task has multiple sub-steps, either (a) write one upfront PRE-FLIGHT enumerating every sub-step's inputs, or (b) write a per-sub-step PRE-FLIGHT before each sub-step's DO.

## §4.2 SMOKE — trivial-scale dry run

Run the operation on the smallest input that exercises the logic before running on real data. Skipping the smoke run is a halt condition. The smoke run is **always at least 100× cheaper than the real run**; if your smoke run is more than 5% of the real-run cost, it's wrong-sized.

For HVS specifically, the smoke ladder is:

| Tier | Scale | Purpose | Halt if |
|---|---|---|---|
| **0. Synthetic fixture** | 5–10 hand-constructed rows | Function does what its name says | Hand-computed expected output disagrees |
| **1. Smoke** | 100 real rows, 1 year, 1 product | Survives real data without crashing or silently nulling | Unexpected null, schema mismatch, dtype drift |
| **2. Single-year** | One full year of one product | Per-year aggregate matches the corresponding *NVSR* cell | Per-year count or rate differs from published target |
| **3. Multi-year, one product** | All years of one product | Cross-era behavior + bridge application | Trend has unexplained discontinuity at a non-era boundary |
| **4. Cross-product** | Joint use of natality + linked + fetal-death | Joint-use rate computation | Numerator-denominator mismatch; row counts don't conserve at join boundaries |

Each tier costs roughly 10× the previous. Catching a bug at Tier 0 saves 10,000× the rework cost vs catching it at Tier 4.

### §4.2.1 SHAPE-not-VALUE convention for new smoke harnesses

Every new smoke harness asserts **structural invariants that survive authorized canonical-state mutation**, not mutable annotation values pinned at the harness's authoring moment. Pinning a value that is expected to evolve under later authorized tasks turns a correct subsequent mutation into a SMOKE FAIL — stale pinning, not a regression. (See §8 row L17.)

**DO** assert: column count, row count, presence-of-key, parse-validity, dtype, monotonic invariants, schema-level enums, row-count conservation across joins, sum-across-strata = unstratified-total.

**DO NOT** pin: specific cell values that may evolve (a row count that will grow when V2.1 adds 2003+2004 fetal-death records; a sha256 that will change when a script is correctly edited; a docs string that will be reworded; a `notes` field whose content evolves).

When a SMOKE must pin a value (e.g., a frozen-at-task assertion that documents the state at a specific historical task), declare its design intent on the **first docstring line** of the harness file:

- `DESIGN: tracks-current-state` — asserts post-DO canonical state for the task that authored it; updated under authorized canonical drift.
- `DESIGN: frozen-at-<task_id>` — asserts the historical schema state by design; remains FAIL under later renames — that IS the test (e.g., `tests/v1_4_smoke_fixtures/` asserting pre-rename schema state).

If a SMOKE FAILs after an authorized canonical mutation: check the DESIGN tag first. `tracks-current-state` → bundle the minimal Edit into the same commit as the canonical mutation. `frozen-at-<task>` → expected FAIL; do not "fix."

## §4.3 DO — real-scale operation

Run on real data. Idempotent (re-running produces identical output, byte-for-byte). Resumable (checkpoint at sub-step boundaries). Non-destructive (the previous artifact is preserved or version-bumped, never overwritten).

Before the DO phase, `git tag <task_id>-pre-do` so rollback is one command. After a successful RECEIPT, `git tag <task_id>-complete`.

## §4.4 VERIFY — explicit success criteria

Each task has explicit, written-down success criteria (in §10's Validation field for each task). The verify phase computes the criterion and compares.

If a criterion is not met → halt. Do not write a successful receipt. Do not advance STATUS.md.

If a criterion is met but the result *feels wrong* (distribution looks off, count is suspiciously round, an "obvious" check happened to pass), do not silently accept. Write a soft-flag entry in `DECISION_LOG.md` and ask the human before advancing.

## §4.5 RECEIPT — append-only record of what happened

Write to `RECEIPTS/<task_id>_<UTC_timestamp>.md` using the template in §6. Update `STATUS.md` to reflect that the task is complete. Tag the git commit `<task_id>-complete`. The receipt is the ground truth for "did this task happen?" — if a receipt does not exist, the task did not happen.

**Commit-message brevity.** The commit that ships the receipt carries a ~5-line summary (task ID, one-line what-was-done, key inputs/outputs by sha-prefix, link to the receipt path, halt-status). The full narrative lives in the receipt, not the commit. Saves repo bloat across many tasks; receipts remain the canonical record. `[plan-update]` commits (protocol or schema changes) follow the same shape with `[plan-update]` as the leading bracket-tag.

---

# §5. PRE-FLIGHT checklist template

Append to `PRE_FLIGHT_LOG.md` **before** any DO phase begins.

```markdown
## PRE-FLIGHT for <task_id> — <UTC timestamp>

### Inputs
- [ ] All required input files exist
  - <path>: present, sha256=<sha> matches manifest ✓ / ✗
  - <path>: present ✓ / ✗
- [ ] All required upstream tasks marked complete in STATUS.md
  - <task_id>: ✓ / ✗
- [ ] No stale checkpoints from previous incomplete runs of this task
  - <path>: ✗ (good) / ✓ (halt)

### Environment
- [ ] Python version: <version> (required: ≥3.11): ✓ / ✗
- [ ] R version (if applicable): <version>: ✓ / ✗
- [ ] pandas version: <version> (required: ≥2.3): ✓ / ✗
- [ ] pyarrow version: <version> (required: ≥18.0): ✓ / ✗
- [ ] Working directory clean (`git status`): ✓ / ✗
- [ ] On expected branch (`main` or task branch): ✓ / ✗

### Source documentation
- [ ] All NVSR PDFs / NCHS user guides referenced in this task have current SHA-256 matching the relevant `file_inventory.csv`
  - <path>: ✓ / ✗
- [ ] All cited Zenodo DOIs resolve

### Outputs
- [ ] Intended output paths do not exist OR are explicitly marked for overwrite
  - <path>: does not exist (good) / exists, no overwrite mark (HALT)

### Field-value snapshot for cells / rows / columns being mutated

For every canonical artifact this task will mutate (a row in `harmonized_schema.csv`, a cell in a validation-target CSV, a derived column in a parquet, a numeric in a doc), snapshot the **current values of the fields being touched** and verify against the task plan's assumed state. Catches surprises like "task plan said `notes` field has existing prose to append to; actual `notes` is empty" at the cheap-check moment rather than mid-DO. Cost: ~1 minute wall-clock per task; saves Tier-2+ rework when a surprise would otherwise surface during DO.

- [ ] Target rows / cells / columns enumerated:
  - `<file_path> <row_key_or_column_name> <fields_being_mutated>`
- [ ] Current values match task plan's assumed state ✓ / ✗
  - If ✗: name the divergence; resolve at this cheap-check moment by amending the task plan OR halting and asking the human. Do not silently proceed under the divergent state.

### Halt conditions tripped
(list any ✗ above; if any present, do not proceed; ask human)

### Result
PROCEED / HALT
```

---

# §6. RECEIPT template

Write to `RECEIPTS/<task_id>_<UTC_timestamp>.md` after every completed task.

```markdown
# Receipt: <task_id>
## <UTC timestamp>

### What was done
<one-paragraph summary>

### Inputs consumed
- <path>: sha256=<sha>
- <path>: sha256=<sha>

### Outputs produced
- <path>: sha256=<sha>, rows=<n>, cols=<n>
- <path>: sha256=<sha>

### Five-phase trace
- PRE-FLIGHT: ✓ (PRE_FLIGHT_LOG.md timestamp <ts>)
- SMOKE: ✓ (Tier 0/1/2/3/4 results: ...)
- DO: ✓ (commits <sha1>..<sha2>)
- VERIFY: ✓ (criteria below)
- RECEIPT: ✓ (this file)

### Verify results
- <criterion 1>: PASS, value=<v>, threshold=<t>
- <criterion 2>: PASS, value=<v>, threshold=<t>
- <criterion 3>: SOFT-FLAG, escalated to human in DECISION_LOG <ts>

### Reproducibility
- Re-run produces bit-identical output ✓ (sha256 unchanged)
- Or: regression noted, FIX_LOG entry filed

### Cross-product re-probe (if applicable)
- Tasks that depend on this output: re-verified ✓ / N/A

### Git
- Pre-DO tag: `<task_id>-pre-do`, commit=<sha>
- Post-RECEIPT tag: `<task_id>-complete`, commit=<sha>

### STATUS.md updated
- New section dated <ts> marking task complete

### Self-check
What could I have gotten wrong that VERIFY wouldn't catch?
1. <residual risk>
2. <residual risk>
(See §8.)

### Forward-looking HALTs for next session
Caller-written PRE-FLIGHT checks the next session must verify. For each assertion, the next session HALTs if the assertion does not hold. Saves the next session from re-deriving "what would trigger a halt." Token cost paid here; benefit at the next task's PRE-FLIGHT.

- Forward-looking HALT 1: "<assertion>" (e.g., "the linked-file validation CSV sha256 must change in the expected direction after Task 6; if unchanged, the reconciliation edit did not take")
- Forward-looking HALT 2: "<...>"
- Forward-looking HALT N: "<...>" (or `NONE — explicit` if no caller-known HALT applies)

### Notes for next session
<anything the next LLM should know — open follow-ups, soft-flags, deferred items>
```

---

# §7. Halt conditions — when to stop and ask

Halt and write to `STATUS.md` "Open questions for human" rather than working around any of these. Do not proceed even if the human says "just continue" — instead, restate the halt and offer concrete options.

1. **PRE-FLIGHT check fails.**
2. **Smoke test fails at any tier.**
3. **VERIFY criterion not met.**
4. **Per-year *NVSR* count or rate disagreement** beyond documented tolerance.
5. **V1 byte-clean regression**: a previously-stable cell drifts after a change to an adjacent era.
6. **Schema validation failure** on `harmonized_schema.csv` or any metadata file.
7. **Sentinel value treated as data** — a derived indicator returns True/False on a record where the underlying value is a sentinel (99, 999, 9999, blank).
8. **Row counts don't conserve at a join boundary** in a cross-product computation.
9. **R/Python parity failure** if both languages are involved.
10. **Citation cannot be resolved** (PMID/DOI does not exist or returns an unrelated paper).
11. **Source PDF SHA-256 has changed upstream** — NCHS may have re-released the document.
12. **Conflicting documentation** between source PDF, NCHS doc page, and codebook.
13. **Validity-domain ambiguity** — the analytic filter is unclear for a year/era.
14. **A new mistake class** not in the §8 matrix.
15. **Time/cost budget exceeded** for the task.
16. **Output looks plausible but VERIFY is unclear** — soft-flag in DECISION_LOG.
17. **Scope creep** — the task would touch files outside its declared scope.
18. **Reproducibility regression** — re-running a previously-completed task produces different output.
19. **Two harmonized schema columns disagree on a value-level normalization** for the same source field across products.
20. **A documented `within_era` column is being used in a cross-era groupby.**

When in doubt: halt. The cost of asking is one round-trip; the cost of proceeding wrong is rework.

---

# §8. Mistake-class prevention matrix

Each row: the failure mode, the symptom, where in the five-phase structure it gets caught, and the specific catch. Most rows are adapted from the natality `HARMONIZATION_LESSONS.md` and the NHANES protocol. Add new rows as new classes are discovered (per §9).

| # | Class | Symptom | Caught at | Specific catch |
|---|---|---|---|---|
| H1 | Field-position / schema drift | A column 100% null in one year while neighbors look normal | PRE-FLIGHT + Tier 1 smoke | Per-year null-rate report; flag YoY jump > 5pp |
| H2 | Null-propagation in boolean ops | Output silently null where inputs nullable | DO + VERIFY | Always wrap pyarrow `pc.and_` / `pc.or_` with `fill_null(False)`; unit test injects null on each input |
| H3 | Validator self-blindness | Validator says PASS on broken data | Tier 0 + DO | Mutation-test every validator: inject a known violation; assert the validator catches it |
| H4 | Sentinel values treated as data | Implausible values at 99/999/9999/-1; derived flag True for "missing" record | PRE-FLIGHT + Tier 1 | Sentinel dictionary read first; per-column distribution report; sentinels converted to NaN in the derivation step before threshold comparisons |
| H5 | Era-boundary fencepost | Trend knee at non-method-change boundary | Tier 3 | Knee-detection on per-year counts/rates; every knee documented |
| H6 | Silent row drops in joins | Row count drops between stages | DO + VERIFY | Row-count assertion at every stage boundary; assert input = output + documented_drop |
| H7 | Sibling-pipeline drift | Natality and fetal-death pipelines diverge on a shared concept | VERIFY | Both products' harmonized_schema.csv must agree on dtype, allowed_values, comparability_class for any column with the same name |
| H8 | Docs vs data drift | Number in a doc is stale | RECEIPT | Auto-generate every numeric in every doc from the validation CSVs; if a doc number is hand-edited, accompany it with the inline computation it came from |
| H9 | External targets cancel internal bugs | Aggregate matches *NVSR*, internal field broken | Tier 2 + 3 | Validate sex × age × race × Hispanic-stratified aggregates in addition to the overall total |
| H10 | Provenance / reproducibility drift | Re-run produces different output | RECEIPT | SHA-256 in PROVENANCE.md for every shipped artifact; bit-identical reproduction required |
| F1 | Wrong analytic filter applied | Counts off by 5–10% from *NVSR* targets | VERIFY | Each product has exactly one canonical filter (see `docs/JOINT_USE_GUIDE.md`); assert it is applied at load time in every notebook |
| F2 | Cross-product join without filter on both sides | Stratified rate biased upward or downward | Tier 4 + VERIFY | Both numerator AND denominator must apply their canonical filters; row-count assertion before join |
| F3 | Era-name confusion | Code uses "V1" to mean fetal-death-V1-era but applies it to natality | PRE-FLIGHT + Tier 0 | "V1"/"V2" suffixes are fetal-death-specific; natality uses different era nomenclature; never reuse era names across products |
| F4 | Within-era column used cross-era | Cross-era groupby on `breech_unrevised`, `delivery_place_unrevised`, or `maternal_race_bridged_detail` | Tier 0 | Schema's `comparability_class == 'within_era'` columns must trigger a warning if a cross-era operation is attempted |
| F5 | Sentinel not converted before derivation | `low_birthweight=True` for a record with `birthweight=9999` | Tier 0 | Derived-indicator scripts must convert known sentinels to NaN BEFORE the threshold comparison; mutation test asserts a `birthweight=9999` record produces a NaN low-birthweight flag |
| L1 | LLM hallucinated file path | "Edit X.py" — X.py doesn't exist | PRE-FLIGHT | Every target path verified to exist (or explicitly marked as new) before DO |
| L2 | LLM hallucinated function/library | Code references a non-existent API | Tier 0 | Smoke test exercises every imported symbol; `python -c "import x; x.fn()"` before claiming the function exists |
| L3 | LLM rubber-stamps passing test | Test passes but doesn't actually test the claim | Tier 0 + DECISION_LOG | Mutation test required for every validator; LLM must explicitly state what mutation the test catches |
| L4 | LLM forgets to propagate fix to sibling | Fix lands in fetal_death/ only, not natality/ | VERIFY | After any change to a shared concept (column dtype, comparability class, normalization rule), grep both products' `harmonized_schema.csv` to confirm parity |
| L5 | LLM forgets to re-probe adjacent years | Fix regresses a neighboring year | VERIFY | After any harmonization change, re-run validation for the cycle on either side of the changed cycle |
| L6 | LLM invents numbers in docs | Doc says "~1.6 million" — fabricated, not derived from parquets | RECEIPT | Every numeric in every doc must be either auto-generated or accompanied by inline computation (`# computed as: df[df['data_year']==2022].shape[0]`) |
| L7 | LLM accepts plausible-looking output | "Looks right" instead of explicit threshold check | VERIFY | No "looks reasonable" allowed; every VERIFY check has a numeric threshold |
| L8 | Citation does not match the canonical filename's named coauthors | Filename says "Salihu_2004" but the resolved PMID is a different paper | PRE-FLIGHT + SMOKE | Resolve the PMID via NCBI E-utilities; verify authors and title match the filename's implied paper |
| L9 | Walkthrough cites wrong table or page | Build session looks for "Table N page M" and finds something else | PRE-FLIGHT or Tier 0 | Always verify the named source location in the actual PDF before relying on a walkthrough's location text |
| L10 | Back-filled PRE-FLIGHT entry | Multi-sub-step task writes its PRE-FLIGHT mid-task or post-DO | Self-check at receipt drafting | Multi-sub-step tasks require either one upfront PRE-FLIGHT or per-sub-step PRE-FLIGHT; back-fill is forbidden |
| L11 | Stale roadmap claim | Doc says "V4: Natality" but natality is already shipped | RECEIPT | Cross-check VERSION_ROADMAP.md and each subproject's README for "future" items that are actually done; fix on contact |
| L12 | LLM trusts its own grep | LLM says "no other references to X" without verification | DO | Use `git ls-files | xargs grep -n` (not just `grep -r .` which can miss .gitignored or symlinked files) |
| L13 | Inventory CSV records file roles before column-content verification | An inventory / manifest CSV's `role` or `description` field claims a file contains columns A/B/C; downstream PRE-FLIGHT discovers the file actually contains X/Y/Z (different domain entirely); the cheap-check window had closed at the original inventory write | Downstream PRE-FLIGHT (too late for cheap-check at the original PRE-FLIGHT) | At inventory CSV write time, enumerate **columns alongside roles** (open the codebook / SAS layout / column header; record column names so the role label is verifiable). For PDF-only inputs, extract TOC + first 2 pages and verify topical alignment. Any inventory row whose role/description names columns without a sibling column-name list is a soft-flag for downstream consumers to re-verify. |
| L14 | Validation script's per-row failure flag not propagated to process exit code | A reproduction / validation script's per-row CSV has FAIL / `exceeds_tolerance` / `bridge_applicable=False` rows, but `main()` returns 0 (Python: implicit None; R: missing `q(status=1)`); CI / PRE-FLIGHT reads exit code only and reports PASS. Adversarial mutation tests using OR-of-rows aggregation can mask a single-row pre-mutation if other rows independently flag | DO + adversarial mutation testing | At every validation/reproduction script's last `main()` line: `sys.exit(1 if FAIL_COUNT > 0 else 0)` (Python) / `if (n_fail > 0) q(status=1)` (R). Per-row classifier must return non-empty truthy strings (not `""`) so summary aggregation can count. Mutation-runner detectors use **AND-of-rows** (not OR) for family-level verdicts. Defense-in-depth: add Phase-0 cross-CSV invariant comparing fixture metadata to canonical CSVs per row key. |
| L17 | SMOKE / test asset hard-codes a mutable annotation value pinned at authoring time; canonical state evolves; pin becomes stale; SMOKE FAILs on a CORRECT subsequent mutation | A SMOKE harness asserts `field == "<value-at-task-N-authoring-moment>"` for a field whose value is expected to evolve under later authorized tasks (e.g., row count grows when V2.1 adds 2003-2004 records; sha256 changes when a script is correctly edited; harmonized_schema column count grows). The SMOKE FAILs and is treated as a regression when it is in fact stale pinning | VERIFY (focused defense-in-depth re-probe at the cheap-check moment) | (a) SHAPE-not-VALUE convention per §4.2.1: SMOKE asserts STRUCTURAL invariants. (b) When a SMOKE must pin a value, declare `DESIGN: tracks-current-state` vs `DESIGN: frozen-at-<task_id>` on the first docstring line. (c) When canonical-state mutation surfaces stale pinning: bundle the minimal Edit into the same commit as the canonical mutation. |
| L13-ext (year-axis) | A layout reconstructed from ONE source year/guide and value-verified only on anchor fields at one era-year is NOT proven byte-stable for non-anchor fields at OTHER era-years of the same record length | A non-anchor byte re-purposes mid-era (e.g. `RECWT@91` is a clean inflation weight in 1983/85 but byte-identical to `DMRACE@57` in 1988) and is not caught by anchor-only verification at a single year | PRE-FLIGHT Convention-3 read-only real-data probe, per-era-year (NOT anchors + one year). NB: a single ≤5000-row head-sample byte-equality is itself NOT a per-year proof — see LESSONS 2026-05-22 (the 2026-05-20 (A′) head-sample conclusion was FALSIFIED for 1983-1987) | Before harmonize-mapping a multi-year era from a single-year-derived layout, value-distribution-verify EACH year's non-anchor fields (esp. trailing/last-byte) against the source's own file-level NCHS control total — a per-year `byte_i == byte_j` cross-tab or per-year distribution catches a mid-era byte re-purposing. Conservative-NULL the non-byte-stable field; route the full per-year re-verification to the parquet-build + NCHS-validate step. |
| H6-ext (heterogeneous-union) | `pa.Table.from_pylist`/`from_pandas` infers the Arrow schema from the FIRST record's keys only → silent column drop on a heterogeneous-key union | A lossless multi-segment union materialized this way, where segments have DIFFERENT key sets and the narrower segment is yielded first, SILENTLY DROPS the late-arriving segment's columns (or crashes a chunked `ParquetWriter` at the segment boundary) | SMOKE on real data (§9-#9) — assert the late-segment-only columns survive the parse→parquet→read round-trip | Any `from_pylist`/`from_pandas` materialization of a heterogeneous-key stream MUST pass an explicit unified schema (derived from the layout, not from data order); add a SMOKE that round-trips a first-segment-then-second-segment fixture and asserts the second segment's exclusive columns are non-null. |
| L13-ext (shared CSV) | A SHARED targets/inventory CSV is extended at task N with rows a downstream consumer at task M does not own | The consumer crashes (`raise` on an unknown `metric_id`) or mis-computes (applies its owned-era logic to non-owned rows) once the mutated parquet + the extended CSV meet at M (e.g. the v3 linked validator on the 6a-added pre-2005 cohort rows) | PRE-FLIGHT (enumerate downstream consumers of the shared file at write time) / downstream VERIFY | At write time of a shared targets/inventory CSV, enumerate every downstream reader and verify each skips-or-supports non-owned rows: scope each consumer to its owned surface (skip-with-disclosure, not crash, not mis-compute) while keeping the L14 non-zero-exit on its owned surface. |
| L17-ext (grep-scope) | The L17 PRE-FLIGHT grep-scope enumerates only the named release-state pins and misses test-infra shape-derived count literals; split-run summaries can hide a failed count | The grep-scope missed `EXPECTED_*`/`*_TOTAL`/`*_COUNT` literals deriving from a mutated parquet's shape (e.g. `EXPECTED_TOTAL=340`, `EXPECTED_COLUMN_COUNTS[linked]=94`); compounded by a per-file split-run summary printing only the pass count, letting a split run be hand-summed into a false VERIFY pass | VERIFY (authoritative consolidated re-baseline) — should be PRE-FLIGHT | The L17 PRE-FLIGHT grep-scope MUST enumerate test-infra `EXPECTED_*`/`*_TOTAL`/`*_COUNT` literals that derive from a mutated parquet's shape, not only the named release-state pins; the per-file kill/fail-detection harness MUST print each file's full summary incl. the failed count (never hand-summate a split run into a VERIFY pass). |

If a new mistake class is encountered: append to `LESSONS.md` with the date, file references, what failed, what worked. Propose a new row for this matrix. Halt for human approval before continuing if the lesson reveals a bug in already-completed work.

---

# §9. LLM-specific anti-patterns to refuse

Hard rules. Do not do these. If a human asks for one, raise the concern explicitly and propose an alternative.

1. **Never edit a state file by overwriting.** Append-only. New row supersedes.
2. **Never write a numeric value into a doc by hand without an inline computation comment.** If you write "1,634,195 records," follow it with `<!-- computed as: df.shape[0] for fetal_death_derived.parquet, see RECEIPTS/<id> -->` or auto-generate from a script.
3. **Never proceed past a halt condition.** Even if the human says "just continue." Reframe: "halt was tripped because X — to proceed, options A/B/C; which?"
4. **Never silently swap in a fallback.** A `try/except` that hides an error is not a fix.
5. **Never accept a passing test as evidence the test is right.** Mutation-test the test.
6. **Never edit `harmonized_schema.csv` without bumping the schema version OR adding a comment row referencing the relevant DECISION_LOG entry.**
7. **Never patch a downstream artifact to match a buggy upstream.** Fix the root cause; re-run the pipeline.
8. **Never compress two tasks into one because "they go together."** Each task gets its own PRE-FLIGHT, SMOKE, VERIFY, RECEIPT.
9. **Never write code without first writing the fixture it must pass.**
10. **Never delete a checkpoint, git tag, or RECEIPTS/ file** even if it looks redundant.
11. **Never trust your own grep.** Use `git ls-files | xargs grep -n` so you cannot miss tracked files.
12. **Never run a destructive action without a dry-run first.** `rm -rf`, `git reset --hard`, `pip uninstall` all require dry-run output first.
13. **Never advance `STATUS.md` to "task complete" without a corresponding receipt file.**
14. **Never carry assumptions across sessions silently.** Re-read STATUS.md, last 10 DECISION_LOG entries, last 5 FIX_LOG entries, all of LESSONS.md at session start.
15. **Never modify the existing Zenodo deposits' published artifacts.** They are persistent. Bug fixes go in a new version with a new DOI.

---

# §10. The self-check question

Before claiming a task is complete, answer this in writing in the receipt's "Self-check" section: **what could I have gotten wrong that the VERIFY phase wouldn't catch?**

Examples for HVS:

- I could have applied the canonical filter on the numerator but forgotten it on the denominator.
- I could have transcribed correct *NVSR* numbers but assigned them to the wrong year.
- The PDF could have been silently updated by NCHS and my SHA-256 manifest is stale.
- I could have used the wrong era's bridge for the wrong era's data (the V2 5-category collapse applied to a V1 record).
- The "cross-product alignment" claim might be true for race but false for Hispanic origin because of the Oklahoma 1992–2002 non-reporting quirk.
- I could have used the linked file's `recwt` column when the analytic question requires the `wt` column (or vice versa).
- I could have computed fetal mortality rate per 1,000 live births when the standard is per 1,000 (live births + fetal deaths).

Each "could have gotten wrong" gets logged in `DECISION_LOG.md` as a residual risk. If the risk is plausible enough to investigate, propose an additional check; ask the human before adding it to VERIFY.

This question is load-bearing. It forces the LLM out of the rubber-stamp mode that the natality `HARMONIZATION_LESSONS.md` warns about.

---

# §11. Plan-update process

This document and `VERSION_ROADMAP.md` are not frozen. When a new mistake class, ambiguity, or improved technique is discovered:

1. **Append to `LESSONS.md`** with date, file references, what failed, what worked.
2. **Propose the plan amendment** — write the proposed change to this file or to VERSION_ROADMAP.md as a diff. Do not edit the plan until the human approves.
3. **Human review and merge** — human approves; LLM applies the diff; commit with `[plan-update]` prefix.
4. **Backport** — if the lesson reveals a bug in already-completed work, retroactively re-verify affected tasks. If they fail re-verify, file in `FIX_LOG.md` and roll back to the relevant git tag.

The plan is a living document, but only the human merges changes.

---

# §12. Session start / session end checklists

## Session start
1. Read [`STATUS.md`](STATUS.md). Identify current task, last completed task, blocks, open questions.
2. Read the last 10 entries of [`DECISION_LOG.md`](DECISION_LOG.md).
3. Read the last 5 entries of [`FIX_LOG.md`](FIX_LOG.md).
4. Read [`LESSONS.md`](LESSONS.md) end-to-end.
5. Verify state files are not corrupted (well-formed markdown).
6. Verify git working directory is clean (`git status`). If not, ask human about uncommitted changes before doing anything.
7. Verify expected branch.
8. Confirm the previous task's PRE-FLIGHT entry timestamp precedes that task's first DO commit (per L10). If a back-fill is detected, file an L10 entry forensically and propose remediation BEFORE starting the next task.
9. Tell the human (a) current task, (b) open questions, (c) what you propose to do, (d) any halt tripped.
10. Wait for confirmation before starting work.

## Session end
1. Update `STATUS.md` with a new dated section at the top: current state, in-progress, next planned task, open questions for human.
2. Commit all changes with a descriptive message.
3. Tag git if a task completed in this session.
4. Confirm all `RECEIPTS/` files are present for tasks marked complete in STATUS.md.
5. Note in the STATUS.md session-end summary anything the next session must know.

---

# §13. Quick reference — what the LLM does at every task

```
1. Read STATUS.md → identify next task
2. Run PRE-FLIGHT checklist → halt if any ✗
3. Run SMOKE tests (Tier 0, 1, 2, 3, 4 as relevant) → halt if any tier fails
4. Tag `<task_id>-pre-do` and DO the operation
5. Run VERIFY criteria → halt if any not met
6. Write RECEIPT to RECEIPTS/<task_id>_<UTC_timestamp>.md
7. Update STATUS.md
8. Tag `<task_id>-complete`
9. Write Self-check in receipt: "what could I have gotten wrong"
10. (If new lesson) update LESSONS.md and propose plan update
11. Move to next task
```

If steps 2–9 trigger a halt: stop, write to STATUS.md "Open questions for human", do not advance.

---

---

# §14. Project context (what HVS is, why it exists)

The U.S. National Center for Health Statistics (NCHS) releases public-use natality, linked birth–infant death, and fetal death microdata as annual fixed-width files whose layouts have changed multiple times. Three boundary types make cross-year analyses difficult: (i) the 1989-to-2003 U.S. Standard Certificate revision; (ii) within-revision NCHS reformats; (iii) state-by-state staggered adoption of the 2003 revision. Researchers have historically been forced into single-revision analytic windows (see [`docs/PRIOR_ART.md`](docs/PRIOR_ART.md)).

This resource integrates and disseminates the three NCHS public-use microdata products as three companion harmonized parquet files with one stable column schema per product, validated against every per-year aggregate NCHS publishes in the relevant *National Vital Statistics Reports* (*NVSR*) series.

**Three products (current state, as of 2026-05-09):**

| Product | Coverage | Records | Columns | NVSR validation |
|---|---|---|---|---|
| Natality | 1990–2024 | 138,819,655 | 84 | 183/183 byte-exact |
| Linked birth–infant death | 2005–2023 | 74,943,824 | 94 | 33/35 byte-exact + 2 cells differ by 1 record (within tolerance; resolved Task 6 2026-05-11) |
| Fetal death | 1992–2022 (excl. 2003–2004) | 1,634,195 | 89 | 29/29 counts + 26/26 rates exact; 13/19 detail-cell + 6 docs diffs |

**Repository state (as of 2026-05-09):**
- Initial monorepo migration committed at `7fd9cdf`.
- `natality/` mirrors v2.7.0 of yoelplutchok/natality-harmonization.
- `fetal_death/` mirrors v2.0.1 of yoelplutchok/fetal-death-harmonization (large parquets and the per-year raw zip are .gitignored; they live in Zenodo).
- Both original GitHub repos are unchanged. The user plans a new unified Zenodo deposit anchored to this monorepo.

---

# §15. Tasks, in priority order

Each task is a five-phase unit per §4. The fields below specify the PRE-FLIGHT inputs, the SMOKE plan, the DO scope, the VERIFY criteria, and the RECEIPT requirement.

---

### Task 1 — Joint-use convenience layer (stratified live-birth denominators)

**Goal.** Ship a single parquet (or CSV) inside the fetal-death deposit that gives demographically stratified live-birth counts by year, so users can compute fetal mortality rates by race × age × ethnicity without loading the 138.8M-row natality file.

**Why this matters.** The manuscript's strongest claim is the three products are "designed for joint use." Listed in `VERSION_ROADMAP.md` as the joint-use convenience layer.

**PRE-FLIGHT inputs.**
- Natality derived parquet (download from Zenodo DOI 10.5281/zenodo.19868835 or build via `natality/scripts/`).
- `natality/metadata/harmonized_schema.csv` (verify columns `data_year`, `maternal_age`, `maternal_race_bridged`, `hispanic_origin`, `restatus` exist with expected dtypes).
- `fetal_death/harmonized_schema.csv` (verify the same column names and dtypes for join compatibility — F3, H7, L4 in §8).

**SMOKE plan.**
- Tier 0: 5 hand-constructed natality rows; group by 2 race × 2 age × 1 year; assert correct counts.
- Tier 1: 100 real natality rows from 2022; assert grouping returns plausible (no nulls, all races represented).
- Tier 2: full 2022 natality; assert sum across strata matches *NVSR 73-11* total live births for 2022.

**DO scope.**
- Write `shared/helpers/build_stratified_denominators.py`.
- Apply canonical filter `restatus != '4'` (F1 in §8).
- Group by `data_year` × `maternal_age_band` × `maternal_race_bridged` × `hispanic_origin`.
- Output `fetal_death/stratified_denominators.parquet` (long format).
- Document in `fetal_death/CODEBOOK.md` and `docs/JOINT_USE_GUIDE.md`.

**VERIFY criteria.**
- Sum across strata for each year matches the unstratified count in `fetal_death/live_births_by_year.csv` exactly.
- Spot-check 5 cells against published *NVSR* tables (e.g., *NVSR 73(11)* Table 1 race × year cells).
- Re-running `build_stratified_denominators.py` produces a bit-identical output.

**RECEIPT requirement.** Standard template; explicitly answer self-check question. Note in "what could I have gotten wrong": did I apply `restatus != '4'`? did I use the same age-binning convention as fetal_death? did I handle the V2 fetal-death era's state reporting quirks (Oklahoma Hispanic, Maryland/Massachusetts early years)?

**Estimated effort.** Half a session if natality parquet is on disk; one session if it has to be downloaded.

**Dependencies.** None.

**Halt-condition flags for this task.** F1, F2, H6, H9 are the most likely catches.

---

### Task 2 — `notebooks/joint_use_demo.ipynb`

**Shipped 2026-05-11 with PRE-FLIGHT-amended scope** (Section A 2022 by maternal age vs *NVSR 73-09* Table 4, 8/8 cells byte-exact; Section B 2017 by maternal race, joint-use machinery demo; Section B NVSR cell-level validation absorbed into Task 4). The original-intent text below is preserved for audit; see `RECEIPTS/task2_joint_use_demo_2026-05-11T18-51-59Z.md` for the canonical record of what shipped and why the scope was amended at PRE-FLIGHT.

**Goal.** A runnable Jupyter notebook that loads all three parquets, applies each canonical filter, joins on demographic strata, computes the fetal mortality rate per 1,000 (live births + fetal deaths) by maternal race for 2022, and matches each cell against *NVSR 73-09* Table A.

**Why this matters.** Demonstrates the manuscript's "designed for joint use" claim from outside the manuscript.

**PRE-FLIGHT inputs.**
- Pseudocode in `docs/JOINT_USE_GUIDE.md` ("Worked example: fetal mortality rate by maternal race, 2022").
- All three parquets accessible.
- *NVSR 73-09* Table A figures (already encoded in `fetal_death/external_validation_targets.csv` for the unstratified case; stratified targets need to be transcribed from the PDF — apply L9 cheap-check).

**SMOKE plan.**
- Tier 0: Apply `tabulation_flag == '2'` and `restatus != '4'` to a 10-row hand-constructed input; assert correct subset.
- Tier 1: Single race stratum 2022; compute rate; spot-check against NVSR.
- Tier 4: Full 2022 cross-product with all three parquets.

**DO scope.**
- Build the notebook from the pseudocode in `docs/JOINT_USE_GUIDE.md`.
- Save with executed outputs.

**VERIFY criteria.**
- Notebook runs end-to-end without manual intervention.
- Every per-race cell matches *NVSR 73-09* Table A within rounding.
- Pass/fail table at the bottom of the notebook is all PASS, or any FAIL is documented and matches the existing 6 documented diffs in the fetal-death validation.

**RECEIPT requirement.** Standard. Self-check: did I use the right NVSR rate base (per 1,000 (live births + fetal deaths), NOT per 1,000 live births)?

**Estimated effort.** Half a session.

**Dependencies.** Task 1 helpful but not required.

**Halt-condition flags.** F1, F2, F4, H9.

---

### Task 3 — Fetal-death V2.1 (add 2003 and 2004 transition years)

**Goal.** Bring fetal-death coverage to 1992–2022 (31 consecutive years) by parsing and harmonizing the two transition years currently deferred.

**PRE-FLIGHT inputs.**
- 2003 fetal-death zip from NCHS FTP (1351-byte records).
- 2004 fetal-death zip from NCHS FTP (1501-byte records).
- `fetaldeath0304problems.pdf` from NCHS FTP.
- Existing parser at `fetal_death/scripts/01_import/parse_fetal_year.py`.
- Existing record-layout CSVs (1992, 2006); reconstruct 2003 and 2004 from NCHS user guides.

**SMOKE plan.**
- Tier 0: 5 hand-constructed records per layout (one per state-version combination).
- Tier 1: 100 records per year per state-version branch.
- Tier 2: Full 2003 and 2004 separately; per-year count match against *NVSR 57-08* Table B.
- Tier 3: 1992–2022 multi-year trend with 2003 and 2004 inserted; check no knee at the boundary.

**DO scope.**
- Reconstruct `fetal_death/record_layout_2003.csv` and `record_layout_2004.csv`.
- Extend `field_specs.py` for transition layouts.
- Per-state branch on the version-byte (A vs S) to dispatch to the right schema.
- Apply existing B1–B6 normalizations.
- Re-run all validation.
- Bump fetal-death version to v2.1.0; update `.zenodo.json`, `CITATION.cff`, `ABOUT_THIS_RELEASE.md`, `README.md`, `COMPARABILITY.md`, `FAQ.md`.

**VERIFY criteria.**
- 2003 and 2004 per-year counts match *NVSR 57-08* Table B exactly.
- V1 era (2005–2022) byte-clean: 0/73 harmonized + 0/89 derived columns drift after the V2.1 extension (per L5).
- Total per-year counts: 31/31 exact (was 29/29).
- Total per-year fetal mortality rates: 28/28 exact (was 26/26).

**RECEIPT requirement.** Standard. Self-check: did I correctly distinguish per-state which records use 1989-revision vs 2003-revision schema in 2003 and 2004? Did I re-run the 2005 validation to confirm V1 baseline holds?

**Estimated effort.** One to two sessions.

**Dependencies.** None for inputs; orthogonal to Tasks 1, 2.

**Halt-condition flags.** H1, H5, H6, F3, F5, L5.

---

### Task 4 — `notebooks/paper_companion.ipynb`

**Goal.** A notebook that reproduces every numeric claim in the manuscript directly from the parquets, with each cell mapped to the paper paragraph it supports. **Also absorbs Section B NVSR cell-level validation deferred from Task 2** (2017 fetal mortality rate by maternal race, validated against the appropriate per-year NVSR fetal-mortality table; PDF-source location to be verified at Task 4 PRE-FLIGHT per L9 cheap-check).

**PRE-FLIGHT inputs.** Current preferred manuscript at `paper/draft_v2_hmd_styled.md`. All three parquets.

**SMOKE plan.**
- Tier 0: Reproduce one explicit number (e.g., 1,634,195 fetal-death records) from the parquet.

**DO scope.**
- Walk through the manuscript and extract every numeric claim with paragraph reference.
- For each claim, write a notebook cell that computes the value from the relevant artifact.
- Final markdown pass/fail table.

**VERIFY criteria.**
- Every cell matches the paper. If any cell does not, fix the paper.

**RECEIPT requirement.** Standard. Self-check: did I check every number, or just the easy ones?

**Estimated effort.** One session.

**Dependencies.** Task 5 (manuscript stable) ideally precedes or runs alongside.

**Halt-condition flags.** L6.

---

### Task 5 — Manuscript trim and admin sections

**Goal.** Bring `paper/draft_v2_hmd_styled.md` to the IJE main-text limit of 2,500 words; fill in admin sections (Author contributions, AI-tool disclosure, Funding); finalize references.

**PRE-FLIGHT inputs.** Current draft. IJE author guidelines (see `paper/README.md` for the section list and word limit).

**SMOKE plan.** Word-count the current draft per section before and after edits.

**DO scope.**
- Trim Strengths and Weaknesses (longest section, currently ~1,000 words; aim for 600).
- Move the 19-detail-cell breakdown to a supplementary table.
- Trim the V2-era reporting-quirk paragraph to a footnote or supplementary note.
- Add a *Companion paper* sentence pointing to the monorepo and Task 2's notebook.
- Fill Ethics approval, Author contributions, AI-tool disclosure, Conflict of interest, Funding.
- Format references to journal style.

**VERIFY criteria.**
- Main text ≤ 2,500 words excluding abstract, Key Features, references, tables, supplementary.
- All required IJE sections present.
- All admin sections filled.

**RECEIPT requirement.** Standard. Self-check: did I trim substantive content or just filler? Did the trimmed paragraphs lose claims that the manuscript depends on?

**Estimated effort.** One session.

**Dependencies.** Task 6 should resolve before final word-count freeze.

**Halt-condition flags.** L11.

---

### Task 6 — Verify and reconcile linked-file validation framing

**Goal.** Resolve a discrepancy between the natality README ("35/35 V3 linked targets pass") and the manuscript drafts ("33 of 35 byte-exact, two cells differ by exactly one record each because of NCHS upstream survivor records with null record weights").

**PRE-FLIGHT inputs.**
- `natality/README.md` (current language).
- `natality/output/validation/external_validation_v3_linked_comparison.md` and `.csv` (authoritative).
- Manuscript drafts in `paper/`.

**SMOKE plan.** Read the validation comparison file; count PASS rows.

**DO scope.**
- Determine actual current state: 35/35, or 33/35 + 2 docs?
- Update either the natality README or the manuscript drafts to match.
- Note the canonical framing in `paper/README.md`.

**VERIFY criteria.**
- The natality README, top-level monorepo README, manuscript draft, and validation CSV all agree.

**RECEIPT requirement.** Standard. DECISION_LOG entry recording which framing is canonical and why.

**Estimated effort.** 15–30 minutes.

**Dependencies.** None. Should precede Task 5.

**Halt-condition flags.** L11, H8.

---

### Task 7 — Fetal-death V3 (extend backward to 1982)

**Goal.** Bring fetal-death coverage to 1982–2022 (41 years) by parsing the 1978-revision (1982–1988) and early 1989-revision (1989–1991) layouts.

**PRE-FLIGHT inputs.**
- 1982–1991 fetal-death zips from NCHS FTP.
- NCHS user guides for those years (some may only be scanned PDFs; OCR may be needed).
- 1978-revision Standard Report of Fetal Death documentation.

**SMOKE plan.** Same Tier 0–3 ladder as Task 3. Plus an extra Tier 0 for OCR sanity if guides are scanned.

**DO scope.** Parallel to Task 3; multiple eras instead of two.

**VERIFY criteria.**
- Per-year counts match user-guide control counts for years where guides ship clean control counts.
- 1992–2022 slice byte-clean regression after V3 extension (per L5).

**RECEIPT requirement.** Standard.

**Estimated effort.** Two to four sessions.

**Dependencies.** Task 3 should ship first (cleaner versioning, V2.1 layout work serves as precedent).

**Halt-condition flags.** All of Task 3's, plus L9 for older PDFs that may have transcription pitfalls.

---

### Task 8 — Cross-product timeline figure

**Goal.** A single figure showing all three products' coverage on one timeline with era boundaries.

**PRE-FLIGHT inputs.** `natality/figures/fig2_timeline.{pdf,png}` for reference. Era-boundary metadata in each subproject's COMPARABILITY.

**SMOKE plan.** Tier 0: render a 1-row test timeline; verify era bands appear at correct years.

**DO scope.** Build `shared/helpers/build_timeline_figure.py`. Save `figures/fig1_coverage_timeline.{pdf,png}`.

**VERIFY criteria.** Era boundaries match COMPARABILITY documentation in both subprojects.

**Estimated effort.** Half a session.

**Dependencies.** None.

**Halt-condition flags.** H8 (era-boundary documentation drift).

---

### Task 9 — Update old GitHub repos with redirect notices

**Goal.** Add a notice block to the top of each old repo's README pointing to this monorepo.

**PRE-FLIGHT inputs.** Existing READMEs in both old repos. This monorepo pushed to GitHub.

**SMOKE plan.** Tier 0: render the proposed notice block in markdown and check it looks right.

**DO scope.** Add notice; commit; push. Optionally archive the old repos (but **only after explicit user approval** — archiving is hard to reverse).

**VERIFY criteria.** Both old repos render the notice at the top.

**Estimated effort.** 15–30 minutes.

**Dependencies.** This monorepo must be pushed to GitHub first.

**Halt-condition flags.** None unique.

---

### Task 10 — Set up unified Zenodo deposit

**Goal.** Publish a new unified Zenodo deposit covering all three products under the HVS umbrella.

**PRE-FLIGHT inputs.** This monorepo. Existing two `.zenodo.json` files. Tasks 1–6 ideally complete.

**SMOKE plan.** Validate `.zenodo.json` schema before upload.

**DO scope.**
- Write top-level `.zenodo.json` describing the unified resource. Include both subproject DOIs as `isPartOf` related identifiers.
- Reserve the DOI in advance and inject it into the manuscript before final submission.
- Update top-level `CITATION.cff` and `README.md` with the new DOI.
- Update both legacy Zenodo deposits' descriptions with a note pointing to the new one.

**VERIFY criteria.**
- New Zenodo DOI resolves to the deposit.
- Concept DOI resolves to latest version.
- Old deposits still resolve and have the redirect notice.

**Estimated effort.** One session, plus user time for the Zenodo upload.

**Dependencies.** Tasks 1–6 done; Task 9 done.

**Halt-condition flags.** L11.

---

# §15.C Phase C tasks (authorized 2026-05-12 per `EXPLORATION_REPORT.md` Q35 = Tier 1+2)

The C8.X entries below were appended at the `phase-c-authorized` `[plan-update]` commit (`DECISION_LOG.md` 2026-05-12T21:00:00Z). Tier 1 = C8.1-C8.8 (pre-Phase-D must-haves). Tier 2 = C8.9-C8.15 (high-value additions). Each task uses the §4 five-phase discipline; halts on any §7 condition; tagged `<task_id>-pre-do` and `<task_id>-complete`.

---

### Task C8.1 — Smoke retag + dtype parity (B.1 + B.2)

**Goal.** (i) Repin `fetal_death/tests/test_release_smoke.py` to post-V3b state with Convention 2 `DESIGN: tracks-current-state` first-docstring tag; (ii) fix monorepo path drift in the test fixtures + the `_regenerate_schema_years.py` import (analog of FIX_LOG 2026-05-12T01:30Z); (iii) author `fetal_death/tests/test_schema_dtype_parity.py` + `natality/tests/test_schema_dtype_parity.py` to enforce every `harmonized_schema.csv` `type` row matches the parquet's pyarrow dtype (durable H8 defense per FIX_LOG 2026-05-11T18:50Z follow-up).

**Why this matters.** The existing smoke pins V2.0 row count = 1,634,195 (current = 2,352,011) and 29-yr year set; **runs FAIL on the V3b parquet today.** This is a textbook L17 stale-pin case; the smoke also currently `ImportError`s in the monorepo because its `_regenerate_schema_years` import resolves to a path that exists only in the standalone build dir. Plus the v2.0 H8 incident (5 demographic columns shipped as `object` while schema declared `int`, FIX_LOG 2026-05-11T18:50Z) explicitly recommended a `tests/test_schema_dtype_parity.py` as the durable defense; it was never written. C8.1 closes both loops in one task.

**PRE-FLIGHT inputs.**
- Existing `fetal_death/tests/test_release_smoke.py` (smoke under repair) + `fetal_death/tests/conftest.py` (path-drift target).
- Standalone-build `scripts/_regenerate_schema_years.py` (source of `compute_years_available()` helper; needs monorepo copy or import path fix).
- Post-V3b parquet at monorepo `output/harmonized/fetal_death_{harmonized,derived}.parquet` (SHAs `e3d6c64abcb7762d…` / `4d1b37cc3a214eea…` per STATUS 20:30Z FL-HALTs 7-8).
- `fetal_death/harmonized_schema.csv` (current SHA `69f92bf775251f1e…`, 73 rows; post-V3b state per STATUS 18:45Z) for dtype parity.
- `natality/metadata/harmonized_schema.csv` for natality-side dtype parity.
- Natality v2.8.0 derived parquet (monorepo `output/...` or per natality build-dir symlink).
- Field-value snapshot (Convention 3) of:
  - `test_release_smoke.py` EXPECTED_ROW_COUNT, EXPECTED_YEARS, EXPECTED_YEAR_ROWS dict.
  - `conftest.py` HARMONIZED_PARQUET / DERIVED_PARQUET / SCHEMA_CSV paths.
  - smoke module-level `_SCRIPTS_DIR` path.

**SMOKE plan.**
- Tier 0 (mutation-test of the new dtype parity assertion): inject a known dtype mismatch (e.g., temporarily edit a copy of `harmonized_schema.csv` to claim `type=int` for a string column); assert the parity test fails. Restore the canonical schema.
- Tier 1: run the retagged smoke against the V3b parquet on a clean checkout; expect 100% PASS (9/9 tests + new dtype-parity test).
- Tier 2: confirm SHAPE assertions (column counts 73 + 89; year-set membership; B-PUB-3 invariant; B4 paternal_age_recode11 no-residue; NVSR_2010 anchor 24,258) are unchanged by the retag — they were always SHAPE-class and must remain so.

**DO scope.** Three commits within the task:

1. **DO-1 path drift fix**: copy `scripts/_regenerate_schema_years.py` from the standalone build dir into `fetal_death/scripts/` (the monorepo's canonical scripts location). Update `conftest.py` parquet/schema constants to point at monorepo-canonical paths (parquets resolve via the `output/` symlink at monorepo root; schema CSV at `fetal_death/harmonized_schema.csv` not `fetal_death/metadata/harmonized_schema.csv` per the existing flat layout).

2. **DO-2 smoke retag**: edit `test_release_smoke.py`:
   - Add `DESIGN: tracks-current-state` on the first docstring line (Convention 2).
   - Repin: `EXPECTED_ROW_COUNT = 2_352_011`; `EXPECTED_YEARS = tuple(range(1982, 2023))` (41 contiguous years 1982-2022).
   - Rewrite `EXPECTED_YEAR_ROWS` with all 41 years from STATUS 18:45Z per-year counts.
   - Update test 5 to assert version_flag='S' across **1982-2002** (V3b + V3a + V2 eras, all synthesized 'S' per harmonize.py era branches); explicitly EXCLUDE 2003-2004 (V2.1 transition; mixed A/S) and 2005+ (V1; native A/S).
   - Re-verify the NVSR_2010 anchor against the V3b parquet (B7 TABFLG correction may have shifted the count; if shifted, this is an EXPECTED tracks-current-state update with a DECISION_LOG soft-flag).
   - Update module-level + per-test docstrings to mention V3b state.

3. **DO-3 dtype parity test**:
   - Author `fetal_death/tests/test_schema_dtype_parity.py` with `DESIGN: tracks-current-state` first-docstring tag. Reads `harmonized_schema.csv`; reads each parquet column's pyarrow `physical_type` + `logical_type`; asserts the schema's `type` field maps to the actual dtype (e.g., schema `int` matches Int8/Int16/Int32/Int64; schema `str` matches `string` or `binary`; schema `float` matches `float32/64`).
   - Author `natality/tests/test_schema_dtype_parity.py` analog (natality columns; same DESIGN tag).
   - Both harnesses include a Tier-0 mutation-test docstring documenting which specific dtype-mismatch they catch (e.g., "if `tabulation_flag` ships as `object` while schema declares `int`, this test FAILs at row N").

**VERIFY criteria.**
- `pytest fetal_death/tests/` returns 100% PASS (9 existing + 1 new = 10 tests).
- `pytest natality/tests/` returns 100% PASS (1 new test; natality previously had 0).
- The new dtype-parity tests catch the mutation injected in Tier-0 SMOKE (and PASS on canonical schemas).
- Re-running the full suite produces identical output (idempotent).
- Existing v2.0/V2.1/V3a baseline parquets still load correctly under the new conftest paths (forward-stability anchor still valid).

**RECEIPT requirement.** Standard template + Forward-looking HALTs covering: new smoke + dtype-parity SHAs; conftest SHA post-path-fix; the EXPECTED_YEAR_ROWS dict's tracks-current-state status (will need re-update at every future data-extension task — flag this in the FL-HALT).

**Estimated effort.** 1.5 sessions (DO-1 ~0.3, DO-2 ~0.5, DO-3 ~0.7).

**Dependencies.** None upstream. C8.6 (CI wiring) depends on this.

**Halt-condition flags.** L13 (path-drift extension to test harness), L17 (smoke-pin shift), H8 (schema-data dtype drift this defends against). Convention 1 SHAPE-not-VALUE retained where structural; Convention 2 DESIGN tag added.

---

### Task C8.2 — Latest-year refresh (fetal death 2023+2024) — FETAL-ONLY

**Re-scoped 2026-05-12T22:30:00Z at PRE-FLIGHT.** Original §15 entry covered fetal-death 2023+2024 + linked 2024 (DECISION_LOG 2026-05-12T21:00:00Z). C8.2 PRE-FLIGHT discovered that the linked-file portion was a no-op (`2024PE2023CO.zip` is cohort year **2023**, already imported as `2023_linked` in `natality/metadata/file_inventory.csv`; NCHS naming pattern is `period`PE`cohort`CO, not `year`PE`prev`CO; the cohort-2024 file `2025PE2024CO.zip` does not yet exist — HTTP 404). User authorized re-scope to fetal-only at 2026-05-12T22:30Z (DECISION_LOG 2026-05-12T22:30:00Z). Linked-2024-cohort refresh deferred to a future task triggered when NCHS publishes `2025PE2024CO.zip` (estimated 2027-Q1 by annual cadence).

**Goal.** Extend fetal-death from 1982-2022 (41 yrs) to **1982-2024 (43 yrs)** by parsing the two newly-released NCHS public-use files. Natality stays at 1990-2024 (NCHS Natality 2025 not yet released; expected ≈Aug-Oct 2026). Linked stays at 2005-2023 (most-recent NCHS public-use cohort).

**Why this matters.** Cheapest pre-submission data win identified by Phase B (`EXPLORATION_REPORT.md` §A.1, fetal-only portion). Two NCHS source files released **after** the most recent HVS shipment:
- `Fetal2023US_COD.zip` (NCHS released 2024-12-05; 2,219,550 B; verified HTTP 200 at C8.2 PRE-FLIGHT)
- `Fetal2024US_COD.zip` (NCHS released 2026-02-04; 1,925,286 B; verified HTTP 200 at C8.2 PRE-FLIGHT)

Both are sibling-layout extensions of the post-2017 V1-era COD layout already parsed. Layout-byte delta vs 2022 expected to be ≤1 byte/column if any (NCHS rarely reorders within a release series). Will be confirmed at SMOKE Tier 0 via `page.get_text()` PDF text-layer probe (per LESSONS L12-extension 2026-05-12T15:00:00Z) of both 2023 and 2024 user guides against the on-disk 2022 sibling.

**PRE-FLIGHT inputs (recorded in PRE_FLIGHT_LOG entry 2026-05-12T22:30:00Z).**
- 2 NCHS source zip URLs (verified HTTP 200 + sizes + Last-Modified + ETags at PRE-FLIGHT).
- 2 user-guide PDFs at the **corrected URL** `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/fetaldeath/{2023,2024}fetaluserguide.pdf` (NOT `fetaldeathus/`; NCHS reorganized between the 2022 and 2023 releases). SHAs recorded.
- Existing parser `fetal_death/scripts/01_import/parse_fetal_year.py` + `field_specs.py` (post-V3b SHAs recorded in PRE-FLIGHT).
- Existing 2022 fetal user guide on disk (`raw_docs/fetal_death/2022fetaluserguide.pdf` sha=`d515813f89765af0…`) — sibling-byte-position diff anchor for 2023+2024.
- Field-value snapshot (Convention 3): `fetal_death/file_inventory.csv` (current 32 rows; plan adds 2), `fetal_death/external_validation_targets.csv` (current 84 rows; plan adds 2), `fetal_death/harmonized_schema.csv` `years_available` cells (plan regenerates via `_regenerate_schema_years.py`), parquet SHAs.

**SMOKE plan.**
- Tier 0: byte-position diff between 2024 fetal user guide and 2022 (sibling-derive via `page.get_text()`). Per L13-extension, value-distribution sanity-check 5 anchor fields after parse (TABFLG, RESTATUS, DOD_YY, MAGER, MRACEREC).
- Tier 1: 100-record parse of 2024 fetal-death; assert plausible distribution (no unexpected nulls).
- Tier 2: full-year 2023 + 2024 fetal-death parse; per-year control-count match against user-guide page-7 control counts.
- Tier 3: 1982-2024 re-harmonize; V3b-era byte-clean regression (0/162 column drift on 1982-2022 slice vs current parquet).

(Tier 4 linked smoke removed under re-scope.)

**DO scope.**
1. Download 2 source zips + 2 user-guide PDFs to `raw_data/fetal_death/` + `raw_docs/fetal_death/`; record SHAs.
2. Probe layout-byte deltas vs the 2022 sibling. If no delta: reuse existing era_tag. If delta: extend `field_specs.py` with new era_tag + DECISION_LOG entry.
3. Add 2 rows to `fetal_death/file_inventory.csv` (2023, 2024); 2 rows to `fetal_death/external_validation_targets.csv` (one per new year); regenerate `harmonized_schema.csv` `years_available` via `_regenerate_schema_years.py` (auto-derived; no version bump required per DECISION_LOG 2026-05-12T22:00:00Z precedent).
4. Re-harmonize + re-derive fetal-death parquet (now 1982-2024); preserve V3b parquet as a `.V3b_baseline.parquet` forward-stability anchor.
5. Bump fetal-death version v2.3.0 → v2.4.0.
6. Update CITATION.cff + .zenodo.json + ABOUT_THIS_RELEASE.md + README.md (fetal-death only). Natality + linked version files unchanged.
7. Refresh smoke EXPECTED_ROW_COUNT + EXPECTED_YEARS + EXPECTED_YEAR_ROWS (C8.1 smoke pins under tracks-current-state — explicit re-pin).

(Original DO step 5 "re-harmonize linked parquet" removed under re-scope.)

**VERIFY criteria.**
- Per-year fetal counts 2023+2024 match user-guide control counts byte-exact.
- V3b baseline byte-clean regression: 0/162 columns drift on 1982-2022 slice (anchor preserved per L5).
- C8.1's updated dtype-parity test PASSes on the v2.4.0 parquet.
- External validation count: 88/88 → 90/90 (fetal +2 counts).

(Linked verification criteria removed.)

**RECEIPT requirement.** Standard. Self-check: did I re-run V3b baseline byte-clean comparison after the re-harmonize? Did I correctly omit linked-file work per the re-scope? Did I update the manuscript's pipeline-timing claims if the wall-clock materially changed?

**Estimated effort.** **1 session** (revised from 1-2 under re-scope; linked-file work was ~50% of the original scope).

**Dependencies.** None. Recommended FIRST Phase C data task (Q37) since it predates any test/CI scaffolding work — subsequent tests gate on the extended envelope.

**Halt-condition flags.** H1, L13 (if layout-byte delta surfaces vs 2022 sibling), L17 (SMOKE pin shifts post-refresh — handled by C8.1's `DESIGN: tracks-current-state` tag). Convention 1 SHAPE-not-VALUE on every new SMOKE.

**Forward-looking HALTs to write in receipt.**
- 2023+2024 fetal zip + PDF SHAs unchanged.
- Post-refresh fetal_death parquet SHAs.
- `field_specs.py` SHA unchanged if no era_tag added; new SHA otherwise.
- C8.1's smoke EXPECTED_YEAR_ROWS dict updated to include +2023, +2024.
- 4× `__init__.py` files (added 2026-05-12T22:30Z C8.1-followup commit) present at `fetal_death/`, `fetal_death/tests/`, `natality/`, `natality/tests/` — if any missing, the pytest co-collection bug returns.
- Future linked-2024-cohort refresh task: trigger when NCHS publishes `2025PE2024CO.zip` (sibling check via `curl -sIk` HEAD probe; PRE-FLIGHT triggered automatically by §11 plan-update at that time).

---

### Task C8.3 — Cross-product Tier-1: timeline + perinatal joint + 2022 race validation

**Re-scoped 2026-05-12T23:50:00Z at PRE-FLIGHT.** Original §15 entry (DECISION_LOG 2026-05-12T21:00:00Z) named "NVSR 73-09 Table A for 2022 perinatal validation" and "NVSR fetal-mortality table for 2017 by maternal race" as PRE-FLIGHT sources. C8.3 PRE-FLIGHT L9 cheap-check discovered: (a) NVSR 73-09 is fetal-mortality-only, not perinatal; Table A is 2022 fetal-mortality by single-race + Hispanic, not a perinatal table — NCHS no longer publishes a combined perinatal-mortality rate per year (the MacDorman *Fetal and Perinatal Mortality* series stopped after 2013 data); (b) no NVSR titled "Fetal Mortality: United States, 2017" exists — the NCHS annual fetal-mortality NVSR series gaps 2014–2018 data years (resumes at NVSR 70-11 = 2019). User authorized re-scope to **(a) 2022 race + perinatal demo** at 2026-05-12T22:30Z (DECISION_LOG 2026-05-12T23:50:00Z files the [plan-update]).

**Goal.** Land three cross-product items in one task: (i) cross-product timeline figure (`shared/helpers/build_timeline_figure.py` + `figures/fig1_coverage_timeline.{pdf,png}`); (ii) three-product perinatal-mortality joint computation as a JOINT-USE DEMO in `notebooks/joint_use_demo.ipynb` Section C, with two sub-component validations against on-disk NVSR cells; (iii) Section B refactor to 2022 single-race + Hispanic fetal-mortality validation against NVSR 73-09 Table A (7 cells) — preserves the existing 2017 bridged-race machinery as a documented "machinery demo" for the last-bridged-race-year, but the NVSR-validated cells move to 2022.

**Why this matters.** Manuscript's "designed for joint use" central claim is currently demoed only as single-product fetal mortality. The perinatal-mortality rate formula `(FD ≥28wk + ENN <7d) / (live_births + FD ≥28wk) × 1000` requires all three products simultaneously — this is the *unique* HVS capability. The new Section C surfaces it; the timeline figure plausibly becomes manuscript Figure 1.

**PRE-FLIGHT inputs.**
- All three parquets (post-C8.2 refresh state): fetal-death v2.4.0 (43 yrs); natality v2.8.0 (35 yrs); linked v3 (19 yrs). SHAs recorded in PRE-FLIGHT 2026-05-12T22:30:00Z.
- **NVSR 73-09 Table 1** (on disk at `/Users/.../fetal-death-harmonization-build/raw_docs/fetal_death/validation/nvsr73-09.pdf` sha=`2590e417…`): 2022 row publishes total 20,202; 20–27wk 10,246; **28+wk 9,956**; live births 3,667,758. Footnote: gestational age proportionally redistributed.
- **NVSR 73-09 Table A** (same PDF, page 6): 2022 fetal mortality rates by single-race + Hispanic — Total 5.48; AIAN 7.22; Asian 3.70; Black 10.05; NHOPI 10.36; White 4.48; Hispanic 4.63.
- **NVSR 73-05** (Ely & Driscoll 2024, *Infant Mortality in the United States, 2022: Data From the Period Linked Birth/Infant Death File*, sha=`dccdc895022c3c9d…`): Table 2 publishes 2022 **early neonatal (<7 days) rate = 2.81 per 1,000 live births**, with race-stratified breakouts (AIAN 3.73; Asian 2.01; Black 5.05; NHOPI 3.36; White 2.23; Hispanic 2.65). To be fetched into `raw_docs/natality/nvsr/` at DO step 1 (or referenced read-only from CDC URL with SHA pinned).
- Era-boundary metadata: `fetal_death/COMPARABILITY.md` §"Era Structure" + STATUS for 2003-rev transition + V3a/V3b ranges; `natality/docs/COMPARABILITY.md` §"Known structural breaks" + linked-file format-transition + bridged-race-dropped; the era-band spec is summarized in the C8.3 PRE-FLIGHT log entry.

**SMOKE plan.**
- Tier 0 (timeline): render a 1-row prototype timeline figure with just fetal-death bars; verify era bands hit the right years (1982/1989/1992/2003/2005/2018) and the certificate-revision boundaries (1989/2003/2014) render as expected.
- Tier 0 (perinatal joint): compute 2022 perinatal numerator on a 100-record sample of each product; manual sanity check of the gestational-age filter + age-at-death filter.
- Tier 0 (Section B 2022): compute fetal-mortality rates for the 7 NVSR 73-09 Table A groups on a 100-record fixture; verify cell-count alignment.
- Tier 1 (full): notebook end-to-end execute via `nbclient` (existing builder pattern in `_build_joint_use_demo.py`); cells must produce values matching NVSR within rounding tolerance.

**DO scope.**
1. Fetch NVSR 73-05 to `raw_docs/natality/nvsr/nvsr73-05.pdf` with SHA-verify against the PRE-FLIGHT-recorded value (`dccdc895022c3c9d…`).
2. Author `shared/helpers/build_timeline_figure.py` producing `figures/fig1_coverage_timeline.{pdf,png}`. Render three horizontal bars (fetal-death 1982–2024; natality 1990–2024; linked 2005–2023) with era-band coloring + vertical revision-boundary guidelines + legend.
3. Author new Section B + new Section C content in `notebooks/_build_joint_use_demo.py`. Section B → 7 NVSR 73-09 Table A cells (2022 single-race + Hispanic fetal mortality, using `race_hispanic_revised` in fetal-death and `maternal_race_ethnicity_5` in natality); preserve existing 2017 bridged-race cells as machinery demo with a "no NVSR cell published for 2017 by maternal race" caveat. Section C → 2022 perinatal joint computation with sub-component validations.
4. Re-build `notebooks/joint_use_demo.ipynb` deterministically via `python notebooks/_build_joint_use_demo.py`. Confirm Section A 2022-by-age cells (existing) remain byte-exact.
5. Update `docs/JOINT_USE_GUIDE.md` adding the perinatal-mortality worked example and a pointer to the timeline figure.

**VERIFY criteria.**
- Timeline figure era bands match COMPARABILITY docs cell-by-cell (visual + a programmatic check that band-start/end years match a small fixture dict in the helper).
- Section B 7/7 NVSR 73-09 Table A 2022 cells match within rounding (rate cells, 2 decimal places).
- Section C 28+wk fetal-death count matches NVSR 73-09 Table 1 9,956 within proportional-redistribution tolerance (~50 records due to "not stated gestation" handling).
- Section C early-neonatal rate from linked-file 2022 matches NVSR 73-05 Table 2 Total = 2.81 per 1,000 within rounding.
- Section C perinatal rate sanity-checks against published sub-components (computed = 28+wk-FMR + ENN-rate where the denominators reconcile).
- `pytest fetal_death/tests/ natality/tests/` 15 passed + 1 xfailed still holds (C8.3 does not touch parquets).
- All Section A 2022 NVSR 73-09 Table 4 age cells remain byte-exact (regression gate).

**Estimated effort.** 2 sessions.

**Dependencies.** C8.2 (post-refresh parquets — present at SHAs in PRE-FLIGHT).

**Halt-condition flags.** F1, F2, F4 (cross-product join + canonical filter on both sides), H9, L9 (NVSR cell location resolved at PRE-FLIGHT for 2022 sources; NVSR 73-05 still to fetch at DO step 1). Convention 1 SHAPE-not-VALUE for any new test in C8.4 territory (none in C8.3). Convention 3 Field-value snapshot recorded in PRE-FLIGHT 2026-05-12T22:30:00Z.

**Notes for next session.**
- The 2017 deferred-Task-4-fragment commitment is reframed: NVSR cell-validation moves to 2022 (cleanly publishable); the 2017 bridged-race machinery in Section B is preserved as a documented "machinery demo." Manuscript line 99's existing claim ("the 2022 maternal-age-stratified fetal mortality cells against NVSR 73-09 Table 4") is unaffected and a sibling claim for Section B (2022 race) + Section C (perinatal demo) is candidate manuscript-edit scope for Phase D step 6.
- The early-neonatal sub-component validation uses NVSR 73-05's Table 2 total = 2.81 per 1,000. The race-stratified breakouts (AIAN 3.73; Asian 2.01; …) are available if Section C needs deeper validation; a "single cell" total-validation is sufficient for the headline JOINT-USE DEMO claim.
- The H8-class "proportional redistribution of unknown gestation" caveat (NVSR 73-09 Table 1's 9,956 is post-redistribution; our parquet stores observed gestation) is documented in the Section C narrative + RECEIPT Self-check; closing this drift is C8.4-scope (canonical-filter invariant tests), not C8.3.

---

### Task C8.4 — Invariant tests: canonical-filter + row-count conservation + cross-product join parity (B.3 + B.4 + B.5)

**Goal.** Author three invariant test harnesses defending the core analytic-correctness invariants: (B.3) sum-across-strata = unstratified-total per canonical filter per product per year; (B.4) row-count conservation at every parse → harmonize → derive boundary (input = output + documented_drops); (B.5) cross-product join parity (natality joined to fetal-death + linked produces the expected demographic-stratum counts per JOINT_USE_GUIDE).

**Why this matters.** These three close §8 H6 (silent row drops), §8 F2 (cross-product join without filter), §8 H9 (external targets cancel internal bugs). Currently no automated guard against these classes.

**PRE-FLIGHT inputs.** All three parquets; `docs/JOINT_USE_GUIDE.md` for canonical-filter definitions; `shared/helpers/canonical_join_keys.py` for join keys; DECISION_LOG entries for documented drops (need consolidation registry).

**SMOKE plan.** Tier 0: mutation tests (inject a violation: duplicate a row, drop a row, mis-apply a filter; assert the harness catches each).

**DO scope.** Three new test files in `tests/` (monorepo-root level since they're cross-product). Each harness with `DESIGN: tracks-current-state` (B.4 documented-drops dict) or `DESIGN: structural-invariant-no-pins` (B.3, B.5 — pure SHAPE invariants).

**VERIFY criteria.** All three tests PASS on current parquet state. Mutation injections fail predictably.

**Estimated effort.** 3 sessions.

**Dependencies.** C8.1 (test infrastructure), C8.2 (refreshed parquets).

**Halt-condition flags.** H6, F2, H9, L3 (validator self-blindness — defended via mutation tests).

---

### Task C8.5a — Distribution: pyproject.toml + uv.lock (F.3)

**Note: Originally bundled with C8.5b Dockerfile work as one task C8.5.** Split into C8.5a + C8.5b at C8.5 PRE-FLIGHT 2026-05-13T04:00:00Z (DECISION_LOG entry of same timestamp) after PRE-FLIGHT discovered (i) `docker` not installed on build machine; (ii) §15 Python pin (`3.11-slim`) conflicts with actual build env (3.13.9); (iii) §15 VERIFY criterion references monorepo-root `scripts/run_pipeline.py` that does not exist (C8.7 scope). The §11 plan-update preserves all original C8.5 work but separates the locally-verifiable lockfile portion (C8.5a, this entry) from the docker-dependent Dockerfile portion (C8.5b, follows).

**Goal.** Author `pyproject.toml` (PEP 621 metadata + `requires-python = ">=3.13,<3.14"`) and `uv.lock` pinning exact versions for Python 3.13.x + pandas + pyarrow + numpy + matplotlib + jupyter + nbformat + pytest + nbclient + any other runtime dep. Replace `requirements.txt` `>=` semantics with the lockfile as the canonical pinned env; `requirements.txt` files preserved as discovery-pointers for users without `uv`.

**Why this matters.** Manuscript Reproducibility Strengths claim is currently advertised without a pinned env. Closes the F.3 gap per `EXPLORATION_REPORT.md`. Unblocks C8.6 (CI) which needs `uv sync --frozen` for deterministic GitHub Actions runs.

**PRE-FLIGHT inputs.** Existing `requirements.txt` (monorepo root + 2 subprojects); current Python version on build machine (3.13.9 per natality v2.7.0 + fetal_death V2.0 build notes); `uv` available (verified 0.11.10 at PRE-FLIGHT).

**SMOKE plan.** Tier 0: `uv lock` resolves; `uv sync --check` reports the env matches the lock; `pytest fetal_death/tests/ natality/tests/ tests/` returns 56 PASS + 1 XFAIL under the lockfile-defined env.

**DO scope.** Choose `uv` (faster than poetry, simpler conventions). Author `pyproject.toml` at monorepo root: PEP 621 metadata block (`name = "vital-statistics-harmonization"`, version mirrors per-product version conventions but lives at monorepo root for env-only purposes), `requires-python = ">=3.13,<3.14"`, `dependencies = [...]` listing every runtime dep with `==` pins matching currently-installed versions, `[tool.uv.dev-dependencies] = [...]` for pytest + nbclient + pymupdf (if used for L9 cheap-checks). Run `uv lock` to produce `uv.lock`. Author `.python-version` (single-line `3.13`). Append README section "Reproducibility via uv lockfile" (~5-10 lines) describing `uv sync` workflow.

**VERIFY criteria.** (revised per §11 plan-update 2026-05-13T04:00:00Z): (i) `uv lock` produces a deterministic lock; running `uv lock` twice produces bit-identical output. (ii) `uv sync --check` reports env-OK. (iii) Cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` under the lockfile-defined env returns 56 PASS + 1 XFAIL (the C8.4 baseline). (iv) All four parquet SHAs unchanged (C8.5a is metadata-only). (v) `requirements.txt` content survives unchanged at all 3 locations; only the lockfile becomes the new pinned canonical env. — The original §15 VERIFY criterion (pipeline-rebuild via `scripts/run_pipeline.py`) moves to C8.7's responsibility; C8.5a relies on C8.7 for end-to-end pipeline-rebuild closure.

**Estimated effort.** 0.5–1 session.

**Dependencies.** None upstream. C8.6 (CI) depends on this. C8.5b (Dockerfile) depends on this.

**Halt-condition flags.** None unique. Soft-flag: if `uv lock` cannot resolve (e.g., a transitive dep doesn't support Python 3.13), the §11 plan-update may need to revise the version pin or drop a dep.

---

### Task C8.5b — Distribution: Dockerfile (F.2) [DEFERRED]

**Status: DEFERRED at C8.5 PRE-FLIGHT 2026-05-13T04:00:00Z** per user authorization (DECISION_LOG entry of same timestamp). Originally bundled with C8.5a as a single C8.5 task. Deferred because (i) `docker` is not installed on the build machine, so the Tier 1 + Tier 2 SMOKE steps (`docker build` + `docker run`) cannot run locally; (ii) the §15 VERIFY-via-pipeline-rebuild criterion requires C8.7's monorepo-root orchestrator to land first for a non-fetal-only verification. Trigger for resumption: user installs Docker Desktop / OrbStack / colima OR C8.6 CI ships and validates remotely via GitHub Actions' hosted-runner `docker build`.

**Goal.** Author `Dockerfile` + `.dockerignore` at monorepo root producing a runnable image that rebuilds every parquet end-to-end. Base image `python:3.13-slim` (revised from §15's original `3.11-slim` text per §11 plan-update 2026-05-13T04:00:00Z to match the canonical build env). Multi-stage: base → `uv sync --frozen` (consuming C8.5a's lockfile) → script copy → entrypoint. Bind-mount `raw_data/` rather than baking 5+ GB of raw zips into the image. README section "Reproducibility via Docker."

**Why this matters.** Manuscript Reproducibility Strengths claim is currently advertised without a one-command rebuild. Closes the F.2 gap. Provides a portable env for users without `uv`.

**PRE-FLIGHT inputs (when resumed).** C8.5a-complete (`uv.lock` present, sha-recorded); `docker` (or compatible runtime: `podman`, `colima` + `docker` CLI) available on build machine; C8.7-complete OR scoped acceptance that the Dockerfile rebuild VERIFY is partial (fetal-death only).

**SMOKE plan (when resumed).** Tier 0: Dockerfile syntax lints clean. Tier 1: `docker build .` on a clean checkout; verify the image builds. Tier 2: `docker run` invokes `scripts/run_pipeline.py` (post-C8.7) end-to-end; verify outputs match expected parquet SHAs.

**DO scope (when resumed).** Author `Dockerfile` (multi-stage: `python:3.13-slim` base → `uv sync --frozen` → script copy → CMD/ENTRYPOINT pointing at monorepo-root pipeline orchestrator). Author `.dockerignore` excluding `output/`, `raw_data/`, `raw_docs/`, `.git/`, `__pycache__/`, `.venv/`, parquet artifacts, large PDFs. README section update.

**VERIFY criteria (when resumed).** `docker build .` produces an image. `docker run --rm -v $(pwd)/raw_data:/app/raw_data -v $(pwd)/output:/app/output <image>` rebuilds parquets to SHAs matching the canonical build (C8.7's smoke baseline).

**Estimated effort.** 1–2 sessions (when resumed; depends on whether bind-mount complexity drives `docker-compose.yml` authoring).

**Dependencies.** C8.5a (lockfile); C8.7 (pipeline orchestrator) for full-rebuild VERIFY; `docker` runtime on build machine.

**Halt-condition flags.** None unique (H10 covered by SHA cross-check at Tier 2).

---

### Task C8.6 — CI: GitHub Actions wiring (B.9)

**Note: §15 entry revised at C8.6 PRE-FLIGHT 2026-05-13T05:30:00Z** (DECISION_LOG entry of same timestamp; user-authorized at AskUserQuestion 2026-05-13T05:30:00Z with "do what you think is the best move" = Option A "ship workflow now, live-VERIFY at Phase D step 3"). The §11 plan-update resolves two §7-class HALTs surfaced at PRE-FLIGHT: (i) §7.17 + §7.12-shape — this monorepo has no `origin` remote (it is the dev workspace; the public repo at `yoelplutchok/vital-statistics-harmonization` is at v1.0 commit `a18ca3a` and lacks Tier-1 outputs); a live remote push from here would expose all state files; the canonical mechanism for moving Tier-1 outputs to the public repo is Phase D step 3 (staging-dir rsync + scrub + push). (ii) §7.12 — original DO scope's "matrix on Python 3.11 + 3.12" predates C8.5a's `requires-python = ">=3.13,<3.14"` pin; single-version 3.13 is the correct target.

**Goal.** Author `.github/workflows/ci.yml` running C8.1 dtype-parity (`fetal_death/tests/test_schema_dtype_parity.py`) + C8.4 invariant tests (`tests/test_canonical_filter_invariants.py`, `tests/test_row_count_conservation.py`, `tests/test_cross_product_join_parity.py`) + the existing C8.1-retagged release-smoke (`fetal_death/tests/test_release_smoke.py`, `natality/tests/test_schema_dtype_parity.py`) on every push to main and on pull requests. Workflow installs the pinned env via `uv sync --frozen` (consuming C8.5a's `uv.lock`). The workflow file is the canonical artifact shipped this task; the live-CI green-check VERIFY closes at Phase D step 3's first public-repo sync.

**Why this matters.** No automated test runs today; regressions discovered post-hoc. CI is the cheapest single signal of project health for external reviewers (`EXPLORATION_REPORT.md` §B.9). Public-repo CI minutes are free at this scale. Authoring the workflow file ahead of Phase D ensures the first public sync ships a runnable CI scaffold, not a workflow-less repo.

**PRE-FLIGHT inputs.** Existing tests (C8.1 + C8.4); pinned env (C8.5a lockfile `uv.lock` sha=`ab627034…`; `pyproject.toml` sha=`c8826a61…`; `.python-version` sha=`02e735b3…`); public GitHub repo at `https://github.com/yoelplutchok/vital-statistics-harmonization` (v1.0 commit `a18ca3a`; will receive the workflow at Phase D step 3 first sync); `uv 0.11.10` on build machine; `.venv/` ready for local-emulation VERIFY.

**SMOKE plan.** Tier 0: workflow YAML validates structurally via `python -c "import yaml; yaml.safe_load(open(...))"` round-trip + dict-key assertions on top-level (`name`, `on`, `jobs`, `concurrency`), per-job (`runs-on`, `steps`), per-step (`uses` or `run` set; pinned action versions); fallback to `actionlint` if available (not installed locally — yaml.safe_load + structural assertions is the durable check).

**DO scope.** Single-job workflow targeting `ubuntu-latest` with Python pinned to **3.13** sourced from `.python-version` (no version matrix; `requires-python = ">=3.13,<3.14"` excludes 3.11 / 3.12 / 3.14 by design). Triggers: `push` on `main`, `pull_request` on `main`, `workflow_dispatch` (manual). Steps:
1. `actions/checkout@v5`
2. `astral-sh/setup-uv@v6` with `version: "0.11.x"`, `enable-cache: true`, `cache-dependency-glob: "**/uv.lock"` (Python auto-resolved by uv from `.python-version` + `pyproject.toml`; no separate `actions/setup-python` step).
3. `uv lock --check` (gates against `pyproject.toml` ↔ `uv.lock` drift).
4. `uv sync --frozen` (installs the pinned env).
5. `uv run pytest fetal_death/tests/ natality/tests/ tests/ -v` (expected 56 PASS + 1 XFAIL when parquets are present; under a clean checkout with no parquets, the conftest `_require()` skip-if-missing protocol will cleanly skip parquet-dependent tests — this is the parquet-skip-in-CI concern documented as a Forward-looking HALT routed to C8.13 for future resolution via GitHub release artifacts).

Concurrency control: `group: ci-${{ github.ref }}`, `cancel-in-progress: true`.

**VERIFY criteria.** (Revised per §11 plan-update 2026-05-13T05:45:00Z.)
1. **YAML structurally valid** — `python -c "import yaml; d = yaml.safe_load(open('.github/workflows/ci.yml'))"` raises no exception; top-level keys present (`name`, `on`, `jobs`, `concurrency`); jobs.test has `runs-on` + `steps`; each step has `uses` or `run`.
2. **Locally-emulated workflow steps produce the C8.5a baseline** under `.venv`: cache-cleared (`find . -name __pycache__ -type d -exec rm -rf {} +`) + `uv lock --check` exit 0 + `uv sync --check` "Would make no changes" + `.venv/bin/python -m pytest fetal_death/tests/ natality/tests/ tests/` returns 56 PASS + 1 XFAIL.
3. **All four parquet SHAs unchanged** (this is a workflow-file-only task; no data mutation).
4. **All four C8.5a file SHAs unchanged** (workflow file is additive; no edits to pyproject.toml / uv.lock / .python-version / README.md).
5. **Forward-looking VERIFY (closes at Phase D step 3 first sync)**: First push to public repo containing `.github/workflows/ci.yml` triggers a workflow run on `ubuntu-latest`; the run completes successfully (parquet-dependent tests may skip cleanly per conftest `_require()` — that's expected pending C8.13). If the first remote run is red, the Phase D session must halt + surface failure modes; if green, the live-CI VERIFY closes.

**Estimated effort.** 1 session (unchanged from original §15 estimate; the deferred live-CI VERIFY is a forward-looking step, not added effort).

**Dependencies.** C8.1 (test inventory), C8.4 (invariant tests + `tests/` directory + 4× `__init__.py`), C8.5a (`uv.lock` + `pyproject.toml` + `.python-version`). C8.5b (Dockerfile, DEFERRED) is NOT a dependency per the C8.5 plan-update's dependency narrowing. Live-CI VERIFY depends on Phase D step 3 (staging-dir sync + push).

**Halt-condition flags.** None unique. L11 (stale roadmap claim) and L17-extension (test-infra invariants) are sibling defenses; the workflow's `uv lock --check` + `uv sync --frozen` + cache-cleared `pytest` ladder is the durable defense against both.

---

### Task C8.7a — Path-drift static audit across per-step pipeline scripts (B.10, narrowed)

**Note: Originally bundled with C8.7b orchestrator + Tier-1/Tier-2 reproducibility VERIFY as one task C8.7.** Split into C8.7a + C8.7b at C8.7 PRE-FLIGHT 2026-05-13T07:30:00Z (DECISION_LOG entry of same timestamp) after PRE-FLIGHT discovered (i) no monorepo-root `scripts/run_pipeline.py` exists (the §15-named entry point); (ii) `fetal_death/scripts/run_pipeline.py` mis-resolves `REPO_ROOT` from monorepo cwd AND its `ALL_YEARS = 29` is stale relative to the current v2.4.0 43-year envelope (V3a + V3b shipped 2026-05-12); (iii) natality has no orchestrator at all; (iv) Tier-2 full re-derive across three products is 6-12+ hours of compute — well beyond §15's 1-session estimate. The §11 plan-update preserves the path-drift-surfacing GOAL (the locally-verifiable cheap-check portion) in C8.7a (this entry) and moves orchestrator authoring + Tier-1 / Tier-2 reproducibility VERIFY to C8.7b (DEFERRED follows).

**Goal.** Statically audit every per-step pipeline script under `fetal_death/scripts/` and `natality/scripts/` (entry-point scripts + helpers); enumerate each script's path-constant computation (`REPO_ROOT`, `RAW_DIR`, `INPUT_DIR`, `OUTPUT_DIR`, etc.) and verify whether each resolves to an existing monorepo-relative path under current monorepo cwd. For each broken case: patch on contact (L13 fix-on-contact pattern) OR document with a FIX_LOG entry naming the broken constants + the runtime invocation that would surface them.

**Why this matters.** FIX_LOG 2026-05-12T01:30Z surfaced three latent path-drift bugs in `fetal_death/scripts/`; FIX_LOG 2026-05-12T22:00Z (C8.1 followup) surfaced two more in the test harness. Class L13-extension (monorepo migration path drift). Static audit confirms whether the path-constant surface is closed — without incurring the compute cost of a live re-derive. Live re-derive is C8.7b's responsibility.

**PRE-FLIGHT inputs.** Existing per-step pipeline scripts under `fetal_death/scripts/01_import` / `03_harmonize` / `04_derive` / `05_validate` and `natality/scripts/01_import` / `02_clean_yearly` / `03_harmonize` / `04_derive` / `05_validate` (entry-point `.py` files + helpers); `fetal_death/scripts/run_pipeline.py` (the existing fetal-death-only orchestrator); current symlink state at `output/` (verified: only fetal-death subdirs symlinked; natality + linked outputs NOT symlinked from monorepo `output/`). C8.6-complete tag at `67ab76f`; ci.yml sha=`c248cf51…`; 4 C8.5a file SHAs and 4 parquet SHAs all match the C8.6 forward-looking HALTs.

**SMOKE plan (revised).** Tier 0a (Python AST audit): import each entry-point script via `importlib.util.spec_from_file_location` + `module_from_spec` (in a sandboxed namespace where `__main__` doesn't execute); read its module-level path constants by inspecting the loaded module's globals. Tier 0b (resolution test): for each path constant, `pathlib.Path.exists()` under monorepo cwd. Tier 0c (helper-script reachability): grep each entry-point script for imports of sibling helpers (`from common import …`, `from harmonize import …`, etc.) + verify each importable from monorepo cwd. No live data invocation; no canonical-state mutation.

**DO scope.** For each entry-point script: record path-constant audit row in `RECEIPTS/C8.7a_<UTC>.md` audit table. For each FAIL: apply minimal L13-style patch (sibling of FIX_LOG 2026-05-12T01:30Z entries) — typically replace `Path(__file__).resolve().parent.parent` with a `MONOREPO_ROOT` / `SUBPROJECT_ROOT` distinction; pin output paths relative to the symlinked `output/` location at monorepo root. File one consolidated FIX_LOG entry per script-class (entry-point orchestrator / per-step parse / harmonize / derive / validate) rather than one entry per script, to avoid log bloat. NO orchestrator authoring; NO Tier-1 live run; NO parquet re-derive.

**VERIFY criteria.** (i) Every per-step pipeline script's path-constant resolution from monorepo cwd is documented in the receipt's audit table with verdict PASS / PATCHED / DOCUMENTED. (ii) Every PATCHED case has its Edit captured in the commit + a FIX_LOG entry (consolidated by script class). (iii) No parquet SHAs change (this is a metadata-only task — VERIFY all 4 SHAs unchanged: fd_harm=`38e2cecb…`, fd_der=`185c071e…`, nat_der=`e16ad53…`, linked_der=`9b828a4d…`). (iv) Cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` still returns 56 PASS + 1 XFAIL (no test-suite regression from any path-constant edit). (v) C8.5a file SHAs unchanged; ci.yml sha unchanged. (vi) **Forward-looking live-rebuild VERIFY closes at C8.7b** (whenever orchestrator + Tier-1 + Tier-2 are authorized).

**Estimated effort.** 1 session (matches original §15 1-session estimate; static audit + targeted L13 patches; no compute cost).

**Dependencies.** None upstream. C8.7b depends on C8.7a (orchestrator delegates to per-step scripts; their path-constants must be correct first).

**Halt-condition flags.** L13 (path-drift class); L4 (sibling-propagation for any fix landing in fetal_death/ must check natality/ + tests/); L11 (any audit row whose script is `out of scope per a prior DECISION_LOG entry` must cite the entry).

---

### Task C8.7b — Monorepo-root pipeline orchestrator + Tier-1 single-year-per-product re-build + Tier-2 full re-derive VERIFY (B.10 follow-up; **DEFERRED**)

**Status: DEFERRED at C8.7 PRE-FLIGHT 2026-05-13T07:30:00Z** per user authorization (DECISION_LOG entry of same timestamp). Originally bundled with C8.7a as a single C8.7 task. Deferred because (i) authoring a monorepo-root orchestrator is a substantive new design decision (entry-point shape + per-subproject delegation + output-path symlinks for natality + linked + extending fetal-death `ALL_YEARS` to 43 to cover V3a/V3b) — not bounded by the original §15 1-session estimate; (ii) Tier-2 full re-derive across three products is 6-12+ hours of wall-clock compute — well beyond a single session even if authored cleanly; (iii) Anti-Pattern #8 forbids compressing two tasks into one because they go together (path-drift surfacing vs orchestrator authoring vs reproducibility VERIFY are logically distinct concerns).

**Trigger for resumption.** AND-coupled: (a) C8.7a-complete (path-constants verified across all per-step scripts so the orchestrator delegates to a known-clean substrate); AND (b) user authorization for the multi-session compute window (Tier-2 wall-clock is dominated by natality 35yr × 138.8M-record re-derive + linked 19yr × 74.9M-record re-derive); a future PRE-FLIGHT at C8.7b resumption proposes either (i) split into Tier-1-only "single-year per product" close (~1.5-2 sessions) + Tier-2 deferred; OR (ii) full Tier-2 background-compute over multiple sessions (~3-5 sessions; Q33 effort-ceiling check).

**PRE-FLIGHT inputs (when resumed).** C8.7a-complete (path constants audited + patched); `fetal_death/scripts/run_pipeline.py` post-C8.7a sha (verify unchanged or re-audit); current parquet SHAs (4 values); current raw-zip inventory (43 fetal-death + 35 natality + 19 linked = 97 zips) verified bit-identical to file_inventory.csv; compute-time budget acknowledged.

**SMOKE plan (when resumed).** Tier 0: orchestrator dry-run (parse args, resolve all delegated-script paths, NO execution). Tier 1: live run on 1 year per product (e.g., FD 2020 + nat 2020 + linked 2020); re-derive single-year intermediate + compare to slice extracted from current shipped parquet. Tier 2 (OPTIONAL within C8.7b scope; can be split off): full 43-year FD re-derive (~30-60 min) + full 35-year nat re-derive (multi-hour) + full 19-year linked re-derive (multi-hour); compare final parquet SHAs against current shipped SHAs byte-exact.

**DO scope (when resumed).** Author `scripts/run_pipeline.py` at monorepo root with per-product subcommands (`fd`, `natality`, `linked`, `all`) + `--year` and `--steps` args. Add output symlinks for natality + linked under monorepo `output/` (or accept that natality re-derive writes to its standalone build-dir). Extend fetal-death `ALL_YEARS` from 29 to 43 to cover V3a + V3b (or document the gap as out-of-scope and pin to current 29-year scope as a tracks-current-state assertion).

**VERIFY criteria (when resumed).** Per Tier (1 or 2): re-derived parquet (or slice) sha256-matches the corresponding slice from current shipped parquet. Or: H10 reproducibility regression filed in FIX_LOG with reproducer.

**Dependencies.** C8.7a (path-constants audited). Independent of C8.5b (Dockerfile) — the orchestrator can run under uv-pinned env (C8.5a) without docker.

**Halt-condition flags.** L13 (orchestrator path-constants); H10 (reproducibility regression on byte-exact re-derive); L11 (stale `ALL_YEARS` claim — confirm scope at resumption).

---

### Task C8.8 — CHANGELOG.md + PRIOR_ART.md updates (E.1 + E.5)

**Goal.** (E.1) Author `CHANGELOG.md` at monorepo root: one section per version, v1.0 → v1.x → … delta. (E.5) Three concrete PRIOR_ART.md updates from `EXPLORATION_REPORT.md` §A.7 + literature-gap agent: (i) GitHub precursors subsection (Mikuana, arebe, damiancclarke); (ii) Hoyert et al. 2024 + NICHD Stillbirth WG July 2024 citation; (iii) one-sentence HL7/fhir-bfdr mention.

**Why this matters.** No CHANGELOG exists today. PRIOR_ART literature gap defensible as of 2026-05; three small updates close it to 2024. Pre-empts manuscript-reviewer pushback.

**PRE-FLIGHT inputs.** Existing RECEIPTS/ (changelog source); ABOUT_THIS_RELEASE.md files; existing PRIOR_ART.md; cited PMIDs (resolve at PRE-FLIGHT per L8); HL7/fhir-bfdr standard URL.

**DO scope.** Author CHANGELOG.md with sections: v1.0 (2026-05-12 public push) → v1.1 (C8.X work ships); each section has "data extensions / robustness / docs / breaking" subsections. Edit PRIOR_ART.md per §A.7 specifics. Update boundary statement per Q34 (out-of-scope M-D / MCD / abortion).

**VERIFY criteria.** CHANGELOG covers every shipped version since v1.0; cited PMIDs/DOIs resolve; HL7 reference is current.

**Estimated effort.** 1 session.

**Dependencies.** Tier 1 work ideally lands first (so CHANGELOG cites concrete deltas).

**Halt-condition flags.** L8 (citation resolution); L11 (stale roadmap claims — re-check on contact).

---

### Task C8.9 — Usability: R quickstart + DuckDB views (C.2 + C.4) — **C.1 DROPPED (NCHS public-use suppression policy)**

**Header note (2026-05-13T10:00Z PRE-FLIGHT plan-update, DECISION_LOG 2026-05-13T10:00:00Z, KICKOFF.md line 190 in lock-step):** the original C8.9 scope bundled three sub-deliverables (C.1 state denominators + C.2 R quickstart + C.4 DuckDB views). C8.9 PRE-FLIGHT cheap-checks surfaced two §7.13 conditions: (i) **C.1 is structurally unbuildable** because NCHS suppresses state-level geography in all three products' public-use files (confirmed via 11-year column probe across natality `yearly_clean` parquets + `natality/docs/FAQ.md:87-89` + `natality/docs/ABOUT_THIS_RELEASE.md:70` + 84+6-column natality harmonized schema absence + fetal-death harmonized_schema state-column absence); the upstream fix (NCHS RDC / restricted-use workflow) is out of HVS pre-submission scope. (ii) `duckdb` Python package is NOT in `pyproject.toml`/`uv.lock` despite the original PRE-FLIGHT-input claim "DuckDB installed in the env (C8.5 lockfile)". Resolution: drop C.1; ship C.2 + C.4 only; `uv add duckdb` is an authorized C8.9 DO step (pyproject.toml + uv.lock SHA drift acknowledged + recorded). **C.1 is permanently out of HVS pre-submission scope** — any future re-attempt requires either NCHS RDC access OR a different geographic stratification (Census region/division) with state→region derived-column infrastructure that does not currently exist.

**Goal.** Two usability layers: **(C.2)** `quickstart.R` per-product (fetal_death + natality + linked) mirroring `quickstart.py` with `arrow::read_parquet()` round-trip + sample analytic queries; **(C.4)** `views.sql` at monorepo root defining canonical-filter views + one cross-product join view as DuckDB-compatible views over the parquets.

**Why this matters.** R-using and SQL-using communities need worked examples. R quickstart shows `arrow::read_parquet()` round-trip + the canonical filter + a representative aggregate query. DuckDB-views path means zero Python for ad-hoc analyses (any DuckDB-supporting tool — CLI, R, Python, BI tools — can query the parquets via these views). Both independently support the manuscript *Accessibility* claim.

**PRE-FLIGHT inputs.**
- Both subprojects' harmonized parquets (4 SHAs unchanged from C8.7a forward-looking HALTs).
- Existing `fetal_death/quickstart.py` as R template (verified present per `PROJECT_STRUCTURE.md` line 95).
- R 4.5.1 at `/usr/local/bin/R` with `arrow` + `duckdb` + `dplyr` packages installed (probed PRE-FLIGHT 2026-05-13T10:00Z).
- **`duckdb` Python package will be added** via `uv add duckdb` as C8.9 DO step 1; pyproject.toml + uv.lock SHA drift from C8.5a-recorded values is an authorized addition.
- `shared/helpers/canonical_join_keys.py` providing the canonical filter convention.
- `docs/JOINT_USE_GUIDE.md` for cross-link target.

**SMOKE plan.**
- **Tier 0a (R syntax parse)**: `Rscript --vanilla -e 'parse(file = "fetal_death/quickstart.R")'` returns expression list without error (analogous for natality + linked).
- **Tier 0b (SQL syntax parse)**: `python -c "import duckdb; duckdb.connect().execute(open('views.sql').read())"` creates views without error.
- **Tier 1 (R parquet read)**: each `quickstart.R` reads its target parquet via `arrow::read_parquet()` and prints (column count, row count, dtype summary) for the harmonized parquet. Plausible row counts vs the corresponding C8.4 `tests/test_release_smoke.py` expectations.
- **Tier 1 (DuckDB view parity)**: each DuckDB view's row count matches the equivalent Python pyarrow filter on the same parquet for a 100-record subset. Spot-check one cell per product against an existing NVSR-equivalent validation target.

**DO scope.**
1. `uv add duckdb` — adds duckdb to pyproject.toml; `uv lock` regenerates uv.lock; `uv sync` installs into `.venv`.
2. Author 3× `quickstart.R` files: `fetal_death/quickstart.R`, `natality/quickstart.R`, `linked/quickstart.R` (or unified at monorepo root if cleaner). Each: arrow + dplyr load; `arrow::read_parquet()`; sample queries; documented R package deps.
3. Author `views.sql` at monorepo root: 3 canonical-filter views (fetal_death_canonical, natality_canonical, linked_canonical) + 1 cross-product join view (joint_use_demo). `CREATE OR REPLACE VIEW` syntax for idempotent re-runs.
4. Update `docs/JOINT_USE_GUIDE.md` with R + DuckDB usage sections; cross-link to new quickstart files + views.sql.
5. (Optional, if time) Update `natality/docs/FAQ.md` line 87-89 with a cross-reference back to JOINT_USE_GUIDE / EXPLORATION_REPORT for the state-suppression context.

**VERIFY criteria.**
1. **R quickstart loads each parquet successfully**: `Rscript fetal_death/quickstart.R` + `Rscript natality/quickstart.R` + `Rscript linked/quickstart.R` all exit 0; each prints the expected column count + row count.
2. **DuckDB views produce same record counts as canonical filter in Python**: per-product view row count = pyarrow-filtered row count (exact match).
3. **Cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returns 56 PASS + 1 XFAIL** (unchanged from C8.7a baseline; the test suite must be unaffected by the new files + duckdb dependency).
4. **All 4 parquet SHAs unchanged** post-C8.9 (no parquet mutation).
5. **`pyproject.toml` + `uv.lock` SHAs change in expected direction** — both files must show duckdb in their diff; the receipt records the before+after SHAs. `.python-version` + `README.md` + `.github/workflows/ci.yml` SHAs unchanged.

**Estimated effort.** 1-1.5 sessions (revised from 2.5-3 after C.1 drop).

**Dependencies.** None upstream. C8.10 onward depends on duckdb being in the lockfile.

**Halt-condition flags.** F1 (canonical filter on natality side — must apply `residence_status != 4` in both R + DuckDB); L11 (stale roadmap claims — surfaced at PRE-FLIGHT this session, dropped from §15 here).

---

### Task C8.10 — Worked-example notebooks 1-3 of 5 (C.6.a + C.6.b + C.6.c)

**Goal.** Author three notebooks:
- C.6.a `maternal_age_stratified_imr.ipynb` (linked file; replicable IMR-by-maternal-age curve).
- C.6.b `preterm_outcomes_time_series.ipynb` (FD + natality + linked; preterm-birth secular trends).
- C.6.c `cross_race_fetal_mortality.ipynb` (V3a/V3b demo; race-stratified FD; documents the B3 1-digit-recode caveats).

**Why this matters.** First two are the most-cited HVS use cases per literature scan. Third demonstrates the analytic value of the V3a/V3b backward extension shipped 2026-05-12.

**PRE-FLIGHT inputs.** All three parquets (post-C8.2 refresh state). NVSR validation cells per notebook (L9 cheap-check). `notebooks/_build_*.py` builder pattern from existing notebooks.

**DO scope.** Per-notebook: `notebooks/_build_<name>.py` deterministic builder + `notebooks/<name>.ipynb` with executed outputs. Each notebook validates ≥3 published-NVSR-equivalent cells at the bottom in a PASS/FAIL summary table.

**VERIFY criteria.** Each notebook runs end-to-end with the builder script; PASS/FAIL table all-PASS or any FAIL documented.

**Estimated effort.** 3-4 sessions (one session per notebook minimum).

**Dependencies.** C8.2 (refreshed parquets), C8.3 (perinatal demo precedent).

**Halt-condition flags.** F1, F2, F4 (within-era columns in cross-era contexts), L6 (manuscript numerics), H9.

---

### Task C8.11 — Migration guides + cross-product COMPARABILITY.md + sub-project SHA manifest (E.2 + E.4 + E.8)

**Goal.** (E.2) Two migration guides: `migrations/v2.7.0-to-v2.8.0-natality.md` (column renames + sample sed/awk) + `migrations/v2.0.0-to-v2.3.0-fetal-death.md` (V2.1 + V3a + V3b extension + query updates). (E.4) `docs/COMPARABILITY.md` at monorepo root synthesizing within_era/cross_era caveats from both subprojects. (E.8) Cross-product NCHS-source-data SHA manifest at monorepo root.

**Why this matters.** Users with legacy code need migration aids. Cross-product COMPARABILITY currently requires reading two separate files. SHA manifest confirms reproducibility from raw inputs.

**PRE-FLIGHT inputs.** DECISION_LOG entries (migration content source); both COMPARABILITY files; both `file_inventory.csv` files.

**DO scope.** Author the 4 documents. Cross-link from monorepo README + per-product README sections.

**VERIFY criteria.** Migration guides include working sample queries (PASS). Cross-product COMPARABILITY covers every era boundary. SHA manifest checksums match each subproject's file_inventory.csv.

**Estimated effort.** 3-4 sessions.

**Dependencies.** C8.2 (post-refresh column state + SHAs).

**Halt-condition flags.** L11 (stale claims in COMPARABILITY narratives), H8 (SHA drift).

---

### Task C8.12 — Mutation tests + L13 audit + L14 audit + SHA-stability test + snapshot regression (B.6 + B.7 + B.8 + B.11 + B.12)

**Goal.** Author mutation-test scaffolding for every validator (B.6); audit every metadata CSV for L13 role-vs-column claims (B.7); audit every validator's main() for L14 exit-code propagation (B.8); author SHA-stability test (B.11); author per-column snapshot regression test (B.12).

**Why this matters.** Five durable defenses against L3, L5, L11, L13, L14 in one task. Currently no validator has a paired mutation test; every L13/L14 case surfaces only at downstream cost.

**PRE-FLIGHT inputs.** All validators across both subprojects (~13 across 5 scripts); all metadata CSVs; PROVENANCE.md.

**DO scope.** Per-validator mutation test in `tests/mutations/`; mutation-runner uses AND-of-rows per L14. L13 audit script enumerates every metadata CSV's role/description claims; verifies column-content matches. L14 audit patches any `main()` returning implicit None on per-row failures. SHA-stability test reads PROVENANCE.md SHAs + on-disk SHAs; FAILs on drift. Snapshot regression: per-column SHA manifest at release; CI compares.

**VERIFY criteria.** Every validator has a paired mutation test that catches a known violation. L13/L14 audit FIX_LOG entries filed per finding (or empty if none). SHA-stability test PASSes on current state.

**Estimated effort.** 3-4 sessions.

**Dependencies.** C8.6 (CI to run them).

**Halt-condition flags.** L3, L13, L14, H10. **Likely surfaces FIX_LOG cascades** — budget for fix-on-contact.

---

### Task C8.13 — Pipeline timing benchmark (F.5 only; F.1 dropped + F.4 deferred 2026-05-13T22:30Z)

**Note: §15 entry revised at C8.13 PRE-FLIGHT 2026-05-13T22:30:00Z** (DECISION_LOG entry of same timestamp). Originally bundled F.1 (parquet dict-encoding tuning) + F.4 (GitHub Release) + F.5 (timing benchmark) as one task. C8.13 PRE-FLIGHT cheap-check probed the per-column encoding state via `pyarrow.parquet.ParquetFile.metadata.row_group(0).column(c).encodings` for all 340 columns across the 4 parquets and discovered: **both fetal-death parquets are already 100% dict-encoded** (73/73 + 89/89; 29 + 36 MB total); **all 38+41 non-dict columns in natality + linked are booleans using RLE+PLAIN** — the optimal 1-bit-per-value encoding for 2-state columns. Forcing dict-encoding on booleans does not reduce size and likely increases it. The §15 "30-50% size reduction via `use_dictionary=True` per column" premise is empirically falsified for our specific schemas. User authorized **Option A (drop F.1 entirely)** + **Option A (defer F.4 to Phase D step 3)** + **Option A (run real F.5 benchmark this session)** via AskUserQuestion 2026-05-13T22:30:00Z. Precedent: C8.5 / C8.6 / C8.7 / C8.9 PRE-FLIGHT-time §11 plan-updates with same shape.

**Goal.** (F.5 ONLY) Pipeline timing benchmark: measure real end-to-end wall-clock for the fetal-death pipeline (43-yr 1982-2024 envelope; per-step manual run since `fetal_death/scripts/run_pipeline.py` has stale `ALL_YEARS=29` per soft-flag (d), out-of-scope per C8.7b DEFERRED) and the natality+linked pipeline (35 + 19 yr; per-step manual run since no orchestrator exists per C8.7b DEFERRED). Compare against manuscript claim `paper/draft_v2_hmd_styled.md:68` *"approximately six minutes" (fetal) / "approximately ninety minutes" (natality)*. If within ±10%, ship a `docs/PIPELINE_TIMING_BENCHMARK.md` record + RECEIPT; if outside ±10%, propose manuscript line 68 edit to Phase D step 4.

**Why this matters (F.5).** Manuscript-cited reproducibility number. ±10% tolerance is the §15 VERIFY criterion. Builds substrate for Phase D step 4 manuscript re-pass.

**F.1 disposition (DROPPED):** Permanently out of pre-submission scope per soft-flag (p) filed at C8.13 PRE-FLIGHT 2026-05-13T22:30:00Z. Any future per-parquet encoding work (alternative codecs like ZSTD vs default SNAPPY; row-group size tuning) requires explicit re-authorization. Analog of C.1 NCHS-suppression permanent drop at C8.9.

**F.4 disposition (DEFERRED to Phase D step 3):** GitHub Release v1.x with parquet uploads moves to the Phase D step 3 staging-dir scrub + v1.x push session for one bundled public-facing release event. `gh` CLI substrate verified ready at C8.13 PRE-FLIGHT (gh 2.87.3 + auth OK with `repo` scope). The Release create command itself runs at Phase D step 3.

**PRE-FLIGHT inputs (this PRE-FLIGHT entry covers all of these).** All 14 C8.12 forward-looking HALTs verified byte-exact. Per-stage script inventory (fetal-death: parse_fetal_year.py × 43 + harmonize.py + derive.py; natality: parse_all_v1_years.py + parse_all_linked_years.py + 2× harmonize + 2× derive). Raw zip inventory: 43 fetal + 35 nat + 19 linked present at canonical absolute paths. Manuscript timing-claim cite at `paper/draft_v2_hmd_styled.md:68`.

**SMOKE plan.** Tier 0 (cheap-check): probe at least one zip's first-record byte length via the inventory's `record_length` column (already validated by C8.12 invariant tests; no new check needed). Tier 0b: dry-run timer harness on a 1-year fetal-death subset (verify timer wraps `subprocess.run` correctly + records start/end wall-clock; abort on non-zero exit). Tier 1: not applicable to F.5 (this IS the full DO measurement).

**DO scope (F.5 only).**

1. **Author lightweight timer wrapper** at `scripts/_time_pipeline.py` (~50 LOC; runs a list of `(stage_label, command_argv)` tuples; logs `start_ts, end_ts, duration_seconds, returncode` per stage to a CSV; aggregates into a summary). Not an orchestrator (no per-product subcommands; no smart skip-if-already-done — those are C8.7b scope).
2. **Run fetal-death 43-yr per-step benchmark** in background:
   - parse: 43 invocations of `parse_fetal_year.py` (one per year 1982-2024); time the batch
   - harmonize: 1 invocation of `harmonize.py` (output → `output/yearly_clean/...`)
   - derive: 1 invocation of `derive.py`
   - total wall-clock vs ~6 min manuscript claim
3. **Run natality+linked per-step benchmark** in background:
   - parse_all_v1: 1 invocation (iterates 35 years internally; the bulk of the ~90 min claim)
   - parse_all_linked: 1 invocation (iterates 19 cohort years)
   - harmonize_v1_core + harmonize_linked_v3: 2 invocations
   - derive_v1_core + derive_linked_v3: 2 invocations
   - total wall-clock vs ~90 min manuscript claim
4. **CRITICAL: idempotency preservation.** Each pipeline writes to its canonical output paths. The re-run MUST produce parquets byte-identical to the current shipped SHAs (`38e2cecb…` / `185c071e…` / `e16ad5323d…` / `9b828a4d…`). H10 reproducibility regression is the primary §7 halt condition for this DO; if any post-rerun SHA differs, FIX_LOG entry filed + halt-and-ask.
5. **Aggregate results** into `docs/PIPELINE_TIMING_BENCHMARK.md`: per-stage wall-clock + total + reconciliation vs manuscript claim + machine spec + caveats (e.g., parallel-run cache effects; the 2024-vintage-laptop manuscript anchor).
6. **Manuscript-drift handling:** If measured wall-clock is within ±10% of `~6 min` / `~90 min`, log PASS + cite `paper/draft_v2_hmd_styled.md:68` UNCHANGED. If outside ±10%, propose the edit + cite the propose-edit-deferred-to-Phase-D-4 precedent (C8.12 RECEIPT framing); do NOT edit the manuscript line in this session per the manuscript-edit-bundles-at-Phase-D-step-4 precedent.

**VERIFY criteria.**
1. Both pipelines completed end-to-end with exit code 0 (every stage).
2. **All 4 parquet SHAs preserved byte-exact** (H10 reproducibility gate; primary §7 halt condition).
3. Cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returns 74 PASS + 1 SKIP + 1 XFAIL (unchanged from C8.12 close; the F.5 re-derive must not affect any test outcome).
4. `docs/PIPELINE_TIMING_BENCHMARK.md` exists with per-stage breakdown + reconciliation table + caveats.
5. Manuscript drift recorded as PASS (within ±10%) or PROPOSE-EDIT (outside ±10%; edit deferred to Phase D step 4).

**RECEIPT requirement.** Standard template + Forward-looking HALTs covering: F.5 timer harness presence; new docs/PIPELINE_TIMING_BENCHMARK.md sha; 4 parquet SHAs unchanged byte-exact (H10 gate); 74 PASS + 1 SKIP + 1 XFAIL preserved; manuscript-line-68 disposition (PASS / PROPOSE-EDIT-for-Phase-D-4).

**Estimated effort.** ~1 session under narrowed scope (was §15 1.5-2 sessions; F.1 drop + F.4 defer cuts ~50%; F.5 = ~96 min compute + ~30 min plan-update + ~30 min RECEIPT/VERIFY).

**Dependencies.** None upstream (C8.2 already shipped; C8.7 deferred per C8.7b but F.5 routes around the orchestrator via per-step manual invocation).

**Halt-condition flags.** **H10 (reproducibility regression)** primary: re-run MUST produce byte-identical parquets. **L17-extension**: F.5 wall-clock is wall-time-VALUE, not a SHAPE invariant; the timing record file declares `DESIGN: tracks-current-state` analog (snapshot of current measurement; future builds may shift under hardware / pyarrow upgrades). **L11**: F.1 falsified premise resolved via this plan-update; no further L11 expected.

---

### Task C8.14 — Worked-example FAQ + PROJECT_STRUCTURE.md upgrade (E.3 + E.6)

**Goal.** (E.3) `docs/WORKED_EXAMPLE_FAQ.md` answering "how do I compute the perinatal mortality rate?", "how do I get state-level data?", "what's the right canonical filter?". (E.6) Upgrade PROJECT_STRUCTURE.md with notebook-deps graph, build-order DAG, "which-file-by-use-case" matrix.

**Why this matters.** Lowers the onboarding cost for new users. Cross-references existing notebooks + JOINT_USE_GUIDE + COMPARABILITY.

**PRE-FLIGHT inputs.** Existing FAQ files (per subproject); notebooks; PROJECT_STRUCTURE.md.

**DO scope.** Author the two documents.

**VERIFY criteria.** FAQ answers reference live notebook cells. PROJECT_STRUCTURE.md DAG matches actual script invocation order.

**Estimated effort.** 1 session.

**Dependencies.** C8.10 (notebooks ship before FAQ cites them).

**Halt-condition flags.** L11.

---

### Task C8.15 — Worked-example notebooks 4-5 (C.6.d + C.6.e)

**Goal.** (C.6.d) `education_gradient.ipynb` (within-era only, with 1989/2003 boundary explicit). (C.6.e) `state_reporting_quirks.ipynb` (Oklahoma Hispanic, Maryland/Massachusetts 1992-1998, Louisiana plurality).

**Why this matters.** C.6.d demonstrates the 1989/2003 boundary problem the manuscript invokes. C.6.e operationalizes COMPARABILITY notes that are currently text-only.

**PRE-FLIGHT inputs.** Same as C8.10. State-reporting-quirk references in COMPARABILITY.md.

**DO scope.** Same builder pattern as C8.10. Each notebook documents within_era usage (per §8 F4) for any cross-era field.

**VERIFY criteria.** Each notebook runs end-to-end; within_era columns flagged in markdown; no cross-era groupby on within_era columns.

**Estimated effort.** 2 sessions.

**Dependencies.** C8.10, C8.11.

**Halt-condition flags.** F4 (within_era column cross-era misuse).

---

# §15.D Phase C Tier 3 + Tier 5 tasks (authorized 2026-05-14 per `[plan-update] scope_expansion_tier3_tier5`)

The C8.16-C8.22 entries below were appended at the 2026-05-14T02:00:00Z `[plan-update]` commit (DECISION_LOG 2026-05-14T02:00:00Z). They expand pre-Zenodo scope to include Tier 3 (matched-multiples + CODEBOOK + Stata/SAS + cross-tabs) + Tier 5 (natality 1968-1989 + linked 1983-2004 + perinatal-record) per user authorization, in the sequence matched-multiples → natality 1968-1989 → linked 1983-2004 → perinatal-record → CODEBOOK → Stata/SAS → cross-tabs.

Each task uses the §4 five-phase discipline; halts on any §7 condition; tagged `<task_id>-pre-do` and `<task_id>-complete`. Effort-ceiling cap is now 86 sessions (raised from 42); Q33 re-ask invariant triggers if cumulative drift exceeds 86.

---

### Task C8.16 — Matched-multiples ancillary release (A.5; 4th HVS product)

**Goal.** Parse 3 NCHS matched-multiples linkage files (matched-multiple-birth-fetal-death-1995-1997 + 1995-2000 + 2016-2020) at `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/matched-multiples/`. Ship as a 4th HVS data product (`matched_multiples/` subproject parallel to `natality/` + `fetal_death/`) with per-file harmonized parquet + harmonized schema + validation against the NCHS documentation tables for each file. ~43 MB total raw.

**Why this matters.** Adds a 4th HVS data product covering multiple-gestation IMR + fetal-mortality analyses that currently require manual NCHS-side joining. The 1995-1997 + 1995-2000 + 2016-2020 windows are the only published NCHS matched-multiples linkages; canonically these are tested by the multiple-gestation research community but not currently distributed alongside HVS. Independent of C8.17 + C8.18 (matched-multiples files don't share an era with the natality 1968-1989 or linked 1983-2004 work).

**PRE-FLIGHT inputs.**
- 3 NCHS source zips at the matched-multiples FTP path (probe via `curl -sIk` for HTTP 200 + size + Last-Modified + ETag; record SHAs).
- 3 documentation PDFs at `ftp.cdc.gov/.../Dataset_Documentation/DVS/matched-multiples/` (probe via L12-extension `page.get_text()` text-layer check before assuming OCR is needed).
- Field-value snapshot (Convention 3): existing `fetal_death/file_inventory.csv` + `natality/metadata/file_inventory.csv` schemas (column structure to mirror for the new `matched_multiples/metadata/file_inventory.csv`); existing `harmonized_schema.csv` formats (column structure for new `matched_multiples/harmonized_schema.csv`); `PROJECT_STRUCTURE.md` top-level layout (to extend with new subproject directory).
- Architectural decision substrate: does the matched-multiples parquet ship as (i) standalone product with its own harmonized schema + canonical filter, or (ii) joined-into-existing-products as a `matched_multiple_flag` boolean column on fetal-death + linked? PRE-FLIGHT records the design decision with a DECISION_LOG entry.

**SMOKE plan.**
- Tier 0: 100-record parse of each of 3 files; verify record-length + column-count matches documentation.
- Tier 1: full-file parse of each; per-year + per-file aggregate counts match NCHS documentation tables (page-X cell-by-cell).
- Tier 2: cross-product join sanity check (matched-multiples records' maternal-demographics + state + delivery-year reconcile against fetal-death + natality + linked of the same year/cohort).

**DO scope.**
1. Architectural decision (PRE-FLIGHT artifact, DECISION_LOG entry): standalone subproject vs join-flag column. Default recommendation: standalone subproject for clean schema; future task can derive a join-flag if needed.
2. Create `matched_multiples/` subproject layout: README.md + GETTING_STARTED.md + ABOUT_SOURCE_DATA.md + harmonized_schema.csv + file_inventory.csv + scripts/01_import/parse_matched_multiples.py + scripts/03_harmonize/ + scripts/04_derive/ + scripts/05_validate/ + tests/.
3. Author parser; harmonize; derive (if applicable); validate against documentation tables.
4. Add a `notebooks/matched_multiples_demo.ipynb` worked example showing a multiple-gestation IMR computation (≥1 cell vs NCHS-published table).
5. Update monorepo top-level README.md, PROJECT_STRUCTURE.md, CITATION.cff to reflect 4th HVS product.

**VERIFY criteria.**
- Per-file aggregate counts match NCHS documentation byte-exact.
- `pytest matched_multiples/tests/` returns 100% PASS (new test directory).
- C8.1's dtype-parity test pattern extended to matched-multiples (`matched_multiples/tests/test_schema_dtype_parity.py`).
- `pytest fetal_death/tests/ natality/tests/ tests/ matched_multiples/tests/` returns at-least-74-PASS + 1 SKIP + 1 XFAIL (the existing baseline preserved + new tests added).
- 4 prior parquet SHAs unchanged (matched-multiples work is additive; existing products untouched).

**RECEIPT requirement.** Standard. Forward-looking HALTs: new matched-multiples parquet SHAs; new `matched_multiples/` directory presence + file inventory; documentation PDF SHAs; architectural decision artifact at DECISION_LOG.

**Estimated effort.** **1-2 sessions** (1 if architectural decision = standalone with mostly-V1-era-sibling layout; 2 if join-flag-column approach or substantial layout reconstruction).

**Dependencies.** None. First Tier-3+5 task per the 2026-05-14 plan-update sequencing.

**Halt-condition flags.** H1 (field-position drift; new layouts), H6 (row-count conservation across new pipeline), L12-extension (PDF text-layer probe before OCR assumption), L13 (inventory CSV column-content verification at write time), L17 (any new SMOKE harness asserts SHAPE-not-VALUE; carries `DESIGN:` tag).

---

### Task C8.17 — Natality 1968-1989 backward extension (A.2; 22 new years; 4 distinct layouts)

**Goal.** Extend natality coverage from 1990-2024 (35 yrs) to **1968-2024 (57 yrs)** by parsing the 22 pre-1990 NCHS public-use natality files at `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/natality/`. Reconstruct 4 distinct pre-1989 layouts (1968 / 1969-1971 / 1972-1977 / 1978-1988 / 1989). Re-harmonize natality from 1968-2024 (current schema + per-era era_tag extensions). Bump natality v2.8.0 → v2.9.0 (or v3.0.0 if cert-revision boundary triggers major bump per H10 reproducibility-gate cascade).

**Why this matters.** Largest single "more data" win identified by Phase B (per EXPLORATION_REPORT §A.2 + §G.5). Doubles natality coverage to 57 yrs. Pairs with fetal-death 1982-2024 to push joint analyses backward to 1982 (limited by FD floor; symmetric earlier extension blocked by RDC per §A.4). Substantial manuscript Coverage paragraph re-paragraph at D.4; manuscript *Future developments* "Annual extension" framing gains a sibling.

**PRE-FLIGHT inputs.**
- 22 NCHS source zips (probe HTTP 200 + size + Last-Modified per LESSONS L1-extension sibling-derivation: `Nat<YYYY>.zip` for 1969+; `Nat1968.ZIP` uppercase for 1968).
- ~17 user-guide PDFs at `ftp.cdc.gov/.../Dataset_Documentation/DVS/natality/Nat<YYYY>doc.pdf` + 2 multi-year joint docs (`Nat1969-71doc.pdf`, `Nat1972-77doc.pdf`). L12-extension `page.get_text()` text-layer probe BEFORE OCR assumption per the 1985 fetal-death precedent (LESSONS 2026-05-12T15:00Z).
- Layout substrate: natality 1990+ layouts live in `natality/scripts/01_import/field_specs.py` as Python `list[tuple[str, int, int]]` (not CSV — fetal_death + matched_multiples use CSV, natality uses Python; substrate-format reconciliation resolved at C8.17 DO step 2 entry via AskUserQuestion 2026-05-14 Q1 Option A = extend `field_specs.py`). DO steps 2-4 extend this Python substrate with `PUBLIC_US_<era>_FIELDS` lists + `RECORD_LEN_<era>` constants per era; sibling-derive byte positions from the 1968 + 1969-71 + 1972-77 + 1978-88 + 1989 user-guide PDFs cross-verified empirically against actual record bytes (L13-extension).
- Era-boundary registry: 1968 (50% sample alone) / 1969-1971 (50% sample multi-year joint doc) / 1972-1977 (mixed sample fraction; multi-year joint doc) / 1978-1988 (1978-revision birth cert 100% file from 1985) / 1989 (1989-revision birth cert; sibling of 1990-2002 V2 era).
- Field-value snapshot (Convention 3): `natality/metadata/harmonized_schema.csv` `years_available` cells (will need union-extension to 1968); `natality/metadata/file_inventory.csv` (currently 35 yrs + 19 linked rows; will need +22 rows); existing parquet SHAs (forward-stability anchor preservation).

**SMOKE plan.**
- Tier 0: byte-position layout reconstruction for 4 new eras as `PUBLIC_US_<era>_FIELDS` extensions in `field_specs.py` (Python substrate per substrate-format reconciliation above); sibling-derive from existing 1990+ layouts where applicable; verify anchor fields (year, sex, race, birthweight, gestation) align with the user-guide documentation pages per L9 cheap-check.
- Tier 1: 100-record parse of one year per layout (1968 + 1971 + 1975 + 1985 + 1989); assert plausible value distributions per L13-extension (don't trust byte positions alone; value-distribution-verify each anchor field).
- Tier 2: full-year parse of each of 22 years; per-year aggregate counts match NCHS *Vital Statistics of the United States* annual-volume control counts (paper-only; OCR friction acknowledged per EXPLORATION_REPORT §A.2).
- Tier 3: re-harmonize 1968-2024 natality; 1990-2024 byte-clean regression (0/N column drift on the post-1989 slice vs current parquet); per-era within-era invariants pass.

**DO scope (multi-sub-step; expect ~6-10 sub-step commits).**
1. **DO step 1 (1 session)**: download 22 source zips + 17 user-guide PDFs; record SHAs; SHA-verify against documentation.
2. **DO step 2 (1-2 sessions)**: `field_specs.py` extension for 1968 (81-byte) + 1969-1971 (215-byte) layouts; 35 + 71 anchor fields authored at C8.17 DO step 2 close (2026-05-14T08:30:00Z); 50%-sample-fraction handling unchanged.
3. **DO step 3 (1-2 sessions)**: `field_specs.py` extension for 1972-1977 (mixed sample fraction; multi-year joint doc; highest-risk single artifact).
4. **DO step 4 (1-2 sessions)**: `field_specs.py` extension for 1978-1988 + 1989 (1978-revision birth cert; 100% file from 1985; soft-flag (t) reconciliation at this step).
5. **DO step 5 (1 session)**: parser + harmonize.py extensions per era; B3-style 1-digit MRACE recodes (analogue of 2026-05-12T14:30Z task7_v3a + 2026-05-12T18:30Z task7_v3b precedents); Hispanic-origin null pre-1978 convention.
6. **DO step 6 (1 session)**: re-harmonize 1968-2024 full pipeline; preserve v2.8 parquet as `.v28_baseline.parquet` forward-stability anchor; bump natality v2.8.0 → v2.9.0 (or v3.0.0 if cert-revision boundary triggers major).
7. **DO step 7 (0.5-1 session)**: update CITATION.cff + .zenodo.json + ABOUT_THIS_RELEASE.md + README.md + monorepo PROJECT_STRUCTURE.md; refresh smoke EXPECTED_ROW_COUNT + EXPECTED_YEARS + EXPECTED_YEAR_ROWS (C8.1's `DESIGN: tracks-current-state` smoke pins re-anchor).

**VERIFY criteria.**
- Per-year counts 1968-1989 match NCHS-published annual-volume control counts.
- 1990-2024 byte-clean regression: 0/N columns drift on the post-1989 slice vs current parquet (anchor preserved per L5).
- C8.1's dtype-parity test PASSes on the v2.9.0 parquet (and any new era-specific columns added).
- B.12 snapshot regression baseline re-snaps post-rebuild; new `tests/snapshots/v2_<UTC>_columns.csv`.
- External validation grid: existing 183/183 NVSR cells preserved; new pre-1990 cells added incrementally.

**RECEIPT requirement.** Standard + Forward-looking HALTs covering: 22 source zip SHAs; 15 user-guide PDF SHAs (revised from 17 at PRE-FLIGHT per empirical doc-PDF inventory); new `PUBLIC_US_<era>_FIELDS` field counts + `RECORD_LEN_<era>` constants in `field_specs.py`; v2.9.0 parquet SHAs; B.12 snapshot baseline shift; C8.1 smoke re-pin status; whether the v2.8 baseline anchor preserved byte-exact on the 1990-2024 slice.

**Estimated effort.** **6-10 sessions** (lower if layouts sibling-derive cleanly; higher if 1972-1977 mixed-sample joint-doc handling inflates).

**Dependencies.** C8.16 (matched-multiples; non-blocking but should ship first for plumbing-validation reasons). C8.18 (linked 1983-2004) benefits modestly from this task's 1978-cert layout work but does not block.

**Halt-condition flags.** H1, H6, H7 (sibling-pipeline drift; natality's harmonized schema must agree with fetal-death's on shared concepts), L1-extension (sibling-derive ALL filename probes; per LESSONS L1-extension), L12-extension (PDF text-layer probe before OCR), L13-extension (value-distribution verify each anchor field), L17 (smoke pins shift; tracks-current-state DESIGN tag). Convention 1 SHAPE-not-VALUE on every new SMOKE.

**Sub-Q42 triggers.** Any sub-step >1 session beyond its DO step estimate triggers a §11 plan-update. Specifically: if 1972-1977 mixed-sample handling requires >2 sessions, file [plan-update] sub-entry; if Hispanic-origin pre-1978 handling surfaces an unanticipated B-recode, file [plan-update] sub-entry.

---

### Task C8.18 — Linked birth-infant death 1983-2004 cohort-only backward extension (A.3; 19 new cohort years; 1992-1994 gap)

> **[plan-update] 2026-05-17 (scope-correction; applied per §11 step 3; resolves soft-flag (ff)).** This entry's original premise — *"existing post-2005 HVS-linked ships period-format only"* — was **inverted**. A Convention-3 PRE-FLIGHT Field-value snapshot at C8.18 DO step 1 (5 converging substrate sources: `docs/NCHS_SOURCE_MANIFEST.md` §3; every `external_validation_targets_v3_linked.csv` `value_source`; `parse_linked_year.py`/`parse_linked_cohort_year.py`; `GETTING_STARTED.md:171`; `VALIDATION.md:220`/`COMPARABILITY.md:213`) established that the existing 2005-2023 product is the **cohort-linked** series. The §7-#12/#13 divergence was surfaced before any DO mutation and resolved via the §15.D-prescribed DO-step-1 + Sub-Q42 AskUserQuestion mechanism → **Option A "Cohort-only backward extension"** (user-selected 2026-05-17; DECISION_LOG 2026-05-17T05:30:00Z; RECEIPTS/C8.18_step1_2026-05-17T05-30-00Z.md). Corrections applied below: premise period→cohort; source scope 29→**19 zips**; period-linked 1995-2004 dropped from C8.18 (separate deferrable future product, separate `[plan-update]` if a user need arises); DO list re-sequenced 8→7 (DO step 1 now RESOLVED/decision-only); effort narrowed toward the lower 8-14 end; VERIFY "per-cohort/period" → per-cohort. The pre-correction text is preserved in DECISION_LOG 2026-05-17T05:30:00Z + the C8.18 PRE_FLIGHT_LOG entry per the append-only-supersede convention (§3).

> **[plan-update] 2026-05-23 (model-clarification; applied per §11 step 3 — user-authorized 2026-05-23 "Pre-D cleanup first"; resolves soft-flag (ii)).** The monolithic DO-scope step list below was decomposed during execution at each Convention-3/§7 cheap-check (the established within-task-decomposition precedent). Recorded here append-only-supersede (§3 — original step list preserved, no scope/deliverable change): **DO step 3 → 3a/3b** (1983-1988 pure births-only two-file [keyless den/num, no fabricated record-level join] vs 1989-1991 denominator-plus; DECISION_LOG 2026-05-17T20:00:00Z). **DO step 4 → 4a/4b/4c** (4a 1995-2002 cohort 1989-rev; 4b 2003 cohort 2003-rev DEFLATE64; 4c 2004 cohort 2003-rev dual-cert DEFLATE; DECISION_LOG 2026-05-18T14:30:00Z → 2026-05-18T23:00:00Z). **DO step 5 → 5a/5b/5c**, and **5c → 5c-i / 5c-ii (→ 5c-ii-a + 5c-ii-b) / 5c-iii** (5a `_find_denomplus_member` cross-era; 5b 1983-1988 keyless den+num `link_segment` construction; 5c-i 1989-1991 reference era; 5c-ii-a 1995-2002 1989-rev; 5c-ii-b 2003-2004 2003-rev dual-cert; 5c-iii the keyless 1983-1988 harmonized encoding + a bundled human-authorized §7 root-cause fix to `parse_linked_year.run_parse`'s `from_pylist` schema-from-first-record silent-drop + the (A′) RECWT@91 Convention-3 finding; DECISION_LOG 2026-05-19T05:00:00Z → 2026-05-20T02:00:00Z). **DO step 6 → 6a / 6a-RECWT / 6b** (6a the pre-2005 parse-driver + the H6 byte-exact parser-conservation gate + the binding §7 1983-1984 50%-non-VSCP-weighted-denominator halt-and-ask; 6a-RECWT the bounded 1983-1984 `record_weight` root-cause fix — the 5c-iii (A′) "RECWT@91 era-unstable" conclusion was FALSIFIED at the §2 cheap-check, see LESSONS 2026-05-22; 6b the FIRST canonical v3→v4 re-harmonize + the documented NCHS cohort numerator-vs-denominator-linkage residual; DECISION_LOG 2026-05-21T12:00:00Z → 2026-05-23T02:00:00Z). **DO step 7** = the docs/metadata consumer-surface sync (DECISION_LOG 2026-05-23T05:00:00Z); `C8.18-complete` set. This block records the executed structure only — the substantive choices live in the cited append-only DECISION_LOG/RECEIPTS entries; the inline "soft-flag (ii), proposed-not-applied, queued for §11 human-merge" note in DO step 3 below is hereby resolved.

**Goal.** Extend linked coverage from 2005-2023 (19 yrs) to **1983-2023 (41 yrs with permanent 1992-1994 gap)** as a **cohort-only backward extension** — append to the existing cohort-linked 2005-2023 series by parsing **19 NCHS cohort source files**: cohort-linked 1983-1991 (9 yrs; `LinkCO83.zip`-`LinkCO91.zip`, no `US` suffix pre-1995) + cohort-linked 1995-2004 (10 yrs; `LinkCO95US.zip`-`LinkCO04US.zip`). The cohort-vs-period publishing-design decision is **RESOLVED at DO step 1 = Option A cohort-only** (the existing product is cohort-linked; period-linked 1995-2004 is a different linkage method = a separate future product, OUT of C8.18 scope). Re-harmonize linked 1983-2023 (with documented 1992-1994 gap). Bump linked v3 → v4.

**Why this matters.** Second-largest "more data" win. Doubles linked coverage to 41 yrs. Under cohort-only, two boundary types remain materially in-scope (cert-revision 1989→2003; ICD-9→ICD-10 1998→1999); the third (linkage-method cohort-vs-period) is settled (cohort-only). One of the largest single-task efforts in the project (~8-11 sessions post-correction; lower end of the original 8-14). Strong support for the manuscript's "single-revision-window forced" framing.

**PRE-FLIGHT inputs.**
- 19 NCHS cohort source zips (probe HTTP 200 + sizes per EXPLORATION_REPORT §A.3 sizes). Filename convention: no `US` suffix pre-1995 (`LinkCO{83..91}.zip`); `US` suffix 1995+ (`LinkCO{95..04}US.zip`). Period-linked `LinkPE*US.zip` is OUT of scope.
- Cohort user-guide PDFs at `ftp.cdc.gov/.../Dataset_Documentation/DVS/cohortlinked/Link*Guide.pdf` (~19; exact count + naming sibling-derived at DO step 2 PRE-FLIGHT from on-disk `LinkCO{05..15}Guide.pdf`, L1-extension). L12-extension text-layer probe per the natality 2007-08 / fetal 2009-01 re-OCR-batch precedent.
- 1992-1994 gap: permanent; NCHS suspended ALL linkage (no cohort, no period). Must surface loud in schema (`years_available` cells include the gap), CODEBOOK, and manuscript per EXPLORATION_REPORT §A.3 risk (a).
- Cohort-vs-period publishing-design: **RESOLVED = Option A cohort-only** (DECISION_LOG 2026-05-17T05:30:00Z). The existing 2005-2023 HVS-linked product is the cohort-linked series; the methodologically-consistent extension is cohort-linked. §15.D EXPLORATION_REPORT §A.3 options (b) "period-equivalent view of cohort" / (c) "stop at 1995, period-only" were predicated on the inverted premise and are moot.
- ICD-9 vs ICD-10 cause-of-death substrate: cohort 1983-1998 carries ICD-9; 1999+ carries ICD-10 (existing 2005-2023 product is ICD-10, schema col `underlying_cause_icd10`). **Coupled decision settled at DO step 1 (DECISION_LOG 2026-05-17T05:30:00Z): default-null + revision-tagged** — populate `underlying_cause_icd10` only for 1999-2023 (null 1983-1998); preserve raw ICD-9 in `_raw` parquets + a within-era ICD-9 harmonized representation (exact column shape decided at DO step 5/6 PRE-FLIGHT, H7 fetal-death sibling-parity, soft-flag (gg)); published 9→10 crosswalk deferred to a dedicated post-C8.18 derivation task. `cause_recode_130` per-era availability = DO step 5/6 PRE-FLIGHT question (soft-flag (gg)).

**SMOKE plan.**
- Tier 0: cohort-vs-period design decision — **RESOLVED at DO step 1** (Option A cohort-only; AskUserQuestion 2026-05-17; DECISION_LOG 2026-05-17T05:30:00Z).
- Tier 0: byte-position layout-CSV reconstruction per cohort era (1983-1988 cohort 1978-rev + ICD-9; 1989-1991 cohort 1989-rev + ICD-9; 1995-1998 cohort 1989-rev + ICD-9; 1999-2002 cohort 1989-rev + ICD-10; 2003-2004 cohort 1989+2003-rev mix + ICD-10).
- Tier 1: 100-record parse per cohort era; anchor-field value-distribution verify per L13-extension.
- Tier 2: full-year parse; per-year cohort aggregate counts match NCHS cohort Linked File reports cell-by-cell.
- Tier 3: re-harmonize linked 1983-2023; 2005-2023 byte-clean regression (0/N column drift on the post-2005 slice vs current cohort parquet; H10 gate per Q38 default-validity-anchor preservation).

**DO scope (multi-sub-step; ~7 sub-step commits post-correction; DO step 1 = decision-only/RESOLVED).**
1. **DO step 1 — RESOLVED (decision-only; SHIPPED 2026-05-17)**: cohort-vs-period publishing-design = **Option A cohort-only** via AskUserQuestion 2026-05-17 (DECISION_LOG 2026-05-17T05:30:00Z; RECEIPTS/C8.18_step1_2026-05-17T05-30-00Z.md; zero canonical-state mutation; `C8.18-pre-do`@`6632a15`).
2. **DO step 2 (1 session)**: download **19 cohort source zips** (9 × `LinkCO{83..91}.zip` + 10 × `LinkCO{95..04}US.zip`) + cohort user-guide PDFs (L1-extension sibling-derive; L12-extension text-layer probe); SHA-verify; extend `file_inventory.csv` + `docs/NCHS_SOURCE_MANIFEST.md`.
3. **DO step 3 (2-3 sessions)**: `field_specs.py` layout reconstruction for cohort 1983-1991 (1978-rev birth + ICD-9; sibling of natality 1978-1988 from C8.17's DO step 4). *[fix-on-contact 2026-05-17T22:30:00Z, C8.18 DO step 3a, C8.17-DO2 precedent: "layout-CSV" → `field_specs.py` Python tuple-list substrate — the linked pipeline uses `field_specs.py`, not CSV record_layouts (DECISION_LOG 2026-05-17T20:00:00Z; the broader model-clarification — 1983-1988 pure births-only two-file vs 1989-1991 denominator-plus; DO step 3 → 3a/3b — is soft-flag (ii), proposed-not-applied, queued for §11 human-merge).]*
4. **DO step 4 (2-3 sessions)**: `field_specs.py` layout reconstruction for cohort 1995-2004 (1989-rev birth; ICD-9 1995-1998 / ICD-10 1999-2004; 2003-2004 cohort 1989+2003-rev mix). [former §15.D DO steps 4+5 merged — period work dropped; substrate = `field_specs.py` per the DO step 3 fix-on-contact note above.]
5. **DO step 5 (1-2 sessions)**: parser + `harmonize_linked.py` extensions per cohort era; ICD-9 default-null + revision-tagged per the DO step 1 coupled decision; `cause_recode_130` per-era reconciliation (soft-flag (gg)).
6. **DO step 6 (1-2 sessions)**: re-harmonize linked 1983-2023; preserve v3 parquet as `.v3_baseline.parquet` forward-stability anchor; bump linked v3 → v4; Convention-2/L17 same-commit re-pin of `tests/test_row_count_conservation.py` LINKED pins + B.12 re-snap.
7. **DO step 7 (0.5-1 session)**: update CITATION.cff + .zenodo.json + ABOUT_THIS_RELEASE.md + README.md + PROJECT_STRUCTURE.md + manuscript references; refresh smoke pins; tag `C8.18-complete`.

**VERIFY criteria.**
- Per-year cohort counts 1983-2004 match NCHS cohort Linked File report tables byte-exact.
- 2005-2023 byte-clean regression: 0/N columns drift on the post-2005 slice (anchor preserved per L5 + H10).
- 1992-1994 gap documented in `harmonized_schema.csv` `years_available` cells + CODEBOOK + ABOUT_THIS_RELEASE.md + manuscript Coverage paragraph.
- C8.1's dtype-parity test PASSes on v4 parquet.
- B.12 snapshot regression baseline re-snaps post-rebuild.
- External validation grid: existing 33/35 + 2 docs preserved; new pre-2005 cohort cells added incrementally.

**RECEIPT requirement.** Standard + Forward-looking HALTs covering: 19 cohort source zip SHAs; cohort user-guide PDF SHAs; new layout-CSV SHAs; v4 parquet SHAs; cohort-vs-period design decision artifact at DECISION_LOG (RESOLVED at DO step 1 = Option A cohort-only); B.12 snapshot baseline shift; whether the v3 baseline anchor preserved byte-exact on the 2005-2023 slice; ICD-9 vs ICD-10 handling at DO step 5 (default-null + revision-tagged + future crosswalk task framing per DECISION_LOG 2026-05-17T05:30:00Z).

**Estimated effort.** **~8-11 sessions** (lower end of the original 8-14; cohort-only drops the ~2-3 period sessions and the ICD-9→10 crosswalk is deferred; higher if cohort 1972-1977-analogue layout friction or `cause_recode_130` per-era reconciliation inflates DO step 5).

**Dependencies.** C8.17 modestly (1978-cert layout knowledge from natality 1978-1988 work). Independent of C8.16. One of the largest single-task efforts in pre-Zenodo Phase C.

**Halt-condition flags.** H1, H6, H7 (linked schema must agree with natality on shared concepts), F1 (canonical filter must be year-and-cohort aware), F4 (within-era for ICD-9/10), L1-extension, L9 (NVSR + cohort Linked File report cell-validation at PRE-FLIGHT), L12-extension, L13-extension, L17. Convention 1 SHAPE-not-VALUE.

**Sub-Q42 triggers.** Cohort/period publishing-design = methodology-paper-level decision — **RESOLVED at DO step 1** via the AskUserQuestion + `[plan-update]` sub-entry mechanism (this scope-correction). ICD-9→10 crosswalk if *pursued* >1 session beyond default-null handling triggers a new `[plan-update]` (the settled default-null does not). Period-linked 1995-2004 reconsideration requires its own `[plan-update]` (out of C8.18 scope per Option A).

---

### Task C8.19 — Perinatal-record pre-joined parquet (C.8; methodology research)

> **[plan-update] 2026-05-23 (scope re-definition; applied per §11 step 3; user-authorized 2026-05-23 via AskUserQuestion Option 1).** The original deliverable below — *a validated record-level "perinatal record" parquet (one row per linked-file infant with its fetal-death **sibling** flagged)* — was **proven structurally infeasible on NCHS public-use data** at the §15.D-designed C8.19 PRE-FLIGHT / Tier-0 cheap-check (the off-ramp this spec explicitly built in). Evidence (`PRE_FLIGHT_LOG.md` 2026-05-23T08:00:00Z; 2020 fixture, best value-harmonized maternal key): expected unique-sibling match rate = **0.00000% ≪ the 5% threshold**; mean **15,985** candidate live births per fetal death; the only computable "flag" is true for 98.5% of births (~0 bits of sibling information). Root cause is permanent: NCHS public-use suppresses ALL maternal / household / pregnancy identifiers + ALL sub-national geography, and `maternal_race_bridged` is 100% NULL post-2018; a stillbirth and the same mother's live birth are different pregnancies with no shared key; NCHS publishes no perinatal-record file or record-level linkage. The only public-use-supportable perinatal record-linkage (a stillborn fetus ↔ its liveborn co-multiple) **already ships** as `matched_multiples/` (C8.16); the aggregate perinatal-mortality *rate* already ships via `notebooks/joint_use_demo.ipynb` §C + `docs/JOINT_USE_GUIDE.md` §128. **Corrected deliverable (this re-scope):** ship — pre-submission — a cross-product **perinatal-record feasibility / methodology note** (`docs/PERINATAL_RECORD_FEASIBILITY.md`) + a deterministic reproducible analysis script (`scripts/perinatal_feasibility_analysis.py`) quantifying the suppression limit across representative years, pointers to the two supported perinatal analyses, and a restricted-data (NCHS RDC / state vital records) future-work note. **No 5th parquet; zero canonical-state mutation; no manuscript edit now** (the perinatal limitations paragraph is a D.4 input per the KICKOFF "manuscript re-paragraphed ONCE at D.4" precedent). Manuscript impact moves from "zero if it doesn't" to a **small positive** (a documented rigor / limitations contribution + a future-researcher signpost). C8.20 / C8.21 / C8.22 + Phase D are **unaffected** — C8.19 was purely additive and now produces no parquet; the settled envelope (natality v3.0.0 + linked v4.0.0 + fetal-death v2.4.0 + matched-multiples) is unchanged, so each downstream task's "Dependencies: … C8.19 (final envelope settled)" clause is satisfied. Effort **2-3 → ~1 session** (downward; cap-86 invariant unaffected; the cumulative band below not re-derived for a downward delta — §7-#17-safe). The original text below is preserved (superseded, not deleted) per the §3 append-only-supersede convention + the C8.18 2026-05-17 [plan-update] precedent; full rationale in `DECISION_LOG.md` 2026-05-23 + `PRE_FLIGHT_LOG.md` 2026-05-23T08:00:00Z. **No LESSONS.md entry** — this is not a new mistake class; the §15.D Tier-0 off-ramp worked exactly as designed (the cheap-check caught infeasibility before any expensive DO).

**Goal.** Produce a validated pre-joined "perinatal record" parquet: one row per linked-file infant with fetal-death sibling records flagged (via maternal demographics + state + year join keys, since NCHS suppresses direct identifiers). Limited by suppression; join success rate may be low. Ship as a derived 5th parquet alongside the three existing products. Validate against any published NCHS perinatal-record tabulations.

**Why this matters.** Genuine research-grade derivation. Pairs the linked file's infant-death surface with the fetal-death sibling surface in one record. If successful, substantial manuscript contribution. If join success rate is too low (NCHS identifier suppression limits joinability), task PRE-FLIGHT may surface as too-sparse-to-be-useful and DEFER to v1.1 methodology-paper subproject. Per EXPLORATION_REPORT §C.8: "manuscript-level contribution if it works; zero if it doesn't."

**PRE-FLIGHT inputs.**
- All three (now four including matched-multiples) parquets at post-C8.16 + C8.17 + C8.18 SHAs.
- Maternal-identifier proxy strategy: maternal demographic columns (age + race + Hispanic + education + nativity) + state + delivery year + gestation. PRE-FLIGHT computes the join-key entropy + expected uniqueness; if join-key collisions are dense, surfaces a §7 halt for human review.
- Field-value snapshot (Convention 3): linked-file derived parquet columns + fetal-death derived parquet columns; intersect on join-key proxies; record on-disk count of plausible match candidates per year.
- NCHS-published perinatal-record tabulations (if any exist; PRE-FLIGHT verifies via WebFetch on NCHS canonical pages).

**SMOKE plan.**
- Tier 0: join-key entropy analysis on a 1-year fixture (e.g., 2020 linked + 2020 fetal-death); compute expected match rate; if <5% halt for human review (Q42 trigger; defer to v1.1 methodology-paper subproject).
- Tier 1: full-year 2020 join; count matches; compute matched-vs-unmatched rates by maternal demographic stratum.
- Tier 2: multi-year join (2005-2023 linked × 2005-2023 fetal-death); per-year + per-stratum match counts.
- Tier 3: validation against any NCHS-published perinatal-record tabulations (likely none direct; sub-component validations against fetal-mortality + early-neonatal rate tables).

**DO scope.**
1. Architectural decision (DECISION_LOG entry): join-key proxy strategy; threshold for plausible vs implausible matches; how to flag uncertain matches (`perinatal_match_confidence` column?).
2. Author `scripts/04_derive/build_perinatal_record.py` producing `output/harmonized/perinatal_record_derived.parquet`.
3. Validation grid: per-year + per-stratum match counts vs expected (NCHS-published fetal-mortality + ENN rate sub-components).
4. Worked-example notebook `notebooks/perinatal_record_demo.ipynb` (within-era only).
5. Update CITATION.cff + ABOUT_THIS_RELEASE.md + manuscript references; document the join-key proxy methodology + the suppression-induced limitations.

**VERIFY criteria.**
- Join success rate ≥ documented threshold (set at PRE-FLIGHT per Tier-0 analysis).
- Per-year match counts within ±5% of NCHS-published fetal-mortality + ENN sub-component cells.
- C8.1 dtype-parity test PASSes on perinatal_record parquet.
- No regression on existing 4 parquets (this task is purely additive).

**RECEIPT requirement.** Standard + Forward-looking HALTs + join-key methodology DECISION_LOG entry + suppression-induced-limitations documentation.

**Estimated effort.** **2-3 sessions** (lower if architecture decision is clear at PRE-FLIGHT; higher if join-key proxy strategy requires iterative refinement).

**Dependencies.** C8.17 (post-extension natality + linked parquets at v2.9 + v4 SHAs).

**Halt-condition flags.** H6 (row-count conservation across the new join), F2 (cross-product join without canonical filter on both sides), H9, L7 ("looks reasonable" without explicit threshold), L9 (NCHS perinatal-record cell location must be cited if available). Sub-Q42 trigger: PRE-FLIGHT Tier-0 entropy analysis may surface a §7.13 halt → defer to v1.1.

---

### Task C8.20 — CODEBOOK extensions (E.7; per-variable historical distributions + sentinel disambiguation + era diffs)

**Goal.** Extend per-product CODEBOOK.md with three new per-variable subsections: (i) historical-value-distribution panels (per-era code-frequency tables); (ii) sentinel-code disambiguation tables (e.g., MAGER 99 vs 999 vs blank semantics per era); (iii) era-by-era coding-scheme diff (which fields changed semantics at 1989 / 2003 / etc. cert-revision boundaries). Cover both `fetal_death/CODEBOOK.md` and `natality/docs/CODEBOOK.md`.

**Why this matters.** Current CODEBOOK gives variable definitions but not the per-era code-distribution evidence that lets researchers decide whether to use a variable across a boundary. Extends manuscript *Comparability classification* claim. EXPLORATION_REPORT §E.7 priority = medium; diminishing returns vs existing CODEBOOK.

**PRE-FLIGHT inputs.**
- Per-product harmonized_schema.csv (variable list).
- Per-product COMPARABILITY.md (era-boundary catalog).
- Final post-C8.16 + C8.17 + C8.18 + C8.19 parquets (so distributions reflect the full envelope).
- Field-value snapshot (Convention 3): current CODEBOOK.md line counts + structure; sample existing variable-section format to mirror.

**SMOKE plan.**
- Tier 0: render 1 example variable's historical-distribution panel + sentinel-disambiguation table; verify rendering + cell-content + cross-link integrity.
- Tier 1: render all variables for one product (fetal-death first as smaller surface).
- Tier 2: render all variables for both products; verify total line count + cross-link target integrity (no broken internal references).

**DO scope.**
1. Author `scripts/_build_codebook_extensions.py` (per-product deterministic builder).
2. Render fetal-death CODEBOOK extensions (per-variable historical-distribution + sentinel + era-diff).
3. Render natality CODEBOOK extensions.
4. Update each product's docs/FAQ.md with pointers to the new CODEBOOK sections.

**VERIFY criteria.**
- Both per-product CODEBOOK.md files extended with the three new subsections per variable.
- Cross-link integrity: all internal anchors resolve.
- C8.20-shipped tables reconcile against parquet distributions (deterministic builder; re-running produces identical CODEBOOK byte-exact).
- No regression in test suite (pure docs task).

**RECEIPT requirement.** Standard + Forward-looking HALTs covering: new CODEBOOK.md SHAs; builder script SHAs.

**Estimated effort.** **2-4 sessions** (lower if final envelope from C8.17 + C8.18 doesn't add new per-variable historical patterns; higher if new pre-1990 natality + pre-2005 linked variables require novel sentinel-disambiguation work).

**Dependencies.** C8.17 + C8.18 + C8.19 (final envelope must be settled for the historical-distribution panels to reflect the v1.0 release state).

**Halt-condition flags.** H8 (docs vs data drift; CODEBOOK numbers must auto-derive from the parquets), L6 (no invented numbers in docs; every cell traces to parquet computation). Convention 1 SHAPE-not-VALUE (CODEBOOK extension assertions are SHAPE: structural-class).

---

### Task C8.21 — Stata + SAS quickstart pointer files (C.3)

> **[plan-update] 2026-05-23 (premise-correction; optional, non-blocking; applied per §11 step 3 — user-authorized 2026-05-23 "Pre-D cleanup first"; the L9/§7-#12 fix-on-contact class, NOT a §7 human-halt).** The Goal/PRE-FLIGHT-inputs claim *"Stata 17+ supports `import parquet`"* / *"PROC IMPORT … (or PROC PARQUET if available)"* is factually wrong and was corrected in the shipped C8.21 deliverable (DECISION_LOG 2026-05-23T16:00:00Z; L9-verified on official domains): native Stata `import parquet` is **StataNow-only** (stata.com/manuals/dimportparquet.pdf — "part of StataNow"), not "Stata 17+"; **SAS 9.4 has no native Parquet read** (Parquet LIBNAME unsupported in SAS 9; **SAS Viya** exposes an ORC/Parquet **LIBNAME engine**, not `PROC IMPORT DBMS=PARQUET`). The shipped `STATA_SAS_QUICKSTART.md` uses the verified Parquet→CSV bridge (DuckDB `COPY` / `quickstart.py` → `import delimited` / `PROC IMPORT DBMS=CSV`) as the primary universal path, with the native options correctly version-caveated. Deliverable surface/scope unchanged ⇒ §15.D-text accuracy correction only (the C8.19/C8.21/C8.22 §15.D-vs-reality fix-on-contact class).

**Goal.** Author half-page pointer files for Stata + SAS users explaining how to load the parquet artifacts. Stata 17+ supports `import parquet`; older Stata + SAS need a conversion path (Python or DuckDB). Files ship as `quickstart.do` (Stata) + `quickstart.sas` (SAS) or `STATA_SAS_QUICKSTART.md` (pointer; deferred full worked examples per EXPLORATION_REPORT §C.3).

**Why this matters.** Stata + SAS users currently have no entry point. Pointer files lower the barrier even without full worked examples (which would need Stata/SAS licenses on the build machine). EXPLORATION_REPORT §C.3 priority = medium.

**PRE-FLIGHT inputs.**
- Published Stata 17+ `import parquet` documentation.
- Published SAS PROC IMPORT documentation (or PROC PARQUET if available).
- One DuckDB-based conversion path (parquet → CSV via `duckdb`).

**SMOKE plan.**
- Tier 0: render the pointer text; verify the Stata + SAS code samples are syntactically plausible (cite published examples).

**DO scope.**
1. Author `STATA_SAS_QUICKSTART.md` (or sibling per-language `quickstart.do` + `quickstart.sas`).
2. Update `docs/WORKED_EXAMPLE_FAQ.md` "Load the data in R / Stata / SAS" matrix entry to reference the new pointer file.
3. Update monorepo README.md if needed.

**VERIFY criteria.**
- Pointer file exists at canonical path.
- Cross-link from WORKED_EXAMPLE_FAQ.md matrix resolves.
- No test-surface regression (pure docs).

**Estimated effort.** **0.5 sessions**.

**Dependencies.** None.

**Halt-condition flags.** L6 (cite published syntax; don't invent), L9 (verify named Stata/SAS doc anchors exist).

---

### Task C8.22 — Pre-computed cross-tab CSVs (C.5)

> **[plan-update] 2026-05-23 (scope-clarification; optional, non-blocking; applied per §11 step 3 — user-authorized 2026-05-23 "Pre-D cleanup first"; the L9/L11/§7-#12 fix-on-contact class, NOT a §7 human-halt).** The Goal's *"per-year × per-state × per-race counts"* per-**state** slice is structurally infeasible: NCHS suppresses ALL sub-national geography in the public-use natality/fetal-death/linked files (an explicit Convention-3 geography-column probe returned NONE in all three gate parquets; cf. §16 Known-data-caveats + `PROJECT_STRUCTURE.md` "Get state-level data → not available from public-use NCHS files"). It was substituted in the shipped C8.22 deliverable by the feasible, higher-NVSR-citation **race + maternal-age national stratifications**, documented prominently in `csv/published_tabulations/README.md` + `docs/WORKED_EXAMPLE_FAQ.md` (DECISION_LOG 2026-05-23T18:00:00Z D1). Same class as C8.19 ("5th record-level perinatal parquet" infeasible) + C8.21 ("Stata 17+ import parquet" false). Deliverable surface/scope (a `csv/published_tabulations/` folder of top-N NVSR-cited tabulations) unchanged ⇒ §15.D-text correction only.

**Goal.** Generate `csv/published_tabulations/` folder with the top-10 most-cited NVSR-equivalent tabulations as pre-computed CSVs: per-year × per-state × per-race counts; per-year × age-band fertility rates; per-year × race fetal mortality rates; per-year × race IMR; etc. Lets users cite HVS without loading the parquet.

**Why this matters.** Convenience layer for non-Python users. Pure derivation from the parquets; deterministic builder. Maintenance tax: every parquet bump regenerates these.

**PRE-FLIGHT inputs.**
- Final post-C8.16 + C8.17 + C8.18 + C8.19 parquets (envelope settled).
- Canonical-filter definitions from `docs/JOINT_USE_GUIDE.md`.
- Top-N NVSR-cited tabulation list (curated from manuscript references + existing validation_results.csv).

**SMOKE plan.**
- Tier 0: generate 1 example cross-tab CSV; verify rendering + filter application + per-cell count vs known NVSR cell.

**DO scope.**
1. Curate top-N tabulation list (~10 cross-tabs).
2. Author `scripts/_build_published_tabulations.py` (deterministic builder; one function per tabulation).
3. Generate `csv/published_tabulations/<tab_name>.csv` for each tabulation.
4. Author `csv/published_tabulations/README.md` describing each tabulation + the canonical filter applied.
5. Update monorepo README.md + PROJECT_STRUCTURE.md + WORKED_EXAMPLE_FAQ.md with pointers.

**VERIFY criteria.**
- All N cross-tab CSVs present at canonical path.
- Each CSV's cells reconcile against the corresponding NVSR cell (where validated NVSR cells exist).
- Deterministic builder: re-running produces byte-identical CSVs.

**RECEIPT requirement.** Standard + Forward-looking HALTs covering: cross-tab CSV SHAs; builder script SHA; SHA stability across re-run.

**Estimated effort.** **1 session**.

**Dependencies.** C8.17 + C8.18 + C8.19 (final envelope must be settled for the cross-tabs to reflect v1.0 release state).

**Halt-condition flags.** F1 (canonical filter applied per tab), F2 (cross-product joins use canonical filter on both sides), H6 (row-count conservation), L6 (no invented numbers; every cell auto-derived).

---

# §15.E Phase D-prep tasks (authorized 2026-05-24; agent-executable; reversible; standing authorization)

Per the 2026-05-24 `[plan-update]` (KICKOFF.md "Phase D-prep" section + DECISION_LOG 2026-05-24T01:30:00Z), 5 reversible doc/CSV-only tasks ship before externally-irreversible Phase D entry. **All zero canonical-state mutation expected; 4 gate parquet SHAs must remain byte-exact** (`38e2cecb…` / `185c071e…` / `acb5c48a…` / `f630d8cf…`). Sessions proceed under standing authorization; halt only on §7 conditions.

### Task D-prep.1 — `fetal-death-other-docs-v240-sync` (R2d + `data_year` L60 fix)

**Goal.** Sync the remaining `fetal_death/*.md` hand-docs from the V2.0 / 29-yr / 1992-2022 envelope to v2.4.0 / 43-yr / 1982-2024 / 7-era, matching the depth of the 2026-05-23 `fetal-death-codebook-comparability-v240` task (CODEBOOK + COMPARABILITY). Also fix the `data_year` L60 stale `Years` column (`1992-2022` → match v2.4.0 envelope) flagged as self-check residual in `RECEIPTS/audit-fix-r1r2-bundle_2026-05-24T00-45-00Z.md`.

**Why this matters.** Audit R2d explicit defer; these docs land in Phase D.3 public-repo sync and the unified Zenodo deposit — V2.0-stale envelope text would mislead permanent-DOI users.

**PRE-FLIGHT inputs.** All 7 target files + `fetal_death/CODEBOOK.md` L60. Field-value snapshot per file: quote the V2.0/1992-2022 anchor phrases; enumerate every parquet-derived number that needs v2.4.0 replacement (envelope total 2,427,233 + per-era counts from CODEBOOK Appendix C8.20).

**SMOKE plan.** Tier-0/1 doc-only: per-edit anchor-string uniqueness via `grep -c`; baseline 4 gate parquet SHAs; baseline `fetal_death/CODEBOOK.md` Appendix C8.20 marker block (must be byte-identical post-DO — same C8.20 generated-block invariant the 2026-05-23 task preserved).

**DO scope.** Per-file: Option-A envelope + cross-era narrative depth (per-variable V2/V1 within-era statements preserved; V3b/V3a/V2.1 added; every number parquet-derived from Appendix C8.20, none hand-invented — L6-safe). Files: `ABOUT_THIS_RELEASE.md`, `ABOUT_SOURCE_DATA.md`, `FAQ.md`, `GETTING_STARTED.md`, `REPRODUCING.md`, `REPORTING_THRESHOLDS.md`, `README.md` + `CODEBOOK.md` L60. Bundle as ONE single task under full five-phase discipline (the C8.20-auditfix + audit-fix-r1r2-bundle precedent for multi-file doc bundles sharing the zero-canonical-mutation invariant).

**VERIFY criteria.** Per-edit grep evidence; 4 gate parquet SHAs byte-exact pre/post; Appendix C8.20 marker block byte-identical pre/post (use marker-extraction, not line-range — per FIX_LOG 2026-05-23 lesson); no V2.0/1992-2022 envelope phrasing residue in the 7 target docs (post-DO grep).

**RECEIPT requirement.** Standard + Forward-looking HALTs (Convention 4) flagging: (a) Phase D-prep.1 closed; (b) gate SHAs unchanged; (c) D-prep.4 audit will now see post-R2d state; (d) Phase D entry remains explicitly-authorization-gated.

**Estimated effort.** 1-2 sessions.

**Dependencies.** None internal. `audit-fix-r1r2-bundle` (2026-05-24) deferred R2d to this task explicitly.

**Halt-condition flags.** L6 (no invented numbers — all parquet-derived from Appendix C8.20), L11 (stale roadmap claims — fix-on-contact within scope), H8 (doc-data drift — the target class), §7-#17 (scope creep — keep the 7 target docs scope; do not touch CODEBOOK.md or COMPARABILITY.md hand-body content, which the 2026-05-23 task already shipped at v2.4.0).

---

### Task D-prep.2 — `provenance-refresh-current-envelope`

**Goal.** Refresh each subproject's `PROVENANCE.md` so the documented shipped-artifact SHA-256s match the current on-disk parquets: fetal-death v2.4.0 (`38e2cecb…` / `185c071e…`), natality v3.0.0 (`c8a740eb…` / `acb5c48a…`; legacy `natality_v2_*` filename retained per C8.17 schema-family-tag convention), linked v4.0.0 (`ea89ab3c…` / `f630d8cf…`), matched-multiples (C8.16 SHAs). Cross-reference with `docs/NCHS_SOURCE_MANIFEST.md` (the unified source-zip SHA manifest).

**Why this matters.** Phase D.2 Zenodo deposit deposit integrity depends on documented SHAs matching uploaded artifacts. §9-#15 forbids modifying published deposits, so the PROVENANCE files must be correct BEFORE deposit creation.

**PRE-FLIGHT inputs.** Each subproject's current `PROVENANCE.md`; independently re-hash all shipped parquets; verify against the STATUS-anchor SHAs.

**SMOKE plan.** Tier-0 doc-only: `shasum -a 256` on each shipped parquet; verify each matches the canonical STATUS anchor + the `docs/NCHS_SOURCE_MANIFEST.md` SHIPPED reference if applicable.

**DO scope.** Per-subproject `PROVENANCE.md` update; every SHA explicitly typed (no copy-paste from stale doc); cross-product manifest in `docs/NCHS_SOURCE_MANIFEST.md` regenerated if shipped-artifact references are present.

**VERIFY criteria.** Every documented SHA in every PROVENANCE.md matches the on-disk re-hash; `git diff` confined to PROVENANCE files (+ docs manifest if touched); 4 gate parquet SHAs unchanged.

**RECEIPT requirement.** Standard.

**Estimated effort.** 0.5 session.

**Dependencies.** Can run in parallel with D-prep.1 (different file surface). Must precede D-prep.4 (audit will check PROVENANCE integrity).

**Halt-condition flags.** L6 (no invented SHAs — re-hash empirically), H10 (provenance/reproducibility drift — the target class).

---

### Task D-prep.3 — `schema-years-available-gap-notation`

**Goal.** Retroactively annotate per-product `harmonized_schema.csv` `years_available` cells to reflect the current envelope's era boundaries + permanent gaps: fetal-death V3b (1982-1988, 1978-rev) + V3a (1989-1991, early-1989-rev) + V2.1 (2003-2004, transition); linked 1992-1994 permanent NCHS gap. Per the 2026-05-12T18:45Z Q30 plan + the Phase-D deposit integrity requirement.

**Why this matters.** `years_available` is a per-column declarative field that downstream consumers read to know "which years of data is this column populated for". Stale cells (e.g., a column with V3b coverage that says `1992-2022` instead of `1982-1988, 1992-2022`) misroute analyses.

**PRE-FLIGHT inputs.** Each subproject's current `harmonized_schema.csv`; per-product per-year null-rate report (cheap: groupby data_year + count non-nulls per column) to ground-truth which columns DO have V3b/V3a/V2.1 coverage and which don't.

**SMOKE plan.** Tier-0 doc/CSV-only: cheap empirical null-rate ground-truth via DuckDB or pandas; SHAPE-not-VALUE schema row count preserved.

**DO scope.** Per-product `harmonized_schema.csv` update only; per-column `years_available` cell annotation; +1 column comment row referencing this DECISION_LOG entry per §9-#6.

**VERIFY criteria.** Every annotated `years_available` cell matches the empirical null-rate ground-truth; schema row count unchanged; 4 gate parquet SHAs unchanged; existing tests pass (`test_schema_dtype_parity.py`).

**RECEIPT requirement.** Standard.

**Estimated effort.** 0.5 session.

**Dependencies.** Can run in parallel with D-prep.1 + D-prep.2.

**Halt-condition flags.** L6 (annotations must be empirically grounded), H7 (sibling-pipeline drift — both products' schemas must agree on shared concepts).

---

### Task D-prep.4 — `pre-zenodo-audit-pass`

**Goal.** One focused fresh-eyes adversarial audit pass covering the substantive Phase C deliverables C8.16-C8.22 + the cross-product joint-use surface + user-facing docs (post-D-prep.1/2/3) + reproducibility surface + the existing `paper/draft_v2_hmd_styled.md` draft as D.4 input. Surface findings BEFORE externally-irreversible Phase D entry.

**Why this matters.** §9-#15: Zenodo deposits are immutable once published. The prior 2-round adversarial audit covered only the 5-task Pre-D cleanup block; the substantive Phase C deliverables (C8.16-C8.22) have RECEIPTS paper trails but no adversarial audit. Cheap to run; high-leverage at this point.

**PRE-FLIGHT inputs.** Confirm Phase D-prep 1+2+3 complete (otherwise audit will re-flag known stale items as findings); confirm working tree clean; confirm 4 gate parquet SHAs match anchors.

**SMOKE plan.** N/A — audit is a read-only investigation, not a mutation.

**DO scope.** **Two execution modes:**
- **Recommended (user-triggered): `/ultrareview`** from this repo. The KICKOFF audit-session framing's prescribed mechanism for pre-Zenodo broader-audit surfaces (canonical pipelines + cross-product surface + Phase D itself surfaces explicitly out of scope of 2-round-fresh-eyes pattern, per KICKOFF). User-triggered + billed; agent cannot launch.
- **Fallback (agent-launched): 5-agent fresh-eyes adversarial round** paralleling the prior R1/R2 Pre-D cleanup pattern. 5 parallel sub-agents, each scoped to one surface, each refused prior RECEIPTS/FIX_LOG/LESSONS/DECISION_LOG access:
  - **Audit #1 — Data integrity**: 4 shipped parquet SHAs re-hash; per-product schema parity with pyarrow dtypes; NVSR validation cells reproducible
  - **Audit #2 — User-facing docs (post-D-prep.1)**: per-product CODEBOOK + COMPARABILITY + FAQ + GETTING_STARTED + REPRODUCING + READMEs; cross-product `docs/JOINT_USE_GUIDE.md` + `docs/COMPARABILITY.md`; numerics derivable; no V2.0-envelope residue
  - **Audit #3 — Reproducibility surface**: `file_inventory.csv` SHAs match on-disk NCHS source files; `NCHS_SOURCE_MANIFEST.md` cross-references intact; per-product `REPRODUCING.md` instructions accurate
  - **Audit #4 — Notebooks**: `joint_use_demo.ipynb` + `paper_companion.ipynb` + `matched_multiples_demo.ipynb` runnable end-to-end against shipped parquets; documented values reproduce
  - **Audit #5 — Manuscript-readiness (D.4 input)**: `paper/draft_v2_hmd_styled.md` numerics match current envelope; word count under IJE Data Resource Profile limit (2,500 main excl. abstract/refs/tables); references resolve; admin sections drafted
- User may request additional rounds (2nd round mirroring R1/R2 pattern).

**VERIFY criteria.** Audit reports written to `AUDITS/round3/*.md` (mode: fallback) or wherever `/ultrareview` deposits findings (mode: recommended). Findings categorized PASS / FINDING / HALT. Consolidated report at `AUDITS/CONSOLIDATED_PRE_ZENODO_<UTC>.md`.

**RECEIPT requirement.** Standard + per-audit verdict summary + remediation-bundle proposal if findings.

**Estimated effort.** ~1 session (parallel audits).

**Dependencies.** D-prep.1 + D-prep.2 + D-prep.3 ALL complete (otherwise re-flags known items).

**Halt-condition flags.** Any audit-surfaced §7 condition → halt before Phase D entry. Any §6 schema validation failure → halt.

---

### Task D-prep.5 — `pre-zenodo-audit-fix-bundle` [CONDITIONAL on D-prep.4 findings]

**Goal.** Ship a doc/CSV-only remediation bundle if D-prep.4 surfaces non-blocking findings. Mirrors the 2026-05-24 `audit-fix-r1r2-bundle` + 2026-05-23 `C8.20-auditfix` precedents: ONE single task under full five-phase discipline, doc/CSV-only, zero canonical-state mutation.

**Trigger condition.** D-prep.4 surfaces ≥1 remediable finding (L7/L11/H8/L6-family class) that doesn't require canonical pipeline rebuild. If D-prep.4 returns PASS / no findings: this task is SKIPPED.

**Why this matters.** §9-#15: Zenodo immutability. Land all known-good remediations before D.2.

**PRE-FLIGHT/SMOKE/DO/VERIFY/RECEIPT shape.** Inherited from the `audit-fix-r1r2-bundle` precedent. Field-value snapshot for every site to be mutated; SHAPE-not-VALUE smoke on the doc/CSV diff dry-runs; DO in one commit; VERIFY via per-edit grep + 4 gate SHA invariant + scope check; RECEIPT with §10 self-check + Convention 4 forward-looking HALTs.

**Estimated effort.** 0.5-1 session (proportional to finding count).

**Dependencies.** D-prep.4 surfaces findings.

**Halt-condition flags.** If audit surfaces a finding that REQUIRES canonical pipeline rebuild (e.g., a parquet schema defect, NVSR cell regression): **§7 halt**; halt-and-ask the human; do not silently absorb into a doc-only bundle (that's L6 / §9-#7).

---

# §15.F Robustness roadmap (authorized 2026-05-24; agent-executable; local-first)

Per the manuscript *Future developments* robustness roadmap (user-authorized 2026-05-24; supersedes stale KICKOFF "D.2 next" queue for agent sessions that explicitly defer paper work). Four tasks strengthen validation and consistency without canonical parquet mutation unless a task explicitly requires it. **Default invariant: 4 gate parquet SHAs byte-exact** (`38e2cecb…` / `185c071e…` / `acb5c48a…` / `f630d8cf…`); matched-multiples harmonized (`adbec108…`) may be read but not rebuilt in doc/validation-only tasks.

### Task RD.1 — `pre-1990-natality-nvsr-benchmarking` ✅ **COMPLETE 2026-05-24**

**Goal.** Extend natality external validation backward to 1968–1989 using *Births: Final Data* / NVSR published tables, matching the 1990–2024 byte-exact discipline.

**Shipped (2026-05-24).** 22 `resident_births` cells (1968–1989); SAMPWT-weighted compare path; smoke tests. **205/205 PASS** (183/183 1990–2024 unchanged). Receipt: `RECEIPTS/RD.1-pre-1990-natality-nvsr-benchmarking_2026-05-24T20-20-42Z.md`. Tags: `RD.1-pre-1990-natality-nvsr-benchmarking-{pre-do,complete}`.

**Deferred to RD.1b.** Rate metrics (LBW, preterm, twin, cesarean, etc.) for years before 1990.

**Why this matters.** Largest single "more data" win (EXPLORATION_REPORT §A.2); doubles natality coverage to 57 yrs; pairs with fetal-death 1982–2024 for joint analyses back to 1982.

**PRE-FLIGHT inputs.** Build tree at `~/Desktop/natality-harmonization` (required — pre-1990 yearly parquets not in this clone). NVSR table inventory from PRIOR_ART + existing `external_validation_targets*.csv` patterns.

**SMOKE/DO/VERIFY.** Full five-phase discipline; new targets committed to CSV before validator changes; zero regression on existing 183/183 V2 targets.

**Estimated effort.** 2–3 sessions (NVSR transcription + target commit + validator extension).

**Dependencies.** Build host / natality-harmonization tree.

**Halt-condition flags.** L6 (no invented NVSR cells), H6 (row-count conservation), §7 if pre-1990 parquet envelope differs from assumed.

---

### Task RD.2 — `matched-multiples-cell-validation-1995-2000` ✅ **COMPLETE 2026-05-24**

**Goal.** Extend matched-multiples validation from 2016-2020 PDF Table 1 (5 cells) to all three windows: 14 Table 1-equivalent targets per 1995-1997 and 1995-2000 window (5 BIRTHID outcome totals + 9 set_complete×outcome cells) + retained structural invariants → **41 targets total**.

**Why this matters.** Closes the largest validation gap in the matched-multiples product; manuscript *Future developments* item #2.

**Shipped (2026-05-24).** New `matched_multiples/external_validation_targets.csv` (28 committed cells); extended `scripts/05_validate/validate_matched_multiples.py`; smoke tests for 1995-1997 / 1995-2000 Table 1 totals; README + ABOUT_SOURCE_DATA updates; `validation_results.{csv,md}` regenerated. **41/41 PASS.** Harmonized parquet SHA `adbec108…` unchanged. Receipt: `RECEIPTS/RD.2-matched-multiples-cell-validation_2026-05-24T19-40-00Z.md`. Tags: `RD.2-matched-multiples-cell-validation-{pre-do,complete}`.

**Deferred within scope.** Table 2 (gender × maternal age / set-level tables) — NBER `e_Cnttab2a.pdf` structure acquired; numeric transcription not yet committed.

**Halt-condition flags (resolved).** Layout PDFs omit printable Table 1 counts → targets anchored at C8.16 raw BIRTHID crosstab + NBER structure PDF (DECISION_LOG 2026-05-24T19:40:00Z).

---

### Task RD.3 — `consistency-cleanup-cross-race-roadmap` ✅ **COMPLETE 2026-05-24**

**Goal.** Doc/consistency pass: reconcile `notebooks/cross_race` stale claims, `VERSION_ROADMAP.md` natality-V4 wording, and any L11 stale roadmap items surfaced during RD.1/RD.2 — **no `paper/` edits** unless user explicitly re-opens manuscript work.

**Why this matters.** Pre-Zenodo audit (D-prep.4) will flag stale cross-doc claims; cheap to fix now.

**Shipped (2026-05-24).** `VERSION_ROADMAP.md` → unified Zenodo v1.0.1 + four-product table; root `README.md` → 41/41 matched-multiples + four-product validation framing; `natality/README.md` + `fetal_death/README.md` Zenodo/citation lines; `cross_race_fetal_mortality.ipynb` intro (seven eras, 2014–2024 OE); `PROJECT_STRUCTURE.md` notebook-deps row. Residual grep: no `5/5` / `not yet deposited` in user-facing docs (append-only logs excluded). Receipt: `RECEIPTS/RD.3-consistency-cleanup-cross-race-roadmap_2026-05-24T19-47-38Z.md`. Tags: `RD.3-consistency-cleanup-cross-race-roadmap-{pre-do,complete}`.

**Estimated effort.** 0.5–1 session.

**Dependencies.** None blocking; best after RD.2 (validation headline counts stable).

**Halt-condition flags.** L11 (stale roadmap claims — fix-on-contact within scope only).

---

### Task RD.4 — `matched-multiples-icd9-icd10-derived-layer` ⏳ [OPTIONAL]

**Goal.** Add a **derived-only** ICD-9→ICD-10 bridge column for 1995-2000 infant-death cause codes (1999-2000 native ICD-10 block already present); never write into canonical `cause_of_death_icd` harmonized column.

**Why this matters.** Enables cross-window cause-of-death analysis without breaking the ICD-9/ICD-10-as-shipped comparability class.

**PRE-FLIGHT inputs.** Empirical ICD-9/ICD-10 overlap on 1999-2000 records; GEM or published bridge table choice; schema `derived_*` column naming convention.

**Estimated effort.** 1–2 sessions (bridge table + derived parquet + tests).

**Dependencies.** RD.2 complete (validation baseline stable).

**Halt-condition flags.** H7 (sibling schema drift), §7 if bridge requires RDC-only mappings.

---

### Task RD.1b — `pre-1990-natality-rate-benchmarking` ⏳ (Phase A ✅ 2026-05-24; Phase B–C open)

**Phase A shipped (2026-05-24).** 10 `lbw_rate_pct` cells (1980–1989) from childstats HEALTH1.B; SAMPWT-weighted raw LBW path for 1980–1988; **215/215 PASS**. Receipt: `RECEIPTS/RD.1b-pre-1990-natality-rate-benchmarking-phase-a_*.md`. Tags: `RD.1b-pre-1990-natality-rate-benchmarking-phase-a-{pre-do,complete}`.

### Task RD.1b (continued) — Phase B–C ⏳ **NEXT after Phase A**

**Goal.** Extend natality external validation **rate** targets backward before 1990, in slices:

1. **Phase A (this task’s MVP):** `lbw_rate_pct` for **1980–1989** from childstats.gov table HEALTH1.B (Total row; same source class as 1990–2004 targets). Tolerance 0.05 pct-pt. Derived-parquet stream (1989 = 100% file; 1980–1988 validated on build host — add SAMPWT-weighted rate path only if derived rates fail).
2. **Phase B (follow-on session):** `preterm_rate_pct` 1980–1989 if a citable national series is located (HEALTH1.A starts 1990; do not invent).
3. **Phase C (follow-on / defer):** 1968–1979 rates — NVSR *Vital Statistics of the United States* / MVSR transcription (no childstats HEALTH1.A/B floor before 1980).

**Why this matters.** Closes the largest remaining natality validation gap after RD.1; manuscript *Future developments* “pre-1990 NVSR benchmarking” item.

**PRE-FLIGHT inputs.** Build tree `~/Desktop/natality-harmonization`; `external_validation_targets_v1.csv`; childstats HEALTH1.B cited values; 4 gate derived SHA `acb5c48a…` unchanged.

**SMOKE/DO/VERIFY.** Five-phase discipline; commit targets before validator changes; zero regression on 205/205 resident-birth + 183/183 1990+ rate cells; expect **+10** LBW cells → **215/215** minimum on Phase A alone.

**Estimated effort.** Phase A ~0.5–1 session; Phase B–C +2–3 sessions if authorized.

**Dependencies.** RD.1 complete.

**Halt-condition flags.** L6 (no invented NVSR/childstats cells), §7 if derived vs SAMPWT-weighted rates diverge >tolerance for 1972–1988.

---

# §16. Cross-cutting concerns

### What NOT to change without consulting the user

- Era boundaries, harmonization rules, value-level normalizations (B1–B6 for fetal death; the analogous within-revision normalizations for natality and linked).
- The canonical analytic filters (`tabulation_flag == '2' AND residence_status != '4'` for fetal death; `restatus != '4'` for natality and linked). These reproduce the *NVSR* aggregates.
- Existing column names in any `harmonized_schema.csv`. Renames break user code.
- Existing Zenodo DOIs.

### Conventions to preserve

- **Subproject independence.** Each subproject is self-contained. Cross-product code lives in `shared/helpers/` or `notebooks/`, not inside either subproject.
- **One stable schema per product.** Harmonized schema columns do not change across versions. Within a column, values may be added but existing codes are not redefined.
- **Per-year raw parquets are sacred.** They preserve every documented source field. Do not modify after release.
- **Validation against published *NVSR* figures is the gold standard.** Any change that breaks a previously-passing *NVSR* cell is a regression and must be justified.
- **Bit-reproducibility.** The harmonized parquet is byte-identical when the pipeline is re-run. SHA-256 checksums in PROVENANCE.md are the test.

### Known data caveats

- **Cause-of-death codes for fetal deaths before 2014.** Not in the public-use file. RDC-only.
- **State-level identifiers in V1-era fetal-death public-use files (2005+).** Suppressed by NCHS at source.
- **Maternal education across the 1989/2003 boundary.** No bridge provided. The two fields (`maternal_education_unrevised`, `maternal_education`) are deliberately separate.
- **State reporting quirks 1992–2002.** Oklahoma Hispanic, Maryland (1992–1998), Massachusetts (1992–1997), Louisiana plurality 1992–1994. Documented in `fetal_death/COMPARABILITY.md`.

### Stale items in current docs to fix on contact

- ~~`fetal_death/README.md` Version Roadmap lists "V4: Natality companion product" as future.~~ **Resolved RD.3 (2026-05-24)** — fetal README roadmap now lists joint-use layer; no V4 natality line.

---

# §17. Definition of "ready to submit"

The manuscript is ready to submit when:

1. ✅ Three products published to Zenodo with persistent DOIs.
2. ✅ Pipelines deterministic and re-runnable end-to-end.
3. ✅ Joint-use convenience layer shipped (Task 1, 2026-05-11).
4. ✅ Joint-use demo notebook shipped (Task 2, 2026-05-11).
5. ✅ Linked-file validation framing reconciled (Task 6, 2026-05-11).
6. ✅ Manuscript at IJE word limit with admin sections drafted (Task 5, 2026-05-11).
7. ✅ Paper-companion notebook reproducing every numeric claim (Task 4, 2026-05-11).
8. ⏳ V2.1 fetal-death (2003–2004) ideally shipped (Task 3).
9. ⏳ Cross-product Figure 1 (Task 8).
10. ⏳ Old GitHub repos pointed at the monorepo (Task 9).
11. ⏳ Unified Zenodo deposit reserved (Task 10).

Task 7 (V3 1982 extension) is post-submission. Do not block submission on V3.

---

# §18. How to use this document

### As an LLM agent

1. Run the §1 session-start sequence.
2. Pick a task from §15 in priority order, or follow the user's explicit instruction.
3. Run the five-phase structure (§4) for the task. Halt on any §7 condition.
4. Write the receipt (§6). Update STATUS.md.
5. If new lesson: append to LESSONS.md and propose a §8 matrix entry.

### As a human collaborator

1. Skim §1 and §14 to load context.
2. Pick what to work on or hand a task to an agent. Be explicit about which task ID from §15.
3. Update §15 task statuses as tasks complete; promote completed tasks to ✅ in §17.
4. When the manuscript is submitted, archive this document or move it to `docs/post-submission-followups.md` for V3 and later work.

---

---

# §19. LLM prompt templates for paper drafting (fresh-chat use, OUTSIDE Claude Code)

Per the 2026-05-24 plan-update (KICKOFF "Phase E" section + DECISION_LOG 2026-05-24T01:30:00Z), the two paper drafting prompts below are **self-contained for use in a fresh LLM chat that does NOT have access to this monorepo**. Paste the prompt into claude.ai web (or similar), attach the listed files as inputs, and engage the chat. **These prompts are NOT for Claude Code in this monorepo**; the Claude Code agent's role is narrow (data-structure Q&A, small analysis-script helpers, companion-paper tooling) and the substantive paper drafting happens in the fresh chat.

The prompts deliberately do not embed numerics or quote internal narrative — those go in the attached files. The fresh chat will read the attachments, not infer from prompt text. This keeps the prompts stable as the project evolves (Zenodo DOI lands, public GitHub URL lands, etc. — the fresh chat reads the latest CITATION.cff / README.md from the attached repo snapshot).

### §19.1 — Paper 1 (Data Descriptor) finalization prompt — Phase D.4 use

**When to use.** At Phase D.4, after Phase D-prep + Phase D.1-D.3 complete. The Zenodo DOI + the public GitHub URL exist by D.4 (D.2 + D.3 ship them). The descriptor draft at `paper/draft_v2_hmd_styled.md` is the substrate.

**What to attach (fresh chat input files):**
- `paper/draft_v2_hmd_styled.md` (the current preferred draft, modeled on HMD IJE 2015)
- Top-level `README.md` (4-products-at-a-glance summary)
- Per-product `README.md` for `natality/`, `fetal_death/`, `matched_multiples/`
- `docs/JOINT_USE_GUIDE.md`
- `docs/COMPARABILITY.md`
- `docs/PRIOR_ART.md`
- Each subproject's `harmonized_schema.csv` + `external_validation_targets*.csv` + `validation_results.csv`
- `CITATION.cff` (post-D.2 — has the unified Zenodo concept DOI)

**Prompt (paste verbatim into fresh chat):**

```
I'm finalizing a Data Resource Profile manuscript for the International Journal
of Epidemiology (IJE) describing a Harmonized U.S. Vital Statistics (HVS)
microdata resource covering four products: natality 1968-2024, linked
birth-infant death 1983-2023 (permanent 1992-1994 NCHS-linkage gap), fetal
death 1982-2024, and matched-multiples 1995-2020 (three publication windows).
The resource is validated against every per-year aggregate NCHS publishes in
the National Vital Statistics Reports (NVSR) series, with byte-exact
reproduction documented in the per-product output/validation/ tables. I'm
attaching: the current preferred draft (modeled on the Human Mortality
Database IJE 2015 paper), the top-level + per-product READMEs, the
cross-product JOINT_USE_GUIDE and COMPARABILITY docs, the harmonized schemas,
the validation target + result CSVs, and the CITATION metadata.

Please help me with:
(a) Structural improvements vs the HMD IJE 2015 template — what does HMD do
    in its Data Resource Profile that my draft is currently missing or
    under-developing? Be specific (section by section).
(b) The "Strengths and Weaknesses" section — currently ~1,000 words; IJE
    Data Resource Profile word limit is 2,500 main text excluding abstract,
    references, tables, and supplementary. Propose a trim to ~600 words
    that preserves the load-bearing claims; flag what gets moved to
    supplementary.
(c) Word-count audit across the full draft — propose section-by-section
    targets summing to 2,500.
(d) Numeric audit — every claim in the draft must reconcile with the
    attached validation results. Flag any claim that's not directly
    supported by the attached evidence (these are L6 risks per the HVS
    operating protocol: "no invented numbers").
(e) The admin sections IJE requires: Ethics approval, Author contributions,
    AI-tool disclosure (mandatory at IJE), Conflict of interest, Funding.
    Draft minimal-acceptable language for each.
(f) Reference style — IJE uses Vancouver-style; verify citation formatting
    in the draft conforms.
(g) Cover letter to the editor — 1-page max; lead with the literature gap
    (cross-revision harmonization), the validation evidence (byte-exact
    NVSR reproduction), and the public availability (Zenodo DOI + GitHub).

Output: specific edit proposals with line numbers + a final 5-bullet list
of "ship-blocking" issues I should resolve before submission. Use IJE's
Vancouver style for any new citations you add. Do NOT invent numerics; if
a claim's evidence isn't in the attached files, flag it and stop.
```

### §19.2 — Paper 2 (Companion empirical) drafting prompt — Phase E use

**When to use.** After Paper 1 submits to IJE at Phase D.4. The HVS resource is publicly available (Zenodo + GitHub). Paper 2 is the substantive empirical companion paper that demonstrates what HVS uniquely enables.

**Default substance.** The "U.S. fetal mortality 1982-2024 by maternal race, age, and certificate revision" paper — the most HVS-uniquely-enabled (V3a/V3b backward extension is HVS's biggest novel data contribution; nobody else has 1982-2024 harmonized fetal death). Alternative substances (infant mortality 1983-2023; perinatal mortality across revisions; matched-multiples twin/triplet IMR) noted in KICKOFF "Phase E" section; user picks at Phase E entry.

**What to attach (fresh chat input files):**
- `paper/draft_v2_hmd_styled.md` (the descriptor; describes the resource the companion paper uses)
- `paper/published_manuscript.pdf` (the IJE-published Paper 1, if available; otherwise the submitted preprint)
- `fetal_death/COMPARABILITY.md` (era boundaries; certificate-revision details; state reporting quirks)
- `fetal_death/CODEBOOK.md` (per-variable definitions + per-era distributions in Appendix C8.20)
- `csv/published_tabulations/` (pre-computed cross-tabs, esp. `fetal_mortality_rate_by_year{,_x_maternal_race}.csv`)
- `docs/JOINT_USE_GUIDE.md` (canonical filter + joint-use rate computation)
- `docs/PRIOR_ART.md` (literature gap framing)

**Prompt (paste verbatim into fresh chat):**

```
I'm planning an empirical companion paper to my Harmonized U.S. Vital
Statistics (HVS) Microdata Resource, which is published at [INSERT Zenodo
DOI from CITATION.cff] and code on GitHub at [INSERT public-repo URL].
The descriptor paper is published in IJE as a Data Resource Profile
[INSERT citation once accepted].

The companion paper I want to draft analyzes U.S. fetal mortality rate
trends 1982-2024 by maternal race, maternal age, and certificate revision
(1978-revision 1982-1988 → 1989-revision 1989-2002 → 2003-revision
transition 2003-2004 → 2003-revision 2005+), using the HVS resource's
unique V3b (1982-1988, 1978-rev) + V3a (1989-1991, early-1989-rev)
backward extension. Prior single-revision analyses (e.g., MacDorman 2015,
NVSR vols cited in PRIOR_ART) were limited to within-revision windows
(1990-2024 natality, 2005+ fetal death). HVS uniquely enables a 43-year
harmonized analysis across all three certificate revisions. Bridged-race
coding ends 2018+ (a documented NCHS discontinuity); this caveat must
be surfaced in any race-stratified analysis.

I'm attaching: the descriptor paper, the fetal-death COMPARABILITY and
CODEBOOK (which describe the era boundaries + the bridged-race
discontinuity + state reporting quirks like Louisiana 1992-1994 plurality
non-reporting and Oklahoma all-years 100% unknown Hispanic), the
pre-computed published_tabulations CSVs (FMR by year + by maternal race),
the JOINT_USE_GUIDE (canonical filter + joint-use rate computation), and
the PRIOR_ART literature gap framing.

Please help me with:
(a) The most scientifically novel framing — what's the literature gap
    this paper closes that prior single-revision analyses couldn't?
    Articulate 3-4 candidate framings; pick the strongest with rationale.
(b) The right journal — American Journal of Epidemiology, Paediatric and
    Perinatal Epidemiology, JAMA Network Open, Epidemiology, or
    something else? Weigh trade-offs (audience reach, impact factor,
    review timeline, fee structure, suitability for methodological +
    substantive papers).
(c) Analytic approach — should I use joinpoint regression for trend
    changepoints? Age-period-cohort decomposition? Race-by-era
    interaction tests? How do I handle the NCHS suppression of
    sub-national geography? How do I handle the bridged-race 2018+
    discontinuity in a 43-year trend analysis?
(d) The headline finding I should lead with — is this a substantive
    race-disparity narrative, a methodological "harmonization-enables"
    story, or both? What 1-sentence finding would the abstract lead with?
(e) Draft section outline — Introduction, Methods, Results, Discussion;
    propose section-by-section content + a 5-cell substantive results
    table mockup with placeholder numbers (I'll fill in the real
    numbers from HVS).
(f) The ethics/Data-availability/AI-disclosure sections appropriate
    for the chosen journal.

Output: a structured planning document with: framing → journal choice
→ analytic plan → outline → results-table mockup → 3-step next-actions
for me to take. Do NOT invent substantive numbers; placeholder rows
are fine ("X.XX deaths per 1,000") but the structure must be concrete.
```

---

**End of NEXT_STEPS.**

The LLM's first action in every session: §1 session-start sequence. The human's first action: read STATUS.md to see what the LLM did last.
