"""v0 demo: the living light field.

Wires World + Tejas + the ASCII renderer over a loop: patches ignite,
glow, fade, and reappear across the terminal. The reference parameters
are the WorldConfig defaults; the seed is always explicit on the CLI.

Usage: python demos/light.py --seed 42 [--ticks 200] [--delay 0.08] [--no-render]
"""

import argparse
import sys
import time

from nadiloka.counters import counter_line
from nadiloka.render import render_frame
from nadiloka.world import World, WorldConfig

CLEAR = "\x1b[H\x1b[2J"


def run(config: WorldConfig, ticks: int, frame_sink=None) -> list[str]:
    """Step a fresh world `ticks` times; return one counter line per tick.

    With a frame_sink, one rendered frame per tick is written to it as
    well. Rendering is read-only, so the returned counter log is
    identical with the sink attached or absent -- the invariant
    NADI-011's suite pins.
    """
    world = World(config)
    lines = []
    for _ in range(ticks):
        world.step()
        lines.append(counter_line(world))
        if frame_sink is not None:
            frame_sink.write(render_frame(world) + "\n")
    return lines


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticks", type=int, default=200, help="number of Meru ticks")
    parser.add_argument("--seed", type=int, required=True, help="explicit RNG seed")
    parser.add_argument(
        "--delay", type=float, default=0.08, help="seconds between frames"
    )
    parser.add_argument(
        "--no-render",
        action="store_true",
        help="emit counter lines only (no frames)",
    )
    args = parser.parse_args(argv)
    world = World(WorldConfig(seed=args.seed))
    for _ in range(args.ticks):
        world.step()
        if args.no_render:
            print(counter_line(world))
        else:
            sys.stdout.write(CLEAR + render_frame(world) + "\n")
            sys.stdout.flush()
            time.sleep(args.delay)


if __name__ == "__main__":
    main()
