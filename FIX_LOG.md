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

(no other entries yet)
