import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from checks.specimen_drift import check_app, prefix_problem, scan  # noqa: E402


class SpecimenDriftTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.workspace = Path(self.temp.name)
        self.specimen = self.workspace / "reference" / "specimen"
        self.specimen.mkdir(parents=True)
        (self.specimen / "reader.js").write_text("export const a = 1;\n", encoding="utf-8")
        (self.specimen / "tokens.css").write_text(":root { --x: 1; }\n", encoding="utf-8")
        (self.specimen / "style.css").write_text("* { box-sizing: border-box; }\n", encoding="utf-8")

    def app(self, name: str) -> Path:
        app = self.workspace / "repos" / name
        (app / ".git").mkdir(parents=True)
        (app / "site").mkdir()
        return app

    def test_an_identical_copy_passes(self):
        app = self.app("gleich")
        (app / "site" / "reader.js").write_text("export const a = 1;\n", encoding="utf-8")
        (app / "site" / "tokens.css").write_text(":root { --x: 1; }\n", encoding="utf-8")
        result = check_app(app, self.specimen)
        self.assertTrue(result["ok"])

    def test_one_changed_character_fails(self):
        app = self.app("anders")
        (app / "site" / "reader.js").write_text("export const a = 2;\n", encoding="utf-8")
        (app / "site" / "tokens.css").write_text(":root { --x: 1; }\n", encoding="utf-8")
        result = check_app(app, self.specimen)
        self.assertFalse(result["ok"])
        states = {entry["file"]: entry["state"] for entry in result["files"]}
        self.assertEqual(states["site/reader.js"], "differs")
        self.assertEqual(states["site/tokens.css"], "ok")

    def test_an_app_may_append_to_style_css(self):
        app = self.app("erweitert")
        (app / "site" / "reader.js").write_text("export const a = 1;\n", encoding="utf-8")
        (app / "site" / "style.css").write_text(
            "* { box-sizing: border-box; }\n.card { color: red; }\n", encoding="utf-8"
        )
        self.assertTrue(check_app(app, self.specimen)["ok"])

    def test_an_app_may_not_reword_the_base(self):
        app = self.app("umgeschrieben")
        (app / "site" / "reader.js").write_text("export const a = 1;\n", encoding="utf-8")
        (app / "site" / "style.css").write_text("*{box-sizing:border-box}\n", encoding="utf-8")
        result = check_app(app, self.specimen)
        self.assertFalse(result["ok"])

    def test_an_app_without_the_library_code_is_not_judged(self):
        # diary carries its own style.css; it never copied the specimen, so the prefix
        # contract does not apply to it.
        app = self.app("eigen")
        (app / "site" / "style.css").write_text(":root { --own: 1; }\n", encoding="utf-8")
        result = check_app(app, self.specimen)
        self.assertTrue(result["ok"])
        self.assertEqual(result["files"], [])

    def test_a_build_folder_is_not_a_copy(self):
        app = self.app("gebaut")
        (app / "site" / "reader.js").write_text("export const a = 1;\n", encoding="utf-8")
        (app / "node_modules" / "x").mkdir(parents=True)
        (app / "node_modules" / "x" / "reader.js").write_text("kaputt\n", encoding="utf-8")
        (app / "dist").mkdir()
        (app / "dist" / "reader.js").write_text("kaputt\n", encoding="utf-8")
        self.assertTrue(check_app(app, self.specimen)["ok"])

    def test_the_workspace_scan_collects_the_apps(self):
        app = self.app("gesammelt")
        (app / "site" / "reader.js").write_text("export const a = 1;\n", encoding="utf-8")
        (app / "site" / "tokens.css").write_text(":root { --x: 1; }\n", encoding="utf-8")
        report = scan(self.workspace, self.specimen)
        self.assertEqual([entry["name"] for entry in report["apps"]], ["gesammelt"])
        self.assertTrue(report["ok"])

    def test_a_missing_line_is_named(self):
        app = self.app("kurz")
        (app / "site" / "reader.js").write_text("export const a = 1;\n", encoding="utf-8")
        (app / "site" / "style.css").write_text("", encoding="utf-8")
        result = check_app(app, self.specimen)
        reason = result["files"][-1]["reason"]
        self.assertIn("shorter", reason)

    def test_the_prefix_reason_names_the_line(self):
        reason = prefix_problem(b"a\nb\n", b"a\nc\n")
        self.assertIn("line 2", reason)


if __name__ == "__main__":
    unittest.main()
