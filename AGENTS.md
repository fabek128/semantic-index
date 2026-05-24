# Agent instructions

These instructions apply to all AI coding agents working in this repository.

## Project summary

`semantic-index` is a CLI-first local semantic search tool for Markdown notes.
The project is intentionally local-only and database-free.

## Before making changes

1. Read `README.md`.
2. Read the relevant files in `docs/`.
3. Keep changes small, explicit, and easy to review.

## Current scope

Implemented:

- Python package scaffold.
- Minimal CLI entrypoint.
- `semantic-index --help`.
- `semantic-index version`.

Not implemented yet:

- Markdown discovery.
- Markdown chunking.
- Embedding generation.
- Search.
- Index persistence.

## Constraints

- Prefer Python standard library until dependencies are justified.
- Do not add APIs, web servers, databases, or external services.
- Do not implement full embedding/search unless explicitly requested.
- Future indexing should use local files only.
- Future persistence should prefer `docs.jsonl` + `index.npz`.
- Avoid `pickle` for index persistence.

## Security

- Treat Markdown notes, generated chunks, embeddings, and indexes as potentially sensitive.
- Do not print or commit secrets.
- Do not read `.env` unless a task explicitly requires environment configuration.
- Never include secret values in docs, logs, commits, PRs, or responses.
- Prefer safe defaults and explicit user-provided paths.

## Verification

For CLI-only changes, run at least:

```bash
PYTHONPATH=src python -m semantic_index --help
PYTHONPATH=src python -m semantic_index version
python -m compileall -q src
```

If the package metadata or entrypoint changes, also verify an editable install:

```bash
python -m pip install -e .
semantic-index --help
semantic-index version
```
