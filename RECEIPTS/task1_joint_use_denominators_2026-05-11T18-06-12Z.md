# Receipt: task1_joint_use_denominators
## 2026-05-11T18:06:12Z

### What was done

Shipped the joint-use convenience layer (NEXT_STEPS.md §15 Task 1, §17 readiness item 3). Three new code artifacts (`shared/helpers/__init__.py`, `shared/helpers/canonical_join_keys.py`, `shared/helpers/build_stratified_denominators.py`) and one new data artifact (`fetal_death/stratified_denominators.csv`). One reference doc rewritten (`docs/JOINT_USE_GUIDE.md`) and three trackers updated (`fetal_death/README.md` companion-project section + version-roadmap, `VERSION_ROADMAP.md` joint-use section status, `NEXT_STEPS.md` §17 checklist item 3).

The convenience CSV gives one row per (`data_year`, `maternal_age_band`, `maternal_race_bridged`, `hispanic_origin`) stratum with a `live_births` count. 4,906 strata across 29 joint-coverage years (1992–2002 + 2005–2022). Per-year sums match `natality/output/validation/external_validation_v1_comparison.csv resident_births` byte-exact for all 29 years (29/29).

The PRE-FLIGHT's Field-value snapshot surfaced cross-product schema divergence on every non-age join key (`year`/`data_year`, `restatus`/`residence_status`, `maternal_race_bridged4`/`maternal_race_bridged`, `maternal_hispanic_origin`/`hispanic_origin`). Resolved by an aliasing helper rather than mutating either shipped schema. A second Field-value gap surfaced at SMOKE Tier 1 (the `natality_v2_residents_only.parquet` convenience file drops `restatus` post-filter) and was handled per Convention 3 by a pre-DO addendum to PRE_FLIGHT_LOG.md — input switched to the full `natality_v2_harmonized_derived.parquet` with the canonical filter applied audit-explicit in the build script. The shipped natality v2.7.0 parquet was not mutated; the convenience layer is purely an additive layer over the existing Zenodo deposit.

### Inputs consumed

- `/Users/yoelplutchok/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet`: 2,202,879,406 bytes, sha256=`9f917a43474eb9e3ed23aa95c714209421c25c29937376651149d22fab934ef0` (locally computed; not in any shipped PROVENANCE.md — see residual risk (c)).
- `/Users/yoelplutchok/Desktop/natality-harmonization/output/convenience/PROVENANCE.md`: build hash `2d3c3d8`, Zenodo v2.7.0 timestamp 2026-04-28T22:53:25Z (referenced for provenance, not read by the build script).
- `natality/metadata/harmonized_schema.csv`: 95 rows; columns `year`, `restatus`, `maternal_age`, `maternal_race_bridged4`, `maternal_hispanic_origin` verified at PRE-FLIGHT.
- `fetal_death/harmonized_schema.csv`: columns `data_year`, `maternal_age`, `maternal_race_bridged`, `hispanic_origin`, `residence_status` verified at PRE-FLIGHT.
- `natality/output/validation/external_validation_v1_comparison.csv`: `resident_births` rows for 1990–2024 used as the per-year benchmark (29 years intersect joint coverage).
- `fetal_death/live_births_by_year.csv`: read for the NCHS-series cross-reference table in JOINT_USE_GUIDE.md.

### Outputs produced

- `shared/helpers/__init__.py`: new, sha256=`e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` (empty marker).
- `shared/helpers/canonical_join_keys.py`: new, sha256=`22287272a4488699228ebcf77d8099cda8c4dd115a5c9516569f99aca3fdaee2`, 65 lines.
- `shared/helpers/build_stratified_denominators.py`: new, sha256=`d1482336b53aeb4de909a5dcb641999c72aee9fc7ebb407e85d36fbe137f578c`, 158 lines. `DESIGN: tracks-current-state` per Convention 2.
- `fetal_death/stratified_denominators.csv`: new, sha256=`6874d5d65e7b3888acf8a833e4fa98063630765e2eeaf6e1c6cb48ad7b0db5c1`, 4,907 lines (1 header + 4,906 strata), 29 years.
- `docs/JOINT_USE_GUIDE.md`: rewritten end-to-end; replaces stub-quality v1 that incorrectly claimed cross-product column-name parity.
- `fetal_death/README.md`: companion-project section expanded; version-roadmap "V4: Natality companion product" replaced with shipped-joint-use-layer note (per NEXT_STEPS.md §16 stale-on-contact entry).
- `VERSION_ROADMAP.md`: joint-use section status → ✅ shipped.
- `NEXT_STEPS.md` §17 item 3: ⏳ → ✅.

