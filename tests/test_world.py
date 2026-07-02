"""World container: config, RNG discipline, tick counter, population."""

import re
from pathlib import Path

import nadiloka
from nadiloka.world import World, WorldConfig


def test_same_seed_yields_identical_draw_sequence():
    a = World(WorldConfig(seed=42))
    b = World(WorldConfig(seed=42))
    draws_a = [a.rng.random() for _ in range(100)]
    draws_b = [b.rng.random() for _ in range(100)]
    assert draws_a == draws_b


def test_different_seeds_diverge():
    a = World(WorldConfig(seed=1))
    b = World(WorldConfig(seed=2))
    assert [a.rng.random() for _ in range(10)] != [b.rng.random() for _ in range(10)]


def test_fresh_world_state():
    world = World(WorldConfig(seed=7))
    assert world.config.seed == 7
    assert world.tick == 0
    assert world.population == {}


def test_no_module_level_random_calls_in_engine():
    """Pinning test for RNG discipline (ARCHITECTURE, Key invariants).

    Only random.Random(seed) construction is allowed in the engine;
    any other random.<name> reference is a module-level call that
    silently breaks reproducibility.
    """
    engine_dir = Path(nadiloka.__file__).parent
    pattern = re.compile(r"\brandom\.(?!Random\b)\w+")
    offenders = [
        f"{path.name}: {match.group(0)}"
        for path in sorted(engine_dir.glob("*.py"))
        for match in pattern.finditer(path.read_text())
    ]
    assert offenders == []
