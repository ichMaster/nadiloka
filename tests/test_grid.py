"""Grid: bounds behaviour and deterministic neighbourhood queries."""

import pytest

from nadiloka.grid import Grid


def test_in_bounds_at_corners_and_edges():
    grid = Grid(width=10, height=6)
    assert grid.in_bounds(0, 0)
    assert grid.in_bounds(9, 5)
    assert not grid.in_bounds(10, 5)
    assert not grid.in_bounds(9, 6)
    assert not grid.in_bounds(-1, 0)
    assert not grid.in_bounds(0, -1)


def test_out_of_bounds_is_an_explicit_error_never_a_wrap():
    grid = Grid(width=10, height=6)
    with pytest.raises(ValueError):
        grid.require_in_bounds(10, 0)
    with pytest.raises(ValueError):
        grid.index(-1, 0)


def test_neighbourhood_full_disc_in_the_interior():
    grid = Grid(width=10, height=10)
    cells = grid.neighbourhood(5, 5, 1)
    assert cells == [(5, 4), (4, 5), (5, 5), (6, 5), (5, 6)]


def test_neighbourhood_is_clipped_at_a_corner():
    grid = Grid(width=10, height=10)
    cells = grid.neighbourhood(0, 0, 1)
    assert cells == [(0, 0), (1, 0), (0, 1)]


def test_neighbourhood_is_clipped_at_an_edge():
    grid = Grid(width=10, height=10)
    cells = grid.neighbourhood(9, 5, 1)
    assert cells == [(9, 4), (8, 5), (9, 5), (9, 6)]


def test_neighbourhood_respects_euclidean_radius():
    grid = Grid(width=20, height=20)
    cells = grid.neighbourhood(10, 10, 2)
    assert (12, 12) not in cells  # distance sqrt(8) > 2
    assert (12, 10) in cells
    assert (11, 11) in cells  # distance sqrt(2) <= 2
    assert len(cells) == 13


def test_neighbourhood_out_of_bounds_center_raises():
    grid = Grid(width=5, height=5)
    with pytest.raises(ValueError):
        grid.neighbourhood(5, 0, 1)


def test_query_order_is_stable_row_major():
    grid = Grid(width=8, height=8)
    cells = grid.neighbourhood(4, 4, 2)
    assert cells == sorted(cells, key=lambda c: (c[1], c[0]))
    assert list(grid.cells())[:3] == [(0, 0), (1, 0), (2, 0)]
