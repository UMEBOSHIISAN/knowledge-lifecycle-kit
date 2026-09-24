from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from dataclasses import dataclass
import json
from io import StringIO
from pathlib import Path

from knowledge_lifecycle_gate.cli import main


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = PROJECT_ROOT / "examples"


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


def test_validate_emits_json_without_absolute_paths() -> None:
    completed = run_cli("validate", str(EXAMPLES / "evidence.md"), "--json")
    assert completed.returncode == 0
    report = json.loads(completed.stdout)
    assert report["valid"] is True
    assert report["file"] == "evidence.md"
    assert ("/" + "Users/") not in completed.stdout
    assert report["mutation_performed"] is False


def test_propose_transition_emits_stale_proposal() -> None:
    completed = run_cli("propose-transition", str(EXAMPLES / "stale_evidence.md"), "--json")
    assert completed.returncode == 0
    report = json.loads(completed.stdout)
    assert report["proposal"]["event_type"] == "STALE_PROPOSED"
    assert report["proposal"]["human_confirmation_required"] is True


def test_human_report_mentions_no_mutation() -> None:
    completed = run_cli("propose-transition", str(EXAMPLES / "stale_evidence.md"))
    assert completed.returncode == 0
    assert "Suggested transition: STALE_PROPOSED" in completed.stdout
    assert "Human confirmation required: YES" in completed.stdout
    assert "Mutation performed: NO" in completed.stdout
    assert ("/" + "Users/") not in completed.stdout


def test_inspect_emits_report() -> None:
    completed = run_cli("inspect", str(EXAMPLES / "evidence.md"), "--json")
    assert completed.returncode == 0
    report = json.loads(completed.stdout)
    assert report["valid"] is True
    assert report["asset_type"] == "EVIDENCE"
    assert report["state"] == "CONFIRMED"


def test_validate_with_as_of_override() -> None:
    completed = run_cli("validate", str(EXAMPLES / "stale_evidence.md"), "--as-of", "2020-01-15", "--json")
    assert completed.returncode == 0
    report = json.loads(completed.stdout)
    assert report["freshness"] == "FRESH"


def test_cli_nonexistent_file_fails() -> None:
    completed = run_cli("validate", "nonexistent.md", "--json")
    assert completed.returncode == 1
    report = json.loads(completed.stdout)
    assert report["valid"] is False
    assert ("/" + "Users/") not in completed.stdout


