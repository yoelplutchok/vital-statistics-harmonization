# Source data: NCHS Matched Multiple Birth and Fetal Death files

NCHS publishes three matched-multiples public-use linkage files at the canonical FTP path:

```
https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/matched-multiples/
```

with companion user-guide PDFs at:

```
https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/Dataset_Documentation/DVS/matched-multiples/
```

All three were probed and validated at C8.16 PRE-FLIGHT (2026-05-14T02:30:00Z; STATUS.md + DECISION_LOG.md entries) per L1-extension (sibling-derivation discipline) and L12-extension (PDF text-layer check before assuming OCR is needed; PASS on all 87 PDF pages).

## File-by-file detail

### 1995-1997 — *The Matched Multiple Birth File* (first generation)

| Item | Value |
|---|---|
| Raw filename | `1995-1997.zip` (contains `sets9597.public`) |
| Raw zip SHA-256 | `5675d57d198d1870c600500edb72c95a1f9e7cb426c451192f1641ab791a50a7` |
| Doc filename | `1995-1997.pdf` (33 pages) |
| Doc PDF SHA-256 | `f982ad93fbd435484173d6a08014e503e7f45208994cf1305b20ad0cae675d66` |
| Record format | Fixed-width 502 bytes per record (content; CRLF-terminated → 504 bytes per line) |
| Total records | 324,490 (empirical; PRE-FLIGHT 325,135 was a file-size / record-length division estimate) |
| Plurality covered | Twins + triplets only (quadruplets excluded per confidentiality) |
| Cause-of-death coding | ICD-9 only |
| Cert revision | 1989 |
| Authors | Joyce A. Martin, M.P.H.; Sally A. Curtin, M.A.; Margaret L. Saulnier, M.A.; Jaleh Mousavi, B.A. |

### 1995-2000 — *The Matched Multiple Birth File* (expanded second generation)

| Item | Value |
|---|---|
| Raw filename | `1995-2000.zip` (contains `Sets9500.public`) |
| Raw zip SHA-256 | `8315dd24c9be2f034fd494b55362b4a022e7a69668432461cdacd35c85de28e3` |
| Doc filename | `1995-2000.pdf` (33 pages) |
| Doc PDF SHA-256 | `07b7260d4284402f9068f9dc160612b0fb0240fdd0536c6c1ad1d0ffd478b886` |
| Record format | Fixed-width 754 bytes per record (content) |
| Total records | 699,144 (empirical) |
| Plurality covered | Twins + triplets + **quadruplets** |
| Cause-of-death coding | ICD-9 (1995-1998 records) + **ICD-10** (1999-2000 records); both blocks present in every record |
| Cert revision | 1989 |
| Authors | Joyce A. Martin, M.P.H.; Brady E. Hamilton, Ph.D.; Candace M. Cosgrove, M.P.H.; Sally A. Curtin, M.A.; Margaret L. Saulnier, M.A.; Martha L. Munson, M.S. |

### 2016-2020 — *The Matched Multiple Birth and Fetal Death File* (third generation; 2003-revision)

| Item | Value |
|---|---|
| Raw filename | `2016-2020.zip` (contains `MULTIPLES.TXT`) |
| Raw zip SHA-256 | `4e45d5315b24d2c6d7c98a15e8bd9279c057a50b2c4ef651659ad19b19e28d8b` |
| Doc filename | `2016-2020.pdf` (21 pages) |
| Doc PDF SHA-256 | `ed5e96ab662e970dc8fab3295942b3dfffac8c845120b8e92e125cf7d39152be` |
| Record format | **Variable-length** 155-157 bytes per record (UCODR130 trailing-blank stripped) |
| Total records | 641,934 (empirical; matches PDF Table 1 byte-exact) |
| Plurality covered | Twins + triplets + quadruplets (no quintuplets+ per confidentiality) |
| Cause-of-death coding | ICD-10 only |
| Cert revision | 2003 |

## Methodology differences between the three windows

The three generations are **not strict supersession** of one another. Each is a distinct NCHS publication with its own authoring team, inclusion criteria, and column structure:

