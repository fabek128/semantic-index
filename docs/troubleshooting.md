# Troubleshooting

Common issues when using `semantic-index`, with causes and solutions.

## Model download fails

**Error:**
```
Error installing 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'.
Connection error.
```

**Causes:**
- No internet connection on first run.
- Firewall or proxy blocking Hugging Face.

**Solutions:**
1. Ensure network access and retry. The model downloads once and is
   cached in `~/.cache/fastembed/`.
2. For offline use, pre-cache the model on a machine with internet:
   ```python
   from fastembed import TextEmbedding
   TextEmbedding(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
   ```
   Then copy `~/.cache/fastembed/` to the offline machine.

## Index not found

**Error:**
```
Error: index directory not found: .semantic-index
```

**Causes:**
- You have not built an index yet.
- You are running `search` from a different directory than `build`.
- The `--index` path is wrong.

**Solutions:**
1. Run `semantic-index build <path>` first.
2. Use `--index` to point to the correct index directory:
   ```bash
   semantic-index search "query" --index /path/to/index
   ```

## Corrupt or inconsistent index

**Error:**
```
Error: index file ... is missing or corrupt
```

**Causes:**
- Index files were manually modified or deleted.
- The index was built with a different model version.
- Disk error during write.

**Solutions:**
1. Rebuild the index:
   ```bash
   semantic-index build <path> --out <index-dir>
   ```
2. If a rebuild does not help, delete the index directory and rebuild
   from scratch.

## Embedding dimension mismatch

**Error:**
```
Embedder produces X-dimensional vectors, but the index has Y dimensions.
The search model differs from the one used during indexing.
```

**Causes:**
- You built the index with one model and are searching with another.

**Solutions:**
1. Rebuild the index with the intended model:
   ```bash
   semantic-index build <path> --model <model-name>
   ```
2. Or remove the `--model` flag to use the default model (which must
   match the one used during build).

## No Markdown files found

**Output:**
```
No Markdown files found in: /path/to/notes
```

**Causes:**
- The path does not contain `.md` files.
- The path does not exist or is a single file with a different extension.
- The path contains only excluded directories (e.g., `.git`, `node_modules`).

**Solutions:**
1. Verify the path:
   ```bash
   find /path/to/notes -name '*.md' | head
   ```
2. If the path is correct, verify file permissions:
   ```bash
   ls -la /path/to/notes
   ```

## Permission denied

**Error:**
```
Error: [Errno 13] Permission denied: '/path/to/file'
```

**Causes:**
- The tool does not have read permission on the input path.
- The tool does not have write permission on the output directory.

**Solutions:**
1. Ensure the input path is readable:
   ```bash
   chmod -R +r /path/to/notes
   ```
2. Ensure the output directory is writable, or use a different `--out`
   path:
   ```bash
   semantic-index build <path> --out /tmp/my-index
   ```

## Which search mode should I use?

| Mode | When to use |
| --- | --- |
| `semantic` (default) | When you need conceptual or fuzzy matching. Best for general-purpose search. |
| `lexical` | When you need exact term matching (e.g., identifiers, code snippets, proper names). No model download needed. |
| `hybrid` | When you want both semantic and lexical relevance. Adjust `--semantic-weight` to favour one over the other. |

## Empty results from lexical search

**Possible causes:**
- The query terms do not appear in any chunk.
- Lexical search is case-insensitive but word-boundary-sensitive.
  Partial terms (e.g., `program` matching `programming`) are not found.

**Solutions:**
- Try full words or `semantic` mode for fuzzy matching.
- Verify the terms exist in the indexed notes:
  ```bash
  grep -ri "your-term" /path/to/notes
  ```

## Build hangs or is very slow

**Causes:**
- First run downloads the embedding model (~470 MB).
- Very large corpus (thousands of files).
- Resource contention.

**Solutions:**
- The first build is expected to be slow. Subsequent builds use the
  cached model.
- For large corpora, increase `--max-chars` to reduce chunk count:
  ```bash
  semantic-index build <path> --max-chars 3000
  ```

## Unexpected scores in hybrid mode

Hybrid scores are a weighted combination:
```
score = semantic_weight * semantic_score + (1 - semantic_weight) * lexical_score
```

- If the lexical score dominates unexpectedly, lower
  `--semantic-weight`.
- If the semantic score dominates unexpectedly, raise
  `--semantic-weight`.
- Both sub-scores are exposed in JSON output as `semantic_score`
  and `lexical_score` for debugging.
