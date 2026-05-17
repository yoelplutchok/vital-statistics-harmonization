"""
Fixed-field positions for NCHS U.S. public-use natality (subset of variables).

Layouts used in this repo:
- **81-byte** record: 1968 (`PUBLIC_US_1968_FIELDS`; 50% sample, 1968-revision certificate, standalone year)
- **215-byte** record: 1969–1971 (`PUBLIC_US_1969_1971_FIELDS`; 50% sample, 1968-revision certificate, joint user-guide)
- **215-byte** record: 1972–1973 (`PUBLIC_US_1972_1977_FIELDS`; mixed sample fraction per-state, 1968-revision certificate, joint 1972-1977 user-guide)
- **213-byte** record: 1974–1977 (same field list, same joint 1972-1977 user-guide; trailing 2 RESERVED bytes at pos 214-215 dropped from on-disk records)
- **213-byte** record: 1978–1979 (same `PUBLIC_US_1972_1977_FIELDS`; 100% sample, 1968-revision certificate continued; truncated like 1974-1977; per-year user-guide PDFs `Nat<YYYY>doc.pdf`)
- **215-byte** record: 1980–1988 (same `PUBLIC_US_1972_1977_FIELDS` for the MVP-density positions 1-212; 100% sample, 1968-revision certificate continued; pos 213-215 populated on-disk but not exposed in MVP. 1981 on-disk records are variable-length 213/214 bytes — trailing-whitespace-stripping inconsistency, NOT a field-position shift; positions 1-212 byte-exact common with 1972-1977.)
- **350-byte** record: 1989–2002 (`PUBLIC_US_1990_2002_FIELDS`; 1989-revision certificate. 1989 empirically inherits this V2 layout byte-exact at 5,000-record value-distribution probe per L13-extension; rollout to public-use begins with the 1989 data year.)
- **1350-byte** record: 2003 (`PUBLIC_US_2003_FIELDS`)
- **1500-byte** record: 2004–2005 (`PUBLIC_US_2004_FIELDS` / `PUBLIC_US_2005_2010_FIELDS`)
- **775-byte** record: 2006–2013 (same field list as 2005 subset, with added 2013-only fields)
- **1345-byte** record: 2014–2024 (`PUBLIC_US_2014_2015_FIELDS`; positions match 2014–2015
  User Guides. For 2016+ the URF_DIAB/CHYPER/PHYPER tail block at 1331–1333 is filler;
  the harmonizer's RF_PDIAB/RF_GDIAB/RF_PHYPE/RF_GHYPE fallback covers these years.)

Sources:
  1990–2004 positions: NBER Stata dictionaries (natl{year}.dct) + CDC documentation
    (Nat{year}doc.pdf).
  1968 + 1969–1971 positions (C8.17 DO step 2): CDC documentation
    (`~/Desktop/natality-harmonization/raw_docs/Nat1968doc.pdf` 9 pp;
     `Nat1969-71doc.pdf` 26 pp) cross-verified empirically against actual
    `NATL1968.PUB` / `NATL1969.PUB` / `NATL70.PUB` / `Natl1971.pub` extracts
    (per LESSONS L13-extension 2026-05-12T01:40:00Z — value-distribution
    verification on anchor fields DATAYEAR, CSEX, DMAGE, DBIRWT, DPLURAL,
    MRACE, BIRATTND at 5,000-record sample per file; all PASS).
  1972–1977 positions (C8.17 DO step 3): CDC documentation
    (`Nat1972-77doc.pdf` 29 pp; "DVS-PB 1972-1977 NATALITY PROCESSING — Outline of
    Items and Codes Arranged by Location in the Final Detail BIRTH Record") cross-verified
    empirically against `Natl1972.pub` (1,749,402 records) / `Natl1973.pub` (1,839,736) /
    `Natl74.pb` (2,029,150) / `Natl75.pb` (2,232,406) / `Natl76.pb` (2,463,852) /
    `Natl77.pb` (2,772,206) at a 5,000-record value-distribution probe (L13-extension)
    on 17 anchor fields. Year-specific PDF claims confirmed byte-exact: PLACE OF DELIVERY
    (pos 80) BLANK 1972-1974 / populated 1975+ ("Effective 1975"); MOTHER'S PLACE OF
    BIRTH (pos 138-139) '99' for 1972 / populated 1973+ ("1973-1977 ONLY"); PERSON IN
    ATTENDANCE (pos 176) BLANK 1972-1974 / populated 1975+ ("Effective 1975").
  1978–1988 layout reuse (C8.17 DO step 4): CDC documentation (12 individual user-guide
    PDFs `Nat1978doc.pdf` through `Nat1988doc.pdf`; PDF page-2 / page-6-8 declarations
    "Record length: 215" for 1980/1982/1985/1988 / "Record length: 215" tape-format for
    1978 with on-disk 213-byte ASCII truncation) cross-verified empirically against
    `Natl78.pb` (2,865,686 records @ 213b), `Natl1979` (3,184,421 @ 213b), `NATL80.PUB`
    (3,310,301 @ 215b), `NATL1981.txt` (3,319,054 = 2,802,433 @ 213b + 516,621 @ 214b
    MIXED — trailing-whitespace-stripping inconsistency, NOT a field-position shift),
    `Natl1982` (3,376,813 @ 215b), `NATL1983.txt` (3,337,883 @ 215b), `NATL1984.txt`
    (3,360,871 @ 215b), `Natl1985` (3,765,064 @ 215b), `NATL1986` (3,760,695 @ 215b),
    `NATL1987.txt` (3,813,216 @ 215b), `NATL1988.txt` (3,913,793 @ 215b). All 16 anchor
    fields (DATAYEAR, RECTYPE, RESTATUS, CSEX, BIRATTND, FRACE, MRACE, DMAGE, DBIRWT,
    BIRWT_R3, DPLURAL, DOB_MONTH, MPLACEB, PLDEL, PERSATT, SAMPWT) PASS at 5,000-record
    samples per year × 11 years = 176 PASS — value distributions byte-exact match the
    1972-1977 layout, confirming the 1968-revision certificate continues through 1988
    at the MVP-density positions 1-212. The 1978-revision birth certificate ROLLED OUT
    nationally in 1978-1985 (per NCHS history) but the public-use file POSITIONS did
    NOT change at the anchor-field level — positions 1-212 are byte-stable across the
    entire 1972-1988 envelope. 1981's variable-length on-disk records are handled by the
    parser via right-pad to 215 (or read-position-1-212-only discipline).
  1989 V2-layout inheritance (C8.17 DO step 4): CDC documentation (`Nat1989doc.pdf`
    285 pp; documents the 1989-revision Standard Certificate of Live Birth implementation)
    cross-verified empirically against `NATL1989.PUB` (4,045,693 records @ 350b). All 10
    anchor fields (DATAYEAR pos 1-4 = '1989', RECTYPE pos 5, RESTATUS pos 6, PLDEL pos 8,
    BIRATTND pos 10, DMAGE pos 70-71, MRACE pos 80-81, CSEX pos 189, DBIRWT pos 193-196,
    DPLURAL pos 201) match `PUBLIC_US_1990_2002_FIELDS` byte-exact. 1989 collapses into
    the V2 era for layout purposes; the user-guide PDFs differ (per-year for 1989, NBER
    Stata dictionaries for 1990+) but the field positions are uniform.

Positions are 1-based inclusive (NCHS convention).

File terminators: 1968 + 1969–1971 + 1972–1977 + 1978–1988 + 1989 raw `.PUB` / `.pub` /
`.pb` / `.txt` files use \\r\\n line terminators (stripped on read). The byte positions
below are the **data-only** positions (81 bytes for 1968; 215 bytes for 1969–1971 +
1972–1973; 213 bytes for 1974–1979; 215 bytes for 1980 + 1982–1988 + variable 213/214 for
1981; 350 bytes for 1989); the on-disk record-block size is the data length + 2 terminator
bytes.
"""

RECORD_LEN_1968 = 81         # 1968 50%-sample, 1968-revision cert, standalone year
RECORD_LEN_1969_1971 = 215   # 1969–1971 50%-sample, 1968-revision cert, joint user-guide
RECORD_LEN_1972_1973 = 215   # 1972–1973 mixed-sample-by-state, 1968-revision cert, joint 1972-1977 doc
RECORD_LEN_1974_1977 = 213   # 1974–1977 same layout as 1972-1973 truncated 2 trailing RESERVED bytes
RECORD_LEN_1978_1979 = 213   # 1978–1979 100%-sample, 1968-rev cert continued; truncated like 1974-1977
RECORD_LEN_1980_1988 = 215   # 1980-1988 100%-sample, 1968-rev cert continued; pos 213-215 populated on-disk.
                              # 1981 anomaly: on-disk variable 213/214 bytes (2.80M @ 213b + 0.52M @ 214b
                              # trailing-whitespace-stripping inconsistency, not a field-position shift);
                              # MVP positions 1-212 byte-exact identical to PUBLIC_US_1972_1977_FIELDS.
RECORD_LEN_1990 = 350        # 1989–2002 1989-revision certificate; 1989 empirically inherits this layout byte-exact
                              # (C8.17 DO step 4 L13-extension probe; see module docstring "1989 V2-layout inheritance")
RECORD_LEN_2003 = 1350       # 2003 (first year of dual certificate transition)
RECORD_LEN_2004 = 1500       # 2004 (same as 2005)
RECORD_LEN_2005 = 1500
RECORD_LEN_2010 = 775
RECORD_LEN_2014_2015 = 1345  # 2014–2020 (and likely later revised-era years)

# --- 1968: 1968-revision Standard Certificate of Live Birth (50% sample, standalone) ---
# Record length 81 bytes (data) + \\r\\n terminator on disk.
#
# Authored at C8.17 DO step 2 (2026-05-14) from `Nat1968doc.pdf` (9 pp; "NATALITY TAPE
# FILE FOR CALENDAR YEAR 1968 — Outline of Items and Codes Arranged by Location in the
# Final Birth Tape Record"). Field semantics cross-verified empirically against
# `/tmp/c8_17_step2/NATL1968.PUB` (1,750,782 records; ~50% US sample) at a
# 5,000-record value-distribution probe per LESSONS L13-extension. All seven anchor
# fields (DATAYEAR, CSEX, DMAGE, DBIRWT, DPLURAL, MRACE, BIRATTND) match documented
# code ranges within population-plausible bounds.
#
# Field-name convention: this era predates NBER `natl{year}.dct` (NBER series begins
# 1969 with `natl69.dct` though that file is not currently on disk in this monorepo).
# Names below follow the 1968 user-guide field labels mapped to a sibling-NCHS
# convention (e.g., DATAYEAR / RECTYPE / RESTATUS / MAGER / DBIRWT / DPLURAL match
# 1990+ field-name convention where the underlying concept is identical).
#
# RESTATUS: empirical position is **byte 12**, not byte 4 as a first-pass PDF reading
# might suggest — position 4 is a uniformly-zero placeholder of undocumented purpose
# in this era; position 12 carries the documented Resident Status codes (1=Resident,
# 2=Intrastate nonresident, 3=Interstate nonresident).
#
# Positions 34–37 (4 bytes; uniformly '9911' across the empirical sample) and
# 45–46 (2 bytes; uniformly '11' across the empirical sample) appear in the
# record but the user-guide OCR does NOT clearly document them; both are treated
# as UNDOCUMENTED in this layout and are not exposed as fields. Positions 51–57
# (7 bytes; mostly zero with some single-digit codes near pos 53–57) include
# Children-Born-Alive-Now-Living/Now-Dead detail not enumerated by the user-guide;
# the harmonizer reads only CBA_TOTAL (pos 47–48) + CBA_REC1 (pos 49) + CBA_REC2
# (pos 50). Positions 79–81 (3 bytes; non-blank in raw data) are documented in the
# user-guide as BLANK but empirically carry race-recode-like codes; left undecoded.
PUBLIC_US_1968_FIELDS: list[tuple[str, int, int]] = [
    ("DATAYEAR", 1, 1),       # Year code: "8" → 1968 (single-digit encoding)
    ("RECTYPE", 2, 3),        # Record Type (01=Resident, 02=Nonresident, ...)
    # pos 4: undocumented placeholder; uniformly '0' in empirical sample
    # pos 5–10: blank (6 spaces in empirical sample)
    ("RECTYPE_REC", 11, 11),  # Record Type recode (1=Resident, 2=Nonresident)
    ("RESTATUS", 12, 12),     # Resident Status (1/2/3; see header note above)
    ("STATERES", 13, 14),     # Place of Residence — State (01-51)
    ("CNTYRES", 15, 17),      # Place of Residence — County
    ("CITYRES", 18, 20),      # Place of Residence — City (999=balance of county)
    ("POPSIZE", 21, 21),      # Population Size of place of residence (0-6, 9)
    ("SMSA_RES", 22, 24),     # Standard Metropolitan Statistical Area (residence)
    ("METRORES", 25, 25),     # Metropolitan-Nonmetropolitan County Code (1=Metro, 2=Nonmetro)
    ("FRACE", 26, 26),        # Race of Father (1=White, 2=Negro, 3=Indian, 4=Chinese, 5=Japanese, 6=Hawaiian, 7=Other Nonwhite, 9=Unknown)
    ("MRACE", 27, 27),        # Race of Mother (same codes as FRACE)
    ("CRACE", 28, 28),        # Race of Child (computed from parents)
    ("RACER1", 29, 29),       # Race Recode #1 (1=White, 2=Nonwhite)
    ("RACER2", 30, 30),       # Race Recode #2 (1=White, 2=Negro, 3=Other Nonwhite)
    ("CSEX", 31, 31),         # Sex of child (1=Male, 2=Female)
    ("DMONTH", 32, 33),       # Month of Birth (01-12)
    # pos 34–37: 4-byte block, undocumented in user-guide OCR; empirically uniform '9911'
    ("DMAGE", 38, 39),        # Mother's age detail (12-49, single years)
    ("MAGER_R36", 40, 41),    # Mother's Age Recode #1 / AM36 (14=Under 15; 15-49 single years)
    ("MAGER_R8", 42, 42),     # Mother's Age Recode #2 / AM8 (1=<15, 2=15-19, ..., 8=45-49)
    ("MAGER_R12", 43, 44),    # Mother's Age Recode #3 / AM12 (01-12)
    # pos 45–46: 2-byte block, undocumented in user-guide OCR; empirically uniform '11'
    ("CBA_TOTAL", 47, 48),    # Children Born Alive, Number of (01-54, 99=NS)
    ("CBA_REC1", 49, 49),     # Children Born Alive Recode #1 (1=First, ..., 8=Eighth+, 9=NS)
    ("CBA_REC2", 50, 50),     # Children Born Alive Recode #2 (1=First, 2=Second, 3=Other/NS)
    # pos 51–57: 7-byte block, partially documented (Children Now Living / Now Dead detail);
    # not exposed as fields in this minimum-viable layout (DO step 5 can extend if needed).
    ("BIRATTND", 58, 58),     # Attendant at Birth (1=Hosp/Inst, 2=Phys not hosp, 3=Midwife, 4=Other)
    ("DGESTAT", 59, 60),      # Gestation Period (17-52 weeks, 66=Premature, 88=Not on cert, 99=NS)
    ("GESTREC", 61, 61),      # Gestation Period Recode (0-9; 9=NS+premature+not on cert)
    ("DBIRWT", 62, 65),       # Weight at Birth in grams (0227-8165, 9999=NS)
    ("BIRWT_R12", 66, 67),    # Birthweight Recode #1 (01-11 g-categories, 12=NS)
    ("BIRWT_R3", 68, 68),     # Birthweight Recode #2 (1=≤2500g, 2=≥2501g, 3=NS)
    ("LEGITIM", 69, 69),      # Legitimacy (1=Legitimate, 2=Illegitimate, 8=Not on cert, 9=NS)
    ("DPLURAL", 70, 70),      # Plurality (1=Single, 2=Twin, 3=Triplet, 4=Quad, 5=Quint)
    ("DPLURAL_R", 71, 71),    # Plurality Recode (1=Single, 2=Plural)
    # pos 72–73: blank
    ("STATEOCC", 74, 75),     # Place of Occurrence — State (NCHS state codes)
    ("CNTYOCC", 76, 78),      # Place of Occurrence — County
    # pos 79–81: per user-guide BLANK; empirically non-blank with race-recode-like codes;
    # left undecoded in this layout pending DO step 5 follow-up.
]

