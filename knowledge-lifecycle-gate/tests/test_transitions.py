from __future__ import annotations

from knowledge_lifecycle_gate.transitions import (
    propose_transition,
    validate_transition_path,
)


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


def test_validate_transition_path_empty_or_too_short():
    assert validate_transition_path([]) == (False, "Transition path must contain at least 2 states", 0)
    assert validate_transition_path(["NEW"]) == (False, "Transition path must contain at least 2 states", 0)
    assert validate_transition_path(None) == (False, "Transition path must contain at least 2 states", 0)
    assert validate_transition_path(42) == (False, "Transition path must contain at least 2 states", 0)


def test_validate_transition_path_direct_illegal_jump():
    result = validate_transition_path(["NEW", "CONFIRMED"])
    assert result[0] is False
    assert result[2] == 0
    assert "direct" in result[1].lower()


def test_validate_transition_path_valid_full_lifecycle():
    result = validate_transition_path(["NEW", "CANDIDATE", "CONFIRMED", "STALE", "RETIRED"])
    assert result == (True, "Valid transition path across 4 steps", 4)


def test_validate_transition_path_intermediate_rejection():
    result = validate_transition_path(["NEW", "CANDIDATE", "CONFIRMED", "NEW"])
    assert result[0] is False
    assert result[2] == 2


def test_validate_transition_path_unknown_state():
    result = validate_transition_path(["NEW", "BOGUS"])
    assert result[0] is False
    assert result[2] == 0

