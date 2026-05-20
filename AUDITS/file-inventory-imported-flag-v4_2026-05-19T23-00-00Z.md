# Adversarial audit — file-inventory-imported-flag-v4 (commit 84a9af3)

Auditor: fresh-eyes adversarial pass
Date: 2026-05-19T23:00:00Z
Scope: commit `84a9af3` only — tag `file-inventory-imported-flag-v4-complete`
Forbidden reads honored: receipt + post-2026-05-23T22:00:00Z STATUS/DECISION_LOG/PRE_FLIGHT_LOG entries.

## Verdict

**1 finding, every check executed.** Core canonical claim (19/19 right rows flipped, 76 byte-identical, zero number mutation, tests green) holds. One human-readable-prose regression in the fix-on-contact rewords.

---

## FINDING #1 — L7 looks-right typo in 19/19 col5 rewords

The agent's col5 rewrite dropped the space between `per` and the guide filename in every one of the 19 changed rows.

| | text |
|---|---|
| Pre-edit (`7521366`) | `record byte-width = C8.18 DO step 3 (per LinkCO83Guide.pdf)` |
| Post-edit (`84a9af3`) | `layout reconstructed at C8.18 (perLinkCO83Guide.pdf)` |

Evidence:

```
$ grep -c '(perLinkCO' natality/metadata/file_inventory.csv
19
$ grep -c '(per Link' natality/metadata/file_inventory.csv
0
$ git show 7521366:natality/metadata/file_inventory.csv | grep -c '(per LinkCO'
19
$ git show 7521366:natality/metadata/file_inventory.csv | grep -c '(perLinkCO'
0
```

Risk class: **L7 (looks-right)** — reads cleanly at a glance, but the space is missing in 19/19 rows.

Severity: **cosmetic**. The parenthetical content is human-readable metadata only and no programmatic consumer parses it (verified in Check 5 below). But the commit message brands this as a hygiene pass ("+fix-on-contact the 2 now-self-contradictory clauses"), and the fix itself shipped a 19/19 typo. The agent's §7-gate analysis correctly declared L6 (invented numbers) clean — and indeed every SHA-anchored member byte-size is preserved — but skipped L7 verification of the new prose.

Recommended remediation: 19-row search/replace `(perLinkCO` → `(per LinkCO` (within col5 only — col7/notes was untouched in this respect).

---

## CHECK 1 — Independent re-derivation of the 19 rows

Used Python `csv.DictReader` (not awk — notes column has embedded commas).

| metric | pre-edit (`7521366`) | post-edit (`84a9af3`) |
|---|---|---|
| total rows | 95 | 95 |
| imported=true | 76 | 95 |
| imported=false | 19 | 0 |
| changed rows | — | 19 (cols: imported + file_format + notes) |
| OTHER column changes | — | 0 |

19 flipped rows (full enumeration):

```
1983_linked, 1984_linked, 1985_linked, 1986_linked, 1987_linked, 1988_linked,
1989_linked, 1990_linked, 1991_linked, 1995_linked, 1996_linked, 1997_linked,
1998_linked, 1999_linked, 2000_linked, 2001_linked, 2002_linked, 2003_linked,
2004_linked
```

Cross-check against C8.18 DO step 6b at commit `127f101`:

> "re-harmonize linked 1983-2023 → v4 … 149,386,620 rows (= 74,442,796 pre-2005 cohort + 74,943,824 existing 2005-2023)"

The 19 flipped rows are exactly the pre-2005 cohort-linked years (1983-91 + 1995-2004; canonical 1992-94 cohort-linked gap is expected — those years were period-linked, not in the cohort series). Re-derivation matches. No row missed; no row over-flipped.

**Pass.**

---

## CHECK 2 — Minimal-diff sanity

```
$ git diff --numstat 7521366..84a9af3
...
19	19	natality/metadata/file_inventory.csv
```

Python line-by-line comparison:

| metric | value |
|---|---|
| Pre-edit lines | 96 (1 header + 95 data) |
| Post-edit lines | 96 |
| Lines differing | 19 (indices 54–72, contiguous, natural order) |
| Header line identical | True |
| Trailing newline preserved | True (both end with `\n`) |
| `DictReader`-equal rows | 76 |

No CSV re-quoting of the other 76 rows. **Pass.**

---

## CHECK 3 — Run all three tests + read assertions

```
$ uv run pytest tests/test_inventory_invariants.py tests/test_source_zip_sha_stability.py \
    tests/mutations/test_compare_external_targets_v3_linked_mutation.py -v
============================== 7 passed in 24.49s ==============================
```

| test | reads file_inventory.csv? | result |
|---|---|---|
| `test_fetal_death_inventory_years_match_schema_years_available` | fetal_death only | PASS |
| `test_natality_inventory_years_match_schema_years_available` | yes, `imported_only=True`, skips `*_linked` via `int()` ValueError | PASS |
| `test_fetal_death_inventory_record_length_populated_for_all_rows` | fetal_death only | PASS |
| `test_manifest_anchor_row_count` | reads `docs/NCHS_SOURCE_MANIFEST.md` | PASS |
| `test_manifest_section_row_counts` | reads manifest | PASS |
| `test_source_zip_sha_matches_manifest` | reads manifest + zips on disk | PASS |
| `test_compare_external_targets_v3_linked_catches_impossible_target` | reads v3-linked parquet | PASS |

