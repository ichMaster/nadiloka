# Nadiloka — Roadmap

> Project context document for Claude Code. A layered, versioned development plan. Implement strictly in order: each version adds one idea, and each phase inside it must be runnable and pass its readiness criterion before moving on.

Seven self-contained versions, built in order: **v0** World + light (Tejas) → **v1** Producers (Bindu) → **v2** Producer movement → **v3** Nadi bus + producer signals → **v4** Consumers (Chara) → **v5** Predators (Vyaghra) → **v6** Evolution. Versions are numbered from 0; phases inside a version are numbered `vA.B` (A = version, B = phase), e.g. `v4.2`. Each phase lists a **Goal**, a short description, a **Tasks** list, a **Definition of Done (DoD)** that is the layer's readiness criterion, and the **Tests** (unit checks plus a smoke run) that encode it. Each phase also has an implementation breakdown — a per-phase GitHub-issues file (`NADI-xxx` issues with sizes, dependencies, and acceptance criteria) under [roadmap/implementation/](roadmap/implementation/) (e.g. `v0.1-issues.md`), derived from that phase's Tasks list.

Arc of the world: the model grows resource (v0) → producers (v1) → movement (v2) → communication (v3) → herbivores (v4) → predators (v5) → evolution (v6); observability grows alongside it — a living light field, then colonies, then movement regimes, then settlement patterns, then two-level oscillation, then a three-level cascade, then trait drift over generations — rendered in the terminal from v0.3 and in the browser (React) from v0.4. Throughout, two things never change: the **body-tick stays cheap** (pure arithmetic, no LLM) and **every tick stays deterministic** (fixed phase order, one seed, snapshot iteration, deferred delivery). Complexity is added only by version, never all at once.

**Versioning (`A.B.C`).** `A` = roadmap version (v0→0 … v6→6), `B` = phase within it (`v4.2` → `4.2.0`), `C` = a post-release fix on that phase. Roadmap phase `vA.B` → semver `A.B.0`; a fix after it bumps `C`. (These seven versions map onto the original ladder as Layer 1 → v0 … Layer 7 → v6.)

## The ladder principle

- One new idea per version.
- Each phase stays runnable at its end.
- Each phase has a way to see its result (a renderer) and measure it (counters).
- After each version, a smoke run proves the system neither explodes nor dies out under reasonable parameters.

Dependencies are tight: movement (v2) is needed by consumers (v4); Nadi (v3) by predator signals (v5); evolution (v6) builds on reproduction, which appears in v1. **Do not reorder** — movement (v2) deliberately precedes communication (v3): each strongly changes the balance, and introducing them separately means seeing the effect of each cleanly.

---

## v0 — World and light (Tejas)

The foundation: an empty Nadiloka with the Meru clock and a living Tejas light field — no digitants yet. It establishes the invariants everything later depends on: the fixed five-phase tick order, a single seeded RNG, deterministic replay, the spatial-grid scaffold, and the observation layer (an ASCII renderer + counters, then a web viewer). Depends on: nothing — this is the base.

### v0.1 — Skeleton and the Meru tick

**Goal:** an empty world ticks deterministically.

Stand up the project skeleton and the `nadiloka/` engine package, the `World` container (config, a single seeded RNG, tick counter, empty population), and `Meru.step()` with the fixed phase order stubbed — update Tejas → rebuild grid → act → flush Nadi → death — each phase a no-op hook. The point is to lock the phase order and the reproducibility seam before any state exists.

**Tasks:**
- Repo skeleton + the `nadiloka/` package; `pyproject.toml` (ruff + pytest); minimal deps (`pysm`, `pyyaml`).
- `World` holding config, one seeded `random.Random`, a tick counter, and an empty population dict.
- `Meru.step()` calling the five phases in fixed order, each an empty hook.
- A `demos/` runner that steps N ticks; a counters scaffold (tick, population, energy).

**DoD:** `World.step()` runs N times with no state and no error; two runs with the same seed produce identical counter logs.

**Tests:** unit — same seed yields an identical RNG draw sequence and tick count; the five phases are called once each per tick in the fixed order.

**Implementation plan** (issue details in [roadmap/implementation/v0.1-issues.md](roadmap/implementation/v0.1-issues.md)):

