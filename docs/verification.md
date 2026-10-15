# Local verification

Runtime inspection/proposal commands use the standard library. Test-only wheels
are hash-pinned; acquiring missing wheels requires the existing human
network/download authority.

With a reviewed wheelhouse already populated, from the repository root:

```sh
PYTHONPATH=. python3.11 tools/verify_test_wheelhouse.py verification/test-wheelhouse.json .wheelhouse
python3.11 -m venv .verify-venv
.verify-venv/bin/python -m pip install --no-index --find-links .wheelhouse pytest==8.3.5
.verify-venv/bin/python -m pip install --no-index --no-deps ./knowledge-lifecycle-gate
(cd knowledge-lifecycle-gate && ../.verify-venv/bin/python -B -m pytest -p no:cacheprovider -q tests)
PYTHONPATH=. .verify-venv/bin/python -B -m unittest discover -s tests -v
PYTHONPATH=. .verify-venv/bin/python -B tools/check_public_boundary.py .
```

The CI uses the same root discovery command. It replaces the deleted routing
test reference and includes the artifact-license regressions. The collection
regression uses the real unittest loader; CI must still execute the collected
tests. It intentionally supports the documented current command form.

Follow the existing [component evaluation protocol](../knowledge-lifecycle-gate/EVALUATION.md)
with explicit as-of dates. Record expected exit 1 for invalid inputs, proposal
fields and before/after hashes. Expiry day is inclusive; the next day is
EXPIRED. Inspect validity and freshness separately.

## Recorded public-source verification

The 2026-10-15 audit of
`411d6b3642f359dfbaa4529337e47a842702e4d3` passed 81 component tests and
9 root tests: 50 existing tests plus 40 Writer regressions, 90 unique cases.
The component suite exercised a regular distribution in a fresh environment,
with the checkout-src injection omitted. A separate fresh editable test install
also passed the same 81 component tests. All eight installed module hashes,
four test-wheel hashes, five unchanged examples and the full 1,073-byte wheel
notice were checked.

The [fixed-source audit](verification-411d6b36.md) records W1–W6, CLI results,
README/asset/link checks and limits. Its
[sanitized summary](../verification/public-audit-411d6b36.json) separates public
source hashes from private parent-verified logs. These were same-host fresh
Python 3.11.15 / pytest 8.3.5 environments, not another-machine acceptance.

The earlier `96e7edad` packaging/CI repair passed 41 component and 9 root tests
using the existing environment; that is historical evidence. CI run
[38719897632](https://github.com/UMEBOSHIISAN/knowledge-lifecycle-kit/actions/runs/38719897632)
belongs to `411d6b36`. A later documentation envelope requires its own source
binding and exact-head CI receipt; the older run cannot satisfy that check.

The scanner checks enumerated text patterns, not all Git history, binary
provenance or legal rights. Review those separately.
`.wheelhouse/`, `.verify-venv/`, local editable wheels and raw audit logs are
not publication artifacts. See [readiness](../RELEASE_READINESS.md).
