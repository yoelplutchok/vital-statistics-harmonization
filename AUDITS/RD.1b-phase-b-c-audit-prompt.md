# RD.1b Phase B + Phase C — fresh-eyes audit prompt

Copy **everything inside the fenced block below** as your first message. Clone or open this repo at commit **`2b37ee1`** (or later on `main` if Phase C is merged). This prompt is **read-only audit** unless the human explicitly authorizes fixes.

Optional: attach build-host paths if you have access to `~/Desktop/natality-harmonization/output/yearly_clean/` and the gate derived parquet (not in git).

---

```
You are conducting a **fresh-eyes adversarial audit** of **RD.1b Phase B and Phase C** in the U.S. Harmonized Vital Statistics (HVS) monorepo. These phases extended natality **external validation** for pre-1990 **LBW rate** and **preterm rate** targets (1968–1989), raising the claimed pass count from **215/215** (Phase A only) → **225/225** (+ Phase B preterm 1980–1989) → **249/249** (+ Phase C LBW + preterm 1968–1979).

Your job: determine whether the shipped targets, compare-path logic, tests, and documentation are **correct, citable, internally consistent, and non-regressive** — not whether an earlier agent said PASS.

**You are NOT authorized** to mutate `external_validation_targets_v1.csv`, `compare_external_targets_v1.py`, canonical parquets, or validation targets unless the human explicitly asks for a fix session afterward.

---

## Audit session rules (binding)

### 1. Evidence hierarchy (use in this order)

1. **Primary:** NCHS/MVSR PDFs (transcribed values must appear in cited tables or narrative sentences).
2. **Primary:** `natality/metadata/external_validation_targets_v1.csv` (expected values + tolerances + source strings).
3. **Primary:** `natality/scripts/05_validate/compare_external_targets_v1.py` (how “actual” is computed).
4. **Primary:** Build-host recomputation from `natality_{year}_raw.parquet` (if available).
5. **Secondary:** Smoke tests (`natality/tests/test_pre1990_*.py`) — **L3 risk**: they may duplicate validator logic rather than independently test claims.
6. **Untrusted until re-verified:** `RECEIPTS/RD.1b-*`, agent narratives in `STATUS.md` older sections, “249/249 PASS” headlines without re-running compare.

### 2. What you MAY read

| Category | Paths |
|----------|--------|
| Targets | `natality/metadata/external_validation_targets_v1.csv` |
| Validator | `natality/scripts/05_validate/compare_external_targets_v1.py` |
| Tests | `natality/tests/test_pre1990_lbw_rate_smoke.py`, `test_preterm_rate_smoke.py`, `test_pre1990_rate_phase_c_smoke.py`, `test_pre1990_resident_births_smoke.py` |
| Phase context | `NEXT_STEPS.md` §15.F RD.1b blocks; `KICKOFF.md` current sequence only |
| Decisions (for hypotheses only) | `DECISION_LOG.md` entries dated **2026-05-24** and **2026-05-25** with “RD.1b Phase B/C” |
| Receipts (claims to verify) | `RECEIPTS/RD.1b-pre-1990-natality-rate-benchmarking-phase-b_2026-05-24T18-00-00Z.md`, `RECEIPTS/RD.1b-pre-1990-natality-rate-benchmarking-phase-c_2026-05-25T02-05-00Z.md` |
| Phase A baseline | `RECEIPTS/RD.1b-pre-1990-natality-rate-benchmarking-phase-a_2026-05-24T22-57-47Z.md` (regression context only) |
| Public-use semantics | Nat1968doc (GESTREC) if on build host: `~/Desktop/natality-harmonization/raw_docs/Nat1968doc.pdf` |
| Prior audits (dedup only) | `AUDITS/*.md` — do not assume prior findings apply |

### 3. What you must NOT treat as proof

- Receipt §10 self-checks (treat as **audit leads**, not closures).
- Smoke tests passing without independent PDF transcription.
- Rounded one-decimal MVSR headlines matching microdata within 0.05 without checking **denominator definition** (resident vs all births; LMP reporting areas vs national; known gestation only vs all births).

### 4. Mistake-class priorities (`NEXT_STEPS.md` §8)

| Class | Hunt for |
|-------|----------|
| **L6** | Invented or mis-transcribed NVSR/MVSR percentages; wrong year in cite; PDF that does not contain the quoted value |
| **L3** | Validator logic mirrored in tests; no independent transcription check |
| **L7** | PASS because tolerance absorbed definition mismatch, not rounding |
| **L11** | README/KICKOFF says 249/249 but CSV row count or metric inventory wrong |
| **L10** | PRE_FLIGHT back-filled after DO (check git log: PRE_FLIGHT timestamp vs first commit touching targets) |
| **§7** | Derived-parquet path used where plan required raw SAMPWT; gate SHA changed |

### 5. Output deliverable

Write **`AUDITS/RD.1b-phase-b-c-audit_<UTC>.md`** with:

1. **Executive verdict:** `PASS` | `PASS-WITH-NOTES` | `FAIL` | `HALT` for Phase B, Phase C, and combined RD.1b B+C.
2. **Per-finding entries:** `ID`, `severity` (critical/high/med/low), `phase` (B|C|both), `location`, `evidence`, `remediation`.
3. **Transcription matrix:** all 34 rate cells (10 preterm B + 24 C) — columns: year, metric, CSV expected, PDF value found (Y/N), page/quote, delta vs microdata if computed.
4. **Validator definition audit:** one subsection per era (1968 GESTREC, 1969–1971 uniform 2×, 1972–1988 SAMPWT GESTREC3, 1989 GESTAT3 unweighted, LBW raw grams).
5. **Regression check:** confirm 205 `resident_births` + 10 Phase A LBW + 10 Phase B preterm unchanged in substance.

**Do not** edit `STATUS.md` or commit fixes unless the human asks.

---

## Git anchors (verify scope)

| Commit | Message | Files touched (headline) |
|--------|---------|-------------------------|
| `d7da1bf` | RD.1b Phase B: MVSR preterm 1980-1989 (225/225) | +10 preterm targets; compare preterm helpers; `test_preterm_rate_smoke.py` |
| `2b37ee1` | RD.1b Phase C: MVSR LBW/preterm 1968-1979 (249/249) | +24 targets; `_weighted_preterm_rate_from_raw_1968`; `test_pre1990_rate_phase_c_smoke.py` |

Run: `git show d7da1bf --stat` and `git show 2b37ee1 --stat` and `git diff d7da1bf^..2b37ee1 -- natality/metadata/external_validation_targets_v1.csv`.

**Gate invariant (must still hold):** derived parquet SHA-256  
`acb5c48a9abf82ac78e6bf210d6be5d62cba6afae271b978b0e53ed528856974`  
Path on build host: `~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet`

---

## Scope summary

### Phase A (baseline — regression only)

- 10 × `lbw_rate_pct` 1980–1989 from **childstats HEALTH1.B** (not MVSR).
- Compare uses SAMPWT-weighted raw LBW for 1980–1988; 1989 derived with **0.06** tolerance.
- End state before Phase B: **215/215**.

### Phase B (primary audit)

- **+10** `preterm_rate_pct` 1980–1989.
- Source class: **MVSR Advance Report of Final Natality Statistics** (NOT childstats HEALTH1.A).
- Compare:
  - 1980–1988: SAMPWT-weighted raw `GESTREC3` code `1` = numerator (<37 wk); denominator codes `1|2` only (exclude `0`, `3`).
  - 1989: **unweighted** raw `GESTAT3` (100% file, no SAMPWT).
- Claimed VERIFY: **225/225**; max |diff| 0.04 pct-pt on preterm years.

### Phase C (primary audit)

- **+24** cells: 12 years × (`lbw_rate_pct` + `preterm_rate_pct`) for **1968–1979**.
- Source class: MVSR **Final Natality Statistics** / **Registered Births** supplements; exceptions:
  - **1968 LBW 8.2%:** cite chain includes NCHS Series 21 No. 48 (1967 = 8.2%) + MVSR mv22_12 (1969 = 8.1%) — **no direct 1968 MVSR headline claimed**.
  - **1971 LBW 7.6%:** IOM 1985 *Preventing Low Birthweight* Table B.1 (7.64%) — **not** a direct MVSR PDF sentence for 1971 LBW.
  - **1979 LBW + preterm:** values taken from **1980** Final Natality report (mv31_08) describing **1979** levels.
- Compare additions:
  - **1968 preterm:** `_weighted_preterm_rate_from_raw_1968` — `GESTREC` codes 0–4 = <37 wk; denom 0–8; exclude 9; uniform 2×.
  - 1969–1971 preterm: `GESTREC3` with uniform 2× (same as Phase B logic but no SAMPWT).
  - 1972–1979: same as Phase B SAMPWT + GESTREC3.
  - LBW 1968–1979: `_weighted_lbw_rate_from_raw` (grams < 2500; 2× 1968–1971, SAMPWT 1972–1979).
- Tolerance exceptions: **1971 and 1973 LBW** use **0.06** pct-pt (not 0.05) per DECISION_LOG.
- Claimed VERIFY: **249/249**; gate SHA unchanged.

---

## Full target inventory (transcribe every cell)

Extract from CSV at audit time; expected values as of commit `2b37ee1`:

### Phase B — preterm 1980–1989

| Year | Expected % | Tol | Cited PDF (per CSV) |
|------|------------|-----|---------------------|
| 1980 | 8.9 | 0.05 | mv36_04sacc.pdf |
| 1981 | 9.4 | 0.05 | mv34_06s.pdf |
| 1982 | 9.5 | 0.05 | mv34_06s.pdf |
| 1983 | 9.6 | 0.05 | mv34_06s.pdf |
| 1984 | 9.4 | 0.05 | mv36_04sacc.pdf |
| 1985 | 9.8 | 0.05 | mv36_04sacc.pdf |
| 1986 | 10.0 | 0.05 | mv37_03s.pdf |
| 1987 | 10.2 | 0.05 | mv38_03s.pdf |
| 1988 | 10.2 | 0.05 | mv39_04s.pdf |
| 1989 | 10.6 | 0.05 | mv40_08s.pdf |

MVSR base URL pattern: `https://www.cdc.gov/nchs/data/mvsr/supp/<filename>`

### Phase C — LBW 1968–1979

| Year | Expected % | Tol | Cited source (per CSV) |
|------|------------|-----|------------------------|
| 1968 | 8.2 | 0.05 | Series 21 No. 48 + mv22_12 adjacent |
| 1969 | 8.1 | 0.05 | mv22_12sacc.pdf |
| 1970 | 7.9 | 0.05 | mv22_12sacc.pdf |
| 1971 | 7.6 | **0.06** | IOM 1985 Table B.1 |
| 1972 | 7.7 | 0.05 | mv23_08sacc.pdf |
| 1973 | 7.6 | **0.06** | mv23_11sacc.pdf |
| 1974 | 7.4 | 0.05 | mv24_11s2acc.pdf |
| 1975 | 7.4 | 0.05 | mv25_10sacc.pdf |
| 1976 | 7.3 | 0.05 | mv26_12sacc.pdf |
| 1977 | 7.1 | 0.05 | mv27_11sacc.pdf |
| 1978 | 7.1 | 0.05 | mv29_01sacc.pdf |
| 1979 | 6.9 | 0.05 | mv31_08sacc.pdf (1980 report) |

### Phase C — preterm 1968–1979

| Year | Expected % | Tol | Cited source (per CSV) |
|------|------------|-----|------------------------|
| 1968 | 8.9 | 0.05 | Nat1968doc GESTREC; mv22_12 adjacent |
| 1969 | 9.8 | 0.05 | mv22_12sacc.pdf |
| 1970 | 9.3 | 0.05 | mv22_12sacc.pdf |
| 1971 | 9.3 | 0.05 | mv23_08sacc.pdf (1972 report cites 1971) |
| 1972 | 9.6 | 0.05 | mv23_08sacc.pdf |
| 1973 | 9.2 | 0.05 | mv23_11sacc.pdf |
| 1974 | 8.5 | 0.05 | mv24_11s2acc.pdf |
| 1975 | 8.9 | 0.05 | mv25_10sacc.pdf |
| 1976 | 8.8 | 0.05 | mv26_12sacc.pdf |
| 1977 | 8.8 | 0.05 | mv27_11sacc.pdf |
| 1978 | 8.9 | 0.05 | mv29_01sacc.pdf |
| 1979 | 8.9 | 0.05 | mv31_08sacc.pdf (1980 report) |

---

## Six audit lanes (run all)

### Lane 1 — Transcription fidelity (L6) — **highest priority**

For **each of the 34 cells** above:

1. Download or open the cited MVSR PDF (or IOM table / Series 21 report for exceptions).
2. Locate the **national resident all-live-births** percentage (not race-specific subtables unless CSV explicitly says otherwise).
3. Record exact quote, table number, and whether the PDF describes:
   - “low birth weight” / “2,500 grams or less”
   - “premature” / “prior to 37 weeks” / “LMP areas” only
4. Flag **HIGH** if:
   - Value not found in cited document
   - Cite is cross-year (“9.3% in 1970 vs 9.8% in 1969”) but wrong year assigned to target row
   - 1968 LBW relies on 1967 national + 1969 MVSR with no 1968 direct quote
   - 1971 LBW is IOM secondary, not MVSR Final Natality 1971
   - 1979 uses 1980 report (document the sentence: “unchanged from 1979” vs direct 1979 table)

**Spot-check anchors (must pass independent review):**

| Year | Metric | Why it matters |
|------|--------|----------------|
| 1980 | preterm | Phase B template; GESTREC3 denom |
| 1989 | preterm | Unweighted GESTAT3 vs derived `preterm_lt37` in 1990+ |
| 1968 | preterm | GESTREC 0–4 vs GESTREC3 era |
| 1972 | both | First Final Natality 1972 PDF; LMP-area preterm wording |
| 1971 | LBW | 0.06 tolerance + IOM source |
| 1979 | both | Cross-report year (1980 PDF → 1979 target) |

### Lane 2 — Validator logic vs NCHS definitions (L3, L7)

Read `compare_external_targets_v1.py` functions:

- `_weighted_lbw_rate_from_raw`
- `_weighted_preterm_rate_from_raw`
- `_weighted_preterm_rate_from_raw_1968`
- `_unweighted_preterm_rate_from_raw_1989`
- Dispatch in `main()` for `lbw_rate_pct` / `preterm_rate_pct`

Answer explicitly:

1. **Resident filter:** Is `RESTATUS == 4` exclusion correct and consistent with other pre-1990 paths?
2. **LBW:** DBIRWT vs DBWT column choice; grams < 2500; unknown weight excluded from denominator?
3. **Preterm 1980–1988:** Why denominator = GESTREC3 ∈ {1,2} only? Recompute 1980 with code 3 in denominator — does rate drop to ~7% (would fail MVSR 8.9)?
4. **1968 GESTREC:** Is 0–4 = <37 wk faithful to Nat1968doc? What happens if code 5–8 are excluded from denominator?
5. **1972 preterm:** MVSR says “LMP areas” — does national PDF headline match our national microdata path?
6. **1989:** Document break between raw GESTAT3 and 1990+ derived `preterm_lt37` for joint-use users.

If build host available, recompute each anchor year and fill:

| Year | Metric | CSV expected | Recomputed actual | |diff| | Pass at tol? |

### Lane 3 — Independent recomputation (build host)

If `~/Desktop/natality-harmonization/output/yearly_clean/natality_{year}_raw.parquet` exists:

```bash
cd <repo>
uv run python natality/scripts/05_validate/compare_external_targets_v1.py \
  --in ~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet \
  --targets natality/metadata/external_validation_targets_v1.csv \
  --yearly-parquet-dir ~/Desktop/natality-harmonization/output/yearly_clean \
  --out-dir /tmp/rd1b-b-c-audit-validation
```

Then:

1. Confirm summary: **249 pass, 0 fail** (or report failures).
2. List rows where `|actual - expected| > 0.8 * tolerance` (near-misses).
3. `shasum -a 256` gate parquet — must equal `acb5c48a9abf82ac78e6bf210d6be5d62cba6afae271b978b0e53ed528856974`.

```bash
uv run pytest natality/tests/test_pre1990_*.py -v
```

Expected: **19 passed** (3 lbw smoke + 4 preterm smoke + 3 phase_c smoke + resident births tests — verify count matches files).

If parquets absent: state **cannot verify numeric path**; Lane 1 transcription becomes blocking.

### Lane 4 — Smoke test independence (L3, L17)

Compare smoke implementations to validator:

- `test_pre1990_preterm_rate_smoke.py` — does it copy GESTREC3 logic or import from compare script?
- `test_pre1990_rate_phase_c_smoke.py` — only 3 LBW + 3 preterm anchors; is that sufficient?
- Are tests **SHAPE-not-VALUE** per file header, or do they hard-pin stale rates?

**FINDING** if smoke duplicates validator and Lane 1 fails — double false confidence.

### Lane 5 — Regression & inventory (L11)

1. Count CSV data rows for `resident_births` 1968–1989 → expect **22** years (or 205 total resident_births 1968–2024 per README).
2. Count `lbw_rate_pct` + `preterm_rate_pct` 1968–1989 → expect **44**.
3. Total external validation targets → expect **249** (verify by running compare or counting unique metric×year×universe rows).
4. Confirm Phase A childstats LBW 1980–1989 targets unchanged in `git diff d7da1bf^..2b37ee1` except comment lines.
5. README / natality/README / KICKOFF headlines match 249/249 arithmetic.

### Lane 6 — Cross-era comparability & receipt §10 risks

Explicitly judge these **known risks** from receipts (PASS only if you confirm acceptable with evidence):

| Risk | Source | Audit question |
|------|--------|----------------|
| Preterm denom excludes GESTREC3 code 3 | Phase B receipt §10 | Alternate NCHS denom would invalidate targets? |
| 1989 preterm ≠ 1990+ derived | Phase B receipt §10 | Documented in COMPARABILITY.md? |
| 1968 preterm ≠ 1972+ LMP narrative | Phase C receipt §10 | Is 8.9% target still publishable? |
| 1979 from 1980 PDF | Phase C receipt §10 | Is 8.9% / 6.9% correctly attributed to 1979? |
| 1971/1973 LBW 0.06 tol | DECISION_LOG | Masking real bias or honest rounding? |
| 1968 LBW indirect cite | Phase C | Should §15.F close with this cell flagged defer? |

Recommend whether §15.F robustness roadmap can **close** after B+C or needs follow-up transcription for 1968 LBW / 1971 LBW.

---

## Red-team scenarios (try to break PASS)

1. **Wrong denominator:** Include GESTREC3=3 in preterm denominator for 1985 — does “pass” disappear?
2. **Wrong year transcription:** Swap 1973 LBW 7.6 with 1972 7.7 in CSV — would compare still pass on mislabeled row?
3. **Foreign births:** Include RESTATUS=4 — material rate shift?
4. **1968 GESTREC code 9:** If included in denominator, preterm rate change > 0.05?
5. **SAMPWT:** For 1972, compare uniform 2× vs per-record SAMPWT — >0.05 delta on LBW or preterm?
6. **IOM vs MVSR 1971:** IOM Table B.1 says 7.64% — is target 7.6 defensible or should expected be 7.64?

---

## Consolidated verdict rubric

| Verdict | Meaning |
|---------|---------|
| **PASS** | All 34 new cells independently transcribed; validator definitions defensible; 249/249 reproduced or failure explained by missing parquets only; no §7 issues |
| **PASS-WITH-NOTES** | Transcription sound but 1–3 med issues (indirect cites, 0.06 tol, cross-year PDF) — safe for §15.F close with documented comparability caveats |
| **FAIL** | Any wrong transcription, wrong year, or validator definition mismatch > tolerance class |
| **HALT** | Gate SHA changed; derived path used where raw required; invented numbers (L6 confirmed) |

---

## Suggested time budget

- Lane 1 (PDF transcription): **40–60%** of effort — do not skip cells
- Lane 2–3 (validator + recompute): **25–35%**
- Lanes 4–6: **15–25%**

---

## What to return to the human (short cover note)

1. Executive verdict table (Phase B, Phase C, combined).
2. Count of findings by severity.
3. List of cells requiring re-transcription or tolerance/source amendment (if any).
4. Clear **yes/no**: “Is 249/249 publication-honest for the manuscript robustness section?”
5. Clear **yes/no**: “May §15.F close?”

Do not implement fixes in the audit session unless asked.
```

---

## Quick reference — key file paths

| Artifact | Path |
|----------|------|
| Targets CSV | `natality/metadata/external_validation_targets_v1.csv` |
| Validator | `natality/scripts/05_validate/compare_external_targets_v1.py` |
| Phase B receipt | `RECEIPTS/RD.1b-pre-1990-natality-rate-benchmarking-phase-b_2026-05-24T18-00-00Z.md` |
| Phase C receipt | `RECEIPTS/RD.1b-pre-1990-natality-rate-benchmarking-phase-c_2026-05-25T02-05-00Z.md` |
| Phase A receipt | `RECEIPTS/RD.1b-pre-1990-natality-rate-benchmarking-phase-a_2026-05-24T22-57-47Z.md` |
| Halt matrix | `NEXT_STEPS.md` §7–§8 |
| Task spec | `NEXT_STEPS.md` §15.F RD.1b |

**Commits:** `d7da1bf` (Phase B), `2b37ee1` (Phase C)
