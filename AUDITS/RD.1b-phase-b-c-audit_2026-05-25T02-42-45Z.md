# RD.1b Phase B & C — Fresh-Eyes Adversarial Audit

**Auditor:** Claude (Opus 4.7, 1M) — independent fresh-eyes pass
**UTC:** 2026-05-25T02:42:45Z
**Scope:** RD.1b Phase B (preterm 1980–1989) + Phase C (LBW + preterm 1968–1979) external validation.
**Commits audited:** `d7da1bf` (Phase B, 225/225), `2b37ee1` (Phase C, 249/249).
**Mutations made:** none (read-only audit; targets/validator/parquets untouched, as instructed).

> **Remediation applied 2026-05-25 (human-authorized fix sessions, after this audit):**
> - **F1 — DONE.** `lbw_rate_pct,1971` re-sourced to MVSR `mv23_08sacc` → `7.7 / tol 0.05` (was IOM `7.6 / 0.06`). Re-validated **249/249**; cell passes at standard tolerance (\|Δ\|=0.045). DECISION_LOG entry `2026-05-25T02:47:41Z`.
> - **F2 — DONE.** Added §"Pre-1990 (1968–1989) external-validation comparability" to `natality/docs/COMPARABILITY.md` (preterm known-gestation/LMP-reporting-area denominator; 1968 GESTREC vs 1972+ recode; 1989 raw `GESTAT3` vs 1990+ derived `preterm_lt37`; LBW comparability + sourcing). Scope note updated to point to it; broader pre-1990 narrative still routed to C8.20.
> - **F3 — DONE (data artifacts).** 1968 LBW + 1968 preterm CSV `notes` now explicitly flag INDIRECT / PUF-DEFINITIONAL status; documented in the new COMPARABILITY section. **Manuscript not touched** (`paper/` gated until §15.F closes) — the footnote action remains for the future manuscript session, now backed by the artifact caveats.
> - **F5 — DONE.** README.md + natality/README.md "205 resident-births 1968–2024" corrected to the true composition (56 resident-births + 44 LBW/preterm 1968–1989 + 149 1990+ rate/indicator cells = 249). Milestone "205/205" counts in KICKOFF/STATUS/NEXT_STEPS left as-is (accurate cumulative totals, not composition labels).
> - **F4, F6 — no change** (accepted: smoke-test regression-guard limitation noted; 1973 LBW 0.06 tol is honest).

---

## 1. Executive verdict

| Phase | Verdict | One-line basis |
|-------|---------|----------------|
| **Phase B** (preterm 1980–1989) | **PASS** | All 10 cells transcribed verbatim from cited MVSR Advance Reports; `{1,2}` denominator = NCHS "known gestation," confirmed by microdata distribution + mv31 narrative + DECISION_LOG; 10/10 reproduced on clean recompute. |
| **Phase C** (LBW + preterm 1968–1979) | **PASS-WITH-NOTES** | 22/24 cells transcribed verbatim/definitionally faithful; 1968 cells are indirect/PUF-definitional (disclosed); **1971 LBW target (7.6, IOM secondary) conflicts with the available MVSR primary 7.7% and needs the 0.06 tol** (F1). |
| **Combined RD.1b B+C** | **PASS-WITH-NOTES** | 249/249 reproduced against the gate parquet (SHA verified unchanged); zero regression; denominators definitionally sound and documented; residual notes are source-fidelity + comparability-documentation, not wrong numbers. |

**Is 249/249 publication-honest for the manuscript robustness section?** → **YES**, with two caveats that should be stated in the manuscript: (a) the pre-1990 preterm series is a *known-gestation, LMP-reporting-area* rate (it excludes the gestation-not-stated/non-reporting fraction — up to ~20% of births in 1980, ~40% in 1972), and 1968 preterm uses a different recode than 1972+; (b) 1968 LBW/preterm are bracketed/definitional, not direct external transcriptions.

**May §15.F close?** → **YES, conditionally** — the validation work itself is correct and non-regressive, so §15.F may close, *provided* the two low-cost documentation actions in F1 and F5 are taken (reconcile/annotate the 1971 LBW source; add the pre-1990 preterm comparability caveat to COMPARABILITY.md or explicitly route to C8.20). None of these block; none require touching canonical data.

