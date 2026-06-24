#!/usr/bin/env bash
# Generate a worksheet PDF plus its matching compact answer-key PDF.
#
# Invoked by `make worksheet`. Knobs are passed as environment variables so the
# Makefile (or you) can override them:
#   COUNT  number of problems          (default: 20)
#   SEED   RNG seed for reproducibility (default: unset → random)
#   OUT    output basename             (default: out/worksheet)
#   PAPER  page size letter|a4         (default: letter)
#
# Produces:  ${OUT}.pdf  and  ${OUT}_key.pdf
#
# NOTE: the `generate` subcommand is implemented in Phase 1+ of spec/roadmap.md.
# Until then this script documents and exercises the intended interface.

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
    --out "$OUT")

if [[ -n "${SEED:-}" ]]; then
    args+=(--seed "$SEED")
fi

echo "=== Generating worksheet: ${OUT}.pdf (+ ${OUT}_key.pdf) ==="
echo "    problems=${COUNT} paper=${PAPER} seed=${SEED:-<random>}"
exec python -m algebra_worksheets "${args[@]}"
