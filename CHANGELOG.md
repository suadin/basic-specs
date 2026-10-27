# Changelog

## 1.0.2 — 2026-10-27

- Fix remote `sync`: `--from` and `--source` no longer share one argparse target.

## 1.0.1 — 2026-10-27

- Generated note is plain text that every reader renders without markup.
- The normative spec links to the README.
- Added the fleet report and the weekly update workflow template.

## 1.0.0 — 2026-10-27

First version. Extracted from the workspace contract and the four-wins, die-wand and
diary implementations.

- Rule IDs for documents, reader, footer, links, layout, design, dates, data, tests
  and quality.
- Profiles `web-static`, `web-server`, `design-only`, `quality-typescript` and
  `quality-python`.
- Portable `basics.py` checker, `sync`, `docs` and `init`.
- Pinned `basics.lock` with SHA-256 for every copied file.
- Specimen and vanilla static template.
- Public registry generated from the `basic-specs` GitHub topic.
