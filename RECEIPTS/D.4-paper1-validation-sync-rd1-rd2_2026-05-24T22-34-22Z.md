# Receipt: D.4 — manuscript validation-count sync (RD.1 + RD.2 envelope)

## 2026-05-24T22:34:22Z

### What was done

Updated `paper/draft_v2_hmd_styled.md` validation claims to match committed repo state after RD.1 (205/205 resident births 1968–2024) and RD.2 (41/41 matched-multiples cells). No parquet or target CSV mutation.

### Five-phase trace

- **PRE-FLIGHT:** Read STATUS RD.1 receipt; grep paper for stale 183/183-only and 13/13 MM counts.
- **SMOKE:** N/A (doc-only).
- **DO:** Edited Strengths/weaknesses, Future developments, Key Features future bullet, case study 2.
- **VERIFY:** Grep confirms no remaining "pre-1990 benchmarking planned" or "13/13" in paper; README already 205/205.
- **RECEIPT:** This file.

### Self-check (§10)

1. **Word-count regression** — Abstract + Key Features at front may push body over IJE 2,500; VERIFY did not re-count trimmed body-only words.
2. **Humanized draft drift** — `draft_v2_hmd_styled_humanized.md` not synced; parallel copy may stale if used for submission.
3. **Deposit-structure FLAGS** — "four companion parquet files" / "single-file" comments still open; not addressed this pass.

### Forward-looking HALTs for next session

1. Re-measure body word count excluding Abstract, Key Features, References; trim to ≤2,500 before submit.
2. If promoting humanized draft, re-apply validation-count edits there or regenerate from `draft_v2_hmd_styled.md`.

### Git

- Commit `d390349` on `main`.
