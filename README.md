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
- Output formats: `text` (human-readable), `json`, `jsonl` (agent-friendly, see [JSON/JSONL schema](#jsonjsonl-schema))
- Architecture documentation in [`docs/architecture.md`](docs/architecture.md).
- Default embedding model: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dims, multilingual, no prefixes needed).
- Prefix policy: the default model does **not** use `passage:` / `query:` prefixes. E5-family models require them — see [`docs/spec.md#prefix-policy`](docs/spec.md).

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
chunks each file, generates local embeddings, and writes the index atomically.

Options:

- `--max-chars` (default 1800): maximum characters per Markdown chunk.
- `--model` (default: built-in multilingual MiniLM): embedding model name
  from Hugging Face. The model is downloaded on first use and cached locally.
- `--out` (default `.semantic-index`): output directory for the index.

If the output directory already contains an index (`manifest.json`,
`docs.jsonl`, or `index.npz`), the build command overwrites those files
and prints a list of overwritten files. The overwrite is **atomic** —
files are written to a temporary subdirectory first and renamed into
place, so a failed build does not leave a corrupt partial index.

### Index output

```bash
# Build a full index
semantic-index build ./notes --out .semantic-index
```

The index produces three files:

- `.semantic-index/manifest.json` — self-describing index metadata
  (schema version, model name, dimensions, chunk count, creation timestamp).
- `.semantic-index/docs.jsonl` — one JSON object per chunk with metadata
  (id, path, title, heading, chunk_index, text).
- `.semantic-index/index.npz` — normalized `float32` embedding matrix
  (n_chunks × 384).

Search validates the manifest to ensure the index was built with a compatible
schema version and that the embedder model dimensions match the stored
embeddings. If the manifest is missing, corrupt, or incompatible, the search
command prints a clear error and exits non-zero.

### JSON/JSONL schema

The `json` format returns a JSON array of result objects. The `jsonl` format
returns one JSON object per line. Each object has the following fields:

```json
{
  "score": 0.8123,
  "id": "a1b2c3d4e5f6_0",
  "path": "/notes/project.md",
  "title": "Project notes",
  "heading": "Architecture",
  "chunk_index": 0,
  "text": "Relevant chunk text (truncated to --max-chars)"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `score` | float | Cosine similarity score (0–1) |
| `id` | str | Deterministic chunk identifier |
| `path` | str | Source Markdown file path (relative to the discovery root by default) |
| `title` | str or null | Document title (first `#` heading or filename stem) |
| `heading` | str or null | Current section heading |
| `chunk_index` | int | Chunk index within the source file |
| `text` | str | Chunk text, truncated to `--max-chars` characters |

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

### Setting up a clean development environment

From the repository root, create a fresh virtual environment and install:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -e .
```

### Smoke-test checklist

After a clean install, verify the CLI works and the tests pass:

```bash
# 1. Help and version
semantic-index --help
semantic-index version

# 2. Discover a small notes directory
mkdir -p /tmp/smoke-test
echo '# Hello' > /tmp/smoke-test/welcome.md
echo '## Section' >> /tmp/smoke-test/welcome.md
echo 'World.' >> /tmp/smoke-test/welcome.md
semantic-index build /tmp/smoke-test --out /tmp/smoke-index

# 3. Search the index
semantic-index search "hello" --index /tmp/smoke-index

# 4. Test search output formats
semantic-index search "hello" --index /tmp/smoke-index --format json
semantic-index search "hello" --index /tmp/smoke-index --format jsonl

# 5. Clean up
rm -rf /tmp/smoke-test /tmp/smoke-index

# 6. Run unit tests
python -m unittest discover

# 7. Verify no regressions in code quality
python -m compileall -q src
```

> **Note on model caching**: The first `semantic-index build` call downloads the default embedding model (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`) and caches it locally via `fastembed`. This is a one-time download; subsequent runs use the cached model. No data is sent to external services.

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
├── .github/
│   └── workflows/
│       └── ci.yml           # GitHub Actions CI
├── CHANGELOG.md
├── .gitignore
├── pyproject.toml
└── README.md
```

## Architecture

The CLI implements two commands:

1. **`build`**: discover Markdown files, split into chunks, generate local embeddings, and save `docs.jsonl` + `index.npz`.
2. **`search`**: load `docs.jsonl` + `index.npz`, embed the query, and return the best chunks with ranked scores.

Future phases: hybrid search, incremental indexing, ANN acceleration.

See details in [`docs/architecture.md`](docs/architecture.md).

## Versioning policy

This project uses [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

During **`0.x` pre-alpha** development:

- The **minor** version (`0.minor.patch`) is incremented for each feature
  milestone (v0.1, v0.2, …).
- The **patch** version (`0.x.patch`) is incremented for fixes, doc updates,
  and smaller changes within a milestone.
- There is **no API/ABI stability guarantee** until `1.0.0`.
- Breaking changes bump the minor version, even in `0.x`.

### Version bump checklist

```bash
# 1. Update src/semantic_index/__init__.py   (__version__)
# 2. Update pyproject.toml                   (version)
# 3. Add entry to CHANGELOG.md
# 4. Run full validation (see Release checklist)
# 5. Commit with message "Bump version to X.Y.Z"
# 6. Tag: git tag -a vX.Y.Z -m "vX.Y.Z"
# 7. Push: git push origin main --tags
```

## Release checklist

Run these commands in a clean environment before tagging a release:

```bash
# 1. Clean install
python3 -m venv /tmp/release-check
source /tmp/release-check/bin/activate
pip install --upgrade pip
pip install -e .

