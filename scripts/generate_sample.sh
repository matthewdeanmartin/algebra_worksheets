#!/usr/bin/env bash
# Generate a reproducible sample worksheet + answer key into out/sample.
# Fixed seed so the output is stable for docs/screenshots and quick demos.
#
# Invoked by `make sample`. Produces:
#   out/sample.pdf       student worksheet (24 substitution systems)
#   out/sample_key.pdf   compact answer key (fits on one page)

set -euo pipefail

OUT="out/sample"
mkdir -p out

echo "=== Generating reproducible sample (seed=42, 24 problems) ==="
exec python -m algebra_worksheets generate \
    --type substitution \
    --count 24 \
    --seed 42 \
    --paper letter \
    --backend latex \
    --title "Systems of Equations — Substitution" \
    --out "$OUT"
