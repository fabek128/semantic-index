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

## Current recommendation

The next milestone should be:

```text
v0.9.0-pre-alpha: Quality automation and docs correctness
```

Do **not** jump directly to FAISS, APIs, databases, web UI, or heavy indexing frameworks. The next step is to make the current pre-alpha MVP consistently verifiable, clean in CI, and accurately documented before adding retrieval features.

Recommended execution order:

1. #28 — clean ResourceWarning noise from tests.
2. #30 — fix documentation inconsistencies found after v0.8.
3. #31 — make NumPy index loading explicitly pickle-safe.
4. #38 — harden multi-file index consistency validation.
5. #29 — add minimal GitHub Actions checks once local tests are clean.

## Open phases

### v0.9.0-pre-alpha: Quality automation and docs correctness

Issues: #28, #29, #30, #31, #38

Goal: make the repository consistently verifiable and clean after the first pre-alpha release-readiness pass.

Focus:

- remove ResourceWarning noise from tests;
- add minimal GitHub Actions checks;
- correct post-v0.8 documentation inconsistencies;
- make NumPy index loading explicitly pickle-safe;
- harden multi-file index consistency validation.

Known corrections captured in this milestone:

- `python -m unittest discover` passes but emits `ResourceWarning` noise from temporary test files;
- `docs/architecture.md` has malformed list numbering around build/search responsibilities;
- README and roadmap contain stale wording from earlier phases;
- security/offline wording must distinguish local note processing from first-run model download/cache behavior;
- index loading should use `np.load(..., allow_pickle=False)` explicitly;
- mixed or malformed multi-file indexes should fail with actionable validation errors.

Non-goals:

- no deployment;
- no PyPI publishing;
- no new runtime service;
- no large framework migration.

### v0.10.0-pre-alpha: Privacy, offline mode, and configuration

Issues: #32, #33, #34

Goal: reduce accidental local metadata exposure and make model/cache/configuration behavior explicit.

Focus:

- avoid leaking absolute local paths in index metadata and search output by default;
- define first-run model download/cache/offline behavior;
- expose minimal safe build configuration such as chunk size and, if justified, model name.

Known corrections captured in this milestone:

- generated index metadata can expose absolute local paths;
- offline expectations are not explicit enough for first-run model downloads;
- the build command does not yet expose a safe `--max-chars` option even though chunking supports it internally.

Non-goals:

- no encryption layer;
- no secret scanner;
- no external embedding API;
- no global config file.

### v0.11.0-pre-alpha: Retrieval quality evaluation and hybrid search

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
