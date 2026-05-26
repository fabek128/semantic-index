# Roadmap

Current stage: **alpha** (v0.12.0a1).

The project has a complete end-to-end local CLI: Markdown discovery, chunking, local embedding index persistence, semantic search, lexical search, hybrid ranking, JSON/JSONL output, CI, and safety checks for local index files.

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

## Current phase

```text
v0.12.0-alpha.1: First alpha release
```

The alpha-candidate milestone is complete and `main` CI is green. The remaining release operations are:

1. #54 — Finalize alpha release docs and agent specs.
2. #55 — Run preflight, create annotated tag `v0.12.0-alpha.1`.
3. #56 — Publish GitHub prerelease with release notes.

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
