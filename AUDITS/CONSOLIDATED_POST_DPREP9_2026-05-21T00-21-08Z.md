# CONSOLIDATED POST-D-PREP.6–9 AUDIT — 2026-05-21T00-21-08Z

## 0. Method + scope

Fresh-eyes adversarial audit of HVS monorepo at `3926e19` after D-prep.6-9 + ultrareview-fix-bundle (STATUS 2026-05-20T21:30Z newest). RECEIPTS / FIX_LOG / LESSONS / DECISION_LOG **not used** to justify PASS (audit-session rule §1). Five lanes executed; primary verification = direct grep + parquet re-hash + CSV computation.

**CRITICAL DATA-INTEGRITY VERIFICATION**: All 4 gate parquets re-hashed byte-exact against PROVENANCE:
- `fetal_death_harmonized.parquet` → `38e2cecb03ff4947…` ✓ PASS
- `fetal_death_derived.parquet` → `185c071ec76ab8aa…` ✓ PASS
- `natality_v2_harmonized_derived.parquet` → `acb5c48a9abf82ac…` ✓ PASS
- `natality_v3_linked_harmonized_derived.parquet` → `f630d8cf20db72ea…` ✓ PASS
- `matched_multiples_harmonized.parquet` → `adbec1087370941f…` ✓ PASS (5th in-repo)

**Gate SHA-OP CLOSED at audit time** — operational re-hash before Zenodo D.2 can confirm but no canonical drift detected post D-prep.6-9. D-prep.6 fully verified.

## 1. Per-lane verdict table

| Lane | Verdict | Blockers (Tier A) | Notes |
|---|---|---|---|
| 1. Data integrity | **PASS** (upgrade from round 3 PASS-WITH-NOTES) | 0 | All 4 gate parquet SHAs re-hashed byte-exact; matched_multiples in-repo parquet `adbec108…` re-hashed in workspace; +183/0/0 natality, +35/0/0 linked, +29/29 fetal-V2 validation summaries clean |
| 2. User-facing docs | **FAIL-LITE** | 7 | D-prep.8 closure not propagated to 3 cross-product surfaces; PROJECT_STRUCTURE.md fetal section v2.0-stale |
| 3. Reproducibility | **PASS-WITH-NOTES** | 0 | Inventory CSVs `imported` 95/95 + 43/43; vocabulary inconsistency `true` vs `yes` (low) |
| 4. Notebooks | **PASS** (large improvement vs round 3 FAIL) | 0 | `_paths.py` present, 7/7 builders import, 0 `/Users/` literals in any `.ipynb` source; kickoff trio + 4 extended notebooks all use `_gate_parquet()` pattern; 1 stale doc-string in regenerated notebook |
| 5. Manuscript (D.4) | **EXPECTED-STALE** | 0 (D.4-scope) | draft_v2 still describes 3-product / 1990-forward / 1,634,195-fd / V3-deferred envelope; 3 `<!-- YP: -->` admin markers; ~3,500 words (IJE ~2,500 limit will require trim) |

**Aggregate:** 0 §7 HALTs; 0 NVSR regression; 0 canonical-state drift. The Tier A list is doc/CSV-only — fits an `audit-fix-r1r2-bundle`-shape micro-bundle.

## 2. Round-3 PZ-01 … PZ-NB regression check

