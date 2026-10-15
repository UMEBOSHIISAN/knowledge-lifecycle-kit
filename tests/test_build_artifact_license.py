import base64
import csv
import hashlib
import importlib.util
import io
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
import zipfile


ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "knowledge-lifecycle-gate"
DIST_INFO = "knowledge_lifecycle_gate-0.1.0.dist-info"


def load_backend():
    spec = importlib.util.spec_from_file_location("klg_build_backend", COMPONENT / "build_backend.py")
    backend = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(backend)
    return backend


class BuildArtifactLicenseTests(unittest.TestCase):
    def test_regular_and_editable_wheels_ship_the_full_notice_and_record_its_hash(self):
        """Dropping the notice or its RECORD binding makes the distributable incomplete."""
        notice = (COMPONENT / "LICENSE").read_bytes()
        self.assertIn(b"Copyright (c) 2026 KLG contributors", notice)
        self.assertIn(b"The above copyright notice and this permission notice", notice)
        backend = load_backend()
        for build in (backend.build_wheel, backend.build_editable):
            with self.subTest(build=build.__name__), TemporaryDirectory() as directory:
                wheel_path = Path(directory) / build(directory)
                with zipfile.ZipFile(wheel_path) as wheel:
                    license_path = f"{DIST_INFO}/LICENSE"
                    self.assertIn(license_path, wheel.namelist())
                    self.assertEqual(wheel.read(license_path), notice)
                    rows = list(csv.reader(io.StringIO(wheel.read(f"{DIST_INFO}/RECORD").decode())))
                    license_rows = [row for row in rows if row[0] == license_path]
                    digest = base64.urlsafe_b64encode(hashlib.sha256(notice).digest()).rstrip(b"=").decode()
                    self.assertEqual(license_rows, [[license_path, f"sha256={digest}", str(len(notice))]])

    def test_prepared_metadata_keeps_the_same_full_notice(self):
        """Metadata-only preparation must not discard the copyright/permission notice."""
        backend = load_backend()
        notice = (COMPONENT / "LICENSE").read_bytes()
        for prepare in (backend.prepare_metadata_for_build_wheel, backend.prepare_metadata_for_build_editable):
            with self.subTest(prepare=prepare.__name__), TemporaryDirectory() as directory:
                dist_info = Path(directory) / prepare(directory)
                self.assertTrue((dist_info / "LICENSE").is_file())
                self.assertEqual((dist_info / "LICENSE").read_bytes(), notice)


if __name__ == "__main__":
    unittest.main()
