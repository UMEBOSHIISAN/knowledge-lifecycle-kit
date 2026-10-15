# Release preparation

This checklist prepares a candidate OSS release without publishing it.

1. Run the tests in `CONTRIBUTING.md` on a clean supported Python version.
2. Run `klg validate` and `klg propose-transition` against every synthetic
   example.
3. Confirm example hashes are unchanged and reports contain no local paths.
4. Inspect the source tree for credentials, private data, generated caches,
   and unintended network or process execution.
5. Build and inspect a wheel or source archive in a temporary directory.
6. Review `LICENSE`, `SECURITY.md`, `CHANGELOG.md`, and `OSS_READINESS.md`.
7. Obtain an explicit human publication decision before any registry upload,
   repository push, tag, or release action.

The enclosing repository includes test-only CI. This component includes no
publishing credential, registry URL or deployment command. The three klg
commands are read-only; the exported KnowledgeTrustWriter is a local writer
API and is outside that guarantee. See the enclosing repository's
RELEASE_READINESS.md and docs/asset-rights.md before any publication decision.
