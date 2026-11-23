# 0014. The agent acts with the user's permissions (no confused deputy)

- **Date:** 2026-11-20
- **Status:** Accepted

## Context
Approvals need identity (who approved?) and authorization (who may approve?). The agent acts on behalf of a user. If its tools run with full database rights, a low-privilege user can ask the agent to do something they couldn't do themselves. This is the *confused deputy* problem.

## Decision
- JWT auth with two roles: `dispatcher` (ask, draft proposals) and `manager` (also approve). Plus a demo-login button.
- Every agent run is bound to the user who started it. Every tool receives that user's identity and role and **enforces permissions in code**. The prompt is never a security boundary.
- `approved_by` is recorded on every executed proposal.

## Alternatives considered
- **No auth in M1** — approvals without identity make the audit trail meaningless.
- **Permission rules in the system prompt** — models can be talked out of prompt rules. Code can't.

## Consequences
- An eval trap case checks that a dispatcher asking the agent to approve is refused by the tool.
- Every new tool must declare the role it requires.