### Five-phase trace

- **PRE-FLIGHT**: ✓ at PRE_FLIGHT_LOG.md timestamp 2026-05-11T17:50:48Z (entry + 17:58:10Z addendum). Field-value snapshot enumerated all cross-product join keys; surfaced naming divergence on 4 of 5 keys; resolution: aliasing helper. Addendum: switched input parquet at SMOKE Tier 1 per Convention 3.
- **SMOKE**:
  - Tier 0 (synthetic 8-row fixture): PASS. 6 output strata, sum=7 live births (1 row excluded for `restatus=4`). Idempotent re-run unchanged (sha256 `ffaf2eb5...` both times). Validates: rename helper, filter, age band derivation (incl. age=99 sentinel → null band), null-race preservation (2018+ scenario).
  - Tier 1 (100 real 2022 rows from natality parquet): PASS after addendum. 16 strata, sum=100. All 2022 rows have null `maternal_race_bridged` per NCHS post-2019 source change.
  - Tier 2 (full 2022 natality): PASS. 42 strata × null-race × 7 hispanic codes; sum=3,667,758 = natality validation target byte-exact.
- **DO**: ✓ Tagged `task1-pre-do` at `7b058fc` (the PRE-FLIGHT commit). Build script run on the full harmonized parquet for years 1992–2002 + 2005–2022. Result: 114,886,832 total live births across 4,906 strata; 29 years.
- **VERIFY**: ✓ Three criteria pass (see below).
- **RECEIPT**: ✓ this file.

### Verify results

- **Criterion A — per-year sums match natality validation target**: PASS 29/29 byte-exact. Each year in `external_validation_v1_comparison.csv resident_births` (status=`pass`, diff=0 against CDC residence series) equals the corresponding sum-across-strata in `stratified_denominators.csv`. Values: 1992=4,065,014; 1993=4,000,240; 1994=3,952,767; 1995=3,899,589; 1996=3,891,494; 1997=3,880,894; 1998=3,941,553; 1999=3,959,417; 2000=4,058,814; 2001=4,025,933; 2002=4,021,726; 2005=4,138,349; 2006=4,265,555; 2007=4,316,233; 2008=4,247,694; 2009=4,130,665; 2010=3,999,386; 2011=3,953,590; 2012=3,952,841; 2013=3,932,181; 2014=3,988,076; 2015=3,978,497; 2016=3,945,875; 2017=3,855,500; 2018=3,791,712; 2019=3,747,540; 2020=3,613,647; 2021=3,664,292; 2022=3,667,758. Sum=114,886,832.
- **Criterion B — reproducibility (bit-identical re-run)**: PASS. Re-running `build_stratified_denominators.py --tier full` produced sha256=`6874d5d65e7b3888acf8a833e4fa98063630765e2eeaf6e1c6cb48ad7b0db5c1` unchanged. `diff -q` between the two runs reports no differences.
- **Criterion C — race × year cross-check via independent code path**: PASS 18/18. For years {2000, 2010, 2015, 2017} (chosen to span the V2 era + V1 era + late-V1-bridged-race years), a direct pandas groupby on the natality parquet under `restatus != 4` × `maternal_race_bridged4` × `year` produced cell counts byte-exact to the corresponding sum-across-(age, hispanic) in the stratified denominator. Detailed comparison in session transcript; key cells: 2000 race=1 → 3,194,005; 2010 race=2 → 636,425; 2017 race=4 → 297,624. All 18 cells match.

### Reproducibility

Re-run produces bit-identical output ✓ (sha256 unchanged across two consecutive `--tier full` invocations on the same input parquet). Determinism guarantees: `to_csv` with `lineterminator="\n"` (explicit), sort key on `GROUPBY_COLUMNS` with `na_position="last"`, `groupby` with `observed=True, dropna=False`. No regression noted; no FIX_LOG entry.

### Cross-product re-probe (if applicable)

