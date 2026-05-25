# semantic-index

`semantic-index` is a CLI-first tool for turning local Markdown notes into retrievable context for AI agents.

Current status: **pre-alpha**. The CLI supports index building and semantic search.

## Goal

- Read local Markdown documents.
- Split them into useful retrieval chunks.
- Generate local embeddings.
- Search in memory without a database.
- Persist the index in simple local files (`docs.jsonl` + `index.npz`).

## Current scope

Included now:

- Installable Python project.
- `semantic-index` CLI entrypoint.
- Commands:
  - `semantic-index --help`
  - `semantic-index version`
  - `semantic-index build <path>` — discover, chunk, embed, and persist index
  - `semantic-index search <query>` — search an existing index with ranked results
- Output formats: `text` (human-readable), `json`, `jsonl` (agent-friendly)
- Architecture documentation in [`docs/architecture.md`](docs/architecture.md).
- Default embedding model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dims, multilingual).

Not included yet:

- Hybrid lexical/BM25 search.
- Index merge / incremental indexing.
- FAISS or ANN acceleration.
- APIs, web servers, databases, or external services.

## Requirements

- Python 3.10 or newer.
- Dependencies: `fastembed`, `numpy` (installed automatically with the package).

## Development installation

From the repository root:

```bash
python -m pip install -e .
```

Then:

```bash
# Specify a custom output directory
semantic-index build ./notes --out ./my-index
```

The build command validates paths, skips common generated directories (`.git`,
`.venv`, `.semantic-index`, `.embeddings`, `__pycache__`), ignores symlinks,
chunks each file, generates local embeddings, and writes the index.

### Index output

```bash
# Build a full index
semantic-index build ./notes --out .semantic-index
```

The index produces two files:

- `.semantic-index/docs.jsonl` — one JSON object per chunk with metadata
  (id, path, title, heading, chunk_index, text).
- `.semantic-index/index.npz` — normalized `float32` embedding matrix
  (n_chunks × 384).

### Chunking (library module)

The `semantic_index.chunker` module provides Markdown chunking used by the
build command:

```python
from pathlib import Path
from semantic_index.chunker import chunk_markdown

chunks = chunk_markdown(Path("notes/project.md"), max_chars=1800)
for chunk in chunks:
    print(chunk["heading"], chunk["text"][:80])
```

Each chunk includes:
- `id` — deterministic hash based on the file path and chunk index
- `path` — source file path
- `title` — first `#` heading or filename stem as fallback
- `heading` — current ATX heading
- `chunk_index` — sequential index within the file
- `text` — chunk content

The chunker depends only on the Python standard library.

## Testing

Run the unit test suite from the repository root:

```bash
python -m unittest discover
```

The test suite covers CLI entrypoints, Markdown discovery, chunking, index building, and search.

## Project structure

```text
semantic-index/
├── docs/
│   ├── architecture.md   # Architecture and components
│   ├── roadmap.md        # Development roadmap and milestones
│   └── spec.md           # Technical specification / recipe
├── src/
│   └── semantic_index/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── discovery.py
│       ├── chunker.py
│       └── indexer.py
├── tests/
│   ├── __init__.py
│   ├── test_cli.py
│   ├── test_discovery.py
│   ├── test_chunker.py
│   └── test_indexer.py
├── .gitignore
├── pyproject.toml
└── README.md
```

## Architecture

The CLI implements two commands:

1. **`build`**: discover Markdown files, split into chunks, generate local embeddings, and save `docs.jsonl` + `index.npz`.
2. **`search`**: load `docs.jsonl` + `index.npz`, embed the query, and return the best chunks with ranked scores.

Future phases: hybrid search, index metadata and lifecycle, retrieval quality controls.

See details in [`docs/architecture.md`](docs/architecture.md).

## Security and privacy

- The tool must operate only on local files explicitly provided by the user.
- It must not send notes, embeddings, or metadata to external services.
- It must not use `pickle` to load untrusted indexes.
- Local indexes may contain sensitive text derived from notes; `.semantic-index/`, `.embeddings/`, `docs.jsonl`, and `index.npz` are ignored by Git by default.

## Roadmap

The first local MVP shape is implemented: Markdown discovery, chunking, local embedding index persistence, and CLI search.

Next phases focus on pre-alpha hardening, index metadata/lifecycle, retrieval quality, and release readiness. See [`docs/roadmap.md`](docs/roadmap.md).
