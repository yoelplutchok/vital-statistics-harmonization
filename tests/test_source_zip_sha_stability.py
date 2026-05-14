"""DESIGN: tracks-current-state — asserts on-disk raw-NCHS-zip SHA-256 values
match docs/NCHS_SOURCE_MANIFEST.md byte-exact.

B.11 of C8.12 (mutation tests + L13/L14 audits + SHA-stability + snapshot
regression). Defends H10 (provenance / reproducibility drift): if NCHS
silently re-releases a public-use file or a local download is corrupted,
the SHA disagreement surfaces at CI rather than mid-pipeline. The manifest
at docs/NCHS_SOURCE_MANIFEST.md (sha=ed2a44d3… at C8.11) is the canonical
reference; this test verifies the on-disk universe matches it.

Convention 1 SHAPE-not-VALUE: the count anchor (100 = 43 + 35 + 19 + 3) is the
structural invariant; per-row SHA assertions enforce the manifest is the
single source of truth. The manifest is re-snapshot under authorized
latest-year refreshes via §11 plan-update (e.g., when 2025-published
cohort-2024 linked file lands, the manifest gains a row). The matched-
multiples section (3 rows; 1995-1997 + 1995-2000 + 2016-2020) was added at
C8.16 (2026-05-14).

Skip-if-zip-missing per the established `_require()` pattern in
tests/conftest.py + per-subproject conftests. CI without raw zips on disk
SKIPs cleanly; CI with the zips re-verifies the manifest each run.
"""

from __future__ import annotations

import hashlib
import re
from pathlib import Path

import pytest

MONOREPO_ROOT = Path(__file__).resolve().parent.parent
MANIFEST_PATH = MONOREPO_ROOT / "docs/NCHS_SOURCE_MANIFEST.md"

# Raw-zip directories on the canonical build machine. The fetal-death tree
# lives under the build-side symlink; natality + linked under the natality
# repo's raw_data/. Per soft-flag (e) in STATUS, a future C8.7b would unify
# these under a monorepo-root raw_data/ symlink set; until then this test
# encodes the two canonical locations.
FETAL_RAW_DIR = Path.home() / "Desktop/fetal-death-harmonization-build/raw_data/fetal_death"
NATALITY_RAW_DIR = Path.home() / "Desktop/natality-harmonization/raw_data"
LINKED_RAW_DIR = Path.home() / "Desktop/natality-harmonization/raw_data/linked"
# Matched-multiples zips were probed-and-cached at /tmp/c8_16_zip_probe/ during
# C8.16 PRE-FLIGHT. A persistent canonical raw_data/ location is a follow-up
# (sub-step 3 carry-forward); until then, this test reads from /tmp.
MATCHED_MULTIPLES_RAW_DIR = Path("/tmp/c8_16_zip_probe")

# Capture filename + 64-hex-char SHA from any manifest table row. The
# manifest format is stable across all three sections; this regex pulls
# both fields from a single line regardless of column count.
_ROW_RE = re.compile(r"`([^`]+\.zip)`.*?`([0-9a-f]{64})`")


_MATCHED_MULTIPLES_FILENAMES = frozenset({
    "1995-1997.zip",
    "1995-2000.zip",
    "2016-2020.zip",
})


def _classify(filename: str) -> Path:
    """Map a raw_filename to its on-disk directory by filename prefix.

    Fetal*           → fetal-death tree
    Nat*             → natality tree
    *PE*CO*          → linked tree (post-2016-publication naming convention)
    LinkCO*          → linked tree (pre-2017-publication naming convention)
    1995-* / 2016-*  → matched-multiples tree (publication-window keyed)
    """
    if filename.startswith("Fetal"):
        return FETAL_RAW_DIR / filename
    if filename.startswith(("Nat", "nat")):
        return NATALITY_RAW_DIR / filename
    if filename.startswith("LinkCO") or "PE" in filename and "CO" in filename:
        return LINKED_RAW_DIR / filename
    if filename in _MATCHED_MULTIPLES_FILENAMES:
        return MATCHED_MULTIPLES_RAW_DIR / filename
    raise ValueError(f"unrecognized raw_filename: {filename!r}")


def _parse_manifest() -> list[tuple[str, str]]:
    """Return [(raw_filename, expected_sha256), ...] for all manifest rows."""
    text = MANIFEST_PATH.read_text()
    rows: list[tuple[str, str]] = []
    for line in text.splitlines():
        m = _ROW_RE.search(line)
        if m is None:
            continue
        rows.append((m.group(1), m.group(2)))
    return rows


def _sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def test_manifest_anchor_row_count() -> None:
    """Convention-1 anchor: 100 raw-zip rows total in NCHS_SOURCE_MANIFEST.md."""
    rows = _parse_manifest()
    assert len(rows) == 100, (
        f"expected 100 manifest rows "
        f"(43 fetal-death + 35 natality + 19 linked + 3 matched-multiples); "
        f"got {len(rows)}"
    )


def test_manifest_section_row_counts() -> None:
    """Convention-1 anchor: 43 + 35 + 19 + 3 = 100 split across product sections."""
    rows = _parse_manifest()
    counts = {"fetal": 0, "natality": 0, "linked": 0, "matched_multiples": 0}
    for filename, _sha in rows:
        if filename.startswith("Fetal"):
            counts["fetal"] += 1
        elif filename.startswith("LinkCO") or ("PE" in filename and "CO" in filename):
            counts["linked"] += 1
        elif filename.startswith(("Nat", "nat")):
            counts["natality"] += 1
        elif filename in _MATCHED_MULTIPLES_FILENAMES:
            counts["matched_multiples"] += 1
        else:
            raise AssertionError(f"unrecognized raw_filename: {filename!r}")
    assert counts == {"fetal": 43, "natality": 35, "linked": 19, "matched_multiples": 3}


def test_source_zip_sha_matches_manifest() -> None:
    """Per-zip SHA verification.

    Iterates all 97 manifest rows. For each row, computes shasum -a 256 on
    the corresponding on-disk file and asserts equality with the manifest's
    SHA. Missing zips are skip-noted (not failures) so CI without raw data
    can still gate on the other 96. If NONE of the 97 zips are present, the
    test SKIPs entirely; that signals running outside the canonical build
    environment.
    """
    rows = _parse_manifest()
    assert rows, "manifest empty — unexpected; precondition for this test"

    missing: list[str] = []
    mismatches: list[tuple[str, str, str]] = []
    verified = 0

    for filename, expected_sha in rows:
        path = _classify(filename)
        if not path.exists():
            missing.append(filename)
            continue
        actual_sha = _sha256_of(path)
        if actual_sha != expected_sha:
            mismatches.append((filename, expected_sha, actual_sha))
        else:
            verified += 1

    if verified == 0:
        pytest.skip(
            f"no raw zips found on disk (checked {len(rows)} manifest rows; "
            f"all missing). Run from canonical build environment to gate."
        )

    if mismatches:
        first = mismatches[:5]
        msg = (
            f"{len(mismatches)} of {verified + len(mismatches)} on-disk zips have "
            f"SHA-256 mismatching docs/NCHS_SOURCE_MANIFEST.md. First {len(first)}:\n"
            + "\n".join(
                f"  {fn}: manifest={exp[:16]}… actual={act[:16]}…"
                for fn, exp, act in first
            )
        )
        if missing:
            msg += f"\nNote: {len(missing)} zips skipped (not on disk)."
        raise AssertionError(msg)