# --- 1969–1971: 1968-revision certificate, 50% sample, joint user-guide ---
# Record length 215 bytes (data) + \\r\\n terminator on disk.
#
# Authored at C8.17 DO step 2 (2026-05-14) from `Nat1969-71doc.pdf` (26 pp).
# Cross-verified empirically against `NATL1969.PUB` (1,800,103 records),
# `NATL70.PUB` (1,868,900 records), `Natl1971.pub` (1,781,774 records).
#
# Year encoding in DATAYEAR @ pos 1 (single digit):
#   "9" → 1969 ; "0" → 1970 ; "1" → 1971
# (Harmonize.py must expand: ord(raw[0])-ord('0') + 1960 for the 1968-revision era's
# 50%-sample years, with a year-of-file disambiguator since "0" / "1" are also used
# by sibling decade-suffix encodings later. Recommended: pair with on-disk file
# year to disambiguate.)
#
# Year-specific differences per user-guide page 2:
#   - Position 12 RESIDENT STATUS: 1969 does NOT identify Foreign Residents
#     (only codes 1/2/3); 1970-71 adds code 4 (Foreign Resident).
#   - Positions 13-27 / 28-32 (Residence + Occurrence Geographic codes): 1969
#     uses 1960 Census; 1970-71 uses 1970 Census.
#   - Position 81 DPLURAL: PRESENT for 1971 data; BLANK for 1969-70 data
#     (empirically confirmed: 1969 + 1970 samples have pos 81 = uniform space;
#     1971 sample has pos 81 ∈ {1, 2, 3, 4, 5} per documented Plurality codes).
#   - Position 115-116 (Year of Last Birth) + 127-128 (Year of Last Fetal Death):
#     coding varies by data year (1969: codes 8 & 9 acceptable; 1970: 9 & 0;
#     1971: 0 & 1). Harmonize.py must consume the file's data-year as context.
#   - Position 138-139 Mother's Place of Birth: 1970-71 only; NOT coded for 1969.
#   - Position 142 Congenital Malformations: 1969 codes 0/1/8; 1970-71 codes
#     0/1/2/8 (adds code 2 for "YES check box entry").
PUBLIC_US_1969_1971_FIELDS: list[tuple[str, int, int]] = [
    ("DATAYEAR", 1, 1),       # Single-digit data year (9=1969, 0=1970, 1=1971)
    ("SHIPNUM", 2, 3),        # Shipment Number (assigned within reporting area)
    ("REPAREA", 4, 4),        # Reporting Area code (NYC boroughs, Chicago, etc.; see PDF page 3)
    # pos 5–10: CERTIFICATE NUMBER, blank in PUF
    ("RECTYPE", 11, 11),      # Record Type (1=Resident, 2=Nonresident)
    ("RESTATUS", 12, 12),     # Resident Status (1/2/3 for 1969; 1/2/3/4 for 1970-71; 4=Foreign Resident)
    ("STATERES", 13, 14),     # Place of Residence — State (01-51 US + 52-59 foreign)
    ("CNTYRES", 15, 17),      # Place of Residence — County (ZZZ for foreign 1970-71)
    ("CITYRES", 18, 20),      # Place of Residence — City (999=balance, ZZZ=foreign 1970-71)
    ("POPSIZE", 21, 21),      # Population Size of place of residence (0-6, 9, Z=foreign)
    ("SMSA_RES", 22, 24),     # SMSA (residence) — 1969: 1960-Census 001-201; 1970-71: 1970-Census 001-229
    ("METRORES", 25, 25),     # Metro/Nonmetro County Code (1=Metro, 2=Nonmetro, Z=foreign)
    ("DIVRES", 26, 27),       # Division + Subcode (residence) — Division 1-9, Subcode within
    ("STATEOCC", 28, 29),     # Place of Occurrence — State (01-51)
    ("CNTYOCC", 30, 32),      # Place of Occurrence — County
    ("DIVOCC", 33, 34),       # Division + Subcode (occurrence)
    ("CSEX", 35, 35),         # Sex of child (1=Male, 2=Female)
    ("BIRATTND", 36, 36),     # Attendant at Birth (1=Phys Hosp, 2=Phys not hosp, 3=Midwife not hosp, 4=Other/NS)
    ("FRACE", 37, 37),        # Detail Race of Father (0=Guamian, 1=White, 2=Negro, 3=Indian, 4=Chinese, 5=Japanese, 6=Hawaiian, 7=Other Nonwhite, 8=Filipino, 9=NS)
    ("MRACE", 38, 38),        # Detail Race of Mother (same codes as FRACE)
    ("CRACE", 39, 39),        # Detail Race of Child (same codes, no "9" since computed)
    ("CRACE_R3", 40, 40),     # Race of Child Recode 3 (1=White, 2=Other excl Negro, 3=Negro)
    ("DMAGE", 41, 42),        # Detail Age of Mother (10-49 single years; 99=NS)
    ("MAGER_R36", 43, 44),    # Age of Mother Single Years Recode 36 (01=<15, 02-36 = 15-49)
    ("MAGER_R15", 45, 46),    # Age of Mother Recode 15 (01-17 categorical)
    ("MAGER_R12", 47, 48),    # Age of Mother Recode 12 (01-13 categorical)
    ("MAGER_R8", 49, 49),     # Age of Mother Recode 8 (1-8 categorical)
    ("MAGER_R7", 50, 50),     # Age of Mother Recode 7 (1-7 categorical)
    ("MAGER_R6", 51, 51),     # Age of Mother Recode 6 (1-6 categorical)
    ("CBA_NL", 52, 53),       # Children Born Alive, Now Living (00-54, 55/66/77/99 sentinels)
    ("CBA_ND", 54, 55),       # Children Born Alive, Now Dead (same codes as CBA_NL)
    ("CBA_FD", 56, 57),       # Children Born Dead = Fetal Deaths (same codes)
    ("TBORD", 58, 59),        # Total Birth Order Detail (01-54, 99=NS)
    ("TBORD_R9", 60, 60),     # Total Birth Order Recode 9 (1-9)
    ("DLIVBORD", 61, 62),     # Detail Live Birth Order (01-54, 99=NS)
    ("LBORD_R9", 63, 63),     # Live Birth Order Recode 9
    ("LBORD_R8", 64, 64),     # Live Birth Order Recode 8
    ("LBORD_R7", 65, 65),     # Live Birth Order Recode 7
    ("LBORD_R6", 66, 66),     # Live Birth Order Recode 6
    ("LBORD_R3", 67, 67),     # Live Birth Order Recode 3
    ("COMBOFLG", 68, 68),     # "77 & 77 COMBINATION FLAG" — both BA/NL and BA/ND = blank
    ("DFAGE", 69, 70),        # Detail Age of Father (10-98 single yrs for 1971; 17-98 for 1969-70; 99=NS)
    ("FAGER_R11", 71, 72),    # Age of Father Recode 11 (01-11 categorical; varies between 1969-70 / 1971)
    ("DBIRWT", 73, 76),       # Birthweight Detail in grams (0227-8165, 9999=NS)
    ("BIRWT_R12", 77, 78),    # Birthweight Recode 12 (01-11 g-categories, 12=NS)
    ("BIRWT_R3", 79, 79),     # Birthweight Recode 3 (1=≤2500, 2=≥2501, 3=NS)
    # pos 80: BLANK per user-guide
    ("DPLURAL", 81, 81),      # Plurality Detail (1971 only: 1-5; BLANK for 1969-70 — see header note)
    ("DPLURAL_R3", 82, 82),   # Plurality Recode 3 (1971 only: 1=Single, 2=Twin, 3=Other Multiple)
    ("DPLURAL_R2", 83, 83),   # Plurality Recode 2 (1971 only: 1=Single, 2=Multiple)
    ("DOB_MONTH", 84, 85),    # Birth Date — Month (01-12)
    ("DOB_DAY", 86, 87),      # Birth Date — Day (01-31, 99=NS)
    ("LMP_MONTH", 88, 89),    # Date of LMP — Month (88=non-reporting state, 01-12, 99=NS)
    ("LMP_DAY", 90, 91),      # Date of LMP — Day (88=non-reporting, 01-31, 99=NS)
    ("LMP_YEAR", 92, 92),     # Date of LMP — Year (single digit; year-specific codes per header note)
    ("DGESTAT", 93, 94),      # Detail Gestation in Weeks (00=non-reporting, 17-52, 99=NS)
    ("GESTREC10", 95, 96),    # Gestation Recode 10 (00=non-reporting, 01-09 categories, 10=NS)
    ("GESTREC3", 97, 97),     # Gestation Recode 3 (0=non-reporting, 1=<37wk, 2=37+wk, 3=NS)
    ("DMEDUC", 98, 99),       # Mother's Education Detail (88=non-reporting, 00-17 yrs, 66/77/99 sentinels)
    ("MEDUC_R14", 100, 101),  # Mother's Education Recode 14 (00=non-reporting, 01-13 categories, 14=NS)
    ("MEDUC_R6", 102, 102),   # Mother's Education Recode 6 (0=non-reporting, 1-5 categories, 6=NS)
    ("DFEDUC", 103, 104),     # Father's Education Detail (same code structure as DMEDUC)
    ("FEDUC_R14", 105, 106),  # Father's Education Recode 14
    ("LEGITIM", 107, 107),    # Detail Legitimacy (8=non-reporting, 1=Legit, 2=Illegit, 9=NS)
    ("LEGITIM_R3", 108, 108), # Legitimacy Recode 3 (0=non-reporting, 1=Legit incl NS, 2=Illegit)
    ("MONPRE", 109, 109),     # Month Prenatal Care Began Detail (Y=non-reporting, 2-9 month, 0=No care, X=NS)
    ("MONPRE_R10", 110, 111), # Month Prenatal Care Began Recode 10 (00=non-reporting, 01-09 month, 10=NS)
    # pos 112-126: Birth interval fields (last live birth date + interval recodes); not exposed in MVP
    # pos 127-128: Year of Last Fetal Death + reporting flag; not exposed in MVP
    # pos 129-136: Interval since last fetal death + termination interval; not exposed in MVP
    # pos 137: Outcome of Last Pregnancy
    ("OUTPREG_LAST", 137, 137), # Outcome of Last Pregnancy (0=non-reporting/no prev preg, 1=Live, 2=FD, 3=Unknown)
    ("MPLACEB", 138, 139),    # Mother's Place of Birth (1970-71 only; BLANK for 1969)
    # pos 140-141: Blank
    ("CONGMAL", 142, 142),    # Congenital Malformations (0/1/2/8; 2 only for 1970-71)
    # pos 143-145: Reserved for Indian Health Service community-residence codes (1972+ data only)
    ("LEGITIM_STATE", 146, 146),     # Legitimacy by State (per-state coding override)
    ("EDU_PARENT_STATE", 147, 147),  # Education of Parents by State
    ("DATE_LNM_STATE", 148, 148),    # Date of Last Normal Menses by State
    # pos 149+: Month Prenatal Care Began by State + additional state-specific items;
    # not exposed in this MVP layout — DO step 5 may extend if harmonization requires.
]

