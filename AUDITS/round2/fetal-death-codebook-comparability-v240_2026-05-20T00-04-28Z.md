# Round 2 adversarial audit: fetal-death codebook / comparability v2.4.0 re-paragraph

**Auditor:** Fresh-eyes Round 2 (independent; did not read Round 1 audits or session receipts)  
**Scope commit:** `6eecda2` (tag `fetal-death-codebook-comparability-v240-complete`)  
**Files in scope:** `fetal_death/CODEBOOK.md` hand-body (lines 1–258 pre-`<!-- C8.20-GENERATED:BEGIN -->`) + `fetal_death/COMPARABILITY.md` (whole file)  
**Out of scope:** C8.17/C8.18/V3a/V3b decision re-litigation; hand-editing the C8.20 appendix  
**Audit UTC:** 2026-05-20T00:04:28Z

---

## Verdict (no HALT)

| Check | Result |
|-------|--------|
| 1 Envelope numeric sum | **PASS** |
| 2 C8.20 appendix invariant | **PASS** |
| 3 Within-era preservation | **PASS** (no within-era mutations in diff) |
| 4 Stale-envelope sweep | **PASS** (hand-body + COMPARABILITY); informational appendix residue |
| 5 V3b/V3a/V2.1 narrative factuality | **PASS** |
| 6 Record-length bytes | **PASS** |
| 7 Per-variable notes sample | **PASS** (counts verified); **ADVISORY** on legacy “V2” label vs counts |
| 8 Condensation honesty | **PASS** |

**§7-#18 reproducibility HALT:** Not triggered. Appendix extraction SHA matches pre-DO tag byte-for-byte.

---

## Halt criterion

Per audit charter:

- **Trigger HALT** if Check 2 appendix SHA ≠ `b27640eeb6eda142…` → **not triggered**.
- **No other automatic HALT** defined for this round. Residual risks are documented below; none block acceptance of commit `6eecda2` for the stated hand-body re-paragraph scope.

---

## Check 1 — Envelope numeric sum-check

**Claim (hand-body):** Seven era counts 421,125 + 188,909 + 700,704 + 107,782 + 510,528 + 204,923 + 293,262 = 2,427,233.

**Recompute:**

```text
python3: sum([421125,188909,700704,107782,510528,204923,293262]) → 2,427,233  ✓
```

**Independent derivation from C8.20 `version_flag` (i)-panel `n` column** (lines 287–293 of current `CODEBOOK.md`):

| Era | n (appendix) |
|-----|-------------|
| 1982-1988 | 421,125 |
| 1989-1991 | 188,909 |
| 1992-2002 | 700,704 |
| 2003-2004 | 107,782 |
| 2005-2013 | 510,528 |
| 2014-2017 | 204,923 |
| 2018-2024 | 293,262 |
| **Sum** | **2,427,233** |

**README cross-check:** `README.md` four-products row: `Fetal death | 1982–2024 (43 years) | 2,427,233` — **matches**.

**Parquet provenance (optional):** `~/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_derived.parquet` on disk; `shasum -a 256` prefix `185c071ec76a…` matches hand-body / appendix provenance line.

---

## Check 2 — C8.20 appendix invariant (CRITICAL)

```bash
git show fetal-death-codebook-comparability-v240-pre-do:fetal_death/CODEBOOK.md \
  | awk '/<!-- C8.20-GENERATED:BEGIN/{f=1} f' | shasum -a 256
# → b27640eeb6eda142fa6c2e84a951ee662ea17ba1597f207d22e586c33afd9140

awk '/<!-- C8.20-GENERATED:BEGIN/{f=1} f' fetal_death/CODEBOOK.md | shasum -a 256
# → b27640eeb6eda142fa6c2e84a951ee662ea17ba1597f207d22e586c33afd9140
```

**Result:** Byte-identical. Hand-body edits did not touch the generated appendix.

---

## Check 3 — Within-era preservation

`git diff 560c754..6eecda2 -- fetal_death/CODEBOOK.md`: **44 insertions, 36 deletions** (106 diff lines total). **Zero changes** below `<!-- C8.20-GENERATED:BEGIN -->`.

