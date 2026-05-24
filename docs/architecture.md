# Architecture

This document describes the architecture for `semantic-index`. The build command (discovery, chunking, embedding, persistence) and the search command are implemented.

## Principles

- CLI-first: every operation must be runnable from a terminal or from an AI agent.
- Local-first: use local files only.
- No database: persist data in simple, auditable formats.
- No external services: do not send note content outside the machine.
- Minimal dependencies: add `fastembed` and `numpy` only when embeddings/search are implemented.
- Safe formats: avoid `pickle`; prefer `jsonl` and `npz`.

## Components

### 1. Build command — Full pipeline (implemented)

```bash
semantic-index build ./notes --out .semantic-index
```

Current responsibilities:

1. Validate that the input path exists and is local.
2. Discover `*.md` files (single file or recursive directory walk).
3. Skip common generated/hidden directories (`.git`, `.venv`, `.semantic-index`, `.embeddings`, `__pycache__`, `node_modules`).
4. Do not follow symlinks.
5. Read each file as UTF-8.
6. Convert each document into Markdown chunks.
7. Generate local embeddings with `fastembed`.
8. Normalize vectors for cosine similarity via dot product.
9. Save:
   - `.semantic-index/docs.jsonl`: chunk text and metadata.
   - `.semantic-index/index.npz`: normalized `float32` embedding matrix.

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

Security notes:

- Do not follow symlinks by default until an explicit policy is defined.
- Do not write outside the `--out` directory provided by the user.
- Do not include secrets in logs.
- Treat `docs.jsonl` and `index.npz` as sensitive data because they are derived from private notes.

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

Responsibilities:

1. Load `docs.jsonl`.
2. Load `index.npz`.
3. Generate a local embedding for the query.
4. Normalize the query.
5. Compute dot products with `numpy`.
6. Sort results by descending score.
7. Print results in the requested format.

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

## Planned persistence

Future default directory:

```text
.semantic-index/
├── docs.jsonl
└── index.npz
```

`docs.jsonl` stores metadata and text per chunk. `index.npz` stores the normalized embedding matrix.

Reasons:

- `jsonl` is inspectable and easy to process.
- `npz` is efficient for `numpy` arrays.
- Both avoid introducing a database in the first version.

## Non-goals for now

- HTTP API.
- Web UI.
- Local or remote database.
- FAISS, ChromaDB, LanceDB, or SQLite.
- Filesystem watchers.
- Cross-machine synchronization.
- Advanced incremental indexing.
