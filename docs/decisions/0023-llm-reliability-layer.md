# 0023. LLM reliability layer: timeouts, retries, self-correction, fallback, idempotent writes

- **Date:** 2026-11-22
- **Status:** Accepted

## Context
On free tiers, failures are routine: 429 rate limits, 5xx errors, timeouts, malformed tool arguments, quota exhaustion. The server can also restart in the middle of a run.

## Decision
1. **Timeouts:** 60 s per LLM call, plus an overall deadline per run.
2. **Retry only temporary errors** (429, 5xx, timeouts), with exponential backoff (1, 2, 4, 8 s) + random jitter, honouring `Retry-After`. Max 4 attempts. Never retry 400/401.
3. **Self-correction:** a tool call that fails validation returns a precise error as the tool result (what was wrong, the valid options). The model gets to fix it; this counts as a step under the max-steps guardrail.
4. **Fallback model:** a configured list `[primary, fallback]`. Each `run_steps` row records which model answered.
5. **Crash-safe resume + idempotent writes:** runs resume from the event log. Proposals have a unique `(run_id, tool_call_id)` key and are inserted with `ON CONFLICT DO NOTHING`, so replaying a step never creates a second proposal.

## Alternatives considered
- **No retries** — free-tier hiccups would fail visible runs.
- **Retry everything** — permanent errors (bad key, bad request) would loop pointlessly.
- **Circuit breakers, retry queues, an LLM gateway service** — real patterns, but speculative for one app with one user.

## Consequences
- Harness tests use `ScriptedModel` to simulate a 429, a timeout, malformed JSON and a crash between steps.
- Eval results and traces must show the model actually used for each step.
