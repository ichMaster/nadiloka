"""The light demo: reproducible runs and the renderer on/off invariant."""

import importlib.util
import io
from pathlib import Path

from nadiloka.world import WorldConfig

DEMO_PATH = Path(__file__).resolve().parent.parent / "demos" / "light.py"


def _load_demo():
    spec = importlib.util.spec_from_file_location("demo_light", DEMO_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_run_emits_one_counter_line_per_tick():
    demo = _load_demo()
    lines = demo.run(WorldConfig(seed=42), 40)
    assert len(lines) == 40
    assert lines[0].startswith("tick=1 ")
    assert lines[-1].startswith("tick=40 ")


def test_same_seed_reproduces_the_run():
    demo = _load_demo()
    config = WorldConfig(seed=42)
    assert demo.run(config, 60) == demo.run(config, 60)


def test_renderer_on_or_off_gives_identical_counter_logs():
    demo = _load_demo()
    config = WorldConfig(seed=1234)
    with_sink = demo.run(config, 60, frame_sink=io.StringIO())
    without_sink = demo.run(config, 60)
    assert with_sink == without_sink


def test_frames_flow_alongside_counter_lines():
    demo = _load_demo()
    sink = io.StringIO()
    lines = demo.run(WorldConfig(seed=7), 10, frame_sink=sink)
    # Every frame opens with its counter header; one frame per tick.
    headers = [
        row for row in sink.getvalue().split("\n") if row.startswith("tick=")
    ]
    assert len(headers) == 10
    assert headers == lines