**No HALT condition tripped.** Gate SHA-256 = `acb5c48a9abf82ac78e6bf210d6be5d62cba6afae271b978b0e53ed528856974` (verified identical on disk). Raw SAMPWT path used where required (no derived-parquet substitution for pre-1989 rates). No invented numbers.

---

## 2. Findings by severity

**Count:** 0 critical · 0 high · 3 medium · 3 low.

| ID | Severity | Phase | Location | Evidence | Remediation |
|----|----------|-------|----------|----------|-------------|
| **F1** | **medium** | C | `external_validation_targets_v1.csv:249` (lbw 1971) | Target = `7.6, tol 0.06`, sourced to **IOM 1985 Table B.1 (7.64%)**. But the **MVSR primary already in the citation set** (`mv23_08sacc`, cited for 1972 LBW + 1971/1972 preterm) states verbatim: *"During 1972, 7.7 percent of all live births were classified as low-birth-weight … the same percent as in 1971."* → MVSR 1971 LBW = **7.7%**. Microdata = **7.6553%**, which **rounds to 7.7**, not 7.6, and sits 0.0553 from 7.6 (92% of the widened tol). DECISION_LOG rationale claims "headline parity with MVSR narrative tables," but the MVSR narrative value for 1971 is 7.7, not 7.6. | Re-source 1971 LBW to `mv23_08sacc` (**7.7%, tol 0.05**: \|7.6553−7.7\|=0.045 → passes at standard tol), **or** set expected to IOM's two-decimal 7.64 (tol 0.05: \|7.6553−7.64\|=0.015). Either is more faithful than 7.6@0.06. |
| **F2** | **medium** | both | `natality/docs/COMPARABILITY.md:3` | Doc is **explicitly scoped to 1990–2024**; states pre-1990 comparability "is tracked as a dedicated follow-up (C8.20 / soft-flag (aa)) and is **not yet reflected here**." Yet both receipts' §10 self-checks instruct cross-era users to "read COMPARABILITY notes" about (i) 1989 raw `GESTAT3` vs 1990+ derived `preterm_lt37`, and (ii) 1968 `GESTREC` 0–4 vs 1972+ LMP-narrative "premature." **Those notes do not exist for the pre-1990 era.** The pre-1990 preterm *denominator caveat* (known gestation in LMP-reporting area only; up to ~20% excluded in 1980) is also undocumented. | Add a short pre-1990 preterm/LBW comparability note (denominator = known gestation; LMP-reporting-area; 1968 recode difference; 1989 vs 1990 measurement change), **or** make §15.F closure explicitly contingent on C8.20 and stop referencing not-yet-written COMPARABILITY notes in receipts/manuscript. |
| **F3** | **medium** | C | `external_validation_targets_v1.csv:246,258` (1968 LBW + preterm) | **1968 LBW (8.2):** no direct 1968 MVSR headline; bracketed by Series 21 No. 48 (1967=8.2%) + mv22_12 (1969=8.1%); microdata 8.196 → rounds to 8.2. **1968 preterm (8.9):** not an external published figure at all — it is a **PUF-definitional reproduction** (GESTREC 0–4 per Nat1968doc, verified below) bracketed by mv22_12 (1969=9.8%). Both are *internally* validated, not *externally* cross-checked against a published 1968 number. Honestly disclosed in CSV notes + receipt §10 + DECISION_LOG. | Keep, but flag both 1968 cells as **footnote/“defer-direct-cite”** in the manuscript (do not present as direct external transcriptions). Optional: locate the 1968 Registered Births / Series 21 No. 48 PDF to upgrade 1968 LBW to a direct cite. |
| **F4** | **low** | both | `tests/test_pre1990_preterm_rate_smoke.py`, `tests/test_pre1990_rate_phase_c_smoke.py` | Smoke tests **re-implement** the validator's exact denominator logic (`{1,2}`, GESTREC 0–4, SAMPWT) inline rather than importing `compare_external_targets_v1.py`, and assert against hard-coded MVSR values. They therefore cannot independently catch a *denominator-definition* error or a *transcription* error — if the denom were wrong and the target chosen to match, both validator and smoke would agree (double false-confidence; the receipt §10 + L3 risk). | Acceptable as a regression guard (headers honestly say `tracks-current-state` / `SHAPE-not-VALUE`). The independent checks are this audit's Lane 1 (PDF) + Lane 2 (distribution/doc). No change required; note the limitation. |
| **F5** | **low** | both | `README.md:16`, `natality/README.md:21,29` | Headline reads "**205 resident-births** 1968–2024." Only **56** of the 249 targets are `resident_births`. The "205" is correct as an arithmetic remainder (249−44 rate cells), but it is **not 205 resident-births** — it bundles 56 resident_births + 34 LBW(1990+) + 34 preterm(1990+) + 29 twin + 20 cesarean + 18 triplet + 6 smoking + 6 medicaid + 1 singleton + 1 male = 205. | Reword to "205 prior targets (resident-births + 1990+ rate/indicator cells) + 44 LBW/preterm rate cells 1968–1989." (Receipts repeat the same loose "205 resident-births" phrasing — they are untrusted artifacts, lower priority.) |
| **F6** | **low** | C | `external_validation_targets_v1.csv:251` (lbw 1973) | Target 7.6 (**direct** MVSR `mv23_11sacc`: *"During 1973, 7.6 percent … compared with 7.7 percent in 1972"*) but microdata = 7.5477 (rounds to 7.5), 0.0523 from 7.6 → needs `tol 0.06`. This is an honest disclosed ~0.05 microdata-vs-published gap (likely public-use vs final-tabulation), **not** a tolerance masking a definition error (direction/magnitude consistent with rounding class). | None required; keep 0.06 with the existing note. Listed for completeness (genuine near-miss, honest). |

