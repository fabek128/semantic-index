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

## Current recommendation

The next milestone should be:

```text
v0.5.0-pre-alpha: MVP hardening and release readiness
```

Do **not** jump directly to FAISS, APIs, databases, web UI, or advanced indexing. The current code should first be hardened, documented, and made easier to validate in clean environments.

## Known corrections discovered after v0.4

These should be tracked before expanding feature scope:

1. Some docs still describe older scaffold behavior or future-only persistence even though build/search are implemented.
2. The embedding model and prefix strategy need a clear decision. The original spec recommended E5-style `query:` / `passage:` prefixes, but the implemented default model is `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, which does not have the same E5 prefix contract.
3. Index files do not yet include a manifest with schema version, model name, embedding dimensions, chunking parameters, or creation metadata.
4. Some discovery/read error behavior should be made more explicit and consistently tested, especially nested unreadable directories and malformed/corrupt index files.
5. The release workflow is not yet documented as a repeatable pre-alpha checklist.

## Planned phases

### v0.5.0-pre-alpha: MVP hardening and release readiness

Issues: #12, #13, #14, #20

Goal: make the current MVP safer, more consistent, and easier to validate.

Focus:

- documentation consistency;
- CLI error handling;
- corrupt/missing index validation;
- nested permission/error handling;
- clean-environment packaging checks;
- release checklist for the current local-only CLI.

Non-goals:

- no FAISS;
- no database;
- no API/web server;
- no incremental indexing yet.

### v0.6.0-pre-alpha: Index metadata and lifecycle

Issues: #15, #16

Goal: make generated indexes self-describing and safer to rebuild/search later.

Focus:

- `manifest.json` or equivalent metadata;
- schema version;
- embedding model name;
- embedding dimensions;
- chunking configuration;
- creation timestamp and source summary;
- search-time compatibility validation;
- safe overwrite/rebuild behavior.

Non-goals:

- no index merge;
- no background watcher;
- no database.

### v0.7.0-pre-alpha: Retrieval quality and agent context controls

Issues: #17, #18

Goal: improve result usefulness without changing the local-only architecture.

Focus:

- resolve embedding model/prefix policy;
- stable result schemas for agents;
- output limits and snippet controls;
- optional context block formatting;
- preparation for future lexical/hybrid search decisions.

Non-goals:

- no ANN engine;
- no BM25 implementation unless explicitly scoped in a later issue;
- no external service.

### v0.8.0-pre-alpha: Pre-alpha release readiness

Issues: #19

Goal: prepare the project for a tagged pre-alpha release.

Focus:

- versioning policy;
- changelog;
- clean install verification;
- local smoke-test script or documented checklist;
- packaging metadata review;
- security/privacy review for generated indexes.

Non-goals:

- no public hosting;
- no online service;
- no production deployment.

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
