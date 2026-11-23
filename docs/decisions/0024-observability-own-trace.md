# 0024. Observability: run_steps as the trace, structured logs, Run Inspector

- **Date:** 2026-11-22
- **Status:** Accepted

## Context
Bad runs must be explainable after the fact: what the model saw and decided, which tool returned what, latency, tokens, retries, and which model. The append-only `run_steps` log (ADR 0010) already records each step.

## Decision
1. **`run_steps` is the trace.** Columns: `seq`, `kind` (model/tool/approval/error), `model`, `prompt_tokens`, `completion_tokens`, `latency_ms`, `tool_name`, `tool_args`, `result_summary`, `artifact_id`, `error`, `attempt`, `sim_time`, `created_at`. README metrics come from SQL over this table.
2. **Structured JSON logs (structlog)** with a `run_id` correlation ID set once per run in a `contextvar` and added to every log line automatically.
3. **Run Inspector** page in the frontend: one run's trace as a timeline (steps, timings, tokens, retries, artifacts). It's the same data the eval tooling shows.

## Alternatives considered
- **Hosted LLM tracing (Langfuse, LangSmith, Helicone)** — another dependency, prompts leave the machine, and it hides the mechanics. Possible M2 comparison.
- **OpenTelemetry + Jaeger/Grafana** — built for many services; heavy for one.
- **Metrics dashboards and alerting** — no on-call, one user.

## Consequences
- No new services. Traces live next to the data they describe.
- The Run Inspector doubles as a demo feature ("how the agent reasoned").
