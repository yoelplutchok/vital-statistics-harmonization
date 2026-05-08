# V2.0 1992 Record Layout — Extraction Decisions Log

**Authored:** session 2026-04-20 (V2.0 kick-off)
**Scope:** The 1989-revision U.S. Fetal Death public-use layout that applies to data years **1992–2002** (11 uniform years, pre-2003-revision).
**Output:** `record_layout_1992.csv` (in this Zenodo deposit; in the GitHub source repository: `metadata/record_layout_1992.csv`) — the authoritative canonical layout used by the V2 parser.

This document exists so future readers can trace exactly *how* the layout CSV was produced, what was verified against the source, and what was inferred or corrected, without re-doing the work.

---

## 1. Record length: 360 bytes (not 361)

The V2 scope memory said "361-byte layout"; that figure was wrong. Verified against two independent sources:

1. **1992FetalUserGuide.pdf, page 7, Machine/File/Data Characteristics:** `Record length: 360`.
2. **Raw extracted files** from `Fetal{1992,1995,2000,2002}US.zip`: each file is exactly `N × 362` bytes where the last 2 bytes of every line are `\r\n`. That is, 360 data bytes + CRLF terminator per physical line.

Every record in all 4 spot-checked years had a clean `\r\n` terminator (`0` bad terminators across 252,512 records tested). 1992 record count derived from file size exactly matches the 70,929 figure the guide states on page 7.

**Implication:** `RECORD_LEN_1992 = 360` in `scripts/01_import/field_specs.py`. The file reader must be aware that physical lines are 362 bytes (strip CRLF) but field positions are relative to the 360-byte record.

## 2. Year coverage uniformity

Confirmed uniform 360-byte records for all 11 V2 years (1992-2002). The four spot-checked years (1992, 1995, 2000, 2002) were verified at session-open. The remaining seven years (1993, 1994, 1996-1999, 2001) were verified by a follow-on byte-level pass — every year has 360-byte records with clean CRLF terminators and a record-count derivable from file size that matches each year's NVSR 57-08 / user-guide published total.

Background:
- The 1989 U.S. Standard Report of Fetal Death was in effect nationally from January 1989 through end of 2002 (superseded by the 2003 revision, which phased in over 2003-2014).
- The 2003 and 2004 years have known distinct transition layouts (1351 and 1501 bytes respectively, per pre-session fetch probing) — confirming the uniform era ends in 2002.

## 3. CSV schema and naming conventions

Matches existing V1 format exactly:

```
position_start, position_end, length, field_name, description, version, values_summary, notes
```

- **`version` column:** set to `1989` for every row (the 1989 U.S. Standard Report of Fetal Death). This distinguishes 1992-era fields from V1's `A` / `S` / `A,S` tags (2003-revision / 1989-revision / both), which only make sense post-2003 when the two revisions coexisted.
- **Reserved/unused positions:** labeled `FILLER` (matching the 2014 and 2022 CSV convention; 2006 CSV used a mix of `FILLER` and `BLANK`, we standardize on `FILLER`). The 1992 guide sometimes gives reserved spans a placeholder name like `R2A`, `R5A`, `WA`, `R4B`; these placeholder names are recorded in the `notes` column but not used as `field_name`.

## 4. Umbrella vs atomic field policy

The 1992 guide defines several "umbrella" fields that are themselves composed of atomic sub-fields (e.g., `FOCCUR` 12–27, `FRESID` 28–59, `LMPDATE` 121–128, `LLBDATE` 129–134, `MEDINFO` 220–314, `B5EDRISK` 228–244, `LABOR` 263–278, `CONGENIT` 279–300, `FLRES` 315–339). These umbrellas duplicate their subfields.

**Decision:** CSV contains only **atomic** rows (no umbrella rows). Umbrella groupings are noted in the `notes` column of their first sub-field. Rationale: V1 record_layout CSVs follow the same convention, and the parser consumes atomic rows only.

## 5. PDF OCR corrections

