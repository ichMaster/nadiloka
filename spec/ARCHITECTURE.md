# Nadiloka — Architecture

> Project context document for Claude Code. Describes components, the data model, the tick cycle, invariants, and extension points. Implement in versions and phases per `ROADMAP.md`.

## Component overview

- **World (Nadiloka)** — holds everything: the space grid, the Tejas resource field, the digitant population, the Nadi bus, the spatial index, the counters, and the single seeded RNG. Drives the tick cycle (Meru), birth, and death.
- **Meru** — the world clock. One turn of Meru = one `World.step()`, single and synchronous for all.
- **Tejas** — a resource field over the grid: moving patches of light (center, radius, intensity, lifetime).
- **EventBus (Nadi)** — publish/subscribe with deferred delivery and three addressing modes.
- **Digitant** — an individual creature: state (needs, position, age, health), two-clock, an FSM brain, a diet `ahara`, and (from v6) a personal genome.
- **Jati loader** — reads declarative species descriptors and instantiates digitants from them.
- **Spatial grid** — a spatial hash for fast neighbour lookup (rebuilt each tick).
- **Observation layer** — renderers (ASCII from v0.3, the web viewer from v0.4) and counters. Strictly read-only over the world.

## World model

- **Space.** A W×H grid, coordinates (x, y), bounded, no edge wrapping.
- **Tejas.** A scalar field: each cell holds 0..FOOD_MAX units of light energy. Patches ignite, live, fade, and reappear elsewhere; cells under a patch feed producers.
- **Population.** A dict id → Digitant. Variable; capped at MAX_POP.
- **Time.** Discrete, in Meru ticks; a single seeded RNG owned by the World for reproducibility (see RNG discipline below).

## Event bus (Nadi)

The mechanism for communication without direct references between agents.

- **Message:** topic, sender, payload, addressing.
- **Addressing:**
  - `target=id` — to one specific agent;
  - `radius=r` — to neighbours within radius r (via the spatial grid);
  - otherwise — globally to all.
- **Deferred delivery:** `emit()` during a tick only queues a message; `flush()` delivers the whole queue at the end of the tick. Replies generated during delivery go out the *next* tick. This keeps cascades bounded and the tick deterministic.
- **Deterministic order:** `flush()` delivers in emit (FIFO) order; for radius and global addressing, recipients are resolved in a stable order (sorted by agent id). Delivery order must never depend on hash or dict ordering.
- **Subscription wiring:** a species declares what it emits and listens to in its Jati `signals` field. On delivery, a message becomes a pysm event on the recipient's brain with the payload passed via `cargo` (never `input=` — see the pitfalls).

### Topic protocol (grown per version)

| Topic | Meaning |
| --- | --- |
| crowd_signal / bloom | producer signals (v3.2) |
| hunt / flee | predator-prey (v5.2) |
| mate_request / mate_ack | mate-based reproduction (optional extension; base reproduction in v1.3 does not use the bus) |
| greet / offer_food / hungry_call | sociality and cooperation (optional extension) |

## Digitant

An individual creature's state:

- `id`, `pos` — identifier and position.
- `needs` — hunger, energy, social (within a range).
- `health` — falls under extreme hunger, otherwise slowly recovers; zero = death.
- `age`, `lifespan`, `repro_cd` — age, natural-death threshold, reproduction cooldown.
- `jati` — species (defines diet, harvest, signals, parameters).
- `genome` — the individual's copy of the mutable trait fields (see Genome and heredity).
- `brain` — an FSM mode machine (pysm): `Wander` / `Hungry` / `Sleeping` (+ species-specific). Incoming Nadi messages arrive as pysm events with data in `cargo`.

### Two-clock

- **Body-tick (body):** a cheap deterministic step on every Meru turn — aging, needs decay, movement, feeding (per `ahara`), emitting messages.
- **Brain:** a tiny machine that only re-evaluates the mode based on fresh needs. The body acts in the current mode, then the brain picks the next one.

### Genome and heredity (from v6)

