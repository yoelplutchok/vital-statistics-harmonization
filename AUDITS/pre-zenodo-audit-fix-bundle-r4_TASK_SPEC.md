# Task: `pre-zenodo-audit-fix-bundle-r4`

**Authority:** `AUDITS/CONSOLIDATED_POST_DPREP9_2026-05-21T00-21-08Z.md` Tier A (A1-001–A1-007) + extras A1-008 (PAPER2 prompt), A1-009 (run_pipeline comment clarity).  
**Precedent:** `audit-fix-r1r2-bundle`, `pre-zenodo-audit-fix-bundle`, `ultrareview-fix-bundle`.  
**Invariant:** doc/CSV/notebook-source only; **zero canonical parquet mutation**; 4 gate SHAs byte-exact pre/post.

---

## PRE-FLIGHT — Field-value snapshot (Convention 3)

Snapshot **before** any edit; halt if divergent from plan.

| ID | File | Field / lines | Current (expected) | Planned |
|---|---|---|---|---|
| A1-001 | `VERSION_ROADMAP.md` | L18 | `4,906 strata × 29 years` … `not yet extended` | `4,990` / `31 years` / shipped |
| A1-001 | `VERSION_ROADMAP.md` | L24–26 | `### Convenience CSV year extension` Planned | Remove or mark **Shipped** |
| A1-002 | `docs/COMPARABILITY.md` | L154 | `29 years` + `not extended to 2023-2024` | `31 years` through 2024 |
| A1-003 | `docs/JOINT_USE_GUIDE.md` | L22 fetal row | `null 2018–2022` | `null 2018–2024` (harmonized column) |
| A1-004 | `fetal_death/quickstart.py` | L50–51 | `2005-2022` + 2023-2024 fallback | `2005-2024`; drop 2023-2024 clause |
| A1-005 | `PROJECT_STRUCTURE.md` | L68–98 | v2.0 / 1992–2022 framing | v2.4.0 / 1982–2024 + 3 layout docs |
| A1-006 | `notebooks/_build_paper_companion.py` | C37 block ~509–516 | `2005-2022` LBY window | `2005-2024`; **do not** change C42 “26 years” (rate targets, not LBY) |
| A1-007 | `tests/test_cross_product_join_parity.py` | L38, L299 | `29 years` | `31 years` |
| A1-008 | `paper/PAPER2_ANALYSIS_DISCOVERY_PROMPT.md` | L77 | fetal null `2018–2022` | `2018–2024` harmonized; strat CSV `2020–2024` |
| A1-009 | `fetal_death/scripts/run_pipeline.py` | L41–44 | stale `ALL_YEARS` comment | clarify orchestrator deferred to C8.7b (no `ALL_YEARS` code change) |

**Gate SHAs (verify unchanged post-DO):**

- `38e2cecb03ff4947bbf6bcecbe9a79bf4bbe58df74ed4e7809b5078899c5cf48` — fetal harmonized  
- `185c071ec76ab8aae24c9d7524b2495900f78afbf43cd6a32537124fa7968a09` — fetal derived  
- `acb5c48a9abf82ac78e6bf210d6be5d62cba6afae271b978b0e53ed528856974` — natality derived  
- `f630d8cf20db72eaf5e482e856e621ff73a6ad1c932de0fc832b237546b09073` — linked derived  

**Result:** PROCEED (no §7 trip if SHAs match and working tree intentional).

---

## SMOKE — SHAPE-not-VALUE (`DESIGN: tracks-current-state`)

Tier 0 (no parquet read required):

1. `grep -nE '29 years|not yet extended|not extended to 2023|2018–2022.*null|null 2018–2022' VERSION_ROADMAP.md docs/COMPARABILITY.md docs/JOINT_USE_GUIDE.md fetal_death/quickstart.py PROJECT_STRUCTURE.md` → expect **hits before DO**, **zero false-positive envelope claims after DO** (historical v2.0.0 changelog lines may retain `29 years` in migration context — allowed).

2. `python3 -c` strat row count = **4990**, years = **31**, LBY years = **28** (unchanged by this task).

3. `uv run pytest tests/test_cross_product_join_parity.py::test_stratified_denominators_year_coverage_within_joint -q` → PASS (dynamic years; docstring-only change).

---

## DO — Edits (single commit)

### A1-001 `VERSION_ROADMAP.md`

