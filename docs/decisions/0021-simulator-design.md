# 0021. Simulator: injected sim clock, fixed time step, cached routes, single leader

- **Date:** 2026-11-22
- **Status:** Accepted (refines ADR 0001)

## Context
The simulator drives the demo and the evals. Its key property: the world must be a **pure function of (seed, scenario, simulated time)**, so it can be tested, replayed and evaluated.

## Decision
1. **SimClock:** simulated time (default 1 real second = 60 simulated seconds; pause, ×1, ×10). It's injected everywhere. **No code calls `datetime.now()`**: ETAs, proposal expiry and metrics all use the sim clock.
2. **Fixed time step with scheduled events:** each tick moves every in-transit truck in **one SQL statement** (`progress_m += speed × dt`, `position = ST_LineInterpolatePoint(...)`). Speed variation comes from a seeded RNG. Scenario events (a hazard starting, and so on) fire at scheduled simulated times.
3. **Routes are cached:** the routing API is called only at world setup or reroute planning, and results are stored in a `routes` table. Ticks never call external APIs.
4. **Scenario YAML** (world, seed, start time, speed, events with recorded data sources) defines each world.
5. **Single simulator via a Postgres advisory lock** (`pg_try_advisory_lock`): with any number of API workers, exactly one runs the tick loop. If it dies, the lock is released and another takes over.
6. **Evals freeze the clock** per case, so LLM latency can't change the expected answer.
7. It runs as an `asyncio` task in the FastAPI process. The clock and tick loop are Tier 1.

## Alternatives considered
- **Real clock (`datetime.now()`)** — not replayable; demos would take hours.
- **Event-driven (discrete-event) simulation** — fits sparse events, not continuous movement.
- **Per-truck updates in Python** — N round trips per tick (the N+1 lesson).
- **Routing API per tick** — rate limits, and evals would depend on an external, changing service.
- **"Just run one worker"** — correct only until someone deploys with `--workers 4`.

## Consequences
- Every time-dependent function takes the clock as a dependency (easy to fake in tests).
- Ticks briefly wait on approval row locks (ADR 0010, race-lab experiment 4). That's fine at millisecond scale.