| Aspect | 1995-1997 | 1995-2000 | 2016-2020 |
|---|---|---|---|
| Quadruplets included | No | Yes | Yes |
| Records pre-20wk gestation | Yes (matched to ≥20wk sibling) | Yes (matched to ≥20wk sibling) | No (NCHS restricts to ≥20wk fetal deaths at source) |
| Cause-of-death blocks | ICD-9 only | ICD-9 (1995-1998) + ICD-10 (1999-2000) | ICD-10 only |
| Matching algorithm stage | 3-stage (plurality + state + county + DOB + DOD; LMP + tolerance; hand) | 3-stage (similar to 1995-1997) | Algorithm based on PLURAL + XOSTATE + OCNTYFIPS + FACIDS + DOBM_YY/MM/DD + SETORDER; verification via independent state-MATCH variable |
| Verification gold standard | Missouri state-database comparison | Missouri (carried forward) | Two large states with valid MATCH variable (>99% agreement) |
| Set completeness flag (FLGCOMP / COMPLETE) | 0=complete; 1=incomplete; 2=unmatched | Same as 1995-1997 | 1=complete; 2=incomplete (with COUNT=1 implying unmatched) |
| 1992-1994 records | Absent | Absent | Absent (gap predates 2016 cohort) |
| Methodology paper | Internal NCHS doc (no published companion) | Internal NCHS doc | Internal NCHS doc with extended verification narrative |

Users analyzing 1995-1997 records should choose either the 1995-1997 file (full original spec) OR the 1995-2000 file (extended methodology with quadruplets added retrospectively). The two are NOT directly comparable cell-by-cell for the 1995-1997 sub-window because the second-generation file applied its updated matching algorithm to all 1995-2000 records uniformly.

## L13-extension caveat: byte-position-vs-semantics

The 1995-1997 PDF documentation may have a 1-byte off-by-one error around position 115-116 (CLINGEST). The 1995-2000 PDF places CLINGEST at 2 bytes (positions 115-116); the 1995-1997 PDF places CLINGEST at 1 byte (position 115) with DELMETH umbrella at position 116. The two windows share most of positions 1-227 but this region differs. C8.16 DO sub-step 2 (parser) will resolve via empirical value-distribution probing per L13-extension (LESSONS 2026-05-12T01:40:00Z).

## L12-extension caveat: PDF text-layer probe

All three PDFs passed the `page.get_text()` text-extractability probe at PRE-FLIGHT (cumulative 87 pages × ~3500 chars/page average; zero pages text-empty). No OCR needed. This avoids the cascading effort-estimation error documented at LESSONS 2026-05-12T15:00:00Z.

## Variable-length file handling (2016-2020 only)

The 2016-2020 file ships with `UCODR130` (last field; positions 155-157) trailing-blank stripped on a per-record basis. This produces 3 record-length variants:

| Record length (content; no CRLF) | Population | Cause |
|---|---|---|
| 155 bytes | 634,863 records (98.9%) | Survivors + fetal-death (UCODR130 blank) OR 1-digit code |
| 156 bytes | 4,089 records (0.6%) | Infant death with 2-digit UCODR130 |
| 157 bytes | 2,982 records (0.5%) | Infant death with 3-digit UCODR130 |
| **Total** | **641,934** (matches PDF Table 1) | |

The parser at sub-step 2 will handle the variable-length tail by reading each line as text + parsing fixed fields up to position 154 + right-padding UCODR130 to 3 chars before integer conversion. This is documented in `record_layout_2016_2020.csv` notes for the UCODR130 row.

The two older files (1995-1997, 1995-2000) ship strict fixed-width per-record bytes (no trailing-blank stripping).

## Validation targets (RD.2, 2026-05-24)

The NCHS layout PDFs for 1995-1997 and 1995-2000 describe Table 1 structure (BIRTHID outcome totals; complete/incomplete/unmatched sets via FLGCOMP) but **omit printable count tables** — unlike the 2016-2020 PDF, which ships extractable Table 1 *Total* column cells. RD.2 committed byte-exact targets for all three windows in `external_validation_targets.csv` (28 cells for the two older windows) plus the five 2016-2020 PDF Table 1 cells. Target values for 1995-1997 and 1995-2000 are anchored at C8.16 parse-time raw BIRTHID crosstabs (verified raw == harmonized); Table 1 set_complete×outcome structure is cross-checked against NBER `d_Cntltab1.pdf` (SHA `2778c656…`). **Do not cross-compare 1995-1997 vs 1995-2000 cells** — the two files are distinct methodology generations (see above). Table 2a twin-set validation (gender × maternal age × perinatal outcome for complete twin sets) is committed for 1995-1997 and 1995-2000 (68 cells; NBER `e_Cnttab2a.pdf` structure; values anchored at harmonized set-level crosstab). Do not numerically compare these windows to the NBER 1995-98 pooled table.
