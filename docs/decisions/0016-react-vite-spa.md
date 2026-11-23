# 0016. Frontend: React + Vite + TypeScript SPA, talking only to FastAPI

- **Date:** 2026-11-22
- **Status:** Accepted

## Context
The frontend logs in, shows a chat next to agent-chosen views (map, chart, table, Gantt, document), receives streamed agent output, and shows the live simulation. It's an app behind a login: no SEO. All logic and auth already live in FastAPI. The map, live updates and streaming are client-side by nature.

## Decision
A single-page app built with React + Vite + TypeScript. It talks only to the FastAPI API.
Libraries: TanStack Query (server data), MapLibre GL (map, no API key), Recharts (charts), a small Gantt library or our own SVG timeline, and Tailwind (styling). Most of the frontend is Tier 3; the view registry and the streaming hook are Tier 2 (ADR 0012).

## Alternatives considered
- **Next.js** — SSR, server components and API routes would duplicate FastAPI and add a server/client split with no benefit here. It appears in more job postings, but the developer already has Next.js experience in another project (JobScout).

## Consequences
- One backend, one source of truth.
- The static build can be hosted anywhere for free, or served by FastAPI.
- Note: the browser's `EventSource` can't send an `Authorization` header. Streaming plus auth needs either cookie-based auth or fetch-based SSE (decided with the transport and auth details).
