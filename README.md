# semantic-index

`semantic-index` is a CLI-first tool for turning local Markdown notes into retrievable context for AI agents.

Current status: **pre-alpha**. The build command can discover Markdown files locally. Index building and semantic search are not implemented yet.

## Goal

- Read local Markdown documents.
- Split them into useful retrieval chunks.
- Generate local embeddings in a future stage.
- Search in memory without a database.
- Persist the index in simple local files (`docs.jsonl` + `index.npz`) when implemented.

## Current scope

Included now:

- Installable Python project.
- `semantic-index` CLI entrypoint.
- Commands:
  - `semantic-index --help`
  - `semantic-index version`
  - `semantic-index build <path>` — discover Markdown files safely
- Planned architecture documentation in [`docs/architecture.md`](docs/architecture.md).

Not included yet:

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
```

Alternative without installing the package:

```bash
PYTHONPATH=src python -m semantic_index --help
PYTHONPATH=src python -m semantic_index version
PYTHONPATH=src python -m semantic_index build ./notes
PYTHONPATH=src python -m semantic_index build ./docs --out ./my-index
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

## Short roadmap

1. Add a `build` command with basic path validation and `.md` discovery.
2. Implement simple Markdown chunking by headings and approximate size.
3. Add `fastembed` + `numpy` for embeddings and exact in-memory search.
4. Persist the index as `docs.jsonl` + `index.npz`.
5. Add agent-oriented output (`text`, `json`, `jsonl`) with explicit limits.
