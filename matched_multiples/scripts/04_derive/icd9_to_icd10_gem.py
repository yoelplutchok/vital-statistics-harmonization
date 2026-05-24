"""Load CMS ICD-9-CM → ICD-10-CM GEM and map NCHS UCOD codes."""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

_DEFAULT_GEM = (
    Path(__file__).resolve().parents[2] / "metadata" / "icd_gem" / "2018_I9gem.txt"
)


def nchs_ucod_to_gem_keys(code: str) -> list[str]:
    """Candidate 5-char GEM keys for a NCHS 4-position UCOD code."""
    c = str(code).strip().upper()
    if not c:
        return []

    keys: list[str] = []

    def add(raw: str) -> None:
        k = raw[:5].ljust(5)
        if k not in keys:
            keys.append(k)

    add(c)
    if len(c) == 3:
        add(c + "0")
        add(c + "00")
    if len(c) == 4:
        add(c + "0")
        add(c[:3])
        add(c[:3] + "0")
    if len(c) <= 4 and not c.startswith("E"):
        add("E" + c)
    return keys


def _pick_gem_target(
    candidates: list[tuple[str, bool, bool, bool]],
) -> tuple[str, bool]:
    """Choose one ICD-10 target from GEM rows for a single ICD-9 key."""
    good = [c for c in candidates if not c[2] and not c[3]]
    if not good:
        good = [c for c in candidates if not c[2]]
    if not good:
        good = candidates
    exact = [c for c in good if not c[1]]
    pool = exact or good
    icd10, approx, _, _ = sorted(pool, key=lambda x: x[0])[0]
    return icd10, approx


def load_gem_tables(
    gem_path: Path | None = None,
) -> dict[str, list[tuple[str, bool, bool, bool]]]:
    """Parse CMS fixed-width GEM file keyed by 5-char ICD-9-CM code."""
    path = gem_path or _DEFAULT_GEM
    by_key: dict[str, list[tuple[str, bool, bool, bool]]] = defaultdict(list)
    with path.open(encoding="ascii", errors="replace") as fh:
        for line in fh:
            i9 = line[0:5]
            i10 = line[6:13].strip()
            approx = line[14] == "1"
            no_map = line[15] == "1"
            combo = line[16] == "1"
            by_key[i9].append((i10, approx, no_map, combo))
    return by_key


def map_nchs_ucod(
    code: str,
    by_key: dict[str, list[tuple[str, bool, bool, bool]]],
) -> tuple[str | None, bool | None]:
    """Map one NCHS UCOD to ICD-10 via GEM; returns (icd10, approximate)."""
    for key in nchs_ucod_to_gem_keys(code):
        if key not in by_key:
            continue
        i10, approx = _pick_gem_target(by_key[key])
        return i10, approx
    return None, None
