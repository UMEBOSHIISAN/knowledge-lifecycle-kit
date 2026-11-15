# knowledge-lifecycle-gate

<picture>
  <source media="(prefers-reduced-motion: reduce)" srcset="assets/knowledge-lifecycle-orbit.png">
  <img src="assets/knowledge-lifecycle-orbit.gif" width="192" height="192" alt="A green whale and crescent moon with three books orbiting between them">
</picture>

[Static logo](assets/knowledge-lifecycle-orbit.png)

Offline knowledge-asset lifecycle checks and an optional local writer API for candidate evaluation.

The `klg inspect`, `klg validate`, and `klg propose-transition` commands inspect Markdown knowledge-asset metadata, validate a public lifecycle profile, detect expired confirmed evidence, and propose the next safe state. These CLI commands are read-only.

The CLI does not modify source files, append lifecycle events, promote assets automatically, or simulate human approval.

The package also exports an optional `KnowledgeTrustWriter` Python API. Constructing it initializes local store, version, audit, and redaction paths. Commit, revalidate, rollback, and redact operations can write local files. This API is separate from the CLI. Callers must authorize their target and operation separately. Neither interface needs a network, external API, LLM, or operational host.

### Revalidate an Evidence note

Call `writer.revalidate(target_path, content, actor, reason, evidence=source_bytes, review=review)`
after the caller has authorized a human decision covering the exact source and
Markdown bytes. The current note must be `STALE` or expired `CONFIRMED` Evidence.
The candidate must be `CONFIRMED` Evidence verified on the local operation date,
with an expiry date that includes that day.

The review mapping has exactly these fields.

| Field | Value |
| --- | --- |
| `target` | Canonical target path relative to `store/`, with forward slashes |
| `current_audit_index` | Zero-based position of the target's latest record in the nonblank audit JSONL records |
| `before_hash`, `after_hash` | SHA-256 of the current file bytes and the candidate Markdown encoded as UTF-8, in `sha256:<lowercase hex>` form |
| `evidence_ref` | Source reference appearing in the candidate's `lineage` |
| `evidence_sha256` | SHA-256 of the exact `source_bytes` passed to the writer, in the same digest form |
| `reviewer`, `decision_ref` | Reviewer identifier and decision reference. Use a distinct decision reference for each review within the store. |

The writer compares the record to the current revision, candidate, and evidence
under a local POSIX publication lock. A successful call preserves earlier
generations, saves the new one, and adds a `revalidate` audit record. The caller
is responsible for authenticating the reviewer and authorizing the operation.
The audit stores the evidence digest and reference. The caller retains the source bytes.

Ordinary commit and rollback reject a confirmed update to expired Evidence.
Rollback also rejects a version containing expired `CONFIRMED` Evidence.
Cooperating Writer calls fail immediately on lock contention. Synchronous
publication errors use the existing compensation path. Power loss and edits
from outside the Writer are outside that guarantee.

This package is an adapter profile, not a replacement for any larger lifecycle implementation. The public profile is intentionally limited to:

- asset types: `CONCEPT`, `EVIDENCE`, `TRIAL`, `PROCEDURE`, `QUESTION`;
- states: `NEW`, `CANDIDATE`, `CONFIRMED`, `STALE`, `RETIRED`.

Richer or unsupported lifecycle values fail closed. A proposal is represented by an event-like `*_PROPOSED` label and always carries a human-confirmation requirement. No `*_RECORDED` event is emitted.

## Commands

```bash
klg inspect FILE
klg validate FILE
klg propose-transition FILE
```

Add `--json` for machine-readable output and `--as-of YYYY-MM-DD` for deterministic freshness checks.

## Parser boundary

The package supports a documented strict YAML-frontmatter subset: top-level scalars, one-level mappings, and one-level lists. Unsupported YAML constructs fail closed. This keeps runtime behavior dependency-free and offline-safe for the first clean-machine experiment.

## Development

From this component directory in a checkout of the public repository:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest -q
```

For a runtime-only install, use `python -m pip install .` without the `[test]`
extra. See [Quickstart](QUICKSTART.md) for the complete clone-to-CLI sequence.

The package is intended for candidate evaluation. Publication requires an explicit
human decision and a separate release review.

## OSS preparation

The package includes an MIT license, contributor/security guidance, a changelog,
and logo assets. See [OSS_READINESS.md](OSS_READINESS.md) for the preparation
checklist. These files prepare a candidate release; they do not authorize
publication or imply that this candidate has been publicly released.

- [Contributing](CONTRIBUTING.md)
- [Security](SECURITY.md)
- [Code of Conduct](CODE_OF_CONDUCT.md)
- [Changelog](CHANGELOG.md)
- [Release preparation](RELEASING.md)

The dependency-free editable backend requires a pip release with PEP 660
editable-build support. Very old pip releases may need a controlled bootstrap
step before installation.