# 2. CLI validation
semantic-index --help
semantic-index version

# 3. Build and search smoke test
mkdir -p /tmp/release-notes
echo '# Hello' > /tmp/release-notes/welcome.md
echo '## Section' >> /tmp/release-notes/welcome.md
echo 'World.' >> /tmp/release-notes/welcome.md
semantic-index build /tmp/release-notes --out /tmp/release-idx
semantic-index search "hello" --index /tmp/release-idx
semantic-index search "hello" --index /tmp/release-idx --format json
semantic-index search "hello" --index /tmp/release-idx --format jsonl
semantic-index search "hello" --index /tmp/release-idx --max-chars 5
rm -rf /tmp/release-notes /tmp/release-idx

# 4. Unit tests
python -m unittest discover

# 5. Code quality
python -m compileall -q src

# 6. Cleanup
deactivate
rm -rf /tmp/release-check
```

## Security and privacy

- The tool operates only on local files explicitly provided by the user.
- It does not send notes, embeddings, or metadata to external services.
- The first use of the build command downloads the default embedding model
  from Hugging Face and caches it locally. This is a **one-time download**;
  no note content is sent to external servers.
- It must not use `pickle` to load untrusted indexes.
- Local indexes may contain sensitive text derived from notes;
  `.semantic-index/`, `.embeddings/`, `docs.jsonl`, `index.npz`,
  and `manifest.json` are ignored by Git by default.

### Security review checklist

Before every release, verify:

- [ ] No secrets, tokens, or credentials are committed or logged.
- [ ] No user note content is sent over the network. Model download is cached locally.
- [ ] All user-facing errors go to stderr with no stack traces.
- [ ] Symlinks are not followed during discovery.
- [ ] Index files are written atomically (temp dir + rename).
- [ ] Corrupt or missing index files produce actionable errors.
- [ ] `pickle` is not used for index persistence.
- [ ] `.gitignore` covers all generated artifacts.
- [ ] Embedding model is downloaded and cached locally (no data sent externally).
- [ ] Default model does not require `passage:` / `query:` prefixes.
- [ ] `--top-k` and `--max-chars` bound output size.

### Offline use and model caching

The build command generates embeddings locally and **never sends note content
to external services**.

The first call to `semantic-index build` downloads the default embedding model
from Hugging Face and caches it in ``~/.cache/fastembed/``.  This is a **one-time
download**; subsequent builds use the local cache.  To prepare a machine for
fully offline use:

1. Run ``semantic-index build`` once with a network connection so the model
   is cached.
2. Subsequent builds in offline mode use the cached model automatically.

If the model is not cached and no network is available, ``fastembed`` raises
an error.  The error message includes the model name and suggests checking
the network connection or pre-caching the model.
- [ ] Exit codes are non-zero on expected errors.

## Roadmap

The first local MVP shape is implemented: Markdown discovery, chunking, local embedding index persistence, and CLI search.

Next phases focus on pre-alpha hardening, index metadata/lifecycle, retrieval quality, and release readiness. See [`docs/roadmap.md`](docs/roadmap.md).
