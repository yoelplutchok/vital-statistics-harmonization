# Receipt: file-inventory-imported-flag-v4
## 2026-05-23T22:15:00Z

### What was done

TaskList #3 of the user-authorized 2026-05-23 "Pre-D cleanup first" block. Discharged the carried Phase-D deferral: `natality/metadata/file_inventory.csv` `imported` flag flipped `false`→`true` for **exactly the 19 pre-2005 cohort-linked rows** (`<YYYY>_linked` for `LinkCO83-91.zip` 1983-1991 + `LinkCO95US-04US.zip` 1995-2004) that C8.18 DO step 6b harmonized into the v4 linked parquet (1983-2023) but step 7 deliberately did not flip. Fix-on-contact (L11, same 19 rows, internal-consistency — the C8.17/C8.18-step7 honest-propagation precedent, not §7-#17): the two clauses that become self-contradictory after the flip were retargeted — col5 `file_format` `"record byte-width = C8.18 DO step 3 (per "` → `"layout reconstructed at C8.18 (per"`; `notes` `"(imported=false until C8.18 re-harmonize)"` → `"(imported=true; C8.18 v4 re-harmonize complete — DO step 6b, linked 1983-2023)"`. No invented numbers (L6 — the SHA-anchored member byte-sizes in `notes` are C8.18 DO-step-2 facts, preserved verbatim). Metadata-CSV only; zero canonical-state mutation.

### Inputs consumed
- `natality/metadata/file_inventory.csv` (95 data rows) @ `file-inventory-imported-flag-v4-pre-do`@`7521366`
- Canonical truth: C8.18 DO step 6b (linked v3→v4 1983-2023, 149,386,620 rows; DECISION_LOG 2026-05-23T02:00:00Z) + step 7 deferral (2026-05-23T05:00:00Z)
- §7-gate substrate: `tests/test_inventory_invariants.py`, `tests/test_source_zip_sha_stability.py`

### Outputs produced
- `natality/metadata/file_inventory.csv` — 19 rows modified (19 ins / 19 del; other 76 rows byte-identical) + this receipt + STATUS/DECISION_LOG/PRE_FLIGHT_LOG appends

### Five-phase trace
- PRE-FLIGHT: ✓ `PRE_FLIGHT_LOG.md` 2026-05-23T22:00:00Z — PROCEED; tag `file-inventory-imported-flag-v4-pre-do`@`7521366` before DO (no L10 back-fill). §7 gate analyzed + cleared.
- SMOKE: ✓ Tier-0 for a deterministic metadata edit — each of the 3 target substrings counted exactly 19× (and `,false,` exactly 19×, no incidental) BEFORE `replace_all`, so each replacement provably hits exactly the 19 target rows and the other 76 byte-identical
- DO: ✓ 3 `replace_all` edits, commits `7521366`..`<this commit>`
- VERIFY: ✓ criteria below
- RECEIPT: ✓ this file

### Verify results
- V1 flag state: PASS — `imported` counts = {true: 95, false: 0}; all 19 pre-2005 `<YYYY>_linked` rows now `true`; **zero** residual `"C8.18 DO step 3"` / `"imported=false until"` clauses; CSV well-formed (95 rows × 8 cols, `csv` parse clean)
- V2 minimal-diff scope: PASS — `git diff --numstat` = `19 19 natality/metadata/file_inventory.csv` only (pure per-line replacement; the other 76 rows byte-identical; no CSV re-quoting)
- V2b zero canonical mutation: PASS — no `.parquet`/`harmonized_schema`/`external_validation`/`.py`/`tests/` in the diff
- V3 §7-gate proof: PASS — `uv run pytest tests/test_inventory_invariants.py tests/test_source_zip_sha_stability.py` = **6 passed** post-flip (the natality parity test skips `<YYYY>_linked` keys regardless of `imported`; the sha-stability test is manifest/filename-based — exactly as PRE-FLIGHT analyzed)

### Reproducibility
- No build step. `git revert <commit>` restores the prior CSV; `file-inventory-imported-flag-v4-pre-do`@`7521366` is the anchor. The flip is canonical-truth (C8.18 6b) + deterministic (3 count-asserted substring replacements).

