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

## 2026-05-11T18:50:00Z — task2_joint_use_demo — H8 — fetal-death schema documents `int` dtype for five columns shipped as `object`/string in v2.0.0 parquet

**Symptom:** Task 2 SMOKE Tier 1 produced 0 rows when the filter `(fd["tabulation_flag"] == 2) & (fd["residence_status"] != 4)` was applied to the shipped `fetal_death_derived.parquet`. `JOINT_USE_GUIDE.md` documented the filter with int literals, matching `fetal_death/harmonized_schema.csv`'s `type=int` column for `tabulation_flag` (allowed_values `1-2`) and `residence_status` (allowed_values `1-4`). A naive user copy-pasting the worked example would silently filter out 100% of records.

**Root cause:** The shipped v2.0.0 parquet stores **five** demographic/filter columns as pyarrow `object` (Python `str`) dtype, not `int`:

| Column | harmonized_schema.csv `type` | parquet dtype (verified) |
|---|---|---|
| `tabulation_flag` | `int` | `object` (string `'1'`, `'2'`) |
| `residence_status` | `int` | `object` (string `'1'`, `'2'`, `'3'`, `'4'`) |
| `maternal_age` | `int` | `object` (string `'10'`-`'54'`, `'99'`) |
| `maternal_race_bridged` | `int` | `object` (string `'1'`-`'4'`) |
| `hispanic_origin` | `int` | `object` (string `'0'`-`'9'`) |

Natality v2.7.0 columns covering the same concepts ARE int (`year` int16, `restatus` int8, `maternal_age` int16, `maternal_race_bridged4` int8) — confirmed at PRE-FLIGHT. The drift is fetal-death-only.

