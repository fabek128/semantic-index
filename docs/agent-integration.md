# AI-agent integration

`semantic-index` is designed for AI agents that need to retrieve relevant
context from local Markdown notes.

## Quick start for agents

```bash
# 1. Build an index from your notes
semantic-index build ~/notes --out ~/notes/.semantic-index

# 2. Search with JSON output (easiest for agent parsing)
semantic-index search "your query" --index ~/notes/.semantic-index --format json

# 3. Use JSONL for streaming-friendly output
semantic-index search "your query" --index ~/notes/.semantic-index --format jsonl
```

## Workflow patterns

### 1. Semantic search (default)

Best for conceptual, fuzzy, or open-ended queries.

```bash
semantic-index search "what are the design principles" --index ~/notes/.semantic-index \
  --format json --top-k 5
```

Use this when you need to find related content even when the exact
wording differs.

### 2. Lexical search (exact term matching)

Best for code identifiers, proper names, symbols, or exact phrases.

```bash
semantic-index search "FastEmbedEmbedder" --index ~/notes/.semantic-index \
  --mode lexical --format json --top-k 3
```

Lexical search does not load an embedding model, making it fast
(~0.1 s) and usable offline without model download.

### 3. Hybrid search (combined relevance)

Best when you want both semantic and exact-term relevance.

```bash
semantic-index search "CLI argument parser" --index ~/notes/.semantic-index \
  --mode hybrid --format json --top-k 5 --semantic-weight 0.6
```

The `semantic_weight` parameter controls the balance (default 0.5).
The output includes `semantic_score` and `lexical_score` for each
result, which can be useful for debugging or reranking.

### 4. Bounded output for agent context windows

```bash
# Limit number of results
semantic-index search "your query" --index ~/notes/.semantic-index \
  --top-k 3

# Truncate each chunk to a fixed character count
semantic-index search "your query" --index ~/notes/.semantic-index \
  --max-chars 500

# Combined
semantic-index search "your query" --index ~/notes/.semantic-index \
  --top-k 3 --max-chars 500 --format json
```

### 5. Multiple queries for broader context

Run several focused queries instead of one broad query. Each call is
independent and can use a different mode.

```bash
# Get semantic matches for the concept
semantic-index search "authentication flow" --index ~/notes/.semantic-index --format jsonl

# Get exact references
semantic-index search "OAuth2Callback" --index ~/notes/.semantic-index --mode lexical --format jsonl
```

## Output parsing

### JSON (single array)

```json
[
  {
    "score": 0.92,
    "id": "abc123_0",
    "path": "notes/project.md",
    "title": "Project notes",
    "heading": "Architecture",
    "chunk_index": 0,
    "text": "The system uses OAuth2 for authentication..."
  }
]
```

Parse with any JSON library:

```python
import json, subprocess
result = subprocess.run(
    ["semantic-index", "search", "query", "--index", ".", "--format", "json"],
    capture_output=True, text=True, check=True
)
chunks = json.loads(result.stdout)
```

### JSONL (one JSON object per line)

```
{"score": 0.92, "id": "abc123_0", ...}
{"score": 0.85, "id": "abc123_1", ...}
```

Parse line by line:

```python
for line in result.stdout.strip().split("\n"):
    chunk = json.loads(line)
    # process chunk
```

## Security and privacy for agents

1. **Indexes contain sensitive content**: `docs.jsonl` stores chunk text
   derived from your notes. Treat index directories like you treat your
   notes — do not commit them to public repositories or share them.

2. **No network traffic**: search commands never send data to external
   services. Only the initial model download (one-time) reaches Hugging
   Face.

3. **Paths are relative**: by default, paths in index output are relative
   to the indexed root. Use this to avoid leaking absolute paths.

4. **Output bounds**: always use `--top-k` and `--max-chars` to control
   how much context enters your agent context window.

## Agent checklist

Before running `semantic-index search` or `semantic-index build`:

- [ ] The index path is a known, writable directory.
- [ ] The search query does not contain secrets (query text appears in
      command history and process listings).
- [ ] Output format is `json` or `jsonl` for agent-friendly parsing.
- [ ] `--top-k` and `--max-chars` are set to bound context usage.
- [ ] The index was built with the same model (default is fine unless
      `--model` was explicitly set during build).
