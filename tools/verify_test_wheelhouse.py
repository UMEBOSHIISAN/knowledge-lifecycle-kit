"""Verify the explicit local wheelhouse used by release tests."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys
from typing import Sequence


ERROR = "test wheelhouse verification failed"


def verify_test_wheelhouse(manifest_path: Path, wheel_dir: Path) -> tuple[Path, ...]:
    """Return wheels named by a complete, hash-verified manifest."""
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        entries = manifest["wheels"]
        if not isinstance(entries, list) or not entries:
            raise ValueError
        verified: list[Path] = []
        filenames: set[str] = set()
        for entry in entries:
            if not isinstance(entry, dict):
                raise ValueError
            filename = entry.get("filename")
            digest = entry.get("sha256")
            if (
                not isinstance(filename, str)
                or Path(filename).name != filename
                or not filename.endswith(".whl")
                or filename in filenames
                or not isinstance(digest, str)
                or len(digest) != 64
                or any(character not in "0123456789abcdef" for character in digest)
            ):
                raise ValueError
            filenames.add(filename)
            wheel = wheel_dir / filename
            if not wheel.is_file():
                raise ValueError
            if hashlib.sha256(wheel.read_bytes()).hexdigest() != digest:
                raise ValueError
            verified.append(wheel)
        return tuple(verified)
    except (OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        raise ValueError(ERROR) from exc


def main(argv: Sequence[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    if len(arguments) != 2:
        print(json.dumps({"error": ERROR}, sort_keys=True))
        return 2
    try:
        wheels = verify_test_wheelhouse(Path(arguments[0]), Path(arguments[1]))
    except ValueError:
        print(json.dumps({"error": ERROR}, sort_keys=True))
        return 1
    print(json.dumps({"status": "passed", "wheels": [wheel.name for wheel in wheels]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
