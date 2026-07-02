"""Counters scaffold: line format and the read-only observation invariant."""

from nadiloka.counters import counter_line
from nadiloka.world import World, WorldConfig


def test_counter_line_format():
    world = World(WorldConfig(seed=5))
    assert counter_line(world) == "tick=0 population=0 energy=0.0 patches=0"


def test_counter_line_tracks_tick_energy_and_patches():
    world = World(WorldConfig(seed=5))
    world.step()
    world.step()
    line = counter_line(world)
    assert line.startswith("tick=2 population=0 energy=")
    assert line.endswith(f"patches={world.config.patch_target}")
    energy = float(line.split("energy=")[1].split()[0])
    assert energy == round(world.tejas.total_energy(), 1)
    assert energy > 0.0


def test_counter_emission_is_read_only():
    """Observation never mutates the world (ARCHITECTURE, Observation layer)."""
    world = World(WorldConfig(seed=9))
    world.step()
    rng_state = world.rng.getstate()
    tick = world.tick
    first = counter_line(world)
    second = counter_line(world)
    assert first == second
    assert world.rng.getstate() == rng_state
    assert world.tick == tick
    assert world.population == {}
