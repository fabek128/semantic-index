# Changelog

All notable changes to `semantic-index` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
for its `0.x` pre-alpha releases (see [Versioning policy](README.md#versioning-policy)).

## [0.12.0a1] — 2026-05-25

### Added

- Lexical search mode (`--mode lexical`) — local term-frequency matching
  over chunk text, heading, and title. No embedding model required.
- Hybrid search mode (`--mode hybrid`) — weighted combination of semantic
  (cosine) and lexical scores via `--semantic-weight` (default 0.5).
- `semantic-index/lexical.py`: new module providing `score_query` and
  `search_index` for database-free lexical retrieval.
- `--max-chars` option to `semantic-index build` for configurable chunk
  size (default 1800).
- `--model` option to `semantic-index build` for custom embedding models.
- Chunk paths stored relative to the discovery root by default, reducing
  absolute path leakage in index metadata.
- Offline/cache documentation: model download behavior, cache location
  (`~/.cache/fastembed/`), and pre-cache workflow for fully offline use.
- GitHub Actions CI workflow (two Python versions, tests, compile check,
  CLI smoke tests).
- Stronger index consistency validation: ndim/dtype checks, manifest
  `chunk_count` cross-validation, and actionable rebuild hints.
- Explicit `allow_pickle=False` in `np.load()` for pickle-safe index
  loading.

### Changed

- Package version set to `0.12.0a1` (first alpha candidate).
- `handle_search` in `cli.py` dispatches by `--mode`; lexical mode skips
  embedder creation.
- Source directory (`source_dirs` in manifest) uses paths relative to
  the indexed root.

### Fixed

- `test_partial_term_match`: corrected test expectation to match
  case-insensitive tokenization behavior.
- README formatting: security checklist item placement, project tree
  includes `lexical.py` and `test_lexical.py`.
- `docs/architecture.md`: malformed numbering in build responsibilities.

## [0.1.0] — Unreleased
