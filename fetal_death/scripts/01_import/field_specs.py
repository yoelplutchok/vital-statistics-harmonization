"""
Field specifications for NCHS fetal death fixed-width files.

Each spec is a list of (field_name, start_pos, end_pos) tuples where
positions are 1-based inclusive (matching NCHS documentation).

Eras:
  - 1982-1988: V3b — 1978-revision uniform layout (200 data bytes)
  - 1989-2002: V2.0 + V3a — single uniform 1989-revision layout (360 data bytes)
  - 2003: V2.1 transition — 1350 data bytes; A/S per-record revision overlay
  - 2004: V2.1 transition — 1500 data bytes (= 2003 layout + 150-byte trailing pad)
  - 2005-2013: V1 — non-COD layout, varying record lengths
  - 2014-2017: V1 — COD layout available (use COD variant)
  - 2018-2022: V1 — COD-only layout

Sources: NCHS fetal death user guide PDFs for each year.
"""

# --- Record lengths (bytes per line excluding newline) ---

RECORD_LEN_1978 = 200    # 1982-1988 V3b uniform 1978-revision layout
RECORD_LEN_1992 = 360    # 1989-2002 uniform 1989-revision layout (V3a extended 1989-1991)
RECORD_LEN_2003 = 1350   # 2003 transition (V2.1; 801 useful data + 549 trailing pad)
RECORD_LEN_2004 = 1500   # 2004 transition (V2.1; = 2003 + 150 trailing pad)
RECORD_LEN_2022 = 2651   # 2018-2022 COD-only
RECORD_LEN_2014 = 3050   # 2014-2017 COD variant
RECORD_LEN_2006 = 3350   # 2005-2006 (non-COD, dual revision layout, 801 data + 2549 filler)
RECORD_LEN_2007 = 801    # 2007 (non-COD, no trailing filler)
RECORD_LEN_2008 = 3338   # 2008-2013 (non-COD, 801 data + 2537 filler)


# --- 1982-1988 uniform layout (1978 revision, 200 data bytes per record) ---
# Raw files are 202 bytes/line (200 data + CR+LF) empirically verified
# 2026-05-12 across 1982/1983/1985/1988 first-record probes. Field positions
# are 1-based inclusive, relative to the 200-byte record.
#
# This is a STRUCTURALLY DIFFERENT layout from the 1989-revision (V2/V3a):
# different field names (e.g., AGE/RACE instead of MAGER/MRACE), different
# byte positions (e.g., DMAGE @ 81-82 here vs DMAGE @ 71-72 in V2; MRACE @ 86
# single-byte here vs MRACE @ 79-80 two-byte in V2), and different recodes
# (e.g., 1-digit MRACE 0-9 here vs 2-digit MRACE 01-99 in V2). Canonical
# layout CSV is metadata/record_layout_1982_1988.csv (87 rows, all 200
# bytes covered, no gaps/overlaps; verified at task7_v3b DO step 2).
#
# Page-4/5/6 cross-year diff across all 7 V3b years 2026-05-12 (PRE-FLIGHT
# 15:45Z): byte-identical field byte-positions in the "List of Data Elements"
# overview. Empirical anchor-field spot-check (1982/1983/1985/1988 raw zips
# 2026-05-12 DO step 2): DATAYEAR bytes 1-2 match filename year; TABFLAG/
# RECTYPE/RESTATUS in {1,2}; STATEOCC=01 (Alabama, alphabetical first).
#
# B3 maternal_race_bridged: V3b 1978-rev uses 1-digit MRACE codes 0-9
# (vs V2/V3a 2-digit). The harmonize.py B3 map extension required for V3b
# is documented in V3b_1982_1988_LAYOUT_DECISIONS.md at DO step 10.
#
# Source: 1985FetalUserGuide.pdf pages 8-26 (detail record layout),
# cross-checked against 1982 + 1988 user guides for byte-position uniformity.

FETAL_1982_1988_FIELDS: list[tuple[str, int, int]] = [
    # ========================
    # Record identification
    # ========================
    ("DATAYEAR",               1,    2),   # Last 2 digits of year (1978-rev); harmonize.py expands int(raw)+1900
    ("REPAREA",                3,    3),   # Reporting Area (NYC boroughs + Chicago; PUF caveat: do not use)
    # 4-9: CERTNUM (blank in PUF per user-guide p8)
    ("TABFLAG",               10,   10),   # Tabulation flag: 1=<20wk; 2=20wk+ (same coding as V2/V3a)
    ("RECTYPE",               11,   11),   # Record type: 1=Resident; 2=Nonresident
    ("RESTATUS",              12,   12),   # Residence status: 1/2/3/4 (4=Foreign)

    # ========================
    # Occurrence geography (FOCCUR umbrella 13-22 in 1978-rev)
    # ========================
    ("STATEOCC",              13,   14),   # NCHS State of occurrence (01-51)
    ("CNTYOCC",               15,   17),   # NCHS County of occurrence
    ("REGNOCC",               18,   18),   # Region of occurrence (1=NE; 2=NC; 3=S; 4=W)
    ("DIVOCC",                19,   19),   # Division of occurrence (1-9)
    ("STSDBOCC",              20,   20),   # State subcode of occurrence (1-9 within Division)
    ("STFETEXP",              21,   22),   # Expanded NCHS state of occurrence (NYC=34 split from NY=33)

    # ========================
    # Residence geography (FRESID umbrella 23-40)
    # ========================
    ("STATERES",              23,   24),   # NCHS State of residence (01-51 + foreign 52-59)
    ("CNTYRES",               25,   27),   # NCHS County of residence (222=Foreign)
    ("CITYRES",               28,   30),   # NCHS City of residence
    ("CITRSPOP",              31,   31),   # Population size of city of residence
    ("METRORES",              32,   32),   # Metro/Nonmetro county of residence
    ("REGNRES",               33,   33),   # Region of residence
    ("DIVRES",                34,   34),   # Division of residence
    ("STSUBRES",              35,   35),   # State subcode of residence
    ("STRESEXP",              36,   37),   # Expanded NCHS state of residence
    ("SMSARES",               38,   40),   # NCHS SMSA (000=Nonmetro; 001-305=SMSAs)

    # 41-46: FILLER (reserved)

    # ========================
    # LMP dates
    # ========================
    ("LMPMON",                47,   48),   # Month of LMP (01-12; 99=Not stated)
    ("LMPDAY",                49,   50),   # Day of LMP (01-31; 99=Not stated)
    ("LMPYR",                 51,   51),   # Year of LMP (1=current; 2=previous; 3=Not stated) — RELATIVE

    # ========================
    # Delivery date / place
    # ========================
    ("DELMON",                52,   53),   # Month of delivery
    ("DELDAY",                54,   55),   # Day of delivery (99=Not stated)
    ("PLDEL",                 56,   56),   # Place of delivery (1=Hospital; 2=Nonhospital; 3=Enroute; 9=NC)

    # 57: FILLER (reserved)

    # ========================
    # Prenatal care
    # ========================
    ("MONPRE",                58,   59),   # Month prenatal care began (00=None; 01-09; 99=NS)
    ("MPRE6",                 60,   60),   # MPCB recode 6
    ("NPREVIST",              61,   62),   # Total prenatal visits (00=None; 01-49; 99=NS)
    ("NPREV9",                63,   63),   # PNC visits recode 9 (V3b-specific 9-cat)

    # ========================
    # Fetus (sex/race/plurality)
    # ========================
    ("FSEX",                  64,   64),   # Sex (1=Male; 2=Female; 9=NS)
    ("RACEF",                 65,   65),   # Detail Race of fetus (1-digit 0-8 1978-rev scheme)
    ("RACEF3",                66,   66),   # Race recode 3 (fetus)
    ("RACEF2",                67,   67),   # Race recode 2 (fetus, V3b-specific)
    ("NUMDEL",                68,   68),   # Number at delivery (1=Single; 2=Twin; 3=Triplet+)

    # ========================
    # Birthweight
    # ========================
    ("DBIRWT",                69,   72),   # Detail in grams (0227-8165; 9999=NS)
    ("BIRWT14",               73,   74),   # Birthweight recode 14
    ("BIRWT3",                75,   75),   # Birthweight recode 3 (V3b-specific 3-cat)

    # ========================
    # Gestation (combined)
    # ========================
    ("DGESTAT",               76,   77),   # Detail gestation in weeks (combined; 01-52; 99=NS)
    ("GESTAT12",              78,   79),   # Gestation recode 12
    ("GESTAT5",               80,   80),   # Gestation recode 5

    # ========================
    # Mother (age/race/marital/education, 81-90 umbrella)
    # ========================
    ("DMAGE",                 81,   82),   # Detail age of mother (10-49 single year)
    ("MAGE12",                83,   84),   # Age of mother recode 12
    ("MAGE8",                 85,   85),   # Age of mother recode 8
    ("MRACE",                 86,   86),   # Detail race of mother (1-digit 0-9 1978-rev scheme)
    ("DMAR",                  87,   87),   # Marital status (1=Married; 2=Unmarried; 9=NS)
    ("DMEDUC",                88,   89),   # Detail education of mother (00; 01-08; 09-17; 99=NS)
    ("MEDUC6",                90,   90),   # Mother's education recode 6

    # ========================
    # Pregnancy history (91-106 umbrella)
    # ========================
    ("NLBNL",                 91,   92),   # Born alive, now living (00-50; 99=Unknown)
    ("NLBND",                 93,   94),   # Born alive, now dead
    ("NBD",                   95,   96),   # Born dead (fetal deaths) — V3b-specific
    ("NOTBEF20",              97,   98),   # Other terminations <20wk (00-50; 88=NA; 99=Unknown)
    ("NOTAFT20",              99,  100),   # Other terminations 20+wk
    ("DTOTORD",              101,  102),   # Detail total birth order (01-50; 99=Unknown)
    ("TOTORD9",              103,  103),   # Total birth order recode 9
    ("DLIVORD",              104,  105),   # Detail live birth order (00-50; 99=Unknown)
    ("LIVORD10",             106,  106),   # Live birth order recode 10 (V3b-specific 10-cat including 0=None)

    # ========================
    # Father (107-114 umbrella)
    # ========================
    ("DFAGE",                107,  108),   # Detail age of father (10-98; 99=NS)
    ("FAGE12",               109,  110),   # Age of father recode 12 (V3b 12-cat; V2 uses 11-cat FAGE11)
    ("FRACE",                111,  111),   # Detail race of father (1-digit 0-9)
    ("DFEDUC",               112,  113),   # Detail education of father
    ("FEDUC6",               114,  114),   # Father's education recode 6

    # ========================
    # Gestation estimates (separate from combined @ 76-80)
    # ========================
    ("CLINGEST",             115,  116),   # Physician's estimate of gestation
    ("COMPGEST",             117,  118),   # Computed gestation (V3b exposes separately; V2 combines)

    # ========================
    # Congenital malformation (umbrella flag only)
    # ========================
    ("CONGEN",               119,  119),   # 0=None reported; 1=Any reported (V3b has no 22-field breakdown like V2)

    # 120-122: FILLER (reserved)

    # ========================
    # Residence reporting flags (123-140)
    # Code: 0=Not reported by residence state; 1=Reported
    # ========================
    ("RF_GESTALL",           123,  123),   # All periods of gestation
    ("RF_MARBC",             124,  124),   # Marital status on Birth Certificate
    ("RF_EDUC",              125,  125),   # Education of parents (mother+father combined in V3b)
    ("RF_LMP",               126,  126),   # Date of LMP
    ("RF_MARFD",             127,  127),   # Marital status on Fetal Death Form
    ("RF_MONPNC",            128,  128),   # Month prenatal care began
    ("RF_NPNC",              129,  129),   # Number of prenatal visits
    ("RF_CLINGEST",          130,  130),   # Physician's estimate of gestation
    ("RF_CONGEN",            131,  131),   # Congenital malformations

    # 132-140: FILLER (reserved, 9 bytes)

    # ========================
    # Occurrence reporting flag
    # ========================
    ("OCC_GESTALL",          141,  141),   # All periods of gestation: occurrence flag

    # 142-186: FILLER (reserved, 45 bytes)

    # ========================
    # FIPS geographic codes (187-200)
    # ========================
    ("STOCCFIP",             187,  188),   # FIPS state of occurrence
    ("CNTOCFIP",             189,  191),   # FIPS county of occurrence
    ("STRESFIP",             192,  193),   # FIPS state of residence (00=Foreign)
    ("CNTRSFIP",             194,  196),   # FIPS county of residence (000=Foreign)
    ("SMSARFIP",             197,  200),   # FIPS SMSA of residence (0000=Nonmetro/Foreign; 0040-9340)
]


