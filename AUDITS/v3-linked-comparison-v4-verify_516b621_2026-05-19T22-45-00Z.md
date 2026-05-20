---
audit_id: v3-linked-comparison-v4-verify_516b621
audit_date: 2026-05-19
auditor: fresh-eyes adversarial auditor (Opus 4.7, 1M context)
target_commit: 516b621 (tag: v3-linked-comparison-v4-verify-complete)
target_claim: "discharge-as-verified, no commit needed for the artifact" — zero artifact mutation, H10-reproducible
verdict: NO IN-SCOPE FINDINGS — discharge claim holds
high_risk_classes_checked: [L3, L7, §7-#18, F1, F2]
---

# Adversarial audit — `v3-linked-comparison-v4-verify` (commit 516b621)

## Scope

ONLY commit `516b621`. The agent claimed a zero-artifact-mutation outcome:
re-running the deliberately-2005-2023-scoped v3-linked validator against the
SHA-stable v4 linked-derived parquet (SHA `f630d8cf…`) produced byte-identical
output. Verdict was discharge-as-verified.

Per the audit charter: "the most dangerous shape to audit: a CLAIM of zero
work." Mandate was to genuinely re-execute the H10 check and probe for ways
the validator could be silently producing the same wrong output twice (L3
self-blindness).

## Adversarial checks — all executed

### 1. INDEPENDENT H10 CHECK — PASS

Snapshotted the committed `.md`/`.csv` to `/tmp`, then re-ran:
```
uv run python natality/scripts/05_validate/compare_external_targets_v3_linked.py \
  --in $HOME/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet \
  --out-dir natality/output/validation
```
Stdout: `Results: 35 pass, 0 fail, 0 missing` + `[load_targets] SKIPPED 95 target rows of 5 non-owned metric_id(s)`.

SHAs before / after re-run (identical):
- `external_validation_v3_linked_comparison.md` → `e8fe3bed6e66801da8615dca91b2d68f4a48ba7b18e2e8f272fc6aec3c0c8b43`
- `external_validation_v3_linked_comparison.csv` → `fbe7e2911a99e3e0ed0526fbc70a65a79a05836eb314a82285bf5414d0b343f7`

`diff -q` against `/tmp` snapshots: no output. Byte-identical. H10 holds.

### 2. PARQUET SHA — PASS

```
shasum -a 256 $HOME/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet
→ f630d8cf20db72eaf5e482e856e621ff73a6ad1c932de0fc832b237546b09073
```
Starts with `f630d8cf20db72ea` as claimed. SHA-stable-input claim is true.

### 3. VALIDATOR L3 SELF-BLINDNESS PROBE — NOT a tautology

```
uv run pytest tests/mutations/test_compare_external_targets_v3_linked_mutation.py -v
→ 1 passed in 3.01s
```

Test body inspection (`tests/mutations/test_compare_external_targets_v3_linked_mutation.py`):
- Writes a tempdir-CSV with `resident_births,2005,resident,expected=0,tol=0`.
- 2005 is the BOUNDARY of the OWNED 2005-2023 surface — strict-`<` skip at
  `compare_external_targets_v3_linked.py:134` keeps the row in scope.
- Real value is ~4.1M → `abs(diff) > tol` → `n_fail` increments →
  validator prints `*** FAILURES DETECTED ***` (line 403) and
  `raise SystemExit(1)` (line 404).

Runner assertion (`tests/mutations/_runner.py:94-138`) is the **AND** of:
- (i) `returncode != 0` (only true when `n_fail > 0`)
- (ii) fail-surface in stdout markers OR in output-file text

The conjunct (i) cannot be satisfied unless the validator actually caught
a real failure. A "summary line says **Fail**: 0" false-positive cannot
satisfy (i). Mutation guard is structurally non-tautological. ✓

### 4. SCOPING CORRECTNESS — PASS

`compare_external_targets_v3_linked.py:108-137` implements two skips with
disclosure:
- `metric_id not in SUPPORTED_METRICS` → skip
- `_yr is not None and _yr < 2005` → skip

Stdout reported `SKIPPED 95 target rows of 5 non-owned metric_id(s)
[metric:cohort_den_file_records=19, metric:cohort_num_file_records=19,
metric:resident_infant_deaths=19, pre2005-cohort:imr_per_1000=19,
pre2005-cohort:resident_births=19]`.

Manual count from targets CSV: 19 years × 5 categories = 95. Matches exactly.

Leak-path analysis:
- A pre-2005 row with metric_id in `SUPPORTED_METRICS` is caught by the
  year skip (line 134). Verified by the 19 + 19 pre2005-cohort skips above.
- A row with metric_id in `SUPPORTED_METRICS` and unparseable year sets
  `_yr = None`, which bypasses the year-skip check (line 134), but then
  `int(year_s)` at line 142 raises `ValueError` — loud crash, not silent
  leak.
- IMR trend table separately gated by `if y >= 2005` at line 324. Trend
  rows in the MD start at 2005 (lines 58-76). ✓

Scoping matches FIX_LOG 2026-05-23 rationale and inline comments at
`:108-125` and `:315-323`.

### 5. NO MISSED FAIL — PASS

Read all 35 CSV rows. Non-zero diffs:
- Row 7: `unweighted_infant_deaths,2015` — `diff=1, tol=2.0, status=pass` ✓
- Row 10: `postneonatal_deaths,2015`  — `diff=1, tol=2.0, status=pass` ✓

Both match the documented "differ by 1 (LATEREC edge case)" cells. All
other 33 rows have `diff=0`. Pass logic at `:284` is `abs(diff) <= tol`
— correct.

No row has non-zero diff > tolerance with status=pass. No silent passes.

### 6. SCOPE OF DISCHARGE — PASS (with one pre-existing portability smell, out of audit scope)

- `.md` line 3 ("Computed from `natality_v3_linked_harmonized_derived.parquet`")
  uses `args.in_path.name` (`:344`) → relative filename. Filename unchanged
  v3→v4; the file at that path IS the v4 file. Appropriate for v4. ✓
- `.md` line 5 embeds an absolute path
  (`/Users/yoelplutchok/Desktop/vital-statistics-harmonization/natality/metadata/...`).
  This is rendered by `f"- Targets: \`{args.targets}\`"` at `:346` —
  `args.targets` defaults to an absolute path computed from `Path(__file__).resolve()`.
  Pre-existing: `git log` on the MD shows last touch was `127f101` (the v4
  canonical mutation), NOT `516b621`. This commit honestly did not touch
  the artifact, so the smell pre-dates the discharge. Out of scope for
  this audit; flagged here for completeness.

## Verdict

NO HALT. Discharge-as-verified verdict is supported by independent
re-execution. The committed `external_validation_v3_linked_comparison.{md,csv}`
is:
- byte-identically reproducible from the SHA-stable v4 parquet (H10 ✓);
- gated by a structurally non-tautological mutation guard (L3 cleared);
- scoped to the OWNED 2005-2023 surface as documented (95 pre-2005/non-NVSR
  rows skipped with disclosure, no leak path);
- free of silent passes (only the 2 documented within-tolerance "differ
  by 1" cells).

## Commands actually executed

```
git show 516b621 --stat
shasum -a 256 $HOME/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet
wc -l natality/output/validation/external_validation_v3_linked_comparison.{csv,md}
cp natality/output/validation/external_validation_v3_linked_comparison.md /tmp/snap_v3l.md
cp natality/output/validation/external_validation_v3_linked_comparison.csv /tmp/snap_v3l.csv
shasum -a 256 /tmp/snap_v3l.md /tmp/snap_v3l.csv
uv run python natality/scripts/05_validate/compare_external_targets_v3_linked.py \
  --in $HOME/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet \
  --out-dir natality/output/validation
diff -q /tmp/snap_v3l.md natality/output/validation/external_validation_v3_linked_comparison.md
diff -q /tmp/snap_v3l.csv natality/output/validation/external_validation_v3_linked_comparison.csv
shasum -a 256 natality/output/validation/external_validation_v3_linked_comparison.{md,csv}
uv run pytest tests/mutations/test_compare_external_targets_v3_linked_mutation.py -v
git log --oneline natality/output/validation/external_validation_v3_linked_comparison.md
awk … natality/metadata/external_validation_targets_v3_linked.csv  (skip-count verification)
```

## Files actually read

- `natality/scripts/05_validate/compare_external_targets_v3_linked.py` (full)
- `natality/output/validation/external_validation_v3_linked_comparison.csv` (full)
- `natality/output/validation/external_validation_v3_linked_comparison.md` (full)
- `tests/mutations/test_compare_external_targets_v3_linked_mutation.py` (full)
- `tests/mutations/_runner.py` (full)
- `natality/metadata/external_validation_targets_v3_linked.csv` (filtered greps for leak-path coverage)
