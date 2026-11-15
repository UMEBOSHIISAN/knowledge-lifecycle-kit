"""Knowledge Trust Canonical Writer and Durability Subsystem.

Connects knowledge-lifecycle-gate (lifecycle semantics & promotion gate)
with memory_trust (immutable versions, audit trail, redaction, rollback).

Invariant (Gen2 Consolidation):
- SEMANTIC_OWNER: knowledge-lifecycle-gate (propose_transition / validate_metadata)
- DURABLE_WRITER: memory_trust storage substrate (store/, versions/, audit/, redact/)
- RUNTIME_ENTRYPOINT: KnowledgeTrustWriter.commit(...)
"""

from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass, field
import datetime
from functools import wraps
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Mapping

from .parser import FrontmatterError, parse_markdown_text
from .transitions import propose_transition
from .validator import ValidationResult, validate_metadata

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


def _serialized_write(method):
    @wraps(method)
    def run(writer, *args, **kwargs):
        with writer._publication_lock():
            return method(writer, *args, **kwargs)
    return run


def _expired_evidence(result: ValidationResult) -> bool:
    return (result.asset_type == "EVIDENCE" and result.state == "CONFIRMED"
            and result.freshness == "EXPIRED")


class KnowledgeTrustWriter:
    """Local single-writer API with compensation for synchronous I/O failures.

    Cooperating writers on a local POSIX filesystem reject lock contention.
    The lock does not protect against external writers, hostile path races
    or process/power loss. A failed compensation is reported to the caller.
    """

    def __init__(self, base_dir: Path | str) -> None:
        self.base_dir = Path(base_dir).resolve()
        self.store_dir = self.base_dir / "store"
        self.versions_dir = self.base_dir / "versions"
        self.audit_dir = self.base_dir / "audit"
        self.redact_dir = self.base_dir / "redact"
        self.audit_path = self.audit_dir / "audit.jsonl"
        self.redact_path = self.redact_dir / "redact.jsonl"
        self.base_dir.mkdir(mode=0o700, parents=True, exist_ok=True)
        self._init_dirs()

    @contextmanager
    def _publication_lock(self):
        try:
            import fcntl
            fd = os.open(self.base_dir, os.O_RDONLY | os.O_DIRECTORY)
        except (ImportError, OSError) as exc:
            raise StorageDurabilityError("Cannot open local Writer publication lock") from exc
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise StorageDurabilityError("Writer publication lock is busy") from exc
            except OSError as exc:
                raise StorageDurabilityError("Cannot acquire Writer publication lock") from exc
            yield
        finally:
            os.close(fd)

    def _confined(self, path: Path, root: Path) -> Path:
        """Reject existing symlinks and use component-wise containment."""
        try:
            path.relative_to(root)
            current = self.base_dir
            for part in path.relative_to(self.base_dir).parts:
                current = current / part
                if current.is_symlink():
                    raise StorageBoundaryError(f"Symlinked storage path: {current}")
            path.resolve().relative_to(root.resolve())
        except (ValueError, OSError, RuntimeError) as exc:
            raise StorageBoundaryError(f"Storage path escapes its root: {path}") from exc
        return path

    def _check_storage(self) -> None:
        for directory in (self.store_dir, self.versions_dir, self.audit_dir, self.redact_dir):
            self._confined(directory, self.base_dir)
            if directory.exists() and not directory.is_dir():
                raise StorageBoundaryError(f"Storage root is not a directory: {directory}")
        for log in (self.audit_path, self.redact_path):
            self._confined(log, self.base_dir)
            if log.exists() and not log.is_file():
                raise StorageBoundaryError(f"Storage log is not a regular file: {log}")

    @_serialized_write
    def _init_dirs(self) -> None:
        self._check_storage()
        for directory in (self.store_dir, self.versions_dir, self.audit_dir, self.redact_dir):
            directory.mkdir(mode=0o700, parents=True, exist_ok=True)
        for log in (self.audit_path, self.redact_path):
            if not log.exists():
                log.touch(mode=0o600, exist_ok=False)

    @staticmethod
    def _normalize_target(target_path: str) -> str:
        if not isinstance(target_path, str):
            raise StorageBoundaryError("target_path must be relative text")
        norm = target_path.replace("\\", "/")
        if (not norm or "\x00" in norm or norm.startswith("/")
                or any(part in ("", ".", "..") for part in norm.split("/"))
                or not any(norm.startswith(prefix) for prefix in _ALLOWED_PREFIXES)):
            raise StorageBoundaryError(f"Illegal canonical target: {target_path!r}")
        return norm

    def _validate_target_path(self, target_path: str) -> Path:
        self._check_storage()
        return self._confined(self.store_dir / self._normalize_target(target_path), self.store_dir)

    def _version_dir(self, target_path: str) -> Path:
        path = self._confined(self.versions_dir / target_path, self.versions_dir)
        if path.exists() and not path.is_dir():
            raise StorageBoundaryError(f"Version path is not a directory: {path}")
        return path

    def _version_file(self, target_path: str, filename: str) -> Path:
        if (not isinstance(filename, str) or filename in ("", ".", "..")
                or "/" in filename or "\\" in filename or "\x00" in filename):
            raise StorageBoundaryError("version_filename must name one direct target generation")
        path = self._confined(self._version_dir(target_path) / filename, self.versions_dir)
        if not path.is_file():
            raise StorageBoundaryError(f"Target version does not exist: {filename!r}")
        return path

    def _validate_lifecycle(
        self, content: str, explicit_metadata: Mapping[str, Any] | None = None,
        as_of: datetime.date | None = None,
    ) -> ValidationResult:
        try:
            metadata, _ = parse_markdown_text(content)
        except FrontmatterError as exc:
            raise PromotionGateError(f"Invalid canonical Markdown: {exc}") from exc
        if explicit_metadata is not None:
            if not isinstance(explicit_metadata, Mapping) or any(
                key not in metadata or metadata[key] != value
                for key, value in explicit_metadata.items()
            ):
                raise PromotionGateError("Explicit metadata must agree with the exact Markdown bytes")
        result = validate_metadata(metadata, as_of=as_of)
        if not result.valid or result.state not in ("CONFIRMED", "STALE", "RETIRED"):
            errors = "; ".join(issue.message for issue in result.issues if issue.severity == "error")
            raise PromotionGateError(f"Ineligible canonical lifecycle state: {errors or result.state}")
        return result

    def _audit_records(self) -> list[dict[str, Any]]:
        self._confined(self.audit_path, self.audit_dir)
        try:
            raw = self.audit_path.read_bytes()
            if raw and not raw.endswith(b"\n"):
                raise ValueError("incomplete JSONL record")
            records = [json.loads(line) for line in raw.decode("utf-8").splitlines() if line.strip()]
            for record in records:
                if (not isinstance(record, dict) or not isinstance(record.get("target"), str)
                        or record.get("action") not in ("write", "rollback", "redact", "revalidate")
                        or not isinstance(record.get("after_hash"), str)
                        or re.fullmatch(r"sha256:[0-9a-f]{64}", record["after_hash"]) is None):
                    raise ValueError("invalid audit record")
                if record["action"] == "revalidate":
                    decision_ref = record.get("decision_ref")
                    if not isinstance(decision_ref, str) or not decision_ref or decision_ref != decision_ref.strip():
                        raise ValueError("invalid revalidation decision reference")
            return records
        except (OSError, ValueError, UnicodeError) as exc:
            raise StorageDurabilityError(f"Cannot use incomplete audit evidence: {exc}") from exc

    def _guard_existing(
        self, target: str, store: Path, state: str | None,
        records: list[dict[str, Any]], as_of: datetime.date | None = None,
    ) -> tuple[bytes | None, ValidationResult | None]:
        history = self._version_dir(target)
        if not store.exists():
            if (history.exists() and any(history.iterdir())) or any(r["target"] == target for r in records):
                raise StorageDurabilityError("Canonical file missing while target history remains")
            return None, None
        if not store.is_file():
            raise StorageBoundaryError("Canonical target must be a regular file")
        raw = store.read_bytes()
        self._verify_no_change(target, compute_sha256(raw), records)
        try:
            previous = self._validate_lifecycle(raw.decode("utf-8"), as_of=as_of)
        except UnicodeError as exc:
            raise PromotionGateError("Existing canonical Markdown is not UTF-8") from exc
        if state is not None and previous.state != state:
            decision = propose_transition(previous.state, state)
            if not decision.allowed:
                raise PromotionGateError(decision.reason)
        return raw, previous

    def _verify_no_change(self, target: str, digest: str, records: list[dict[str, Any]]) -> None:
        matching = [row for row in records if row["target"] == target]
        if not matching or matching[-1]["after_hash"] != digest:
            raise StorageDurabilityError("Identical canonical bytes have no matching latest target audit")
        history = self._version_dir(target)
        found = False
        if history.exists():
            for version in history.iterdir():
                self._confined(version, history)
                if not version.is_file() or version.suffix != ".md":
                    raise StorageDurabilityError("Unexpected incomplete version inventory")
                found = compute_sha256(version.read_bytes()) == digest or found
        if not found:
            raise StorageDurabilityError("Identical canonical bytes have no matching immutable version")

    def _new_version(self, target: str, actor: str, digest: str) -> tuple[Path, str]:
        now = datetime.datetime.now(datetime.timezone.utc)
        actor_safe = re.sub(r"[^A-Za-z0-9._-]", "_", actor)
        name = f"{now.strftime('%Y%m%dT%H%M%S%fZ')}_{actor_safe}_{digest[7:15]}.md"
        version = self._confined(self._version_dir(target) / name, self.versions_dir)
        if version.exists():
            raise StorageDurabilityError(f"Version already exists: {version}")
        return version, now.strftime("%Y-%m-%dT%H:%M:%SZ")

    def _snapshot(self, path: Path) -> tuple[bytes | None, int | None]:
        self._confined(path, self.base_dir)
        if not path.exists():
            return None, None
        if not path.is_file():
            raise StorageBoundaryError(f"Expected regular storage file: {path}")
        return path.read_bytes(), path.stat().st_mode & 0o777

    @staticmethod
    def _stage(path: Path, raw: bytes, mode: int, staging: list[Path]) -> Path:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile("wb", dir=str(path.parent), delete=False) as stream:
            temp = Path(stream.name)
            staging.append(temp)
            os.fchmod(stream.fileno(), mode)
            if stream.write(raw) != len(raw):
                raise OSError("short storage write")
            stream.flush()
            os.fsync(stream.fileno())
        return temp

    def _publish(self, updates: list[tuple[Path, bytes]],
                 appends: list[tuple[Path, dict[str, Any]]]) -> None:
        """Compensate a single writer's raised exceptions; never retry a caller."""
        staging: list[Path] = []
        attempted: list[tuple[Path, bytes, bool]] = []
        before: dict[Path, tuple[bytes | None, int | None]] = {}
        recovery_errors = []
        failure = None
        try:
            for path, _ in updates + appends:
                before[path] = self._snapshot(path)
            prepared = [(path, raw, self._stage(
                path, raw, before[path][1] if before[path][1] is not None else 0o600, staging))
                        for path, raw in updates]
            for path, raw, temp in prepared:
                if self._snapshot(path) != before[path]:
                    raise OSError("storage changed before publication")
                attempted.append((path, raw, False))
                os.replace(str(temp), str(path))
            for path, entry in appends:
                if self._snapshot(path) != before[path]:
                    raise OSError("log changed before append")
                line = json.dumps(entry, ensure_ascii=False) + "\n"
                attempted.append((path, line.encode("utf-8"), True))
                with open(path, "a", encoding="utf-8") as stream:
                    if stream.write(line) != len(line):
                        raise OSError("short log append")
                    stream.flush()
                    os.fsync(stream.fileno())
        except Exception as exc:
            failure = exc
            for path, payload, append in reversed(attempted):
                try:
                    old, mode = before[path]
                    current, current_mode = self._snapshot(path)
                    if (current, current_mode) == (old, mode):
                        continue
                    expected_mode = mode if mode is not None else 0o600
                    owned = current == payload
                    if append:
                        prior = old or b""
                        owned = (current is not None and current.startswith(prior)
                                 and payload.startswith(current[len(prior):]))
                    if not owned or current_mode != expected_mode:
                        raise OSError("unexpected storage change; refusing to overwrite foreign bytes")
                    if old is None:
                        path.unlink()
                    else:
                        restore = self._stage(path, old, expected_mode, staging)
                        os.replace(str(restore), str(path))
                except Exception as recovery:
                    recovery_errors.append(f"{path.name}: {recovery}")
        finally:
            for temp in staging:
                try:
                    temp.unlink(missing_ok=True)
                except OSError as cleanup:
                    recovery_errors.append(f"staging cleanup: {cleanup}")
        if failure is not None or recovery_errors:
            suffix = f"; recovery failed: {'; '.join(recovery_errors)}" if recovery_errors else "; prior bytes restored"
            raise StorageDurabilityError(f"Storage operation failed: {failure}{suffix}") from failure

    @staticmethod
    def _content_bytes(content: str) -> bytes:
        if not isinstance(content, str):
            raise KnowledgeTrustError("content must be a string")
        raw = content.encode("utf-8")
        if len(raw) > _MAX_BYTES:
            raise StorageBoundaryError("content exceeds maximum bytes")
        return raw

    def _write_generation(
        self, store: Path, raw: bytes, entry: dict[str, Any], status: str,
    ) -> KnowledgeTrustResult:
        target = entry["target"]
        version, timestamp = self._new_version(target, entry["actor"], entry["after_hash"])
        entry.update(ts=timestamp, version=version.name)
        self._publish([(store, raw), (version, raw)], [(self.audit_path, entry)])
        return KnowledgeTrustResult(
            True, status, target, entry["before_hash"], entry["after_hash"],
            str(version), entry, True, {"state": entry["state"]},
        )

    @_serialized_write
    def commit(
        self, target_path: str, content: str, actor: str, reason: str,
        metadata: Mapping[str, Any] | None = None, approval_token: str | None = None,
        as_of: datetime.date | None = None,
    ) -> KnowledgeTrustResult:
        today = datetime.date.today()
        validation_date = as_of or today
        raw = self._content_bytes(content)
        state = self._validate_lifecycle(content, metadata, as_of=validation_date).state
        target_path = self._normalize_target(target_path)
        store = self._validate_target_path(target_path)
        records = self._audit_records()
        previous, previous_result = self._guard_existing(
            target_path, store, state, records, validation_date,
        )
        before_hash = compute_sha256(previous) if previous is not None else "none"
        after_hash = compute_sha256(raw)
        if previous is not None:
            delta = abs(len(previous.decode("utf-8").splitlines()) - len(content.splitlines()))
            if delta > _MAX_LINE_DELTA and not approval_token:
                raise StorageBoundaryError("line delta exceeds limit without approval token")
        if before_hash == after_hash:
            self._verify_no_change(target_path, after_hash, records)
            return KnowledgeTrustResult(True, "NO_CHANGE", target_path, before_hash,
                                        after_hash, None, None, False,
                                        {"message": "Content identical to existing canonical store; no-op."})
        if (previous_result is not None and state == "CONFIRMED"
                and _expired_evidence(validate_metadata(previous_result.metadata, as_of=today))):
            raise PromotionGateError("Expired evidence requires revalidation before a confirmed update")
        entry = {"actor": actor, "action": "write", "target": target_path,
                 "before_hash": before_hash, "after_hash": after_hash, "reason": reason,
                 "state": state, "approval_token": approval_token}
        return self._write_generation(store, raw, entry, "COMMITTED")

    @_serialized_write
    def revalidate(
        self, target_path: str, content: str, actor: str, reason: str, *,
        evidence: bytes, review: Mapping[str, str | int],
    ) -> KnowledgeTrustResult:
        """Save a new Evidence generation after an externally authorized review."""
        today = datetime.date.today()
        raw = self._content_bytes(content)
        candidate = self._validate_lifecycle(content, as_of=today)
        if (candidate.asset_type != "EVIDENCE" or candidate.state != "CONFIRMED"
                or candidate.freshness != "FRESH"
                or candidate.metadata.get("last_verified") != today.isoformat()):
            raise PromotionGateError("Revalidation needs fresh confirmed evidence verified today")
        if not isinstance(evidence, bytes) or not evidence or not isinstance(review, Mapping):
            raise PromotionGateError("Revalidation requires evidence bytes and a review record")
        approved = dict(review)
        review_fields = {"evidence_ref", "reviewer", "decision_ref"}
        for field_name in review_fields:
            value = approved.get(field_name)
            if not isinstance(value, str) or not value or value != value.strip():
                raise PromotionGateError(f"Invalid review field: {field_name}")
        if approved["evidence_ref"] not in candidate.metadata["lineage"]:
            raise PromotionGateError("Review evidence reference is missing from candidate lineage")

        target_path = self._normalize_target(target_path)
        store = self._validate_target_path(target_path)
        records = self._audit_records()
        previous, previous_result = self._guard_existing(target_path, store, None, records, today)
        if (previous is None or previous_result is None or previous_result.asset_type != "EVIDENCE"
                or (previous_result.state != "STALE" and not _expired_evidence(previous_result))):
            raise PromotionGateError("Revalidation requires current stale or expired evidence")

        current_index = max(index for index, record in enumerate(records)
                            if record["target"] == target_path)
        expected = {
            "target": target_path,
            "current_audit_index": current_index,
            "before_hash": compute_sha256(previous),
            "after_hash": compute_sha256(raw),
            "evidence_sha256": compute_sha256(evidence),
        }
        if (approved.keys() != expected.keys() | review_fields
                or type(approved["current_audit_index"]) is not int
                or any(approved[key] != value for key, value in expected.items())):
            raise PromotionGateError("Review does not match the current revision, candidate or evidence")
        if any(record["action"] == "revalidate" and record["decision_ref"] == approved["decision_ref"]
               for record in records):
            raise PromotionGateError("Review decision reference was already used")

        entry = {**approved, "actor": actor, "reason": reason, "state": candidate.state,
                 "action": "revalidate", "operation_date": today.isoformat()}
        return self._write_generation(store, raw, entry, "REVALIDATED")

    @_serialized_write
    def rollback(self, target_path: str, version_filename: str,
                 actor: str, reason: str) -> KnowledgeTrustResult:
        target_path = self._normalize_target(target_path)
        store = self._validate_target_path(target_path)
        version = self._version_file(target_path, version_filename)
        restored = version.read_bytes()
        today = datetime.date.today()
        try:
            restored_result = self._validate_lifecycle(restored.decode("utf-8"), as_of=today)
        except UnicodeError as exc:
            raise PromotionGateError("Version is not UTF-8 Markdown") from exc
        if _expired_evidence(restored_result):
            raise PromotionGateError("Cannot restore expired confirmed evidence")
        state = restored_result.state
        previous, previous_result = self._guard_existing(
            target_path, store, state, self._audit_records(), today,
        )
        if previous_result is not None and state == "CONFIRMED" and _expired_evidence(previous_result):
            raise PromotionGateError("Expired evidence requires revalidation before a confirmed restore")
        before_hash = compute_sha256(previous) if previous is not None else "none"
        after_hash = compute_sha256(restored)
        entry = {"ts": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
                 "actor": actor, "action": "rollback", "target": target_path,
                 "restored_version": version_filename, "version": version.name,
                 "before_hash": before_hash, "after_hash": after_hash, "reason": reason, "state": state}
        self._publish([(store, restored)], [(self.audit_path, entry)])
        return KnowledgeTrustResult(True, "ROLLED_BACK", target_path, before_hash,
                                    after_hash, str(version), entry, True,
                                    {"restored_version": version_filename})

    @_serialized_write
    def redact(self, target_path: str, version_filename: str,
               actor: str, reason: str) -> KnowledgeTrustResult:
        target_path = self._normalize_target(target_path)
        store = self._validate_target_path(target_path)
        self._version_file(target_path, version_filename)
        tombstone = ("---\nstate: RETIRED\nasset_type: PROCEDURE\ntitle: Redacted\n"
                     "created: 2026-08-23\nlineage:\n  - system\n---\n# REDACTED\n"
                     f"This knowledge item was redacted by {actor}: {reason}\n")
        state = self._validate_lifecycle(tombstone).state
        previous, _ = self._guard_existing(target_path, store, state, self._audit_records())
        before_hash = compute_sha256(previous) if previous is not None else "none"
        raw = tombstone.encode("utf-8")
        after_hash = compute_sha256(raw)
        version, timestamp = self._new_version(target_path, actor, after_hash)
        redaction = {"ts": timestamp, "actor": actor, "target": target_path,
                     "version": version_filename, "reason": reason}
        entry = {"ts": timestamp, "actor": actor, "action": "redact", "target": target_path,
                 "redacted_version": version_filename, "version": version.name,
                 "before_hash": before_hash, "after_hash": after_hash, "reason": reason, "state": state}
        self._publish([(store, raw), (version, raw)],
                      [(self.redact_path, redaction), (self.audit_path, entry)])
        return KnowledgeTrustResult(True, "REDACTED", target_path, before_hash,
                                    after_hash, None, entry, True,
                                    {"redacted_version": version_filename})

    def export_canonical_knowledge(self) -> list[dict[str, Any]]:
        self._check_storage()
        entries: list[dict[str, Any]] = []
        for root, _, files in os.walk(str(self.store_dir)):
            for fname in sorted(files):
                if fname.startswith("."):
                    continue
                path = self._confined(Path(root) / fname, self.store_dir)
                content = path.read_text(encoding="utf-8", errors="replace")
                entries.append({"target_path": path.relative_to(self.store_dir).as_posix(),
                                "content": content, "sha256": compute_sha256(content),
                                "mtime": path.stat().st_mtime})
        entries.sort(key=lambda entry: entry["target_path"])
        return entries
