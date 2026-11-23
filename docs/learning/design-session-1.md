# Design session 1 — reading guide (2026-11-16 → 2026-11-23)

The design conversation, in order: the question, what we decided, and where to read the details.
Read this instead of (or alongside) the raw transcript. If something is unclear, open a session and ask *"explain ADR 00XX using my POS code"*.

| # | Question | Decision (one line) | Read | New concepts |
|---|---|---|---|---|
| 1 | What is the project for? | Learning + portfolio. Not real users | `M1.md` (Goal) | vertical slice |
| 2 | Customer / scope | No real customer. A fictional persona (Atlas Distribution) | ADR 0001 | — |
| 3 | Simulated or real world? | Simulated, deterministic, replayable, with real recorded weather | ADR 0001, 0021 | determinism, seed |
| 3b | Which region? | Geography is data: any operating area. One global hazard source (Open-Meteo) | ADR 0002, 0003 | ports and adapters |
| 3c | Units, languages | UTC + SI inside; FR/EN handled by the model, verified by evals | ADR 0004, 0005 | — |
| 4 | Framework or own harness? | Build our own; compare with LangGraph after M1 (posts) | ADR 0006 | harness, agent loop, tool calling |
| 5 | One agent or many? | One agent, ~7 tools. Multi-agent only with context overload, parallelism or permission isolation | ADR 0007 | — |
| 6 | Which LLM provider? | One OpenAI-compatible adapter; OpenRouter free models; Groq; Ollama; `ScriptedModel` for tests | ADR 0008 | — |
| 7 | Who decides what's on screen? | Constrained generative UI: "reference, don't copy" | ADR 0009 | structured output, artifacts |
| 8 | Approvals | Durable runs, proposals, exactly-once claim, precondition re-check | ADR 0010 + `labs/race-lab` | race condition, check-then-act, transaction ≠ lock, row lock, TOCTOU, optimistic/pessimistic, isolation levels, invariant |
| — | How you code + how we work | Concepts tied to your POS code; ORM with SQL shown; three tiers | ADR 0011, 0012 | lost update |
| 9 | How do we know the agent works? | Three layers of tests/evals, code graders first, pass^3 | ADR 0013 | eval, grader, LLM-as-judge, trace, pass@k vs pass^k, regression |
| 10 | Definition of done | Closed M1 list: S1–S6, US + Spain worlds, auth, Gantt, ≥ 25 evals | `M1.md`, ADR 0014 | confused deputy, authn vs authz |
| 11 | Async or sync? | Async everywhere + no lazy loading | ADR 0015 + `labs/n-plus-one-lab` | event loop, blocking, N+1, MissingGreenlet, selectinload/joinedload |
| 12 | Next.js or React? | React + Vite SPA | ADR 0016 | — |
| 13 | Live data + auth | SSE; JWT in an httpOnly cookie; single origin; CSRF header | ADR 0017 | SSE, Last-Event-ID, XSS, CSRF, SameSite, CORS, token-in-URL |
| 14 | Repo + tooling | Public monorepo; uv + lockfile; ruff, pyright, pre-commit, CI | ADR 0018 | lockfile, transitive deps, supply chain, monorepo, secret rotation |
| — | Name | Corridor | ADR 0020 | — |
| 15 | Geo-maths where? | PostGIS for storage/queries, Shapely for polygons | ADR 0019 | PostGIS, GiST, SRID, geometry vs geography |
| 16 | Simulator | SimClock, fixed time step, cached routes, advisory-lock leader, frozen clock in evals | ADR 0021 | advisory lock, leader election |
| 17 | Conversation memory | Compact thread memory with artifact references | ADR 0022 | context engineering, token budget, stale context |
| 18 | LLM failures | Timeouts, backoff + jitter, self-correction, fallback, idempotency key | ADR 0023 | backoff, jitter, thundering herd, idempotency key |
| 19 | Observability | `run_steps` as the trace; structlog; Run Inspector | ADR 0024 | trace, span, correlation ID, contextvar |
| 20 | Prompt injection | Limit the blast radius by architecture; safe rendering; fencing; eval traps | ADR 0025 | prompt injection, indirect injection, exfiltration |
| — | Workflow + context | Subagents by tier; fresh session per phase; `STATUS.md` as handoff | CLAUDE.md §5–11, `M1-plan.md` | context rot, compaction |

**Suggested reading order** if you reread everything: this file → `M1.md` → ADRs 0010 + race lab (hardest, most valuable) → ADR 0009, 0013 (core AI engineering) → `concepts.md` top to bottom.
