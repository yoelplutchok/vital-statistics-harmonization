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
