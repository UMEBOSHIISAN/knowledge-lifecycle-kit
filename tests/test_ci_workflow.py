from pathlib import Path
import shlex
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
        self.assertIn("python tools/check_public_boundary.py .", workflow)

        for forbidden in ("secrets", "publish", "release", "deploy", "curl", "wget"):
            self.assertNotIn(forbidden, workflow.lower())

    def test_ci_unittest_command_collects_existing_tests(self):
        """A stale workflow target must fail before a CI run is advertised as valid."""
        commands = [
            shlex.split(line.strip().removeprefix("run: "))
            for line in WORKFLOW.read_text(encoding="utf-8").splitlines()
            if line.strip().startswith("run: python -m unittest ")
        ]
        self.assertEqual(len(commands), 1)
        arguments = commands[0][3:]
        loader = unittest.TestLoader()
        if arguments[0] == "discover":
            start = arguments[arguments.index("-s") + 1]
            suite = loader.discover(str(ROOT / start))
        else:
            targets = [
                arg.removesuffix(".py").replace("/", ".")
                for arg in arguments if not arg.startswith("-")
            ]
            suite = loader.loadTestsFromNames(targets)
        self.assertEqual(loader.errors, [])
        self.assertGreater(suite.countTestCases(), 0)
