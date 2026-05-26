# Alpha smoke test — v0.12.0a1

Procedure to verify that the alpha release installs, builds an index, and
executes all three search modes correctly.

## Prerequisites

- Python 3.10+
- `git` (for install from tag)
- Internet connection on first run (downloads the default embedding model
  ~470 MB to `~/.cache/fastembed/`)

## 1. Install from tag

```bash
python3 -m venv /tmp/semantic-index-alpha-test
source /tmp/semantic-index-alpha-test/bin/activate

pip install --upgrade pip
pip install "git+https://github.com/fabek128/semantic-index.git@v0.12.0-alpha.1"
```

## 2. Verify CLI

```bash
semantic-index --help
semantic-index version
```

Expected:

```
semantic-index 0.12.0a1
```

## 3. Create test notes

```bash
mkdir -p /tmp/si-notes

cat > /tmp/si-notes/animals.md <<'EOF'
# Animals

## Mammals

Foxes are quick and clever animals.

## Birds

Eagles can fly.
EOF

cat > /tmp/si-notes/programming.md <<'EOF'
# Programming

## Python

Python supports multiple programming paradigms.

## CLI

Command line tools are useful for AI agents.
EOF
```

## 4. Build index

```bash
semantic-index build /tmp/si-notes --out /tmp/si-index
```

Expected output:

```
Index built in: /tmp/si-index
  Files discovered: 2
  Chunks indexed:   4
```

Verify index files:

```bash
ls -la /tmp/si-index
```

Expected:

```
manifest.json
docs.jsonl
index.npz
```

## 5. Test search modes

### Semantic search

```bash
semantic-index search "quick animal" --index /tmp/si-index
```

### Lexical search

```bash
semantic-index search "Python" --index /tmp/si-index --mode lexical
```

### Hybrid search

```bash
semantic-index search "command line agents" --index /tmp/si-index --mode hybrid
```

### JSON output

```bash
semantic-index search "Python" --index /tmp/si-index --format json
```

### JSONL output

```bash
semantic-index search "Python" --index /tmp/si-index --format jsonl
```

### Limited output

```bash
semantic-index search "Python" --index /tmp/si-index --max-chars 40
```

## 6. Cleanup

```bash
rm -rf /tmp/si-notes /tmp/si-index
deactivate
rm -rf /tmp/semantic-index-alpha-test
```

## Checklist

| Step | Command | Expected |
| --- | --- | --- |
| Help | `semantic-index --help` | usage help |
| Version | `semantic-index version` | `0.12.0a1` |
| Build | `semantic-index build /tmp/si-notes --out /tmp/si-index` | 2 files, 4 chunks |
| Files | `ls /tmp/si-index` | `manifest.json`, `docs.jsonl`, `index.npz` |
| Search semantic | `semantic-index search "quick animal" --index /tmp/si-index` | ranked results |
| Search lexical | `semantic-index search "Python" --index /tmp/si-index --mode lexical` | ranked results |
| Search hybrid | `semantic-index search "command line agents" --index /tmp/si-index --mode hybrid` | ranked results |
| Format JSON | `semantic-index search "Python" --index /tmp/si-index --format json` | JSON array |
| Format JSONL | `semantic-index search "Python" --index /tmp/si-index --format jsonl` | JSON lines |
| Max chars | `semantic-index search "Python" --index /tmp/si-index --max-chars 40` | truncated text |
