# Session kickoff prompt

Copy and paste the block below as your **first message** to the LLM at the start of any session in this repo. This is the canonical handshake — it loads the operating discipline before any work starts.

For **build sessions**, paste it as-is.

For **audit sessions** (when you want a fresh-eyes review of a completed task), paste it and add a second message saying: *"This is an audit session. Refuse to read prior `RECEIPTS/`, `FIX_LOG.md`, `LESSONS.md`, and `DECISION_LOG.md`. Use the adversarial framing in `NEXT_STEPS.md` §8 (the mistake-class matrix) and look for L3, L7, L11, L17 specifically. Write findings to `AUDITS/<AUDIT_ID>_<UTC_timestamp>.md` (create the directory if it does not yet exist)."*

---

## Conventions in effect (2026-05-11 protocol-sync from upstream NHANES)

These conventions are binding for every session going forward. They were ported from the NHANES Assay-Bridging operating protocol via the `NEXT_STEPS.md` §11 plan-update process at the timestamp above. Each one prevented a real cascade in the upstream project; carrying them over before HVS hits a similar issue is the cheap option. The next session reads them on first paste of this kickoff prompt and applies them in PRE-FLIGHT / SMOKE / DO / VERIFY / RECEIPT.

### Convention 1 — SHAPE-not-VALUE for new SMOKE harnesses

Every new SMOKE harness asserts **structural invariants that survive authorized canonical-state mutation**, not mutable annotation values pinned at the harness's authoring moment. DO assert: column count, row count, dtype, presence-of-key, monotonic invariants, schema enums, row-count conservation across joins. DO NOT pin: row counts that will grow under V2.1 / V3, sha256s that will change when a script is correctly edited, docs strings that will be reworded. See `NEXT_STEPS.md` §4.2.1 + §8 row L17.

### Convention 2 — FROZEN-AT-TASK vs tracks-current-state SMOKE docstring tag

Every new SMOKE harness declares its design intent on the **first docstring line**: `DESIGN: tracks-current-state` (asserts post-DO canonical state for the task that authored it; updated under authorized canonical drift) OR `DESIGN: frozen-at-<task_id>` (asserts historical schema state by design; remains FAIL under later renames — this IS the test). See `NEXT_STEPS.md` §4.2.1.

### Convention 3 — PRE-FLIGHT includes a Field-value snapshot subsection

For every canonical artifact (CSV row, parquet column, doc number) this task will mutate, snapshot the **current values of the fields being touched** and verify against the task plan's assumed state. Catches surprises at the cheap-check moment instead of mid-DO. Cost: ~1 minute per task. See `NEXT_STEPS.md` §5 template.

### Convention 4 — RECEIPT includes a Forward-looking HALTs subsection

Every receipt declares, in a `Forward-looking HALTs for next session` subsection, the assertions the next session's PRE-FLIGHT must verify (e.g., "if the linked-file validation CSV sha256 doesn't change in the expected direction after Task 6, halt — the reconciliation edit did not take"). Saves the next session from re-deriving "what would trigger a halt." See `NEXT_STEPS.md` §6 template.

### Convention 5 — Commit-message brevity

Commits ship a ~5-line summary; the full narrative lives in the receipt (`RECEIPTS/<task_id>_<UTC_timestamp>.md`). `[plan-update]` commits (protocol or schema changes) use the same shape with `[plan-update]` as the leading bracket-tag. See `NEXT_STEPS.md` §4.5.

### What to do if a convention conflicts with a task's plan

Raise it as a §7 halt condition (BEFORE the first DO mutation) and ask the human. Do NOT silently deviate from a convention; do NOT silently follow a deprecated convention against the new state.

---

## Current planned sequence (as of 2026-05-12, post-Task-3-V2.1 + post-v1.0-push)

