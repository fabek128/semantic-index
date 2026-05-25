# Roadmap

Current stage: **pre-alpha**.

The project already has the first end-to-end local MVP shape: Markdown discovery, chunking, local embedding index persistence, and semantic search through the CLI.

## Completed phases

| Milestone | Status | Summary |
| --- | --- | --- |
| `v0.1.0-pre-alpha: Foundation and test baseline` | Complete | Python CLI scaffold and baseline unit tests. |
| `v0.2.0-pre-alpha: Markdown input pipeline` | Complete | Safe Markdown discovery and deterministic Markdown chunking. |
| `v0.3.0-pre-alpha: Local embedding index` | Complete | Local embedding index build with `docs.jsonl` + `index.npz`. |
| `v0.4.0-pre-alpha: Search and agent retrieval MVP` | Complete | Local semantic search with `text`, `json`, and `jsonl` output. |
| `v0.5.0-pre-alpha: MVP hardening and release readiness` | Complete | CLI error hardening, packaging validation, test discovery fix, and docs alignment. |
| `v0.6.0-pre-alpha: Index metadata and lifecycle` | Complete | Index manifest, compatibility validation, and safe overwrite behavior. |
| `v0.7.0-pre-alpha: Retrieval quality and agent context controls` | Complete | Prefix policy alignment and bounded output controls. |
| `v0.8.0-pre-alpha: Pre-alpha release readiness` | Complete | Versioning policy, changelog, release checklist, and security review checklist. |
| `v0.9.0-pre-alpha: Quality automation and docs correctness` | Complete | CI, test warnings cleanup, docs fixes, pickle safety, and consistency validation. |
| `v0.10.0-pre-alpha: Privacy, offline mode, and configuration` | Complete | Relative paths, offline/cache docs, --max-chars and --model CLI options. |

## Current recommendation

The next milestone should be:

```text
v0.11.0-pre-alpha: Retrieval quality evaluation and hybrid search
```

This milestone adds local lexical search, a hybrid ranking mode, and deterministic retrieval fixtures.

Issues: #35, #36, #37

Goal: improve technical-note retrieval quality without adding a database or external service.

Focus:

- add local lexical search for exact identifiers and terms;
- combine lexical and semantic signals in a simple hybrid mode;
- add small deterministic retrieval fixtures and golden tests.

Known limitations captured in this milestone:

- semantic search alone is weak for exact identifiers, filenames, symbols, and error codes;
- ranking changes need deterministic fixtures before hybrid retrieval grows;
- retrieval improvements must preserve the CLI-first, local-only, database-free architecture.

Non-goals:

- no SQLite/FTS database;
- no FAISS/ANN engine;
- no external benchmark dataset;
- no network dependency.

## Issue policy

Every issue in these phases must include:

- detailed context;
- explicit scope and non-goals;
- acceptance criteria;
- security/privacy notes when relevant;
- documentation requirements;
- unit-test requirements for implementation or bug-fix work.

Every issue must be assigned to:

- repository: `fabek128/semantic-index`;
- project: `semantic-index Roadmap`;
- one roadmap milestone.
