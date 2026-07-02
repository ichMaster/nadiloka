# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Nadiloka is an artificial-life ecosystem engine: many simple agents ("digitants") feed along a food chain, communicate through an event bus, and evolve — with behaviour emerging from local rules. The repository currently contains only specs; the engine is implemented from them.

Read the specs in `spec/` before making changes — they are the source of truth, written specifically as context for Claude Code:

- `spec/VISION.md` — philosophy and long-term direction.
- `spec/MISSION.md` — goals, scope, development principles, conventions.
- `spec/ARCHITECTURE.md` — components, data model, tick cycle, invariants.
- `spec/ROADMAP.md` — the layered build plan. **Implement strictly in layer order; do not skip ahead.** Each layer adds one idea, must be runnable at its end, and must pass its readiness criterion (a smoke run showing populations neither explode nor die out).
- `spec/nadiloka_ukr/` — Ukrainian translations of the same four documents. If you change a spec, keep the translation in sync.

## SDLC workflow

Each roadmap phase `vA.B` carries an **Implementation plan** checklist (`NADI-xxx` issues) in ROADMAP.md, detailed in `spec/roadmap/implementation/vA.B-issues.md`. The flow is: `/upload-issues <vA.B-issues.md>` (create GitHub issues with `vA::` labels) → `/execute-issues <label>` (implement one issue per commit, validate, close, tick the roadmap checkbox, write the execution report) → `/release-version A.B.0` (per-phase release; never bump without explicit user confirmation). Semver `A.B.C` = version.phase.fix.

## Stack and conventions

- Python 3.11+. Dependencies are deliberately minimal: `pysm` (FSM brains), `pyyaml` (declarative specs); `pygame` optional and only for visualization. There is no build/test tooling yet — set it up when the first code layer lands.
- All pseudo-randomness goes through one explicit seed; every tick must be reproducible.
- No emoji anywhere: code, docs, diagrams, output.
- New species/behaviours are added via Jati descriptors (YAML in `species/`) and yamlfsm specs — never by editing the engine. If a new species requires engine changes, the abstraction is leaking.

## Architecture essentials

Naming is Sanskrit-derived and used consistently: **Meru** = world clock, **Nadi** = event bus, **Tejas** = light/resource field, **Jati** = declarative species descriptor, **digitant** = agent.

- **Tick cycle (`World.step`) has a fixed phase order:** update Tejas → rebuild spatial grid → digitants act (body-tick + brain) → flush Nadi → death/cleanup. Determinism depends on this order.
- **Two-clock design:** the body-tick runs every Meru tick and must stay pure cheap arithmetic (no heavy computation, no LLM calls); the brain is a small pysm FSM that only re-evaluates the agent's mode.
- **All agent interaction goes through the Nadi bus** (target / radius / global addressing) with deferred delivery: `emit()` queues, `flush()` delivers at end of tick, replies go out the next tick. No direct agent-to-agent references in behaviour logic.
- **Energy flows upward via Jati:** a species' `ahara` (diet) names its prey; prey `yields` → predator `gain`, ~10% per trophic level.
- Proposed layout: engine modules in `nadiloka/` (`world.py`, `tejas.py`, `nadi.py`, `digitant.py`, `jati.py`, `render.py`), species YAML in `species/`, runnable per-layer scenarios in `demos/`.

## Critical invariants (bugs waiting to happen)

- **pysm: pass event data via `cargo` (kwargs on Event), never via `input=`** — `input` is for transition matching and silently drops the event on mismatch.
- **pysm does not call the initial state's `on_enter`** — call it manually after `initialize()`.
- **Iterate over a population snapshot** in the act phase so newborns don't act this tick or break iteration.
- **Use internal transitions** for actions that don't change state, otherwise re-entering a state re-fires `on_enter`.
