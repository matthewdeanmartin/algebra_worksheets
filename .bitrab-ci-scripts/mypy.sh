#!/usr/bin/env bash
set -euo pipefail
source ./.bitrab-ci-scripts/setup.sh
uv run mypy --hide-error-context algebra_worksheets tests