# --- 1972-1977: 1968-revision certificate, mixed-sample-fraction (per-state), joint user-guide ---
# Record length 215 bytes data (+ \\r\\n) on disk for 1972-1973; 213 bytes data (+ \\r\\n)
# for 1974-1977 (the trailing 2 RESERVED bytes at positions 214-215 are dropped).
#
# Authored at C8.17 DO step 3 (2026-05-14) from `Nat1972-77doc.pdf` (29 pp; "DVS-PB 1972-1977
# NATALITY PROCESSING — Outline of Items and Codes Arranged by Location in the Final Detail
# BIRTH Record"). Empirically cross-verified (L13-extension) at 5,000-record per-year samples
# against PDF-documented anchor positions DATAYEAR / CSEX / BIRATTND / FRACE / MRACE / DMAGE /
# DBIRWT / BIRWT_R3 / PLDEL / DPLURAL / DOB_MONTH / DMEDUC / MPLACEB / PERSATT / SAMPWT
# (17 fields × 6 years = 102 PASS).
#
# Year encoding in DATAYEAR @ pos 1 (single digit):
#   "2" → 1972 ; "3" → 1973 ; "4" → 1974 ; "5" → 1975 ; "6" → 1976 ; "7" → 1977
# (Harmonize.py: ord(raw[0])-ord('0') + 1970 for the joint 1972-1977 era; pair with on-disk
# file year to disambiguate from sibling 1968-1971 + 1978-1988 single-digit-encoding eras.)
#
# Mixed sample fraction: per PDF page 2 §1.2, "Beginning with the 1972 data year, 100 percent
# of the births occurring in certain States were processed. Births occurring in all other
# States were coded on a 50 percent basis. A record weight factor of 1 (for 100% States) or 2
# (for 50% States) appears in tape location 208." Harmonize.py at DO step 5 must consume the
# per-record SAMPWT @ pos 208 to produce correctly weighted control counts; the per-state
# per-year 100%-vs-50% mapping lives in PDF Appendix A (page 29).
#
# Year-specific differences (all empirically confirmed at C8.17 DO step 3):
#   - PLACE OF DELIVERY (pos 80): "Effective 1975" per PDF page 14. BLANK 1972-1974
#     (5,000-rec sample uniformly space ' ' across each year); populated 1975+ with codes
#     1=Hospital/Institution, 2=Clinic/Center/Home, 3=Named places (Dr's offices), 4=Street
#     address, 9=Not classifiable. (Empirically: 1975 = 84% code 1; 1976 = 86% code 1;
#     1977 = 76% code 1 + 21% code 2 — suggests progressive home-birth reporting expansion.)
#   - MOTHER'S PLACE OF BIRTH (pos 138-139): "1973-1977 ONLY" per PDF page 24. For 1972 data,
#     the field is uniformly '99' = "Not Classifiable" (functional-BLANK); for 1973-1977 the
#     field is populated with 01-51 (US states + DC), 52-59 (foreign), 99=Not Classifiable.
#   - PERSON IN ATTENDANCE (pos 176): "Effective 1975" per PDF page 26. BLANK 1972-1974;
#     populated 1975+ with codes 1=Physician, 2=Midwife, 3=Status specified-other,
#     9=Status unknown / not specified / not classified. Supplements BIRATTND (pos 36;
#     populated all years 1972-1977) with a distinct codification.
#   - DETAIL MONTH OF PRENATAL CARE BEGAN (pos 109): 1972 uses codes Y/2-9/0/X where "2 =
#     1st & 2nd Months combined"; 1973-1977 uses Y/1-9/0/X where "1 = 1st Month" discrete
#     (per PDF page 19; this is a 1973+ refinement of the 1972 coding).
#   - DATE OF LMP - YEAR (pos 92): per PDF page 15, single-digit code with year-specific
#     mapping (1972 data uses 1=1971/2=1972; 1973 data uses 2=1972/3=1973; etc.; "X" = NS;
#     "8" = non-reporting state). Harmonize.py must consume file-year context.
#   - DATE OF LAST LIVE BIRTH - YEAR (pos 115-116): same year-specific 2-digit coding pattern;
#     "OO-72/73/74" stated year per file year; "77" = No Previous Live Birth (per PDF page 20).
#   - DATE OF LAST FETAL DEATH - YEAR (pos 127-128): same year-specific pattern as DOLLB_YEAR.
#   - BIRTH INJURIES reporting flag (pos 156, 169): "Not applicable for 1972" per PDF
#     page 25-26; populated 1973-1977 as 0/1 reporting flags.
#
# Trailing RESERVED bytes (pos 213-215, 1972-1973 ONLY): per PDF page 28 "213-215 RESERVED
# POSITIONS". Empirically uniform 3-byte spaces for 1972-1973; absent from 1974-1977 files
# (which truncate the on-disk record at byte 213). NOT exposed as fields.
PUBLIC_US_1972_1977_FIELDS: list[tuple[str, int, int]] = [
    ("DATAYEAR", 1, 1),         # Single-digit data year (2=1972, 3=1973, 4=1974, 5=1975, 6=1976, 7=1977)
    ("SHIPNUM", 2, 3),          # Shipment Number (internal processing)
    ("REPAREA", 4, 4),          # Reporting Area code (NYC boroughs, Chicago, other; PDF page 3)
    # pos 5-10: CERTIFICATE NUMBER, blank in PUF
    ("RECTYPE", 11, 11),        # Record Type (1=Resident, 2=Nonresident)
    ("RESTATUS", 12, 12),       # Resident Status (1=Resident, 2=Intrastate nonres, 3=Interstate nonres, 4=Foreign Resident)
    ("STATERES", 13, 14),       # Place of Residence — State (01-51 US + DC; 52-59 foreign)
    ("CNTYRES", 15, 17),        # Place of Residence — County (foreign coded ZZZ)
    ("CITYRES", 18, 20),        # Place of Residence — City (999=balance, foreign ZZZ)
    ("POPSIZE", 21, 21),        # Population Size of place of residence (0-6, 9, Z=foreign)
    ("SMSA_RES", 22, 24),       # SMSA (residence) — 1970-Census 001-229; 000=non-metro; ZZZ=foreign
    ("METRORES", 25, 25),       # Metro/Nonmetro County Code (1=Metro, 2=Nonmetro, Z=foreign)
    ("DIVRES", 26, 27),         # Division + Subcode (residence) — Division 1-9, Subcode within
    ("STATEOCC", 28, 29),       # Place of Occurrence — State (01-51)
    ("CNTYOCC", 30, 32),        # Place of Occurrence — County
    ("DIVOCC", 33, 34),         # Division + Subcode (occurrence)
    ("CSEX", 35, 35),           # Sex of child (1=Male, 2=Female)
    ("BIRATTND", 36, 36),       # Attendant at Birth (1=Phys Hosp, 2=Phys not hosp, 3=Midwife, 4=Other/NS)
    ("FRACE", 37, 37),          # Detail Race of Father (0=Guamian, 1=White, 2=Negro, 3=Indian, 4=Chinese, 5=Japanese, 6=Hawaiian, 7=Other, 8=Filipino, 9=NS)
    ("MRACE", 38, 38),          # Detail Race of Mother (same codes as FRACE)
    ("CRACE", 39, 39),          # Detail Race of Child (no 9 since computed from parents)
    ("CRACE_R3", 40, 40),       # Race of Child Recode 3 (1=White, 2=All Other excl Negro, 3=Negro)
    ("DMAGE", 41, 42),          # Detail Age of Mother (10-49 single years; 99=NS)
    ("MAGER_R36", 43, 44),      # Age of Mother Single Years Recode 36 (01=<15, 02-36 = 15-49)
    ("MAGER_R15", 45, 46),      # Age of Mother Recode 15 (01-17 categorical)
    ("MAGER_R12", 47, 48),      # Age of Mother Recode 12 (01-13 categorical)
    ("MAGER_R8", 49, 49),       # Age of Mother Recode 8 (1-8 categorical)
    ("MAGER_R7", 50, 50),       # Age of Mother Recode 7 (1-7 categorical)
    ("MAGER_R6", 51, 51),       # Age of Mother Recode 6 (1-6 categorical)
    ("CBA_NL", 52, 53),         # Children Born Alive, Now Living (00-54, 55/66/77/99 sentinels)
    ("CBA_ND", 54, 55),         # Children Born Alive, Now Dead (same codes as CBA_NL)
    ("CBA_FD", 56, 57),         # Children Born Dead = Fetal Deaths (same codes)
    ("TBORD", 58, 59),          # Total Birth Order Detail (01-54, 99=NS)
    ("TBORD_R9", 60, 60),       # Total Birth Order Recode 9 (1-9)
    ("DLIVBORD", 61, 62),       # Detail Live Birth Order (01-54, 99=NS)
    ("LBORD_R9", 63, 63),       # Live Birth Order Recode 9
    ("LBORD_R8", 64, 64),       # Live Birth Order Recode 8
    ("LBORD_R7", 65, 65),       # Live Birth Order Recode 7
    ("LBORD_R6", 66, 66),       # Live Birth Order Recode 6
    ("LBORD_R3", 67, 67),       # Live Birth Order Recode 3
    # pos 68: undocumented in PDF page 13 OCR; sibling 1969-71 layout names this COMBOFLG
    # ("77 & 77 combination flag"); not exposed as a field in this MVP — DO step 5 may extend.
    ("DFAGE", 69, 70),          # Detail Age of Father (10-98 single years; 99=NS)
    ("FAGER_R11", 71, 72),      # Age of Father Recode 11 (01-11 categorical)
    ("DBIRWT", 73, 76),         # Birthweight Detail in grams (0227-8165, 9999=NS)
    ("BIRWT_R12", 77, 78),      # Birthweight Recode 12 (01-11 g-categories, 12=NS)
    ("BIRWT_R3", 79, 79),       # Birthweight Recode 3 (1=≤2500, 2=≥2501, 3=NS)
    ("PLDEL", 80, 80),          # PLACE OF DELIVERY (Effective 1975; BLANK 1972-1974)
    ("DPLURAL", 81, 81),        # Plurality Detail (1=Single, 2=Twin, 3=Triplet, 4=Quad, 5=Quint)
    ("DPLURAL_R3", 82, 82),     # Plurality Recode 3 (1=Single, 2=Twin, 3=Other Multiple)
    ("DPLURAL_R2", 83, 83),     # Plurality Recode 2 (1=Single, 2=Multiple)
    ("DOB_MONTH", 84, 85),      # Birth Date — Month (01-12)
    ("DOB_DAY", 86, 87),        # Birth Date — Day (01-31, 99=NS)
    ("LMP_MONTH", 88, 89),      # Date of LMP — Month (88=non-reporting state, 01-12, 99=NS)
    ("LMP_DAY", 90, 91),        # Date of LMP — Day (88=non-reporting, 01-31, 99=NS)
    ("LMP_YEAR", 92, 92),       # Date of LMP — Year (single digit; year-specific codes per header note)
    ("DGESTAT", 93, 94),        # Detail Gestation in Weeks (00=non-reporting, 17-52, 99=NS)
    ("GESTREC10", 95, 96),      # Gestation Recode 10 (00=non-reporting, 01-09 categories, 10=NS)
    ("GESTREC3", 97, 97),       # Gestation Recode 3 (0=non-reporting, 1=<37wk, 2=37+wk, 3=NS)
    ("DMEDUC", 98, 99),         # Mother's Education Detail (88=non-reporting, 00-17 yrs, 66/77/99 sentinels)
    ("MEDUC_R14", 100, 101),    # Mother's Education Recode 14 (00=non-reporting, 01-13 cat, 14=NS)
    ("MEDUC_R6", 102, 102),     # Mother's Education Recode 6 (0=non-reporting, 1-5 cat, 6=NS)
    ("DFEDUC", 103, 104),       # Father's Education Detail (same code structure as DMEDUC)
    ("FEDUC_R14", 105, 106),    # Father's Education Recode 14
    ("LEGITIM", 107, 107),      # Detail Legitimacy (8=non-reporting, 1=Legit, 2=Illegit, 9=NS)
    ("LEGITIM_R3", 108, 108),   # Legitimacy Recode 3 (0=non-reporting, 1=Legit incl NS, 2=Illegit)
    ("MONPRE", 109, 109),       # Month Prenatal Care Began Detail (Y=non-rpt; 1972: 2-9 + 0/X; 1973+: 1-9 + 0/X)
    ("MONPRE_R10", 110, 111),   # Month Prenatal Care Began Recode 10 (00=non-rpt, 01-09 month, 10=NS)
    ("MONPRE_R6", 112, 112),    # Month Prenatal Care Began Recode 6 (0=non-rpt, 1-5 cat, 6=NS)
    ("DOLLB_MONTH", 113, 114),  # Date of Last Live Birth — Month (88=non-rpt, 01-12, 99=NS, 77=No prev LB)
    ("DOLLB_YEAR", 115, 116),   # Date of Last Live Birth — Year (88=non-rpt, year-specific 2-digit code)
    ("INTLLB", 117, 119),       # Detail Months Interval Since Last Live Birth (888=non-rpt, 000-500, 999=NS, 777=No prev LB)
    ("INTLLB_R17", 120, 121),   # Interval Since Last Live Birth Recode 17 (00=non-rpt+No prev LB)
    ("INTLLB_R10", 122, 123),   # Interval Since Last Live Birth Recode 10
    ("INTLLB_R8", 124, 124),    # Interval Since Last Live Birth Recode 8
    ("DOLFD_MONTH", 125, 126),  # Date of Last Fetal Death — Month (88=non-rpt, 01-12, 99=NS, 77=No prev FD)
    ("DOLFD_YEAR", 127, 128),   # Date of Last Fetal Death — Year (88=non-rpt, year-specific code)
    # pos 129: used for internal processing only
    ("INTLFD", 130, 132),       # Detail Interval Since Last Fetal Death (888=non-rpt, 000-500, 999=NS, 777=No prev FD)
    ("INTLTERMP", 133, 135),    # Detail Interval Since Termination of Last Pregnancy
    ("INTLTERMP_R9", 136, 136), # Interval Since Termination of Last Pregnancy Recode 9
    ("OUTPREG_LAST", 137, 137), # Outcome of Last Pregnancy (0=non-rpt/no prev preg, 1=Live, 2=FD, 3=Unknown)
    ("MPLACEB", 138, 139),      # Mother's Place of Birth (1973-1977 ONLY; '99'/uniform for 1972)
    ("TPRENVIS", 140, 141),     # Total Number of Prenatal Visits (88=non-rpt, 00=none, 01-49, 99=NS)
    # pos 142-145: used for internal processing only (3 + 1 bytes)
    ("FLAG_LEGITIM_STATE", 146, 146),    # Reporting flag (residence): Legitimacy by State (0=NOT rpt, 1=IS rpt)
    ("FLAG_EDU_STATE", 147, 147),        # Reporting flag (residence): Education of Parents by State
    ("FLAG_LNM_STATE", 148, 148),        # Reporting flag (residence): Date of Last Normal Menses by State
    ("FLAG_MONPRE_STATE", 149, 149),     # Reporting flag (residence): Month Prenatal Care Began by State
    ("FLAG_DOLLB_STATE", 150, 150),      # Reporting flag (residence): Date of Last Live Birth by State
    ("FLAG_DOLFD_STATE", 151, 151),      # Reporting flag (residence): Date of Last Fetal Death by State
    ("FLAG_LEGITIM_SMSA", 152, 152),     # Reporting flag (residence): Legitimacy by SMSA
    ("FLAG_EDU_SMSA", 153, 153),         # Reporting flag (residence): Education by SMSA
    ("FLAG_CONGMAL_STATE", 154, 154),    # Reporting flag (residence): Congenital Malformations by State
    ("FLAG_PRENVIS_STATE", 155, 155),    # Reporting flag (residence): Number of Prenatal Visits by State
    ("FLAG_BIRINJ_STATE", 156, 156),     # Reporting flag (residence): Birth Injuries by State (1973-1977 only; "Not applicable for 1972")
    # pos 157-160: 4-byte RESERVED for possible later use
    # pos 161-169: occurrence-side reporting flags (sibling-symmetric to 146-156 residence-side);
    # not exposed in this MVP layout — DO step 5 may extend if harmonization requires.
    # pos 170-175: 6-byte RESERVED POSITIONS / USED FOR INTERNAL PROCESSING ONLY
    ("PERSATT", 176, 176),                # Person in Attendance (Effective 1975; BLANK 1972-1974; 1=Phys, 2=Midwife, 3=Other, 9=Unk)
    # pos 177-207: 31-byte RESERVED POSITIONS / USED FOR INTERNAL PROCESSING ONLY
    ("SAMPWT", 208, 208),                 # Record Weight: 1=100% State record; 2=50% State record (per-state per-year; PDF Appendix A)
    ("NPRENVIS_R28", 209, 210),           # Number of Prenatal Visits Recode 28 (00=non-rpt, 01-28 categories)
    ("NPRENVIS_R12", 211, 212),           # Number of Prenatal Visits Recode 12 (00=non-rpt, 01-12 categories)
    # pos 213-215 (1972-1973 ONLY): 3-byte RESERVED POSITIONS, uniform spaces empirically;
    # absent from 1974-1977 on-disk records (which truncate at byte 213). NOT exposed.
]
# REUSE: PUBLIC_US_1972_1977_FIELDS extends byte-exact to 1978-1988 at the MVP-density
# positions 1-212 per C8.17 DO step 4 empirical L13-extension verification (16 anchor
# fields × 11 years × 5,000-record samples = 176 PASS). Parser at C8.17 DO step 5 will
# dispatch year ∈ {1972, 1973, ..., 1988} → PUBLIC_US_1972_1977_FIELDS at the per-year
# RECORD_LEN_<era> constant declared above. Years 1980-1988 have populated content at
# pos 213-215 on-disk but those positions are NOT exposed in this MVP — DO step 5 may
# add them if harmonization requires.

# --- 1989–2002: 1989-revision Standard Certificate of Live Birth (formerly "Unrevised 1989") ---
# Record length 350 bytes.  Variable names follow NBER convention (lowercase in dct;
# we use UPPERCASE to be consistent with later-era raw field names).
#
# 1989 REUSE (C8.17 DO step 4 empirical L13-extension probe): the 1989 public-use file
# (`NATL1989.PUB`; 4,045,693 records @ 350-byte data + \\r\\n terminator) inherits this
# V2 layout byte-exact. Verified at 10 anchor fields × 5,000-record sample: DATAYEAR pos
# 1-4 = '1989' (4-byte year encoding distinct from the 1968-1988 single-digit encoding);
# RECTYPE pos 5, RESTATUS pos 6, PLDEL pos 8, BIRATTND pos 10, DMAGE pos 70-71, MRACE pos
# 80-81, CSEX pos 189, DBIRWT pos 193-196 (gram-encoded), DPLURAL pos 201 all align with
# 1990-2002 V2 semantics. The 1989 data year is the public-use ROLLOUT of the 1989-revision
# birth certificate; layout positions stabilized at this point and remain unchanged through
# 2002. Soft-flag (t) "5-vs-4 pre-1989 era boundaries" is RESOLVED at this DO step toward
# the 3-distinct-pre-1989-layouts + 1989-collapses-into-V2 framing.
#
# NOTE: 1990–1993 files (Nat{year}.zip) contain only US records despite the
# name.  Position 5 (RECTYPE) mirrors RESTATUS: 1 = same-state resident,
# 2+ = cross-state/foreign.  Do NOT filter on RECTYPE.  1994–2002 "us" files
# are also US-only.
#
# Education is coded as years of schooling (00–17, 99=unknown), NOT the 2003-era
# category codes.  Race uses the old NCHS coding (no bridged-race recode).
# Medical risk factors are individual Y/N/unknown flags (1/2/9), not URF_ composites.
# Smoking is average cigarettes/day + Y/N flag, not trimester-specific counts.
PUBLIC_US_1990_2002_FIELDS: list[tuple[str, int, int]] = [
    ("DATAYEAR", 1, 4),       # Data year
    ("RECTYPE", 5, 5),        # Record type (1=US, 2=territory; useful for 1990-1993)
    ("RESTATUS", 6, 6),       # Resident status (same codes as later years)
    ("DMAGE", 70, 71),        # Mother's age (single year)
    ("ORMOTH", 77, 77),       # Hispanic origin of mother (0=non-Hisp, 1-5=Hisp types, 9=unknown)
    ("ORRACEM", 78, 78),      # Hispanic origin and race of mother combined recode
    ("MRACE", 80, 81),        # Race of mother (detail code)
    ("MRACE3", 82, 82),       # Race of mother recode 3 (1=White, 2=Black, 3=Other)
    ("DMEDUC", 83, 84),       # Education of mother (years 00-17, 99=unknown)
    ("MEDUC6", 85, 85),       # Education of mother recode 6
    ("DMAR", 87, 87),         # Marital status (1=married, 2=unmarried)
    ("DLIVORD", 100, 101),    # Detail live birth order
    ("LIVORD9", 102, 102),    # Live birth order recode 9
    ("DTOTORD", 103, 104),    # Detail total birth order
    ("TOTORD9", 105, 105),    # Total birth order recode 9
    ("MONPRE", 106, 107),     # Month prenatal care began (00=none, 01-09, 99=unknown)
    ("NPREVIS", 110, 111),    # Total number of prenatal visits (00-49, 99=unknown)
    ("DGESTAT", 183, 184),    # Gestation detail in weeks (LMP-based)
    ("GESTAT10", 185, 186),   # Gestation recode 10
    ("GESTAT3", 187, 187),    # Gestation recode 3 (1=<37, 2=37+, 3=not stated)
    ("CSEX", 189, 189),       # Sex of child (1=Male, 2=Female)
    ("DBIRWT", 193, 196),     # Birthweight in grams (0099-8165, 9999=unknown)
    ("DPLURAL", 201, 201),    # Plurality (1-5+)
    ("FMAPS", 205, 206),      # Five minute Apgar score (00-10, 99=unknown)
    ("DELMETH5", 224, 224),   # Method of delivery recode 5 (1=vag, 2=vbac, 3=prim cs, 4=rep cs, 5=other/unknown)
    ("DIABETES", 228, 228),   # Diabetes (1=yes, 2=no, 9=unknown)
    ("CHYPER", 232, 232),     # Chronic hypertension (1=yes, 2=no, 9=unknown)
    ("PHYPER", 233, 233),     # Pregnancy-associated hypertension (1=yes, 2=no, 9=unknown)
    ("TOBACCO", 242, 242),    # Tobacco use during pregnancy (1=yes, 2=no, 9=unknown)
    ("CIGAR", 243, 244),      # Average number of cigarettes per day (00-98, 99=unknown)
    ("CIGAR6", 245, 245),     # Cigarettes recode 6 (0=nonsmoker, 1-5=intensity, 6=unknown)
    ("DFAGE", 154, 155),      # Father's combined age (10-98, 99=unknown)
    ("ORFATH", 158, 158),     # Hispanic origin of father (0=non-Hisp, 1-5=Hisp types, 9=unknown)
    ("ORRACEF", 159, 159),    # Hispanic origin and race of father combined recode (1-8, 9=unknown)
    ("DFEDUC", 163, 164),     # Education of father (years 00-17, 99=unknown; DROPPED from 1995+ public-use files → blank)
    ("PLDEL", 8, 8),          # Place of delivery (1=hospital, 2=birth ctr, 3=clinic, 4=residence, 5=other, 9=unknown)
    ("BIRATTND", 10, 10),     # Attendant at birth (1=MD, 2=DO, 3=CNM, 4=other midwife, 5=other, 9=unknown)
]

