# Advisory LLM routing

This component recommends a worker alias from a synthetic/local registry and
validates evidence-linked scorecards. It is deliberately advisory-only:

- `recommended_alias` is router output;
- `selected_alias` belongs to a human/orchestrator;
- `actual_alias` belongs to measured execution evidence;
- the router does not execute commands or models.

Run the root test for deterministic routing and scorecard behavior.
