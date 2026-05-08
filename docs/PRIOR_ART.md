# Prior art: the literature gap

This document collects the literature evidence that motivates the harmonization. It is the source for the corresponding paragraph in the Data Resource Profile manuscript.

## The gap

NCHS releases U.S. natality, linked birth–infant death, and fetal death public-use microdata as annual fixed-width files whose layouts change at three kinds of boundary: (i) the 1989-to-2003 Standard Certificate transition; (ii) within-revision NCHS reformats; and (iii) state-by-state staggered adoption of the 2003 revision. Users of these files have had no harmonized longitudinal microdata product to work with. The field has adapted by restricting analyses to single-revision windows.

## Cited adaptations in the literature

These citations appear in the manuscript's *Data resource basics* section as evidence that researchers have been forced into single-revision windows for lack of harmonized cross-revision microdata.

### Salihu et al. 2004 — single 1989-revision window (1995–1998)

> Salihu HM, Aliyu MH, Pierre-Louis BJ, Alexander GR. Racial disparity in stillbirth among singleton, twin, and triplet gestations in the United States. *Obstet Gynecol* 2004;104(4):734–740.

The four-year span 1995–1998 was chosen because it provided 1989-revision uniformity (no states had yet adopted the 2003 revision) and the maximum window for which the 1995 data block was internally consistent.

### Willinger et al. 2009 — last two years of 1989-revision uniformity

> Willinger M, Ko CW, Reddy UM. Racial disparities in stillbirth risk across gestation in the United States. *Am J Obstet Gynecol* 2009;201(5):469.e1–8.

Used 2001–2002 as the last two years before the staggered 2003-revision rollout began (2003 was the first year any state adopted the new certificate).

### Hogue & Silver 2011 — forced to aggregates

> Hogue CJR, Silver RM. Racial and ethnic disparities in United States: stillbirth rates, trends, risk factors, and research needs. *Semin Perinatol* 2011;35(4):221–233.

Surveying disparities through 2005, Hogue and Silver were forced to operate on aggregate published rates rather than microdata because the 2003-revision rollout was mid-flight.

### Ananth et al. 2022 — explicitly excluded Hispanic ethnicity

> Ananth CV, Fields JC, Brandt JS, Graham HL, Keyes KM, Zeitlin J. Evolving stillbirth rates among Black and White women in the United States, 1980–2020: a population-based study. *Lancet Reg Health Am* 2022;16:100380.

This is the most pointed citation. Ananth and colleagues explicitly excluded Hispanic ethnicity from their age-period-cohort analysis spanning 1980–2020 because the variable "was only made available in the revised 2003 birth certificates"—i.e., because no cross-revision harmonized microdata existed to support inclusion of Hispanic ethnicity across the boundary.

## NCHS itself harmonizes — but only at the aggregate level

NCHS publishes harmonized cross-revision tabulations in:

- *Births: Final Data* (NVSR; annual)
- *Fetal and Perinatal Mortality, United States* (NVSR; periodic; the 2022 edition is *NVSR 73(09)*; an earlier edition covering 1995–2005 is *NVSR 57(08)*)
- *Linked Birth/Infant Death Data Set* (NCHS; annual)

These are aggregate tables, not microdata. NCHS performs the harmonization internally on a fixed tabulation grid, and only the published cells survive. Researchers wanting microdata-level cross-revision analyses have had to redo the harmonization themselves—the work this resource performs once and for all.

## Adjacent harmonized resources (none cover U.S. vital statistics)

- **IPUMS-International** — harmonized census microdata across countries. Sobek M, Cleveland L, Flood S, et al. *Data Resource Profile: IPUMS-International*. *International Journal of Epidemiology* 2017;46(2):390. https://doi.org/10.1093/ije/dyx012
- **Human Mortality Database (HMD)** — harmonized national mortality and life-table data. Barbieri M, Wilmoth JR, Shkolnikov VM, et al. *Data Resource Profile: The Human Mortality Database*. *International Journal of Epidemiology* 2015;44(5):1549–1556. https://doi.org/10.1093/ije/dyv105
- **IPUMS Health Surveys (NHIS)** — harmonized health-survey microdata 1963 onward.
- **NBER vital-statistics archive** — redistributes NCHS public-use files but does not harmonize across revisions.

None of these covers U.S. natality, linked birth–infant death, or fetal death microdata.

## What this resource adds

A single harmonized parquet column schema per product, spanning all three boundary types, validated against every per-year aggregate NCHS publishes in the relevant *NVSR* series. The harmonization is performed once, in the open, with deterministic re-runnable pipelines, so future researchers do not need to repeat it.
