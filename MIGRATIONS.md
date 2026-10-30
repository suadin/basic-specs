# Migrations

## 1.2.0

The reference implementation changed, so the copies in the apps have to follow. No rule
changed and no app has to alter its behaviour.

- `reference/specimen/reader.js` exports `composeSpecs`. Copy it over the app's
  `reader.js` and delete the local function of the same name in `app.js`, otherwise two
  copies live side by side.
- `reference/specimen/style.css` gained two rules that only `app-template` had. Copy the
  file over the app's `style.css` and keep the app's own rules below it.
- `design/tokens.css` is unchanged.

To check the result: `python3 checks/specimen_drift.py --workspace ~/dev`.

## 1.1.1

Clarifies footer item wrapping and the placement of the automated test list. No
behavioural change for an app that already follows 1.1.0.

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
