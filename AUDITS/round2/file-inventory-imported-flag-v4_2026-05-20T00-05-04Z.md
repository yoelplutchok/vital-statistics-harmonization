# Round 2 — file-inventory-imported-flag-v4 adversarial audit

## Scope

- **Commit:** `84a9af3` (tag `file-inventory-imported-flag-v4-complete`)
- **In scope:** `natality/metadata/file_inventory.csv` — 19 row mutations (`imported` false→true) + fix-on-contact rewords on the same 19 rows (`file_format`, `notes`)
- **Out of scope (same commit, not audited here):** `DECISION_LOG.md`, `STATUS.md`, `RECEIPTS/file-inventory-imported-flag-v4_2026-05-23T22-15-00Z.md`
- **Pre-edit anchor:** `7521366` (`file-inventory-imported-flag-v4-pre-do`)
- **Governing canonical fact:** C8.18 DO step 6b @ `127f101` / `DECISION_LOG` 2026-05-23T02:00:00Z — linked re-harmonize 1983-2023 → v4
- **Forbidden reads honored:** No round-1 `AUDITS/file-inventory-imported-flag-v4_*` or `AUDITS/CONSOLIDATED_*`; no `RECEIPTS/file-inventory-imported-flag-v4_*`; no `DECISION_LOG` / `STATUS` / `PRE_FLIGHT_LOG` entries dated ≥ 2026-05-23T22:00:00Z

## Checks performed (each: command + result + interpretation)

### Check 1 — Independent re-derivation of the 19 rows

**Commands:**

```bash
git show 7521366:natality/metadata/file_inventory.csv  # pre
git show 84a9af3:natality/metadata/file_inventory.csv   # post
# Python csv module: rows with year.endswith('_linked') and int(year.split('_')[0]) < 2005
```

**Rule (derived from 6b only):** Cohort-linked inventory keys `<YYYY>_linked` with calendar year &lt; 2005 were harmonized at 6b and should be `imported=true` post-flip. Years 2005+ `_linked` were already `true` pre-edit. Gap years 1992–1994 have no inventory rows (NCHS linkage gap).

| Metric | Result |
|--------|--------|
| Pre-edit `imported=false` among pre-2005 `_linked` | **19** |
| Post-edit `imported=true` among pre-2005 `_linked` | **19** |
| Rows with `imported` column changed | **19** (exact set match) |
| Post-edit `imported=false` anywhere | **0** |
| Post-edit `imported` counts | `{true: 95}` |
| Extra flip (20th row) | **None** |
| Missed flip | **None** |

**Changed years (sorted):** `1983_linked` … `1991_linked`, `1995_linked` … `2004_linked`.

**Field diffs on changed rows:** `imported`, `file_format`, `notes` only (all 19).

**Interpretation:** The flip set is exactly the pre-2005 cohort-linked block deferred since C8.18 step 2 / step 7. No erroneous inclusion or omission.

---

### Check 2 — Minimal diff sanity

**Commands:**

```bash
git diff --numstat 7521366..84a9af3 -- natality/metadata/file_inventory.csv
# → 19  19  natality/metadata/file_inventory.csv

# Line-level byte compare (96 lines = header + 95 data)
# → 77 byte-identical lines, 19 differing line indices (rows 54–72, 0-based)

# Dict equality on parsed csv rows
# → 76 of 95 data rows unchanged
```

**Result:** CSV-only diff in the scoped file is **19 insertions / 19 deletions**; no other natality inventory rows altered. The other **76** data rows are dict-identical pre→post (no re-quoting drift).

**Commit envelope (ancillary):** `git diff --name-only 7521366..84a9af3` also lists `DECISION_LOG.md`, `STATUS.md`, `RECEIPTS/…` — expected five-phase packaging, outside CSV scope.

**Interpretation:** Minimal-diff claim holds for `file_inventory.csv`.

---

### Check 3 — Tests post-edit + assertion audit

**Command:**