- The Jati descriptor defines **species defaults**. Each digitant carries a **personal copy of the mutable trait fields** — its genome: needs thresholds and rates, movement speed, signal sensitivity, feeding efficiency (`harvest.gain`).
- Until v6 the genome simply equals the species defaults. From v6, reproduction copies the parent's genome and applies small, bounded, seeded mutations per trait.
- **Species identity is not part of the genome** and never mutates: the `jati` name, `ahara`, and the topic lists stay fixed.
- The body-tick reads traits from the individual, not from the species descriptor, so evolution adds nothing to the hot loop.

## Species descriptive language (Jati)

Each species is a declarative descriptor; the engine instantiates thousands of individuals from it. Fields:

- `jati` — species name;
- `ahara` — diet: `tejas` or another species (wires it into the food chain);
- `harvest` — where and how much energy it takes (`gain`), in what radius;
- `yields` — how much energy it gives when eaten;
- `needs` — needs and their rates;
- `brain` — behaviour modes: a named pysm preset implemented in the engine (v0–v5); mapping to a yamlfsm spec is a later extension (see Extension points) — yamlfsm is not a dependency yet;
- `reproduce` — conditions (adulthood, energy threshold, cooldown, cap) and cost;
- `move` — movement style (stay / wander / seek_light; later seek_prey / flee);
- `signals` — which Nadi topics the species emits/listens to;
- `life` — lifespan, health rules.

Energy flow upward is set by `gain`/`yields`; the pyramid is ~10% per level. Adding a level/species = writing a descriptor with a different `ahara`; the engine does not change.

## One tick cycle (Meru.step)

A strict sequence of phases:

1. **Update Tejas** — light patches ignite/fade/disappear; the field updates.
2. **Rebuild the spatial grid** — the position index for neighbour lookup.
3. **Digitants act** — each living agent runs its body-tick (movement, feeding per `ahara`, metabolism, emitting to Nadi) and updates its brain. Iterate over a **snapshot** of the population, so newborns act only from the next tick.
4. **Flush Nadi** — deliver all messages emitted during the tick; recipients react.
5. **Death and cleanup** — agents with zero health, eaten, or past their lifespan are removed.

### Predation within a tick

Eating another digitant follows one rule set so the act phase stays deterministic:

- Eating sets an `eaten` flag on the prey; the flagged prey is removed in phase 5, not immediately.
- Every agent checks it is still alive (not eaten, health > 0) at the start of its own body-tick; an agent eaten earlier in the same act phase does not act.
- A flagged prey cannot be eaten twice: the first eater (in snapshot order) wins and receives `yields`; a later would-be eater misses and stays hungry.

## Observation layer

Everything that watches the world; none of it may mutate the world.

### Renderers

- **ASCII (v0.3):** a terminal grid view mapping cell intensity (and later species/state) to glyphs, plus a header line of live counters.
- **Web (v0.4):** a **JSON world snapshot** is serialized at the engine boundary each tick — `{tick, grid: {w, h}, tejas: [nonzero cells], agents: [], counters}` — versioned and additive, so later versions (digitants, species colours, Nadi activity) extend the payload, not the protocol. A small read-only server (FastAPI + uvicorn, optional deps) drives the demo loop, streams one snapshot per tick over WebSocket, and serves the React (Vite) app in `web/`. Play/pause/speed controls pace the demo loop; they never mutate world state.
- **Read-only invariant:** with any renderer attached or absent, a same-seed run produces identical counter logs.

### Counters and measurement

Counters are the measurable half of observability; every readiness criterion in `ROADMAP.md` is asserted against them. The core set, grown per version:

- v0: tick, total Tejas field energy, live patch count.
- v1: per-species population, births and deaths per tick, mean energy and health per species.
- v3: emitted/delivered message counts per topic.
- v4–v5: energy per trophic level, the abundance pyramid.
- v6: per-trait mean and variance per species (histograms over generations).

Counters are emitted as structured log lines / CSV time-series consumable by tests and demos; the renderers show the live subset in their header.

## Configuration and parameters

Two homes for every number — nothing tunable lives as a constant in engine code:

- **World config** — grid size (W, H), the seed, Tejas patch parameters (target count, radius, intensity, lifetime, FOOD_MAX), MAX_POP, demo tick counts. One config file (or dataclass) per demo scenario, passed into the World.
- **Species parameters** — everything per-species lives in the Jati descriptor (`species/*.yaml`), never in code.

