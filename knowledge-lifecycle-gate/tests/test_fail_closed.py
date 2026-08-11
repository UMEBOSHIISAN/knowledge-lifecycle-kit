from __future__ import annotations

from pathlib import Path

import pytest

from knowledge_lifecycle_gate.parser import FrontmatterError, parse_markdown
from knowledge_lifecycle_gate.validator import validate_metadata


def test_missing_lineage_is_an_error_after_admission() -> None:
    result = validate_metadata(
        {"asset_type": "EVIDENCE", "state": "CANDIDATE", "lineage": []}
    )

    assert result.valid is False
    assert any(issue.code == "lineage_missing" for issue in result.issues)


def test_new_without_lineage_is_only_a_warning() -> None:
    result = validate_metadata({"asset_type": "CONCEPT", "state": "NEW"})

    assert result.valid is True
    assert any(issue.code == "lineage_missing" for issue in result.issues)


def test_unknown_public_state_fails_closed() -> None:
    result = validate_metadata(
        {"asset_type": "EVIDENCE", "state": "UNDER_REVIEW", "lineage": ["x"]}
    )

    assert result.valid is False
    assert any(issue.code == "state_unsupported" for issue in result.issues)


def test_malformed_frontmatter_is_rejected(tmp_path: Path) -> None:
    note = tmp_path / "malformed.md"
    note.write_text("---\nasset_type: EVIDENCE\n  broken\n---\n", encoding="utf-8")

    with pytest.raises(FrontmatterError):
        parse_markdown(note)
