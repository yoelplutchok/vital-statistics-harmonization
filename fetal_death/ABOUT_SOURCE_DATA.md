# About the Source Data: U.S. Fetal Death Files

## What Is Fetal Death Reporting?

Fetal death reporting in the United States is administered through the National Vital Statistics System (NVSS), operated by the National Center for Health Statistics (NCHS). When a fetal death occurs, the attending physician or facility completes a Standard Report of Fetal Death (also referred to as the fetal death certificate). These reports are filed with state vital registration offices and subsequently transmitted to NCHS, which compiles them into annual national data files.

## Definition

A fetal death is defined as "death prior to the complete expulsion or extraction from its mother of a product of human conception, irrespective of the duration of pregnancy." The death is indicated by the absence of breathing, heartbeat, umbilical cord pulsation, or definite movement of voluntary muscles after expulsion or extraction. Induced terminations of pregnancy are excluded from fetal death reporting.

## Source Files

NCHS releases annual public-use microdata files containing individual-level fetal death records. These are distributed as fixed-width ASCII text files accompanied by technical documentation describing the record layout, variable coding, and file structure. Each annual release follows the record format dictated by the certificate revision in effect at the time.

The V2.0 release of this project parses 29 annual files spanning 1992 through 2022 (with 2003 and 2004 deferred to V2.1 because of distinct transition layouts):

| Era | Years | Files | Record length | Notes |
|---|---|---|---|---|
| 1989-revision uniform | 1992-2002 | 11 | 360 bytes (362 with CRLF) | All states on the 1989 revision; no native VERSION field |
| 2003-revision transition | 2005-2013 | 9 | 3351 / 801 / 3338 bytes (varies by year) | Mixed 1989 (S) and 2003 (A) revision content; VERSION field discriminates. Record lengths reflect the full layout including end-of-record FILLER (the last named field ends at position 800-801; trailing FILLER carries the record to the documented length). |
| 2003-revision COD-variant | 2014-2017 | 4 | 3050 bytes | Cause-of-death (ICD-10) added; mostly A-version |
| 2003-revision COD-only | 2018-2022 | 5 | 2652 bytes | All states A-version; bridged-race column dropped. Last named field `F_ICOD` is at position 2651; record ends at position 2652 (final 1-byte FILLER). |

## Coverage

The public-use files typically contain between 40,000 and 70,000 records per year. Of these, approximately 20,000 to 30,000 represent fetal deaths occurring at 20 or more weeks of gestation — the population most commonly studied in stillbirth research. The remainder includes earlier gestational age deaths reported by states with lower reporting thresholds.

V2.0 totals: **1,634,195 total records across 29 years**, of which **727,155** form the standard NVSR-comparable subset (`tabulation_flag == '2'` AND `residence_status != '4'`). 728,483 records carry `tabulation_flag == '2'`; the remaining 1,328 are foreign-resident records (`residence_status == '4'`), which NVSR excludes from resident-based tabulations. Note that NCHS's `tabulation_flag` is a compound criterion, *not* a pure GA cutoff — it is typically "GA >= 20 weeks OR BW >= 350g when GA is unknown" with state-specific reporting overlays — so the NVSR-comparable subset includes ~5,400 records (V1 2014+) with GA below 20 weeks and excludes ~63,700 records across all 29 years that have GA >= 20 but flag = 1. Per-year NVSR-comparable counts have been validated to exact match against NVSR 73-09 (2005-2022, 18 years), NVSR 57-08 (1995-2002, 8 years), and the NCHS user guides (1992-1994, 3 years).

## Certificate Revisions

The fetal death certificate has undergone three major revisions: in 1978, 1989, and 2003. Each revision introduced changes to variable definitions, coding schemes, and the set of items collected. The 2003 revision was particularly consequential, adding new fields for BMI, tobacco use detail, plurality/set order changes, and revised cause-of-death reporting. States adopted the 2003 revision on a staggered schedule beginning in 2003, with near-universal adoption achieved by approximately 2018. During the transition period (roughly 2005-2017 in the public-use files), NCHS released files containing a mix of records reported under both the 1989 and 2003 revisions, with revision-specific variable layouts.

