"""ASCII renderer: the first observation layer (ARCHITECTURE, Observation layer).

Maps cell intensity to brightness glyphs under a header line of live
counters. Strictly read-only over the world: rendering never mutates
anything, and attaching or removing the renderer never changes a run.
The renderer is loop-independent -- it produces one frame per call;
the demo owns the loop.
"""

from __future__ import annotations

from nadiloka.counters import counter_line
from nadiloka.world import World

# Dark-to-bright ramp; index 0 is an unlit cell, the last glyph is FOOD_MAX.
BRIGHTNESS_RAMP = " .:-=+*#%@"


def glyph_for(intensity: float, food_max: float) -> str:
    """Map an intensity to a brightness glyph.

    Total over 0..food_max and beyond: values outside the range clamp
    to the darkest or brightest glyph; no input raises.
    """
    if food_max <= 0 or intensity <= 0:
        return BRIGHTNESS_RAMP[0]
    index = int(intensity / food_max * len(BRIGHTNESS_RAMP))
    return BRIGHTNESS_RAMP[min(index, len(BRIGHTNESS_RAMP) - 1)]


def render_frame(world: World) -> str:
    """One ASCII frame: the counter header over the W x H glyph grid.

    The header is the structured counter line itself (tick, population,
    total field energy, live patches), so every rendered frame carries
    the measurable counters alongside the visible field.
    """
    tejas = world.tejas
    food_max = world.config.food_max
    rows = [counter_line(world)]
    for y in range(world.grid.height):
        rows.append(
            "".join(
                glyph_for(tejas.energy_at(x, y), food_max)
                for x in range(world.grid.width)
            )
        )
    return "\n".join(rows)
