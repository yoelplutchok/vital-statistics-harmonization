"""DESIGN: tracks-current-state — fetal-death schema↔parquet dtype parity.

Durable defense against H8 (docs vs data drift) at the schema-CSV ↔ parquet
boundary. Authored 2026-05-12 per C8.1 DO-3; closes the follow-up filed in
FIX_LOG 2026-05-11T18:50:00Z (the v2.0 incident where 5 demographic columns
shipped as pyarrow `object` while harmonized_schema.csv declared `type=int`).

Two tests:

1. **`test_v21_h8_fixed_columns_remain_int`** (STRICT, PASS):
   The 5 columns explicitly cast to Int8/Int16 in the v2.1.0 H8 fix
   (FIX_LOG 2026-05-12T01:30:00Z's `_apply_h8_int_cast`) must remain int.
   This is the regression gate: if a future task reverts the cast, this test
   FAILS loudly. Mutation-test: change one of the 5 columns back to object;
   this test catches it on first parquet load.

2. **`test_full_schema_type_matches_parquet_dtype`** (XFAIL strict — broader latent surface):
   For ALL 73 schema rows, schema `type` should match parquet dtype per the
   acceptable mapping. **This is currently expected to FAIL** because ~50
   fetal-death raw harmonized columns ship as pyarrow `string` despite schema
   declaring `type=int`. Documented latent state inherited from v2.0; the
   v2.1.0 fix closed only the 5 demographic columns the H8 incident named.
   The xfail(strict=True) marker means: if a future task reconciles the
   shipped state (either casts more columns to int, OR updates schema rows to
   declare `str` for the string-shipping columns), pytest reports
   `XPASS [unexpected]` which is itself a FAIL — forcing removal of the
   xfail marker. That is the gate that closes the latent issue.

Convention: fetal_death's harmonized_schema.csv uses generic `type` values
('int', 'str', 'int32', 'float'). The mapping below defines which pyarrow
dtype family is acceptable per schema value.
"""

from __future__ import annotations

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
import pytest

# Schema-type → set of acceptable pyarrow type name strings.
_INT_TYPES = {
    "int8", "int16", "int32", "int64",
    "uint8", "uint16", "uint32", "uint64",
}
_STR_TYPES = {"string", "large_string", "binary", "large_binary", "object"}
_FLOAT_TYPES = {"float", "double", "halffloat", "float16", "float32", "float64"}

_SCHEMA_TYPE_ACCEPTABLE = {
    "int": _INT_TYPES,
    "str": _STR_TYPES,
    "int32": {"int32"},
    "float": _FLOAT_TYPES,
}

# The 5 columns explicitly cast to int in the v2.1.0 H8 fix
# (FIX_LOG 2026-05-12T01:30:00Z `_apply_h8_int_cast`). These MUST remain int.
V21_H8_FIXED_COLUMNS = {
    "tabulation_flag",     # Int8
    "residence_status",    # Int8
    "maternal_age",        # Int16 (matches natality v2.7.0 dtype)
    "maternal_race_bridged",  # Int8
    "hispanic_origin",     # Int8
}


def _pyarrow_type_name(pa_type: pa.DataType) -> str:
    """Return the canonical pyarrow type name as a comparable string."""
    return str(pa_type).lower()


def test_every_schema_row_has_a_parquet_column(schema_df: pd.DataFrame, harmonized_path) -> None:
    """Every harmonized_name in schema CSV exists in the harmonized parquet.
    Pre-condition for the parity checks."""
    harmonized_cols = set(pq.ParquetFile(harmonized_path).schema_arrow.names)
    schema_names = set(schema_df["harmonized_name"])
    missing = schema_names - harmonized_cols
    assert not missing, (
        f"{len(missing)} schema rows have no matching column in the harmonized parquet: "
        f"{sorted(missing)}"
    )


