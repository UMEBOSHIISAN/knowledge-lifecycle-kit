#!/usr/bin/env python3
"""Aggregate only execution receipts backed by passing verification."""

import argparse
import json
from collections import Counter
from pathlib import Path


def _events(path):
    for line_number, raw in enumerate(Path(path).read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            yield json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"malformed JSONL at line {line_number}") from exc


def compute_scoreboard(ledger_path):
    executions = {}
    passing = set()
    for event in _events(ledger_path):
        trace_id = event.get("trace_id")
        if not trace_id:
            continue
        if event.get("event_type") == "ExecutionReceipt":
            executions[trace_id] = event
        elif event.get("event_type") == "VerificationReceipt" and event.get("verification_status") == "pass":
            passing.add(trace_id)
    verified = [event for trace_id, event in executions.items() if trace_id in passing]
    counts = Counter(event.get("worker_alias", "UNKNOWN") for event in verified)
    return {
        "schema_version": "scoreboard.v1",
        "execution_receipts": len(executions),
        "verified_executions": len(verified),
        "verified_by_worker": dict(sorted(counts.items())),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", type=Path)
    args = parser.parse_args()
    print(json.dumps(compute_scoreboard(args.ledger), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
