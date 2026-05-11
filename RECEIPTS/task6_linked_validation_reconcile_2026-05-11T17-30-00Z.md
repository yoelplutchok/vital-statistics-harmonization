# Receipt: task6_linked_validation_reconcile
## 2026-05-11T17:30:00Z

### What was done

Reconciled the V3 linked external-target validation framing across the HVS monorepo. Resolved the prior STATUS section's Open Question #3: which framing is canonical, "35/35 pass" or "33/35 byte-exact + 2 cells differ by 1 record"? Canonical decision adopted: **"33/35 byte-exact + 2 cells (2015 `unweighted_infant_deaths` and `postneonatal_deaths`) differ by exactly 1 record from NCHS upstream null-record-weight survivor records; all 35 pass within documented tolerance"** — matching the framing already used by both manuscript drafts and the monorepo top-level `README.md`. Six files updated to align (`natality/README.md`, `natality/docs/{ABOUT_THIS_RELEASE,COMPARABILITY,VALIDATION}.md`, `paper/README.md`, `NEXT_STEPS.md`); the manuscript drafts and monorepo top-level README were unchanged (already canonical). `DECISION_LOG.md` entry records the choice and reasons. `NEXT_STEPS.md` §17 checklist item 5 marked ✅. This is the first task to exercise Convention 3 (PRE-FLIGHT Field-value snapshot) and Convention 4 (RECEIPT Forward-looking HALTs) under the 2026-05-11 NHANES protocol-sync.

### Inputs consumed

- `natality/output/validation/external_validation_v3_linked_comparison.md` (read-only authoritative source; **not modified**). 35 PASS / 0 FAIL / 0 MISSING; 33 rows Diff=0, 2 rows Diff=1 (2015 `unweighted_infant_deaths`: 23326→23327; 2015 `postneonatal_deaths`: 7772→7773). Notes attribute the 1-record diffs to LATEREC late-filed-births edge cases.
- `paper/draft_v2_hmd_styled.md` line 94 (canonical reference; **not modified**).
- `paper/draft_v1_ipums_styled.md` line 93 (canonical reference; **not modified**).
- `README.md` (monorepo top-level) line 17 (canonical reference; **not modified**).
- `STATUS.md` 2026-05-11T16:32:34Z section: Open Question #3 statement of the discrepancy.
- `NEXT_STEPS.md` §15 Task 6 spec (DO scope, VERIFY criteria, RECEIPT requirement).

### Outputs produced

- `natality/README.md`: lines 19, 27, 146 updated.
- `natality/docs/ABOUT_THIS_RELEASE.md`: line 80 updated.
- `natality/docs/COMPARABILITY.md`: line 367 updated.
- `natality/docs/VALIDATION.md`: line 206 updated (line 219 mechanism-wording preserved as soft-flag, see DECISION_LOG).
- `paper/README.md`: line 18 updated to mark RESOLVED.
- `NEXT_STEPS.md`: line 440 (§14 Table 1) updated; line 791 (§17 checklist) marked ✅.
- `DECISION_LOG.md`: new entry at top recording the canonical-framing decision, alternatives, reasons, residual risks.
- `PRE_FLIGHT_LOG.md`: new PRE-FLIGHT entry for this task (appended before any DO edit; timestamp 2026-05-11T17:05:00Z precedes the first DO edit).
- `STATUS.md`: new session-end section at top (timestamp 2026-05-11T17:30:00Z) marking Task 6 complete.
- `RECEIPTS/task6_linked_validation_reconcile_2026-05-11T17-30-00Z.md` (this file).

### Five-phase trace

- **PRE-FLIGHT**: ✓ (`PRE_FLIGHT_LOG.md` entry timestamped 2026-05-11T17:05:00Z; precedes first DO edit; includes Convention 3 Field-value snapshot subsection enumerating all 9 target locations with current-text quoted and plan-assumption verified).
- **SMOKE**: ✓ Tier 0 — read the authoritative validation comparison file directly and counted PASS rows / Diff=0 rows / Diff=1 rows by hand: 35 / 33 / 2. This IS the cheap-check; no separate harness exercise is appropriate for a docs-only reconciliation task. (Per §4.2 the smoke ladder is HVS-data-scaled; for a documentation-only task whose verification is "count rows in an existing CSV / MD," Tier 0 cheap-check by direct read of the authoritative artifact is the operationally correct smoke.)
- **DO**: ✓ Seven file edits applied via `Edit` tool (six content files + one §17 checklist update in `NEXT_STEPS.md`). Pre-DO tag `task6-pre-do` set at `596e8ce` before any edit.
- **VERIFY**: ✓ Re-grep `git ls-files | xargs grep -n -E '35/35|33/35|35 of 35|33 of 35'` post-edit confirms canonical framing is consistent across the four scoped artifacts and the four additional in-scope-by-fix-on-contact docs (see Verify results below).
- **RECEIPT**: ✓ This file.

