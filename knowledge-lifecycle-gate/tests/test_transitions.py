from __future__ import annotations

from knowledge_lifecycle_gate.transitions import propose_transition


def test_direct_new_to_confirmed_is_rejected() -> None:
    decision = propose_transition("NEW", "CONFIRMED")

    assert decision.allowed is False
    assert decision.event_type == "TRANSITION_REJECTED"
    assert "direct" in decision.reason.lower()
    assert decision.human_confirmation_required is False


def test_candidate_to_confirmed_is_a_human_gated_proposal() -> None:
    decision = propose_transition("CANDIDATE", "CONFIRMED")

    assert decision.allowed is True
    assert decision.event_type == "CONFIRMED_PROPOSED"
    assert decision.target_state == "CONFIRMED"
    assert decision.human_confirmation_required is True


def test_unknown_transition_fails_closed() -> None:
    decision = propose_transition("STALE", "CONFIRMED")

    assert decision.allowed is False
    assert decision.event_type == "TRANSITION_REJECTED"
    assert "unsupported" in decision.reason.lower()
