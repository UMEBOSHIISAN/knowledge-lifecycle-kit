"""Read-only knowledge lifecycle inspection and unified trust writer."""

__version__ = "0.1.0"

from .parser import FrontmatterError, ParsedMarkdown, parse_markdown
from .transitions import TransitionDecision, propose_from_result, propose_transition
from .trust_writer import (
    KnowledgeTrustError,
    KnowledgeTrustResult,
    KnowledgeTrustWriter,
    PromotionGateError,
    StorageBoundaryError,
    StorageDurabilityError,
)
from .validator import ValidationIssue, ValidationResult, validate_file, validate_metadata

__all__ = [
    "FrontmatterError",
    "KnowledgeTrustError",
    "KnowledgeTrustResult",
    "KnowledgeTrustWriter",
    "ParsedMarkdown",
    "PromotionGateError",
    "StorageBoundaryError",
    "StorageDurabilityError",
    "TransitionDecision",
    "ValidationIssue",
    "ValidationResult",
    "parse_markdown",
    "propose_from_result",
    "propose_transition",
    "validate_file",
    "validate_metadata",
]
