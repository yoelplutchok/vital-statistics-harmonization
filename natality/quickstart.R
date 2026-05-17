#!/usr/bin/env Rscript
# Quickstart: U.S. Natality Harmonized Dataset (v3.0.0, 1968-2024)
#
# R companion to natality/notebooks/quickstart.ipynb. Demonstrates basic
# loading and analysis of the harmonized natality dataset across all 57 years.
#
# Uses arrow::open_dataset() rather than read_parquet() because the full
# natality parquet has ~201.2M rows × 84 columns and exceeds typical R memory
# limits when materialized. open_dataset() returns a queryable handle; dplyr
# verbs are pushed down to Arrow and only the aggregated result is brought
# into R memory.
#
# Run:
#
#   Rscript natality/quickstart.R /path/to/natality_v2_harmonized_derived.parquet
#
# Requires R packages: arrow, dplyr.

suppressPackageStartupMessages({
  library(arrow)
  library(dplyr)
})

args <- commandArgs(trailingOnly = TRUE)
parquet_path <- if (length(args) >= 1) args[[1]] else "natality_v2_harmonized_derived.parquet"

if (!file.exists(parquet_path)) {
  stop(sprintf(
    "parquet not found at '%s'. Pass an explicit path as first argument.",
    parquet_path
  ))
}

# ============================================================
# 1. Open the dataset (lazy — does not materialize into R memory)
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
# residence_status != 4 excludes foreign residents.
us_resident <- ds %>% filter(residence_status != 4)
us_count <- us_resident %>% count() %>% collect() %>% pull(n)
cat(sprintf("\nU.S. resident subset: %s records\n",
            format(us_count, big.mark = ",")))

# ============================================================
# 3. Counts by year
# ============================================================
cat("\nLive births (U.S. resident) by year:\n")
counts_by_year <- us_resident %>%
  count(data_year) %>%
  arrange(data_year) %>%
  collect()
for (i in seq_len(nrow(counts_by_year))) {
  cat(sprintf("  %d: %s\n",
              counts_by_year$data_year[i],
              format(counts_by_year$n[i], big.mark = ",")))
}

# ============================================================
# 4. Sex distribution (sex ratio at birth ~1.05 M/F)
# ============================================================
sex_counts <- us_resident %>%
  filter(infant_sex %in% c("M", "F")) %>%
  count(infant_sex) %>%
  collect()
n_m <- sex_counts$n[sex_counts$infant_sex == "M"]
n_f <- sex_counts$n[sex_counts$infant_sex == "F"]
cat(sprintf("\nMale %% among known-sex births: %.2f%%\n",
            n_m / (n_m + n_f) * 100))

# ============================================================
# 5. LBW and preterm rates (rates among known-value records)
# ============================================================
lbw_counts <- us_resident %>%
  filter(!is.na(low_birthweight)) %>%
  summarise(lbw = sum(low_birthweight), n = n()) %>%
  collect()
cat(sprintf("LBW (<2500g) rate among known-BW: %.2f%%\n",
            lbw_counts$lbw / lbw_counts$n * 100))

preterm_counts <- us_resident %>%
  filter(!is.na(preterm_lt37)) %>%
  summarise(pt = sum(preterm_lt37), n = n()) %>%
  collect()
cat(sprintf("Preterm (<37wk) rate among known-GA: %.2f%%\n",
            preterm_counts$pt / preterm_counts$n * 100))

# ============================================================
# 6. Certificate-revision adoption by year (% A-version)
# ============================================================
# A = 2003-revision; S = 1989-revision; tracks state-by-year adoption.
cat("\nCertificate-revision adoption by year (% A-version):\n")
revision_pct <- us_resident %>%
  filter(!is.na(certificate_revision)) %>%
  group_by(data_year) %>%
  summarise(n_a = sum(certificate_revision == "A"),
            n_total = n()) %>%
  mutate(pct_a = n_a / n_total * 100) %>%
  arrange(data_year) %>%
  collect()
for (i in seq_len(nrow(revision_pct))) {
  cat(sprintf("  %d: %.1f%%\n",
              revision_pct$data_year[i], revision_pct$pct_a[i]))
}

cat("\nDone. See natality/docs/COMPARABILITY.md for cross-era guidance.\n")
cat("For linked birth-infant death analysis, see natality/quickstart_linked.R.\n")
