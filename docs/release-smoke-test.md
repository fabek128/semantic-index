# Release smoke test

A scripted end-to-end smoke test for `semantic-index` releases.

## Script

`scripts/release-smoke.sh` runs the full release validation in an isolated
temporary environment:

1. Creates a fresh Python virtual environment.
2. Installs `semantic-index` from the specified source.
3. Verifies `--help` and `version`.
4. Creates two small Markdown test files.
5. Runs `semantic-index build` and verifies output files.
6. Tests semantic, lexical, and hybrid search modes.
7. Validates JSON and JSONL output formats.
8. Verifies `--max-chars` output length.
9. Cleans up all temporary files.

## Usage

### Test a local checkout

```bash
bash scripts/release-smoke.sh .
```

### Test an installed tag

```bash
bash scripts/release-smoke.sh "git+https://github.com/fabek128/semantic-index.git@v0.12.0-beta.1"
```

## Exit code

- `0`: all checks passed.
- `1`: one or more checks failed.

## Output example

```
=== semantic-index release smoke test ===
Install source: .
Temp root:      /tmp/semantic-index-smoke-12345

--- Step 1: Install ---
Install OK
--- Step 2: CLI basics ---
  Version: semantic-index 0.12.0b1
...
=== Results: 12 passed, 0 failed ===
```

## Notes

- The first build downloads the default embedding model (~470 MB) and caches
  it in `~/.cache/fastembed/`. Subsequent runs use the cached model.
- Exact ranking scores vary by model version. The script checks for
  well-formed output, not exact scores.
- All temporary data is written to `/tmp/semantic-index-smoke-*` and deleted
  on exit.
