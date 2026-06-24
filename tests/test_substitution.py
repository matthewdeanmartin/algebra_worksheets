"""Tests for the substitution-system generator."""

import random

import pytest
from hypothesis import given
from hypothesis import strategies as st

from algebra_worksheets.generators.substitution import (
    _random_nonzero,
    generate_system,
    generate_systems,
)


def test_generate_systems_count() -> None:
    """The generator returns exactly the requested number of systems."""
    assert len(generate_systems(15, seed=1)) == 15


def test_generate_systems_zero() -> None:
    """Requesting zero problems yields an empty tuple."""
    assert len(generate_systems(0, seed=1)) == 0


def test_generate_systems_negative_raises() -> None:
    """A negative count is rejected."""
    with pytest.raises(ValueError):
        generate_systems(-1)


def test_seed_is_reproducible() -> None:
    """The same seed produces identical systems."""
    assert generate_systems(8, seed=99) == generate_systems(8, seed=99)


def test_different_seeds_differ() -> None:
    """Different seeds (very likely) produce different systems."""
    assert generate_systems(8, seed=1) != generate_systems(8, seed=2)


def test_random_nonzero_all_zero_range_raises() -> None:
    """A range containing only zero is rejected."""
    with pytest.raises(ValueError):
        _random_nonzero(random.Random(0), 0, 0)


@given(seed=st.integers(min_value=0, max_value=10_000))
def test_generated_solution_is_correct_and_unique(seed: int) -> None:
    """Every generated system has its stored value as the unique solution."""
    system = generate_system(random.Random(seed))
    # Unique solution exists (non-singular).
    assert system.determinant != 0
    # The recorded solution actually solves both equations.
    assert system.is_consistent()


@given(seed=st.integers(min_value=0, max_value=10_000))
def test_substitution_stays_integer(seed: int) -> None:
    """At least one equation has a unit coefficient (clean substitution)."""
    system = generate_system(random.Random(seed))
    unit_coeffs = {1, -1}
    has_unit = (
        system.eq1.a in unit_coeffs
        or system.eq1.b in unit_coeffs
        or system.eq2.a in unit_coeffs
        or system.eq2.b in unit_coeffs
    )
    assert has_unit


@given(
    seed=st.integers(min_value=0, max_value=10_000),
    lo=st.integers(min_value=-5, max_value=5),
    span=st.integers(min_value=0, max_value=8),
)
def test_solution_respects_bounds(seed: int, lo: int, span: int) -> None:
    """Solution values stay within the requested bounds."""
    hi = lo + span
    system = generate_system(random.Random(seed), sol_min=lo, sol_max=hi)
    x, y = system.solution
    assert lo <= x <= hi
    assert lo <= y <= hi
