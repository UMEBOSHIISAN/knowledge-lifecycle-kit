# Quickstart

Run the literal runtime acceptance sequence from the package root:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pytest
klg validate examples/evidence.md
klg propose-transition examples/stale_evidence.md
```

The runtime package has no third-party dependency. A clean venv does not
automatically contain pytest; provide it through the evaluator's controlled
environment or use `python -m pip install -e '.[test]'` with a reviewed
wheelhouse.

Expected stale proposal output includes:

```text
Suggested transition: STALE_PROPOSED
Human confirmation required: YES
Mutation performed: NO
```

The direct promotion example must fail validation:

```bash
klg validate examples/invalid_promotion.md
```

No example file should change during any command.