- [x] NADI-001 — Project skeleton & tooling (S)
- [x] NADI-002 — `World` container: config, seeded RNG, tick counter, population (S; after NADI-001)
- [x] NADI-003 — `Meru.step`: the five-phase hook order (S; after NADI-002)
- [x] NADI-004 — Demo runner + counters scaffold (S; after NADI-003)

### v0.2 — Space and the Tejas field

**Goal:** light patches ignite, live, fade, and reappear across the grid.

Add the bounded grid and the Tejas scalar field driven from the "update Tejas" phase. Patches ignite at seeded random cells, illuminate their radius, decay over a lifetime, disappear, and respawn elsewhere, holding a target number of live patches.

**Tasks:**
- A W×H bounded grid (coords `(x, y)`, no edge wrapping) + neighbourhood helpers.
- `tejas.py`: a scalar field, each cell `0..FOOD_MAX`; `Patch{center, radius, intensity, lifetime}`.
- Patch lifecycle in the update-Tejas phase: ignite, illuminate, fade, disappear, respawn; hold a target live-patch count.
- A total field-energy counter.

**DoD:** patches appear, live their lifetime, fade, and reappear; total field energy fluctuates around a steady intended level, with no runaway growth or collapse.

**Tests:** unit — no cell exceeds `FOOD_MAX`; total energy stays within a band over M ticks (fixed seed); patch ignite/decay/respawn transitions fire correctly.

**Implementation plan** (issue details in [roadmap/implementation/v0.2-issues.md](roadmap/implementation/v0.2-issues.md)):

- [x] NADI-005 — Grid and neighbourhood helpers (S; after NADI-002)
- [x] NADI-006 — Tejas scalar field + `Patch` model (M; after NADI-005)
- [x] NADI-007 — Patch lifecycle in the update-Tejas phase (M; after NADI-006, NADI-003)
- [x] NADI-008 — Field-energy counter and energy-band test (S; after NADI-007)

### v0.3 — ASCII renderer and the light demo

**Goal:** see the living light field.

Add the observation layer over the v0.2 field and prove Layer 1's readiness with a smoke run.

**Tasks:**
- `render.py`: an ASCII grid view mapping cell intensity to brightness glyphs; a header line of counters (tick, energy, live patches).
- A `demos/light.py` scenario wiring World + Tejas + renderer over a loop.
- A smoke run at reasonable parameters.

**DoD (Layer 1 readiness):** the renderer shows a living, moving light field; total energy holds steadily at the intended level over the smoke run.

**Tests:** smoke — a fixed-seed run of K ticks stays within the energy band and renders without error; unit — the intensity→glyph mapping is total.

**Implementation plan** (issue details in [roadmap/implementation/v0.3-issues.md](roadmap/implementation/v0.3-issues.md)):

- [ ] NADI-009 — ASCII renderer (S; after NADI-006)
- [ ] NADI-010 — `demos/light.py` scenario (S; after NADI-009, NADI-007)
- [ ] NADI-011 — Layer smoke run: the living light field (S; after NADI-010)

### v0.4 — Web visualization (React)

**Goal:** watch the world live in the browser — a second renderer alongside the ASCII one.

A decoupled web observation layer: the Python side exposes read-only **world-state snapshots** per tick (a small server streaming JSON over WebSocket) and a **React app** renders them — the Tejas field now; digitants, species colours, and Nadi activity ride the same channel in later versions. It is **another renderer over the same `World.step()`**: strictly observation, never input into the tick — with the web layer on or off, a same-seed run produces identical counters (the determinism invariant). The snapshot schema is generic from the start (tick, grid, cells, agents, counters) so later versions **extend the payload, not the protocol**. The server and the Node/React tooling are optional observation-layer dependencies (like `pygame`) — the engine never imports them. Depends on: v0.2 (the field) and v0.3 (the counters/demo loop).

