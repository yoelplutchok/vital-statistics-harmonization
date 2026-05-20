# Adversarial Audit — fetal-death-codebook-comparability-v240

Auditor: fresh-eyes adversarial pass.
Auditor invocation timestamp (harness `currentDate`): 2026-05-19T22:45:00Z.
Repo append-only clock (per STATUS soft-flag): 2026-05-23T21:30:00Z. Both clocks reference the same wall-clock session; the offset is a known, documented soft-flag — not a finding.

## Scope

Single commit **`6eecda2`** (tag `fetal-death-codebook-comparability-v240-complete`): the re-paragraphing of `fetal_death/CODEBOOK.md` (hand-body, lines 1–258 pre-DO) + `fetal_death/COMPARABILITY.md` (whole file) from the V2.0/1992-2022/29-year/1,634,195-rec envelope to v2.4.0/1982-2024/43-year/2,427,233-rec/7-era.

Out of scope: editing the auto-generated C8.20 appendix (out per audit instruction; SHA-invariant verified); re-litigating C8.17/C8.18/V3a/V3b decisions; this-session RECEIPTS/STATUS/DECISION_LOG/PRE_FLIGHT_LOG entries dated 2026-05-23T21:00:00Z or later (not read, per instruction).

Permitted reads exercised: `git show 6eecda2 -- fetal_death/CODEBOOK.md fetal_death/COMPARABILITY.md`; both post-edit docs; the C8.20 marker-extracted appendix; the pre-edit docs at `560c754`; pre-this-session STATUS entries dated 2026-05-12 (T02:45 V2.1 / T14:30 V3a / T16:45 V3b layout / T18:45 V3b complete / T23:30 C8.2); README.md.

## Checks performed

### Check 1 — Envelope numeric sum (CRITICAL)

Re-derived each era's count independently from the C8.20 appendix `version_flag` (i)-panel and summed in Python:

```
421,125 + 188,909 + 700,704 + 107,782 + 510,528 + 204,923 + 293,262 = 2,427,233
```

- Matches doc claim (CODEBOOK L35 / L63; COMPARABILITY L4 / L18): ✓
- Matches README.md L18 "Fetal death | 1982–2024 (43 years) | 2,427,233": ✓
- Sum byte-exact. **PASS.**

### Check 2 — C8.20 appendix SHA invariant (CRITICAL — §7-#18 reproducibility)

Marker-extracted appendix (from `<!-- C8.20-GENERATED:BEGIN -->` onward), `shasum -a 256`:

| Source | SHA-256 |
|---|---|
| `fetal-death-codebook-comparability-v240-pre-do:fetal_death/CODEBOOK.md` | `b27640eeb6eda142fa6c2e84a951ee662ea17ba1597f207d22e586c33afd9140` |
| Current `fetal_death/CODEBOOK.md` (on disk, post-commit) | `b27640eeb6eda142fa6c2e84a951ee662ea17ba1597f207d22e586c33afd9140` |
| `560c754:fetal_death/CODEBOOK.md` (PRE-FLIGHT) | `b27640eeb6eda142fa6c2e84a951ee662ea17ba1597f207d22e586c33afd9140` |

All three SHAs byte-equal `b27640eeb6eda142…`. Confirms agent claim of marker-extracted byte-identical appendix. **PASS.**

### Check 3 — Within-era preservation (diff classification)

Ran `git show 6eecda2 -- fetal_death/CODEBOOK.md fetal_death/COMPARABILITY.md`. Every +/- line classifies as **envelope-correction (E)** or **addition (A)**; **zero within-era-mutation (WEM)**:

