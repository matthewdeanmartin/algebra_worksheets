"""Compile LaTeX source to PDF using whichever engine is available.

Detection order: ``tectonic`` (self-contained, recommended) → ``latexmk`` →
``pdflatex``. The chosen engine can be overridden explicitly.
"""

from __future__ import annotations

import shutil
import subprocess  # nosec B404  # used with fixed argv, shell=False
import tempfile
from pathlib import Path

_ENGINES = ("tectonic", "latexmk", "pdflatex")


class EngineNotFoundError(RuntimeError):
    """Raised when no usable LaTeX engine is available."""


def detect_engine(preferred: str = "auto") -> str:
    """Return the name of an available LaTeX engine.

    Args:
        preferred: Engine name to require, or ``"auto"`` to pick the first
            available from the detection order.

    Returns:
        The resolved engine name.

    Raises:
        EngineNotFoundError: If the requested (or any) engine is unavailable.
    """
    if preferred != "auto":
        if shutil.which(preferred) is None:
            raise EngineNotFoundError(f"requested engine {preferred!r} not found on PATH")
        return preferred
    for engine in _ENGINES:
        if shutil.which(engine) is not None:
            return engine
    raise EngineNotFoundError("no LaTeX engine found; install tectonic (recommended), latexmk, or pdflatex")


def _command(engine: str, tex_path: Path, out_dir: Path) -> list[str]:
    """Build the argv for the given engine.

    Args:
        engine: Resolved engine name.
        tex_path: Path to the ``.tex`` source.
        out_dir: Directory to write the PDF into.

    Returns:
        The command argument vector.
    """
    if engine == "tectonic":
        return ["tectonic", "--outdir", str(out_dir), str(tex_path)]
    if engine == "latexmk":
        return ["latexmk", "-pdf", "-interaction=nonstopmode", f"-outdir={out_dir}", str(tex_path)]
    return ["pdflatex", "-interaction=nonstopmode", f"-output-directory={out_dir}", str(tex_path)]


def compile_to_pdf(source: str, out_pdf: Path, *, engine: str = "auto") -> Path:
    """Compile LaTeX ``source`` and write the resulting PDF to ``out_pdf``.

    Args:
        source: Complete LaTeX document source.
        out_pdf: Destination path for the compiled PDF.
        engine: Engine to use, or ``"auto"`` to detect one.

    Returns:
        The path to the written PDF (``out_pdf``).

    Raises:
        EngineNotFoundError: If no engine is available.
        subprocess.CalledProcessError: If compilation fails.
    """
    resolved = detect_engine(engine)
    out_pdf.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmp_dir = Path(tmp)
        tex_path = tmp_dir / "doc.tex"
        tex_path.write_text(source, encoding="utf-8")
        cmd = _command(resolved, tex_path, tmp_dir)
        subprocess.run(cmd, check=True, capture_output=True)  # nosec B603
        produced = tmp_dir / "doc.pdf"
        shutil.move(str(produced), str(out_pdf))
    return out_pdf