# --- 2003: Dual certificate transition (first year) ---
# Same field positions as 2005 EXCEPT:
# - MAGER at 89-90 is actually MAGER41 (41-category recode), NOT single-year age.
#   Reported age at 77-78 is suppressed (all 99).  We extract MAGER41 and convert in harmonization.
# - DMETH_REC is at position 401 (not 403 as in 2005).
# Record length: 1350 bytes.
PUBLIC_US_2003_FIELDS: list[tuple[str, int, int]] = [
    ("DOB_YY", 15, 18),
    ("DOB_MM", 19, 20),
    ("MAGER41", 89, 90),      # 41-category age recode (01=<15, 02=15, ..., 41=54)
    ("LBO_REC", 212, 212),
    ("TBO_REC", 217, 217),
    ("RESTATUS", 138, 138),
    ("MRACE", 141, 142),
    # MRACE15 is NOT at bytes 108-109 in the 2003 public-use layout. Raw-byte
    # probing of Nat2003us.zip at those bytes returns 2-letter alphabetic codes
    # (AC/XT/CN/LF/HO/AP/KA/ZA/...) — probably the middle two bytes of a 4-byte
    # state/country-of-birth field around 107-110 — not the NCHS MRACE15 recode
    # (which would be numeric 01-15). Leave the column absent from the spec so
    # maternal_race_detail_15cat is null for 2003, matching the CODEBOOK.
    ("MRACEREC", 143, 143),
    ("UMHISP", 148, 148),
    ("MRACEHISP", 149, 149),
    ("MAR", 153, 153),
    ("MEDUC", 155, 155),
    ("MEDUC_REC", 158, 158),
    ("PRECARE", 245, 246),
    ("MPCB", 256, 257),
    ("UPREVIS", 270, 271),
    ("CIG_1", 284, 285),
    ("CIG_2", 286, 287),
    ("CIG_3", 288, 289),
    ("CIG_REC6", 293, 293),
    ("URF_DIAB", 331, 331),
    ("URF_CHYPER", 335, 335),
    ("URF_PHYPER", 336, 336),
    ("DMETH_REC", 401, 401),   # NOTE: position 401, not 403 as in 2005
    ("APGAR5", 415, 416),
    ("DPLURAL", 423, 423),
    ("SEX", 436, 436),
    ("COMBGEST", 451, 452),
    ("GESTREC3", 455, 455),
    ("DBWT", 463, 466),
    ("UFAGECOMB", 184, 185),  # Father's combined age, unrevised/national (10-98, 99=unknown)
    ("UBFACIL", 42, 42),      # Birth facility, unrevised/national (1=hosp, 2=birth ctr, 3=clinic, 4=residence, 5=other, 9=unk)
    ("ATTEND", 408, 408),     # Attendant at birth (1=MD, 2=DO, 3=CNM, 4=other midwife, 5=other, 9=unknown)
    ("UFHISP", 195, 195),    # Father's Hispanic origin, unrevised/national (0=non-Hisp, 1-5=Hisp, 9=unknown)
    ("FRACEHISP", 196, 196),  # Father's race/Hispanic combined recode (1-8, 9=unknown)
]

# --- 2004: Dual certificate transition ---
# Record length is 1500 bytes (same as 2005), but several field positions still
# match the 2003 layout rather than the 2005 layout:
#   - DMETH_REC at 401 (2005 moves to 403)
#   - ATTEND at 408 (2005 moves to 410) — verified against Nat2004doc.pdf p.45
#     which shows `402-407 FILLER`, `408 ATTEND`, `409-414 FILLER`. Position 410
#     is filler in 2004; reading ATTEND there produces 100% null.
# Position 89-90 is MAGER (single-year age), same as 2005+ (not MAGER41 as in 2003).
PUBLIC_US_2004_FIELDS: list[tuple[str, int, int]] = [
    ("DOB_YY", 15, 18),
    ("DOB_MM", 19, 20),
    ("MAGER", 89, 90),
    ("LBO_REC", 212, 212),
    ("TBO_REC", 217, 217),
    ("RESTATUS", 138, 138),
    ("MBCNTRY", 94, 95),
    ("MRACE", 141, 142),
    # MRACE15 is NOT at bytes 108-109 in the 2004 public-use layout (same caveat
    # as the 2003 spec above — raw-byte probing of Nat2004us.zip returns
    # 2-letter alpha codes, not the numeric 01-15 NCHS recode).
    ("MRACEREC", 143, 143),
    ("UMHISP", 148, 148),
    ("MRACEHISP", 149, 149),
    ("MAR", 153, 153),
    ("MEDUC", 155, 155),
    ("MEDUC_REC", 158, 158),
    ("PRECARE", 245, 246),
    ("MPCB", 256, 257),
    ("UPREVIS", 270, 271),
    ("CIG_1", 284, 285),
    ("CIG_2", 286, 287),
    ("CIG_3", 288, 289),
    ("CIG_REC6", 293, 293),
    ("URF_DIAB", 331, 331),
    ("URF_CHYPER", 335, 335),
    ("URF_PHYPER", 336, 336),
    ("DMETH_REC", 401, 401),   # NOTE: position 401, not 403 as in 2005
    ("APGAR5", 415, 416),
    ("DPLURAL", 423, 423),
    ("SEX", 436, 436),
    ("COMBGEST", 451, 452),
    ("GESTREC3", 455, 455),
    ("DBWT", 463, 466),
    ("UFAGECOMB", 184, 185),  # Father's combined age, unrevised/national (10-98, 99=unknown)
    ("UBFACIL", 42, 42),      # Birth facility, unrevised/national (1=hosp, 2=birth ctr, 3=clinic, 4=residence, 5=other, 9=unk)
    ("ATTEND", 408, 408),     # Attendant at birth — 2004 uses position 408 (same as 2003), NOT 410 (2005+).
                               # Verified against Nat2004doc.pdf p.45.
    ("UFHISP", 195, 195),    # Father's Hispanic origin, unrevised/national (0=non-Hisp, 1-5=Hisp, 9=unknown)
    ("FRACEHISP", 196, 196),  # Father's race/Hispanic combined recode (1-8, 9=unknown)
]

# 2005 and 2010 share these positions for this core subset.
PUBLIC_US_2005_2010_FIELDS: list[tuple[str, int, int]] = [
    ("DOB_YY", 15, 18),
    ("DOB_MM", 19, 20),
    ("MAGER", 89, 90),
    ("LBO_REC", 212, 212),
    ("TBO_REC", 217, 217),
    ("RESTATUS", 138, 138),
    ("MBCNTRY", 94, 95),
    ("MRACE", 141, 142),
    ("MRACEREC", 143, 143),
    ("UMHISP", 148, 148),
    ("MRACEHISP", 149, 149),
    ("MAR", 153, 153),
    ("MEDUC", 155, 155),
    ("MEDUC_REC", 158, 158),
    ("PRECARE", 245, 246),
    ("MPCB", 256, 257),
    ("UPREVIS", 270, 271),
    ("CIG_1", 284, 285),
    ("CIG_2", 286, 287),
    ("CIG_3", 288, 289),
    ("CIG_REC6", 293, 293),
    ("URF_DIAB", 331, 331),
    ("URF_CHYPER", 335, 335),
    ("URF_PHYPER", 336, 336),
    ("DMETH_REC", 403, 403),
    ("APGAR5", 415, 416),
    ("DPLURAL", 423, 423),
    ("SEX", 436, 436),
    ("COMBGEST", 451, 452),
    ("GESTREC3", 455, 455),
    ("DBWT", 463, 466),
    ("UFAGECOMB", 184, 185),  # Father's combined age, unrevised/national (10-98, 99=unknown).
                               # Populated 2005-2011; blank 2012-2013 (NCHS moved / removed the field).
    ("FAGECOMB", 182, 183),    # Father's combined age, revised-certificate (10-98, 99=unknown).
                               # Populated on revised-certificate rows from 2006 onward
                               # (empirical coverage: ~28% 2006 → 65% 2008 → 86% 2011 → 90% 2013),
                               # tracking the revised-cert adoption curve. Blank on unrevised rows.
                               # Harmonizer prefers FAGECOMB over UFAGECOMB when both are present;
                               # the two values agree 100% in the overlap region (verified across
                               # 2.1M sampled rows 2006-2011).
    ("FAGEREC11", 186, 187),   # Father's age recode 11 (01=<15, 02=15-19, ..., 10=50+, 11=unknown).
                               # Populated 2005-2013 (a categorical fallback when raw age is suppressed — 2012).
    ("MRACE15", 108, 109),     # Mother's race recode 15 (01-15; 15=multiracial).
                               # Empirically 100% BLANK at bytes 108-109 for 2005-2013 public-use
                               # records. Kept in the spec as a placeholder for downstream checks;
                               # the real MRACE15 data only starts 2014+ (see PUBLIC_US_2014_2015_FIELDS).
    ("UBFACIL", 42, 42),      # Birth facility, unrevised/national (1=hosp, 2=birth ctr, 3=clinic, 4=residence, 5=other, 9=unk)
    ("ATTEND", 410, 410),     # Attendant at birth (1=MD, 2=DO, 3=CNM, 4=other midwife, 5=other, 9=unknown)
    ("UFHISP", 195, 195),    # Father's Hispanic origin, unrevised/national (0=non-Hisp, 1-5=Hisp, 9=unknown)
    ("FRACEHISP", 196, 196),  # Father's race/Hispanic combined recode (1-8, 9=unknown)
    ("FEDUC", 197, 197),      # Father's education (1-8 categories, 9=unknown; filler/blank 2005-2008, valid 2009+ partial, 2011+ near-full)
    ("PAY_REC", 413, 413),    # Payment source recode (1-4, 9=unknown; filler/blank 2005-2008, valid 2009+ partial, 2011+ near-full)
    ("RF_CESAR", 324, 324),    # Prior cesarean, revised-cert (Y/N/U).
                               # Populated on revised-certificate rows from 2005 onward (empirical
                               # coverage: 30.76% 2005 → 90.24% 2013, tracking cert adoption).
    ("RF_CESARN", 325, 326),   # Number of prior cesareans, revised-cert (00-30, 99=unknown).
                               # Same population dynamics as RF_CESAR (revised-cert-only, 2005-2013).
]

# (field_name, start_pos, end_pos) — inclusive on both ends
PUBLIC_US_2014_2015_FIELDS: list[tuple[str, int, int]] = [
    ("DOB_YY", 9, 12),
    ("DOB_MM", 13, 14),
    ("RESTATUS", 104, 104),
    ("MAGER", 75, 76),
    ("MBSTATE_REC", 84, 84),
    ("MRACE6", 107, 107),     # Mother's Race Recode 6 (1 byte; values 1-6; code 6 = multiracial).
    ("MRACE15", 108, 109),    # Mother's Race Recode 15 (2 bytes; values 01-15; 99=unknown)
    ("MBRACE", 110, 110),
    ("MHISP_R", 115, 115),
    ("MRACEHISP", 117, 117),
    ("DMAR", 120, 120),
    ("F_MAR_P", 123, 123),    # Reporting flag for marital/paternity (0=non-reporting state, 1=reporting)
    ("MEDUC", 124, 124),
    ("LBO_REC", 179, 179),
    ("TBO_REC", 182, 182),
    ("ILLB_R", 198, 200),
    ("PRECARE", 224, 225),
    ("PREVIS", 238, 239),
    ("CIG0_R", 261, 261),
    ("CIG1_R", 262, 262),
    ("CIG2_R", 263, 263),
    ("CIG3_R", 264, 264),
    ("BMI", 283, 286),
    ("BMI_R", 287, 287),
    ("WTGAIN", 304, 305),        # Weight gain during pregnancy in pounds (00-97 plain, 98="98+ lbs"
                                  # top-code, 99=unknown). Verified via distribution: 98 has ~17× the
                                  # frequency of 97 in every year, consistent with a top-code bucket
                                  # rather than a second sentinel.
    ("RF_PDIAB", 313, 313),
    ("RF_GDIAB", 314, 314),
    ("RF_PHYPE", 315, 315),
    ("RF_GHYPE", 316, 316),
    ("LD_INDL", 383, 383),       # Induction of labor (Y/N/U)
    ("RDMETH_REC", 407, 407),
    ("DMETH_REC", 408, 408),
    ("APGAR5", 444, 445),
    ("DPLURAL", 454, 454),
    ("SEX", 475, 475),
    ("COMBGEST", 490, 491),
    ("GESTREC10", 492, 493),
    ("GESTREC3", 494, 494),
    # Obstetric estimate of gestation (edited + recodes) — best-practice gestation measure for revised-era years
    ("OEGEST_COMB", 499, 500),
    ("OEGEST_R10", 501, 502),
    ("OEGEST_R3", 503, 503),
    ("DBWT", 504, 507),
    # Unified U/R variables for cross-era comparability (near end of record)
    ("URF_DIAB", 1331, 1331),
    ("URF_CHYPER", 1332, 1332),
    ("URF_PHYPER", 1333, 1333),
    ("FAGECOMB", 147, 148),   # Father's combined age (09-98, 99=unknown)
    ("BFACIL", 32, 32),       # Birth facility (1=hosp, 2=birth ctr, 3-5=home, 6=clinic, 7=other, 9=unknown)
    ("ATTEND", 433, 433),     # Attendant at birth (1=MD, 2=DO, 3=CNM, 4=other midwife, 5=other, 9=unknown)
    ("PAY_REC", 436, 436),    # Payment source recode (1=Medicaid, 2=Private, 3=Self-Pay, 4=Other, 9=Unknown)
    ("RF_CESAR", 331, 331),   # Prior cesarean (Y/N/U)
    # Father demographics
    ("FHISP_R", 160, 160),    # Father's Hispanic origin recode (0=non-Hisp, 1-5=Hisp, 9=unknown)
    ("FRACEHISP", 162, 162),  # Father's race/Hispanic combined recode (1-8, 9=unknown)
    ("FEDUC", 163, 163),      # Father's education (1-8 categories, 9=unknown)
    # Congenital anomalies (revised cert only; Y/N/U except CA_DOWN/CA_DISOR use C/P/N/U)
    ("CA_ANEN", 537, 537),    # Anencephaly
    ("CA_MNSB", 538, 538),    # Spina bifida
    ("CA_CCHD", 539, 539),    # Congenital heart disease
    ("CA_CDH", 540, 540),     # Diaphragmatic hernia
    ("CA_OMPH", 541, 541),    # Omphalocele
    ("CA_GAST", 542, 542),    # Gastroschisis
    ("CA_LIMB", 549, 549),    # Limb reduction
    ("CA_CLEFT", 550, 550),   # Cleft lip/palate
    ("CA_CLPAL", 551, 551),   # Cleft palate alone
    ("CA_DOWN", 552, 552),    # Down syndrome (C/P/N/U)
    ("CA_DISOR", 553, 553),   # Chromosomal disorder (C/P/N/U)
    ("CA_HYPO", 554, 554),    # Hypospadias
    # Infections present (revised cert only; Y/N/U)
    ("IP_GON", 343, 343),     # Gonorrhea
    ("IP_SYPH", 344, 344),    # Syphilis
    ("IP_CHLAM", 345, 345),   # Chlamydia
    ("IP_HEPB", 346, 346),    # Hepatitis B
    ("IP_HEPC", 347, 347),    # Hepatitis C
    # Clinical outcomes (revised cert only; Y/N/U)
    ("AB_NICU", 519, 519),    # NICU admission (Y/N/U)
    ("BFED", 569, 569),       # Breastfed at discharge (Y/N/U)
    # Prior cesarean count and fertility treatment (revised cert only)
    ("RF_CESARN", 332, 333),  # Number of prior cesareans (00-30, 99=unknown)
    ("RF_FEDRG", 326, 326),   # Fertility-enhancing drugs (Y/N/X/U)
    ("RF_ARTEC", 327, 327),   # Assisted reproductive technology (Y/N/U)
]

# =====================================================================
# Linked Birth-Infant Death: Birth-side field overrides
# =====================================================================
# The linked denominator-plus files mostly reuse the same birth-side
# positions as the natality file, BUT some fields differ (notably
# birthweight is at a different position because the linked file uses
# the imputed BRTHWGT field instead of DBWT).
#
# We define complete linked birth-side specs here by copying the natality
# specs and overriding the differing positions.
#
# Sources:
#   - LinkCO05Guide.pdf p44: BRTHWGT at 467-470 (vs natality DBWT at 463-466)
#   - LinkCO15Guide.pdf p35: BRTHWGT at 512-515 (vs natality DBWT at 504-507)
#   - All other fields verified at same positions as natality (DOB_YY, SEX,
#     MAGER, DPLURAL, COMBGEST, GESTREC3, MEDUC, RESTATUS, etc.)

LINKED_BIRTH_2005_2013_FIELDS: list[tuple[str, int, int]] = [
    f if f[0] != "DBWT" else ("DBWT", 467, 470)
    for f in PUBLIC_US_2005_2010_FIELDS
]

LINKED_BIRTH_2014_2020_FIELDS: list[tuple[str, int, int]] = [
    f if f[0] != "DBWT" else ("DBWT", 512, 515)
    for f in PUBLIC_US_2014_2015_FIELDS
]

# =====================================================================
# Linked Birth-Infant Death: Death-side field specs
# =====================================================================
# These are ADDITIONAL fields appended to the birth-certificate portion
# in the linked cohort denominator-plus files.  Positions differ by era
# because the birth-side record length changes.
#
# Sources:
#   - LinkCO05Guide.pdf (2005 cohort linked, pp 51-53) → positions 868-900
#   - LinkCO10Guide.pdf (2010 cohort linked, pp 43+)   → same positions as 2005
#   - LinkCO15Guide.pdf (2015 cohort linked, pp 38-40)  → positions 1346-1384

# --- 2005-2013 linked denominator-plus: death-side fields ---
# Birth section uses LINKED_BIRTH_2005_2013_FIELDS (same as natality
# except BRTHWGT at 467-470 instead of DBWT at 463-466).
# Death fields begin at position 868.  Denominator-plus record length = 900.
LINKED_DEATH_2005_2013_FIELDS: list[tuple[str, int, int]] = [
    ("FLGND", 868, 868),         # Match status (1 = infant death linked; blank = survived)
    ("AGED", 872, 874),          # Age at death in days (000-365)
    ("AGER5", 875, 875),         # Infant age recode 5 (1=<1hr, 2=1-23hr, 3=1-6d, 4=7-27d, 5=28d+)
    ("AGER22", 876, 877),        # Infant age recode 22
    ("MANNER", 878, 878),        # Manner of death (1-7, blank)
    ("DISPO", 879, 879),         # Method of disposition (B/C/D/E/O/R/U)
    ("AUTOPSY", 880, 880),       # Autopsy (Y/N/U)
    ("PLACE_INJ", 882, 882),     # Place of injury (0-9, blank)
    ("UCOD", 884, 887),          # Underlying cause of death (ICD-10 code)
    ("UCODR130", 889, 891),      # 130 Selected Causes of Infant Death recode
    ("RECWT", 893, 900),         # Record weight (1.XXXXXX)
]

