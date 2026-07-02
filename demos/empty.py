"""v0.1 demo: an empty Nadiloka ticking deterministically.

Builds a World from a config and steps it N ticks, emitting one counter
line per tick. The seed is always explicit on the CLI (ARCHITECTURE,
Configuration and parameters).

Usage: python demos/empty.py --ticks 100 --seed 42
"""

import argparse

from nadiloka.counters import counter_line
from nadiloka.world import World, WorldConfig


def run(config: WorldConfig, ticks: int) -> list[str]:
    """Step a fresh world `ticks` times; return one counter line per tick."""
    world = World(config)
    lines = []
    for _ in range(ticks):
        world.step()
        lines.append(counter_line(world))
    return lines


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ticks", type=int, default=100, help="number of Meru ticks")
    parser.add_argument("--seed", type=int, required=True, help="explicit RNG seed")
    args = parser.parse_args(argv)
    for line in run(WorldConfig(seed=args.seed), args.ticks):
        print(line)


if __name__ == "__main__":
    main()
