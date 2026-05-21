# Cover letter — Data Resource Profile submission

<!-- YP: add date, your affiliation/address, and the editor's name if known, before submitting. -->

To the Editors
*International Journal of Epidemiology*

Dear Editors,

I am pleased to submit **"Data Resource Profile: U.S. Harmonized Vital Statistics microdata, 1968–2024"** for consideration as a Data Resource Profile.

**The gap.** U.S. natality, linked birth–infant death, and fetal death public-use microdata are released by the National Center for Health Statistics (NCHS) as annual fixed-width files whose layouts change at every U.S. Standard Certificate revision (1968, 1978, 1989, 2003), at within-revision reformats, and across a state-by-state staggered adoption window. Because no openly published, reproducible, validated harmonized microdata product has existed, investigators have been forced into single-revision windows or have dropped variables across the boundary — most pointedly, Ananth and colleagues (2022) excluded Hispanic ethnicity from a 1980–2020 stillbirth analysis because the variable "was only made available in the revised 2003 birth certificates." NCHS performs the cross-revision harmonization internally, but only aggregate published tables survive.

**The resource.** HVS supplies the missing artifact: four companion Apache Parquet products — natality (201,161,456 records, 1968–2024), linked birth–infant death (149,386,620, 1983–2023), fetal death (2,427,233, 1982–2024), and matched multiples (1,665,568, 1995–2020) — each with one stable column schema spanning all the years it covers, in the spirit of IPUMS and the Human Mortality Database for their respective domains.

**The evidence.** Each product is validated, byte-exact under a documented analytic filter, against the per-year aggregates NCHS publishes: natality 183/183 *Births: Final Data* targets (1990–2024); the linked file 33/35 for 2005–2023 (the two remaining cells differ by exactly one record, from documented NCHS upstream survivor records with null weights) plus byte-exact pre-2005 cohort denominators; fetal death all 29 per-year published counts and 26 fetal-mortality rates; and matched multiples 13/13 documentation-table and structural checks. The pipelines are deterministic and re-runnable end-to-end from the public NCHS files, producing byte-identical parquets — a sceptical reader is asked not to trust the author but to re-build and diff.

**Availability.** The resource is openly deposited on Zenodo (DOI 10.5281/zenodo.20326150) under CC BY 4.0 with no data-use agreement or credentialing, and the pipelines are openly developed on GitHub (https://github.com/yoelplutchok/vital-statistics-harmonization) and included verbatim in the deposit.

The manuscript is original, is not under consideration elsewhere, and reports no prior publication of the resource as a Data Resource Profile. It has a single author with no competing interests and no funding to declare; use of AI tools is disclosed in the manuscript per IJE policy.

I believe HVS fits the Data Resource Profile remit — a reusable, documented, validated public resource — and I would be glad to respond to reviewer feedback.

Sincerely,

Yoel Plutchok
<!-- YP: affiliation and contact email -->
