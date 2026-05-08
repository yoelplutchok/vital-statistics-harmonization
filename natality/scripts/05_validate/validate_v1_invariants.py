#!/usr/bin/env python3
"""
Validate internal invariants of the V1 harmonized + derived file.

This is a regression-style check: it verifies that key derived fields are internally
consistent and that known structural coverage constraints (e.g., revised-only domains
in 2009–2013 public-use files) still hold.

Outputs:
- Default (2005–2015): `output/validation/v1_invariants_report.md` and `output/validation/v1_invariants_year_summary.csv`
- Other year ranges: `output/validation/invariants_report_{min}_{max}.md` and `output/validation/invariants_year_summary_{min}_{max}.csv`
"""

from __future__ import annotations

import argparse
import csv
from dataclasses import dataclass
from pathlib import Path

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.parquet as pq


@dataclass
class YearStats:
    year: int
    rows_total: int = 0
    rows_resident: int = 0
    cert_revised: int = 0
    cert_unrevised: int = 0
    cert_unknown: int = 0
    # For 2009–2013, unrevised rows should have revised-only domains missing.
    unrevised_rows_2009_2013: int = 0
    unrevised_educ_nonnull_2009_2013: int = 0
    unrevised_pnmonth_nonnull_2009_2013: int = 0
    unrevised_smokeint_nonnull_2009_2013: int = 0


def parse_args() -> argparse.Namespace:
    repo_root = Path(__file__).resolve().parents[2]
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--in",
        dest="in_path",
        type=Path,
        default=repo_root / "output" / "harmonized" / "natality_v2_harmonized_derived.parquet",
        help="Input derived Parquet path",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=repo_root / "output" / "validation",
        help="Directory to write outputs",
    )
    p.add_argument(
        "--years",
        type=str,
        default="2005-2015",
        help="Comma years or range like 2005-2015",
    )
    p.add_argument(
        "--batch-rows",
        type=int,
        default=750_000,
        help="Rows per Parquet batch scan",
    )
    return p.parse_args()


def _count_true(arr: pa.Array) -> int:
    return int(pc.sum(pc.cast(arr, pa.int64())).as_py() or 0)


def _ne(a, b):
    """Null-safe inequality. Returns True when a and b are definitely not equal
    (treating null as a value). Use this in invariant checks so that a null
    violation does not silently read as 0."""
    eq = pc.equal(a, b)
    a_null = pc.is_null(a)
    b_null = pc.is_null(b)
    one_null_one_not = pc.xor(a_null, b_null)
    both_null = pc.and_(a_null, b_null)
    # not_equal when: neither is null AND eq is False, OR exactly one is null.
    neither_null_but_ne = pc.fill_null(pc.invert(eq), False)
    return pc.or_(neither_null_but_ne, one_null_one_not)


def _safe_and(*parts):
    """Null-safe AND: treat null operands as False so that a null condition
    cannot silently propagate through pc.and_ and suppress a violation."""
    from functools import reduce
    return reduce(pc.and_, (pc.fill_null(p, False) for p in parts))


def _parse_years(spec: str) -> list[int]:
    spec = spec.strip()
    if "-" in spec and "," not in spec:
        a, b = spec.split("-", 1)
        return list(range(int(a), int(b) + 1))
    return [int(x.strip()) for x in spec.split(",") if x.strip()]


