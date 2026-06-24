#!/usr/bin/env bash
# Generate ONLY the compact answer key PDF (no student worksheet).
#
# Invoked by `make answer-key`. Env knobs:
#   COUNT  number of problems          (default: 20)
#   SEED   RNG seed                     (default: unset → random)
#   OUT    output basename             (default: out/worksheet)
#   PAPER  page size letter|a4         (default: letter)
#
# Produces:  ${OUT}_key.pdf  (dense, multi-column, paper-saving layout)

set -euo pipefail

COUNT="${COUNT:-20}"
OUT="${OUT:-out/worksheet}"
PAPER="${PAPER:-letter}"

mkdir -p "$(dirname "$OUT")"

args=(generate
    --type substitution
    --count "$COUNT"
    --paper "$PAPER"
    --backend latex
    --key-only
    --out "$OUT")

if [[ -n "${SEED:-}" ]]; then
    args+=(--seed "$SEED")
fi

echo "=== Generating compact answer key: ${OUT}_key.pdf ==="
exec python -m algebra_worksheets "${args[@]}"
