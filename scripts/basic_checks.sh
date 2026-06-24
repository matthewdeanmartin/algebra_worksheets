#!/usr/bin/env bash
# Smoke test: exercises the CLI arg parser and verifies basic invocations exit cleanly.
# Counts successes and failures; exits non-zero if any check failed.
# Source an already-active venv before running, or call via `uv run bash scripts/basic_checks.sh`.

set -ou pipefail

PASS=0
FAIL=0
CLI_PYTHON="${PYTHON:-python}"

run_cli() {
    "$CLI_PYTHON" -m algebra_worksheets "$@"
}

check() {
    local desc="$1"
    shift
    if "$@" > /dev/null 2>&1; then
        echo "  PASS: $desc"
        ((PASS++))
    else
        echo "  FAIL: $desc  (cmd: $*)"
        ((FAIL++))
    fi
}

check_fails() {
    local desc="$1"
    shift
    if "$@" > /dev/null 2>&1; then
        echo "  FAIL: $desc  (expected non-zero exit, got 0)"
        ((FAIL++))
    else
        echo "  PASS: $desc"
        ((PASS++))
    fi
}

echo "=== algebra_worksheets basic_checks ==="
echo ""
echo "using: ${CLI_PYTHON} -m algebra_worksheets"
echo ""

echo "--- global flags ---"
check "algebra_worksheets --help"    run_cli --help
check "algebra_worksheets --version" run_cli --version

echo ""
echo "--- generate subcommand ---"
SMOKE_OUT="$(mktemp -d)/ws"
check       "generate --help"           run_cli generate --help
check       "generate --emit source"    run_cli generate -n 4 --seed 1 --emit source -o "$SMOKE_OUT"
check_fails "generate rejects -n -1"    run_cli generate -n -1 --emit source -o "$SMOKE_OUT"

echo ""
echo "=== Results: ${PASS} passed, ${FAIL} failed ==="

if [ "$FAIL" -gt 0 ]; then
    exit 1
fi
