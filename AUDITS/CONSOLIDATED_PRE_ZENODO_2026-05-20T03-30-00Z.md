# CONSOLIDATED PRE-ZENODO AUDIT — Phase D-prep.4 (round 3)

- **Timestamp:** 2026-05-20T03:30:00Z
- **Method:** 5 parallel fresh-eyes agents (fallback mode; user did not trigger `/ultrareview`); consolidator synthesis only
- **Dependencies verified:** D-prep.1–3 complete (`3926e19`..`eb11b41`); working tree clean at audit start
- **Gate parquets:** Not present in audit workspace (gitignored); documented SHAs internally consistent across PROVENANCE files

---

## 1. Per-audit verdicts

| # | Audit file | Verdict | Blockers |
|---|---|---|---|
| 1 | `round3/01_data-integrity_*.md` | PASS-WITH-NOTES | 0 (1 operational: re-hash on build host) |
| 2 | `round3/02_user-facing-docs_*.md` | **FAIL** | 2 critical (JOINT_USE, quickstart) |
| 3 | `round3/03_reproducibility_*.md` | CONDITIONAL PASS | 0 |
| 4 | `round3/04_notebooks_*.md` | **FAIL** | 2 (paths, no parquets locally) |
| 5 | `round3/05_manuscript_*.md` | **FAIL** | 0 for D-prep.5 — **D.4 scope** |

**Aggregate:** 0 §7 halts requiring canonical pipeline rebuild. **No NVSR regression** surfaced in committed validation artifacts. **Substantive doc/CSV drift** remains on cross-product entry points, reproducibility UX, notebooks, and manuscript (D.4).

---

## 2. Independently verified (strongest signals)

1. **D-prep.1–3 closed** — fetal hand-docs v2.4.0, PROVENANCE refresh, schema `#ENVELOPE_NOTE` + linked gap notation shipped.
2. **Four gate SHA prefixes** mutually consistent in `fetal_death/PROVENANCE.md`, `natality/PROVENANCE.md`, `matched_multiples/PROVENANCE.md`, `docs/NCHS_SOURCE_MANIFEST.md` §5.
3. **README four-product table** internally consistent (201.2M / 149.4M / 2.43M / 1.67M).
4. **Fetal product README/CODEBOOK L60/GETTING_STARTED** aligned to v2.4.0 envelope post-D-prep.1.
5. **C8.18 linked inventory** — 38 cohort years `imported=true`; 1992–1994 gap documented in schema.
6. **Committed validation summaries** — natality 183/0/0 (1990–2024 surface); linked 35/0/0 (2005–2023 owned surface); published_tabulations reconciliation honest on pre-1990 rows.

---

## 3. Consolidated findings (ranked)

### Tier A — Pre-Zenodo doc/CSV bundle (D-prep.5 candidates)

| ID | Sev | Items | Est. |
|---|---|---|---|
| **PZ-01** | critical | `docs/JOINT_USE_GUIDE.md` — full v2.4.0 / v3.0.0 envelope + joint year math + column version table | 0.25 session |
| **PZ-02** | critical | `fetal_death/quickstart.py` — v2.4.0 docstring, drop deferred-years message, examples through 2024 | 0.1 session |
| **PZ-03** | high | Root `README.md` L8 heritage + citation block (1982–2024) | 0.1 session |
| **PZ-04** | high | `fetal_death/CODEBOOK.md` L63 `delivery_year` Values + **regenerate C8.20** schema-note lines (A1-003/A2-005) | 0.25 session |
| **PZ-05** | high | `matched_multiples/README.md` — current gate SHAs + shipped-state (not "planned") | 0.1 session |
| **PZ-06** | high | `natality/REPRODUCING.md` + `fetal_death/REPRODUCING.md` — monorepo paths, zip counts, shapes; remove false "SHA in file_inventory" | 0.25 session |
| **PZ-07** | med | `file_inventory.csv` — flip fetal 43× + MM 3× `imported=true`; patch manifest §2 intro | 0.1 session |
| **PZ-08** | med | `natality/metadata/harmonized_schema.csv` — `data_year` (and peers) `years_available` → 1968–2024 | 0.1 session |
| **PZ-09** | med | `docs/COMPARABILITY.md` L154 + denominator policy note (CSV through 2022) | 0.1 session |
| **PZ-10** | med | `VERSION_ROADMAP.md` Planned → Shipped; `CHANGELOG.md` exact 2,427,233 | 0.1 session |
| **PZ-11** | low | Test docstrings (`conftest`, v2.8.0 refs); `STATA_SAS_QUICKSTART.md` pointer | 0.1 session |

**Bundle estimate:** ~1 session doc/CSV-only (fits D-prep.5 precedent).

### Tier B — Notebook portability (recommend D-prep.5 extension OR separate micro-task)

| ID | Sev | Items |
|---|---|---|
| **PZ-NB** | high | Regenerate `joint_use_demo`, `paper_companion`, `matched_multiples_demo` from `_build_*.py` with `REPO_ROOT`-relative parquet paths; fix `natality/quickstart` `data_year` + 201M copy |

Not strictly CSV — touches `.ipynb` + `_build_*.py`. **Zero parquet mutation** if paths-only + re-execute on build host. User may fold into D-prep.5 or defer.

### Tier C — Phase D.4 only (externally visible publication)

| ID | Items |
|---|---|
| **PZ-MS** | Full `paper/draft_v2_hmd_styled.md` envelope sync (four products, gap, validation counts, Table 1, Future developments); re-run `paper_companion`; IJE word-count re-trim |
| **PZ-OP** | Mandatory `shasum` on build host for 4 gate parquets before Zenodo upload |
| **PZ-H8** | Fetal dtype xfail disposition (document on deposit vs cast) — **not doc-only** if fixing |

### Tier D — Explicit non-findings / deferred

- **R2d / CODEBOOK L60 / PROVENANCE / schema gap** — do not re-flag (D-prep.1–3 closed).
- **Convenience CSV extension to 2023–2024** — product decision; not blocking if documented (A2-007).
- **Fetal H8 ~50 string columns** — known; document or fix at deposit, not silent.

---

## 4. D-prep.5 recommendation

**Trigger:** ≥1 remediable finding — **YES**.

**Proposed task:** `pre-zenodo-audit-fix-bundle` = **Tier A (PZ-01–PZ-11)** in one commit, doc/CSV-only, mirroring `audit-fix-r1r2-bundle`.

**Optional add-on (ask human):** Tier B notebook path fix in same bundle vs separate session.

**SKIP manuscript (Tier C)** until D.4 explicit go-ahead.

---

## 5. Verdict for Phase D entry

| Gate | Status |
|---|---|
| Data integrity / NVSR committed artifacts | **PASS-WITH-NOTES** |
| User-facing cross-product truth | **FAIL** until PZ-01–03 |
| Reproducibility docs | **CONDITIONAL PASS** until PZ-06–07 |
| Notebooks portable | **FAIL** until PZ-NB |
| Manuscript Zenodo-ready | **FAIL** — expected at D.4 |

**Recommendation:** Run **D-prep.5** (Tier A) before Phase D.2 Zenodo upload. Re-hash gate parquets on build machine at D.2 PRE-FLIGHT.