Tasks that depend on this output: Task 2 (`notebooks/joint_use_demo.ipynb`) is the immediate downstream consumer; this receipt's existence and the JOINT_USE_GUIDE.md worked example unblock it. No retroactive re-verification needed — Task 1 ships new artifacts only and does not mutate any prior validated output.

### Git

- Pre-DO tag: `task1-pre-do`, commit=`7b058fc` (PRE-FLIGHT-only commit).
- Post-RECEIPT tag (to be set after the task commit): `task1-complete`.

### STATUS.md updated

New section dated 2026-05-11T18:06:12Z marking Task 1 complete and §17 item 3 → ✅.

### Self-check (§10): what could I have gotten wrong that VERIFY wouldn't catch?

1. **`maternal_age_band` derivation could disagree with how fetal-death-side users derive theirs.** The helper bins at edges [0, 19, 24, 29, 34, 39, 54] with `right=True`. NVSR conventions exactly match this binning (age 20 → "20-24", age 19 → "<20"). If a user derives bands using `pd.cut` with default `right=True` from `maternal_age` they get the same result; if they accidentally use `right=False` (or off-by-one bins), their numerator strata won't match the denominator's. JOINT_USE_GUIDE.md documents the labels but doesn't ship a `derive_maternal_age_band` exposure on the fetal-death side — users would have to import from `shared/helpers/canonical_join_keys.py`. Mitigation suggested: future receipt could add a fetal_death/scripts smoke test asserting fetal-death's `derive_maternal_age_band(fd['maternal_age'])` produces compatible bands.
2. **Hispanic origin code 9 (Unknown) is treated as a stratum, not a missingness sentinel.** Real NVSR-comparable rate computation often drops unknown-Hispanic records before stratifying. By preserving code 9 as a distinct row, the convenience file lets users see the unknown-Hispanic count per stratum and decide whether to drop or impute. If a downstream notebook accidentally sums the code-9 stratum into "non-Hispanic" (code 0) or into "Hispanic" (codes 1–5), the rates are biased. JOINT_USE_GUIDE.md flags this but doesn't enforce it.
3. **Natality `maternal_race_bridged4` for years 1990–2002 is an "approximate bridge from MRACE@80-81" (per natality schema notes), not the official NCHS bridged race**. For 1992–2002 in this convenience file, race=1 means "White via approximate-pre2003 crosswalk", race=4 means "Asian/PI" from the same approximate crosswalk. Fetal-death-side `maternal_race_bridged` for 1992–2002 uses a different harmonization (`harmonize.py recodes 01→1, 02→2, 03→3, 04-78→4, 99→blank`). The two approximate-bridge methods *probably* produce identical 4-category outputs because the underlying MRACE source-code spaces are the same in those years, but I did not byte-verify that natality's approximate-pre2003 crosswalk produces the same 4-category recode as fetal-death's `harmonize.py`. If they differ, joint-stratified rates for 1992–2002 would be subtly biased on race. This is a soft-flag for a future verify-pass (DECISION_LOG residual risk (a)).
4. **The `live_births` count is a row count under `residence_status != 4`, not a sum of any record-weight field.** Natality v2.7.0 records are unweighted (each row = 1 birth); this is correct for natality. But if a future natality version were to introduce a weight (e.g., a linked-file-style `recwt`), summing rows instead of weights would silently miscount. The build script asserts neither the absence of a weight column nor that rows equal weight sums.
5. **The `task1-pre-do` git tag was set at `7b058fc` — the PRE-FLIGHT-only commit — which precedes the PRE-FLIGHT addendum (17:58:10Z).** The addendum was written to `PRE_FLIGHT_LOG.md` AFTER `task1-pre-do` was tagged but BEFORE any DO mutation. A literal rollback to `task1-pre-do` would lose the addendum entry. The addendum is part of the task commit's tree, so rollback to the pre-DO commit is still semantically correct (it reverts to a state where no canonical DO has happened); but if a future audit reads `task1-pre-do` and expects "everything PRE-FLIGHT-related at this commit," they'd find the addendum missing. Documented here so audit understands the time sequence.
6. **CSV row order within (data_year, age_band) groups depends on pandas's categorical-vs-Int8 sort.** I asserted deterministic re-run; if a future pandas version changes `groupby(observed=True, dropna=False)` ordering, the sha256 would shift even though the data is identical. This is a known L17-class risk for any pinned-sha test. The build script tests SHAPE (row count, sum) not VALUE (sha), so the script-internal SMOKE doesn't pin sha. The receipt records the sha as a snapshot, not a contract.

