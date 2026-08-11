"""Strict, read-only Markdown frontmatter parser.

The public profile intentionally supports a small YAML subset so the runtime
has no network or third-party dependency. Unsupported YAML constructs fail
closed instead of being silently misinterpreted.
"""

from __future__ import annotations

import ast
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class FrontmatterError(ValueError):
    """Raised when a Markdown note has unsupported or malformed frontmatter."""


_KEY_RE = re.compile(r"^[A-Za-z_][A-Za-z0-9_-]*$")


@dataclass(frozen=True)
class ParsedMarkdown:
    path: Path
    metadata: dict[str, Any]
    body: str
    raw: bytes

    @property
    def display_name(self) -> str:
        return self.path.name

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.raw).hexdigest()


def _scalar(value: str, *, line_number: int) -> Any:
    value = value.strip()
    if value == "":
        raise FrontmatterError(f"line {line_number}: empty scalar")
    if value in {"[]", "[ ]"}:
        return []
    if value in {"{}", "{ }"}:
        return {}
    if value.lower() in {"null", "~"}:
        return None
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value[:1] in {"'", '"'}:
        try:
            parsed = ast.literal_eval(value)
        except (SyntaxError, ValueError) as exc:
            raise FrontmatterError(f"line {line_number}: invalid quoted scalar") from exc
        if not isinstance(parsed, str):
            raise FrontmatterError(f"line {line_number}: quoted scalar must be text")
        return parsed
    if value.startswith("[") or value.startswith("{"):
        raise FrontmatterError(
            f"line {line_number}: inline collections are unsupported; use indented YAML"
        )
    return value


def _key_value(line: str, *, line_number: int) -> tuple[str, str]:
    if ":" not in line:
        raise FrontmatterError(f"line {line_number}: expected key: value")
    key, value = line.split(":", 1)
    key = key.strip()
    if not _KEY_RE.fullmatch(key):
        raise FrontmatterError(f"line {line_number}: invalid key {key!r}")
    return key, value.strip()


def _frontmatter_and_body(text: str) -> tuple[list[str], str]:
    lines = text.splitlines(keepends=True)
    if not lines or lines[0].rstrip("\r\n") != "---":
        raise FrontmatterError("Markdown must start with YAML frontmatter")

    closing_index = None
    for index in range(1, len(lines)):
        if lines[index].rstrip("\r\n") == "---":
            closing_index = index
            break
    if closing_index is None:
        raise FrontmatterError("frontmatter closing delimiter is missing")

    frontmatter = [line.rstrip("\r\n") for line in lines[1:closing_index]]
    body = "".join(lines[closing_index + 1 :])
    return frontmatter, body


def _parse_frontmatter(lines: list[str]) -> dict[str, Any]:
    metadata: dict[str, Any] = {}
    index = 0
    while index < len(lines):
        raw_line = lines[index]
        line_number = index + 2
        if "\t" in raw_line:
            raise FrontmatterError(f"line {line_number}: tabs are unsupported")
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            index += 1
            continue
        if raw_line.startswith(" "):
            raise FrontmatterError(f"line {line_number}: unexpected indentation")

        key, value = _key_value(raw_line, line_number=line_number)
        if key in metadata:
            raise FrontmatterError(f"line {line_number}: duplicate key {key!r}")
        if value:
            metadata[key] = _scalar(value, line_number=line_number)
            index += 1
            continue

        next_index = index + 1
        while next_index < len(lines) and not lines[next_index].strip():
            next_index += 1
        if next_index >= len(lines) or not lines[next_index].startswith("  "):
            metadata[key] = {}
            index += 1
            continue

        first_child = lines[next_index][2:]
        if first_child.startswith("- "):
            values: list[Any] = []
            child_index = next_index
            while child_index < len(lines):
                child_line = lines[child_index]
                if not child_line.strip():
                    child_index += 1
                    continue
                if not child_line.startswith("  - "):
                    break
                values.append(
                    _scalar(child_line[4:], line_number=child_index + 2)
                )
                child_index += 1
            metadata[key] = values
            index = child_index
            continue

        nested: dict[str, Any] = {}
        child_index = next_index
        while child_index < len(lines):
            child_line = lines[child_index]
            if not child_line.strip():
                child_index += 1
                continue
            if not child_line.startswith("  ") or child_line.startswith("    "):
                break
            nested_key, nested_value = _key_value(
                child_line[2:], line_number=child_index + 2
            )
            if nested_key in nested:
                raise FrontmatterError(
                    f"line {child_index + 2}: duplicate nested key {nested_key!r}"
                )
            if not nested_value:
                raise FrontmatterError(
                    f"line {child_index + 2}: nested mappings need a scalar value"
                )
            nested[nested_key] = _scalar(
                nested_value, line_number=child_index + 2
            )
            child_index += 1
        metadata[key] = nested
        index = child_index

    return metadata


def parse_markdown(path: Path) -> ParsedMarkdown:
    """Parse one Markdown note without writing to it or its parent directory."""

    path = Path(path)
    raw = path.read_bytes()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise FrontmatterError("Markdown must be valid UTF-8") from exc
    frontmatter, body = _frontmatter_and_body(text)
    return ParsedMarkdown(
        path=path,
        metadata=_parse_frontmatter(frontmatter),
        body=body,
        raw=raw,
    )
