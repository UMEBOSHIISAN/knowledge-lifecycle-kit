"""The read-only ``klg`` command line interface."""

from __future__ import annotations

import argparse
from datetime import date
from pathlib import Path
from typing import Sequence

from .report import build_report, render_human, render_json
from .validator import validate_file


def run_command(command: str, path: Path, *, as_of: date | None = None) -> dict:
    result = validate_file(path, as_of=as_of)
    return build_report(result)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="klg")
    commands = parser.add_subparsers(dest="command", required=True)
    for name in ("inspect", "validate", "propose-transition"):
        command = commands.add_parser(name)
        command.add_argument("file", type=Path)
        command.add_argument("--as-of", type=date.fromisoformat, default=None)
        command.add_argument("--json", action="store_true")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    report = run_command(args.command, args.file, as_of=args.as_of)
    if args.json:
        print(render_json(report), end="")
    else:
        print(render_human(report), end="")
    return 0 if report["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