### Forward-looking HALTs for next session

Per Convention 4. If the next session is Task 2 (`notebooks/joint_use_demo.ipynb`), Task 4 (paper companion), or any task that consumes `stratified_denominators.csv` or the canonical-join-keys helper:

1. **stratified_denominators.csv sha256 unchanged at PRE-FLIGHT time**. If `shasum -a 256 fetal_death/stratified_denominators.csv` does not produce `6874d5d65e7b3888acf8a833e4fa98063630765e2eeaf6e1c6cb48ad7b0db5c1`, the file has been re-derived or edited. Halt and check whether the re-derivation was authorized (e.g., a natality v2.8 with renamed columns landing). If unauthorized, this is an L17-class drift.
2. **canonical_join_keys.py NATALITY_TO_CANONICAL mapping unchanged**. If a future natality v2.8 rename lands and the dict is mutated, the helper's rename becomes a no-op or an inversion. The PRE-FLIGHT should grep `NATALITY_TO_CANONICAL` and verify its content matches this receipt's snapshot before any joint-use code is run on natality v2.8 data.
3. **Joint-use code in any new notebook MUST apply the canonical residence filter on BOTH sides**. Numerator filter: `tabulation_flag == 2 AND residence_status != 4` for fetal-death. Denominator filter: `residence_status != 4` for natality (already pre-applied in the convenience CSV). Per §8 F2; not assertable from the CSV alone since the CSV is post-filter. The next session's PRE-FLIGHT should grep the new notebook for both filter clauses before running.
4. **bridged-race 2018–2022 gap is documented as null cells, not as missing rows**. If a downstream notebook accidentally `.dropna(subset=['maternal_race_bridged'])` before joining, the 2018–2022 strata vanish and the joint denominator is undercounted by ~17M records. JOINT_USE_GUIDE.md caveat 4 documents this; the next session should verify any race-stratified rate-computation code respects the null-or-not policy.
5. **Plan-update candidate for a future session**: propose a natality v2.8 schema rename (`year` → `data_year`, `restatus` → `residence_status`, `maternal_race_bridged4` → `maternal_race_bridged`, `maternal_hispanic_origin` → `hispanic_origin`) so that the cross-product helper becomes unnecessary at the source schema level. This would be a §11 plan-update commit (proposal first, human approval before edits), accompanied by re-running the full 183-target natality validation and a new Zenodo v2.8 deposit. Not done in this task; flagged for a dedicated session.
6. **Convention 3 second-bullet drill**: this task is the first one where a Field-value snapshot caught a divergence (cross-product column-name mismatch) AT PRE-FLIGHT and a second divergence (residents_only.parquet schema gap) at SMOKE Tier 1. Both were resolved without silently proceeding. Future tasks that mutate canonical artifacts should be braced for this pattern — the Field-value snapshot is the cheapest place to surface drift, and the addendum protocol (writing a new dated PRE-FLIGHT entry rather than back-filling the original) is the L10-safe response when divergence surfaces post-PRE-FLIGHT but pre-DO.

### Notes for next session

- The natality `maternal_race_bridged4` vs fetal-death `maternal_race_bridged` recode equivalence for 1992–2002 is unverified (Self-check residual risk 3). A 5-minute cross-check (compute both recodes from the same MRACE input on a 1000-row sample; assert identical) would close this. Suggested for Task 2's PRE-FLIGHT.
- `fetal_death/CODEBOOK.md` was NOT updated by this task — CODEBOOK documents data-file columns, and the convenience CSV is documented in JOINT_USE_GUIDE.md. If the future Zenodo v2.1 deposit ships a flat docs structure, CODEBOOK may need a new section for the convenience CSV; defer to Zenodo-prep time.
- The next obvious task is Task 2 (joint_use_demo.ipynb) which consumes this convenience file. Estimated effort: half a session.
- The natality v2.8 rename proposal (Forward-looking HALT 5) is the cleanest long-term fix for cross-product naming. It is a substantive task (re-run 183-target validation, new Zenodo deposit, breaking-change communication). Recommend bundling with Task 3 (V2.1 fetal-death) or a dedicated session — not a side-effect of Task 2.
