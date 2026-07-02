"""ASCII renderer: total glyph mapping, frame shape, read-only invariant."""

from nadiloka.counters import counter_line
from nadiloka.render import BRIGHTNESS_RAMP, glyph_for, render_frame
from nadiloka.world import World, WorldConfig


def test_glyph_mapping_is_total_over_the_full_range():
    food_max = 10.0
    steps = 200
    for i in range(steps + 1):
        glyph = glyph_for(food_max * i / steps, food_max)
        assert len(glyph) == 1
        assert glyph in BRIGHTNESS_RAMP


def test_glyph_mapping_boundaries():
    assert glyph_for(0.0, 10.0) == BRIGHTNESS_RAMP[0]
    assert glyph_for(10.0, 10.0) == BRIGHTNESS_RAMP[-1]


def test_glyph_mapping_never_raises_even_out_of_range():
    assert glyph_for(-1.0, 10.0) == BRIGHTNESS_RAMP[0]
    assert glyph_for(99.0, 10.0) == BRIGHTNESS_RAMP[-1]
    assert glyph_for(5.0, 0.0) == BRIGHTNESS_RAMP[0]


def test_frame_is_header_plus_one_glyph_per_cell():
    config = WorldConfig(seed=13, width=17, height=9)
    world = World(config)
    world.step()
    lines = render_frame(world).split("\n")
    assert len(lines) == 1 + config.height
    assert lines[0] == counter_line(world)
    for row in lines[1:]:
        assert len(row) == config.width


def test_a_lit_world_renders_visible_light():
    world = World(WorldConfig(seed=42))
    world.step()
    grid_part = render_frame(world).split("\n", 1)[1]
    assert any(ch != BRIGHTNESS_RAMP[0] for ch in grid_part.replace("\n", ""))


def test_rendering_is_read_only():
    world = World(WorldConfig(seed=9))
    world.step()
    rng_state = world.rng.getstate()
    tick = world.tick
    energy = world.tejas.total_energy()
    first = render_frame(world)
    second = render_frame(world)
    assert first == second
    assert world.rng.getstate() == rng_state
    assert world.tick == tick
    assert world.tejas.total_energy() == energy
