# Changelog

## Unreleased

- Reports now include a `content_digest` (`sha256:<lowercase hex>`) binding
  each report to the exact validated file bytes; file commands accept
  `--expect-digest` and fail closed on a mismatch.
- Added a read-only `scan` command that validates every Markdown note under
  a directory and reports per-file results with a summary.

## 0.1.0 — candidate preview

- Added strict Markdown YAML-frontmatter parsing.
- Added public asset-type, lifecycle-state, lineage, freshness, and expiry
  validation.
- Added read-only `inspect`, `validate`, and `propose-transition` commands.
- Added human-readable and JSON reports with `*_PROPOSED` transitions only.
- Added synthetic examples, schema, fail-closed tests, no-network tests, and
  read-only tests.
- Added OSS preparation metadata and a vector/raster logo mark.

This preview has not been published or pushed.
