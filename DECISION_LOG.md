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
