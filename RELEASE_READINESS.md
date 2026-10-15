# Public Release Readiness

**Public source audited on 2026-10-15 JST; record updated on 2026-10-16.**
The fixed audit source is `411d6b3642f359dfbaa4529337e47a842702e4d3`.
The scoped audit found no additional required correction. A later commit
containing this documentation still needs its own measured exact-head CI;
neither an older success nor this label supplies that result or authority.

## Scope and identity

Claim: inspect Markdown provenance, verification dates, expiry and lifecycle
transitions, and propose changes for human review.

- Anonymous public main, clone and fixed-source archive agreed on 61 files.
- The three `klg` commands are read-only. The optional local writer API is
  separate and does not authenticate human approval or authorize execution.
- Root/component MIT files are identical. The maintainer-selected green whale
  GIF/PNG and existing README/CLI/claim boundary were preserved by the Writer
  repair. The repair changed only the Writer and its new regression tests.
- The repository was observed public, with default branch `main`, on 2026-10-16.
- [Fixed-source audit](docs/verification-411d6b36.md) and
  [sanitized measurements](verification/public-audit-411d6b36.json) identify
  the evidence and its limits. Raw local logs/JUnit and the full audit receipt
  remain private and parent-verified, not publicly fetchable proof.

## Measured acceptance at 411d6b36

- [x] Fresh regular installation; all eight installed module hashes match source.
- [x] Runtime CLI works before pytest installation, with no third-party runtime dependency.
- [x] Installed-package component suite: 81 passed, 0 failure/error/skip.
- [x] Root unittest discovery: 9 passed; total 90 unique tests = 50 existing + 40 new.
- [x] Original 13 Writer counterexamples retained; 27 additional cases passed.
- [x] Separate fresh editable test install: same 81 component cases passed.
- [x] Four reviewed test-wheel hashes matched.
- [x] Full 1,073-byte LICENSE and installed RECORD hash/size matched; actual
  regular/editable wheel and metadata regressions passed.
- [x] Expiry day inclusive, expired proposal, forbidden promotion, missing lineage,
  future verification date and expected error exits checked.
- [x] Five example hashes unchanged; reports retain original state and say no mutation.
- [x] Existing no-network regression passed; boundary scan found no enumerated matches.
- [x] Both README displays, green GIF, static PNG and Quickstart inspected;
  18 references to 12 distinct public targets returned anonymous HTTP 200.
- [x] Existing artwork provenance/permission record hashes matched, with no new
  legal or trademark clearance claimed.

All local acceptance above used the same macOS host, fresh Python 3.11.15
environments and pytest 8.3.5. It is parent/self-verified. Earlier independent
implementation advice is not a fresh independent endorsement of this audit.

## Exact-candidate remote gate

Existing main CI
[38719897632](https://github.com/UMEBOSHIISAN/knowledge-lifecycle-kit/actions/runs/38719897632)
completed successfully for `411d6b36`, with 81 component and 9 root tests.
The audit checked the existing same-SHA receipt; it did not trigger a new CI
or reacquire logs. This run cannot attest a later documentation commit.

For each selected new candidate, the operator must measure:

1. Actual authenticated writer and repository permission; preserve shared auth settings.
2. Destination branch and remote commit equal to the selected local SHA.
3. Completed successful CI whose head SHA equals that exact candidate.
4. The candidate's scoped boundary checks and delivery receipt.

Save the final SHA and its CI receipt outside the source commit. Inserting
the future self-hash or result into this file would create another candidate
requiring another check. Publication, tags, registry uploads and settings
changes require their own applicable human authority; this record grants none.

## History and limits

The earlier `96e7edad` CI-reference and wheel-notice repair passed 41 component
and 9 root tests in an existing environment. Its wheel hash, initial private
main observation, bounded history/log checks and protected-CI approval are
retained as historical evidence in [the audit](PUBLIC_OSS_CANDIDATE.md).
The earlier green-logo envelope retained runtime bytes; the later Writer
repair is separately identified by the current `411d6b36` audit.

The Writer verification covers a single writer and synchronous `Exception`
failures. Power/process loss, `BaseException`, multiple writers and hostile
concurrent path changes have no complete atomicity guarantee. Token strings
are not human authentication. Different-machine/external-maintainer acceptance,
Windows, the full Python matrix, fresh dark/mobile presentation and OS motion
preference switching were not verified. No exhaustive secret/history/binary
absence, exclusive artwork rights, authenticated authorization, sdist release
or full Writer durability is certified.