LINKED_DENOMPLUS_RECLEN_2005_2013 = 900

# --- 2014-2020 linked denominator-plus: death-side fields ---
# Birth section uses LINKED_BIRTH_2014_2020_FIELDS (same as natality
# except BRTHWGT at 512-515 instead of DBWT at 504-507).
# Death fields begin at position 1346.  Denominator-plus record length = 1384.
LINKED_DEATH_2014_2020_FIELDS: list[tuple[str, int, int]] = [
    ("FLGND", 1346, 1346),       # Match status (1 = infant death linked; blank = survived)
    ("AGED", 1356, 1358),        # Age at death in days (000-365)
    ("AGER5", 1359, 1359),       # Infant age recode 5 (1=<1hr, 2=1-23hr, 3=1-6d, 4=7-27d, 5=28d+)
    ("AGER22", 1360, 1361),      # Infant age recode 22
    ("MANNER", 1362, 1362),      # Manner of death (1-7, blank)
    ("DISPO", 1363, 1363),       # Method of disposition (B/C/O/U)
    ("AUTOPSY", 1364, 1364),     # Autopsy (Y/N/U)
    ("PLACE_INJ", 1366, 1366),   # Place of injury (0-9, blank)
    ("UCOD", 1368, 1371),        # Underlying cause of death (ICD-10 code)
    ("UCODR130", 1373, 1375),    # 130 Selected Causes of Infant Death recode
    ("RECWT", 1377, 1384),       # Record weight (1.XXXXXX)
]

LINKED_DENOMPLUS_RECLEN_2014_2020 = 1384

# =====================================================================
# Linked Birth-Infant Death: pre-1990 COHORT denominator layouts
# (C8.18 DO step 3a — 1983-1991 cohort backward extension)
# =====================================================================
# The pre-1990 NCHS cohort-linked files use COMPACT fixed-width layouts
# that are NOT byte-position-aligned with the natality public-use file
# (unlike the 2005+ LINKED_BIRTH_* specs, which copy natality positions
# + a few overrides). They are therefore authored here as standalone
# tuple lists, transcribed from the NCHS cohort user guides and
# value-distribution-verified at C8.18 DO step 3a SMOKE Tier 1
# (L13-extension: byte position alone is not trusted).
#
# Two distinct physical layouts span 1983-1991 (the 1989 birth-cert
# revision is the boundary — verified empirically, NOT assumed):
#
#   * 1983-1988: a PURE births-only 91-byte Denominator file
#     (LinkCO{YY}USden.dat; match status + birth cert + record weight;
#     NO death section — the linked death detail is in the separate
#     500-byte numerator file -> C8.18 DO step 3b). 91 data bytes +
#     CR/LF = 93-byte block (e.g. LinkCO83USden.dat 310,738,482 / 93
#     = 3,341,274 = guide count).
#   * 1989-1991: a 225-byte Denominator-PLUS file (birth cert locs
#     7-212 + a small appended death-derived "plus" 213-225),
#     structurally analogous to the 2005+ denominator-plus model
#     (alongside a richer 535-byte numerator -> DO step 3b/5).
#     225 data bytes + CR/LF = 227-byte block (LinkCO89USden.dat
#     918,414,987 / 227 = 4,045,881 = guide count).
#
# The 2005+ parser member-finder (`_find_denomplus_member`, matches
# "DENOM") + the 1983-1988 two-file numerator left-join + the
# `.dat` decode strategy are C8.18 DO step 5 parser concerns; this
# step authors the LAYOUT substrate + an additive dispatcher branch.
#
# Sources:
#   - 1983-1988: PRE_FLIGHT_LOG.md 2026-05-17T20:00:00Z SMOKE Tier 0
#     (full 1983 denominator layout reconstructed from LinkCO83Guide.pdf
#     pp12-31; state-on-disk; 1983 == 1988 == 91 bytes per-year stable).
#   - 1989-1991: LinkCO89Guide.pdf p17 (file characteristics: 225 B /
#     4,045,881) + pp18-19 ("List of Data Elements and Locations",
#     Denominator-Plus File column) + pp20-47 (detail code outlines);
#     captured in PRE_FLIGHT_LOG.md 2026-05-17T22:30:00Z SMOKE Tier 0.
#     1989-1991 share the 1989-revision certificate (per-year stable).
#
# Field names are NCHS-cohort-guide-traceable raw names; the
# harmonized-schema mapping (v4 schema continuity with 2005-2023) is
# C8.18 DO step 5. Positions are 1-based inclusive (start, end).

# --- 1983-1988 cohort: births-only Denominator (91 bytes) ---
LINKED_BIRTH_1983_1988_FIELDS: list[tuple[str, int, int]] = [
    ("MATCHS", 1, 1),       # Match status (1 matched / 3 surviving)
    ("BIRYR", 2, 5),        # Year of birth
    ("RECTYPE", 10, 10),    # Record type
    ("RESSTAT", 11, 11),    # Resident status (1-4)
    ("STOCC", 17, 18),      # State of occurrence (01-51; * = 50% sample)
    ("CNTYOCC", 19, 21),    # County of occurrence (999 = <250k pop)
    ("STRES", 27, 28),      # State of residence
    ("CNTYRES", 29, 31),    # County of residence
    ("CITYRES", 32, 34),    # City of residence
    ("CRACE", 36, 36),      # Detail race of child (1-8)
    ("CRACE3", 37, 37),     # Race of child recode 3
    ("CSEX", 38, 38),       # Sex of child (1 M / 2 F)
    ("DGEST", 39, 40),      # Detail gestation weeks (17-52, 99 = NS)
    ("GESTR10", 41, 42),    # Gestation recode 10
    ("DBIRWT", 43, 46),     # Birth weight grams (0227-8165, 9999 = NS)
    ("BWR14", 47, 48),      # Birth weight recode 14
    ("BWR3", 49, 49),       # Birth weight recode 3
    ("DPLURAL", 50, 50),    # Plurality (1 single / 2 twin / 3 other)
    ("APGAR1", 51, 52),     # Apgar 1 minute (00-10, 99)
    ("APGAR5", 53, 54),     # Apgar 5 minute (00-10, 99)
    ("ORMOTH", 55, 56),     # Mother origin/descent (00-24, 88, 99)
    ("DMRACE", 57, 57),     # Detail race of mother (1-8, 0/9 = NS)
    ("DMAGE", 58, 59),      # Detail age of mother (10-49)
    ("MAGER12", 60, 61),    # Age of mother recode 12
    ("DMEDUC", 62, 63),     # Mother education detail (00-17, 99)
    ("MEDUC6", 64, 64),     # Mother education recode 6
    ("DMAR", 65, 65),       # Marital status (1 married / 2 unmarried)
    ("MPLBIR", 66, 67),     # Mother place of birth (01-59, 99)
    ("ORFATH", 68, 69),     # Father origin/descent
    ("DFRACE", 70, 70),     # Detail race of father
    ("DFAGE", 71, 72),      # Detail age of father (10-98, 99 = NS)
    ("DFEDUC", 73, 74),     # Father education detail
    ("DLLB", 75, 75),       # Interval since last live birth (0-7, 9)
    ("OUTCOME", 76, 76),    # Outcome of last pregnancy (0/1/2/9)
    ("DLPT", 77, 77),       # Interval since last preg termination (0-9)
    ("DMPCB", 78, 79),      # Detail month prenatal care began (01-09, 00, 99)
    ("MPCR6", 80, 80),      # Month prenatal care recode 6
    ("NPREVIS", 81, 82),    # Total prenatal visits (00-49, 99)
    ("DTOTORD", 83, 84),    # Detail total birth order (01-50, 99)
    ("TOTORD9", 85, 85),    # Total birth order recode 9
    ("DLIVORD", 86, 87),    # Detail live birth order (01-50, 99)
    ("LIVORD9", 88, 88),    # Live birth order recode 9
    ("PLDEL", 89, 89),      # Place of delivery (1 hosp / 2-3 nonhosp / 9)
    ("BIRATTND", 90, 90),   # Attendant at birth (1 MD / 2 midwife / 3 / 9)
    ("RECWT", 91, 91),      # Record weight (denominator inflation weight)
]

LINKED_DEN_RECLEN_1983_1988 = 91

# --- 1989-1991 cohort: 225-byte Denominator-PLUS, birth-cert section ---
# Positions are byte-exact from the LinkCO89Guide.pdf DETAIL code-outline
# (pp20-47), NOT the pp18-19 element-span summary. C8.18 DO step 3a
# SMOKE Tier 1 (L13-extension value-distribution) caught that the
# pp18-19 spans are composites (e.g. "Birthweight 79-85" = DBIRWT@79-82
# + BIRWT12@83-84 + BIRWT4@85); the detail code-outline is authoritative.
LINKED_BIRTH_1989_1991_FIELDS: list[tuple[str, int, int]] = [
    ("MATCHS", 1, 1),         # Match status (1/2/3)
    ("IDNUMBER", 2, 6),       # Infant death number
    ("BIRYR", 7, 10),         # Year of birth (1989-1991)
    ("RESSTATB", 11, 11),     # Resident status - birth (1-4)
    ("PLDEL", 12, 12),        # Place/facility of delivery (1-5, 9)
    ("BIRATTND", 13, 13),     # Attendant at delivery (1-5, 9)
    ("STOCCFIPB", 14, 15),    # State of occurrence FIPS - birth
    ("CNTOCFIPB", 16, 18),    # County of occurrence FIPS - birth
    ("STRESFIPB", 19, 20),    # State of residence FIPS - birth
    ("CNTRESFIPB", 21, 23),   # County of residence FIPS - birth
    ("BRSTATE", 24, 25),      # NCHS state of residence - birth
    ("CITYRESB", 26, 28),     # NCHS city of residence - birth
    ("MAGEFLG", 29, 29),      # Mother age imputed flag
    ("DMAGE", 30, 31),        # Detail age of mother (10-49)
    ("MAGER8", 32, 32),       # Age of mother recode 8
    ("ORMOTH", 33, 33),       # Hispanic origin of mother
    ("ORRACEM", 34, 34),      # Hispanic-origin race recode (mother)
    ("MRACEIMP", 35, 35),     # Mother race imputed flag
    ("MRACE", 36, 37),        # Detail race of mother
    ("MRACE3", 38, 38),       # Race of mother recode 3
    ("DMEDUC", 39, 40),       # Detail education of mother (00-17, 99)
    ("MEDUC6", 41, 41),       # Education of mother recode 6
    ("DMARIMP", 42, 42),      # Marital status imputed flag
    ("DMAR", 43, 43),         # Marital status (1/2)
    ("MPLBIR", 44, 45),       # Mother place of birth
    ("MPLBIRR", 46, 46),      # Mother place of birth recode
    ("DTOTORD", 47, 48),      # Detail total birth order (01-40, 99)
    ("DLIVORD", 49, 50),      # Detail live birth order (00-31, 99)
    ("MONPRE", 51, 52),       # Detail month prenatal care began (00-09, 99)
    ("MPRE5", 53, 53),        # Month prenatal care recode 5
    ("NPREVIS", 54, 55),      # Number of prenatal visits (00-48, 49)
    ("ADEQUACY", 56, 56),     # Adequacy of care recode
    ("DLLB", 57, 59),         # Interval since last live birth
    ("FAGERFLG", 60, 60),     # Father age imputed flag
    ("DFAGE", 61, 62),        # Detail age of father (10-98, 99)
    ("ORFATH", 63, 63),       # Hispanic origin of father
    ("ORRACEF", 64, 64),      # Hispanic-origin race recode (father)
    ("FRACE", 65, 66),        # Detail race of father
    ("DFEDUC", 67, 68),       # Detail education of father (00-17, 99)
    ("CDOBMIMP", 69, 69),     # Date-of-birth month imputed flag
    ("BIRMON", 70, 71),       # Month of birth (01-12)
    ("GESTFLG", 72, 72),      # Gestation imputed flag
    ("GESTAT", 73, 74),       # Detail gestation weeks (17-47, 99)
    ("GESTAT10", 75, 76),     # Gestation recode 10
    ("CSEXIMP", 77, 77),      # Sex imputed flag
    ("CSEX", 78, 78),         # Sex of child (1 M / 2 F)
    ("DBIRWT", 79, 82),       # Detail birth weight (grams)
    ("BIRWT12", 83, 84),      # Birth weight recode 12
    ("BIRWT4", 85, 85),       # Birth weight recode 4
    ("PLURIMP", 86, 86),      # Plurality imputed flag
    ("DPLURAL", 87, 87),      # Plurality (1-5)
    ("OMAPS", 88, 89),        # Apgar 1 minute (00-10, 99)
    ("FMAPS", 90, 91),        # Apgar 5 minute (00-10, 99)
    ("DELMTH", 92, 99),       # Method of delivery (composite)
    ("MEDRISK", 101, 117),    # Medical risk factors (composite)
    ("OTHERRSK", 118, 128),   # Other risk factors (tobacco/alcohol/wtgain)
    ("OBSTETRC", 130, 136),   # Obstetric procedures (composite)
    ("LABOR", 138, 153),      # Complications of labor/delivery (composite)
    ("ABNORMNB", 155, 163),   # Abnormal conditions of the newborn (composite)
    ("CONGENIT", 165, 186),   # Congenital anomalies (composite)
    ("FLRES", 187, 206),      # Residence reporting flags (composite)
    ("DOW", 208, 208),        # Day of week of birth
    ("CRACE", 209, 210),      # Detail race of child
    ("CRACE3", 211, 212),     # Race of child recode
]

# --- 1989-1991 cohort: Denominator-PLUS appended death-derived section ---
# Locations 213-225 of the 225-byte denominator-plus record (the "plus";
# LinkCO89Guide.pdf pp46-47). The FULL ICD-9 multiple-cause detail
# (entity/record axis, 261-504) lives in the separate 535-byte
# numerator -> C8.18 DO step 3b/5 (soft-flag (gg)).
LINKED_DEATH_1989_1991_FIELDS: list[tuple[str, int, int]] = [
    ("AGED", 213, 215),       # Age at death in days (000-364)
    ("AGER5", 216, 216),      # Infant age recode 5
    ("AUTOPSY", 217, 217),    # Autopsy performed (1/2/8/9)
    ("ACCIDPL", 218, 218),    # Place of accident
    ("UCOD", 219, 222),       # Underlying cause of death (ICD-9)
    ("UCODR61", 223, 225),    # 61 selected causes of infant death recode
]

LINKED_DENOMPLUS_RECLEN_1989_1991 = 225

# =====================================================================
# Linked Birth-Infant Death: pre-1990 COHORT numerator layouts
# (C8.18 DO step 3b — 1983-1991 cohort backward extension)
# =====================================================================
# The cohort NUMERATOR file (LinkCO{YY}USnum.dat) is the linked
# infant-death <-> birth-certificate record set (one row per linked
# infant death). It is a SEPARATE physical file from the denominator
# (the 3a-authored LINKED_*_1983_1988 / _1989_1991 specs); this block
# authors the numerator LAYOUT substrate only. The two-file num/den
# construction (1983-1988) + the numerator<->denominator-plus join
# (1989-1991, key = (MATCHS, IDNUMBER)) + `_find_denomplus_member`
# "DEN"/"NUM" support + the harmonize path are C8.18 DO step 5
# parser/harmonize concerns (per PRE_FLIGHT_LOG 2026-05-17T20:00:00Z
# + 2026-05-18T00:30:00Z; soft-flag (ii) §11 model-clarification).
#
# Cert match key (PRE_FLIGHT_LOG 2026-05-18T00:30:00Z HALT-4 finding):
#   * 1989-1991: (MATCHS@1, IDNUMBER@2-6) — both already in
#     LINKED_BIRTH_1989_1991_FIELDS; the DO-step-5 numerator<->
#     denominator-plus join key.
#   * 1983-1988: NO record-level public-use key. The 500-byte
#     numerator is SELF-CONTAINED — locs 1-91 are the deceased
#     infant's full birth covariates (byte-identical to the 91-byte
#     denominator LINKED_BIRTH_1983_1988_FIELDS — the NCHS
#     "Denominator Record and Natality Section of Linked Record"
#     shared layout). The standard pre-2005 cohort-IMR construction
#     is self-contained-numerator + aggregate-denominator (DO step 5).
#
# Both layouts are byte-exact from the guide DETAIL code-outline
# (L13-extension; the C8.18 DO step 3a SMOKE-Tier-1 governing
# precedent — the p13/pp18-19 element-span summary is composite +
# NOT trusted), value-distribution-verified at DO step 3b SMOKE
# Tier 1 on real LinkCO{83..91}USnum.dat.
#
# Sources:
#   - 1983-1988: LinkCO83Guide.pdf p12 (file char: 500 B / 39,704),
#     p32 (locs 92-193 = numerator-only RESERVED), pp33-45
#     ("Mortality Part/Section of Linked Record" detail, locs
#     194-500). Natality section locs 1-91 == the 3a-authored
#     LINKED_BIRTH_1983_1988_FIELDS (do not re-author).
#   - 1989-1991: LinkCO89Guide.pdf p17 (file char: 535 B / 38,605;
#     Unlinked also 535 B / 1,029), p20 (locs 7-212 = Birth Cert,
#     213-535 = Death Cert), pp46-56 ("Mortality Section of Linked
#     Record" detail). Birth section locs 1-212 == the 3a-authored
#     LINKED_BIRTH_1989_1991_FIELDS; death-derived "plus" locs
#     213-225 == LINKED_DEATH_1989_1991_FIELDS (do not re-author).
#
# Positions are 1-based inclusive (start, end). Composite ENTITY /
# RECORDAX multiple-cause spans are single fields here (per-condition
# decomposition + `cause_recode_130` per-era = DO step 5; the C8.18
# DO3a MEDRISK/OBSTETRC composite-span precedent; soft-flag (gg)).

