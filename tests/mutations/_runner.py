"""DESIGN: tracks-current-state — shared B.6 mutation-test subprocess runner.

Per C8.12 §15 + STATUS 2026-05-13T21:00:00Z: each B.6 mutation test injects a
known violation into a validator (either via a tempdir-mutated input CSV or
via a module-level constant patched in a child-process bootstrap), spawns the
validator in a subprocess, and asserts (i) non-zero returncode AND (ii) a
FAIL surface in captured stdout/stderr. The AND aggregation is L14 defense:
a validator that exits non-zero for an unrelated reason (e.g., import crash)
without printing a per-row FAIL marker is NOT a passing mutation test.

The runner deliberately does NOT pin a specific returncode. The 7 validators
in scope use either `sys.exit(1)` (4) or `raise SystemExit(2)` (2) or
`raise SystemExit(1)` (1). Pinning `== 1` would break under future code-style
unification; the structural invariant is "non-zero exit + FAIL surface."

The bootstrap harness imports the validator as a module (so `__name__` is the
module name, NOT `__main__`), patches one or more module-level attributes, then
calls `main()`. SystemExit propagates naturally to the child-process exit code.
The validator's own `Path(__file__).resolve().parents[N]` paths still resolve
correctly because the validator's `__file__` is its real on-disk location, not
the harness's location.
"""

from __future__ import annotations

import shlex
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def run_validator_with_module_mutation(
    validator_path: Path,
    mutations: list[str],
    cli_args: list[str] | None = None,
    timeout: int = 600,
) -> subprocess.CompletedProcess:
    """Spawn `validator_path` after applying `mutations` to its module namespace.

    Each entry in `mutations` is a Python statement executed in the child after
    the validator module is loaded. Examples:
        "v.NVSR_FETAL_DEATHS[2022] = 999_999"
        "v.LIVE_BIRTHS[2022] = 1"

    The validator's `main()` is then called via the same `if __name__ == ...`
    path it uses normally. The harness sets `sys.argv` so argparse-using
    validators see the requested CLI args.

    Returns a CompletedProcess; SystemExit from the validator becomes the
    child-process returncode.
    """
    cli_args = cli_args or []
    mutation_block = "\n".join(mutations)
    harness = f"""
import importlib.util, sys
spec = importlib.util.spec_from_file_location("v", {str(validator_path)!r})
v = importlib.util.module_from_spec(spec)
sys.modules["v"] = v
spec.loader.exec_module(v)
{mutation_block}
sys.argv = [{str(validator_path)!r}] + {cli_args!r}
v.main()
"""
    return subprocess.run(
        [sys.executable, "-c", harness],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(REPO_ROOT),
    )


def run_validator_with_args(
    validator_path: Path,
    cli_args: list[str],
    timeout: int = 600,
) -> subprocess.CompletedProcess:
    """Spawn `validator_path` directly with the given CLI args (no module mutation).

    Used by tests that mutate the validator's INPUT CSV in a tempdir and pass
    the tempdir-CSV path via `--targets`. No bootstrap harness needed.
    """
    return subprocess.run(
        [sys.executable, str(validator_path), *cli_args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(REPO_ROOT),
    )


def assert_mutation_caught(
    result: subprocess.CompletedProcess,
    fail_markers: list[str] | None = None,
    output_files_with_fail_text: list[Path] | None = None,
) -> None:
    """Convention 1 SHAPE-not-VALUE assertion + L14 AND-of-rows aggregation.

    BOTH conditions must hold:
      (i) returncode != 0  (validator exited with a failure code)
      (ii) at least one FAIL surface in either:
           - captured stdout OR stderr (if `fail_markers` provided), OR
           - the on-disk content of `output_files_with_fail_text` (validators
             whose FAIL detail lands in a written report rather than stdout —
             e.g., `compare_external_targets_v1.py` writes per-row `status=fail`
             into the comparison CSV; the stdout only carries `Wrote <path>`).
    Pinning `returncode == 1` would break for the 2 validators that use
    `SystemExit(2)`; pinning the exact FAIL marker text would break under
    routine output-message rewording (Convention 2 `tracks-current-state`).
    """
    cmd = shlex.join(result.args) if isinstance(result.args, list) else str(result.args)
    combined = (result.stdout or "") + (result.stderr or "")

    assert result.returncode != 0, (
        f"Mutation runner expected non-zero returncode; got {result.returncode}.\n"
        f"Command: {cmd}\n"
        f"--- STDOUT ---\n{result.stdout}\n"
        f"--- STDERR ---\n{result.stderr}\n"
    )

    stdout_match = bool(fail_markers) and any(m in combined for m in fail_markers)
    file_match = False
    if output_files_with_fail_text:
        for f in output_files_with_fail_text:
            if f.is_file() and "fail" in f.read_text(encoding="utf-8").lower():
                file_match = True
                break

    assert stdout_match or file_match, (
        f"Mutation runner expected a FAIL surface in stdout markers={fail_markers!r} "
        f"or output files {output_files_with_fail_text!r}; none found.\n"
        f"Command: {cmd}\n"
        f"Returncode: {result.returncode}\n"
        f"--- STDOUT ---\n{result.stdout}\n"
        f"--- STDERR ---\n{result.stderr}\n"
    )
