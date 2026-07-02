"""Grid: the bounded W x H spatial scaffold (ARCHITECTURE, World model).

Coordinates are (x, y); the grid is bounded with no edge wrapping --
out-of-bounds access is an explicit error, never a silent wrap. All
iteration and query helpers return cells in a stable row-major order
(y, then x), never hash or dict order.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Grid:
    """A W x H bounded grid; width and height come from the world config."""

    width: int
    height: int

    def in_bounds(self, x: int, y: int) -> bool:
        return 0 <= x < self.width and 0 <= y < self.height

    def require_in_bounds(self, x: int, y: int) -> None:
        """Raise on out-of-bounds access; there is no silent wrapping."""
        if not self.in_bounds(x, y):
            raise ValueError(
                f"({x}, {y}) is outside the {self.width}x{self.height} grid"
            )

    def index(self, x: int, y: int) -> int:
        """Flat row-major index for per-cell storage (the Tejas field)."""
        self.require_in_bounds(x, y)
        return y * self.width + x

    def cells(self):
        """All cells in stable row-major order (y, then x)."""
        for y in range(self.height):
            for x in range(self.width):
                yield (x, y)

    def neighbourhood(self, cx: int, cy: int, radius: int) -> list[tuple[int, int]]:
        """Cells within Euclidean distance `radius` of (cx, cy), center included.

        Clipped at the edges: a query near a border returns the
        truncated disc. Row-major order (y, then x) keeps the result
        deterministic.
        """
        self.require_in_bounds(cx, cy)
        result = []
        for y in range(max(0, cy - radius), min(self.height, cy + radius + 1)):
            for x in range(max(0, cx - radius), min(self.width, cx + radius + 1)):
                if (x - cx) ** 2 + (y - cy) ** 2 <= radius * radius:
                    result.append((x, y))
        return result