**Tasks:**
- A **JSON snapshot schema** + serializer at the engine boundary: `{tick, grid: {w, h}, tejas: [nonzero cells], agents: [], counters}`; versioned and additive so digitants/species/events extend it later without breaking the viewer.
- A small **read-only server** (FastAPI + uvicorn, optional deps): drives the demo loop, streams a snapshot per tick over WebSocket, serves the built React bundle; a `--web` flag on the demo runner; a tick-rate/pace control.
- A **React app** (Vite, `web/`): a canvas grid rendering cell intensity as brightness, a header of counters (tick, total energy, live patches), play/pause and speed controls (they pace the demo loop, never mutate world state).
- **Read-only guard:** the viewer has no write path into the world; the sim produces snapshots, the web layer only consumes them.

**DoD:** running the light demo with `--web` shows the living, moving Tejas field in the browser, updating each tick, with counters matching the ASCII renderer; a same-seed run with the web layer on and off produces identical counter logs; without `--web` (or without Node installed) everything from v0.3 works unchanged.

**Tests:** unit — the snapshot serializer is faithful (field cells and counters round-trip; empty cells omitted) and additive fields don't break parsing; the read-only invariant (same seed, web on/off → identical counter logs); pause/speed affect pacing only, never state. Frontend — a minimal render test: a fixture snapshot draws the expected grid and counters (no live server in CI).

**Implementation plan** (issue details in [roadmap/implementation/v0.4-issues.md](roadmap/implementation/v0.4-issues.md)):

- [ ] NADI-012 — JSON snapshot schema + serializer (M; after NADI-007)
- [ ] NADI-013 — Read-only snapshot server (M; after NADI-012)
- [ ] NADI-014 — React viewer app (M; after NADI-012)
- [ ] NADI-015 — Read-only guard and determinism proof (S; after NADI-013, NADI-014)

---

## v1 — Producers, stationary (Bindu)

The first life. Bindu are stationary producers that absorb Tejas, accumulate energy, and reproduce — "plants" that follow the light through birth and death while never moving themselves. This version stands up the Digitant, the two-clock, the minimal FSM brain, the Jati loader, and the population lifecycle, and puts the spatial grid to real use. Depends on: v0.

### v1.1 — Digitant and the Jati loader

**Goal:** a species descriptor instantiates living (idle) digitants on the grid.

Introduce the Digitant and the declarative species loader. The brain is a single-mode FSM here, but the pysm invariants are respected from the start so later species inherit a correct base.

**Tasks:**
- `digitant.py`: `Digitant{id, pos, needs, health, age, lifespan, repro_cd, jati}` + the two-clock skeleton (body-tick hook + brain hook).
- A minimal pysm brain (one mode) honouring the invariants: manual initial `on_enter`, internal transitions, event data via `cargo` (never `input=`).
- `jati.py`: load and validate a YAML descriptor (`jati, needs, harvest, yields, reproduce, life`); author `species/bindu.yaml`.
- Wire the population dict; the rebuild-grid phase now fills the spatial hash from live digitants; the act phase iterates a population **snapshot**.

**DoD:** from `bindu.yaml` the world spawns N Bindu at seeded positions; they appear in the renderer and the spatial index; ticking ages them deterministically.

**Tests:** unit — Jati loads/validates fields; snapshot iteration (a newborn injected mid-act does not act this tick); the spatial hash returns correct neighbours; the pysm initial `on_enter` fires.

**Implementation plan** (issue details in [roadmap/implementation/v1.1-issues.md](roadmap/implementation/v1.1-issues.md)):

- [ ] NADI-016 — Digitant dataclass + two-clock skeleton (M; after NADI-003)
- [ ] NADI-017 — Minimal pysm brain honouring the invariants (M; after NADI-016)
- [ ] NADI-018 — Jati loader + `species/bindu.yaml` (M; after NADI-001)
- [ ] NADI-019 — Population wiring: spawn, spatial hash, snapshot iteration (M; after NADI-016, NADI-018, NADI-005)

### v1.2 — Feeding and metabolism

**Goal:** Bindu harvest Tejas and gain or lose energy.

**Tasks:**
- Body-tick: harvest `gain` from the cell and `harvest.radius` neighbourhood of the Tejas field, capped by what the field holds; debit the harvested energy from the field.
- Metabolism: energy decays per tick; hunger rises; the brain re-evaluates mode from fresh needs (Idle/Hungry as internal transitions).
- Health: falls under sustained starvation, recovers slowly when fed.
- Counters: mean energy, mean health, harvested-this-tick.

