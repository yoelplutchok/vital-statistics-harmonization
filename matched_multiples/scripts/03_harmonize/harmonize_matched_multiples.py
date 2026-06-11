#!/usr/bin/env python3
"""
DESIGN: tracks-current-state

Harmonize the 3 matched-multiples yearly_clean parquets into one canonical
parquet covering all 3 publication windows.

Reads:
  matched_multiples/output/yearly_clean/matched_multiples_<window>_raw.parquet
    for window in {1995-1997, 1995-2000, 2016-2020}.

Writes:
  matched_multiples/output/harmonized/matched_multiples_harmonized.parquet
    with 24 canonical columns spanning all 3 windows (1,665,568 rows total).

Field mapping is per-window and follows harmonized_schema.csv:
  1995-1997: BIRTHID/SETID/PLURALITY/FLGCOMP/SETORDER/RESTATUS/DMAGE/...
  1995-2000: same as 1995-1997 plus UCOD9 + UCOD10 (mixed ICD-9/10 by year)
  2016-2020: PLURAL/MULTID/COMPLETE/COUNT/MAGER/SEX/OEGEST/BWTR12/...

Sentinel handling:
  - " " / "" / "." -> NaN
  - "9" for race-recode unknown; "99" for age-unknown; "9999" for birthweight
    unknown -> NaN where the schema's allowed_values excludes the sentinel
  - Trailing spaces on multi-byte text fields -> stripped before parse

Example:
  python harmonize_matched_multiples.py \\
    --out ../../output/harmonized/matched_multiples_harmonized.parquet
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

_SCRIPT_DIR = Path(__file__).resolve().parent
_SUBPROJECT_ROOT = _SCRIPT_DIR.parents[1]  # matched_multiples/
_YEARLY_DIR = _SUBPROJECT_ROOT / "output" / "yearly_clean"

_WINDOWS = ("1995-1997", "1995-2000", "2016-2020")

# Final harmonized column order. Aligns with harmonized_schema.csv (24 cols;
# data_year and maternal_age_recode9 dropped at sub-step 3 as not derivable /
# not cross-window present per sub-step 1 residual risk b).
_OUT_COLS: tuple[str, ...] = (
    "data_window",
    "record_type",
    "set_id",
    "set_size",
    "set_complete",
    "set_order",
    "tabulation_flag",
    "residence_status",
    "maternal_age",
    "maternal_race_hispanic",
    "maternal_education_cat4",
    "nativity",
    "marital_status",
    "plurality_imputed",
    "sex_infant",
    "gestation_weeks",
    "birthweight_g",
    "birthweight_recode12",
    "apgar_5_min",
    "delivery_method",
    "age_at_death_days",
    "age_at_death_recode5",
    "cause_of_death_icd",
    "cause_of_death_icd_revision",
)


def _str_or_nan(s: pd.Series) -> pd.Series:
    """Strip + treat empty / '.' as NaN. Keeps string dtype."""
    out = s.astype("string").str.strip()
    return out.mask(out.isin(["", "."]))


def _int_or_nan(s: pd.Series, sentinels: tuple[str, ...] = ()) -> pd.Series:
    """Strip, drop empties + sentinels, coerce to nullable Int64."""
    out = s.astype("string").str.strip()
    out = out.mask(out.isin(("",) + sentinels))
    return pd.to_numeric(out, errors="coerce").astype("Int64")


_RECORD_TYPE_MAP = {"1": "survivor", "2": "infant_death", "3": "fetal_death"}


def _harmonize_1995x(df: pd.DataFrame, window: str) -> pd.DataFrame:
    """Shared harmonization for 1995-1997 and 1995-2000 (same byte layout 1-228)."""
    out = pd.DataFrame(index=df.index)
    out["data_window"] = window
    out["record_type"] = _str_or_nan(df["BIRTHID"]).map(_RECORD_TYPE_MAP)
    out["set_id"] = _str_or_nan(df["SETID"])
    out["set_size"] = _int_or_nan(df["PLURALITY"])

    # FLGCOMP: 0=complete -> 1; 1=incomplete -> 2; 2=unmatched -> 3
    flg = _int_or_nan(df["FLGCOMP"])
    out["set_complete"] = (flg + 1).astype("Int64")

    # SETORDER: 0/9 -> NaN; 1-4 kept
    so = _int_or_nan(df["SETORDER"], sentinels=("0", "9"))
    out["set_order"] = so

    # TABFLAG: '1' under 20wk; '2' 20+; blank for live-birth records
    out["tabulation_flag"] = _str_or_nan(df["TABFLAG"])

    # RESTATUS: 1/2/3; the 1995-X files do not ship 4=foreign
    out["residence_status"] = _int_or_nan(df["RESTATUS"])

    # DMAGE: numeric single-year; 99 = unknown
    out["maternal_age"] = _int_or_nan(df["DMAGE"], sentinels=("99",))

    # ORRACEM (1995-X 4-category within-era):
    # 1=Hispanic; 2=NH White; 3=NH Black; 4=NH Other; 9=unknown
    race_map_1995x = {
        "1": "Hispanic",
        "2": "NH_White",
        "3": "NH_Black",
        "4": "NH_Other",
        "9": "unknown",
    }
    out["maternal_race_hispanic"] = (
        _str_or_nan(df["ORRACEM"]).map(race_map_1995x)
    )

    # MEDUC6 (1995-X years-based recode):
    # 1-2 -> lt_hs; 3 -> hs; 4 -> some_college; 5 -> ba_plus; 6 -> unknown
    educ_map_1995x = {
        "1": "lt_hs",
        "2": "lt_hs",
        "3": "hs",
        "4": "some_college",
        "5": "ba_plus",
        "6": "unknown",
    }
    out["maternal_education_cat4"] = (
        _str_or_nan(df["MEDUC6"]).map(educ_map_1995x)
    )

    # MPLBIRR: 1=US-born; 2=foreign-born; 3=unknown (blank for fetal-death records)
    nativ_map = {"1": "US_born", "2": "foreign_born", "3": "unknown"}
    out["nativity"] = _str_or_nan(df["MPLBIRR"]).map(nativ_map)

    marital_map = {"1": "married", "2": "unmarried", "9": "unknown"}
    out["marital_status"] = _str_or_nan(df["DMAR"]).map(marital_map)

    out["plurality_imputed"] = _int_or_nan(df["PLUIMP"])

    sex_map = {"1": "M", "2": "F", "9": "U"}
    out["sex_infant"] = _str_or_nan(df["CSEX"]).map(sex_map)

    out["gestation_weeks"] = _int_or_nan(df["GESTAT"], sentinels=("99",))
    out["birthweight_g"] = _int_or_nan(df["DBIRWT"], sentinels=("9999",))
    out["birthweight_recode12"] = _int_or_nan(df["BIRWT12"])
    out["apgar_5_min"] = _int_or_nan(df["FMAPS"], sentinels=("99",))

    # DELMETH6 (1995-X): 1=vaginal; 2=VBAC; 3=primary csec; 4=repeat csec;
    # 5=csection (rev unknown); 6=hysterotomy/hysterectomy; 9=unknown
    delm_map_1995x = {
        "1": "vaginal",
        "2": "vaginal_after_csection",
        "3": "primary_csection",
        "4": "repeat_csection",
        "5": "csection_unknown",
        "6": "hysterotomy",
        "9": "unknown",
    }
    out["delivery_method"] = _str_or_nan(df["DELMETH6"]).map(delm_map_1995x)

    # AGED: '999' or blank for non-infant-death records
    out["age_at_death_days"] = _int_or_nan(df["AGED"], sentinels=("999",))
    out["age_at_death_recode5"] = _int_or_nan(df["AGER5"])

    return out


def _harmonize_1995_1997(df: pd.DataFrame) -> pd.DataFrame:
    out = _harmonize_1995x(df, "1995-1997")
    # 1995-1997 ships only UCOD (ICD-9). Cause = UCOD on ID rows, NaN otherwise.
    is_id = out["record_type"] == "infant_death"
    ucod = _str_or_nan(df["UCOD"])
    out["cause_of_death_icd"] = ucod.where(is_id)
    out["cause_of_death_icd_revision"] = pd.Series(
        np.where(is_id & ucod.notna(), 9, pd.NA), dtype="Int64"
    )
    return out


def _harmonize_1995_2000(df: pd.DataFrame) -> pd.DataFrame:
    out = _harmonize_1995x(df, "1995-2000")
    # 1995-2000 ships UCOD9 (1995-1998 records) AND UCOD10 (1999-2000 records).
    # Per-record revision = whichever block is non-blank for ID rows.
    is_id = out["record_type"] == "infant_death"
    u9 = _str_or_nan(df["UCOD9"])
    u10 = _str_or_nan(df["UCOD10"])
    cause = u10.where(u10.notna(), u9)
    out["cause_of_death_icd"] = cause.where(is_id)
    revision = pd.Series(pd.NA, index=df.index, dtype="Int64")
    revision = revision.mask(is_id & u9.notna(), 9)
    revision = revision.mask(is_id & u10.notna(), 10)
    out["cause_of_death_icd_revision"] = revision
    return out


def _harmonize_2016_2020(df: pd.DataFrame) -> pd.DataFrame:
    out = pd.DataFrame(index=df.index)
    out["data_window"] = "2016-2020"
    out["record_type"] = _str_or_nan(df["BIRTHID"]).map(_RECORD_TYPE_MAP)
    out["set_id"] = _str_or_nan(df["MULTID"])
    out["set_size"] = _int_or_nan(df["PLURAL"])

    # set_complete: COUNT=1 -> 3 (unmatched); else COMPLETE 1=complete -> 1,
    # 2=incomplete -> 2
    count = _int_or_nan(df["COUNT"])
    complete = _int_or_nan(df["COMPLETE"])
    sc = complete.copy()
    sc = sc.mask(count == 1, 3)
    out["set_complete"] = sc

    out["set_order"] = _int_or_nan(df["SETORDER"], sentinels=("0", "9"))

    # 2016-2020 file restricts to >=20wk fetal-deaths at NCHS source; no TABFLAG.
    # Set to '2' (>=20wk) for FD rows so downstream filters work cross-window;
    # NaN for live-birth rows.
    is_fd = out["record_type"] == "fetal_death"
    out["tabulation_flag"] = pd.Series(
        np.where(is_fd, "2", pd.NA), dtype="string"
    )

    # residence_status: suppressed in 2016-2020 public file
    out["residence_status"] = pd.Series(pd.NA, index=df.index, dtype="Int64")

    out["maternal_age"] = _int_or_nan(df["MAGER"], sentinels=("99",))

    # MRACEHISP (2016-2020 8-category) -> 4-cat within-era collapse for cross-
    # window compatibility:
    # 1=NH White; 2=NH Black; 3=NH AIAN -> NH_Other; 4=NH Asian -> NH_Other;
    # 5=NH NHOPI -> NH_Other; 6=NH multiple -> NH_Other; 7=Hispanic; 8=unknown.
    # (Users wanting the native 8-category split can derive from MRACEHISP raw.)
    race_map_2016 = {
        "1": "NH_White",
        "2": "NH_Black",
        "3": "NH_Other",
        "4": "NH_Other",
        "5": "NH_Other",
        "6": "NH_Other",
        "7": "Hispanic",
        "8": "unknown",
    }
    out["maternal_race_hispanic"] = (
        _str_or_nan(df["MRACEHISP"]).map(race_map_2016)
    )

    # MEDUC (2016-2020 degree-based 9-cat):
    # 1=8th or less; 2=9-12th no diploma; 3=HS/GED; 4=some college; 5=AA;
    # 6=BA; 7=MA; 8=Doctorate/Prof; 9=unknown
    educ_map_2016 = {
        "1": "lt_hs",
        "2": "lt_hs",
        "3": "hs",
        "4": "some_college",
        "5": "some_college",
        "6": "ba_plus",
        "7": "ba_plus",
        "8": "ba_plus",
        "9": "unknown",
    }
    out["maternal_education_cat4"] = (
        _str_or_nan(df["MEDUC"]).map(educ_map_2016)
    )

    nativ_map_2016 = {"1": "US_born", "2": "foreign_born", "3": "unknown"}
    out["nativity"] = _str_or_nan(df["NATIVITY"]).map(nativ_map_2016)

    marital_map_2016 = {"1": "married", "2": "unmarried"}
    out["marital_status"] = _str_or_nan(df["MARRIED"]).map(marital_map_2016)

    # 2016-2020 does not ship a plurality-imputation flag
    out["plurality_imputed"] = pd.Series(pd.NA, index=df.index, dtype="Int64")

    # SEX already M/F/U native
    out["sex_infant"] = _str_or_nan(df["SEX"])

    out["gestation_weeks"] = _int_or_nan(df["OEGEST"], sentinels=("99",))

    # 2016-2020 does not ship single-gram birthweight (only the 12/14-cat recodes)
    out["birthweight_g"] = pd.Series(pd.NA, index=df.index, dtype="Int64")
    out["birthweight_recode12"] = _int_or_nan(df["BWTR12"])

    out["apgar_5_min"] = _int_or_nan(df["APGAR5"], sentinels=("99",))

    # DMETHOD (2016-2020): 1=vaginal; 2=VBAC; 3=primary csec; 4=repeat csec;
    # 9=unknown.  No hysterotomy/csection-unknown categories in 2016-2020.
    delm_map_2016 = {
        "1": "vaginal",
        "2": "vaginal_after_csection",
        "3": "primary_csection",
        "4": "repeat_csection",
        "9": "unknown",
    }
    out["delivery_method"] = _str_or_nan(df["DMETHOD"]).map(delm_map_2016)

    out["age_at_death_days"] = _int_or_nan(df["AGED"], sentinels=("999",))
    out["age_at_death_recode5"] = _int_or_nan(df["AGER5"])

    # 2016-2020 ships ICD-10 only.
    is_id = out["record_type"] == "infant_death"
    ucod = _str_or_nan(df["UCOD"])
    out["cause_of_death_icd"] = ucod.where(is_id)
    out["cause_of_death_icd_revision"] = pd.Series(
        np.where(is_id & ucod.notna(), 10, pd.NA), dtype="Int64"
    )

    return out


_DISPATCH = {
    "1995-1997": _harmonize_1995_1997,
    "1995-2000": _harmonize_1995_2000,
    "2016-2020": _harmonize_2016_2020,
}


def harmonize_all() -> pd.DataFrame:
    """Read 3 yearly_clean parquets, harmonize each, concatenate."""
    parts: list[pd.DataFrame] = []
    for window in _WINDOWS:
        raw_path = _YEARLY_DIR / f"matched_multiples_{window}_raw.parquet"
        if not raw_path.exists():
            raise FileNotFoundError(
                f"Missing yearly_clean parquet for {window}: {raw_path}"
            )
        raw = pq.read_table(raw_path).to_pandas()
        out = _DISPATCH[window](raw)
        # Pin column order so concat is byte-stable
        parts.append(out[list(_OUT_COLS)])
        print(f"  {window}: harmonized {len(out):,} rows", file=sys.stderr)

    df = pd.concat(parts, axis=0, ignore_index=True)
    return df


def run_harmonize(out: Path) -> int:
    df = harmonize_all()
    out.parent.mkdir(parents=True, exist_ok=True)
    tbl = pa.Table.from_pandas(df, preserve_index=False)
    pq.write_table(tbl, str(out))
    print(f"Wrote {len(df):,} rows × {df.shape[1]} cols to {out}", file=sys.stderr)
    return len(df)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    default_out = (
        _SUBPROJECT_ROOT / "output" / "harmonized" / "matched_multiples_harmonized.parquet"
    )
    p.add_argument("--out", type=Path, default=default_out, help="Output Parquet path")
    args = p.parse_args()
    n = run_harmonize(args.out)
    if n == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
