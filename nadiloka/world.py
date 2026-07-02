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
