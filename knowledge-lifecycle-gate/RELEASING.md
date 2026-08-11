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

No CI, publishing credential, registry URL, or deployment command is included
in this package. Those are deliberate authority boundaries, not missing
runtime features.