**DoD:** Bindu on lit cells accumulate energy and stay healthy; Bindu in darkness starve and lose health; the Tejas field is visibly drawn down where they feed.

**Tests:** unit — energy conservation on harvest (field loss equals agent gain, clamped); starvation lowers health and feeding recovers it; mode re-evaluation is an internal transition (no `on_enter` re-fire).

**Implementation plan** (issue details in [roadmap/implementation/v1.2-issues.md](roadmap/implementation/v1.2-issues.md)):

- [ ] NADI-020 — Harvest from the Tejas field (M; after NADI-019, NADI-007)
- [ ] NADI-021 — Metabolism, needs decay, and mode re-evaluation (M; after NADI-017, NADI-020)
- [ ] NADI-022 — Health model + species counters (S; after NADI-021)

### v1.3 — Reproduction and death

**Goal:** the population sustains itself on the moving light.

**Tasks:**
- Reproduce: at adulthood + energy threshold + cooldown and under `MAX_POP`, spawn a new Bindu in a nearby free cell, paying the energy `cost`; the newborn is added after the snapshot.
- Death/cleanup phase: remove digitants at zero health or past `lifespan`.
- A `demos/bindu.py` scenario; balance counters (births, deaths, population).

**DoD (Layer 2 readiness):** under reasonable parameters the Bindu population holds steadily on the moving light — colonies bloom on lit zones and die as the light leaves — neither exploding to `MAX_POP` nor dying out entirely.

**Tests:** smoke — a fixed-seed run of K ticks keeps population in a healthy band (`0 < pop < MAX_POP`); unit — reproduction respects threshold/cooldown/cap and debits `cost`; death removes exactly the qualifying agents.

**Implementation plan** (issue details in [roadmap/implementation/v1.3-issues.md](roadmap/implementation/v1.3-issues.md)):

- [ ] NADI-023 — Reproduction (M; after NADI-022)
- [ ] NADI-024 — Death and cleanup phase (S; after NADI-022)
- [ ] NADI-025 — `demos/bindu.py` + balance smoke run (M; after NADI-023, NADI-024)

---

## v2 — Producer movement

Bindu learn to move. First undirected wandering, then directed seeking of light — turning the stationary "plant" into something that chases patches, forms queues, and depletes resources. A `move` style switch (stay / wander / seek_light) exposes three distinct population regimes. Depends on: v1.

### v2.1 — Random wandering

**Goal:** Bindu move by an undirected walk.

**Tasks:**
- A `move` field in Jati (`stay` | `wander`); body-tick movement: a seeded random step to a free neighbour cell, bounded, no wrap.
- The spatial hash reflects new positions (already rebuilt in the grid phase).
- Renderer shows motion; a mean-displacement counter.

**DoD:** with `move: wander` Bindu drift over the grid; with `move: stay` they behave exactly as in v1.

**Tests:** unit — a wander step stays in bounds and respects occupancy; determinism (same seed → same paths); `stay` is a no-op.

**Implementation plan** (issue details in [roadmap/implementation/v2.1-issues.md](roadmap/implementation/v2.1-issues.md)):

- [ ] NADI-026 — The `move` field + wander step (M; after NADI-019, NADI-018)
- [ ] NADI-027 — Motion observability (S; after NADI-026, NADI-009)

### v2.2 — Seek light

**Goal:** Bindu move toward brighter cells.

**Tasks:**
- `move: seek_light`: pick the step maximizing local Tejas (gradient ascent over the neighbourhood; ties broken by the seeded RNG).
- Wire the style switch into the demo (`stay` / `wander` / `seek_light`).
- Counters to distinguish the regimes (mean energy, clustering, field depletion).

**DoD (Layer 3 readiness):** switching movement style yields three visibly different regimes — stationary colonies, diffuse drift, and light-chasing clusters that deplete patches and form queues.

**Tests:** smoke — each of the three styles runs K ticks without collapse and produces distinguishable counters; unit — seek picks the brightest reachable cell and is deterministic under ties.

**Implementation plan** (issue details in [roadmap/implementation/v2.2-issues.md](roadmap/implementation/v2.2-issues.md)):

