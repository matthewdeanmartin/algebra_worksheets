"""Tests for the core data model."""

from algebra_worksheets.model import LinearEquation, System


def test_equation_evaluate_and_satisfied() -> None:
    """An equation evaluates its left-hand side and checks satisfaction."""
    eq = LinearEquation(2, -3, 12)  # 2x - 3y = 12
    assert eq.evaluate(3, -2) == 12
    assert eq.is_satisfied_by(3, -2)
    assert not eq.is_satisfied_by(0, 0)


def test_system_determinant() -> None:
    """The determinant is a1*b2 - a2*b1."""
    system = System(LinearEquation(1, 1, 0), LinearEquation(2, -1, 0), (0, 0))
    assert system.determinant == 1 * -1 - 2 * 1


def test_consistent_system() -> None:
    """A system whose solution solves both equations is consistent."""
    # x=3, y=-2:  x + y = 1 ; 2x - y = 8
    system = System(LinearEquation(1, 1, 1), LinearEquation(2, -1, 8), (3, -2))
    assert system.is_consistent()


def test_dependent_system_is_inconsistent() -> None:
    """A zero-determinant system is not consistent (no unique solution)."""
    # Parallel lines: x + y = 1 ; 2x + 2y = 2  -> determinant 0
    system = System(LinearEquation(1, 1, 1), LinearEquation(2, 2, 2), (0, 1))
    assert system.determinant == 0
    assert not system.is_consistent()


def test_wrong_solution_is_inconsistent() -> None:
    """A recorded solution that doesn't satisfy the equations is inconsistent."""
    system = System(LinearEquation(1, 1, 1), LinearEquation(2, -1, 8), (0, 0))
    assert not system.is_consistent()