# --- 1983-1988 cohort numerator: mortality section (locs 194-500) ---
# (Natality section locs 1-91 REUSE LINKED_BIRTH_1983_1988_FIELDS;
#  locs 92-193 = numerator-only RESERVED, not enumerated.)
LINKED_NUM_DEATH_1983_1988_FIELDS: list[tuple[str, int, int]] = [
    ("YOD", 194, 197),         # Year of death (1983-19xx)
    ("RECTYPED", 198, 198),    # Record type - death (1 res / 2 nonres)
    ("RESSTATD", 199, 199),    # Resident status - death (1-4)
    ("REGOCCD", 200, 200),     # Region of occurrence - death
    ("DIVOCCD", 201, 202),     # Division + state subcode of occurrence
    ("XSTOCCD", 203, 204),     # Expanded state of occurrence (01-52)
    ("STOCCD", 205, 206),      # State of occurrence (01-51)
    ("CNTOCCD", 207, 209),     # County of occurrence (999 = <250k)
    ("REGRESD", 210, 210),     # Region of residence - death
    ("DIVRESD", 211, 212),     # Division + state subcode of residence
    ("XSTRESD", 213, 214),     # Expanded state of residence
    ("STRESD", 215, 216),      # State of residence
    ("CNTRESD", 217, 219),     # County of residence (999 = <250k)
    ("CITYRESD", 220, 222),    # City of residence (999 = balance)
    ("AGER5", 223, 223),       # Infant age recode 5 (1=<1hr..5=postneo)
    ("AGER76", 224, 225),      # Infant age recode 76
    ("AGER38", 226, 227),      # Infant age recode 38
    ("HOSPD", 228, 228),       # Hospital and patient status
    ("AUTOPSY", 229, 229),     # Autopsy performed (1/8/9)
    ("ACCIDPL", 230, 230),     # Place of accident (causes E850-E929)
    ("UCOD", 231, 234),        # Underlying cause of death (ICD-9; no E)
    ("UCODR61", 235, 237),     # 61 selected causes recode (010-680)
    ("NENTITY", 238, 239),     # Number of entity-axis conditions (00-20)
    ("ENTITY", 240, 379),      # Entity-axis conditions (20 x 7-byte)
    ("NRECORD", 380, 381),     # Number of record-axis conditions (00-20)
    ("RECORDAX", 382, 481),    # Record-axis conditions (20 x 5-byte)
    ("RESERVED", 482, 500),    # Reserved positions (19 bytes)
]

LINKED_NUM_RECLEN_1983_1988 = 500

# --- 1989-1991 cohort numerator: mortality section (locs 226-535) ---
# (Birth section locs 1-212 REUSE LINKED_BIRTH_1989_1991_FIELDS;
#  death-derived "plus" locs 213-225 REUSE LINKED_DEATH_1989_1991_FIELDS.)
LINKED_NUM_DEATH_1989_1991_FIELDS: list[tuple[str, int, int]] = [
    ("RESERVED1", 226, 260),   # Reserved positions (35 bytes)
    ("NENTITY", 261, 262),     # Number of entity-axis conditions (00-20)
    ("ENTITY", 263, 402),      # Entity-axis conditions (20 x 7-byte, ICD-9)
    ("NRECORD", 403, 404),     # Number of record-axis conditions (00-20)
    ("RECORDAX", 405, 504),    # Record-axis conditions (20 x 5-byte, ICD-9)
    ("RESSTATD", 505, 505),    # Resident status - death (1-4)
    ("STOCCFIPD", 506, 507),   # State of occurrence FIPS - death
    ("CNTOCFIPD", 508, 510),   # County of occurrence FIPS - death
    ("STRESFIPD", 511, 512),   # State of residence FIPS - death (00=for)
    ("CNTRESFIPD", 513, 515),  # County of residence FIPS - death
    ("DRSTATE", 516, 517),     # State of residence NCHS codes - death
    ("CITYRESD", 518, 520),    # City of residence NCHS codes (999=bal)
    ("EOSPD", 521, 521),       # Place of death
    ("DTHYR", 522, 525),       # Year of death (1989-19xx)
    ("DTHMON", 526, 527),      # Month of death (01-12)
    ("WEEKDAYD", 528, 528),    # Day of week of death (1-7)
    ("RESERVED2", 529, 535),   # Reserved positions (7 bytes)
]

LINKED_NUM_RECLEN_1989_1991 = 535

# =====================================================================
# Linked Birth-Infant Death: 1995-2002 COHORT layouts
# (C8.18 DO step 4a — 1995-2002 cohort backward extension)
# =====================================================================
# The 1995-2002 cohort-linked files use a 230-byte Denominator-PLUS
# (LinkCO{YY}US{Den,DEN}.dat) + a 535-byte Numerator
# (LinkCO{YY}US{Num,NUM}.dat) + a 535-byte Unlinked file. This is the
# three-file denominator-plus model (the same family as 1989-1991 +
# 2005+, NOT the pure two-file 1983-1988 form): the denominator-plus
# IS the one-row-per-birth set; the numerator adds the richer
# multiple-cause mortality detail (joined via IDNUMBER at DO step 5).
#
# Authored byte-exact from the LinkCO95Guide.pdf DETAIL "Item and Code
# Outline" (pp20-62; the Item-Location column), NOT the pp18-19 "List
# of Data Elements and Locations" element-span SUMMARY (L13-extension:
# the C8.18 DO step 3a SMOKE-Tier-1 catch is the governing precedent —
# the SUMMARY spans are composites, e.g. SUMMARY pos 210 = "flag in
# both num/den" + 220-222 = part of "multiple conditions", whereas the
# byte-level DETAIL labels 210 = R7 reserved + 220-222 = UCODR recode;
# the DETAIL is authoritative). The 1995-2002-reuses-1989-1991
# hypothesis was FALSIFIED at the C8.18 DO step 4 PRE-FLIGHT
# (2026-05-18T05:00:00Z) by a read-only real-data value-distribution
# probe (same 535-byte numerator length != same layout): this layout
# is authored FRESH and value-distribution-verified at C8.18 DO step
# 4a SMOKE Tier 1 on real LinkCO{95,98,99,02}US{Den,Num}.dat.
#
# ONE physical layout spans 1995-2002 (record lengths 230/535 constant
# across the 1998->1999 ICD-9->ICD-10 boundary — empirically confirmed:
# LinkCO99Guide.pdf Den 230 / Num 535 + all 11 spot-checked DETAIL
# anchors byte-identical to LinkCO95Guide; only the UCOD@216-219
# value-domain changes "ICD 9th Revision" (1995-98) -> "ICD 10th
# Revision" (1999-2002), and UCODR@220-222 "61 Infant Cause Recode"
# (ICD-9) -> "130-cause" (ICD-10) — a within-era value-domain, NOT a
# byte shift; the harmonized cause-column shape + per-era recode
# semantics are C8.18 DO step 5/6, soft-flag (gg)).
#
# Structural boundaries (LinkCO95Guide.pdf p20 + p50):
#   * Locations 1-210   = MATCHS@1 + IDNUMBER@2-6 + Birth Certificate
#                          (7-210); identical in den-plus + numerator
#                          (the shared "Denominator Record and Natality
#                          Section of Numerator (Linked) Record" detail).
#   * Locations 211-222 = death-derived "plus" (AGED..UCODR); on BOTH
#                          the numerator AND denominator-plus files.
#   * Locations 223-230 = RECWT (record weight); ends the den-plus.
#   * Locations 223-535 = numerator file only (RECWT 223-230, then a
#                          231-260 reserved gap + multiple-cause +
#                          death geo/date 261-535).
#
# The two-file num<->denom-plus construction (1995-2002 join key =
# IDNUMBER@2-6, per LinkCO95Guide p20: "This number uniquely identifies
# the same infant in the numerator and denominator-plus files"), the
# `_find_denomplus_member` "DEN"/"NUM" support, the DEFLATE64-at-2003
# tooling decision (1995-2002 = DEFLATE, stdlib-fine), and the
# harmonize path are C8.18 DO step 4b/5 concerns; this step authors the
# LAYOUT substrate + additive dispatcher branches only.
#
# Composite multiple-field blocks (DELMETH/MEDRISK/OTHERRSK/OBSTETRC/
# LABOR/NEWBORN/CONGENIT/FLRES + the entity/record-axis ENTITY/RECORD
# spans) are single composite spans here; per-condition leaf
# decomposition + per-era cause recode = C8.18 DO step 5 (the C8.18
# DO3a MEDRISK/OBSTETRC + DO3b ENTITY/RECORDAX composite-span
# precedent; soft-flag (gg)). Positions are 1-based inclusive.
#
# Sources:
#   - LinkCO95Guide.pdf p15-17 (file char: Den 230 / Num 535 / Unl 535;
#     LinkCO95USDen.dat 905,498,784 / 232 = 3,903,012 = p15), pp20-49
#     ("Denominator Record and Natality Section of Numerator (Linked)
#     Record" DETAIL, locs 1-210), pp50-51 ("...Mortality Section..."
#     DETAIL, locs 211-230), pp52-62 ("Mortality Section of Numerator
#     (Linked) Record" DETAIL, locs 231-535); captured state-on-disk in
#     PRE_FLIGHT_LOG.md 2026-05-18T14:30:00Z SMOKE Tier 0.
#   - LinkCO99Guide.pdf p16-18 (Den 230 / Num 535 / Unl 535) + DETAIL
#     anchor cross-check (ICD-10 1999-2002 sub-era; byte-identical).

# --- 1995-2002 cohort: 230-byte Denominator-PLUS, birth-cert section ---
# Locs 1-210 (MATCHS/IDNUMBER + Birth Certificate). Identical in the
# den-plus AND the numerator's natality section (LinkCO95Guide p20-49).
LINKED_BIRTH_1995_2002_FIELDS: list[tuple[str, int, int]] = [
    ("MATCHS", 1, 1),         # Match status (1 matched B/ID, 2 surviving, 3 unmatched-unl-only)
    ("IDNUMBER", 2, 6),       # Infant death number (num<->denom-plus join key)
    ("BIRYR", 7, 10),         # Year of birth (1995-2002)
    ("RESSTATB", 11, 11),     # Resident status - birth (1-4)
    ("BRSTATE", 12, 13),      # Expanded state of residence - NCHS codes - birth
    ("STOCCFIPB", 14, 15),    # State of occurrence FIPS - birth
    ("CNTOCFIPB", 16, 18),    # County of occurrence FIPS - birth
    ("STRESFIPB", 19, 20),    # State of residence FIPS - birth
    ("CNTYRFPB", 21, 23),     # County of residence FIPS - birth
    ("PLRES", 24, 28),        # Place (city) of residence FIPS
    ("MAGEFLG", 29, 29),      # Age of mother flag
    ("DMAGE", 30, 31),        # Age of mother (10-49)
    ("MAGER8", 32, 32),       # Age of mother recode 8
    ("ORMOTH", 33, 33),       # Hispanic origin of mother
    ("ORRACEM", 34, 34),      # Hispanic origin and race of mother recode
    ("MRACEIMP", 35, 35),     # Race of mother imputation flag
    ("MRACE", 36, 37),        # Race of mother (detail)
    ("MRACE3", 38, 38),       # Race of mother recode 3
    ("DMEDUC", 39, 40),       # Education of mother detail (00-17, 99)
    ("MEDUC6", 41, 41),       # Education of mother recode 6
    ("DMARIMP", 42, 42),      # Marital status imputation flag
    ("DMAR", 43, 43),         # Marital status of mother (1/2)
    ("MPLBIR", 44, 45),       # Place of birth of mother
    ("MPLBIRR", 46, 46),      # Place of birth of mother recode
    ("DTOTORD", 47, 48),      # Detail total birth order
    ("DLIVORD", 49, 50),      # Detail live birth order
    ("MONPRE", 51, 52),       # Detail month prenatal care began (00-09, 99)
    ("MPRE5", 53, 53),        # Month prenatal care began recode 5
    ("NPREVIST", 54, 55),     # Total number of prenatal visits
    ("ADEQUACY", 56, 56),     # Adequacy of care recode (Kessner)
    ("R1", 57, 59),           # Reserved positions
    ("FAGERFLG", 60, 60),     # Reported age of father used flag
    ("DFAGE", 61, 62),        # Age of father
    ("ORFATH", 63, 63),       # Hispanic origin of father
    ("ORRACEF", 64, 64),      # Hispanic origin and race of father recode
    ("FRACE", 65, 66),        # Race of father (detail)
    ("PLDEL", 67, 67),        # Place or facility of delivery
    ("BIRATTND", 68, 68),     # Attendant at delivery
    ("R2", 69, 69),           # Reserved position
    ("GESTESTM", 70, 70),     # Clinical estimate of gestation used flag
    ("CLINGEST", 71, 72),     # Clinical estimate of gestation (17-47, 99)
    ("GESTIMP", 73, 73),      # Gestation imputation flag
    ("GESTAT", 74, 75),       # Gestation - detail in weeks (17-47, 99)
    ("GESTAT10", 76, 77),     # Gestation recode 10
    ("CSEXIMP", 78, 78),      # Sex imputation flag
    ("CSEX", 79, 79),         # Sex of child (1 M / 2 F)
    ("BWIF", 80, 80),         # Birth weight imputation flag
    ("DBIRWT", 81, 84),       # Birth weight detail in grams (imputed)
    ("BIRWT12", 85, 86),      # Birth weight recode 12 (imputed)
    ("BIRWT4", 87, 87),       # Birth weight recode 4 (imputed)
    ("PLURIMP", 88, 88),      # Plurality imputation flag
    ("DPLURAL", 89, 89),      # Plurality
    ("FMAPS", 90, 91),        # Five-minute Apgar score (00-10, 99)
    ("DELMETH", 92, 99),      # Method of delivery (composite; leaves DO5)
    ("MEDRISK", 100, 117),    # Medical risk factors (composite; MRFLAG@100..OTHERMR@117; DO5)
    ("OTHERRSK", 118, 128),   # Other risk factors - tobacco/alcohol/wt-gain (composite; DO5)
    ("OBSTETRC", 129, 136),   # Obstetric procedures (composite; leaves DO5)
    ("LABOR", 137, 153),      # Complications of labor and/or delivery (composite; DO5)
    ("NEWBORN", 154, 163),    # Abnormal conditions of the newborn (composite; DO5)
    ("CONGENIT", 164, 186),   # Congenital anomalies (composite; leaves DO5)
    ("FLRES", 187, 203),      # Reporting flags for place of residence (composite; DO5)
    ("CDOBMIMP", 204, 204),   # Month of birth of child imputation flag
    ("BIRMON", 205, 206),     # Month of birth (01-12)
    ("R6", 207, 208),         # Reserved position
    ("WEEKDAYB", 209, 209),   # Day of week child born
    ("R7", 210, 210),         # Reserved (SUMMARY claims num/den flag; DETAIL authoritative, L13-ext)
]

# --- 1995-2002 cohort: Denominator-PLUS appended death "plus" + RECWT ---
# Locs 211-230. 211-222 on BOTH num + den-plus; 223-230 RECWT (den-plus
# ends at 230). Analogous to LINKED_DEATH_1989_1991 / _2005_2013.
LINKED_DEATH_1995_2002_FIELDS: list[tuple[str, int, int]] = [
    ("AGED", 211, 213),       # Age at death in days (000-364)
    ("AGER5", 214, 214),      # Infant age recode 5
    ("ACCIDPL", 215, 215),    # Place of accident (E850-E869, E880-E928)
    ("UCOD", 216, 219),       # Underlying cause - ICD-9 (1995-98) / ICD-10 (1999-2002)
    ("UCODR", 220, 222),      # Infant cause recode - 61-cause ICD-9 / 130-cause ICD-10 (DO5)
    ("RECWT", 223, 230),      # Record weight (1.XXXXXX; ~1.0 surviving, >1.0 infant death)
]

LINKED_DENOMPLUS_RECLEN_1995_2002 = 230

