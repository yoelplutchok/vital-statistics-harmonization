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

**Goal.** A notebook that reproduces every numeric claim in the manuscript directly from the parquets, with each cell mapped to the paper paragraph it supports.

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

- `fetal_death/README.md` Version Roadmap lists "V4: Natality companion product" as future. Natality is already shipped. Reword to "Joint-use convenience layer + cross-product validation notebook" per `VERSION_ROADMAP.md` at the monorepo root.

---

# §17. Definition of "ready to submit"

The manuscript is ready to submit when:

1. ✅ Three products published to Zenodo with persistent DOIs.
2. ✅ Pipelines deterministic and re-runnable end-to-end.
3. ✅ Joint-use convenience layer shipped (Task 1, 2026-05-11).
4. ⏳ Joint-use demo notebook shipped (Task 2).
5. ✅ Linked-file validation framing reconciled (Task 6, 2026-05-11).
6. ⏳ Manuscript at IJE word limit with admin sections filled (Task 5).
7. ⏳ Paper-companion notebook reproducing every numeric claim (Task 4).
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

**End of NEXT_STEPS.**

The LLM's first action in every session: §1 session-start sequence. The human's first action: read STATUS.md to see what the LLM did last.
