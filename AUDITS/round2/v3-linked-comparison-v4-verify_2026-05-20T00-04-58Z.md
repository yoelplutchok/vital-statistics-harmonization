# Round 2 adversarial audit — v3-linked-comparison-v4-verify

- **Audit UTC:** 2026-05-20T00:04:58Z
- **Auditor:** fresh-eyes adversarial pass (Round 2; no prior `AUDITS/` reads)
- **Scope commit:** `516b621` (tag `v3-linked-comparison-v4-verify-complete`)
- **Claim under test:** zero-artifact-mutation verify+discharge — committed `external_validation_v3_linked_comparison.{md,csv}` already v4-current and H10-reproducible against SHA-stable v4 parquet `f630d8cf…`; only state-file records in `516b621`
- **High-risk classes probed:** L3 (validator self-blindness), L7 (looks-right), §7-#18 (reproducibility), F1/F2 (canonical filter)

## Forbidden-reads compliance

Did **not** read: `RECEIPTS/v3-linked-comparison-v4-verify_2026-05-23T23-00-00Z.md`; `STATUS.md` / `DECISION_LOG.md` / `PRE_FLIGHT_LOG.md` entries ≥ 2026-05-23T22:45:00Z; any other file under `AUDITS/` except this output.

**Permitted reads used:** `git show 516b621`; committed `.md`/`.csv`; validator script; targets CSV; mutation test; v4 parquet; `FIX_LOG.md` 2026-05-23T02:00:00Z (L13-extension scoping entry).

---

## Adversarial checks

### 1. INDEPENDENT H10 CHECK — **PASS**

Procedure:

1. Snapshotted committed artifacts to `/tmp/hvs-audit-r2/committed.{md,csv}`.
2. Re-ran:
   ```bash
   uv run python natality/scripts/05_validate/compare_external_targets_v3_linked.py \
     --in $HOME/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet \
     --out-dir natality/output/validation
   ```
3. `diff -q` regenerated vs snapshots.

**Result:** exit 0, no output from `diff -q` (byte-identical `.md` and `.csv`). Validator stdout: `35 pass, 0 fail, 0 missing`. `[load_targets] SKIPPED 95` rows disclosed (95 = 19×5 skip buckets). Parquet read: 149,386,620 rows, 97 columns.

§7-#18 HALT: **not triggered**.

### 2. PARQUET SHA — **PASS**

```
f630d8cf20db72eaf5e482e856e621ff73a6ad1c932de0fc832b237546b09073
```

Prefix matches claimed `f630d8cf20db72ea…`. SHA-stable input claim holds on this machine.

### 3. VALIDATOR L3 SELF-BLINDNESS PROBE — **PASS (not tautological)**

```bash
uv run pytest tests/mutations/test_compare_external_targets_v3_linked_mutation.py -v
```

→ `1 passed in 2.87s`.

Test body (`tests/mutations/test_compare_external_targets_v3_linked_mutation.py`):

- Writes a **mutated** targets CSV with a single row: `resident_births,2005,resident,0,0` (impossible expected value).
- Runs the real validator against the real v4 parquet with `--targets` pointing at the mutation file and `--out-dir` in a temp dir.
- Asserts via `assert_mutation_caught`: non-zero exit / `"FAILURES DETECTED"` / `"Fail:"` markers and fail text in generated comparison outputs.

This is a genuine injection + detection test, not a self-referential pass. L3 residual risk: mutation only covers one owned metric/year; it does not prove correctness of all eight `SUPPORTED_METRICS`, but it does prove the fail path is live.

### 4. SCOPING CORRECTNESS — **PASS**

`FIX_LOG.md` 2026-05-23T02:00:00Z (L13-extension entry) claims:

- Skip `metric_id ∉ SUPPORTED_METRICS` with disclosure.
- Skip `data_year < 2005` (pre-2005 cohort surface).
- Print `[load_targets] SKIPPED …` disclosure.
- MD IMR trend limited to ≥2005.

Code at `load_targets` (lines 130–137, 150–159) and `main()` trend `all_years` filter (line 324) matches FIX_LOG verbatim.

**Pre-2005 leak paths considered:**

| Path | Leak? | Why |
|------|-------|-----|
| Target rows `data_year < 2005` for NVSR metrics | No | Explicit `continue` before append |
| `cohort_*` / `resident_infant_deaths` rows | No | `metric_id not in SUPPORTED_METRICS` → skip |
| Parquet scan still accumulates 1983–2004 in `accum` | N/A | Only used for trend table; trend filtered `>= 2005` |
| Comparison uses `metrics` for unloaded targets | No | `targets` list is post-filter; only 35 owned rows compared |
| Invalid `data_year` string | No | Would fail `int(year_s)` at Target construction (not silently included) |

Re-run skip line: `[metric:cohort_den_file_records=19, metric:cohort_num_file_records=19, metric:resident_infant_deaths=19, pre2005-cohort:imr_per_1000=19, pre2005-cohort:resident_births=19]` — consistent with 19 years × 5 skip classes = 95.

