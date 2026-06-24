"""Tests for the ``generate`` CLI subcommand."""

import sys
from pathlib import Path

import pytest

from algebra_worksheets import cli


def _run(args: list[str]) -> int:
    """Invoke the CLI with ``args`` and return its exit code.

    Args:
        args: Arguments after the program name.

    Returns:
        The exit code raised via ``SystemExit``.
    """
    with pytest.raises(SystemExit) as exc:
        sys.argv = ["algebra_worksheets", *args]
        cli.main()
    code = exc.value.code
    return int(code) if code is not None else 0


def test_emit_source_writes_both_files(tmp_path: Path) -> None:
    """Source emission writes worksheet and answer-key .tex files."""
    base = tmp_path / "ws"
    code = _run(["generate", "-n", "5", "--seed", "1", "--emit", "source", "-o", str(base)])
    assert code == 0
    assert (tmp_path / "ws.tex").exists()
    assert (tmp_path / "ws_key.tex").exists()


def test_no_answer_key(tmp_path: Path) -> None:
    """--no-answer-key suppresses the key file."""
    base = tmp_path / "ws"
    _run(["generate", "-n", "3", "--seed", "1", "--emit", "source", "--no-answer-key", "-o", str(base)])
    assert (tmp_path / "ws.tex").exists()
    assert not (tmp_path / "ws_key.tex").exists()


def test_key_only(tmp_path: Path) -> None:
    """--key-only writes only the answer key."""
    base = tmp_path / "ws"
    _run(["generate", "-n", "3", "--seed", "1", "--emit", "source", "--key-only", "-o", str(base)])
    assert not (tmp_path / "ws.tex").exists()
    assert (tmp_path / "ws_key.tex").exists()


def test_negative_count_rejected(tmp_path: Path) -> None:
    """A negative count exits with code 2."""
    code = _run(["generate", "-n", "-1", "--emit", "source", "-o", str(tmp_path / "ws")])
    assert code == 2


def test_seeded_source_is_reproducible(tmp_path: Path) -> None:
    """Two seeded source runs produce identical worksheet content."""
    for name in ("a", "b"):
        _run(["generate", "-n", "6", "--seed", "7", "--emit", "source", "-o", str(tmp_path / name)])
    assert (tmp_path / "a.tex").read_text() == (tmp_path / "b.tex").read_text()
