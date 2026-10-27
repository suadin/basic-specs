#!/usr/bin/env python3
"""Read the generated public registry and show drift from the current major."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", default=str(ROOT / "registry" / "apps.json"))
    args = parser.parse_args()
    data = json.loads(Path(args.registry).read_text(encoding="utf-8"))
    standard = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    major = standard.split(".")[0]
    failed = False
    print(f"standard {standard}")
    for app in data.get("apps", []):
        version = str(app.get("version", "—"))
        run = app.get("latestRun") or {}
        state = run.get("conclusion") or run.get("status") or "not run"
        same_major = version.split(".")[0] == major
        if not same_major or state != "success":
            failed = True
        print(
            f"{app['repo']:<32} {version:<8} {state:<12} "
            f"deviations={app.get('deviations', 0)} "
            f"{'' if same_major else 'MAJOR DRIFT'}"
        )
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