### 5. NO MISSED FAIL — **PASS**

Committed `.md`: Pass 35 / Fail 0 / Missing 0.

Committed `.csv`: 36 lines (1 header + 35 data rows).

Python pass over all 35 rows:

- Rows with non-zero `diff`: **exactly 2**
  - `unweighted_infant_deaths,2015` — diff=1, tolerance_abs=2.0, status=pass
  - `postneonatal_deaths,2015` — diff=1, tolerance_abs=2.0, status=pass
- No row has non-zero diff with status≠pass.
- No fail/missing rows.

These two are the documented LATEREC within-tolerance cells (23326→23327; 7772→7773). No additional hidden failures.

### 6. SCOPE OF DISCHARGE — **PASS (with pre-existing portability note)**

`git show 516b621 --stat`: **only** `DECISION_LOG.md`, `RECEIPTS/v3-linked-comparison-v4-verify_2026-05-23T23-00-00Z.md`, `STATUS.md`. Zero changes to `natality/output/validation/*` or validator — consistent with honest zero-artifact-mutation discharge.

Artifact provenance:

- Last commit touching comparison artifacts + validator: `127f101` (C8.18 DO step 6b) — i.e., post-scoping regeneration at 6b, not at `516b621`.

`.md` header line 3: ``Computed from `natality_v3_linked_harmonized_derived.parquet` `` — basename only; still correct for v4 linked-derived product (filename unchanged across v3→v4 re-harmonize).

`.md` line 5: absolute path to targets CSV (`/Users/yoelplutchok/Desktop/vital-statistics-harmonization/natality/metadata/...`). **Pre-existing** since `127f101` (identical in `git show 127f101:…md`); not introduced by verify task. Portability cosmetic only — does not affect H10 byte identity on re-run from this repo layout.

Post-audit `git status` for `natality/output/validation/`: clean (re-run did not dirty tree vs committed bytes).

---

## Commit-scope verification (`516b621`)

| Claim element | Audit finding |
|---------------|----------------|
| No artifact commit needed | **Confirmed** — `516b621` diff is state-files only |
| Artifacts already v4-current | **Confirmed** — H10 byte-match vs v4 parquet; 97-col parquet; 35/0/0 on 2005–2023 owned surface |
| Validator unchanged since scoping fix | **Confirmed** — validator last touched `127f101`, not `516b621` |
| NOT a re-scoping | **Confirmed** — scoping matches FIX_LOG; 95 skips on re-run |

---

## High-risk class summary

| Class | Result | Notes |
|-------|--------|-------|
| §7-#18 | Clear | Byte-identical regeneration |
| L3 | Clear | Mutation test catches impossible 2005 target |
| L7 | Clear | Did not rely on receipt/status narrative; re-executed |
| F1/F2 | N/A at this commit | No canonical parquet/metadata mutation in scope |

---

## Halt conditions

| Halt | Triggered? |
|------|------------|
| §7-#18 (H10 mismatch) | **No** |
| §7 (artifact stale but claimed fresh) | **No** |
| §7 (SHA mismatch) | **No** |
| L3 (mutation guard dead) | **No** |

**HALT: none.**

---

## Verdict

**ACCEPT** the `516b621` zero-artifact-mutation discharge-as-verified outcome.

The dangerous "no work done" shape was tested adversarially: independent H10 reproduction is byte-identical; input parquet SHA matches; the mutation guard is real; scoping prevents pre-2005/cohort mis-comparison; the 35-row CSV has no silent fails; the commit correctly records state without manufacturing an empty artifact diff.

---

## Findings (ranked)

None blocking.

### Observation (cosmetic, pre-existing)

- **O1 — Absolute targets path in generated `.md`:** Line 5 embeds a machine-specific absolute path. Pre-dates `516b621`. Optional future hygiene: emit repo-relative path in `write_md` (out of this audit's commit scope).

---

## Anti-cheerleading record

What this audit **did not** verify (explicit limits):

- Did not re-run `verify_6b_peryear.py` or independently prove the 95 skipped pre-2005/cohort targets against NCHS sources (correctly out of this validator's owned surface per FIX_LOG).
- Did not prove v4 parquet semantic correctness beyond SHA pin + 35 NVSR comparisons.
- Mutation test covers one fail scenario (2005 `resident_births`), not full metric/year Cartesian coverage.
- Did not read the agent receipt or post-22:45 state logs (by design); verdict is evidence-based from re-execution only.

What would have **failed** this audit:

- Any `diff -q` mismatch after H10 re-run.
- Parquet SHA ≠ `f630d8cf20db72ea…`.
- Mutation test pass without detecting `expected=0` for ~4M births.
- Any CSV row with `diff≠0` and `status=pass` where `|diff| > tolerance_abs`.
- `516b621` containing artifact diffs while claiming zero mutation.

None occurred.
