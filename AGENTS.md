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
- `semantic-index build` — Markdown file discovery with path validation,
  excluded dirs, symlink safety, and summary output.

Not implemented yet:

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

## GitHub workflow and planning

Current development stage: **pre-alpha**.

Use the simplest GitHub workflow for this project:

```text
GitHub issue -> branch -> PR -> merge
```

Rules:

- Use the GitHub CLI (`gh`) for GitHub project management tasks, including issues, bugs, pull requests, labels, milestones, Projects, and repository metadata.
- Prefer `gh` over manual browser workflows or ad-hoc API calls when managing this project's GitHub state.
- Track planned work as GitHub issues before starting non-trivial changes.
- Every issue and bug must belong to the repository `fabek128/semantic-index`.
- Every issue and bug must be assigned to the GitHub Project `semantic-index Roadmap` (`https://github.com/users/fabek128/projects/2`).
- Every issue and bug must be assigned to a milestone before implementation starts.
- When Fabian asks an agent to work on an issue, the agent must assign the issue to the active GitHub user and move its Project status to `In Progress` before making code changes.
- When work is paused, blocked, risky, or needs extra context, the agent should add an issue comment with the relevant details, decisions, blockers, or follow-up notes.
- Agents may also add issue comments proactively when they discover useful implementation context that should be preserved for future agents or reviewers.
- If `gh project` reports missing `project` or `read:project` scope, stop and ask Fabian to authorize the GitHub CLI with the required project scope before creating or updating project-backed issues.
- Create a focused branch for each issue or small set of closely related issues.
- Open a PR targeting `main` after finishing work on every issue.
- After finishing issue work, tell Fabian explicitly that the issue work is complete and provide the PR URL.
- Open a PR for review before merging changes into `main`.
- Link PRs to issues using GitHub keywords when appropriate, for example `Fixes #123`.
- Keep issues and PRs small, concrete, and easy for agents to understand.
- Do not expose tokens or credentials in commands, logs, documentation, commits, PRs, or responses.
- Before making destructive or high-impact GitHub changes, confirm the intended repository, scope, and action.

Issue creation checklist:

1. Create or update the GitHub issue with a detailed description, scope, out-of-scope notes, acceptance criteria, documentation requirements, and unit-test requirements.
2. Assign the issue to the correct milestone from the roadmap below.
3. Add the issue to the GitHub Project `semantic-index Roadmap` with `gh project item-add 2 --owner fabek128 --url <issue-url>`.
4. Add appropriate labels when useful, such as `enhancement`, `bug`, or `documentation`.
5. When starting work, assign the issue to the active GitHub user.
6. Move the issue Project status to `In Progress`.
7. Add issue comments for blockers, risks, decisions, or useful extra context.
8. Only then create a branch and start implementation.
9. After completing the issue work, push the branch and open a PR targeting `main`.
10. Tell Fabian that the issue work is complete and include the PR URL in the final response.

Milestone roadmap:

| Milestone | Purpose | Current issues |
| --- | --- | --- |
| `v0.1.0-pre-alpha: Foundation and test baseline` | Keep the existing CLI stable, add baseline unit tests, and document the development/test workflow. | #1 |
| `v0.2.0-pre-alpha: Markdown input pipeline` | Add safe local Markdown discovery and deterministic chunking without embeddings or search. | #2, #3 |
| `v0.3.0-pre-alpha: Local embedding index` | Generate local embeddings and persist `docs.jsonl` + `index.npz` without databases or external services for note contents. | #4 |
| `v0.4.0-pre-alpha: Search and agent retrieval MVP` | Add local search, ranked output, and agent-friendly result formats. | #5 |
| `v0.5.0-pre-alpha: MVP hardening and release readiness` | Improve packaging, docs, errors, security checks, and release readiness after search exists. | Future issues |

## Documentation and testing requirements

- Every process, issue, bug, feature, and behavior change must be documented in detail.
- Every implementation task and bug fix must include unit tests.
- If a task is documentation-only or cannot reasonably include unit tests, document why and run the relevant verification checks.

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
