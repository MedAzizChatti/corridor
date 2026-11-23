# 0007. Single agent, no multi-agent

- **Date:** 2026-11-16
- **Status:** Accepted

## Context
Multi-agent setups (planner, specialists, supervisor) are fashionable. A second agent is justified only when at least one of these holds:
1. **Context overload** — too many tools or documents for one prompt.
2. **Parallelism** — independent subtasks that are too slow one after another.
3. **Permission isolation** — a part must not see certain data or tools.

Milestone 1 needs about 7 tools: `get_hazards`, `find_affected_shipments`, `get_fleet_status`, `list_warehouses`, `plan_reroute` (compute only), `draft_transfer_order` (write intent → approval), `query_metrics`. None of the three conditions applies.

## Decision
One agent with a small set of well-designed tools. Executing an approved action is plain deterministic backend code (a transaction, a lock and an idempotency key), never the LLM.

## Alternatives considered
- **Multi-agent (planner, weather, routing, supervisor)** — several times the prompts, failure points and LLM calls (a problem on free-tier rate limits), traces that are harder to debug, and evals that are harder to write. It solves a problem we don't have.

## Consequences
- One trace explains every decision, and evals stay simple.
- Revisit when the tool count passes about 20–25 or a condition above becomes true. The first step then is a **router** that picks a tool subset per request, not agents talking to each other.
- Learning note: knowing *when and why* to use multi-agent matters more than knowing *how*.