No finding reaches **high/critical/HALT**: every transcribed value was located in its cited document (or disclosed as indirect), the validator definitions are faithful, the gate SHA is unchanged, and the raw SAMPWT path is used where required.

---

## 3. Transcription matrix — all 34 new rate cells

**Method.** Cited PDFs downloaded from `https://www.cdc.gov/nchs/data/mvsr/supp/` (all HTTP 200); text extracted via PyMuPDF OCR layer; narrative sentences read directly. "Microdata" = clean recompute via `compare_external_targets_v1.py` against the gate parquet + raw yearly parquets (Lane 3). "Util%" = |Δ| as % of tolerance.

### Phase B — preterm 1980–1989 (10 cells)

| Year | CSV exp | Cited PDF | Found? | PDF quote (verbatim) | Microdata | Δ | Util% |
|------|---------|-----------|--------|----------------------|-----------|------|-------|
| 1980 | 8.9 | mv36_04sacc | **Y** | "In 1980 it was 8.9 percent" (mv36); also mv31: "In 1980, 8.9 percent of all births were preterm, unchanged from the 1979 level" | 8.8882 | −0.0118 | 24 |
| 1981 | 9.4 | mv34_06s | **Y** | "risen steadily since 1981 (9.4 percent)"; mv40: "9.4 percent in 1981" | 9.4461 | +0.0461 | 92 |
| 1982 | 9.5 | mv34_06s | **Y** | "and 1982 (9.5 percent)" | 9.4990 | −0.0010 | 2 |
| 1983 | 9.6 | mv34_06s | **Y** | "In 1983, 9.6 percent of all babies were born preterm, that is, prior to 37 completed weeks" | 9.6093 | +0.0093 | 19 |
| 1984 | 9.4 | mv36_04sacc | **Y** | "compared with 9.4 percent in 1984" | 9.4067 | +0.0067 | 13 |
| 1985 | 9.8 | mv36_04sacc | **Y** | "was 9.8 percent in 1985 compared with 9.4 percent in 1984"; mv37 confirms | 9.7640 | −0.0360 | 72 |
| 1986 | 10.0 | mv37_03s | **Y** | "In 1986, 10.0 percent of all births were preterm" | 9.9661 | −0.0339 | 68 |
| 1987 | 10.2 | mv38_03s | **Y** | "increased to 10.2 percent in 1987, compared with 10.0 percent in 1986" | 10.1970 | −0.0030 | 6 |
| 1988 | 10.2 | mv39_04s | **Y** | "remained unchanged from the 1987 level of 10.2 percent"; mv40: "10.2 percent in 1988" | 10.2239 | +0.0239 | 48 |
| 1989 | 10.6 | mv40_08s | **Y** | "The proportion of babies born preterm rose in 1989 to 10.6 percent compared with 10.2 percent in 1988" | 10.5847 | −0.0153 | 31 |

