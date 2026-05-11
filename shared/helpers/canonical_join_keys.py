"""Cross-product canonical join-key names for joint-use code.

natality (`natality/metadata/harmonized_schema.csv`) and fetal_death
(`fetal_death/harmonized_schema.csv`) ship four shared concepts under
divergent column names. This module renames natality columns to the
fetal_death-style names so joint-use code reads from one canonical
namespace. The shipped natality and fetal_death parquets are NOT
mutated; this is a read-time alias. A future natality v2.8 may adopt
these names natively (proposed plan-update; see DECISION_LOG).

Canonical name space (matches fetal_death/harmonized_schema.csv):
    data_year, maternal_age, maternal_race_bridged,
    hispanic_origin, residence_status
"""

from __future__ import annotations

import pandas as pd

NATALITY_TO_CANONICAL: dict[str, str] = {
    "year": "data_year",
    "restatus": "residence_status",
    "maternal_race_bridged4": "maternal_race_bridged",
    "maternal_hispanic_origin": "hispanic_origin",
}

CANONICAL_JOIN_KEYS: list[str] = [
    "data_year",
    "maternal_age",
    "maternal_race_bridged",
    "hispanic_origin",
    "residence_status",
]

AGE_BAND_LABELS: list[str] = ["<20", "20-24", "25-29", "30-34", "35-39", "40+"]
AGE_BAND_BINS: list[int] = [0, 19, 24, 29, 34, 39, 54]


def to_canonical_natality(df: pd.DataFrame) -> pd.DataFrame:
    """Rename a natality DataFrame's join-key columns to canonical names.

    Returns a new DataFrame; the input is not modified. Columns absent
    from the input are silently skipped (the helper is safe to call on
    a column-projected subset).
    """
    rename_map = {k: v for k, v in NATALITY_TO_CANONICAL.items() if k in df.columns}
    return df.rename(columns=rename_map)


def derive_maternal_age_band(age: pd.Series) -> pd.Series:
    """Bin maternal age (single year) into the NVSR-standard 6-category band.

    Sentinel 99 ("Unknown" in NCHS fetal-death V2 era) and any value
    outside the documented analytic range 10-54 produce NaN. Returns a
    pandas Categorical with the six canonical labels (ordered).
    """
    age_num = pd.to_numeric(age, errors="coerce")
    age_num = age_num.where((age_num >= 10) & (age_num <= 54), other=pd.NA)
    return pd.cut(
        age_num,
        bins=AGE_BAND_BINS,
        labels=AGE_BAND_LABELS,
        right=True,
        include_lowest=True,
    )
