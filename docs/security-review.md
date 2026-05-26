# Beta privacy and security review — v0.12.0b1

## Scope

Review of generated artifacts, documentation, CLI behavior, and `.gitignore`
coverage before RC readiness.

## Items reviewed

### Generated artifacts

| Artifact | Finding |
| --- | --- |
| `manifest.json` | Contains schema version, model name, source dirs (relative). No sensitive content. |
| `docs.jsonl` | Contains chunk text derived from notes. **Treat as sensitive.** |
| `index.npz` | Contains float32 embedding vectors. Theoretically reversible with enough data. Treat as sensitive. |

### .gitignore coverage

All generated artifacts and common sensitive files are covered:

| Pattern | Covers |
| --- | --- |
| `.semantic-index/` | Default build output directory |
| `.embeddings/` | Legacy embedding directory |
| `docs.jsonl`, `index.npz`, `manifest.json` | Individual index files (any location) |
| `.env`, `.env.*` | Environment files with secrets |
| `dist/`, `build/`, `*.egg-info/`, `__pycache__/` | Build and Python artifacts |

### CLI output

- All errors go to **stderr** with no Python tracebacks.
- Build success message shows absolute path via `output_dir.resolve()` for
  user convenience. Actual paths stored in the index are **relative**.
- No secrets, tokens, or credentials are logged or printed.

### Documentation

- `docs/agent-integration.md` includes a security checklist and warnings
  about index sensitivity.
- `docs/troubleshooting.md` uses only generic, non-sensitive example paths
  (`/path/to/notes`).
- `docs/corpus-validation.md` uses only synthetic content.
- `docs/dogfood-report.md` contains only aggregate metrics and sanitized
  observations.
- README explicitly warns that indexes contain sensitive derived content.

### Pickle safety

- `np.load()` in `indexer.py:267` uses `allow_pickle=False`.

## Findings

1. **No security or privacy blockers found.** The beta release is not
   blocked from a privacy/security perspective.

2. **Minor observation**: `docs.jsonl` contains plain-text chunks from
   notes. This is expected and documented. Users should add their index
   directories to `.gitignore` — the project already ships a default
   `.gitignore` that covers common patterns.

3. **Minor observation**: The build success message prints an absolute
   path. This is intentional (user feedback). The stored paths are
   relative.

## Conclusion

RC readiness is not blocked from a privacy/security perspective.
