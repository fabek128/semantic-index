# CLI contract

This document defines the `semantic-index` CLI behavior, output schemas,
and exit codes for the beta phase. Agents and integrations may depend on
these contracts.

## Commands

### `semantic-index version`

Print the installed version and exit.

| Flag | Default | Description |
| --- | --- | --- |
| *(none)* | | |

- Exit code: `0`
- Output: `semantic-index <semver>` (one line)

### `semantic-index build`

Discover Markdown files from a local path, split into chunks, generate
embeddings, and persist the index.

| Flag | Default | Description |
| --- | --- | --- |
| `input_path` | *(required)* | Markdown file or directory |
| `--out` | `.semantic-index` | Output directory |
| `--max-chars` | `1800` | Max characters per chunk |
| `--model` | `None` | Embedding model name |

- Exit code: `0` on success
- Error exits: `1`

### `semantic-index search`

Load a built index and return ranked results.

| Flag | Default | Description |
| --- | --- | --- |
| `query` | *(required)* | Free-text search query |
| `--index` | `.semantic-index` | Index directory |
| `--top-k` | `5` | Number of results |
| `--format` | `text` | Output format: `text`, `json`, `jsonl` |
| `--max-chars` | `200` | Max chars per chunk (`0` = no limit) |
| `--mode` | `semantic` | Search mode: `semantic`, `lexical`, `hybrid` |
| `--semantic-weight` | `0.5` | Semantic score weight for `hybrid` mode |

- Exit code: `0` on success
- Error exits: `1`

## Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success |
| `1` | Error (invalid args, file not found, corrupt index, etc.) |

All errors are written to stderr. Stack traces are not printed by default.

## JSON and JSONL schemas

All results are arrays (JSON) or newline-delimited objects (JSONL)
containing the following fields.

### Base fields (present in all modes)

| Field | Type | Description |
| --- | --- | --- |
| `score` | `float` | Relevance score, `[0, 1]` range (higher = more relevant) |
| `id` | `string` | Deterministic chunk identifier |
| `path` | `string` | File path relative to indexed root |
| `title` | `string` | Document title (first `# ` heading) |
| `heading` | `string` | Section heading under which this chunk falls |
| `chunk_index` | `int` | Order of this chunk within the file |
| `text` | `string` | Chunk text content (possibly truncated by `--max-chars`) |

### `semantic` mode

Uses cosine similarity between query and chunk embeddings.

- Score: cosine similarity, normalized `[0, 1]`
- No extra fields beyond base fields.

### `lexical` mode

Uses term-frequency matching over chunk text, heading, and title.
No embedder is loaded.

- Score: fraction of query terms found in the chunk + heading/title bonus
- No extra fields beyond base fields.

### `hybrid` mode

Weighted combination of semantic (cosine) and lexical scores.

- `score`: combined score `= semantic_weight * semantic + (1 - semantic_weight) * lexical`
- Extra fields:

| Field | Type | Description |
| --- | --- | --- |
| `semantic_score` | `float` | Raw cosine similarity score |
| `lexical_score` | `float` | Raw lexical score (not normalised by max) |

### `text` format

One result block per chunk:

```
<score:.4f>  <path>  #<heading>
  <text>
```

## Error handling

- Errors are written to stderr.
- The CLI does not print Python tracebacks by default.
- An index directory is validated for the expected files
  (`manifest.json`, `docs.jsonl`, `index.npz`) before searching.

## Compatibility note

- The exact `score` values vary by model version and embedding
  implementation. The schema (field names, types, score range) is
  stable. Exact numerical values are not guaranteed across versions.
