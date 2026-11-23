# 0017. Live data over SSE; auth with an httpOnly cookie on a single origin

- **Date:** 2026-11-22
- **Status:** Accepted

## Context
Two live streams go server → browser: agent run events and simulator positions. User actions (ask, approve, reject) are occasional requests. The browser's `EventSource` can't send an `Authorization` header, and putting tokens in URLs leaks them into logs, history and `Referer`.

## Decision
**Transport**
- Server-Sent Events for both streams. Plain POST for actions.
- Agent stream events carry `id` = `run_steps.id`. On reconnect the browser sends `Last-Event-ID` and the server replays `WHERE run_id = :id AND id > :last ORDER BY id`. The durable event log (ADR 0010) is the replay buffer.
- The simulator sends all truck positions every tick (~2 KB/s for 40 trucks). No diffing.
- Closing the tab disconnects the *view*; the run continues (it's durable).

**Auth (option A: cookie)**
- At login, the JWT is set as a cookie: `HttpOnly; Secure; SameSite=Lax`. JavaScript never sees the token, so an XSS bug can't steal it. Native `EventSource` works, with built-in reconnect and `Last-Event-ID`.
- **One origin:** in development the Vite dev server proxies `/api` to FastAPI; in production FastAPI serves the built SPA. The browser only ever talks to one site, so there's no CORS and no third-party-cookie problem.
- **CSRF defence:** `SameSite=Lax` plus a required custom header (`X-Corridor-CSRF: 1`) on every state-changing request. Browsers can't add custom headers to cross-site requests without a CORS preflight, and we allow no cross-origin access.

## Alternatives considered
- **WebSocket** — two-way, but we only need server → browser. It needs a hand-written reconnect, protocol and auth on the upgrade.
- **Polling** — laggy and wasteful.
- **Fetch-based SSE + bearer token in localStorage (option B)** — familiar from the PFA POS, but the token can be read by any injected script (XSS), and reconnect/replay becomes the library's job instead of the browser's.
- **Token in the query string** — leaks credentials into logs and history. Never.

## Consequences
- Frontend and backend must share an origin in every environment. Free hosting must serve both from one site (FastAPI serving the SPA, or a proxy/rewrite).
- New concepts to learn and test: XSS, CSRF, SameSite, same-origin policy, CORS.
