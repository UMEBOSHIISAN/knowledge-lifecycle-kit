# Release preparation

Local repairs and verification are recorded in
[RELEASE_READINESS.md](RELEASE_READINESS.md). Publication remains human-owned.

1. Fix the intended candidate SHA and inspect its exact archive.
2. Run [verification](docs/verification.md), record commands/versions/hashes/
   exit codes, and follow the component evaluation protocol.
3. Review reachable history, assets, notices, private links, Actions settings
   and obtainable logs; record unavailable scope. Review the
   [file-specific artwork permission](docs/asset-rights.md).
4. The CI routing-test reference and wheel notice omission are repaired.
   The real CI command must execute successfully for the selected final SHA;
   local discovery or old remote success does not substitute.
5. Record final source identity and its exact-head CI result outside the
   source commit, with any documentation-only envelope explicitly bound.
6. Obtain the separate human decision before private-branch push, tag,
   registry upload or visibility change, under the applicable action scope.

The accepted surface is the three read-only klg commands. The exported local
writer is outside that claim. This preparation does not add an execution
authority, scheduler, provider adapter or deployment system.
