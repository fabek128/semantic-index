# Roadmap

Current stage: **beta** (v0.12.0b1).

The project has published alpha and beta prereleases and a complete end-to-end local CLI: Markdown discovery, chunking, local embedding index persistence, semantic search, lexical search, hybrid ranking, JSON/JSONL output, CI, and safety checks for local index files.

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
| `v0.12.0-beta.1: Beta hardening and distribution` | Complete | Reproducible smoke tests, artifact validation, platform docs/CI, dependency policy, corpus validation, troubleshooting, and beta prerelease. |

## Current phase

```text
v0.13.0-beta.1: Dogfood, fixes, and RC readiness
```

The beta release is published. The next phase is dogfooding against realistic notes, fixing beta blockers, hardening AI-agent workflows, and deciding whether the next prerelease should be another beta or the first release candidate.

Recommended execution order:

1. #76 — run real-notes dogfood validation with a sanitized report.
2. #77 — establish beta scale and performance baseline.
3. #78 — document AI-agent integration workflows for beta.
4. #79 — perform beta privacy and security review before RC.
5. #80 — triage and implement beta CLI UX polish.
6. #81 — define RC readiness criteria and next version target.
7. #82 — prepare and publish the next beta or first RC prerelease.

## Open phase

### v0.13.0-beta.1: Dogfood, fixes, and RC readiness

Issues: #76, #77, #78, #79, #80, #81, #82

Goal: validate `semantic-index` in realistic local workflows and reduce risk before a release candidate.

Focus:

- dogfood with real or representative Markdown notes without exposing private content;
- capture sanitized metrics and search-quality observations;
- document scale/performance expectations and practical limits;
- document safe AI-agent workflows for Codex, Claude Code, OpenCode, and similar agents;
- perform a privacy/security review based on generated artifacts and real usage;
- polish CLI help, error messages, and common workflows based on beta feedback;
- define RC readiness gates and select the next prerelease version target;
- prepare either another beta or the first RC after dogfood results are known.

Non-goals:

- no stable `1.0.0` release until RC criteria are met;
- no PyPI publishing unless explicitly requested;
- no API or web server;
- no database;
- no FAISS/ANN acceleration unless dogfood proves exact in-memory search is insufficient and a separate issue scopes it.

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

## RC readiness

See [`docs/rc-criteria.md`](rc-criteria.md) for the RC readiness checklist
and version target recommendations.
