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
