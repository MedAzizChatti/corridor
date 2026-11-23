# CLAUDE.md

Behavioral guidelines to reduce common LLM coding mistakes. Merge with project-specific instructions as needed.

**Tradeoff:** These guidelines bias toward caution over speed. For trivial tasks, use judgment.

## 1. Think Before Coding

**Don't assume. Don't hide confusion. Surface tradeoffs.**

Before implementing:
- State your assumptions explicitly. If uncertain, ask.
- If multiple interpretations exist, present them - don't pick silently.
- If a simpler approach exists, say so. Push back when warranted.
- If something is unclear, stop. Name what's confusing. Ask.

## 2. Simplicity First

**Minimum code that solves the problem. Nothing speculative.**

- No features beyond what was asked.
- No abstractions for single-use code.
- No "flexibility" or "configurability" that wasn't requested.
- No error handling for impossible scenarios.
- If you write 200 lines and it could be 50, rewrite it.

Ask yourself: "Would a senior engineer say this is overcomplicated?" If yes, simplify.

## 3. Surgical Changes

**Touch only what you must. Clean up only your own mess.**

When editing existing code:
- Don't "improve" adjacent code, comments, or formatting.
- Don't refactor things that aren't broken.
- Match existing style, even if you'd do it differently.
- If you notice unrelated dead code, mention it - don't delete it.

When your changes create orphans:
- Remove imports/variables/functions that YOUR changes made unused.
- Don't remove pre-existing dead code unless asked.

The test: Every changed line should trace directly to the user's request.

## 4. Goal-Driven Execution

**Define success criteria. Loop until verified.**

Transform tasks into verifiable goals:
- "Add validation" → "Write tests for invalid inputs, then make them pass"
- "Fix the bug" → "Write a test that reproduces it, then make it pass"
- "Refactor X" → "Ensure tests pass before and after"

For multi-step tasks, state a brief plan:
```
1. [Step] → verify: [check]
2. [Step] → verify: [check]
3. [Step] → verify: [check]
```

Strong success criteria let you loop independently. Weak criteria ("make it work") require constant clarification.

---

**These guidelines are working if:** fewer unnecessary changes in diffs, fewer rewrites due to overcomplication, and clarifying questions come before implementation rather than after mistakes.

<!-- ======================================================================
     ADDED 2026-11-23: Corridor project rules (everything below this line).
     Everything above is the original generic CLAUDE.md, left unchanged.
     ====================================================================== -->

---

# Corridor project rules (added)

Corridor (local folder: `flowstate/`) is an AI dispatcher for logistics: a simulated fleet, a tool-using agent, human-approved actions, and evals.
It's a **learning and portfolio project**: the developer must understand and defend every line.

## 5. Start of every session
1. Read `docs/STATUS.md` (where we are, what's next).
2. Read `docs/milestones/M1.md` (definition of done) and the current phase plan in `docs/plans/`.
3. Before touching an area, read its ADRs (`docs/decisions/README.md` is the index). Don't contradict an accepted ADR. Propose a new ADR that supersedes it instead.

## 6. Who writes the code (ADR 0012)
- **Tier 1, the developer writes it:** harness loop, tool registry, context builder, approval claim and locks, SimClock and tick loop, eval runner, the first async endpoint and DB session. **Never write this code for them.** Give a spec, test ideas and hints, then review it like a PR.
- **Tier 2, the agent writes it after the developer writes the tests:** tools, simulator logic, API endpoints, models. Then a teach-back: ask 3 questions before calling it done.
- **Tier 3, the agent writes it:** tooling, CI, Docker, scaffolding, styling. Explain briefly.

## 7. Teaching
- When explaining a new concept, show it in code the developer **already wrote** before using a generic example. Their own code is the most familiar starting point, so the new idea attaches to something they know. Sources: Corridor's own code once it exists; before that, their earlier PFA POS project (`desktop/projects/PFA/POS-back`), e.g. the race in `crud/order.py` `add_order`, the N+1 in `routers/employee.py:58`, the JWT in `localStorage`. The POS is only a source of examples; it is not part of Corridor.
- Add every new concept to `docs/learning/concepts.md` (plain definition + example). Add a row to `docs/learning/post-ideas.md` if it could make a post.
- Whenever ORM code appears in an explanation, show the SQL it emits next to it.
- When the developer asks you to choose, choose and explain why.

## 8. Backend rules
- **Async everywhere** (ADR 0015). No blocking calls in async code (`time.sleep`, `requests`, sync drivers). CPU-heavy work goes through `asyncio.to_thread`.
- **No lazy loading.** Use `selectinload` (one-to-many) or `joinedload` (many-to-one).
- **State that can race** (statuses, stock, capacity, claims): `update(...).where(condition).returning(...)` and `select(...).with_for_update()`. Never load → modify in Python → commit (ADR 0011, 0010).
- **Never call `datetime.now()`**: use the injected `SimClock` (ADR 0021). Store UTC and SI units; convert only at the edges (ADR 0004).
- Geometry in PostGIS, SRID 4326, `geography` for metres. Shapely only for building hazard polygons (ADR 0019).
- LLM access only through the single OpenAI-compatible adapter (ADR 0008). Retries, timeouts and the fallback model live there (ADR 0023).
- **Tools:** validate arguments with Pydantic, return precise errors, enforce the *user's* permissions in code (ADR 0014), return artifact references, not copied data (ADR 0009).
- **Write tools only create proposals**, idempotent on `(run_id, tool_call_id)`. Execution happens only on human approval (ADR 0010, 0023).
- Model output is rendered as safe text/Markdown: no raw HTML, no remote images (ADR 0025).

## 9. Testing
- Tests first. Concurrency and spatial tests run against **real PostGIS**, never SQLite or mocks.
- Harness tests use `ScriptedModel`, with no network.
- Every bug becomes a failing test or eval case **before** it's fixed.
- Assert invariants ("never overbooked"), not incidental outcomes ("P2 wins").

## 10. Process
- One branch and one PR per task. Commit messages: `feat:`, `fix:`, `test:`, `docs:`, `chore:`.
- A new design decision gets a new ADR (copy `docs/decisions/template.md`). Accepted ADRs are never edited, only superseded.
- Failures, fixes and numbers go in `docs/journal.md`.
- **The M1 scope is closed.** New ideas go to the M2 list in `docs/milestones/M1.md`.
- Never commit secrets. `.env` is gitignored; `.env.example` holds fake values.

## 11. Context hygiene
- One session per phase or task. Start fresh rather than carrying an old conversation.
- At a task boundary, run `/compact` with a focus hint, or start a new session.
- Use subagents for work whose output you only need the conclusion of (research, Tier 3 tasks).
- **Before ending a session, update `docs/STATUS.md`** (done / in progress / next / open questions). The repo is the memory, not the chat.
