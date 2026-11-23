# 0013. Three-layer testing and evals, graded by code first

- **Date:** 2026-11-18
- **Status:** Accepted

## Context
Agents are non-deterministic: one successful try proves nothing. Failure modes: wrong or missing tools, made-up IDs, wrong result set, wrong view, wrong language, proposing writes when it shouldn't (or not proposing them when it should), and too many steps, tokens or seconds.

## Decision
1. **Unit tests** (pytest) on deterministic code: geo-maths, tools, approvals. Every push.
2. **Harness tests** with `ScriptedModel`: pause and resume, max steps, bad JSON, made-up IDs. Every push, in CI.
3. **Agent evals** with a real model on deterministic scenario worlds, one YAML file per case. Run manually or nightly, not on every push (rate limits).
- Graders are **code first**: sets of artifact IDs, tools called, view types, `proposes_write`, language, step count. An LLM judge only for things code can't check, and only after checking it against hand grades.
- Each case runs 3 times; report the pass rate and **pass^3** (passes every time). Write-action cases must pass^3.
- Every bug found becomes an eval case **before** it is fixed.
- Plain YAML cases, a Python runner (Tier 1, hand-built), and results JSON committed to git. No eval platform.

## Alternatives considered
- **An LLM judge for everything** — expensive, noisy, and unreliable unless checked against human grades. Not needed: "reference, don't copy" (ADR 0009) makes most outputs gradable by code.
- **Hosted eval platforms (LangSmith, Braintrust)** — useful at scale, but speculative here and they hide the mechanics we want to learn.
- **Real-model evals on every push** — burns free-tier limits, and flaky CI.

## Consequences
- Model choice and prompt changes are decided by numbers.
- README metrics (pass^3, latency, unapproved writes = 0) come straight from the committed results.
- The case set can be published as a Hugging Face dataset.
