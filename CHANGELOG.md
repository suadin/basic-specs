# Changelog

## 1.2.0 — 2026-10-30

- The reference implementation gains `composeSpecs` in `reader.js`: the reader composes
  the SPECS page from the app rules and the release notes. It was written in `die-wand`
  and never came back; `app.js` now imports it instead of defining a second copy.
- Two generic rules move from `app-template` into `style.css`: `.actions .mode.active`
  and `#basic-specs.outdated`.
- New tool `checks/specimen_drift.py` compares every app's copy of the shared runtime
  with the specimen. `reader.js` and `tokens.css` must be byte identical, `style.css`
  must start with the specimen; an app may append. Advisory: it runs where the
  workspace lies, not in this repository's CI.

## 1.1.1 — 2026-10-27

- Clarify that a footer item never wraps internally; only the row wraps between
  items on narrow screens.
- Clarify that the automated test list stays inside the documentation card, below
  the body and above the dashed separator.

## 1.1.0 — 2026-10-27

- Six footer items: README, SPECS, BASIC SPECS, source, unit, E2E.
- App version and Basic Specs version are clickable documentation items.
- Basic Specs turns red only for a newer major release; minor and patch updates are
  visible in the tooltip.
- SPECS begins with one Changelog page from `RELEASE-NOTES.md`; the separate release
  notes tab is gone.
- `version.json`, app runtime metadata and `appVersion` are part of the check.
- This is a visible breaking change for external consumers; all workspace apps move
  in the same pass.

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
