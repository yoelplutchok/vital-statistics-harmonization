"""Portable gate-parquet paths for notebook builders (D-prep.9).

Builders import resolved paths for their own execution. Notebook cells get
`paths_setup_source()` — portable env/repo/fallback logic, not literal paths.
"""

from __future__ import annotations

import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

_GATE_FN = """\
def _gate_parquet(env_var, repo_rel, build_fallback):
    override = os.environ.get(env_var)
    if override:
        return Path(override).expanduser()
    candidate = REPO_ROOT / repo_rel
    if candidate.exists():
        return candidate
    return Path(os.path.expanduser(build_fallback))
"""

_NAT = """\
NAT_PARQUET = _gate_parquet(
    "HVS_NATAL_DERIVED",
    "natality/output/harmonized/natality_v2_harmonized_derived.parquet",
    "~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet",
)"""

_LINKED = """\
LINKED_PARQUET = _gate_parquet(
    "HVS_LINKED_DERIVED",
    "natality/output/harmonized/natality_v3_linked_harmonized_derived.parquet",
    "~/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet",
)"""

_FD = """\
FD_PARQUET = _gate_parquet(
    "HVS_FETAL_DERIVED",
    "fetal_death/output/harmonized/fetal_death_derived.parquet",
    "~/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_derived.parquet",
)"""

_MM = """\
PARQUET = _gate_parquet(
    "HVS_MM_HARMONIZED",
    "matched_multiples/output/harmonized/matched_multiples_harmonized.parquet",
    "~/Desktop/vital-statistics-harmonization/matched_multiples/output/harmonized/matched_multiples_harmonized.parquet",
)"""

_STRAT = "STRAT_CSV = REPO_ROOT / 'fetal_death' / 'stratified_denominators.csv'"


def gate_parquet(env_var: str, repo_rel: str, build_fallback: str) -> Path:
    override = os.environ.get(env_var)
    if override:
        return Path(override).expanduser()
    candidate = REPO_ROOT / repo_rel
    if candidate.exists():
        return candidate
    return Path(os.path.expanduser(build_fallback))


NAT_PARQUET = gate_parquet(
    "HVS_NATAL_DERIVED",
    "natality/output/harmonized/natality_v2_harmonized_derived.parquet",
    "~/Desktop/natality-harmonization/output/harmonized/natality_v2_harmonized_derived.parquet",
)
LINKED_PARQUET = gate_parquet(
    "HVS_LINKED_DERIVED",
    "natality/output/harmonized/natality_v3_linked_harmonized_derived.parquet",
    "~/Desktop/natality-harmonization/output/harmonized/natality_v3_linked_harmonized_derived.parquet",
)
FD_PARQUET = gate_parquet(
    "HVS_FETAL_DERIVED",
    "fetal_death/output/harmonized/fetal_death_derived.parquet",
    "~/Desktop/fetal-death-harmonization-build/output/harmonized/fetal_death_derived.parquet",
)
MM_PARQUET = gate_parquet(
    "HVS_MM_HARMONIZED",
    "matched_multiples/output/harmonized/matched_multiples_harmonized.parquet",
    "~/Desktop/vital-statistics-harmonization/matched_multiples/output/harmonized/matched_multiples_harmonized.parquet",
)
STRAT_CSV = REPO_ROOT / "fetal_death" / "stratified_denominators.csv"


def parquet_basename_status(
    *,
    nat: bool = False,
    linked: bool = False,
    fd: bool = False,
    mm: bool = False,
) -> str:
    """Notebook-safe status line (filenames only — no absolute paths in outputs)."""
    parts: list[str] = []
    if nat:
        parts.append(f"natality={NAT_PARQUET.name}")
    if linked:
        parts.append(f"linked={LINKED_PARQUET.name}")
    if fd:
        parts.append(f"fetal={FD_PARQUET.name}")
    if mm:
        parts.append(f"matched_multiples={MM_PARQUET.name}")
    return "Parquets resolved: " + ", ".join(parts)


def paths_setup_source(
    *,
    marker: str = "README.md",
    sys_path: bool = False,
    nat: bool = False,
    linked: bool = False,
    fd: bool = False,
    strat: bool = False,
    mm: bool = False,
    nat_linked_aliases: bool = False,
) -> str:
    """Return portable path-setup Python for embedding in notebook code cells."""
    lines = [
        "import os",
        "from pathlib import Path",
        "",
        "REPO_ROOT = Path.cwd()",
        f"while not (REPO_ROOT / '{marker}').exists():",
        "    if REPO_ROOT == REPO_ROOT.parent:",
        "        raise RuntimeError('Run from the vital-statistics-harmonization repo.')",
        "    REPO_ROOT = REPO_ROOT.parent",
        "",
        _GATE_FN,
    ]
    if sys_path:
        lines.extend(["import sys", "sys.path.insert(0, str(REPO_ROOT))", ""])
    if nat:
        lines.append(_NAT)
    if linked:
        lines.append(_LINKED)
    if fd:
        lines.append(_FD)
    if strat:
        lines.append(_STRAT)
    if mm:
        lines.append(_MM)
    if nat_linked_aliases:
        lines.extend(["NAT = NAT_PARQUET", "LINKED = LINKED_PARQUET"])
    return "\n".join(lines) + "\n"