# --- 1995-2002 cohort numerator: mortality section (locs 231-535) ---
# (Birth section 1-210 REUSE LINKED_BIRTH_1995_2002_FIELDS; death "plus"
#  211-230 REUSE LINKED_DEATH_1995_2002_FIELDS.) 231-260 = reserved gap
# (unenumerated in the DETAIL; the LinkCO95Guide DETAIL jumps RECWT@230
# -> MULTCOND@261; mirrors the 1989-1991 numerator RESERVED1@226-260).
LINKED_NUM_DEATH_1995_2002_FIELDS: list[tuple[str, int, int]] = [
    ("RESERVED1", 231, 260),  # Reserved gap (RECWT@230 -> MULTCOND@261)
    ("EANUM", 261, 262),      # Number of entity-axis conditions (00-20)
    ("ENTITY", 263, 402),     # Entity-axis conditions (20 x 7-byte; ICD-9/10; composite, DO5)
    ("RANUM", 403, 404),      # Number of record-axis conditions (00-20)
    ("RECORD", 405, 504),     # Record-axis conditions (20 x 5-byte; ICD-9/10; composite, DO5)
    ("RESSTATD", 505, 505),   # Resident status - death (1-4)
    ("DRSTATE", 506, 507),    # Expanded state of residence - NCHS codes - death
    ("STOCCFIPD", 508, 509),  # State of occurrence FIPS - death
    ("CNTOCFIPD", 510, 512),  # County of occurrence FIPS - death
    ("STRESFIPD", 513, 514),  # State of residence FIPS - death (00 = foreign)
    ("CNTYRFPD", 515, 517),   # County of residence FIPS - death
    ("PLRESD", 518, 522),     # Place (city) of residence FIPS - death
    ("HOSPD", 523, 523),      # Hospital and patient status
    ("DTHYR", 524, 527),      # Year of death (cohort .. cohort+1)
    ("DTHMON", 528, 529),     # Month of death (01-12)
    ("R8", 530, 531),         # Reserved position
    ("WEEKDAYD", 532, 532),   # Day of week of death (1-7, 9)
    ("R9", 533, 535),         # Reserved positions (numerator ends at 535)
]

LINKED_NUM_RECLEN_1995_2002 = 535


# ==========================================================================
# C8.18 DO step 4b — cohort 2003 linked layout (783-byte Denominator-PLUS
# + 1142-byte numerator; 2003-revision transition).
#
# REVISION@7 flags the certificate revision per record (S=1989 version
# unrevised / A=2003 version revised); the byte LAYOUT is one fixed-width
# record regardless (the "Vers*" column flags which revision populates a
# field, not a layout shift). 2003 is the cohort-linked birth year so all
# infant deaths are ICD-10 (deaths occur 2003-2004).
#
# Reconstructed byte-exact FRESH from the LinkCO03Guide.pdf DETAIL
# "Position/Len/Field" code-outline (pp20-72; the L13-extension governing
# precedent — the pp18-19 "Linked 2003 Cohort Data Elements and Locations"
# element-span SUMMARY is composite + NOT trusted, used only as an
# independent block-range cross-check, all 9 cross-checks matched). The
# prior C8.18 DO step 4 PRE-FLIGHT *assumption* "2003 = 783/1259" was
# FALSIFIED: the guide p17 File Characteristics + exact zip-member
# arithmetic give numerator = 1142 (27,843 x (1142+2 CRLF) = 31,852,392
# = VS03LKBC.USNUMPUB) / den-plus = 783 (4,096,151 x 785 = 3,215,478,535
# = VS03LKBC.USDENPUB). Never assume same-model==same-layout (L13-ext).
#
# Composite multiple-field blocks (MEDRISK/OBSTETRC/LABOR/DELMETH/NEWBORN/
# CONGENIT + the entity/record-axis ENTITY/RECORD spans) are single
# composite spans here; per-condition leaf decomposition + per-era cause
# recode = C8.18 DO step 5 (the C8.18 DO3a/3b/4a composite-span precedent;
# soft-flag (gg)). RESERVED_<n> = unenumerated reserved gap-fill (the
# 1995-2002 R1/RESERVED1 precedent; gaps explicit, never silently dropped
# — §2 fail-closed); FILLER_<n> = DETAIL-enumerated filler (suffix = the
# unique-name SMOKE invariant). Positions are 1-based inclusive.
#
# Sources:
#   - LinkCO03Guide.pdf p17 (file char: Den US 783 / Num US 1142 / Unl US
#     1142), pp20-55 ("...denominator-plus..." DETAIL locs 1-783; p55
#     divider "Here ends the denominator-plus file."), pp55-72
#     ("mortality section of the numerator (linked) file" DETAIL locs
#     784-1142). pp18-19 element-span SUMMARY = NOT trusted (L13-ext).
#     Captured state-on-disk in PRE_FLIGHT_LOG.md 2026-05-18T20:30:00Z
#     SMOKE Tier 0 + value-distribution-verified first-run-clean on real
#     DEFLATE64 LinkCO03US.zip data (7z e -so stream).
# ==========================================================================

# --- 2003 cohort: 783-byte Denominator-PLUS, birth-cert section ---
# Locs 1-750 (REVISION/IDNUMBER + Birth Certificate). Identical in the
# den-plus AND the numerator's natality section (LinkCO03Guide pp20-55).
LINKED_BIRTH_2003_FIELDS: list[tuple[str, int, int]] = [
    ("FILLER_1", 1, 6),
    ("REVISION", 7, 7),     # Birth-cert revision (S=1989 unrevised / A=2003 revised)
    ("FILLER_8", 8, 8),
    ("LATEREC", 9, 9),      # Late record flag
    ("IDNUMBER", 10, 14),   # Infant death number (num<->den-plus join key)
    ("DOB_YY", 15, 18),     # Birth year (== 2003 for the 2003 cohort)
    ("DOB_MM", 19, 20),     # Birth month (01-12)
    ("FILLER_21", 21, 28),
    ("DOB_WK", 29, 29),     # Day of week of birth
    ("OSTATE", 30, 31),     # Occurrence FIPS state
    ("XOSTATE", 32, 33),
    ("FILLER_34", 34, 36),
    ("OCNTYFIPS", 37, 39),
    ("OCNTYPOP", 40, 40),
    ("FILLER_41", 41, 41),
    ("UBFACIL", 42, 42),
    ("FILLER_43", 43, 58),
    ("BFACIL3", 59, 59),
    ("FILLER_60", 60, 86),
    ("RESERVED_87", 87, 88),
    ("MAGER41", 89, 90),    # Age of mother recode 41
    ("MAGER14", 91, 92),    # Age of mother recode 14
    ("MAGER9", 93, 93),     # Age of mother recode 9
    ("FILLER_94", 94, 95),
    ("UMBSTATE", 96, 97),
    ("FILLER_98", 98, 99),
    ("RESERVED_100", 100, 100),
    ("FILLER_101", 101, 106),
    ("XMRSTATE", 107, 108),
    ("MRSTATEFIPS", 109, 110),
    ("FILLER_111", 111, 113),
    ("MRCNTYFIPS", 114, 116),
    ("FILLER_117", 117, 119),
    ("MRCITYFIPS", 120, 124),
    ("CMSA", 125, 126),
    ("MSA", 127, 130),
    ("MSA_POP", 131, 131),
    ("RCNTY_POP", 132, 132),
    ("RCITY_POP", 133, 133),
    ("FILLER_134", 134, 134),
    ("METRORES", 135, 135),
    ("FILLER_136", 136, 136),
    ("RECTYPE", 137, 137),
    ("RESTATUS", 138, 138),
    ("MBRACE", 139, 140),   # Bridged race of mother
    ("MRACE", 141, 142),    # Race of mother (detail)
    ("MRACEREC", 143, 143), # Race of mother recode
    ("MRACEIMP", 144, 144),
    ("FILLER_145", 145, 147),
    ("UMHISP", 148, 148),
    ("MRACEHISP", 149, 149),
    ("FILLER_150", 150, 152),
    ("MAR", 153, 153),      # Marital status of mother
    ("MAR_IMP", 154, 154),
    ("MEDUC", 155, 155),    # Education of mother
    ("UMEDUC", 156, 157),   # Education of mother (2003-rev)
    ("MEDUC_REC", 158, 158),
    ("FILLER_159", 159, 174),
    ("FAGERPT_FLG", 175, 175),
    ("FAGERPT", 176, 177),
    ("FILLER_178", 178, 183),
    ("UFAGECOMB", 184, 185),
    ("FAGEREC11", 186, 187),
    ("FBRACE", 188, 189),
    ("FILLER_190", 190, 190),
    ("FRACEREC", 191, 191),
    ("FILLER_192", 192, 194),
    ("UFHISP", 195, 195),
    ("FRACEHISP", 196, 196),
    ("FILLER_197", 197, 198),
    ("FRACE", 199, 200),
    ("FILLER_201", 201, 203),
    ("PRIORLIVE", 204, 205),
    ("PRIORDEAD", 206, 207),
    ("PRIORTERM", 208, 209),
    ("LBO", 210, 211),
    ("LBO_REC", 212, 212),
    ("FILLER_213", 213, 214),
    ("TBO", 215, 216),
    ("TBO_REC", 217, 217),
    ("FILLER_218", 218, 219),
    ("DLLB_MM", 220, 221),
    ("DLLB_YY", 222, 225),
    ("FILLER_226", 226, 244),
    ("PRECARE", 245, 246),  # Month prenatal care began
    ("PRECARE_REC", 247, 247),
    ("FILLER_248", 248, 255),
    ("MPCB", 256, 257),
    ("MPCB_REC6", 258, 258),
    ("MPCB_REC5", 259, 259),
    ("FILLER_260", 260, 269),
    ("UPREVIS", 270, 271),  # Number of prenatal visits
    ("PREVIS_REC", 272, 273),
    ("FILLER_274", 274, 275),
    ("WTGAIN", 276, 277),   # Weight gain during pregnancy
    ("WTGAIN_REC", 278, 278),
    ("FILLER_279", 279, 283),
    ("CIG_1", 284, 285),
    ("CIG_2", 286, 287),
    ("CIG_3", 288, 289),
    ("TOBUSE", 290, 290),
    ("CIGS", 291, 292),     # Cigarettes (recode)
    ("CIG_REC6", 293, 293),
    ("CIG_REC", 294, 294),
    ("ALCOHOL", 295, 295),  # Alcohol use
    ("DRINKS", 296, 297),
    ("DRINKS_REC", 298, 298),
    ("FILLER_299", 299, 327),
    ("MEDRISK", 328, 344),  # Medical risk factors (composite; per-condition leaves DO5; gg)
    ("FILLER_345", 345, 354),
    ("OBSTETRC", 355, 361), # Obstetric procedures (composite; leaves DO5; gg)
    ("FILLER_362", 362, 373),
    ("LABOR", 374, 389),    # Complications of labor/delivery (composite; leaves DO5; gg)
    ("FILLER_390", 390, 394),
    ("DELMETH", 395, 401),  # Method of delivery (composite; UME_*+DMETH_REC; leaves DO5; gg)
    ("FILLER_402", 402, 407),
    ("ATTEND", 408, 408),   # Attendant at birth
    ("FILLER_409", 409, 414),
    ("APGAR5", 415, 416),   # Five-minute Apgar score
    ("APGAR5R", 417, 417),  # Apgar recode
    ("FILLER_418", 418, 422),
    ("DPLURAL", 423, 423),  # Plurality
    ("FILLER_424", 424, 424),
    ("IMP_PLUR", 425, 425), # Plurality imputation flag
    ("FILLER_426", 426, 435),
    ("SEX", 436, 436),      # Sex of infant (1 M / 2 F)
    ("IMP_SEX", 437, 437),  # Sex imputation flag
    ("DLMP_MM", 438, 439),
    ("DLMP_DD", 440, 441),
    ("DLMP_YY", 442, 445),
    ("ESTGEST", 446, 447),  # Obstetric estimate of gestation
    ("FILLER_448", 448, 450),
    ("COMBGEST", 451, 452), # Combined gestation - detail weeks
    ("GESTREC10", 453, 454),# Gestation recode 10
    ("GESTREC3", 455, 455), # Gestation recode 3
    ("OBGEST_FLG", 456, 456),
    ("GEST_IMP", 457, 457),
    ("FILLER_458", 458, 466),
    ("DBWT", 467, 470),     # Birth weight detail in grams
    ("BWTR14", 471, 472),   # Birth weight recode 14
    ("BWTR4", 473, 473),    # Birth weight recode 4
    ("FILLER_474", 474, 474),
    ("BWTIMP", 475, 475),
    ("FILLER_476", 476, 482),
    ("NEWBORN", 483, 491),  # Abnormal conditions of the newborn (composite; leaves DO5; gg)
    ("FILLER_492", 492, 503),
    ("CONGENIT", 504, 525), # Congenital anomalies (composite; leaves DO5; gg)
    ("FILLER_526", 526, 568),
    ("F_MORIGIN", 569, 569),
    ("F_FORIGIN", 570, 570),
    ("F_MEDUC", 571, 571),
    ("FILLER_572", 572, 572),
    ("F_CLINEST", 573, 573),
    ("F_APGAR5", 574, 574),
    ("F_TOBACO", 575, 575),
    ("RESERVED_576", 576, 646),
    ("F_MED", 647, 647),
    ("F_WTGAIN", 648, 648),
    ("F_ALCOL", 649, 649),
    ("F_API", 650, 650),
    ("RESERVED_651", 651, 666),
    ("F_TOBAC", 667, 667),
    ("F_MPCB", 668, 668),
    ("F_MPCB_U", 669, 669),
    ("FILLER_670", 670, 682),
    ("MRACE1E", 683, 685),
    ("MRACE2E", 686, 688),
    ("MRACE3E", 689, 691),
    ("MRACE4E", 692, 694),
    ("MRACE5E", 695, 697),
    ("MRACE6E", 698, 700),
    ("MRACE7E", 701, 703),
    ("MRACE8E", 704, 706),
    ("RESERVED_707", 707, 717),
    ("FRACE1E", 718, 720),
    ("FRACE2E", 721, 723),
    ("FRACE3E", 724, 726),
    ("FRACE4E", 727, 729),
    ("FRACE5E", 730, 732),
    ("FRACE6E", 733, 735),
    ("FRACE7E", 736, 738),
    ("FRACE8E", 739, 741),
    ("RESERVED_742", 742, 750),
]

# --- 2003 cohort: Denominator-PLUS appended death "plus" + RECWT ---
# Locs 751-783. Present on BOTH num + den-plus; den-plus ends @783
# (RECWT@776-783). Analogous to LINKED_DEATH_1995_2002 / _2005_2013.
LINKED_DEATH_2003_FIELDS: list[tuple[str, int, int]] = [
    ("MATCHS", 751, 751),   # Match status (den-plus {1,2}; numerator {1} linked deaths)
    ("RESERVED_752", 752, 754),
    ("AGED", 755, 757),     # Age at death in days (000-366)
    ("AGER5", 758, 758),    # Infant age recode 5
    ("AGER22", 759, 760),   # Infant age recode 22
    ("MANNER", 761, 761),   # Manner of death
    ("DISPO", 762, 762),    # Method of disposition
    ("AUTOPSY", 763, 763),  # Autopsy
    ("FILLER_764", 764, 764),
    ("PLACE", 765, 765),    # Place of injury
    ("RESERVED_766", 766, 766),
    ("UCOD", 767, 770),     # Underlying cause of death - ICD-10 (2003 cohort all ICD-10)
    ("RESERVED_771", 771, 771),
    ("UCODR130", 772, 774), # 130 infant cause recode (ICD-10; DO5; gg)
    ("RESERVED_775", 775, 775),
    ("RECWT", 776, 783),    # Record weight (1.XXXXXX; den-plus ENDS @783)
]

LINKED_DENOMPLUS_RECLEN_2003 = 783

# --- 2003 cohort numerator: mortality section (locs 784-1142) ---
# (Birth section 1-750 REUSE LINKED_BIRTH_2003_FIELDS; death "plus"
#  751-783 REUSE LINKED_DEATH_2003_FIELDS.) 784-1142 = numerator-only
# mortality (multiple-cause ENTITY/RECORD + death geo/date). ICD-10
# throughout (2003 cohort). The prior "1259" assumption was FALSIFIED;
# numerator = 1142 (guide p17 + byte-exact zip-member arithmetic).
LINKED_NUM_DEATH_2003_FIELDS: list[tuple[str, int, int]] = [
    ("FILLER_784", 784, 785),
    ("EANUM", 786, 787),    # Number of entity-axis conditions (00-20)
    ("ENTITY", 788, 927),   # Entity-axis conditions (20 x 7-byte; composite; leaves DO5; gg)
    ("FILLER_928", 928, 929),
    ("RANUM", 930, 931),    # Number of record-axis conditions (00-20)
    ("RECORD", 932, 1031),  # Record-axis conditions (20 x 5-byte; composite; leaves DO5; gg)
    ("FILLER_1032", 1032, 1033),
    ("RESERVED_1034", 1034, 1044),
    ("DRCNTRY", 1045, 1046),# Country of residence - death
    ("RESERVED_1047", 1047, 1064),
    ("CNTRSPPD", 1065, 1065),# Place of death and decedent status
    ("RESERVED_1066", 1066, 1068),
    ("HOSPD", 1069, 1069),  # Hospital and patient status
    ("WEEKDAYD", 1070, 1070),# Day of week of death
    ("DTHYR", 1071, 1074),  # Year of death (cohort .. cohort+1)
    ("FILLER_1075", 1075, 1140),
    ("DTHMON", 1141, 1142), # Month of death (01-12; numerator ENDS @1142)
]

LINKED_NUM_RECLEN_2003 = 1142