**Fix:**
- `docs/JOINT_USE_GUIDE.md` line 51 filter table updated to specify string-literal syntax for fetal-death and int-literal syntax for natality, plus a dtype-caveat paragraph immediately below the table.
- `docs/JOINT_USE_GUIDE.md` worked-example code (lines 92-95) updated to use `tabulation_flag == "2"` and `residence_status != "4"` (string literals).
- `notebooks/joint_use_demo.ipynb` (new in Task 2) uses string literals on the fetal-death side and int literals on the natality side throughout; the dtype caveat is documented in the notebook's intro markdown cell.
- `fetal_death/harmonized_schema.csv` was NOT edited (anti-pattern #6: schema edits require a schema-version bump). A future task will reconcile the schema doc to match shipped state.

**Files touched (this fix):**
- `docs/JOINT_USE_GUIDE.md`
- `notebooks/joint_use_demo.ipynb` (new)
- `notebooks/_build_joint_use_demo.py` (new — deterministic notebook builder)
- `notebooks/README.md`
- This `FIX_LOG.md` entry

**Regression scope:** None — Task 2 surfaced this; no prior task touched these filter columns directly. The natality-side derivation in Task 1 (`build_stratified_denominators.py`) is unaffected (natality columns are int, not object). The fetal-death validation pipeline (`fetal_death/scripts/05_validate/`) is unaffected — it presumably already accommodates the actual shipped dtype since the existing per-year validation passes 29/29 byte-exact.

**Verified by:**
- Section A in `notebooks/joint_use_demo.ipynb` reproduces NVSR 73-09 Table 4 8/8 age cells byte-exact for 2022 using the string-literal filter.
- Section B reproduces 2017 race-stratified joint-use counts cell-by-cell across both denominator paths.
- SMOKE Tier 0 mutation tests verify the corrected string-comparison filter excludes the correct records on a 10-row hand-constructed fixture.

**Could the §8 matrix have caught this earlier?** Yes — this is squarely an **H8 (docs vs data drift)** instance. The schema-doc claim `type=int` was not auto-checked against the parquet's pyarrow schema at validation time. The mistake-class matrix recommends "Auto-generate every numeric in every doc from the validation CSVs; if a doc number is hand-edited, accompany it with the inline computation it came from" — analogously, every shipped harmonized_schema.csv `type` value should be auto-derived from the parquet's pyarrow schema (or asserted by a `tests/` smoke that loads the parquet and compares column dtypes to the schema CSV). Proposed follow-up:

1. Add a `tests/test_schema_dtype_parity.py` smoke harness in `fetal_death/tests/` that reads the parquet, reads `harmonized_schema.csv`, and asserts dtype parity for every row.
2. When the schema-doc reconciliation task lands (schema-version bump), make the parity test the gate that prevents recurrence.

This follow-up is recommended for a future task; not bundled into Task 2 to keep scope tight.

---

## 2026-05-12T01:30:00Z — task3_v21_fetal_death — H8 closure — fetal-death v2.1.0 parquet reconciles 5 demographic/filter dtypes to nullable Int matching the schema CSV

**Symptom (closed):** v2.0.0 `fetal_death_derived.parquet` stored 5 columns (`tabulation_flag`, `residence_status`, `maternal_age`, `maternal_race_bridged`, `hispanic_origin`) as `object`/string despite `fetal_death/harmonized_schema.csv` declaring them as `int`. Open since 2026-05-11T18:50:00Z (Task 2 surface).

**Root cause:** No dtype-parity assertion existed in the parse → harmonize → derive pipeline; the schema CSV's `type=int` claim was unenforced.

**Fix:** Bundled into Task 3 V2.1 build per DECISION_LOG 2026-05-11T20:50Z's data-first sequencing choice. `fetal_death/scripts/03_harmonize/harmonize.py` now applies `_apply_h8_int_cast()` after the per-year concat:
- `tabulation_flag` → Int8
- `residence_status` → Int8
- `maternal_age` → Int16 (matches natality v2.7.0 dtype)
- `maternal_race_bridged` → Int8
- `hispanic_origin` → Int8

Empty strings become `pd.NA`; sentinel ints (e.g., `maternal_age=99`) are preserved. `pd.to_numeric(errors='raise')` fail-loud catches any non-numeric drift.

**Files touched (this fix):**
- `fetal_death/scripts/03_harmonize/harmonize.py` (cast function + module-level dtype map)
- `fetal_death/scripts/05_validate/validate_external.py` (int-literal filter)
- `fetal_death/scripts/05_validate/validate_external_v2.py` (int-literal filter)
- `fetal_death/quickstart.py` (int-literal filter)
- `docs/JOINT_USE_GUIDE.md` (int-literal filter + dtype reconciliation note)
- `notebooks/_build_joint_use_demo.py` (int-literal filter + dtype note)
- `notebooks/_build_paper_companion.py` (int-literal filter)
- `notebooks/joint_use_demo.ipynb` (rebuilt; 9 PASS)
- `notebooks/paper_companion.ipynb` (rebuilt; 34 PASS, 0 FAIL)
- New v2.1.0 parquet: `fetal_death_harmonized.parquet` sha=`333e1e66…d9e0`; `fetal_death_derived.parquet` sha=`55d3d310…c447`.

**Regression scope:** V1-era 2005-2022 byte-clean: 55/55 external validation passes still (validate_external.py); V2-era 1992-2002 13 counts + 8 rates pass (validate_external_v2.py); 2003-2004 NEW 2 counts + 2 rates pass byte-exact against fetaldeath0304problems.pdf Table 1. **Total: 78/78 checks pass** (was 13 counts + 8 rates + 55 V1 = 76 before V2.1; now 13+10+55 = 78). Joint-use demo's 8/8 NVSR Table-4 age-band cells still byte-exact.

**Verified by:**
- `validate_external_v2.py` 23/23 (1992–2004 counts + 1995–2004 rates).
- `validate_external.py` 55/55 (V1 era unchanged).
- `_build_joint_use_demo.py` and `_build_paper_companion.py` re-run; no FAILs.

**Could the §8 matrix have caught this earlier?** It DID (H8 itself was the catch, at Task 2). The follow-up `tests/test_schema_dtype_parity.py` proposed in the 2026-05-11 entry remains valuable but not yet implemented; added to the post-submission queue.

---

## 2026-05-12T01:30:00Z — task3_v21_fetal_death — pre-existing-bug — `data_year` int32 init silently overwritten by crosswalk's `derived` field loop

**Symptom:** After re-deriving the V2.1 parquet, `validate_external_v2.py` returned 0/23 PASS. Root cause: `data_year` column was `object` (empty string) dtype in the harmonized parquet, breaking the int comparison `harm["data_year"] == year`.

**Root cause:** `harmonize_year()` initialized `data_year` as `int32` via `harmonized: dict[str, pd.Series] = {"data_year": pd.Series([year] * len(raw), dtype="int32")}`. The subsequent `for hname, era_map in field_map.items()` loop iterated over every crosswalk row, including the `data_year` row whose `field_2006` (etc.) is the literal string `"derived"`. The loop's else-branch fired (since `"derived"` is not a real raw column), overwriting the int32 series with `[""] * len(raw)` (object empty-string).

**Fix:** Added `if raw_field == "derived": continue` inside `harmonize_year()`'s field-map loop. The int32 initialization is preserved.

**Files touched:** `fetal_death/scripts/03_harmonize/harmonize.py`.

**Regression scope:** This bug presumably existed in v2.0.0 too. v2.0.0 derived parquet's `data_year` dtype: `int32` (verified at `/Users/yoelplutchok/Desktop/fetal-death-harmonization/fetal_death_derived.parquet`, sha `90af89b9…`). So either v2.0.0 ran a different harmonize.py path or `_apply_sentinels` (which v2.0.0 may have used) was repairing the dtype. The latent-bug commit history is not traced; the fix here is forward-compatible and produces int32 in v2.1.0 matching v2.0.0.

**Verified by:** Post-fix harmonize → derive → validate_external_v2.py: 23/23 PASS.

**Could the §8 matrix have caught this earlier?** L7 (LLM accepts plausible-looking output) is closest — the bug went unnoticed because the v2.0.0 validator might have passed even with the wrong dtype, or v2.0.0 used a different path. Adding `tests/test_schema_dtype_parity.py` (per the H8 closure follow-up) would catch this class of bug at build time.

---

## 2026-05-12T01:30:00Z — task3_v21_fetal_death — pre-existing-monorepo-path-drift — `harmonize.py` + `validate_external*.py` paths pointed at non-existent `fetal_death/metadata/` subdirectory

**Symptom:** `python3 fetal_death/scripts/03_harmonize/harmonize.py --years 2003 …` failed with `FileNotFoundError: fetal_death/metadata/variable_crosswalk_working.csv`. Same issue for `validate_external.py` and `validate_external_v2.py`.

**Root cause:** Pre-existing from the monorepo migration commit `7fd9cdf` (2026-05-09). The standalone `yoelplutchok/fetal-death-harmonization` repo had a `metadata/` subdirectory; the monorepo flattened it to `fetal_death/` per PROJECT_STRUCTURE.md but did not update the path constants in the scripts. The bug was latent because the harmonize step had not been re-run from the monorepo yet — the existing v2.0.0 parquet predated the monorepo migration.

**Fix:** Updated `_CROSSWALK_CSV`, `_SCHEMA_CSV`, `_HARM_PATH`, `_DERIVED_PATH`, `_TARGETS_PATH`, `_OUT_PATH`, `_YEARLY_DIR` in:
- `fetal_death/scripts/03_harmonize/harmonize.py`
- `fetal_death/scripts/05_validate/validate_external.py`
- `fetal_death/scripts/05_validate/validate_external_v2.py`

`_PROJECT.parent` (the monorepo root) now resolves to the symlinked `output/` and `raw_data/`; `_PROJECT` (the `fetal_death/` subdir) resolves to the flat metadata layout.

**Regression scope:** None. The scripts had never been runnable from the monorepo state.

**Verified by:** Successful harmonize → derive → validate runs this session.

**Could the §8 matrix have caught this earlier?** Yes — running ANY of the 3 scripts as part of monorepo-migration acceptance testing (`scripts/run_pipeline.py` end-to-end smoke from the monorepo root) would have surfaced this. The original monorepo migration treated `fetal_death/` as a static archive (parquets-and-docs) rather than a runnable pipeline.

**Forward-looking follow-up:** Other scripts in `fetal_death/scripts/` (`parse_fetal_year.py`, `derive.py`, `run_pipeline.py`, `tests/conftest.py`) may have similar path-drift bugs not yet surfaced. Recommended: post-submission, do an end-to-end `scripts/run_pipeline.py` smoke from the monorepo root and fix any path-drift findings as L13-style "fix on contact" patches.
