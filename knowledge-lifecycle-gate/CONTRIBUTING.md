# Contributing

Knowledge Lifecycle Gate is intentionally small and read-only. Contributions
should preserve the public profile and the authority boundary:

- machine code may inspect, validate, and propose;
- recorded lifecycle changes remain human-only;
- source assets, ledgers, schedulers, credentials, and external services are
  out of scope;
- a change must include a focused regression test when behavior changes.

## Local checks

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest -q
```

The runtime package has no third-party dependency. If network access is not
allowed, provide pytest through a reviewed local wheelhouse and keep the
runtime install separate.

Before submitting a change, also verify that examples remain unchanged after
`inspect`, `validate`, and `propose-transition` commands.
