r"""LaTeX rendering backend for worksheets and answer keys.

Uses Jinja2 with TeX-safe delimiters (``\VAR{}`` / ``\BLOCK{}``) so template
syntax does not collide with LaTeX's own braces and percent comments.
"""

from __future__ import annotations

from pathlib import Path

import jinja2

from algebra_worksheets.model import LinearEquation, System, Worksheet

_TEMPLATE_DIR = Path(__file__).parent / "templates"

_PAPER_SIZES = {"letter": "letterpaper", "a4": "a4paper"}


def _environment() -> jinja2.Environment:
    """Build a Jinja2 environment configured for LaTeX output.

    Returns:
        An environment whose delimiters are safe to embed in ``.tex`` source.
    """
    # autoescape must be off: output is LaTeX, not HTML. HTML escaping would
    # corrupt .tex source, and there is no browser/XSS surface (output is a
    # local PDF). Input is integer coefficients, not untrusted markup.
    return jinja2.Environment(  # nosec B701
        block_start_string=r"\BLOCK{",
        block_end_string="}",
        variable_start_string=r"\VAR{",
        variable_end_string="}",
        comment_start_string=r"\#{",
        comment_end_string="}",
        line_statement_prefix="%%",
        trim_blocks=True,
        lstrip_blocks=True,
        autoescape=False,
        loader=jinja2.FileSystemLoader(str(_TEMPLATE_DIR)),
    )


def _term(coef: int, var: str, first: bool) -> str:
    """Render a single ``coef * var`` term with its sign.

    Args:
        coef: Integer coefficient (assumed non-zero).
        var: Variable name, e.g. ``"x"``.
        first: Whether this is the leading term (controls a leading ``+``).

    Returns:
        A LaTeX fragment such as ``"2x"``, ``"- y"`` or ``"+ 3y"``.
    """
    sign = "-" if coef < 0 else "+"
    magnitude = abs(coef)
    body = var if magnitude == 1 else f"{magnitude}{var}"
    if first:
        return f"-{body}" if coef < 0 else body
    return f"{sign} {body}"


def equation_to_latex(eq: LinearEquation) -> str:
    """Render an equation as a LaTeX math fragment ``a x + b y = c``.

    Args:
        eq: The equation to render.

    Returns:
        A LaTeX string (without surrounding math delimiters).
    """
    return f"{_term(eq.a, 'x', True)} {_term(eq.b, 'y', False)} = {eq.c}"


def system_to_latex(system: System) -> str:
    """Render a system as a LaTeX ``cases`` environment.

    Args:
        system: The system to render.

    Returns:
        A LaTeX ``\\begin{cases}...\\end{cases}`` fragment.
    """
    line1 = equation_to_latex(system.eq1)
    line2 = equation_to_latex(system.eq2)
    return r"\begin{cases}" + line1 + r"\\" + line2 + r"\end{cases}"


def solution_to_latex(system: System) -> str:
    """Render a system's solution as ``(x,\\ y)``.

    Args:
        system: The system whose solution to render.

    Returns:
        A LaTeX fragment such as ``"(3,\\ -2)"``.
    """
    x, y = system.solution
    return rf"({x},\ {y})"


def render_worksheet(worksheet: Worksheet, *, paper: str = "letter", columns: int = 2) -> str:
    """Render the student worksheet ``.tex`` source.

    Args:
        worksheet: The worksheet to render.
        paper: Page size, ``"letter"`` or ``"a4"``.
        columns: Number of problem columns.

    Returns:
        Complete LaTeX document source.
    """
    template = _environment().get_template("worksheet.tex.j2")
    return template.render(
        worksheet=worksheet,
        paper=_PAPER_SIZES[paper],
        columns=columns,
        systems=[system_to_latex(s) for s in worksheet.problems],
    )


def render_answer_key(worksheet: Worksheet, *, paper: str = "letter", columns: int = 5) -> str:
    """Render the compact answer-key ``.tex`` source.

    Args:
        worksheet: The worksheet whose answers to render.
        paper: Page size, ``"letter"`` or ``"a4"``.
        columns: Number of answer columns (dense layout).

    Returns:
        Complete LaTeX document source.
    """
    template = _environment().get_template("answer_key.tex.j2")
    return template.render(
        worksheet=worksheet,
        paper=_PAPER_SIZES[paper],
        columns=columns,
        answers=[solution_to_latex(s) for s in worksheet.problems],
    )
