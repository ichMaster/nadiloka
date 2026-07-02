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


@dataclass(frozen=True)
class WorldConfig:
    """Per-scenario world parameters (ARCHITECTURE, Configuration and parameters).

    Nothing tunable lives as an engine constant: every number belongs
    here or in a species descriptor. The seed is always explicit --
    from the config or the demo CLI (--seed), never implicit. Grid and
    Tejas parameters join in v0.2.
    """

    seed: int


class World:
    """Holds config, the single seeded RNG, the tick counter, and the population."""

    def __init__(self, config: WorldConfig) -> None:
        self.config = config
        self.rng = random.Random(config.seed)
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
        """Phase 1: light patches ignite, fade, and respawn. Filled in v0.2."""

    def _rebuild_grid(self) -> None:
        """Phase 2: rebuild the spatial hash from live digitants. Filled in v1."""

    def _act(self) -> None:
        """Phase 3: digitants act over a population snapshot. Filled in v1."""

    def _flush_nadi(self) -> None:
        """Phase 4: deliver all Nadi messages emitted this tick. Filled in v3."""

    def _cleanup(self) -> None:
        """Phase 5: remove dead, eaten, and expired digitants. Filled in v1."""
