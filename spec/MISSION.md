# Nadiloka — Mission

> Project context document for Claude Code. States WHY we are building this and HOW to approach it. Guides decisions during development.

## Mission

Build a minimal, transparent, and extensible artificial-life engine in which an ecosystem with trophic levels and evolution emerges from simple declarative rules — and build it in layers, so that each step is self-contained, runnable, and understandable.

## Goals

- Provide an observable model of an ecosystem: resource → producers → consumers → predators → evolution.
- Keep the engine cheap so it scales to hundreds or thousands of agents.
- Make species and behaviour declarative (Jati + yamlfsm), not hardcoded.
- Serve as a personal sandbox for experiments in ALife, FSM/HSM, and multi-agent systems.

## Development principles (how to build)

These principles should directly guide the code Claude Code writes:

1. **In layers, one idea at a time.** Implement strictly per `ROADMAP.md`. Each layer adds exactly one concept and stays runnable at its end. Do not jump several layers ahead.
2. **Cheap body-tick.** The hot loop is pure arithmetic — no heavy computation and no LLM calls. Complexity goes into the brain, which ticks less often or only when needed.
3. **Determinism.** A single tick must be reproducible: deferred message delivery (flush at end of tick), iterating over a population snapshot, a fixed phase order. Pseudo-randomness goes through one controlled seed.
4. **Declarative over code.** New species and behaviours are added via descriptors (Jati) and specs (yamlfsm), not engine changes. If a new species requires editing the engine, that is a sign the abstraction is leaking.
5. **Low coupling via the bus.** Agents interact only through Nadi messages. No direct agent-to-agent references in behaviour logic.
6. **Observability built in.** Each layer ships with a way to see its result (a renderer) and measure it (counters: populations, energy, events).
7. **Balance verified by running.** After each layer, a smoke run proves the system neither explodes nor dies out under reasonable parameters.

## In scope

- World model, the Tejas resource, the food chain, the Nadi bus, reproduction, evolution.
- ASCII / lightweight visualization for observation.
- Declarative descriptions of species and behaviour.

## Out of scope (non-goals)

- Neural-network brains by default (the brain is an FSM; LLM/RL is an optional late extension).
- Realtime 3D graphics, a physics engine, networked multiplayer.
- Optimizing a single metric or "winning" — this is an open sandbox.
- Premature performance optimization before a layer works correctly.

## Success criteria

- Every layer from `ROADMAP.md` is implemented, runs, and passes its readiness criterion.
- Under reasonable parameters, populations neither explode nor die out entirely; the expected emergent patterns are visible.
- Adding a new species requires no engine changes — only a Jati descriptor.
- The code stays readable; the hot loop stays cheap.

## Conventions

- Implementation language: Python (3.11+).
- Minimal dependencies: `pysm` (state machines), `pyyaml` (specs). `pygame` — optional, for visualization only.
- Documentation in prose, without excessive formatting.
- No emoji icons anywhere: in diagrams, documents, code, or text.
- Pseudo-randomness always through an explicit seed for reproducibility.
