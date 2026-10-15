# Knowledge Lifecycle Kit

![Knowledge Lifecycle Gate mark](knowledge-lifecycle-gate/assets/knowledge-lifecycle-gate-mark.svg)

Knowledge Lifecycle Kit is a public-surface candidate containing an offline-safe component:

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

## Quick checks

```bash
cd knowledge-lifecycle-gate
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
pytest
klg validate examples/evidence.md
klg propose-transition examples/stale_evidence.md
cd ..
python3 -m unittest discover -s tests
```

The runtime component uses only the Python standard library. A fresh venv may
need pytest supplied by a reviewed local wheelhouse. No network call is needed
for runtime behavior.

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