- L18: `4,990 strata × 31 years: 1992–2002 + 2005–2024` (shipped in-repo 2026-05-20 D-prep.8).  
- L24–26: Replace “Planned > Convenience CSV year extension” with **Shipped** note pointing at D-prep.8 / JOINT_USE_GUIDE convenience section; optional 2003–2004 LBY NVSR refresh remains a separate open question (STATUS).

### A1-002 `docs/COMPARABILITY.md` L154

- `1992-2002 + 2005-2024 (31 years)`; remove “not extended to 2023-2024”; keep pointer to JOINT_USE for microdata vs NVSR nuance.

### A1-003 `docs/JOINT_USE_GUIDE.md` L22

- Fetal `maternal_race_bridged`: **`null 2018–2024`** (harmonized parquet; see `fetal_death/COMPARABILITY.md`).

### A1-004 `fetal_death/quickstart.py` L50–51

- `# live_births_by_year.csv covers 1995-2002 + 2005-2024 (NVSR series through 2022; 2023-2024 per JOINT_USE_GUIDE).`  
- Remove “For 2023-2024 … recompute” line; keep 1992-1994 clause if present.

### A1-005 `PROJECT_STRUCTURE.md` § fetal_death/

- Header + table rows per README v2.4.0; add `V2_1_*`, `V3a_*`, `V3b_*` layout decision paths; parsing **1982–2024**; validation “V2-era rates + envelope control counts”.

### A1-006 `notebooks/_build_paper_companion.py` (C37 only)

- Extend `lb_73` to `between(2005, 2024)`; update `record()` expected string to include 2023–2024 / natality-canonical 2024.  
- **C42 L385:** add comment in generated print: “26 = NVSR `fetal_mortality_rate` target rows (through 2022), not `live_births_by_year` span”.  
- Regenerate `notebooks/paper_companion.ipynb` via `uv run python notebooks/_build_paper_companion.py` on build host (VERIFY).

### A1-007 `tests/test_cross_product_join_parity.py`

- L38, L299: `31 years` / `1992-2002 + 2005-2024`.

### A1-008 `paper/PAPER2_ANALYSIS_DISCOVERY_PROMPT.md` L77

- Harmonized fetal bridged null **2018–2024**; strat CSV **2020–2024**.

### A1-009 `fetal_death/scripts/run_pipeline.py`

- Comment only: `ALL_YEARS` is legacy 29-year orchestrator scope; full 43-year envelope requires C8.7b — **no change to `ALL_YEARS` list in this bundle**.

---

## VERIFY

| Check | Criterion |
|---|---|
| V1 | `grep` residual sweep (see SMOKE) on edited files |
| V2 | `stratified_denominators.csv` still 4990 rows / 31 years (byte-unchanged) |
| V3 | `uv run pytest tests/test_cross_product_join_parity.py -q` — all pass |
| V4 | 4 gate parquet SHAs byte-exact vs PRE-FLIGHT |
| V5 | `git diff --name-only` ⊆ task file list + state files |
| V6 | If notebook regen run: `paper_companion` C37 references 2005–2024 |

**§10 self-check (receipt):** Could a wrong “31 years” claim slip through if strat CSV regressed? Mitigation: V2 byte-unchanged on CSV. Could C42 be misread as LBY years? Mitigation: clarifying comment in builder. Could PROJECT_STRUCTURE miss a layout doc? Mitigation: glob `V*_LAYOUT_DECISIONS.md`.

---

## RECEIPT + STATUS

- Write `RECEIPTS/pre-zenodo-audit-fix-bundle-r4_<UTC>.md`.  
- Append STATUS section: bundle complete; next = Phase D.1 on human go-ahead.  
- Tags: `pre-zenodo-audit-fix-bundle-r4-pre-do`, `pre-zenodo-audit-fix-bundle-r4-complete` (if human requests git tag).  
- **Forward-looking HALTs (Convention 4):**  
  1. Re-hash 4 gate SHAs immediately before Zenodo D.2.  
  2. Manuscript + `paper_companion` full envelope sync remains D.4.  
  3. `preterm` / `cross_race` notebook execute health — separate build-host pass (Tier B).  
  4. `fetal_death/scripts/run_pipeline.py` `ALL_YEARS` extension — C8.7b, not this bundle.

---

## Explicitly out of scope

- `paper/draft_v2_hmd_styled.md` (D.4)  
- Parquet / `harmonized_schema.csv` / validation-target mutation  
- Adding 2023–2024 rows to `external_validation_targets.csv` fetal_mortality_rate (would change C42 row count — separate task)  
- `fetal_death/validation_results.csv` V2-era scope refresh (Tier B B1-003)
