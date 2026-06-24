#!/usr/bin/env bash
# Emit the worksheet/answer-key *source* (LaTeX or HTML) without compiling a PDF.
# Useful for inspecting templating output and for golden-file tests.
#
# Invoked by `make worksheet-source`. Env knobs:
#   COUNT  number of problems          (default: 20)
#   SEED   RNG seed                     (default: unset → random)
#   OUT    output basename             (default: out/worksheet)
#   PAPER  page size letter|a4         (default: letter)
#
# Produces:  ${OUT}.tex  and  ${OUT}_key.tex  (or .html for the html backend)

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
    --emit source
    --out "$OUT")

if [[ -n "${SEED:-}" ]]; then
    args+=(--seed "$SEED")
fi

echo "=== Emitting worksheet source for ${OUT} (no PDF compile) ==="
exec python -m algebra_worksheets "${args[@]}"
