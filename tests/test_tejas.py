"""Tejas field: illumination, the FOOD_MAX clamp, and the harvest seam."""

from nadiloka.grid import Grid
from nadiloka.tejas import Patch, TejasField


def _field(width=10, height=10, food_max=10.0):
    return TejasField(Grid(width, height), food_max)


def test_fresh_field_is_dark():
    field = _field()
    assert field.total_energy() == 0.0
    assert field.energy_at(5, 5) == 0.0


def test_illumination_covers_the_patch_disc():
    field = _field()
    patch = Patch(center=(5, 5), radius=1, intensity=3.0, lifetime=10)
    field.illuminate(patch, patch.intensity)
    assert field.energy_at(5, 5) == 3.0
    assert field.energy_at(5, 4) == 3.0
    assert field.energy_at(6, 6) == 0.0  # outside the Euclidean disc
    assert field.total_energy() == 15.0  # 5 cells at radius 1


def test_illumination_is_clipped_at_the_border():
    field = _field()
    patch = Patch(center=(0, 0), radius=1, intensity=2.0, lifetime=10)
    field.illuminate(patch, patch.intensity)
    assert field.total_energy() == 6.0  # 3 cells in the corner-clipped disc


def test_no_cell_exceeds_food_max_under_overlapping_patches():
    field = _field(food_max=10.0)
    a = Patch(center=(5, 5), radius=2, intensity=7.0, lifetime=10)
    b = Patch(center=(6, 5), radius=2, intensity=7.0, lifetime=10)
    field.illuminate(a, a.intensity)
    field.illuminate(b, b.intensity)
    overlap = {(x, y) for x, y in field.grid.neighbourhood(5, 5, 2)} & {
        (x, y) for x, y in field.grid.neighbourhood(6, 5, 2)
    }
    assert overlap
    for x, y in field.grid.cells():
        assert 0.0 <= field.energy_at(x, y) <= 10.0
    for x, y in overlap:
        assert field.energy_at(x, y) == 10.0  # 7 + 7 clamped


def test_take_debits_and_returns_what_was_taken():
    field = _field()
    field.add(3, 3, 5.0)
    assert field.take(3, 3, 2.0) == 2.0
    assert field.energy_at(3, 3) == 3.0
    assert field.take(3, 3, 99.0) == 3.0  # capped by what the cell holds
    assert field.energy_at(3, 3) == 0.0
    assert field.take(3, 3, 1.0) == 0.0


def test_clear_zeroes_the_field():
    field = _field()
    field.add(1, 1, 4.0)
    field.clear()
    assert field.total_energy() == 0.0
