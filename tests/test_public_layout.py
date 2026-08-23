from pathlib import Path
import unittest


ROOT = Path(__file__).parents[1]


class PublicLayoutTests(unittest.TestCase):
    def test_public_root_contains_only_the_declared_components_and_public_docs(self):
        self.assertTrue((ROOT / "knowledge-lifecycle-gate" / "pyproject.toml").is_file())
        self.assertTrue((ROOT / "docs" / "mothership-relationship.md").is_file())
        self.assertFalse((ROOT / "llm-routing").exists())
        self.assertFalse((ROOT / ".env").exists())
        self.assertFalse((ROOT / "tasks").exists())


if __name__ == "__main__":
    unittest.main()
