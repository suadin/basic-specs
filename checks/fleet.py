#!/usr/bin/env python3
"""Show where the apps stand: pinned standard, app version, deviations, last commit.

Two sources, and only one of them can be current:

- `--registry` (default) reads the generated public registry. It is what GitHub knows,
  and it is stale whenever an app forgot the `basic-specs` topic.
- `--workspace` reads `repos/*/basics.json` and `git log` on this machine. That is the
  fact, and it needs no token.

    python3 checks/fleet.py --workspace ~/dev
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent


def last_commit(app: Path) -> str:
    try:
        answer = subprocess.run(
            ["git", "-C", str(app), "log", "-1", "--format=%ad %s", "--date=format:%Y-%m-%d"],
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.SubprocessError):
        return "—"
    return (answer.stdout or "—").strip()[:52]


def from_workspace(workspace: Path, standard: str) -> tuple[list[str], bool]:
    major = standard.split(".")[0]
    rows: list[str] = []
    failed = False
    for app in sorted((workspace / "repos").iterdir()):
        manifest = app / "basics.json"
        if not manifest.is_file():
            continue
        data = json.loads(manifest.read_text(encoding="utf-8"))
        version = str(data.get("standard", "—"))
        same_major = version.split(".")[0] == major
        failed = failed or not same_major
        rows.append(
            f"{app.name:<16} {version:<8} {str(data.get('appVersion', '—')):<8} "
            f"{len(data.get('deviations') or []):<5} {last_commit(app)}"
            f"{'' if same_major else '  MAJOR DRIFT'}"
        )
    return rows, failed


def from_registry(path: Path, standard: str) -> tuple[list[str], bool]:
    major = standard.split(".")[0]
    data = json.loads(path.read_text(encoding="utf-8"))
    rows: list[str] = []
    failed = False
    for app in data.get("apps", []):
        version = str(app.get("version", "—"))
        run = app.get("latestRun") or {}
        state = run.get("conclusion") or run.get("status") or "not run"
        same_major = version.split(".")[0] == major
        failed = failed or not same_major or state != "success"
        rows.append(
            f"{app['repo']:<32} {version:<8} {state:<12} "
            f"{app.get('deviations', 0):<5}{'' if same_major else '  MAJOR DRIFT'}"
        )
    return rows, failed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", default=str(ROOT / "registry" / "apps.json"))
    parser.add_argument("--workspace", help="read this machine's repos instead of the registry")
    arguments = parser.parse_args()

    standard = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if arguments.workspace:
        rows, failed = from_workspace(Path(arguments.workspace).expanduser(), standard)
        print(f"standard {standard} — {len(rows)} apps on this machine")
        print(f"{'app':<16} {'pinned':<8} {'version':<8} {'dev.':<5} last commit")
    else:
        rows, failed = from_registry(Path(arguments.registry), standard)
        print(f"standard {standard} — {len(rows)} apps in the public registry")
        print(f"{'app':<32} {'pinned':<8} {'ci':<12} dev.")
    for row in rows:
        print(row)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
