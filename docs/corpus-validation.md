# Synthetic corpus validation

Procedure for validating `semantic-index` behavior with a larger,
non-sensitive synthetic Markdown corpus.

## Generator

`scripts/generate-corpus.py` creates a deterministic Markdown corpus
covering:

- Nested directories (up to 3 levels)
- Unicode text (Japanese, French, Cyrillic)
- Long sections (30+ paragraphs)
- Code-like identifiers (`CamelCaseClass`, `snake_case_function`, etc.)
- Repeated terms for lexical search validation
- Mixed-language content

## Usage

```bash
# Generate corpus (default: /tmp/si-corpus)
python3 scripts/generate-corpus.py

# Custom output directory
python3 scripts/generate-corpus.py --out /tmp/my-corpus

# Different random seed
python3 scripts/generate-corpus.py --seed 99
```

## Expected characteristics

| Metric | Typical range |
| --- | --- |
| Directories | 8–10 |
| Files | 20–24 |
| Total size | 350–450 KB |
| Generation time | < 1s |

## Build and search validation

### Build

```bash
semantic-index build /tmp/si-corpus --out /tmp/si-index
```

Expected output:

```
Index built in: /tmp/si-index
  Files discovered: 22
  Chunks indexed:   284
```

| Metric | Typical range |
| --- | --- |
| Build time (first run, includes model download) | 15–60s |
| Build time (cached model) | 10–20s |
| `docs.jsonl` size | 400–460 KB |
| `index.npz` size | 380–420 KB |
| `manifest.json` size | ~500 B |

### Semantic search

```bash
semantic-index search "python programming" --index /tmp/si-index --top-k 3
```

- Returns results from `dev/python/` and `dev/cli/` directories.
- Scores are in `[0, 1]` range.

### Lexical search

```bash
semantic-index search "stir fry" --index /tmp/si-index --mode lexical --top-k 3
```

- Returns results from `recipes/asian/` (contains "stir-fries").
- Exact score values depend on term frequency in each chunk.
- Search time: < 1s (no embedder needed).

### Hybrid search

```bash
semantic-index search "command line tools" --index /tmp/si-index --mode hybrid --top-k 3
```

- Combines semantic and lexical scores.
- Results include `semantic_score` and `lexical_score` fields.

## Notes

- Exact ranking and score values vary by `fastembed` version.
- The corpus is generated deterministically from a seed — the same seed
  always produces the same files.
- The corpus is written to `/tmp` and is not committed to Git.
- First build triggers a model download (~470 MB) to `~/.cache/fastembed/`.
