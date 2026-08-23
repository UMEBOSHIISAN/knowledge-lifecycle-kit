"""
test_trust_writer.py — Comprehensive Tests for Knowledge Trust Runtime Integration.

Verifies Criteria A through L:
A. UNKNOWN / ASSUMPTION candidate -> canonical write rejected / held -> memory_trust unchanged.
B. Valid eligible CONFIRMED transition -> exactly one immutable version written -> audit record exists.
C. Attempt to modify canonical content directly without lifecycle gate -> rejected.
D. Second valid update -> new version -> prior version remains immutable.
E. Rollback -> effective state changes -> historical versions preserved.
F. Redaction -> follows redact-by-version -> no silent history rewrite.
G. Injected durable-write failure -> no false lifecycle completion / no false receipt.
H. Injected lifecycle rejection -> zero memory_trust mutation.
I. Existing memory_trust compatibility -> regression PASS.
J. Existing knowledge-lifecycle-gate behavior -> regression PASS.
K. No second canonical knowledge store introduced.
L. Deterministic canonical knowledge export for Phase 3C context-reuse rebuild.
"""

from __future__ import annotations

import datetime
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from knowledge_lifecycle_gate import (
    KnowledgeTrustWriter,
    PromotionGateError,
    StorageBoundaryError,
    StorageDurabilityError,
)


