# About the Source Data: U.S. Fetal Death Files

## What Is Fetal Death Reporting?

Fetal death reporting in the United States is administered through the National Vital Statistics System (NVSS), operated by the National Center for Health Statistics (NCHS). When a fetal death occurs, the attending physician or facility completes a Standard Report of Fetal Death (also referred to as the fetal death certificate). These reports are filed with state vital registration offices and subsequently transmitted to NCHS, which compiles them into annual national data files.

## Definition

A fetal death is defined as "death prior to the complete expulsion or extraction from its mother of a product of human conception, irrespective of the duration of pregnancy." The death is indicated by the absence of breathing, heartbeat, umbilical cord pulsation, or definite movement of voluntary muscles after expulsion or extraction. Induced terminations of pregnancy are excluded from fetal death reporting.

## Source Files

NCHS releases annual public-use microdata files containing individual-level fetal death records. These are distributed as fixed-width ASCII text files accompanied by technical documentation describing the record layout, variable coding, and file structure. Each annual release follows the record format dictated by the certificate revision in effect at the time.

The **v2.4.0** harmonization parses **43** annual files spanning **1982 through 2024** across seven layout eras:

| Era | Years | Files | Record length (typical) | Notes |
|---|---|---|---|---|
| **V3b** (1978-revision) | 1982-1988 | 7 | 200 bytes (202 with CRLF) | Predates 1989 revision; see `record_layout_1982_1988.csv` |
| **V3a** (early 1989-rev) | 1989-1991 | 3 | 360 bytes | Uniform 1989-revision; byte-aligned to 1992 benchmark |
| **V2** (1989-rev uniform) | 1992-2002 | 11 | 360 bytes (362 with CRLF) | No native VERSION field |
| **V2.1** (transition) | 2003-2004 | 2 | 1,351 / 1,501 bytes | Mixed 1989/2003 content; see `fetaldeath0304problems.pdf` |
| **V1** (2006-era) | 2005-2013 | 9 | 3,351 / 801 / 3,338 bytes | Mixed S/A; VERSION discriminates |
| **V1** (2014-era) | 2014-2017 | 4 | 3,050 bytes | ICD-10 cause added |
| **V1** (2018-era) | 2018-2024 | 7 | 2,652 bytes | All A-version; bridged-race dropped 2018+ |

See `COMPARABILITY.md` for revision-transition detail and `CODEBOOK.md` Appendix C8.20 for parquet-derived per-era record counts (sum = **2,427,233**).

## Coverage

The public-use files typically contain between 40,000 and 70,000 records per year. Of these, approximately 20,000 to 30,000 represent fetal deaths occurring at 20 or more weeks of gestation — the population most commonly studied in stillbirth research.

**v2.4.0 totals:** **2,427,233** total records across **43 years**; **1,121,986** form the standard NVSR-comparable subset (`tabulation_flag == 2` AND `residence_status != 4`; parquet-derived). **1,123,940** records carry `tabulation_flag == 2`. NCHS's tabulation flag is a compound criterion (typically "GA >= 20 weeks OR BW >= 350g when GA unknown"), not a pure GA cutoff — see Appendix C8.20 for per-era distributions. Per-year NVSR-comparable counts are validated **90/90** byte-exact against NCHS user-guide control blocks and NVSR published tables (`external_validation_targets.csv`).

## Certificate Revisions

The fetal death certificate has undergone three major revisions: in 1978, 1989, and 2003. States adopted the 2003 revision on a staggered schedule (roughly 2005-2017 in public-use files; near-universal by 2018). The harmonized file covers the full span from the 1978-revision years (1982-1988) through 2024.

## Key Variable Domains

Identification and filing; maternal/paternal demographics; pregnancy and obstetric history; fetal characteristics; risk factors; delivery method; and (2014+ only) ICD-10 cause of death. State geographic identifiers are available in pre-2005-revision raw yearly files where NCHS did not suppress them; suppressed in V1-era public-use harmonized output for 2005+.

## The Reporting Threshold Problem

State laws vary in reportable gestational age / birthweight thresholds. See `REPORTING_THRESHOLDS.md`.

## Why This Data Matters

Fetal death data are essential for stillbirth surveillance, perinatal epidemiology, and maternal-child health research. These files represent the only population-based source for studying fetal mortality at a national scale in the United States.

## Key Limitation: No Prior Harmonized Longitudinal Product

Before this project, no harmonized longitudinal fetal-death product existed at national scale. NCHS releases each year standalone; major harmonization efforts for other vital domains (NBER, IPUMS, ICPSR) do not include fetal death. This resource provides **43 consecutive years (1982-2024)** under one stable schema.

## Documented Source Data Quirks

Faithfully preserved (not silently corrected):

- **Stale-guide years (1996, 2001, 2002)** — user-guide control blocks copy-pasted; NVSR 57-08 authoritative; parsed counts match NVSR.
- **Louisiana plurality 1992-1994** — `DPLURAL=9` for ≈99% of LA resident-occurrence records; resumed 1995.
- **Hispanic-origin non-reporting** — Oklahoma (1992-2002), Maryland (1992-1998), Massachusetts (1992-1997); NVSR 57-08 footnotes.
- **V1 plurality "5" anomaly (2005-2013)** — see `COMPARABILITY.md` §7.
- **V1 delivery method "3" anomaly (2006-2013)** — preserved per V1 baseline policy.
- **3 V2 1992 GA rows** — non-canonical single-digit `gestational_age_combined`; upstream NCHS bytes; all three have `birthweight=9999`.
- **V3b 1978-revision race** — 1-digit `MRACE` recode; codes 7+9 → null; see `V3b_1982_1988_LAYOUT_DECISIONS.md`.