The V2.0 release covers 11 years of pure 1989-revision data (1992-2002) plus the full transition window (2005-2022). The two transition years 2003 and 2004 (V2.1 scope) had unique non-uniform layouts that NCHS itself documents as problematic in `fetaldeath0304problems.pdf`.

## Key Variable Domains

The fetal death files contain variables spanning several domains: record identification and filing information; maternal demographic characteristics (age, race, ethnicity, education, marital status, state of residence — state available in 1992-2002 raw files; suppressed in V1-era public-use files); paternal demographics (age, race, ethnicity); pregnancy and obstetric history (prior pregnancies, live births, losses, prenatal care, gestational age, plurality); fetal characteristics (sex, weight, presentation); maternal risk factors and complications; method of delivery; and (2014+ only) ICD-10-coded cause of death.

## The Reporting Threshold Problem

A persistent challenge with fetal death data is the lack of a uniform national reporting threshold. State laws vary in their definitions of a reportable fetal death: some require reporting at 20 weeks of gestation, others at 350 grams birthweight, and still others use various combinations of gestational age and weight criteria. Some states report all products of conception. This heterogeneity complicates cross-state comparisons and trend analysis, particularly for earlier gestational ages.

## Why This Data Matters

Fetal death data are essential for stillbirth surveillance, perinatal epidemiology, and maternal-child health research. They enable analysis of temporal trends in stillbirth rates, identification of risk factors, evaluation of disparities by race, ethnicity, and geography, and assessment of the impact of clinical and public health interventions. These files represent the only population-based source for studying fetal mortality at a national scale in the United States.

## Key Limitation: No Harmonized Longitudinal Product

Despite the research value of these files, no harmonized longitudinal data product existed prior to this project. NCHS releases each year as a standalone fixed-width file with year-specific documentation. Major data harmonization efforts that cover other vital statistics domains — including NBER, IPUMS, and ICPSR — do not include fetal death data. Researchers wishing to conduct multi-year analyses have had to independently parse, recode, and align variables across file layouts and certificate revisions. This project addresses that gap, now covering 29 consecutive years (1992-2022, with 2003-2004 added in V2.1) under one stable schema.

## Documented Source Data Quirks

V2.0 faithfully preserves several known NCHS data quirks rather than silently correcting them:

- **Stale-guide years (1996, 2001, 2002)** — three NCHS Fetal Death User Guides have a "U.S. DATA SET → Record count" block copy-pasted from an adjacent year. The actual raw bytes are correct; the guides' self-reported counts for those three years are documentation errors. NVSR 57-08 supplies the authoritative figures and matches the parsed counts exactly.
- **Louisiana plurality non-reporting 1992-1994** — Louisiana reports `DPLURAL=9` for ≈99% of resident-occurrence fetal deaths in those three years. Reporting resumed in 1995.
- **Hispanic-origin non-reporting** — Oklahoma reports `ORMOTH=9` (unknown) on 100% of records for all 11 V2 years; Maryland 1992-1998; Massachusetts 1992-1997. Documented in NVSR 57-08 footnotes.
- **V1 plurality "5" anomaly (2005-2013)** — A-version records contain an epidemiologically implausible concentration of `plurality=5` codes, most plausibly explained as state-level miscoding of unknown plurality during the 2003-revision transition. See `COMPARABILITY.md` §7.
- **V1 delivery method "3" anomaly (2006-2013)** — 2,553 V1 records carry `DMETH_REC=3` even though the documented coding is 1/2/9. Preserved as-is per V1 baseline policy.
- **3 V2 1992 records with non-canonical single-digit `gestational_age_combined`** — raw bytes `'2 '`/`'3 '`/`'4 '` (digit followed by space) are stripped to `'2'`/`'3'`/`'4'`; all three rows have BIRWT=9999 and represent an upstream NCHS data-quality issue.
