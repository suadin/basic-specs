# Migrations

## 1.0.0

This is the first release. There is no earlier standard to migrate from.

To adopt it in an existing app:

1. Add `basics.json` with `standard`, `name`, `profiles` and `docs`.
2. Run `python3 basics/check.py sync --from ../basic-specs`.
3. Run `python3 basics/check.py docs`.
4. Add missing tests or record a deviation with a reason and review date.
5. Add `python3 basics/check.py check` to the app's check command and CI.