The 1992 user guide's PDF text extraction has systematic OCR corruption — tildes, stray punctuation, glyph substitution. The following field names in the CSV are **corrected from the PDF text**; every correction is annotated in the `notes` column of its row. The original PDF token is preserved in the note so auditors can trace the correction.

| Position | Corrected name | Raw PDF token | Basis for correction |
|---|---|---|---|
| 13 | `DIVOCC` | `Drvocc` | Description "Division of Occurrence"; consistent with `DIVRES` at 29 |
| 76 | `ORMOTH` | `OI?MOTH` | Description "Hispanic Origin of Mother"; consistent with `ORFATH` at 165 |
| 81 | `MRACE3` | `ldItAcF13` | Description "Race of Mother Recode"; pattern matches `FRACE4` / `FRACE3` recodes elsewhere |
| 82–83 | `DMEDUC` | position shown as `82-03` | Guide narrative confirms positions 82–83; analogous to `DFEDUC` at 170–171 |
| 86 | `DMAR` | `mu-m` | Description "Marital Status of Mother"; reporting flag is `DMARF` at 321 |
| 123–124 | `LMPDAY` | `LKPDAY` | Part of `LMPDATE` umbrella; description "01-31 As applicable to month of LMP" |
| 185 | FILLER (labeled `WA`) | `WA` | Guide text explicitly says "Reserved Position"; name retained only in note |
| 196 | `GESTIMP` | `GESTIM.P` | Description "Gestation Imputation Flag"; stray period is an OCR artifact |
| 202 | `FSEXIMP` | `FSEX~` | Description "Sex Imputation Flag"; tilde is an OCR artifact |
| 215 | `DPLURAL` | `DPLUR.AL` | Description "Plurality"; matches V1 `DPLURAL` naming in 2005–2022 |
| 227 | `DELMETH6` | `DEmTH6` | Description "Method of Delivery Recode"; **canonical name confirmed from clean 1998 & 2002 guides** — initial reconstruction `DMETH6` was wrong, corrected 2026-04-21 |
| 239 | `PRE4000` | `PRE4 000` | Description "Previous infant 4000+ grams"; space is an OCR artifact |
| 242 | `RH` | `~` (single tilde) | Description "Rh sensitization"; name inferred from description text |
| 244 | `OTHERMR` | `OTHE~` | Description "Other Medical Risk Factors"; OCR dropped final chars |
| 258 | `INDUCT` | raw PDF shows `250 INDUCT` (position mis-OCR) | Description "Induction of labor"; sequential position between `MONITOR` (257) and `STIMUL` (259); confirms 258 |
| 259 | `STIMULA` | `ST=A` | Description "Stimulation of labor"; **canonical name confirmed from clean 1998 & 2002 guides** — initial reconstruction `STIMUL` was wrong, corrected 2026-04-21 |
| 264 | `MECONIUM` | `WCONIUM` | Description "Meconium"; initial `M` OCR'd as `W` |
| 279 | `ANEN` | `~` | Description "Anencephalus"; listed first in the 22-position CONGENIT block; **canonical name confirmed from clean 1998 & 2002 guides** — initial reconstruction `ANENCEPH` was wrong (that form only appears as narrative prose later in the guides; layout column is `ANEN`), corrected 2026-04-21 |
| 283 | `NERVOUS` | `~RVOUS` | Description "Other central nervous system anomalies" |
| 287 | `TRACHEO` | `T~CHEO` | Description "Tracheo-esophageal fistula/Esophageal atresia" |
| 326 | `DELMETRF` | `DHJ4ETRF` | Reporting flag for "Method of delivery"; **canonical name confirmed from clean 1998 & 2002 guides** — initial reconstruction `DMETHF` was wrong, corrected 2026-04-21 |
| 334 | `CLABOR` | `33=4` (position mis-OCR) | Sequential reporting flag position; description "Complications of labor and/or delivery" |

All OCR-corrected names were re-verified against the cleaner 1998 and 2002 user guides. Four names required correction: `DMETH6 → DELMETH6` (pos 227), `STIMUL → STIMULA` (259), `ANENCEPH → ANEN` (279), `DMETHF → DELMETRF` (326). All other names confirmed canonical.