# --- 1989-2002 uniform layout (1989 revision, 360 data bytes per record) ---
# Raw files are 361 bytes/line (360 data + LF) or 362 bytes/line (360 data +
# CR+LF). Field positions are 1-based inclusive, relative to the 360-byte
# record.
#
# Decisions, OCR corrections, and gaps documented in
# docs/V2_1992_LAYOUT_DECISIONS.md and (for V3a) V3a_1989_1991_LAYOUT_DECISIONS.md.
# Canonical layout CSV is metadata/record_layout_1992.csv.
#
# All records are 1989-revision (the 2003 revision had not yet been issued).
# Cause-of-death (ICD-9) codes are NOT in the public-use file for this era;
# per V2 scope they are not harmonized (see project_v2_scope memory).
#
# Spot-checked on 2026-04-20 for 1992, 1995, 2000, 2002 (all 4 match). The
# remaining years 1993-1994, 1996-1999, 2001 are presumed uniform; AUDIT-PARSE-2
# must confirm each. V3a extension (2026-05-12): page 5-6 Data Elements lists
# in 1989/1990/1991 user guides match the 1992 user guide field-by-field; first-
# record DATAYEAR @ bytes 1-4 verified for each year; record-length 360 bytes
# verified empirically.
#
# Source: 1989FetalUserGuide.pdf / 1990FetalUserGuide.pdf / 1991FetalUserGuide.pdf
# (V3a) and 1992FetalUserGuide.pdf (V2.0; identical layout through 2002).

