# Public-source audit at 411d6b36

Audited on **2026-10-15 JST**; this public summary was prepared on 2026-10-16.
The source was fixed at
[`411d6b3642f359dfbaa4529337e47a842702e4d3`](https://github.com/UMEBOSHIISAN/knowledge-lifecycle-kit/tree/411d6b3642f359dfbaa4529337e47a842702e4d3).
Anonymous main API, clone and exact-SHA archive observations agreed on all
61 source files. The scoped audit found no additional required correction.

The accepted claim remains: **inspect Markdown provenance, verification dates,
expiry and lifecycle transitions, and propose changes for human review.**
Provenance validation checks declared metadata, not the factual truth of a
source. The three `klg` commands are read-only. `KnowledgeTrustWriter` is a
separate local writer API; its validation or token strings do not authenticate
human approval or grant execution authority.

## Installation and tests

The audit used fresh virtual environments on the same macOS host, with
Python 3.11.15 and pytest 8.3.5. A normal `pip install .` built and installed
the public source. Before installing test dependencies, the runtime CLI worked
without pytest or any third-party runtime dependency. All eight installed
Python module hashes matched the fixed public source.

| Check | Result |
| --- | --- |
| Regular installed-package component suite | 81 passed; 0 failure/error/skip; 0.27 s |
| Root unittest discovery | 9 passed; 0.015 s |
| Unique tests | 90 = 50 existing + 40 Writer regressions |
| Writer regressions | 13 original counterexamples + 27 additional cases |
| Separate fresh editable `[test]` install | 81 component tests passed; 0.33 s; repeated tests, not 81 additional unique cases |
| Offline test inputs | All four hashes in `verification/test-wheelhouse.json` matched |
| Installed LICENSE | Full 1,073-byte notice; RECORD hash and size matched |
| Artifact-license regressions | Regular/editable wheels and prepared metadata covered |
| Public-boundary scanner | No matches under its enumerated text rules |

To test the regular distribution, the audit copied the unchanged tests,
examples and schema outside the checkout and omitted only `tests/conftest.py`,
which otherwise inserts checkout `src` into the import path. There was no
`src` directory in that copy. The suite used the installed `site-packages`
distribution. The original counterexample class's AST was unchanged.

## Writer W1–W6

| Finding | Corrected behavior exercised by the regressions |
| --- | --- |
| W1: metadata differs from saved Markdown | Reject explicit metadata disagreement and malformed Markdown; permit equal metadata. |
| W2: forbidden existing-state transition | Reject RETIRED → CONFIRMED and rollback bypass; a missing canonical with remaining history is not a first import. |
| W3: unrelated rollback input | Reject absolute paths, other-target generations and symlinked generations; accept only a direct generation of the target. |
| W4: storage escape | Reject prefix-sharing sibling and storage-root/version/audit symlinks; use one normalized target for canonical, history and audit. |
| W5: publication without complete evidence | Compensate synchronous write/flush/fsync and partial-append exceptions; report recovery failures; reject subsequent operations on unbacked canonical bytes; preserve unexpected foreign log bytes. |
| W6: invalid writer-generated tombstone | Validate the generated RETIRED Markdown before writing and preserve earlier historical bytes. |

This is a **single-writer, synchronous `Exception` failure** verification.
It does not establish atomicity across files after power loss, process death,
`BaseException`, concurrent writers or hostile concurrent path changes.
Existing limits include unbounded actor/reason text, current-date evaluation
for rollback/redact, possible empty directories after failure and a truthy
approval token bypassing the line-delta limit. That token is not authentication.

## CLI and nonmutation

Console and module entrypoints, help, all three commands, JSON and human output
were checked. The five example files had identical hashes before and after.

| Case | Expected and observed result |
| --- | --- |
| Valid confirmed Evidence | FRESH; exit 0 |
| Expiry day, 2099-01-01 | FRESH; exit 0 |
| Following day, 2099-01-02 | EXPIRED; STALE_PROPOSED; human confirmation required; original CONFIRMED state retained |
| Already expired Evidence | Same human-facing stale proposal; exit 0 |
| NEW → CONFIRMED request | No proposal; exit 1 |
| Missing lineage after NEW | No proposal; exit 1 |
| Verification date later than the selected as-of date | Invalid; exit 1; freshness does not override validity |
| Invalid `--as-of` argument | Argument error; exit 2 |

Reports stated `mutation_performed=false` / `Mutation performed: NO` and the
tested validation output contained no user-specific absolute path. The
existing no-network regression passed as part of the component suite.

## README, artwork and links

A logged-out browser displayed both README files and loaded the green GIF
at 192 × 192 pixels, from a 384 × 384 asset, with descriptive alt text.
The static PNG and Quickstart links were followed. GitHub retained the
`prefers-reduced-motion` picture source. The two README files contained
18 link/image references to 12 distinct public targets; all targets existed
and returned anonymous HTTP 200.

The GIF structure had 120 frames at 50 ms, a six-second duration and a complete
trailer. This is a structure check, not a pixel-by-pixel motion acceptance or
an OS motion-preference switching test. Current asset hashes matched the
existing [rights and provenance record](asset-rights.md). No new legal or
trademark clearance was performed.

## Evidence identity and limits

The [sanitized audit summary](../verification/public-audit-411d6b36.json)
contains source module hashes, measured counts, example hashes and CLI reports.
The full audit receipt hash is
`e12f58c1f01a33bcfd312f0533686f6a6216458794ea1ea376b0de4f54bae15a`.
That receipt and its raw logs/JUnit records remain private. The parent checked
the receipt and all 84 referenced artifact hashes; public readers cannot fetch
those private artifacts or independently verify that receipt from this summary.
The audit is **parent/self-verified**, not a fresh independent-actor endorsement.

The existing main CI
[38719897632](https://github.com/UMEBOSHIISAN/knowledge-lifecycle-kit/actions/runs/38719897632)
completed successfully for the exact `411d6b36` source, with 81 component and
9 root tests. The audit reused its checked same-SHA integration receipt; it
did not trigger a new CI or reacquire logs. This run does **not** attest a later
documentation commit. Each such commit needs its own exact-head CI receipt,
saved outside that source commit to avoid changing the candidate being tested.

Different-machine/external-maintainer acceptance, Windows, the full supported
Python matrix, fresh dark/mobile presentation and OS reduced-motion switching
were not verified. No exhaustive history/binary/secret absence, legal rights,
authenticated authorization or complete Writer durability is certified.
Historical confidentiality and advisory-review records remain separately
identified in [the publication audit](../PUBLIC_OSS_CANDIDATE.md).