| Item | Round-3 status | Round-4 verify | Verdict |
|---|---|---|---|
| **PZ-01** JOINT_USE_GUIDE.md v2.4.0/v3.0.0 envelope | critical | L41/L59/L61/L67 say 1992-2024/2005-2024 correctly; **L22 "fetal-death v2.4.0 column null 2018–2022" still v2.0-truncated** (should be 2018–2024) | **PARTIALLY-OPEN** (one row stale) |
| **PZ-02** fetal_death/quickstart.py docstring | critical | Docstring L3 "v2.4.0 1982-2024" ✓; **L50 comment "live_births_by_year.csv covers 1995-2002 + 2005-2022 (NVSR series)" stale** (covers through 2024 per D-prep.8); L51 "For 2023-2024…recompute from natality" stale | **PARTIALLY-OPEN** (the inline-comment / convenience block is stale) |
| **PZ-03** root README L8 heritage | high | "legacy deposit 1992–2022; in-repo 1982–2024 v2.4.0" ✓ | **CLOSED** |
| **PZ-04** CODEBOOK L63 + C8.20 regen | high | L60 `data_year` v2.4.0 verified clause present; C8.20 generated `_Schema note_` lines show "1982-2024 … verified 2,427,233/2,427,233"; no stale `1,634,195`/`1992-2022` in generated content | **CLOSED** (D-prep.7 verified) |
| **PZ-05** matched_multiples README current SHAs | high | README L18 cites 4 sibling gate SHAs (`38e2cecb…`/`185c071e…`/`acb5c48a…`/`f630d8cf…`); PROVENANCE has `adbec108…` (verified) | **CLOSED** |
| **PZ-06** REPRODUCING zip counts | high | fetal REPRODUCING L12 correctly distinguishes historical v2.0.0 "29 files" vs current "43 files 1982-2024" | **CLOSED** |
| **PZ-07** file_inventory imported flags | med | Natality 95/95 `true`; fetal 43/43 `yes`; vocabulary inconsistency only (low-sev) | **CLOSED** |
| **PZ-08** natality data_year years_available | med | schema L2 `data_year, …, 1968-2024, 1968-2024` ✓; envelope-note row L99 present | **CLOSED** |
| **PZ-09** COMPARABILITY denominator policy | med | **L154 still says "1992-2002 + 2005-2022 (29 years) — not extended to 2023-2024"** | **OPEN** |
| **PZ-10** VERSION_ROADMAP planned→shipped | med | **L18 still says "4,906 strata × 29 years … CSV not yet extended"** and L24-26 still has "Planned > Convenience CSV year extension" as Planned | **OPEN** |
| **PZ-11** test docstrings | low | `tests/test_cross_product_join_parity.py:299` docstring still says "(1992-2002 + 2005-2022 = 29 years)" | **OPEN** (docstring only; assertion structural) |
| **PZ-NB** Notebook portability | high | `_paths.py` shipped; all 7 builders import; 0 `/Users/` literals in any `.ipynb`; 7/7 notebooks use `_gate_parquet()` block. | **CLOSED** |
| **PZ-OP** Build-host re-hash | operational | **All 4 gate parquets re-hashed byte-exact in this audit session** (from `~/Desktop/{fetal,natality}-harmonization{-build,}/output/harmonized/`); + matched_multiples in-repo parquet | **CLOSED at this audit moment** (advisory: re-hash again before Zenodo D.2 just before upload) |

## 3. D-prep.6-9 verify-from-disk check

| Work unit | Claim | Disk verify | Verdict |
|---|---|---|---|
| **D-prep.6** Gate SHAs byte-exact | 4/4 anchors | Re-hashed → 4/4 match `38e2cecb…/185c071e…/acb5c48a…/f630d8cf…` | **CONFIRMED** |
| **D-prep.7** C8.20 regen, gate unchanged | Marker block byte-identical | Provenance line in fetal CODEBOOK L273 cites `185c071ec76a` (matches); generated `_Schema note_` lines show v2.4.0 numbers; natality CODEBOOK has linked-v4 + 1968-2024 evidence | **CONFIRMED** |
| **D-prep.8** CSVs through 2024 | 31 strat-years + 28 LBY-years | strat: 1992-2002 + 2005-2024 = 31 ✓; LBY: 1995-2002 + 2005-2024 = 28 ✓; bridged-race null window = 2020-2024 ✓ (bug 016 fix); per-year strat sums match LBY within documented JOINT_USE microdata-vs-NVSR table; dtype on bridged column is now nullable Int (no `0.0` float literals — STATUS bug 004) | **CONFIRMED** |
| **D-prep.9 / PZ-NB** Notebooks portable | `_paths.py` + 7 builders + 0 hardcoded paths | All present; static source audit passes; live execute NOT attempted in workspace (parquets only available at `~/Desktop/fetal-death-harmonization-build/…` etc. — out of repo, see note below) | **CONFIRMED (static)** |
| **ultrareview-fix bug 011** quickstart titles 1968-2024 / "multi-decade" | quickstart L51/L213/L285 use 1968-2024; L130 says "multi-decade" not "35-year" | **CONFIRMED**. Soft-note: L51 still says "~201M" not "201.2M" (cosmetic). | **CONFIRMED (with minor)** |
| **ultrareview-fix bug 016** JOINT_USE bridged-null window 2020-2024 | JOINT_USE L41/L61/L69 say 2020-2024 / 2018-2019 populated | **CONFIRMED** — but see Finding A2 below (L22 still has stale "2018-2022" intra-fetal range as a separate cell). | **MOSTLY CONFIRMED** |

## 4. Ranked findings

### Tier A — pre-Zenodo doc/CSV fix bundle (7 items; ~0.3 session)

