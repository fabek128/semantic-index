# semantic-index

`semantic-index` is a CLI-first tool for turning local Markdown notes into retrievable context for AI agents.

Current status: **pre-alpha scaffold**. It can validate a local input path and discover Markdown files for a future index build, but it does not chunk documents, generate embeddings, write index files, or run semantic search yet.

## Goal

- Read local Markdown documents.
- Split them into useful retrieval chunks.
- Generate local embeddings in a future stage.
- Search in memory without a database.
- Persist the index in simple local files (`docs.jsonl` + `index.npz`) when implemented.

## Initial scope

Included now:

- Installable Python project.
- `semantic-index` CLI entrypoint.
- Minimal commands:
  - `semantic-index --help`
  - `semantic-index version`
  - `semantic-index build ./notes`
- Safe Markdown file discovery for local files/directories.
- Planned architecture documentation in [`docs/architecture.md`](docs/architecture.md).

Not included yet:

- Markdown content reading.
- Real document chunking.
- Embeddings with `fastembed`.
- Search with `numpy`.
- `docs.jsonl` / `index.npz` persistence.
- APIs, web servers, databases, or external services.

## Requirements

- Python 3.10 or newer.
- No external runtime dependencies in this scaffold.

## Development installation

From the repository root:

```bash
python -m pip install -e .
```

Then:

```bash
semantic-index --help
semantic-index version
semantic-index build ./docs
```

`build` currently discovers Markdown files and prints a summary only. It does not write `.semantic-index`, `docs.jsonl`, or `index.npz` yet.

Alternative without installing the package:

```bash
PYTHONPATH=src python -m semantic_index --help
PYTHONPATH=src python -m semantic_index version
PYTHONPATH=src python -m semantic_index build ./docs
```

## Testing

Run the unit test suite from the repository root:

```bash
python -m unittest discover
```

The current tests use only the Python standard library and cover the minimal CLI entrypoints plus safe Markdown discovery behavior.

## Project structure

```text
semantic-index/
├── docs/
│   ├── architecture.md   # Planned architecture
│   └── spec.md           # Base specification / technical recipe
├── src/
│   └── semantic_index/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       └── discovery.py
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   └── test_discovery.py
├── .gitignore
├── pyproject.toml
└── README.md
```

## Planned architecture

The planned flow is:

1. `build index`: discover Markdown files, split them into chunks, generate local embeddings, and save the index. The current `build` command only performs safe discovery.
2. `search index`: load `docs.jsonl` + `index.npz`, embed the query, and return the best chunks.
3. Agent integration: expose results through the CLI in simple and stable formats, without a daemon or API.

See details in [`docs/architecture.md`](docs/architecture.md).

## Security and privacy

- The tool must operate only on local files explicitly provided by the user.
- It must not send notes, embeddings, or metadata to external services.
- It must not use `pickle` to load untrusted indexes.
- Local indexes may contain sensitive text derived from notes; `.semantic-index/`, `.embeddings/`, `docs.jsonl`, and `index.npz` are ignored by Git by default.

## Short roadmap

1. Extend `build` beyond discovery into Markdown content loading.
2. Implement simple Markdown chunking by headings and approximate size.
3. Add `fastembed` + `numpy` for embeddings and exact in-memory search.
4. Persist the index as `docs.jsonl` + `index.npz`.
5. Add agent-oriented output (`text`, `json`, `jsonl`) with explicit limits.
