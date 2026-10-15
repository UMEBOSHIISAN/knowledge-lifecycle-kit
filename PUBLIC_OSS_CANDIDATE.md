# Public OSS candidate audit

## Fixed-source result

**LOCAL_PREPARATION_VERIFIED — 2026-10-15 JST.**
Publication still requires a separate human decision and passing remote CI for
the exact selected candidate. This document is not publication authority.

- Audited implementation SHA: `96e7edadc770a03afe34cc7dbd95b6eba4c776db`.
- Earlier baseline: `57927750aa85ee7409ef80ffd83e40b6ca8763b7`.
- The final documentation-envelope SHA and its own remote CI evidence are
  measured separately in the task's immutable per-candidate receipt. A document
  cannot contain its own future Git commit hash. Do not reuse a run for the
  implementation SHA as proof of a different envelope SHA.
- Remote main measured during the initial review:
  `a8d8a79f11a58316b5a9279e023fa96903ead426`, repository private.
  August successes remain historical only.

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

## Fresh implementation verification

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

## Lifecycle behavior

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

## Confidentiality, assets, rights and links

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

## Actions review and external evidence

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

## Evidence and limits

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
