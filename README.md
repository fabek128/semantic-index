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
semantic-index --help
semantic-index version
```

Alternative without installing the package:

```bash
PYTHONPATH=src python -m semantic_index --help
PYTHONPATH=src python -m semantic_index version
PYTHONPATH=src python -m semantic_index build ./notes
PYTHONPATH=src python -m semantic_index build ./docs --out ./my-index
```

### Search command examples

```bash
# Search with default text output
semantic-index search "query text" --index .semantic-index --top-k 5

# Agent-friendly JSON output
semantic-index search "query text" --index .semantic-index --format json

# JSONL output (one object per line)
semantic-index search "query text" --index .semantic-index --format jsonl
```

### Build command examples

```bash
# Discover Markdown files in a directory
semantic-index build ./notes

# Use a single Markdown file as input
semantic-index build ./notes/project.md

# Specify a custom output directory (index not built yet)
semantic-index build ./notes --out ./my-index
```

The build command validates paths, skips common generated directories (`.git`,
`.venv`, `.semantic-index`, `.embeddings`, `__pycache__`), ignores symlinks,
and prints a deterministic summary of discovered files.

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

The `semantic_index.chunker` module provides Markdown chunking for future
indexing:

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

The chunker is a pure standard-library function with no runtime dependencies.

## Testing

Run the unit test suite from the repository root:

```bash
python -m unittest discover
```

The current tests use only the Python standard library and cover the minimal CLI entrypoints.

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
│       ├── discovery.py
│       └── chunker.py
├── tests/
│   ├── test_cli.py
│   ├── test_discovery.py
│   └── test_chunker.py
├── .gitignore
├── pyproject.toml
└── README.md
```

## Planned architecture

The planned flow is:

1. `build index`: discover Markdown files, split them into chunks, generate local embeddings, and save the index.
2. `search index`: load `docs.jsonl` + `index.npz`, embed the query, and return the best chunks.
3. Agent integration: expose results through the CLI in simple and stable formats, without a daemon or API.

See details in [`docs/architecture.md`](docs/architecture.md).

## Security and privacy

- The tool must operate only on local files explicitly provided by the user.
- It must not send notes, embeddings, or metadata to external services.
- It must not use `pickle` to load untrusted indexes.
- Local indexes may contain sensitive text derived from notes; `.semantic-index/`, `.embeddings/`, `docs.jsonl`, and `index.npz` are ignored by Git by default.

## Roadmap

The first local MVP shape is implemented: Markdown discovery, chunking, local embedding index persistence, and CLI search.

Next phases focus on pre-alpha hardening, index metadata/lifecycle, retrieval quality, and release readiness. See [`docs/roadmap.md`](docs/roadmap.md).
