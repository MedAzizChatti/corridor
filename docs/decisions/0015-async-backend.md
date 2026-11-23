# 0015. Async backend: FastAPI, SQLAlchemy, openai client and httpx

- **Date:** 2026-11-20
- **Status:** Accepted

## Context
The backend mostly waits: LLM calls (1–5 s), weather and routing APIs, and the database. It also needs a simulator running in the background forever, streaming of agent answers to the UI, and parallel tool calls. Sync FastAPI uses one sleeping thread per waiting request (a pool of about 40).

## Decision
Async throughout: async FastAPI endpoints, async SQLAlchemy 2.0 (asyncpg driver), the async `openai` client, and `httpx.AsyncClient` for external APIs. The simulator runs as an `asyncio` task. CPU-heavy work (large Shapely operations) goes through `asyncio.to_thread`.

Rules:
1. **No blocking calls in async code:** no `time.sleep` or `requests`, and no sync DB drivers. One blocking call freezes every user.
2. **No lazy loading:** relationships are loaded explicitly (`selectinload` by default, `joinedload` for many-to-one). Async SQLAlchemy crashes on lazy loads (`MissingGreenlet`), which keeps N+1 queries visible.
3. The first async endpoint, DB session and simulator task are Tier 1 (hand-built), per ADR 0012.

## Alternatives considered
- **Sync (as in the PFA POS)** — familiar, but streaming, the background simulator and parallel tool calls become awkward. It would also avoid a core skill for AI-backend jobs.

## Consequences
- One process handles many concurrent agent runs while they wait on LLMs.
- New failure modes to learn (blocking the event loop, `MissingGreenlet`); see `labs/n-plus-one-lab`.
- Possible blog post: "Why AI backends are async".
