# Receipt: plan-merge-owed-backlog
## 2026-05-23T20:00:00Z

### What was done

Cleared the owed §11 human-merge backlog in a single `[plan-update]` commit (the 2026-05-11 protocol-sync precedent — one §11 process commit may carry multiple owed amendments; NOT §9-#8 task-compression, which forbids merging distinct *five-phase tasks*). User-authorized 2026-05-23 (KICKOFF handshake → AskUserQuestion "Pre-D cleanup first"). Seven owed items, every one a *merge of already-recorded-verbatim* text from append-only LESSONS/FIX_LOG/DECISION_LOG (not a new proposal): (1)+(2) two new §8 matrix rows `L13-ext (year-axis)` + `H6-ext (heterogeneous-union)` from LESSONS 2026-05-20T02:00:00Z; (3) §8 `L13-ext (shared CSV)` from FIX_LOG 2026-05-23T02:00:00Z; (4) §8 `L17-ext (grep-scope)` from FIX_LOG 2026-05-23T02:00:00Z; (5) NEXT_STEPS §15.D C8.18 model-clarification `[plan-update]` block recording the executed DO-step decomposition (resolves soft-flag (ii)); (6) §15.D C8.21 premise-correction block ("Stata 17+ import parquet" false → StataNow-only / SAS-Viya LIBNAME); (7) §15.D C8.22 scope-clarification block (per-state structurally infeasible → race/age substitution). Plus the owed LESSONS 2026-05-22 (A′)-falsification addendum entry. Plan/lessons-doc only; **zero canonical-state mutation**; fully `git revert`-able.

### Inputs consumed
- `NEXT_STEPS.md` §8 (L13/L14/L17), §15.D C8.18/C8.21/C8.22 — pre-edit state @ `plan-merge-owed-backlog-pre-do`@`453c2b3`
- `LESSONS.md` 2026-05-20T02:00:00Z entry (verbatim "Proposed matrix-row sharpening (§11 — human-merge)")
- `FIX_LOG.md` 2026-05-23T02:00:00Z ×2 (L17 grep-scope @ line 52; L13-extension shared-CSV @ line 68)
- `DECISION_LOG.md` 2026-05-22T02:00:00Z (the (A′)-FALSIFIED finding + the explicit "a §11 LESSONS addendum is owed" sentence) + 2026-05-17→2026-05-23 C8.18 sub-step entries (executed-decomposition substrate) + 2026-05-23T16:00:00Z (C8.21) + 2026-05-23T18:00:00Z D1 (C8.22)

### Outputs produced
- `NEXT_STEPS.md` — 4 new §8 rows (after L17, before the closing para; L13/L14/L17 byte-untouched) + 3 prepended §15.D `[plan-update]` blocks (C8.18 model-clar, C8.21 premise, C8.22 scope; all original Goal/DO-step text preserved per §3 append-only-supersede). +10 insertions / 0 deletions.
- `LESSONS.md` — 1 new dated entry at top (2026-05-22T02:00:00Z (A′)-falsification addendum; the 2026-05-20 entry preserved, referenced as partially-superseded). +18 insertions / 0 deletions.
- `PRE_FLIGHT_LOG.md` — PRE-FLIGHT entry 2026-05-23T20:00:00Z (committed @ `453c2b3` before any DO)
- This receipt + `STATUS.md` + `DECISION_LOG.md` appends

### Five-phase trace
- PRE-FLIGHT: ✓ `PRE_FLIGHT_LOG.md` 2026-05-23T20:00:00Z — PROCEED; committed + tagged `plan-merge-owed-backlog-pre-do`@`453c2b3` before DO (no L10 back-fill)
- SMOKE: ✓ Tier-0 analog (SHAPE-not-VALUE for a plan/lessons-doc task): (a) `git ls-files | xargs grep` confirmed **no test/script asserts on §8-matrix or LESSONS prose** (all 10 filename hits are static citation strings; the F4 + §15 citations unaffected by appended rows) ⇒ zero test-surface regression; (b) reference §8 row (L17) = 5 content pipe-cells, new rows authored to match
- DO: ✓ commits `453c2b3` (PRE-FLIGHT) .. `<this commit>` (the `[plan-update]`)
- VERIFY: ✓ criteria below
- RECEIPT: ✓ this file

### Verify results
- V1 scope: PASS — `git diff --name-only plan-merge-owed-backlog-pre-do` = exactly `NEXT_STEPS.md` + `LESSONS.md` (+ state files this commit)
- V2 zero canonical mutation: PASS — no `.parquet`/`harmonized_schema.csv`/`external_validation*`/`file_inventory.csv`/`.py`/`tests/` path in the diff (numeric grep = NONE)
- V3 §8 well-formed: PASS — all 4 new rows exactly 5 content pipe-cells; `L13`/`L14`/`L17` byte-intact; all 4 new ids present; closing "If a new mistake class…" para intact. (1 pre-existing 6-cell row @ line 320 = the L12 `git ls-files | xargs grep -n` literal-pipe row, NOT in this commit's diff hunks — pre-existing documented state, GitHub-rendered project-wide; out of plan-merge scope per §7-#17 → soft-flag, not fixed, not silently accepted)
- V4 §15.D append-only-supersede: PASS — C8.18 has BOTH the 2026-05-17 block AND the new 2026-05-23 model-clar block; C8.21/C8.22 new blocks present; all 3 original `**Goal.**` lines + the C8.18 `DO step 7` list preserved (grep counts == expected)
- V5 LESSONS append-only-supersede: PASS — new 2026-05-22 entry present; 2026-05-20 entry preserved (1 each)
- V6 reproducibility: PASS — 0 deletions, +28 insertions; pure additive; `git revert <commit>` fully restores prior plan/lessons state

### Reproducibility
- No build step (plan/lessons-doc only); the 3 settled-envelope gate parquet SHAs (`185c071e…`/`acb5c48a…`/`f630d8cf…`) are byte-exact by construction (not touched). pytest surface unchanged (SMOKE proved no test reads these). `git revert` is the one-command rollback; `plan-merge-owed-backlog-pre-do`@`453c2b3` is the tag anchor.

### Cross-product re-probe
- N/A — no canonical artifact, no downstream consumer of §8/§15.D/LESSONS prose (SMOKE-verified).

### Git
- Pre-DO tag: `plan-merge-owed-backlog-pre-do`, commit=`453c2b3`
- Post-RECEIPT tag: `plan-merge-owed-backlog-complete`, commit=`<this commit>` (`[plan-update]`-prefixed per §4.5)

### STATUS.md updated
- New section dated 2026-05-23T20:00:00Z prepended; title "last updated" bumped to 2026-05-23T20:00:00Z

### Self-check — what could I have gotten wrong that VERIFY wouldn't catch?
1. **Lossy condensation of binding-contract text.** The §8 matrix is single-line-per-row; the LESSONS/FIX_LOG proposals are multi-paragraph. I condensed them into 5-cell rows. Risk: a nuance dropped. Mitigation: the *full* proposed prose remains verbatim in the source LESSONS/FIX_LOG entries (the §8 row is the operational summary; the LESSONS entry is the canonical detail — exactly how the existing L13/L14/L17 rows relate to their LESSONS sources). Residual risk logged in DECISION_LOG; not VERIFY-catchable (judgment, not a structural check).
2. **C8.18 model-clarification fidelity.** The executed decomposition (3→3a/3b; 5→5a/5b/5c→5c-i/5c-ii(-a/-b)/5c-iii; 6→6a/6a-RECWT/6b) is transcribed from the DECISION_LOG headers; a sub-step could be mislabeled. Mitigation: every sub-step cites its exact DECISION_LOG timestamp for a reader to verify; no scope/deliverable claim made (structure-only). Residual risk logged.
3. **"Optional" framing of C8.21/C8.22 §15.D fixes.** I applied them (user authorized "clear the owed §11 plan-merges"; STATUS listed them as owed). If the user intended only the *mandatory* ones, the optional two are still pure append-only-supersede ⇒ trivially revertable; no harm, fully disclosed here.
4. **Date convention.** Used 2026-05-23T20:00:00Z (monotonic-after the 18:00:00Z C8.22 section) though the harness `currentDate`=2026-05-19. The append-only newest-first invariant *requires* monotonic-after; wall-clock accuracy is not the protocol invariant. Flagged in PRE-FLIGHT + here + STATUS. If the user wants real-wall-clock dating, that is a global state-file convention question (every prior 2026-05-2x section has the same property) — surfaced, not silently decided.
5. **Pre-existing L12 6-cell row.** Could indicate the §8 table mis-renders somewhere. Checked: it is the documented `git ls-files | xargs grep -n` row, has been in the matrix since the protocol-sync, renders on GitHub (code-span pipe); fixing it is out of this task's declared scope. Soft-flagged for a future docs-hygiene pass — NOT silently accepted, NOT scope-crept.

### Forward-looking HALTs for next session (Convention 4)
1. `plan-merge-owed-backlog-pre-do`@`453c2b3` + `plan-merge-owed-backlog-complete` set ⇒ this task CLOSED. The **owed §11 human-merge backlog is now empty** — STATUS "Owed §11 human-merge" should henceforth read "(none)". If a future session still cites owed §11 merges from before 2026-05-23T20:00:00Z, it is reading a stale STATUS section — re-check the newest one.
2. The 3 settled-envelope gate parquet SHAs are unchanged (`185c071ec76a`/`acb5c48a9abf`/`f630d8cf20db`); plan/lessons-doc task, zero build-side change.
3. **Carried (NOT this task):** the internal Phase-D-deferred prep — fetal-death CODEBOOK/COMPARABILITY v2.4.0 full-body re-paragraph; `file_inventory.csv` `imported`-flag refresh; `external_validation_v3_linked_comparison.{md,csv}` v4 refresh; convenience/benchmark v4 refresh — are SEPARATE five-phase tasks (TaskList #2-#5), still owed before Phase D. Manuscript Coverage re-paragraph remains D.4 (untouched here, by design).
4. **Soft-flag (new, non-blocking):** §8 matrix line ~320 (L12 row) carries a literal `|` inside a code span (`git ls-files | xargs grep -n`) → a strict CSV-split flags 6 cells; GitHub renders it. Pre-existing project-wide; candidate for a future docs-hygiene pass (escape `\|` or `&#124;`). Not on any VERIFY gate; do not fix mid-other-task (§7-#17).
5. Date observation: the repo's append-only state-file clock (2026-05-2x) runs ahead of the harness `currentDate` (2026-05-19). Future sessions: keep timestamps monotonic-after the newest STATUS section regardless of wall-clock.

### Notes for next session
- §11 backlog cleared. Next TaskList item = #2 (fetal-death CODEBOOK + COMPARABILITY v2.4.0 full-body re-paragraph), then #3/#4/#5, each its own five-phase task. After #2-#5, the internal Pre-D cleanup is complete and Phase D (externally irreversible, human-authorization-gated) is the only remaining work.
- §2/§3/§9-#8 honored: cheap PRE-FLIGHT Field-value snapshot before any edit; append-only-supersede (zero deletions; originals preserved); the §11 backlog is one process commit, the internal-prep items are explicitly NOT compressed into it.
