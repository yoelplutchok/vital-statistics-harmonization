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

After reading, tell me in 4-6 sentences:
  (a) the current task per STATUS.md (or "bootstrap, no STATUS state
      yet" if uninitialized),
  (b) any open questions for human you found,
  (c) what you propose to do this session,
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