**Classification of every `+`/`-` hunk:**

| Hunk | Classification |
|------|----------------|
| Title / row counts / year-coverage paragraph | envelope-correction |
| v2.4.0 scope note (deferral → re-paragraphed) | envelope-correction |
| Variable availability matrix (4 → 7 eras, counts, V3b/V3a/V2.1 prose) | envelope-correction |
| `data_year` note: removed `1,634,195/1,634,195 in V2.0` | envelope-correction |
| `tabulation_flag` quantitative aside reword | envelope-correction + Check 8 (scoped to V2.0 slice) |
| Reporting-flags / Source crosswalk / raw-parquet year range | envelope-correction |
| Data Quality §6 bullet (V3b/V3a/V2.1 pointer) | envelope-correction |
| `education_cat4` “not provided by V2.0” → “this resource” | neutral wording (no numeric change) |

**Per-variable quantitative notes unchanged in diff** (verified unchanged on disk): e.g. `397,397 V2 rows` (birthweight), `1,686 of the 1,713 V2 plurality=9`, `700,704` paternal_age, `3/700,704` GA quirk, `108` maternal_age 50–54, etc.

**Within-era-mutation signals:** **None.**

---

## Check 4 — Stale-envelope sweep

Patterns: `V2\.0,|1,634,195|933,491|29-year|29 years|spans \*\*four\*\*|2018-2022`

### `fetal_death/COMPARABILITY.md` (post-`6eecda2`)

**No matches.** Era table uses `2018-2024`; “four eras” removed.

### `fetal_death/CODEBOOK.md` hand-body (lines 1–258)

**No matches** for forbidden stale-envelope patterns.

**Intentional within-era references retained** (not sweep failures): e.g. `1992-2022` in `data_year`/`delivery_year` Values columns; `1992-2002` in `version_flag` synthesis note; per-table “1992 era” / “2006 era” labels — consistent with scope note that per-variable tables remain V2/V1-detail for those eras.

### Appendix residue (informational, out of edit scope)

Line 359 (inside C8.20, auto-generated): `_Schema note:_ 1992-2022 … verified 1,634,195/1,634,195 in V2.0`. Pre-existing; unchanged per Check 2. Not a failure of this commit’s hand-body work; flag for a future `_build_codebook_extensions.py` regeneration if envelope-wide schema notes should update.

---

## Check 5 — V3b / V3a / V2.1 narrative factuality

Sources: `STATUS.md` sections **2026-05-12T14:30:00Z** (V3a), **2026-05-12T16:45:00Z** (V3b layout), **2026-05-12T18:45:00Z** (V3b complete), **2026-05-12T02:45:32Z** (V2.1), **2026-05-12T23:30:00Z** (C8.2 / 2,427,233).

| Doc claim | Upstream support |
|-----------|------------------|
| V3b 1982-1988 = 1978-revision | STATUS 16:45Z: `record_layout_1982_1988.csv`, version `"1978"`, 200-byte layout |
| V3a 1989-1991 = early 1989-revision (= V2 family) | STATUS 14:30Z: 1989/90/91 guides page 5-6 match 1992 field-by-field; harmonize era 1989-2002 |
| V2.1 2003-2004 = 1989→2003 transition, 1351/1501-byte layouts | STATUS 02:45Z Task 3; pre-edit `COMPARABILITY.md` §Era (“1351-byte and 1501-byte”) |
| B3 extended to V3a/V3b; 1978-rev 1-digit MRACE recode; null caveat for V3b | STATUS 14:30Z B3 `08`/`09`; STATUS 18:45Z / 16:45Z notes on codes 7/9 → null (1978-rev residual) |
| 2,427,233 / 43 years / 7 eras | STATUS 23:30Z C8.2; appendix `version_flag` panel |

**Unsupported claims:** None found in scoped narrative additions.

---

## Check 6 — Record-length bytes

| Claim | Verification |
|-------|----------------|
| V3b ~200 bytes | STATUS 2026-05-12T16:45:00Z: “87 rows, **200 bytes covered**”; empirical 202 bytes/line = 200 + CRLF |
| V2.1 1,351 / 1,501 | Pre-edit `git show 560c754:fetal_death/COMPARABILITY.md`: “1351-byte and 1501-byte” — **survived verbatim** (comma-formatted `1,351 / 1,501` in post-edit table) |

