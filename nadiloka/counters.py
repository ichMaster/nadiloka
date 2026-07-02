"""Counters: the measurable half of observability.

Every readiness criterion in ROADMAP.md is asserted against counter
logs (ARCHITECTURE, Counters and measurement). Emission is strictly
read-only over the world; the v0 set (total Tejas field energy, live
patch count) fills in with v0.2.
"""

from __future__ import annotations

from nadiloka.world import World


def counter_line(world: World) -> str:
    """Format one structured counter log line for the world's current tick."""
    population = len(world.population)
    energy = 0.0  # total Tejas field energy; wired in v0.2
    return f"tick={world.tick} population={population} energy={energy:.1f}"
