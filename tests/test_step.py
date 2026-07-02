"""Meru tick cycle: the fixed five-phase hook order (ARCHITECTURE, One tick cycle)."""

from nadiloka.world import World, WorldConfig

PHASE_ORDER = [
    "_update_tejas",
    "_rebuild_grid",
    "_act",
    "_flush_nadi",
    "_cleanup",
]


def _spy_on_phases(world, calls):
    for name in PHASE_ORDER:
        setattr(world, name, lambda name=name: calls.append(name))


def test_five_phases_fire_once_each_per_tick_in_order():
    world = World(WorldConfig(seed=3))
    calls = []
    _spy_on_phases(world, calls)
    world.step()
    assert calls == PHASE_ORDER


def test_phase_order_holds_across_ticks():
    world = World(WorldConfig(seed=3))
    calls = []
    _spy_on_phases(world, calls)
    for _ in range(4):
        world.step()
    assert calls == PHASE_ORDER * 4


def test_tick_counter_increments_once_per_step():
    world = World(WorldConfig(seed=11))
    for expected in range(1, 6):
        world.step()
        assert world.tick == expected


def test_n_steps_on_an_empty_world_run_clean():
    world = World(WorldConfig(seed=0))
    for _ in range(1000):
        world.step()
    assert world.tick == 1000
    assert world.population == {}