### Verify results

Criterion (from `NEXT_STEPS.md` §15 Task 6 VERIFY): **"The natality README, top-level monorepo README, manuscript draft, and validation CSV all agree."**

| Artifact | Post-edit framing | Agrees with canonical? |
|---|---|---|
| `natality/output/validation/external_validation_v3_linked_comparison.md` (authoritative) | 35 PASS / 33 rows Diff=0 / 2 rows Diff=1 | — (this is canonical) |
| `README.md` (monorepo top-level) line 17 | "33/35 byte-exact (2 cells differ by 1 record from NCHS upstream null-weight survivor records)" | ✓ PASS |
| `paper/draft_v2_hmd_styled.md` line 94 | "33 of 35 targets... two cells differ by exactly one record each because of NCHS upstream survivor records with null record weights" | ✓ PASS |
| `paper/draft_v1_ipums_styled.md` line 93 | same as draft_v2 | ✓ PASS |
| `natality/README.md` line 19 | "33/35 V3 linked targets byte-exact + 2 cells differ by exactly 1 record from NCHS upstream null-record-weight survivor records, both in 2015, passing within documented tolerance" | ✓ PASS |
| `natality/README.md` line 27 | "33/35 byte-exact + 2 cells (2015 `unweighted_infant_deaths` and `postneonatal_deaths`) differ by exactly 1 record from NCHS upstream null-record-weight survivor records — all 35 pass within documented tolerance" | ✓ PASS |
| `natality/docs/ABOUT_THIS_RELEASE.md` line 80 | "33/35 byte-exact + 2/35 differ by 1 record... all 35 pass within documented tolerance" | ✓ PASS (in-scope by fix-on-contact / L11) |
| `natality/docs/COMPARABILITY.md` line 367 | "V3 linked 33/35 byte-exact + 2/35 differ-by-1 (within tolerance)" | ✓ PASS (in-scope by fix-on-contact / L11) |
| `natality/docs/VALIDATION.md` line 206 | "33/35 active targets byte-exact + 2/35 differ by exactly 1 record (both 2015...)" | ✓ PASS (in-scope by fix-on-contact / L11) |
| `paper/README.md` line 18 | RESOLVED, restates canonical | ✓ PASS |
| `NEXT_STEPS.md` §14 Table 1 line 440 | "33/35 byte-exact + 2 cells differ by 1 record (within tolerance; resolved Task 6 2026-05-11)" | ✓ PASS |