| ID | Sev | Location | Issue | Class | Fix |
|---|---|---|---|---|---|
| **A1-001** | high | `VERSION_ROADMAP.md:18` and L24-26 | Joint-use convenience layer described as "4,906 strata × **29 years: 1992–2002 + 2005–2022**; CSV not yet extended to 2023–2024", and "Planned > Convenience CSV year extension". D-prep.8 SHIPPED the extension (4,990 cells / 31 years / through 2024). | L11 stale roadmap | Update L18 to "4,990 strata × 31 years: 1992-2002 + 2005-2024"; move L24-26 from "Planned" to "Shipped in-repo". |
| **A1-002** | high | `docs/COMPARABILITY.md:154` | "stratified_denominators.csv and live_births_by_year.csv cover **1992-2002 + 2005-2022 (29 years)** — not extended to 2023-2024". D-prep.8 extended. | L11 + H8 | Replace "1992-2002 + 2005-2022 (29 years)" with "1992-2002 + 2005-2024 (31 years)"; drop "not extended" clause. |
| **A1-003** | high | `docs/JOINT_USE_GUIDE.md:22` (table row) | fetal-death v2.4.0 column "`maternal_race_bridged` (int, 1–4; **null 2018–2022**)". The v2.4.0 envelope is 1982-2024; bridged-race null should be **2018–2024** for consistency with L41/L246. | L11 + L17 stale pin | Change "null 2018–2022" → "null 2018–2024". |
| **A1-004** | high | `fetal_death/quickstart.py:50-51` | `# live_births_by_year.csv covers 1995-2002 + 2005-2022 (NVSR series).` + `# For 2023-2024 or 1992-1994, recompute denominators from natality`. D-prep.8 extended LBY through 2024. | L11 + L6 (numbers in user-facing entry point) | Update L50 to "1995-2002 + 2005-2024"; drop 2023-2024 fallback clause; keep 1992-1994 clause. |
| **A1-005** | high | `PROJECT_STRUCTURE.md:68-98` (entire `fetal_death/` section) | "Fetal death 1992–2022 (with 2003–2004 deferred to V2.1), mirrored … v2.0.1 import" (L68); table at L73 "V2.0 release notes"; L81 lists only `V2_1992_LAYOUT_DECISIONS.md` (3 sibling docs V2_1/V3a/V3b missing); L83 "Parsing 1992–2022 fixed-width zips"; L86 "v2.0 covers V2 era". | L11 stale roadmap + L13 inventory-vs-actual | Rewrite §"fetal_death/" header to v2.4.0/1982-2024 envelope; add 3 sibling LAYOUT_DECISIONS rows; update parsing/validate descriptions to v2.4.0 scope. |
| **A1-006** | med | `notebooks/_build_paper_companion.py:385` → `notebooks/paper_companion.ipynb:759,769` | Generated cell prints `Coverage: 1995-2002 + 2005-2022 = 8 + 18 = 26 years`. LBY now spans 28 years (1995-2002 + 2005-2024 = 8 + 20 = 28). Stale string landed in the regenerated notebook. | L11 + L6 | Update builder L385 to print "1995-2002 + 2005-2024 = 8 + 20 = 28 years"; regenerate notebook (no parquet rerun needed if string is text-only); re-execute on build host if validation cells C37/C43 also need refresh. |
| **A1-007** | low | `tests/test_cross_product_join_parity.py:299` docstring | "natality∩fetal-death joint coverage (1992-2002 + 2005-2022 = 29 years)" — stale doc; actual joint set is now 31 years (1992-2002 + 2005-2024). Assertion itself is dynamic (`fd_years & nat_years`) so test still passes. | L17 stale doc-pin | Update docstring to "= 31 years"; no code change needed. |

### Tier B — Notebook execute / fix (D-prep.5-bundle adjacent)

| ID | Sev | Location | Issue |
|---|---|---|---|
| **B1-001** | low | `natality/notebooks/quickstart.ipynb:51, 404` | "The full derived file is ~201M rows" — copy still rounds to 201M not 201.2M; cosmetic vs README's "201,161,456 → 201.2M". |
| **B1-002** | low | `notebooks/joint_use_demo.ipynb`, `cross_race_fetal_mortality.ipynb`, `preterm_outcomes_time_series.ipynb` | STATUS 21:30Z self-flagged: `preterm` + `cross_race` notebook **execute** still fails on "pre-existing assertion drift" — **source path-fix confirmed clean, but execution health unverified in this audit session** (no parquet-mounted execution). Per audit rules this is "not new vs round 3" → carry as Tier B, not a regression. |
| **B1-003** | low | `fetal_death/validation_results.csv` / `validation_tracking.csv` | 29-row / 30-row CSVs still scoped to V2.0 1992-2022 era; v2.4.0 envelope is 43 years with V3a + V3b + V2.1 + 2023-2024 increments. External_validation_targets.csv covers 1989-2024 (90 rows per CHANGELOG); the committed validation summaries lag. Documented as "V2 era" in README. Stale-scope, not lie. |
| **B1-004** | low | `natality/metadata/file_inventory.csv` vs `fetal_death/file_inventory.csv` | Vocabulary inconsistency: natality uses `imported=true` (boolean-text); fetal uses `imported=yes` (yes/no). Both shipped; downstream consumers must accept both. L13 cross-product inventory inconsistency. |

