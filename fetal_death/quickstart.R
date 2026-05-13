#!/usr/bin/env Rscript
# Quickstart: U.S. Fetal Death Harmonized Dataset (v2.4.0, 1982-2022)
#
# R mirror of fetal_death/quickstart.py. Demonstrates basic loading and
# analysis of the harmonized fetal-death dataset across the 41-year envelope
# (1982-2002 V3a/V3b/V2 + 2005-2022 V1; 2003-2004 in V2.1).
#
# Run from the directory containing the unpacked Zenodo deposit (the directory
# that holds fetal_death_derived.parquet and live_births_by_year.csv), OR pass
# an explicit path:
#
#   Rscript fetal_death/quickstart.R /path/to/fetal_death_derived.parquet
#
# Requires R packages: arrow, dplyr.

suppressPackageStartupMessages({
  library(arrow)
  library(dplyr)
})

args <- commandArgs(trailingOnly = TRUE)
parquet_path <- if (length(args) >= 1) args[[1]] else "fetal_death_derived.parquet"

if (!file.exists(parquet_path)) {
  stop(sprintf(
    "parquet not found at '%s'. Pass an explicit path as first argument.",
    parquet_path
  ))
}

# ============================================================
# 1. Load the data
# ============================================================
df <- arrow::read_parquet(parquet_path)
cat(sprintf("Loaded %s records, %d columns\n",
            format(nrow(df), big.mark = ","), ncol(df)))
cat(sprintf("Years: %d-%d (%d distinct years)\n",
            min(df$data_year), max(df$data_year),
            length(unique(df$data_year))))

# ============================================================
# 2. Canonical analytic subset (>=20wk, U.S. residents)
# ============================================================
# tabulation_flag == 2 selects records meeting the NVSR >=20wk threshold;
# residence_status != 4 excludes foreign residents. This is the canonical
# HVS fetal-death filter for cross-era rates.
gte20 <- df %>% filter(tabulation_flag == 2, residence_status != 4)
cat(sprintf("\n>=20wk, U.S. resident subset: %s records\n",
            format(nrow(gte20), big.mark = ",")))

# ============================================================
# 3. Counts by year
# ============================================================
cat("\nFetal deaths >=20wk (resident) by year:\n")
counts_by_year <- gte20 %>% count(data_year) %>% arrange(data_year)
for (i in seq_len(nrow(counts_by_year))) {
  cat(sprintf("  %d: %s\n",
              counts_by_year$data_year[i],
              format(counts_by_year$n[i], big.mark = ",")))
}

# ============================================================
# 4. Sex distribution among >=20wk deaths
# ============================================================
# fetal_sex is M/F/U across all eras after the V2 B1 normalization.
known_sex <- gte20 %>% filter(fetal_sex %in% c("M", "F"))
male_pct <- mean(known_sex$fetal_sex == "M") * 100
cat(sprintf("\nMale %% among known-sex fetal deaths >=20wk: %.1f%%\n",
            male_pct))

# ============================================================
# 5. Preterm and LBW among >=20wk deaths
# ============================================================
known_preterm <- gte20 %>% filter(preterm %in% c("0", "1"))
preterm_pct <- mean(known_preterm$preterm == "1") * 100
cat(sprintf("Preterm (<37wk) among >=20wk deaths w/ known GA: %.1f%%\n",
            preterm_pct))

known_lbw <- gte20 %>% filter(lbw %in% c("0", "1"))
lbw_pct <- mean(known_lbw$lbw == "1") * 100
cat(sprintf("LBW (<2500g) among >=20wk deaths w/ known BW: %.1f%%\n",
            lbw_pct))

cat("\nDone. See fetal_death/COMPARABILITY.md for cross-era guidance,\n")
cat("including the three within_era columns to avoid in cross-era groupby.\n")