Balance tuning — hardest at v4–v5 — happens in these two places only. The seed is always explicit: in the config or on the CLI (`--seed`), never implicit.

## Testing and CI

- **Layout:** `tests/` mirrors the engine modules; `pytest` for tests, `ruff` for linting.
- **Unit tests** per phase, per the Tests list in `ROADMAP.md`; the pysm pitfalls (cargo, on_enter, internal transitions) each get a pinning test.
- **Determinism harness:** two runs with the same seed and config must produce byte-identical counter logs. The cheapest regression net; runs on every CI pass.
- **Smoke runs:** a fixed-seed run of K ticks under the current version's reference parameters, asserting population and energy stay inside a configured band (no explosion, no extinction). Each version's readiness criterion is encoded as its smoke test.
- **CI needs no network, no Node, no pygame:** the engine and all its tests are pure Python. Frontend tests (a fixture snapshot rendered by the React app) live in `web/` and run separately.

## Key invariants and pitfalls

- **cargo, not input (pysm).** Pass event data via cargo (kwargs on Event), NOT via `input=`. The `input` field in pysm is for transition matching; on mismatch the event is silently dropped.
- **on_enter initialization.** pysm does not call the initial state's on_enter itself — do it manually after `initialize()`.
- **Snapshot iteration.** In the act phase, iterate over a snapshot list of the population so that individuals born this tick do not act immediately and break iteration.
- **Internal transitions.** An action without a state change (e.g. lose energy while staying in Wander) must be an internal transition, otherwise re-entering the state re-fires on_enter.
- **RNG discipline.** One `random.Random` instance, owned by the World and passed explicitly to whatever needs randomness. Module-level `random.*` calls are forbidden — they silently break reproducibility.
- **Deterministic Nadi order.** Flush delivers FIFO by emit order; recipients resolve in a stable (id-sorted) order.
- **No double-eat.** Eating flags the prey; the first eater wins; a flagged or dead agent does not act.
- **Observation is read-only.** Renderers, counters, and the web server never mutate the world; toggling them never changes a run.
- **Deterministic phase order** and a single seed are prerequisites for reproducibility.

## Stack and dependencies

- Python 3.11+.
- `pysm` — state machines (the digitants' brain).
- `pyyaml` — Jati descriptors and world configs.
- Optional, observation layer only (the engine never imports them):
  - `pygame` — local graphical visualization;
  - `fastapi` + `uvicorn` — the v0.4 snapshot server;
  - Node + Vite + React — the v0.4 web client in `web/`.
- `yamlfsm` — a separate project, the planned extension for declarative brains; **not a dependency yet**.

## Directory structure (proposed)

```
nadiloka/
  spec/            VISION.md MISSION.md ARCHITECTURE.md ROADMAP.md
    nadiloka_ukr/  Ukrainian translations of the four documents
  nadiloka/        the engine
    world.py       World, the Meru cycle, spatial grid
    tejas.py       the light resource field
    nadi.py        EventBus
    digitant.py    Digitant, two-clock, brain
    jati.py        the species descriptor loader
    render.py      ASCII renderer
    snapshot.py    the world-snapshot serializer (v0.4)
    server.py      the read-only WebSocket server (v0.4, optional deps)
  web/             the React (Vite) viewer (v0.4)
  species/         Jati descriptors (bindu.yaml, chara.yaml, vyaghra.yaml)
  demos/           runnable scenarios per version
  tests/           pytest suites mirroring the engine modules
```

## Extension points

- **Brain from a spec.** The `brain` field in Jati maps to a yamlfsm spec (a separate project), so behaviour becomes fully declarative. Until then, brains are named pysm presets implemented in the engine and selected by the `brain` field.
- **Heterogeneous brains.** Give a few agents a slow "brain clock" with an LLM (local Qwen via mlx) or an RL policy; the rest run on the cheap FSM.
- **Visualization.** Every renderer sits on the same `World.step()` and, from v0.4, the same snapshot schema: colour by state/species, lines for active Nadi channels, population graphs over time — the web viewer is the natural host for these.
