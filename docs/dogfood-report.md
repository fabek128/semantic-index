# Dogfood validation — v0.12.0b1

## Environment

| Metric | Value |
| --- | --- |
| OS | macOS 26.0 arm64 |
| Python | 3.14 |
| Package | `semantic-index==0.12.0b1` |
| Model | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (384 dims) |
| Model cache | Pre-cached |

## Corpus

| Metric | Value |
| --- | --- |
| Source | Repo `docs/` directory |
| Files | 11 (architecture, spec, roadmap, contract, troubleshooting, etc.) |
| Chunks | 110 |
| Index size | `docs.jsonl` 58 KB, `index.npz` 153 KB |

## Build

| Metric | Value |
| --- | --- |
| Build time (cached model) | ~11 s |
| Embedding dimensions | 384 |
| Max chars per chunk | 1800 (default) |

## Search results

### 1. `"chunk markdown"` — semantic

Top result correctly returns the `text` format section in `cli-contract.md`.
Relevant chunks from `spec.md` and `cli-contract.md` follow.

- **Relevance**: good — top result is about chunk output format.
- **Time**: ~1.6 s.

### 2. `"path security symlink"` — semantic

Top result from `troubleshooting.md` (No Markdown files found) — partially
relevant. Second result from `spec.md` (pickle safety) — correct.
Third result from `architecture.md` (persistence format) — correct.

- **Relevance**: adequate — multi-topic query returns varied relevant docs.
- **Time**: ~1.3 s.

### 3. `"incremental"` — lexical

Top result is `architecture.md` (Non-goals for now) which explicitly
mentions "Advanced incremental indexing". Correct exact match.

- **Relevance**: perfect — exact term match.
- **Time**: ~0.1 s.

### 4. `"manifest.json"` — lexical

All three top results from `architecture.md` where `manifest.json`
appears in code blocks. Correct exact matches.

- **Relevance**: perfect.
- **Time**: ~0.1 s.

### 5. `"release smoke test"` — hybrid

Top result is `artifact-build.md` (Full release validation) — correct.
Second is `release-smoke-test.md` (Output example) — correct.
Third is `dependency-policy.md` (Updating dependencies) — correct.

- **Relevance**: good — all three directly reference the smoke test.
- **Time**: ~1.2 s.

### 6. `"security"` — semantic, JSON output

Valid JSON output with all expected fields (`score`, `id`, `path`,
`title`, `heading`, `chunk_index`, `text`).

- **Time**: ~1.3 s.

## UX observations

- **No confusing errors** encountered during build or any search mode.
- **Help text** is clear.
- **No stack traces** printed for any operation.
- **Model warning** about mean pooling appears on every semantic/hybrid
  query (fastembed 0.8.0). Not a blocker but noisy.

## Findings

1. **fastembed UserWarning noise**: Every semantic/hybrid search prints a
   UserWarning about mean pooling vs CLS. This is cosmetic but cluttered
   for agent consumption. Consider suppressing or documenting in
   troubleshooting.

2. **No blockers found**. RC readiness is not blocked by dogfood
   validation.

3. All three search modes return meaningful results for realistic docs.
   Lexical mode is notably fast (~0.1 s) and precise for identifiers.

## Conclusion

The beta release is functional on a realistic corpus. No RC blockers
identified. The fastembed warning is the only cosmetic issue worth
tracking before RC.