All 10 describe "preterm / prior to 37 completed weeks of gestation." Source-year labels in CSV (Advance Report 1983/1985/1986/1987/1988/1989) all match the PDFs' subject years. **Phase B transcription: 10/10 clean.**

### Phase C — LBW 1968–1979 (12 cells)

| Year | CSV exp | Tol | Cited source | Found? | PDF quote / basis | Microdata | Δ | Util% |
|------|---------|-----|--------------|--------|-------------------|-----------|------|-------|
| 1968 | 8.2 | .05 | Series 21 #48 + mv22_12 | **Indirect** | No direct 1968 headline; 1967=8.2 (Series 21, not re-verified here), 1969=8.1 (mv22 verified); microdata brackets | 8.1960 | −0.0040 | 8 |
| 1969 | 8.1 | .05 | mv22_12sacc | **Y** | "compared with 8.1 percent in 1969" | 8.0899 | −0.0101 | 20 |
| 1970 | 7.9 | .05 | mv22_12sacc | **Y** | "Of all live births in 1970, 7.9 percent weighed 2,500 grams … or less" | 7.9331 | +0.0331 | 66 |
| 1971 | 7.6 | **.06** | IOM 1985 B.1 | **Conflict (F1)** | IOM=7.64; but mv23_08 (primary) says 1971 **= 7.7%** ("same percent as in 1971"); microdata rounds to 7.7 | 7.6553 | +0.0553 | **92** |
| 1972 | 7.7 | .05 | mv23_08sacc | **Y** | "During 1972, 7.7 percent of all live births were classified as low-birth-weight" | 7.6626 | −0.0374 | 75 |
| 1973 | 7.6 | **.06** | mv23_11sacc | **Y** (F6) | "During 1973, 7.6 percent of all live births were in this category compared with 7.7 percent in 1972" | 7.5477 | −0.0523 | 87 |
| 1974 | 7.4 | .05 | mv24_11s2acc | **Y** | "During 1974, 7.4 percent of all live births … compared with 7.6 percent in 1973" | 7.4144 | +0.0144 | 29 |
| 1975 | 7.4 | .05 | mv25_10sacc | **Y** | "In 1975, 7.4 percent of all live births" | 7.3806 | −0.0194 | 39 |
| 1976 | 7.3 | .05 | mv26_12sacc | **Y** | "decreased from 7.4 percent in 1975 to 7.3 percent in 1976" | 7.2507 | −0.0493 | **99** |
| 1977 | 7.1 | .05 | mv27_11sacc | **Y** | "7.1 percent compared with 7.3 percent" (1977 vs 1976) | 7.0638 | −0.0362 | 72 |
| 1978 | 7.1 | .05 | mv29_01sacc | **Y** | "The proportion of all infants in this category was 7.1 percent in 1978, unchanged from 1977" | 7.0777 | −0.0223 | 45 |
| 1979 | 6.9 | .05 | mv31_08sacc (1980 rpt) | **Y** | "6.8 percent … in 1980, a slight decline from the level of 6.9 percent observed in 1979" | 6.9361 | +0.0361 | 72 |

### Phase C — preterm 1968–1979 (12 cells)

