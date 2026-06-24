#!/usr/bin/env bash
set -euo pipefail
source ./.bitrab-ci-scripts/setup.sh
uv run isort --check-only algebra_worksheets tests
uv run black --check algebra_worksheets tests
uv run ruff check --quiet algebra_worksheets tests
uv run pylint --score=n --reports=n --rcfile=.pylintrc algebra_worksheets
uv run pylint --score=n --reports=n --rcfile=.pylintrc_tests tests
