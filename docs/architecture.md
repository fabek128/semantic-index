# Architecture

This document describes the architecture for `semantic-index`. The build command (discovery, chunking, embedding, persistence) and the search command are implemented.

## Principles

- CLI-first: every operation must be runnable from a terminal or from an AI agent.
- Local-first: use local files only.
- No database: persist data in simple, auditable formats.
- No external services: do not send note content outside the machine.
- Minimal dependencies: `fastembed` and `numpy` for embeddings and search.
- Safe formats: avoid `pickle`; prefer `jsonl` and `npz`.

## Components

### 1. Build command — Full pipeline (implemented)

```bash
semantic-index build ./notes --out .semantic-index
```

Current CLI options for the build command:

- `input_path`: path to a Markdown file or directory.
- `--out` (default `.semantic-index`): output directory for index data.
- `--max-chars` (default 1800): maximum characters per chunk.
- `--model` (default: built-in multilingual MiniLM): embedding model name.

Current responsibilities:

1. Validate that the input path exists and is local.
2. Discover `*.md` files (single file or recursive directory walk).
3. Skip common generated/hidden directories (`.git`, `.venv`, `.semantic-index`, `.embeddings`, `__pycache__`, `node_modules`).
4. Do not follow symlinks.
5. Read each file as UTF-8.
6. Convert each document into Markdown chunks (respecting ``--max-chars``).
7. Generate local embeddings via ``fastembed`` (using ``--model`` if provided).
8. Normalize vectors for cosine similarity via dot product.
9. Save:
    - `.semantic-index/manifest.json`: self-describing index metadata.
    - `.semantic-index/docs.jsonl`: chunk text and metadata.
    - `.semantic-index/index.npz`: normalized `float32` embedding matrix.

Paths stored in chunk metadata are relative to the discovery root by default.
For a single-file build the root is the parent directory; for a directory build
the root is the directory itself. This prevents leaking absolute paths when
search results are printed or indexes are shared.

Minimum metadata per chunk:

```json
{
  "id": "stable-chunk-id",
  "path": "relative/path/to/note.md",
  "title": "Document title",
  "heading": "Current heading",
  "chunk_index": 0,
  "text": "Chunk content"
}
```

The three index files are written to a temporary subdirectory first and
renamed into place one by one. If any write fails before the renames
start, the original index is untouched. However, this is **not** a fully
transactional multi-file commit — a crash between consecutive
`replace()` calls can leave the files out of sync. `load_index` detects
these inconsistent states and raises a clear error requesting a rebuild.

Security notes:

- Do not follow symlinks by default until an explicit policy is defined.
- Do not write outside the `--out` directory provided by the user.
- Do not include secrets in logs.
- Treat `manifest.json`, `docs.jsonl`, and `index.npz` as sensitive data because they are derived from private notes.
- Chunk paths are stored relative to the discovery root to reduce absolute path leakage.

### 2. Markdown chunking (implemented — used by the build command)

Goal: produce context units that are small enough for retrieval and large enough to preserve meaning.

Current strategy:

1. Split by Markdown headings (`#`, `##`, `###`, etc.).
2. Keep metadata for the active heading.
3. If a section is long, split it by paragraphs up to an approximate character limit.
4. If a paragraph is still too long, split by individual lines.
5. Avoid empty chunks.
6. Preserve path, title, heading, chunk index, and deterministic chunk id.

Parameters:

- `max_chars=1800` as a simple default.
- The chunker is a library module (`semantic_index.chunker`).
- It is called by the build command to produce chunks before embedding.

Deterministic chunk ids:

- Each file gets a short `md5` hash based on its resolved path.
- Chunk ids are `{file_hash}_{chunk_index}`, making them stable for the same file path and chunk order.

### 3. Search index (implemented)

```bash
semantic-index search "query text" --index .semantic-index --top-k 5
```

Search modes:

- ``semantic`` (default) — cosine similarity with stored embeddings.
- ``lexical`` — exact term-frequency matching over chunk text, heading,
  and title.  No embedding model required.
- ``hybrid`` — weighted combination of semantic and lexical scores
  (``--semantic-weight``, default 0.5).

Responsibilities:

1. Load and validate `manifest.json` (schema version, embedding dimensions, chunk count).
2. Load `docs.jsonl`.
3. Load `index.npz` and validate embedding matrix is 2D float.
4. Validate consistency: chunk count, embedding dimensions, row counts.
5. Generate a local embedding for the query.
6. Normalize the query.
7. Compute dot products with `numpy`.
8. Sort results by descending score.
9. Print results in the requested format.

Output formats:

- `text` (default) — human-readable with score, path, heading, and snippet:

  ```text
  0.8123  notes/project.md  #Architecture
    Relevant chunk text...
  ```

- `json` — JSON array of result objects (score + full chunk metadata):

  ```bash
  semantic-index search "auth flow" --format json --top-k 8
  ```

- `jsonl` — one JSON object per line (agent-friendly):

  ```bash
  semantic-index search "auth flow" --format jsonl --top-k 8
  ```

### 4. AI-agent integration

Integration should happen through the CLI, not through a server.

Expected pattern:

1. The agent runs `semantic-index search` with a question or context terms.
2. The tool returns a bounded number of chunks.
3. The agent uses those chunks as context for the current task.

Requirements for agents:

- Deterministic and easy-to-parse output (`json` or `jsonl`).
- Explicit limits (`--top-k`, maximum snippet size).
- Clear exit codes.
- Actionable errors without stack traces by default.
- Do not modify files during `search`.

## Persistence format

The build command writes to a user-specified `--out` directory (default `.semantic-index/`):

```text
.semantic-index/
├── manifest.json     # Self-describing index metadata
├── docs.jsonl        # Chunk metadata and text (JSONL)
└── index.npz         # Normalized float32 embedding matrix
```

`manifest.json` fields:

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | int | Manifest schema version (currently 1) |
| `package_version` | str | `semantic-index` version that built the index |
| `model_name` | str or null | Embedding model name |
| `embedding_dimensions` | int or null | Embedding vector dimensions |
| `chunk_count` | int | Number of chunks indexed |
| `created_at` | str | ISO 8601 creation timestamp |
| `chunking` | object | Chunking parameters (`max_chars`) |
| `source` | object | Source summary (`file_count`, `directories`) |

The manifest is validated during search. Incompatible or missing metadata
produces a clear error and a non-zero exit code.

Reasons:

- `jsonl` is inspectable and easy to process.
- `npz` is efficient for `numpy` arrays.
- Both avoid introducing a database.

## Non-goals for now

- HTTP API.
- Web UI.
- Local or remote database.
- FAISS, ChromaDB, LanceDB, or SQLite.
- Filesystem watchers.
- Cross-machine synchronization.
- Advanced incremental indexing.
