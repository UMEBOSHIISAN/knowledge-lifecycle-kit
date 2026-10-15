# Security policy

The accepted inspection surface is klg inspect, klg validate and
klg propose-transition. These commands inspect Markdown metadata and propose
human-reviewed changes without rewriting the source. They do not authenticate
human approval, prove a source true or grant execution authority.

The package also exports KnowledgeTrustWriter. Constructing it initializes
local storage; commit, rollback and redact methods write local files. Its
caller must authorize the target and operation separately. An approval-token
string or a validation result is not human authentication. This writer must
not be described as covered by the CLI's read-only guarantee.

This public candidate must not receive credentials, private knowledge bodies,
customer data, model outputs or live approval ledgers. Do not open a public
issue containing a secret or private asset. Use the private report channel
supplied by the maintainer and a minimal reproduction without sensitive data.

No network listener, external API client, scheduler or daemon is included in
the inspected fixed source. These exclusions do not mean every exported API
is nonmutating. See the [publication audit](../PUBLIC_OSS_CANDIDATE.md) for its
specific checks, known holds and unverified scope.
