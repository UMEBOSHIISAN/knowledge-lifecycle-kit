import importlib.util
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).parents[1]
SCANNER_PATH = ROOT / "tools" / "check_public_boundary.py"


def load_scanner():
    spec = importlib.util.spec_from_file_location("check_public_boundary", SCANNER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class PublicBoundaryTests(unittest.TestCase):
    def test_reports_private_path_and_github_token_in_stable_order(self):
        self.assertTrue(SCANNER_PATH.is_file())
        scanner = load_scanner()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            private_path = "/" + "Users/example/private"
            token = "ghp" + "_" + "a" * 36
            (root / "bad.txt").write_text(f"token={token}\npath={private_path}\n", encoding="utf-8")
            self.assertEqual(
                scanner.check_public_tree(root),
                [
                    {"line": 1, "path": "bad.txt", "rule": "github_token"},
                    {"line": 2, "path": "bad.txt", "rule": "absolute_private_path"},
                ],
            )

    def test_staging_tree_has_no_public_boundary_violations(self):
        self.assertTrue(SCANNER_PATH.is_file())
        self.assertEqual(load_scanner().check_public_tree(ROOT), [])


if __name__ == "__main__":
    unittest.main()
