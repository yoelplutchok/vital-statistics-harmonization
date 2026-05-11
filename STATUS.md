# STATUS — last updated 2026-05-09T00:00:00Z

> **Append-only.** To update: add a new dated section at the top. Do not edit earlier sections. Each session reads the most recent section as the authoritative current state and writes its own session-end section above it.

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
