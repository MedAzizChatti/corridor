# 0009. Constrained generative UI: reference, don't copy

- **Date:** 2026-11-16
- **Status:** Accepted

## Context
The headline feature: the agent decides whether an answer is best shown as a map, chart, table or document. LLMs produce wrong data when asked to copy large structured payloads (coordinates, order lists), and every copied token counts against free-tier limits.

## Decision
- Tools store their results on the backend as **typed artifacts with IDs** (for example `a_17: ShipmentSet`). The LLM sees only a short summary plus the ID.
- The agent's final answer is a structured output: a `message` plus a list of `views`, each with a type from a **fixed registry** that references artifact IDs:
  ```json
  {"message": "...", "views": [{"type": "map", "layers": ["a_12:hazard", "a_17:shipments"]}]}
  ```
- The backend validates it: the artifacts exist, and the view type is compatible with the artifact type. If validation fails, it falls back to each artifact's **default view**.
- v1 registry: `map`, `chart`, `table`, `document` (the transfer order card). Gantt later.

## Alternatives considered
- **The LLM writes UI code (JSX or HTML)** — unreliable, slow, and unsafe (executing code the model wrote).
- **Purely deterministic views from tool results** — reliable but loses the "agent chooses the presentation" capability. Kept as the fallback.

## Consequences
- The screen can never show made-up data: the only thing the model can make up is an ID, and validation catches that.
- Far fewer output tokens.
- Each new view type means one registry entry, one compatibility rule and one frontend component.