## 6. Gap at positions 48–52

The list of data elements (guide pages 5–6) documents residence FIPS fields at 43–44 (state), 45–47 (county), 53–54 (CMSA), 55–58 (PMSA/MSA). Positions 48–52 (5 bytes) are **not** documented as any named field in the detail record. The pypdf parser extracted an umbrella `FIPSRES` spanning 43–58, so 48–52 is an undocumented internal gap — likely reserved space for future FIPS fields not populated in the public-use file.

**Decision:** labeled `FILLER` with a note, then validated empirically against the raw bytes.

**Empirical confirmation:** all 70,929 records in 1992 have bytes 48-52 = `b'     '` (five ASCII spaces, single distinct value across the full file). FILLER decision is empirically confirmed.

## 7. Sentinel value conventions (for reference)

Based on the guide's code outlines, 1992-era sentinels are:

- **Unknown age / count (2-digit field):** `99`
- **Unknown age / count (1-digit):** `9`
- **Unknown year:** `9999`
- **Unknown weight:** `9999` grams
- **Not classifiable risk factor / anomaly / procedure:** `9`
- **Not on certificate:** `8`
- **Not reported by state:** `2` (risk/proc/anomaly blocks); `0` in reporting flags
- **Foreign resident (geography):** `4` in `RESTATUS`; `Z` / `ZZZ` in population-size and MSA codes
- **No prior live birth (`LLBYR`):** `9999` or `7777`

These must match V1's sentinel convention (retain raw codes in harmonized file; derived file converts to NaN before threshold comparisons).

## 8. External validation source

The V2 era is validated against the NVSR Fetal & Perinatal Mortality series (MacDorman et al., NVSR 57(8), "Fetal and Perinatal Mortality, United States, 2005"), Tables A and B. NVSR 57-08 publishes per-year fetal death counts and rates for 1995-2002 (8 years). For 1992-1994 (a documented gap in the NVSR Fetal & Perinatal Mortality series), the 1992-1994 NCHS Fetal Death User Guide control counts are the authoritative source; all three match the parsed counts exactly. Three known stale-guide years (1996, 2001, 2002) — where the user-guide control block was copy-pasted from an adjacent year — are resolved in favor of NVSR 57-08, which matches the parsed counts. **Total V2 external validation: 19/19 exact (8 NVSR-57-08 counts + 8 NVSR-57-08 rates + 3 user-guide counts).**

## 9. What this layout does NOT contain

- **Cause-of-death (ICD-9) codes.** The 1992 public-use file does not include them; pre-2014 ICD codes are only available via the NCHS Research Data Center. Dropped from V2 scope.
- **State of mother's birth / nativity.** Not in the 1989 revision.
- **BMI / prepregnancy weight / height.** Not in the 1989 revision (added in 2003 revision).
- **WIC / DDC / infertility treatment flags.** Not in the 1989 revision.
- **Maternal morbidity (MM_*).** Not in the 1989 revision.

These will all be `NaN` / absent in the harmonized V2 output for 1992–2002; the crosswalk must mark them `not_available`.

---

## Change log

- 2026-04-20: Initial extraction and decisions (this document).
- 2026-04-21: Byte-level verification pass across the remaining seven years (1993, 1994, 1996-1999, 2001) confirmed uniform 360-byte records. Applied four canonical-name corrections from the cleaner 1998 and 2002 user guides: `DMETH6`→`DELMETH6` (pos 227), `STIMUL`→`STIMULA` (259), `ANENCEPH`→`ANEN` (279), `DMETHF`→`DELMETRF` (326). Added empirical confirmation of FILLER 48-52 (§6).
- 2026-04-22: V2 external validation closed — 19/19 exact (§8).
- 2026-04-22: Cross-era harmonization fixes B4/B5/B6 and `delivery_place_unrevised` applied and re-verified; V1 2005-2022 slice held byte-clean (0 of 73 harmonized + 0 of 89 derived columns drifted).
