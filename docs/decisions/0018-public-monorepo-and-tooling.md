# 0018. Public monorepo, uv lockfile, and the tooling baseline

- **Date:** 2026-11-22
- **Status:** Accepted

## Context
The project exists for learning and for the portfolio. Frontend and backend change together: a new view type touches both. Installs must be reproducible across the developer's machine, CI, and later deployment.

## Decision
- **One public GitHub repo** (`backend/`, `frontend/`, `docs/`, `labs/`, `docker-compose.yml` for Postgres only), MIT license, built in public from the first commit.
- **Secrets never committed:** `.env` gitignored, `.env.example` committed, a secret-scanning pre-commit hook, and GitHub push protection on. A leaked key is **rotated**, not just deleted from history.
- **Python:** `uv` with `pyproject.toml` (direct dependencies, with ranges) plus `uv.lock` (every package pinned exactly, with hashes), both committed. Also ruff (lint and format), pyright (types), pytest + pytest-asyncio, and pre-commit.
- **Frontend:** npm with `package-lock.json` committed, ESLint and Prettier (or Biome), Vitest. TypeScript types are generated from FastAPI's OpenAPI schema, so frontend and backend can't silently disagree.
- **CI (GitHub Actions):** lint, types, tests against a real Postgres service, frontend build. Evals on a manual trigger.
- **Git:** one branch and one PR per feature, even solo. PRs are where Tier 1 reviews and Tier 2 teach-backs happen (ADR 0012).

## Alternatives considered
- **Separate frontend and backend repos** — separate history, CI and README for changes that always go together. Justified only by separate teams or release cycles.
- **Private until finished** — loses the visible history of how the work was done, which is part of the portfolio.
- **`pip freeze` requirements.txt** — pins versions, but mixes direct and indirect dependencies, captures platform-specific packages, has no hashes, and is painful to update.

## Consequences
- Recruiters get one link: code, decisions, evals and history together.
- Anything public is permanent: secrets hygiene from the first commit.
- Naming: the project was named **Corridor** before the first commit (ADR 0020).
