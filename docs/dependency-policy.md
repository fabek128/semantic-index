# Dependency policy

## Current dependencies

| Package | Version range | Purpose |
| --- | --- | --- |
| `fastembed` | `>=0.5.0,<1.0.0` | Local embedding generation |
| `numpy` | `>=1.26.0,<3.0.0` | Embedding vector operations and index persistence |

## Policy

1. **Lower bounds** are set to the minimum version that provides the
   required APIs. This is usually the version used during initial
   implementation.

2. **Upper bounds** are set to the next major version to prevent
   breakage from incompatible upstream releases. They are updated
   when a new major version is tested and confirmed compatible.

3. **Only runtime dependencies** are declared in `pyproject.toml`.
   Build and test dependencies (`build`, `unittest`) are not declared
   — they are expected to be installed by the developer or CI.

4. **No lockfile**. The project does not ship a lockfile. Reproducible
   installs are achieved via version constraints and CI testing.

## Supported Python versions

- Minimum: **3.10**
- CI-tested: 3.10, 3.13

Intermediate versions (3.11, 3.12) are expected to work but are not
in the CI matrix.

## Updating dependencies

When updating a dependency:

1. Update the version range in `pyproject.toml`.
2. Run the full unit test suite (`python -m unittest discover`).
3. Run the release smoke test (`bash scripts/release-smoke.sh .`).
4. Document the change in `CHANGELOG.md`.

## Security

- All dependencies are pure-Python or have published wheels.
- `fastembed` downloads model files from Hugging Face on first use.
  Model files are cached locally. No note content is sent to external
  services.
- `numpy` is used only for array operations on local data.