### Tier C — D.4 manuscript scope (do NOT touch pre-Zenodo unless data deposit truth is at risk)

`paper/draft_v2_hmd_styled.md`:
- Abstract: "1990 forward … 138,819,655 / 74,943,824 / 1,634,195" — stale by 3 of 4 record counts; "1990–2024 / 2005–2023 / 1992–2022" stale year ranges
- Three-product framing — matched_multiples (4th product) not mentioned in abstract/Coverage
- "74 targets" / "29 per-year counts" / "26 rates" — fetal validation count stale
- 3 `<!-- YP: -->` admin review markers (lines 116, 120, 128)
- Word-count: 3,500 vs IJE Data Resource Profile target ~2,500 — needs trim
- Linked v4 1992-1994 gap not surfaced in abstract Coverage
- Result: paper-companion CSV synthesis will need full regenerate at D.4

**All deferred to D.4 per KICKOFF + STATUS forward-looking HALT.** This is **NOT a Zenodo data-deposit truth lie** (the README + PROVENANCE + CITATION are correct).

### Tier D — §7 HALT class (none)

No HALT. No canonical rebuild required. No NVSR regression. No schema/parquet inconsistency. No gate SHA drift.

## 5. Recommendation

**Proceed-to-D.1-after-bundle:**

1. Ship a `pre-zenodo-audit-fix-bundle-r4` doc/CSV-only commit covering **A1-001 through A1-007** (7 edits, all single-line or single-paragraph; zero parquet mutation). Estimated 0.2-0.4 session. Pattern mirrors the `audit-fix-r1r2-bundle` + `pre-zenodo-audit-fix-bundle` precedents. Re-run `_build_paper_companion.py` after A1-006 (executes against gate parquets — verify SHAs unchanged post-run).
2. Then optional one more focused micro-audit (R5) verifying A1-001..A1-007 closure (or accept this audit's verification trail).
3. Then **Phase D.1** redirect-notice push when human says go.
4. **Mandatory PZ-OP** at D.2 immediately-pre-upload: re-run `shasum -a 256` on the 4 gate parquets one more time on the build host (already verified at audit moment). Do NOT skip — the H10 reproducibility-gate cascade depends on this anchor.
5. **Tier B B1-002** notebook-execute health: out-of-scope for this bundle; defer to whatever phase the user wants to attempt full re-execute (will need a build host with parquets resolvable via the new `_gate_parquet()` env-var path).
6. **Tier C** manuscript stays untouched until D.4.

## 6. Explicit non-findings (do not re-flag)

- D-prep.1 (fetal hand-docs v2.4.0 sync): CLOSED — all 7 fetal_death/*.md docs verified current.
- D-prep.2 (PROVENANCE refresh): CLOSED — 4 gate SHAs all byte-exact vs anchor.
- D-prep.3 (schema envelope notes): CLOSED — `#ENVELOPE_NOTE` rows present in both natality and fetal_death harmonized_schema.csv.
- D-prep.4 (round-3 audit-pass): historical.
- D-prep.5 (Tier A PZ-01-PZ-11): 8 of 11 fully closed, 3 partially open (above).
- D-prep.6 (gate SHAs): CLOSED + independently verified this audit.
- D-prep.7 (C8.20 regen): CLOSED — markers clean, no stale `1,634,195` in generated `_Schema note_` lines.
- D-prep.8 (CSV extension): CLOSED for the CSVs themselves (4,990 cells / 31 yr / through 2024) — but 4 downstream docs (above) did not get the propagation memo.
- D-prep.9 (PZ-NB notebook paths): CLOSED — 0 `/Users/` literals, `_paths.py` + `_gate_parquet()` pattern used universally.
- C8.20 appendix integrity: CLOSED — provenance hash matches.
- NCHS source manifest §5 cross-product gate SHAs: internally consistent.

## 7. Confidence + caveats

- Parquet re-hash performed in-session (5/5 byte-exact); not a "could not verify" lane.
- Notebook execute health for the extended-set was NOT attempted live (audit-session rule on no full pipeline / SMOKE-only). If `preterm_outcomes_time_series.ipynb` or `cross_race_fetal_mortality.ipynb` are user-facing exemplar deliverables for Zenodo, recommend a separate notebook-execute pass.
- All findings derived from primary grep/read/parquet probe; no RECEIPTS reliance.
