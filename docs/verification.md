# Local verification

Knowledge Lifecycle Kit keeps runtime behavior dependency-free. Pytest and its
transitive dependencies are test-only inputs stored in a local, hash-pinned
wheelhouse. The wheel binaries are ignored and must be acquired separately
under an explicit human network/download approval.

Run the following commands from the repository root after the reviewed
wheelhouse has been populated:

```sh
PYTHONPATH=. python3.11 tools/verify_test_wheelhouse.py verification/test-wheelhouse.json .wheelhouse
python3.11 -m venv .verify-venv
.verify-venv/bin/python -m pip install --no-index --find-links .wheelhouse pytest==8.3.5
.verify-venv/bin/python -m pip install --no-index --no-deps ./knowledge-lifecycle-gate
(cd knowledge-lifecycle-gate && ../.verify-venv/bin/python -m pytest -q tests)
PYTHONPATH=. python3.11 -m unittest -v tests/test_routing.py tests/test_public_layout.py tests/test_verify_test_wheelhouse.py tests/test_public_boundary.py
PYTHONPATH=. python3.11 tools/check_public_boundary.py .
```

The wheelhouse verifier fails before installation when any expected wheel is
missing or its SHA-256 does not match. The final scanner emits deterministic
JSON and fails when it finds private-path or credential-shaped text.

`.wheelhouse/` and `.verify-venv/` are disposable local verification artifacts.
Do not commit them.
