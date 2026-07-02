"""World: the Nadiloka container and, from NADI-003, the Meru tick cycle.

The World owns everything: the config, the single seeded RNG, the Meru
tick counter, and the population. RNG discipline (ARCHITECTURE, Key
invariants and pitfalls): the one random.Random instance is owned by the
World and passed explicitly to whatever needs randomness; module-level
random.* calls are forbidden -- they silently break reproducibility.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

from nadiloka.grid import Grid
from nadiloka.tejas import Patch, TejasField


@dataclass(frozen=True)
class WorldConfig:
    """Per-scenario world parameters (ARCHITECTURE, Configuration and parameters).

    Nothing tunable lives as an engine constant: every number belongs
    here or in a species descriptor. The seed is always explicit --
    from the config or the demo CLI (--seed), never implicit. The
    defaults below are the reference parameters the tests and smoke
    runs pin their bands against.
    """

    seed: int
    width: int = 40
    height: int = 25
    # Tejas patch parameters (NADI-006): the light the world runs on.
    food_max: float = 10.0
    patch_target: int = 6
    patch_radius: int = 4
    patch_intensity: float = 5.0
    patch_lifetime: int = 30
    # The energy band (NADI-008): the "no runaway, no collapse" guard the
    # band test and the v0.3 smoke run assert against, over band_ticks.
    energy_band_low: float = 150.0
    energy_band_high: float = 1500.0
    band_ticks: int = 300


class World:
    """Holds config, the single seeded RNG, the tick counter, and the population."""

    def __init__(self, config: WorldConfig) -> None:
        self.config = config
        self.rng = random.Random(config.seed)
        self.grid = Grid(config.width, config.height)
        self.tejas = TejasField(self.grid, config.food_max)
        self.patches: list[Patch] = []
        self.tick = 0
        # id -> Digitant; stays empty until v1.
        self.population: dict[int, object] = {}

    def step(self) -> None:
        """One turn of Meru: the five phases in fixed order, then advance the tick.

        Invariant (ARCHITECTURE, One tick cycle): the phase order below
        is deterministic and must never be reordered. Later versions
        fill the hooks (Tejas in v0.2, grid/act/cleanup in v1, flush in
        v3); the seams themselves stay fixed. Single and synchronous
        for all.
        """
        self._update_tejas()
        self._rebuild_grid()
        self._act()
        self._flush_nadi()
        self._cleanup()
        self.tick += 1

    def _update_tejas(self) -> None:
        """Phase 1: light patches age, fade, expire, and respawn (v0.2).

        Every live patch ages one tick and fades linearly over its
        lifetime; expired patches disappear and free their cells;
        replacements ignite at fresh seeded positions to hold the
        configured target count, so the light visibly moves. The field
        is then rebuilt from the live patches, keeping it a pure
        function of patch state.
        """
        for patch in self.patches:
            patch.age += 1
        self.patches = [p for p in self.patches if p.age < p.lifetime]
        while len(self.patches) < self.config.patch_target:
            self.patches.append(self._ignite())
        self.tejas.clear()
        for patch in self.patches:
            faded = patch.intensity * (1 - patch.age / patch.lifetime)
            self.tejas.illuminate(patch, faded)

    def _ignite(self) -> Patch:
        """A new patch at a seeded random cell, via the World's one RNG.

        The initial batch (tick 0) ignites at staggered ages so total
        field energy holds a steady level instead of the whole sky
        pulsing in lockstep; every respawn after that starts at age 0.
        """
        x = self.rng.randrange(self.config.width)
        y = self.rng.randrange(self.config.height)
        age = self.rng.randrange(self.config.patch_lifetime) if self.tick == 0 else 0
        return Patch(
            center=(x, y),
            radius=self.config.patch_radius,
            intensity=self.config.patch_intensity,
            lifetime=self.config.patch_lifetime,
            age=age,
        )

    def _rebuild_grid(self) -> None:
        """Phase 2: rebuild the spatial hash from live digitants. Filled in v1."""

    def _act(self) -> None:
        """Phase 3: digitants act over a population snapshot. Filled in v1."""

    def _flush_nadi(self) -> None:
        """Phase 4: deliver all Nadi messages emitted this tick. Filled in v3."""

    def _cleanup(self) -> None:
        """Phase 5: remove dead, eaten, and expired digitants. Filled in v1."""