def test_v21_h8_fixed_columns_remain_int(schema_df: pd.DataFrame, harmonized_path) -> None:
    """The 5 columns cast to int in v2.1.0 (FIX_LOG 2026-05-12T01:30Z) must
    remain int. Regression gate for the H8 incident class."""
    pa_schema = pq.ParquetFile(harmonized_path).schema_arrow
    parquet_dtypes = {field.name: _pyarrow_type_name(field.type) for field in pa_schema}

    regressed: list[str] = []
    for col in sorted(V21_H8_FIXED_COLUMNS):
        if col not in parquet_dtypes:
            regressed.append(f"  {col}: MISSING from parquet")
            continue
        if parquet_dtypes[col] not in _INT_TYPES:
            regressed.append(
                f"  {col}: parquet={parquet_dtypes[col]!r}; expected int (V2.1 H8 fix)"
            )

    assert not regressed, (
        "v2.1.0 H8-fixed columns regressed:\n" + "\n".join(regressed)
    )


@pytest.mark.xfail(
    strict=True,
    reason=(
        "~50 fetal-death raw harmonized columns ship as pyarrow `string` "
        "while schema declares type=int — documented latent state inherited "
        "from v2.0; partial closure in v2.1 (5 demographic columns cast to "
        "Int8/Int16 per FIX_LOG 2026-05-12T01:30Z). Full reconciliation "
        "deferred to a future C8.X task (either cast more columns OR rephrase "
        "schema type column to declare 'str' for the string-shipping columns). "
        "When a future task closes this, xfail(strict) flips to XPASS=FAIL, "
        "forcing removal of this marker — the gate that closes the latent issue."
    ),
)
def test_full_schema_type_matches_parquet_dtype(
    schema_df: pd.DataFrame, harmonized_path
) -> None:
    """For every column in the harmonized parquet, the schema CSV's `type`
    value must map to the pyarrow type-name in the acceptable set per the
    convention table above. Expected XFAIL on current state."""
    pa_schema = pq.ParquetFile(harmonized_path).schema_arrow
    parquet_dtypes = {field.name: _pyarrow_type_name(field.type) for field in pa_schema}

    mismatches: list[str] = []
    for _, row in schema_df.iterrows():
        name = row["harmonized_name"]
        if name not in parquet_dtypes:
            continue  # tested separately in test_every_schema_row_has_a_parquet_column
        schema_type = str(row["type"]).strip().lower()
        actual_pa_name = parquet_dtypes[name]
        acceptable = _SCHEMA_TYPE_ACCEPTABLE.get(schema_type)
        if acceptable is None:
            mismatches.append(
                f"  {name}: schema declared unknown type {schema_type!r} (not in "
                f"{sorted(_SCHEMA_TYPE_ACCEPTABLE)})"
            )
            continue
        if actual_pa_name not in acceptable:
            mismatches.append(
                f"  {name}: schema={schema_type!r}; parquet={actual_pa_name!r} "
                f"(acceptable for schema={schema_type!r}: {sorted(acceptable)})"
            )

    assert not mismatches, (
        "schema/parquet dtype drift (H8 incident class):\n" + "\n".join(mismatches)
    )


def test_derived_parquet_columns_present_or_listed_in_schema(
    schema_df: pd.DataFrame, derived_path
) -> None:
    """The derived parquet may contain additional columns not in
    harmonized_schema.csv (the 16 derived columns: low_birthweight,
    gestational_age_band, etc.). This test asserts every harmonized-schema
    row exists in the derived parquet (the 16 derived adds are non-schema-
    listed; that's expected)."""
    derived_cols = set(pq.ParquetFile(derived_path).schema_arrow.names)
    schema_names = set(schema_df["harmonized_name"])

    missing_in_derived = schema_names - derived_cols
    assert not missing_in_derived, (
        f"{len(missing_in_derived)} schema rows missing from derived parquet: "
        f"{sorted(missing_in_derived)}"
    )