Residual "35/35" occurrences remaining post-edit (intentionally retained, all are historical / task-spec context — not shipping-doc framing):
- `NEXT_STEPS.md` line 631 (Task 6 spec describing the problem that was solved)
- `NEXT_STEPS.md` line 641 (Task 6 spec DO-scope question)
- `PRE_FLIGHT_LOG.md` lines 47-56 (this task's PRE-FLIGHT entry, recording pre-edit field-value snapshot)
- `STATUS.md` lines 53, 122 (historical Open Questions from prior session entries; append-only)

### Reproducibility

- Re-running this task on the same `task6-pre-do` HEAD with the same Edit operations on the same input strings produces bit-identical post-edit file content ✓ (Edit tool is deterministic; no random / time-of-day inputs).
- The validation MD itself is unchanged; canonical framing is a documentation convention layered on top of it.

### Cross-product re-probe (if applicable)

- N/A. Task 6 is a docs-only reconciliation; no canonical data was mutated. Fetal-death and natality parquets unchanged; validation results unchanged. Sibling-product check (L4 in §8): the fetal-death subproject does not use the V3-linked validation count framing, so no propagation needed there.

### Git

- Pre-DO tag: `task6-pre-do`, commit=`596e8ce` (set 2026-05-11T17:05:00Z before any DO edit).
- Post-RECEIPT tag: `task6-complete`, commit=`<set after commit lands; see STATUS.md session-end section for resolved SHA>`.

### STATUS.md updated

- New session-end section at top of `STATUS.md` dated 2026-05-11T17:30:00Z marks Task 6 complete and supersedes the prior section's Open Question #3.

### Self-check (§10)

**What could I have gotten wrong that VERIFY wouldn't catch?**

1. The mechanism-attribution wording across files is locally inconsistent and I intentionally preserved each file's local phrasing rather than reconciling. If a future reader compares `natality/README.md` line 146 ("two null-`record_weight` survivor rows in 2014/2015"), `natality/docs/VALIDATION.md` line 219 ("LATEREC edge cases"), and the manuscript drafts ("NCHS upstream survivor records with null record weights"), they may infer these describe different phenomena rather than the same underlying NCHS upstream LATEREC-class issue under different terminology. VERIFY (which checks headline-count agreement) does not catch this. Mitigation: explicitly soft-flagged in DECISION_LOG entry residual-risk (a). Downstream task can disambiguate if pursued.
2. `natality/README.md` line 146 retains "2014/2015" for the underlying survivor rows although both validation diffs manifest in 2015 cells. If the original "2014/2015" wording was an inadvertent misrecording (i.e., the underlying NCHS records are also from 2015 only), then line 146 retains a small factual inaccuracy that VERIFY does not test. Mitigation: DECISION_LOG residual-risk (b) records the choice not to speculate.
3. The chosen canonical framing depends on the count "33/35 byte-exact + 2 differ by 1" being current. If `compare_external_targets_v3_linked.py` is re-run after a future natality parquet rebuild and the split changes (e.g., 34/35 + 1 differ, or 33/35 + 2 differ but on different rows), every file updated in this task must be paired-updated. Mitigation: Forward-looking HALT 1 below.
4. I did not re-run `compare_external_targets_v3_linked.py` to independently regenerate the validation MD; I relied on the existing MD as authoritative. If the existing MD is itself stale relative to the current shipped parquet, the canonical framing rests on a stale ground truth. Mitigation: shipped artifacts have SHA-256 in PROVENANCE; the existing MD's pass/fail counts have been the working canonical state of the project. A future audit could re-run the validation as an independent verification.
5. I did not update `natality/output/validation/external_validation_v3_linked_comparison.md` itself, since it IS the ground truth. If a future reader treats this MD as also requiring "canonical framing" alignment, they might unhelpfully edit the ground truth to match shipping-doc framing rather than the other way around — which would erode the audit chain. Mitigation: the MD is structured as a Pass/Fail/Missing summary + per-row breakdown, not a headline assertion; the canonical framing is a downstream synthesis.

### Forward-looking HALTs for next session

Per Convention 4 (§6 receipt template) and the §11 plan-update protocol-sync that introduced it. These are PRE-FLIGHT assertions the next session must verify; halt and ask the human if any fails.

- **Forward-looking HALT 1** — If the next session re-runs `natality/scripts/05_validate/compare_external_targets_v3_linked.py` and the resulting `external_validation_v3_linked_comparison.csv` or `.md` shows a different split than 33 Diff=0 / 2 Diff=1 (e.g., the parquet was re-derived under different harmonization, or NCHS revised an upstream user guide), then the canonical framing established in this task is stale and all six post-edit shipping docs (`natality/README.md` lines 19/27/146, `natality/docs/{ABOUT_THIS_RELEASE,COMPARABILITY,VALIDATION}.md`, `paper/README.md`, `NEXT_STEPS.md` §14 Table 1) plus the manuscript drafts and the monorepo top-level `README.md` need paired updates. Halt and re-derive.
- **Forward-looking HALT 2** — Carries forward from the prior session's STATUS Forward-looking HALT 3 (still applicable for tasks AFTER Task 6 that mutate canonical artifacts): the first task to mutate a canonical parquet, `harmonized_schema.csv`, or `external_validation_targets*.csv` must use the new PRE-FLIGHT template's Field-value snapshot subsection (Convention 3) and the new RECEIPT template's Forward-looking HALTs subsection (Convention 4). Task 6 has now demonstrated the templates on a docs-only task; the next task (Task 1 or Task 2) is the first to demonstrate them on a canonical-data mutation. If that PRE-FLIGHT or RECEIPT is missing either subsection, that is an L10-class back-fill risk and a regression on the protocol-sync convention adoption.
- **Forward-looking HALT 3** — If the next session is **Task 1 (joint-use convenience layer)**, the natality parquet's PROVENANCE.md sha256 must match the file's current sha256 at PRE-FLIGHT time. If the parquet has been re-derived since v2.7.0 was published, the validation count may have shifted from 33/35 byte-exact + 2 differ-by-1 to a different split, which would invalidate HALT 1's canonical claim. Halt and re-validate before stratifying.
- **Forward-looking HALT 4** — Mechanism-attribution phrases vary across `natality/README.md` line 146 vs `natality/docs/VALIDATION.md` line 219 vs the manuscript drafts (see DECISION_LOG residual-risk (a)). If a future task disambiguates them, it should propose a §11 plan-update that touches all three locations together so the wording converges atomically rather than drifting piecemeal.

### Notes for next session

- Task 6 is complete. Open questions remaining for human (carried from prior STATUS): #1 (push monorepo to GitHub now or wait until Task 1 ships?) and #2 (Task 1 next or another?). #3 (this task) is now resolved.
- Task 6 was the first exercise of Conventions 3 and 4. The Field-value snapshot subsection (Convention 3) caught no surprises here because the task was already well-specified, but the discipline did force enumeration of every target line BEFORE any edit, which improved the receipt's traceability. The Forward-looking HALTs subsection (Convention 4) here above proved load-bearing for HALT 2 (carrying forward an unfinished concern from the prior session) and HALT 3 (specific to whichever task runs next).
- No new mistake-class lesson surfaced; LESSONS.md not appended.
- The §17 readiness checklist now has 4 ⏳ remaining items relevant to manuscript submission (was 5; Task 6 → ✅).
