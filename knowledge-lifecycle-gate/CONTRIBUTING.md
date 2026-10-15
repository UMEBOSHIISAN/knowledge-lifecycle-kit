# Contributing

Knowledge Lifecycle Gate has a small public profile. Its `klg inspect`,
`klg validate`, and `klg propose-transition` commands are read-only.
Contributions should preserve that CLI boundary:

- machine code may inspect, validate, and propose;
- the CLI must not record lifecycle changes or modify source assets or ledgers;
- schedulers, credentials, and external services are out of scope;
- a change must include a focused regression test when behavior changes.

The optional `KnowledgeTrustWriter` Python API is separate from these commands.
Construction initializes local store, version, audit, and redaction paths;
commit, rollback, and redact operations can write local files. Callers must
authorize the target and operation separately. A validation result or an
approval-token string does not authenticate human approval or grant execution
authority. Changes to that API must preserve its documented boundary and tests;
do not describe the entire package as read-only.

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
