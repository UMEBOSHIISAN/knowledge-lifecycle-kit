# Quickstart

With Python 3.9+ installed, start from the public source. On macOS/Linux:

```bash
git clone https://github.com/UMEBOSHIISAN/knowledge-lifecycle-kit.git
cd knowledge-lifecycle-kit/knowledge-lifecycle-gate
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
klg validate examples/evidence.md
klg propose-transition examples/stale_evidence.md
```

On Windows, create the environment with `py -3 -m venv .venv` and activate it
with `.venv\Scripts\Activate.ps1` in PowerShell. The runtime package has no third-party dependency and does not
require pytest, an API key, or a service account.

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

## Optional tests

From `knowledge-lifecycle-gate/` with the virtual environment active:

```bash
python -m pip install -e '.[test]'
python -m pytest -q
cd ..
python -m unittest discover -s tests -v
```

The `[test]` extra supplies pytest. Editable installs require pip with PEP 660
support. For controlled/offline test inputs, follow [local verification](../docs/verification.md)
with a reviewed wheelhouse; the wheelhouse is not bundled in this repository.
