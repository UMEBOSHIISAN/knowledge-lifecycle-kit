"""Human and machine-readable reports."""

from __future__ import annotations

import json
from typing import Any

from .transitions import TransitionDecision, propose_from_result
from .validator import ValidationResult


def build_report(
    result: ValidationResult, *, proposal: TransitionDecision | None = None
) -> dict[str, Any]:
    if proposal is None:
        proposal = propose_from_result(result)
    return {
        "schema_version": "klg.report.v0.1",
        "file": result.path.name if result.path else "<input>",
        "valid": result.valid,
        "asset_type": result.asset_type,
        "state": result.state,
        "freshness": result.freshness,
        "issues": [
            {"code": issue.code, "message": issue.message, "severity": issue.severity}
            for issue in result.issues
        ],
        "proposal": (
            {
                "event_type": proposal.event_type,
                "target_state": proposal.target_state,
                "reason": proposal.reason,
                "human_confirmation_required": proposal.human_confirmation_required,
            }
            if proposal and proposal.allowed
            else None
        ),
        "mutation_performed": False,
    }


def render_human(report: dict[str, Any]) -> str:
    proposal = report.get("proposal")
    suggested = proposal["event_type"] if proposal else "NONE"
    human_required = "YES" if proposal and proposal["human_confirmation_required"] else "NO"
    lines = [
        f"Asset type: {report.get('asset_type') or 'UNKNOWN'}",
        f"Current state: {report.get('state') or 'UNKNOWN'}",
        f"Freshness: {report.get('freshness', 'UNKNOWN')}",
        f"Suggested transition: {suggested}",
        f"Human confirmation required: {human_required}",
        "Mutation performed: NO",
        f"Validation: {'PASS' if report.get('valid') else 'FAIL'}",
    ]
    issues = report.get("issues", [])
    if issues:
        lines.append("Issues:")
        lines.extend(f"- {issue['code']}: {issue['message']}" for issue in issues)
    return "\n".join(lines) + "\n"


def render_json(report: dict[str, Any]) -> str:
    return json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
