# Public OSS candidate audit

## Result

`PUBLIC_OSS_CANDIDATE_READY_WITH_GAPS`

This tree is the public-surface candidate. It is deliberately smaller than the
full transfer bundle.

## Included

- Standalone KLG implementation, schema, synthetic examples, tests, OSS docs,
  and logo assets.
- Deterministic advisory routing and scorecard contracts with synthetic
  fixtures and a no-execution test.
- MIT license and a single public-surface manifest.

## Excluded

- Repository-specific inventories and repair notes.
- Source-machine provenance maps, owner aliases, model registries, wrappers,
  approval ledgers, runtime logs, prompts, model outputs, and customer data.
- Provider adapters, shell/model invocation, schedulers, daemon/service files,
  CI configuration, deployment configuration, and credentials.
- Reference-only orchestration snapshots from the transfer bundle.

## Verification gates

- KLG tests: run from `knowledge-lifecycle-gate/`.
- Router tests: `python3 -m unittest -v tests/test_routing.py`.
- JSON schema/fixture parse, SVG parse, source-path scan, secret scan, archive
  traversal scan, and no-live execution scan must all pass before publication.
- A human must still decide whether and where to publish. This candidate has
  not been pushed or uploaded.

## Remaining gaps

1. Independent external maintainer review.
2. Human publication decision and public repository selection.
3. A fully isolated pytest wheelhouse if the receiving environment has no test
   runner and network access is prohibited.

The full transfer bundle remains available separately for local evaluation; it
must not be confused with this public-surface candidate.