- [ ] NADI-028 — `seek_light` movement (M; after NADI-026)
- [ ] NADI-029 — Three-regime demo and smoke (M; after NADI-028, NADI-025)

---

## v3 — Nadi and communication

The event bus. Agents stop being solitary: they communicate through Nadi with three addressing modes and deferred delivery, so cascades stay bounded and the tick stays deterministic. Producers gain modest signals — crowding, rich zones — that produce the first collective behaviour. Placed before consumers so its effect on settlement is seen cleanly. Depends on: v2.

### v3.1 — The Nadi bus

**Goal:** deferred, addressed messaging wired into the tick.

**Tasks:**
- `nadi.py`: `Message{topic, sender, payload, addressing}`; `emit()` queues; `flush()` delivers at end of tick; replies emitted during delivery go out the next tick.
- Addressing: `target=id` (one agent), `radius=r` (neighbours via the spatial hash), else global.
- Wire `flush()` into the flush-Nadi phase; a subscription registry; event counters (emitted, delivered per topic).

**DoD:** a message emitted this tick is delivered in the same tick's flush; a reply is delivered the next tick; radius addressing hits exactly the in-range neighbours; delivery order is deterministic.

**Tests:** unit — deferred delivery (emit-during-tick delivered at flush; reply delayed one tick); each addressing mode targets the right set; counters match; delivery order is deterministic.

**Implementation plan** (issue details in [roadmap/implementation/v3.1-issues.md](roadmap/implementation/v3.1-issues.md)):

- [ ] NADI-030 — Message model + deferred queue (M; after NADI-003)
- [ ] NADI-031 — Addressing modes with deterministic resolution (M; after NADI-030, NADI-019)
- [ ] NADI-032 — Subscription registry + brain wiring + counters (M; after NADI-031, NADI-017)

### v3.2 — Producer signals

**Goal:** Bindu coordinate settlement through Nadi.

**Tasks:**
- Topics `crowd_signal` (emitted when local density is high) and `bloom` (emitted on a rich Tejas zone); Bindu listen and bias movement/reproduction (avoid overcrowding, settle toward blooms).
- A global Nadi on/off toggle.
- Counters: clustering/evenness, signals per topic.

**DoD (Layer 4 readiness):** toggling Nadi on/off noticeably changes the settlement pattern — a more even spread and less overcrowding with it on.

**Tests:** smoke — Nadi on vs off over the same seed yields measurably different clustering counters, both stable; unit — signals emit under the right conditions and listeners react.

**Implementation plan** (issue details in [roadmap/implementation/v3.2-issues.md](roadmap/implementation/v3.2-issues.md)):

- [ ] NADI-033 — `crowd_signal` and `bloom` emission (M; after NADI-032)
- [ ] NADI-034 — Listener reactions: settlement bias (M; after NADI-033, NADI-026)
- [ ] NADI-035 — Nadi toggle + clustering counters + smoke (M; after NADI-034, NADI-025)

---

## v4 — Consumers (Chara)

The second trophic level. Chara are herbivores (`ahara: Bindu`) that hunt, eat, and pass energy upward (prey `yields` → predator `gain`), move with real needs and a full brain, and reproduce. This is where balance gets hard: with random movement predator and prey rarely meet, so the directed seeking from v2 becomes a survival tool. The target is two-level Lotka-Volterra oscillation. Depends on: v2 (movement) and v1 (the lifecycle); benefits from v3.

### v4.1 — Chara and eating Bindu

**Goal:** one digitant eats another; energy flows up a level.

**Tasks:**
- `species/chara.yaml` with `ahara: Bindu`; the eat action wired generically through Jati (`ahara` names the prey species or `tejas`), so adding a level needs no engine change.
- Eat: when a Chara is co-located with or in range of a Bindu, transfer prey `yields` → predator `gain`; mark the prey eaten (removed in the death phase).
- An energy-per-level counter.

**DoD:** Chara gain energy by eating Bindu; eaten Bindu die; the roughly 10% transfer ratio holds via `yields`/`gain`.

**Tests:** unit — eating transfers `yields`→`gain` and removes the prey exactly once (no double-eat within a tick); the generic `ahara` resolves prey with no engine change.

**Implementation plan** (issue details in [roadmap/implementation/v4.1-issues.md](roadmap/implementation/v4.1-issues.md)):