| Year | CSV exp | Cited source | Found? | PDF quote / basis | Microdata | Δ | Util% |
|------|---------|--------------|--------|-------------------|-----------|------|-------|
| 1968 | 8.9 | Nat1968doc GESTREC | **Definitional** | PUF GESTREC 0–4 = <37 wk (Nat1968doc p6, verified §4); bracketed by 1969=9.8 | 8.8998 | −0.0002 | 0 |
| 1969 | 9.8 | mv22_12sacc | **Y** | "9.3 percent were premature compared with 9.8 percent of the births reported by 38 LMP areas in 1969" | 9.7571 | −0.0429 | 86 |
| 1970 | 9.3 | mv22_12sacc | **Y** | "9.3 percent were premature compared with 9.8 percent … in 1969" | 9.2508 | −0.0492 | **98** |
| 1971 | 9.3 | mv23_08sacc | **Y** | "an increase … from the proportion observed in 1971 (9.3 percent)" | 9.3382 | +0.0382 | 76 |
| 1972 | 9.6 | mv23_08sacc | **Y** | "In 1972, 9.6 percent of live births occurring in the LMP areas were considered premature" | 9.6012 | +0.0012 | 2 |
| 1973 | 9.2 | mv23_11sacc | **Y** | "9.6 percent in 1972 and 9.2 percent in 1973" | 9.1775 | −0.0225 | 45 |
| 1974 | 8.5 | mv24_11s2acc | **Y** | "9.2 percent in 1973 and 8.5 percent in 1974" | 8.5152 | +0.0152 | 30 |
| 1975 | 8.9 | mv25_10sacc | **Y** | "premature (8.9 percent … )"; mv26: "8.9 percent in 1975" | 8.9347 | +0.0347 | 69 |
| 1976 | 8.8 | mv26_12sacc | **Y** | "decreased from 8.9 percent in 1975 to 8.8 percent in 1976" | 8.7796 | −0.0204 | 41 |
| 1977 | 8.8 | mv27_11sacc | **Y** | mv29: "slightly above the 1977 level of 8.8 percent" | 8.8015 | +0.0015 | 3 |
| 1978 | 8.9 | mv29_01sacc | **Y** | "In 1978, 8.9 percent of births occurred prematurely (less than 37 weeks gestation)" | 8.8745 | −0.0255 | 51 |
| 1979 | 8.9 | mv31_08sacc (1980 rpt) | **Y** | "In 1980, 8.9 percent of all births were preterm, unchanged from the 1979 level" | 8.8963 | −0.0037 | 7 |

**Transcription summary:** 30 of 34 new cells confirmed **verbatim** in their cited PDFs. 3 cells are honestly-disclosed indirect/definitional (1968 LBW indirect, 1968 preterm PUF-definitional, 1979 cross-report from the 1980 PDF — the 1980 report explicitly says "unchanged from 1979," so attribution is correct). 1 cell (1971 LBW) has a defensible-but-inferior secondary source that conflicts with an available primary (F1).

**Near-misses (>80% of tolerance):** new cells — 1971 LBW (92%), 1973 LBW (87%), 1976 LBW (99%), 1969 preterm (86%), 1970 preterm (98%), 1981 preterm (92%). **Every near-miss except 1971/1973 LBW rounds correctly to its published one-decimal figure**, confirming honest measurement agreement rather than tolerance-gaming. 1971 (rounds to 7.7≠7.6) → F1; 1973 (rounds to 7.5≠7.6, direct cite) → F6.

---

## 4. Validator definition audit (per era)

Functions reviewed in `natality/scripts/05_validate/compare_external_targets_v1.py`. **Resident filter is consistent across all pre-1990 paths:** `str(RESTATUS).strip() == "4"` excluded (≡ `is_foreign_resident == False`; DECISION_LOG D2 confirms byte-exact). Red-team #3: including foreign moves rates by <0.01 pct-pt (immaterial).

