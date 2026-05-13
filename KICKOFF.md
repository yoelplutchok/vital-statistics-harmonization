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

## Current planned sequence (as of 2026-05-12, post-V3b-complete + scope-expansion mandate)

Phase A (data-first pre-submission scope) is **COMPLETE**. The user (chat 2026-05-12, post-commit `b0c8b4a` `task7_v3b-complete`) has issued a **§11 plan-update directive** expanding pre-submission scope further: *"i would like do do everything possible with this project in terms of extending the actual project and adding diferent things to the project to make it as robust and useful as possible before we do the paper or the zenodo."* Manuscript submission, Zenodo deposits, and the public-repo v1.1 sync are all paused until Phases B + C complete.

### Phase A — data-first pre-submission scope (COMPLETE)

- ✅ Task 1 (joint-use stratified denominators, 2026-05-11)
- ✅ Task 2 (joint-use demo notebook, 2026-05-11)
- ✅ Task 3 V2.1 (fetal-death 2003-2004 + H8 + data_year + monorepo path-drift bundle, 2026-05-12 `task3-complete` @ `8ca5bf9`)
- ✅ Task 4 (paper companion notebook, 2026-05-11)
- ✅ Task 5 (manuscript trim, 2026-05-11)
- ✅ Task 6 (linked-validation framing reconcile, 2026-05-11)
- ✅ Natality v2.8.0 column rename (2026-05-12)
- ✅ Task 7 V3a (fetal-death 1989-1991 backward extension, 2026-05-12 `task7_v3a-complete`)
- ✅ Task 7 V3b (fetal-death 1982-1988 backward extension, 2026-05-12 `task7_v3b-complete` @ `b0c8b4a`)
- ✅ Public v1.0 GitHub repo push 2026-05-12 (commit `a18ca3a` at https://github.com/yoelplutchok/vital-statistics-harmonization; will be superseded by v1.x at Phase D)

Current data envelope: 41-yr fetal death (1982-2022, 2.35M records, 88/88 NVSR validation byte-exact) + 35-yr natality (1990-2024, 138.8M records, 183/183 byte-exact) + 19-yr linked birth-infant death (2005-2023, 74.9M records, 33/35 + 2 docs).

### Phase B — EXPLORATION SESSION (NEXT SESSION'S WORK; READ-ONLY)

**MANDATORY: the next LLM session is a READ-ONLY investigative / exploration session.** Per the 2026-05-12 user directive (logged in DECISION_LOG at commit time of this `[plan-update]`), Phase B EXPANDS pre-submission scope by investigating what additional work would make the project maximally robust and useful BEFORE Phase D (paper + Zenodo + public repo). The exploration session is mandated to:

1. **Brainstorm + research the full frontier of pre-submission additions** across the six dimensions below. Open-ended exploration; do not narrow prematurely. The user wants "everything possible" — the session's job is to enumerate everything plausible, score it, and propose an executable order.

2. **Six exploration dimensions** (each becomes a section in the exploration report):

   **B.a. Data extensions (additional years / additional NCHS files)**
   - **Natality 1968-1989 backward extension** — symmetric sibling of the V3b fetal-death work just shipped. NCHS public-use natality files exist 1968+; 1968-revision (1968-1971 50% sample + 1972-1977 100%) and 1978-revision (1978-1988 100%) covered. Probe URLs at `ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/natality/` and `Dataset_Documentation/DVS/natality/`. Verify per-year layout availability + user-guide existence via sibling-derived URL probing (per LESSONS L1-extension 2026-05-12T04:30:00Z).
   - **Linked birth-infant death pre-2005 backward extension** — NCHS cohort-linked files exist back to 1983; period-linked starts 1995 (with the well-known 1995-1998 gap that ended NCHS's prior series). Verify which years are public-use and which layouts apply. Probe `ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/linked/`.
   - **Latest-year refreshes**: 2023+ fetal death, 2025+ natality, 2024+ linked. Verify NCHS public-use release status via WebFetch on `https://www.cdc.gov/nchs/data_access/vitalstatsonline.htm`.
   - **Pre-1982 fetal death** — almost certainly RDC-only (NCHS public-use FD canonical series begins 1982); confirm by WebFetch + sibling-URL probing.
   - **Other NCHS public-use vital-events files** worth considering: marriage/divorce series, multiple-cause-of-death (all-age mortality — out of HVS scope unless user redirects), abortion surveillance summaries.
   - **IPUMS-International + IPUMS-USA**: are there pre-harmonized versions worth cross-referencing for validation?
   - For each candidate: NCHS URL probe result; raw-zip estimated size + record count; user-guide availability; era-layout count; estimated harmonization effort.

   **B.b. Robustness / testing / validation infrastructure**
   - `tests/test_schema_dtype_parity.py` (durable H8 defense; recommended in FIX_LOG 2026-05-11T18:50:00Z) — asserts every harmonized_schema.csv `type` matches the parquet's pyarrow dtype.
   - `tests/test_canonical_filter_invariants.py` — sum-across-strata = unstratified-total for every canonical filter, every product, every year.
   - `tests/test_row_count_conservation.py` — input = output + documented_drops at every parse/harmonize/derive boundary.
   - `tests/test_cross_product_join_parity.py` — natality joined to fetal-death + linked has the expected demographic-stratum row counts (per JOINT_USE_GUIDE).
   - **Mutation-test scaffolding** for every validator (L3 defense in §8): inject a known violation; assert the validator catches it.
   - **L13 file-inventory completeness audit** — for every CSV in `metadata/`, verify role/description names columns that actually exist with claimed dtypes.
   - **L14 exit-code-vs-per-row aggregation defense** — every validator's `main()` must exit non-zero on any per-row FAIL.
   - **CI integration** — GitHub Actions workflow running smoke + invariant tests on every push (currently no automated test runs).
   - **`scripts/run_pipeline.py` end-to-end smoke from monorepo root** — confirms no latent path-drift bugs (per FIX_LOG 2026-05-12T01:30Z forward-looking follow-up).
   - **PROVENANCE.md refresh + sha-stability test** — automated check that every shipped artifact's documented SHA matches its on-disk SHA.
   - **Snapshot regression test** — every release tags a per-column SHA manifest; subsequent release CI fails if any "stable" column drifts.

   **B.c. Usability / convenience layers / multi-language quickstarts**
   - **Additional pre-computed denominator tables**: state-stratified live births × year; race × age × Hispanic × state; period vs cohort linked-file denominators.
   - **R quickstart**: `quickstart.R` mirroring `quickstart.py`; verifies `arrow::read_parquet()` round-trip; documents R package dependencies.
   - **Stata + SAS quickstarts**: `quickstart.do` + `quickstart.sas`; document `import delimited` or `use` syntax for Stata; PROC IMPORT for SAS. Even a pointer file telling these users "load via pyarrow then export to CSV" would be a usability win.
   - **DuckDB views / pre-built SQL queries**: a `views.sql` file with the canonical filter + common joins as DuckDB-compatible views over the parquets.
   - **Pre-computed cross-tab CSVs** for users who don't want to load the parquet: per-year × per-state × per-race counts for the top 10 most-cited NVSR-equivalent tabulations.
   - **Worked-example notebooks beyond the current 2**:
     - `maternal_age_stratified_imr.ipynb` (using linked file)
     - `preterm_outcomes_time_series.ipynb` (fetal+natality+linked)
     - `cross_race_fetal_mortality.ipynb` (V3a/V3b race-stratified analysis demo, with V3b's code-7+9 null caveat documented)
     - `education_gradient.ipynb` (within-era only, with the 1989/2003 boundary explicit)
     - `state_reporting_quirks.ipynb` (Oklahoma Hispanic, Maryland/Massachusetts 1992-1998, Louisiana plurality)
   - **CLI tool**: `hvs` command-line tool wrapping `quickstart.py` use cases (e.g., `hvs count fetal_deaths --year 2020 --race AIAN`).
   - **Validated "perinatal record" pre-joined parquet**: one row per linked-file infant with fetal-death sibling records flagged (where infant + sibling fetal death share maternal identifiers — limited by suppressed identifiers, but partial joins are possible).

   **B.d. Cross-product / joint-use enhancements**
   - **Three-product perinatal mortality joint computation**: rate = (fetal deaths 28+wk + infant deaths <7d) / (live births + fetal deaths 28+wk) × 1000, computed by year × race using all three products. Currently only fetal mortality (single product) is demoed.
   - **Section B 2017 race-stratified NVSR validation** (the deferred Task 4 fragment).
   - **Task 8 — cross-product timeline figure** (from NEXT_STEPS.md §15; not yet shipped). Era-boundary visualization, all 3 products on one timeline with revision-boundary bands.
   - **Cross-product reproducibility figure** — fetal-mortality rate + IMR + preterm rate + LBW rate on one panel, with documented sources for each.

   **B.e. Documentation / discoverability**
   - **CHANGELOG.md** at the monorepo root with one section per version (v1.0 → v1.1 → … delta).
   - **Migration guides**:
     - v2.7.0 → v2.8.0 natality (column renames; sample sed/awk recipes for legacy code).
     - v2.0.0 → v2.3.0 fetal death (V2.1 transition years added, V3a/V3b backward extension; sample query updates).
   - **Worked-example FAQ** ("how do I compute the perinatal mortality rate?" "how do I get state-level data?" "what's the right canonical filter for my analysis?").
   - **Cross-product COMPARABILITY.md** at monorepo root — synthesizes the within_era/cross_era caveats from both subprojects' COMPARABILITY docs.
   - **PROJECT_STRUCTURE.md upgrade** — add notebook deps + build-order DAG + which-file-to-read-first-by-use-case.
   - **CODEBOOK extensions** — per-variable historical-value-distribution panels, sentinel-code disambiguation tables, era-by-era coding scheme diff.
   - **PRIOR_ART.md update** — does the literature gap argument still hold given recent harmonization efforts (e.g., NBER's IPUMS-Health Surveys, RWJF's 500 Cities)?
   - **NCHS-source-data SHA manifest at sub-project level** — confirms a downstream user replicating from scratch gets bit-identical inputs.

   **B.f. Performance / distribution / reproducibility tooling**
   - **Parquet column dictionary tuning** — set `use_dictionary=True` per low-cardinality column (e.g., race, sex, version_flag); measure size reduction.
   - **Smaller derived parquet** — drop redundant intermediates if any (e.g., string sibling of a numeric column).
   - **Reproducibility container** — `Dockerfile` pinning python+pandas+pyarrow versions; one `docker run` rebuilds every parquet end-to-end.
   - **`uv` / `poetry` lockfile** for deterministic Python environment.
   - **GitHub release artifacts** — attach the parquets to a GitHub Release alongside the Zenodo deposit.
   - **`scripts/run_pipeline.py` from-scratch smoke** — verify clean rebuild from raw zips in <30 min on a standard laptop.
   - **Mirror parquet on a CDN** (CloudFront / S3 / GitHub LFS) for users behind Zenodo-blocking firewalls.

3. **For each candidate, produce a structured writeup** with:
   - **Name** + 1-line description
   - **Why this matters** (use case, who benefits)
   - **Effort estimate** (sessions, with per-session breakdown)
   - **Source / data dependencies** (NCHS user-guide URLs verified via WebFetch + sibling probing; SHA recordable; OCR-needed flag)
   - **Risks / blockers** (RDC-only? requires direct NCHS contact? schema-version-bump-triggering? cross-era incompatible?)
   - **Manuscript impact** (changes a published number? adds a new validation cell? requires re-paragraph?)
   - **Priority recommendation**: must-have / nice-to-have / defer
   - **Execution dependency** (does X need to happen before Y?)

4. **Produce a §11 plan-update proposal** at the end of the session:
   - Diff for `NEXT_STEPS.md` §15 (new task entries with full PRE-FLIGHT/SMOKE/DO/VERIFY/RECEIPT framing per §4)
   - Diff for `KICKOFF.md` (replace this Phase B/C/D placeholder with a concrete ordered task list)
   - **Total effort estimate** (cumulative sessions; surface the trade-off explicitly so the user can decide whether to trim before authorizing)
   - **Suggested execution order** within Phase C (group tasks by data-product-touched; minimize parquet rebuilds; place high-risk early)

5. **HALT and write findings to**:
   - `EXPLORATION_REPORT.md` at monorepo root (NEW file, append-only thereafter)
   - New STATUS.md section appending the proposal pointer + "Open questions for human"
   - DECISION_LOG entry recording the plan-update proposal (status: PENDING USER REVIEW)
   - Do **NOT** execute any of the investigated items. Do **NOT** advance to Phase C without explicit user authorization.

**Investigation methods allowed in Phase B**:
- `WebFetch` on NCHS canonical URLs (`https://www.cdc.gov/nchs/data_access/vitalstatsonline.htm` + sibling-derived `ftp.cdc.gov` paths).
- `WebSearch` for academic / IPUMS / NBER / ICPSR / GitHub references.
- `WebFetch` on `https://web.archive.org/web/*/` for older NCHS pages.
- `Read` on existing repo files (any path).
- `Bash` for read-only repo inspection: `git log`, `git diff`, `grep`, `find`, `ls`, `wc`. **Forbidden**: any tool invocation that mutates state (no `git commit`, no `mv`, no `cp` of canonical files, no script execution that writes to canonical paths).

**Forbidden in Phase B**:
- Any canonical-state mutation (scripts, parquets, schema, metadata CSVs, RECEIPTS/, manuscript drafts).
- Any DO-phase work on any candidate.
- Skipping the halt-and-ask step at session end.
- Hallucinating data sources without sibling-derivation evidence (per LESSONS L1-extension).
- Asserting "PDF X needs OCR" without an explicit `page.get_text()` probe (per LESSONS L12-extension 2026-05-12T15:00Z).
- Inflating effort estimates to discourage user expansion, or deflating them to encourage it. Report honestly.

**Time budget**: 1 session (estimated 60-120 min of agent time). If the exploration is incomplete at session end, deliver a partial proposal + flag the unfinished dimensions; do NOT defer the halt.

### Phase C — EXECUTE PHASE B-AUTHORIZED ADDITIONS (Tier 1 + Tier 2, ~29-35 sessions)

Per Phase B `EXPLORATION_REPORT.md` §G.4 (drafted 2026-05-12T20:30Z) and user authorization 2026-05-12 (Q35 = Tier 1 + Tier 2; logged in `DECISION_LOG.md` 2026-05-12T21:00:00Z; Q32-Q42 self-resolutions in same entry). Each task below uses the full `NEXT_STEPS.md` §4 five-phase discipline (PRE-FLIGHT, SMOKE, DO, VERIFY, RECEIPT) per the `§15` entries C8.1-C8.15 appended at the same `[plan-update]` commit.

#### Tier 1 — pre-Phase-D must-haves (~13-15 sessions)

- **C8.1** — SMOKE retag + dtype parity (B.1 + B.2)               [1.5 sessions]
- **C8.2** — Latest-year refresh: fetal 2023+2024 (fetal-only)    [1 session]
- **C8.3** — Cross-product Tier-1: timeline + perinatal joint + 2022 race [2 sessions]
- **C8.4** — Invariant tests: filter + row-count + join           [3 sessions]
- **C8.5a** — Distribution: pyproject.toml + uv.lock              [0.5-1 session]
- **C8.5b** — Distribution: Dockerfile (DEFERRED; needs docker)   [1-2 sessions]
- **C8.6** — CI: GitHub Actions wiring                            [1 session]
- **C8.7a** — Path-drift static audit across per-step scripts    [1 session]
- **C8.7b** — Orchestrator + Tier-1/2 re-derive (DEFERRED)        [1.5-5 sessions]
- **C8.8** — CHANGELOG + PRIOR_ART update                         [1 session]

#### Tier 2 — high-value additions (~16-20 sessions)

- **C8.9** — Usability: R quickstart + DuckDB views (C.1 DROPPED)  [1-1.5 sessions]
- **C8.10** — Worked-example notebooks (3 of 5)                   [3-4 sessions]
- **C8.11** — Migration guides + cross-product COMPARABILITY      [3-4 sessions]
- **C8.12** — Mutation tests + L13/L14 audits + SHA stability     [3-4 sessions]
- **C8.13** — Performance + GitHub release artifacts              [1.5-2 sessions]
- **C8.14** — Worked-example FAQ + PROJECT_STRUCTURE upgrade      [1 session]
- **C8.15** — Notebooks 4-5 (education, state quirks)             [2 sessions]

**Tier 3 (5 candidates) and Tier 5 (3 candidates) deferred** per user authorization. Tier 3 reconsidered at Phase D close (Q41 default = defer all to post-v1); Tier 5 framed as a post-v1 v1.1/v2.0 release (Q40 default = single submission after Tier 2, Tier 5 ships as Zenodo concept-DOI patch with IJE *Update* note). Re-authorization needed before any Tier 3 / Tier 5 task starts.

#### Sequencing notes within Phase C

- **C8.1 first** (Q37): cheapest item, pure-metadata, fixes the known stale L17 smoke case (forward-looking HALT #10 in STATUS 20:30Z). Unblocks any subsequent task that touches fetal-death state.
- **C8.2 second** (Q37): latest-year refresh extends the data envelope before downstream test/CI scaffolding so subsequent CI runs gate on the full extended envelope (no rework when 2023-2024 land).
- **C8.5a + C8.6 paired**: CI (B.9) depends on a pinned env (F.3 lockfile = C8.5a); ship lockfile first. C8.5b Dockerfile deferred to after `docker` is available on build machine OR after C8.7b lands the monorepo-root pipeline orchestrator (whichever comes first). Note: C8.7a (path-drift audit, this session's narrowed C8.7 scope) does NOT land the orchestrator; that work is in C8.7b (DEFERRED).
- **C8.4 before C8.6**: CI gates on real invariant tests, not bare structural smokes.
- **C8.8 last in Tier 1**: PRIOR_ART updates + CHANGELOG land after Tier 1 work supplies the evidence to cite.
- **C8.9-C8.11 ordering within Tier 2**: usability (C8.9, C8.10) ships before docs (C8.11) so migration guides can reference live R/DuckDB examples.
- **C8.12 mutation tests last in Tier 2**: defends every prior validator; surfaces FIX_LOG cascades if any validator rubber-stamps.

#### Always-on Phase C discipline

- Each task: full five-phase (`NEXT_STEPS.md` §4). PRE-FLIGHT writes Field-value snapshot (Convention 3). RECEIPT writes Forward-looking HALTs (Convention 4). Every new SMOKE asserts SHAPE-not-VALUE (Convention 1) + carries `DESIGN:` first-docstring tag (Convention 2).
- Each shipped task tagged `<task_id>-pre-do` (before DO) + `<task_id>-complete` (after RECEIPT). Receipt at `RECEIPTS/<task_id>_<UTC_timestamp>.md`.
- Halt-and-ask on any §7 condition. Do not silently work around. Do not patch downstream artifacts to match buggy upstream.
- Effort-ceiling cap (Q33 self-resolution): if cumulative Phase C effort drifts beyond +20% of the 29-35 session estimate (i.e., >42 sessions), halt at the next clean checkpoint and re-ask the user.
- Phase B-2 trigger (Q42 self-resolution): any new candidate >1 session triggers a `[plan-update]` per §11; silent in-Phase-C scope-creep forbidden.

### Phase D — PRE-PAPER POLISH + ZENODO + SUBMIT (after Phase C completes)

Phase D was the original Tasks 9/10/sync/manuscript sequence. Sequence preserved; timing pushed to after Phases B + C ship.

- **D.1. Task 9** — redirect notices on the two old GitHub repos (`yoelplutchok/natality-harmonization`, `yoelplutchok/fetal-death-harmonization`). Notice text proposed in STATUS 2026-05-12T18:45Z Q30. ~15-30 min, human-driven.
- **D.2. Task 10** — Unified Zenodo deposit + version patches: (i) new unified HVS concept DOI; (ii) v2.3.0 (or whatever Phase B/C bumps it to) patch to fetal-death concept DOI 10.5281/zenodo.20031571; (iii) v2.8.0 (or later) patch to natality concept DOI 10.5281/zenodo.19363074; (iv) description-only redirect notes on both old deposits pointing to (i). Includes PROVENANCE.md refresh + schema-CSV `years_available` retroactive V3a/V2.1 gap fix. 1 session + Zenodo upload time.
- **D.3. KICKOFF step 5** — Sync monorepo to public staging dir + push v1.x to GitHub. Re-rsync `~/Desktop/vital-statistics-harmonization-public/`, re-scrub (same exclude list + LLM-mention scrub edits as 2026-05-12 v1.0 push). Excludes: `STATUS.md`, `DECISION_LOG.md`, `FIX_LOG.md`, `LESSONS.md`, `NEXT_STEPS.md`, `KICKOFF.md`, `PRE_FLIGHT_LOG.md`, `RECEIPTS/`, `.claude/`, `paper/`, `notebooks/_build_*.py`, `EXPLORATION_REPORT.md`. Commit + push to overwrite v1.0.
- **D.4. KICKOFF step 6 — Manuscript re-pass + submit** (~½ session). Update all numerics affected by Phase B/C work (record counts, coverage windows, validation counts). Inject unified HVS concept DOI + public GitHub URL. Resolve the three `<!-- YP: review -->` admin-section markers (Author contributions, AI-tool disclosure, Funding) — these stay in the published manuscript per journal AI-disclosure requirements but were excluded from the public repo at v1.0 push. Reformat references to IJE style. Submit.

**Always-on guardrails for Phase C / D execution**:

- §7 halt conditions are binding. Every task PRE-FLIGHT runs the Field-value snapshot (Convention 3) + every RECEIPT writes Forward-looking HALTs (Convention 4) + every new SMOKE harness asserts SHAPE-not-VALUE (Convention 1) + carries a `DESIGN:` docstring tag (Convention 2).
- L9 cheap-checks on every cited external document; L13 column-content verification on every inventory CSV; L17 SMOKE stale-pinning awareness.
- Halt-and-ask on any §7 condition. Do not silently work around. Do not patch downstream artifacts to match buggy upstream.
- §2 four-core-principle: cheap-before-expensive, fail-closed, state-on-disk-never-only-in-memory, re-running-must-be-free.

**When Phase B / C / D may legitimately deviate**:

- If Phase B reveals that a candidate has a RDC-only blocker (or any other immovable obstacle): defer it to post-submission, document the deferral with the specific blocker.
- If Phase C reveals a cumulative effort exceeding what the user is willing to absorb: halt at the next clean checkpoint and re-ask.
- If a Phase B/C/D task surfaces a new mistake class (per §11): log to LESSONS.md, propose §8 matrix row, halt for human approval before continuing.

**Source for this sequence:** 2026-05-12 chat sessions — DECISION_LOG entries 2026-05-11T20:50Z, 2026-05-12T01:35Z, 2026-05-12T03:30Z, 2026-05-12T18:30:00Z (B3 1-digit recode + DATAYEAR Option A for V3b), and the 2026-05-12 post-V3b-complete chat directive *"i would like do do everything possible with this project … before we do the paper or the zenodo"* (logged in this `[plan-update]` commit's accompanying DECISION_LOG entry). STATUS.md's 2026-05-12T18:45:00Z section is the canonical current-state file; this kickoff is the canonical sequencing pointer.

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
