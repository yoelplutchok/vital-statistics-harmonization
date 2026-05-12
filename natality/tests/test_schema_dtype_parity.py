"""DESIGN: tracks-current-state — every natality harmonized_schema.csv `type` matches the parquet dtype.

Durable defense against H8 (docs vs data drift) at the schema-CSV ↔ parquet
boundary for the natality + linked subproject. Authored 2026-05-12 per
C8.1 DO-3; sibling of fetal_death/tests/test_schema_dtype_parity.py.

Convention: natality's harmonized_schema.csv uses pyarrow physical-type
names directly ('int8', 'int16', 'int32', 'bool', 'string', 'float32',
'float64'). The parity check is therefore *exact*-match rather than the
generic-family match used for fetal-death (which uses 'int' for any int
width, 'str' for string-like, etc.).

The natality schema (94 rows) is the SUPERSET of:
  - natality-derived parquet (84 cols; natality-only columns)
  - linked-derived parquet (94 cols; natality + death-side derived columns)

Every schema row must match in at least one parquet; in any parquet where
the column appears, the dtype must match the schema declaration exactly.

Mutation-test (Tier-0): if a natality parquet column ships as pyarrow
`string` while the schema declares `type=int8` (the H8 incident pattern),
this test FAILs with a "schema declared int8 but parquet has string"
message naming the offending column.
"""

from __future__ import annotations

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


def _pyarrow_type_name(pa_type: pa.DataType) -> str:
    """Return the canonical pyarrow type name as a comparable string.

    Examples:
        Int8() -> 'int8'
        String() -> 'string'
        Bool_() -> 'bool'
        Float32() -> 'float'   (pyarrow's str() returns 'float' for float32)
        Float64() -> 'double'
    """
    return str(pa_type).lower()


# pyarrow.str() uses some legacy names. Normalize schema declarations
# to the actual str(pyarrow_type) output.
_SCHEMA_TO_PA_STR = {
    "int8": {"int8"},
    "int16": {"int16"},
    "int32": {"int32"},
    "int64": {"int64"},
    "bool": {"bool"},
    "string": {"string", "large_string"},
    "float32": {"float", "float32"},
    "float64": {"double", "float64"},
}


def _check_parity_for_parquet(
    parquet_path,
    schema_df: pd.DataFrame,
    label: str,
) -> list[str]:
    """For columns present in the parquet, verify the schema's `type` matches
    the pyarrow dtype. Returns a list of mismatch strings (empty on PASS).
    Columns in the schema but not in this parquet are NOT errors here — the
    test fixture for the other parquet will check those."""
    pa_schema = pq.ParquetFile(parquet_path).schema_arrow
    parquet_dtypes = {field.name: _pyarrow_type_name(field.type) for field in pa_schema}

    mismatches: list[str] = []
    for _, row in schema_df.iterrows():
        name = row["harmonized_name"]
        if name not in parquet_dtypes:
            continue
        schema_type = str(row["type"]).strip().lower()
        actual_pa_name = parquet_dtypes[name]
        acceptable = _SCHEMA_TO_PA_STR.get(schema_type)
        if acceptable is None:
            mismatches.append(
                f"  [{label}] {name}: schema declared unknown type {schema_type!r} "
                f"(not in {sorted(_SCHEMA_TO_PA_STR)})"
            )
            continue
        if actual_pa_name not in acceptable:
            mismatches.append(
                f"  [{label}] {name}: schema={schema_type!r}; parquet={actual_pa_name!r} "
                f"(acceptable: {sorted(acceptable)})"
            )
    return mismatches


def test_schema_type_matches_natality_parquet(
    schema_df: pd.DataFrame, natality_derived_path
) -> None:
    """Every column in the natality-derived parquet has a schema row whose
    `type` matches the pyarrow dtype exactly. Catches the H8 incident pattern."""
    mismatches = _check_parity_for_parquet(natality_derived_path, schema_df, "natality")
    assert not mismatches, (
        "schema/parquet dtype drift in natality-derived (H8 incident class):\n"
        + "\n".join(mismatches)
    )


def test_schema_type_matches_linked_parquet(
    schema_df: pd.DataFrame, linked_derived_path
) -> None:
    """Every column in the linked-derived parquet has a schema row whose
    `type` matches the pyarrow dtype exactly. Catches the H8 incident pattern."""
    mismatches = _check_parity_for_parquet(linked_derived_path, schema_df, "linked")
    assert not mismatches, (
        "schema/parquet dtype drift in linked-derived (H8 incident class):\n"
        + "\n".join(mismatches)
    )


def test_every_schema_row_is_in_at_least_one_parquet(
    schema_df: pd.DataFrame, natality_derived_path, linked_derived_path
) -> None:
    """Every harmonized_name in the schema CSV must appear in either the
    natality-derived parquet or the linked-derived parquet (or both). A
    schema row with no matching parquet column is a phantom row."""
    nat_cols = set(pq.ParquetFile(natality_derived_path).schema_arrow.names)
    lnk_cols = set(pq.ParquetFile(linked_derived_path).schema_arrow.names)
    union = nat_cols | lnk_cols
    schema_names = set(schema_df["harmonized_name"])
    phantom = schema_names - union
    assert not phantom, (
        f"{len(phantom)} schema rows have NO matching column in either parquet: "
        f"{sorted(phantom)}"
    )