- **1968 preterm — `GESTREC` (codes 0–4 num / 0–8 den, exclude 9):** **FAITHFUL.** Nat1968doc p6 "Gestation Period, Recode (Computer-generated)": `0=Under 20wk, 1=20–27, 2=28–31, 3=32–35, 4=36, 5=37–39, 6=40, 7=41–42, 8=43+, 9=Not stated (incl. premature & item not on certificate).` Codes 0–4 = all ≤36 wk = <37 = preterm ✓; code 5 = first term group ✓; code 9 correctly excluded. Red-team #4: including code 9 in denominator → 7.37% (fails 8.9 badly), so exclusion is essential and correct. Microdata 8.8998 vs target 8.9.
- **1969–1971 preterm — `GESTREC3` codes {1,2}, uniform 2×:** **FAITHFUL.** No SAMPWT (50% sample); uniform 2× inflation cancels in a rate (red-team #5: 1972 SAMPWT 9.6012 vs no-SAMPWT 9.5925 — 0.009 pct-pt; weighting is immaterial to the rate, applied correctly regardless).
- **1972–1988 preterm — `GESTREC3` codes {1,2} + per-record SAMPWT:** **FAITHFUL — and this is the crux (L7) the receipts flagged. RESOLVED.** Microdata distribution shows GESTREC3 ∈ {1,2,3} (plus a `0` for 1972-era), with code 3 swinging 1980=20.27% → 1985=3.86% → 1988=4.26% (1972: code0=24.4%, code3=15.5%) — the signature of **gestation not-stated / not-in-LMP-reporting-area**, not a stable postterm category. The mv31 narrative pins it: "74.5 percent of births in 1980 occurred at term (37–41 weeks)" + 8.9% preterm leaves ~16.6% postterm; microdata code 2 (37+ = term+postterm) = 91.1% of known {1,2}, and 74.5%+16.6%=91.1% ✓ → **code 1 = <37, code 2 = 37+ wk, code 3 = not stated.** `{1,2}` = "known gestation" = exactly NCHS's published "premature/preterm % of LMP-area live births with stated gestation." Red-team #1: putting code 3 in the denominator collapses 1980 to 7.05% (vs MVSR 8.9), 1972 to 7.68% (vs 9.6) — far outside tol; DECISION_LOG explicitly considered and rejected this with the identical 7.05% figure. The tight match across **all** 1972–1988 years (max util 92%, all round correctly) confirms definition, not coincidence.
- **1989 preterm — `GESTAT3` codes {1,2}, unweighted (100% file):** **FAITHFUL** to plan (raw GESTAT3, no SAMPWT on the 1989 V2 layout). Microdata 10.5847 vs 10.6 (util 31%). GESTAT3 code 3 = 1.43% (not-stated). **Measurement break vs 1990+ derived `preterm_lt37` is real but undocumented in COMPARABILITY** (F2).
- **LBW 1968–1979 — `DBIRWT`<2500 / known-weight denom; 2× for 1968–1971, SAMPWT 1972–1979:** **FAITHFUL.** Nat1968doc p6: birthweight in grams, `9999 = Not stated`; validator excludes 9999 and ≤0 ✓. Denominator = known birthweight (matches NCHS published LBW%). Column auto-selects `DBIRWT` else `DBWT`. One open definitional nuance: NCHS LBW% denominator is births with *known* birthweight (validator matches); the residual ~0.03–0.05 gaps (e.g., 1976 util 99%) are public-use-vs-final rounding class, all within tol.

**§7 check:** raw yearly SAMPWT parquets are used for every pre-1989 LBW/preterm cell (the derived parquet is used only for years not in the pre-1990 maps). No derived-path substitution where raw was required. Gate parquet SHA unchanged.

---

## 5. Regression & inventory check

- **Gate SHA-256:** on-disk `acb5c48a9abf82ac78e6bf210d6be5d62cba6afae271b978b0e53ed528856974` == expected ✓.
- **Clean recompute (Lane 3):** `compare_external_targets_v1.py` against gate parquet + raw yearly parquets → **249 pass / 0 fail / 0 missing** ✓.
- **Smoke tests:** `pytest natality/tests/test_pre1990_*.py` → **19 passed** in 65s (3 lbw_smoke + 4 preterm_smoke + 6 phase_c_smoke + 6 resident_births_smoke) ✓ — matches Phase C receipt.
- **Validator non-regression:** `git diff d7da1bf^..2b37ee1 -- …compare_external_targets_v1.py` has **zero removed/modified lines** (pure additions: `_weighted_preterm_rate_from_raw`, `_unweighted_preterm_rate_from_raw_1989`, `_weighted_preterm_rate_from_raw_1968`, maps + dispatch). Existing `resident_births` / Phase A LBW paths untouched ✓.
- **Targets non-regression:** `git diff` of the CSV across B+C removed exactly **one** line (the stale `# Preterm + 1968-1979 rates deferred` comment), replaced by 3 phase-comment lines + 34 data rows. **No pre-existing data row was removed or modified** → the 205 prior targets + 10 Phase A LBW (1980–1989) + 10 Phase B preterm are substance-unchanged ✓.
- **Inventory (from recompute output, 249 rows):** resident_births 56 (1968–2023; 22 are 1968–1989) · lbw_rate_pct 56 (22 are 1968–1989) · preterm_rate_pct 56 (22 are 1968–1989) · cesarean 20 · twin 29 · triplet 18 · smoking 6 · medicaid 6 · singleton 1 · male 1. **44 LBW/preterm rate cells 1968–1989** ✓; **249 = 205 prior + 10 A + 10 B + 24 C** ✓. (README's "205 resident-births" label is inaccurate — see F5.)
- **L10 (PRE_FLIGHT back-fill):** Phase C PRE-FLIGHT 2026-05-25T01:30Z < commit 02:07Z; Phase B PRE-FLIGHT 2026-05-24T18:00Z < commit 2026-05-25T01:26Z. PRE_FLIGHT precedes its commit in both cases ✓ (no back-fill). PRE_FLIGHT even records the same 10 MVSR preterm values and the same micro-probe figures I independently reproduced.

---

## 6. Lane 6 — cross-era / receipt §10 risk dispositions

| Risk | Disposition |
|------|-------------|
| Preterm denom excludes GESTREC3 code 3 | **CLEARED.** Code 3 = not-stated (distribution volatility + mv31 narrative + Nat1968doc analog + DECISION_LOG). `{1,2}` is the correct NCHS known-gestation denominator. |
| 1989 preterm ≠ 1990+ derived | **REAL, undocumented** → F2. Numerically fine (1989=10.6 ≈ 1990=10.6); measurement-construct break not in COMPARABILITY. |
| 1968 preterm ≠ 1972+ LMP narrative | **REAL, disclosed in receipt/DECISION_LOG, not in COMPARABILITY** → F2/F3. 8.9% is publishable *as a PUF-definitional figure*, not as a direct external transcription. |
| 1979 from 1980 PDF | **CLEARED.** mv31 explicitly: LBW "6.9 percent observed in 1979"; preterm "unchanged from the 1979 level." Attribution to 1979 is correct. |
| 1971/1973 LBW 0.06 tol | 1973 = honest rounding-class gap on a direct cite (F6, low). 1971 = source-selection issue (F1, medium) — primary MVSR says 7.7%. |
| 1968 LBW indirect cite | **Flag defer/footnote** in manuscript (F3); §15.F may still close. |

**§15.F recommendation:** May close. The robustness benchmarking is correct, reproducible, and non-regressive. Close *with* F1 (1971 LBW re-source/annotate) and F2 (pre-1990 comparability note or explicit C8.20 hand-off) addressed — both are documentation-only, no canonical mutation.

---

## 7. Cover note (for the human)

1. **Verdicts:** Phase B = **PASS**; Phase C = **PASS-WITH-NOTES**; combined RD.1b B+C = **PASS-WITH-NOTES**.
2. **Findings:** 0 critical · 0 high · 3 medium (F1 1971-LBW source; F2 pre-1990 COMPARABILITY gap; F3 1968 indirect cites) · 3 low (F4 smoke-test non-independence; F5 README "205 resident-births" mislabel; F6 1973-LBW honest 0.06 tol).
3. **Cells needing re-transcription / amendment:** only **1971 LBW** (F1) — prefer `mv23_08sacc` 7.7%@0.05, or IOM 7.64@0.05, over the current 7.6@0.06. 1968 LBW + 1968 preterm should be footnoted as indirect/definitional (F3). No other cell needs a value change.
4. **Is 249/249 publication-honest for the manuscript robustness section?** → **YES** (with the pre-1990 "known-gestation, LMP-area" preterm caveat + 1968-cell footnotes stated).
5. **May §15.F close?** → **YES**, conditional on the two documentation actions (F1 + F2). No blocking issue; no canonical-data change required.

*Audit performed read-only. No edits made to `external_validation_targets_v1.csv`, `compare_external_targets_v1.py`, `STATUS.md`, canonical parquets, or any committed artifact.*
