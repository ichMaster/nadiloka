"""Tejas: the light resource field (ARCHITECTURE, World model).

A scalar field over the grid; each cell holds 0..FOOD_MAX units of
light energy. Patches shape the field: applying one writes intensity
into the cells within its radius, clamped so no cell ever exceeds
FOOD_MAX. Cells under a patch feed producers from v1.2; the harvest
debits the field through take(). The hot path stays pure arithmetic
over a flat list -- no allocation churn.
"""

from __future__ import annotations

from dataclasses import dataclass

from nadiloka.grid import Grid


@dataclass
class Patch:
    """A light patch: where it shines, how wide, how bright, how long.

    A plain data model; the lifecycle (ignite, fade, expire, respawn)
    is driven by the update-Tejas phase (NADI-007). `age` is the
    lifecycle clock, in ticks since ignition.
    """

    center: tuple[int, int]
    radius: int
    intensity: float
    lifetime: int
    age: int = 0


class TejasField:
    """Per-cell light energy in 0..food_max over a bounded grid."""

    def __init__(self, grid: Grid, food_max: float) -> None:
        self.grid = grid
        self.food_max = food_max
        self._cells = [0.0] * (grid.width * grid.height)

    def energy_at(self, x: int, y: int) -> float:
        return self._cells[self.grid.index(x, y)]

    def add(self, x: int, y: int, amount: float) -> None:
        """Deposit energy into a cell, clamped to 0..food_max."""
        i = self.grid.index(x, y)
        self._cells[i] = min(self._cells[i] + amount, self.food_max)

    def take(self, x: int, y: int, amount: float) -> float:
        """Debit up to `amount` from a cell; returns what was actually taken.

        The read/decrement seam v1.2's harvest goes through: field loss
        always equals the harvester's gain.
        """
        i = self.grid.index(x, y)
        taken = min(self._cells[i], amount)
        self._cells[i] -= taken
        return taken

    def clear(self) -> None:
        """Zero the whole field (the per-tick rebuild in the update phase)."""
        for i in range(len(self._cells)):
            self._cells[i] = 0.0

    def illuminate(self, patch: Patch, intensity: float) -> None:
        """Write `intensity` over the patch's clipped disc, clamped per cell.

        Overlapping patches accumulate, but no cell ever exceeds
        food_max. `intensity` is passed explicitly so the lifecycle can
        apply the patch's current (faded) brightness.
        """
        cx, cy = patch.center
        for x, y in self.grid.neighbourhood(cx, cy, patch.radius):
            self.add(x, y, intensity)

    def total_energy(self) -> float:
        """Sum over all cells (the v0 total-field-energy counter)."""
        return sum(self._cells)
