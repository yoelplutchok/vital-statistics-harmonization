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

(no entries yet)

## How this file relates to the natality `HARMONIZATION_LESSONS.md`

The natality project's `natality/HARMONIZATION_LESSONS.md` (when it exists) and the NHANES Assay-Bridging project's `HARMONIZATION_LESSONS.md` are upstream sources of distilled lessons from prior harmonization work. This file is for **HVS-specific** new lessons that emerge as we work on the cross-product joint-use layer, V2.1 transition years, V3 backward extension, manuscript work, and unified Zenodo deposit.

Lessons that turn out to be general-harmonization lessons (not HVS-specific) should also be reported upward — flag them in the entry, and the human can decide whether to propose them as updates to the upstream lessons documents.