```bash
uv run pytest tests/test_inventory_invariants.py \
  tests/test_source_zip_sha_stability.py \
  tests/mutations/test_compare_external_targets_v3_linked_mutation.py -v
```

**Result:** **7 passed** in 24.31s (agent receipt cited 6 — the mutation test is a seventh item in this command list).

| Test | What it actually asserts | Sensitivity to this CSV change |
|------|--------------------------|--------------------------------|
| `test_fetal_death_inventory_years_match_schema_years_available` | fetal_death inventory (no `imported_only`) | None (different file) |
| `test_natality_inventory_years_match_schema_years_available` | `imported=true` **numeric** `year` keys vs `harmonized_schema.csv` union | **Skips** `*_linked` via `int(year)` ValueError — **cannot detect linked flip** |
| `test_fetal_death_inventory_record_length_populated_for_all_rows` | fetal_death `record_length` non-empty | None |
| `test_manifest_anchor_row_count` | 141 manifest rows | None (manifest, not inventory) |
| `test_manifest_section_row_counts` | 43+57+38+3 section split | None |
| `test_source_zip_sha_matches_manifest` | on-disk zip SHA vs manifest | None (filename-based `_classify`, not `imported`) |
| `test_compare_external_targets_v3_linked_catches_impossible_target` | validator fails on mutated 2005 target | None (parquet + temp CSV) |

**Post-edit parity (independent):** `imported=true` natality numeric years = schema union = **57 years (1968–2024)**, zero symmetric diff.

**Assertions the §7-gate analysis could miss:**

- None of these tests parse `file_format` or `notes` text (so the L7 spacing defect below is invisible to CI).
- `test_natality_inventory_years_match_schema_years_available` docstring still says pre-1990 rows are `imported=false` “as of C8.17 step 1” — **stale comment** (data now has 1968–1989 `true`; test still passes).

**Interpretation:** Green pytest is necessary but not sufficient for linked-row metadata correctness; the flip is justified by 6b facts, not by these tests alone.

---

### Check 4 — Fix-on-contact rewords

**Per-row pattern (all 19 cohort rows):**

| Field | Before | After | Factual? | SHA-anchored byte sizes |
|-------|--------|-------|----------|-------------------------|
| `imported` | `false` | `true` | Yes (6b harmonized 1983–2004 cohort into v4) | N/A |
| `file_format` | `record byte-width = C8.18 DO step 3 (per LinkCO…Guide.pdf)` | `layout reconstructed at C8.18 (perLinkCO…Guide.pdf)` | Yes — step 3 layout work is done; omitting numeric byte-width avoids L6 invention | N/A |
| `notes` | `…(imported=false until C8.18 re-harmonize).…` | `…(imported=true; C8.18 v4 re-harmonize complete — DO step 6b, linked 1983-2023).…` | Yes | **Preserved** — regex `\([\d,]+ b\)` token lists identical pre→post on all 19 rows |

**Defect (L7 — looks-right prose):** The `replace_all` on `file_format` dropped the space after `per` in all 19 rows: `(per LinkCO83Guide.pdf)` → `(perLinkCO83Guide.pdf)`. This is not an L6 number change but is a **copy/paste typo** in a human-readable parenthetical.

**Interpretation:** Substance of both rewords is correct; byte-size anchors intact; spacing regression is minor documentation quality, not a data/provenance failure.

---

### Check 5 — Downstream consumers

**Command:**

```bash
git ls-files | xargs grep -ln 'natality/metadata/file_inventory' 2>/dev/null
```

**Tracked references:** `tests/test_inventory_invariants.py`, plus narrative docs (`DECISION_LOG`, `FIX_LOG`, `NEXT_STEPS`, `PROJECT_STRUCTURE`, `docs/NCHS_SOURCE_MANIFEST.md`, receipts, `STATUS`, `PRE_FLIGHT_LOG`).

**`imported` column gating in code:**

```bash
grep -r '\bimported\b' --include='*.py' --include='*.R' --include='*.ipynb'
```

