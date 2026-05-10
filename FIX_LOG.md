# FIX_LOG

> **Append-only.** Every bug found during HVS work is logged here as a dated row. Bugs include parsing errors, harmonization mistakes, validator self-blindness, doc-data drift, and cross-product join errors.
>
> Use the bug class IDs from `NEXT_STEPS.md` §8 (mistake-class matrix): H1-H10 (harmonization), F1-F5 (HVS-specific cross-product), L1-L12 (LLM-execution).
>
> Entry format:
>
> ```markdown
> ## YYYY-MM-DDTHH:MM:SSZ — <task_id> — <bug class> — <one-line title>
> **Symptom:** <what was observed>
> **Root cause:** <what was actually wrong>
> **Fix:** <what was changed>
> **Files touched:** <paths>
> **Regression scope:** <which adjacent cycles, products, or tasks were re-verified after the fix>
> **Verified by:** <which validator or test confirms the fix>
> **Could the §8 matrix have caught this earlier?** yes/no + how
> ```

---

(no entries yet)