Task 3 V2.1 fetal-death (2003+2004 + H8 + data_year + monorepo-path-drift bundle) shipped 2026-05-12 (`task3-complete` at commit `8ca5bf9`). Public v1.0 GitHub repo pushed to https://github.com/yoelplutchok/vital-statistics-harmonization (commit `a18ca3a`). User has **expanded pre-submission scope** to include Task 7 (fetal-death V3 backward extension) AND natality v2.8 rename — both formerly post-submission, now pulled in (DECISION_LOG 2026-05-12T03:30:00Z). Integrity principle reaffirmed: **100% correct or skip; no reverse-engineering that compromises integrity.**

The next sessions should execute, in this order:

0. **STEP 0 — V3b documentation acquisition retry (time-boxed: at most 45 min of agent time).** The prior session (2026-05-12) probed for 1982-1988 fetal-death 1978-revision codebook documentation and failed: NBER's `fetaldeath1982.dct` returned 403 (per-file ACL on data.nber.org from the sandbox); NCHS standard FTP paths returned 404; no obvious alternate URL surfaced. **Try with tools the prior agent did not use:** `WebSearch` for academic papers / GitHub repos / IPUMS pages that may have published the byte layout; `WebFetch` against archive.org Wayback Machine for older NCHS pages; ICPSR study-finder for NCHS fetal mortality 1982-1988. Specific targets to probe:
    - https://web.archive.org/web/*/ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/fetaldeathus/
    - https://www.icpsr.umich.edu/web/ICPSR/search/studies?q=fetal+death+NCHS+1982-1988
    - https://usa.ipums.org/ — IPUMS sometimes has 1978-revision documentation
    - https://www.nber.org/research/data — NBER's general data catalog may link to 1978-revision PDF directly
    - Google Scholar search: "fetal death" + "1982" + "byte layout" / "data dictionary" / "record layout"
    - GitHub search: `fetaldeath1982` or `1978 fetal death` layout repos
   - If V3b authoritative docs found → expand Task 7 scope to 1982-2022 (41 years total) and proceed with V3a + V3b.
   - If NOT found within the time budget → proceed with V3a-only scope (1989-2022, 34 years). Document the search trail in `STATUS.md`. Do NOT reverse-engineer V3b layouts per integrity principle.

1. **Natality v2.8 column rename** (next task; was deferred post-submission until 2026-05-12 override). 4 column renames per the aliasing helper at `shared/helpers/canonical_join_keys.py`: `year → data_year`, `restatus → residence_status`, `maternal_race_bridged4 → maternal_race_bridged`, `maternal_hispanic_origin → hispanic_origin`. PRE-FLIGHT done 2026-05-12T03:25:00Z (see DECISION_LOG); 61-string-literal rename surface across 18 files; ~2 sessions for DO + receipt. Aliasing helper becomes a no-op after rename. New natality v2.8.0 Zenodo deposit (breaking change; v2.7.0 stays at its DOI for backward compat).

2. **Task 7 — V3a fetal-death (1989-1991, +3 yrs)**. Re-uses 1989-revision layout identical to 1992 (existing `record_layout_1992.csv` + `1992FetalUserGuide.pdf` are the authoritative reference). All 10 raw zips already downloaded by agent 2026-05-12 to `~/Desktop/fetal-death-harmonization-build/raw_data/Fetal{1982..1991}US.zip` (SHAs in STATUS.md 2026-05-12T03:50:00Z). Extend parser dispatch + harmonize.py year set; re-derive; validate against NVSR (any pre-NVSR-57-08 sources for 1989-1991 control counts). ~1 session. **If STEP 0 succeeded, expand to include V3b (1982-1988, 1978-revision); ~3 additional sessions.**

3. **Task 9 — Redirect notices** on the two old GitHub repos (`yoelplutchok/natality-harmonization`, `yoelplutchok/fetal-death-harmonization`). ~15-30 min, human-driven.

