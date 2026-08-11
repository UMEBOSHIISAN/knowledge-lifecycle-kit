#!/usr/bin/env python3
"""Validate compact scorecard.v2 Markdown and pair evidence artifacts."""

import argparse
import json
from pathlib import Path


REQUIRED = {
    "schema_version", "date", "task_id", "run_id", "orchestrator",
    "verified_by", "grade", "outcome", "workers",
}
VERIFICATION_LEVELS = {"self-verified", "cross-verified", "human-verified"}


def _parse_frontmatter(text):
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("missing opening frontmatter delimiter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("missing closing frontmatter delimiter") from exc

    data = {}
    workers = []
    current_worker = None
    in_workers = False
    for raw in lines[1:end]:
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        stripped = raw.strip()
        if stripped == "workers:":
            in_workers = True
            data["workers"] = workers
            continue
        if in_workers and stripped.startswith("- "):
            current_worker = {}
            workers.append(current_worker)
            stripped = stripped[2:].strip()
            if stripped:
                key, separator, value = stripped.partition(":")
                if not separator:
                    raise ValueError("malformed worker field")
                current_worker[key.strip()] = value.strip()
            continue
        if in_workers and raw.startswith("    ") and current_worker is not None:
            key, separator, value = stripped.partition(":")
            if not separator:
                raise ValueError("malformed worker field")
            current_worker[key.strip()] = value.strip()
            continue
        if in_workers:
            raise ValueError("malformed workers list")
        key, separator, value = stripped.partition(":")
        if not separator:
            raise ValueError("malformed scalar field")
        data[key.strip()] = value.strip()
    return data


def validate_scorecard(path):
    errors = []
    try:
        data = _parse_frontmatter(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        return [str(exc)]
    missing = sorted(REQUIRED - data.keys())
    if missing:
        errors.append("missing fields: " + ", ".join(missing))
    if data.get("schema_version") != "scorecard.v2":
        errors.append("schema_version must be scorecard.v2")
    if data.get("verified_by") not in VERIFICATION_LEVELS:
        errors.append("verified_by must be a declared verification level")
    workers = data.get("workers", [])
    if not workers:
        errors.append("at least one worker is required")
    required_worker = {"alias", "role", "outcome", "verification", "note"}
    for index, worker in enumerate(workers):
        absent = sorted(required_worker - worker.keys())
        if absent:
            errors.append(f"worker {index} missing fields: {', '.join(absent)}")
        if worker.get("verification") not in VERIFICATION_LEVELS:
            errors.append(f"worker {index} verification is invalid")
    return errors


def pair_artifacts(artifact_dir, scorecard_dir):
    artifacts = {path.stem for path in Path(artifact_dir).iterdir() if path.is_file()}
    scorecards = {path.stem for path in Path(scorecard_dir).iterdir() if path.is_file()}
    result = {}
    for name in sorted(artifacts | scorecards):
        if name in artifacts and name in scorecards:
            result[name] = "audit-ready"
        elif name in artifacts:
            result[name] = "evaluation unknown"
        else:
            result[name] = "evidence incomplete"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    validate = subparsers.add_parser("validate")
    validate.add_argument("scorecard", type=Path)
    pair = subparsers.add_parser("pair")
    pair.add_argument("artifacts", type=Path)
    pair.add_argument("scorecards", type=Path)
    args = parser.parse_args()
    if args.command == "validate":
        errors = validate_scorecard(args.scorecard)
        print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
        raise SystemExit(0 if not errors else 1)
    print(json.dumps(pair_artifacts(args.artifacts, args.scorecards), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