### Cross-product re-probe
- The only git-tracked readers of the natality `imported` column are the two inventory tests — both re-run green (V3). No notebook/script consumes it for behaviour.

### Git
- Pre-DO tag: `file-inventory-imported-flag-v4-pre-do`, commit=`7521366`
- Post-RECEIPT tag: `file-inventory-imported-flag-v4-complete`, commit=`<this commit>`

### STATUS.md updated
- New section dated 2026-05-23T22:15:00Z prepended; title "last updated" → 2026-05-23T22:15:00Z

### Self-check — what could I have gotten wrong that VERIFY wouldn't catch?
1. **A 20th row that should also be true.** Mitigation: the PRE-FLIGHT Python `csv` parse enumerated all `imported=false` rows = exactly 19, all `<YYYY>_linked` pre-2005; natality 1968-1989 already `true` (C8.17, not this task); linked 2005-2023 already `true`. The post-VERIFY count {true:95,false:0} confirms none missed and none over-flipped.
2. **The fix-on-contact reword altered a fact.** Mitigation: only a stale *forward-ref* ("DO step 3") and a stale *"until" clause* were reworded; the SHA-anchored member byte-sizes + member filenames in `notes` are byte-preserved (the 19/19 numstat = one changed line per row, the member-size text untouched). No invented numbers (L6).
3. **A downstream consumer outside the git-tracked test surface.** Mitigation: `git ls-files | xargs grep` found only the two inventory tests reading the natality `imported` column; both pass. A non-tracked/external consumer is out of scope and would be reading a metadata flag that is now *more* accurate, not less.
4. **`imported=true` now implies a schema/years_available parity the natality test would enforce.** Checked + mitigated: `test_natality_inventory_years_match_schema_years_available()` skips `<YYYY>_linked` keys (they belong to the sibling linked-cohort schema, not natality `harmonized_schema.csv`) — the flip is correctly invisible to that parity assertion (the linked product's year-set is governed by `external_validation_targets_v3_linked.csv` + the linked pipeline, validated at C8.18, not by this test). V3 green confirms.

### Forward-looking HALTs for next session (Convention 4)
1. `file-inventory-imported-flag-v4-pre-do`@`7521366` + `-complete` set ⇒ task CLOSED; the `file_inventory.csv` `imported`-flag Phase-D deferral is **discharged** (STATUS Phase-D-deferrals should drop it). `natality/metadata/file_inventory.csv` `imported` is now uniformly `true` (95/95) — every SHA-anchored row reflects a shipped/harmonized state.
2. 3 gate parquet SHAs unchanged (`185c071e…`/`acb5c48a…`/`f630d8cf…`); metadata-CSV only; zero build-side change.
3. Remaining Pre-D cleanup: TaskList #4 (`external_validation_v3_linked_comparison.{md,csv}` v4 refresh — note FIX_LOG 2026-05-23T02:00:00Z deliberately scoped the v3 validator to its 2005-2023 owned surface; #4 PRE-FLIGHT must reconcile "full-v4 refresh" against that deliberate scoping), #5 (convenience/benchmark v4). Manuscript Coverage re-paragraph = D.4.
4. Date convention: 2026-05-23T22:15:00Z (monotonic-after; repo append-only clock ahead of harness `currentDate` 2026-05-19).

### Notes for next session
- The natality inventory `imported` column is now fully accurate for the v4 envelope. Next: TaskList #4 under five-phase discipline; its PRE-FLIGHT must carefully reconcile the "v4 refresh" wording with the FIX_LOG 2026-05-23 deliberate v3-validator-owned-surface scoping (the v3 validator is intentionally 2005-2023; the pre-2005 cohort is verified by the C8.18 DO-step VERIFY, not this validator) — likely a re-run + recommit of the already-correctly-scoped artifact, not a re-scoping.
- §2/§7/§9-#8/L6/L11 honored: §7 gate analyzed + cleared at the cheap PRE-FLIGHT before any mutation; deterministic count-asserted substring edits (minimal diff, no CSV re-quoting); fix-on-contact kept to the same 19 rows with no invented numbers; this task not compressed with #2 or #4.
