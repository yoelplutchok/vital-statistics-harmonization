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

## 2026-05-12T22:30:00Z — C8.1 (followup) — L17-extension — Test-infra basename collision: `pytest fetal_death/tests/ natality/tests/` errors at collection under default import mode because both subprojects ship `test_schema_dtype_parity.py` and neither directory had `__init__.py`

**Symptom:** C8.2 PRE-FLIGHT (2026-05-12T22:30:00Z) verification of STATUS 22:00Z forward-looking HALT #7 ("16 tests across both subprojects") reproduced an `ImportPathMismatchError` / "import file mismatch" collection error:

```
ERROR collecting natality/tests/test_schema_dtype_parity.py
import file mismatch:
imported module 'test_schema_dtype_parity' has this __file__ attribute:
  .../fetal_death/tests/test_schema_dtype_parity.py
which is not the same as the test file we want to collect:
  .../natality/tests/test_schema_dtype_parity.py
HINT: remove __pycache__ / .pyc files and/or use a unique basename
```

Reproducible after `find . -name __pycache__ -delete`. Each subproject's test directory could be run in isolation (`pytest fetal_death/tests/` → 12 passed, 1 xfailed; `pytest natality/tests/` → 3 passed), but the documented combined run failed at collection. The STATUS 22:00Z claim "VERIFY: full pytest run `pytest fetal_death/tests/ natality/tests/` returns **15 PASSED + 1 XFAIL**" was reproducible **only** with `--import-mode=importlib`, an undocumented flag not part of the recorded command.

**Root cause:** Pytest's default import mode (`prepend`) inserts each test directory at the head of `sys.path` and imports the test module by its bare filename (e.g., `test_schema_dtype_parity`). When two test directories without `__init__.py` files contain modules with the same basename, the second import collides with the first under the same fully-qualified name. C8.1 DO-3 authored `fetal_death/tests/test_schema_dtype_parity.py` and `natality/tests/test_schema_dtype_parity.py` simultaneously without adding the `__init__.py` files that would make them namespace-distinct (`fetal_death.tests.test_…` vs `natality.tests.test_…`). The C8.1 VERIFY step ran `pytest fetal_death/tests/ natality/tests/` in a session where pytest happened to silently succeed (likely via a cached __pycache__ or with a different invocation than what was recorded) but the recorded command does not reproduce that result on a clean run.

