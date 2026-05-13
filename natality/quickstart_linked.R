#!/usr/bin/env Rscript
# Quickstart: U.S. Linked Birth-Infant Death Harmonized Dataset (v3, 2005-2023)
#
# R demo for the linked file (cohort-linked 2005-2023). Each record is a
# live birth with optional death-side fields filled when the infant died
# within the first year. Same canonical filter as natality
# (residence_status != 4) plus any death-side filter the analytic question
# requires.
#
# Uses arrow::open_dataset() rather than read_parquet() because the linked
# parquet has ~74.9M rows × 94 columns and exceeds typical R memory limits
# when materialized. open_dataset() returns a queryable handle; dplyr verbs
# are pushed down to Arrow and only the aggregated result is materialized.
#
# Run:
#
#   Rscript natality/quickstart_linked.R /path/to/natality_v3_linked_harmonized_derived.parquet
#
# Requires R packages: arrow, dplyr.

suppressPackageStartupMessages({
  library(arrow)
  library(dplyr)
})

args <- commandArgs(trailingOnly = TRUE)
parquet_path <- if (length(args) >= 1) args[[1]] else "natality_v3_linked_harmonized_derived.parquet"

if (!file.exists(parquet_path)) {
  stop(sprintf(
    "parquet not found at '%s'. Pass an explicit path as first argument.",
    parquet_path
  ))
}

# ============================================================
# 1. Open the dataset
# ============================================================
ds <- arrow::open_dataset(parquet_path)
total_rows <- ds %>% count() %>% collect() %>% pull(n)
cat(sprintf("Opened %s records, %d columns\n",
            format(total_rows, big.mark = ","), length(ds$schema$names)))

year_range <- ds %>%
  summarise(min_year = min(data_year), max_year = max(data_year)) %>%
  collect()
cat(sprintf("Years: %d-%d\n", year_range$min_year, year_range$max_year))

# ============================================================
# 2. Canonical analytic subset (U.S. residents)
# ============================================================
us_resident <- ds %>% filter(residence_status != 4)
us_count <- us_resident %>% count() %>% collect() %>% pull(n)
cat(sprintf("\nU.S. resident subset: %s records\n",
            format(us_count, big.mark = ",")))

# ============================================================
# 3. Infant mortality rate by year (per 1,000 live births)
# ============================================================
# infant_death = TRUE when the linked death record is present (died within
# 365 days). Compute IMR by year.
cat("\nInfant mortality rate by year (per 1,000 resident live births):\n")
imr_by_year <- us_resident %>%
  group_by(data_year) %>%
  summarise(
    births = n(),
    deaths = sum(infant_death, na.rm = TRUE)
  ) %>%
  arrange(data_year) %>%
  collect() %>%
  mutate(imr_per_1000 = deaths / births * 1000)

for (i in seq_len(nrow(imr_by_year))) {
  cat(sprintf("  %d: %s births, %s deaths, IMR = %.2f\n",
              imr_by_year$data_year[i],
              format(imr_by_year$births[i], big.mark = ","),
              format(imr_by_year$deaths[i], big.mark = ","),
              imr_by_year$imr_per_1000[i]))
}

# ============================================================
# 4. Neonatal vs postneonatal split
# ============================================================
death_split <- us_resident %>%
  filter(infant_death == TRUE) %>%
  summarise(
    neo = sum(neonatal_death, na.rm = TRUE),
    post = sum(postneonatal_death, na.rm = TRUE)
  ) %>%
  collect()
cat(sprintf("\nInfant deaths split: neonatal=%s; postneonatal=%s\n",
            format(death_split$neo, big.mark = ","),
            format(death_split$post, big.mark = ",")))

# ============================================================
# 5. Top causes (2014+; cause_group blank pre-2014)
# ============================================================
cat("\nTop 5 cause groups among infant deaths 2014+:\n")
recent_deaths <- us_resident %>%
  filter(infant_death == TRUE,
         data_year >= 2014,
         !is.na(cause_group),
         cause_group != "")
recent_total <- recent_deaths %>% count() %>% collect() %>% pull(n)
top_causes <- recent_deaths %>%
  count(cause_group, sort = TRUE) %>%
  collect() %>%
  slice_head(n = 5)
for (i in seq_len(nrow(top_causes))) {
  pct <- top_causes$n[i] / recent_total * 100
  cat(sprintf("  %s: %s (%.1f%%)\n",
              top_causes$cause_group[i],
              format(top_causes$n[i], big.mark = ","),
              pct))
}

cat("\nDone. See docs/JOINT_USE_GUIDE.md for cross-product analyses.\n")
