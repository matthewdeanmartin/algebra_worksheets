# Algebra Worksheets — Roadmap & Specification

> Generate printable algebra worksheets with matching, compact answer keys.

## 1. Vision

A command-line application that generates **algebra worksheets** as
print-ready PDFs, together with a separate, **compact answer key**. The
proof-of-concept (PoC) focuses on **systems of two linear equations solved by
substitution**, where all solutions are **integers** (negatives allowed).

The output must look good on a home/office printer (US Letter by default, A4
supported) and must not waste paper — the answer key in particular should pack
many answers onto a single page.

## 2. Goals & Non-Goals

### Goals (PoC)

- Generate systems of two linear equations in two unknowns (`x`, `y`).
- Guarantee a **unique integer solution** per system (negatives allowed).
- Render a **worksheet** (problems, generous work space) and a **separate
  answer key** (compact).
- Be driven entirely by an **`argparse`** CLI.
- Deterministic output via a `--seed` for reproducible worksheets.
- Look nice when printed: clean math typesetting, page numbers, title,
  instructions, name/date line.
- A `Makefile` whose generation targets call **`./scripts/*.sh`** bash scripts.

### Non-Goals (PoC — deferred to later phases)

- Other problem types (quadratics, factoring, word problems, elimination).
- Non-integer / fractional answers.
- Web UI or interactive mode.
- Per-student randomized variants at scale (lightly addressed in Phase 5).
- Localization / non-English instructions.

## 3. Rendering Strategy (recommended)

I evaluated three rendering approaches. Recommendation: **build the model and
templating layer renderer-agnostic, ship LaTeX as the primary backend, and HTML
as a no-TeX fallback.**

| Approach | Math quality | Compactness control | Install burden | Verdict |
|---|---|---|---|---|
| **LaTeX** (Jinja2 → `.tex` → `latexmk`/`tectonic`) | Excellent | Excellent (`multicols`, `enumitem`) | Needs a TeX distro **or** `tectonic` | **Primary** |
| **HTML + CSS print** (Jinja2 → HTML → WeasyPrint / browser) | Good (MathML / KaTeX) | Good (CSS columns) | `weasyprint` pip install | **Fallback** |
| **ReportLab** (direct PDF drawing) | Mediocre for math | Total, but manual | Pure pip | Not recommended |

### Why LaTeX is primary

- Best-in-class equation typesetting with zero effort (`$\begin{cases}…\end{cases}$`).
- `multicol` + `enumitem` give precise, paper-saving column layouts — ideal for
  the compact answer key.
- `tectonic` (a single self-contained binary) removes the "install a 4 GB TeX
  distro" objection and is reproducible — we'll document it as the recommended
  engine and let users fall back to `latexmk`/`pdflatex`.

### Why HTML is the fallback

- Users without any TeX engine still get a clean printable artifact.
- `WeasyPrint` renders HTML+CSS → PDF in pure-Python (pip-installable).
- CSS `@page` + `columns` cover headers, margins, and compact answer layout.

### Library choices

