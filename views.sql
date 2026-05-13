-- ============================================================
-- views.sql — DuckDB canonical-filter views over HVS parquets
-- ============================================================
--
-- Defines three product-level views applying each product's canonical
-- analytic filter, plus one cross-product aggregate view illustrating
-- the joint-use computation for fetal mortality rate.
--
-- Designed for the unpacked Zenodo deposit layout. Run from a directory
-- containing all three parquets at the root:
--
--   fetal_death_derived.parquet
--   live_births_by_year.csv
--   natality_v2_harmonized_derived.parquet
--   natality_v3_linked_harmonized_derived.parquet
--
-- Usage:
--
--   duckdb hvs.duckdb < views.sql
--   duckdb hvs.duckdb -c "SELECT * FROM fetal_mortality_rate_by_year LIMIT 5"
--
-- or via Python:
--
--   import duckdb
--   con = duckdb.connect()
--   con.execute(open("views.sql").read())
--   con.execute("SELECT * FROM fetal_mortality_rate_by_year").fetchdf()
--
-- or via R:
--
--   library(duckdb); con <- dbConnect(duckdb())
--   DBI::dbExecute(con, paste(readLines("views.sql"), collapse = "\n"))
--   DBI::dbGetQuery(con, "SELECT * FROM fetal_mortality_rate_by_year")
--
-- CREATE OR REPLACE means views can be re-sourced without errors.

-- ============================================================
-- 1. Fetal-death canonical view (>=20wk gestation, U.S. residents)
-- ============================================================
-- Filter matches the NVSR fetal-death analytic subset across all years
-- 1982-2024 (V3a + V3b + V2 + V2.1 + V1 + 2023-2024 extensions). The
-- tabulation_flag = 2 selects records meeting the >=20wk threshold; the
-- residence_status != 4 excludes foreign residents.
CREATE OR REPLACE VIEW fetal_death_canonical AS
SELECT *
FROM read_parquet('fetal_death_derived.parquet')
WHERE tabulation_flag = 2
  AND residence_status != 4;

-- ============================================================
-- 2. Natality canonical view (U.S. residents)
-- ============================================================
-- The canonical filter for natality is residence_status != 4 (exclude
-- foreign residents). This matches the denominator NCHS uses for the
-- per-year live-birth totals published in NVSR.
CREATE OR REPLACE VIEW natality_canonical AS
SELECT *
FROM read_parquet('natality_v2_harmonized_derived.parquet')
WHERE residence_status != 4;

-- ============================================================
-- 3. Linked birth-infant death canonical view (U.S. residents)
-- ============================================================
-- Same residence filter as natality. Each row is a live birth with
-- optional death-side fields filled when the infant died <365 days.
CREATE OR REPLACE VIEW linked_canonical AS
SELECT *
FROM read_parquet('natality_v3_linked_harmonized_derived.parquet')
WHERE residence_status != 4;

-- ============================================================
-- 4. Fetal mortality rate by year (cross-product joint-use)
-- ============================================================
-- Computes per-year fetal mortality rate using the standard NVSR
-- denominator (live births + fetal deaths >=20wk). Pre-aggregates each
-- side independently to avoid a record-level join across 138M+ natality
-- rows; then joins the small per-year aggregates.
--
-- This view illustrates the joint-use pattern documented in
-- docs/JOINT_USE_GUIDE.md. For race- or age-stratified rates, use the
-- same pattern but add the stratifier to both GROUP BY clauses.
CREATE OR REPLACE VIEW fetal_mortality_rate_by_year AS
WITH fd_counts AS (
  SELECT data_year, COUNT(*) AS fd_count
  FROM fetal_death_canonical
  GROUP BY data_year
),
lb_counts AS (
  SELECT data_year, COUNT(*) AS lb_count
  FROM natality_canonical
  GROUP BY data_year
)
SELECT
  fd.data_year,
  fd.fd_count AS fetal_deaths_gte20wk,
  lb.lb_count AS live_births,
  CAST(fd.fd_count AS DOUBLE) / (fd.fd_count + lb.lb_count) * 1000 AS fmr_per_1000
FROM fd_counts fd
INNER JOIN lb_counts lb USING (data_year)
ORDER BY fd.data_year;