---

## Check 7 — Per-variable notes factual sample

### Sample A — `birthweight` (line 116): “397,397 V2 rows have BW=9999”

**Appendix C8.20** `birthweight` sentinel panel:

- `1992-2002` era: `9999` → **397,397** (56.71%) — **byte-exact match**.

**Scope note:** Count is for the **1992-2002** layout era only, not the expanded glossary “V2” = 1982-2002 (V3b has 220,861; V3a has 96,799 per appendix). Numbers are **not stale** for 1992-2002; label ambiguity is the risk (see Advisory).

### Sample B — `plurality` (line 97) / `singleton` (line 217): “1,686 of the 1,713 V2 plurality=9 rows”

**Appendix:** `1992-2002` `plurality=9` count = **1,713** (sentinel panel line 1009) — matches denominator.

**Upstream:** `fetal_death/COMPARABILITY.md` §11 (line 279): “1,686 of 1,714 LA-occurrence records” — numerator traceable to prior verification (C8.15 / raw STATEFET=19 convention); 1,713 is all V2-era `plurality=9`, of which 1,686 are LA 1992-1994 occurrence.

**Stale V2.0-slice?** No — counts remain valid for 1992-2002; not silently forwarded to full v2.4.0 envelope.

### Advisory (L7 / H8 — label, not arithmetic)

Line 12 redefines legacy **“V2”** as 1982-2002 (V3b+V3a+V2), but per-variable Notes still use **“V2”** with counts that are **1992-2002-era only** (and table “Years” still say `1992 era`). A reader applying the new glossary could mis-scope counts. Mitigation already partial: appendix + era matrix disambiguate; residual doc UX risk only.

---

## Check 8 — Condensation honesty

### `tabulation_flag` (line 62)

| | Text |
|---|------|
| **Pre-edit** | “~5,400 V1 flag-2 … ~63,700 flag-1 rows across all **29 years** (~42,200 in V1 alone)” |
| **Post-edit** | “in the **V2.0 1992-2022 slice** this was ~5,400 and ~63,700 rows respectively; for the full v2.4.0 per-era … see **Appendix C8.20**” |

**Assessment:** V2.0-slice numbers **preserved** with explicit slice label + appendix pointer. Did **not** silently forward 29-year figures to v2.4.0. **PASS.**

### `education_cat4` “not provided by V2.0” → “not provided by this resource”

No quantitative claim; neutral. **PASS.**

---

## Residual risks (honest, not cheerleading)

1. **Legacy “V2” label vs 1992-2002 counts** (Check 7 advisory): arithmetic correct; glossary widened. Low severity; fix would be clarifying “V2 (1992-2002)” in Notes or narrowing the glossary sentence.
2. **Per-variable tables still show 1992-2022 value ranges** in Identification rows while envelope is 1982-2024 — documented deferral in scope note; not a regression introduced by this diff.
3. **Appendix `data_year` schema note** still cites V2.0 / 1,634,195 — auto-generated stale text; regenerate script when envelope-wide appendix notes are in scope.
4. **Other fetal_death/*.md** (GETTING_STARTED, FAQ, etc.) still carry V2.0 envelope — **out of this commit’s scope**; project-wide doc sync remains open.

---

## Commands log (reproducibility)

```bash
# Check 2
git show fetal-death-codebook-comparability-v240-pre-do:fetal_death/CODEBOOK.md \
  | awk '/<!-- C8.20-GENERATED:BEGIN/{f=1} f' | shasum -a 256
awk '/<!-- C8.20-GENERATED:BEGIN/{f=1} f' fetal_death/CODEBOOK.md | shasum -a 256

# Check 1 sum
python3 -c "print(sum([421125,188909,700704,107782,510528,204923,293262]))"

# Check 3
git diff 560c754..6eecda2 -- fetal_death/CODEBOOK.md fetal_death/COMPARABILITY.md

# Parquet (if present)
shasum -a 256 ~/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_derived.parquet
```

---

**End of Round 2 audit.**
