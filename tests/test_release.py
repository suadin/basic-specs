import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class ReleaseTest(unittest.TestCase):
    def test_version_json_matches_version(self):
        version = (ROOT / "VERSION").read_text().strip()
        release = json.loads((ROOT / "version.json").read_text())
        self.assertEqual(release["version"], version)
        self.assertEqual(release["url"].rsplit("/", 1)[-1], f"v{version}")

    def test_rules_pin_the_same_version(self):
        version = (ROOT / "VERSION").read_text().strip()
        rules = json.loads((ROOT / "rules.json").read_text())
        self.assertEqual(rules["standard"], version)


if __name__ == "__main__":
    unittest.main()
