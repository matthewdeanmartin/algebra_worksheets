"""Tests for the LaTeX rendering backend, including a golden-file snapshot."""

from pathlib import Path

from algebra_worksheets.generators.substitution import generate_systems
from algebra_worksheets.model import LinearEquation, System, Worksheet
from algebra_worksheets.render import latex

_GOLDEN_DIR = Path(__file__).parent / "golden"


def _sample_worksheet() -> Worksheet:
    """Build a small fixed worksheet for snapshot testing.

    Returns:
        A deterministic worksheet.
    """
    return Worksheet(
        title="Systems of Equations",
        instructions="Solve each system of equations by substitution. Show your work.",
        problems=generate_systems(4, seed=42),
        seed=42,
    )


def test_equation_to_latex_signs_and_units() -> None:
    """Coefficient signs and unit coefficients render correctly."""
    assert latex.equation_to_latex(LinearEquation(1, 1, 0)) == "x + y = 0"
    assert latex.equation_to_latex(LinearEquation(-1, 1, 8)) == "-x + y = 8"
    assert latex.equation_to_latex(LinearEquation(2, -3, 12)) == "2x - 3y = 12"
    assert latex.equation_to_latex(LinearEquation(-9, 1, 33)) == "-9x + y = 33"


def test_system_to_latex_uses_cases() -> None:
    """A system renders as a LaTeX cases environment."""
    system = System(LinearEquation(1, 1, 1), LinearEquation(2, -1, 8), (3, -2))
    out = latex.system_to_latex(system)
    assert out.startswith(r"\begin{cases}")
    assert out.endswith(r"\end{cases}")
    assert r"\\" in out


def test_solution_to_latex() -> None:
    """A solution renders as an ordered pair."""
    system = System(LinearEquation(1, 1, 1), LinearEquation(2, -1, 8), (3, -2))
    assert latex.solution_to_latex(system) == r"(3,\ -2)"


def test_render_worksheet_structure() -> None:
    """The worksheet document has the expected LaTeX scaffolding."""
    out = latex.render_worksheet(_sample_worksheet(), paper="letter", columns=2)
    assert r"\documentclass[11pt,letterpaper]{article}" in out
    assert r"\begin{document}" in out and r"\end{document}" in out
    assert r"\begin{multicols}{2}" in out
    assert out.count(r"\item") == 4


def test_render_answer_key_is_compact() -> None:
    """The answer key uses a dense multi-column layout."""
    out = latex.render_answer_key(_sample_worksheet(), paper="a4")
    assert r"\documentclass[10pt,a4paper]{article}" in out
    assert r"\begin{multicols}{5}" in out
    assert out.count(r"\item") == 4


def test_worksheet_golden(request: object) -> None:
    """Rendered worksheet matches the committed golden snapshot.

    Args:
        request: Pytest request fixture (used to detect ``--update-golden``).
    """
    out = latex.render_worksheet(_sample_worksheet(), paper="letter", columns=2)
    golden = _GOLDEN_DIR / "worksheet.tex"
    if getattr(request.config.option, "update_golden", False):  # type: ignore[attr-defined]
        golden.parent.mkdir(parents=True, exist_ok=True)
        golden.write_text(out, encoding="utf-8")
    assert out == golden.read_text(encoding="utf-8")


def test_answer_key_golden(request: object) -> None:
    """Rendered answer key matches the committed golden snapshot.

    Args:
        request: Pytest request fixture (used to detect ``--update-golden``).
    """
    out = latex.render_answer_key(_sample_worksheet(), paper="letter")
    golden = _GOLDEN_DIR / "answer_key.tex"
    if getattr(request.config.option, "update_golden", False):  # type: ignore[attr-defined]
        golden.parent.mkdir(parents=True, exist_ok=True)
        golden.write_text(out, encoding="utf-8")
    assert out == golden.read_text(encoding="utf-8")
