#!/usr/bin/env python3
"""Deterministic advisory routing. This module never executes a worker."""

import argparse
import json
from pathlib import Path


def route(task, workers):
    """Return a recommendation while leaving selection and execution unset."""
    required = set(task.get("required_capabilities", []))
    ceiling = int(task.get("max_cost_rank", 0))
    eligible = []
    for worker in workers:
        if worker.get("status") != "available":
            continue
        if int(worker.get("cost_rank", ceiling + 1)) > ceiling:
            continue
        if not required.issubset(set(worker.get("capabilities", []))):
            continue
        eligible.append(worker)

    eligible.sort(key=lambda worker: (
        int(worker["cost_rank"]),
        int(worker["priority"]),
        worker["alias"],
    ))
    aliases = [worker["alias"] for worker in eligible]
    recommended = aliases[0] if aliases else None
    risk = task.get("risk_level", "unknown")
    status = "ROUTE_RECOMMENDED" if recommended and risk in {"low", "medium"} else "HUMAN_REVIEW_REQUIRED"
    return {
        "schema_version": "routing_decision.v1",
        "task_id": task.get("task_id"),
        "status": status,
        "risk_level": risk,
        "recommended_alias": recommended,
        "selected_alias": None,
        "actual_alias": None,
        "eligible_aliases": aliases,
        "authority": "advisory-only",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", type=Path)
    parser.add_argument("workers", type=Path)
    args = parser.parse_args()
    task = json.loads(args.task.read_text(encoding="utf-8"))
    workers = json.loads(args.workers.read_text(encoding="utf-8"))
    print(json.dumps(route(task, workers), ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
