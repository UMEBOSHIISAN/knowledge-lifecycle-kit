# Evaluation protocol

This package is a clean-machine simulation artifact. It has not been run on another person's machine by this session.

## Acceptance checks

1. Create a fresh virtual environment.
2. Run `pip install -e .` from the handoff directory.
3. Run the available `pytest` command and record whether it is venv-local or host-provided.
4. Validate the valid Evidence example.
5. Propose a stale transition for the expired Evidence example.
6. Validate the missing-lineage and direct-promotion examples.
7. Compare SHA-256 values of all examples before and after the commands.
8. Capture stdout and confirm that it contains no user-specific absolute path.
9. Run the no-network regression test through the controlled test environment.

## Expected policy

- Machine inspection and validation are allowed.
- Machine output may contain `*_PROPOSED` only.
- Human confirmation is required for a recorded transition.
- `NEW -> CONFIRMED` is rejected.
- Missing lineage is a warning for `NEW` and an error after admission.
- Confirmed Evidence requires `last_verified` and `next_review` or `valid_until`.
- An Evidence item is expired only when the validation date is later than its expiration date.
- `RETIRED` is terminal in this public profile.

## Installation note

The runtime package has no third-party dependency. The test extra installs pytest. If the evaluator forbids network access during installation, provide a separately reviewed local wheelhouse or install the test runner through the evaluator's controlled dependency process. Runtime tests themselves assert that no network connection is opened.

## Out of scope

No source-asset rewrite, event log append, human approval simulation, deletion, retirement action, scheduler, daemon, host integration, secret access, external API, LLM call, publication, or remote push is part of this evaluation.
