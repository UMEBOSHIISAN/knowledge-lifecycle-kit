"""Independent safe-expectation regressions for the reported W1--W6.

Synthetic TemporaryDirectory stores only. Original safe expectations are kept
from the independent W1--W6 reproduction. Run with the normal component suite.
"""
from __future__ import annotations

import builtins
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch


from knowledge_lifecycle_gate import (  # noqa: E402
    KnowledgeTrustWriter, PromotionGateError, StorageBoundaryError,
    StorageDurabilityError,
)
from knowledge_lifecycle_gate.validator import validate_file  # noqa: E402
from knowledge_lifecycle_gate.transitions import propose_transition  # noqa: E402
import knowledge_lifecycle_gate.trust_writer as writer_module  # noqa: E402

OBSERVATIONS = {}


def note(title="Original", state="CONFIRMED"):
    return (
        "---\n"
        f'title: "{title}"\n'
        'asset_type: "CONCEPT"\n'
        f'state: "{state}"\n'
        'created: "2026-08-23"\n'
        "lineage:\n"
        '  - "docs/synthetic-source.md"\n'
        "---\n"
        f"# {title}\nSynthetic evidence only.\n"
    )


def inventory(root):
    return {
        str(p.relative_to(root)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in root.rglob("*") if p.is_file() and not p.is_symlink()
    }


class WriterCounterexamples(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.writer = KnowledgeTrustWriter(self.root)
        self.target = "memory/item.md"
        self.actual = {}

    def tearDown(self):
        OBSERVATIONS[self.id().split(".")[-1]] = self.actual
        self.tmp.cleanup()

    def audit(self):
        return [json.loads(line) for line in self.writer.audit_path.read_text().splitlines() if line]

    def test_00_normal_initial_import_update_and_no_change(self):
        first = self.writer.commit(self.target, note(), "tester", "initial import")
        second = self.writer.commit(self.target, note("Updated"), "tester", "same-state edit")
        duplicate = self.writer.commit(self.target, note("Updated"), "tester", "duplicate")
        self.actual = {"first": first.status, "second": second.status, "duplicate": duplicate.status,
                       "versions": len(list((self.writer.versions_dir / self.target).glob("*.md"))),
                       "audit": len(self.audit())}
        self.assertEqual("COMMITTED", first.status)
        self.assertEqual("COMMITTED", second.status)
        self.assertEqual("NO_CHANGE", duplicate.status)
        self.assertEqual(note("Updated"), (self.writer.store_dir / self.target).read_text())
        self.assertEqual(2, self.actual["versions"])
        self.assertEqual(2, self.actual["audit"])

    def test_w1_explicit_metadata_cannot_promote_different_saved_bytes(self):
        before = inventory(self.root)
        error = None
        result = None
        try:
            result = self.writer.commit(self.target, note(state="ASSUMPTION"), "tester", "mismatch",
                                        metadata={"state": "CONFIRMED"})
        except PromotionGateError as exc:
            error = type(exc).__name__
        saved = self.writer.store_dir / self.target
        self.actual = {"error": error, "returned": result.status if result else None,
                       "saved_assumption": saved.exists() and 'state: "ASSUMPTION"' in saved.read_text(),
                       "audit_states": [r.get("state") for r in self.audit()]}
        self.assertIsNotNone(error, "Writer must reject metadata/serialized-state disagreement")
        self.assertEqual(before, inventory(self.root))

    def test_w2_existing_retired_state_cannot_return_to_confirmed(self):
        self.writer.commit(self.target, note(state="RETIRED"), "tester", "import retired item")
        before = inventory(self.root)
        error = None
        result = None
        try:
            result = self.writer.commit(self.target, note("Reactivated"), "tester", "forbidden transition")
        except PromotionGateError as exc:
            error = type(exc).__name__
        self.actual = {"proposal_allowed": propose_transition("RETIRED", "CONFIRMED").allowed,
                       "writer_error": error, "writer_returned": result.status if result else None}
        self.assertFalse(self.actual["proposal_allowed"])
        self.assertIsNotNone(error, "Existing canonical state must use the existing transition policy")
        self.assertEqual(before, inventory(self.root))

    def _rollback_boundary(self, absolute):
        self.writer.commit(self.target, note(), "tester", "initial")
        if absolute:
            external = self.root / "synthetic-unrelated.md"
            external.write_text(note("Foreign absolute input"))
            version_name = str(external)
        else:
            foreign = self.writer.commit("memory/other.md", note("Other target version"), "tester", "other")
            version_name = "../other.md/" + Path(foreign.version_path).name
        before = inventory(self.root)
        error = None
        result = None
        try:
            result = self.writer.rollback(self.target, version_name, "tester", "outside target history")
        except StorageBoundaryError as exc:
            error = type(exc).__name__
        self.actual = {"absolute": absolute, "error": error, "returned": result.status if result else None,
                       "canonical_changed": inventory(self.root) != before}
        self.assertIsNotNone(error, "Rollback must accept only a direct version of this target")
        self.assertEqual(before, inventory(self.root))

    def test_w3_absolute_rollback_source_is_rejected(self):
        self._rollback_boundary(True)

    def test_w3_other_target_generation_is_rejected(self):
        self._rollback_boundary(False)

    def test_w4_prefix_sibling_symlink_cannot_escape_store(self):
        outside = self.root / "store-shadow"
        outside.mkdir()
        (self.writer.store_dir / "memory").mkdir()
        (self.writer.store_dir / "memory" / "linked").symlink_to(outside, target_is_directory=True)
        error = None
        result = None
        try:
            result = self.writer.commit("memory/linked/escape.md", note(), "tester", "symlink boundary")
        except StorageBoundaryError as exc:
            error = type(exc).__name__
        self.actual = {"error": error, "returned": result.status if result else None,
                       "outside_file_created": (outside / "escape.md").exists()}
        self.assertIsNotNone(error, "A prefix-sharing sibling is outside the store")
        self.assertFalse((outside / "escape.md").exists())

    def fault_boundary(self, boundary, existing):
        if existing:
            self.writer.commit(self.target, note(), "tester", "preimage")
        before = inventory(self.root)
        original_replace = os.replace
        original_open = builtins.open
        hits = []

        def replace(src, dst):
            destination = Path(dst)
            is_target = destination == self.writer.store_dir / self.target
            is_version = self.writer.versions_dir in destination.parents
            if (boundary == "store" and is_target) or (boundary == "version" and is_version):
                hits.append(boundary)
                raise OSError("synthetic single-boundary write failure")
            return original_replace(src, dst)

        def opened(file, mode="r", *args, **kwargs):
            if boundary == "audit" and Path(file) == self.writer.audit_path and mode == "a":
                hits.append("audit")
                raise OSError("synthetic audit-open failure after file publications")
            return original_open(file, mode, *args, **kwargs)

        error = None
        with patch.object(writer_module.os, "replace", side_effect=replace), \
                patch("builtins.open", side_effect=opened):
            try:
                self.writer.commit(self.target, note("After failure"), "tester", "fault injection")
            except StorageDurabilityError as exc:
                error = type(exc).__name__

        after_failure = inventory(self.root)
        # Explicit caller invocation under the requested regression, not an autonomous retry.
        second = self.writer.commit(self.target, note("After failure"), "tester", "caller after error")
        records = self.audit()
        self.actual = {"boundary": boundary, "existing": existing, "injected_hits": hits,
                       "error": error, "preimage_unchanged_after_error": after_failure == before,
                       "caller_after_error_status": second.status, "audit_records_after_caller": len(records),
                       "versions_after_caller": len(list((self.writer.versions_dir / self.target).glob("*.md"))),
                       "audit_after_hash_matches_canonical": bool(records) and records[-1]["after_hash"] ==
                           "sha256:" + hashlib.sha256((self.writer.store_dir / self.target).read_bytes()).hexdigest()}
        self.assertEqual([boundary], hits, "Failure must actually reach the named boundary")
        self.assertIsNotNone(error)
        self.assertEqual(before, after_failure, "Raised write failure must preserve the complete preimage")
        self.assertEqual("COMMITTED", second.status, "A failed operation cannot become an unbacked NO_CHANGE")
        self.assertEqual(2 if existing else 1, len(records))
        self.assertEqual(2 if existing else 1, self.actual["versions_after_caller"])
        self.assertTrue(self.actual["audit_after_hash_matches_canonical"])

    def test_w5_initial_store_failure(self):
        self.fault_boundary("store", False)

    def test_w5_initial_version_failure(self):
        self.fault_boundary("version", False)

    def test_w5_initial_audit_failure(self):
        self.fault_boundary("audit", False)

    def test_w5_update_store_failure(self):
        self.fault_boundary("store", True)

    def test_w5_update_version_failure(self):
        self.fault_boundary("version", True)

    def test_w5_update_audit_failure(self):
        self.fault_boundary("audit", True)

    def test_w6_redact_output_is_parseable_valid_retired_markdown(self):
        initial = self.writer.commit(self.target, note(), "tester", "initial")
        version = Path(initial.version_path)
        historical_bytes = version.read_bytes()
        result = self.writer.redact(self.target, version.name, "tester", "synthetic redaction")
        validation = validate_file(self.writer.store_dir / self.target)
        self.actual = {"returned": result.status, "valid": validation.valid, "state": validation.state,
                       "issues": [i.code + ":" + i.message for i in validation.issues]}
        self.assertEqual(historical_bytes, version.read_bytes())
        self.assertTrue(validation.valid, "Writer-generated Markdown must be accepted by its own parser")
        self.assertEqual("RETIRED", validation.state)


class WriterBoundaryRegressions(unittest.TestCase):
    setUp = WriterCounterexamples.setUp
    tearDown = WriterCounterexamples.tearDown
    audit = WriterCounterexamples.audit

    def test_reopening_writer_preserves_existing_log_timestamps(self):
        self.writer.commit(self.target, note(), "tester", "initial")
        old_ns = 1_700_000_000_000_000_000
        for path in (self.writer.audit_path, self.writer.redact_path):
            os.utime(path, ns=(old_ns, old_ns))
        before = inventory(self.root)
        KnowledgeTrustWriter(self.root)
        self.assertEqual(before, inventory(self.root))
        for path in (self.writer.audit_path, self.writer.redact_path):
            self.assertEqual(old_ns, path.stat().st_mtime_ns)

    def test_explicit_metadata_cannot_replace_malformed_markdown(self):
        before = inventory(self.root)
        with self.assertRaises(PromotionGateError):
            self.writer.commit(self.target, "# No metadata", "tester", "bad input", metadata={
                "state": "CONFIRMED", "asset_type": "CONCEPT", "lineage": ["source.md"]})
        self.assertEqual(before, inventory(self.root))

    def test_explicit_lineage_mismatch_is_rejected(self):
        with self.assertRaises(PromotionGateError):
            self.writer.commit(self.target, note(), "tester", "mismatch",
                               metadata={"lineage": ["different.md"]})
        self.assertFalse((self.writer.store_dir / self.target).exists())

    def test_equal_explicit_metadata_and_legal_retirement_remain_usable(self):
        first = self.writer.commit(self.target, note(), "tester", "import",
                                   metadata={"state": "CONFIRMED"})
        second = self.writer.commit(self.target, note(state="RETIRED"), "tester", "retire")
        self.assertEqual("COMMITTED", first.status)
        self.assertEqual("COMMITTED", second.status)
        self.assertTrue(validate_file(self.writer.store_dir / self.target).valid)

    def test_deleted_canonical_with_history_is_not_a_first_import(self):
        self.writer.commit(self.target, note(state="RETIRED"), "tester", "initial")
        (self.writer.store_dir / self.target).unlink()
        before = inventory(self.root)
        with self.assertRaises(StorageDurabilityError):
            self.writer.commit(self.target, note(), "tester", "reimport")
        self.assertEqual(before, inventory(self.root))

    def test_rollback_cannot_bypass_retired_transition(self):
        first = self.writer.commit(self.target, note(), "tester", "initial")
        self.writer.commit(self.target, note(state="RETIRED"), "tester", "retire")
        before = inventory(self.root)
        with self.assertRaises(PromotionGateError):
            self.writer.rollback(self.target, Path(first.version_path).name, "tester", "reactivate")
        self.assertEqual(before, inventory(self.root))

    def test_symlinked_storage_root_is_rejected_by_constructor(self):
        outside = self.root / "outside"
        outside.mkdir()
        self.writer.store_dir.rmdir()
        self.writer.store_dir.symlink_to(outside, target_is_directory=True)
        with self.assertRaises(StorageBoundaryError):
            KnowledgeTrustWriter(self.root)
        self.assertEqual([], list(outside.iterdir()))

    def test_symlinked_version_directory_is_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.writer.versions_dir / "memory").mkdir()
        (self.writer.versions_dir / self.target).symlink_to(outside, target_is_directory=True)
        with self.assertRaises(StorageBoundaryError):
            self.writer.commit(self.target, note(), "tester", "history escape")
        self.assertEqual([], list(outside.iterdir()))
        self.assertFalse((self.writer.store_dir / self.target).exists())

    def test_symlinked_audit_is_rejected_before_publication(self):
        outside = self.root / "outside.jsonl"
        outside.write_text("")
        self.writer.audit_path.unlink()
        self.writer.audit_path.symlink_to(outside)
        with self.assertRaises(StorageBoundaryError):
            self.writer.commit(self.target, note(), "tester", "audit escape")
        self.assertEqual("", outside.read_text())
        self.assertFalse((self.writer.store_dir / self.target).exists())

    def test_symlinked_rollback_version_is_rejected(self):
        first = self.writer.commit(self.target, note(), "tester", "initial")
        outside = self.root / "unrelated.md"
        outside.write_text(note("Foreign"))
        (Path(first.version_path).parent / "linked.md").symlink_to(outside)
        with self.assertRaises(StorageBoundaryError):
            self.writer.rollback(self.target, "linked.md", "tester", "link")
        self.assertEqual(note(), (self.writer.store_dir / self.target).read_text())

    def test_redact_requires_a_real_target_version(self):
        self.writer.commit(self.target, note(), "tester", "initial")
        before = inventory(self.root)
        with self.assertRaises(StorageBoundaryError):
            self.writer.redact(self.target, "absent.md", "tester", "invalid generation")
        self.assertEqual(before, inventory(self.root))

    def test_normalized_target_has_one_consistent_history_location(self):
        result = self.writer.commit("memory\\normalized.md", note(), "tester", "normalized")
        self.assertEqual(self.writer.versions_dir / "memory" / "normalized.md",
                         Path(result.version_path).parent)
        self.assertEqual("memory/normalized.md", self.audit()[0]["target"])

    def test_no_change_rejects_missing_version(self):
        first = self.writer.commit(self.target, note(), "tester", "initial")
        Path(first.version_path).unlink()
        before = inventory(self.root)
        with self.assertRaises(StorageDurabilityError):
            self.writer.commit(self.target, note(), "tester", "duplicate")
        self.assertEqual(before, inventory(self.root))

    def test_no_change_rejects_missing_target_audit(self):
        self.writer.commit(self.target, note(), "tester", "initial")
        self.writer.audit_path.write_text("")
        before = inventory(self.root)
        with self.assertRaises(StorageDurabilityError):
            self.writer.commit(self.target, note(), "tester", "duplicate")
        self.assertEqual(before, inventory(self.root))

    def test_no_change_rejects_malformed_audit(self):
        self.writer.commit(self.target, note(), "tester", "initial")
        with self.writer.audit_path.open("a") as stream:
            stream.write('{"partial":')
        before = inventory(self.root)
        with self.assertRaises(StorageDurabilityError):
            self.writer.commit(self.target, note(), "tester", "duplicate")
        self.assertEqual(before, inventory(self.root))

    def test_no_change_rejects_mismatched_audit_hash(self):
        self.writer.commit(self.target, note(), "tester", "initial")
        rows = self.audit()
        rows[-1]["after_hash"] = "sha256:" + "0" * 64
        self.writer.audit_path.write_text(json.dumps(rows[0]) + "\n")
        before = inventory(self.root)
        with self.assertRaises(StorageDurabilityError):
            self.writer.commit(self.target, note(), "tester", "duplicate")
        self.assertEqual(before, inventory(self.root))

    def test_tombstone_validation_rejection_precedes_every_write(self):
        first = self.writer.commit(self.target, note(), "tester", "initial")
        before = inventory(self.root)
        real_validate = writer_module.validate_metadata

        def rejected(metadata, **kwargs):
            return real_validate({**metadata, "asset_type": "INVALID"}, **kwargs)

        with patch.object(writer_module, "validate_metadata", side_effect=rejected):
            with self.assertRaises(PromotionGateError):
                self.writer.redact(self.target, Path(first.version_path).name, "tester", "rejected")
        self.assertEqual(before, inventory(self.root))

    def test_redaction_keeps_all_original_historical_bytes(self):
        first = self.writer.commit(self.target, note(), "tester", "initial")
        self.writer.commit(self.target, note("Updated"), "tester", "second")
        history = {p: p.read_bytes() for p in Path(first.version_path).parent.glob("*.md")}
        self.writer.redact(self.target, Path(first.version_path).name, "tester", "redact")
        for path, raw in history.items():
            self.assertEqual(raw, path.read_bytes())
        self.assertTrue(validate_file(self.writer.store_dir / self.target).valid)

    def test_no_change_uses_latest_matching_target_not_last_global_row(self):
        self.writer.commit(self.target, note(), "tester", "initial")
        self.writer.commit("memory/other.md", note("Other"), "tester", "other")
        self.assertEqual("NO_CHANGE", self.writer.commit(self.target, note(), "tester", "same").status)

    def test_staging_write_flush_and_fsync_failures_preserve_preimage(self):
        self.writer.commit(self.target, note(), "tester", "initial")
        target = self.writer.store_dir / self.target
        target.chmod(0o640)
        for fault in ("write", "flush", "fsync"):
            with self.subTest(fault=fault):
                before = inventory(self.root)
                original = tempfile.NamedTemporaryFile
                original_fsync = os.fsync
                hit = []

                class FaultFile:
                    def __init__(self, inner): self.inner = inner
                    def __enter__(self): self.inner.__enter__(); return self
                    def __exit__(self, *args): return self.inner.__exit__(*args)
                    def __getattr__(self, key): return getattr(self.inner, key)
                    def write(self, data):
                        if fault == "write" and not hit:
                            hit.append(fault)
                            self.inner.write(data[:5])
                            raise OSError("synthetic stage write")
                        return self.inner.write(data)
                    def flush(self):
                        if fault == "flush" and not hit:
                            hit.append(fault)
                            raise OSError("synthetic stage flush")
                        return self.inner.flush()

                def fsync(fd):
                    if fault == "fsync" and not hit:
                        hit.append(fault)
                        raise OSError("synthetic stage fsync")
                    return original_fsync(fd)

                with patch.object(writer_module.tempfile, "NamedTemporaryFile",
                                  side_effect=lambda *a, **k: FaultFile(original(*a, **k))), \
                        patch.object(writer_module.os, "fsync", side_effect=fsync):
                    with self.assertRaises(StorageDurabilityError):
                        self.writer.commit(self.target, note("Updated"), "tester", "stage failure")
                self.assertEqual([fault], hit)
                self.assertEqual(before, inventory(self.root))
                self.assertEqual(0o640, target.stat().st_mode & 0o777)

    def test_partial_audit_write_and_flush_preserve_bytes_and_modes(self):
        self.writer.commit(self.target, note(), "tester", "initial")
        target = self.writer.store_dir / self.target
        target.chmod(0o640)
        self.writer.audit_path.chmod(0o600)
        original_open = builtins.open
        for fault in ("write", "flush"):
            with self.subTest(fault=fault):
                before = inventory(self.root)
                hit = []

                class FaultLog:
                    def __init__(self, inner): self.inner = inner
                    def __enter__(self): self.inner.__enter__(); return self
                    def __exit__(self, *a): return self.inner.__exit__(*a)
                    def __getattr__(self, key): return getattr(self.inner, key)
                    def write(self, data):
                        if fault == "write":
                            hit.append(fault)
                            self.inner.write(data[:11]); self.inner.flush()
                            raise OSError("synthetic partial append")
                        return self.inner.write(data)
                    def flush(self):
                        self.inner.flush()
                        hit.append(fault)
                        raise OSError("synthetic audit flush")

                def opened(file, mode="r", *a, **k):
                    stream = original_open(file, mode, *a, **k)
                    return FaultLog(stream) if Path(file) == self.writer.audit_path and mode == "a" else stream

                with patch("builtins.open", side_effect=opened):
                    with self.assertRaises(StorageDurabilityError):
                        self.writer.commit(self.target, note("Updated"), "tester", "audit failure")
                self.assertEqual([fault], hit)
                self.assertEqual(before, inventory(self.root))
                self.assertEqual(0o640, target.stat().st_mode & 0o777)
                self.assertEqual(0o600, self.writer.audit_path.stat().st_mode & 0o777)

    def test_audit_fsync_failure_is_not_ignored(self):
        self.writer.commit(self.target, note(), "tester", "initial")
        before = inventory(self.root)
        original_fsync = os.fsync
        inode = self.writer.audit_path.stat().st_ino
        hit = []

        def fsync(fd):
            if os.fstat(fd).st_ino == inode and not hit:
                hit.append(True)
                raise OSError("synthetic audit fsync")
            return original_fsync(fd)

        error = None
        with patch.object(writer_module.os, "fsync", side_effect=fsync):
            try:
                self.writer.commit(self.target, note("Updated"), "tester", "audit fsync")
            except StorageDurabilityError as exc:
                error = exc
        self.assertEqual([True], hit)
        self.assertIsNotNone(error)
        self.assertEqual(before, inventory(self.root))

    def test_redaction_ledger_fsync_failure_restores_all_files(self):
        first = self.writer.commit(self.target, note(), "tester", "initial")
        before = inventory(self.root)
        original_fsync = os.fsync
        inode = self.writer.redact_path.stat().st_ino
        hit = []

        def fsync(fd):
            if os.fstat(fd).st_ino == inode and not hit:
                hit.append(True)
                raise OSError("synthetic redaction ledger fsync")
            return original_fsync(fd)

        error = None
        with patch.object(writer_module.os, "fsync", side_effect=fsync):
            try:
                self.writer.redact(self.target, Path(first.version_path).name, "tester", "ledger fault")
            except StorageDurabilityError as exc:
                error = exc
        self.assertEqual([True], hit)
        self.assertIsNotNone(error)
        self.assertEqual(before, inventory(self.root))

    def test_compensation_preserves_unexpected_foreign_log_bytes(self):
        self.writer.commit(self.target, note(), "tester", "initial")
        before = self.writer.audit_path.read_bytes()
        original_open = builtins.open
        foreign = '{"foreign": true}\n'

        def opened(file, mode="r", *args, **kwargs):
            if Path(file) == self.writer.audit_path and mode == "a":
                with original_open(file, mode, *args, **kwargs) as stream:
                    stream.write(foreign); stream.flush()
                raise OSError("synthetic foreign append before failed own append")
            return original_open(file, mode, *args, **kwargs)

        with patch("builtins.open", side_effect=opened):
            with self.assertRaises(StorageDurabilityError):
                self.writer.commit(self.target, note("Updated"), "tester", "foreign change")
        self.assertEqual(before + foreign.encode(), self.writer.audit_path.read_bytes())
        self.assertEqual(note(), (self.writer.store_dir / self.target).read_text())

    def test_failed_compensation_cannot_be_hidden_by_no_change(self):
        self.writer.commit(self.target, note(), "tester", "initial")
        original_replace = os.replace
        published = []

        def replace(src, dst):
            if Path(dst) == self.writer.store_dir / self.target:
                if published:
                    raise OSError("synthetic restoration failure")
                published.append(True)
            if self.writer.versions_dir in Path(dst).parents:
                raise OSError("synthetic version failure")
            return original_replace(src, dst)

        with patch.object(writer_module.os, "replace", side_effect=replace):
            with self.assertRaises(StorageDurabilityError):
                self.writer.commit(self.target, note("Updated"), "tester", "double fault")
        with self.assertRaises(StorageDurabilityError):
            self.writer.commit(self.target, note("Updated"), "tester", "caller after failed recovery")

    def test_unbacked_canonical_blocks_every_further_writer_operation(self):
        first = self.writer.commit(self.target, note(), "tester", "initial")
        # This is also the state left by a canonical restore failure: bytes
        # differ from the last complete version and audit receipt.
        (self.writer.store_dir / self.target).write_text(note("Orphaned update"))
        before = inventory(self.root)
        calls = (
            lambda: self.writer.commit(self.target, note("Third version"), "tester", "unbacked edit"),
            lambda: self.writer.rollback(self.target, Path(first.version_path).name, "tester", "unbacked restore"),
            lambda: self.writer.redact(self.target, Path(first.version_path).name, "tester", "unbacked redact"),
        )
        for operation in calls:
            with self.assertRaises(StorageDurabilityError):
                operation()
            self.assertEqual(before, inventory(self.root))

    def test_rollback_and_redact_audit_failure_restore_preimage(self):
        first = self.writer.commit(self.target, note(), "tester", "initial")
        self.writer.commit(self.target, note("Updated"), "tester", "second")
        original_open = builtins.open

        def opened(file, mode="r", *a, **k):
            if Path(file) == self.writer.audit_path and mode == "a":
                raise OSError("synthetic audit open")
            return original_open(file, mode, *a, **k)

        for operation in (self.writer.rollback, self.writer.redact):
            with self.subTest(operation=operation.__name__):
                before = inventory(self.root)
                error = None
                with patch("builtins.open", side_effect=opened):
                    try:
                        operation(self.target, Path(first.version_path).name, "tester", "fault")
                    except Exception as exc:
                        error = exc
                self.assertIsInstance(error, StorageDurabilityError)
                self.assertEqual(before, inventory(self.root))