- [ ] NADI-036 — Generic `ahara` prey resolution (M; after NADI-018, NADI-019)
- [ ] NADI-037 — The eat action: `yields`→`gain`, eaten flag, no double-eat (M; after NADI-036)
- [ ] NADI-038 — `species/chara.yaml` + energy-per-level counter (S; after NADI-037)

### v4.2 — Needs, brain, and seek-prey

**Goal:** Chara live a full digitant life.

**Tasks:**
- The full brain: Wander / Hungry / Sleeping as pysm modes with internal transitions; needs (hunger, energy) with rates from Jati.
- `move: seek_prey` — when Hungry, move toward the nearest known prey (via the spatial hash or a hunger signal); wander otherwise.
- Reproduction and death for Chara (as v1.3, per its Jati).

**DoD:** Chara wander when fed, seek Bindu when hungry, reproduce when rich, and die when starved or old.

**Tests:** unit — brain modes transition on need thresholds (internal, no `on_enter` re-fire); `seek_prey` heads toward the nearest prey deterministically; reproduction and death honour the Jati.

**Implementation plan** (issue details in [roadmap/implementation/v4.2-issues.md](roadmap/implementation/v4.2-issues.md)):

- [ ] NADI-039 — The full brain: Wander / Hungry / Sleeping (M; after NADI-017)
- [ ] NADI-040 — `seek_prey` movement (M; after NADI-039, NADI-028)
- [ ] NADI-041 — Chara reproduction and death (S; after NADI-038, NADI-023, NADI-024)

### v4.3 — Two-level balance

**Goal:** a persistent two-echelon ecosystem.

**Tasks:**
- A `demos/chara.py` two-species scenario; parameter tuning for coexistence.
- Population time-series counters for both levels; a phase-offset indicator.

**DoD (Layer 5 readiness):** the Bindu and Chara populations oscillate out of phase; under reasonable parameters neither level dies out permanently over a long smoke run.

**Tests:** smoke — a long fixed-seed run keeps both populations above zero with detectable out-of-phase oscillation; a runaway/collapse case is flagged as a regression guard on the tuned parameters.

**Implementation plan** (issue details in [roadmap/implementation/v4.3-issues.md](roadmap/implementation/v4.3-issues.md)):

- [ ] NADI-042 — `demos/chara.py` two-species scenario (S; after NADI-040, NADI-041)
- [ ] NADI-043 — Time-series counters + phase-offset indicator (M; after NADI-042)
- [ ] NADI-044 — Balance tuning + the Lotka-Volterra smoke guard (M; after NADI-043)

---

## v5 — Predators (Vyaghra)

The third trophic level and the payoff of the bus. Vyaghra are predators (`ahara: Chara`) that hunt through Nadi (`hunt`) while prey flee (`flee`) — the v3 communication takes on dramatic meaning. The goal is a full three-level trophic cascade with a stable-if-oscillating equilibrium and a standing abundance pyramid. Depends on: v4 and v3.

### v5.1 — Vyaghra and the third level

**Goal:** a top predator eats Chara.

**Tasks:**
- `species/vyaghra.yaml` with `ahara: Chara`; reuse the generic eat/lifecycle/brain from v4 (descriptor-only, no engine change).
- Three-level energy-pyramid counters.

**DoD:** Vyaghra gain energy by eating Chara; the third level lives, reproduces, and dies with no engine changes beyond the descriptor.

**Tests:** unit — adding `vyaghra.yaml` wires a third level via `ahara` alone; the eat/lifecycle path reused from v4 works unchanged.

**Implementation plan** (issue details in [roadmap/implementation/v5.1-issues.md](roadmap/implementation/v5.1-issues.md)):

- [ ] NADI-045 — `species/vyaghra.yaml`: the third trophic level (S; after NADI-044, NADI-036)
- [ ] NADI-046 — Three-level energy-pyramid counters (S; after NADI-045)

### v5.2 — Hunt and flee via Nadi

**Goal:** predator-prey signalling drives behaviour.

**Tasks:**
- `hunt` (a Vyaghra broadcasts a hunt in radius) and `flee` (a Chara receiving it, or sensing a predator, runs away) topics over v3.
- Movement responds: predators seek, prey flee (directed avoidance); the `signals` field in Jati declares who emits and who listens.

