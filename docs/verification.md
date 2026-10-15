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

At implementation SHA `96e7edadc770a03afe34cc7dbd95b6eba4c776db`,
the fixed archive passed 41 KLG tests, 9 root tests, four wheel hashes and the
scanner. Seven CLI reports were reproduced and all five example hashes were
unchanged. A regular wheel contained the full 1,073-byte notice; both build
kinds and metadata preparation are covered by actual artifact tests.

The existing Python 3.11.15 / pytest 8.3.5 environment was reused; this was not
another-machine acceptance. A final documentation envelope requires its own
source binding and exact-head CI receipt. No old CI is substituted.

The scanner checks enumerated text patterns, not all Git history, binary
provenance or legal rights. Review those separately.
`.wheelhouse/`, `.verify-venv/`, local editable wheels and raw audit logs are
not publication artifacts. See [readiness](../RELEASE_READINESS.md).