This is a class L17 cousin — not a stale-pin per se, but a similar pattern: a test-infrastructure assertion (STATUS's "16 tests across both subprojects") was authored at a moment when it held, then became invalid as soon as the test-discovery environment was reset (clean `__pycache__`).

**Fix:** Added four empty `__init__.py` files to make the test suites proper namespace packages:

- `fetal_death/__init__.py` (NEW; empty)
- `fetal_death/tests/__init__.py` (NEW; empty)
- `natality/__init__.py` (NEW; empty)
- `natality/tests/__init__.py` (NEW; empty)

Under this layout, pytest's prepend mode generates the fully-qualified names `fetal_death.tests.test_schema_dtype_parity` and `natality.tests.test_schema_dtype_parity`, which are distinct.

**Files touched (this fix):**
- `fetal_death/__init__.py` (NEW)
- `fetal_death/tests/__init__.py` (NEW)
- `natality/__init__.py` (NEW)
- `natality/tests/__init__.py` (NEW)

**Regression scope:**
- Searched `git ls-files | xargs grep -lE "^(from|import) (fetal_death|natality)\b"` → zero matches. No existing Python code imports either subproject as a top-level package, so the new `__init__.py` files are inert outside of pytest's test-discovery machinery.
- Dry-imported `fetal_death/scripts/03_harmonize/harmonize.py` via `importlib.util.spec_from_file_location` → loads OK (no breakage from the new `__init__.py`).
- All four __init__.py files are empty; no module-level side effects.

**Verified by:**
- `find . -name __pycache__ -path "*tests*" -type d | xargs rm -rf ; pytest fetal_death/tests/ natality/tests/` → `15 passed, 1 xfailed in 38.77s`. Documented STATUS 22:00Z claim now reproducible under default import mode.

**Could the §8 matrix have caught this earlier?** Yes — this is L17-adjacent. The matrix's L17 row names "SMOKE / test asset hard-codes a mutable annotation value pinned at authoring time; canonical state evolves; pin becomes stale; SMOKE FAILs on a CORRECT subsequent mutation." The bug here is the dual: the test infrastructure's *collectability* (not the asserted values) was pinned at a moment when an environmental side-effect (cached `__pycache__`?) hid the basename collision, and the bug surfaced on a clean re-run. Sharpening L17 to cover test-infra-collectability claims, or adding a defense-in-depth invariant ("every documented `pytest <dirs>` command must reproduce its claimed pass count after `find . -name __pycache__ -delete`"), would have caught this at the C8.1 VERIFY moment. Filed as L17-extension; promotion to a §8 row pending C8.6 CI authoring (where automated cache-cleared runs become the durable defense).

**Forward-looking follow-up:** C8.6 (GitHub Actions wiring) runs in clean checkouts where __pycache__ never exists; the cache-cleared discipline becomes free. No additional `pyproject.toml` config needed (the four `__init__.py` are sufficient).

---

## 2026-05-12T22:00:00Z — C8.1 — H8 (latent surface broader than v2.0 incident) — ~50 fetal-death raw harmonized columns ship as pyarrow `string` while schema declares `type=int`; documented via xfail(strict=True) test pending full reconciliation

**Symptom:** C8.1's new `fetal_death/tests/test_schema_dtype_parity.py::test_full_schema_type_matches_parquet_dtype` test FAILed on first run with **49 mismatches**: harmonized_schema.csv declares `type=int` (or `type=float` for `prepregnancy_bmi`) for ~50 columns; the actual parquet ships them as pyarrow `string`. Affected columns include: `delivery_year`, `maternal_age_recode14/9`, `maternal_race_multi`, `maternal_race_recode6`, `maternal_race_bridged_detail`, `race_hispanic_combined`, `race_hispanic_revised`, `maternal_education(_unrevised)`, `marital_status`, `maternal_nativity`, `paternal_age_combined`, `paternal_age_recode11`, `live_birth_order`, `plurality`, `prenatal_care_*`, `delivery_method_*`, `delivery_route`, `prior_cesarean_number`, `gestational_age_clinical/oe_edited/combined`, `gestational_age_recode12/5`, `oe_gest_recode12/5`, `birthweight`, `birthweight_recode14/4`, `fetal_presentation`, `diabetes_unrevised`, `chronic_hypertension_unrevised`, `pregnancy_hypertension_unrevised`, `eclampsia_unrevised`, `tobacco_*`, `prepregnancy_bmi(_recode)`, `cause_recode124`, `cause_reporting_flag`, `attendant`, `delivery_place_*`, `breech_unrevised`, `gestation_imputed_flag`, `obgest_used_flag`.

**Root cause:** The fetal-death v2.0 release shipped these columns as `object`/string because the parser (`parse_fetal_year.py`) extracts each raw field as a fixed-width string slice and `harmonize.py` passes the values through without per-column dtype enforcement. The v2.0 H8 incident (FIX_LOG 2026-05-11T18:50Z) named 5 demographic/filter columns; the v2.1 closure (FIX_LOG 2026-05-12T01:30Z) cast those 5 (tabulation_flag, residence_status, maternal_age, maternal_race_bridged, hispanic_origin) but did not extend the cast to the remaining ~50. The `harmonized_schema.csv` `type=int` declaration was therefore correct as a *conceptual* statement ("this column holds integer-coded values") but inaccurate as a pyarrow-dtype statement.

**Fix (partial; latent state documented):** C8.1 documents this via `test_full_schema_type_matches_parquet_dtype` decorated with `@pytest.mark.xfail(strict=True, reason=...)`. The marker:
- Lets the test live in the suite without blocking PASS.
- Documents the latent state in the test docstring + the xfail reason.
- Will flip to XPASS=FAIL when a future task closes the issue, forcing removal of the marker (and re-evaluation of whether the closure is intentional).

The **strict regression gate** for the original H8 incident is preserved as `test_v21_h8_fixed_columns_remain_int`: the 5 V2.1-cast columns MUST remain int; revert is caught immediately.

**Files touched (this fix):**
- `fetal_death/tests/test_schema_dtype_parity.py` (NEW; 4 tests including the xfail-marked full-parity test)

**Regression scope:** None — this is documentation of a pre-existing latent state surfaced by the new test. No canonical data state mutated. The xfail discipline prevents the latent state from being silently "fixed" by an unrelated future change without explicit reconciliation.

**Verified by:**
- `pytest fetal_death/tests/test_schema_dtype_parity.py::test_full_schema_type_matches_parquet_dtype` returns XFAIL (expected).
- `pytest fetal_death/tests/test_schema_dtype_parity.py::test_v21_h8_fixed_columns_remain_int` returns PASS — the 5 V2.1-fixed columns are still int.
- Manual probe of natality's harmonized_schema.csv: natality uses pyarrow physical type names directly ('int8'/'int16'/'bool'/'string'/...); the natality parity test passes 3/3 strict matches. fetal-death's generic-name convention is the divergence.

**Could the §8 matrix have caught this earlier?** Yes — this is squarely H8 (docs vs data drift) at broader surface than the original v2.0 incident named. The existing matrix recommends "auto-generate every numeric in every doc from the validation CSVs; if a doc number is hand-edited, accompany it with the inline computation it came from" — the analog for schema CSVs is: every schema `type` value must be auto-derived from the parquet's pyarrow schema (or asserted by a test). C8.1's dtype parity test IS this defense, and would have caught the v2.0 incident at build time if it had existed.

**Forward-looking follow-up:** A future Phase C task (TBD; not in current Tier 1+2 plan) reconciles by either:
- **Option A (canonical recommend)**: cast the ~50 columns to appropriate pyarrow integer widths in `harmonize.py` (extending the existing `_apply_h8_int_cast()`); re-derive the parquet; bump fetal-death version v2.x → v2.x+1; SHA update propagates to PROVENANCE.md and the smoke's EXPECTED state.
- **Option B**: rephrase the schema CSV's `type` column to declare 'str' for the string-shipping columns (lower-cost; preserves shipped parquet SHA; arguably more honest since the values are coded-string anyway like "01" maternal_education). Anti-Pattern #6 schema-version bump still applies.

Recommendation: Option A — restores user expectation that 'int' means int filterable. Probably 1 session.

---

## 2026-05-12T22:00:00Z — C8.1 — L13-extension — Monorepo path drift surfaced in `fetal_death/tests/` (sibling of FIX_LOG 2026-05-12T01:30Z); test harness pointed at `fetal_death/output/...` non-existent path + `_regenerate_schema_years.py` missing in monorepo

**Symptom:** During C8.1 input verification, discovered:
1. `fetal_death/tests/conftest.py` parquet/schema constants pointed at `REPO_ROOT/output/harmonized/...` where `REPO_ROOT = fetal_death/`. The monorepo has no `fetal_death/output/` directory; only `output/` at top level (symlinks to standalone-build dir). All smoke tests would `pytest.skip` cleanly (per `_require()` skip-if-missing protocol) — silently failing.
2. `fetal_death/tests/test_release_smoke.py` line 48 imports `from _regenerate_schema_years import compute_years_available`, with sys.path insert pointing at `fetal_death/scripts/`. That file did not exist in the monorepo — only in the standalone build dir's `scripts/`. Test discovery would `ImportError` before any test could run.

Both bugs latent since the 2026-05-09 monorepo migration commit `7fd9cdf`. Same class as FIX_LOG 2026-05-12T01:30Z (harmonize.py + validate_external*.py paths drift) — that fix surfaced 3 cases; C8.1 surfaces 2 more in the test harness.

**Root cause:** Same as the prior L13-extension entry: the monorepo migration treated `fetal_death/` as a static archive (data + docs) rather than a fully-runnable subproject; path-constant updates were applied to runtime scripts (harmonize/validate/derive) but not to the test harness.

**Fix:**
1. Copied `_regenerate_schema_years.py` from `~/Desktop/fetal-death-harmonization-build/scripts/` into `fetal_death/scripts/` with monorepo-adapted paths (`_SUBPROJECT_ROOT.parent / "output/harmonized/..."` instead of `REPO_ROOT / "output/harmonized/..."`; `_SUBPROJECT_ROOT / "harmonized_schema.csv"` instead of `REPO_ROOT / "metadata/harmonized_schema.csv"`).
2. Updated `fetal_death/tests/conftest.py` constants: introduced `SUBPROJECT_ROOT` + `MONOREPO_ROOT` distinction; `HARMONIZED_PARQUET = MONOREPO_ROOT / "output/harmonized/..."`; `SCHEMA_CSV = SUBPROJECT_ROOT / "harmonized_schema.csv"`. Updated `_require()` error-path `relative_to` to use `MONOREPO_ROOT` with graceful fallback.

**Files touched (this fix):**
- `fetal_death/scripts/_regenerate_schema_years.py` (NEW)
- `fetal_death/tests/conftest.py` (path-constants edit)

**Regression scope:** Test suite was effectively non-runnable in the monorepo before this fix. No prior canonical state was affected (the parquets, schemas, validators all ran from their own correct paths). All 9 existing release-smoke tests now run cleanly (12 PASSED + 1 XFAIL after smoke retag).

**Verified by:**
- `pytest fetal_death/tests/` collects and runs 13 tests (no ImportError); 12 PASS + 1 XFAIL.
- `python3 fetal_death/scripts/_regenerate_schema_years.py --check` returns "OK: schema years_available matches data for all 73 columns" (post-regen).

**Could the §8 matrix have caught this earlier?** Yes — L13-extension (path-drift across monorepo migration) is exactly this class. The prior fix (FIX_LOG 2026-05-12T01:30Z) recommended `scripts/run_pipeline.py` end-to-end smoke from monorepo root as the durable defense — that work is scheduled as **C8.7** in the Phase C plan and will surface any remaining path-drift cases. Authoring a `pytest fetal_death/tests/` run at monorepo-migration acceptance time would have caught these two cases.

**Forward-looking follow-up:** C8.7 (end-to-end pipeline smoke from monorepo root) is the authoritative defense against further path-drift surfaces. CI wiring (C8.6) will gate every PR on a clean test run going forward, preventing new path-drift bugs from landing.

---

## 2026-05-12T13:35:02Z — natality_v28_rename — H8 — 3 doc references to `restatus` survived the v2.8 build-dir rename pass

**Symptom:** Post-sync grep of monorepo `natality/` for `\brestatus\b` returned 3 hits: `natality/README.md:38` (`Residents-only subsets (exclude foreign residents; \`restatus != 4\`)` in a docs file-table cell) and `natality/docs/GETTING_STARTED.md:41 + :50` ("Full file with foreign residents + restatus columns" in V2 and V3 file-table descriptors). All three describe the v2.8-renamed column, but the build-dir rename pass overlooked them.

**Root cause:** The build-dir v2.8 rename pass (DECISION_LOG 2026-05-12T03:25Z 14-step plan) targeted `metadata/harmonized_schema.csv`, scripts (string-literal column-name references), and 6 documented docs (`CODEBOOK`, `COMPARABILITY`, `ABOUT_THIS_RELEASE`, `VALIDATION`, `FAQ`, `GETTING_STARTED`). The pass caught the schema rows + the script string literals + most doc backtick references. It missed:
1. `README.md` was NOT in the 6-docs list (the natality build-dir README was treated as a top-level README, not a "doc"); the `restatus != 4` filter expression on line 38 escaped.
2. `GETTING_STARTED.md` was in the list, but the rename caught backtick `\`restatus\`` patterns and missed two bare-word "restatus columns" instances in narrative-text file-table cells.

**Fix:** Edited the 3 lines in both repos (monorepo `natality/README.md` + `natality/docs/GETTING_STARTED.md`; build-dir `README.md` + `docs/GETTING_STARTED.md`). The grep `\brestatus\b` for monorepo now returns zero hits in `natality/` user-facing docs. (3 other occurrences exist in state files — FIX_LOG entries, STATUS sections, PRE_FLIGHT_LOG — which are append-only historical records and intentionally retain the old name where they describe pre-rename state.)

**Files touched (this fix):**
- `natality/README.md` (monorepo + build-dir)
- `natality/docs/GETTING_STARTED.md` (monorepo + build-dir) — `replace_all=true` caught both lines 41 + 50.

**Regression scope:** None — these are user-facing doc strings; the rename does not affect data, validation, or notebook execution. Caught during the routine post-sync `\brestatus\b` grep that runs as part of the v2.8 close-out's verification gate.

**Verified by:**
- `grep -rn '\brestatus\b' natality/ --include='*.md'` returns no hits.
- Build-dir `grep -rn '\brestatus\b' README.md docs/*.md` returns no hits.
- (Scripts still contain `restatus` as a LOCAL PYTHON VARIABLE — `restatus = _to_int_or_null(_get_col(batch, "RESTATUS"), ...)` — which is intentional per the raw-field-name convention. Output column is `residence_status`. Documented in the natality_v28_rename receipt Self-check item 3.)

**Could the §8 matrix have caught this earlier?** Yes — this is squarely **L4 (LLM forgets to propagate fix to sibling)** + **H8 (docs vs data drift)** in combination. The 14-step plan's doc-edit list was incomplete: it should have included `README.md` as a top-level user-facing doc. The cheap-check that would have caught it before this point: at PRE-FLIGHT time, the Field-value snapshot's "edit surface" enumeration could have used a stronger filter than the targeted-sed patterns — specifically a word-boundary grep `\brestatus\b` across ALL markdown in the build dir, not just the 6 listed docs. Proposed plan-update for future schema-rename tasks: the PRE-FLIGHT edit-surface table must specify the regex/grep that enumerates the surface, NOT a curated file list, so that no files are silently omitted from the rename pass. Filed as a residual L4-class catch; documented for future schema renames.

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
