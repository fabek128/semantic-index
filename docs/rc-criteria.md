# RC readiness criteria

Checklist for declaring Release Candidate readiness. A release candidate
(`1.0.0rc1`) should be prepared only when all criteria below are met.
Otherwise, publish another beta (`0.x.xbN`) to address remaining items.

## Checklist

### Code and CI

- [ ] All open issues in the active milestone are closed or explicitly
      deferred with a documented rationale.
- [ ] CI is green on `main` for all configured platforms (Linux + macOS).
- [ ] Full unit suite passes (`python -m unittest discover`).
- [ ] Compile checks pass (`python -m compileall -q src tests`).

### Smoke and artifact validation

- [ ] Release smoke test passes from local editable install
      (`bash scripts/release-smoke.sh .`).
- [ ] sdist and wheel build successfully (`python -m build`).
- [ ] Wheel installs in a clean virtual environment outside the source
      tree, CLI entry points work.

### Search and output quality

- [ ] All three search modes (semantic, lexical, hybrid) produce correct
      results on representative corpora.
- [ ] JSON and JSONL output formats produce valid, parseable data with
      all expected fields.
- [ ] Output bounds (`--top-k`, `--max-chars`) work correctly.
- [ ] Specific error messages for: missing index, corrupt index, invalid
      flags, permissions, empty directories.

### Documentation

- [ ] README accurately describes current scope, installation, and usage.
- [ ] CLI contract doc (`docs/cli-contract.md`) matches actual behavior.
- [ ] Troubleshooting guide (`docs/troubleshooting.md`) covers common
      failure modes.
- [ ] Agent integration guide (`docs/agent-integration.md`) exists and
      includes security/privacy guidance.
- [ ] Changelog is up to date.

### Security and privacy

- [ ] Privacy/security review is complete with no blockers.
- [ ] `.gitignore` covers all generated artifacts.
- [ ] `np.load` uses `allow_pickle=False`.
- [ ] No stack traces are exposed in user-facing errors.
- [ ] Documentation warns that indexes contain sensitive derived content.

### Beta assessment

- [ ] Dogfood validation completed on realistic notes with no RC blockers.
- [ ] Scale/performance baseline documented.
- [ ] Known limitations are documented and acceptable for RC.

## If criteria are not met

If any item in the checklist is incomplete or failed, the next release
should be another beta (`0.x.xbN`) rather than an RC. Create a new
milestone for the remaining items and continue iterating.

## Recommended next version

Based on the current state:

| Target | When |
| --- | --- |
| `0.13.0b1` / `v0.13.0-beta.1` | After closing remaining v0.13 issues, if any RC criteria are unmet. |
| `1.0.0rc1` / `v1.0.0-rc.1` | Only when all RC criteria above are greenlit by explicit review. |
