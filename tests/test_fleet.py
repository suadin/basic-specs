import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from checks.fleet import from_registry, from_workspace  # noqa: E402


class FleetTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def app(self, name: str, standard: str) -> None:
        app = self.root / "repos" / name
        app.mkdir(parents=True)
        (app / "basics.json").write_text(
            json.dumps({"standard": standard, "appVersion": "1.0.0", "deviations": [{}]}),
            encoding="utf-8",
        )

    def test_the_workspace_lists_every_app_with_a_manifest(self):
        self.app("current", "1.2.1")
        (self.root / "repos" / "ohne").mkdir()
        rows, failed = from_workspace(self.root, "1.2.1")
        self.assertEqual(len(rows), 1)
        self.assertIn("1.2.1", rows[0])
        self.assertFalse(failed)

    def test_a_major_lag_is_a_failure(self):
        self.app("alt", "1.1.9")
        rows, failed = from_workspace(self.root, "2.0.0")
        self.assertTrue(failed)
        self.assertIn("MAJOR DRIFT", rows[0])

    def test_the_registry_reports_a_red_run(self):
        path = self.root / "apps.json"
        path.write_text(
            json.dumps(
                {
                    "apps": [
                        {
                            "repo": "suadin/app",
                            "version": "1.2.1",
                            "latestRun": {"conclusion": "failure"},
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        rows, failed = from_registry(path, "1.2.1")
        self.assertTrue(failed)
        self.assertIn("failure", rows[0])


if __name__ == "__main__":
    unittest.main()
