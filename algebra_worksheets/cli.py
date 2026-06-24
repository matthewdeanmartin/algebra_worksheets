"""Command-line entry point for algebra_worksheets."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from algebra_worksheets.__about__ import __version__
from algebra_worksheets.compile import EngineNotFoundError, compile_to_pdf
from algebra_worksheets.generators.substitution import generate_systems
from algebra_worksheets.model import Worksheet
from algebra_worksheets.render import latex

_DEFAULT_INSTRUCTIONS = "Solve each system of equations by substitution. Show your work."


def _build_parser() -> argparse.ArgumentParser:
    """Build the argument parser.

    Returns:
        The configured top-level parser.
    """
    parser = argparse.ArgumentParser(
        prog="algebra_worksheets",
        description="Generate printable algebra worksheets with answer keys.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = parser.add_subparsers(dest="command", required=True)
    gen = sub.add_parser("generate", help="Generate a worksheet and answer key.")
    gen.add_argument("-n", "--count", type=int, default=20, help="Number of problems (default: 20).")
    gen.add_argument("--seed", type=int, default=None, help="RNG seed for reproducible output.")
    gen.add_argument("--type", choices=["substitution"], default="substitution", help="Problem type.")
    gen.add_argument("--coef-min", type=int, default=-9, help="Minimum coefficient (default: -9).")
    gen.add_argument("--coef-max", type=int, default=9, help="Maximum coefficient (default: 9).")
    gen.add_argument("--sol-min", type=int, default=-10, help="Minimum solution value (default: -10).")
    gen.add_argument("--sol-max", type=int, default=10, help="Maximum solution value (default: 10).")
    gen.add_argument("--paper", choices=["letter", "a4"], default="letter", help="Page size.")
    gen.add_argument("--columns", type=int, default=2, help="Worksheet problem columns (default: 2).")
    gen.add_argument("--backend", choices=["latex"], default="latex", help="Rendering backend.")
    gen.add_argument(
        "--engine",
        choices=["auto", "tectonic", "latexmk", "pdflatex"],
        default="auto",
        help="LaTeX engine (default: auto-detect).",
    )
    gen.add_argument("--title", default="Systems of Equations", help="Worksheet title.")
    gen.add_argument("--emit", choices=["pdf", "source"], default="pdf", help="Emit PDF or source.")
    gen.add_argument("-o", "--out", default="out/worksheet", help="Output basename.")
    gen.add_argument("--no-answer-key", action="store_true", help="Skip the answer key.")
    gen.add_argument("--key-only", action="store_true", help="Generate only the answer key.")
    gen.set_defaults(func=_cmd_generate)
    return parser


def _cmd_generate(args: argparse.Namespace) -> int:
    """Handle the ``generate`` subcommand.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Process exit code.
    """
    if args.count < 0:
        print("error: --count must be non-negative", file=sys.stderr)
        return 2

    systems = generate_systems(
        args.count,
        seed=args.seed,
        sol_min=args.sol_min,
        sol_max=args.sol_max,
        coef_min=args.coef_min,
        coef_max=args.coef_max,
    )
    worksheet = Worksheet(
        title=args.title,
        instructions=_DEFAULT_INSTRUCTIONS,
        problems=systems,
        seed=args.seed if args.seed is not None else -1,
    )

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    want_worksheet = not args.key_only
    want_key = not args.no_answer_key or args.key_only

    suffix = ".tex" if args.emit == "source" else ".pdf"
    written: list[Path] = []

    try:
        if want_worksheet:
            source = latex.render_worksheet(worksheet, paper=args.paper, columns=args.columns)
            written.append(_emit(source, out.with_suffix(suffix), args))
        if want_key:
            key_source = latex.render_answer_key(worksheet, paper=args.paper)
            key_path = out.with_name(out.name + "_key").with_suffix(suffix)
            written.append(_emit(key_source, key_path, args))
    except EngineNotFoundError as exc:
        print(f"error: {exc}", file=sys.stderr)
        print("hint: re-run with `--emit source` to write .tex files instead.", file=sys.stderr)
        return 1

    for path in written:
        print(f"wrote {path}")
    return 0


def _emit(source: str, path: Path, args: argparse.Namespace) -> Path:
    """Write LaTeX source or a compiled PDF to ``path``.

    Args:
        source: LaTeX document source.
        path: Destination path (``.tex`` or ``.pdf``).
        args: Parsed CLI arguments (for the engine and emit mode).

    Returns:
        The written path.
    """
    if args.emit == "source":
        path.write_text(source, encoding="utf-8")
        return path
    return compile_to_pdf(source, path, engine=args.engine)


def main() -> None:
    """Run the algebra_worksheets CLI."""
    parser = _build_parser()
    args = parser.parse_args()
    raise SystemExit(args.func(args))


if __name__ == "__main__":
    main()
