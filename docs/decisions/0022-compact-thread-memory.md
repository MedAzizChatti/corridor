# 0022. Conversation context: compact thread memory with artifact references

- **Date:** 2026-11-22
- **Status:** Accepted

## Context
The LLM is stateless. Follow-ups like "reroute **them**" need earlier turns. A thread holds several runs (one per user message). Sending full histories makes tokens explode on free tiers, feeds the model stale world data, and lowers accuracy with noise.

## Decision
- Each model call gets: the system prompt, tool schemas, a world header (operating area, current sim time, units), **compact thread memory**, and the current run's messages.
- Compact memory = for each previous turn: the user message, the final assistant message, and the artifacts produced (ID, type, one-line summary, sim time). Tool calls and raw tool results from earlier runs are dropped.
- Artifacts are **references to which entities**, never sources of their current state: tools always read current state from the database (ADR 0009 applied over time).
- Keep the last 10 turns and drop older ones deterministically. No LLM summarization in M1; add it only if an eval shows a need.
- The context builder is a pure function (thread → messages), Tier 1, unit-tested.
- Multi-turn eval cases (`turns:` in YAML), including a trap: "reroute them" with no previous turn must lead to a clarifying question.

## Alternatives considered
- **Full history** — token blow-up, stale data in context, noisier reasoning.
- **No history** — follow-ups can't be resolved.
- **LLM summarization of old turns** — an extra call, can lose or invent details, hard to test. Deferred.

## Consequences
- A predictable context size of ~4–8k tokens per call.
- Old turns beyond 10 are forgotten; the README must state this limit.