# ==========================================================================
# C8.18 DO step 4c — cohort 2004 linked layout (900-byte Denominator-PLUS
# + 1259-byte numerator; 2003-revision transition continued).
#
# 2004 is the second year of the 2003-revision dual-certificate transition.
# REVISION@7 flags the certificate revision per record (S=1989 version
# unrevised / A=2003 version revised); the byte LAYOUT is one fixed-width
# record regardless (the "Vers*" column flags which revision populates a
# field, not a layout shift). 2004 is the cohort-linked birth year so all
# infant deaths are ICD-10 (deaths occur 2004-2005).
#
# Reconstructed byte-exact FRESH from the LinkCO04Guide.pdf DETAIL
# "Position/Len/Field" code-outline (pp21-60; the L13-extension governing
# precedent — the pp18-19 "Linked 2004 Cohort Selected Data Elements and
# Locations" element-span SUMMARY is composite + NOT trusted, used only as
# an independent cross-check) and value-distribution-verified on real
# DEFLATE LinkCO04US.zip data FIRST-RUN-CLEAN (n=500 den-plus + numerator;
# FAILS: NONE).
#
# TWO L13-extension findings resolved at the Convention-3 snapshot BEFORE
# any field_specs.py mutation (both were non-binding RECEIPTS/C8.18_step4b
# forward-looking-note extrapolations/hypotheses explicitly flagged for
# value-verification; real data + guide p18 + zip-member arithmetic are
# authoritative; same class as the 4b 1259->1142 catch):
#   * "2004 = 900/1142" extrapolation FALSIFIED -> numerator = 1259
#     (guide p18: Num US reclen 1259 / count 27,763 ;
#      VS04LKBC.USNUMPUB 35,009,143 / (1259+2 CRLF) = 27,763 byte-exact ;
#      den VS04LKBC.DUSDENOM 3,715,298,312 / (900+2) = 4,118,956).
#   * "2004 den-plus == LINKED_BIRTH_2005_2013" HYPOTHESIS FALSIFIED ->
#     2004 birth is the 2003-rev *cohort* layout (FILLER@1-6 + REVISION@7
#     + IDNUMBER@10-14); LINKED_BIRTH_2003 value-verifies byte-exact on
#     real 2004 den-plus only for locs 1-575, then DIVERGES (2004 carries
#     more 2003-rev F_* edit flags; MRACE1E@800 vs 2003's @683).
#   * LinkCO04US.zip = DEFLATE (stdlib zipfile; NOT DEFLATE64 like 2003 —
#     no special tooling for 2004).
#
# Composite-span convention (soft-flag (gg); per-condition leaf
# decomposition + per-era cause recode = C8.18 DO step 5/6; the 2003 4b
# precedent): MEDRISK@328-344 OBSTETRC@355-361 LABOR@374-389
# DELMETH@395-401 NEWBORN@483-491 CONGENIT@504-525 (birth) ;
# ENTITY@905-1044 (20x7) RECORD@1049-1148 (20x5) (numerator). Cleanly
# DETAIL-enumerated F_* edit scalars kept individually. FILLER_<n> =
# DETAIL-enumerated filler ; RESERVED_<n> = unenumerated synthesized
# gap-fill (the 2003 4b provenance-distinction; gaps explicit, never
# silently dropped — §2 fail-closed). Field names are NCHS-cohort-guide-
# traceable raw names (IDNUMBER@10-14 = the num<->den-plus join key, named
# for sibling-2003 + p18-summary consistency though the DETAIL token is
# "SEQNUM"; MAGER@89-90 = 2003-sibling MAGER41; BRTHWGT@467-470 =
# 2003-sibling DBWT — positions identical + value-verified). Positions
# 1-based inclusive.
#
# Sources:
#   - LinkCO04Guide.pdf p18 (file char: Den US 900 / Num US 1259 / Unl US
#     1259), pp21-57 (denominator-plus DETAIL locs 1-900; p57 divider
#     "Here ends the denominator-plus file."), pp57-60 (numerator-only
#     mortality DETAIL locs 901-1259). pp18-19 element-span SUMMARY =
#     NOT trusted (L13-ext). Captured state-on-disk in PRE_FLIGHT_LOG.md
#     2026-05-18T23:00:00Z SMOKE Tier 0 + /tmp/c8_18_s4c/ builder.
# ==========================================================================

# --- 2004 cohort: 900-byte Denominator-PLUS, birth-cert section ---
# Locs 1-867. Identical in the den-plus AND the numerator's natality
# section (LinkCO04Guide pp21-57). 1-575 structurally == LINKED_BIRTH_2003
# (value-verified on real 2004 data); 576-867 reconstructed from the 2004
# DETAIL (the 2004-specific 2003-rev F_* edit-flag region + relocated
# MRACE1E@800-823 / FRACE1E@835-858).
LINKED_BIRTH_2004_FIELDS: list[tuple[str, int, int]] = [
    ("FILLER_1", 1, 6),
    ("REVISION", 7, 7),     # Birth-cert revision (S=1989 unrevised / A=2003 revised)
    ("FILLER_8", 8, 8),
    ("LATEREC", 9, 9),      # Late record flag
    ("IDNUMBER", 10, 14),   # Infant death number (num<->den-plus join key; DETAIL "SEQNUM")
    ("DOB_YY", 15, 18),     # Birth year (== 2004 for the 2004 cohort)
    ("DOB_MM", 19, 20),     # Birth month (01-12)
    ("FILLER_21", 21, 28),
    ("DOB_WK", 29, 29),     # Day of week of birth
    ("OSTATE", 30, 31),     # Occurrence FIPS state
    ("XOSTATE", 32, 33),
    ("FILLER_34", 34, 36),
    ("OCNTYFIPS", 37, 39),
    ("OCNTYPOP", 40, 40),
    ("FILLER_41", 41, 41),
    ("UBFACIL", 42, 42),
    ("FILLER_43", 43, 58),
    ("BFACIL3", 59, 59),
    ("RESERVED_60", 60, 88),
    ("MAGER", 89, 90),      # Age of mother (2003-sibling MAGER41; same pos)
    ("MAGER14", 91, 92),    # Age of mother recode 14
    ("MAGER9", 93, 93),     # Age of mother recode 9
    ("FILLER_94", 94, 95),
    ("UMBSTATE", 96, 97),
    ("FILLER_98", 98, 99),
    ("MBSTATER3", 100, 100),
    ("FILLER_101", 101, 106),
    ("XMRSTATE", 107, 108),
    ("MRSTATEFIPS", 109, 110),
    ("FILLER_111", 111, 113),
    ("MRCNTYFIPS", 114, 116),
    ("FILLER_117", 117, 119),
    ("MRCITYFIPS", 120, 124),
    ("FILLER_125", 125, 131),
    ("RCNTY_POP", 132, 132),
    ("RCITY_POP", 133, 133),
    ("CITYLIM", 134, 134),
    ("METRORES", 135, 135),
    ("FILLER_136", 136, 136),
    ("RECTYPE", 137, 137),
    ("RESTATUS", 138, 138),
    ("MBRACE", 139, 140),   # Bridged race of mother
    ("MRACE", 141, 142),    # Race of mother (detail)
    ("MRACEREC", 143, 143), # Race of mother recode
    ("MRACEIMP", 144, 144),
    ("FILLER_145", 145, 147),
    ("UMHISP", 148, 148),
    ("MRACEHISP", 149, 149),
    ("FILLER_150", 150, 152),
    ("MAR", 153, 153),      # Marital status of mother
    ("MAR_IMP", 154, 154),
    ("MEDUC", 155, 155),    # Education of mother
    ("UMEDUC", 156, 157),   # Education of mother (2003-rev)
    ("MEDUC_REC", 158, 158),
    ("FILLER_159", 159, 174),
    ("FAGERPT_FLG", 175, 175),
    ("FAGERPT", 176, 177),
    ("FILLER_178", 178, 181),
    ("FAGECOMB", 182, 183),
    ("UFAGECOMB", 184, 185),
    ("FAGEREC11", 186, 187),
    ("FBRACE", 188, 189),
    ("FILLER_190", 190, 190),
    ("FRACEREC", 191, 191),
    ("FILLER_192", 192, 194),
    ("UFHISP", 195, 195),
    ("FRACEHISP", 196, 196),
    ("FILLER_197", 197, 198),
    ("UFRACE", 199, 200),
    ("FILLER_201", 201, 203),
    ("PRIORLIVE", 204, 205),
    ("PRIORDEAD", 206, 207),
    ("PRIORTERM", 208, 209),
    ("LBO", 210, 211),
    ("LBO_REC", 212, 212),
    ("FILLER_213", 213, 214),
    ("TBO", 215, 216),
    ("TBO_REC", 217, 217),
    ("FILLER_218", 218, 244),
    ("PRECARE", 245, 246),  # Month prenatal care began
    ("PRECARE_REC", 247, 247),
    ("FILLER_248", 248, 255),
    ("MPCB", 256, 257),
    ("MPCB_REC6", 258, 258),
    ("MPCB_REC5", 259, 259),
    ("FILLER_260", 260, 269),
    ("UPREVIS", 270, 271),  # Number of prenatal visits
    ("PREVIS_REC", 272, 273),
    ("FILLER_274", 274, 274),
    ("APNCU", 275, 275),
    ("WTGAIN", 276, 277),   # Weight gain during pregnancy
    ("WTGAIN_REC", 278, 278),
    ("U_APNCU", 279, 279),
    ("DFPC_IMP", 280, 280),
    ("FILLER_281", 281, 283),
    ("CIG_1", 284, 285),
    ("CIG_2", 286, 287),
    ("CIG_3", 288, 289),
    ("TOBUSE", 290, 290),
    ("CIGS", 291, 292),     # Cigarettes (recode)
    ("UCIG_REC6", 293, 293),
    ("CIG_REC", 294, 294),
    ("ALCOHOL", 295, 295),  # Alcohol use
    ("DRINKS", 296, 297),
    ("DRINKS_REC", 298, 298),
    ("FILLER_299", 299, 327),
    ("MEDRISK", 328, 344),  # Medical risk factors (composite; URF_* leaves DO5; gg)
    ("FILLER_345", 345, 354),
    ("OBSTETRC", 355, 361), # Obstetric procedures (composite; UOP_* leaves DO5; gg)
    ("FILLER_362", 362, 373),
    ("LABOR", 374, 389),    # Complications of labor/delivery (composite; ULD_* DO5; gg)
    ("FILLER_390", 390, 394),
    ("DELMETH", 395, 401),  # Method of delivery (composite; UME_*+DMETH_REC; DO5; gg)
    ("FILLER_402", 402, 407),
    ("ATTEND", 408, 408),   # Attendant at birth
    ("FILLER_409", 409, 414),
    ("APGAR5", 415, 416),   # Five-minute Apgar score
    ("APGAR5R", 417, 417),  # Apgar recode
    ("FILLER_418", 418, 422),
    ("DPLURAL", 423, 423),  # Plurality
    ("FILLER_424", 424, 424),
    ("IMP_PLUR", 425, 425), # Plurality imputation flag
    ("FILLER_426", 426, 435),
    ("SEX", 436, 436),      # Sex of infant
    ("IMP_SEX", 437, 437),  # Sex imputation flag
    ("DLMP_MM", 438, 439),
    ("DLMP_DD", 440, 441),
    ("DLMP_YY", 442, 445),
    ("ESTGEST", 446, 447),  # Obstetric estimate of gestation
    ("FILLER_448", 448, 450),
    ("COMBGEST", 451, 452), # Combined gestation - detail weeks
    ("GESTREC10", 453, 454),# Gestation recode 10
    ("GESTREC3", 455, 455), # Gestation recode 3
    ("OBGEST_FLG", 456, 456),
    ("GEST_IMP", 457, 457),
    ("FILLER_458", 458, 466),
    ("BRTHWGT", 467, 470),  # Birth weight in grams (2003-sibling DBWT; same pos)
    ("BWTR12", 471, 472),   # Birth weight recode 12
    ("BWTR4", 473, 473),    # Birth weight recode 4
    ("FILLER_474", 474, 474),
    ("BWTIMP", 475, 475),
    ("FILLER_476", 476, 482),
    ("NEWBORN", 483, 491),  # Abnormal conditions of the newborn (composite; UAB_* DO5; gg)
    ("FILLER_492", 492, 503),
    ("CONGENIT", 504, 525), # Congenital anomalies (composite; UCA_* leaves DO5; gg)
    ("FILLER_526", 526, 568),
    ("F_MORIGIN", 569, 569),
    ("F_FORIGIN", 570, 570),
    ("F_MEDUC", 571, 571),
    ("FILLER_572", 572, 572),
    ("F_CLINEST", 573, 573),
    ("F_APGAR5", 574, 574),
    ("F_TOBACO", 575, 575),
    ("RESERVED_576", 576, 646),
    ("F_MED", 647, 647),
    ("F_WTGAIN", 648, 648),
    ("F_ALCOL", 649, 649),
    ("F_API", 650, 650),
    ("RESERVED_651", 651, 666),
    ("F_TOBAC", 667, 667),
    ("F_MPCB", 668, 668),
    ("F_MPCB_U", 669, 669),
    ("RESERVED_670", 670, 682),
    ("F_URF_LUNG", 683, 683),
    ("RESERVED_684", 684, 686),
    ("F_URF_HEMO", 687, 687),
    ("RESERVED_688", 688, 693),
    ("F_URF_RENAL", 694, 694),
    ("F_URF_RH", 695, 695),
    ("RESERVED_696", 696, 722),
    ("F_ULD_CORD", 723, 723),
    ("RESERVED_724", 724, 726),
    ("FILLER_727", 727, 729),
    ("F_U_VAGINAL", 730, 730),
    ("F_U_VBAC", 731, 731),
    ("F_U_PRIMAC", 732, 732),
    ("F_U_REPEAC", 733, 733),
    ("F_U_FORCEP", 734, 734),
    ("F_U_VACUUM", 735, 735),
    ("RESERVED_736", 736, 746),
    ("F_UAB_NSEIZ", 747, 747),
    ("RESERVED_748", 748, 751),
    ("F_UCA_ANEN", 752, 752),
    ("F_UCA_SPINA", 753, 753),
    ("RESERVED_754", 754, 767),
    ("F_UCA_CLUB", 768, 768),
    ("RESERVED_769", 769, 773),
    ("FILLER_774", 774, 799),
    ("MRACE1E", 800, 802),
    ("MRACE2E", 803, 805),
    ("MRACE3E", 806, 808),
    ("MRACE4E", 809, 811),
    ("MRACE5E", 812, 814),
    ("MRACE6E", 815, 817),
    ("MRACE7E", 818, 820),
    ("MRACE8E", 821, 823),
    ("RESERVED_824", 824, 834),
    ("FRACE1E", 835, 837),
    ("FRACE2E", 838, 840),
    ("FRACE3E", 841, 843),
    ("FRACE4E", 844, 846),
    ("FRACE5E", 847, 849),
    ("FRACE6E", 850, 852),
    ("FRACE7E", 853, 855),
    ("FRACE8E", 856, 858),
    ("FILLER_859", 859, 867),
]

# --- 2004 cohort: Denominator-PLUS appended death "plus" + RECWT ---
# Locs 868-900. Present on BOTH num + den-plus; den-plus ends @900
# (RECWT@893-900). == LINKED_DEATH_2005_2013 model (FLGND@868 /
# AGED@872-874 / RECWT@893-900; DETAIL + real-data verified).
LINKED_DEATH_2004_FIELDS: list[tuple[str, int, int]] = [
    ("FLGND", 868, 868),    # Match status (den-plus {1,2}; numerator {1} linked deaths)
    ("RESERVED_869", 869, 871),
    ("AGED", 872, 874),     # Age at death in days (000-366)
    ("AGER5", 875, 875),    # Infant age recode 5
    ("AGER22", 876, 877),   # Infant age recode 22
    ("MANNER", 878, 878),   # Manner of death
    ("DISPO", 879, 879),    # Method of disposition
    ("AUTOPSY", 880, 880),  # Autopsy
    ("FILLER_881", 881, 881),
    ("PLACE", 882, 882),    # Place of injury
    ("RESERVED_883", 883, 883),
    ("UCOD", 884, 887),     # Underlying cause of death - ICD-10 (2004 cohort all ICD-10)
    ("RESERVED_888", 888, 888),
    ("UCODR130", 889, 891), # 130 infant cause recode (ICD-10; DO5; gg)
    ("RESERVED_892", 892, 892),
    ("RECWT", 893, 900),    # Record weight (1.XXXXXX; den-plus ENDS @900)
]

LINKED_DENOMPLUS_RECLEN_2004 = 900

# --- 2004 cohort numerator: mortality section (locs 901-1259) ---
# (Birth section 1-867 REUSE LINKED_BIRTH_2004_FIELDS; death "plus"
#  868-900 REUSE LINKED_DEATH_2004_FIELDS.) 901-1259 = numerator-only
# mortality (multiple-cause ENTITY/RECORD + death geo/date). ICD-10
# throughout (2004 cohort -> deaths 2004-2005). numerator = 1259
# (NOT 1142 — the prior receipt-note extrapolation was FALSIFIED;
# guide p18 + byte-exact zip-member arithmetic).
LINKED_NUM_DEATH_2004_FIELDS: list[tuple[str, int, int]] = [
    ("FILLER_901", 901, 902),
    ("EANUM", 903, 904),    # Number of entity-axis conditions (00-20)
    ("ENTITY", 905, 1044),  # Entity-axis conditions (20 x 7-byte; composite; DO5; gg)
    ("FILLER_1045", 1045, 1046),
    ("RANUM", 1047, 1048),  # Number of record-axis conditions (00-20)
    ("RECORD", 1049, 1148), # Record-axis conditions (20 x 5-byte; composite; DO5; gg)
    ("FILLER_1149", 1149, 1185),
    ("HOSPD", 1186, 1186),  # Hospital and patient status
    ("WEEKDAYD", 1187, 1187),# Day of week of death
    ("DTHYR", 1188, 1191),  # Year of death (cohort .. cohort+1)
    ("FILLER_1192", 1192, 1257),
    ("DOD_MM", 1258, 1259), # Month of death (01-12; numerator ENDS @1259)
]

LINKED_NUM_RECLEN_2004 = 1259
