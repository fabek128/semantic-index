# Roadmap

Current stage: **alpha** (v0.12.0a1).

The project has a published first alpha release and a complete end-to-end local CLI: Markdown discovery, chunking, local embedding index persistence, semantic search, lexical search, hybrid ranking, JSON/JSONL output, CI, and safety checks for local index files.

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
| `v0.10.0-pre-alpha: Privacy, offline mode, and configuration` | Complete | Relative paths, offline/cache docs, `--max-chars`, and `--model` CLI options. |
| `v0.11.0-pre-alpha: Retrieval quality evaluation and hybrid search` | Complete | Lexical search, hybrid ranking, and deterministic retrieval fixtures. |
| `v0.12.0-alpha-candidate: Executable package and alpha readiness` | Complete | Regression fix, docs alignment, artifact validation, version/changelog, and alpha smoke flow. |
| `v0.12.0-alpha.1: First alpha release` | Complete | Final release docs, tag `v0.12.0-alpha.1`, and GitHub prerelease publication. |

## Current phase

```text
v0.12.0-beta.1: Beta hardening and distribution
```

The alpha release is published. The beta phase should harden distribution, repeatability, platform coverage, output contracts, dependency policy, realistic corpus validation, and troubleshooting before publishing the first beta prerelease.

Recommended execution order:

1. #58 — archive alpha release evidence and switch docs to beta phase.
2. #59 — make the release smoke test reproducible for beta.
3. #60 — build and validate wheel/sdist artifacts.
4. #61 — expand CI and document supported platforms.
5. #62 — document and test the beta CLI/output contract.
6. #63 — define dependency version policy.
7. #64 — add realistic synthetic corpus validation.
8. #65 — add beta troubleshooting guide.
9. #66 — prepare and publish `v0.12.0-beta.1`.

## Open phase

### v0.12.0-beta.1: Beta hardening and distribution

Issues: #58, #59, #60, #61, #62, #63, #64, #65, #66

Goal: make `semantic-index` beta-ready without changing the local-only, database-free architecture.

Focus:

- preserve alpha release evidence and align docs/specs for beta;
- make the smoke test reproducible and safe for agents/humans;
- validate wheel/sdist artifact installation outside the source tree;
- expand CI or explicitly document platform support limits;
- document CLI flags, exit codes, and JSON/JSONL output contract;
- define dependency version policy for `fastembed`, `numpy`, and supported Python versions;
- validate behavior with a larger synthetic Markdown corpus;
- provide troubleshooting guidance for model cache, offline mode, permissions, corrupt indexes, and search modes;
- prepare the `0.12.0b1` / `v0.12.0-beta.1` prerelease.

Non-goals:

- no PyPI publishing unless explicitly requested;
- no API or web server;
- no database;
- no FAISS/ANN acceleration;
- no Docker image or standalone binary unless separately scoped.

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
