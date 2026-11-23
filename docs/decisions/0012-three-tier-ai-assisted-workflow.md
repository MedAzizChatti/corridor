# 0012. Three-tier AI-assisted workflow: learn deep, still ship fast

- **Date:** 2026-11-16
- **Status:** Accepted

## Context
Two goals pull against each other: learn deeply (and defend every line in interviews) versus finish fast and move on. Coding agents type faster than any human; what holds value is judgment: specifying, reviewing, testing, debugging.

## Decision
Split the work by learning value:

| Tier | Scope | Who writes | Gate |
|---|---|---|---|
| 1. Hand-built (~15–20%) | New concepts and the interview story: harness loop, approval claim and locks, eval runner | Developer | PR-style review by the mentor |
| 2. AI-built, must explain (~50%) | Domain code: tools, simulator, API, models | Agent | Developer writes tests first (the spec), then a **teach-back gate**: 3 questions answered before it counts as done |
| 3. AI-built, skim (~30%) | Plumbing: Docker, CI, config, frontend boilerplate | Agent | Short summary |

Rules: nothing gets merged that the developer can't explain. The first occurrence of a new concept moves up a tier. Teach-back answers go into `docs/journal.md`.

## Alternatives considered
- **The developer writes everything** — maximum learning, too slow, and it ignores how the industry works now.
- **The agent writes everything** — fast, but the developer can't defend the project or catch the agent's mistakes.

## Consequences
- An estimated ~70% of full-agent speed, with most of the learning.
- The workflow itself (CLAUDE.md, ADRs, tests first, evals) is a portfolio point.
