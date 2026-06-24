"""Generate systems of two linear equations solvable by substitution.

Every generated :class:`~algebra_worksheets.model.System` has a unique integer
solution (negatives allowed). To keep the systems cleanly solvable by
substitution, at least one equation is guaranteed to have a variable with
coefficient ``+1`` or ``-1`` so that isolating that variable introduces no
fractions.
"""

from __future__ import annotations

import random

from algebra_worksheets.model import LinearEquation, System


def _random_nonzero(rng: random.Random, lo: int, hi: int) -> int:
    """Return a random integer in ``[lo, hi]`` that is not zero.

    Args:
        rng: Random source.
        lo: Inclusive lower bound.
        hi: Inclusive upper bound.

    Returns:
        A non-zero integer in range.

    Raises:
        ValueError: If the range contains only zero.
    """
    if lo == 0 and hi == 0:
        raise ValueError("coefficient range must contain a non-zero value")
    while True:
        value = rng.randint(lo, hi)
        if value != 0:
            return value


def generate_system(
    rng: random.Random,
    *,
    sol_min: int = -10,
    sol_max: int = 10,
    coef_min: int = -9,
    coef_max: int = 9,
) -> System:
    """Generate one solvable system with a unique integer solution.

    Args:
        rng: Random source (seed it for reproducibility).
        sol_min: Inclusive lower bound for the solution values ``x`` and ``y``.
        sol_max: Inclusive upper bound for the solution values.
        coef_min: Inclusive lower bound for generated coefficients.
        coef_max: Inclusive upper bound for generated coefficients.

    Returns:
        A consistent :class:`System` whose recorded solution is its unique
        solution.
    """
    x = rng.randint(sol_min, sol_max)
    y = rng.randint(sol_min, sol_max)

    while True:
        # First equation: force a unit coefficient so a variable isolates
        # without fractions, keeping it a clean substitution problem.
        if rng.random() < 0.5:
            a1, b1 = rng.choice((1, -1)), _random_nonzero(rng, coef_min, coef_max)
        else:
            a1, b1 = _random_nonzero(rng, coef_min, coef_max), rng.choice((1, -1))

        a2 = _random_nonzero(rng, coef_min, coef_max)
        b2 = _random_nonzero(rng, coef_min, coef_max)

        eq1 = LinearEquation(a1, b1, a1 * x + b1 * y)
        eq2 = LinearEquation(a2, b2, a2 * x + b2 * y)
        system = System(eq1, eq2, (x, y))

        # Reject dependent/parallel systems (no unique solution).
        if system.determinant != 0:
            return system


def generate_systems(
    count: int,
    *,
    seed: int | None = None,
    sol_min: int = -10,
    sol_max: int = 10,
    coef_min: int = -9,
    coef_max: int = 9,
) -> tuple[System, ...]:
    """Generate ``count`` solvable systems.

    Args:
        count: Number of systems to generate.
        seed: RNG seed for reproducible output; ``None`` for random.
        sol_min: Inclusive lower bound for solution values.
        sol_max: Inclusive upper bound for solution values.
        coef_min: Inclusive lower bound for coefficients.
        coef_max: Inclusive upper bound for coefficients.

    Returns:
        A tuple of generated systems.

    Raises:
        ValueError: If ``count`` is negative.
    """
    if count < 0:
        raise ValueError("count must be non-negative")
    rng = random.Random(seed)
    return tuple(
        generate_system(
            rng,
            sol_min=sol_min,
            sol_max=sol_max,
            coef_min=coef_min,
            coef_max=coef_max,
        )
        for _ in range(count)
    )
