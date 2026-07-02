"""Patch lifecycle: ignite, fade, expire, respawn -- deterministically."""

from nadiloka.world import World, WorldConfig


def _single_patch_config(seed=21):
    return WorldConfig(
        seed=seed,
        patch_target=1,
        patch_radius=2,
        patch_intensity=5.0,
        patch_lifetime=5,
    )


def test_live_patch_count_holds_at_the_target():
    world = World(WorldConfig(seed=8))
    for _ in range(100):
        world.step()
        assert len(world.patches) == world.config.patch_target


def test_a_patch_fades_while_it_lives():
    world = World(_single_patch_config())
    world.step()
    patch = world.patches[0]
    cx, cy = patch.center
    previous = world.tejas.energy_at(cx, cy)
    assert previous > 0.0
    while True:
        world.step()
        if world.patches[0] is not patch:
            break
        current = world.tejas.energy_at(cx, cy)
        assert current < previous
        previous = current


def test_an_expired_patch_disappears_and_a_replacement_ignites():
    world = World(_single_patch_config())
    world.step()
    first = world.patches[0]
    ticks_left = first.lifetime - first.age
    for _ in range(ticks_left):
        world.step()
    assert first not in world.patches
    assert len(world.patches) == 1
    replacement = world.patches[0]
    assert replacement.age < replacement.lifetime


def test_replacements_ignite_at_age_zero_after_the_first_tick():
    world = World(_single_patch_config())
    world.step()
    first = world.patches[0]
    while world.patches[0] is first:
        world.step()
    assert world.patches[0].age == 0


def test_faded_cells_are_freed_when_a_patch_expires():
    world = World(_single_patch_config())
    world.step()
    patch = world.patches[0]
    cx, cy = patch.center
    while world.patches[0] is patch:
        world.step()
    replacement = world.patches[0]
    rx, ry = replacement.center
    if (cx, cy) not in world.grid.neighbourhood(rx, ry, replacement.radius):
        assert world.tejas.energy_at(cx, cy) == 0.0


def test_same_seed_gives_identical_placements_and_lifecycle():
    a = World(WorldConfig(seed=99))
    b = World(WorldConfig(seed=99))
    for _ in range(80):
        a.step()
        b.step()
        assert [(p.center, p.age) for p in a.patches] == [
            (p.center, p.age) for p in b.patches
        ]
        assert a.tejas.total_energy() == b.tejas.total_energy()


def test_different_seeds_give_different_light():
    a = World(WorldConfig(seed=1))
    b = World(WorldConfig(seed=2))
    a.step()
    b.step()
    assert [p.center for p in a.patches] != [p.center for p in b.patches]
