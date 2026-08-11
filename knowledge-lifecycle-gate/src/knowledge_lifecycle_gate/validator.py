"""Fail-closed validation for the public KLG adapter profile."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Mapping

from .parser import FrontmatterError, ParsedMarkdown, parse_markdown
from .transitions import PUBLIC_STATES, propose_transition


PUBLIC_ASSET_TYPES = (
    "CONCEPT",
    "EVIDENCE",
    "TRIAL",
    "PROCEDURE",
    "QUESTION",
)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str
    severity: str = "error"


@dataclass
class ValidationResult:
    path: Path | None
    metadata: dict[str, Any]
    valid: bool
    asset_type: str | None = None
    state: str | None = None
    freshness: str = "UNKNOWN"
    issues: list[ValidationIssue] = field(default_factory=list)
    parsed: ParsedMarkdown | None = None


def _date(value: Any, field_name: str, issues: list[ValidationIssue]) -> date | None:
    if not isinstance(value, str):
        issues.append(
            ValidationIssue(
                f"{field_name}_invalid",
                f"{field_name} must be an ISO date string",
            )
        )
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        issues.append(
            ValidationIssue(
                f"{field_name}_invalid",
                f"{field_name} must be YYYY-MM-DD",
            )
        )
        return None


def _lineage(metadata: Mapping[str, Any], state: str | None, issues: list[ValidationIssue]) -> None:
    value = metadata.get("lineage")
    if not isinstance(value, list) or not value or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        severity = "warning" if state == "NEW" else "error"
        issues.append(
            ValidationIssue(
                "lineage_missing",
                "lineage must contain at least one non-empty source after NEW",
                severity=severity,
            )
        )
    elif any(
        item.startswith(("/", "~")) or ("/" + "Users/") in item or "\\Users\\" in item
        for item in value
    ):
        issues.append(
            ValidationIssue(
                "private_path",
                "lineage must not expose a user-specific absolute path",
            )
        )


def validate_metadata(
    metadata: Mapping[str, Any], *, as_of: date | None = None, path: Path | None = None
) -> ValidationResult:
    """Validate metadata without touching its source."""

    issues: list[ValidationIssue] = []
    normalized = dict(metadata)
    asset_type = normalized.get("asset_type")
    state = normalized.get("state")
    if asset_type not in PUBLIC_ASSET_TYPES:
        issues.append(
            ValidationIssue("asset_type_unsupported", "asset_type is not in the public profile")
        )
    if state not in PUBLIC_STATES:
        issues.append(
            ValidationIssue("state_unsupported", "state is not in the public profile")
        )

    _lineage(normalized, state if isinstance(state, str) else None, issues)
    today = as_of or date.today()
    freshness = "UNKNOWN"

    last_verified: date | None = None
    if "last_verified" in normalized:
        last_verified = _date(normalized["last_verified"], "last_verified", issues)
        if last_verified and last_verified > today:
            issues.append(
                ValidationIssue(
                    "last_verified_future",
                    "last_verified cannot be later than the validation date",
                )
            )

    expiration_values = [
        (name, normalized[name])
        for name in ("next_review", "valid_until")
        if name in normalized
    ]
    expiration_dates: list[tuple[str, date]] = []
    for name, value in expiration_values:
        parsed = _date(value, name, issues)
        if parsed:
            expiration_dates.append((name, parsed))
    if len(expiration_dates) == 2 and expiration_dates[0][1] != expiration_dates[1][1]:
        issues.append(
            ValidationIssue(
                "expiration_ambiguous",
                "next_review and valid_until disagree; choose one expiration field",
            )
        )

    if asset_type == "EVIDENCE" and state == "CONFIRMED":
        if "last_verified" not in normalized:
            issues.append(
                ValidationIssue(
                    "last_verified_missing",
                    "confirmed Evidence requires last_verified",
                )
            )
        if not expiration_values:
            issues.append(
                ValidationIssue(
                    "expiration_missing",
                    "confirmed Evidence requires next_review or valid_until",
                )
            )

    if expiration_dates and state == "CONFIRMED":
        expiration = expiration_dates[0][1]
        freshness = "EXPIRED" if today > expiration else "FRESH"

    request = normalized.get("transition_request")
    if request is not None:
        if not isinstance(request, dict) or not isinstance(
            request.get("target_state"), str
        ):
            issues.append(
                ValidationIssue(
                    "transition_request_invalid",
                    "transition_request.target_state must be a public state",
                )
            )
        elif state in PUBLIC_STATES:
            decision = propose_transition(state, request["target_state"])
            if not decision.allowed:
                code = "direct_promotion" if state == "NEW" and request["target_state"] == "CONFIRMED" else "transition_invalid"
                issues.append(ValidationIssue(code, decision.reason))

    valid = not any(issue.severity == "error" for issue in issues)
    return ValidationResult(
        path=path,
        metadata=normalized,
        valid=valid,
        asset_type=asset_type if isinstance(asset_type, str) else None,
        state=state if isinstance(state, str) else None,
        freshness=freshness,
        issues=issues,
    )


def validate_file(path: Path, *, as_of: date | None = None) -> ValidationResult:
    path = Path(path)
    try:
        parsed = parse_markdown(path)
    except (OSError, FrontmatterError) as exc:
        return ValidationResult(
            path=path,
            metadata={},
            valid=False,
            issues=[ValidationIssue("parse_error", str(exc))],
        )
    result = validate_metadata(parsed.metadata, as_of=as_of, path=path)
    result.parsed = parsed
    return result
