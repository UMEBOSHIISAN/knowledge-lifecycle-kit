# Knowledge Lifecycle Kit

![Knowledge Lifecycle Gate mark](knowledge-lifecycle-gate/assets/knowledge-lifecycle-gate-mark.svg)

Knowledge Lifecycle Kit is a public-surface candidate containing two small,
offline-safe components:

- `knowledge-lifecycle-gate/` — read-only Markdown asset inspection and
  human-gated lifecycle proposals.
- `llm-routing/` — deterministic advisory worker recommendation and
  evidence-linked scorecard validation.

The routing component never executes a worker, starts a model, selects a seat,
or writes an approval. It leaves `selected_alias` and `actual_alias` empty for
the human/orchestrator layer. No provider adapter, credential, private
registry, runtime log, or operational wrapper is included in this public
candidate.

## Mothership relationship

Knowledge Lifecycle Kit is an independently adoptable companion in
Mothership's wider constellation. It is not registered in Mothership's frozen
protocol suite and does not claim suite compatibility. Validation and routing
output are evidence and recommendations only: they do not grant authority,
select an executor, or trigger execution. See
[the relationship statement](docs/mothership-relationship.md).

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
python3 -m unittest -v tests/test_routing.py
```

The runtime components use only the Python standard library. A fresh venv may
need pytest supplied by a reviewed local wheelhouse. No network call is needed
for runtime behavior or the routing test.

The KLG test wheelhouse is a verification-only input. Its manifest records
every wheel filename and SHA-256, and local release checks reject an absent or
mismatched wheelhouse before installing anything. The wheel binaries are not
part of the repository or either runtime dependency set.

## Boundaries

Machine code may inspect, validate, and recommend. Human authority remains
required for recorded lifecycle changes and any worker execution. Schedulers,
daemons, external APIs, credentials, and deployment configuration are out of
scope.

See [PUBLIC_OSS_CANDIDATE.md](PUBLIC_OSS_CANDIDATE.md) for the exclusion and
release-readiness audit.
