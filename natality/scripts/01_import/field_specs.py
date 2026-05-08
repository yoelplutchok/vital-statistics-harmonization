"""
Fixed-field positions for NCHS U.S. public-use natality (subset of variables).

Layouts used in this repo:
- **350-byte** record: 1990–2002 (`PUBLIC_US_1990_2002_FIELDS`; unrevised 1989 certificate)
- **1350-byte** record: 2003 (`PUBLIC_US_2003_FIELDS`)
- **1500-byte** record: 2004–2005 (`PUBLIC_US_2004_FIELDS` / `PUBLIC_US_2005_2010_FIELDS`)
- **775-byte** record: 2006–2013 (same field list as 2005 subset, with added 2013-only fields)
- **1345-byte** record: 2014–2024 (`PUBLIC_US_2014_2015_FIELDS`; positions match 2014–2015
  User Guides. For 2016+ the URF_DIAB/CHYPER/PHYPER tail block at 1331–1333 is filler;
  the harmonizer's RF_PDIAB/RF_GDIAB/RF_PHYPE/RF_GHYPE fallback covers these years.)

Sources for 1990–2004 positions: NBER Stata dictionaries (natl{year}.dct)
  and CDC documentation (Nat{year}doc.pdf).

Positions are 1-based inclusive (NCHS convention).
"""

RECORD_LEN_1990 = 350       # 1990–2002 unrevised certificate
RECORD_LEN_2003 = 1350      # 2003 (first year of dual certificate transition)
RECORD_LEN_2004 = 1500      # 2004 (same as 2005)
RECORD_LEN_2005 = 1500
RECORD_LEN_2010 = 775
RECORD_LEN_2014_2015 = 1345  # 2014–2020 (and likely later revised-era years)

# --- 1990–2002: Unrevised 1989 Standard Certificate of Live Birth ---
# Record length 350 bytes.  Variable names follow NBER convention (lowercase in dct;
# we use UPPERCASE to be consistent with later-era raw field names).
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
