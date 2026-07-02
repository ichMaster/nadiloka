"""Counters: the measurable half of observability.

Every readiness criterion in ROADMAP.md is asserted against counter
logs (ARCHITECTURE, Counters and measurement). Emission is strictly
read-only over the world; the v0 set (total Tejas field energy, live
patch count) fills in with v0.2.
"""

from __future__ import annotations

from nadiloka.world import World


def counter_line(world: World) -> str:
    """Format one structured counter log line for the world's current tick.

    The v0 set: tick, population (0 until v1), total Tejas field
    energy, and the live-patch count.
    """
    population = len(world.population)
    energy = world.tejas.total_energy()
    patches = len(world.patches)
    return (
        f"tick={world.tick} population={population} "
        f"energy={energy:.1f} patches={patches}"
    )