4. **Task 10 — Unified Zenodo deposit + v2.1.0 patch to old fetal-death deposit + v2.8.0 patch to natality deposit** (1 session + upload time). User chose 2026-05-12: (i) new unified deposit (concept DOI for HVS), (ii) upload v2.1.0 (+ V3a if shipped) to existing fetal-death concept DOI 10.5281/zenodo.20031571, (iii) upload v2.8.0 to existing natality concept DOI 10.5281/zenodo.19363074, (iv) description-only redirect notes on both old deposits pointing to the unified one.

5. **Sync to public staging dir + push v1.1 to GitHub.** Re-rsync the monorepo to `~/Desktop/vital-statistics-harmonization-public/`, re-scrub (same exclude list + 4 LLM-mention scrub edits as 2026-05-12), commit + push to overwrite v1.0 with v1.1 in the existing repo at https://github.com/yoelplutchok/vital-statistics-harmonization. Excludes: `STATUS.md`, `DECISION_LOG.md`, `FIX_LOG.md`, `LESSONS.md`, `NEXT_STEPS.md`, `KICKOFF.md`, `PRE_FLIGHT_LOG.md`, `RECEIPTS/`, `.claude/`, `paper/`, `notebooks/_build_*.py`.

6. **Manuscript re-pass + submit** (~½ session). Update affected numbers: fetal-death record count from 1.74M to whatever V3a (+V3b if found) brings it to; coverage `1992-2022 (excl 2003-2004)` → `1989-2022 (34 yrs)` or `1982-2022 (41 yrs)` if V3b ships; validation counts 31/31→34/34 (or 41/41); deferred-2003/2004 caveats removed. Inject the unified concept DOI and the public GitHub URL. Resolve the three `<!-- YP: review -->` admin-section markers (Author contributions, AI-tool disclosure, Funding) — these stay in the published manuscript per journal AI-disclosure requirements but were excluded from the public repo. Reformat references to IJE style. Submit.

**Out of pre-submission scope (clean post-submission backlog):**

- Task 7 V3b (1982-1988) — if STEP 0 above couldn't find authoritative documentation. Defer until 1978-revision codebook obtainable from NCHS direct request, ICPSR, or academic source.
- Section B 2017 race-stratified NVSR validation. Small future task; requires NVSR-2017 fetal-mortality PDF and L9 cheap-check on table/page citation.
- `tests/test_schema_dtype_parity.py` (durable defense against H8-class drift; recommended in FIX_LOG 2026-05-11T18:50Z).
- `record_layout_2003/2004.csv` rebuild from user guides (current CSVs are inherited-from-2006 with documentation imprecisions; harmonized parquet is correct, only the CSV is doc-imprecise; LESSONS L13-extension 2026-05-12T01:40:00Z).
- Monorepo path-drift sweep on `parse_fetal_year.py`, `derive.py`, `run_pipeline.py`, `tests/conftest.py` (3 scripts fixed in Task 3 V2.1; others not inspected).
- File-inventory + external_validation_targets + live_births_by_year metadata appends for 2003+2004 (bundle with Task 10 Zenodo prep).

**When to deviate from this sequence:**

