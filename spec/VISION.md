# Nadiloka — Vision

> Project context document for Claude Code. Describes the essence, philosophy, and long-term vision. Not an implementation spec (see `ARCHITECTURE.md`) or a plan (see `ROADMAP.md`).

## In one sentence

Nadiloka is an artificial-life world where many tamagotchi agents (digitants) live, feed along a food chain, communicate through an event bus, and evolve over time — while all the interesting behaviour emerges from simple local rules.

## What it is

Not a game to be won, but an observable ecosystem sandbox. You define the rules of the world and its species, seed a population, and watch trophic cascades, waves of birth and death, cooperation, predation, and adaptation unfold. The goal is not to control each agent, but to create conditions under which life organizes itself.

## The name cosmology

The whole naming system comes from a single Sanskrit-yogic layer (kindred to the Terra Tacita trilogy):

- **Nadiloka** — the world ("a world woven from channels").
- **Meru** — the central axis: the master tick, the world clock around which everything is synchronized.
- **Nadi** — the event bus: the network of channels through which communication flows.
- **Tejas** — the base resource: sunlight-energy that appears in patches and travels across the world.
- **Jati** — the descriptive language of species ("species, kind"): a declarative genome.
- **digitants** — the inhabitants (digital + ants).

## Experience vision

What we want to see on screen:

- A living field of Tejas light travelling across the world.
- Producers that bloom in the light and wither when it leaves.
- Herbivores that follow the producers in a wave, and predators that follow the herbivores.
- An energy pyramid: many producers, few predators.
- Cooperation and predator-prey signals running through the Nadi channels.
- Evolutionary drift of traits under environmental pressure over many generations.

## Design principles

1. **Emergence from local rules.** No central control. Complex population-level behaviour must arise from simple individual rules and interactions.
2. **Two-clock.** Every agent has a cheap deterministic body-tick (the body) and a light brain that only re-evaluates its mode. The cheapness of the body is what makes scaling to thousands of agents possible.
3. **Spec-driven.** Species are described declaratively (Jati), brain behaviour declaratively (yamlfsm). Adding a species or a trophic level means writing a descriptor, not rewriting the engine.
4. **Communication only through the bus.** Agents hold no direct references to one another. All interaction is messages on Nadi. This keeps coupling low and the system extensible.
5. **Tick determinism.** Deferred message delivery and iterating over a population snapshot make each tick reproducible.
6. **Observability.** The world must be visible (ASCII now, graphics later) and its state measurable (populations, energy flows, event counters).

## Long-term vision

- A full food chain of several trophic levels with a stable (if oscillating) equilibrium.
- Evolution: heredity of the Jati genome with mutation and natural selection, producing specialization and arms races.
- Heterogeneous brains: most agents on a cheap FSM, a few on a slow LLM clock (local Qwen via mlx) or an RL policy.
- A rich visual observation tool (colour by state/species, lines for active Nadi channels, population graphs over time).

## What it is NOT

- Not about neural networks (despite the associations — the brains here are finite state machines).
- Not realtime 3D and not a game to be won.
- Not a simulation aimed at optimizing a single metric — it is an open sandbox for observation.
