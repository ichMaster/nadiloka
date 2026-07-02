"""Layer 1 (v0) readiness: the living-light-field smoke run.

Encodes the ROADMAP v0.3 DoD as a test: a fixed-seed run of K ticks at
the reference parameters renders every frame without error while total
field energy holds inside the configured band, and the whole run
reproduces byte-identically under the same seed. Pure Python -- no
network, no Node, no pygame.
"""

import importlib.util
import io
from pathlib import Path

from nadiloka.render import render_frame
from nadiloka.world import World, WorldConfig

DEMO_PATH = Path(__file__).resolve().parent.parent / "demos" / "light.py"

SMOKE_SEED = 42


def _load_demo():
    spec = importlib.util.spec_from_file_location("demo_light", DEMO_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_smoke_the_living_light_field():
    """K ticks at the reference parameters: render every frame, hold the band."""
    config = WorldConfig(seed=SMOKE_SEED)
    world = World(config)
    seen_frames = set()
    for _ in range(config.band_ticks):
        world.step()
        frame = render_frame(world)
        assert frame  # every tick renders without raising
        seen_frames.add(frame.split("\n", 1)[1])
        energy = world.tejas.total_energy()
        assert config.energy_band_low <= energy <= config.energy_band_high
    # The field lives: the grid keeps changing rather than freezing.
    assert len(seen_frames) > 1


def test_smoke_two_same_seed_runs_are_byte_identical():
    demo = _load_demo()
    config = WorldConfig(seed=SMOKE_SEED)
    sink_a, sink_b = io.StringIO(), io.StringIO()
    log_a = "\n".join(demo.run(config, config.band_ticks, frame_sink=sink_a))
    log_b = "\n".join(demo.run(config, config.band_ticks, frame_sink=sink_b))
    assert log_a.encode() == log_b.encode()
    assert sink_a.getvalue().encode() == sink_b.getvalue().encode()
