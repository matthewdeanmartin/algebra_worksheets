"""Core data model for algebra worksheets.

The proof-of-concept models systems of two linear equations in two unknowns
(``x`` and ``y``) of the form ``a*x + b*y = c``, with a known unique integer
solution.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LinearEquation:
    """A linear equation ``a*x + b*y = c`` with integer coefficients."""

    a: int
    b: int
    c: int

    def evaluate(self, x: int, y: int) -> int:
        """Return ``a*x + b*y`` for the given ``x`` and ``y``.

        Args:
            x: Value substituted for the first unknown.
            y: Value substituted for the second unknown.

        Returns:
            The left-hand side evaluated at ``(x, y)``.
        """
        return self.a * x + self.b * y

    def is_satisfied_by(self, x: int, y: int) -> bool:
        """Return whether ``(x, y)`` satisfies this equation.

        Args:
            x: Value substituted for the first unknown.
            y: Value substituted for the second unknown.

        Returns:
            ``True`` if ``a*x + b*y == c``.
        """
        return self.evaluate(x, y) == self.c


@dataclass(frozen=True)
class System:
    """A pair of linear equations with a known unique integer solution."""

    eq1: LinearEquation
    eq2: LinearEquation
    solution: tuple[int, int]

    @property
    def determinant(self) -> int:
        """Return the determinant ``a1*b2 - a2*b1`` of the coefficient matrix.

        Returns:
            The determinant; non-zero iff the system has a unique solution.
        """
        return self.eq1.a * self.eq2.b - self.eq2.a * self.eq1.b

    def is_consistent(self) -> bool:
        """Return whether the stored solution satisfies both equations.

        Returns:
            ``True`` if the recorded solution solves both equations and the
            system has a unique solution.
        """
        x, y = self.solution
        return self.determinant != 0 and self.eq1.is_satisfied_by(x, y) and self.eq2.is_satisfied_by(x, y)


@dataclass(frozen=True)
class Worksheet:
    """A titled collection of problems plus the seed that produced them."""

    title: str
    instructions: str
    problems: tuple[System, ...]
    seed: int