FETAL_1992_2002_FIELDS: list[tuple[str, int, int]] = [
    # ========================
    # Record identification
    # ========================
    ("DATAYEAR",        1,    4),   # Year of Delivery (1989-2002)
    ("TABFLAG",         5,    5),   # Tabulation flag: 1=<20wk; 2=20wk+
    ("RECTYPE",         6,    6),   # Record type: 1=Resident; 2=Nonresident
    ("RESTATUS",        7,    7),   # Residence status: 1/2/3/4 (4=Foreign)

    # ========================
    # Delivery place / attendant
    # ========================
    ("PLDEL",           8,    8),   # Place of delivery
    ("PLDEL2",          9,    9),   # Place of delivery recode
    ("FATTND",         10,   10),   # Attendant at delivery
    ("FATTNDR",        11,   11),   # Attendant recode (phys/midwife/other)

    # ========================
    # Occurrence geography (FOCCUR umbrella 12-27)
    # ========================
    ("REGNOCC",        12,   12),   # Region of occurrence (1-4)
    ("DIVOCC",         13,   13),   # Division of occurrence (1-9)
    ("STSDBOCC",       14,   14),   # State subcode of occurrence
    ("STFETEXP",       15,   16),   # Expanded state of occurrence (NYC separate)
    ("STATEFET",       17,   18),   # NCHS state of occurrence
    ("CNTYFET",        19,   21),   # NCHS county of occurrence (100K+ only)
    ("STOCCFIP",       22,   23),   # FIPS state of occurrence
    ("CNTOCFIP",       24,   26),   # FIPS county of occurrence
    ("CNTOCPOP",       27,   27),   # County of occurrence population size

    # ========================
    # Residence geography (FRESID umbrella 28-59)
    # ========================
    ("REGNRES",        28,   28),   # Region of residence
    ("DIVRES",         29,   29),   # Division of residence
    ("STSUBRES",       30,   30),   # State subcode of residence
    ("STRESEXP",       31,   32),   # Expanded state of residence
    ("STATERES",       33,   34),   # NCHS state of residence
    ("CNTYRES",        35,   37),   # NCHS county of residence
    ("CITYRES",        38,   40),   # NCHS city of residence (100K+ only)
    ("CITRSPOP",       41,   41),   # City of residence population size
    ("METRORES",       42,   42),   # Met/nonmet county of residence
    ("STRESFIP",       43,   44),   # FIPS state of residence
    ("CNTYRFIP",       45,   47),   # FIPS county of residence
    ("CMSA",           53,   54),   # FIPS CMSA of residence (gap at 48-52)
    ("SMSARFIP",       55,   58),   # FIPS PMSA/MSA of residence
    ("CNTRSPOP",       59,   59),   # County of residence population size

    # 60-68: FILLER (reserved)

    # ========================
    # Mother age
    # ========================
    ("MAGERFLG",       69,   69),   # Reported age used flag
    ("MAGEIMP",        70,   70),   # Age imputation flag
    ("DMAGE",          71,   72),   # Age (used in NCHS pubs)
    ("MAGE12",         73,   74),   # Age recode 12
    ("MAGE8",          75,   75),   # Age recode 8

    # ========================
    # Mother ethnicity / race / education / marital
    # ========================
    ("ORMOTH",         76,   76),   # Hispanic origin of mother (OCR: OI?MOTH)
    ("ORRACEM",        77,   77),   # Hispanic origin & race recode
    ("MRACEIMP",       78,   78),   # Race imputation flag
    ("MRACE",          79,   80),   # Race of mother (1992+ API codes 18-78)
    ("MRACE3",         81,   81),   # Race recode (OCR: ldItAcF13)
    ("DMEDUC",         82,   83),   # Education (OCR: 82-03)
    ("MEDUC6",         84,   84),   # Education recode
    # 85: FILLER (reserved)
    ("DMAR",           86,   86),   # Marital status (OCR: mu-m)
    ("DMAGERPT",       87,   88),   # Reported age of mother (raw)

    # 89-97: FILLER (reserved)

    # ========================
    # Pregnancy history
    # ========================
    ("NLBNL",          98,   99),   # Live births now living
    ("NLBND",         100,  101),   # Live births now dead
    ("NOTERM",        102,  103),   # Other terminations
    # 104: FILLER
    ("DLIVORD",       105,  106),   # Detail live birth order
    ("LIVORD9",       107,  107),   # Live birth order recode
    # 108: FILLER
    ("DTOTORD",       109,  110),   # Detail total birth order
    ("TOTORD9",       111,  111),   # Total birth order recode
    # 112: FILLER

    # ========================
    # Prenatal care
    # ========================
    ("MONPRE",        113,  114),   # Detail month prenatal care began
    ("MPRE6",         115,  115),   # MPCB recode 6
    ("MPRE5",         116,  116),   # MPCB recode 5
    ("NPREVIST",      117,  118),   # Total prenatal visits
    ("NPREV12",       119,  120),   # PNC visits recode

    # ========================
    # Dates — LMP (umbrella 121-128)
    # ========================
    ("LMPMON",        121,  122),   # Month of LMP
    ("LMPDAY",        123,  124),   # Day of LMP (OCR: LKPDAY)
    ("LMPYR",         125,  128),   # Year of LMP

    # ========================
    # Dates — Last live birth (umbrella 129-134)
    # ========================
    ("LLBMON",        129,  130),   # Month of last live birth
    ("LLBYR",         131,  134),   # Year of last live birth

    ("DISLLB",        135,  137),   # Interval since last live birth
    ("ISLLBIO",       138,  139),   # Interval recode

    # 140-159: FILLER (reserved, 20 bytes)

    # ========================
    # Father
    # ========================
    ("FAGERFLG",      160,  160),   # Reported age used flag
    ("DFAGE",         161,  162),   # Age of father
    ("FAGE11",        163,  164),   # Age recode 11
    ("ORFATH",        165,  165),   # Hispanic origin of father
    ("ORRACEF",       166,  166),   # Hispanic origin & race recode
    ("FRACE",         167,  168),   # Race of father
    ("FRACE4",        169,  169),   # Race recode 4
    ("DFEDUC",        170,  171),   # Education
    ("FEDUC6",        172,  172),   # Education recode
    ("DFAGERPT",      173,  174),   # Reported age of father (raw)

    # 175-183: FILLER

    # ========================
    # Delivery date / gestation / sex
    # ========================
    ("FDODMIMP",      184,  184),   # Month of delivery imputation flag
    # 185: FILLER (guide labels WA, text says Reserved)
    ("DELMON",        186,  187),   # Month of delivery
    # 188-189: FILLER (R4B)
    ("DELYR",         190,  193),   # Year of delivery
    ("WEEKDAY",       194,  194),   # Day of week
    ("GESTESTM",      195,  195),   # Clinical estimate used flag
    ("GESTIMP",       196,  196),   # Gestation imputation flag (OCR: GESTIM.P)
    ("DGESTAT",       197,  198),   # Gestation (used in NCHS pubs)
    ("GESTAT12",      199,  200),   # Gestation recode 12
    ("GESTAT5",       201,  201),   # Gestation recode 5
    ("FSEXIMP",       202,  202),   # Sex imputation flag (OCR: FSEX~)
    ("FSEX",          203,  203),   # Sex

    # ========================
    # Fetus — race / weight / plurality
    # ========================
    ("RACEF",         204,  205),   # Race of fetus
    ("FRACE3",        206,  206),   # Race recode
    ("DBIRWT",        207,  210),   # Weight at delivery (grams)
    ("BIRWT14",       211,  212),   # Weight recode 14
    ("BIRWT4",        213,  213),   # Weight recode 4
    ("PLURIMP",       214,  214),   # Plurality imputation flag
    ("DPLURAL",       215,  215),   # Plurality (OCR: DPLUR.AL)
    ("CLINGEST",      216,  217),   # Clinical estimate of gestation

    # 218-219: FILLER

    # ========================
    # Method of delivery (DEWTH umbrella 220-226)
    # ========================
    ("VAGINAL",       220,  220),   # Vaginal delivery
    ("VEAC",          221,  221),   # VBAC
    ("PRIMAC",        222,  222),   # Primary C-section
    ("REPEAC",        223,  223),   # Repeat C-section
    ("FORCEP",        224,  224),   # Forceps
    ("VACUUM",        225,  225),   # Vacuum
    ("HYSTER",        226,  226),   # Hysterotomy/Hysterectomy
    ("DELMETH6",      227,  227),   # Method of delivery recode (1992 OCR: DEmTH6; canonical name confirmed in 1998 & 2002 guides)

    # ========================
    # Medical risk factors (B5EDRISK umbrella 228-244)
    # ========================
    ("ANEMIA",        228,  228),
    ("CARDIAC",       229,  229),
    ("LUNG",          230,  230),
    ("DIABETES",      231,  231),
    ("HERPES",        232,  232),
    ("HYDRA",         233,  233),
    ("HEMO",          234,  234),
    ("CHYPER",        235,  235),   # Chronic hypertension
    ("PHYPER",        236,  236),   # Pregnancy-assoc hypertension
    ("ECLAMP",        237,  237),
    ("INCERVIX",      238,  238),
    ("PRE4000",       239,  239),   # Prev infant 4000+ g (OCR: PRE4 000)
    ("PRETERM",       240,  240),
    ("RENAL",         241,  241),
    ("RH",            242,  242),   # Rh sensitization (OCR: ~)
    ("UTERINE",       243,  243),
    ("OTHERMR",       244,  244),   # Other medical risk (OCR: OTHE~)

    # ========================
    # Other risks — tobacco, alcohol, weight gain (OTHERRSK 245-255)
    # ========================
    ("TOBACCO",       245,  245),
    ("CIGAR",         246,  247),
    ("CIGAR6",        248,  248),
    ("ALCOHOL",       249,  249),
    ("DRINK",         250,  251),
    ("DRINKS",        252,  252),
    ("WTGAIN",        253,  254),
    ("WTGAIN8",       255,  255),

    # ========================
    # Obstetric procedures (OBSTETRC umbrella 256-262)
    # ========================
    ("AMNIO",         256,  256),
    ("MONITOR",       257,  257),
    ("INDUCT",        258,  258),   # OCR pos mis-read as 250
    ("STIMULA",       259,  259),   # Stimulation of labor (1992 OCR: ST=A; canonical name confirmed in 1998 & 2002 guides)
    ("TOCOL",         260,  260),
    ("ULTRAS",        261,  261),
    ("OTHEROB",       262,  262),

    # ========================
    # Complications of labor (LABOR umbrella 263-278)
    # ========================
    ("FEBRILE",       263,  263),
    ("MECONIUM",      264,  264),   # OCR: WCONIUM
    ("RUPTURE",       265,  265),
    ("ABRUPTIO",      266,  266),
    ("PREPLACE",      267,  267),
    ("EXCEBLD",       268,  268),
    ("SEIZURE",       269,  269),
    ("PRECIP",        270,  270),
    ("PROLONG",       271,  271),
    ("DYSFUNC",       272,  272),
    ("BREECH",        273,  273),
    ("CEPHALO",       274,  274),
    ("CORD",          275,  275),
    ("ANESTHE",       276,  276),
    ("DISTRESS",      277,  277),
    ("OTHERLB",       278,  278),

    # ========================
    # Congenital anomalies (CONGENIT umbrella 279-300)
    # ========================
    ("ANEN",          279,  279),   # Anencephalus (1992 OCR: ~; canonical name confirmed in 1998 & 2002 guides)
    ("SPINA",         280,  280),
    ("HYDRO",         281,  281),
    ("MICROCE",       282,  282),
    ("NERVOUS",       283,  283),   # OCR: ~RVOUS
    ("HEART",         284,  284),
    ("CIRCUL",        285,  285),
    ("RECTAL",        286,  286),
    ("TRACHEO",       287,  287),   # OCR: T~CHEO
    ("OMPHALO",       288,  288),
    ("GASTRO",        289,  289),
    ("GENITAL",       290,  290),
    ("RENALAGE",      291,  291),
    ("UROGEN",        292,  292),
    ("CLEFTLP",       293,  293),
    ("ADACTYLY",      294,  294),
    ("CLUBFOOT",      295,  295),
    ("HERNIA",        296,  296),
    ("MUSCULO",       297,  297),
    ("DOWNS",         298,  298),
    ("CHROMO",        299,  299),
    ("OTHERCON",      300,  300),

    # 301-314: FILLER (R5A, reserved)

    # ========================
    # Residence reporting flags (FLRES umbrella 315-339)
    # Code: 0=Not reported by residence state; 1=Reported
    # ========================
    ("GESTALL",       315,  315),   # All gestations reported
    ("ORIGM",         316,  316),   # Origin of mother
    ("ORIGF",         317,  317),   # Origin of father
    ("EDUCM",         318,  318),   # Education of mother
    ("EDUCF",         319,  319),   # Education of father
    ("LLBF",          320,  320),   # Date of last live birth
    ("DMARF",         321,  321),   # Marital status
    ("DATELMP",       322,  322),   # Date of last menses
    ("PNCF",          323,  323),   # Month PNC began
    ("PNVF",          324,  324),   # Number of PNC visits
    ("GESTE",         325,  325),   # Clinical estimate of gestation
    ("DELMETRF",      326,  326),   # Reporting flag, method of delivery (1992 OCR: DHJ4ETRF; canonical name confirmed in 1998 & 2002 guides)
    ("MEDRSK",        327,  327),   # Medical risk factors
    ("TOBUSE",        328,  328),   # Tobacco use
    ("CIGARSF",       329,  329),   # Cigarettes
    ("ALCUSE",        330,  330),   # Alcohol use
    ("DRINKSF",       331,  331),   # Drinks
    ("WTGN",          332,  332),   # Weight gain
    ("OBSTRC",        333,  333),   # Obstetric procedures
    ("CLABOR",        334,  334),   # Complications of labor (OCR pos: 33=4)
    ("CONGAN",        335,  335),   # Congenital anomalies
    ("UCF",           336,  336),   # Underlying cause
    ("PLURALF",       337,  337),   # Plurality
    # 338-339: FILLER

    ("ALLGOCC",       340,  340),   # All-gestations occurrence reporting flag

    # 341-356: FILLER (reserved, 16 bytes)

    # ========================
    # NCHS MSA residence
    # ========================
    ("S14SARES",      357,  359),   # NCHS PMSA/MSA (distinct from FIPS at 55-58)
    ("POPSMAS",       360,  360),   # MSA population size
]


