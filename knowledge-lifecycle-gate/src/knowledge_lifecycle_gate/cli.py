"""The read-only ``klg`` command line interface."""

from __future__ import annotations

import argparse
import json
from datetime import date
from pathlib import Path
from typing import Any, Sequence

from .report import build_report, render_human, render_json
from .validator import validate_file


def run_command(
    command: str,
    path: Path,
    *,
    as_of: date | None = None,
    expected_digest: str | None = None,
) -> dict:
    result = validate_file(path, as_of=as_of, expected_digest=expected_digest)
    return build_report(result)


def _markdown_files(root: Path) -> list[Path]:
    return sorted(
        (
            candidate
            for candidate in root.rglob("*.md")
            if candidate.is_file()
            and not any(
                part.startswith(".") for part in candidate.relative_to(root).parts
            )
        ),
        key=lambda candidate: candidate.relative_to(root).as_posix(),
    )


def run_scan(root: Path, *, as_of: date | None = None) -> dict[str, Any]:
    """Validate every Markdown note under ``root`` without writing anything."""

    root = Path(root)
    reports: list[dict[str, Any]] = []
    by_state: dict[str, int] = {}
    by_freshness: dict[str, int] = {}
    valid_count = 0
    files = _markdown_files(root) if root.is_dir() else []
    for file_path in files:
        result = validate_file(file_path, as_of=as_of)
        report = build_report(result)
        report["file"] = file_path.relative_to(root).as_posix()
        reports.append(report)
        state_key = report["state"] or "UNKNOWN"
        by_state[state_key] = by_state.get(state_key, 0) + 1
        freshness_key = report["freshness"] or "UNKNOWN"
        by_freshness[freshness_key] = by_freshness.get(freshness_key, 0) + 1
        if report["valid"]:
            valid_count += 1
    return {
        "schema_version": "klg.scan.v0.1",
        "root": root.name,
        "summary": {
            "total": len(reports),
            "valid": valid_count,
            "invalid": len(reports) - valid_count,
            "by_state": by_state,
            "by_freshness": by_freshness,
        },
        "reports": reports,
        "mutation_performed": False,
    }


def _render_scan_human(scan: dict[str, Any]) -> str:
    summary = scan["summary"]
    lines = [f"Root: {scan['root']}"]
    for report in scan["reports"]:
        verdict = "PASS" if report["valid"] else "FAIL"
        lines.append(
            f"- {report['file']}: {report['state'] or 'UNKNOWN'}"
            f" / {report['freshness'] or 'UNKNOWN'} {verdict}"
        )
    lines.append(
        f"Files scanned: {summary['total']}"
        f" (valid {summary['valid']}, invalid {summary['invalid']})"
    )
    lines.append("Mutation performed: NO")
    return "\n".join(lines) + "\n"


def _render_scan_json(scan: dict[str, Any]) -> str:
    return json.dumps(scan, ensure_ascii=False, sort_keys=True, indent=2) + "\n"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="klg")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("inspect", "validate", "propose-transition"):
        command = commands.add_parser(name)
        command.add_argument("file", type=Path)
        command.add_argument("--as-of", type=date.fromisoformat, default=None)
        command.add_argument("--expect-digest", default=None)
        command.add_argument("--json", action="store_true")
    scan = commands.add_parser("scan")
    scan.add_argument("path", type=Path)
    scan.add_argument("--as-of", type=date.fromisoformat, default=None)
    scan.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.command == "scan":
        scan = run_scan(args.path, as_of=args.as_of)
        if args.json:
            print(_render_scan_json(scan), end="")
        else:
            print(_render_scan_human(scan), end="")
        summary = scan["summary"]
        return 0 if summary["total"] > 0 and summary["invalid"] == 0 else 1
    report = run_command(
        args.command,
        args.file,
        as_of=args.as_of,
        expected_digest=args.expect_digest,
    )
    if args.json:
        print(render_json(report), end="")
    else:
        print(render_human(report), end="")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
