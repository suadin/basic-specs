#!/usr/bin/env python3
"""Collect public apps that opted into the `basic-specs` topic.

The result is a generated registry. Public apps are visible; private apps stay
local and are not queried here.
"""

from __future__ import annotations

import json
import os
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OWNER = os.environ.get("BASICS_OWNER", "suadin")
TOKEN = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")


def api(path: str) -> dict:
    request = urllib.request.Request(
        f"https://api.github.com{path}",
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "basic-specs-registry",
            **({"Authorization": f"Bearer {TOKEN}"} if TOKEN else {}),
        },
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def raw(repo: str, branch: str, name: str) -> dict | None:
    url = f"https://raw.githubusercontent.com/{repo}/{branch}/{name}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return json.load(response)
    except Exception:
        return None


def update_kind(pinned: str | None, latest: str) -> str:
    try:
        old = [int(part) for part in str(pinned).split(".")[:3]]
        new = [int(part) for part in latest.split(".")[:3]]
    except ValueError:
        return "unknown"
    if len(old) < 3 or len(new) < 3:
        return "unknown"
    if new[0] > old[0]:
        return "major"
    if new[1] > old[1]:
        return "minor"
    if new[2] > old[2]:
        return "patch"
    return "none"


def main() -> int:
    query = urllib.parse.quote(f"topic:basic-specs user:{OWNER}")
    latest = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    found = api(f"/search/repositories?q={query}&per_page=100")
    apps = []
    for repo in found.get("items", []):
        full = repo["full_name"]
        branch = repo.get("default_branch", "main")
        manifest = raw(full, branch, "basics.json")
        if not manifest:
            continue
        run = api(f"/repos/{full}/actions/runs?per_page=1").get("workflow_runs", [])
        latest = run[0] if run else {}
        apps.append(
            {
                "repo": full,
                "url": repo["html_url"],
                "appVersion": manifest.get("appVersion"),
                "profiles": manifest.get("profiles", []),
                "version": manifest.get("standard"),
                "latest": latest,
                "update": update_kind(manifest.get("standard"), latest),
                "deviations": len(manifest.get("deviations") or []),
                "latestRun": {
                    "status": latest.get("status"),
                    "conclusion": latest.get("conclusion"),
                    "url": latest.get("html_url"),
                },
            }
        )
    apps.sort(key=lambda item: item["repo"].lower())
    data = {
        "standard": (ROOT / "VERSION").read_text().strip(),
        "updatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%MZ"),
        "apps": apps,
    }
    (ROOT / "registry" / "apps.json").write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    lines = [
        "# Registry",
        "",
        "Generated from public repositories with the `basic-specs` topic.",
        "",
        f"Standard: **{data['standard']}** · updated {data['updatedAt']}",
        "",
        "| App | App version | Standard | Update | Profiles | Deviations | Latest run |",
        "|---|---|---|---|---|---|---|",
    ]
    for app in apps:
        run = app["latestRun"]
        status = run.get("conclusion") or run.get("status") or "not run"
        link = f"[{status}]({run['url']})" if run.get("url") else status
        lines.append(
            f"| [{app['repo']}]({app['url']}) | {app['appVersion'] or '—'} | "
            f"{app['version']} | {app['update']} | "
            f"{', '.join(app['profiles'])} | {app['deviations']} | {link} |"
        )
    if not apps:
        lines.append("| — | — | — | — | — | — | — |")
    (ROOT / "registry" / "REGISTRY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"registry: {len(apps)} public app(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
