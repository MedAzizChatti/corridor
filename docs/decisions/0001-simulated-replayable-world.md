# 0001. Simulated, deterministic, replayable world

- **Date:** 2026-11-16
- **Status:** Accepted

## Context
Corridor needs trucks, orders and warehouses to reason about. There is no real fleet or company behind the project. Testing an agent also requires the *same* world to be reproducible on every run.

## Decision
A simulation engine moves a fictional fleet ("Atlas Distribution") over real roads with a simulated clock. Each world comes from a `seed` plus a scenario file (for example `storm_east_coast.yaml`), so any run can be replayed exactly. External signals such as weather can be recorded and replayed into a scenario.

## Alternatives considered
- **Static seed data** — nothing moves, so there's no "live" world to reason about.
- **Real GPS feed or a real company** — not available.

## Consequences
- The golden eval set becomes possible: "in scenario X, the agent must flag trucks 3, 7 and 12."
- Demos don't depend on a real storm happening.
- Cost: the simulator is a real component to build and test (discrete-event simulation).
