"""Determinism harness (ARCHITECTURE, Testing and CI).

Two runs with the same seed and config must produce byte-identical
counter logs. This is the cheapest regression net; it runs on every CI
pass from v0.1 on, and encodes the v0.1 DoD verbatim.
"""

import importlib.util
import subprocess
import sys
from pathlib import Path

from nadiloka.world import WorldConfig

DEMO_PATH = Path(__file__).resolve().parent.parent / "demos" / "empty.py"


def _load_demo():
    spec = importlib.util.spec_from_file_location("demo_empty", DEMO_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_same_seed_and_config_yield_byte_identical_counter_logs():
    demo = _load_demo()
    config = WorldConfig(seed=2026)
    log_a = "\n".join(demo.run(config, 200)).encode()
    log_b = "\n".join(demo.run(config, 200)).encode()
    assert log_a == log_b


def test_n_ticks_with_no_state_complete_without_error():
    demo = _load_demo()
    lines = demo.run(WorldConfig(seed=0), 500)
    assert len(lines) == 500
    assert lines[-1].startswith("tick=500 ")


def test_demo_runner_process_output_is_byte_identical():
    """End to end: the CLI runner itself reproduces exactly under one seed."""
    cmd = [sys.executable, str(DEMO_PATH), "--ticks", "50", "--seed", "123"]
    first = subprocess.run(cmd, capture_output=True, check=True)
    second = subprocess.run(cmd, capture_output=True, check=True)
    assert first.stdout == second.stdout
    assert first.stdout.count(b"\n") == 50
