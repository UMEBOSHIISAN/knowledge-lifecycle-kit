"""Scan an explicit local tree for public-boundary violations."""

from __future__ import annotations

import json
import os
from pathlib import Path
import re
import sys
from typing import Sequence


IGNORED_DIRECTORIES = {
    ".git",
    ".pytest_cache",
    ".venv",
    ".verify-venv",
    ".wheelhouse",
    "__pycache__",
    "build",
    "dist",
}
RULES = (
    ("absolute_private_path", re.compile(r"/(?:Users|private|var)/")),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("github_token", re.compile(r"\b(?:ghp|github_pat)_[A-Za-z0-9_]+\b")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
)


def text_lines(path: Path) -> list[str] | None:
    try:
        payload = path.read_bytes()
    except OSError:
        return None
    if b"\0" in payload:
        return None
    try:
        return payload.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        return None


def check_public_tree(root: Path) -> list[dict[str, object]]:
    """Return sorted rule findings for an explicit non-symlinked directory."""
    root = root.resolve()
    violations: list[dict[str, object]] = []
    for directory, directories, filenames in os.walk(root, followlinks=False):
        directory_path = Path(directory)
        directories[:] = sorted(
            name
            for name in directories
            if name not in IGNORED_DIRECTORIES and not (directory_path / name).is_symlink()
        )
        for name in sorted(filenames):
            if name == ".git":
                continue
            path = directory_path / name
            if path.is_symlink():
                continue
            lines = text_lines(path)
            if lines is None:
                continue
            relative_path = path.relative_to(root).as_posix()
            for line_number, line in enumerate(lines, 1):
                for rule, pattern in RULES:
                    if pattern.search(line):
                        violations.append({"line": line_number, "path": relative_path, "rule": rule})
    return sorted(violations, key=lambda item: (item["path"], item["line"], item["rule"]))


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 1:
        print(json.dumps({"error": "invalid_root"}, sort_keys=True, separators=(",", ":")))
        return 2
    root = Path(arguments[0])
    if not root.is_dir() or root.is_symlink():
        print(json.dumps({"error": "invalid_root"}, sort_keys=True, separators=(",", ":")))
        return 2
    violations = check_public_tree(root)
    status = "passed" if not violations else "failed"
    print(json.dumps({"status": status, "violations": violations}, sort_keys=True, separators=(",", ":")))
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
