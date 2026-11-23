# 0010. Durable runs, proposals, exactly-once execution, precondition re-checks

- **Date:** 2026-11-16
- **Status:** Accepted

## Context
Write actions (reroutes, transfer orders) need human approval, which can take minutes. Approval must execute exactly once, even with double-clicks, two tabs or network retries. The simulated world keeps moving while a human decides, so a plan can become invalid between drafting and approval (TOCTOU: time-of-check to time-of-use).

## Decision
1. **A run is a state machine in Postgres** (`running → awaiting_approval → running → completed | failed | cancelled`), and every model and tool call goes into an append-only `run_steps` log. The LLM is stateless, so the message history *is* the state: pausing means "stop calling the model", and resuming means "load the history, append the tool result, keep looping".
2. **Write tools never write.** They insert a `proposals` row (`pending`, payload, preconditions, expiry). The harness marks the run `awaiting_approval` and returns. No process waits.
3. **Exactly-once:** approval runs in a single transaction that starts with a conditional claim, `UPDATE proposals SET status='approved' WHERE id=:id AND status='pending' RETURNING *`. Concurrent requests block on the row lock, re-check the `WHERE`, and get 0 rows, which means `409 already handled`.
4. **Precondition re-check:** inside the same transaction, lock the affected rows (trucks, warehouse) and re-check the stored preconditions against the *current* world. If they fail, the proposal becomes `stale` and the agent re-plans.
5. **Reject** with a reason, which becomes the tool result the agent sees. **Expiry** is checked lazily at approval time, so no cron job is needed.

## Alternatives considered
- **Await approval inside the running coroutine** — lost on restart, can't scale, and double execution is possible.
- **SELECT FOR UPDATE plus an idempotency-key table** — correct, but more moving parts than the conditional UPDATE needs here.
- **Locking the truck during the human wait (pessimistic)** — impossible, because the world must keep moving.

## Consequences
- Survives restarts, and every decision is auditable from the step log.
- Needs concurrency tests that race real approvals against a real Postgres.
- "The plan went stale, the agent re-planned" becomes a demo scenario.
