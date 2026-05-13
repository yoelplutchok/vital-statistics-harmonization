# DECISION_LOG

> **Append-only.** Every non-trivial choice the LLM (or human) makes during HVS work is logged here as a dated row. Each entry includes the alternatives considered and the reason for the choice.
>
> A "non-trivial choice" is anything that:
> - Affects the harmonized schema, the analytic filters, or the validation targets
> - Resolves an ambiguity in the source documentation
> - Trades off two reasonable approaches with different downstream costs
> - Documents a residual risk surfaced by the §10 self-check in NEXT_STEPS.md
> - Defers a deferral or scope change
>
> Entry format:
>
> ```markdown
> ## YYYY-MM-DDTHH:MM:SSZ — <task_id> — <one-line title>
> **Choice:** <what was chosen>
> **Alternatives:** <what else was considered>
> **Reason:** <why; cite source documents with page/section if relevant>
> **Source:** <PMID, PDF SHA-256, or repo path>
> **Verifiable by:** <how a future reviewer can check the choice was right>
> **Reversible:** yes / no — <if yes, how>
> ```

---

## 2026-05-13T05:45:00Z — [plan-update] C8.6 — Ship workflow file in monorepo + defer live-CI green-check VERIFY to Phase D step 3 first sync; revise §15 C8.6 DO scope (single-version Python 3.13, not 3.11+3.12 matrix) + VERIFY criterion (YAML structurally valid + locally-emulated test command runs green + forward-looking live-CI VERIFY at Phase D)

