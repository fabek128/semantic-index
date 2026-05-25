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
| `v0.5.0-pre-alpha: MVP hardening and release readiness` | Complete | CLI error hardening, packaging validation, and security baseline. |
| `v0.6.0-pre-alpha: Index metadata and lifecycle` | Complete | Index manifest, compatibility validation, and safe overwrite behavior. |
| `v0.7.0-pre-alpha: Retrieval quality and agent context controls` | Complete | Prefix policy alignment and bounded output controls. |

## Current recommendation

The next milestone should be:

```text
v0.8.0-pre-alpha: Pre-alpha release readiness
```

Do **not** jump directly to FAISS, APIs, databases, web UI, or advanced indexing.

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