# --- 2005-2006 non-COD layout (documented record length 801) ---
# PDF says record length is 801. Actual file records are 3350 bytes, but
# positions 802-3350 are entirely blank filler (padded to match later
# format). All data lives in positions 1-801.
#
# This file contains BOTH 2003-revision (VERSION='A') and 1989-revision
# (VERSION='S') state records. Many fields are version-specific:
#   A-only: revised items (MEDUC, PRECARE, CIG_1/2/3, RF_* revised, ME_*,
#           CA_* revised, PWGT, DWGT, etc.)
#   S-only: unrevised items (UMEDUC, MPCB, TOBUSE, CIGS, UME_VBAC/PRIMC/REPEC,
#           UME_HYSTER, etc.)
#   A+S:   common items (MAGER, RESTATUS, UMHISP, SEX, DBWT, COMBGEST, etc.)
#
# 2006 revised states (VERSION='A', 16 states, 23% of fetal deaths >=20 wk):
#   California, Delaware, Florida, Idaho, Kansas, Kentucky, Maryland,
#   Michigan, Nebraska, New Hampshire, Oklahoma, Pennsylvania, South Dakota,
#   Texas, Utah, Washington
#
# Remaining 34 states + DC + NYC on VERSION='S' (1989 revision).
#
# Source: 2006 Fetal Death Public Use File User Guide (PDF, 104 pages)

