# Receipt: v3-linked-comparison-v4-verify
## 2026-05-23T23:00:00Z

### What was done

TaskList #4 of the user-authorized 2026-05-23 "Pre-D cleanup first" block. Reconciled the carried Phase-D deferral wording "`external_validation_v3_linked_comparison.{md,csv}` full-v4 regen" against the **deliberate** FIX_LOG 2026-05-23T02:00:00Z v3-validator-owned-surface scoping, and discharged it as **verified-already-v4-current**: re-ran the deterministic validator against the SHA-confirmed v4 linked-derived parquet and proved the committed artifact is **byte-identically reproducible** (the H10 gate). **Zero net artifact mutation, zero canonical-state mutation** — the committed `external_validation_v3_linked_comparison.{md,csv}` (last committed at `127f101` = C8.18 DO step 6b) was already correct for v4; the "deferral" was a conservative carry. The honest §4.4/§10 disposition was to *verify + formally discharge* (no manufactured edit), not to "regenerate" a non-stale artifact.

### Inputs consumed
- `natality/output/validation/external_validation_v3_linked_comparison.{md,csv}` (committed @ `127f101`) + `natality/scripts/05_validate/compare_external_targets_v3_linked.py` (committed @ `127f101`) + `natality/metadata/external_validation_targets_v3_linked.csv`
- v4 linked-derived parquet `~/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet`, SHA `f630d8cf20db72ea` == gate SHA (UNCHANGED since C8.18 6b)
- FIX_LOG 2026-05-23T02:00:00Z (the deliberate 2005-2023-owned-surface scoping); `tests/mutations/test_compare_external_targets_v3_linked_mutation.py`

### Outputs produced
- (none — the validator re-run produced a byte-identical `.md`/`.csv`; no tracked-file change) + this receipt + STATUS/DECISION_LOG/PRE_FLIGHT_LOG appends

### Five-phase trace
- PRE-FLIGHT: ✓ `PRE_FLIGHT_LOG.md` 2026-05-23T22:45:00Z — PROCEED; tag `v3-linked-comparison-v4-verify-pre-do`@`c4287b9` before DO (no L10 back-fill). Established: parquet SHA unchanged since 6b + validator deterministic ⇒ byte-identical re-run expected.
- SMOKE: ✓ folded into DO — the validator run is itself the trivial-then-real exercise; mutation-test baseline green pre-DO (1 passed)
- DO: ✓ `uv run python …/compare_external_targets_v3_linked.py --in <SHA-confirmed v4 parquet> --out-dir natality/output/validation` → 149,386,620 rows × 97 cols, "35 pass, 0 fail, 0 missing", exit 0; commits `c4287b9`..`<this commit>`
- VERIFY: ✓ criteria below
- RECEIPT: ✓ this file

### Verify results
- V1 (H10 / disposition decider): **PASS** — `git diff --quiet v3-linked-comparison-v4-verify-pre-do -- …comparison.md …comparison.csv` = no diff ⇒ regenerated artifact **byte-identical** to the committed (`127f101`) version. The artifact is already v4-current AND deterministically reproducible.
- V2 scope: PASS — `git status --porcelain` = only untracked `.claude/`, `AUDITS/`; the validator run changed **no** tracked file (byte-identical overwrite)
- V3 zero canonical mutation: PASS — v4 parquet SHA still `f630d8cf20db72ea` (validator is read-only wrt the parquet/schema)
- V4 guard intact: PASS — `tests/mutations/test_compare_external_targets_v3_linked_mutation.py` = 1 passed (the L14/L3 adversarial guard holds post-run)

### Reproducibility
- This task **is** the reproducibility proof: the committed artifact re-renders byte-identically from the SHA-stable v4 parquet via the deterministic validator. `v3-linked-comparison-v4-verify-pre-do`@`c4287b9` is the anchor. No revert needed (no artifact change).

### Cross-product re-probe
- The v3-linked validator + its mutation guard re-run green; the artifact's 2005-2023 owned surface (35 cells, the documented within-tolerance "differ by 1" cells) is unchanged and correct on v4.

### Git
- Pre-DO tag: `v3-linked-comparison-v4-verify-pre-do`, commit=`c4287b9`
- Post-RECEIPT tag: `v3-linked-comparison-v4-verify-complete`, commit=`<this commit>` (state-files only — no artifact change to ship)

### STATUS.md updated
- New section dated 2026-05-23T23:00:00Z prepended; title "last updated" → 2026-05-23T23:00:00Z

### Self-check — what could I have gotten wrong that VERIFY wouldn't catch?
1. **"Byte-identical" is correct but the artifact is wrong-for-v4 in a way the 6b commit baked in.** Mitigation: not plausible — the FIX_LOG 2026-05-23T02:00:00Z 6b entry independently verified "35 pass, 0 fail" against the v4 parquet with the deliberate 2005-2023 owned-surface scoping (the pre-2005 cohort is the C8.18 DO-step VERIFY's domain, by design — re-adding it here is explicitly out of scope and was NOT done); my re-run reproduces that exact verified state and the mutation guard is green. The artifact reflects the correct, deliberately-scoped v4 owned surface.
2. **The deferral intended a *fuller* artifact (pre-2005 cohort cells in this file).** Mitigation: that would contradict the deliberate FIX_LOG 2026-05-23 scoping (a naive pre-2005 cohort row in this shipped MD would misstate published-comparable cohort figures — §9-#2/L6; documented). The PRE-FLIGHT explicitly flagged "NOT a re-scoping"; the pre-2005 cohort is verified at the C8.18 DO-step VERIFY (its correct home), not duplicated/mis-scoped here.
3. **Determinism could be machine/path-specific** (the abs path in the .md line 4). Mitigation: it reproduced byte-identical on this machine/path (the same environment that committed it at 6b); the abs-path non-portability is a pre-existing artifact property out of this task's scope (soft-flag-able, not a v4-correctness issue).

### Forward-looking HALTs for next session (Convention 4)
1. `v3-linked-comparison-v4-verify-pre-do`@`c4287b9` + `-complete` set ⇒ task CLOSED; the `external_validation_v3_linked_comparison.{md,csv}` v4 deferral is **discharged-as-verified** (the artifact was already v4-current + is H10-reproducible — STATUS Phase-D-deferrals should drop it).
2. The v3-linked validator is deliberately scoped to its 2005-2023 owned surface (FIX_LOG 2026-05-23T02:00:00Z); the pre-2005 cohort is the C8.18 DO-step VERIFY's domain. Do NOT "expand" this validator/artifact to pre-2005 — that is by-design, not a gap.
3. 3 gate parquet SHAs unchanged (`185c071e…`/`acb5c48a…`/`f630d8cf…`); validator is read-only; zero build-side change.
4. Remaining Pre-D cleanup: TaskList #5 (convenience/benchmark v4 refresh, soft-flag (ee)). Manuscript Coverage re-paragraph = D.4.

### Notes for next session
- #4 closed as verified-current (the cleanest outcome — the §2 PRE-FLIGHT hypothesis [SHA-stable input + deterministic generator ⇒ byte-identical] held). Next: TaskList #5 under five-phase discipline; then internal Pre-D cleanup complete and only the human-authorization-gated Phase D remains.
- §2/§4.4/§9-#3/§10/H10 honored: the cheap PRE-FLIGHT (parquet-SHA + determinism check) predicted the outcome; the DO proved it; the honest disposition was verify+discharge (no manufactured commit), not a spurious "regen".
