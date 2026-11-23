# 0005. French and English handled by the model, verified by evals

- **Date:** 2026-11-16
- **Status:** Accepted

## Context
Operators may write in French or English. Current LLMs handle both natively, but weaker free-tier models fail in subtle ways: they answer in English after English tool output, mix decimal formats (`12,5` vs `12.5`), and confuse place names across languages.

## Decision
No translation layer and no language detector. One system-prompt rule: answer in the user's language. Correctness is enforced by French cases in the eval set.

## Alternatives considered
- **Detect, then translate to English and back** — more code, more latency, and meaning gets lost.

## Consequences
- Zero lines of production code for language support.
- Arabic and Darja are out of scope for now. Adding them means new eval cases first.