**Choice (user-authorized at C8.6 PRE-FLIGHT halt-and-ask 2026-05-13T05:30:00Z, AskUserQuestion response "do what you think is the best move" interpreted as Option A "Ship workflow now, live-VERIFY at Phase D" per the agent's stated recommendation in the question preamble):** Apply a single `[plan-update]` commit resolving two §7-class HALTs surfaced at C8.6 PRE-FLIGHT:

1. **HALT #1 resolution (§7.17 + §7.12-shape, dev/public separation) — ship workflow in monorepo + defer live-CI VERIFY to Phase D step 3.** This monorepo has no `git remote` configured (verified PRE-FLIGHT: `git remote -v` returns empty). The public repo `yoelplutchok/vital-statistics-harmonization` is at v1.0 commit `a18ca3a` (2026-05-12T03:20:06Z; verified via `gh api repos/.../commits/main`) with no `.github/workflows/` directory (verified via `gh api repos/.../contents/.github/workflows` → HTTP 404) and lacks all Tier-1 outputs (no `pyproject.toml`, `uv.lock`, `.python-version`, `tests/`, the four C8.1-followup `__init__.py` files, the C8.1 dtype-parity test). Per KICKOFF Phase D step 3 (line 235), the canonical mechanism for moving Tier-1 outputs to the public repo is a complete staging-dir sync from `~/Desktop/vital-statistics-harmonization-public/` (verified to exist, currently at the v1.0 state, no `.github/`) + scrub + push. A live-CI VERIFY from this session would require either (i) configuring an `origin` remote here + pushing — but this monorepo's HEAD includes all state files (STATUS.md, DECISION_LOG.md, FIX_LOG.md, LESSONS.md, NEXT_STEPS.md, KICKOFF.md, PRE_FLIGHT_LOG.md, RECEIPTS/, EXPLORATION_REPORT.md, paper/) that the Phase D exclude list deliberately scrubs, so a direct push would leak them; (ii) a surgical sync to the staging dir + push from there — which is partial-Phase-D-step-3 ahead of schedule and forward-syncs questions that aren't ready (Task 9 redirect notices, manuscript admin-section markers, etc.). Option A ships the workflow file in this monorepo as canonical state; the file moves to the public repo at Phase D step 3 along with all other Tier-1 outputs; the live-CI green-check VERIFY closes on that first sync.

2. **HALT #2 resolution (§7.12, Python pin) — single-version 3.13.** §15 C8.6 DO scope (pre-revision line 1011) specified "matrix on Python 3.11 + 3.12 if both supported per uv.lock." This text predates C8.5a (which pinned `requires-python = ">=3.13,<3.14"` + `.python-version = 3.13`). Neither 3.11 nor 3.12 is supported under the canonical env; a matrix would either resolve to zero supported versions or be silently misleading. STATUS 2026-05-13T05:00:00Z line 118 already flagged this as a candidate consideration for C8.6 PRE-FLIGHT. Revised DO scope: single-job, `runs-on: ubuntu-latest`, Python auto-resolved from `.python-version` via `astral-sh/setup-uv@v6` (no explicit matrix needed).

**Plan-update applied (this commit):**

1. **`NEXT_STEPS.md` §15.C C8.6 entry rewritten** (lines 1001–1019 pre-revision):
   - Header note added documenting the 2026-05-13T05:30:00Z PRE-FLIGHT revision + §7 HALTs resolved.
   - Goal expanded to enumerate the specific test files (`test_schema_dtype_parity.py`, `test_canonical_filter_invariants.py`, `test_row_count_conservation.py`, `test_cross_product_join_parity.py`, `test_release_smoke.py`) being gated.
   - Why-this-matters narrative extended to note authoring-ahead-of-Phase-D rationale.
   - PRE-FLIGHT inputs extended to enumerate exact C8.5a SHAs being depended on.
   - SMOKE plan rewritten: Tier 0 `yaml.safe_load` + structural-key assertions (actionlint not installed locally; fallback documented).
   - DO scope rewritten: 5-step workflow specified (checkout, setup-uv, uv lock --check, uv sync --frozen, pytest); concurrency control noted.
   - VERIFY criteria rewritten as 5 numbered items: (1) YAML structurally valid; (2) locally-emulated steps reproduce 56 PASS + 1 XFAIL baseline; (3) parquet SHAs unchanged; (4) C8.5a file SHAs unchanged; (5) **forward-looking live-CI VERIFY closes at Phase D step 3 first sync**.
   - Dependencies extended to clarify C8.5b is NOT a dependency (per C8.5 plan-update narrowing); live-CI VERIFY depends on Phase D step 3.

2. **`KICKOFF.md`** — no edits needed; Phase C Tier-1 sequencing (line 184) names C8.6 as the next task with no implicit "remote push happens at C8.6" claim that conflicts with this plan-update.

3. **`PRE_FLIGHT_LOG.md`** — PRE-FLIGHT entry at 2026-05-13T05:30:00Z (RESULT: HALT) + addendum at 2026-05-13T05:45:00Z (RESULT: PROCEED post-resolution) document the two HALTs + this plan-update.

4. **This DECISION_LOG entry** records the §11 plan-update + Option A rationale.

**Alternatives considered (per AskUserQuestion 2026-05-13T05:30:00Z):**

For HALT #1:

1. **(A) Ship workflow now, live-VERIFY at Phase D (chosen).** Pro: smallest scope; matches existing dev/public architecture cleanly; workflow IS canonical state that belongs in the public repo; one-session cost; locally-emulated VERIFY gives high-confidence signal (uv sync --frozen + pytest works under the same Python pin + same lockfile that CI will use); aligns with KICKOFF's Phase D step 3 as the canonical sync mechanism. Con: "live CI green check" doesn't close until Phase D step 3; parquet-skip-in-CI deferred to C8.13 (acceptable separate matter).

2. **(B) Surgical sync to staging dir + live push now.** Pro: live CI green check closes this session; forward-syncs Tier-1 to public; reduces Phase D step 3 burden. Con: ~45-60 min overhead; jumps Phase D step 3 ahead of schedule, partially; brings forward questions that aren't ready (Task 9 redirect notice content, manuscript admin-section markers, EXPLORATION_REPORT exclude question, paper/ exclude question, etc.); Phase D step 3 was deliberately designed as a single sweep — partial sweeps create more state to track; **violates Anti-Pattern #8** ("Never compress two tasks into one because they go together"). Rejected.

3. **(C) Re-order Tier-1: C8.7 + C8.8 first, C8.6 last.** Pro: C8.6 ships alongside Phase D step 3 (cleanest live-CI VERIFY). Con: defers C8.6 indefinitely (Phase D start is conditional on Tier-1 + Tier-2 completion — many sessions out); doesn't address the structural issue, just defers it; KICKOFF.md sequencing note revision is plan-update overhead; loses the "early CI scaffolding" benefit (`EXPLORATION_REPORT.md` §B.9 cites this as the value of C8.6 specifically). Rejected.

For HALT #2:

1. **(A) Single-version Python 3.13 (chosen).** Pro: matches `.python-version` + `requires-python` literally; cleanest workflow; no dead-matrix-cell complexity. Con: forward-compat extension (e.g., 3.14 migration) requires a workflow edit — acceptable since 3.14 migration is itself a §11 plan-update event per C8.5a forward-looking HALT #5.

2. **(B) Keep matrix wording but with values 3.13 only.** Pro: forward-compat-shape preserved. Con: zero current benefit; complicates the workflow file. Rejected.

3. **(C) Keep 3.11+3.12 matrix as-written and let CI fail.** Pro: follows §15 literally. Con: would produce a CI workflow that cannot run (uv won't install Python 3.11 or 3.12 because of `requires-python = ">=3.13,<3.14"`); breaks any "Live CI green check" VERIFY. **Rejected (would violate §2 principle 2 "fail closed" — knowingly authoring a broken workflow).**

**Reason:** §11 plan-update process is the canonical path for in-Phase-C scope adjustments surfaced during PRE-FLIGHT verification of plan-vs-reality alignment (per Q42 self-resolution + Convention 3 Field-value snapshot). Both HALTs were caught at the cheap-check moment before any DO mutation — exactly what PRE-FLIGHT cheap-checks are for. The Option A choice + Python pin resolution preserve every original C8.6 design intent (workflow file, dependency on lockfile, pytest invocation, gating on push events) while aligning the immediate-session scope with what's locally verifiable + deferring the live-CI surface to its natural home at Phase D step 3.

Three protocol justifications: (i) §2 principle 1 "cheap-before-expensive" — discovering the dev/public-separation + Python-pin misalignments at PRE-FLIGHT saves ~30-60 min of rework that would have surfaced mid-DO if I'd attempted a direct push or authored a 3.11+3.12 matrix workflow. (ii) §11 plan-update process is the canonical path for in-Phase-C scope adjustments per Q42 (>1-session candidates trigger plan-update; the deferred live-CI VERIFY is ~5 minutes of Phase D step 3 work but the architectural shift in VERIFY criterion is plan-update-shape; sibling of C8.5's plan-update precedent). (iii) §10 self-check encourages the LLM to surface "what could I have gotten wrong that VERIFY wouldn't catch" — in this case, two ground-truth-unverified §15 PRE-FLIGHT-input assumptions (remote configured; 3.11+3.12 supported) that L9 cheap-checks at PRE-FLIGHT caught.

**Source:**

- `PRE_FLIGHT_LOG.md` 2026-05-13T05:30:00Z entry documenting the two HALTs (HALT #1 §7.17 + §7.12-shape, HALT #2 §7.12).
- `NEXT_STEPS.md` §15.C C8.6 entry pre-revision text (lines 1001–1019 at commit `e9cd08e`; full text preserved in git history).
- `git remote -v` → empty (verified PRE-FLIGHT).
- `gh api repos/yoelplutchok/vital-statistics-harmonization/commits/main --jq '.sha'` → `a18ca3acdc5b3c6012511aab99de2f9da7508840` (v1.0 commit, 2026-05-12T03:20:06Z).
- `gh api repos/yoelplutchok/vital-statistics-harmonization/contents/.github/workflows` → HTTP 404 (no workflows dir in public repo).
- `ls -la ~/Desktop/vital-statistics-harmonization-public/.github` → "No such file or directory" (staging dir also has no workflows; consistent with v1.0 state).
- C8.5a outputs: `pyproject.toml` sha=`c8826a61…`; `uv.lock` sha=`ab627034…`; `.python-version` sha=`02e735b3…`; content `requires-python = ">=3.13,<3.14"` (verified).
- STATUS 2026-05-13T05:00:00Z line 118 ("C8.5a surfaced one candidate consideration for C8.6: Python version matrix (single-version 3.13.x per `requires-python`, OR matrix of {3.13} for forward compat — single suffices given the narrow Python pin).") confirms HALT #2 was foreseen.
- KICKOFF.md Phase D step 3 (line 235) "Re-rsync `~/Desktop/vital-statistics-harmonization-public/`, re-scrub (same exclude list + LLM-mention scrub edits as 2026-05-12 v1.0 push)" — the canonical sync mechanism.
- User authorization chat 2026-05-13T05:30:00Z: "do what you think is the best move" — interpreted as Option A per the agent's recommendation in the AskUserQuestion preamble.

**Verifiable by:**

- This `[plan-update]` commit's diff shows `NEXT_STEPS.md` §15.C C8.6 entry rewritten + `DECISION_LOG.md` this entry + `PRE_FLIGHT_LOG.md` PRE-FLIGHT entry + addendum.
- Tag `C8.6-pre-do` lands on this `[plan-update]` commit (PRE-FLIGHT now PROCEEDS to C8.6 DO post-resolution; mirrors C8.2 / C8.3 / C8.5 plan-update precedent).
- C8.6 DO ships in a sibling commit tagged `C8.6-complete` containing `.github/workflows/ci.yml` + RECEIPT + STATUS append.
- Phase D step 3 first sync: a future session's RECEIPT records the first remote workflow-run URL + green/red status. If green, the live-CI VERIFY closes; if red, the §15 C8.6 VERIFY criterion #5 triggers a halt.

**Reversible:** yes — `git revert <this commit>` restores the original §15 C8.6 entry. The deferred live-CI VERIFY claim is per-task; reverting affects only C8.6's scope, not C8.5a's outputs or the dev/public separation pattern itself.

**Residual risks:**

- (a) **The Phase D step 3 first sync may surface workflow-on-runner failure modes not caught by local emulation.** E.g., `astral-sh/setup-uv@v6` on `ubuntu-latest` may resolve to a different uv build than the local `0.11.10 (aarch64-apple-darwin)`. Mitigation: the workflow pins `version: "0.11.x"` which constrains the major-minor; first sync's Forward-looking HALT explicitly requires verification of green CI before claiming closure. If the first remote run is red, the Phase D session halts + surfaces.
- (b) **The parquet-skip-in-CI concern weakens the CI signal**. On a clean Ubuntu runner with no parquets, the conftest `_require()` skip-if-missing protocol will cleanly skip parquet-dependent tests; CI reports "N passed + M skipped" instead of the local "56 PASS + 1 XFAIL." Mitigation: routed to C8.13 (Performance + GitHub release artifacts) for resolution via parquet-fetch-step or GitHub release artifact attachment. Documented as a Forward-looking HALT.
- (c) **The §15 entry's "Python matrix" wording (now revised)** may resurface in a future plan-update if 3.14 / 3.15 migration is desired. Mitigation: C8.5a forward-looking HALT #5 ("Python pin: 3.13.x. `requires-python = ">=3.13,<3.14"`. A future 3.14 migration is a §11 plan-update event") names the migration trigger explicitly.
- (d) **Cross-platform lockfile resolution untested locally (macOS arm64 build).** First CI run on `ubuntu-latest` (x86_64) is the durable cross-platform test. If `uv sync --frozen` fails due to a missing wheel for a transitive dep on linux-x86_64, the lockfile may need a `--python-platform linux` re-lock. Mitigation: this is C8.5a's open soft-flag (b); surfaces at first CI run, which is Phase D step 3.

**Self-check (residual risks the VERIFY phase wouldn't catch):**

- The locally-emulated VERIFY runs `uv sync --frozen` + `pytest` under macOS arm64 (`aarch64-apple-darwin`); the workflow will run on linux-x86_64. Wheel-availability for all 38 packages on linux-x86_64 is not directly tested by local emulation. The first Phase D step 3 push is the durable test. Risk: if a linux-x86_64-specific wheel is missing, CI fails immediately — and we won't know until Phase D. Mitigation: defer to Phase D first-run + surface as Forward-looking HALT.
- The workflow's concurrency control (`group: ci-${{ github.ref }}`, `cancel-in-progress: true`) is appropriate for single-contributor + main-branch + PR-from-fork patterns; it may cancel useful in-flight runs on rapid pushes. Acceptable trade-off; not VERIFY-blocking.
- The single-job design assumes all tests pass under a single env. If a future test requires e.g. R interop, the workflow will need restructuring. Acceptable for current scope.
- The locally-emulated `uv sync --check` returns "Would make no changes" today; that's environment-consistent confirmation. If a different machine produces a different result on the same lockfile, that's a uv-internal-state bug — not a workflow bug.

**Backport scope (per §11.4):** None directly. C8.1 / C8.2 / C8.3 / C8.4 / C8.5a receipts unaffected. C8.6 ships forward under the revised scope; C8.7 / C8.8 / Phase D step 3 inherit the Forward-looking HALT lineage.

---

## 2026-05-13T04:30:00Z — [plan-update] C8.5 — Split task into C8.5a (lockfile, this session) + C8.5b (Dockerfile, DEFERRED); revise Python pin from 3.11-slim to 3.13-slim; revise VERIFY scope from pipeline-rebuild to env-resolution + test-suite

**Choice (user-authorized at C8.5 PRE-FLIGHT halt-and-ask 2026-05-13T04:15:00Z; all three options (a)):** Apply a single §11 [plan-update] commit resolving three §7-class HALT conditions surfaced at C8.5 PRE-FLIGHT:

1. **HALT #1 resolution — split C8.5 → C8.5a + C8.5b.** `docker` is not installed on the build machine (PRE-FLIGHT verified via `which docker` → exit 1; `docker --version` → command-not-found). C8.5 SMOKE Tier 1 (`docker build`) and Tier 2 (`docker run`) cannot run locally. Split the task: **C8.5a** = lockfile-only (fully locally verifiable; this session); **C8.5b** = Dockerfile (DEFERRED until docker available on build machine OR C8.6 CI ships and validates remotely via GitHub Actions' hosted-runner `docker build`). C8.6 dependency narrows: C8.6 depends on C8.5a's lockfile only (not on C8.5b).

2. **HALT #2 resolution — Python pin to 3.13.x.** §15 line 963 originally specified `python:3.11-slim` base, but every actual build event in this repo's history uses Python 3.13.9 (natality v2.7.0 + fetal-death V2.0 build notes both name Python 3.13.9 explicitly; current build interpreter is 3.13.9 via miniconda). §15's `3.11-slim` appears to be a EXPLORATION_REPORT §F.2 carryover wording without ground-truth check. Plan-update revises §15 C8.5b entry to `python:3.13-slim`; `pyproject.toml` `requires-python = ">=3.13,<3.14"`; `.python-version` = `3.13`.

3. **HALT #3 resolution — C8.5a VERIFY revised to env-resolution + test-suite passes.** §15 line 965 originally specified `python scripts/run_pipeline.py` at monorepo root as the VERIFY witness. No monorepo-root `scripts/run_pipeline.py` exists; the only pipeline orchestrator is `fetal_death/scripts/run_pipeline.py` (rebuilds fetal-death V2.0 era only — 29 of the 43 years now covered). A monorepo-root orchestrator is C8.7's explicit scope per KICKOFF Tier-1 sequencing. Plan-update revises C8.5a VERIFY to: (i) `uv lock` deterministic (running twice produces bit-identical output); (ii) `uv sync --check` reports env-OK; (iii) cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returns 56 PASS + 1 XFAIL (the C8.4 baseline); (iv) all four parquet SHAs unchanged. Pipeline-rebuild VERIFY moves to C8.7.

**Plan-update applied (this commit):**

1. **`NEXT_STEPS.md` §15.C C8.5 entry rewritten into two entries:**
   - C8.5a (lockfile) — Goal/Why/PRE-FLIGHT inputs/SMOKE/DO/VERIFY all revised per the three resolutions. Effort revised 1.5–3 sessions → 0.5–1 session.
   - C8.5b (Dockerfile, DEFERRED) — preserves all original §15 C8.5 Dockerfile language with revisions: `3.11-slim` → `3.13-slim`; explicit "DEFERRED at C8.5 PRE-FLIGHT 2026-05-13T04:00:00Z"; resumption trigger documented; dependency on C8.5a (lockfile) + C8.7 (orchestrator) for full-rebuild VERIFY.

2. **`KICKOFF.md` Tier 1 task list (line 181)**: single `C8.5` row split into two rows (C8.5a `0.5-1 session`, C8.5b `1-2 sessions [DEFERRED]`).

3. **`KICKOFF.md` sequencing note (line 202)**: `C8.5 + C8.6 paired` revised to `C8.5a + C8.6 paired` with Dockerfile deferral note.

4. **`PRE_FLIGHT_LOG.md`** PRE-FLIGHT addendum at 2026-05-13T04:30:00Z records the resolution + PROCEED-to-C8.5a-DO.

5. **This DECISION_LOG entry** records the §11 plan-update.

**Alternatives considered (per AskUserQuestion 2026-05-13T04:15:00Z):**

For HALT #1:
1. **(a) Split into C8.5a + C8.5b (chosen).** Pro: surgical; preserves Tier-1 progress; clean tag boundary; lockfile lands this session with full SMOKE+VERIFY; Dockerfile resumption trigger explicit. Con: 2 RECEIPTS + 2 tags instead of 1.
2. **(b) Author Dockerfile now, defer docker SMOKE to C8.6 CI.** Pro: ships Dockerfile artifact in same session. Con: Dockerfile lands un-locally-validated; C8.6 CI is the implicit acceptance gate but it doesn't exist yet either. Rejected for same-session-ship-without-local-SMOKE concern.
3. **(c) Halt C8.5 entirely until docker installed.** Pro: full local SMOKE. Con: introduces out-of-band human step (Docker Desktop install ~5-15 min); delays C8.5a indefinitely; the lockfile portion is independently shippable so blocking it on docker is over-conservative. Rejected.
4. **(d) Lockfile-only this session; no Dockerfile commitment.** Pro: simplest. Con: loses the C8.5b follow-up tracking; future agent may not surface the deferred Dockerfile as a clear future task without explicit §15 entry. Rejected in favor of (a)'s explicit C8.5b stub.

For HALT #2:
1. **(a) Pin to 3.13.x; §11 plan-update (chosen).** Pro: matches every actual build event in repo history; lockfile reproduces documented builds byte-exact. Con: requires §11 plan-update commit (which is happening anyway for HALT #1).
2. **(b) Pin to 3.11.x per §15 literal.** Pro: follows §15 as-written. Con: lockfile becomes a hypothetical-env pin; no actual 3.11 build event in repo's history; resolver may pick different versions on 3.11 vs 3.13 (pandas 2.3.2 + numpy 2.3.1 both still support 3.11 but the resolution flag may differ); breaks reproducibility of every existing build. Rejected.
3. **(c) Range pin `>=3.11,<3.14`.** Pro: broader downstream-consumer compat. Con: lockfile still resolves against one specific Python at lock time; the range constrains downstream consumers, not the resolver; gives the illusion of multi-version support without actually testing it. Rejected.

For HALT #3:
1. **(a) Env-resolution + test-suite VERIFY; pipeline-rebuild moves to C8.7 (chosen).** Pro: aligns C8.5a scope with what's locally verifiable; C8.7 explicitly takes the pipeline-rebuild VERIFY responsibility per its KICKOFF Tier-1 entry. Con: weakens C8.5a VERIFY; relies on C8.7 for end-to-end closure (acceptable since C8.7 is the next-after-C8.6 Tier-1 task).
2. **(b) Author stub `scripts/run_pipeline.py` at monorepo root.** Pro: closes §15 VERIFY per literal. Con: scope creep (~0.5-1 session that belongs in C8.7); duplicates C8.7's intent. Rejected.
3. **(c) Use `fetal_death/scripts/run_pipeline.py` as partial witness.** Pro: minimal scope. Con: covers fetal-death only (29 V2 years, not the 43-year v2.4.0 envelope); doesn't address natality or linked. Rejected as partial verification.
4. **(d) Defer C8.5 to after C8.7.** Pro: §15 VERIFY satisfied per literal. Con: re-orders Tier 1 sequencing (§15/KICKOFF say C8.5 before C8.6, C8.6 before C8.7); C8.6 depends on the lockfile, which is C8.5a's deliverable — deferring C8.5a means deferring C8.6 too. Rejected.

**Reason:** §11 plan-update process is the canonical path for in-Phase-C scope adjustments surfaced during PRE-FLIGHT (per Q42 self-resolution + Convention 3 Field-value snapshot). All three HALTs were caught at the cheap-check moment before any DO mutation — exactly what PRE-FLIGHT cheap-checks are for. The split + Python pin + VERIFY revision preserve every original C8.5 design intent (lockfile + Dockerfile + reproducibility-via-pinned-env) while aligning the immediate-session scope with what's locally verifiable.

Three protocol justifications: (i) §2 principle 1 "cheap-before-expensive" — discovering the docker/Python/VERIFY misalignments at PRE-FLIGHT saves ~1 session of rework after a DO-time docker invocation would have surfaced a halt mid-task; (ii) §11 plan-update process is the canonical path for in-Phase-C scope adjustments per Q42 (>1 session candidates require [plan-update]; the deferral of C8.5b is ~1-2 sessions of work; well past the §11 threshold); (iii) §10 self-check encourages the LLM to surface "what could I have gotten wrong that VERIFY wouldn't catch" — in this case, the §15 entry's `python:3.11-slim` text + the assumed monorepo-root pipeline orchestrator were both ground-truth-unverified at plan-write time. The L9 cheap-check at PRE-FLIGHT caught both.

**Source:**

- `PRE_FLIGHT_LOG.md` 2026-05-13T04:00:00Z entry documenting the three HALTs (Halt #1 §7.2, Halt #2 §7.12, Halt #3 §7.17).
- §15.C C8.5 entry pre-revision text (NEXT_STEPS.md lines 953–971 at commit `4b78dd0`; full text preserved in git history).
- `EXPLORATION_REPORT.md` §F.2 + §F.3 (the source for the original C8.5 scope; §F.2 doesn't actually specify a Python version, confirming the §15 `3.11-slim` text was an authoring-time interpolation).
- `which docker` → exit 1 (docker not installed); `which uv` → `/opt/miniconda3/bin/uv`; `uv --version` → `0.11.10`; `python3 --version` → `Python 3.13.9`.
- natality `requirements.txt` + fetal-death `requirements.txt` both reference Python 3.13.9 as the build-time interpreter explicitly.
- `find . -maxdepth 4 -name run_pipeline.py` → only `fetal_death/scripts/run_pipeline.py` exists at monorepo root.
- User authorization chat 2026-05-13T04:15:00Z: HALT #1 = "Split C8.5 → C8.5a (lockfile now) + C8.5b (Dockerfile later)"; HALT #2 = "Pin to 3.13.x; §11 plan-update revises §15 line 963"; HALT #3 = "Env-resolution + test-suite passes (§11 plan-update)".

**Verifiable by:**

- This `[plan-update]` commit's diff shows `NEXT_STEPS.md` §15.C C8.5 entry rewritten into C8.5a + C8.5b + `KICKOFF.md` Tier 1 list + sequencing note edits + this DECISION_LOG entry + PRE_FLIGHT_LOG.md addendum.
- Tag `C8.5-pre-do` lands on this `[plan-update]` commit (PRE-FLIGHT now PROCEEDS to C8.5a DO post-resolution; mirrors C8.2/C8.3 pattern).
- C8.5a DO ships in a sibling commit tagged `C8.5a-complete`.
- C8.5b resumption: a future session's PRE-FLIGHT addendum at the resumption-trigger moment + tag `C8.5b-pre-do` on whichever commit ships the Dockerfile.

**Reversible:** yes — `git revert <this commit>` restores the original §15 C8.5 entry. The split is per-entry; reverting reverses both C8.5a + C8.5b stubs simultaneously.

**Residual risks:**

- (a) **The `requires-python = ">=3.13,<3.14"` may be too narrow** if a downstream consumer wants 3.14 support before we authorize a re-pin. Mitigation: this matches the build env; broader-pin authorization is a future §11 plan-update if requested.
- (b) **The `uv.lock` will pin transitive dependencies that aren't in `requirements.txt`** (e.g., `numpy` is in requirements but `python-dateutil` (pandas transitive dep) is not). The lockfile will declare its own preferred versions. Mitigation: `uv lock` is deterministic given a fixed dependency tree; subsequent re-locks against the same `pyproject.toml` produce bit-identical output (verified at SMOKE Tier 0).
- (c) **The deferred C8.5b may slip beyond Phase D start** if the docker-availability trigger doesn't fire. Mitigation: the resumption trigger is OR-coupled ("docker available OR C8.6 CI ships"); C8.6 (next Tier-1 task after C8.5a) ships GitHub Actions which has docker natively. C8.5b will become unblockable as soon as C8.6 lands, even without local docker install.
- (d) **The original §15 VERIFY's pipeline-rebuild criterion is non-trivially weakened.** Specifically, the assertion "running the full pipeline from raw zips against this pinned env produces canonical parquet SHAs" loses its C8.5a anchor. Mitigation: C8.7's §15 entry explicitly takes this VERIFY (line 1006-ish: "VERIFY criteria: `uv sync && python scripts/run_pipeline.py` rebuilds parquets to canonical SHAs"). The end-to-end VERIFY chain still closes at C8.7-complete.

**Self-check (residual risks the VERIFY phase wouldn't catch):**

- This entry assumes `uv lock` against the currently-installed env produces a lockfile that resolves cleanly on a fresh `uv sync` (no transitive dep resolution failure). If `uv lock` discovers a conflict between `pandas==2.3.2` and another dep's `pandas` requirement on Python 3.13, the lockfile generation may fail or produce a different version pin than expected. Mitigation: SMOKE Tier 0 explicitly tests `uv lock` resolution; HALT-on-failure to surface this if it happens.
- The `requires-python = ">=3.13,<3.14"` pin assumes 3.13 stays the canonical Python for the lifetime of this lockfile. If a Phase D / v1.1 Python 3.14 migration is desired, a §11 plan-update bumps the pin.
- The deferred C8.5b is shipped as a §15 entry stub but not a fully-PRE-FLIGHTed task. When resumed, its PRE-FLIGHT must re-verify (i) `uv.lock` post-C8.5a sha = the one this session will produce; (ii) `docker` runtime available; (iii) `scripts/run_pipeline.py` post-C8.7 sha = the one C8.7 will produce. Failure of any of those triggers a fresh §11 plan-update at C8.5b PRE-FLIGHT moment.

**Backport scope (per §11.4):** None directly. C8.1 / C8.2 / C8.3 / C8.4 receipts unaffected. C8.5a ships forward under the revised scope; C8.5b ships forward as a deferred task with explicit resumption trigger.

---

## 2026-05-13T03:00:00Z — C8.4 — Linked-vs-natality per-year drift bounded by 0.01% (was previously undocumented for this product pair); B.5 harness softened from strict-subset to bounded-drift invariant

**Choice (user-authorized at C8.4 DO halt-and-ask 2026-05-13T02:30Z, option `(a) Soften to relative-drift invariant (≤0.01%) + DECISION_LOG entry (Recommended)`):** The B.5 cross-product join parity harness's `test_linked_per_year_count_le_natality` was authored with a strict-subset assumption ("every linked birth is a natality birth"). On first run against the v2.4.0 / v2.8.0 / v3 release state, 5 of 19 joint years (2005, 2006, 2008, 2011, 2012) violated strict subset: linked exceeds natality by 1–228 records (max 0.0055% relative drift, year 2005 with +228 records on a 4.14M base).

**Resolution:** Replace the strict-subset assertion with a bounded-drift invariant: `|linked - natality| / max(linked, natality) ≤ 0.01%` per joint year. The 0.01% tolerance is 2× the observed max (0.0055%) and matches the order of magnitude of the JOINT_USE_GUIDE.md-documented "<0.006% NCHS post-release re-tabulation" between microdata and NVSR-style products. Test renamed: `test_linked_per_year_count_within_drift_tolerance_of_natality`. Mutation test re-shaped: `test_mutation_linked_bounded_drift_violation_caught` injects a 0.5% drift (10× tolerance) on synthetic data and asserts the harness flags it.

**Alternatives considered (per AskUserQuestion 2026-05-13T02:30Z):**

1. **(a) Soften to relative-drift invariant + DECISION_LOG (chosen).** Pro: keeps a meaningful invariant (>0.01% drift still flagged as regression); avoids hard-coding the 5 currently-drifting years (the SHAPE invariant survives any future linked-pipeline retabulation); aligns with JOINT_USE_GUIDE.md's documented tolerance class. Con: a future widening of NCHS's re-tabulation drift past 0.01% triggers a re-pin task.
2. **(b) Strict subset + 5-year exception dict + DECISION_LOG.** Pro: more conservative — any new drifting year triggers FAIL. Con: heavy maintenance; hard-codes a tracks-current-state pin that violates Convention 1 (SHAPE-not-VALUE). Rejected as inconsistent with the file's `DESIGN: structural-invariant-no-pins` tag.
3. **(c) Remove the linked-subset assertion entirely + DECISION_LOG.** Pro: cleanest architectural framing — NCHS doesn't guarantee subset between linked and natality pipelines. Con: loses a useful invariant (a >0.01% widening still indicates a real regression). Rejected as throwing the baby out with the bathwater.
4. **(d) Halt + §11 plan-update.** Pro: methodologically cleanest. Con: ~30 min overhead for a problem solvable inside DO via a tolerance edit + log entry. Rejected as over-engineering.

**Reason:** The JOINT_USE_GUIDE-documented natality-vs-NVSR drift (5 years with diffs of 38–224 records, max 0.0055%) is the same shape as the linked-vs-natality drift surfaced by C8.4 (5 years with diffs of 1–228 records, max 0.0055%). The linked file is constructed by NCHS using NVSR-style cohort tabulations that include the same post-release adjustments. The phenomenon is documented in the source domain; B.5 had inadvertently encoded a stricter invariant than the data supports. The right level of automated defense is a tolerance that catches a *widening* of the documented drift, not a re-litigation of the documented drift itself.

Three protocol justifications: (i) §2 principle 2 "fail closed" — we halted at the FAIL rather than silently softening; AskUserQuestion is the formal "fail closed" surface. (ii) §4.2.1 Convention 1 SHAPE-not-VALUE — the bounded-drift invariant is a SHAPE check (true for any year-set, any record-count growth); the strict-subset claim was effectively a stale-pin against the year-set as it happened to exist when the test was first authored. (iii) §10 self-check — the residual risk "what could I have gotten wrong that VERIFY wouldn't catch" applies in reverse here: I HAD a strict invariant that caught something I hadn't known about. Surfacing it via AskUserQuestion + this log entry rather than silent edit is what the protocol prescribes.

**Source:**
- `tests/test_cross_product_join_parity.py` (NEW; sha=`4cb8b4e0f78d80f4…`) lines around `_LINKED_NATALITY_DRIFT_TOLERANCE = 1e-4`.
- `docs/JOINT_USE_GUIDE.md` "NCHS-series note" table (5 years with 38–224 record diffs; <0.006% relative).
- Observed empirical drift on v3 cohort-linked vs v2.8.0 natality (5 years, max 0.0055%):
    - 2005: linked=4,138,577 natality=4,138,349 diff=+228 (0.0055%)
    - 2006: linked=4,265,593 natality=4,265,555 diff=+38 (0.0009%)
    - 2008: linked=4,247,726 natality=4,247,694 diff=+32 (0.0008%)
    - 2011: linked=3,953,591 natality=3,953,590 diff=+1 (~0%)
    - 2012: linked=3,952,842 natality=3,952,841 diff=+1 (~0%)
- Linked parquet sha=`9b828a4de4e59b17…`; natality parquet sha=`e16ad5323d68e28d…`.
- User authorization chat 2026-05-13: option (a) selected via AskUserQuestion.

**Verifiable by:**
- `pytest tests/test_cross_product_join_parity.py::test_linked_per_year_count_within_drift_tolerance_of_natality` PASS on current parquet state.
- `pytest tests/test_cross_product_join_parity.py::test_mutation_linked_bounded_drift_violation_caught` PASS (mutation test).
- Combined cache-cleared `pytest fetal_death/tests/ natality/tests/ tests/` returns 56 passed + 1 xfailed.

**Reversible:** yes — `git revert` of the C8.4 commit removes the bounded-drift invariant; the strict-subset assertion is preserved in git history. If a future task wants to investigate the underlying NCHS-pipeline cause (e.g., audit the 2005 +228-record source), the log entry + parquet SHAs above are the starting point.

**Residual risks:**

- (a) **The 0.01% tolerance may be too loose.** If a future linked-pipeline regression introduces a 0.005% systematic drift across more years, the harness won't catch it. Mitigation: the test reports actual drift values in the FAIL message, so a per-year drift inspection during any future failure surfaces the widening; the DECISION_LOG entry documents what the current envelope is.
- (b) **The 5 currently-drifting years are not individually pinned.** A future NCHS re-release that re-tabulates one of these years to a different drift will silently pass as long as the new drift remains ≤ 0.01%. Mitigation: the parquet-SHA-pinned C8.4 receipt + this log entry are the canonical record of the v3 / v2.8.0 state.
- (c) **The drift is documented as "NCHS post-release re-tabulation" but not directly verified.** A truly diligent investigation would compare a single drifting year's birth records between the natality public-use file and the linked file to verify that the +228 records in 2005 are NCHS-added (or natality-dropped), not a pipeline bug on our side. Mitigation: Phase D / C8.11 cross-product COMPARABILITY consolidation should incorporate this finding.

**Self-check (residual risks the VERIFY phase wouldn't catch):**

- The bounded-drift tolerance is set at 0.01% (1e-4) — 2× the observed max. If the observed max grew to 0.008% (still well within JOINT_USE_GUIDE's "<0.006%" qualitative bound but above the empirical 0.0055%), the harness would FAIL. Whether that's the right behavior depends on whether 0.008% counts as "expected NCHS drift" or "regression." The conservative choice (FAIL) is what's wired now; tuning is reversible via this entry's 1e-4 constant.
- The 5-year observation list is a snapshot of the v2.8.0 + v3 state. If a future natality v2.9.0 closes some of the diffs (e.g., by re-deriving from a newer NCHS source), the snapshot in this entry becomes a frozen historical record — not a forward-looking invariant. The forward-looking invariant is the test code's 1e-4 tolerance, not the per-year diff list.

**Backport scope (per §11.4):** None directly. C8.1, C8.2, C8.3 receipts are unaffected. Phase D step 6 manuscript re-pass should consider whether to mention the linked-vs-natality bounded drift as a Comparability note (analogous to the existing natality-vs-NVSR microdata mention).

---

## 2026-05-12T23:50:00Z — [plan-update] C8.3 — Re-scope Section B race validation to 2022 single-race + Hispanic (vs NVSR 73-09 Table A); reframe perinatal joint as JOINT-USE DEMO with two sub-component validations (28+wk FD vs NVSR 73-09 Table 1; ENN <7d vs NVSR 73-05 Table 2)

**Choice (user-authorized at PRE-FLIGHT halt-and-ask 2026-05-12T22:30Z, option `(a) 2022 race + perinatal demo (Recommended)`):** Apply a §11 plan-update rewriting `NEXT_STEPS.md` §15.C C8.3 entry's PRE-FLIGHT inputs + DO scope + VERIFY criteria, and `KICKOFF.md` line 179, to reflect actual NVSR contents instead of the original §15 wording's source-location errors.

The two source-location errors in the original entry (DECISION_LOG 2026-05-12T21:00:00Z, written at phase-c-authorized time without L9 PDF cheap-check):

- (A) "NVSR 73-09 Table A for 2022 perinatal validation" — NVSR 73-09 is *Fetal Mortality: United States, 2022* by Gregory et al., not a perinatal-mortality report; Table A is by single-race + Hispanic fetal mortality for 2022. NCHS no longer publishes a combined perinatal-mortality rate per year (the MacDorman/Gregory "Fetal and Perinatal Mortality" combined series stopped after 2013 data per NCHS website; the two strands are now separate annual NVSR series). C8.3 PRE-FLIGHT L9 cheap-check (text-extracted NVSR 73-09 via PyMuPDF; verified every table heading 2026-05-12T22:00Z).
- (B) "NVSR fetal-mortality table for 2017 by maternal race" — no such NVSR exists. C8.3 PRE-FLIGHT (~30 min L9 cheap-check 2026-05-12T22:05–22:25Z): probed `cdc.gov/nchs/data/nvsr/nvsr{65..72}/nvsr{vol}_{nn}{,_,-,-508,_508}.pdf` covers via PyMuPDF; found NCHS annual Fetal Mortality NVSR series resumes at **NVSR 70-11 (2019 data)** after a 2014–2018 gap. The 2017 by-maternal-race fetal mortality tabulation is unpublished.

**Plan-update applied (this commit):**

1. **`NEXT_STEPS.md` §15.C C8.3 entry rewritten:**
   - Title: "timeline + perinatal joint + 2022 race validation" (was "+ Section B race validation").
   - PRE-FLIGHT inputs: cite **NVSR 73-09 Table 1** (28+wk fetal-death = 9,956 for 2022; on-disk PDF sha=`2590e417…`); **NVSR 73-09 Table A** (7 cells for 2022 single-race + Hispanic fetal-mortality rates; same on-disk PDF); **NVSR 73-05** (Ely & Driscoll 2024, *Infant Mortality 2022*, sha=`dccdc895…`, Table 2 = early-neonatal <7-day rate 2.81/1000 + 6 race-stratified breakouts; to be fetched at DO step 1 + recorded in PROVENANCE).
   - DO scope: explicit re-spec — (i) timeline figure; (ii) Section B refactor to 2022 single-race + Hispanic (using `race_hispanic_revised` in fetal-death + `maternal_race_ethnicity_5` in natality); existing 2017 bridged-race cells preserved as documented "machinery demo" closing the manuscript's joint-use bridge for the last-bridged-race-year (no NVSR-validation claim); (iii) Section C perinatal joint computation as JOINT-USE DEMO with sub-component validations (28+wk FD vs NVSR 73-09 Table 1; ENN <7d vs NVSR 73-05 Table 2).
   - VERIFY criteria: explicit per-cell tolerance + regression gate on Section A.

2. **`KICKOFF.md` line 179 edit:** "C8.3 — Cross-product Tier-1: timeline + perinatal joint" → "C8.3 — Cross-product Tier-1: timeline + perinatal joint + 2022 race".

3. **PRE-FLIGHT log addendum** at 2026-05-12T23:50:00Z marks **PROCEED** post-resolution; original HALT entry preserved per append-only convention.

4. **This DECISION_LOG entry** records the §11 plan-update.

**Alternatives considered (per the PRE-FLIGHT AskUserQuestion 2026-05-12T22:30Z):**

1. **(a) 2022 race + perinatal demo (chosen).** Pro: uses on-disk NVSR 73-09 + a single freshly-fetched NVSR 73-05 PDF; latest-year (post-C8.2 refreshed envelope) validation; cleanly aligns with manuscript's joint-use claim; no bridged-race availability issue since 2022 uses the post-2018 single-race standard NCHS publishes for. Preserves the 2017 machinery as documented bridge to the last-bridged-race-year. Con: drops the "2017 deferred Task 4 fragment closes here" framing in favour of a more defensible 2022 validation; manuscript line 99 may need a sibling claim in Phase D step 6.
2. **(b) Keep 2017 machinery + smaller perinatal claim.** Pro: smallest change vs original §15 plan. Con: Section B remains externally unvalidated; defers the deferred-Task-4-fragment ambition again.
3. **(c) Split: timeline + 2022 race only; perinatal becomes new C8.X.** Pro: smaller task (~1 session vs 2). Con: adds plan-update overhead + defers the most distinctive cross-product demo.
4. **(d) Halt + [plan-update] rewriting §15 entry (no DO this session).** Pro: methodologically cleanest. Con: another session of plan-update-only overhead before any DO work.

**Reason:** §11 plan-update process specifically accommodates scope corrections surfaced during PRE-FLIGHT verification of plan-vs-reality alignment (Convention 3 Field-value snapshot caught the NVSR-source mismatch at the right moment — exactly what cheap-checks are for). Option (a) maximizes manuscript-relevance per-NVSR-fetch effort and avoids re-litigating the 2017 deferred-Task-4 framing without dropping it — the 2017 machinery stays in the notebook with a clear "machinery demo" caveat, so the closeable threads stay closed.

Three protocol justifications: (i) §2 principle 1 "cheap-before-expensive" — discovering the NVSR-source mismatch at PRE-FLIGHT saves ~1 session of rework after a DO-time NVSR cell that doesn't exist surfaces a halt mid-task; (ii) §11 plan-update is the canonical path for in-Phase-C scope adjustments per Q42 (>1 session candidates require [plan-update]; this scope change replaces ~0.5 sessions of original 2017 work with ~0.5 sessions of 2022 work + adds NVSR 73-05 fetch + Section B refactor — net effort unchanged at 2 sessions); (iii) §10 self-check encourages the LLM to surface "what could I have gotten wrong that VERIFY wouldn't catch" — in this case, planning errors masquerading as data-availability questions.

**Source:**
- `PRE_FLIGHT_LOG.md` 2026-05-12T22:30:00Z entry documenting the HALT discovery (Halt #1 §7.12 conflicting documentation).
- `EXPLORATION_REPORT.md` §D.1 (perinatal computation candidate) + §D.2 (Section B 2017 race validation candidate; framing inherited the original §15 source assumption — the same fact-error existed at Phase B exploration time but wasn't surfaced as a PRE-FLIGHT-class L9 cheap-check would have).
- On-disk NVSR 73-09 PDF text-extraction (PyMuPDF) confirms Table A topic + Table 1 cell values.
- NVSR series probe 2026-05-12T22:00–22:25Z confirms NVSR 70-11 = Fetal Mortality 2019; gap 2014–2018.
- WebSearch + URL probing at `cdc.gov/nchs/data/nvsr/nvsr73/nvsr73-05.pdf` returned HTTP 200 + Table 2 verified containing 2022 early-neonatal rates by race/Hispanic (Total 2.81; AIAN 3.73; Asian 2.01; Black 5.05; NHOPI 3.36; White 2.23; Hispanic 2.65).
- User authorization chat 2026-05-12T22:30Z: option `(a) 2022 race + perinatal demo (Recommended)`.

**Verifiable by:**
- This `[plan-update]` commit's diff shows `NEXT_STEPS.md` §15.C C8.3 entry rewritten + `KICKOFF.md` line 179 edit + this DECISION_LOG entry + `PRE_FLIGHT_LOG.md` addendum + `STATUS.md` new section (next sub-session).
- Tag `C8.3-pre-do` lands on this `[plan-update]` commit.
- Future re-scope of the perinatal validation: triggers a new `[plan-update]` if NCHS resumes publishing a combined perinatal-mortality rate or if a new linked-file NVSR adds cells that close the redistribution-handling gap.

**Reversible:** yes — `git revert <this commit>` restores the original §15 C8.3 entry (which would re-introduce the source-location errors). The 2017 bridged-race Section B machinery in `notebooks/_build_joint_use_demo.py` is preserved in this plan-update; only its NVSR-validation framing changes. The Section A 2022-by-age cells (existing) are not touched at all.

**Residual risks:**

- (a) **NVSR 73-09 Table 1's "28+wk = 9,956" is post-proportional-redistribution** (footnote 2); our parquet stores observed gestational age without redistribution. The C8.3 VERIFY tolerance allows ~50 records of slop; the canonical fix is C8.4-scope (invariant tests for canonical-filter + redistribution-handling). Mitigation: document the tolerance in Section C narrative + RECEIPT Self-check.

- (b) **NVSR 73-05 Table 2's race-stratified early-neonatal rates** use the post-2018 single-race standard. Our linked-file parquet covers 2005–2023 and has both bridged and single-race columns; for 2022 the single-race columns are authoritative. The race-stratified ENN validation is OPTIONAL in C8.3 scope (headline = Total = 2.81 single cell); the per-race cells are deferred to C8.4 invariant-test territory if desired.

- (c) **Section B's 2017 bridged-race "machinery demo" framing in the notebook** may read as a defensive caveat. Mitigation: the notebook prose explicitly frames it as documentation-of-the-machinery-on-the-last-bridged-race-year, with the 2022 single-race Section B' as the headline NVSR-validated demonstration. The Phase D manuscript pass (step 6) reframes the joint-use paragraph to cite both.

- (d) **The L9 cheap-check that found no 2017 fetal-mortality NVSR is "absence of evidence"** — a future search may surface a non-NVSR NCHS publication (e.g., a Data Brief) that publishes 2017 fetal-mortality-by-maternal-race cells. Mitigation: if such a source surfaces, a Phase C / D `[plan-update]` adds a 2017-race validation cell to `external_validation_targets.csv` and the notebook; the current scope-shift does not preclude that.

**Self-check (residual risks the VERIFY phase wouldn't catch):**

- This entry assumes user authorization for the §11 plan-update via AskUserQuestion's option (a) selection. The selection was a single-question response; the LLM did NOT re-confirm via a second AskUserQuestion before applying. Risk: user may have intended a slight variant (e.g., "preserve the 2017 machinery only as a comment, don't keep the executed cells"). Mitigation: this entry's framing is reversible via a per-section edit if the user surfaces a disagreement post-fact.

- The NVSR 73-05 fetch + SHA-verify at DO step 1 is the first irreversibility boundary for canonical-state mutation in C8.3. If the on-disk SHA differs from PRE-FLIGHT's `dccdc895…`, the file has been re-released; HALT at DO step 1 per §7.11. Defense: PRE-FLIGHT explicitly records the SHA at fetch time + DO step 1 re-verifies.

- The "machinery demo" framing for the 2017 bridged-race cells may surface as "we shipped cells but didn't validate them" in a reviewer-skeptical reading. Mitigation: the joint_use_demo.ipynb pass/fail summary explicitly marks the 2017 cells as machinery-demo + cites this DECISION_LOG entry; the receipt's Self-check enumerates the risk.

**Backport scope (per §11.4):** None directly. C8.1 + C8.2 receipts unaffected. C8.3 ships forward under the revised scope.

---

## 2026-05-12T22:30:00Z — [plan-update] C8.2 — Re-scope to fetal-only; linked-2024-cohort deferred (no NCHS public-use file exists yet); C8.1 test-infra bug fixed as a followup commit

**Choice (user-authorized at PRE-FLIGHT halt-and-ask 2026-05-12T22:30Z):** Apply two resolutions to two HALT conditions surfaced at C8.2 PRE-FLIGHT.

1. **HALT #1 resolution — re-scope C8.2 to fetal-only.** Edit `NEXT_STEPS.md` §15.C C8.2 entry and `KICKOFF.md` Phase C task list: remove all linked-file scope (DO steps 5, 7 partial; SMOKE Tier 4; linked VERIFY criteria). Effort revised from 1-2 sessions to 1 session. Linked-2024-cohort refresh becomes a future task to be triggered via §11 plan-update when NCHS publishes `2025PE2024CO.zip` (estimated 2027-Q1).
2. **HALT #2 resolution — C8.1 test-infra fix.** Add four empty `__init__.py` files at `fetal_death/`, `fetal_death/tests/`, `natality/`, `natality/tests/` to make pytest's default-mode co-collection work. Shipped as a separate `[c8.1-followup]` commit `b84ff0d` immediately before this plan-update commit. FIX_LOG entry filed at 2026-05-12T22:30:00Z as L17-extension.

**Alternatives considered (per HALT #1):**

1. **Re-scope C8.2 to fetal-only (chosen).** Pro: avoids ~50% of original C8.2 effort that has no canonical state to mutate; produces a clean v2.4.0 fetal-death-only release; clear plan-of-record for the linked file (wait for `2025PE2024CO.zip`). Con: leaves the linked refresh as a small future task — but since NCHS hasn't released the 2024-cohort file, there's nothing to do *now* regardless.
2. **Defer C8.2 entirely** (re-sequence Phase C). Pro: zero canonical-state mutation in this session. Con: fetal-death 2023+2024 IS available and refreshing it is the cheapest-pre-submission win identified in Phase B (`EXPLORATION_REPORT.md` §A.1); deferring loses that signal. **Rejected.**
3. **Confirm linked file is current and ship a v2.9.0 no-op refresh-checkpoint.** Pro: explicit version-history note that the C8.2 linked-refresh check ran. Con: a Zenodo version bump for an empty diff is wasteful (Anti-Pattern #6's spirit) and confuses cite-by-version downstream. **Rejected.**

**Alternatives considered (per HALT #2):**

1. **Add four `__init__.py` (chosen).** Pro: cleanest fix; pytest's default prepend mode generates unique fully-qualified names; no new config file; forward-compatible with C8.5 (lockfile) which will add a `pyproject.toml` for environment-pinning unrelated to test config. Con: makes `fetal_death/` and `natality/` formal Python packages (zero existing code imports them as packages — verified via `git ls-files | xargs grep -lE "^(from|import) (fetal_death|natality)\b"` → 0 matches; harmonize.py dry-imports OK).
2. **Add `pyproject.toml` with `[tool.pytest.ini_options] addopts = "--import-mode=importlib"`.** Pro: documents the import mode explicitly; no package-structure change. Con: adds a new top-level config file that C8.5 will then have to coexist with or replace. Slightly more architectural surface.
3. **Rename one test file** (e.g., `test_fd_schema_dtype_parity.py`). Pro: 2-line code change. Con: breaks the symmetry between subprojects' test naming; the next time a paired test file is added (e.g., `test_release_smoke.py` for natality at C8.4) the same bug returns. **Rejected as not-durable.**
4. **Defer to C8.6 (CI wiring).** Pro: zero work now. Con: STATUS 22:00Z's "16 tests across both subprojects" claim remains unverifiable from the documented combined-pytest command until C8.6 forces a fix. **Rejected** — cheap-check moment is now.

**Reason:** Both HALTs are inexpensive to resolve at the C8.2 PRE-FLIGHT cheap-check moment and both have clean, forward-compatible fixes. The §11 plan-update process specifically accommodates this kind of scope correction surfaced during PRE-FLIGHT verification of plan-vs-reality alignment (Convention 3 Field-value snapshot caught the linked-file conflict at the right moment — exactly what cheap-checks are for).

Two protocol justifications: (i) §2 principle 1 "cheap-before-expensive" — discovering the linked no-op now saves a ~412 MB download + multi-hour re-harmonize attempt that would have produced byte-identical output; (ii) §11 plan-update process is the canonical path for in-Phase-C scope adjustments (per Q42 self-resolution: §11 plan-update required for any new candidate adding >1 session OR removing >1 session of scope). The linked-portion of C8.2 was ~0.5-1 session of work; the removal is right at the §11 threshold and gets a [plan-update] commit anyway.

**Source:**
- `PRE_FLIGHT_LOG.md` 2026-05-12T22:30:00Z entry documenting both HALTs.
- §15.C C8.2 entry pre-revision text (line 817-880 in NEXT_STEPS.md at commit `9fe662a`; full text preserved in git history).
- `EXPLORATION_REPORT.md` §A.1 (fetal-only portion remains in scope; linked-file portion already noted as "the 2024-cohort linked file isn't out yet but a refresh task can fire when it lands").
- NCHS public-use FTP HEAD probes 2026-05-12T22:30Z: `2024PE2023CO.zip` → HTTP 200 (cohort 2023, already imported); `2025PE2024CO.zip` → HTTP 404 (cohort 2024 not yet released).
- `natality/metadata/file_inventory.csv` row `2023_linked,…,2024PE2023CO.zip,imported=true,Cohort year 2023` (sha=`0e31b92bc05b6011…`).
- Linked parquet on disk (`/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized.parquet` sha=`e1795ac615a6ee40…`, 74,943,824 rows × data_year ∈ {2005…2023}) confirms 2023-cohort already shipped.
- User authorization chat 2026-05-12T22:30Z: HALT #1 = "Re-scope C8.2 to fetal-only (Recommended)"; HALT #2 = "Add __init__.py to both test dirs now (Recommended)".

**Verifiable by:**
- This `[plan-update]` commit's diff shows `NEXT_STEPS.md` §15.C C8.2 entry rewritten + `KICKOFF.md` line 178 edit + `PRE_FLIGHT_LOG.md` addendum + `STATUS.md` new section + this DECISION_LOG entry.
- Tag `C8.2-pre-do` lands on this commit (PRE-FLIGHT now PROCEEDS post-resolution).
- Commit `b84ff0d` (immediately prior, `[c8.1-followup]`) shows the 4× `__init__.py` additions + FIX_LOG entry.
- `pytest fetal_death/tests/ natality/tests/` under default import mode now returns "15 passed, 1 xfailed in ~39s" (cache-cleared run).
- Future re-scope of the linked-file portion: triggers a new `[plan-update]` commit when NCHS releases `2025PE2024CO.zip` (HEAD-probe will return HTTP 200; PRE-FLIGHT for the new task fires).

**Reversible:** yes — `git revert <this commit>` restores the original C8.2 §15 entry. The 4× `__init__.py` files can be removed by `git revert b84ff0d` (the `[c8.1-followup]` commit). Both reverts are independent and additive.

**Residual risks:**
- (a) **The "linked-2024-cohort needs a future task" assertion may be wrong** if NCHS changes the period-cohort-linked release cadence (e.g., releases two cohorts in one period file, or skips a cohort year). Mitigation: the future task's PRE-FLIGHT will run a sibling-probe of the FTP directory before assuming any specific filename. The §11 plan-update at that time would record any naming-convention surprise.
- (b) **The 4× `__init__.py` may interact with future package-management work** at C8.5 (uv/poetry lockfile) if the lockfile authoring chooses to treat `fetal_death/` and `natality/` as installable packages. Currently they are not installable; the `__init__.py` files are inert for `pip install` purposes. Mitigation: C8.5 PRE-FLIGHT explicitly notes the package-vs-not-package status of each subproject.
- (c) **The re-scoped C8.2 still mutates many files** (file_inventory.csv, validation_targets.csv, schema.csv years_available, harmonize.py SHA if era_tag mutates, version bumps in 4+ doc files, smoke EXPECTED state). The PRE-FLIGHT addendum's PROCEED clause covers these; the receipt's Forward-looking HALTs spec covers them too.

**Self-check (residual risks the VERIFY phase wouldn't catch):**
- This entry asserts the linked file is already at maximum NCHS-public-use extent. Verification: linked parquet data_year ∈ {2005…2023} confirmed by `pq.read_table(p, columns=['data_year'])`. If NCHS *had* released a partial 2024-cohort file under a different naming convention, this entry would miss it. Mitigation: explicit HEAD probes of `2025PE2024CO.zip` (404) and `2024PE2024CO.zip` (404) cover the natural sibling-derived candidate URLs; sibling probe of the NCHS landing page (`cdc.gov/nchs/data_access/vitalstatsonline.htm` via WebFetch 2026-05-12T22:30Z) confirms the most-recent period-cohort release documented is "2024 period/2023 cohort."
- The `[c8.1-followup]` commit's classification as "fix" (not a §11 plan-update) is borderline — it touches test infrastructure not data, and Anti-Pattern #6 ("never edit harmonized_schema.csv without bumping the schema version") doesn't apply. The 4× `__init__.py` files are pure-additive and reversible.

**Backport scope (per §11.4):** None. C8.1's RECEIPT and STATUS 22:00Z section remain canonical for what C8.1 shipped; the `[c8.1-followup]` patch is documented in FIX_LOG 2026-05-12T22:30:00Z; future audits see the trail. The C8.1 RECEIPT's Self-check section already flagged "test infrastructure may need closer scrutiny" as a residual risk (item 1 — though framed around xfail rot, the broader test-infra fragility was implied).

---

## 2026-05-12T22:00:00Z — C8.1 — schema `years_available` regen via `_regenerate_schema_years.py` — auto-derived field cleanup; NO schema-version bump

**Choice:** Run `python3 fetal_death/scripts/_regenerate_schema_years.py` (sibling of standalone-build script, now copied into the monorepo) to update 46 of 73 `harmonized_schema.csv` rows whose `years_available` strings had drifted from the actual parquet data after the V3a + V3b backward extensions (V3a RECEIPT note 8 + V3b RECEIPT note 8 explicitly deferred this cleanup). **No schema-version bump** — `years_available` is an auto-derived field whose canonical value is mechanically derivable from the parquet; the regen script's purpose is exactly this regeneration. New schema SHA: `337a0ad0ab6d0a6b…` (was `69f92bf775251f1e…`).

**Alternatives considered:**

1. **Run the regen now as part of C8.1 (chosen).** Pro: closes the V3a/V3b deferred-cleanup item with the right tool (auto-derivation, not hand-editing); the `_regenerate_schema_years.py` test in the smoke suite (`test_schema_years_available_matches_data`) becomes PASS-able without xfail/skip. Con: schema CSV SHA changes; future grep against the old SHA needs to point at the new SHA.

2. **Bump fetal-death version v2.3.0 → v2.4.0 as part of C8.1.** Pro: Anti-Pattern #6 says "Never edit harmonized_schema.csv without bumping the schema version OR adding a comment row referencing the relevant DECISION_LOG entry"; a literal reading would force a version bump. Con: `years_available` is a documentation field, not a schema-structure change (no column added/removed/redefined); a version bump for a regen feels like inflated bookkeeping. Also: C8.2 (latest-year refresh) will likely re-regen with +2023/+2024 entries and bump to v2.4.0 anyway; doing it now and then bumping again on C8.2 is wasteful.

3. **Defer to C8.2.** Pro: bundle the regen with the version bump. Con: leaves the smoke's `test_schema_years_available_matches_data` failing through C8.1's interim, which violates the "every commit ships green CI" discipline that Tier 1 is building toward.

4. **Mark `test_schema_years_available_matches_data` xfail.** Pro: defers the schema edit. Con: actively hides a fixable drift via xfail when the tooling to close it exists right now.

**Reason:** The DECISION_LOG-entry exception in Anti-Pattern #6 is exactly designed for this case: the rule's spirit is "no silent schema edits that could be missed by a future audit." Filing this DECISION_LOG entry + the C8.1 RECEIPT + the FIX_LOG L13-extension entry makes the regen fully auditable: a future session sees the entry, the per-column drift list in this entry's source, and the test passing on the new state. Anti-Pattern #6 is satisfied.

Three protocol justifications: (i) §2 principle 1 "cheap-before-expensive" — running the canonical regen tool is cheaper than authoring a version-bump migration; (ii) §2 principle 4 "re-running must be free" — `_regenerate_schema_years.py --check` is idempotent and confirms the new state; (iii) §11 plan-update process is not triggered — this is a documentation-field regeneration, not a structural schema change.

**Source:**
- `fetal_death/scripts/_regenerate_schema_years.py` (newly canonicalized in the monorepo per C8.1 DO-1).
- V3a RECEIPT `RECEIPTS/task7_v3a_2026-05-12T14-30-00Z.md` Notes-for-next-session item 8 ("Schema CSV `years_available` retroactive V3a gap fixes still deferred. Task 10 polish.").
- V3b RECEIPT `RECEIPTS/task7_v3b_2026-05-12T18-45-00Z.md` Notes-for-next-session item 8 (same text, V3a→V3a/V2.1 substitution).
- STATUS 2026-05-12T18:45Z Build-artifacts-current item 7 ("PROVENANCE.md still stale at v2.0.0 SHAs … Task 10 PRE-FLIGHT must refresh it.") — note: PROVENANCE.md refresh is separate from this schema CSV regen and remains deferred to C8.13 / Phase D.

**Verifiable by:**
- `git show HEAD:fetal_death/harmonized_schema.csv | shasum -a 256` returns `337a0ad0ab6d0a6b…`.
- `python3 fetal_death/scripts/_regenerate_schema_years.py --check` returns "OK: schema years_available matches data for all 73 columns" on the post-regen schema.
- `pytest fetal_death/tests/test_release_smoke.py::test_schema_years_available_matches_data` PASSes (was FAIL pre-regen).
- 46 rows changed; 27 rows unchanged (those whose `years_available` was already correct pre-V3a/V3b). Per-row diff visible in `git diff HEAD~1 fetal_death/harmonized_schema.csv`.

**Reversible:** yes — `git revert <this commit>` restores the prior `years_available` strings. The script is idempotent so re-running on the reverted state produces the same drift report.

**Residual risks:**
- (a) **The regen overwrites any hand-curated `years_available` strings that intentionally used a non-canonical shorthand.** Verified by inspection of the drift list: every drifted row's "target" is strictly more accurate than the "current" (e.g., `version_flag`: '1982-1988, 1992-2002, 2005-2022' → '1982-2022' — current was just stale, not intentional). No hand-curated annotations lost.
- (b) **Future data extensions (e.g., C8.2 latest-year refresh) will trigger another drift.** Mitigation: every subsequent data-extension task PRE-FLIGHT lists schema regen as a planned in-task step; the regen is bundled into the task that introduces the new year(s) so the schema and parquet always agree at task-completion time.

**Self-check (residual risks the VERIFY phase wouldn't catch):**
- The regen script computes `years_available` as the set of `data_year` values where the column has non-null content. For columns that are *intentionally* null in some years (e.g., `hispanic_origin` truly absent before 1989), the regen reflects shipped reality. If shipped reality is wrong (e.g., a parser bug populated a column erroneously), the regen would document the bug as canonical. Mitigation: V3a/V3b RECEIPT byte-clean regression already verified no spurious populations; the regen reflects intentional state.
- The regen does not update the `notes` field or any other column's annotations that might reference outdated year ranges. Anti-Pattern #6's "schema edits require version bump" applies more naturally to structural changes; documentation-field updates have a lower bar. Mitigation: per-row review during regen confirms no `notes` field references stale year ranges in this case.

**Backport scope (per §11.4):** None directly. The V3a RECEIPT note 8 and V3b RECEIPT note 8 items are now CLOSED.

---

## 2026-05-12T21:00:00Z — [plan-update] phase_c_authorized — User authorized Q35 = Tier 1+2 (~29-35 sessions of Phase C); Q32-Q42 self-resolved by LLM per user directive; KICKOFF.md Phase C populated + NEXT_STEPS.md §15 C8.1-C8.15 task entries appended

**Choice (user-authorized):** Q35 = **(b) Tier 1 + Tier 2** = ~29-35 sessions of Phase C work before Phase D (Task 9 + Task 10 + public-repo v1.x sync + manuscript submit). Phase B `EXPLORATION_REPORT.md` §K plan-update applied at this commit: KICKOFF.md Phase C placeholder replaced with the Tier-1+Tier-2 task list; NEXT_STEPS.md §15 appended with C8.1-C8.15 task entries (each with full five-phase framing per §4 + Convention 1-5 binding); this DECISION_LOG entry + accompanying STATUS section record the authorization.

**Q32-Q42 self-resolutions** (per user directive "the rest of the questions attempt to answer by yourself without my input in the best way possible"):

- **Q32 (Phase B 7th-dimension inclusivity).** CLOSED — no 7th dimension surfaced during Phase B. The six-dimension brief (data extensions, robustness/testing, usability/convenience, cross-product/joint-use, documentation, performance/distribution) was comprehensive. The ~42 candidates enumerated in EXPLORATION_REPORT §A-§F cover every legitimate pre-submission expansion surface identified.

- **Q33 (Phase C effort ceiling).** No explicit cap; user authorized Tier 1+2 ~29-35 sessions and asked LLM to self-pace. **Self-imposed halt-checkpoint**: if cumulative Phase C effort drifts beyond +20% of the 29-35 session estimate (i.e., >42 sessions), halt at the next clean task boundary and re-ask the user before continuing. Encoded in KICKOFF.md "Always-on Phase C discipline" section.

- **Q34 (in-scope vs out-of-HVS-mission boundary).** **Affirmed as-defined**: HVS scope is vital events around birth (natality + fetal death + linked birth-infant death). Marriage/Divorce, Multiple-Cause-of-Death (all-age mortality), and abortion surveillance are explicitly OUT-of-scope per EXPLORATION_REPORT §A.6. The one-paragraph boundary statement in PRIOR_ART.md ships as part of **C8.8** (CHANGELOG + PRIOR_ART update) to preempt reviewer "why not all vital events?" comments.

- **Q35.** **(b) Tier 1 + Tier 2 authorized** by user directive 2026-05-12. ~29-35 sessions of Phase C before Phase D.

- **Q36 (Tier-5 ordering).** **N/A** — Tier 5 not authorized in this round. If user later authorizes Tier 5: default A.2 (natality 1968-1989) first (shorter, cleaner sibling of V3b just shipped), A.3 (linked 1983-2004) second (benefits from A.2's 1978-cert layout knowledge).

- **Q37 (Phase C kickoff item).** **C8.1 first** (cheapest item, pure-metadata, fixes the known stale L17 smoke case per STATUS 20:30Z FL-HALT #10). **C8.2 second** (latest-year refresh: extends data envelope before any test/CI scaffolding so subsequent CI gates on the full envelope). Sequencing encoded in KICKOFF.md "Sequencing notes within Phase C" section.

- **Q38 (R-only vs full Stata/SAS/R coverage).** **R full quickstart ships** (C.2 inside **C8.9**). **Stata/SAS pointer-files deferred** to post-v1 ancillary (C.3 = Tier 3 = deferred per Q41 default). Rationale: R quickstart's marginal cost is ~1 session; full Stata/SAS quickstarts require Stata/SAS licenses on the build machine (we don't have them) and pointer-files give 80% of the value at 10% of the cost. Defer until a Stata/SAS-using contributor surfaces, or until the IJE post-publication community signals demand.

- **Q39 (CLI tool vs DuckDB views).** **DuckDB views ship** (C.4 inside **C8.9**). **CLI tool deferred** (C.7 = Tier 3 = deferred per Q41). Rationale: DuckDB's SQL surface covers the same ad-hoc-query use cases as a custom CLI but with zero maintenance burden (DuckDB ships with its own CLI; users wrap with `duckdb -c "SELECT * FROM <view>"`). The custom CLI was strictly dominated by DuckDB in `EXPLORATION_REPORT.md` §C.7.

- **Q40 (manuscript re-paragraph cadence).** **Single submission after Tier 2.** Tier 5 deferred per Q35; the re-paragraph-twice scenario does not apply. If Tier 5 is later authorized post-submission, ships as v1.1 / v2.0 with an IJE *Update* note or a new Zenodo concept-DOI patch. Manuscript Coverage paragraph updated once (KICKOFF Phase D step 6) reflecting 1982-2024 fetal death + 1990-2024 natality + 2005-2024 linked envelope (post-C8.2 refresh).

- **Q41 (Tier-3 items).** **Defer all to post-v1 ancillary releases.** Specifically: A.5 matched-multiples (1-2 sessions; post-v1), E.7 CODEBOOK extensions (2-4 sessions; post-v1 — diminishing returns vs. existing CODEBOOK), C.3 Stata/SAS pointer-files (per Q38), C.5 pre-computed cross-tab CSVs (1 session; defer — maintenance tax), C.7 CLI tool (per Q39). All five Tier-3 candidates revisitable at Phase D close.

- **Q42 (Phase B-2 trigger conditions).** **§11 plan-update required** for any new candidate adding **>1 session**. ≤1 session candidates may be folded into the nearest in-progress C8.X task as a scope amendment via DECISION_LOG entry (no separate `[plan-update]` commit). >1 session candidates require explicit user authorization before execution. Encoded in KICKOFF.md "Always-on Phase C discipline" section.

**Alternatives considered:** None for this specific authorization-application — the user explicitly directed Q35 = (b) and self-resolution of the rest. The alternatives considered for each Q above are documented in EXPLORATION_REPORT.md §H + this entry's per-Q rationale.

**Reason:** User explicit directive 2026-05-12 in response to LLM's (a)-(d) handshake post-kickoff: *"Q35: Tier 1+2 the rest of the questions attempt to answer by yourself without my input in the best way possible."* The §11 plan-update process (LESSONS → propose diff → human review → LLM applies → commit `[plan-update]`) is satisfied: EXPLORATION_REPORT.md §K is the proposed diff; user reviewed via the (a)-(d) handshake; this commit applies it; the `[plan-update]` prefix tag is on the commit.

**Source:**
- `EXPLORATION_REPORT.md` §G.4 (suggested execution order) + §H (open questions) + §K (plan-update structure).
- `STATUS.md` 2026-05-12T20:30:00Z "Notes for next session" item 2 (Tier 1+2 default path) + items 3-5 (per-prefix execution branches).
- `KICKOFF.md` "Current planned sequence" 2026-05-12 (Phase B mandate; commit `306370e`).
- User authorization chat 2026-05-12: *"Q35: Tier 1+2 the rest of the questions attempt to answer by yourself without my input in the best way possible."*

**Verifiable by:**
- This `[plan-update]` commit's diff shows KICKOFF.md Phase C placeholder replaced with the Tier-1+Tier-2 task list + NEXT_STEPS.md §15 appended with C8.1-C8.15 entries.
- Tag `phase-c-authorized` lands on this commit.
- The next session's `git tag --list 'C8.*'` shows progression: first `C8.1-pre-do` (after PRE-FLIGHT), then `C8.1-complete` (after RECEIPT), then `C8.2-pre-do`, etc.
- Q32-Q42 self-resolutions in this entry are auditable: a future audit session can verify each resolution against the EXPLORATION_REPORT.md options + the user's stated preferences (the user explicitly authorized Tier 1+2 = "robust and useful middle ground" — every Q32-Q42 self-resolution follows that signal).

**Reversible:** yes at any point during Phase C — the user can re-issue any of (a) "skip ahead to Phase D", (b) "trim Tier 2 to subset", (c) "add Tier 5 candidate X", (d) "reverse a specific Q-resolution" — each triggers a new `[plan-update]` commit (per §11). Already-shipped Phase C tasks are reversible via `git tag <task_id>-pre-do` rollback.

**Residual risks:**

- (a) **Q33 effort-ceiling may surface mid-Phase-C.** If C8.4 (invariant tests) takes 5 sessions instead of 3, or if C8.12 (mutation tests) cascades through FIX_LOG, the cumulative drift breaks the +20% cap. Mitigation: halt at next clean checkpoint per encoded discipline; surface honestly; ask user to trim Tier 2 if needed.

- (b) **Q38 + Q39 deferrals may need re-opening if reviewer feedback specifically asks.** A reviewer who works in Stata or wants a CLI tool may surface the request post-submission. Mitigation: framing the deferrals as "post-v1 ancillary" (not "rejected"); easy to add via §11 plan-update.

- (c) **Q41 Tier-3 defer-all may be wrong for E.7 CODEBOOK extensions.** Per-variable historical-value-distribution panels could materially strengthen the manuscript's *Comparability classification* claim. The 2-4 session cost is the friction. Mitigation: revisit at Phase D close; possibly pull E.7 into Phase D scope.

- (d) **Q42 §11-plan-update threshold (>1 session) may be too lenient or too strict.** A 0.6-session candidate that affects schema (e.g., a new derived column) is materially different from a 0.6-session candidate that affects docs only. Mitigation: schema-touching candidates default to §11 regardless of session count; docs-only candidates default to in-progress-task amendment regardless of session count.

- (e) **The plan-update applies the §K.1 KICKOFF replacement + §K.2 NEXT_STEPS §15 appends but does NOT yet update PROVENANCE.md, the manuscript, or any data artifact.** Those updates remain queued per existing STATUS.md notes. Mitigation: encoded in C8.X task descriptions; each task's RECEIPT updates the relevant downstream artifact.

**Self-check (residual risks the VERIFY phase wouldn't catch):**

- The Q32-Q42 self-resolutions reflect *my* read of EXPLORATION_REPORT.md's defaults + the user's "best way possible" signal. A subtle risk: the user might have intended a meaningfully different default for one or more Qs (e.g., they might have wanted Stata/SAS quickstarts to ship, or the CLI tool, or Tier-3 CODEBOOK extensions). Mitigation: each self-resolution is explicit + reversible; if the user surfaces a disagreement post-fact, a single `[plan-update]` commit adjusts the plan.

- The NEXT_STEPS.md §15 C8.1-C8.15 entries vary in detail (C8.1 + C8.2 fully fleshed per §K.2 promise; C8.3-C8.15 compact). The compact entries name the goal + inputs + DO scope + VERIFY but defer the full SMOKE plan + Forward-looking HALTs spec to each task's own PRE-FLIGHT. This is per existing §15 precedent (Task 9 entry is similarly compact). Risk: a future session might claim "C8.X §15 entry is too thin to PRE-FLIGHT from" — mitigated by PRE-FLIGHT extending the entry as needed per §4.1.

- This entry's Q-self-resolutions are not user-confirmed individually. A safer protocol would have surfaced each Q as a separate AskUserQuestion; the user's "answer them yourself" directive explicitly waived that. Risk surfaced + accepted by user; the §11.4 backport process covers any reversal.

**Backport scope (per §11.4):** None. Phase A + Phase B receipts are unaffected by this plan-update. C8.X tasks ship forward.

---

## 2026-05-12T20:30:00Z — phase_b_exploration — Phase B exploration session COMPLETE; `EXPLORATION_REPORT.md` drafted; plan-update proposal status PENDING USER REVIEW; recommended prefix Tier 1+2 ~29-35 sessions

**Choice (proposal pending user confirmation):** Phase B's deliverable is `EXPLORATION_REPORT.md` at monorepo root (new file; 6-dimension candidate enumeration ~42 candidates across §A–§F + cumulative effort estimate + suggested execution order in §G.4 + plan-update proposal in §K + open questions Q35–Q42 in §H). The plan-update proposal (KICKOFF.md Phase C replacement + NEXT_STEPS.md §15 task entries C8.1–C8.23) is NOT yet applied; it requires explicit user authorization via Q35.

**Recommended user choice for Q35**: Tier 1 + Tier 2 (~29-35 sessions of Phase C work) as the "robust and useful" middle ground that maximizes pre-submission polish without the multi-month timeline extension that Tier 5 (backward extensions A.2 natality 1968-1989 + A.3 linked 1983-2004) would impose.

**Alternatives considered (per Q35):**

1. **Tier 1 only (~13–15 sessions)** — Pre-Phase-D must-haves only: smoke retag, dtype parity, invariant tests, latest-year refresh, lockfile/Dockerfile, CI, end-to-end smoke, CHANGELOG + PRIOR_ART update. Ships a substantially more robust HVS than today; submit manuscript with current envelope. Pro: shortest path to submission (~2-3 weeks). Con: leaves R quickstart, DuckDB views, worked-example notebooks, migration guides on the table.

2. **Tier 1 + Tier 2 (~29–35 sessions, chosen as recommendation)** — Tier 1 + state-stratified denominators + R quickstart + DuckDB views + 3 worked-example notebooks + migration guides + cross-product COMPARABILITY + mutation tests + L13/L14 audits + GitHub release artifacts. Pro: maximally polished v1.0; manuscript ships at v1.0 with all infrastructure complete. Con: ~4-6 weeks to submission.

3. **Tier 1 + Tier 2 + Tier 5 (~45–62 sessions)** — adds natality 1968-1989 backward extension (6-10) + linked 1983-2004 (8-14) + perinatal-record pre-joined parquet (2-3). Pro: manuscript launches with maximum-extent coverage (natality 57 yrs, linked 41 yrs with documented 1992-1994 gap). Con: ~3-4 months to submission; re-paragraphs Coverage section twice; methodology-paper territory for the perinatal-record join.

4. **Phase B-2 (defer execution; further investigate before authorizing prefix)** — if any §H open question (Q35-Q42) cannot be answered today. Pro: zero commit risk. Con: another session of latency.

**Reason:** Phase B's mandate was to enumerate the frontier honestly without narrowing prematurely, then present the user with one decision point with full trade-off picture. The Tier-prefix structure in §G.4 lets the user authorize a specific prefix without committing to "everything possible" sight unseen. Each prefix delivers a coherent shipping checkpoint:

- Tier 1 → ships ~2-3 weeks; manuscript at current 1990-2024 / 1982-2024 / 2005-2024 (post-refresh) envelope.
- Tier 1 + Tier 2 → ships ~4-6 weeks; same envelope + maximum polish.
- Tier 1+2+5 → ships ~3-4 months; backward-extended envelope + maximum polish.

Three protocol justifications: (i) §11 plan-update process accommodates this kind of mid-project amendment; (ii) §2 principle 1 "cheap-before-expensive" — Phase B's read-only research was cheap relative to Phase C execution and prevented committing to "everything" sight unseen; (iii) §10 self-check — the structured per-candidate writeup (effort/risk/manuscript-impact) is the planning-level analog of "what could I have gotten wrong that VERIFY wouldn't catch."

**Source:**
- `EXPLORATION_REPORT.md` at monorepo root (drafted this session; ~1400 lines).
- Agent `aea960a496472bb6b` external-research transcript (50 tool uses, ~5min wall): NCHS FTP directory listings for natality, fetal-death, linked, period-cohort-linked, matched-multiples, mortality; CDC NCHS data-access landing page; NBER, ICPSR, IPUMS scope confirmation. Full URL list in EXPLORATION_REPORT.md §A.9.
- Agent `a3e650be058a65976` literature-gap re-verification transcript (50 tool uses, ~4min wall): WebSearch + WebFetch on academic, GitHub, IPUMS, NBER, ICPSR. Gap claim defensible as of 2026-05; three small PRIOR_ART.md updates suggested.
- Internal repo introspection by orchestrating LLM (in parallel with agents): tests inventory (1 test file, stale L17 case post-V3b), CI inventory (none), reproducibility tooling inventory (none), docs inventory (CHANGELOG missing, manuscript stale, PROVENANCE.md 4 versions stale).
- User directive 2026-05-12 chat post-`task7_v3b-complete`: *"i would like do do everything possible with this project in terms of extending the actual project and adding diferent things to the project to make it as robust and useful as possible before we do the paper or the zenodo so i want to do an ivetigative session and exploration of what we can do and then add it to the plan to do it in subsequent sessions."*

**Verifiable by:**

- `EXPLORATION_REPORT.md` at monorepo root exists; sha256 recorded at commit time.
- This DECISION_LOG entry timestamp 2026-05-12T20:30:00Z supersedes 19:15:00Z's Phase-B-mandate status (from MANDATED to COMPLETE-PENDING-AUTHORIZATION).
- Forward-looking HALTs in STATUS 2026-05-12T20:30Z items 1-3 are the next session's pre-flight check: report file present, DECISION_LOG entry status unchanged, no C8.X tags yet.
- Next-session Phase C kickoff: if `git tag --list 'C8.*'` returns any tag, the user must have authorized; otherwise Phase B halt is still in force.

**Reversible:** yes — Phase B is read-only. If the user finds the report's scope inadequate or the prefix structure too coarse, the next session can be a Phase B-2 (further investigation) or a Phase B amendment (re-scoring candidates) without any state to roll back. The plan-update proposal in §K is NOT yet applied to KICKOFF.md or NEXT_STEPS.md; those edits land only on Q35 authorization.

**Residual risks:**

- (a) **Effort estimates may be systematically biased.** Calibration anchor is V3b's empirical 2-3 sessions; the Tier-1 robustness items (test scaffolding, CI) are well-understood; the Tier-2 worked-example notebooks have higher variance (depends on user-validation feedback per notebook); the Tier-5 backward extensions are the highest-variance (cohort/period design decision in A.3 alone could absorb a session). Per the KICKOFF brief: estimates are honest ranges, not pinned values; the user reviews the total and trims if needed.

- (b) **Phase B did not deep-research several candidates' validation grids.** For natality 1968-1989, the *Vital Statistics of the United States* paper volumes are partially online and partially not — building a complete validation grid for A.2 may surface OCR friction not anticipated. For linked 1983-2004, the cohort/period publishing-design decision is mentioned but not adjudicated. Both are documented in §A as risks; Phase C PRE-FLIGHT for those tasks will do the L9 cheap-check on the actual NVSR / Linked-File documentation.

- (c) **The user may want to add a candidate not in this report.** Phase B's §G.4 enumerates ~42 candidates from the KICKOFF brief's six-dimension grid; if the user's response to Q35 surfaces a 43rd ("can we also add X?"), the right protocol is a §11 plan-update at that point (per Q42 default), not a silent in-Phase-C scope creep.

- (d) **Phase B may have under-narrowed.** Tier 3 (matched-multiples ancillary, CODEBOOK extensions, Stata/SAS quickstarts, pre-computed cross-tab CSVs, CLI tool) is listed as defer-to-post-v1 in §G.4 — but a user who wants "everything" maximally might pull some of these into Tier 2. Q41 surfaces this explicitly.

- (e) **Manuscript framing may need adjustment per Q40.** If Tier 5 is in scope, the question of single-submission vs. dual-submission-with-v1.1-update is a real editorial decision (some journals support post-publication data-update notes; some don't). The default in §G.5 — single submission after Tier 2, Tier 5 as v1.1 update — is the lowest-risk path but the user may prefer otherwise.

**Self-check (residual risks the VERIFY phase wouldn't catch):**

- This entry asserts Phase B's deliverable is complete. The verification is the existence of `EXPLORATION_REPORT.md` at monorepo root + its §0-§K structure + the §H open questions being answerable from the report's content. A subtle risk: Phase B may have systematically over-prioritized testing/robustness items (B.1-B.12) because those are the easiest to score with the protocol's existing mistake-class matrix (§8), while harder-to-score items like research-extensions (C.8 perinatal-record join) and methodology-paper territory (A.3 cohort/period design) may be under-prioritized. Mitigation: the §G.4 tiering is explicit about which category each candidate falls into; the user can override the Tier-3/Tier-5 framing in Q41 / Q40.

- The two external-research agents were instructed to verify URLs + literature gap; the orchestrating LLM did not separately re-verify their findings (per "trust but verify" in the harness instructions). Mitigation: agent transcripts are at the disk locations cited in STATUS Notes; the user can spot-check any URL or citation by hand. The HTTP-200 / HTTP-404 results are deterministic facts about the CDC FTP server state on 2026-05-12 and can be re-verified at any time.

- This entry's "Recommended Tier 1+2" framing is a soft recommendation. The user has full discretion via Q35; this entry is not authorization for any specific prefix.

**Backport scope (per §11.4):** None. Phase B is read-only and no prior receipts are invalidated. Phase C work that lands after authorization may surface backports (e.g., the B.7 L13 audit may find an existing inventory CSV with stale claims), at which point §11.4 fires per-task.

---

## 2026-05-12T19:15:00Z — [plan-update] sequencing — Pre-submission scope expanded a 5th time: Phase B (READ-ONLY exploration session) + Phase C (execute proposed additions) inserted between Phase A (data-first; complete) and Phase D (paper + Zenodo + public-repo sync); manuscript submission paused

**Choice:** Add a mandatory **Phase B exploration session** (read-only) and a **Phase C execute-additions phase** to the pre-submission sequence in KICKOFF.md. The next LLM session is Phase B: research the full frontier of additions across 6 dimensions (data extensions, robustness/testing, usability/convenience, cross-product/joint-use, documentation, performance/distribution), produce per-candidate writeups with effort/risk/manuscript-impact estimates, propose a §11 plan-update for KICKOFF.md + NEXT_STEPS.md §15, halt for user authorization. Phase C subsequent sessions execute the user-authorized expanded plan. Phase D (Task 9 redirect notices + Task 10 unified Zenodo + public-repo sync + manuscript submit) runs only after Phase C completes.

**Alternatives considered:**

1. **Lock current 1982-2022/1990-2024/2005-2023 envelope and ship at v1.1** (the LLM's recommendation from chat 2026-05-12, post-V3b-complete). Pro: shortest path to submission; current coverage is already a defensible "Data Resource Profile" extent (41 yr FD + 35 yr natality + 19 yr linked). Con: leaves several plausible high-value additions (natality 1968-1989 backward extension; pre-2005 linked extension; latest-year refreshes; testing/usability infrastructure) on the table for a v2.0 release. User explicitly rejected this option in favor of maximum-extent pre-submission.

2. **Pull a SPECIFIC next addition (e.g., natality 1968-1989) into pre-submission without an exploration session.** Pro: faster than B+C. Con: chooses one expansion without comparing alternatives; loses the value of the systematic frontier sweep; would likely require subsequent ad-hoc expansions when the next idea surfaces. **Rejected** — exploration is a one-time investment that informs all subsequent expansion decisions.

3. **Insert exploration session + execute (chosen).** Pro: enumerates the full candidate set; gives the user one decision point with a concrete trade-off picture; subsequent execution sessions are well-scoped. Con: adds 1 session (Phase B) before any execution starts; total pre-submission timeline grows by Phase B (1 session) + Phase C (5-20 sessions TBD by Phase B output). **Selected**.

**Reason:** This is the 5th expansion of pre-submission scope (after Task 3 V2.1 → V3a → V3b → natality v2.8 → this one). The user's stated objective — *"i would like do do everything possible with this project in terms of extending the actual project and adding diferent things to the project to make it as robust and useful as possible before we do the paper or the zenodo"* — is maximalist; an exploration session is the right tool because individual pull-this-in decisions don't compare alternatives. Phase B's deliverable (a structured per-candidate writeup with effort/risk/impact) lets the user authorize a specific subset rather than committing to "everything" sight unseen.

Three protocol justifications: (i) §11 plan-update process explicitly accommodates this kind of mid-project amendment; (ii) §2 principle 1 "cheap-before-expensive" — Phase B's read-only research is cheap relative to Phase C execution; (iii) §10 self-check — surfacing the full candidate set forces the question "what could I have gotten wrong that VERIFY wouldn't catch" at the planning level, not just the per-task level.

**Source:**
- Chat 2026-05-12 between commits `b0c8b4a` (task7_v3b-complete) and this `[plan-update]` commit. User explicit directive quoted verbatim above.
- KICKOFF.md "Current planned sequence" section, rewritten in this commit, runs ~150 lines and is the canonical sequencing pointer for Phase B/C/D.
- Phase A complete summary in the new KICKOFF section reflects the closed receipts in `RECEIPTS/`.

**Verifiable by:**
- Next session's first action: pasting KICKOFF.md and outputting the (a)-(d) handshake. Expected (c): "Phase B exploration session per KICKOFF.md." If the LLM proposes any DO-phase work instead, halt — the KICKOFF directive was misread.
- Phase B deliverable: `EXPLORATION_REPORT.md` at monorepo root + STATUS.md section + new DECISION_LOG entry. None present today; their existence post-Phase-B is the verification.
- Phase C tasks: tagged `<task_id>-pre-do` + `<task_id>-complete` per added task; receipts in `RECEIPTS/`.

**Reversible:** yes — at any point during Phase B or Phase C, the user can re-issue the "lock current envelope, ship" decision; the existing Phase D plan (Task 9 / Task 10 / public-repo sync / manuscript) is intact and ready to execute. No canonical-state mutation is being committed by this plan-update itself — only the sequencing-pointer file (KICKOFF.md) and this DECISION_LOG entry.

**Residual risks:**
- (a) **Phase B inflates cumulative effort** — if Phase B proposes 15+ sessions of Phase C work, the manuscript submission delays significantly. Mitigation: Phase B's brief explicitly mandates honest effort estimates and a halt-for-authorization step; the user reviews the total before authorizing.
- (b) **Phase B over-narrows or under-narrows** — too narrow misses additions worth doing; too broad balloons Phase C. Mitigation: the six exploration dimensions are explicit in KICKOFF; the LLM must cover all six even if the proposal column for some dimensions ends up "no high-priority items found."
- (c) **Phase B hallucinates a candidate**. Mitigation: the brief mandates `WebFetch` + sibling-derived URL probing for every external data source (per LESSONS L1-extension 2026-05-12T04:30:00Z); any data candidate without verified URL+SHA is flagged as "needs further verification" rather than slotted for execution.
- (d) **Phase C surfaces a new mistake class mid-execution** that retroactively invalidates Phase A receipts. Mitigation: §11 backport process is unchanged; any new LESSONS row triggers a re-verification of affected prior tasks before continuing.
- (e) **Submission target slips past whatever timing the user has implicit**. Mitigation: surfaced honestly in Phase B's report; user decides.

**Self-check (residual risks the VERIFY phase wouldn't catch):**
- This plan-update is itself the kind of decision that the §10 self-check asks about: "what could I have gotten wrong that VERIFY wouldn't catch?" The biggest risk is that the user's intent — "everything possible" — is interpreted maximally when they actually meant "some specific high-value subset." The Phase B halt-for-authorization step is the mitigation: the user sees the proposed Phase C list and trims as desired before any execution. The §11 plan-update process puts the user back in the loop before any code or data is touched.
- The other class of risk: Phase B might surface a candidate the user already implicitly rejected (e.g., scope-creep into all-cause mortality, which is out-of-HVS-mission). Mitigation: the KICKOFF directive notes which extensions are clearly in-scope (vital events around birth: natality, fetal death, linked-infant-death) and lists candidate scope-creeps (e.g., multiple-cause-of-death) with "out of HVS scope unless user redirects" framing.

**Backport scope (per §11.4):** None. No prior receipts are invalidated by this plan-update; it's a forward-looking sequencing change only.

---

## 2026-05-12T18:30:00Z — task7_v3b — B3 maternal_race_bridged extension: 1978-rev 1-digit MRACE 0-9 → 4-cat bridged; code 7 (Other nonwhite) → null + code 9 (Not stated) → null

**Choice:** Extend the B3 `_checked_remap` in `fetal_death/scripts/03_harmonize/harmonize.py` with a new `era=='1985'` branch containing a 1-digit MRACE → bridged-race recode covering the 1978-revision V3b coding scheme:

| 1978-rev MRACE | Bridged | Records affected (1982-1988 total) |
|---|---|---|
| 0 (Other Asian or Pacific Islander) | 4 (API) | ~few hundred |
| 1 (White) | 1 (White) | ~290K |
| 2 (Black) | 2 (Black) | ~91K |
| 3 (American Indian/Aleut/Eskimo) | 3 (AIAN) | ~2K |
| 4 (Chinese), 5 (Japanese), 6 (Hawaiian), 8 (Filipino) | 4 (API) | ~12K combined |
| **7 (Other nonwhite)** | **"" (null)** | **~89 records** |
| **9 (Not stated)** | **"" (null)** | **~18,700 records (~3-5%/yr)** |

**Alternatives considered:**

1. **Map 7 → 4 (API).** Pro: keeps all V3b records in a bridged category. Con: incorrect — 1985 user guide page 18 explicitly names code 7 as "Other nonwhite", a residual catch-all for records not fitting any of the 8 specific named categories. Mapping to API would over-count bridged-API by ~89 records across 1982-1988. **Rejected** as semantically inaccurate.
2. **Map 7 → 3 (AIAN).** Pro: AIAN is a "minority other than Black/Asian" historical convention. Con: explicit conflation of unrelated racial groups. **Rejected**.
3. **Map 7 → null (chosen).** Direct parallel to V3a's 09 → null decision (DECISION_LOG 2026-05-12T14:30:00Z). The 4-cat bridged scheme does not have a residual bucket; null preserves integrity rather than false-categorizing. ~89 records exit race-stratified analyses; all V3b records remain in unbridged analyses (year totals, GA distributions, etc.). **Selected.**
4. **Add a new bridged category 5 = "Other (1978-rev residual)".** Pro: explicit. Con: schema mutation (`allowed_values=1|2|3|4|5`) for a category that exists only for V3b records — cross-era race comparability breaks. **Rejected** as scope-creep.

For code 9 (Not stated), null is the unambiguous choice — parallels V2 99 → null, V3a 09 → null. No alternatives considered.

**Reason:** The 1985 NCHS Fetal Death User Guide page 18 (item 79-81 MRACE field for the 1978-revision) explicitly defines MRACE codes 0-9 for 1978-revision records. Codes 4/5/6/8 cover specific Asian/Pacific-Islander subgroups; code 0 is the residual "Other API"; code 7 is the residual "Other nonwhite" (distinct from the API subgroups). The bridged-race 4-category recode (the NCHS standard since the 1997 OMB directives) has no residual bucket — White/Black/AIAN/API only. Mapping a residual catch-all into one of the 4 specific buckets would be a false categorization; null preserves integrity per the §2 fail-closed principle.

The 1978-revision residual structure differs from the 1989-revision: 1989-rev's residual catch-all is code 09 ("All other Races", catches everything not in 01-08); 1978-rev's residual is code 7 ("Other nonwhite", which sits alongside specific API subgroups 4-6/8 and the general API code 0). Both are residual; both map to null.

**Source:**
- `1985FetalUserGuide.pdf` page 18 (item 79-81 MRACE; PyMuPDF-extracted via text-layer, no OCR needed; SHA recorded in `raw_docs/fetal_death/` and verified at PRE-FLIGHT 2026-05-12T16:00Z).
- Per-year MRACE distributions in `output/yearly_clean/fetal_death_{1982..1988}_raw.parquet` confirming the 1-digit 0-9 scheme (no 99 sentinel; no 18-78 codes; codes 0-9 all observed).
- Existing B3 recode at `fetal_death/scripts/03_harmonize/harmonize.py` lines 271-300 (V2/V3a era; the entries `"99": ""` and `"09": ""` are the precedent for the null mapping).
- Documented in `fetal_death/V3b_1982_1988_LAYOUT_DECISIONS.md` ("Harmonization decision 2: B3 maternal_race_bridged 1-digit recode" section).

**Verifiable by:**
- `validate_external_v2.py` post-V3b: **33/33 PASS** byte-exact (counts 1982-2004 + rates 1995-2004). Per-year fetal-death counts (which use TABFLG/RESTATUS, not race) byte-exact against user-guide controls — confirming the 7→null + 9→null choices don't bias the canonical-filter aggregate (it can't, since the canonical filter doesn't use race).
- `python -c "import pandas as pd; df = pd.read_parquet('output/harmonized/fetal_death_derived.parquet'); v3b = df[(df.data_year >= 1982) & (df.data_year <= 1988)]; print('V3b null bridged-race:', v3b.maternal_race_bridged.isna().sum())"` returns ~18,789 (the ~89 code-7 + ~18,700 code-9 records).
- Re-running the harmonize.py B3 recode map inspection: the era=='1985' branch contains exactly 11 entries (codes 0/1/2/3/4/5/6/7/8/9 + blank); `_checked_remap` would raise on any unmapped code.

**Reversible:** yes — if a future analysis surfaces an NCHS-documented convention for 1978-revision code 7 (e.g., a peer-reviewed paper or an NCHS internal mapping that specifies 7 → bridged-X), the B3 map can be edited and the 1982-1988 yearly_clean parquets re-harmonized; V1+V2.1+V3a era unaffected.

**Residual risks:**
- (a) **NCHS may have a documented bridged-race convention for 1978-revision code 7 that I missed.** The 1985 user guide page 18 doesn't specify a 4-category bridged recode for code 7. RACEF3 (item 66-67 in the layout — the 3-category fetus race recode: 1=White, 2=Other than White or Black, 3=Black) would put code 7 records into RACEF3=2 — but that 3-cat collapse is incompatible with the harmonized schema's 4-category bridged scheme. Mitigation: same as V3a (DECISION_LOG 2026-05-12T14:30Z residual risk a); searching NVSR Series 21 reports for 1982-1988 race-stratified fetal death tables is post-submission scope.
- (b) **The ~89 record impact is small but non-zero on V3b race-stratified analyses.** A researcher using `maternal_race_bridged` to stratify 1982-1988 fetal deaths will see totals not exactly add up (89 records with null bridged-race from code 7; plus ~18.7K from code 9). The ~18.7K Not-stated fraction is ~3-5% per year — larger than V3a's 0.087% — because 1978-revision public-use files have a less-imputed race field than 1989+. Documented in V3b_LAYOUT_DECISIONS.md.

**Self-check (residual risks the VERIFY phase wouldn't catch):**
- Same as V3a — this entry asserts the 4-category bridged-race convention is "the NCHS standard since the 1997 OMB directives," paraphrasing common practice. A strict OMB-directive reading is post-submission scope.
- The ~89 code-7 records are a tiny fraction of V3b's 421K total, but in race-stratified time-series the V3b → V3a transition (1988 → 1989) will show a small step-change in API counts because 1978-rev code 7 (residual nonwhite) maps to null while 1989-rev's nearest analog (code 09 "All other Races") also maps to null — so no false transition is introduced. Verified: V3a's 09 = null and V3b's 7 = null are consistent treatments.

---

## 2026-05-12T18:30:00Z — task7_v3b — DATAYEAR 2-digit→4-digit expansion in harmonize.py era=='1985' branch (Option A)

**Choice:** In `harmonize.py` era=='1985' branch (1982-1988), expand the raw 2-digit DATAYEAR value ("82".."88") to the 4-digit `delivery_year` ("1982".."1988") via `df["delivery_year"] = ("19" + s).astype(str)` where `s` is the stripped raw DATAYEAR string. Defensive `ValueError` raised if any raw value is non-2-digit.

**Alternatives considered:**

1. **Option A — harmonize.py era=='1985' branch (chosen).** Pro: harmonization is the right layer for cross-era schema uniformity; preserves raw-byte fidelity in the yearly_clean parquet (1978-rev "82" stays as "82" there); pattern matches the era=='2003' B7 TABFLG correction structure. Con: adds one short block to harmonize.py.
2. **Option B — pre-process in `parse_fetal_year.py`.** Pro: simpler harmonize.py. Con: parser should preserve raw bytes (the documented `01_import/` convention); year-conversion is a harmonization concern, not a parse concern. **Rejected.**

**Reason:** The harmonized `delivery_year` column is documented as a 4-digit string across all eras for schema uniformity. V2/V2.1/V1 raw fields (DELYR @ 190-193, DOD_YY @ 15-18 / 11-14) are already 4-digit; only V3b needs an expansion. The era=='1985' branch is the natural home — it parallels the era=='2003' B7 TABFLG correction pattern (a runtime field-level fix applied per-era). Putting it in the parser would violate the raw-byte-preservation principle and introduce era awareness into the parse layer.

**Source:**
- `record_layout_1982_1988.csv` row 1 (DATAYEAR at bytes 1-2; description "Last Two Digits of Current Data Year (1978-rev)"; values "82=1982 through 88=1988").
- `harmonize.py` era=='1985' branch (lines newly added at Task 7 V3b DO step 4).
- `harmonize.py` era=='2003' branch precedent (B7 TABFLG correction at lines 358-375) — established the runtime-per-era field-correction pattern.

**Verifiable by:**
- `python -c "import pandas as pd; df = pd.read_parquet('output/harmonized/fetal_death_harmonized.parquet'); print(sorted(df.query('1982 <= data_year <= 1988').delivery_year.unique()))"` returns `['1982', '1983', '1984', '1985', '1986', '1987', '1988']` (all 4-digit strings, no leakage of "82".."88").
- The defensive halt would fire if any raw DATAYEAR was non-2-digit; it didn't fire across all 7 V3b years (421,125 records), confirming clean 2-digit raw input.
- `validate_external_v2.py` post-V3b: 33/33 PASS byte-exact, including all 7 V3b counts that depend on `data_year == year` matching — `data_year` is int32 from harmonize.py's dict init (separately from `delivery_year`), so this verifies both the int32 conversion AND the string expansion produce consistent year values.

**Reversible:** yes — the expansion is a 4-line block at one location in `harmonize.py`. If a future analysis needs the 2-digit raw form, the yearly_clean parquet preserves it.

**Residual risks:**
- (a) **The "19" prefix is hard-coded.** If a future V4 extension covered 2000+ years using the 1978-revision layout (which it won't — 1978-rev was superseded by 1989-rev effective 1989 data), the prefix would be wrong. Mitigation: V3b's coverage is bounded to 1982-1988 by `_era_tag()`; no risk in practice.
- (b) **`delivery_year` is string-typed; `data_year` is int32.** Cross-era consistency: `delivery_year` always string everywhere (V2/V3a/V3b "1985"-format; V1 "2005"-format). `data_year` always int32. Smoke verified at DO step 4.

**Self-check (residual risks the VERIFY phase wouldn't catch):**
- The defensive halt only fires on non-2-digit raw values. If a raw DATAYEAR was "82" but the BYTE positions were wrong (e.g., parser misaligned by 1 byte), the expansion would silently produce "1982" anyway from whatever 2-character substring landed there. Mitigation: the canonical-filter cross-check at DO step 8 (byte-exact NVSR-equivalent statistics for all 7 V3b years) catches byte-misalignment elsewhere; DATAYEAR-specific misalignment would surface as wrong year counts.

---

## 2026-05-12T14:30:00Z — task7_v3a — B3 maternal_race_bridged extension: 1989-rev MRACE 08→4 API, 09→null (consistent with 99 Unknown convention)

**Choice:** Extend the B3 maternal_race_bridged recode map in `fetal_death/scripts/03_harmonize/harmonize.py` with two entries to handle 1989-revision MRACE codes that the V2 (1992+) map doesn't cover:

- **`08` (Other Asian or Pacific Islander) → `4` (API)**: consistent with how codes 04-07 (Chinese, Japanese, Hawaiian, Filipino) and the parallel 1992+ codes 18-78 are mapped to bridged-API.
- **`09` (All other Races) → `""` (null/unknown bridged)**: consistent with how code 99 ("Unknown/Not stated") is handled 1993+. Affects 165 records total (1989: 34; 1990: 72; 1991: 59 — 0.087% of V3a year coverage).

**Alternatives considered:**

1. **Map 09 → 4 (API).** Pro: keeps all 1989-1991 records in some bridged category. Con: incorrect — "All other Races" is a residual catch-all per the 1989 user guide, not specifically API. Mapping it to API would over-count the API-bridged group by 165 records cumulatively and bias race-stratified rates upward for the API subgroup. Rejected as semantically inaccurate.

2. **Map 09 → 3 (AIAN).** Pro: AIAN is a "minority race other than Black" historical convention. Con: even worse than option 1 — explicit conflation of unrelated racial groups. The 1989 user guide's "All other Races" residual contains records whose race did NOT fit any of the 8 specific categories (01-08); imposing AIAN is misleading. Rejected.

3. **Map 09 → null (chosen).** Pro: integrity-preserving (no false categorization); consistent with the existing convention for code 99 "Unknown" (1993+); the 165 affected records remain in the parquet for unbridged analyses (totals, year trends, GA distributions are unaffected); only race-stratified subgroups exclude them, which is what unbridged-unknown records should do. Con: 165 records exit race-stratified analyses without explicit notice; mitigated by documentation in V3a_1989_1991_LAYOUT_DECISIONS.md + this DECISION_LOG entry. **Selected.**

4. **Add a new bridged category 5 = "Other (1989-rev residual)".** Pro: explicit. Con: requires harmonized_schema.csv allowed_values mutation (`1|2|3|4|5`); creates a category that exists only for V3a 1989-1991 records (since 1992+ has no equivalent); cross-era race comparability would break. Rejected as scope-creep beyond V3a.

**Reason:** The 1989 NCHS Fetal Death User Guide page 28 explicitly defines MRACE codes 01-09 for 1989-revision records and states "Race codes effective with 1989 data differ from previous years." Codes 04-08 cover specific Asian/Pacific Islander subgroups (Chinese, Japanese, Hawaiian, Filipino, Other API); code 09 is the residual "All other Races." The bridged-race 4-category recode (the NCHS standard since the 1997 OMB directives, also used downstream in NVSR Fetal/Perinatal Mortality reports) does not have a code for "Other Races" — it's specifically White/Black/AIAN/API. Mapping a residual catch-all into one of the 4 specific buckets would be a false categorization; null preserves integrity per the 4-core-principle "fail closed" (§2 principle 2 — when in doubt, don't fabricate; let downstream code see null).

**Source:**
- `1989FetalUserGuide.pdf` page 28 (item 79-81 MRACE, downloaded this session, sha256=`54c55a40bffea18244bd14acc60a5fa094346e87c4557cb94633c7b52599e9d1`).
- Per-year MRACE distributions in `output/yearly_clean/fetal_death_{1989,1990,1991}_raw.parquet` confirming the 9-code 01-09 scheme (no 99 sentinel; no 18-78 codes).
- Existing B3 recode at `fetal_death/scripts/03_harmonize/harmonize.py` lines 271-284 (V2 era; the entry `"99": ""` is the precedent for the null mapping).
- Documented in `fetal_death/V3a_1989_1991_LAYOUT_DECISIONS.md` ("The one code-system extension: B3 maternal_race_bridged" section).

**Verifiable by:**
- `validate_external_v2.py` post-V3a: 26/26 PASS. Per-year fetal-death counts (which use TABFLG/RESTATUS, not race) are byte-exact against user-guide controls — confirming the 09→null choice doesn't bias the canonical-filter aggregate (it can't, since the canonical filter doesn't use race).
- `python -c "import pandas as pd; df = pd.read_parquet('output/harmonized/fetal_death_derived.parquet'); print(df.query('data_year in [1989,1990,1991]')['maternal_race_bridged'].isna().sum())"` returns ~165 (the 09 records + any other nulled-by-edge-case records).
- Re-running the B3 recode map at `harmonize.py` line 271-300 inspection: the `"09": ""` entry is present alongside `"99": ""`.

**Reversible:** yes — if a future analysis surfaces a defensible convention (e.g., a peer-reviewed paper that handled 1989-rev "All other Races" via a specific bridged mapping), the B3 map can be edited to that mapping with re-derive of the V3a years only (V1+V2.1 era unaffected). A separate FIX_LOG entry would record the re-mapping with regression-scope documentation.

**Residual risks:**
- (a) **NCHS may have a documented bridged-race convention for 1989-rev code 09 that I missed.** The 1989 user guide page 28 does not specify a 4-category bridged recode for code 09. The MRACE3 (item 82-83 in the user guide) field provides a separate 3-category recode (1=White / 2=Other / 3=Black) where code 09 records would have MRACE3=2 — but that 3-category collapse is incompatible with the harmonized schema's 4-category bridged scheme. If NCHS has an internal-use 4-category recode that specifies code 09's mapping (perhaps in a separate document I don't have on disk), my null mapping may diverge from NCHS convention. Mitigation: the 4-category bridged variable is widely used and documented in NVSR; if NCHS's own publications race-stratify the 1989-1991 fetal deaths, those stratifications would be the cross-check (search NVSR Volume 41/42/43 or NCHS Series 21 reports for 1989-1991 fetal deaths by race stratified at the 4-category bridged level). Such a cross-check is out of V3a scope; documented as a possible Task 11+ verification step.

- (b) **The 165-record impact is small but non-zero on race-stratified analyses.** A researcher who uses `maternal_race_bridged` to stratify 1989-1991 fetal deaths will see the totals not exactly add up (165 records with null bridged-race). For unbridged analyses (year totals, year trends, GA-stratified, etc.) this has no effect. The behavior is consistent with how 1993+ Unknown-race records are handled, so a researcher familiar with the V2 era's race-handling will not be surprised. Documented in V3a_1989_1991_LAYOUT_DECISIONS.md.

- (c) **Future audit may surface that "Other Asian or Pacific Islander" (code 08) should NOT map to bridged-API.** Per the 1989 user guide, the 08 records are explicitly Asian/Pacific Islander but not in the 5 specific named groups (Chinese/Japanese/Hawaiian/Filipino/Other API where Other API IS code 08 itself). Mapping 08 → 4 (API) is the natural reading. But a strict reading could argue that "Other Asian or Pacific Islander" was a NCHS-internal pre-bridged category that became finer 1992+ codes 18-78 — and that the bridged-race 4-cat scheme should always use 04-07 + 18-78 paths, never 08. In that strict reading, code 08 records (~2,800 across 1989-1991) would be null-bridged instead. Mitigation: the strict reading is unsupported by the 1989 user guide (which doesn't say "08 should be excluded from the bridged-API bucket"); the natural reading aligns 08 with 04-07 and 18-78 as all API-bridged. Documented as a strict-reading alternative in V3a_1989_1991_LAYOUT_DECISIONS.md.

**Self-check (residual risks the VERIFY phase wouldn't catch):**
- This entry asserts the 4-category bridged-race convention is "the NCHS standard since the 1997 OMB directives." That's a paraphrase of common usage in NCHS publications; if the actual OMB-directive language has more nuance (e.g., a 5-category breakdown that NCHS reduces to 4 for bridged use), the choice rationale should reference the OMB directive directly rather than the NCHS practice. Mitigation: the choice is internally consistent with how the existing V2 era B3 recode handles unknowns (99 → null) and the documented user-guide categories; a strict OMB-directive check is post-submission scope.

---

## 2026-05-12T13:35:02Z — natality_v28_rename — Retain aliasing helper NATALITY_TO_CANONICAL populated post-v2.8 (override prior "becomes no-op" framing to keep v2.7.0 Zenodo backward-compat)

**Choice:** Keep `shared/helpers/canonical_join_keys.py` `NATALITY_TO_CANONICAL` populated with its 4-entry mapping after v2.8 ships. Update the docstring to clarify that the helper is a no-op for v2.8+ input (rename map produces empty dict) but is retained for v2.7.0 input where the immutable Zenodo deposit 10.5281/zenodo.19868835 still has the old column names. Premature neuter (emptying the dict) is deferred — possibly indefinitely — until the v2.7.0 deposit is no longer in common use.

**Alternatives considered:**

1. **Empty the dict post-v2.8 (the prior framing).** DECISION_LOG 2026-05-12T03:25Z DO-plan step 10 said: "Update `shared/helpers/canonical_join_keys.py` in the monorepo: `NATALITY_TO_CANONICAL` becomes empty dict + deprecation note." Pro: visible deprecation; the helper becomes a true passthrough. Con: breaks any code that reads the v2.7.0 Zenodo parquet through the helper expecting the rename to happen. The v2.7.0 deposit is immutable and remains the canonical citable artifact until Task 10 deposits v2.8.0.

2. **Retain dict + add docstring deprecation note (chosen).** Helper continues to work for both v2.7.0 and v2.8.0+ input. Joint-use code that should be version-agnostic keeps calling `to_canonical_natality()` (no-op for v2.8, full rename for v2.7.0). Cost: minor cognitive overhead (the helper "always works" framing requires the docstring to explain why); benefit: zero breakage risk for any current consumer.

3. **Remove the helper entirely.** Aggressive but unnecessary. The helper is small (~50 lines) and the cost of keeping it is near-zero. Premature.

**Reason:** Forward-looking HALT 4 in STATUS 2026-05-12T05:10Z and 06:30Z both flagged premature neuter as risky for v2.7.0 backward-compat. This session's empirical confirmation (re-running both monorepo notebooks against v2.8 parquets and observing the helper's empty-rename-map behavior) verified that the v2.8 path is unchanged whether the dict is populated or empty (no rename needed when input columns are already canonical). The v2.7.0 path REQUIRES the dict populated. Choice 2 dominates choice 1 on both safety and operational simplicity.

**Source:**
- Smoke-test inline at commit `5174552`: `python3 -c "from shared.helpers.canonical_join_keys import to_canonical_natality, NATALITY_TO_CANONICAL; df = pd.DataFrame({'data_year':[2020], 'residence_status':[1]}); out = to_canonical_natality(df); print(list(out.columns))"` returned `['data_year', 'residence_status']` (no rename); v2.7.0 input columns `['year', 'restatus']` renamed to `['data_year', 'residence_status']`. Dual-path verified.
- `paper_companion_results.csv` byte-identical to prior v2.7.0 commit after rebuilding both monorepo notebooks against v2.8 parquets (commit `a6b3d36`). The end-to-end value preservation gives high confidence that the helper's dual-path behavior is correct.

**Verifiable by:**
- The 5-line smoke-test above; reproducible at any time.
- `git diff shared/helpers/canonical_join_keys.py` at commit `5174552`: dict content unchanged; only docstring updated.

**Reversible:** yes — emptying the dict is a one-line edit at a future task (e.g., when the v2.7.0 deposit is migrated or formally deprecated). Recorded here so the future-empty task can cite this entry as the prior-state justification.

**Residual risks:**
- (a) Some user code might check `if NATALITY_TO_CANONICAL: ... ` as a sentinel that the rename is "needed"; that pattern would silently always-rename even on v2.8 input. Mitigation: `to_canonical_natality()` does the right thing in both cases (it's the wrapper that filters by input columns), and the docstring directs callers to use the wrapper, not to introspect the dict.
- (b) When the v2.7.0 Zenodo deposit is eventually superseded (Task 10 deposits v2.8.0), this retention will outlive its useful life. A future task should re-evaluate.

---

## 2026-05-12T04:30:00Z — task7_v3b_doc_hunt — KICKOFF Step 0 V3b doc retry succeeded; proposing Task 7 scope expansion to 1982-2022 (41 years)

**Choice (proposal pending user confirmation):** Expand Task 7 scope from the prior session's "V3a only (1989-1991, 34 years total)" framing back to "V3a + V3b (1982-2022, 41 years total)" per KICKOFF.md Step 0 contingency ("If V3b authoritative docs found → expand Task 7 scope to 1982-2022 and proceed with V3a + V3b"). Step 0 found all 10 fetal-death user guides 1982-1991 obtainable from NCHS canonical FTP path `https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/fetaldeath/<YYYY>FetalUserGuide.pdf` (all HTTP 200; sizes/last-modified per STATUS 2026-05-12T04:30Z). The proposal is NOT yet authorized — it requires explicit user yes before Task 7 PRE-FLIGHT begins downloading the PDFs to the build dir.

**Alternatives considered:**

1. **Keep prior session's V3a-only scope** (1989-1991, 34 years; V3b deferred post-submission). Pro: shorter Task 7 budget (~1 session, not ~4-5); ships a strict superset of the current 31-year coverage; preserves integrity-principle simplicity. Con: leaves 7 years on the table that authoritative sources now confirm are accessible; the manuscript would cite 34 years with a post-submission v1.2 promise to extend, instead of citing the final 41-year extent.

2. **Expand to V3a + V3b (1982-2022, 41 years) — proposed.** Pro: maximum-extent paper coverage from first submission; cited DOI is final not incremental; the integrity principle is SATisfied because authoritative NCHS PDFs anchor V3b layout reconstruction (NOT reverse engineering). Con: +3-4 sessions of effort vs V3a-only; OCR pass required on bitmap-scanned 1980s PDFs (NCHS-published but image-scanned); L13-extension value-distribution discipline must be applied per-field on the new V3b layouts.

3. **Hybrid: V3a + V3b 1988 only.** The Damian Clarke `fetl1988.dct` artifact (88 fields, 200-byte layout) plus the NCHS 1988 user guide is a single-year addition that minimizes OCR risk (1 PDF instead of 7). Adds +4 years total (1988-1991). Rejected as a stopping point — once OCR machinery exists for one year, the marginal cost of 6 more years is small; arbitrary cutoff at 1988 is unjustified.

**Reason:** Step 0 reversed the prior session's empirical assumption ("V3b docs not at NCHS"). Wrong-filename probes by the 2026-05-12T03:50Z agent (used `Fetal82UG.pdf`, `fetal_death_inst.pdf`, NCHS series_04 paths, etc.; did NOT try `<YYYY>FetalUserGuide.pdf` despite that being the exact convention used by 2003-2022 files already on disk in this monorepo). This session's WebFetch on `cdc.gov/nchs/data_access/vitalstatsonline.htm` surfaced the canonical NCHS link list including all 7 V3b years and verified by HEAD probe. Sanity download of 1985 confirmed valid PDF + SHA recorded. The integrity-principle objection in 2026-05-12T04:00Z STATUS ("can't claim 100% correct without authoritative codebook") no longer applies: authoritative codebooks exist and are obtainable.

**Source:**
- WebFetch result for `https://www.cdc.gov/nchs/data_access/vitalstatsonline.htm` showing per-year fetal-death documentation links 1982-1988.
- `curl -sI -k <YYYY>FetalUserGuide.pdf` returning HTTP 200 with valid content-length for all 10 years 1982-1991.
- `/tmp/v3b_hunt/1985FetalUserGuide.pdf` SHA-256 `f7342480302017caf622243510c7e32ea03b6083b9797768b59fa50954eb1ed5`; `file(1)` reports valid PDF v1.4.
- GitHub `damiancclarke/nchs-fetaldata` `process/dicts/fetl1988.dct` 7,412 bytes (cross-check artifact, not authoritative; Damian Clarke 2014-07-02 Version 0.0.0 empty README).
- KICKOFF.md Step 0 contingency clause (lines 47-55 of KICKOFF.md).

**Verifiable by:**
- This entry's HEAD probe results are repeatable via `curl -sI -k https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/fetaldeath/<YYYY>FetalUserGuide.pdf` for any year 1982-1991.
- The 1985 PDF SHA can be reproduced by `curl -s -k -o /tmp/check.pdf <url> && shasum -a 256 /tmp/check.pdf`.
- STATUS.md 2026-05-12T04:30Z section is the canonical current-state record.

**Reversible:** yes — if Task 7 V3b OCR proves intractable (e.g., the 1980s NCHS scan quality is too low for reliable layout-table OCR, or value-distribution verification surfaces unresolvable per-field semantics ambiguity), the user can direct a fall-back to V3a-only scope at Task 7 PRE-FLIGHT halt-and-ask moment. The proposal does not commit V3b irreversibly; it commits to *attempting* V3b with halt-condition discipline.

**Residual risks:**
- (a) **OCR quality on 2009-vintage NCHS bitmap scans is unknown.** Quality varies year-to-year (NCHS rescanned old paper docs in 2009-01-08 batch; some scans may be cleaner than others). Mitigation: a 20-min proof-of-concept OCR run on a few `1985FetalUserGuide.pdf` pages before committing to all 7 V3b years (was option 4 of this session's 4-option ask; user chose option 1 "update state files first").
- (b) **L13-extension discipline overhead per year**: 7 V3b years × (per-field value-distribution verification + layout-CSV reconstruction from OCR'd text) may grow Task 7 V3b beyond the 3-4 session estimate if multiple fields surface semantic mismatches like the MAGER vs MAGER41 incident in V2.1.
- (c) **Damian Clarke 1988.dct provenance gap**: the Clarke artifact's "Version 0.0.0" + empty README means it MAY itself be reverse-engineered or partially-incorrect. Treating it as a cross-check (not authority) preserves integrity; treating it as authority would be the L13-extension shape we explicitly avoid.
- (d) **Manuscript timing**: pre-submission scope was already expanded once (2026-05-11T20:50Z) and again (2026-05-12T03:30Z); this is the third expansion in 3 days. User has accepted the trade-off pattern of "more sessions for final manuscript state" — but the absolute session count keeps growing. If V3b OCR surfaces a multi-session blocker, the user has the option to fall back without re-litigating the data-first-vs-submit-now choice from scratch.

**Self-check (residual risks the VERIFY phase wouldn't catch):**
- This entry asserts "authoritative NCHS PDFs are obtainable" based on (i) HEAD probes returning HTTP 200, (ii) one sanity download verifying valid PDF + matching content-length. It does NOT verify the PDF's *content* is a usable codebook with readable byte-layout tables. The 1985 PDF is bitmap-scanned; if those scans are illegible or missing the layout-table appendix entirely (e.g., the PDF body is some unrelated NCHS report, not a public-use file codebook), this proposal's premise is wrong. Mitigation: Task 7 PRE-FLIGHT MUST include an L9 cheap-check (open one PDF, locate the byte-layout table by page) before downloading all 10 to the build dir and committing harmonization effort.
- The 200-byte record length for 1982-1988 is verified by the prior session's `unzip` + byte-inspection (STATUS 2026-05-12T03:50Z); the layout table in the user guide MUST sum to 200 bytes to be consistent with the actual public-use file. Bond verification at Task 7 PRE-FLIGHT L9 step.

---

## 2026-05-12T03:30:00Z — sequencing — Pull Task 7 (V3 1982-1991) and natality v2.8 rename INTO pre-submission scope

**Choice:** Override the prior "out of pre-submission scope" status (KICKOFF.md, DECISION_LOG 2026-05-11T20:50Z) for both Task 7 fetal-death V3 backward extension AND natality v2.8 column rename. Both will be completed before manuscript submission. New pre-submission sequence:

1. ~~Task 3 V2.1 fetal-death~~ DONE 2026-05-12 (`task3-complete` at `8ca5bf9`).
2. ~~Push monorepo to GitHub at v1.0~~ DONE 2026-05-12 (public repo at https://github.com/yoelplutchok/vital-statistics-harmonization, commit `a18ca3a`).
3. **Natality v2.8 column rename** (start NEXT session per parallel-paths choice; user downloads Task 7 inputs concurrently). ~2 sessions.
4. **Task 7 V3 fetal-death** (1982-1991, +10 years). 2-4 sessions; OCR risk on older user guides.
5. **Task 9 — redirect notices on the two old GitHub repos** (~15-30 min, human-driven).
6. **Task 10 — Unified Zenodo deposit** + v2.1.0 patch to old fetal-death deposit (1 session + upload time).
7. **Push v1.1 to GitHub** (replaces current v1.0 contents; cleanly amended single-commit history not preserved — incremental release).
8. **Manuscript re-pass + submit** (~½ session).

**Alternatives considered:**

1. **Keep prior sequence (Task 7 + natality v2.8 post-submission).** Original NEXT_STEPS.md §17 + KICKOFF.md "out of scope" framing. Pro: shortest path to submission. Con: per the human's preference, the manuscript would cite a 31-year fetal-death series + v2.7.0 natality, then require v3-extended fetal-death + v2.8-renamed natality in a follow-up correction. Pre-emptively doing them before submission means the paper goes out at the latest data state.

2. **Pull Task 7 + natality v2.8 + extend further (chosen).** Pre-submission scope grows by 3-5 sessions. Pro: manuscript ships at maximum-coverage state (41 years fetal-death; aligned natality column names). Con: 3-5 more sessions of work before submission.

**Reason:** Same as DECISION_LOG 2026-05-11T20:50Z (data-first sequencing) but with maximum-extent target instead of minimum-viable. The marginal session-cost of Task 7 + v2.8 (3-5 sessions) is justified by the manuscript-once-and-final outcome. User explicitly authorized.

**Source:** Chat 2026-05-12 between commits `8ca5bf9` (Task 3 V2.1 complete) and `a18ca3a` (public repo push) and this entry. User explicit confirmation of override + parallel-paths sequencing.

**Verifiable by:**
- This DECISION_LOG entry timestamp 2026-05-12T03:30:00Z supersedes 2026-05-11T20:50Z's pre-submission scope listing.
- Future sessions reading STATUS.md + this DECISION_LOG see natality v2.8 as next task; Task 7 follows once 1982-1991 NCHS inputs are downloaded.

**Reversible:** yes — if Task 7 hits a multi-session blocker (e.g., NCHS 1982-1991 user guides only available as scanned/OCR-resistant PDFs), the human can direct a fall-back to submitting at the post-V3-attempt state with Task 7 explicitly deferred again.

**Residual risks:**
- (a) **Task 7 input availability**: PRE-FLIGHT this session showed ZERO 1982-1991 zips or user guides on disk. User has been asked to download from NCHS FTP path `ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/fetal-deaths/`. Some older-year files may not be in the standard public-use FTP path — verification required.
- (b) **Natality v2.8 scope larger than initial estimate**: PRE-FLIGHT shows 61 string-literal column-name references across natality scripts + 4 schema rows + 6 docs + 2 parquets to re-derive + 183 NVSR validation targets to re-gate. Estimated 2 sessions, not 1.
- (c) **Cross-product effects of natality v2.8 rename**: monorepo's `shared/helpers/canonical_join_keys.py` aliasing helper becomes a no-op after v2.8. monorepo's `notebooks/joint_use_demo.ipynb` and `paper_companion.ipynb` use the aliasing helper; they should continue to work (helper still imports, just renames are no-ops). Re-run both notebooks after v2.8 to verify.
- (d) **v1.0 public repo is now slightly stale**: pushed at Task 3 V2.1 state, will be superseded by v1.1 (post-Task-7 + post-v2.8). No external pulls expected in the brief window; acceptable.

---

## 2026-05-12T03:25:00Z — natality_v28_rename — PRE-FLIGHT findings: 61-string-literal rename surface (Field-value snapshot per Convention 3)

**Pre-flight result:** PROCEED to next session DO. No halt conditions. Inputs all available (natality build dir intact at v2.7.0; aliasing helper documents exact renames).

**Field-value snapshot — current state of canonical artifacts that v2.8 will mutate:**

| Artifact | Current (v2.7.0) | Target (v2.8) |
|---|---|---|
| `metadata/harmonized_schema.csv` row 1 | `year,Birth year,int16,...` | `data_year,Data year,int16,...` |
| `metadata/harmonized_schema.csv` row 2 | `restatus,Resident status (NCHS),int8,...` | `residence_status,Residence status,int8,...` |
| `metadata/harmonized_schema.csv` row N | `maternal_hispanic_origin,...` | `hispanic_origin,...` |
| `metadata/harmonized_schema.csv` row M | `maternal_race_bridged4,...` | `maternal_race_bridged,...` |
| natality parquets | columns named `year`, `restatus`, `maternal_hispanic_origin`, `maternal_race_bridged4` | renamed to canonical names |
| `shared/helpers/canonical_join_keys.py` `NATALITY_TO_CANONICAL` dict | 4 explicit renames at read time | EITHER no-op (empty dict) OR full removal with helper deprecation notice |

**String-literal reference counts (the edit surface, scoped to natality build dir scripts/metadata/docs):**

- `"year"` / `'year'`: 48 references (most string-literal column-name uses; some may be `df.groupby("year")` style; many are validation filter expressions like `mask = subset["year"] == y`)
- `"restatus"` / `'restatus'`: 3 references
- `"maternal_race_bridged4"` / `'maternal_race_bridged4'`: 6 references
- `"maternal_hispanic_origin"` / `'maternal_hispanic_origin'`: 4 references
- Total: **61 string-literal references**

**Files touching these columns (per `grep -rln`):**

| Layer | Files |
|---|---|
| Schema | `metadata/harmonized_schema.csv`, `metadata/external_validation_targets_v1.csv` |
| Harmonize | `scripts/03_harmonize/harmonize_v1_core.py`, `scripts/03_harmonize/harmonize_linked_v3.py` |
| Validate | `scripts/05_validate/qa_yearly_core_parquet.py`, `validate_row_counts_vs_nchs.py`, `harmonized_missingness.py`, `key_rates_from_derived_core.py`, `compare_external_targets_v3_linked.py`, `compare_external_targets_v1.py`, `validate_linked_parquets.py`, `validate_v1_invariants.py` |
| Convenience | `scripts/06_convenience/write_residents_only.py` |
| Figures | `scripts/07_figures/generate_paper_figures.py` |
| Docs | `docs/CODEBOOK.md`, `docs/COMPARABILITY.md`, `docs/FAQ.md`, `docs/ABOUT_THIS_RELEASE.md`, `docs/GETTING_STARTED.md`, `docs/VALIDATION.md` |
| Import (linked) | `scripts/01_import/parse_linked_cohort_year.py`, `scripts/01_import/README.md` |

**DO-phase plan:**

1. Edit `metadata/harmonized_schema.csv`: rename 4 rows. Verify schema-version bump (v2.7.0 → v2.8.0) annotated.
2. Edit `scripts/03_harmonize/harmonize_v1_core.py`: rename column-write string literals.
3. Edit `scripts/03_harmonize/harmonize_linked_v3.py`: same.
4. Re-derive `natality_v2_harmonized_derived.parquet` + `natality_v3_linked_harmonized_derived.parquet`.
5. Verify column names in resulting parquets (should be `data_year`, `residence_status`, `maternal_race_bridged`, `hispanic_origin`).
6. Edit 5 validate scripts + 2 misc scripts + 1 import script: rename column-read string literals.
7. Run 183 NVSR validation targets; gate 183/183 byte-exact.
8. Run linked-file validation; gate 33/35 + 2 differ-by-1.
9. Edit 6 docs (CODEBOOK, COMPARABILITY, FAQ, ABOUT_THIS_RELEASE, GETTING_STARTED, VALIDATION) to use new column names.
10. Update `shared/helpers/canonical_join_keys.py` in the monorepo: `NATALITY_TO_CANONICAL` becomes empty dict + deprecation note; the helper continues to import for backward compatibility but is a no-op for natality v2.8.
11. Re-run `notebooks/joint_use_demo.ipynb` + `notebooks/paper_companion.ipynb` against the v2.8 natality parquet to verify cross-product joins still work.
12. Sync renamed files to monorepo's `natality/` subdirectory.
13. Bump version: `CITATION.cff` 2.7.0 → 2.8.0; new Zenodo deposit (since v2.8 is a breaking change; v2.7.0 stays at its DOI for backward compatibility).
14. Write RECEIPT + FIX_LOG + DECISION_LOG entries.

**Forward-looking HALTs for the DO session:**

1. Some "year" references in scripts may be LOCAL VARIABLES, not column-name string literals. The rename must distinguish `df["year"]` (rename target) from `for year in range(...)` (untouched). Use targeted sed patterns like `s|"year"|"data_year"|g` and `s|'year'|'data_year'|g` only — not bare-word replacement.

2. `external_validation_targets_v1.csv` may have "year" as a column header. Inspect before editing; the V1 validation target CSV is canonical state.

3. The downstream user's local projects (multiple-gestation-linked-imr, lbw-imr-divergence per DECISION_LOG 2026-05-11T18:06:12Z) will break on v2.8 — they hard-code `df["year"]` etc. A separate compatibility task to update those projects is OUT OF SCOPE for natality v2.8 itself; flag for the user.

4. The aliasing helper currently maps 4 names. After v2.8, natality natively has the canonical names. The helper's `NATALITY_TO_CANONICAL` dict should be empty `{}` (so `to_canonical_natality(df)` becomes a passthrough). Verify nothing breaks at the call sites.

5. Re-deriving natality parquet takes ~5-10 minutes on the v2.7.0 build laptop. Budget accordingly.

---

## 2026-05-12T01:35:00Z — task3_v21_fetal_death — Bundle 4 fixes into Task 3 V2.1 build (B7 + H8 + data_year + monorepo path drift)

**Choice:** Land the following four orthogonal fixes inside a single Task 3 V2.1 build, producing one new shipped artifact pair (`fetal_death_harmonized.parquet` sha=`333e1e66…d9e0`, `fetal_death_derived.parquet` sha=`55d3d310…c447`) and one set of canonical-state log entries:

1. **B7 TABFLG normalization** for 2003/2004 — NCHS-errata correction per `fetaldeath0304problems.pdf` (records with COMBGEST=99 and OSTATE in 43-state list set TABFLG=2; raises per-year resident totals from 25,653/25,655 originally-reported to 26,004/26,001 corrected, byte-exact against the errata's Table 1).
2. **H8 schema-vs-data dtype reconciliation** — five demographic/filter columns cast from `object` to nullable Int (`tabulation_flag` Int8, `residence_status` Int8, `maternal_age` Int16, `maternal_race_bridged` Int8, `hispanic_origin` Int8), matching the schema CSV and the natality v2.7.0 dtype convention; closes FIX_LOG 2026-05-11T18:50:00Z.
3. **`data_year` derived-column fix** — surfaced when the V2 validator returned 0/23 after H8: the harmonize loop's field-map iteration was overwriting the int32 `data_year` initialization with empty-string `object` because the crosswalk row for `data_year` has `field_2006="derived"` which falls through to the loop's else-branch. Added `if raw_field == "derived": continue` to skip derived-marker rows.
4. **Monorepo path drift in `harmonize.py` + `validate_external*.py`** — pre-existing from monorepo migration `7fd9cdf`; scripts assumed `fetal_death/metadata/` subdir but the monorepo flattened the layout. Re-pointed `_CROSSWALK_CSV`/`_SCHEMA_CSV`/`_HARM_PATH`/etc. to the actual paths.

**Alternatives considered:**

1. **Land each fix as a separate task** (B7 → task3a, H8 → task3b, data_year → task3c, paths → task3d). Cleaner per-task scope; one parquet rebuild per fix. Cost: 4 parquet rebuilds, 4 separate receipts, 4 separate Zenodo deposit considerations. Rejected — H8/data_year/paths are LATENT bugs surfaced as a consequence of running Task 3's re-derive; treating them as separate tasks is artificial, and re-deriving the parquet four times burns reproducibility-budget for no extra information.
2. **Land B7 only; defer H8/data_year/paths to post-submission** (chosen-not). Pro: keeps Task 3 scope tight. Con: V2.1 ships with a known H8 dtype defect AND a latent data_year bug that would re-surface when downstream code starts using the int-comparison path; manuscript references the v2.1.0 parquet with two known issues that would need a v2.1.1 correction. Rejected.
3. **Land all four fixes bundled into one V2.1 build (chosen).** Pro: one parquet, one receipt, one deposit-version, transparent V2.1 release notes covering everything that changed. Con: receipt is denser; Task 3 effort exceeded the 1–2 session estimate. The receipt names all four orthogonally; downstream readers can trace each.

**Reason:** All four fixes converge on the same parquet rebuild. B7 requires harmonize.py edit and re-derive. H8 requires harmonize.py edit and re-derive. data_year bug surfaces during H8 re-derive (the validator failure exposes it). Path drift blocks all of the above from running at all. Bundling is the natural unit. Convention 1 (SHAPE-not-VALUE) is preserved — no SMOKE harnesses pin v2.0.0-specific values that V2.1 changes.

**Source:**
- `FIX_LOG.md` entries 2026-05-12T01:30:00Z (three new entries: H8 closure, data_year, monorepo path drift).
- `fetal_death/V2_1_2003_2004_LAYOUT_DECISIONS.md` (new).
- `raw_docs/fetal_death/fetaldeath0304problems.pdf` page 1 + Tables 2–3 (for B7).
- `raw_docs/fetal_death/2003FetalUserGuide.pdf` pages 17–19 (for the MAGER41-vs-MAGER discovery).

**Verifiable by:**
- `validate_external.py` 55/55 + `validate_external_v2.py` 23/23 = 78/78 byte-exact pass.
- joint_use_demo: 8/8 NVSR Table-4 age-band cells byte-exact for 2022.
- paper_companion: 34/34 PASS, 0 FAIL.

**Reversible:** yes — `git reset --hard task3-pre-do` reverts; v2.0.0 parquet preserved at `/Users/yoelplutchok/Desktop/fetal-death-harmonization/fetal_death_derived.parquet` (sha `90af89b9…`) for byte-clean baseline comparison.

**Residual risks (Self-check feed):**
- (a) **`record_layout_2003/2004.csv` documentation imprecisions** (inherited from 2006 with anchor-field spot-checks; surfaced semantic mismatch at MAGER vs MAGER41 plus several BLANK-vs-actual-field documentation errors). The harmonized parquet is correct (because parser-read positions for fields the harmonizer reads ARE correct, or read-all-blank which is correct behavior); only the layout CSVs need a post-submission audit-rebuild. Documented in `V2_1_2003_2004_LAYOUT_DECISIONS.md`.
- (b) **V1-era byte-clean column-level regression not exhaustively verified.** The V1 validator passed 55/55 (functional verification), but a column-by-column SHA comparison of the 2005–2022 slice of the new derived parquet vs v2.0.0's `90af89b9…` derived parquet was NOT performed this session. The 5 H8 columns are expected to change (string→int); all other 84 columns should be byte-identical. Forward-looking HALT in receipt.
- (c) **maternal_age=null for 2003+2004 may surprise downstream users** unaware that the 2003+2004 public-use files don't ship single-year-of-age. Documented in V2_1_DECISIONS doc and in the JOINT_USE_GUIDE dtype note.
- (d) **Other monorepo scripts may have latent path drift** (parse_fetal_year.py, derive.py, run_pipeline.py, tests/conftest.py). Not touched this session; flagged in FIX_LOG 2026-05-12T01:30:00Z forward-looking follow-up.

---

## 2026-05-11T20:50:00Z — sequencing — Data-first before manuscript submission (Task 3 → push GitHub → Task 9 → Task 10 → manuscript re-pass + submit)

**Choice:** Run the remaining data-side work (Task 3 V2.1 fetal-death with bundled H8 reconciliation) and the cross-product publication tasks (push GitHub, Task 9 redirect notices, Task 10 unified Zenodo) BEFORE manuscript submission, so the manuscript cites the latest fetal-death coverage and the unified Zenodo concept DOI from the first submitted version rather than the two old subproject DOIs.

**Alternatives considered:**
1. **Submit now, do data work later (submit-first).** Three pre-submission process tasks: YP admin review, GitHub push + URL injection, IJE reference reformat. Then submit at v2.0 fetal-death (29 years, with 2003–2004 gap) citing concept DOIs 10.5281/zenodo.19363074 + 10.5281/zenodo.20031571. Pros: fastest path to submission; ½ session. Cons: the paper goes out reporting a 2-year gap and the two old DOIs; a follow-up correction or v2.1 release update would be needed within weeks; the manuscript's headline numbers (1,634,195 fetal deaths; Table 1 fetal-death row count = 3; validation counts 29/29 + 26/26) become stale on a planned schedule.
2. **Data-first sequence: Task 3 → push GitHub → Task 9 → Task 10 → manuscript re-pass + submit (chosen).** Run Task 3 (V2.1 fetal-death; bundles H8 schema-doc reconciliation), push the monorepo to GitHub, do Task 9 redirect notices, set up the unified Zenodo deposit with DOI pre-reservation, then a half-session manuscript re-pass to update affected numbers (fetal-death record count ~1.6M → ~1.7M; Table 1 rows; validation counts 31/31 + 28/28), inject the unified DOI and GitHub URL, resolve the three `<!-- YP: review -->` admin-section markers, and reformat references. Pros: paper is published at the latest data state; cites the unified DOI from day one; H8 dtype fix-up rides for free in the Task 3 parquet re-derivation. Cons: 4–6 session delay before submission; Task 3 has known unknowns (2003 + 2004 transition-layout reconstruction from NCHS user guides — `fetaldeath0304problems.pdf` is the documented source for the known ambiguities).
3. **Maximum-extent: also do Task 7 V3 backward extension to 1982 pre-submission.** Adds 1982–1991 fetal-death (1978-revision + early 1989-revision). Pros: longest paper coverage. Cons: explicitly post-submission per `NEXT_STEPS.md` §17; 2–4 sessions; OCR risk on older user-guide PDFs; the marginal scientific value over the V2.1 state is incremental. Rejected as scope creep.
4. **Maximum-extent: also do natality v2.8 column rename pre-submission.** Renames `year` → `data_year`, `restatus` → `residence_status`, etc., so the aliasing helper becomes a no-op deprecation. Pros: cleaner namespace alignment. Cons: breaking change for downstream natality-only users (the `multiple-gestation-linked-imr` and `lbw-imr-divergence` projects on the human's Desktop); requires re-running 183 NVSR validation targets + new natality Zenodo deposit; the paper's Methods section already documents the cross-product alignment via the aligned shared concepts (`maternal_age`, `maternal_race_bridged`, `hispanic_origin`, `data_year`, `residence_status` per the manuscript), so deferring the rename does not cost the paper a claim. Rejected as scope creep + breaking-change risk.

**Reason:** The Data Resource Profile genre rewards "publish at the latest data state" and the IJE editorial expectation is that a Data Resource Profile cites the unified resource DOI in the manuscript. Submitting at v2.0 fetal-death (29-year coverage) and v2.1-correcting weeks later costs more author and editor time than a 4–6 session pre-submission data push. Task 3 is rated "ideally pre-submission, not blocking" by `NEXT_STEPS.md` §17 — the §17 framing was conservative; the human's preference to upgrade it to "do before submission" is consistent with the underlying intent. Task 7 and natality v2.8 are explicitly post-submission and remain so.

**Source:** Chat transcript 2026-05-11 between Task 5 commit `9aaa702` (20:30Z) and this DECISION_LOG entry (20:50Z); human's explicit confirmation of the sequence after LLM presented the trade-off summary. `KICKOFF.md` "Current planned sequence" block; STATUS.md 2026-05-11T20:50:00Z section.

**Verifiable by:**
- `KICKOFF.md` contains the "Current planned sequence" section listing the 5-step order (Task 3 → push → Task 9 → Task 10 → re-pass + submit).
- `STATUS.md` most-recent section is dated 2026-05-11T20:50:00Z and supersedes the Task 5 entry's "Next planned task: Pre-submission process pass by default" line.
- Future sessions reading KICKOFF.md and STATUS.md will propose Task 3 as the next task by default; the (a)-(d) handshake's (c) "what you propose to do this session" should name Task 3 PRE-FLIGHT unless the human directs otherwise.

**Reversible:** yes. If Task 3 hits a multi-session blocker (e.g., a 2003-revision layout ambiguity that NCHS docs don't resolve), the human can direct a fall-back to the submit-first sequence (alternative 1 above) without needing a new DECISION_LOG entry — just halt Task 3 at the blocked PRE-FLIGHT and pivot.

**Residual risks:**
- (a) Task 3 effort estimate (1–2 sessions) could grow if the 2003 + 2004 transition-layout reconstruction hits ambiguities. The human has implicit budget tolerance for this per the data-first choice; explicit budget reset would be a halt-and-ask moment.
- (b) The manuscript re-pass in step 5 is a paper-side ripple effect; if the journal's IJE author guidelines change in the intervening 4–6 sessions, the re-pass scope grows. Mitigation: low-probability over a multi-week window.
- (c) Cross-pollination between Task 3 (data-side change) and the manuscript edits (Task 5's body) is unavoidable. Task 4's HALT 5 already documents this: any manuscript edit re-runs `_build_paper_companion.py` to detect new/changed claims; Task 3's effect on the manuscript means the synthesis CSV WILL change (currently bit-stable at `7891809c...`).

---

## 2026-05-11T20:30:00Z — task5_manuscript_trim — Override Task 4's C47/C48/C49 L11 recommendation (Task 4 misdiagnosis)

**Choice:** Do NOT apply Task 4's recommended precision edit for C47/C48/C49 (line 104 of `paper/draft_v2_hmd_styled.md`). Keep the manuscript wording for `maternal_education`, `paternal_age_combined`, and `maternal_education_unrevised` exactly as-is.

**Alternatives considered:**
1. **Apply Task 4's recommended edit** — rewrite line 104 to clarify that the italicised names are "raw NCHS field names" rather than harmonized columns. Task 4's PRE-FLIGHT and receipt explicitly recommended this as a Task 5 input.
2. **Override and keep manuscript as-is (chosen).** Direct verification at Task 5 PRE-FLIGHT shows that the italicised names ARE fetal-death harmonized column names per `fetal_death/harmonized_schema.csv` lines 17 (`maternal_education`, years_available `2005-2006, 2014-2022`), 18 (`maternal_education_unrevised`, years_available `1992-2002, 2005-2006`), and 21 (`paternal_age_combined`, years_available `1992-2002, 2005-2006, 2014-2022`). Direct null-rate verification on `fetal_death_derived.parquet` (sha=`90af89b9...`) shows 100% blank for all three columns in 2007–2013 — matching the manuscript's claim byte-exact. The italicization convention is consistent with line 60's `breech_unrevised` / `delivery_place_unrevised` / `maternal_race_bridged_detail` (italics = harmonized column names throughout the manuscript). The manuscript wording at line 104 is correct and self-consistent; no edit is warranted.
3. **Hybrid: keep wording but add a clarifying footnote naming the underlying raw NCHS fields (MEDUC, FAGECOMB, MEDUC).** Considered; rejected as scope creep — the harmonized column / raw-field correspondence is documented in `fetal_death/harmonized_schema.csv` already, and adding a manuscript-level footnote duplicates the schema CSV without adding clarity.

**Reason:** Task 4's PRE-FLIGHT and DO phase checked the NATALITY parquet (`natality_v2_harmonized_derived.parquet`) for these three column names. The natality parquet has different harmonized column names for the same conceptual fields: `maternal_education_cat4` (a 4-category derivation) rather than `maternal_education`; `father_age` (single-year) rather than `paternal_age_combined`; and no equivalent of `maternal_education_unrevised`. Task 4 received "columns not found" from the natality parquet and interpreted the manuscript's italicised names as raw NCHS field names. The fetal-death parquet was not checked. Task 5 PRE-FLIGHT re-verification reads the fetal-death schema CSV and parquet directly and finds the manuscript wording byte-exact correct. This is a Task 4 receipt Self-check item 4 outcome: the receipt explicitly flagged "if the manuscript actually means harmonized columns, then C47–C49 are DIFFs… the latter scenario is plausible — recommend Task 5 author verify which framing was intended" — Task 5 carried out that verification and found the harmonized-columns framing is the correct one.

**Source:**
- `PRE_FLIGHT_LOG.md` 2026-05-11T20:05:00Z (Field-value snapshot, "5 precision-edit candidates from Task 4 — PRE-FLIGHT re-verification" table, C47/C48/C49 row).
- `fetal_death/harmonized_schema.csv` lines 17, 18, 21 (authoritative declaration of harmonized column names + years_available).
- Direct fetal-death parquet null-rate verification (PRE-FLIGHT bash output 2026-05-11T20:00Z): `maternal_education` 100% blank 2007-2013; `paternal_age_combined` 100% blank 2007-2013; `maternal_education_unrevised` 100% blank from V1 2007 onward.
- `RECEIPTS/task4_paper_companion_2026-05-11T19-26-28Z.md` Self-check item 4 (Task 4's own flag that this could be a misdiagnosis).

**Verifiable by:**
- `grep -n "^maternal_education,\|^maternal_education_unrevised,\|^paternal_age_combined," fetal_death/harmonized_schema.csv` returns three rows matching the years_available pattern above.
- A re-run of `python notebooks/_build_paper_companion.py` against an unchanged fetal-death parquet emits 100.00% blank rates for 2007-2013 in C47/C48/C49 cells, matching the manuscript.

**Reversible:** yes — if the IJE author or peer reviewer requests the clarification anyway, the Hybrid alternative (a footnote naming the underlying raw fields) is a one-line addition.

**Residual risks:**
- (a) A reader who is unfamiliar with the harmonization may parse line 104's `maternal_education` as the natality harmonized column (which has a different name) and conclude there is a manuscript-data mismatch. Mitigation: the schema CSV (shipped) is the canonical disambiguation; a future precision pass could add an explicit `(fetal-death harmonized columns)` parenthetical, but this is sub-precision-edit not L6 risk.
- (b) The Task 4 receipt's Forward-looking HALT 1 names C47/C48/C49 as a Task 5 input; future receipt-readers tracing the HALT chain should consult this entry to see the override rationale.
- (c) The C47/C48/C49 rows in `notebooks/paper_companion_results.csv` continue to show `status=L11` because the builder is data-driven (it doesn't read the manuscript line text); the L11 flag is informational not regression. A future refactor of `_build_paper_companion.py` could either fix the C47-C49 check logic to look at the fetal-death parquet rather than expect a hardcoded comparison, or update the synthesis-row status to reflect the Task 5 override. Not done in Task 5 to keep scope tight.

---

## 2026-05-11T19:26:28Z — task4_paper_companion — Re-defer Section B 2017 race-stratified NVSR validation (originally Task 2 → Task 4 absorption)

**Choice:** Re-defer the Section B 2017 race-stratified NVSR cell-level validation that §15 Task 4 (current state at `89ddc77`) names as an absorption from Task 2. Task 4 produces no race-stratified 2017 NVSR cells. The absorption becomes a separate small future task with explicit NVSR-2017 fetal-mortality PDF input.

**Alternatives considered:**
1. **Absorb Section B into Task 4 as §15 currently directs.** Would require: (a) locating the 2017-vintage NVSR fetal-mortality report PDF (likely NVSR 67-?); (b) transcribing 4 race-stratified rows into `fetal_death/external_validation_targets.csv`; (c) adding a verification cell to either `joint_use_demo.ipynb` or `paper_companion.ipynb` that reproduces each cell against the parquet. Cost: one short session if PDF is at hand; L9 risk on table/page citation.
2. **Re-defer with explicit reasoning (chosen).** The original Task 2 deferral cited the same L9 risk. The manuscript itself makes no race-stratified-2017 NVSR claim (line 94's validation claims are aggregate-level), so `paper_companion.ipynb`'s "reproduce every numeric claim in the manuscript" scope is complete without it.
3. **Hybrid: defer the NVSR validation but add a structural sanity check in the notebook** (e.g., assert race-stratified counts sum to the unstratified 2017 = 22,827 from external_validation_targets.csv). Task 2's notebook already does this cross-check (Section B's CSV-vs-direct-natality-recompute consistency check); duplicating it in `paper_companion.ipynb` would be redundant.

**Reason:** Convention 3 second bullet directs the PRE-FLIGHT to surface divergence between §15 spec and the task's available source-of-truth state, and to resolve at the cheap-check moment rather than silently proceeding. `fetal_death/external_validation_targets.csv` ships NO 2017 race-stratified targets (verified at PRE-FLIGHT by metric enumeration: 26 distinct metrics, none race-keyed). The L9 cheap-check therefore concludes that absorbing Section B would require fresh PDF transcription with the same risk profile that motivated Task 2's deferral. Re-deferring keeps Task 4 focused on its primary scope (reproduce manuscript numeric claims, which does not require race-stratified-2017 NVSR cells) and isolates the PDF-transcription work into a separate task where the L9 cheap-check can be done explicitly with the PDF in hand.

**Source:** `PRE_FLIGHT_LOG.md` 2026-05-11T19:15:00Z (Field-value snapshot, "Plan assumption amended at PRE-FLIGHT" section, item 1). `RECEIPTS/task4_paper_companion_2026-05-11T19-26-28Z.md` (Forward-looking HALT 3).

**Verifiable by:**
- `grep -i "race\|maternal_race" fetal_death/external_validation_targets.csv` returns zero hits (no race-stratified targets pre-encoded).
- Task 4's `paper_companion.ipynb` synthesis CSV contains no rows whose `claim` mentions "2017 race"; the 50 claim tags cover only manuscript-stated numeric claims.
- The manuscript's line 94 NVSR-validation claims are aggregate-level (183/183, 33/35+2, 29/29 counts + 26/26 rates); none are race-stratified-2017.

**Reversible:** yes — adding the absorption is additive (new rows in `external_validation_targets.csv` + new notebook cells). The original Task 2 deferral and this re-deferral can both be reversed in a single future session if the PDF is located.

**Residual risks:**
- (a) A reader of `NEXT_STEPS.md` §15 Task 4 may expect the absorption to be present in `paper_companion.ipynb` and be surprised by its absence. Mitigation: the receipt's Forward-looking HALT 3 and Self-check item 6 both flag this; the notebook's intro markdown cell explicitly names the deferral as out-of-scope.
- (b) The manuscript might later be edited (Task 5) to ADD a race-stratified-2017 validation claim, at which point Task 4's "reproduce every numeric claim" status would become stale. Mitigation: receipt Forward-looking HALT 5 says any future edit to `paper/draft_v2_hmd_styled.md` should re-run `python notebooks/_build_paper_companion.py` to surface new claims; the CSV `notebooks/paper_companion_results.csv` is the bit-stable check.
- (c) §15 Task 4's description currently names the absorption as in-scope. A `[plan-update]` could reword §15 Task 4 to mention the re-deferral; not done as part of Task 4 itself to avoid scope creep (similar to Task 2's stale-§15-wording handling).

---

## 2026-05-11T18:06:12Z — task1_joint_use_denominators — Aliasing-helper vs source-schema-rename for cross-product join keys

**Choice:** Reconcile cross-product join-key column-name divergence (`year`↔`data_year`, `restatus`↔`residence_status`, `maternal_race_bridged4`↔`maternal_race_bridged`, `maternal_hispanic_origin`↔`hispanic_origin`) via a read-time aliasing helper at `shared/helpers/canonical_join_keys.py`. The natality v2.7.0 Zenodo deposit's shipped schema is NOT mutated; the helper renames at the joint-use code boundary. Output `fetal_death/stratified_denominators.csv` uses the canonical (fetal_death-style) names.

**Alternatives considered:**
1. **Rename columns in the natality schema** (bump to v2.8 with `year` → `data_year`, etc.) and re-derive the parquet. Cleaner long-term, but: (a) requires re-running 183 NVSR validation targets; (b) breaks downstream user code that imports natality by its current names (e.g., `multiple-gestation-linked-imr` and `lbw-imr-divergence` projects on the user's Desktop); (c) requires a new Zenodo deposit (v2.7.0 stays immutable at its DOI); (d) needs a coordinated bump of `paper/draft_v2_hmd_styled.md` references.
2. **Use the aliasing helper as a stopgap, keep both shipped schemas as-is** (chosen). Pros: ships the joint-use convenience layer today; preserves Zenodo deposit immutability; no breaking change to natality users; isolates the cross-product reconciliation in one auditable place. Cons: future joint-use code must import the helper; the docs must document the divergence (now done in `docs/JOINT_USE_GUIDE.md`).
3. **Build Task 1 against natality-native names; ship the output with fetal_death-style names; defer documentation/helper to later**. Functionally similar to choice 2 but loses the unified-namespace clarity at the helper boundary — joint-use code would each need to know the rename rules locally.

**Reason:** Task 1's purpose is to enable the manuscript's "designed for joint use" claim by producing a stratified denominator file. Choice 1 is the long-term right answer but is a multi-session task with a meaningful breaking-change surface. Choice 2 ships the deliverable today and isolates the cross-product reconciliation behind a single helper, keeping the breaking-change decision for natality v2.8 (or v3.0) as an independent future task. The Forward-looking HALTs in the Task 1 receipt explicitly propose this rename as a §11 plan-update candidate.

**Source:** PRE_FLIGHT_LOG.md 2026-05-11T17:50:48Z (Field-value snapshot of cross-product schema divergence). `shared/helpers/canonical_join_keys.py` (the helper); `docs/JOINT_USE_GUIDE.md` (user-facing docs explaining the choice and the namespace).

**Verifiable by:**
- `python -c "from shared.helpers.canonical_join_keys import NATALITY_TO_CANONICAL; print(NATALITY_TO_CANONICAL)"` should print exactly `{'year': 'data_year', 'restatus': 'residence_status', 'maternal_race_bridged4': 'maternal_race_bridged', 'maternal_hispanic_origin': 'hispanic_origin'}`.
- `shasum -a 256 fetal_death/stratified_denominators.csv` should produce `6874d5d65e7b3888acf8a833e4fa98063630765e2eeaf6e1c6cb48ad7b0db5c1` as long as natality v2.7.0 is the upstream input.
- Per-year sums in `stratified_denominators.csv` should match `external_validation_v1_comparison.csv` `resident_births` for all 29 years in 1992–2002 + 2005–2022.

**Reversible:** yes — `git reset --hard task1-pre-do` reverts the helper and the convenience file; the natality v2.7.0 deposit was never touched.

**Residual risks (Self-check feed from RECEIPTS/task1_joint_use_denominators_2026-05-11T18-06-12Z.md):**
- (a) The 1992–2002 era's `maternal_race_bridged4` in natality uses "approximate_pre2003" crosswalk per natality schema notes; fetal-death uses a different `harmonize.py` recode. Unverified whether they produce identical 4-category outputs on the same source MRACE codes. Joint stratified-by-race rates for 1992–2002 should be cross-checked as a Task 2 PRE-FLIGHT smoke.
- (b) Hispanic code 9 (Unknown) is preserved as a stratum, not dropped. JOINT_USE_GUIDE.md flags this but does not enforce; downstream code that misaggregates would silently bias rates.
- (c) The full natality `natality_v2_harmonized_derived.parquet` is not listed in any shipped PROVENANCE.md (only the residents-only convenience parquet is). Upstream documentation gap. Locally computed sha=`9f917a43474eb9e3ed23aa95c714209421c25c29937376651149d22fab934ef0` is recorded in the receipt and the build script's `--natality-parquet` arg requires the user to provide the path explicitly.

---

## 2026-05-11T17:30:00Z — task6_linked_validation_reconcile — Canonical framing for V3 linked external-target validation count

**Choice:** Adopt "33/35 byte-exact + 2 cells (2015 `unweighted_infant_deaths` and `postneonatal_deaths`) differ by exactly 1 record from NCHS upstream null-record-weight survivor records; all 35 pass within documented tolerance" as the canonical framing across the repo, matching the manuscript drafts and monorepo top-level README. Updated `natality/README.md` (lines 19, 27, 146), `natality/docs/ABOUT_THIS_RELEASE.md` (line 80), `natality/docs/COMPARABILITY.md` (line 367), `natality/docs/VALIDATION.md` (line 206), `paper/README.md` (line 18), `NEXT_STEPS.md` (§14 Table 1 line 440, §17 checklist line 791) to match.

**Alternatives considered:**
1. Keep "35/35 pass" as the headline everywhere and treat the 2-cell differences as a tolerance-aware caveat only in detailed validation tables. Cleaner headline; loses precision.
2. Adopt "33/35 byte-exact + 2 differ by 1" as the headline everywhere. More informative; honest about what "pass" means at the byte level. (Chosen.)
3. Carry both framings in parallel ("35/35 pass under documented tolerance; 33/35 byte-exact"). Most explicit; verbose.

**Reason:** The authoritative source `natality/output/validation/external_validation_v3_linked_comparison.md` shows 35 PASS / 0 FAIL / 0 MISSING under tolerance, AND shows 33 rows at Diff=0 with 2 rows (both 2015) at Diff=1. Both framings are factually correct, but they describe different metrics. The manuscript drafts already use option 2 (33/35 byte-exact + 2 cells differ by 1), as does the monorepo top-level `README.md`. The natality subproject's README and three of its docs were the outliers using only the headline "35/35 pass" framing. Option 2 is more honest about what the validation "pass" status means at the byte level, and aligning the natality subproject docs to it removes the cross-doc inconsistency the prior STATUS section flagged as Open Question #3.

**Source:**
- `natality/output/validation/external_validation_v3_linked_comparison.md` (authoritative validation comparison; 2015 rows `unweighted_infant_deaths` 23326→23327 and `postneonatal_deaths` 7772→7773 each show Diff=1, marked `pass`).
- `paper/draft_v2_hmd_styled.md` line 94 (manuscript canonical framing, retained).
- `README.md` (monorepo top-level) line 17 (already canonical, retained).

**Verifiable by:** `git ls-files | xargs grep -n -E '35/35|33/35' 2>/dev/null` should now show consistent canonical framing across all post-edit shipping docs; residual "35/35" mentions should only appear in (a) historical state-file entries (PRE_FLIGHT_LOG, STATUS open questions), (b) NEXT_STEPS.md §15 Task 6 spec which describes the problem being resolved.

**Reversible:** yes — `git reset --hard task6-pre-do` rolls back the seven file edits; the manuscript drafts and monorepo README would remain canonical (they were unchanged in this task).

**Residual risk (Self-check feed):**
- (a) `natality/README.md` line 146 mechanism-attribution phrase ("two null-`record_weight` survivor rows in 2014/2015") and `natality/docs/VALIDATION.md` line 219 mechanism-attribution phrase ("LATEREC edge cases") differ from the manuscript canonical mechanism phrase ("NCHS upstream survivor records with null record weights"). These three locally-varying mechanism phrasings are intentionally preserved because the task scope is HEADLINE-count reconciliation, not mechanism-attribution reconciliation. Each may describe the same underlying NCHS phenomenon under different terminology (LATEREC = late-filed records that lacked record_weight at file-build time; "survivor" likely refers to the surviving-cohort linkage). Disambiguating these three framings into one is a downstream task if pursued.
- (b) `natality/README.md` line 146 retains "2014/2015" for the underlying survivor rows although both validation diffs manifest in 2015 cells. The two need not contradict (e.g., a 2014-birth-cohort record manifesting in 2015 linked-file death counts), so the original wording is preserved without speculation.
- (c) Headline framing carries forward through future LinkedFile re-validation: if a later release re-derives different per-year counts that change the byte-exact vs differ-by-1 split, every file touched in this task needs a paired update.

---

## 2026-05-09T00:00:00Z — bootstrap — Operating protocol adopted from NHANES Assay-Bridging template

**Choice:** Adopt the NHANES Assay-Bridging Harmonization Project's `EXECUTION_PROTOCOL.md` discipline (five-phase task structure, append-only state files, mistake-class matrix, halt conditions, anti-patterns, self-check) for HVS work. Folded into `NEXT_STEPS.md` §1-§13.

**Alternatives:** (a) lighter-weight ad-hoc protocol with just task list and review hook; (b) full NHANES protocol replicated verbatim; (c) hybrid (this choice).

**Reason:** HVS data is already shipped and validated, so the heaviest NHANES patterns (multi-LLM dual-key transcription, mutation fixtures, NIST SRM checks) don't apply directly. But the patterns that matter most for any harmonization with public-validation-target gold standards — five-phase structure, halt conditions, mistake-class prevention, append-only state — apply equally to HVS. Adopting them now (before Tasks 1-10 ship) means the discipline guards the manuscript-supporting work, not just future maintenance.

**Source:** `/Users/yoelplutchok/Desktop/nhanes-assay-bridging/EXECUTION_PROTOCOL.md` (read 2026-05-09); `NEXT_STEPS.md` §1-§13 (this commit).

**Verifiable by:** A future LLM session, kicked off via `KICKOFF.md`, should be unable to do work without first running the §1 session-start sequence and waiting for human confirmation. The discipline is enforced by the prompt, not by code.

**Reversible:** yes — if the protocol proves too heavy for the actual work pattern, simplify by §11 plan-update process.
