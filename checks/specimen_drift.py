#!/usr/bin/env python3
"""Compare every app's copy of the shared runtime with the specimen.

The standard ships one reference implementation in `reference/specimen/`. Apps do not
import it, they copy it — so the copies drift, and a change made in one app never reaches
the others. This script makes the drift visible. Measured on 30 Oct 2026, it found both
directions at once: two generic CSS rules that only `app-template` had, and
`composeSpecs` that only `die-wand` had moved into `reader.js`.

Two contracts, because the files are not the same kind:

- `reader.js` and `tokens.css` are library code and must be **byte identical**.
- `style.css` is a base plus the app's own rules, so the specimen must be a **prefix**.
  An app may append; it may not reorder or reword the base.

    python3 checks/specimen_drift.py --workspace ~/dev
    python3 checks/specimen_drift.py --workspace ~/dev --json

Exit code 1 when any app deviates.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
SPECIMEN = ROOT / "reference" / "specimen"

IDENTICAL = ("reader.js", "tokens.css")
PREFIXED = ("style.css",)

# Folders that hold a build output, a pinned standard, a dependency tree or a test
# artefact. A hit there is not a copy an app maintains by hand.
SKIP = {
    ".git",
    ".venv",
    "__pycache__",
    "basics",
    "coverage",
    "dist",
    "e2e",
    "node_modules",
    "test-results",
}


def copies(app: Path, name: str) -> list[Path]:
    return sorted(
        path
        for path in app.rglob(name)
        if not (set(path.relative_to(app).parts) & SKIP) and path.is_file()
    )


def differs(original: bytes, candidate: bytes) -> bool:
    return original != candidate


def prefix_problem(original: bytes, candidate: bytes) -> str:
    """Empty when the candidate starts with the original, else a short reason."""
    reference = original.decode("utf-8", "replace").splitlines()
    other = candidate.decode("utf-8", "replace").splitlines()
    if other[: len(reference)] == reference:
        return ""
    for index, (left, right) in enumerate(zip(reference, other), start=1):
        if left != right:
            return f"line {index}: the specimen says {left!r}, the app says {right!r}"
    return f"the app is shorter than the specimen ({len(other)} < {len(reference)} lines)"


def check_app(app: Path, specimen: Path = SPECIMEN) -> dict:
    result: dict = {"name": app.name, "files": [], "ok": True}
    identical_hits = [
        (name, path) for name in IDENTICAL for path in copies(app, name) if (specimen / name).exists()
    ]
    # An app participates only when it carries the specimen's library code. A file that
    # happens to share a name - diary's own style.css - is not a copy of the base.
    if not identical_hits:
        return result
    for name, path in identical_hits:
        same = not differs((specimen / name).read_bytes(), path.read_bytes())
        result["files"].append(
            {
                "file": str(path.relative_to(app)),
                "contract": "identical",
                "state": "ok" if same else "differs",
            }
        )
        result["ok"] = result["ok"] and same
    for name in PREFIXED:
        for path in copies(app, name):
            original = specimen / name
            if not original.exists():
                continue
            reason = prefix_problem(original.read_bytes(), path.read_bytes())
            result["files"].append(
                {
                    "file": str(path.relative_to(app)),
                    "contract": "prefix",
                    "state": "ok" if not reason else "differs",
                    "reason": reason,
                }
            )
            result["ok"] = result["ok"] and not reason
    return result


def scan(workspace: Path, specimen: Path = SPECIMEN) -> dict:
    repos = workspace / "repos"
    apps = []
    if repos.is_dir():
        for app in sorted(repos.iterdir()):
            if not app.is_dir() or not (app / ".git").exists():
                continue
            checked = check_app(app, specimen)
            if checked["files"]:
                apps.append(checked)
    shown = str(specimen)
    try:
        shown = str(specimen.relative_to(ROOT))
    except ValueError:
        pass
    return {
        "specimen": shown,
        "apps": apps,
        "ok": all(app["ok"] for app in apps),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", default=str(ROOT.parent.parent))
    parser.add_argument("--specimen", default=str(SPECIMEN))
    parser.add_argument("--json", action="store_true")
    arguments = parser.parse_args(argv)
    report = scan(Path(arguments.workspace).expanduser(), Path(arguments.specimen).expanduser())
    if arguments.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
        return 0 if report["ok"] else 1
    print(f"specimen: {report['specimen']}")
    for app in report["apps"]:
        state = "ok" if app["ok"] else "ABWEICHUNG"
        print(f"{app['name']:<16} {state}")
        for entry in app["files"]:
            mark = "  " if entry["state"] == "ok" else "!!"
            extra = f" — {entry['reason']}" if entry.get("reason") else ""
            print(f"  {mark} {entry['file']:<20} {entry['contract']:<10} {entry['state']}{extra}")
    if not report["apps"]:
        print("keine App mit einer Kopie der Laufzeit gefunden")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