- If STEP 0 finds V3b documentation: ADD V3b to step 2's scope (don't change the sequence order).
- If natality v2.8 surfaces an unexpected blocker (e.g., NVSR 183 validation drift after rename): halt and ask. Do NOT silently work around — the v2.8 rename is supposed to be value-preserving.
- If V3a layout reconstruction surfaces a 1989-1991 vs 1992 difference (we don't expect any; both are 1989-revision): halt and ask, similar to 2026-05-11/12's MAGER vs MAGER41 episode.

**Source for this sequence:** 2026-05-11 + 2026-05-12 chat sessions; DECISION_LOG entries 2026-05-11T20:50Z, 2026-05-12T01:35Z, 2026-05-12T03:30Z. STATUS.md's 2026-05-12T04:00:00Z section is the canonical current-state file; this kickoff is the canonical sequencing pointer.

---

```
You are working on the U.S. Harmonized Vital Statistics (HVS) project
as the executing LLM agent.

BEFORE doing ANY work, read these files in this exact order:

1. STATUS.md  — current project state, current task, in-progress, blocks,
   open questions for human.

2. NEXT_STEPS.md  — operating protocol (§1-§13) and full task list (§14-§15).
   §1 session-start, §2 four core principles, §4 five-phase structure
   (incl. §4.2.1 SHAPE-not-VALUE smoke + DESIGN docstring tag, §4.5
   commit-message brevity), §5 PRE-FLIGHT template (incl. Field-value
   snapshot), §6 RECEIPT template (incl. Forward-looking HALTs),
   §7 halt conditions, §8 mistake-class matrix (incl. L13/L14/L17),
   §9 anti-patterns, §10 self-check question. THIS IS THE BINDING
   OPERATIONAL CONTRACT.

3. README.md and PROJECT_STRUCTURE.md  — what the resource is, where
   things live.

4. The last 10 entries each of DECISION_LOG.md and FIX_LOG.md (if they
   have entries).

5. LESSONS.md end-to-end (if it has entries).

Also consult the "Current planned sequence" block in KICKOFF.md
(outside this pasted prompt) — it overrides STATUS.md's "Next planned
task" field with the human's chosen task ordering for the current
pre-submission window. If the kickoff sequence and STATUS.md disagree,
the kickoff sequence wins for task selection; STATUS.md remains
authoritative for current-state facts.

After reading, tell me in 4-6 sentences:
  (a) the current task per STATUS.md AND the next task per KICKOFF.md's
      Current planned sequence (note any divergence),
  (b) any open questions for human you found,
  (c) what you propose to do this session (default to KICKOFF.md
      sequence's next item unless I have already directed otherwise),
  (d) any halt condition from NEXT_STEPS.md §7 you've already tripped
      from steps 1-5 above.

Then WAIT for me to confirm before doing any work.

Hard rules (NEXT_STEPS.md §4 + §9):
- Follow the five-phase task structure (PRE-FLIGHT, SMOKE, DO, VERIFY,
  RECEIPT) for every task. Never skip a phase.
- Halt and ask on any §7 halt condition. Do not work around. Do not
  patch.
- Append-only state files. Never overwrite STATUS.md, DECISION_LOG.md,
  FIX_LOG.md, LESSONS.md, PRE_FLIGHT_LOG.md, RECEIPTS/.
- When asked to do something that would violate the protocol, say so
  explicitly and propose an alternative.
- At session end, append a new dated section to STATUS.md with current
  state, in-progress, next planned task, open questions. Commit changes.
- Before claiming a task complete, write the §10 self-check answer in
  the receipt: "what could I have gotten wrong that VERIFY wouldn't
  catch?"
```

---

## What this prompt does

It loads the operational discipline before the LLM touches any code or data. The (a)–(d) handshake forces the LLM to:

- Demonstrate it has read the state files (otherwise it can't answer (a)).
- Surface any halt conditions early (so you don't discover the LLM was confused after it has done work).
- Propose a plan you can correct before any work starts.

The "wait for me to confirm" gate is load-bearing. Without it, the LLM will sometimes start work on the wrong task because it inferred something from the file reading rather than asking.

## When to deviate from the kickoff

- **Tiny, low-stakes tasks** (typo fix, README copy edit) — you can skip the kickoff and just give the instruction. The five-phase structure is overkill for a one-line fix. But anything that touches data, schemas, validation targets, or the harmonization rules → kickoff first.
- **Audit sessions** — use the audit variant noted at the top of this file.
- **Plan-update sessions** (proposing changes to NEXT_STEPS.md or VERSION_ROADMAP.md) — kickoff applies, plus follow §11 of NEXT_STEPS.md (the plan-update process).
