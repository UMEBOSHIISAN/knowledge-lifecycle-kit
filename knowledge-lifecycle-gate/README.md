# knowledge-lifecycle-gate

![Knowledge Lifecycle Gate mark](assets/knowledge-lifecycle-gate-mark.svg)

Offline knowledge-asset lifecycle checks and an optional local writer API for candidate evaluation.

The `klg inspect`, `klg validate`, and `klg propose-transition` commands inspect Markdown knowledge-asset metadata, validate a public lifecycle profile, detect expired confirmed evidence, and propose the next safe state. These CLI commands are read-only.

The CLI does not modify source files, append lifecycle events, promote assets automatically, or simulate human approval.

The package also exports an optional `KnowledgeTrustWriter` Python API. Constructing it initializes local store, version, audit, and redaction paths; commit, rollback, and redact operations can write local files. This API is not invoked by the three CLI commands above. Callers must authorize their target and operation separately; a validation result or an approval-token string is not human authentication or execution permission. Neither interface accesses a network, calls an external API, uses an LLM, or requires an operational host.

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

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[test]'
python -m pytest -q
```

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
