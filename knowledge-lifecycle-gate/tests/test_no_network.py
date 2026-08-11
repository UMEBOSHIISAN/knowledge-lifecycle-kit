from __future__ import annotations

import socket
from pathlib import Path

from knowledge_lifecycle_gate.report import build_report
from knowledge_lifecycle_gate.transitions import propose_from_result
from knowledge_lifecycle_gate.validator import validate_file


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def fail_network(*args, **kwargs):
    raise AssertionError("network access is forbidden in the KLG runtime")


def test_validation_and_proposals_do_not_open_network(monkeypatch) -> None:
    monkeypatch.setattr(socket, "socket", fail_network)
    monkeypatch.setattr(socket, "create_connection", fail_network)

    result = validate_file(PROJECT_ROOT / "examples" / "stale_evidence.md")
    proposal = propose_from_result(result)
    report = build_report(result, proposal=proposal)

    assert report["proposal"]["event_type"] == "STALE_PROPOSED"
