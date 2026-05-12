#!/usr/bin/env python3
"""
Harmonize per-year raw Parquet files into a single schema.

Reads yearly raw Parquet files (from 01_import), maps era-specific field names
and positions to the common harmonized schema defined in harmonized_schema.csv,
and writes a unified output.

Usage:
  python harmonize.py --years 2006 2014 2022 --out ../../output/harmonized/fetal_death_harmonized.parquet
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT = _SCRIPT_DIR.parents[1]
# Monorepo lays output/ at the top level (symlinked to the sibling build dir per
# STATUS 2026-05-11T22:30Z); fetal_death/metadata/ was flattened to fetal_death/
# at monorepo migration 7fd9cdf (see PROJECT_STRUCTURE.md). Both paths resolve
# relative to the monorepo root, not the fetal_death subproject root.
_YEARLY_DIR = _PROJECT.parent / "output" / "yearly_clean"
_SCHEMA_CSV = _PROJECT / "harmonized_schema.csv"
_CROSSWALK_CSV = _PROJECT / "variable_crosswalk_working.csv"


# ---------------------------------------------------------------------------
# Field name mapping: harmonized_name -> raw_field_name for each era
# ---------------------------------------------------------------------------

def _build_field_map() -> dict[str, dict[str, str]]:
    """
    Build a mapping: harmonized_name -> {era_tag -> raw_field_name}.

    era_tag is one of '1992', '2003', '2006', '2014', '2022':
      '1992' = 1989-2002 (1989-revision uniform era, V2.0 + V3a backward extension)
      '2003' = 2003-2004 (V2.1 transition: mixed A+S at 1351/1501-byte records;
               parser dispatches to FETAL_2005_2006_FIELDS so the raw column set
               is identical to '2006'; era tag exists so the B7 TABFLG correction
               can dispatch only on these two years)
      '2006' = 2005-2013 (mixed revision layout, V1)
      '2014' = 2014-2017 (COD era, V1)
      '2022' = 2018-2022 (COD-only era, V1)
    """
    cw = pd.read_csv(_CROSSWALK_CSV)
    mapping: dict[str, dict[str, str]] = {}

    for _, row in cw.iterrows():
        hname = row["candidate_harmonized_name"]
        era_map: dict[str, str] = {}
        for col, era in [
            ("field_1992", "1992"),
            ("field_2006", "2006"),
            ("field_2014", "2014"),
            ("field_2022", "2022"),
        ]:
            val = row.get(col)
            if pd.notna(val) and val != "N/A":
                era_map[era] = val
        # 2003+2004 share most byte positions with the 2006 layout (parser dispatch);
        # mirror field_2006 into era='2003' EXCEPT for harmonized columns whose
        # 2003-layout byte position holds semantically different data:
        #   - maternal_age: bytes 89-90 in 2003/2004 hold MAGER41 (41-category
        #     age recode), NOT MAGER (single-year of age). Confirmed via the
        #     2003 + 2004 Fetal User Guides p17. The 2003+2004 public-use files
        #     ship no single-year age field; only the 41/14/9-category recodes.
        #     Leave maternal_age null for these years; downstream consumers should
        #     use maternal_age_recode14 or _recode9 for age-stratified analysis.
        _OMIT_FROM_2003 = {"maternal_age"}
        if "2006" in era_map and hname not in _OMIT_FROM_2003:
            era_map["2003"] = era_map["2006"]
        mapping[hname] = era_map

    return mapping


def _era_tag(year: int) -> str:
    """Return the era tag for a given data year."""
    if 2018 <= year <= 2022:
        return "2022"
    if 2014 <= year <= 2017:
        return "2014"
    if 2005 <= year <= 2013:
        return "2006"
    if year in (2003, 2004):
        return "2003"  # V2.1 transition era
    if 1989 <= year <= 2002:
        return "1992"  # 1989-revision uniform era (V2.0 + V3a backward extension)
    raise ValueError(f"Year {year} outside supported range (1989-2022)")


# ---------------------------------------------------------------------------
# Sentinel value handling
# ---------------------------------------------------------------------------

# B7 — TABFLG correction set for 2003+2004 transition years.
# NCHS shipped a programming-error TABFLG@position-9 in the 2003 and 2004
# fetal-death public-use files: COMBGEST=99 (not-stated gestation) records
# in 43 specific states were assigned TABFLG='1' (<20wk) when the corrected
# imputation places them in TABFLG='2' (20+wk).
# Source: raw_docs/fetal_death/fetaldeath0304problems.pdf page 1 SAS code.
# The PDF SAS code names XOSTATE @ bytes 32-33; we use raw['OSTATE'] @ 30-31
# because OSTATE ≡ XOSTATE for this comparator (the only OSTATE/XOSTATE
# divergence is NY-state vs YC=NYC, and the 43-state list contains neither
# 'NY' nor 'YC'). Verified: post-B7 + RESTATUS!=4 yields 26,004 (2003) /
# 26,001 (2004) byte-exact against the corrected NVSR totals.
_B7_STATES: frozenset[str] = frozenset({
    "AL", "AK", "AZ", "CA", "CT", "DE", "DC", "FL", "ID", "IL", "IN", "IA",
    "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE",
    "NV", "NH", "NJ", "NM", "NC", "ND", "OH", "OK", "OR", "SC", "SD", "TN",
    "TX", "UT", "VT", "WA", "WI", "WV", "WY",
})
assert len(_B7_STATES) == 43, "B7 state list expected to have 43 codes"


# H8 — five demographic/filter columns declared int in harmonized_schema.csv
# but shipped as object/string in v2.0.0 parquet (FIX_LOG 2026-05-11T18:50Z).
# v2.1.0 re-derivation casts them to nullable Int, matching the schema and
# the natality v2.7.0 dtype convention (year int16, restatus int8, etc.).
_H8_INT_DTYPES: dict[str, str] = {
    "tabulation_flag":        "Int8",
    "residence_status":       "Int8",
    "maternal_age":           "Int16",
    "maternal_race_bridged":  "Int8",
    "hispanic_origin":        "Int8",
}


_SENTINEL_MAP: dict[str, list[str]] = {
    # Fields where specific values mean "unknown/not stated"
    "maternal_age": ["99"],
    "gestational_age_combined": ["99"],
    "gestational_age_recode5": ["5"],  # 5 = unknown in GESTREC5
    "birthweight": ["9999"],
    "birthweight_recode4": ["4"],  # 4 = not stated in BWTR4
    "prenatal_care_month": ["99"],
    "maternal_education": ["9"],
    "hispanic_origin": ["9"],
    "fetal_sex": ["U"],
    "plurality": ["9"],
    "delivery_method_recode": ["9"],
    "tobacco_use_revised": ["U"],
    "prepregnancy_bmi": ["99.9"],
}


def _apply_sentinels(df: pd.DataFrame) -> pd.DataFrame:
    """Replace sentinel values with empty string for harmonized null handling."""
    for field, sentinels in _SENTINEL_MAP.items():
        if field in df.columns:
            df[field] = df[field].where(~df[field].isin(sentinels), "")
    return df


def _apply_h8_int_cast(df: pd.DataFrame) -> pd.DataFrame:
    """Cast five demographic/filter columns from string to nullable Int.

    Closes FIX_LOG 2026-05-11T18:50Z (H8). Empty strings become pd.NA;
    sentinel ints like maternal_age=99 are preserved as Int 99 (sentinel
    masking remains a separate downstream concern via --sentinels mode).
    pd.to_numeric(errors='raise') fail-loud catches any non-numeric drift.
    """
    for col, dtype in _H8_INT_DTYPES.items():
        if col not in df.columns:
            continue
        s = df[col].astype(str).str.strip().replace("", pd.NA)
        df[col] = pd.to_numeric(s, errors="raise").astype(dtype)
    return df


def _checked_remap(
    series: pd.Series,
    mapping: dict[str, str],
    *,
    recode_label: str,
    year: int,
) -> pd.Series:
    """Apply a value remap, raising ValueError on any unseen input code.

    Closes AUDIT-V2-FINAL R3 (and the M3 generalization for B1/B2/B4/B6).
    Silent .map().fillna('') would have hidden a future NCHS test code or a
    parse drift; this raises and points at the recode block to update.
    """
    observed = set(series.dropna().astype(str).unique())
    unseen = observed - set(mapping)
    if unseen:
        raise ValueError(
            f"Year {year}: {recode_label} input has unseen code(s) "
            f"{sorted(unseen)} not in the recode map. Update the map in "
            f"harmonize.py {recode_label} before harmonizing."
        )
    return series.map(mapping)


# ---------------------------------------------------------------------------
# Main harmonization
# ---------------------------------------------------------------------------

def harmonize_year(year: int, field_map: dict[str, dict[str, str]]) -> pd.DataFrame:
    """Load a raw yearly Parquet and harmonize to common schema."""
    path = _YEARLY_DIR / f"fetal_death_{year}_raw.parquet"
    if not path.exists():
        raise FileNotFoundError(f"No parsed file for {year}: {path}")

    raw = pd.read_parquet(path)
    # Strip whitespace from string columns
    for col in raw.select_dtypes(include="object").columns:
        raw[col] = raw[col].str.strip()

    era = _era_tag(year)
    harmonized: dict[str, pd.Series] = {"data_year": pd.Series([year] * len(raw), dtype="int32")}

    for hname, era_map in field_map.items():
        raw_field = era_map.get(era)
        # Skip 'derived' placeholder rows — these are harmonized columns built
        # outside the field-map copy (e.g., data_year is synthesized in the dict
        # init above; derived indicators are added by 04_derive/derive.py).
        # Overwriting them here with empty strings was a latent bug surfaced
        # when V2.1 + H8 dtype reconciliation made the validator dtype-strict.
        if raw_field == "derived":
            continue
        if raw_field and raw_field in raw.columns:
            harmonized[hname] = raw[raw_field].values
        else:
            # Field not available for this era — fill with empty string
            harmonized[hname] = pd.Series([""] * len(raw), dtype="object")

    df = pd.DataFrame(harmonized)

    # 1992-era value normalization: the 1989-revision raw files use different code
    # systems than the 2003-revision for several fields. Without recoding, the
    # same harmonized column would store semantically incompatible values across
    # eras (AUDIT-HARMONIZE-2 blockers B1/B2/B3, closed 2026-04-21).
    if era == "1992":
        # B1 — fetal_sex: 1/2/9 numeric → M/F/U alphabetic (V1 convention).
        # Fail-loud on unseen codes per AUDIT-V2-FINAL M3 (extended to B1/B2/B4/B6
        # 2026-05-03 from the original B3-only hardening).
        if "fetal_sex" in df.columns:
            df["fetal_sex"] = _checked_remap(
                df["fetal_sex"],
                {"1": "M", "2": "F", "9": "U", "": ""},
                recode_label="B1 fetal_sex",
                year=year,
            )

        # B2 — delivery_method_recode: V2 6-cat DELMETH6 → V1 3-cat DMETH_REC.
        # Collapse {Vag-excl-VBAC, VBAC}→Vaginal, {PrimC, RepC, Hyst}→C-section, NS→9.
        # Full 6-cat detail remains available in yearly raw parquets (DELMETH6 column).
        if "delivery_method_recode" in df.columns:
            df["delivery_method_recode"] = _checked_remap(
                df["delivery_method_recode"],
                {"1": "1", "2": "1", "3": "2", "4": "2", "5": "2", "6": "9", "": ""},
                recode_label="B2 delivery_method_recode",
                year=year,
            )

        # B3 — maternal_race_bridged: V2 raw MRACE 2-digit → V1 4-cat MRACEREC.
        # Crosswalk now maps field_1992 to MRACE (79-80) rather than MRACE3 (81)
        # because MRACE retains the AIAN (03) / API (04-78) distinction that MRACE3
        # collapses into "Other". MRACE='99' (Unknown) is mapped explicitly to
        # blank to mirror V1 2018-2022 not-in-layout blank handling
        # (AUDIT-V2-FINAL M6, 2026-04-22). Unseen codes raise instead of silently
        # blanking, to fail loud on future NCHS test codes (AUDIT-V2-FINAL R3 closure).
        #
        # V3a extension (2026-05-12): the 1989-revision codes used in 1989-1991
        # differ from the 1992+ scheme. Per the 1989 NCHS user guide page 28:
        # 01=White, 02=Black, 03=AmIndian, 04=Chinese, 05=Japanese, 06=Hawaiian,
        # 07=Filipino, 08=Other Asian/Pacific Islander, 09=All other Races.
        # In 1992 NCHS switched API granularity from 04-08 to 18-78 (a parallel
        # 2nd-digit scheme); the "All other Races" residual (code 09) was
        # dropped. Mapping: 08→4 (API, same as 04-07 and 18-78); 09→"" (treated
        # as unknown, consistent with how MRACE=99 unknown is handled 1993+).
        # The 09 records (~165 total across 1989-1991) get null
        # maternal_race_bridged but are preserved in the parquet for unbridged
        # analyses. Documented in V3a_1989_1991_LAYOUT_DECISIONS.md.
        if "maternal_race_bridged" in df.columns:
            df["maternal_race_bridged"] = _checked_remap(
                df["maternal_race_bridged"],
                {
                    "01": "1", "02": "2", "03": "3",
                    "04": "4", "05": "4", "06": "4", "07": "4",
                    "08": "4",  # V3a 1989-rev: Other Asian or Pacific Islander → API
                    "09": "",   # V3a 1989-rev: All other Races → unknown/blank
                    "18": "4", "28": "4", "38": "4", "48": "4",
                    "58": "4", "68": "4", "78": "4",
                    "99": "",  # Unknown race -> blank (matches V1 not-in-layout)
                    "": "",
                },
                recode_label="B3 maternal_race_bridged",
                year=year,
            )

        # B4 — paternal_age_recode11: V2 1989-rev FAGE11 is 12-category, V1 2003-rev
        # FAGEREC11 is 11-category. Same column had incompatible codes for Unknown
        # (V2='12', V1='11') and the open-ended top bin (V2 '10'=55-59 + '11'=60-98
        # vs V1 '10'=55+). Recode V2 to V1 11-category scheme:
        #   01-09 -> 01-09 (identical bins <15 through 50-54)
        #   10 (55-59) -> 10  | collapse into V1's open 55+ bin
        #   11 (60-98) -> 10  |
        #   12 (Not stated) -> 11 (Unknown)
        # Full 12-cat detail remains in yearly raw parquets (FAGE11 column).
        # AUDIT-V2-FINAL B4 closure, 2026-04-22.
        if "paternal_age_recode11" in df.columns:
            df["paternal_age_recode11"] = _checked_remap(
                df["paternal_age_recode11"],
                {
                    "01": "01", "02": "02", "03": "03", "04": "04",
                    "05": "05", "06": "06", "07": "07", "08": "08",
                    "09": "09",
                    "10": "10", "11": "10",  # collapse 55-59 + 60-98 into V1 55+
                    "12": "11",  # V2 Not stated -> V1 Unknown
                    "": "",
                },
                recode_label="B4 paternal_age_recode11",
                year=year,
            )

        # B6 — delivery_place_recode: V2 raw PLDEL2 (1=Hospital, 2=Not in hospital
        # incl unknown) conflates Unknown into 2. V1 BFACIL3 distinguishes
        # 1=Hospital, 2=Not in hospital, 3=Unknown. Re-derive from raw PLDEL
        # (which preserves the Unknown distinction at code 9):
        #   PLDEL=1 (Hospital) -> 1
        #   PLDEL=3 (En route) -> 1  (same as PLDEL2 collapse)
        #   PLDEL=2 (Doctor/home/public) -> 2
        #   PLDEL=9 (Unknown) -> 3
        # AUDIT-V2-FINAL B6 closure, 2026-04-22.
        if "delivery_place_recode" in df.columns and "PLDEL" in raw.columns:
            df["delivery_place_recode"] = _checked_remap(
                raw["PLDEL"],
                {"1": "1", "3": "1", "2": "2", "9": "3", "": ""},
                recode_label="B6 delivery_place_recode (from PLDEL)",
                year=year,
            ).values

        # version_flag synthesis: 1992-2002 files are 1989-revision only (no VERSION
        # field in source layout). Per crosswalk, treat era as implicit 'S' so
        # downstream filters like NVSR-comparable subset (version_flag=='S') behave
        # consistently across eras. Fill-only-if-blank form (AUDIT-HARMONIZE-2 R3)
        # protects against a future crosswalk edit that adds a real field_1992 for
        # this column.
        if "version_flag" in df.columns:
            df["version_flag"] = df["version_flag"].where(df["version_flag"] != "", "S")

    if era == "2003":
        # B7 — TABFLG correction for 2003/2004 transition years. See _B7_STATES
        # block above for the source-of-truth citation and the OSTATE/XOSTATE
        # equivalence argument.
        if (
            "tabulation_flag" in df.columns
            and "COMBGEST" in raw.columns
            and "OSTATE" in raw.columns
        ):
            combgest = raw["COMBGEST"].astype(str).str.strip().values
            ostate = raw["OSTATE"].astype(str).str.strip().values
            mask = (combgest == "99") & pd.Series(ostate).isin(_B7_STATES).values
            n_b7 = int(mask.sum())
            df.loc[mask, "tabulation_flag"] = "2"
            print(
                f"    B7 TABFLG correction (year {year}): "
                f"{n_b7:,} records re-flagged to TABFLG=2",
                file=sys.stderr,
            )

    print(f"  Year {year}: {len(df):,} records harmonized ({era} era)", file=sys.stderr)
    return df


def harmonize_all(years: list[int], out: Path, *, apply_sentinels: bool = False) -> int:
    """Harmonize multiple years and write to a single Parquet file."""
    field_map = _build_field_map()

    frames: list[pd.DataFrame] = []
    for year in sorted(years):
        df = harmonize_year(year, field_map)
        frames.append(df)

    combined = pd.concat(frames, ignore_index=True)

    if apply_sentinels:
        combined = _apply_sentinels(combined)

    combined = _apply_h8_int_cast(combined)

    out.parent.mkdir(parents=True, exist_ok=True)
    combined.to_parquet(out, index=False)

    print(f"Wrote {len(combined):,} total records ({len(years)} years) to {out}", file=sys.stderr)
    return len(combined)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--years", type=int, nargs="+", required=True, help="Data years to harmonize")
    p.add_argument("--out", type=Path, required=True, help="Output Parquet path")
    p.add_argument("--sentinels", action="store_true", help="Replace sentinel values with empty")
    args = p.parse_args()

    try:
        harmonize_all(args.years, args.out, apply_sentinels=args.sentinels)
    except (FileNotFoundError, ValueError) as e:
        print(e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
