# Knowledge Lifecycle Kit

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="knowledge-lifecycle-gate/assets/knowledge-lifecycle-orbit.png">
  <img src="knowledge-lifecycle-gate/assets/knowledge-lifecycle-orbit.gif" width="192" height="192" alt="A green whale and crescent moon with three books orbiting between them">
</picture>

[Static logo](knowledge-lifecycle-gate/assets/knowledge-lifecycle-orbit.png)

Inspect Markdown provenance metadata, verification dates, expiry, and lifecycle
state transitions, then propose changes for human review. The runtime works
offline and uses only the Python standard library.

The kit contains one independently usable component:

- `knowledge-lifecycle-gate/` — read-only Markdown asset inspection and
  human-gated lifecycle proposals through the `klg` CLI. The package also exports
  an optional `KnowledgeTrustWriter` Python API that explicitly writes local files.

No provider adapter, credential, private registry, runtime log, or operational
wrapper is included in this public candidate.

## Mothership relationship

Knowledge Lifecycle Kit is an independently adoptable companion in
Mothership's wider constellation. It is not registered in Mothership's frozen
protocol suite and does not claim suite compatibility. Validation output is
evidence only: it does not grant authority, select an executor, or trigger
execution. See [the relationship statement](docs/mothership-relationship.md).

See [local verification](docs/verification.md) for the offline release checks.

## Try it

With Python 3.9+ installed, get the public source and run the CLI:

```bash
git clone https://github.com/UMEBOSHIISAN/knowledge-lifecycle-kit.git
cd knowledge-lifecycle-kit/knowledge-lifecycle-gate
python3 -m venv .venv
source .venv/bin/activate
python -m pip install .
klg validate examples/evidence.md
klg propose-transition examples/stale_evidence.md
```

The expired example proposes `STALE_PROPOSED`, requires human confirmation,
and reports `Mutation performed: NO`. See [Quickstart](knowledge-lifecycle-gate/QUICKSTART.md)
for expected output and the invalid-promotion example.

## Run the tests

From `knowledge-lifecycle-gate/` with the same virtual environment active:

```bash
python -m pip install -e '.[test]'
python -m pytest -q
cd ..
python -m unittest discover -s tests -v
```

The `[test]` extra installs pytest; the runtime-only install does not. If package
index access is unavailable, use a reviewed local wheelhouse as described in
[local verification](docs/verification.md). Runtime commands need no network
access. Editable development installs require pip with PEP 660 support.

## Boundaries

Machine code may inspect, validate, and propose transitions. Human authority
remains required for recorded lifecycle changes and any execution. Schedulers,
daemons, external APIs, credentials, and deployment configuration are out of
scope.

The read-only boundary applies to `klg inspect`, `klg validate`, and
`klg propose-transition`, not every Python API in the package. Constructing
`KnowledgeTrustWriter` creates its local store, version, audit, and redaction
paths; its commit, rollback, and redact methods can write files. A caller must
authorize the target and operation separately. The API and its validation
results do not authenticate human approval or grant execution authority.

See [PUBLIC_OSS_CANDIDATE.md](PUBLIC_OSS_CANDIDATE.md) for the exclusion and
release-readiness audit.