FETAL_2005_2006_FIELDS: list[tuple[str, int, int]] = [
    # ========================
    # Record identification
    # ========================
    ("VERSION",         7,    7),   # A=2003 revision; S=1989 revision
    ("TABFLG",          9,    9),   # 1=Under 20 wk (exclude); 2=20+ wk (include)
    ("DOD_YY",         15,   18),   # Delivery year (2006)
    ("DOD_MM",         19,   20),   # Delivery month (01-12)
    ("DOD_WK",         29,   29),   # Day of week (1=Sun..7=Sat)

    # ========================
    # Geography (territory file only; blank in US file)
    # ========================
    ("OSTATE",         30,   31),   # Territory of occurrence (AS/GU/MP/PR/VI)
    ("OCNTYFIPS",      37,   39),   # Occurrence county FIPS
    ("OCNTYPOP",       40,   40),   # Occurrence county population code

    # ========================
    # Delivery place
    # ========================
    ("BFACIL",         41,   41),   # Delivery place - revised (A only)
    ("UBFACIL",        42,   42),   # Delivery place - unrevised (A+S)
    ("BFACIL3",        59,   59),   # Delivery place recode (A+S)

    # ========================
    # Mother demographics - age
    # ========================
    ("MAGE_IMPFLG",    87,   87),   # Mother's age imputed flag (A+S)
    ("MAGE_REPFLG",    88,   88),   # Reported age of mother flag (A+S)
    ("MAGER",          89,   90),   # Mother's single year of age (A+S)
    ("MAGER14",        91,   92),   # Mother's age recode 14 (A+S)
    ("MAGER9",         93,   93),   # Mother's age recode 9 (A+S)

    # ========================
    # Mother birth country (territory file only)
    # ========================
    ("MBCNTRY",        94,   95),   # Mother's birth country (A,s)

    # ========================
    # Mother residence geography (territory file only)
    # ========================
    ("MRSTATEPSTL",   109,  110),   # Mother's territory of residence
    ("MRCNTYFIPS",    114,  116),   # Mother's FIPS county of residence
    ("RCNTY_POP",     132,  132),   # Residence county population code

    # ========================
    # Record type / residence status
    # ========================
    ("RECTYPE",       137,  137),   # Record type (territory file only)
    ("RESTATUS",      138,  138),   # Residence status (A+S)

    # ========================
    # Mother demographics - race
    # ========================
    ("MBRACE",        139,  140),   # Mother's bridged race (A only, 2-digit)
    ("MRACEREC",      143,  143),   # Mother's race recode (A+S, bridged 4-cat)
    ("MRACEIMP",      144,  144),   # Mother's race imputed flag (A+S)

    # ========================
    # Mother demographics - Hispanic origin
    # ========================
    ("UMHISP",        148,  148),   # Mother's Hispanic origin (A+S)
    ("MRACEHISP",     149,  149),   # Mother's race/Hispanic origin (A+S)

    # ========================
    # Mother demographics - marital status
    # ========================
    ("MAR",           153,  153),   # Mother's marital status (A+S)
    ("MAR_IMP",       154,  154),   # Mother's marital status imputed (A+S)

    # ========================
    # Mother demographics - education
    # ========================
    ("MEDUC",         155,  155),   # Mother's education - revised (A only)
    ("UMEDUC",        156,  157),   # Mother's education - unrevised (S only)
    ("MEDUC_REC",     158,  158),   # Mother's education recode (S only)

    # ========================
    # Father demographics
    # ========================
    ("FAGERPT_FLG",   175,  175),   # Father's reported age used flag (A+S)
    ("FAGECOMB",      182,  183),   # Father's combined age - revised (A only)
    ("UFAGECOMB",     184,  185),   # Father's combined age - unrevised (A+S)
    ("FAGEREC11",     186,  187),   # Father's age recode 11 (A+S)

    # ========================
    # Pregnancy history
    # ========================
    ("LBO_REC",       212,  212),   # Live birth order recode (A+S)
    ("TBO_REC",       217,  217),   # Total birth order recode (A+S)

    # ========================
    # Prenatal care
    # ========================
    ("PRECARE",       245,  246),   # Month prenatal care began - revised (A only)
    ("PRECARE_REC",   247,  247),   # Prenatal care recode - revised (A only)
    ("MPCB",          256,  257),   # Month prenatal care began - unrevised (S only)
    ("MPCB_REC6",     258,  258),   # Prenatal care recode 6 - unrevised (S only)
    ("MPCB_REC5",     259,  259),   # Prenatal care recode 5 - unrevised (S only)
    ("UPREVIS",       270,  271),   # Number of prenatal visits (A+S)
    ("PREVIS_REC",    272,  273),   # Prenatal visits recode (A+S)

    # ========================
    # Weight gain
    # ========================
    ("WTGAIN",        276,  277),   # Weight gain in pounds (A+S)
    ("WTGAIN_REC",    278,  278),   # Weight gain recode (A+S)

    # ========================
    # Prenatal care date imputation
    # ========================
    ("DFPC_IMP",      280,  280),   # Day of first prenatal care imputed (R/A only)

    # ========================
    # Tobacco use
    # ========================
    ("CIG_1",         284,  285),   # Cigarettes 1st trimester (A only)
    ("CIG_2",         286,  287),   # Cigarettes 2nd trimester (A only)
    ("CIG_3",         288,  289),   # Cigarettes 3rd trimester (A only)
    ("TOBUSE",        290,  290),   # Tobacco use - unrevised (S only)
    ("CIGS",          291,  292),   # Cigarettes per day - unrevised (S only)
    ("UCIG_REC6",     293,  293),   # Cigarette recode - unrevised (S only)
    ("CIG_REC",       294,  294),   # Smoking status recode - revised (A only)

    # ========================
    # Mother weight
    # ========================
    ("PWGT",          305,  307),   # Prepregnancy weight (A only)
    ("DWGT",          309,  311),   # Maternal delivery weight (A only)

    # ========================
    # Risk factors - revised (A only)
    # ========================
    ("RF_DIAB",       313,  313),   # Prepregnancy diabetes (A)
    ("RF_GEST",       314,  314),   # Gestational diabetes (A)
    ("RF_PHYP",       315,  315),   # Prepregnancy hypertension (A)
    ("RF_GHYP",       316,  316),   # Gestational hypertension (A)
    ("RF_ECLAM",      317,  317),   # Hypertension eclampsia (A)
    ("RF_PPTERM",     318,  318),   # Previous preterm birth (A)
    ("RF_PPOUTC",     319,  319),   # Poor pregnancy outcome (A)
    ("RF_CESAR",      324,  324),   # Previous cesareans Y/N (A)
    ("RF_CESARN",     325,  326),   # Number of previous cesareans (A)

    # ========================
    # Risk factors - unrevised (A+S for cross-revision items)
    # ========================
    ("URF_DIAB",      331,  331),   # Diabetes - unrevised (A+S)
    ("URF_CHYPER",    335,  335),   # Chronic hypertension - unrevised (A+S)
    ("URF_PHYPER",    336,  336),   # Pregnancy-assoc hypertension - unrevised (A+S)
    ("URF_ECLAMP",    337,  337),   # Eclampsia - unrevised (A+S)

    # ========================
    # Obstetric procedures - unrevised (A+S)
    # ========================
    ("UOP_INDUC",     357,  357),   # Induction of labor (A+S)
    ("UOP_TOCOL",     359,  359),   # Tocolysis (A+S)

    # ========================
    # Complications of labor and delivery
    # ========================
    ("ULD_BREECH",    384,  384),   # Breech delivery (A+S)

    # ========================
    # Method of delivery - revised (A only)
    # ========================
    ("ME_PRES",       392,  392),   # Fetal presentation (A)
    ("ME_ROUT",       393,  393),   # Route and method of delivery (A)
    ("ME_TRIAL",      394,  394),   # Trial of labor attempted (A)
    ("ME_HYSTER",     395,  395),   # Hysterotomy/hysterectomy (A)

    # ========================
    # Method of delivery - unrevised
    # ========================
    ("UME_VAG",       396,  396),   # Vaginal (A+S)
    ("UME_VBAC",      397,  397),   # Vaginal after C-section (S only)
    ("UME_PRIMC",     398,  398),   # Primary C-section (S only)
    ("UME_REPEC",     399,  399),   # Repeat C-section (S only)
    ("UME_FORCP",     400,  400),   # Forceps (A+S)
    ("UME_VAC",       401,  401),   # Vacuum (A+S)
    ("UME_HYSTER",    402,  402),   # Hysterectomy/hysterotomy - unrevised (S)

    # ========================
    # Delivery method recode
    # ========================
    ("DMETH_REC",     403,  403),   # Delivery method recode (A+S)

    # ========================
    # Attendant
    # ========================
    ("ATTEND",        410,  410),   # Attendant at delivery (A+S)

    # ========================
    # Plurality
    # ========================
    ("DPLURAL",       423,  423),   # Plurality recode (A+S)
    ("IMP_PLUR",      425,  425),   # Plurality imputed flag (A+S)

    # ========================
    # Fetal characteristics - sex
    # ========================
    ("SEX",           436,  436),   # Sex of fetus (A+S)
    ("IMP_SEX",       437,  437),   # Sex imputed flag (A+S)

    # ========================
    # Gestation - last menstrual period
    # ========================
    ("DLMP_MM",       438,  439),   # Last normal menses month (A+S)
    ("DLMP_YY",       442,  445),   # Last normal menses year (A+S)

    # ========================
    # Gestation - estimates and recodes
    # ========================
    ("ESTGEST",       446,  447),   # Obstetric/clinical gestation estimate (A+S)
    ("COMBGEST",      451,  452),   # Combined gestation detail in weeks (A+S)
    ("GESTREC12",     453,  454),   # Gestation recode 12 (A+S)
    ("GESTREC5",      455,  455),   # Gestation recode 5 (A+S)
    ("OBGEST_FLG",    456,  456),   # Obstetric estimate used flag (A+S)
    ("GEST_IMP",      457,  457),   # Gestation imputed flag (A+S)

    # ========================
    # Birth weight
    # ========================
    ("DBWT",          463,  466),   # Birth weight detail in grams (A+S)
    ("BWTR14",        471,  472),   # Birth weight recode 14 (A+S)
    ("BWTR4",         473,  473),   # Birth weight recode 4 (A+S)

    # ========================
    # Congenital anomalies - revised (A only)
    # ========================
    ("CA_ANEN",       492,  492),   # Anencephaly (A)
    ("CA_MNSB",       493,  493),   # Meningomyelocele/spina bifida (A)
    ("CA_CCHD",       494,  494),   # Cyanotic congenital heart disease (A)
    ("CA_CDH",        495,  495),   # Congenital diaphragmatic hernia (A)
    ("CA_OMPH",       496,  496),   # Omphalocele (A)
    ("CA_GAST",       497,  497),   # Gastroschisis (A)
    ("CA_LIMB",       498,  498),   # Limb reduction defect (A)
    ("CA_CLEFT",      499,  499),   # Cleft lip w/wo cleft palate (A)
    ("CA_CLPAL",      500,  500),   # Cleft palate alone (A)
    ("CA_DOWN",       501,  501),   # Down syndrome (A) - C/P/N/U
    ("CA_DISOR",      502,  502),   # Suspected chromosomal disorder (A) - C/P/N/U
    ("CA_HYPO",       503,  503),   # Hypospadias (A)

    # ========================
    # Congenital anomalies - unrevised (A+S)
    # ========================
    ("UCA_ANEN",      504,  504),   # Anencephalus (A+S)
    ("UCA_SPINA",     505,  505),   # Spina bifida/meningocele (A+S)
    ("UCA_OMPHA",     513,  513),   # Omphalocele/gastroschisis (A+S)
    ("UCA_CLEFTLP",   518,  518),   # Cleft lip/palate (A+S)
    ("UCA_DOWNS",     523,  523),   # Down syndrome (A+S)

    # ========================
    # Reporting flags (positions 569-801)
    # Coding: 0=Not reporting; 1=Reporting
    # ========================
    ("F_MORIGIN",     569,  569),   # Mother's Hispanic origin flag (A+S)
    ("F_MEDUC",       571,  571),   # Education of mother flag (A)
    ("F_CLINEST",     573,  573),   # Obstetric estimate of gestation flag (A+S)
    ("F_TOBACO",      575,  575),   # Tobacco use flag (A)
    ("F_RF_PDIAB",    582,  582),   # Prepregnancy diabetes flag (A)
    ("F_RF_GDIAB",    583,  583),   # Gestational diabetes flag (A)
    ("F_RF_PHYPER",   584,  584),   # Prepregnancy hypertension flag (A)
    ("F_RF_GHYPER",   585,  585),   # Gestational hypertension flag (A)
    ("F_RF_ECLAMP",   586,  586),   # Hypertension eclampsia flag (A)
    ("F_RF_PPB",      587,  587),   # Previous preterm birth flag (A)
    ("F_RF_PPO",      588,  588),   # Poor pregnancy outcomes flag (A)
    ("F_RF_CESAR",    593,  593),   # Previous cesarean flag (A)
    ("F_RF_NCESAR",   594,  594),   # Number of previous cesareans flag (A)
    ("F_MD_PRESENT",  619,  619),   # Fetal presentation flag (A)
    ("F_MD_ROUTE",    620,  620),   # Route/method of delivery flag (A)
    ("F_MD_TRIAL",    621,  621),   # Trial of labor flag (A)
    ("F_CA_ANEN",     635,  635),   # Anencephaly flag (A)
    ("F_CA_MENIN",    636,  636),   # Meningomyelocele/spina bifida flag (A)
    ("F_CA_HEART",    637,  637),   # Cyanotic congenital heart disease flag (A)
    ("F_CA_HERNIA",   638,  638),   # Congenital diaphragmatic hernia flag (A)
    ("F_CA_OMPHA",    639,  639),   # Omphalocele flag (A)
    ("F_CA_GASTRO",   640,  640),   # Gastroschisis flag (A)
    ("F_CA_LIMB",     641,  641),   # Limb reduction defect flag (A)
    ("F_CA_CLEFTLP",  642,  642),   # Cleft lip/palate flag (A)
    ("F_CA_CLEFT",    643,  643),   # Cleft palate alone flag (A)
    ("F_CA_DOWNS",    644,  644),   # Down syndrome flag (A)
    ("F_CA_CHROM",    645,  645),   # Suspected chromosomal disorder flag (A)
    ("F_CA_HYPOS",    646,  646),   # Hypospadias flag (A)
    ("F_MED",         647,  647),   # Mother's education unrevised flag (S)
    ("F_WTGAIN",      648,  648),   # Weight gain flag (A+S)
    ("F_TOBAC",       667,  667),   # Tobacco use unrevised flag (S)
    ("F_MPCB",        668,  668),   # Month prenatal care began flag (A)
    ("F_CMBGST",      670,  670),   # Combined gestation flag (A)
    ("F_TPCV",        671,  671),   # Total prenatal care visits flag (A+S)
    ("F_CIGS_1",      673,  673),   # Cigarettes 1st trimester flag (A)
    ("F_CIGS_2",      674,  674),   # Cigarettes 2nd trimester flag (A)
    ("F_CIGS_3",      675,  675),   # Cigarettes 3rd trimester flag (A)
    ("F_FACILITY",    676,  676),   # Facility flag (A)
    ("DelMethRecF",   678,  678),   # Delivery method recode flag (A+S)
    ("F_URF_DIAB",    684,  684),   # Diabetes unrevised flag (A+S)
    ("F_URF_CHYPER",  688,  688),   # Chronic hypertension unrevised flag (A+S)
    ("F_URF_PHYPER",  689,  689),   # Pregnancy hypertension unrevised flag (A+S)
    ("F_URF_ECLAMP",  690,  690),   # Eclampsia unrevised flag (A+S)
    ("F_UOB_INDUCT",  703,  703),   # Induction flag (A+S)
    ("F_UOB_TOCOL",   705,  705),   # Tocolysis flag (A+S)
    ("F_ULD_BREECH",  721,  721),   # Breech flag (A+S)
    ("F_U_VAGINAL",   730,  730),   # Vaginal flag - unrevised (S)
    ("F_U_VBAC",      731,  731),   # VBAC flag - unrevised (S)
    ("F_U_PRIMAC",    732,  732),   # Primary C-section flag - unrevised (S)
    ("F_U_REPEAC",    733,  733),   # Repeat C-section flag - unrevised (S)
    ("F_U_FORCEP",    734,  734),   # Forceps flag - unrevised (S)
    ("F_U_VACUUM",    735,  735),   # Vacuum flag - unrevised (S)
    ("F_UCA_ANEN",    752,  752),   # Anencephalus unrevised flag (A+S)
    ("F_UCA_SPINA",   753,  753),   # Spina bifida unrevised flag (A+S)
    ("F_UCA_OMPHALO", 761,  761),   # Omphalocele unrevised flag (A+S)
    ("F_UCA_CLEFTLP", 766,  766),   # Cleft lip unrevised flag (A+S)
    ("F_UCA_DOWNS",   771,  771),   # Down syndrome unrevised flag (A+S)
    ("F_MS",          780,  780),   # Mother's marital status flag (A+S)
    ("F_CIG_DAY",     794,  794),   # Cigarettes per day unrevised flag (S)
    ("F_NPREV",       795,  795),   # Number of prenatal visits flag (A)
    ("F_HYSTER_U",    797,  797),   # Hysterectomy unrevised flag (A+S)
    ("F_HYSTER_R",    800,  800),   # Hysterectomy revised flag (A)
    ("F_ATTENDANT",   801,  801),   # Attendant flag (A+S)
]