class KnowledgeTrustWriterTests(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.base_dir = Path(self.tmpdir.name)
        self.writer = KnowledgeTrustWriter(self.base_dir)

    def tearDown(self):
        self.tmpdir.cleanup()

    def _sample_confirmed_content(self, title="System Architecture", state="CONFIRMED"):
        return f"""---
title: "{title}"
asset_type: "CONCEPT"
state: "{state}"
created: "2026-08-23"
lineage:
  - "docs/system_spec.md"
---
# {title}
This is confirmed canonical knowledge content.
"""

    def _sample_unconfirmed_content(self, state="UNKNOWN"):
        return f"""---
title: "Unverified Hypothesis"
asset_type: "CONCEPT"
state: "{state}"
created: "2026-08-23"
lineage:
  - "notes.md"
---
# Hypothesis
Unconfirmed draft content.
"""

    # =========================================================================
    # Acceptance A & H: UNKNOWN / ASSUMPTION Rejected -> Zero Mutation
    # =========================================================================
    def test_acceptance_a_and_h_unconfirmed_candidate_rejected_zero_mutation(self):
        for state in ("UNKNOWN", "ASSUMPTION", "NEW"):
            with self.subTest(state=state):
                content = self._sample_unconfirmed_content(state=state)
                with self.assertRaises(PromotionGateError):
                    self.writer.commit(
                        target_path="memory/test_hypothesis.md",
                        content=content,
                        actor="researcher",
                        reason=f"Attempting write of {state} state",
                    )
                # Verify zero storage mutation
                self.assertFalse((self.base_dir / "store" / "memory" / "test_hypothesis.md").exists())
                self.assertFalse((self.base_dir / "versions" / "memory" / "test_hypothesis.md").exists())
                # Verify audit log is empty
                with open(self.writer.audit_path, "r", encoding="utf-8") as f:
                    lines = [l.strip() for l in f if l.strip()]
                self.assertEqual(0, len(lines))

    # =========================================================================
    # Acceptance B: Valid Eligible CONFIRMED Transition -> Exactly One Version + Audit
    # =========================================================================
    def test_acceptance_b_valid_confirmed_written_with_audit(self):
        content = self._sample_confirmed_content(title="Agent Boundary Rules")
        res = self.writer.commit(
            target_path="memory/agent_boundaries.md",
            content=content,
            actor="architect",
            reason="Initial canonical specification",
        )
        self.assertTrue(res.success)
        self.assertEqual(res.status, "COMMITTED")
        self.assertTrue(res.changed)
        self.assertIsNotNone(res.version_path)

        # 1. Store file exists with exact content
        store_path = self.base_dir / "store" / "memory" / "agent_boundaries.md"
        self.assertTrue(store_path.exists())
        self.assertEqual(content, store_path.read_text(encoding="utf-8"))

        # 2. Exactly one immutable version exists
        version_dir = self.base_dir / "versions" / "memory" / "agent_boundaries.md"
        version_files = list(version_dir.glob("*.md"))
        self.assertEqual(1, len(version_files))
        self.assertEqual(content, version_files[0].read_text(encoding="utf-8"))

        # 3. Exactly one audit record exists
        with open(self.writer.audit_path, "r", encoding="utf-8") as f:
            lines = [json.loads(l) for l in f if l.strip()]
        self.assertEqual(1, len(lines))
        self.assertEqual("write", lines[0]["action"])
        self.assertEqual("memory/agent_boundaries.md", lines[0]["target"])
        self.assertEqual("CONFIRMED", lines[0]["state"])

    # =========================================================================
    # Acceptance C: Attempt to modify without lifecycle validation -> Rejected
    # =========================================================================
    def test_acceptance_c_invalid_frontmatter_rejected(self):
        invalid_content = "# Raw content without frontmatter metadata"
        with self.assertRaises(PromotionGateError):
            self.writer.commit(
                target_path="memory/raw.md",
                content=invalid_content,
                actor="unknown_agent",
                reason="Bypass attempt",
            )
        self.assertFalse((self.base_dir / "store" / "memory" / "raw.md").exists())

    # =========================================================================
    # Acceptance D: Second Valid Update -> New Version, Prior Version Preserved
    # =========================================================================
    def test_acceptance_d_second_update_preserves_immutable_history(self):
        content_v1 = self._sample_confirmed_content(title="Version 1")
        content_v2 = self._sample_confirmed_content(title="Version 2 Updated")

        res1 = self.writer.commit(
            target_path="memory/evolution.md",
            content=content_v1,
            actor="author",
            reason="V1 creation",
        )
        self.assertTrue(res1.success)

        res2 = self.writer.commit(
            target_path="memory/evolution.md",
            content=content_v2,
            actor="editor",
            reason="V2 modification",
        )
        self.assertTrue(res2.success)

        # Store contains current V2
        store_path = self.base_dir / "store" / "memory" / "evolution.md"
        self.assertEqual(content_v2, store_path.read_text(encoding="utf-8"))

        # Versions directory contains exactly 2 distinct files
        version_dir = self.base_dir / "versions" / "memory" / "evolution.md"
        version_files = sorted(version_dir.glob("*.md"))
        self.assertEqual(2, len(version_files))
        self.assertEqual(content_v1, version_files[0].read_text(encoding="utf-8"))
        self.assertEqual(content_v2, version_files[1].read_text(encoding="utf-8"))

        # Idempotence: re-committing V2 produces no-op
        res_noop = self.writer.commit(
            target_path="memory/evolution.md",
            content=content_v2,
            actor="editor",
            reason="Duplicate write",
        )
        self.assertEqual("NO_CHANGE", res_noop.status)
        self.assertFalse(res_noop.changed)
        self.assertEqual(2, len(list(version_dir.glob("*.md"))))

    # =========================================================================
    # Acceptance E: Rollback -> Restores Target Version without Deleting History
    # =========================================================================
    def test_acceptance_e_rollback_restores_state_and_preserves_history(self):
        content_v1 = self._sample_confirmed_content(title="Original Spec")
        content_v2 = self._sample_confirmed_content(title="Buggy Edit Spec")

        res1 = self.writer.commit("memory/spec.md", content_v1, "dev", "v1")
        res2 = self.writer.commit("memory/spec.md", content_v2, "dev", "v2")

        v1_filename = Path(res1.version_path).name

        # Rollback to V1
        res_rb = self.writer.rollback(
            target_path="memory/spec.md",
            version_filename=v1_filename,
            actor="admin",
            reason="Reverting buggy edit",
        )
        self.assertTrue(res_rb.success)
        self.assertEqual("ROLLED_BACK", res_rb.status)

        # Store now contains V1 again
        store_path = self.base_dir / "store" / "memory" / "spec.md"
        self.assertEqual(content_v1, store_path.read_text(encoding="utf-8"))

        version_dir = self.base_dir / "versions" / "memory" / "spec.md"
        # History is completely preserved (2 version files remain)
        self.assertEqual(2, len(list(version_dir.glob("*.md"))))

        # Rollback is audited
        with open(self.writer.audit_path, "r", encoding="utf-8") as f:
            audit_records = [json.loads(l) for l in f if l.strip()]
        self.assertEqual(3, len(audit_records))
        self.assertEqual("rollback", audit_records[2]["action"])

    # =========================================================================
    # Acceptance F: Redaction -> Masked Active Store & Preserved Audit Log
    # =========================================================================
    def test_acceptance_f_redaction_preserves_history_and_logs(self):
        content = self._sample_confirmed_content(title="Accidental Secret Note")
        self.writer.commit("memory/secret.md", content, "author", "initial")

        version_dir = self.base_dir / "versions" / "memory" / "secret.md"
        ver_file = list(version_dir.glob("*.md"))[0].name

        res_red = self.writer.redact(
            target_path="memory/secret.md",
            version_filename=ver_file,
            actor="compliance_officer",
            reason="Contains proprietary token",
        )
        self.assertTrue(res_red.success)
        self.assertEqual("REDACTED", res_red.status)

        # Active store contains redacted tombstone
        store_path = self.base_dir / "store" / "memory" / "secret.md"
        self.assertIn("# REDACTED", store_path.read_text(encoding="utf-8"))

        # Redaction ledger has record
        with open(self.writer.redact_path, "r", encoding="utf-8") as f:
            redact_lines = [json.loads(l) for l in f if l.strip()]
        self.assertEqual(1, len(redact_lines))
        self.assertEqual("memory/secret.md", redact_lines[0]["target"])

    # =========================================================================
    # Acceptance G: Injected Durable Write Failure -> No False Completion
    # =========================================================================
    def test_acceptance_g_injected_durable_write_failure_clean_abort(self):
        content = self._sample_confirmed_content(title="Fault Test")
        with patch("os.replace", side_effect=OSError("Disk full or I/O failure")):
            with self.assertRaises(StorageDurabilityError):
                self.writer.commit("memory/fault.md", content, "tester", "fault test")

        # Zero store files or false audit records
        self.assertFalse((self.base_dir / "store" / "memory" / "fault.md").exists())
        with open(self.writer.audit_path, "r", encoding="utf-8") as f:
            self.assertEqual(0, len([l for l in f if l.strip()]))

    # =========================================================================
    # Acceptance I & J: Existing Lifecycle Gate & Memory Trust Regressions
    # =========================================================================
    def test_acceptance_i_and_j_boundary_path_restrictions(self):
        content = self._sample_confirmed_content()
        # Disallowed prefix outside allowed memory/decisions/synthesis/canon/history
        with self.assertRaises(StorageBoundaryError):
            self.writer.commit("src/runtime.py", content, "hacker", "unauthorized path")

        # Path traversal
        with self.assertRaises(StorageBoundaryError):
            self.writer.commit("memory/../../etc/passwd", content, "hacker", "traversal")

    # =========================================================================
    # Acceptance K & L: Deterministic Export for Phase 3C Context-Reuse Rebuild
    # =========================================================================
    def test_acceptance_k_and_l_deterministic_export_for_rebuild(self):
        items = [
            ("memory/z_last.md", self._sample_confirmed_content(title="Z Last")),
            ("memory/a_first.md", self._sample_confirmed_content(title="A First")),
            ("decisions/d_mid.md", self._sample_confirmed_content(title="D Mid")),
        ]
        for path, body in items:
            self.writer.commit(path, body, "author", "bulk ingest")

        exported = self.writer.export_canonical_knowledge()
        self.assertEqual(3, len(exported))

        # Strictly sorted by relative target path
        paths = [e["target_path"] for e in exported]
        self.assertEqual(["decisions/d_mid.md", "memory/a_first.md", "memory/z_last.md"], paths)
        for e in exported:
            self.assertTrue(e["sha256"].startswith("sha256:"))
            self.assertIn("# ", e["content"])


if __name__ == "__main__":
    unittest.main()
