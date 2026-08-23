"""Knowledge Trust Canonical Writer and Durability Subsystem.

Connects knowledge-lifecycle-gate (lifecycle semantics & promotion gate)
with memory_trust (immutable versions, audit trail, redaction, rollback).

Invariant (Gen2 Consolidation):
- SEMANTIC_OWNER: knowledge-lifecycle-gate (propose_transition / validate_metadata)
- DURABLE_WRITER: memory_trust storage substrate (store/, versions/, audit/, redact/)
- RUNTIME_ENTRYPOINT: KnowledgeTrustWriter.commit(...)
"""

from __future__ import annotations

from dataclasses import dataclass, field
import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Mapping

from .parser import parse_markdown, parse_markdown_text
from .transitions import propose_transition
from .validator import validate_metadata

_ALLOWED_PREFIXES = ("memory/", "decisions/", "synthesis/", "canon/", "history/")
_MAX_BYTES = 102400
_MAX_LINE_DELTA = 500


class KnowledgeTrustError(Exception):
    """Base error for Knowledge Trust subsystem."""


class PromotionGateError(KnowledgeTrustError):
    """Knowledge candidate failed lifecycle promotion criteria."""


class StorageBoundaryError(KnowledgeTrustError):
    """Storage boundary or path escape violation."""


class StorageDurabilityError(KnowledgeTrustError):
    """Failed to persist durable version or audit record."""


@dataclass(frozen=True)
class KnowledgeTrustResult:
    success: bool
    status: str
    target_path: str
    before_hash: str
    after_hash: str
    version_path: str | None
    audit_entry: dict[str, Any] | None
    changed: bool
    details: dict[str, Any] = field(default_factory=dict)


def compute_sha256(content: str | bytes) -> str:
    """Compute sha256:hex digest for content."""
    raw = content.encode("utf-8") if isinstance(content, str) else content
    return f"sha256:{hashlib.sha256(raw).hexdigest()}"