Assertions audited: the natality invariant test is **structurally insensitive to the linked-row flip** — `int(row["year"])` raises ValueError on `1983_linked` and the row is skipped, so the imported flip on linked rows cannot break it. SHA-stability tests don't touch the inventory CSV. No assertion in the named files would have caught the L7 typo (the parenthetical text is not parsed by any test).

**Pass.** No assertion missed.

---

## CHECK 4 — Fix-on-contact rewords

### (a) Wording correctness given C8.18 step 6b

| field | old wording | new wording | factual? |
|---|---|---|---|
| col5 | `record byte-width = C8.18 DO step 3 (per <Guide>.pdf)` | `layout reconstructed at C8.18 (per<Guide>.pdf)` | **More accurate** — the old "step 3" was wrong for 1995-2004 rows (their layouts were reconstructed at C8.18 step 4a/4b/4c per commits `6fb7acd`/`a0128eb`/`7f09da0`). New "at C8.18" covers both. But space missing — see Finding #1. |
| col7/notes | `(imported=false until C8.18 re-harmonize)` | `(imported=true; C8.18 v4 re-harmonize complete — DO step 6b, linked 1983-2023)` | Factually correct per `127f101` ("re-harmonize linked 1983-2023 → v4"). |

### (b) SHA-anchored member byte-size preservation

Regex sweep `([A-Za-z0-9._]+)\s*\(([\d,]+)\s*(?:b|bytes)\)` across notes of all 19 rows:

| row | anchors pre==post |
|---|---|
| 1983–1991_linked (9 rows) | 3 anchors each (den shown twice; num once); zero mutation |
| 1995–2004_linked (10 rows) | 4 anchors each (den shown twice; num + unl); zero mutation |
| **Total mismatches** | **0** |

Spot-checks (all preserved): `LinkCO83USden.dat (310,738,482 b)`, `LinkCO89USden.dat (918,414,987 b)`, `LinkCO95USDen.dat (905,498,784 b)`, `VS03LKBC.USDENPUB (3,215,478,535 b)`, `VS04LKBC.DUSDENOM (3,715,298,312 b)`.

**Pass** modulo Finding #1 (cosmetic).

---

## CHECK 5 — Downstream consumers

```
$ git ls-files | xargs grep -ln 'natality/metadata/file_inventory' 2>/dev/null
```

Code consumers (Python files that programmatically parse):

| file | parses CSV? |
|---|---|
| `tests/test_inventory_invariants.py` | **yes** — only programmatic consumer |
| `fetal_death/scripts/05_validate/validate_external_v2.py` | no — comment reference only at line 109 |
| `scripts/_drive_fetal_death_benchmark.py` | no — comment reference only at line 27 |
| `tests/test_source_zip_sha_stability.py` | no — comment reference at line 24; reads manifest not CSV |

No notebooks (`*.ipynb`) reference file_inventory at all. Everything else is markdown (READMEs, RECEIPTS, logs).

The agent's §7-gate "only 2 test files" is correct in spirit — and one of those two doesn't even parse the CSV. The flip has no programmatic downstream impact.

**Pass.**

---

## CHECK 6 — No other natality CSV row is stale

Post-edit inventory: 95 rows, 100% imported=true. Verified against shipped envelopes:

### Non-linked (57 rows: 1968–2024)

```
inventory non-linked year-set:           {1968, 1969, ..., 2024} (57 years)
harmonized_schema years_available union: {1968, 1969, ..., 2024} (57 years)
inventory \ schema: []
schema \ inventory: []
```

Exact match. `test_natality_inventory_years_match_schema_years_available` independently confirms this (PASSED).

### Linked (38 rows: 1983–1991, 1995–2023)

```
inventory linked years: {1983..1991, 1995..2023} (38 years)
```

Matches the C8.18 step 7 envelope (`1902415`): "1983-2023; 149,386,620; 1992-1994 gap".

`external_validation_targets_v3_linked.csv` has 26 distinct `data_year` values, all subset of the inventory linked years (validation targets are sparse anchor benchmarks, not row-per-year — expected).

No row is incorrectly `imported=true`; no row is missing; no expected pre-2024 cohort-linked row is absent.

**Pass.**

---

## High-risk-class summary

| risk class | result |
|---|---|
| L1 (file/row hallucination) | clean — 19/19 rows are real, expected, scoped exactly |
| L6 (invented number) | clean — all SHA-anchored byte counts preserved exactly |
| **L7 (looks-right)** | **FINDING #1** — 19/19 missing-space typo `(perLinkCO…)` |
| L12 (trusted own grep) | not applicable to audit; agent's prior failed-awk parse didn't reach this commit |
| L13 (inventory CSV) | clean except Finding #1 |

## Anti-cheerleading attestation

Every check above ran a command or read a file. No finding was manufactured to satisfy the audit, and no claim rests on "looks fine." Finding #1 is supported by four grep counts (pre and post, both polarities). All other checks passed on direct evidence, and the verdict reflects that.
