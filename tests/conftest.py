"""Shared pytest configuration."""

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register the ``--update-golden`` flag.

    Args:
        parser: Pytest's command-line parser.
    """
    parser.addoption(
        "--update-golden",
        action="store_true",
        default=False,
        help="Rewrite golden snapshot files from current output.",
    )
