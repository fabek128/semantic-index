#!/usr/bin/env bash
# release-smoke.sh — End-to-end release smoke test for semantic-index
#
# Usage:
#   bash scripts/release-smoke.sh [install-source]
#
#   install-source: Path or pip install target (default: ".")
#
# Requirements:
#   - Python 3.10+
#   - Internet on first run (downloads default embedding model ~470 MB)

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
SMOKE_ROOT="/tmp/semantic-index-smoke-$$"
INSTALL_SOURCE="${1:-.}"

PASS=0
FAIL=0
STEP=0

pass() { PASS=$((PASS + 1)); }
fail() { FAIL=$((FAIL + 1)); echo "  FAIL: $*"; }
section() { STEP=$((STEP + 1)); echo "--- Step $STEP: $* ---"; }

cleanup() { rm -rf "$SMOKE_ROOT"; }
trap cleanup EXIT

echo "=== semantic-index release smoke test ==="
echo "Install source: $INSTALL_SOURCE"
echo "Temp root:      $SMOKE_ROOT"
echo ""

# ----- Step 1 -----
section "Install"
python3 -m venv "$SMOKE_ROOT/venv"
# shellcheck disable=SC1091
source "$SMOKE_ROOT/venv/bin/activate"
pip install --upgrade pip -q
case "$INSTALL_SOURCE" in
    git+*) pip install "$INSTALL_SOURCE" -q ;;
    *)     pip install -e "$INSTALL_SOURCE" -q ;;
esac
pass

# ----- Step 2 -----
section "CLI basics"
semantic-index --help > /dev/null 2>&1 && pass || fail "semantic-index --help"
VERSION_OUT=$(semantic-index version 2>&1)
echo "  Version: $VERSION_OUT"
if [[ "$VERSION_OUT" =~ ^semantic-index\ [0-9]+\.[0-9]+\.[0-9] ]]; then
    pass
else
    fail "version format: got '$VERSION_OUT'"
fi

# ----- Step 3 -----
section "Create test notes"
mkdir -p "$SMOKE_ROOT/notes"
cat > "$SMOKE_ROOT/notes/animals.md" <<'EOF'
# Animals

## Mammals

Foxes are quick and clever animals.

## Birds

Eagles can fly.
EOF
cat > "$SMOKE_ROOT/notes/programming.md" <<'EOF'
# Programming

## Python

Python supports multiple programming paradigms.

## CLI

Command line tools are useful for AI agents.
EOF
pass

# ----- Step 4 -----
section "Build index"
BUILD_OUT=$(semantic-index build "$SMOKE_ROOT/notes" --out "$SMOKE_ROOT/index" 2>&1 || true)
# Print only summary lines, ignore UserWarning
echo "$BUILD_OUT" | grep -E "Index built|Files discovered|Chunks indexed" || true

# Extract counts - use grep -oE without Perl regex for macOS compat
FILES=$(echo "$BUILD_OUT" | awk '/Files discovered:/ {print $NF}' || echo "0")
CHUNKS=$(echo "$BUILD_OUT" | awk '/Chunks indexed:/ {print $NF}' || echo "0")

if [[ "$FILES" -ge 1 ]] && [[ "$CHUNKS" -ge 1 ]]; then
    pass
else
    fail "build: files=$FILES chunks=$CHUNKS"
fi

for f in manifest.json docs.jsonl index.npz; do
    [[ -f "$SMOKE_ROOT/index/$f" ]] && pass || fail "missing $f"
done

# ----- Step 5 -----
section "Search modes"

search_ok() {
    local label="$1" desc="$2"
    shift 2
    echo "  $desc"
    # Capture stdout separately from stderr to filter warnings
    local stdout_file stderr_file rc
    stdout_file=$(mktemp)
    stderr_file=$(mktemp)
    "$@" > "$stdout_file" 2>"$stderr_file" && rc=0 || rc=$?
    local out
    out=$(cat "$stdout_file")
    rm -f "$stdout_file" "$stderr_file"

    if [[ "$rc" -ne 0 ]]; then
        fail "$label: exit code $rc"
        return 1
    fi
    # Look for score lines or JSON score keys in stdout
    if echo "$out" | grep -qE '^[[:space:]]*[0-9]+\.[0-9]+' || echo "$out" | grep -q '"score"'; then
        pass
    else
        fail "$label: no results"
        echo "    $(echo "$out" | head -4)"
    fi
}

search_ok "semantic" "semantic (default)" semantic-index search "quick animal" --index "$SMOKE_ROOT/index"
search_ok "lexical"  "lexical"            semantic-index search "Python" --index "$SMOKE_ROOT/index" --mode lexical
search_ok "hybrid"   "hybrid"             semantic-index search "command line agents" --index "$SMOKE_ROOT/index" --mode hybrid

# ----- Step 6 -----
section "Output formats"

# JSON: capture stdout only
json_out=$(semantic-index search "Python" --index "$SMOKE_ROOT/index" --format json 2>/dev/null || true)
python3 -c "
import json, sys
data = json.loads(sys.argv[1])
assert isinstance(data, list) and len(data) > 0
for item in data:
    assert 'score' in item
    assert 'path' in item
    assert 'text' in item
    assert 'heading' in item
" "$json_out" 2>/dev/null && pass || fail "JSON: invalid or missing fields"

# JSONL: capture stdout only
jsonl_out=$(semantic-index search "Python" --index "$SMOKE_ROOT/index" --format jsonl 2>/dev/null || true)
valid=true
while IFS= read -r line; do
    [[ -z "$line" ]] && continue
    python3 -c "import json; d=json.loads('''$line'''); assert 'score' in d; assert 'path' in d" 2>/dev/null || { valid=false; break; }
done <<< "$jsonl_out"
$valid && pass || fail "JSONL: invalid line"

# --max-chars: capture stdout only
mc_out=$(semantic-index search "Python" --index "$SMOKE_ROOT/index" --max-chars 40 2>/dev/null || true)
mc_len=$(echo "$mc_out" | grep -vE '^[[:space:]]*[0-9]+\.[0-9]+' | grep -v "^$" | grep -v "\.md" | awk '{print length}' | sort -rn | head -1)
if [[ -n "$mc_len" ]] && [[ "$mc_len" -le 45 ]]; then
    pass
else
    fail "--max-chars 40: longest line ${mc_len:-0} chars (expected <= 45)"
fi

# ----- Summary -----
echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="

deactivate

if [[ "$FAIL" -gt 0 ]]; then
    exit 1
fi
