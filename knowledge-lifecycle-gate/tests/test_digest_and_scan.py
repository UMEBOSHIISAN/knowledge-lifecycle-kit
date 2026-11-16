from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
import hashlib
from io import StringIO
import json
from pathlib import Path

from knowledge_lifecycle_gate.cli import main, run_scan


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = PROJECT_ROOT / "examples"

VALID_NOTE = """---
asset_type: EVIDENCE
state: CONFIRMED
lineage:
  - test-source
last_verified: 2026-01-01
next_review: 2099-01-01
---

Synthetic body.
"""

INVALID_NOTE = """---
asset_type: EVIDENCE
state: CONFIRMED
---

Body without lineage.
"""


@dataclass
class CliResult:
    returncode: int
    stdout: str
    stderr: str


def run_cli(*args: str) -> CliResult:
    stdout = StringIO()
    stderr = StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        returncode = main(args)
    return CliResult(returncode, stdout.getvalue(), stderr.getvalue())


def digest_of(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def test_report_includes_content_digest() -> None:
    target = EXAMPLES / "evidence.md"
    completed = run_cli("validate", str(target), "--json")
    assert completed.returncode == 0
    report = json.loads(completed.stdout)
    assert report["content_digest"] == digest_of(target)


def test_human_report_shows_content_digest() -> None:
    completed = run_cli("validate", str(EXAMPLES / "evidence.md"))
    assert completed.returncode == 0
    assert "Content digest: sha256:" in completed.stdout


def test_expect_digest_match_passes() -> None:
    target = EXAMPLES / "evidence.md"
    completed = run_cli(
        "validate", str(target), "--expect-digest", digest_of(target), "--json"
    )
    assert completed.returncode == 0
    report = json.loads(completed.stdout)
    assert report["valid"] is True


def test_expect_digest_mismatch_fails_closed() -> None:
    target = EXAMPLES / "evidence.md"
    wrong = "sha256:" + "0" * 64
    completed = run_cli(
        "validate", str(target), "--expect-digest", wrong, "--json"
    )
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["valid"] is False
    codes = {issue["code"] for issue in report["issues"]}
    assert "content_digest_mismatch" in codes


def test_expect_digest_malformed_fails_closed() -> None:
    target = EXAMPLES / "evidence.md"
    completed = run_cli(
        "validate", str(target), "--expect-digest", "not-a-digest", "--json"
    )
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    codes = {issue["code"] for issue in report["issues"]}
    assert "content_digest_invalid" in codes


def _write(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_scan_mixed_directory(tmp_path: Path) -> None:
    _write(tmp_path / "a" / "valid.md", VALID_NOTE)
    _write(tmp_path / "b" / "invalid.md", INVALID_NOTE)
    _write(tmp_path / "b" / "nested" / "valid.md", VALID_NOTE)
    _write(tmp_path / ".hidden" / "skipped.md", VALID_NOTE)
    _write(tmp_path / "notes.txt", "not markdown")

    completed = run_cli("scan", str(tmp_path), "--json")
    assert completed.returncode == 1
    scan = json.loads(completed.stdout)
    assert scan["schema_version"] == "klg.scan.v0.1"
    assert scan["mutation_performed"] is False
    assert scan["summary"]["total"] == 3
    assert scan["summary"]["valid"] == 2
    assert scan["summary"]["invalid"] == 1
    assert scan["summary"]["by_state"] == {"CONFIRMED": 3}
    files = [report["file"] for report in scan["reports"]]
    assert files == ["a/valid.md", "b/invalid.md", "b/nested/valid.md"]
    assert str(tmp_path) not in completed.stdout


def test_scan_all_valid_exit_zero(tmp_path: Path) -> None:
    _write(tmp_path / "one.md", VALID_NOTE)
    _write(tmp_path / "two.md", VALID_NOTE)
    completed = run_cli("scan", str(tmp_path), "--json")
    assert completed.returncode == 0
    scan = json.loads(completed.stdout)
    assert scan["summary"] == {
        "total": 2,
        "valid": 2,
        "invalid": 0,
        "by_state": {"CONFIRMED": 2},
        "by_freshness": {"FRESH": 2},
    }
    assert all(
        report["content_digest"] == digest_of(tmp_path / report["file"])
        for report in scan["reports"]
    )


def test_scan_human_output(tmp_path: Path) -> None:
    _write(tmp_path / "one.md", VALID_NOTE)
    completed = run_cli("scan", str(tmp_path))
    assert completed.returncode == 0
    assert "- one.md: CONFIRMED / FRESH PASS" in completed.stdout
    assert "Files scanned: 1 (valid 1, invalid 0)" in completed.stdout
    assert "Mutation performed: NO" in completed.stdout


def test_scan_empty_directory_fails_closed(tmp_path: Path) -> None:
    completed = run_cli("scan", str(tmp_path), "--json")
    assert completed.returncode == 1
    scan = json.loads(completed.stdout)
    assert scan["summary"]["total"] == 0


def test_scan_does_not_modify_files(tmp_path: Path) -> None:
    first = _write(tmp_path / "one.md", VALID_NOTE)
    second = _write(tmp_path / "sub" / "two.md", INVALID_NOTE)
    before = {path: digest_of(path) for path in (first, second)}
    run_scan(tmp_path)
    after = {path: digest_of(path) for path in (first, second)}
    assert after == before
