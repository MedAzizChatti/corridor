# 0006. Build our own agent harness, no framework

- **Date:** 2026-11-16
- **Status:** Accepted

## Context
Every agent framework does the same five things: (1) a model adapter, (2) a tool registry with schemas and argument checks, (3) the call → tool → result loop, (4) persisted run state so a run can pause for human approval and resume, (5) guardrails (max steps, budget, tool allow-list, approval-required tools). A main goal of this project is to learn exactly these, and to be able to defend every line.

## Decision
Write our own harness (target: a few hundred lines). Pydantic for tool schemas and structured outputs, and Postgres for run and step state.

## Alternatives considered
- **LangGraph** — built-in checkpointing and interrupts, but heavy abstraction. We'd learn the framework, not agents.
- **PydanticAI** — clean and typed, but it hides the loop, and pause and resume for approval is still on us.
- **Vendor agent SDKs** — tied to one vendor. Our budget means free-tier Gemini or Groq.

## Consequences
- Full understanding and control. Pause, resume and approval fit our own state model.
- We write the boring parts ourselves, including robustness against bad tool calls from weaker models (validate every argument, never trust IDs the model makes up, repair or retry bad JSON).
- Planned follow-up: rebuild the same flow in LangGraph and publish the comparison.
