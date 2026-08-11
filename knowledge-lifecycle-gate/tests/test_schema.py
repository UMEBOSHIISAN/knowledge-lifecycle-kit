from __future__ import annotations

import json
from pathlib import Path

from knowledge_lifecycle_gate.parser import parse_markdown


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_public_schema_declares_only_the_experimental_profile() -> None:
    schema = json.loads(
        (PROJECT_ROOT / "schema" / "knowledge_asset.v0.1.json").read_text(
            encoding="utf-8"
        )
    )

    assert schema["title"] == "Knowledge Lifecycle Gate asset profile v0.1"
    assert schema["properties"]["asset_type"]["enum"] == [
        "CONCEPT",
        "EVIDENCE",
        "TRIAL",
        "PROCEDURE",
        "QUESTION",
    ]
    assert schema["properties"]["state"]["enum"] == [
        "NEW",
        "CANDIDATE",
        "CONFIRMED",
        "STALE",
        "RETIRED",
    ]
    assert schema["required"] == ["asset_type", "state", "lineage"]


def test_parser_reads_frontmatter_and_preserves_body(tmp_path: Path) -> None:
    note = tmp_path / "asset.md"
    note.write_text(
        "---\n"
        "asset_type: CONCEPT\n"
        "state: NEW\n"
        "lineage:\n"
        "  - synthetic-source\n"
        "---\n"
        "\nBody text.\n",
        encoding="utf-8",
    )

    parsed = parse_markdown(note)

    assert parsed.metadata == {
        "asset_type": "CONCEPT",
        "state": "NEW",
        "lineage": ["synthetic-source"],
    }
    assert parsed.body == "\nBody text.\n"
    assert parsed.raw == note.read_bytes()