def main() -> None:
    args = parse_args()
    if not args.in_path.is_file():
        raise FileNotFoundError(args.in_path)
    args.out_dir.mkdir(parents=True, exist_ok=True)

    pf = pq.ParquetFile(args.in_path)
    cols = set(pf.schema_arrow.names)

    required = {
        "year",
        "is_foreign_resident",
        "certificate_revision",
        "maternal_hispanic_origin",
        "maternal_hispanic",
        "maternal_race_bridged4",
        "maternal_race_ethnicity_5",
        "maternal_education_cat4",
        "prenatal_care_start_month",
        "smoking_any_during_pregnancy",
        "smoking_intensity_max_recode6",
        "gestational_age_weeks_source",
        "gestational_age_weeks",
        "gestational_age_weeks_clean",
        "birthweight_grams",
        "birthweight_grams_clean",
        "apgar5",
        "apgar5_clean",
        "low_birthweight",
        "preterm_lt37",
        "plurality_recode",
        "singleton",
        "infant_sex",
    }
    missing = sorted(required - cols)
    if missing:
        raise RuntimeError(f"Missing required columns: {missing}")

    years = _parse_years(args.years)
    if not years:
        raise ValueError("No years specified")
    min_year = min(years)
    max_year = max(years)
    suffix = f"{min_year}_{max_year}" if min_year != max_year else f"{min_year}"
    ys = {y: YearStats(year=y) for y in years}

    # Scalars for comparisons
    s_revised = pa.scalar("revised_2003", type=pa.string())
    s_unrevised = pa.scalar("unrevised_1989", type=pa.string())
    s_unknown = pa.scalar("unknown", type=pa.string())
    s_hispanic = pa.scalar("Hispanic", type=pa.string())
    s_nh_white = pa.scalar("NH_white", type=pa.string())
    s_nh_black = pa.scalar("NH_black", type=pa.string())
    s_nh_aian = pa.scalar("NH_aian", type=pa.string())
    s_nh_aspi = pa.scalar("NH_asian_pi", type=pa.string())
    s_combined = pa.scalar("combined", type=pa.string())
    s_ob = pa.scalar("obstetric_estimate", type=pa.string())

    # Global invariant violation counters (should be 0)
    violations: dict[str, int] = {
        # plausible range checks
        "year_outside_expected_range": 0,
        "bw_out_of_range": 0,
        "ga_out_of_range": 0,
        # categorical-frame checks (non-null values must lie in the documented code set)
        "mrace15_invalid_when_nonnull": 0,
        # smoking consistency
        "smoke_int_0_not_false": 0,
        "smoke_int_1_5_not_true": 0,
        "smoke_int_6_not_null_any": 0,
        "smoke_any_true_bad_int": 0,
        "smoke_any_false_bad_int": 0,
        # hispanic consistency
        "hisp_origin_0_not_false": 0,
        "hisp_origin_1_5_not_true": 0,
        "hisp_origin_9_not_null": 0,
        # race/ethnicity consistency
        "race_eth_hisp_not_hispanic": 0,
        "race_eth_nh_bad_mapping": 0,
        # race_eth must not be null when the source signals are present enough to label.
        # Added after the 2020+ 100%-null-race_eth bug (audit C2) escaped consistency checks.
        "race_eth_null_when_hisp_true": 0,
        "race_eth_null_when_hisp_false_and_race_detail_valid": 0,
        # gestation source consistency
        "gest_src_pre2014_obstetric": 0,
        # sentinel clean consistency
        "ga99_clean_not_null": 0,
        "bw9999_clean_not_null": 0,
        "apgar99_clean_not_null": 0,
        # derived logic checks
        "lbw_logic_mismatch": 0,
        "preterm_logic_mismatch": 0,
        "singleton_logic_mismatch": 0,
        # certificate revision validity
        "cert_rev_invalid_value": 0,
        "cert_rev_2014plus_not_revised": 0,
        # revised-only coverage constraints
        "unrevised_2009_2013_has_educ": 0,
        "unrevised_2009_2013_has_pnmonth": 0,
        "unrevised_2009_2013_has_smokeint": 0,
        # new variable era-coverage checks
        "ca_nonnull_pre2014": 0,
        "infection_nonnull_pre2014": 0,
        "prior_ces_count_nonnull_pre2005": 0,
        "prior_ces_count_99_post2014": 0,
        "fertility_nonnull_pre2014": 0,
        "art_nonnull_pre2014": 0,
        "father_educ_nonnull_1995_2008": 0,
        "father_hisp_race_eth_mismatch": 0,
        "payment_source_nonnull_pre2009": 0,
        # post-V4 additions (audit AUDIT_REPORT_V4.md gaps G1 + V4 suggestion)
        "delivery_method_recode_invalid_value": 0,
        # Year-aware companion (added after the combined 2026-04-22 audit):
        # 2005+ DMETH_REC only takes values {1, 2, 9}; codes 3 or 4 in a 2005+ row
        # indicate a regression in the 2003/2004 DELMETH5→9 remap branch.
        "delivery_method_recode_post2004_out_of_set": 0,
        "record_weight_null_when_survivor": 0,
        # Symmetric check for deaths (added after the 2026-04-22 audit): a death
        # with null record_weight is a data-integrity violation (weights are
        # supposed to be ≥ 1.0 on linked death rows). Currently 0 in V3 linked.
        "record_weight_null_when_death": 0,
    }

    # Optional columns for new-variable invariant checks
    optional_new = [
        "ca_anencephaly",
        "infection_gonorrhea",
        "prior_cesarean_count",
        "fertility_enhancing_drugs",
        "assisted_reproductive_tech",
        "father_education_cat4",
        "father_hispanic",
        "father_race_ethnicity_5",
        "payment_source_recode",
        # Included regardless of era — always in V2 and V3. Listed here so the
        # batch reader will pull them when present.
        "delivery_method_recode",
        # V3-linked-only; the record_weight_null_when_survivor and
        # record_weight_null_when_death invariants silently skip when the
        # column is absent (V2 natality).
        "record_weight",
        "infant_death",
        # Categorical-frame check (mrace15_invalid_when_nonnull).
        "maternal_race_detail_15cat",
    ]
    has_new_cols = {c: (c in cols) for c in optional_new}

    # Auto-detect V3 linked input. V3 has a genuine upstream-source divergence
    # from V2 on 2009–2010 unrevised-cert rows: the linked denominator-plus layout
    # for 2005–2013 retains MEDUC_REC / MPCB / CIG_1-3 bytes that the natality
    # 2009–2010 public-use layout drops, so `maternal_education_cat4`,
    # `prenatal_care_start_month`, and `smoking_intensity_max_recode6` are
    # populated on ~2M V3 unrevised-cert rows where V2 leaves them null. Skip
    # those three V2-only coverage invariants in V3 mode rather than nulling real
    # upstream data — see `docs/COMPARABILITY.md` §"V3 linked vs V2 natality:
    # 2009–2010 unrevised-cert field retention".
    #
    # Detection requires BOTH `infant_death` AND `record_weight` to be present,
    # not just `infant_death`. A future V2 enhancement that adds an
    # `infant_death`-named column derived from natality alone would otherwise
    # silently flip the validator into V3 mode and skip three V2 invariants.
    is_v3_linked = has_new_cols["infant_death"] and has_new_cols["record_weight"]

    # Known upstream-NCHS exceptions (expected counts). A V3 linked run should
    # report these values exactly; any deviation is a FAIL.
    # Documented in `docs/VALIDATION.md` and `docs/COMPARABILITY.md`.
    KNOWN_EXCEPTIONS: dict[str, int] = (
        {"record_weight_null_when_survivor": 2} if is_v3_linked else {}
    )

    # Invariants skipped entirely in V3 linked mode (see is_v3_linked note above).
    V3_SKIP: set[str] = (
        {
            "unrevised_2009_2013_has_educ",
            "unrevised_2009_2013_has_pnmonth",
            "unrevised_2009_2013_has_smokeint",
        }
        if is_v3_linked
        else set()
    )

    batch_cols = [
        "year",
        "is_foreign_resident",
        "certificate_revision",
        "maternal_hispanic_origin",
        "maternal_hispanic",
        "maternal_race_bridged4",
        "maternal_race_ethnicity_5",
        "maternal_race_detail",
        "maternal_education_cat4",
        "prenatal_care_start_month",
        "smoking_any_during_pregnancy",
        "smoking_intensity_max_recode6",
        "gestational_age_weeks_source",
        "gestational_age_weeks",
        "gestational_age_weeks_clean",
        "birthweight_grams",
        "birthweight_grams_clean",
        "apgar5",
        "apgar5_clean",
        "low_birthweight",
        "preterm_lt37",
        "plurality_recode",
        "singleton",
        "infant_sex",
    ] + [c for c in optional_new if has_new_cols[c]]

    _CORE_COUNT = 24  # number of core columns before optional new ones

    for batch in pf.iter_batches(batch_size=args.batch_rows, columns=batch_cols):
        (
            year,
            foreign,
            cert_rev,
            hisp_origin,
            hisp,
            race4,
            race_eth,
            race_detail_arr,
            educ,
            pnmonth,
            smoke_any,
            smoke_int,
            gest_src,
            ga,
            ga_clean,
            bw,
            bw_clean,
            apgar,
            apgar_clean,
            lbw,
            preterm,
            plur,
            singleton,
            sex,
        ) = batch.columns[:_CORE_COUNT]

        # Basic masks
        is_res = pc.fill_null(pc.and_(pc.is_valid(foreign), pc.invert(foreign)), False)

        # Track per-year totals (streaming)
        present_years = [int(y) for y in pc.unique(year).to_pylist() if y is not None]
        for y in present_years:
            if y not in ys:
                continue
            m_y = pc.equal(year, y)
            ys[y].rows_total += _count_true(m_y)
            ys[y].rows_resident += _count_true(pc.and_(m_y, is_res))

            # certificate revision counts
            m_rev = pc.and_(m_y, pc.equal(cert_rev, s_revised))
            m_unrev = pc.and_(m_y, pc.equal(cert_rev, s_unrevised))
            m_unk = pc.and_(m_y, pc.equal(cert_rev, s_unknown))
            ys[y].cert_revised += _count_true(m_rev)
            ys[y].cert_unrevised += _count_true(m_unrev)
            ys[y].cert_unknown += _count_true(m_unk)

            # revised-only domains among unrevised records in 2009–2013
            if 2009 <= y <= 2013:
                m_unrev_y = m_unrev
                ys[y].unrevised_rows_2009_2013 += _count_true(m_unrev_y)
                ys[y].unrevised_educ_nonnull_2009_2013 += _count_true(
                    pc.and_(m_unrev_y, pc.invert(pc.is_null(educ)))
                )
                ys[y].unrevised_pnmonth_nonnull_2009_2013 += _count_true(
                    pc.and_(m_unrev_y, pc.invert(pc.is_null(pnmonth)))
                )
                ys[y].unrevised_smokeint_nonnull_2009_2013 += _count_true(
                    pc.and_(m_unrev_y, pc.invert(pc.is_null(smoke_int)))
                )

        # ----- Global invariant checks -----

        # Year must be within expected range
        year_ok = pc.and_(
            pc.greater_equal(year, min_year),
            pc.less_equal(year, max_year),
        )
        violations["year_outside_expected_range"] += _count_true(pc.invert(year_ok))

        # Birthweight plausible range: valid non-sentinel values should be 100-8165
        bw_valid = pc.is_valid(bw_clean)
        bw_range_ok = pc.and_(pc.greater_equal(bw_clean, 100), pc.less_equal(bw_clean, 8165))
        violations["bw_out_of_range"] += _count_true(pc.and_(bw_valid, pc.invert(bw_range_ok)))

        # Gestational age plausible range: valid non-sentinel values should be 12-47
        ga_valid = pc.is_valid(ga_clean)
        ga_range_ok = pc.and_(pc.greater_equal(ga_clean, 12), pc.less_equal(ga_clean, 47))
        violations["ga_out_of_range"] += _count_true(pc.and_(ga_valid, pc.invert(ga_range_ok)))

        # APGAR5 sentinel clean consistency
        violations["apgar99_clean_not_null"] += _count_true(
            pc.and_(pc.equal(apgar, 99), pc.is_valid(apgar_clean))
        )

        # certificate_revision allowed values.
        # Null-safe: a null cert_rev is itself a violation (cert_rev should never be null
        # in the harmonized output). Prior to the V4 audit this check used raw pc.or_
        # and would silently count null cert_rev as "not a violation" (null-FN class, G2).
        is_valid_cert_raw = pc.or_(
            pc.or_(pc.equal(cert_rev, s_revised), pc.equal(cert_rev, s_unrevised)),
            pc.equal(cert_rev, s_unknown),
        )
        violations["cert_rev_invalid_value"] += _count_true(
            pc.invert(pc.fill_null(is_valid_cert_raw, False))
        )

        # 2014+ must be revised_2003 (per V1 policy and implementation).
        # AUDIT D9: use _safe_and to guard against a future regression that
        # ever introduces a null cert_rev value — null-in-cond would otherwise
        # silently drop from the violation counter.
        y2014plus = pc.greater_equal(year, 2014)
        violations["cert_rev_2014plus_not_revised"] += _count_true(
            _safe_and(y2014plus, pc.invert(pc.fill_null(pc.equal(cert_rev, s_revised), False)))
        )

        # revised-only coverage constraints (2009–2013 unrevised should not have these)
        y2009_2013 = pc.and_(pc.greater_equal(year, 2009), pc.less_equal(year, 2013))
        is_unrev = pc.equal(cert_rev, s_unrevised)
        violations["unrevised_2009_2013_has_educ"] += _count_true(
            _safe_and(y2009_2013, is_unrev, pc.invert(pc.is_null(educ)))
        )
        violations["unrevised_2009_2013_has_pnmonth"] += _count_true(
            _safe_and(y2009_2013, is_unrev, pc.invert(pc.is_null(pnmonth)))
        )
        violations["unrevised_2009_2013_has_smokeint"] += _count_true(
            _safe_and(y2009_2013, is_unrev, pc.invert(pc.is_null(smoke_int)))
        )

        # smoking consistency
        # In 2003+, smoke_any is derived from smoke_intensity, so they must be consistent.
        # In 1990-2002, TOBACCO and CIGAR6 are independent source fields, so
        # TOBACCO=1 (smoker) with CIGAR6=6 (unknown intensity) is a valid source
        # data pattern, not a harmonization bug.  Restrict these checks to 2003+.
        is_2003plus = pc.greater_equal(year, 2003)

        int_is_0 = pc.equal(smoke_int, 0)
        int_is_6 = pc.equal(smoke_int, 6)
        int_is_1_5 = pc.and_(pc.greater_equal(smoke_int, 1), pc.less_equal(smoke_int, 5))

        violations["smoke_int_0_not_false"] += _count_true(_safe_and(is_2003plus, int_is_0, _ne(smoke_any, pa.scalar(False))))
        violations["smoke_int_1_5_not_true"] += _count_true(_safe_and(is_2003plus, int_is_1_5, _ne(smoke_any, pa.scalar(True))))
        violations["smoke_int_6_not_null_any"] += _count_true(_safe_and(is_2003plus, int_is_6, pc.is_valid(smoke_any)))

        violations["smoke_any_true_bad_int"] += _count_true(
            _safe_and(is_2003plus, pc.equal(smoke_any, True), pc.invert(pc.fill_null(int_is_1_5, False)))
        )
        violations["smoke_any_false_bad_int"] += _count_true(
            _safe_and(is_2003plus, pc.equal(smoke_any, False), pc.invert(pc.fill_null(int_is_0, False)))
        )

        # Hispanic consistency
        origin0 = pc.equal(hisp_origin, 0)
        origin1_5 = pc.and_(pc.greater_equal(hisp_origin, 1), pc.less_equal(hisp_origin, 5))
        origin9 = pc.equal(hisp_origin, 9)

        violations["hisp_origin_0_not_false"] += _count_true(_safe_and(origin0, _ne(hisp, pa.scalar(False))))
        violations["hisp_origin_1_5_not_true"] += _count_true(_safe_and(origin1_5, _ne(hisp, pa.scalar(True))))
        violations["hisp_origin_9_not_null"] += _count_true(_safe_and(origin9, pc.is_valid(hisp)))

        # Race/ethnicity mapping consistency
        # Null-safe: a null race_eth when hisp=True is a VIOLATION, not "no data".
        violations["race_eth_hisp_not_hispanic"] += _count_true(
            _safe_and(pc.equal(hisp, True), _ne(race_eth, s_hispanic))
        )

        # Explicit non-null-when-expected checks. These would have caught the
        # 2020+ 100%-null bug (audit C2) on their own.
        violations["race_eth_null_when_hisp_true"] += _count_true(
            _safe_and(pc.equal(hisp, True), pc.is_null(race_eth))
        )
        # For non-Hispanic births with a race_detail code that SHOULD map to a
        # single bridged group, maternal_race_ethnicity_5 must not be null.
        # Excluded by design (documented null-bridges):
        #   - Pre-2003 MRACE codes 09-17 and 69-99 ("other"/unknown; no bridge available)
        #   - 2020+ MRACE6 code 6 (multiracial; cannot be bridged to a single group)
        # Era-aware rule:
        #   - Pre-2020 (2-digit MRACE detail): rd_int in {01-08, 18-68} should bridge.
        #   - 2020+ (1-digit MRACE6): rd_int in {1-5} should bridge (code 6 stays null).
        rd_int = pc.cast(
            pc.if_else(
                pc.fill_null(pc.equal(pc.utf8_trim_whitespace(race_detail_arr), ""), False),
                pa.scalar(None, type=pa.string()),
                pc.utf8_trim_whitespace(race_detail_arr),
            ),
            pa.int16(), safe=False,
        )
        y_pre2020 = pc.less(year, 2020)
        y_2020plus = pc.greater_equal(year, 2020)
        pre2020_bridge = pc.or_(
            pc.and_(
                pc.fill_null(pc.greater_equal(rd_int, 1), False),
                pc.fill_null(pc.less_equal(rd_int, 8), False),
            ),
            pc.and_(
                pc.fill_null(pc.greater_equal(rd_int, 18), False),
                pc.fill_null(pc.less_equal(rd_int, 68), False),
            ),
        )
        post2020_bridge = pc.and_(
            pc.fill_null(pc.greater_equal(rd_int, 1), False),
            pc.fill_null(pc.less_equal(rd_int, 5), False),
        )
        should_bridge = pc.or_(_safe_and(y_pre2020, pre2020_bridge), _safe_and(y_2020plus, post2020_bridge))
        violations["race_eth_null_when_hisp_false_and_race_detail_valid"] += _count_true(
            _safe_and(pc.equal(hisp, False), should_bridge, pc.is_null(race_eth))
        )
        # For non-Hispanic (hisp == False), race_eth must match race4 mapping when race4 is present.
        is_nh = pc.equal(hisp, False)
        race4_1 = pc.equal(race4, 1)
        race4_2 = pc.equal(race4, 2)
        race4_3 = pc.equal(race4, 3)
        race4_4 = pc.equal(race4, 4)
        mapped_ok = pc.or_(
            pc.or_(
                pc.and_(race4_1, pc.equal(race_eth, s_nh_white)),
                pc.and_(race4_2, pc.equal(race_eth, s_nh_black)),
            ),
            pc.or_(
                pc.and_(race4_3, pc.equal(race_eth, s_nh_aian)),
                pc.and_(race4_4, pc.equal(race_eth, s_nh_aspi)),
            ),
        )
        # Only enforce when non-Hispanic and race4 is present (1-4)
        race4_present = pc.and_(pc.greater_equal(race4, 1), pc.less_equal(race4, 4))
        violations["race_eth_nh_bad_mapping"] += _count_true(
            _safe_and(is_nh, race4_present, pc.invert(pc.fill_null(mapped_ok, False)))
        )

        # Gestation source consistency (no obstetric estimate pre-2014)
        pre2014 = pc.less_equal(year, 2013)
        violations["gest_src_pre2014_obstetric"] += _count_true(
            _safe_and(pre2014, pc.equal(gest_src, s_ob))
        )

        # Sentinel clean consistency
        violations["ga99_clean_not_null"] += _count_true(_safe_and(pc.equal(ga, 99), pc.is_valid(ga_clean)))
        violations["bw9999_clean_not_null"] += _count_true(_safe_and(pc.equal(bw, 9999), pc.is_valid(bw_clean)))

        # Derived logic consistency (where clean values are present).
        # Null-safe: a null derived boolean (e.g. lbw=null) when bw_clean is known
        # is a genuine violation that used to be silently suppressed.
        lbw_expected = pc.less(bw_clean, 2500)
        violations["lbw_logic_mismatch"] += _count_true(
            _safe_and(pc.is_valid(bw_clean), _ne(lbw, lbw_expected))
        )

        pre_expected = pc.less(ga_clean, 37)
        violations["preterm_logic_mismatch"] += _count_true(
            _safe_and(pc.is_valid(ga_clean), _ne(preterm, pre_expected))
        )

        singleton_expected = pc.equal(plur, 1)
        violations["singleton_logic_mismatch"] += _count_true(
            _safe_and(pc.is_valid(plur), _ne(singleton, singleton_expected))
        )

        # ----- New variable invariant checks -----
        pre2014 = pc.less(year, 2014)

        # AUDIT D9: wrap era-coverage checks in _safe_and so a null year or null
        # target column cannot silently drop rows from the violation counters.
        if has_new_cols["ca_anencephaly"]:
            ca_col = batch.column("ca_anencephaly")
            violations["ca_nonnull_pre2014"] += _count_true(_safe_and(pre2014, pc.is_valid(ca_col)))

        if has_new_cols["infection_gonorrhea"]:
            inf_col = batch.column("infection_gonorrhea")
            violations["infection_nonnull_pre2014"] += _count_true(_safe_and(pre2014, pc.is_valid(inf_col)))

        if has_new_cols["prior_cesarean_count"]:
            pcc = batch.column("prior_cesarean_count")
            # AUDIT D3: prior_cesarean_count is populated on revised-cert rows
            # starting 2005 (RF_CESARN@325-326 in 2005-2013 spec; @332-333 in 2014+).
            # Pre-2005 has no RF_CESARN field — should be 100% null there.
            pre2005 = pc.less(year, 2005)
            violations["prior_ces_count_nonnull_pre2005"] += _count_true(_safe_and(pre2005, pc.is_valid(pcc)))
            violations["prior_ces_count_99_post2014"] += _count_true(
                _safe_and(pc.greater_equal(year, 2014), pc.equal(pcc, pa.scalar(99, type=pa.int8())))
            )

        if has_new_cols["fertility_enhancing_drugs"]:
            fert = batch.column("fertility_enhancing_drugs")
            violations["fertility_nonnull_pre2014"] += _count_true(_safe_and(pre2014, pc.is_valid(fert)))

        if has_new_cols["assisted_reproductive_tech"]:
            art = batch.column("assisted_reproductive_tech")
            violations["art_nonnull_pre2014"] += _count_true(_safe_and(pre2014, pc.is_valid(art)))

        if has_new_cols["father_education_cat4"]:
            feduc = batch.column("father_education_cat4")
            y1995_2008 = pc.and_(pc.greater_equal(year, 1995), pc.less_equal(year, 2008))
            violations["father_educ_nonnull_1995_2008"] += _count_true(_safe_and(y1995_2008, pc.is_valid(feduc)))

        if has_new_cols["father_hispanic"] and has_new_cols["father_race_ethnicity_5"]:
            f_hisp = batch.column("father_hispanic")
            f_re5 = batch.column("father_race_ethnicity_5")
            # If father_hispanic == True and father_race_ethnicity_5 is valid,
            # it must be "Hispanic".  Uses _safe_and + _ne to stay null-safe.
            violations["father_hisp_race_eth_mismatch"] += _count_true(
                _safe_and(
                    pc.equal(f_hisp, True),
                    pc.is_valid(f_re5),
                    _ne(f_re5, pa.scalar("Hispanic", type=pa.string())),
                )
            )

        if has_new_cols["payment_source_recode"]:
            pay = batch.column("payment_source_recode")
            pre2009 = pc.less(year, 2009)
            violations["payment_source_nonnull_pre2009"] += _count_true(_safe_and(pre2009, pc.is_valid(pay)))

        # G1 (post-V4): delivery_method_recode must be in {1, 2, 3, 4, 9} when populated.
        # Catches (a) regression of the 2003-2004 DELMETH5→9 remap, (b) post-2004 code-5
        # leaks, and (c) any future parser bug that writes an unexpected integer.
        if has_new_cols["delivery_method_recode"]:
            dmr = batch.column("delivery_method_recode")
            in_allowed = pc.fill_null(
                pc.or_(
                    pc.or_(
                        pc.or_(pc.equal(dmr, pa.scalar(1, type=pa.int8())),
                               pc.equal(dmr, pa.scalar(2, type=pa.int8()))),
                        pc.or_(pc.equal(dmr, pa.scalar(3, type=pa.int8())),
                               pc.equal(dmr, pa.scalar(4, type=pa.int8()))),
                    ),
                    pc.equal(dmr, pa.scalar(9, type=pa.int8())),
                ),
                False,
            )
            violations["delivery_method_recode_invalid_value"] += _count_true(
                _safe_and(pc.is_valid(dmr), pc.invert(in_allowed))
            )

            # Year-aware companion: 2005+ DMETH_REC only takes {1, 2, 9}, so a
            # 2005+ row with code 3 or 4 indicates either (a) a regression in
            # the 2003/2004 DELMETH5→9 remap branch or (b) garbage data.
            y_post2004 = pc.greater_equal(year, 2005)
            dmr_is_3_or_4 = pc.or_(
                pc.equal(dmr, pa.scalar(3, type=pa.int8())),
                pc.equal(dmr, pa.scalar(4, type=pa.int8())),
            )
            violations["delivery_method_recode_post2004_out_of_set"] += _count_true(
                _safe_and(y_post2004, pc.is_valid(dmr), dmr_is_3_or_4)
            )

        # V4 suggestion: record_weight must not be null for survivors.
        # V3-linked-only; silently skipped when both columns aren't present.
        if has_new_cols["record_weight"] and has_new_cols["infant_death"]:
            rw = batch.column("record_weight")
            dead = batch.column("infant_death")
            violations["record_weight_null_when_survivor"] += _count_true(
                _safe_and(pc.equal(dead, pa.scalar(False)), pc.is_null(rw))
            )
            # Symmetric check: deaths must not have null record_weight.
            violations["record_weight_null_when_death"] += _count_true(
                _safe_and(pc.equal(dead, pa.scalar(True)), pc.is_null(rw))
            )

        # F16 (2026-04-22 audit): maternal_race_detail_15cat must contain only
        # values matching /^(0[1-9]|1[0-5])$/ when non-null. This is the
        # categorical-frame check that would have caught the 2003/2004 garbage
        # (2-letter alpha codes like 'AC', 'XT', 'KA', 'LF') on ingest.
        if has_new_cols["maternal_race_detail_15cat"]:
            r15 = batch.column("maternal_race_detail_15cat")
            # Trim any accidental padding before matching
            r15_trim = pc.utf8_trim_whitespace(pc.cast(r15, pa.string()))
            nonblank = pc.fill_null(pc.and_(pc.is_valid(r15_trim), pc.not_equal(r15_trim, "")), False)
            # Validity: any of the numeric labels "01".."15"
            valid_labels = [f"{i:02d}" for i in range(1, 16)]
            is_valid_label = pc.fill_null(
                pc.is_in(r15_trim, value_set=pa.array(valid_labels, type=pa.string())),
                False,
            )
            violations["mrace15_invalid_when_nonnull"] += _count_true(
                _safe_and(nonblank, pc.invert(is_valid_label))
            )

    # ===== Null-rate discontinuity detection =====
    # Second pass: compute per-variable, per-year null rates and flag >5 ppt year-over-year jumps.
    null_rate_cols = [
        "marital_status", "maternal_hispanic", "maternal_race_bridged4",
        "maternal_race_ethnicity_5", "maternal_education_cat4",
        "prenatal_care_start_month", "smoking_any_during_pregnancy",
        "smoking_intensity_max_recode6", "diabetes_any", "hypertension_chronic",
        "hypertension_gestational", "gestational_age_weeks", "birthweight_grams",
        "delivery_method_recode", "apgar5", "father_age",
        # Added 2026-04-22 audit: would have flagged MRACE15 garbage (2002→2003
        # and 2004→2005 null-rate swings of ±100 ppt) as a loud signal of F1.
        "maternal_race_detail", "maternal_race_detail_15cat",
    ]
    null_rate_cols = [c for c in null_rate_cols if c in cols]

    # {(year, col): [n_total, n_null]}
    null_counts: dict[tuple[int, str], list[int]] = {}

    for batch in pf.iter_batches(batch_size=args.batch_rows, columns=["year"] + null_rate_cols):
        year_col = batch.column(0)
        for y in years:
            mask = pc.equal(year_col, y)
            n = _count_true(mask)
            if n == 0:
                continue
            for col_name in null_rate_cols:
                col = batch.column(batch.schema.get_field_index(col_name))
                col_filtered = pc.filter(col, mask)
                n_null = int(pc.sum(pc.cast(pc.is_null(col_filtered), pa.int64())).as_py() or 0)
                key = (y, col_name)
                if key not in null_counts:
                    null_counts[key] = [0, 0]
                null_counts[key][0] += n
                null_counts[key][1] += n_null

    # Detect >5 ppt year-over-year jumps
    NULL_BREAK_THRESHOLD = 5.0  # percentage points
    null_breaks: list[dict[str, object]] = []
    for col_name in null_rate_cols:
        year_pcts: dict[int, float] = {}
        for y in sorted(years):
            key = (y, col_name)
            if key in null_counts and null_counts[key][0] > 0:
                year_pcts[y] = null_counts[key][1] / null_counts[key][0] * 100.0
        sorted_yrs = sorted(year_pcts.keys())
        for i in range(1, len(sorted_yrs)):
            prev_y, curr_y = sorted_yrs[i - 1], sorted_yrs[i]
            delta = year_pcts[curr_y] - year_pcts[prev_y]
            if abs(delta) > NULL_BREAK_THRESHOLD:
                null_breaks.append({
                    "variable": col_name,
                    "year_from": prev_y,
                    "year_to": curr_y,
                    "null_pct_from": round(year_pcts[prev_y], 2),
                    "null_pct_to": round(year_pcts[curr_y], 2),
                    "delta_ppt": round(delta, 2),
                })

    # Coverage thresholds (fail if violated)
    # For 2009–2013 unrevised records, revised-only domains should be (almost) entirely null.
    # Use a strict threshold of 99.9% missing; any non-null is treated as a violation above anyway.

    # Encode V2/V3 mode in the output filename to prevent V2 and V3 reports from
    # clobbering each other when both are run with the same --years range.
    mode_tag = "v3_linked" if is_v3_linked else "v2"
    if suffix == "2005_2015":
        out_csv = args.out_dir / f"{mode_tag}_invariants_year_summary.csv"
        out_md = args.out_dir / f"{mode_tag}_invariants_report.md"
    else:
        out_csv = args.out_dir / f"invariants_year_summary_{mode_tag}_{suffix}.csv"
        out_md = args.out_dir / f"invariants_report_{mode_tag}_{suffix}.md"

    with out_csv.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(
            f,
            fieldnames=[
                "year",
                "rows_total",
                "rows_resident",
                "cert_revised",
                "cert_unrevised",
                "cert_unknown",
                "unrevised_rows_2009_2013",
                "unrevised_educ_nonnull_2009_2013",
                "unrevised_pnmonth_nonnull_2009_2013",
                "unrevised_smokeint_nonnull_2009_2013",
            ],
        )
        w.writeheader()
        for y in years:
            s = ys[y]
            w.writerow(
                {
                    "year": y,
                    "rows_total": s.rows_total,
                    "rows_resident": s.rows_resident,
                    "cert_revised": s.cert_revised,
                    "cert_unrevised": s.cert_unrevised,
                    "cert_unknown": s.cert_unknown,
                    "unrevised_rows_2009_2013": s.unrevised_rows_2009_2013,
                    "unrevised_educ_nonnull_2009_2013": s.unrevised_educ_nonnull_2009_2013,
                    "unrevised_pnmonth_nonnull_2009_2013": s.unrevised_pnmonth_nonnull_2009_2013,
                    "unrevised_smokeint_nonnull_2009_2013": s.unrevised_smokeint_nonnull_2009_2013,
                }
            )

    # Build markdown report
    lines: list[str] = []
    lines.append("# V1 invariants report")
    lines.append("")
    lines.append(f"Input: `{args.in_path}`")
    lines.append(f"Years: {min_year}–{max_year}" if min_year != max_year else f"Years: {min_year}")
    lines.append(f"- Year summary CSV: `{out_csv}`")
    lines.append("")
    mode_label = "V3 linked" if is_v3_linked else "V2 natality"
    lines.append(f"Mode: **{mode_label}** (auto-detected from schema)")
    if is_v3_linked:
        lines.append("")
        lines.append(
            "In V3 linked mode, three V2-only structural-coverage invariants "
            "(`unrevised_2009_2013_has_educ`, `unrevised_2009_2013_has_pnmonth`, "
            "`unrevised_2009_2013_has_smokeint`) are **skipped** because the linked "
            "denominator-plus layout for 2005–2013 retains MEDUC_REC/MPCB/CIG_1-3 "
            "bytes that the natality 2009–2010 public-use layout drops. See "
            "`docs/COMPARABILITY.md` §\"V3 linked vs V2 natality: 2009–2010 unrevised-cert "
            "field retention\". Also, `record_weight_null_when_survivor` is allowed "
            "up to 2 (upstream NCHS quirk: 1 row in 2014 + 1 in 2015)."
        )
    lines.append("")
    lines.append("## Invariant checks (should all be 0 unless a known exception applies)")
    lines.append("")
    any_fail = False
    for k in sorted(violations):
        v = violations[k]
        if k in V3_SKIP:
            lines.append(f"- `{k}`: {v} _(skipped — V2-only, see §4.2 note)_")
            continue
        expected = KNOWN_EXCEPTIONS.get(k, 0)
        if v == expected:
            suffix = ""
            if expected:
                suffix = f" _(within known-exception budget of {expected})_"
            lines.append(f"- `{k}`: {v}{suffix}")
        elif expected and v <= expected:
            lines.append(f"- `{k}`: {v} _(within known-exception budget of {expected})_")
        else:
            any_fail = True
            if expected:
                lines.append(f"- `{k}`: {v} **(exceeds known-exception budget of {expected})**")
            else:
                lines.append(f"- `{k}`: {v}")
    lines.append("")
    lines.append("## Certificate revision by year (counts)")
    lines.append("")
    lines.append("| year | total | revised_2003 | unrevised_1989 | unknown |")
    lines.append("|---:|---:|---:|---:|---:|")
    for y in years:
        s = ys[y]
        lines.append(
            f"| {y} | {s.rows_total:,} | {s.cert_revised:,} | {s.cert_unrevised:,} | {s.cert_unknown:,} |"
        )
    lines.append("")
    lines.append("## 2009–2013 unrevised coverage checks (should be 0 non-null)")
    lines.append("")
    lines.append("| year | unrevised rows | educ non-null | pn month non-null | smoke intensity non-null |")
    lines.append("|---:|---:|---:|---:|---:|")
    for y in [yy for yy in range(2009, 2014) if yy in ys]:
        s = ys[y]
        lines.append(
            f"| {y} | {s.unrevised_rows_2009_2013:,} | {s.unrevised_educ_nonnull_2009_2013:,} | {s.unrevised_pnmonth_nonnull_2009_2013:,} | {s.unrevised_smokeint_nonnull_2009_2013:,} |"
        )
    lines.append("")
    lines.append(f"## Null-rate discontinuities (>{NULL_BREAK_THRESHOLD} ppt year-over-year change)")
    lines.append("")
    if null_breaks:
        lines.append(f"**{len(null_breaks)} break(s) detected** (informational — these reflect known structural changes, not bugs):")
        lines.append("")
        lines.append("| Variable | Year transition | Null % (from → to) | Delta (ppt) |")
        lines.append("|----------|----------------|---------------------|-------------|")
        for b in null_breaks:
            lines.append(
                f"| `{b['variable']}` | {b['year_from']}→{b['year_to']} "
                f"| {b['null_pct_from']:.1f}% → {b['null_pct_to']:.1f}% "
                f"| {b['delta_ppt']:+.1f} |"
            )
    else:
        lines.append("No null-rate discontinuities detected.")
    lines.append("")
    lines.append("## Status")
    lines.append("")
    if any_fail:
        lines.append("**FAIL**: one or more invariant checks were violated. See counts above.")
    else:
        lines.append("**PASS**: all invariant checks passed.")
    lines.append("")

    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Wrote {out_csv}")
    print(f"Wrote {out_md}")

    if any_fail:
        raise SystemExit(2)


if __name__ == "__main__":
    main()

