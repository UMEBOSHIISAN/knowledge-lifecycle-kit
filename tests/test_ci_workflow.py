from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"


class CiWorkflowTests(unittest.TestCase):
    def test_ci_is_test_and_boundary_scan_only(self):
        workflow = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("pull_request:", workflow)
        self.assertIn("push:", workflow)
        self.assertIn("python-version: '3.11'", workflow)
        self.assertIn("python -m pytest -q tests", workflow)
        self.assertIn("python -m unittest -v tests/test_routing.py tests/test_public_layout.py tests/test_verify_test_wheelhouse.py tests/test_public_boundary.py tests/test_ci_workflow.py", workflow)
        self.assertIn("python tools/check_public_boundary.py .", workflow)

        for forbidden in ("secrets", "publish", "release", "deploy", "curl", "wget"):
            self.assertNotIn(forbidden, workflow.lower())

