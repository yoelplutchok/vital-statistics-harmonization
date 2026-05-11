# LESSONS

> **Append-only.** When a new mistake class — one not in `NEXT_STEPS.md` §8 — is encountered, document it here. Then propose a new row for the §8 matrix via the §11 plan-update process.
>
> A "new mistake class" is a failure mode that was not anticipated by the existing matrix and is likely to recur. A one-off typo is not a new class. A pattern that the matrix should have predicted but didn't is a new class.
>
> Entry format:
>
> ```markdown
> ## YYYY-MM-DDTHH:MM:SSZ — <task_id> — <proposed class ID> — <one-line title>
> **What failed:** <the actual incident>
> **Why the existing matrix didn't catch it:** <which row of §8 should have caught it but didn't, and why>
> **What worked:** <how the failure was eventually surfaced>
> **Proposed new matrix row:** <draft row for §8>
> **Backport scope:** <which already-completed tasks should be re-verified now that this class is known>
> ```

---

## 2026-05-11T16:32:34Z — protocol-sync — n/a (sync, not a new bug class) — Port generalizable conventions from upstream NHANES protocol

**What happened (not a failure — a proactive sync):** The HVS operating protocol in `NEXT_STEPS.md` §1-§13 and `KICKOFF.md` was originally modeled on the NHANES Assay-Bridging `EXECUTION_PROTOCOL.md`. The NHANES protocol has since accumulated five generalizable conventions (dated 2026-05-11 in NHANES `KICKOFF.md`) plus three new mistake-class matrix rows (L13, L14, L17) that are HVS-applicable and not already in our discipline.

**Why this matters now:** Each of the five conventions and three mistake-class rows prevented a real cascade in NHANES work. Carrying them over before HVS hits a similar issue is the cheap option. The protocol-update process in §11 expects this kind of upstream-distillation backport.

**What was applied (single `[plan-update]` commit):**
- `KICKOFF.md`: added "Conventions in effect" block listing Conventions 1-5 (SHAPE-not-VALUE; FROZEN-AT-TASK docstring tag; Field-value snapshot in PRE-FLIGHT; Forward-looking HALTs in RECEIPT; commit-message brevity); refined audit-session framing to point findings at `AUDITS/` and added L17 to the audit's "look for these specifically" list.
- `NEXT_STEPS.md` §4.2.1: SHAPE-not-VALUE rule + DESIGN docstring tag for new SMOKE harnesses.
- `NEXT_STEPS.md` §4.5: commit-message brevity (~5-line summary; full narrative in receipt).
- `NEXT_STEPS.md` §5: Field-value snapshot subsection in PRE-FLIGHT template.
- `NEXT_STEPS.md` §6: Forward-looking HALTs subsection in RECEIPT template.
- `NEXT_STEPS.md` §8: new mistake-class matrix rows L13 (inventory file roles vs columns), L14 (per-row failures not propagated to script exit code), L17 (SMOKE pins stale annotation values).

**What was NOT ported (NHANES-specific, not HVS-applicable):** Cross-family dual-key transcription relaxation (NHANES bridges.csv `transcribed_by_a/b` is not an HVS concept); `halt_c_reprobe.sh` (NHANES-specific named script enumerating its SMOKE harness set); schema `$schema_version` field on `BRIDGES/bridges_schema.json` (HVS uses per-product `harmonized_schema.csv` with a different versioning convention); the V1.9-folate.c.9 series planned-task block (NHANES-specific in-flight work).

**Backport scope:** None — bootstrap is the only prior HVS session, no canonical-state mutations have happened yet. The conventions take effect for Task 1 onwards (joint-use convenience layer; first task to actually mutate a canonical artifact).

**Upstream lesson?** No — this entry is HVS-internal record-keeping of an upstream-to-downstream sync. The upstream lessons are already documented in NHANES `EXECUTION_PROTOCOL.md`.

---

## How this file relates to the natality `HARMONIZATION_LESSONS.md`

The natality project's `natality/HARMONIZATION_LESSONS.md` (when it exists) and the NHANES Assay-Bridging project's `HARMONIZATION_LESSONS.md` are upstream sources of distilled lessons from prior harmonization work. This file is for **HVS-specific** new lessons that emerge as we work on the cross-product joint-use layer, V2.1 transition years, V3 backward extension, manuscript work, and unified Zenodo deposit.

Lessons that turn out to be general-harmonization lessons (not HVS-specific) should also be reported upward — flag them in the entry, and the human can decide whether to propose them as updates to the upstream lessons documents.