Only `tests/test_inventory_invariants.py` reads the CSV `imported` field for logic. No script, notebook, or validator branches on `file_inventory.csv` `imported`.

**Interpretation:** Agent’s “two test files” claim is directionally right for **executable** consumers; the only load-bearing reader is `test_inventory_invariants.py`, and it does not observe linked rows. No downstream break from the flip.

---

### Check 6 — Other natality inventory rows vs shipped envelopes

| Slice | Expected | Observed @ `84a9af3` |
|-------|----------|----------------------|
| 1968–1989 natality (numeric years) | `imported=true` (C8.17 step 6) | **22/22 true** |
| 1990–2024 natality | `true` | **true** |
| 2005–2023 `_linked` | `true` (pre-6b) | **19/19 true** |
| 1983–2004 `_linked` | `true` after this task | **19/19 true** |
| Inventory vs `harmonized_schema.csv` (imported numeric years) | equal sets | **Match (57 years)** |

**Pre-flag (out of commit scope, H8 docs-vs-data):** `docs/NCHS_SOURCE_MANIFEST.md` lines ~153 and ~205 still state the `imported` flag refresh is a “tracked Phase-D metadata-sync follow-up” / “deliberately not flipped at C8.18 DO step 7.” That narrative is **stale after `84a9af3`**; the CSV is now correct but the manifest block was not updated in this commit.

**Interpretation:** No incorrect `imported` value remains in the CSV. One related consumer doc still describes the pre-flip deferral.

---

## What was actually verified (anti-cheerleading record)

- Re-derived the 19-row set with Python `csv`, not shell `awk`.
- Confirmed 19/19 numstat and 76/95 unchanged parsed rows without reading agent receipts.
- Ran the three named pytest modules on the working tree; read all assertion bodies.
- Compared SHA-anchored `(N,NNN,NNN b)` tokens pre/post on every cohort row.
- Grepped tracked consumers and `imported` usage in executable code.
- Did **not** re-run full 347-test suite or re-hash gate parquets (commit diff has zero `.py`/parquet changes between anchors; not required for CSV-only scope).

## Findings

| §8 class | Severity | Evidence |
|----------|----------|----------|
| *(core task)* | — | Exactly 19 correct flips; 76 rows untouched; tests green; no L6 number invention. |
| L7 | **minor** | `(perLinkCO…Guide.pdf)` missing space after `per` on all 19 `file_format` cells — replace_all artifact; no test coverage. |
| L11 / H8 | **minor** (follow-up) | `docs/NCHS_SOURCE_MANIFEST.md` still documents the flip as deferred; inventory CSV no longer matches that prose. |
| L11 | **minor** (informational) | `test_inventory_invariants.py` docstring still describes 1968–1989 as `imported=false`; data is `true`. |

No L1 row hallucination, L6 invented byte-size, L12 awk-parse failure mode, or L13 wrong-row inventory defect found in scoped CSV edits.

## Halt conditions

| Condition | Tripped? |
|-----------|----------|
| Wrong row set (≠19 or wrong years) | **No** |
| Canonical / gate parquet mutation in scoped CSV work | **No** (diff is metadata CSV only) |
| §7 test gate failure on named inventory/SHA tests | **No** (7/7 pass) |
| New mistake class requiring human §10 sign-off | **No** |

**Halt:** none for shipping the CSV change. Optional non-blocking follow-ups: fix `(per LinkCO…)` spacing; refresh manifest deferral paragraphs.

## Verdict: **PASS**

Commit `84a9af3` correctly flips exactly the 19 pre-2005 cohort-linked inventory rows to `imported=true` after C8.18 DO step 6b, preserves SHA-anchored member byte sizes in `notes`, leaves the other 76 rows unchanged, and keeps the named pytest modules green. Residual issues are minor L7 wording typos and stale manifest narrative outside the CSV diff — neither reverses the canonical-truth flip nor indicates a missed row.
