"""DESIGN: tracks-current-state

L13 invariant tests over the per-subproject metadata CSVs.

Motivated by C8.11's discovery (2026-05-13) of a 9-row gap between
fetal_death/file_inventory.csv (34 rows pre-C8.11) and the v2.4.0 43-year
data envelope (V3b 1982-1988 + V2.1 2003-2004 silently missing). The C8.11
DO patched the inventory to 43 rows. C8.12 B.7 codifies the underlying
invariant as a durable test so any future inventory-vs-schema drift is
caught at CI gate rather than at next-task PRE-FLIGHT cheap-check.

Each test compares two facts that SHOULD agree by construction:
  - The set of years documented in the subproject's file_inventory.csv
  - The set of years claimed by the harmonized_schema.csv years_available
    column (union across all column rows).

When the two sets disagree, EITHER:
  (a) The inventory is missing a year that the harmonization pipeline
      produced (the C8.11 V3b+V2.1 case), OR
  (b) The schema claims years_available that don't have a corresponding
      raw input documented (e.g., a stale CSV entry from a deprecated
      year, or an out-of-scope ETL-only year).

Either case is an L13-class staleness bug warranting a fix-on-contact patch.
"""

from __future__ import annotations

import csv
import re
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]


def _read_inventory_year_set(path: Path) -> set[int]:
    """Return the set of integer years in a file_inventory.csv.

    Skips rows with non-integer year keys (e.g., the natality inventory's
    `<YYYY>_linked` cohort-year keys, which point to the linked-cohort
    product, not the natality-births product).
    """
    years: set[int] = set()
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            try:
                years.add(int(row["year"]))
            except (KeyError, ValueError):
                continue
    return years


_YEAR_RANGE = re.compile(r"(\d{4})\s*-\s*(\d{4})")
_YEAR_SINGLE = re.compile(r"(?<!\d)(\d{4})(?!\d)")


def _read_schema_years_available_union(path: Path) -> set[int]:
    """Return the union of all years_available ranges from a harmonized_schema.csv.

    Cells use comma-separated `start-end` ranges (e.g., `1992-2002,2005-2024`)
    or single years. Natality schema cells additionally carry product-scope
    annotations (e.g., `2005-2023 (linked)` indicates a linked-cohort-only
    column). Annotations are stripped via regex; the test treats the union
    of every documented year regardless of product scope as the schema's
    coverage envelope.
    """
    years: set[int] = set()
    with open(path, newline="") as fh:
        for row in csv.DictReader(fh):
            ya = (row.get("years_available") or "").strip()
            if not ya:
                continue
            for part in ya.split(","):
                part = part.strip()
                if not part:
                    continue
                m = _YEAR_RANGE.search(part)
                if m:
                    years.update(range(int(m.group(1)), int(m.group(2)) + 1))
                    continue
                m1 = _YEAR_SINGLE.search(part)
                if m1:
                    years.add(int(m1.group(1)))
    return years


def test_fetal_death_inventory_years_match_schema_years_available():
    """fetal_death/file_inventory.csv year-set must equal harmonized_schema.csv years_available union."""
    inv = _REPO / "fetal_death" / "file_inventory.csv"
    sch = _REPO / "fetal_death" / "harmonized_schema.csv"
    if not inv.is_file() or not sch.is_file():
        pytest.skip(f"missing input: {inv} or {sch}")
    inv_years = _read_inventory_year_set(inv)
    sch_years = _read_schema_years_available_union(sch)

    missing_from_schema = inv_years - sch_years
    missing_from_inventory = sch_years - inv_years

    assert not missing_from_schema, (
        f"fetal_death inventory has years not in schema years_available: "
        f"{sorted(missing_from_schema)} — schema CSV likely stale relative to inventory"
    )
    assert not missing_from_inventory, (
        f"fetal_death schema years_available has years not in inventory: "
        f"{sorted(missing_from_inventory)} — inventory CSV likely stale relative to schema (C8.11-class)"
    )


def test_natality_inventory_years_match_schema_years_available():
    """natality/metadata/file_inventory.csv numeric-year keys must equal harmonized_schema.csv years_available union.

    The `<YYYY>_linked` rows are skipped — they belong to the linked-cohort
    product, which uses a sibling schema (external_validation_targets_v3_linked.csv
    + the harmonize_linked_v3.py / derive_linked_v3.py pipeline).
    """
    inv = _REPO / "natality" / "metadata" / "file_inventory.csv"
    sch = _REPO / "natality" / "metadata" / "harmonized_schema.csv"
    if not inv.is_file() or not sch.is_file():
        pytest.skip(f"missing input: {inv} or {sch}")
    inv_years = _read_inventory_year_set(inv)
    sch_years = _read_schema_years_available_union(sch)

    missing_from_schema = inv_years - sch_years
    missing_from_inventory = sch_years - inv_years

    assert not missing_from_schema, (
        f"natality inventory has years not in schema years_available: "
        f"{sorted(missing_from_schema)}"
    )
    assert not missing_from_inventory, (
        f"natality schema years_available has years not in inventory: "
        f"{sorted(missing_from_inventory)}"
    )


def test_fetal_death_inventory_record_length_populated_for_all_rows():
    """fetal_death/file_inventory.csv record_length column is populated for every row.

    Motivated by the C8.12 B.7 L13 audit (2026-05-13): 17 of 43 rows had EMPTY
    record_length cells + 2 had off-by-1 MISMATCH. Patched at C8.12 DO step 1 to
    standardize on the no-terminator convention matching field_specs.py.
    This test fails fast if any future inventory row ships with an EMPTY
    record_length cell.
    """
    inv = _REPO / "fetal_death" / "file_inventory.csv"
    if not inv.is_file():
        pytest.skip(f"missing input: {inv}")
    empty_years: list[int] = []
    with open(inv, newline="") as fh:
        for row in csv.DictReader(fh):
            rl = (row.get("record_length") or "").strip()
            if not rl:
                empty_years.append(int(row["year"]))
    assert not empty_years, (
        f"fetal_death/file_inventory.csv has EMPTY record_length cells for years: {empty_years}"
    )