**DoD:** a hunting Vyaghra makes nearby Chara flee; hunts and flights are visible in the counters and the renderer.

**Tests:** unit — `hunt` emits in radius and reaches exactly the in-range prey; a fleeing Chara moves away from the sender; signals honour the Jati `signals` list.

**Implementation plan** (issue details in [roadmap/implementation/v5.2-issues.md](roadmap/implementation/v5.2-issues.md)):

- [ ] NADI-047 — `hunt` and `flee` topics (M; after NADI-045, NADI-032)
- [ ] NADI-048 — Movement responses: pursue and evade (M; after NADI-047, NADI-040)

### v5.3 — Three-level cascade and the pyramid

**Goal:** a standing three-level ecosystem.

**Tasks:**
- A `demos/vyaghra.py` three-species scenario; tuning for coexistence.
- An abundance-pyramid counter (producers most numerous, predators fewest) and per-level time-series.

**DoD (Layer 6 readiness):** stable-if-oscillating coexistence of all three levels over a long smoke run; the abundance pyramid holds (Bindu > Chara > Vyaghra).

**Tests:** smoke — a long fixed-seed run keeps all three levels above zero with the pyramid ordering intact; a collapse of any level fails the guard.

**Implementation plan** (issue details in [roadmap/implementation/v5.3-issues.md](roadmap/implementation/v5.3-issues.md)):

- [ ] NADI-049 — `demos/vyaghra.py` three-species scenario (S; after NADI-048)
- [ ] NADI-050 — Cascade tuning + the pyramid smoke guard (M; after NADI-049, NADI-046)

---

## v6 — Evolution

Heredity and variation. An offspring inherits its parent's Jati genome with small mutations (needs thresholds, movement speed, signal sensitivity, feeding efficiency); natural selection does the rest. Over many generations, observable traits drift toward advantageous values — specialization, a predator-prey arms race, adaptation to the light regime. Depends on: v5 (and reproduction from v1).

### v6.1 — Heritable genome and mutation

**Goal:** offspring inherit mutated traits.

**Tasks:**
- Treat the mutable Jati fields as a genome carried per-digitant (not only per-species); reproduction copies the parent genome and applies small seeded, bounded mutations per trait: needs thresholds, move speed, signal sensitivity, feeding efficiency.
- Keep the hot body-tick reading traits cheaply.

**DoD:** offspring differ slightly and heritably from parents; mutations are bounded and seeded (reproducible); a single-species run shows trait variance appearing over generations.

**Tests:** unit — offspring genome equals parent ± bounded mutation (deterministic under seed); traits stay within legal ranges; per-digitant traits drive the body-tick.

### v6.2 — Selection and drift

**Goal:** traits shift under environmental pressure.

**Tasks:**
- Trait counters/histograms over time (population mean and variance per trait, per species); a generations counter.
- An evolution demo with a defined selective pressure (e.g. a harsher light regime or an arms race).

**DoD (Layer 7 readiness):** over many generations, observable traits shift statistically toward advantageous values under the imposed pressure (visible in the histograms).

**Tests:** smoke — a long fixed-seed run under a defined pressure moves a trait's population mean in the predicted direction beyond noise; unit — the histogram/statistics counters are correct.

---

## Notes on the ladder

- **Balance is hardest at v4-v5.** The food chain tends to break under random movement (prey and predator rarely meet). This is exactly where directed movement from v2 (seek prey / flee) becomes a survival tool for the pyramid.
- **Declarative growth.** From v4 on, adding a trophic level is mostly writing a Jati descriptor with a different `ahara`, not rewriting the engine. If a new species needs engine changes, the abstraction is leaking.
- **Do not reorder.** Movement (v2) deliberately precedes communication (v3): each strongly changes the balance, and introducing them separately means seeing the effect of each cleanly.

## Current status

- Present: specs only (`VISION`, `MISSION`, `ARCHITECTURE`, `ROADMAP`). No engine code yet.
- Next step: **v0.1** (skeleton + the Meru tick), then the rest of v0 (world + Tejas) as a clean base, then v1 (Bindu on Tejas).
