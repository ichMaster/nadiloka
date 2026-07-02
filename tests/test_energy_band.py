"""The energy-band guard: no runaway growth, no collapse (v0.2 DoD).

Runs the reference parameters under a fixed seed for band_ticks and
asserts total field energy stays inside the configured band and no
cell ever exceeds FOOD_MAX. The v0.3 smoke run reuses this guard.
"""

from nadiloka.world import World, WorldConfig


def test_total_energy_stays_within_the_configured_band():
    config = WorldConfig(seed=42)
    world = World(config)
    for _ in range(config.band_ticks):
        world.step()
        energy = world.tejas.total_energy()
        assert config.energy_band_low <= energy <= config.energy_band_high


def test_no_cell_exceeds_food_max_over_the_run():
    config = WorldConfig(seed=42)
    world = World(config)
    for _ in range(config.band_ticks):
        world.step()
        assert all(
            0.0 <= world.tejas.energy_at(x, y) <= config.food_max
            for x, y in world.grid.cells()
        )
