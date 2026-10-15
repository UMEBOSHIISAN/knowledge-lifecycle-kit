# Public OSS candidate audit

## Current public-source audit

**APPROVE_SCOPED — source audited 2026-10-15 JST; record updated 2026-10-16.**

- Fixed audited public source: `411d6b3642f359dfbaa4529337e47a842702e4d3`.
- Anonymous main API, clone and fixed-SHA archive agreed on all 61 source files.
- Fresh regular installed-package suite: 81 passed; root suite: 9 passed.
  These are 90 unique tests, comprising 50 existing and 40 Writer regressions.
- A separate fresh editable test install passed the same 81 component cases.
- Writer W1–W6 were verified within the single-writer synchronous-Exception
  scope; no additional required correction was found in that audit.
- Both README displays, the green GIF/PNG, Quickstart and 12 distinct public
  link/image targets were checked. CLI source/example nonmutation was verified.
- [Full scoped summary](docs/verification-411d6b36.md) and
  [sanitized measurements](verification/public-audit-411d6b36.json) distinguish
  public hashes from private parent-verified artifacts and unverified scope.
- Main CI [38719897632](https://github.com/UMEBOSHIISAN/knowledge-lifecycle-kit/actions/runs/38719897632)
  succeeded for `411d6b36`. This is evidence for that source only. A later
  documentation commit requires its own measured exact-head CI receipt,
  kept outside the source commit. This document does not assert that future
  result or grant publication authority.

## Accepted claim

**Inspect Markdown provenance, verification dates, expiry and lifecycle
transitions, and propose changes for human review.**

The read-only surface is `klg inspect`, `klg validate` and
`klg propose-transition`. Provenance checks inspect declared metadata, not
the factual truth of a cited source. A CONFIRMED label and a validation result
do not authenticate a human or grant execution authority.

The exported `KnowledgeTrustWriter` creates and writes local storage. Its
safety, authenticated authorization and durability are outside this claim.
The original README changes distinguishing these surfaces were preserved
byte-for-byte and integrated into the implementation SHA. Relationship and
release guidance use the same boundary.

## Historical preparation evidence

The remainder of this section preserves the earlier packaging/CI, presentation,
confidentiality and advisory-review record. Its implementation is
`96e7edadc770a03afe34cc7dbd95b6eba4c776db`; its environment was reused and its
41+9 test counts, initial private-repository observations and old run inventories
are historical, not the current source or a new audit of the documentation
commit. The initial baseline was `57927750aa85ee7409ef80ffd83e40b6ca8763b7`,
and initially measured private main was
`a8d8a79f11a58316b5a9279e023fa96903ead426`. Publication and logo updates
subsequently occurred under the maintainer's separate instructions.

### Historical implementation verification

A fixed Git archive of the implementation SHA was checked using the existing
Python 3.11.15 / pytest 8.3.5 environment. No dependency was installed and no
external-maintainer or different-machine acceptance is claimed.

| Check | Measured result |
| --- | --- |
| Four-wheel hash verifier | PASS, all declared hashes match |
| KLG suite | 41 passed |
| Actual corrected CI unittest command | 9 passed |
| Public-boundary scanner | PASS, violations=[] under its five text rules |
| Seven deterministic CLI evaluations | Expected reports and exit codes reproduced |
| Five example hashes before/after CLI use | Identical; mutation_performed=false |
| Regular wheel license | Full 1,073-byte component LICENSE included |
| Wheel RECORD | Regression tests bind the license bytes, hash and size |
| Regular/editable builds and prepared metadata | Both kinds covered by two artifact regression tests |
| Source and regular-wheel paths | No absolute or traversal archive members |

The wheel repair adds the full notice to the existing metadata and wheel
builders; it changes no runtime lifecycle behavior. Its tests failed before
the repair (two tests, four failing subtests), then passed. The CI repair
replaces a deleted routing-test reference with actual discovery of the root
contracts and build-artifact tests. The new collection regression fails on
the old workflow and passes on the proposed/current workflow.

Regular wheel SHA-256:
`74f3e54fe842930803fcbb62f1b992c5e39a176407c5e08f61957cf5cb21ab86`.
License path: `knowledge_lifecycle_gate-0.1.0.dist-info/LICENSE`.
Notice SHA-256:
`7d16cd34611446171445cff3a3ac28aa80c374e2ce52cf161bb95c1061145551`.

### Lifecycle behavior

| Case | Result |
| --- | --- |
| Confirmed Evidence on 2026-10-15 | Valid and FRESH |
| Expiry date, 2099-01-01 | FRESH |
| Next day, 2099-01-02 | EXPIRED; STALE_PROPOSED; human_confirmation_required=true |
| Already expired Evidence | Same human-facing stale proposal |
| NEW to CONFIRMED request | Rejected, direct_promotion, exit 1, no proposal |
| Missing lineage after admission | Rejected, exit 1 |
| Missing/future verification date | Invalid |
| Missing/invalid/conflicting expiry | Invalid |
| valid_until alternative | Accepted |
| Proposal state and source | Original state retained; no source rewrite or recorded transition |

Expired evidence may still be structurally valid. Inspect validity and
freshness separately; FRESH does not override validation errors. The date
metadata checks from the initial review remain bound to unchanged validator
bytes; the seven CLI cases were rerun at the implementation SHA.

### Confidentiality, assets, rights and links

The maintainer subsequently requested four public-presentation corrections:
onboarding commands, CLI/writer contributor wording, the logo, and repository
About metadata. The original README bytes were preserved through `be74b8ca`;
the scoped presentation updates now revise those documents while retaining
the same runtime, tests, build backend, workflow, and claim boundary.
The maintainer subsequently selected a simpler green whale as the formal logo
and explicitly requested its publication. It has orbiting books in a 192-pixel
README display and a matching static PNG companion. This asset/documentation
update preserves the runtime, tests, build backend, workflow, and claim.
Its separate creation/publication basis and current exact hashes are
recorded in [asset rights](docs/asset-rights.md). Earlier inventory counts below
describe the original audit scope, not these later added files.

The initial reachable-history review covered four local refs, 14 commits,
173 objects, 96 blobs (94 UTF-8 text blobs plus two PNGs), and commit messages.
Recorded credential/private-path/private-link patterns had no matches.
Git identity used a GitHub noreply address. The new candidate receives its own
delta/history and boundary check before any authorized push; the initial
counts are not a final-candidate coverage claim.

The fixed candidate contains the generic KLG SVG and PNG. Both asset hashes
match the original transfer bundle. The maintainer directly declared that
these are their own created/generated works, contain no third-party material
or protected UMEBOSHI IP, and may be published under MIT.
[The file-specific rights record](docs/asset-rights.md) preserves the exact
statement and hashes. Permission is rightsholder-declared, not independently
certified legal exclusivity. The separate historical social-preview PNG is
outside this grant and this candidate.

The SVG parsed without script/image/foreignObject elements. The KLG PNG's
24,910-byte caBX chunk and the historical PNG's 56-byte eXIf chunk were
inspected for the recorded sensitive patterns with no match; cryptographic
provenance verification was unavailable. Root/component MIT files are identical.
Regular distribution wheels now carry the full notice; editable wheels are
local development artifacts and are not publication assets.

The real linked repository, UMEBOSHIISAN/mothership, was measured public.
example.invalid schema URLs in history are synthetic fixtures.
No raw Actions logs, private task evidence or approval tokens are included in
the candidate.

### Actions review and external evidence

Read-only observations used measured UMEBOSHIISAN credentials. Actions were
enabled, all actions allowed, SHA pinning not required; default workflow
permissions were read and PR-review approval was disabled. The workflow's
contents: read permission, checkout@v4/setup-python@v5, Python 3.11 and pytest
8.3.5 remain unchanged by the approved correction. It contains no secret
reference, publish or deploy step. The transitive test dependency versions in
remote CI are not fully locked.

The three obtainable old log archives (runs 31494119094, 31494122117 and
32441327613), six text members total, were hashed and scanned with no match
under the recorded sensitive-content patterns. Artifacts/tags/releases were
empty at that inspection; deleted items are not thereby excluded.
No August run is current acceptance.

A bounded tools-disabled design/code review by registered claude-design-mba
returned ACCEPT_SCOPED for the supplied CI and license patch. It was advisory
only, performed no local execution and granted no authority. The parent
executed the tests and resolved its checks about the component LICENSE,
local-only test discovery and the absent sdist builder. The human separately
provided the protected CI edit/execution tokens.

### Evidence and limits

Private full records remain under task `20261015_klg_public_review`.
Implementation verification record SHA-256:
`9a3cedde846cfefb4f612df85c93c6d2c4fad40ed675b9c149457f42d9ada56c`.
The initial audit and all failed checks remain preserved; the repaired results
do not erase them. Final delivery identity, exact-head CI outcome and source
equivalence are recorded separately after the documentation envelope is fixed.

Unreachable/deleted Git objects, server-hidden refs, deleted/unobtainable logs,
exhaustive binary steganography, independently verified image exclusivity,
full writer security/durability and another person's machine are not certified.
No sdist builder or sdist release is claimed. Pattern checks cannot prove
absence of every secret.

See [RELEASE_READINESS.md](RELEASE_READINESS.md).
