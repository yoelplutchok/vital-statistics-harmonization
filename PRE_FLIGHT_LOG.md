# PRE_FLIGHT_LOG

> **Append-only.** Before every task's DO phase, the LLM appends a PRE-FLIGHT checklist here per the template in `NEXT_STEPS.md` §5.
>
> **Back-fills are forbidden** (per §8 matrix row L10). The PRE-FLIGHT entry's timestamp must precede the first DO commit for that task. If a back-fill is detected (e.g., during receipt drafting), file an L10 entry forensically and remediate via §11 before doing further DO action on that task.
>
> See `NEXT_STEPS.md` §5 for the template.

---

## PRE-FLIGHT for task2_joint_use_demo — 2026-05-11T18:27:14Z

### Inputs
- [x] All required input files exist
  - `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet`: present, 2,202,879,406 bytes, sha256=`9f917a43474eb9e3ed23aa95c714209421c25c29937376651149d22fab934ef0` (matches Task 1 receipt — locally computed, NOT in any shipped PROVENANCE.md; upstream documentation gap carried over from Task 1) ✓
  - `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet`: present, 1,300,258,973 bytes, sha256=`46c169b59b040028d9830546fad71f30d0c6364f10fbc1676b56ae6ee993eb16` (locally computed; same PROVENANCE gap — the v3 linked derived parquet is not enumerated in `/Users/yoelplutchok/Desktop/natality-harmonization/output/convenience/PROVENANCE.md` which only covers convenience parquets) ✓
  - `/Users/yoelplutchok/Desktop/fetal-death-harmonization/fetal_death_derived.parquet`: present, 25,452,090 bytes, sha256=`90af89b9e659ca2b580d8286b5598588cfb2d17e93f26c1dc1ae00d097f0afdd` matches `fetal_death/PROVENANCE.md` v2.0.0 ✓
  - `fetal_death/stratified_denominators.csv` (Task 1 output): present, sha256=`6874d5d65e7b3888acf8a833e4fa98063630765e2eeaf6e1c6cb48ad7b0db5c1` — matches Task 1 RECEIPT Forward-looking HALT 1 byte-exact ✓
  - `shared/helpers/canonical_join_keys.py` (Task 1 output): present, exports `NATALITY_TO_CANONICAL`, `to_canonical_natality`, `derive_maternal_age_band`; `NATALITY_TO_CANONICAL` content verified as exactly `{'year': 'data_year', 'restatus': 'residence_status', 'maternal_race_bridged4': 'maternal_race_bridged', 'maternal_hispanic_origin': 'hispanic_origin'}` — matches Task 1 RECEIPT Forward-looking HALT 2 byte-exact ✓
  - `fetal_death/external_validation_targets.csv`: present, 82 rows, headers `year,metric,metric_detail,expected_value,source,notes` ✓
  - `fetal_death/harmonized_schema.csv`: present, contains `data_year`, `tabulation_flag`, `residence_status`, `maternal_age`, `maternal_race_bridged`, `hispanic_origin` with documented dtypes ✓
  - `docs/JOINT_USE_GUIDE.md`: present, contains "Worked example: fetal mortality rate by maternal race, 2017" (the section that the §15 Task 2 PRE-FLIGHT inputs cite as pseudocode source; the spec's literal year "2022" is stale — see Field-value snapshot below) ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - bootstrap (2026-05-09): ✓
  - protocol-sync `[plan-update]` (2026-05-11, `596e8ce`): ✓
  - task6 (2026-05-11, `efe775d`): ✓
  - task1 (2026-05-11, `4d00ef8`): ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/task2_*.md`: does not exist ✓
  - `notebooks/joint_use_demo.ipynb`: does not exist (only `notebooks/README.md` planned stub describing it) ✓
- [x] Forward-looking HALTs from prior session (Task 1 receipt) verified at PRE-FLIGHT
  - **Task 1 HALT #1** (stratified_denominators.csv sha unchanged): sha=`6874d5d6...` matches receipt ✓
  - **Task 1 HALT #2** (canonical_join_keys.py NATALITY_TO_CANONICAL dict unchanged): 4 entries match receipt byte-exact ✓
  - **Task 1 HALT #3** (canonical filter on BOTH sides): this PRE-FLIGHT commits the policy in the notebook design — numerator filter `(tabulation_flag == 2) AND (residence_status != 4)`; denominator filter `residence_status != 4` (pre-applied in stratified_denominators.csv, re-asserted in the notebook narrative). Tier 0 SMOKE will mutation-verify both filters catch their respective exclusion records.
  - **Task 1 HALT #4** (bridged-race null cells NOT dropna'd): notebook will preserve null-race rows; 2018+ strata in the denominator carry `maternal_race_bridged = NaN`. Section B uses 2017 (race-available year) so this is not an issue for the by-race computation; for the by-age computation (Section A, year 2022) the maternal_race_bridged column is not in the groupby axis, so null-vs-non-null is irrelevant for Section A.
  - **Task 1 HALT #5** (1992-2002 maternal_race_bridged crosswalk equivalence check): incorporated as SMOKE Tier 1 supplementary check — compute natality's `maternal_race_bridged4` from the harmonized parquet on a 1000-row 1995 sample and cross-check against the fetal-death-side recode rule (`harmonize.py`: 01→1, 02→2, 03→3, 04-78→4, 99→null) applied to the equivalent natality MRACE-source values. The receipt will document the result; failure → halt and ask before claiming the by-race joint-use machinery generalizes to pre-2003 era.
  - **Task 1 HALT #6** (Convention 3 second-bullet drill — Field-value-snapshot as the cheapest divergence-surfacer): this PRE-FLIGHT explicitly demonstrates that response — Field-value snapshot below catches a §15-spec / current-state mismatch BEFORE any DO mutation, and amends the plan at PRE-FLIGHT time rather than mid-DO. Per the L10-safe addendum-protocol pattern.

### Environment
- [x] Python version: 3.13.9 (required ≥3.11) ✓
- [x] R version: n/a (Python-only task)
- [x] pandas version: 2.3.2 (required ≥2.3) ✓
- [x] pyarrow version: 18.1.0 (required ≥18.0) ✓
- [x] nbformat version: 5.10.4 (notebook serialization) ✓
- [x] jupyter_client version: 8.8.0 (kernel for executed-output cells) ✓
- [x] Working directory clean (`git status` on `main` at `4d00ef8`): ✓
- [x] On expected branch (`main`): ✓

### Source documentation
- [x] All NVSR PDFs / NCHS user guides referenced — n/a for primary computations; NVSR 73-09 Table 4 8 age cells already encoded in `fetal_death/external_validation_targets.csv` (no PDF re-transcription, zero L9 risk on Section A). Section B (2017 race) does NOT transcribe new NVSR figures (NVSR 67-08 Table I race-stratified-2017 figures are NOT pre-encoded and not re-derived in this task; Section B presents computed rates as a joint-use machinery demonstration with NVSR validation deferred to Task 4).
- [x] All cited Zenodo DOIs resolve — natality concept `10.5281/zenodo.19363074` (v2.7.0=`10.5281/zenodo.19868835`); fetal-death v2.0.0=`10.5281/zenodo.20031571`; not re-fetched (using local parquets, all hash-verified above).

### Outputs
- [x] Intended output paths do not exist OR are explicitly marked for overwrite
  - `notebooks/joint_use_demo.ipynb`: new ✓
  - `RECEIPTS/task2_joint_use_demo_<ts>.md`: new ✓
  - Edits to existing files explicitly intended: `notebooks/README.md` (description currently says "by maternal race, 2022" — both wrong per Field-value snapshot below; update to "by maternal age band 2022 + maternal race 2017"), `NEXT_STEPS.md` §17 item 4 (⏳ → ✅), `STATUS.md`, `DECISION_LOG.md`. Per §11, propose a `[plan-update]` candidate to NEXT_STEPS.md §15 Task 2 description for stale 2022-by-race wording (NOT done as part of Task 2 itself; flagged in receipt Forward-looking HALTs).

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

The §15 Task 2 spec was written at bootstrap (2026-05-09) BEFORE Task 1 discovered the bridged-race-2018+ gap and rewrote `docs/JOINT_USE_GUIDE.md` to use 2017 as the worked-example year. The spec is therefore L11-class stale on the bootstrap-to-Task-1 timeline. Snapshot of the divergence and its resolution:

**§15-spec-vs-current-state divergence**

| §15 Task 2 spec (line 497–519) | Current state (verified at PRE-FLIGHT) | Resolution |
|---|---|---|
| "computes the fetal mortality rate per 1,000 (live births + fetal deaths) by maternal race for 2022" | 2022 has `maternal_race_bridged = null` in BOTH products. `fetal_death/harmonized_schema.csv` line 8 `years_available = 1992-2002, 2005-2017`; `stratified_denominators.csv` 2018-2022 strata all carry null race. NCHS dropped MBRACE from the public-use file for those years. Race-stratified 2022 is physically impossible with shipped data. | Section A in the notebook uses **2022 maternal age band** stratification (race-axis swap forced by data); Section B uses **2017 maternal race** stratification (year-swap forced by data) to preserve the §15 spec's "by race" demonstration intent. |
| "matches each cell against *NVSR 73-09* Table A" | `fetal_death/external_validation_targets.csv` rows attributed to `NVSR 73-09 Table A`: `live_births_total` (denominator), `fetal_deaths_male/female` (by SEX), `fetal_deaths_singleton/twin/triplet+` (by PLURALITY). **Table A has no race stratification.** The spec's "Table A" citation is mis-attributed; correct table for maternal-age stratification in NVSR 73-09 is **Table 4** (8 age cells pre-encoded: `fetal_deaths_age_under15/15_19/20_24/25_29/30_34/35_39/40_44/45_plus` for year 2022). | Section A validates against **NVSR 73-09 Table 4 (8 age cells, all pre-encoded in `external_validation_targets.csv`)** — zero PDF transcription, zero L9 risk. Section B (race) defers NVSR validation to Task 4 (per its §15 spec "reproduce every numeric claim in the manuscript"); Section B presents the joint-use computation as a machinery demonstration only, with cells documented but not NVSR-pinned. |
| "Pseudocode in `docs/JOINT_USE_GUIDE.md` ('Worked example: fetal mortality rate by maternal race, 2022')." | `docs/JOINT_USE_GUIDE.md` line 84 reads "Worked example: fetal mortality rate by maternal race, **2017**" — Task 1 (2026-05-11) rewrote this section using 2017 as the example year explicitly because of the bridged-race-2018+ gap. §15 wasn't updated in lockstep. | Section B follows the JOINT_USE_GUIDE.md 2017 worked example pseudocode verbatim (joint-use machinery demonstration via the canonical helper). The `[plan-update]` candidate for §15's stale "2022" cite is flagged in this task's Forward-looking HALTs (per Convention 4) but is NOT done as part of Task 2 itself — proposed as a separate `[plan-update]` commit. |

**Cross-product join-key column-name state (no divergence vs Task 1)**

| Concept | natality v2.7.0 column | fetal_death v2.0.0 column | Verified at PRE-FLIGHT |
|---|---|---|---|
| Event year | `year` int16 | `data_year` int32 | ✓ (renamed via `to_canonical_natality`; output uses `data_year`) |
| Maternal age | `maternal_age` | `maternal_age` | ✓ (matches; 99 sentinel in fetal-death V2 era → NaN before binning) |
| 4-cat bridged race | `maternal_race_bridged4` | `maternal_race_bridged` | ✓ (renamed; both null for 2018+) |
| Hispanic origin | `maternal_hispanic_origin` | `hispanic_origin` | ✓ (renamed) |
| Residence status | `restatus` | `residence_status` | ✓ (renamed; canonical filter `!= 4` on both sides) |

**Numerator-side fetal-death filter state (Convention 3)**

| Concept | fetal_death schema | Plan assumption | Verified |
|---|---|---|---|
| `tabulation_flag` | `int 1-2`, "1=exclude <20wk; 2=include >=20wk", year coverage 1992-2002 + 2005-2022 | filter = `tabulation_flag == 2` produces NVSR-comparable population | ✓ — `fetal_death/external_validation_targets.csv` 2005-2022 `fetal_deaths_gte20wk_resident` rows reproduce against the parquet's `(tabulation_flag == 2) AND (residence_status != 4)` subset (per the existing fetal-death validation suite; 29/29 byte-exact for the count metric). Already-validated; this task does NOT re-run that validation, but consumes the same filter. |
| `residence_status` | `int 1-4`, "1=Resident; 2=Intrastate nonres; 3=Interstate nonres; 4=Foreign res" | filter = `residence_status != 4` excludes foreign residents | ✓ — same as above |

**NVSR 73-09 Table 4 stratified target snapshot (Section A verify targets)**

| year | metric | expected_value | source |
|---|---|---|---|
| 2022 | `fetal_deaths_age_under15` | 16 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_15_19` | 991 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_20_24` | 3631 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_25_29` | 5071 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_30_34` | 5634 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_35_39` | 3613 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_40_44` | 1138 | NVSR 73-09 Table 4 |
| 2022 | `fetal_deaths_age_45_plus` | 108 | NVSR 73-09 Table 4 |
| **Sum** | (verify against unstratified `fetal_deaths_gte20wk_resident` 2022 = 20,202) | 20,202 | ✓ — table-internal consistency |

**NVSR age bands ≠ helper's 6-band scheme — Section A binning**

`shared/helpers/canonical_join_keys.derive_maternal_age_band` uses 6 bands `<20 / 20-24 / 25-29 / 30-34 / 35-39 / 40+` (Task 1's authoring choice). NVSR 73-09 Table 4 uses **8 bands** including `<15`, `15-19` split (vs the helper's `<20`), and `40-44 / 45+` split (vs the helper's `40+`). Section A's notebook code will compute the 8 NVSR bands directly from `maternal_age` rather than via the helper — the helper stays correct for its joint-use purpose (matching the stratified denominators CSV); the NVSR validation just uses a finer-grained age binning specific to that one comparison. The denominator from `stratified_denominators.csv` for the 2022 by-age comparison can either (a) be re-derived from natality with NVSR's 8-band binning (recommended; ~30 seconds wall-clock on the harmonized parquet), or (b) be aggregated from the existing 6-band CSV with the `<20` and `40+` rows kept whole (acceptable; matches `<15+15-19` and `40-44+45+` sums respectively). Section A uses path (a) for cleanest NVSR-mappable cells, AND demonstrates path (b) sums for cross-check.

**Plan assumptions amended at PRE-FLIGHT (per Convention 3 second bullet)**

1. **Demo year, race-stratified piece**: 2017 (not 2022, per JOINT_USE_GUIDE.md authoritative source). Section B.
2. **Demo year, age-stratified piece**: 2022 (current vintage; matches `external_validation_targets.csv` NVSR 73-09 Table 4 encoded rows). Section A.
3. **NVSR validation scope**: Section A's 8 age cells against NVSR 73-09 Table 4 (pre-encoded). Section B's race cells NOT NVSR-pinned (machinery demonstration only; NVSR validation of race-stratified rates deferred to Task 4 per its scope).
4. **Age binning for Section A**: 8 NVSR bands `<15 / 15-19 / 20-24 / 25-29 / 30-34 / 35-39 / 40-44 / 45+` (derived inline in the notebook from `maternal_age`). Helper's 6-band scheme stays correct for joint-use; the NVSR-specific 8-band scheme is local to this one comparison.
5. **"Loads all three parquets" implementation**: load all three with small column projections; print record counts after canonical filter applied to each; this fulfills the §15 spec's "loads all three parquets, applies each canonical filter" without requiring the linked file in the fetal-mortality-rate computation (linked = infant deaths, not fetal deaths). Demonstrates the unified resource.
6. **Task 1 Forward-looking HALT 5 (1992-2002 crosswalk equivalence)** is incorporated as a SMOKE Tier 1 supplementary check, not as a notebook cell — keeps the notebook focused on the joint-use machinery demonstration; result documented in the receipt.

### Halt conditions tripped
None unresolved. The §15-spec vs current-state divergence (named above) is resolved by amending the task plan at this PRE-FLIGHT moment per Convention 3 and per §15's flexibility ("the spec is a starting point; PRE-FLIGHT may amend based on Field-value snapshot findings"). No previously-stable downstream output is being mutated. The proposed §11 plan-update to §15 Task 2 description is flagged for a separate `[plan-update]` commit (not bundled into Task 2).

### Result
PROCEED.

---

## PRE-FLIGHT addendum for task1_joint_use_denominators — 2026-05-11T17:58:10Z

**Field-value snapshot gap caught at SMOKE Tier 1, resolved pre-DO.** The original PRE-FLIGHT entry (17:50:48Z below) planned to read from `natality_v2_residents_only.parquet`. SMOKE Tier 1 (100 real rows of 2022) failed at parquet-read time:

```
pyarrow.lib.ArrowInvalid: No match for FieldRef.Name(restatus) in year: int16
certificate_revision: string maternal_age: int16 ... [82 column schema]
```

The convenience parquet drops the `restatus` column post-filter — a fact not snapshot in the 17:50:48Z entry's Field-value subsection. Resolution:

1. Switch the build script to read from the full `natality_v2_harmonized_derived.parquet` (2,202,879,406 bytes, locally-computed sha256=`9f917a43474eb9e3ed23aa95c714209421c25c29937376651149d22fab934ef0`). The harmonized parquet carries all 84 columns including `restatus`, and column projection (5 cols out of 84) keeps the read cost roughly equivalent to the residents-only file.
2. Apply the canonical filter `residence_status != 4` in the build script (after the rename helper). This makes the filter audit-explicit rather than relying on the upstream convenience step.
3. Note that the harmonized parquet's sha256 is NOT in any shipped PROVENANCE.md (the natality v2.7.0 deposit's PROVENANCE.md only covers the convenience parquets). This is an upstream documentation gap that I am NOT fixing as part of Task 1 — flagged here for downstream attention.

This addendum precedes the first DO mutation (no canonical output written yet); SMOKE Tier 0 was synthetic and produced only `/tmp/smoke0_out.csv`. The `task1-pre-do` tag remains at commit `7b058fc` (the right rollback point — addendum is still pre-DO).

### Halt conditions tripped
None unresolved. Course correction applied at SMOKE moment per Convention 3.

### Result
PROCEED with build from `natality_v2_harmonized_derived.parquet`.

---

## PRE-FLIGHT for task1_joint_use_denominators — 2026-05-11T17:50:48Z

### Inputs
- [x] All required input files exist
  - `/Users/yoelplutchok/Desktop/natality-harmonization/output/convenience/natality_v2_residents_only.parquet`: present, 1,716,780,400 bytes, sha256=`4c72aaa86c553d53c80c6eb38364c296ebb01636a612ad6664f024b12b153c11` matches `/Users/yoelplutchok/Desktop/natality-harmonization/output/convenience/PROVENANCE.md` v2.7.0 ✓
  - Above parquet's PROVENANCE.md identifies build hash `2d3c3d8` and timestamp 2026-04-28T22:53:25Z; matches Zenodo v2.7.0 (DOI `10.5281/zenodo.19868835`) ✓
  - `natality/metadata/harmonized_schema.csv`: present, 95 rows ✓
  - `fetal_death/harmonized_schema.csv`: present ✓
  - `natality/output/validation/external_validation_v1_comparison.csv`: present; `resident_births` rows confirm byte-exact reproduction for all 35 years 1990–2024 ✓
  - `fetal_death/live_births_by_year.csv`: present, 26 data rows (1995–2002 + 2005–2022) ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - bootstrap (2026-05-09): ✓
  - protocol-sync (2026-05-11, `596e8ce`): ✓
  - task6 (2026-05-11, `efe775d`): ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/task1_*.md`: does not exist ✓
  - `shared/helpers/build_stratified_denominators.py`: does not exist ✓
  - `shared/helpers/canonical_join_keys.py`: does not exist ✓
  - `fetal_death/stratified_denominators.parquet`: does not exist ✓
- [x] Forward-looking HALTs from prior session verified
  - **Task 6 HALT #1** (natality parquet PROVENANCE sha must match file sha at PRE-FLIGHT): sha `4c72aaa…` matches PROVENANCE.md ✓
  - **Task 6 HALT #2** (V3 linked re-validation): not applicable — this task does not re-run V3 linked validation.
  - **Task 6 HALT #3** (Conventions 3/4 non-optional for first canonical-data task): this entry includes the Field-value snapshot subsection per Convention 3 ✓; RECEIPT will include Forward-looking HALTs per Convention 4.
  - **Task 6 HALT #4** (mechanism-attribution wording): out of scope here.

### Environment
- [x] Python version: 3.13.9 (required ≥3.11) ✓
- [x] R version: n/a (Python-only task)
- [x] pandas version: 2.3.2 (required ≥2.3) ✓
- [x] pyarrow version: 18.1.0 (required ≥18.0) ✓
- [x] Working directory clean (`git status` on `main` at `efe775d`): ✓
- [x] On expected branch (`main`): ✓

### Source documentation
- [x] All NVSR PDFs / NCHS user guides referenced — n/a; this task derives stratified counts directly from the validated natality parquet and uses existing validation targets (already PDF-anchored) as the per-year benchmark. No new PDF reads.
- [x] All cited Zenodo DOIs resolve — natality concept DOI `10.5281/zenodo.19363074` (latest = v2.7.0 = `10.5281/zenodo.19868835`); not re-fetched (using local parquet hash-verified above).

### Outputs
- [x] Intended output paths do not exist OR are explicitly marked for overwrite
  - `shared/helpers/__init__.py`: new ✓
  - `shared/helpers/canonical_join_keys.py`: new ✓
  - `shared/helpers/build_stratified_denominators.py`: new ✓
  - `fetal_death/stratified_denominators.csv`: new ✓ (CSV not parquet — `*.parquet` is gitignored repo-wide per `.gitignore` line 2; CSV matches the existing pattern of `fetal_death/live_births_by_year.csv`; expected ~6,000 rows in long format, well under any size concern. Output format amended from the §15 spec's "parquet (or CSV)" wording — §15 explicitly allows either.)
  - `RECEIPTS/task1_joint_use_denominators_<ts>.md`: new ✓
  - Edits to existing files (`docs/JOINT_USE_GUIDE.md`, `fetal_death/CODEBOOK.md`, `fetal_death/README.md`, `VERSION_ROADMAP.md`, `NEXT_STEPS.md` §17, `STATUS.md`, `DECISION_LOG.md`): explicitly intended ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

The original Task 1 spec assumed cross-product column-name parity (`data_year`, `maternal_race_bridged`, `hispanic_origin`, `restatus`). Snapshot of actual schemas shows divergence; resolution documented below.

**Schema-divergence snapshot (cross-product join keys)**

| Concept | natality column (`natality/metadata/harmonized_schema.csv`) | fetal_death column (`fetal_death/harmonized_schema.csv`) | Plan assumed | Divergence resolution |
|---|---|---|---|---|
| Event year | `year` int16 (1990–2024) | `data_year` int32 (1992–2002, 2005–2022) | `data_year` both | Rename at read-time in canonical_join_keys helper; output uses `data_year` |
| Maternal age | `maternal_age` (10–54) | `maternal_age` (10–54;99) | `maternal_age` both | Match ✓ — 99 sentinel in fetal-death; derive age band from non-sentinel values |
| 4-cat bridged race | `maternal_race_bridged4` int8 (1990–2019, null 2020+) | `maternal_race_bridged` int (1992–2002, 2005–2017, null 2018+) | `maternal_race_bridged` both | Rename at read-time; output uses `maternal_race_bridged`; joint-coverage years for non-null bridged race = 1992–2002 + 2005–2017 (24 years); 2018–2022 rows have race=null (documented gap) |
| Hispanic origin | `maternal_hispanic_origin` int8 (codes 0\|1\|2\|3\|4\|5\|9) | `hispanic_origin` int (codes 0–9) | `hispanic_origin` both | Rename at read-time; output uses `hispanic_origin`; code spaces compatible (both expose UMHISP 0–9 with same semantics) |
| Residence status | `restatus` int8 (1\|2\|3\|4) | `residence_status` int (1–4) | `restatus` both | Rename at read-time; canonical filter `residence_status != 4`. Convenience parquet `natality_v2_residents_only.parquet` already applies this filter. |

**Per-year resident_births snapshot (NCHS-series mismatch between two existing artifacts)**

| Year | `natality/output/validation/external_validation_v1_comparison.csv` (CDC residence series; what natality parquet reproduces byte-exact) | `fetal_death/live_births_by_year.csv` (NVSR 57-08 / 73-09 series) | Diff |
|---|---|---|---|
| 1995 | 3,899,589 | 3,899,589 | 0 |
| 1996 | 3,891,494 | 3,891,494 | 0 |
| 1997 | 3,880,894 | 3,880,894 | 0 |
| 1998 | 3,941,553 | 3,941,553 | 0 |
| 1999 | 3,959,417 | 3,959,417 | 0 |
| 2000 | 4,058,814 | 4,058,882 | +68 |
| 2001 | 4,025,933 | 4,026,036 | +103 |
| 2002 | 4,021,726 | 4,021,825 | +99 |
| 2005 | 4,138,349 | 4,138,573 | +224 |
| 2006 | 4,265,555 | 4,265,593 | +38 |
| 2022 | 3,667,758 | 3,667,758 | 0 |

The stratified denominator file reproduces the natality parquet's microdata totals (CDC residence series), which match the natality validation target byte-exact. VERIFY criterion is reframed: sum-across-strata must equal the natality validation target (`external_validation_v1_comparison.csv` `resident_births` for each year), NOT `live_births_by_year.csv`. The latter is preserved as the canonical NVSR-as-published unstratified denominator. The 38–224 record/year discrepancy is documented in JOINT_USE_GUIDE.md, not papered over.

**Plan assumptions amended at PRE-FLIGHT (per Convention 3 second bullet)**

1. **Canonical join-key naming** — output uses fetal_death-style names (`data_year`, `maternal_race_bridged`, `hispanic_origin`, `residence_status`). natality columns are renamed at read-time via a new `shared/helpers/canonical_join_keys.py` helper rather than mutating the shipped natality parquet. Rationale: preserves Zenodo deposit immutability (v2.7.0 stays at its DOI), single source of truth for joint-use code, no breaking change to natality downstream users. A future natality v2.8 rename (Task 11 candidate) is the long-term cross-product parity fix; proposing it as a `[plan-update]` separate from this task.
2. **Output year scope**: 1992–2002 + 2005–2022 (29 joint-coverage years between natality and fetal-death). Years 1990–1991 (natality-only era pre-fetal-death) and 2003–2004 (fetal-death deferred to V2.1) and 2023–2024 (post-fetal-death coverage) excluded from the denominator output.
3. **Bridged race coverage**: 1992–2002 + 2005–2017 populated (24 years); 2018–2022 rows have `maternal_race_bridged = null` (documented gap; users wanting stratified joint-use race rates for 2018–2022 will need to wait for a future task that reconciles `maternal_race_ethnicity_5` vs fetal-death's `race_hispanic_revised`). Cell counts in 2018–2022 stratify on age × hispanic only.
4. **VERIFY criterion 1 reframed**: sum across strata per year matches `natality/output/validation/external_validation_v1_comparison.csv` `resident_births` cell (the natality validation target), not `fetal_death/live_births_by_year.csv` (which uses a different NCHS series). Difference enumerated in the per-year table above.
5. **Age band definition**: <20 / 20-24 / 25-29 / 30-34 / 35-39 / 40+, matching natality's existing `maternal_age_cat` column derivation rule. fetal-death-side users compute the same band from `maternal_age` single year. Sentinel `99` → NaN before binning (per §8 F5).

### Halt conditions tripped
None unresolved. All Field-value-snapshot divergences resolved by amending the task plan in this PRE-FLIGHT (see above) rather than silently proceeding. No previously-stable downstream output (`live_births_by_year.csv`, `external_validation_v1_comparison.csv`, harmonized schemas, manuscript drafts) is being mutated — Task 1 ships new artifacts only.

### Result
PROCEED.

---

## PRE-FLIGHT for task6_linked_validation_reconcile — 2026-05-11T17:05:00Z

### Inputs
- [x] All required input files exist
  - `natality/output/validation/external_validation_v3_linked_comparison.md`: present ✓ (35 PASS / 0 FAIL / 0 MISSING; 2015 `unweighted_infant_deaths` and `postneonatal_deaths` each show Diff=1 but `pass`).
  - `natality/README.md`: present ✓
  - `natality/docs/ABOUT_THIS_RELEASE.md`, `natality/docs/COMPARABILITY.md`, `natality/docs/VALIDATION.md`: present ✓
  - `paper/README.md`, `paper/draft_v1_ipums_styled.md`, `paper/draft_v2_hmd_styled.md`: present ✓
  - Monorepo `README.md`, `NEXT_STEPS.md`, `STATUS.md`: present ✓
- [x] All required upstream tasks marked complete in STATUS.md
  - bootstrap (2026-05-09): ✓
  - protocol-sync `[plan-update]` (2026-05-11, commit `596e8ce`): ✓
- [x] No stale checkpoints from previous incomplete runs of this task
  - `RECEIPTS/task6_*.md`: does not exist (good) ✓

### Environment
- [x] Python version: n/a (docs-only task)
- [x] R version: n/a
- [x] Working directory clean (`git status`): ✓
- [x] On expected branch (`main`, HEAD=`596e8ce`): ✓

### Source documentation
- [x] All NVSR PDFs / NCHS user guides referenced in this task have current SHA-256 matching the relevant `file_inventory.csv`
  - n/a — Task 6 is internal-doc reconciliation; no new NVSR re-verification required.

### Outputs
- [x] Intended output paths do not exist OR are explicitly marked for overwrite
  - `RECEIPTS/task6_linked_validation_reconcile_<ts>.md`: does not exist (good) ✓
  - Edits to existing files (natality/README.md, natality/docs/*, paper/README.md, NEXT_STEPS.md, STATUS.md, DECISION_LOG.md, PRE_FLIGHT_LOG.md): explicitly intended ✓

### Field-value snapshot for cells / rows / columns being mutated (Convention 3)

Target cells enumerated; current values verified against the task plan's assumed state.

| File | Line | Current text (excerpt) | Plan assumes |
|---|---|---|---|
| `natality/README.md` | 19 | `183/183 V2 targets pass, 35/35 V3 linked targets pass` | matches ✓ |
| `natality/README.md` | 27 | `V3 linked external targets 35/35 pass (2005–2023, from NCHS linked user guides)` | matches ✓ |
| `natality/README.md` | 146 | `183/183 and 35/35 are headline numbers, but ... known quirks (e.g., two null-record_weight survivor rows in 2014/2015)` | matches ✓ — soft-flag below |
| `natality/docs/ABOUT_THIS_RELEASE.md` | 80 | `35/35 active pass` | matches ✓ |
| `natality/docs/COMPARABILITY.md` | 367 | `V2 183/183 and V3 linked 35/35 external targets still pass` | matches ✓ |
| `natality/docs/VALIDATION.md` | 206 | `Results: 35/35 active targets pass.` | matches ✓ |
| `paper/README.md` | 18 | `One framing is stale; verify against ...` | matches ✓ (will be marked resolved) |
| `NEXT_STEPS.md` | 440 | `35/35 (or 33/35 + 2 docs diffs — verify; see Task 6)` | matches ✓ (will be resolved) |
| `README.md` (monorepo) | 17 | `33/35 byte-exact (2 cells differ by 1 record from NCHS upstream null-weight survivor records)` | already canonical — no edit ✓ |
| `paper/draft_v1_ipums_styled.md` | 93, `paper/draft_v2_hmd_styled.md` | 94 | `33 of 35 targets ... two cells differ by exactly one record each because of NCHS upstream survivor records with null record weights` | already canonical — no edit ✓ |

- [x] Current values match task plan's assumed state ✓
- Plan assumes the validation file's authoritative state is "35 PASS rows under tolerance; 33 byte-exact + 2 differ by exactly 1 record" — verified by direct read.
- **Soft-flag (DECISION_LOG candidate):** `natality/README.md` line 146 mechanism wording ("two null-`record_weight` survivor rows in 2014/2015") and `natality/docs/VALIDATION.md` line 219 mechanism wording ("LATEREC edge cases") differ from the manuscript canonical mechanism wording ("NCHS upstream survivor records with null record weights"). These three locally-varying mechanism phrasings are out of scope for Task 6 (the task is HEADLINE-count reconciliation); preserving each file's local mechanism wording. Mechanism reconciliation is a separate downstream task if pursued.

### Halt conditions tripped
None.

### Result
PROCEED.
