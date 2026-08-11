# knowledge-lifecycle-gate

![Knowledge Lifecycle Gate mark](assets/knowledge-lifecycle-gate-mark.svg)

Read-only knowledge-asset lifecycle checks for local evaluation.

`knowledge-lifecycle-gate` is a small, read-only package for inspecting Markdown knowledge-asset metadata, validating a public lifecycle profile, detecting expired confirmed evidence, and proposing the next safe state.

It does not modify source files, append lifecycle events, promote assets automatically, simulate human approval, access a network, call an external API, use an LLM, or depend on an operational host.

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
