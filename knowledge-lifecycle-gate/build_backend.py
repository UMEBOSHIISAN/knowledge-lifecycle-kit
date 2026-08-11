"""Dependency-free PEP 517/660 backend for the candidate package."""

from __future__ import annotations

import base64
import hashlib
import os
import stat
import zipfile
from pathlib import Path
from typing import Iterable


ROOT = Path(__file__).resolve().parent
NAME = "knowledge-lifecycle-gate"
DIST_NAME = "knowledge_lifecycle_gate"
VERSION = "0.1.0"
DIST_INFO = f"{DIST_NAME}-{VERSION}.dist-info"


def get_requires_for_build_editable(config_settings=None):
    return []


def get_requires_for_build_wheel(config_settings=None):
    return []


def _metadata() -> bytes:
    return (
        "Metadata-Version: 2.1\n"
        f"Name: {NAME}\n"
        f"Version: {VERSION}\n"
        "Summary: Read-only knowledge-asset lifecycle inspection and transition proposals\n"
        "Requires-Python: >=3.9\n"
        "License: MIT\n"
        "Provides-Extra: test\n"
        "Requires-Dist: pytest (>=8,<10); extra == \"test\"\n"
        "\n"
    ).encode("utf-8")


def _wheel_metadata() -> bytes:
    return (
        "Wheel-Version: 1.0\n"
        "Generator: knowledge-lifecycle-gate-build-backend\n"
        "Root-Is-Purelib: true\n"
        "Tag: py3-none-any\n"
    ).encode("utf-8")


def _entry_points() -> bytes:
    return b"[console_scripts]\nklg = knowledge_lifecycle_gate.cli:main\n"


def _record(name: str, content: bytes) -> str:
    digest = base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b"=").decode()
    return f"{name},sha256={digest},{len(content)}"


def _write_metadata(directory: Path) -> str:
    dist_info = directory / DIST_INFO
    dist_info.mkdir(parents=True, exist_ok=True)
    (dist_info / "METADATA").write_bytes(_metadata())
    (dist_info / "WHEEL").write_bytes(_wheel_metadata())
    (dist_info / "entry_points.txt").write_bytes(_entry_points())
    return DIST_INFO


def prepare_metadata_for_build_editable(metadata_directory, config_settings=None):
    return _write_metadata(Path(metadata_directory))


def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    return _write_metadata(Path(metadata_directory))


def _package_files() -> Iterable[tuple[str, bytes]]:
    package_root = ROOT / "src" / "knowledge_lifecycle_gate"
    for path in sorted(package_root.rglob("*.py")):
        yield f"knowledge_lifecycle_gate/{path.relative_to(package_root)}", path.read_bytes()


def _wheel_path(wheel_directory) -> Path:
    return Path(wheel_directory) / f"{DIST_NAME}-{VERSION}-py3-none-any.whl"


def _write_wheel(wheel_directory, *, editable: bool) -> str:
    wheel_path = _wheel_path(wheel_directory)
    files: list[tuple[str, bytes]] = list(_package_files())
    if editable:
        files.append(
            (
                "knowledge_lifecycle_gate_editable.pth",
                (str(ROOT / "src") + os.linesep).encode("utf-8"),
            )
        )
    else:
        files.append(
            (
                "knowledge_lifecycle_gate-0.1.0.data/scripts/klg",
                b"#!/usr/bin/env python3\nfrom knowledge_lifecycle_gate.cli import main\nraise SystemExit(main())\n",
            )
        )
    files.extend(
        [
            (f"{DIST_INFO}/METADATA", _metadata()),
            (f"{DIST_INFO}/WHEEL", _wheel_metadata()),
            (f"{DIST_INFO}/entry_points.txt", _entry_points()),
        ]
    )
    records = [_record(name, content) for name, content in files]
    records.append(f"{DIST_INFO}/RECORD,,")
    files.append((f"{DIST_INFO}/RECORD", ("\n".join(records) + "\n").encode("utf-8")))

    with zipfile.ZipFile(wheel_path, "w", compression=zipfile.ZIP_DEFLATED) as wheel:
        for name, content in files:
            info = zipfile.ZipInfo(name)
            info.date_time = (1980, 1, 1, 0, 0, 0)
            if name.endswith("/klg"):
                info.external_attr = stat.S_IFREG | 0o755
            wheel.writestr(info, content)
    return wheel_path.name


def build_editable(wheel_directory, config_settings=None, metadata_directory=None):
    return _write_wheel(wheel_directory, editable=True)


def build_wheel(wheel_directory, config_settings=None, metadata_directory=None):
    return _write_wheel(wheel_directory, editable=False)
