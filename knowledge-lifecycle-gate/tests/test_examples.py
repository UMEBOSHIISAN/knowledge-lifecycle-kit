from __future__ import annotations

from pathlib import Path

from knowledge_lifecycle_gate.report import build_report
from knowledge_lifecycle_gate.validator import validate_file


PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = PROJECT_ROOT / "examples"


def test_valid_evidence_example_passes() -> None:
    result = validate_file(EXAMPLES / "evidence.md")

    assert result.valid is True
    assert result.asset_type == "EVIDENCE"
    assert result.state == "CONFIRMED"
    assert result.freshness == "FRESH"


def test_stale_evidence_example_proposes_stale_without_recording() -> None:
    result = validate_file(EXAMPLES / "stale_evidence.md")
    report = build_report(result)

    assert result.valid is True
    assert result.freshness == "EXPIRED"
    assert report["proposal"]["event_type"] == "STALE_PROPOSED"
    assert report["proposal"]["target_state"] == "STALE"
    assert report["proposal"]["human_confirmation_required"] is True
    assert report["mutation_performed"] is False


def test_invalid_promotion_example_is_rejected() -> None:
    result = validate_file(EXAMPLES / "invalid_promotion.md")
    report = build_report(result)

    assert result.valid is False
    assert any(issue.code == "direct_promotion" for issue in result.issues)
    assert report["proposal"] is None


def test_missing_lineage_example_is_rejected() -> None:
    result = validate_file(EXAMPLES / "missing_lineage.md")

    assert result.valid is False
    assert any(issue.code == "lineage_missing" for issue in result.issues)
