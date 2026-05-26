# Artifact build and validation

Instructions for building and validating `semantic-index` distribution
artifacts (sdist and wheel).

## Requirements

- Python 3.10+
- `build` package: `pip install build`

## Build

```bash
python3 -m build --sdist --wheel .
```

Output is written to `dist/`:

```
dist/
  semantic_index-<version>-py3-none-any.whl
  semantic_index-<version>.tar.gz
```

The `dist/` directory is Git-ignored by default.

## Validate in a clean environment

Install the wheel outside the source tree to confirm the console script
works:

```bash
python3 -m venv /tmp/artifact-check
source /tmp/artifact-check/bin/activate
pip install dist/semantic_index-<version>-py3-none-any.whl
semantic-index --help
semantic-index version
deactivate
rm -rf /tmp/artifact-check
```

## Full release validation

Run the [release smoke test](release-smoke-test.md) against a local
editable install before tagging:

```bash
bash scripts/release-smoke.sh .
```

Then build artifacts, install from wheel in a clean environment, and run
the smoke test against the tag to confirm end-to-end reproducibility:

```bash
bash scripts/release-smoke.sh "git+https://github.com/fabek128/semantic-index.git@v<tag>"
```
