from __future__ import annotations

import hashlib
from pathlib import Path

from knowledge_lifecycle_gate.cli import run_command


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_inspect_and_propose_do_not_modify_source_assets() -> None:
    files = sorted((PROJECT_ROOT / "examples").glob("*.md"))
    before = {path: digest(path) for path in files}

    run_command("inspect", PROJECT_ROOT / "examples" / "evidence.md")
    run_command(
        "propose-transition", PROJECT_ROOT / "examples" / "stale_evidence.md"
    )

    after = {path: digest(path) for path in files}
    assert after == before
