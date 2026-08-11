#!/usr/bin/env python3
"""Behavior contract for advisory routing and evidence scorecards."""

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "llm-routing" / "scripts"


def load_module(name):
    path = SCRIPTS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.routing = load_module("route")
        self.task = {
            "task_id": "task-001",
            "required_capabilities": ["audit", "python"],
            "max_cost_rank": 2,
            "risk_level": "low",
        }

    def test_filters_then_uses_stable_cost_priority_alias_order(self):
        workers = [
            {"alias": "zeta", "status": "available", "capabilities": ["audit", "python"], "cost_rank": 1, "priority": 3},
            {"alias": "alpha", "status": "available", "capabilities": ["audit", "python"], "cost_rank": 1, "priority": 3},
            {"alias": "cheap-missing", "status": "available", "capabilities": ["audit"], "cost_rank": 0, "priority": 0},
            {"alias": "retired", "status": "retired", "capabilities": ["audit", "python"], "cost_rank": 0, "priority": 0},
            {"alias": "expensive", "status": "available", "capabilities": ["audit", "python"], "cost_rank": 3, "priority": 0},
        ]
        decision = self.routing.route(self.task, workers)
        self.assertEqual("ROUTE_RECOMMENDED", decision["status"])
        self.assertEqual("alpha", decision["recommended_alias"])
        self.assertIsNone(decision["selected_alias"])
        self.assertIsNone(decision["actual_alias"])
        self.assertEqual(["alpha", "zeta"], decision["eligible_aliases"])

    def test_no_eligible_worker_requires_human_review(self):
        decision = self.routing.route(self.task, [])
        self.assertEqual("HUMAN_REVIEW_REQUIRED", decision["status"])
        self.assertIsNone(decision["recommended_alias"])

    def test_router_has_no_execution_surface(self):
        source = (SCRIPTS / "route.py").read_text(encoding="utf-8")
        for forbidden in ("subprocess", "os.system", "Popen", "exec(", "eval("):
            self.assertNotIn(forbidden, source)


class ScorecardTests(unittest.TestCase):
    def setUp(self):
        self.scorecard = load_module("scorecard")

    def test_validates_required_fields_workers_and_verification_level(self):
        valid = """---
schema_version: scorecard.v2
date: 2026-07-17
task_id: task-001
run_id: run-001
orchestrator: codex
verified_by: cross-verified
grade: A
outcome: done
workers:
  - alias: worker-a
    role: audit
    outcome: done
    verification: cross-verified
    note: synthetic fixture
---
"""
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "task-001.md"
            path.write_text(valid, encoding="utf-8")
            self.assertEqual([], self.scorecard.validate_scorecard(path))
            path.write_text(valid.replace("cross-verified", "VERIFIED"), encoding="utf-8")
            errors = self.scorecard.validate_scorecard(path)
            self.assertTrue(any("verification" in error for error in errors), errors)

    def test_pairs_artifacts_and_scorecards_without_overclaiming(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            artifacts = root / "artifacts"
            scorecards = root / "scorecards"
            artifacts.mkdir()
            scorecards.mkdir()
            (artifacts / "both.md").write_text("artifact", encoding="utf-8")
            (scorecards / "both.md").write_text("scorecard", encoding="utf-8")
            (artifacts / "artifact-only.md").write_text("artifact", encoding="utf-8")
            (scorecards / "scorecard-only.md").write_text("scorecard", encoding="utf-8")
            pairs = self.scorecard.pair_artifacts(artifacts, scorecards)
            self.assertEqual("audit-ready", pairs["both"])
            self.assertEqual("evaluation unknown", pairs["artifact-only"])
            self.assertEqual("evidence incomplete", pairs["scorecard-only"])


class ScoreboardTests(unittest.TestCase):
    def test_counts_only_execution_with_passing_verification(self):
        scoreboard = load_module("scoreboard")
        events = [
            {"event_type": "ExecutionReceipt", "trace_id": "t1", "worker_alias": "alpha", "outcome": "done"},
            {"event_type": "VerificationReceipt", "trace_id": "t1", "verification_status": "pass", "verification_level": "cross-verified"},
            {"event_type": "ExecutionReceipt", "trace_id": "t2", "worker_alias": "beta", "outcome": "done"},
            {"event_type": "VerificationReceipt", "trace_id": "t2", "verification_status": "pending", "verification_level": "self-verified"},
        ]
        with tempfile.TemporaryDirectory() as tmp:
            ledger = Path(tmp) / "receipts.jsonl"
            ledger.write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")
            result = scoreboard.compute_scoreboard(ledger)
        self.assertEqual(2, result["execution_receipts"])
        self.assertEqual(1, result["verified_executions"])
        self.assertEqual({"alpha": 1}, result["verified_by_worker"])


if __name__ == "__main__":
    unittest.main()
