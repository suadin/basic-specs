# AI guide

The app owns its stack. This standard owns the observable behaviour and the
proof. When an AI changes an app:

1. Read `basics.json`, `APP-SPECS.md` and the generated `BASIC-SPECS.md`.
2. Never edit `basics/`, `basics.lock` or the generated part of `BASIC-SPECS.md`.
3. Change the app, then add or update tests carrying the rule ID.
4. Run `python3 basics/check.py --root . check --run`.
5. Commit the code, the tests, the regenerated docs and the metrics together.
6. Push and deploy where the app has a rollout.

If a rule does not apply, add a deviation to `basics.json` with the rule ID, a
one-sentence reason and a review date. Do not delete the rule from the document.

To adopt a new standard release:

```sh
python3 basics/check.py --root . sync --version 1.1.0
python3 basics/check.py --root . check --run
```

The sync is mechanical. The AI does the semantic part and the checker gates it.
