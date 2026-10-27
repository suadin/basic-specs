# Migrations

## 1.1.0

- Add `appVersion` and `runtime` to `basics.json`.
- Generate the runtime file with `basics docs`.
- Remove `RELEASE NOTES` as a reader tab; compose it as the first `SPECS` page.
- Add the six-item footer and the version state rules.
- Publish `version.json` at the Pages root.

## 1.0.0

This is the first release. There is no earlier standard to migrate from.

To adopt it in an existing app:

1. Add `basics.json` with `standard`, `name`, `profiles` and `docs`.
2. Run `python3 basics/check.py sync --from ../basic-specs`.
3. Run `python3 basics/check.py docs`.
4. Add missing tests or record a deviation with a reason and review date.
5. Add `python3 basics/check.py check` to the app's check command and CI.