# --- 2018-2024 COD-only layout (record length 2651) ---
# PDF documents record length as 3150, but the actual data file has trailing
# FILLER (positions 2652-3150) stripped. Last data field is F_ICOD at pos 2651.
# All states on 2003 revision by 2018.
# Source: 2022 Fetal Death User Guide (original); cross-verified at C8.2
# PRE-FLIGHT 2026-05-12T22:30Z against 2023+2024 user guides via PyMuPDF
# text-layer probe — 17/17 captured (start,end,field) triples byte-identical
# across 2022/2023/2024. Record length 2651 confirmed via parsing
# 39,574 (2023) + 35,648 (2024) records, all rows = 2651 bytes.
# Page count grew from 80 (2022) to 85 (2023) to 86 (2024) but no field
# byte-position drift.

FETAL_2018_2022_FIELDS: list[tuple[str, int, int]] = [
    # Record identification
    ("VERSION",         7,    7),
    ("OE_TABFLG",      10,   10),
    ("DOD_YY",         11,   14),
    ("DOD_MM",         15,   16),
    ("DOD_TT",         21,   24),
    ("DOD_WK",         25,   25),

    # Geography (territory file only — blank in US file, but preserve)
    ("OSTATE",         26,   27),
    ("OCNTYFIPS",      30,   32),
    ("OCNTYPOP",       33,   33),

    # Delivery place
    ("BFACIL",         34,   34),
    ("BFACIL3",        52,   52),

    # Mother age
    ("MAGE_IMPFLG",    84,   84),
    ("MAGE_REPFLG",    85,   85),
    ("MAGER",          86,   87),
    ("MAGER14",        88,   89),
    ("MAGER9",         90,   90),

    # Mother birth country / nativity
    ("MBCNTRY",        91,   92),
    ("MBSTATE_REC",    97,   97),

    # Mother residence geography (territory file only)
    ("MRSTATEPSTL",   102,  103),
    ("MRCNTYFIPS",    104,  106),
    ("RCNTY_POP",     112,  112),

    # Record type / residence status
    ("RECTYPE",       130,  130),
    ("RESTATUS",      131,  131),

    # Mother race
    ("MRACE31",       132,  133),
    ("MRACE6",        134,  134),
    ("MRACE15",       135,  136),
    ("MRACEIMP",      138,  138),

    # Hispanic origin
    ("UMHISP",        142,  142),
    ("MHISPX",        143,  143),
    ("SR_MRACEHISP",  144,  144),

    # Education
    ("MEDUC",         145,  145),

    # Father
    ("FAGERPT_FLG",   172,  172),
    ("FAGECOMB",      177,  178),
    ("FAGEREC11",     179,  180),

    # Prior pregnancies
    ("PRIORLIVE",     181,  182),
    ("PRIORDEAD",     183,  184),
    ("LBO_REC",       187,  187),

    # Birth interval
    ("ILLB_R",        197,  199),
    ("ILLB_R11",      200,  201),

    # Prenatal care
    ("PRECARE",       202,  203),
    ("PRECARE_REC",   204,  204),

    # WIC
    ("WIC",           229,  229),

    # Tobacco
    ("CIG_0",         230,  231),
    ("CIG_1",         232,  233),
    ("CIG_2",         234,  235),
    ("CIG_3",         236,  237),
    ("CIG_REC",       238,  238),

    # Mother height / BMI / weight
    ("M_Ht_In",       243,  244),
    ("BMI",           245,  248),
    ("BMI_R",         249,  249),
    ("PWgt_R",        253,  255),

    # Risk factors
    ("RF_DIAB",       257,  257),
    ("RF_GEST",       258,  258),
    ("RF_PHYP",       259,  259),
    ("RF_GHYP",       260,  260),
    ("RF_ECLAM",      261,  261),
    ("RF_INFTR",      262,  262),
    ("RF_FEDRG",      263,  263),
    ("RF_ARTEC",      264,  264),
    ("RF_CESAR",      265,  265),
    ("RF_CESARN",     266,  267),

    # Delivery method
    ("ME_PRES",       274,  274),
    ("ME_ROUT",       275,  275),
    ("ME_TRIAL",      276,  276),
    ("RDMETH_REC",    277,  277),
    ("DMETH_REC",     280,  280),

    # Maternal morbidity
    ("MM_RUPT",       281,  281),
    ("MM_ICU",        282,  282),

    # Attendant
    ("ATTEND",        283,  283),

    # Plurality
    ("DPLURAL",       301,  301),
    ("IMP_PLUR",      303,  303),

    # Sex
    ("SEX",           316,  316),
    ("IMP_SEX",       317,  317),

    # Last menstrual period
    ("DLMP_MM",       318,  319),
    ("DLMP_YY",       322,  325),

    # Gestation
    ("GEST_IMP",      329,  329),
    ("OBGEST_FLG",    330,  330),
    ("COMBGEST",      331,  332),
    ("GESTREC12",     333,  334),
    ("GESTREC5",      335,  335),
    ("OEGest_Unedt",  336,  337),
    ("COMBGEST_USED", 339,  339),
    ("OEGest_Comb",   340,  341),
    ("OEGest_R12",    342,  343),
    ("OEGest_R5",     344,  344),

    # Birth weight
    ("DBWT",          349,  352),
    ("BWTR14",        353,  354),
    ("BWTR4",         355,  355),

    # Fetal death specifics
    ("ESTOFD",        357,  357),
    ("AUTOPSY",       358,  358),
    ("HISTOPF",       359,  359),
    ("AUTOPF",        360,  360),

    # Reporting flags
    ("F_MEDUC",       372,  372),
    ("F_CLINEST",     373,  373),
    ("F_TOBACO",      374,  374),
    ("F_M_HT",        375,  375),
    ("F_PWGT",        376,  376),
    ("F_WIC",         377,  377),
    ("F_RF_PDIAB",    378,  378),
    ("F_RF_GDIAB",    379,  379),
    ("F_RF_PHYPER",   380,  380),
    ("F_RF_GHYPER",   381,  381),
    ("F_RF_ECLAMP",   382,  382),
    ("F_RF_INFT",     383,  383),
    ("F_RF_INFT_DRG", 384,  384),
    ("F_RF_INFT_ART", 385,  385),
    ("F_RF_CESAR",    386,  386),
    ("F_RF_NCESAR",   387,  387),
    ("F_MD_PRESENT",  388,  388),
    ("F_MD_ROUTE",    389,  389),
    ("F_MD_TRIAL",    390,  390),
    ("F_MM_RUPTUR",   391,  391),
    ("F_MM_ICU",      392,  392),
    ("F_MPCB",        403,  403),
    ("F_CMBGST",      404,  404),
    ("F_CIGS_0",      405,  405),
    ("F_CIGS_1",      406,  406),
    ("F_CIGS_2",      407,  407),
    ("F_CIGS_3",      408,  408),
    ("F_FACILITY",    409,  409),
    ("DelMethRecF",   410,  410),
    ("F_MORIGIN",     424,  424),
    ("F_MRACE_R",     425,  425),
    ("F_FAGE_u",      426,  426),
    ("F_DLLB_MM",     427,  427),
    ("F_DLMP_MM",     429,  429),
    ("F_DLMP_YY",     431,  431),
    ("F_MAGE",        432,  432),
    ("F_ATTENDANT",   433,  433),
    ("F_ESTOFD",      435,  435),
    ("F_AUTOPSY",     436,  436),
    ("F_HISTOPF",     437,  437),
    ("F_AUTOPF",      438,  438),
    ("F_MRACEREC",    439,  439),
    ("F_PLBL",        440,  440),
    ("F_PLBD",        441,  441),
    ("F_DBWT",        442,  442),
    ("F_BMI",         445,  445),

    # Cause of death (COD section)
    ("IICOD",        2603, 2607),
    ("IC_124_Fetal", 2643, 2645),
    ("F_ICOD",       2651, 2651),
]


