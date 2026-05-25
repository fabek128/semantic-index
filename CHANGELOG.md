# Changelog

All notable changes to `semantic-index` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
for its `0.x` pre-alpha releases (see [Versioning policy](README.md#versioning-policy)).

## [0.1.0] — Unreleased

### Added

- CLI scaffold with `--help`, `version`, `build`, and `search` commands.
- Markdown file discovery with path validation, excluded directories,
  and symlink safety.
- Deterministic Markdown chunking by ATX headings with configurable
  chunk size, metadata-rich output, and stable chunk IDs.
- Embedding generation with `fastembed` (default model:
  `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`).
- Index persistence as `docs.jsonl` + `index.npz` (no `pickle`).
- Local semantic search with ranked results and agent-friendly
  output formats: `text`, `json`, `jsonl`.
- Index manifest (`manifest.json`) with model name, dimensions,
  chunk count, schema version, and creation timestamp.
- Search-time compatibility validation (schema version, embedding
  dimensions, embedder dimensions).
- Atomic index writes via temp subdirectory + rename, with
  automatic cleanup on failure.
- Overwrite detection with explicit CLI message and list of
  overwritten files.
- `--max-chars` flag for bounded text output in all formats.
- Clear CLI error messages (no stack traces for user errors).
- Nested unreadable directory handling (silently skipped).
- Corrupt/malformed index detection with actionable error messages.
- Clean smoke-test checklist for development environments.
- JSON/JSONL output schema documentation.
- Changelog and versioning policy.
- Security/privacy review checklist.

### Changed

- Default query prefix changed from `"query: "` to `""` (empty),
  aligning with the default model which does not benefit from
  E5-style prefixes.
- `docs/spec.md` updated: default model recommendation, prefix
  policy section, and prefix-free code examples.

### Fixed

- Unit test discovery from clean checkout (no editable install).
- Stale documentation aligned with implementation.