- **Templating:** [`Jinja2`](https://jinja.palletsprojects.com/) for both
  backends. For LaTeX, configure a Jinja `Environment` with custom delimiters
  (e.g. `\VAR{ }`, `\BLOCK{ }`) so they don't collide with TeX's `{}`/`%`.
- **Rendering math (HTML backend):** prefer MathML (no JS) for WeasyPrint; allow
  KaTeX for browser-based printing.
- **PDF engine (LaTeX):** `tectonic` (recommended) → `latexmk` → `pdflatex`,
  auto-detected, overridable via `--engine`.
- **PDF engine (HTML):** `weasyprint` (optional dependency).

All rendering deps are **optional extras** so the core generator stays
dependency-light:

```
pip install algebra_worksheets            # model + LaTeX source emission
pip install algebra_worksheets[html]      # + weasyprint
```

(`tectonic`/`latexmk` are system binaries, documented in the README, not pip deps.)

## 4. Architecture

```
algebra_worksheets/
├── __about__.py
├── cli.py                  # argparse entry point, subcommands
├── model.py                # dataclasses: LinearEquation, System, Problem, Worksheet
├── generators/
│   ├── __init__.py
│   └── substitution.py     # generate solvable integer systems
├── render/
│   ├── __init__.py
│   ├── base.py             # Renderer protocol
│   ├── latex.py            # LaTeX backend (primary)
│   ├── html.py             # HTML/WeasyPrint backend (fallback)
│   └── templates/
│       ├── worksheet.tex.j2
│       ├── answer_key.tex.j2
│       ├── worksheet.html.j2
│       └── answer_key.html.j2
└── compile.py              # invoke tectonic/latexmk/weasyprint → PDF
```

### Core data model (sketch)

```python
@dataclass(frozen=True)
class LinearEquation:        # a*x + b*y = c
    a: int; b: int; c: int

@dataclass(frozen=True)
class System:
    eq1: LinearEquation
    eq2: LinearEquation
    solution: tuple[int, int]   # (x, y), known at generation time

@dataclass(frozen=True)
class Worksheet:
    title: str
    instructions: str
    problems: list[System]
    seed: int
```

### Generation algorithm (substitution, integer solutions)

1. Pick the target solution `(x, y)` from a configurable integer range
   (default `[-10, 10]`, negatives allowed).
2. Pick coefficients so that **substitution is clean**: ensure at least one
   equation has a variable with coefficient `±1` (so isolating that variable
   yields no fractions), keeping the PoC squarely "solvable by substitution."
3. Build `c1`, `c2` by plugging `(x, y)` in — guarantees consistency.
4. Reject degenerate / dependent systems (parallel lines, zero rows); ensure a
   **unique** solution (determinant `a1*b2 - a2*b1 != 0`).
5. Enforce a difficulty knob (coefficient magnitude bounds, allow/disallow
   negative coefficients).

## 5. CLI Design (argparse)

```
algebra_worksheets generate [options]

Options:
  -n, --count N          number of problems (default: 20)
  --seed SEED            RNG seed for reproducible output
  --type {substitution}  problem type (PoC: substitution only)
  --coef-min / --coef-max        coefficient bounds
  --sol-min / --sol-max          solution value bounds (default -10..10)
  --paper {letter,a4}    page size (default: letter)
  --columns N            problem layout columns (default: 2)
  --backend {latex,html} renderer (default: latex)
  --engine {auto,tectonic,latexmk,pdflatex,weasyprint}
  --title TEXT           worksheet title
  --emit {pdf,source}    PDF (default) or just emit .tex/.html source
  -o, --out PATH         output basename (writes <out>.pdf and <out>_key.pdf)
  --no-answer-key        skip the answer key
  --version / --help
```

Examples:

```
algebra_worksheets generate -n 24 --seed 42 -o week1
# → week1.pdf (worksheet) and week1_key.pdf (compact answer key)
```

## 6. Layout & Print Requirements

### Worksheet page

- Header: title, "Name: ______  Date: ______", short instructions.
- Problems numbered, 1–2 columns, each system shown as
  `\begin{cases} … \end{cases}` with blank work space beneath.
- US Letter default, ~0.75in margins, page numbers, problem count balanced
  across pages.

### Answer key page (compactness is a hard requirement)

- Separate file (`*_key.pdf`) so it can be printed on different paper / withheld.
- **Dense multi-column grid** (e.g. `1) (3, -2)   2) (-1, 5) …`), 4–6 columns
  via `multicols`/CSS columns, small font, minimal leading.
- Target: **a full 24-problem key fits on a single page** with room to spare.

## 7. Phases

### Phase 0 — Project scaffold ✅ (this commit)
- Cookiecutter template instantiated as `algebra_worksheets`.
- Spec written (`spec/roadmap.md`).
- `Makefile` generation targets + `scripts/*.sh` stubs.

### Phase 1 — Core model & generator (no rendering)
- Implement `model.py` and `generators/substitution.py`.
- Unique-integer-solution guarantee; `--seed` reproducibility.
- Unit + property tests (Hypothesis): every generated system has the claimed
  unique integer solution; substitution introduces no fractions.
- CLI `generate --emit source` prints a plain-text problem list.

### Phase 2 — LaTeX backend (primary)
- Jinja2 LaTeX environment with safe delimiters + escaping.
- `worksheet.tex.j2`, `answer_key.tex.j2`.
- `compile.py`: detect/select engine (`tectonic`→`latexmk`→`pdflatex`).
- `generate -o NAME` produces `NAME.pdf` + `NAME_key.pdf`.
- Golden-file test on emitted `.tex`; PDF compile gated behind an engine check
  (skipped in CI if no engine present).

### Phase 3 — Compact answer key + layout polish
- Multi-column dense key; verify 24 answers / 1 page.
- Paper size (`letter`/`a4`), column count, margins.
- Visual review pass on real printed output.

### Phase 4 — HTML/WeasyPrint fallback backend
- `worksheet.html.j2`, `answer_key.html.j2`, CSS `@page` + columns.
- `--backend html`; `[html]` optional extra.
- Parity tests with LaTeX backend (same model → equivalent answers).

### Phase 5 — Quality, packaging & extensibility
- Full quality gate green (`make check`): ruff/black/isort, mypy strict,
  pylint, bandit, interrogate, codespell.
- README usage docs + sample PDFs; mkdocs pages.
- Renderer `Protocol` + problem-type registry so new types
  (elimination, one-variable linear, etc.) plug in cleanly — paves the way for
  post-PoC problem types.

## 8. Testing Strategy

- **Unit:** generator invariants, model arithmetic, CLI arg parsing.
- **Property (Hypothesis):** for random seeds/ranges, the stored solution is the
  *unique* solution and substitution stays integer.
- **Golden files:** stable `.tex`/`.html` snapshots for templating regressions.
- **Smoke (`scripts/basic_checks.sh`):** `--help`, `--version`, `generate
  --emit source` exit cleanly.
- **PDF compile:** opportunistic — run only when an engine is detected.

## 9. Open Questions

- Default page size — assuming **US Letter**; A4 supported via `--paper`.
- Bundle a sample answer-key font size, or expose `--key-font`? (Defer; hardcode
  a sane compact default in Phase 3.)
- Ship pre-rendered sample PDFs in the repo, or generate on demand in docs? (Lean
  toward committing a couple of small samples.)