class KnowledgeTrustWriter:
    """Unified Canonical Writer for Knowledge Trust."""

    def __init__(self, base_dir: Path | str) -> None:
        self.base_dir = Path(base_dir).resolve()
        self.store_dir = self.base_dir / "store"
        self.versions_dir = self.base_dir / "versions"
        self.audit_dir = self.base_dir / "audit"
        self.redact_dir = self.base_dir / "redact"
        self.audit_path = self.audit_dir / "audit.jsonl"
        self.redact_path = self.redact_dir / "redact.jsonl"
        self._init_dirs()

    def _init_dirs(self) -> None:
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.versions_dir.mkdir(parents=True, exist_ok=True)
        self.audit_dir.mkdir(parents=True, exist_ok=True)
        self.redact_dir.mkdir(parents=True, exist_ok=True)
        if not self.audit_path.exists():
            self.audit_path.touch()
        if not self.redact_path.exists():
            self.redact_path.touch()

    def _validate_target_path(self, target_path: str) -> Path:
        if not target_path or target_path.endswith("/"):
            raise StorageBoundaryError(f"target_path must name a file, not directory: '{target_path}'")
        if ".." in target_path or target_path.startswith("/"):
            raise StorageBoundaryError(f"target_path contains illegal traversal or root: '{target_path}'")
        norm = target_path.replace("\\", "/")
        if not any(norm.startswith(prefix) for prefix in _ALLOWED_PREFIXES):
            raise StorageBoundaryError(
                f"target_path '{target_path}' is not in allowed prefixes {_ALLOWED_PREFIXES}"
            )
        resolved = (self.store_dir / norm).resolve()
        if not str(resolved).startswith(str(self.store_dir)):
            raise StorageBoundaryError(f"target_path escapes store root: '{target_path}'")
        return resolved

    def _validate_lifecycle(
        self,
        content: str,
        explicit_metadata: Mapping[str, Any] | None = None,
        as_of: datetime.date | None = None,
    ) -> tuple[dict[str, Any], str]:
        """Enforce lifecycle gate promotion rules (CONFIRMED knowledge only)."""
        metadata: dict[str, Any] = {}
        # Parse markdown frontmatter if present
        try:
            parsed_meta, _ = parse_markdown_text(content)
            metadata.update(parsed_meta)
        except Exception:
            pass

        if explicit_metadata:
            metadata.update(explicit_metadata)

        state = str(metadata.get("state", "UNKNOWN")).upper()
        
        # Explicit gate: UNKNOWN and ASSUMPTION cannot be committed as canonical knowledge
        if state in ("UNKNOWN", "ASSUMPTION"):
            raise PromotionGateError(
                f"Content with lifecycle state '{state}' cannot be written to canonical knowledge store."
            )

        # Run full knowledge-lifecycle-gate validation
        val_res = validate_metadata(metadata, as_of=as_of)
        if not val_res.valid:
            error_msgs = [f"[{issue.code}] {issue.message}" for issue in val_res.issues if issue.severity == "error"]
            if error_msgs:
                raise PromotionGateError(
                    f"Lifecycle validation failed: {'; '.join(error_msgs)}"
                )

        if val_res.state not in ("CONFIRMED", "STALE", "RETIRED"):
            raise PromotionGateError(
                f"Target lifecycle state '{val_res.state}' is not a valid canonical state (CONFIRMED required)."
            )

        return metadata, str(val_res.state)

    def commit(
        self,
        target_path: str,
        content: str,
        actor: str,
        reason: str,
        metadata: Mapping[str, Any] | None = None,
        approval_token: str | None = None,
        as_of: datetime.date | None = None,
    ) -> KnowledgeTrustResult:
        """Validate through lifecycle gate and commit an immutable version to memory_trust."""
        if not isinstance(content, str):
            raise KnowledgeTrustError("content must be a string")

        raw_bytes = content.encode("utf-8")
        if len(raw_bytes) > _MAX_BYTES:
            raise StorageBoundaryError(f"content exceeds max bytes ({len(raw_bytes)} > {_MAX_BYTES})")

        # 1. Lifecycle Validation (Promotion Gate)
        meta, canonical_state = self._validate_lifecycle(content, metadata, as_of=as_of)

        # 2. Path & Boundary Validation
        store_file = self._validate_target_path(target_path)
        version_dir = self.versions_dir / target_path
        version_dir.mkdir(parents=True, exist_ok=True)

        # 3. Compute Hashes & Check No-op
        before_hash = "none"
        if store_file.exists() and store_file.is_file():
            before_hash = compute_sha256(store_file.read_bytes())
            # Check line delta if not authorized
            before_lines = len(store_file.read_text(encoding="utf-8", errors="replace").splitlines())
            after_lines = len(content.splitlines())
            delta = abs(after_lines - before_lines)
            if delta > _MAX_LINE_DELTA and not approval_token:
                raise StorageBoundaryError(
                    f"line delta ({delta}) exceeds limit ({_MAX_LINE_DELTA}) without approval token"
                )

        after_hash = compute_sha256(raw_bytes)
        if before_hash == after_hash:
            return KnowledgeTrustResult(
                success=True,
                status="NO_CHANGE",
                target_path=target_path,
                before_hash=before_hash,
                after_hash=after_hash,
                version_path=None,
                audit_entry=None,
                changed=False,
                details={"message": "Content identical to existing canonical store; no-op."},
            )

        # 4. Write Immutable Version & Store Atomic Update
        ts_now = datetime.datetime.now(datetime.timezone.utc)
        ts_iso = ts_now.strftime("%Y-%m-%dT%H:%M:%SZ")
        ts_file = ts_now.strftime("%Y%m%dT%H%M%SZ")
        sha8 = after_hash.replace("sha256:", "")[:8]
        actor_safe = re.sub(r"[^A-Za-z0-9._-]", "_", actor)
        version_file = version_dir / f"{ts_file}_{actor_safe}_{sha8}.md"

        if version_file.exists():
            raise StorageDurabilityError(f"version file already exists: {version_file}")

        audit_entry = {
            "ts": ts_iso,
            "actor": actor,
            "action": "write",
            "target": target_path,
            "before_hash": before_hash,
            "after_hash": after_hash,
            "reason": reason,
            "state": canonical_state,
            "approval_token": approval_token,
        }

        # Atomic writes using temp files
        tmp_store = None
        tmp_version = None
        try:
            store_file.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile("wb", dir=str(store_file.parent), delete=False) as f_store:
                tmp_store = Path(f_store.name)
                f_store.write(raw_bytes)
                f_store.flush()
                os.fsync(f_store.fileno())

            with tempfile.NamedTemporaryFile("wb", dir=str(version_dir), delete=False) as f_ver:
                tmp_version = Path(f_ver.name)
                f_ver.write(raw_bytes)
                f_ver.flush()
                os.fsync(f_ver.fileno())

            os.replace(str(tmp_store), str(store_file))
            tmp_store = None
            os.replace(str(tmp_version), str(version_file))
            tmp_version = None

            # Append audit log
            with open(self.audit_path, "a", encoding="utf-8") as f_audit:
                f_audit.write(json.dumps(audit_entry, ensure_ascii=False) + "\n")
                f_audit.flush()

        except Exception as err:
            if tmp_store and tmp_store.exists():
                tmp_store.unlink(missing_ok=True)
            if tmp_version and tmp_version.exists():
                tmp_version.unlink(missing_ok=True)
            raise StorageDurabilityError(f"Failed to durably commit knowledge: {err}") from err

        return KnowledgeTrustResult(
            success=True,
            status="COMMITTED",
            target_path=target_path,
            before_hash=before_hash,
            after_hash=after_hash,
            version_path=str(version_file),
            audit_entry=audit_entry,
            changed=True,
            details={"state": canonical_state},
        )

    def rollback(
        self,
        target_path: str,
        version_filename: str,
        actor: str,
        reason: str,
    ) -> KnowledgeTrustResult:
        """Rollback active store to a previous immutable version without deleting history."""
        store_file = self._validate_target_path(target_path)
        version_file = (self.versions_dir / target_path / version_filename).resolve()

        if not version_file.exists() or not version_file.is_file():
            raise StorageBoundaryError(f"Version file '{version_filename}' not found in versions/{target_path}")

        before_hash = compute_sha256(store_file.read_bytes()) if store_file.exists() else "none"
        restored_bytes = version_file.read_bytes()
        after_hash = compute_sha256(restored_bytes)

        ts_now = datetime.datetime.now(datetime.timezone.utc)
        ts_iso = ts_now.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Atomic restore of store file
        store_file.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("wb", dir=str(store_file.parent), delete=False) as f_store:
            tmp_store = Path(f_store.name)
            f_store.write(restored_bytes)
            f_store.flush()
            os.fsync(f_store.fileno())

        os.replace(str(tmp_store), str(store_file))

        audit_entry = {
            "ts": ts_iso,
            "actor": actor,
            "action": "rollback",
            "target": target_path,
            "restored_version": version_filename,
            "before_hash": before_hash,
            "after_hash": after_hash,
            "reason": reason,
        }
        with open(self.audit_path, "a", encoding="utf-8") as f_audit:
            f_audit.write(json.dumps(audit_entry, ensure_ascii=False) + "\n")
            f_audit.flush()

        return KnowledgeTrustResult(
            success=True,
            status="ROLLED_BACK",
            target_path=target_path,
            before_hash=before_hash,
            after_hash=after_hash,
            version_path=str(version_file),
            audit_entry=audit_entry,
            changed=True,
            details={"restored_version": version_filename},
        )

    def redact(
        self,
        target_path: str,
        version_filename: str,
        actor: str,
        reason: str,
    ) -> KnowledgeTrustResult:
        """Record redaction event and mask/tombstone active store without destroying history."""
        store_file = self._validate_target_path(target_path)
        ts_now = datetime.datetime.now(datetime.timezone.utc)
        ts_iso = ts_now.strftime("%Y-%m-%dT%H:%M:%SZ")

        redact_entry = {
            "ts": ts_iso,
            "actor": actor,
            "target": target_path,
            "version": version_filename,
            "reason": reason,
        }
        with open(self.redact_path, "a", encoding="utf-8") as f_redact:
            f_redact.write(json.dumps(redact_entry, ensure_ascii=False) + "\n")
            f_redact.flush()

        # Update store with tombstone
        tombstone = f"---\nstate: RETIRED\nasset_type: PROCEDURE\ntitle: Redacted\ncreated: 2026-08-23\nlineage: [system]\n---\n# REDACTED\nThis knowledge item was redacted by {actor}: {reason}\n"
        tombstone_bytes = tombstone.encode("utf-8")
        before_hash = compute_sha256(store_file.read_bytes()) if store_file.exists() else "none"
        after_hash = compute_sha256(tombstone_bytes)

        store_file.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("wb", dir=str(store_file.parent), delete=False) as f_store:
            tmp_store = Path(f_store.name)
            f_store.write(tombstone_bytes)
            f_store.flush()
            os.fsync(f_store.fileno())

        os.replace(str(tmp_store), str(store_file))

        audit_entry = {
            "ts": ts_iso,
            "actor": actor,
            "action": "redact",
            "target": target_path,
            "redacted_version": version_filename,
            "before_hash": before_hash,
            "after_hash": after_hash,
            "reason": reason,
        }
        with open(self.audit_path, "a", encoding="utf-8") as f_audit:
            f_audit.write(json.dumps(audit_entry, ensure_ascii=False) + "\n")
            f_audit.flush()

        return KnowledgeTrustResult(
            success=True,
            status="REDACTED",
            target_path=target_path,
            before_hash=before_hash,
            after_hash=after_hash,
            version_path=None,
            audit_entry=audit_entry,
            changed=True,
            details={"redacted_version": version_filename},
        )

    def export_canonical_knowledge(self) -> list[dict[str, Any]]:
        """Deterministically enumerate and export all canonical knowledge items for Phase 3C."""
        entries: list[dict[str, Any]] = []
        if not self.store_dir.exists():
            return entries

        for root, _, files in os.walk(str(self.store_dir)):
            for fname in sorted(files):
                if fname.startswith("."):
                    continue
                file_path = Path(root) / fname
                rel_path = str(file_path.relative_to(self.store_dir)).replace("\\", "/")
                content = file_path.read_text(encoding="utf-8", errors="replace")
                digest = compute_sha256(content.encode("utf-8"))
                entries.append(
                    {
                        "target_path": rel_path,
                        "content": content,
                        "sha256": digest,
                        "mtime": file_path.stat().st_mtime,
                    }
                )
        # Deterministic sort by relative target path
        entries.sort(key=lambda x: x["target_path"])
        return entries