**CODEBOOK.md (15 hunks):**
- Title: V2.0/1992-2022 → v2.4.0/1982-2024 — E
- Row-counts: 1,634,195 → 2,427,233 (×2) — E
- Year-coverage para (L34): rewritten 4-era→7-era — E
- C8.20 scope-note (L37): rewritten — E
- Variable-availability matrix preamble (L47): added parquet-derived note — E (addition)
- Era table: expanded 4 rows → 7 rows; "mixed A/S" → exact %s; 2018-2022/218,040 → 2018-2024/293,262 — E
- Old V1 subtotal line (510,528+204,923+218,040=933,491+700,704=1,634,195): removed — E (stale-envelope removal)
- New paragraph (L66) on V3b/V3a/V2.1 + B3 race extension — A
- "these era labels" → "the V2/V1 era labels" — E
- L77 `data_year` Notes: dropped "verified 1,634,195/1,634,195 in V2.0" — E (see soft note #3 below)
- L80 `tabulation_flag` Notes: V2.0-slice scoping + C8.20 pointer — E (condensation-honest)
- L89 reporting-flags zip filename: V2-specific → generic per-year — E
- L98 `education_cat4`: "not provided by V2.0" → "not provided by this resource" — E
- L106 V3b/V2.1 quirks pointer — A
- L114 "(4 eras: 1992,2006,2014,2022)" parenthetical removed — E
- L117 layout-pointer: single 1992 → per-era — E

**COMPARABILITY.md (10 hunks):** title; 29-year→43-year; "four"→"seven" file-format eras; era table 4→7 rows (with 2018-2022/218,040→2018-2024/293,262 + record-length parity); new V3b/V3a/V2.1 paragraph; new 1982-1991 row in version_flag table; "29-year span"→"43-year span"; "leaving 218,040 records"→"leaving 293,262 records"; recommendation periods 1992-2022→1982-2024 + 1992-2017→1982-2017 (with V3b B3 1-digit recode mention); "not provided by V2.0"→"not provided by this resource"; "2018-2022"→"2018-2024" (×3); "full 1992-2022 file"→"full 1982-2024 file"; yearly-raw paragraph V2-specific → era-generic; new V2+V1 matrix preamble paragraph.

**Result: zero within-era mutation.** **PASS.** (One soft concern at L77 captured under "Findings — Soft note #3".)

### Check 4 — Stale-envelope sweep

`grep -nE 'V2\.0,|1,634,195|933,491|29-year|29 years|spans \*\*four\*\*|2018-2022'` on both docs:

- Hand-body of CODEBOOK.md (lines outside C8.20 appendix): **no hits.**
- COMPARABILITY.md: **no hits.**
- C8.20 generated appendix (out of scope): one hit on L359 `data_year` Schema note — see "Out-of-scope observation" below.

Broader sweep (`V2\.0|1,634|29.year|2018.2022|218,040|933,491`) found 3 matches, all legitimate:
- CODEBOOK L62 (tabulation_flag): "V2.0 1992-2022 slice this was ~5,400 and ~63,700" — explicitly scoped + C8.20 pointer. **Legitimate.**
- COMPARABILITY L23: "they were deferred in V2.0" — release-history reference (V2.1 added 2003-04). **Legitimate.**
- COMPARABILITY L239: "V2.0 normalizes the V2 values inside `harmonize.py` (era=='1992' branch)" — release-history phrasing; behaviour persists in v2.4.0. **Legitimate but slightly anachronistic (soft).**

**Hand-body clean. PASS.**

### Check 5 — V3b/V3a/V2.1/B3 narrative factuality

Verified each of 4 claims against pre-this-session STATUS entries (all 2026-05-12, well before this session):

| Claim | Source | Result |
|---|---|---|
| V3b 1982-1988 = 1978-revision | STATUS T18:45Z: "B3… `1978-rev predates 2003-rev split`"; T16:45Z: layout CSV `version`="1978" | ✅ MATCHES |
| V3a 1989-1991 = early 1989-revision (= V2 family) | STATUS T14:30Z: "page 5-6 Data Elements list in 1989/1990/1991 user guides matches 1992 user guide field-by-field" | ✅ MATCHES |
| V2.1 2003-2004 = 1989→2003 transition, 1351/1501-byte layouts | STATUS T02:45Z: "Task 3 V2.1 fetal-death (2003+2004 transition years)"; pre-edit COMPARABILITY L20: "1351-byte and 1501-byte records" | ✅ MATCHES |
| B3 race extended to V3a/V3b with 1978-rev 1-digit MRACE recode + null caveat for V3b | STATUS T18:45Z: "B3 1-digit recode (0/4/5/6/8 → 4 API; 1→1; 2→2; 3→3; 7→null; 9→null). DECISION_LOG documents 7+9=null rationale" | ✅ MATCHES (null caveat = 7+9→null) |

**PASS.**

### Check 6 — Record-length bytes

- **V3b ~200 bytes** — STATUS 2026-05-12T16:45Z documents: "record_layout_1982_1988.csv constructed (87 rows, 200 bytes covered, empirical anchor-field spot-check PASS)" + "Record length = 202 bytes/line (= 200 data + CR+LF)". Source value is exact 200. Doc reads "~200 bytes (1978-rev)" — see Finding #2 below.
- **V2.1 1351/1501 preserved** — Pre-edit (`560c754`) COMPARABILITY L20: "(1351-byte and 1501-byte records respectively)". Post-edit table: "1,351 / 1,501 bytes"; post-edit text (L23): "1,351-byte (2003) and 1,501-byte (2004)". Numbers preserved verbatim; only formatting commas added. **PASS.**

### Check 7 — Per-variable Notes factual sample

Sampled two per-variable Notes that carry specific quantitative counts:

**Sample 1 — CODEBOOK L116 `birthweight`**: "397,397 V2 rows have BW=9999".

Appendix `birthweight` (ii)-panel sentinel disambiguation:
```
1982-1988  9999  220,861
1989-1991  9999   96,799
1992-2002  9999  397,397   ← matches the Note (legacy V2 = 1992-2002 only)
2003-2004  9999   56,359
…
```

If "V2" = legacy 1992-2002: 397,397 ✓. If "V2" = 1982-2002 per L35 redefinition: 220,861 + 96,799 + 397,397 = **715,057** — 80% larger.

**Sample 2 — CODEBOOK L97 `plurality`**: "1,686 of the 1,713 V2 plurality=9 rows are LA-occurrence 1992-1994".

Appendix `plurality` (ii)-panel:
```
1989-1991  9   1,851   ← V3a also has plurality=9 rows
1992-2002  9   1,713   ← matches the Note (legacy V2)
2005-2013  9  40,089
…
```

If "V2" = legacy 1992-2002: 1,713 ✓. If "V2" = 1982-2002: 0 + 1,851 + 1,713 = **3,564** — more than 2× the doc figure. Cross-reference to COMPARABILITY L279 (LA-occurrence narrative): the "1,686 of 1,714 LA-occurrence records" figures use a different denominator (state-occ=19 only) and are internally consistent with 1,713.

**Generated Finding #1 below.**

### Check 8 — Condensation honesty

Inventoried each pre-edit V2.0-era quantitative aside vs the post-edit treatment:

| Aside | Pre-edit | Post-edit | Verdict |
|---|---|---|---|
| `tabulation_flag` (~5,400 / ~63,700 across 29 years; ~42,200 in V1 alone) | rewritten | "in the V2.0 1992-2022 slice this was ~5,400 and ~63,700 rows respectively; for the full v2.4.0 per-era… see Appendix C8.20" | ✅ HONEST (numbers preserved + V2.0-slice scoping + appendix pointer; minor soft note: "~42,200 in V1 alone" sub-figure dropped without replacement) |
| `plurality` (1,686 of 1,713 V2 plurality=9) | untouched | unchanged | ⚠️ silently re-interpretable under L35 gloss (Finding #1) |
| `birthweight` (397,397 V2 rows have BW=9999) | untouched | unchanged | ⚠️ silently re-interpretable under L35 gloss (Finding #1) |
| `singleton` (V2: 1,713 blanks total; 1,686 LA / 27 scattered) | untouched | unchanged | ⚠️ silently re-interpretable under L35 gloss (Finding #1) |
| Bullet "108 V2 rows (1997-2002) have age 50-54" | untouched | unchanged | ✅ explicit (1997-2002) sub-range qualifier preserves accuracy |

The rewrite the agent *actively performed* (tabulation_flag) is honest; the rewrites the agent *did not perform* fall foul of the L35 V2-rebroadening gloss it introduced. Same finding as Check 7 from the inverse angle.

### Era-table % spot-check (parquet-derived assertion)

Verified era-table % numbers reconcile to appendix raw counts byte-exact:

```
V2.1 2003-2004: S=104,824/107,782=0.9726 (claim 97.26%) ✓; A=2,958/107,782=0.0274 (claim 2.74%) ✓; S+A=107,782 ✓
V1 2005-2013:   S=304,962/510,528=0.5973 (claim 59.73%) ✓; A=205,566/510,528=0.4027 (claim 40.27%) ✓; S+A=510,528 ✓
V1 2014-2017:   A=178,700/204,923=0.8720 (claim 87.20%) ✓; S=26,223/204,923=0.1280 (claim 12.80%) ✓; A+S=204,923 ✓
```

**PASS.** Confirms the agent's "every number parquet-derived from C8.20 appendix" claim for the era-table %s.

## Findings

### Finding #1 (significant — H8 / L7 / label-legend mismatch)

**Where:** `fetal_death/CODEBOOK.md` L35 (scope-note) interacting with L97 / L116 / L217 (per-variable Notes).

**What:** L35 introduces a global scope-note rebranding "V2" in per-variable Notes to mean "the pre-2003-revision S-synthesized eras (1982-2002 = V3b+V3a+V2; 1989-revision behaviour for 1989-2002, 1978-revision for 1982-1988)". Three per-variable Notes carry quantitative counts that are factually true *only* for the legacy 1992-2002 sub-slice (700,704 rows), not the 1,310,738-row 1982-2002 union. Cross-checked against the C8.20 appendix (parquet-derived, byte-authoritative):

| Doc claim | If V2 = legacy 1992-2002 | If V2 = 1982-2002 per L35 |
|---|---:|---:|
| L97 plurality: "1,713 V2 plurality=9 rows" | 1,713 ✓ | **3,564** ✗ (0 + 1,851 + 1,713) |
| L116 birthweight: "397,397 V2 rows have BW=9999" | 397,397 ✓ | **715,057** ✗ (220,861 + 96,799 + 397,397) |
| L217 singleton: "V2: 1,713 blanks total" | 1,713 ✓ | **3,564** ✗ (same arithmetic as L97) |
| L255 "108 V2 rows (1997-2002) have age 50-54" | 108 ✓ | OK — explicit (1997-2002) qualifier saves it |

Also creates internal label conflict: the variable-availability era table (L55) still names "V2 (1992 era) | 1992-2002 | 700,704" as a discrete era; the L35 gloss says "V2 = 1982-2002" (umbrella); per-variable Notes carry 1992-2002-only counts.

**Class:** H8 (doc-data drift); L7 (looks-right); label-legend mismatch. The agent demonstrated awareness of this exact risk for `tabulation_flag` at L62 (the only Note it actively touched: explicit "V2.0 1992-2022 slice" scoping + C8.20 pointer) but did not apply the pattern to plurality / birthweight / singleton.

**Recommendation:** Either (a) drop the L35 V2-rebroadening gloss and keep "V2 = 1992-2002" everywhere (cleanest; honors the era-table semantics), or (b) apply the tabulation_flag pattern (explicit "V2.0 1992-2002 slice" scoping + "see Appendix C8.20 for the full per-era distribution" pointer) to the plurality / birthweight / singleton Notes.

### Finding #2 (soft / cosmetic)

**Where:** `fetal_death/COMPARABILITY.md` era table (V3b row); also `fetal_death/CODEBOOK.md` variable-availability matrix (V3b row).

**What:** V3b row reads "~200 bytes (1978-rev)". STATUS 2026-05-12T16:45Z documents the exact value: 200 (= 202 with CRLF). The tilde is unnecessary hedging and breaks parity with the V2 row's "360 bytes (362 with CRLF)" and the V1 2022-era row's "2,652 bytes" — both of which give a precise data-byte count.

**Recommendation:** Replace "~200 bytes (1978-rev)" with "200 bytes (202 with CRLF)" for parity with the V2 row.

### Soft note #3

**Where:** `fetal_death/CODEBOOK.md` L77 (`data_year` Notes).

**What:** The L77 reword dropped the pre-edit verification count "(verified 1,634,195/1,634,195 in V2.0)" and did not add a v2.4.0 replacement. The new unqualified "Always equal to int(delivery_year) for every row" is now an asserted invariant with no in-doc evidentiary backing. The C8.20 appendix `data_year` (i)-panel shows 0.00% null/blank across all 7 eras, which would support an updated "verified 2,427,233/2,427,233 in v2.4.0".

**Recommendation:** Optionally add the v2.4.0-scale verification count back, mirroring the pre-edit style.

### Out-of-scope observation

The C8.20 generated appendix `data_year` Schema note (CODEBOOK L359) still reads `1992-2022 — … verified 1,634,195/1,634,195 in V2.0`. This is stale V2.0 prose embedded in the parquet-derived appendix — an upstream `scripts/_build_codebook_extensions.py` generator-input issue (the Schema note source is likely `harmonized_schema.csv`'s `notes` column), not this commit's responsibility. The appendix is byte-identical and marker-extracted correctly per Check 2; the commit correctly did not hand-edit the appendix.

## Verdict

Commit `6eecda2` cleanly executed the envelope and cross-era-narrative re-paragraph, preserved the C8.20 appendix byte-identical, and made **no within-era data-mutation** (Check 3 zero WEM; Checks 1/2/4/5/6/era-table all PASS).

One **significant doc-coherence finding** (Finding #1: L35 V2-rebroadening gloss vs un-rescoped per-variable Notes — a label-legend mismatch making 3 within-era counts ambiguous/silently-wrong under the new gloss) plus one cosmetic finding (Finding #2: V3b "~200 bytes" tilde) and one soft note (Soft #3: L77 lost verification).

Not a release-blocking class, but Finding #1 warrants either a scope-note simplification or a per-variable-Notes rescoping pass before manuscript submission — the failure mode (reader applying the L35 gloss to L116 and getting a 715,057 vs 397,397 mismatch against C8.20) is exactly the kind of silent doc-vs-data drift the §7-#7 / H8 risk classes are intended to catch.
