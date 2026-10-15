# Public Release Readiness

**Local preparation verified — 2026-10-15 JST.**
Remote acceptance is a per-candidate check, followed by a separate human
publication decision. Neither is inferred from old CI or this label.

## Scope and identity

Claim: inspect Markdown provenance, verification dates, expiry and lifecycle
transitions, and propose changes for human review.

- Implementation SHA: `96e7edadc770a03afe34cc7dbd95b6eba4c776db`.
- Final documentation-envelope SHA: recorded from Git after this record is
  committed, together with its matching CI receipt in the existing task result.
- Original README bytes were preserved through `be74b8ca`; the maintainer then
  requested scoped onboarding and logo updates. The CLI/writer claim is retained.
- Root/component MIT files are identical.
- The three klg commands are read-only; the exported local writer is outside
  that claim.
- Repository was observed private; measured remote main before repair was
  `a8d8a79f11a58316b5a9279e023fa96903ead426`.

## Measured local acceptance

- [x] Exact implementation SHA, archive and test environment recorded.
- [x] Four expected wheel hashes verified.
- [x] KLG suite: 41 passed.
- [x] Corrected actual CI unittest command: 9 passed.
- [x] Public-boundary scanner: violations=[] under its specified rules.
- [x] Expiry boundary, expired proposal, forbidden promotion and source
  nonmutation reproduced with explicit as-of dates.
- [x] Missing/future verification dates and missing/invalid/conflicting expiry
  checked; unchanged validator bytes bound to those records.
- [x] Full LICENSE included in regular/editable wheels and prepared metadata;
  artifact regression tests verify actual bytes and RECORD binding.
- [x] Source/regular-wheel archive paths inspected.
- [x] README onboarding corrected at the maintainer's request; CLI/writer
  boundaries retained and contributor guidance aligned.
- [x] Legacy SVG/PNG permission and new whale/moon GIF/PNG provenance recorded.
- [x] Bounded independent advisory design/code review received and parent
  verification performed; review grants no execution authority.
- [x] Human's exact protected CI approval received before application.

Test-wheel inputs (verification/test-wheelhouse.json):

| Wheel | SHA-256 |
| --- | --- |
| iniconfig-2.3.0-py3-none-any.whl | `f631c04d2c48c52b84d0d0549c99ff3859c98df65b3101406327ecc7d53fbf12` |
| packaging-26.3-py3-none-any.whl | `d7193f7c8e4e93f444fde0262bf90af30e16fa0ad0ad44cb553c87339b23cd1c` |
| pluggy-1.6.0-py3-none-any.whl | `e920276dd6813095e9377c0bc5566d94c932c33b27a3e3945d8389c374dd4746` |
| pytest-8.3.5-py3-none-any.whl | `c69214aa47deac29fad6c2a4f590b9c4a9fdb16a403176fe154b79c0b4d4d820` |

Regular wheel SHA-256:
`74f3e54fe842930803fcbb62f1b992c5e39a176407c5e08f61957cf5cb21ab86`.
Full notice: 1,073 bytes,
`7d16cd34611446171445cff3a3ac28aa80c374e2ce52cf161bb95c1061145551`.

## Exact-candidate remote gate

Before publication, the release operator must measure:

1. Authenticated writer and destination branch; preserve shared account settings.
2. Candidate commit SHA on the remote branch, equal to the selected local SHA.
3. A completed successful CI run whose head SHA equals that exact candidate.
4. The current candidate's history/assets/boundary checks and full receipt.

Keep this receipt outside the source commit so adding the receipt does not
silently produce another untested candidate SHA. The receipt must identify
this record's source revision and any documentation-only envelope explicitly.
A pass on the implementation SHA, an August run, or a different branch/head
does not satisfy this gate.

The initial remote audit found three old runs only, all for the old main SHA;
their three archives/six text members were inspected. They are retained as
confidentiality evidence, not release acceptance. Current per-candidate CI is
measured independently after an authorized private-branch push.

## Rights, limitations and human decision

The legacy two-logo permission and the new whale/moon GIF/PNG creation and
publication basis are separated in [asset rights](docs/asset-rights.md).
Neither is independent legal certification or a grant over UMEBOSHI brand IP.

Reachable-history pattern checks and obtainable logs were inspected, with
unavailable/deleted/hidden history and exhaustive binary/rights guarantees
explicitly unverified. No external-maintainer or different-machine acceptance,
sdist release, authenticated writer approval or full writer durability is claimed.

A private CI push, public visibility change, tag and registry upload remain
separate consequential actions. This record grants none of them. Publication
requires the human's decision for the exact reviewed final target.

Detailed evidence: [PUBLIC_OSS_CANDIDATE.md](PUBLIC_OSS_CANDIDATE.md).
