"""
Stream lines from the first member of an NCHS matched-multiples .zip.

Mirrors fetal_death/scripts/01_import/zip_text_stream.py byte-for-byte (each
subproject vendors its own copy per the §15.D standalone-subproject decision).
"""

from __future__ import annotations

import shutil
import subprocess
import zipfile
from collections.abc import Iterator
from pathlib import Path


def _first_member_name(zip_path: Path) -> str:
    with zipfile.ZipFile(zip_path) as zf:
        names = zf.namelist()
    if not names:
        raise ValueError(f"No members in {zip_path}")
    return names[0]


def _compression_method(zip_path: Path, member: str) -> int:
    with zipfile.ZipFile(zip_path) as zf:
        info = zf.getinfo(member)
        return int(info.compress_type)


def iter_lines_from_zip(
    zip_path: Path, member_name: str | None = None
) -> Iterator[bytes]:
    """
    Yield raw line bytes (including trailing \\r\\n if present) from the archive.

    Call ``.close()`` on the iterator if you stop early so any ``7z``
    child process is terminated.
    """
    zip_path = zip_path.resolve()
    member = member_name if member_name is not None else _first_member_name(zip_path)
    method = _compression_method(zip_path, member)

    if method in (zipfile.ZIP_STORED, zipfile.ZIP_DEFLATED):
        with zipfile.ZipFile(zip_path) as zf:
            with zf.open(member) as fh:
                for line in fh:
                    yield line
        return

    seven = shutil.which("7z")
    if not seven:
        raise RuntimeError(
            "This zip uses an unsupported compression method. "
            "Install 7-Zip CLI (`brew install p7zip`) and ensure `7z` is on PATH."
        )

    proc = subprocess.Popen(
        [seven, "x", "-so", str(zip_path), member],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    assert proc.stdout is not None
    killed = False
    try:
        while True:
            line = proc.stdout.readline()
            if not line:
                break
            yield line
    finally:
        if proc.poll() is None:
            proc.kill()
            killed = True
        proc.wait()
        if not killed and proc.returncode != 0:
            err = (proc.stderr.read() if proc.stderr else b"")[:500]
            raise RuntimeError(
                f"7z exited {proc.returncode} reading {zip_path}: {err!r}"
            )
