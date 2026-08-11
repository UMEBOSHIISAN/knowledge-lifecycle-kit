import hashlib
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest


ROOT = Path(__file__).parents[1]
VERIFIER_PATH = ROOT / "tools" / "verify_test_wheelhouse.py"


def load_verifier():
    spec = importlib.util.spec_from_file_location("verify_test_wheelhouse", VERIFIER_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_manifest(root: Path, wheels: list[tuple[str, str]]) -> Path:
    path = root / "test-wheelhouse.json"
    path.write_text(json.dumps({"wheels": [{"filename": name, "sha256": digest} for name, digest in wheels]}))
    return path


class TestWheelhouseTests(unittest.TestCase):
    def test_returns_each_verified_wheel(self):
        self.assertTrue(VERIFIER_PATH.is_file())
        verifier = load_verifier()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            filenames = ("pytest-8.3.5-py3-none-any.whl", "pluggy-1.5.0-py3-none-any.whl")
            wheels = tuple(root / name for name in filenames)
            for wheel in wheels:
                wheel.write_bytes(wheel.name.encode("ascii"))
            manifest = write_manifest(
                root,
                [(wheel.name, hashlib.sha256(wheel.read_bytes()).hexdigest()) for wheel in wheels],
            )
            self.assertEqual(verifier.verify_test_wheelhouse(manifest, root), wheels)

    def test_rejects_missing_or_mismatched_wheel(self):
        self.assertTrue(VERIFIER_PATH.is_file())
        verifier = load_verifier()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            manifest = write_manifest(root, [("pytest-8.3.5-py3-none-any.whl", "0" * 64)])
            with self.assertRaisesRegex(ValueError, "test wheelhouse verification failed"):
                verifier.verify_test_wheelhouse(manifest, root)


if __name__ == "__main__":
    unittest.main()
