# 0004. UTC and SI units internally

- **Date:** 2026-11-16
- **Status:** Accepted

## Context
The worlds span time zones and both metric and imperial conventions. Mixed units in tool outputs lead to wrong numbers in agent answers.

## Decision
Store and compute everything in UTC and SI units (meters, seconds, kg). Convert only at the edges: the UI, and the text shown to the user.

## Alternatives considered
- **Local time and units per company throughout** — conversion bugs spread into every layer.

## Consequences
- Tools always return the same units, so the agent and the evals have one convention to rely on.
- Formatting for display is one explicit layer.
