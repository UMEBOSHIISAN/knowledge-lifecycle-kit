"""Human-gated public transition proposals."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


PUBLIC_STATES = ("NEW", "CANDIDATE", "CONFIRMED", "STALE", "RETIRED")

_ALLOWED = {
    "NEW": {"CANDIDATE"},
    "CANDIDATE": {"CONFIRMED"},
    "CONFIRMED": {"STALE", "RETIRED"},
    "STALE": {"RETIRED"},
    "RETIRED": set(),
}


@dataclass(frozen=True)
class TransitionDecision:
    allowed: bool
    current_state: str
    target_state: str
    event_type: str
    reason: str
    human_confirmation_required: bool


def _rejected(current_state: str, target_state: str, reason: str) -> TransitionDecision:
    return TransitionDecision(
        allowed=False,
        current_state=current_state,
        target_state=target_state,
        event_type="TRANSITION_REJECTED",
        reason=reason,
        human_confirmation_required=False,
    )


def propose_transition(current_state: str, target_state: str) -> TransitionDecision:
    """Validate a transition and return a proposal; never record a transition."""

    if current_state not in PUBLIC_STATES or target_state not in PUBLIC_STATES:
        return _rejected(
            current_state,
            target_state,
            "Unsupported public lifecycle state",
        )
    if current_state == "NEW" and target_state == "CONFIRMED":
        return _rejected(
            current_state,
            target_state,
            "Direct NEW -> CONFIRMED promotion is not allowed",
        )
    if target_state not in _ALLOWED[current_state]:
        return _rejected(
            current_state,
            target_state,
            f"Unsupported transition {current_state} -> {target_state}",
        )
    return TransitionDecision(
        allowed=True,
        current_state=current_state,
        target_state=target_state,
        event_type=f"{target_state}_PROPOSED",
        reason=f"Safe proposal for {current_state} -> {target_state}",
        human_confirmation_required=True,
    )


def propose_from_result(result: Any) -> TransitionDecision | None:
    """Derive one proposal from a validated result without mutating its source."""

    if not result.valid:
        return None
    requested = result.metadata.get("transition_request")
    if requested is not None:
        if not isinstance(requested, dict):
            return None
        return propose_transition(result.state, requested.get("target_state", ""))
    if (
        result.asset_type == "EVIDENCE"
        and result.state == "CONFIRMED"
        and result.freshness == "EXPIRED"
    ):
        return propose_transition("CONFIRMED", "STALE")
    return None
