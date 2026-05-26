# Changelog

All notable changes to `semantic-index` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
for its `0.x` pre-alpha releases (see [Versioning policy](README.md#versioning-policy)).

## [0.13.0b1] — 2026-05-26

### Added

- Dogfood validation report (`docs/dogfood-report.md`) with sanitized
  metrics on a realistic corpus (11 files, 110 chunks, no RC blockers).
- Scale and performance baseline (`docs/corpus-validation.md`) with
  `--scale` flag for the corpus generator, covering small (22 files)
  and medium (106 files) corpus sizes.
- AI-agent integration guide (`docs/agent-integration.md`) with workflow
  patterns, output parsing examples, and security checklist.
- Beta privacy and security review (`docs/security-review.md`) — no
  blockers found.
- RC readiness criteria (`docs/rc-criteria.md`) with checklist for
  declaring a release candidate.
- CLI UX polish: build/search help text documents model download and
  search modes; empty directory returns exit code 1 with actionable
  message.

### Changed

- Package version bumped to `0.13.0b1` (dogfood and RC readiness beta).
- README restructured with agent integration and troubleshooting links.

## [0.12.0b1] — 2026-05-26

### Added

- Release smoke test script (`scripts/release-smoke.sh`) for repeatable
  end-to-end validation in a clean environment.
- Synthetic Markdown corpus generator (`scripts/generate-corpus.py`)
  with nested directories, Unicode, long sections, and code identifiers.
- Dependency version policy (`docs/dependency-policy.md`) with tested
  ranges for `fastembed>=0.5.0,<1.0.0` and `numpy>=1.26.0,<3.0.0`.
- Output format contract (`docs/cli-contract.md`) — commands, flags,
  defaults, exit codes, JSON/JSONL schemas per search mode.
- Beta troubleshooting guide (`docs/troubleshooting.md`).
- Platform support documentation (`docs/platforms.md`).
- Artifact build and validation documentation (`docs/artifact-build.md`).
- Alpha smoke-test evidence archived at
  `docs/releases/0.12.0a1/release-smoke-test.md`.
- Golden tests for JSON/JSONL output shape in all three search modes.

### Changed

- Package version bumped to `0.12.0b1` (first beta prerelease).
- CI expanded: added `macos-latest` runner (Python 3.13).
- Dependency bounds added: `fastembed<1.0.0`, `numpy<3.0.0`.
- Documentation status updated from alpha to beta phase.

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