# --- 2014-2017 COD layout (record length ~3050) ---
# Transition period: most states on 2003 revision, a few stragglers on 1989.
# COD fields at same positions as 2018+.
# Most data fields at same positions as 2018-2022.
# Source: 2014 Fetal Death User Guide (COD variant record layout)

FETAL_2014_2017_FIELDS: list[tuple[str, int, int]] = [
    # Record identification
    ("VERSION",         7,    7),
    ("OE_TABFLG",      10,   10),
    ("DOD_YY",         11,   14),
    ("DOD_MM",         15,   16),
    ("DOD_TT",         21,   24),
    ("DOD_WK",         25,   25),

    # Geography
    ("OSTATE",         26,   27),
    ("OCNTYFIPS",      30,   32),
    ("OCNTYPOP",       33,   33),

    # Delivery place
    ("BFACIL",         34,   34),
    ("UBFACIL",        35,   35),   # Delivery place - unrevised (A+S)
    ("BFACIL3",        52,   52),

    # Mother age
    ("MAGE_IMPFLG",    84,   84),
    ("MAGE_REPFLG",    85,   85),
    ("MAGER",          86,   87),
    ("MAGER14",        88,   89),
    ("MAGER9",         90,   90),

    # Mother birth country / nativity
    ("MBCNTRY",        91,   92),
    ("MBSTATE_REC",    97,   97),

    # Mother residence geography
    ("MRSTATEPSTL",   102,  103),
    ("MRCNTYFIPS",    104,  106),
    ("RCNTY_POP",     112,  112),

    # Record type / residence
    ("RECTYPE",       130,  130),
    ("RESTATUS",      131,  131),

    # Mother race
    ("MRACE31",       132,  133),
    ("MRACE6",        134,  134),
    ("MRACE15",       135,  136),
    ("MRACEREC",      137,  137),  # Bridged race — present in 2014, gone by 2022
    ("MRACEIMP",      138,  138),

    # Hispanic origin
    ("UMHISP",        142,  142),
    ("MRACEHISP",     143,  143),  # Bridged race/Hispanic — present in 2014, gone by 2022
    ("SR_MRACEHISP",  144,  144),

    # Education
    ("MEDUC",         145,  145),

    # Father
    ("FAGERPT_FLG",   172,  172),
    ("FAGECOMB",      177,  178),
    ("FAGEREC11",     179,  180),

    # Prior pregnancies
    ("PRIORLIVE",     181,  182),
    ("PRIORDEAD",     183,  184),
    ("LBO_REC",       187,  187),

    # Birth interval
    ("ILLB_R",        197,  199),
    ("ILLB_R11",      200,  201),

    # Prenatal care
    ("PRECARE",       202,  203),
    ("PRECARE_REC",   204,  204),

    # WIC
    ("WIC",           229,  229),

    # Tobacco
    ("CIG_0",         230,  231),
    ("CIG_1",         232,  233),
    ("CIG_2",         234,  235),
    ("CIG_3",         236,  237),
    ("CIG_REC",       238,  238),

    # Mother height / BMI / weight
    ("M_Ht_In",       243,  244),
    ("BMI",           245,  248),
    ("BMI_R",         249,  249),
    ("PWgt_R",        253,  255),

    # Risk factors - revised (A only)
    ("RF_DIAB",       257,  257),
    ("RF_GEST",       258,  258),
    ("RF_PHYP",       259,  259),
    ("RF_GHYP",       260,  260),
    ("RF_ECLAM",      261,  261),
    ("RF_INFTR",      262,  262),
    ("RF_FEDRG",      263,  263),
    ("RF_ARTEC",      264,  264),
    ("RF_CESAR",      265,  265),
    ("RF_CESARN",     266,  267),

    # Risk factors - unrevised (A+S, present in 2014, absent in 2022)
    ("URF_DIAB",      269,  269),   # Diabetes - unrevised (A+S)
    ("URF_CHYPER",    270,  270),   # Chronic hypertension - unrevised (A+S)
    ("URF_PHYPER",    271,  271),   # Pregnancy-assoc hypertension - unrevised (A+S)
    ("URF_ECLAMP",    272,  272),   # Eclampsia - unrevised (A+S)

    # Complications of labor - unrevised
    ("ULD_BREECH",    273,  273),   # Breech delivery - unrevised (A+S)

    # Delivery method
    ("ME_PRES",       274,  274),
    ("ME_ROUT",       275,  275),
    ("ME_TRIAL",      276,  276),
    ("RDMETH_REC",    277,  277),
    ("DMETH_REC",     280,  280),

    # Maternal morbidity
    ("MM_RUPT",       281,  281),
    ("MM_ICU",        282,  282),

    # Attendant
    ("ATTEND",        283,  283),

    # Plurality
    ("DPLURAL",       301,  301),
    ("IMP_PLUR",      303,  303),

    # Sex
    ("SEX",           316,  316),
    ("IMP_SEX",       317,  317),

    # Last menstrual period
    ("DLMP_MM",       318,  319),
    ("DLMP_YY",       322,  325),

    # Gestation
    ("GEST_IMP",      329,  329),
    ("OBGEST_FLG",    330,  330),
    ("COMBGEST",      331,  332),
    ("GESTREC12",     333,  334),
    ("GESTREC5",      335,  335),
    ("OEGest_Unedt",  336,  337),
    ("COMBGEST_USED", 339,  339),
    ("OEGest_Comb",   340,  341),
    ("OEGest_R12",    342,  343),
    ("OEGest_R5",     344,  344),

    # Birth weight
    ("DBWT",          349,  352),
    ("BWTR14",        353,  354),
    ("BWTR4",         355,  355),

    # Fetal death specifics
    ("ESTOFD",        357,  357),
    ("AUTOPSY",       358,  358),
    ("HISTOPF",       359,  359),
    ("AUTOPF",        360,  360),

    # Reporting flags
    ("F_MEDUC",       372,  372),
    ("F_CLINEST",     373,  373),
    ("F_TOBACO",      374,  374),
    ("F_M_HT",        375,  375),
    ("F_PWGT",        376,  376),
    ("F_WIC",         377,  377),
    ("F_RF_PDIAB",    378,  378),
    ("F_RF_GDIAB",    379,  379),
    ("F_RF_PHYPER",   380,  380),
    ("F_RF_GHYPER",   381,  381),
    ("F_RF_ECLAMP",   382,  382),
    ("F_RF_INFT",     383,  383),
    ("F_RF_INFT_DRG", 384,  384),
    ("F_RF_INFT_ART", 385,  385),
    ("F_RF_CESAR",    386,  386),
    ("F_RF_NCESAR",   387,  387),
    ("F_MD_PRESENT",  388,  388),
    ("F_MD_ROUTE",    389,  389),
    ("F_MD_TRIAL",    390,  390),
    ("F_MM_RUPTUR",   391,  391),
    ("F_MM_ICU",      392,  392),
    ("F_MPCB",        403,  403),
    ("F_CMBGST",      404,  404),
    ("F_CIGS_0",      405,  405),
    ("F_CIGS_1",      406,  406),
    ("F_CIGS_2",      407,  407),
    ("F_CIGS_3",      408,  408),
    ("F_FACILITY",    409,  409),
    ("DelMethRecF",   410,  410),
    ("F_MORIGIN",     424,  424),
    ("F_MRACE_R",     425,  425),
    ("F_FAGE_u",      426,  426),
    ("F_DLLB_MM",     427,  427),
    ("F_DLMP_MM",     429,  429),
    ("F_DLMP_YY",     431,  431),
    ("F_MAGE",        432,  432),
    ("F_ATTENDANT",   433,  433),
    ("F_ESTOFD",      435,  435),
    ("F_AUTOPSY",     436,  436),
    ("F_HISTOPF",     437,  437),
    ("F_AUTOPF",      438,  438),
    ("F_MRACEREC",    439,  439),
    ("F_PLBL",        440,  440),
    ("F_PLBD",        441,  441),
    ("F_DBWT",        442,  442),
    ("F_BMI",         445,  445),

    # Cause of death (COD section — same positions as 2018+)
    ("IICOD",        2603, 2607),
    ("IC_124_Fetal", 2643, 2645),
    ("F_ICOD",       2651, 2651),
]


