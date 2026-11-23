# Architecture Decision Records

Each ADR is a short record of one decision: the context, what we chose, what we rejected, and what it costs us.
An ADR is never edited after it's accepted. If a decision changes, write a new ADR that *supersedes* the old one.

| # | Decision | Status |
|---|---|---|
| [0001](0001-simulated-replayable-world.md) | Simulated, deterministic, replayable world | Accepted |
| [0002](0002-geography-as-data.md) | Geography is data, not code | Accepted |
| [0003](0003-single-global-hazard-source.md) | One global hazard source (Open-Meteo derived polygons) | Accepted |
| [0004](0004-utc-and-si-internally.md) | UTC and SI units internally | Accepted |
| [0005](0005-languages-via-model-verified-by-evals.md) | French and English handled by the model, verified by evals | Accepted |
| [0006](0006-own-agent-harness.md) | Build our own agent harness, no framework | Accepted |
| [0007](0007-single-agent.md) | Single agent, no multi-agent | Accepted |
| [0008](0008-llm-provider-openai-compatible.md) | LLM access through one OpenAI-compatible adapter (OpenRouter default) | Accepted |
| [0009](0009-constrained-generative-ui.md) | Constrained generative UI: reference, don't copy | Accepted |
| [0010](0010-durable-runs-proposals-exactly-once.md) | Durable runs, proposals, exactly-once, precondition re-checks | Accepted |
| [0011](0011-sqlalchemy-orm-with-atomic-updates.md) | SQLAlchemy 2.0 ORM, atomic updates for state that can race | Accepted |
| [0012](0012-three-tier-ai-assisted-workflow.md) | Three-tier AI-assisted workflow | Accepted |
| [0013](0013-three-layer-evals.md) | Three-layer testing and evals, graded by code first | Accepted |
| [0014](0014-agent-acts-with-user-permissions.md) | The agent acts with the user's permissions (no confused deputy) | Accepted |
| [0015](0015-async-backend.md) | Async backend: FastAPI, SQLAlchemy, openai client, httpx | Accepted |
| [0016](0016-react-vite-spa.md) | Frontend: React + Vite + TypeScript SPA | Accepted |
| [0017](0017-sse-and-cookie-auth-same-origin.md) | SSE for live data; httpOnly-cookie auth on one origin | Accepted |
| [0018](0018-public-monorepo-and-tooling.md) | Public monorepo, uv lockfile, tooling baseline | Accepted |
| [0019](0019-postgis-and-shapely.md) | PostGIS for spatial data and queries; Shapely builds hazard polygons | Accepted |
| [0020](0020-project-name-corridor.md) | Project name: Corridor | Accepted |
| [0021](0021-simulator-design.md) | Simulator: sim clock, fixed time step, cached routes, single leader | Accepted |
| [0022](0022-compact-thread-memory.md) | Conversation context: compact thread memory with artifact references | Accepted |
| [0023](0023-llm-reliability-layer.md) | LLM reliability: timeouts, retries, self-correction, fallback, idempotent writes | Accepted |
| [0024](0024-observability-own-trace.md) | Observability: run_steps as trace, structured logs, Run Inspector | Accepted |
| [0025](0025-prompt-injection-blast-radius.md) | Prompt injection: limit the blast radius by architecture | Accepted |

Template: [`template.md`](template.md)
