# Roadmap

Current stage: **pre-alpha**.

The project already has an end-to-end local CLI MVP: Markdown discovery, chunking, local embedding index persistence, semantic search, lexical search, hybrid ranking, JSON/JSONL output, CI, and safety checks for local index files.

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

## Current recommendation

The next milestone should be:

```text
v0.12.0-alpha-candidate: Executable package and alpha readiness
```

This is the final pre-alpha stabilization phase before the first alpha candidate. Do **not** add FAISS, databases, web servers, background watchers, or external services before this phase is complete.

Recommended execution order:

1. #46 — fix the lexical partial-term regression and restore a green test suite.
2. #47 — align post-v0.11 docs and all agent specs.
3. #48 — build and verify installable CLI release artifacts.
4. #49 — normalize alpha versioning, changelog, and tag procedure.
5. #50 — add an alpha end-to-end CLI smoke validation flow.

## Executable and alpha readiness assessment

### Executable CLI status

The project is already executable as an installed Python CLI package:

```bash
python -m pip install -e .
semantic-index --help
semantic-index version
```

However, it is **not ready for a tagged executable alpha artifact** until v0.12 is complete because the current local suite has a failing lexical test and release artifact validation is not yet documented.

### First alpha target

The first alpha should be considered ready when all v0.12 issues are closed and merged:

- the full unit suite is green;
- docs and agent specs match the implemented post-v0.11 behavior;
- wheel/sdist or equivalent installable artifacts are validated from a clean environment;
- package version, changelog, and release tag procedure are consistent;
- an end-to-end CLI smoke flow is documented and runnable.

Expected alpha shape:

```text
0.12.0a1 / v0.12.0-alpha.1
```

The exact version identifier must be finalized in #49.

## Open phase

### v0.12.0-alpha-candidate: Executable package and alpha readiness

Issues: #46, #47, #48, #49, #50

Goal: turn the current pre-alpha CLI MVP into a clean, installable alpha candidate.

Focus:

- fix the post-v0.11 lexical test regression;
- align documentation and agent specifications with actual behavior;
- validate package artifacts and console-script installation outside the source tree;
- normalize version/changelog/tagging for the first alpha;
- document an end-to-end manual smoke test that covers build and all search modes.

Non-goals:

- no PyPI publishing unless explicitly requested later;
- no standalone PyInstaller binary;
- no Docker image;
- no database or external service;
- no ANN/FAISS acceleration;
- no API or web server.

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