def layout_for_year(year: int) -> tuple[int, list[tuple[str, int, int]]]:
    """Return (expected_record_length, field_list) for a given data year.

    Record length is the count of DATA bytes per record. Physical lines in
    the raw files may include trailing terminators (e.g., CR+LF for the
    1992-2002 files); the reader must strip them before applying field
    positions.
    """
    if 2018 <= year <= 2024:
        # C8.2 extension 2026-05-12: 2023+2024 reuse the 2018-2022 layout
        # unchanged (record length 2651; field byte-positions byte-identical
        # per PyMuPDF text-layer diff of 2022/2023/2024 user guides).
        return RECORD_LEN_2022, FETAL_2018_2022_FIELDS
    if 2014 <= year <= 2017:
        return RECORD_LEN_2014, FETAL_2014_2017_FIELDS
    if 2005 <= year <= 2006:
        return RECORD_LEN_2006, FETAL_2005_2006_FIELDS
    if year == 2007:
        return RECORD_LEN_2007, FETAL_2005_2006_FIELDS
    if 2008 <= year <= 2013:
        return RECORD_LEN_2008, FETAL_2005_2006_FIELDS
    if 1989 <= year <= 2002:
        # V3a extension (1989-1991): 1989-revision layout is byte-identical to
        # 1992-2002. Page 5-6 Data Elements lists in the 1989/1990/1991 user
        # guides match the 1992 user guide field-by-field; first-record
        # DATAYEAR @ bytes 1-4 spot-verified. Re-uses FETAL_1992_2002_FIELDS.
        return RECORD_LEN_1992, FETAL_1992_2002_FIELDS
    if 1982 <= year <= 1988:
        # V3b extension (1982-1988): 1978-revision layout, 200 data bytes.
        # Structurally different from V3a/V2/V1: different field names + byte
        # positions + recode schemes. Page-4/5/6 cross-year diff across all 7
        # V3b years confirms byte-identical field positions. Empirical
        # anchor-field spot-check on 1982/1983/1985/1988 raw zips PASS.
        # Canonical layout in record_layout_1982_1988.csv (87 rows).
        return RECORD_LEN_1978, FETAL_1982_1988_FIELDS
    if year == 2003:
        # V2.1: 1350 data bytes. Per-record A/S byte at position 7 selects
        # 2003-revision vs 1989-revision schema. Fields at bytes 1-801 are
        # shared across A and S (parser extracts them uniformly); A-specific
        # race detail at bytes 833-847 + 1088-1111 is documented in
        # fetal_death/record_layout_2003.csv but not used by the V2.1
        # harmonization (race comes from MRACEREC@byte-143 for both branches).
        return RECORD_LEN_2003, FETAL_2005_2006_FIELDS
    if year == 2004:
        # V2.1: 1500 data bytes (= 2003 + 150-byte trailing pad). Same field
        # set as 2003. See fetal_death/record_layout_2004.csv.
        return RECORD_LEN_2004, FETAL_2005_2006_FIELDS
    raise ValueError(
        f"Year {year} not configured. Currently supported: 1982-2024."
    )
