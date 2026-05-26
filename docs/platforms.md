# Supported platforms

## Operating systems

| OS | Status | Notes |
| --- | --- | --- |
| **Linux** | ✅ Fully supported | CI-tested on Python 3.10 and 3.13 |
| **macOS** | ✅ Supported | CI-tested on Python 3.13 |
| **Windows** | ❌ Not tested | Not CI-tested. Path handling, symlink behavior, and shell
commands may differ. Contributions welcome. |

## Python versions

- **3.10**: minimum supported version.
- **3.13**: latest tested version.

Intermediate Python 3.11 and 3.12 are expected to work but are not in the
CI matrix.

## CI matrix

The CI workflow (`.github/workflows/ci.yml`) runs on every push and pull
request to `main`:

- Ubuntu + Python 3.10
- Ubuntu + Python 3.13
- macOS + Python 3.13

All jobs run the full unit test suite, compile check, and CLI smoke tests.
