# OSS readiness checklist

Public source `411d6b3642f359dfbaa4529337e47a842702e4d3` was audited on
2026-10-15; this record was updated on 2026-10-16. No publication authority
is implied by the checklist.

- [x] Standalone pyproject.toml and build backend
- [x] Identical root/component MIT files and full notice in wheel artifacts
- [x] README/quickstart/contributor/security/release guidance
- [x] Synthetic examples and existing tests
- [x] Fresh fixed-source suites and expiry/promotion/nonmutation checks
- [x] Actual CI discovery command corrected; collection regression added
- [x] Actual regular/editable artifact-license regressions
- [x] Legacy SVG/PNG permission and adopted green whale GIF/PNG provenance inventory
- [x] Scoped README onboarding/logo updates; CLI/writer boundary documented
- [x] Reachable-history and obtainable-log pattern checks scoped in the audit
- [x] W1–W6 Writer fixes exercised by 40 regressions, with scope limits retained
- [x] Fresh regular installed-package suite: 81 passed; root suite: 9 passed
- [x] Separate fresh editable test install: same 81 component cases passed
- [x] Both README displays, GIF/PNG and 12 distinct public link targets checked

See the [fixed-source audit](../docs/verification-411d6b36.md) for counts,
module/example hashes, self-verification level and unverified scope. Existing
CI run 38719897632 belongs to `411d6b36`; a new documentation commit requires
its own exact-head result. Delivery and CI receipts are saved separately from
the candidate source commit; see [readiness](../RELEASE_READINESS.md).

Read-only covers klg inspect, klg validate and klg propose-transition.
KnowledgeTrustWriter writes local files and is outside that claim. No routing
component is included. External-maintainer/different-machine acceptance, sdist
release, exclusive artwork rights and full writer durability are not claimed.

See [the audit](../PUBLIC_OSS_CANDIDATE.md) and
[the artwork provenance and permission record](../docs/asset-rights.md).
