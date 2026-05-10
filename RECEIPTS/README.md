# RECEIPTS/

One markdown file per completed task. **Append-only at the directory level** — never edit or delete an existing receipt. New receipts go in new files.

## Filename convention

```
RECEIPTS/<task_id>_<UTC_timestamp>.md
```

Examples:

- `task1_joint_use_layer_2026-05-12T14-30-00Z.md`
- `task6_linked_validation_reconcile_2026-05-09T18-15-00Z.md`
- `task3_v21_transition_years_2026-05-20T22-00-00Z.md`

For multi-sub-step tasks, use a single receipt at task completion. If a sub-step is itself substantial (e.g., layout reconstruction within Task 3), it can have its own intermediate receipt with a `.<sub>` suffix:

- `task3.1_record_layout_2003_reconstruction_2026-05-19T11-00-00Z.md`

## Receipt template

See `NEXT_STEPS.md` §6 for the canonical template. Briefly:

```markdown
# Receipt: <task_id>
## <UTC timestamp>

### What was done
### Inputs consumed (paths + sha256)
### Outputs produced (paths + sha256 + row/col counts)
### Five-phase trace (PRE-FLIGHT/SMOKE/DO/VERIFY/RECEIPT timestamps + commits)
### Verify results (criterion → PASS/SOFT-FLAG with values)
### Reproducibility (re-run produces bit-identical output ✓)
### Cross-product re-probe (if applicable)
### Git (pre-do tag, post-receipt tag)
### STATUS.md updated (link to new STATUS section)
### Self-check (the §10 question: what could I have gotten wrong?)
### Notes for next session
```

## How receipts are used

- **Ground truth for "did this task happen?"** If a receipt does not exist, the task did not happen. Do not advance `STATUS.md` to "task complete" without a corresponding receipt file.
- **Resumability after a session break.** A future LLM (or human) reading STATUS.md sees which receipt corresponds to the last completed task and can read it for full context.
- **Audit trail for the manuscript.** Every numeric claim in the manuscript that is not auto-generated should be traceable to a receipt's "Outputs produced" or "Verify results" section.

## Audit sessions

Audit sessions (per `KICKOFF.md`) deliberately **refuse to read existing receipts** so they cannot inherit the build session's blind spots. The auditor re-derives findings from primary sources (PDFs, raw data, schema CSVs) and compares to what the receipts claim. If the audit's independently-derived result disagrees with the receipt, that's a finding — file it as a `FIX_LOG.md` entry pointing back to the receipt.
