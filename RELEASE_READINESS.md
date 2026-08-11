# Public Release Readiness

Complete this record from measured evidence before requesting a public release.
This repository has no remote publication authority by itself.

## Local verification

- [ ] Date and operator recorded.
- [ ] `tools/verify_test_wheelhouse.py` exit status and output recorded.
- [ ] Every test-wheel filename and SHA-256 recorded from `verification/test-wheelhouse.json`.
- [ ] KLG pytest command and result recorded.
- [ ] Routing and public-contract unittest command and result recorded.
- [ ] Public-boundary scanner JSON result recorded.

## Remote verification

- [ ] Remote repository URL recorded.
- [ ] Exact remote branch name and commit SHA recorded.
- [ ] CI run URL and passing result recorded.

## Human authority

- [ ] Separate `DEPLOY_APPROVED:<target>` authority is present in the conversation.

Do not create a remote, push, tag, or publish until every applicable item above
has measured evidence and the separate authority is present.
