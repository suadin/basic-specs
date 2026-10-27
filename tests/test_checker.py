import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class CheckerTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = Path(self.temp.name)
        basics = self.app / "basics"
        (basics / "specs").mkdir(parents=True)
        (basics / "profiles").mkdir()
        shutil.copy2(ROOT / "VERSION", basics / "VERSION")
        shutil.copy2(ROOT / "README.md", basics / "README.md")
        shutil.copy2(ROOT / "rules.json", basics / "rules.json")
        shutil.copy2(ROOT / "specs" / "BASIC-SPECS.md", basics / "specs" / "BASIC-SPECS.md")
        for path in (ROOT / "profiles").glob("*.md"):
            shutil.copy2(path, basics / "profiles" / path.name)
        shutil.copy2(ROOT / "checks" / "basics.py", basics / "check.py")

        (self.app / "README.md").write_text("# Demo\n", encoding="utf-8")
        (self.app / "RELEASE-NOTES.md").write_text("# Releases\n", encoding="utf-8")
        (self.app / "docs").mkdir()
        (self.app / "docs" / "APP-SPECS.md").write_text("# Demo app\n", encoding="utf-8")
        (self.app / "test").mkdir()
        (self.app / "test" / "demo.test.js").write_text(
            "test('[BASIC-FOOTER-01] footer items', () => {});\n", encoding="utf-8"
        )
        (self.app / "e2e").mkdir()
        (self.app / "e2e" / "demo.spec.js").write_text(
            "test('[BASIC-FOOTER-01] footer items', () => {});\n", encoding="utf-8"
        )

        rules = json.loads((ROOT / "rules.json").read_text())["rules"]
        deviations = [
            {
                "rule": rule["id"],
                "reason": "checker fixture",
                "review": "2099-01-01",
            }
            for rule in rules
            if set(rule.get("profiles", [])) & {"web-static"}
            and rule["id"] != "BASIC-FOOTER-01"
        ]
        manifest = {
            "name": "demo",
            "standard": (ROOT / "VERSION").read_text().strip(),
            "profiles": ["web-static"],
            "docs": "docs/BASIC-SPECS.md",
            "appSpecs": "docs/APP-SPECS.md",
            "deviations": deviations,
            "commands": {
                "unit": "true",
                "e2e": "true",
                "metrics": "true",
            },
        }
        (self.app / "basics.json").write_text(json.dumps(manifest, indent=2) + "\n")
        lock = {
            "standard": manifest["standard"],
            "source": "fixture",
            "files": {
                str(path.relative_to(self.app)): __import__("hashlib").sha256(path.read_bytes()).hexdigest()
                for path in sorted((self.app / "basics").rglob("*"))
                if path.is_file()
            },
        }
        (self.app / "basics.lock").write_text(json.dumps(lock, indent=2) + "\n")

    def tearDown(self):
        self.temp.cleanup()

    def run_basics(self, *args):
        return subprocess.run(
            [sys.executable, str(self.app / "basics" / "check.py"), "--root", str(self.app), *args],
            text=True,
            capture_output=True,
        )

    def test_docs_and_check_pass(self):
        result = self.run_basics("docs")
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_basics("check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        text = (self.app / "docs" / "BASIC-SPECS.md").read_text()
        self.assertIn("generated; do not edit", text)
        self.assertIn("This app", text)

    def test_hand_edit_fails(self):
        self.assertEqual(self.run_basics("docs").returncode, 0)
        path = self.app / "docs" / "BASIC-SPECS.md"
        path.write_text(path.read_text() + "\nhand edit\n")
        result = self.run_basics("check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("not the generated document", result.stdout)

    def test_expired_deviation_fails(self):
        manifest_path = self.app / "basics.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["deviations"][0]["review"] = "2000-01-01"
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n")
        self.assertEqual(self.run_basics("docs").returncode, 0)
        result = self.run_basics("check")
        self.assertEqual(result.returncode, 1)
        self.assertIn("expired", result.stdout)


if __name__ == "__main__":
    unittest.main()
