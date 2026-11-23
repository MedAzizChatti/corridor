# Phase 0 — Workshop Setup Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.
> **Exception:** Task 4 is **Tier 1**: the developer writes it. Agents give hints and review only (CLAUDE.md §6).

**Goal:** A public repo where `docker compose up` + backend + frontend show "DB ok · PostGIS 3.x" in the browser, with CI green.

**Architecture:** Monorepo: `backend/` (FastAPI async + SQLAlchemy async + Alembic, managed by uv) and `frontend/` (Vite + React + TS, proxying `/api` to the backend: single origin). PostGIS runs in Docker; the apps run natively on Windows.

**Tech Stack:** Python 3.12, uv, FastAPI, SQLAlchemy 2 (asyncio) + asyncpg, GeoAlchemy2, Alembic, pydantic-settings, pytest + pytest-asyncio, ruff, pyright · Node 22, npm, Vite, React, TypeScript, Tailwind, ESLint, Prettier, Vitest · Docker (postgis/postgis) · GitHub Actions · pre-commit + gitleaks.

**Spec:** `docs/milestones/M1.md`, `docs/decisions/` (esp. 0011, 0015, 0016, 0017, 0018, 0019), `CLAUDE.md`.

## Global Constraints
- Python `3.12`. Node `22`. Package managers: `uv` (backend), `npm` (frontend). Lockfiles `backend/uv.lock` and `frontend/package-lock.json` are committed.
- PostGIS image: `postgis/postgis:17-3.5`. Host port **5434** (5433 is taken by the labs' `corridor-race-lab`). DB/user/password: `corridor`/`corridor`/`corridor` (dev only, in `.env.example`).
- `DATABASE_URL=postgresql+asyncpg://corridor:corridor@localhost:5434/corridor`
- Backend on port **8000**, all routes under `/api`. Frontend dev server on **5173**, proxying `/api` → `http://localhost:8000`.
- The developer works on Windows (PowerShell). Every command in docs must work there.
- `.env` never committed. Repo is public, MIT licence. Commit prefixes `feat:`/`fix:`/`test:`/`docs:`/`chore:`/`ci:`.
- The local folder stays `flowstate/` (renaming it would lose the session memory path). The GitHub repo is named `corridor`.

## Review Focus
1. **Database down / not started** → `/api/health` must return **503** with `{"status": "error", ...}`, not a 500 stack trace. (Test in Task 4.)
2. **Missing `.env`** → the backend must fail at startup with a clear message naming `DATABASE_URL`. (Test in Task 3: settings without env raise a `ValidationError` mentioning `database_url`.)
3. **A secret committed by mistake** → the pre-commit gitleaks hook must block it. (Verification in Task 1.)
4. **Port clash with the lab container on 5433** → Compose uses 5434. (Verification in Task 2.)
5. **PostGIS extension not enabled in a fresh DB** → the first Alembic migration must create it, and health must report its version. (Tasks 3 + 4.)

---

### Task 1: Repo bootstrap (Tier 3 · subagent; the developer creates the GitHub repo)

**Files:**
- Create: `.gitignore`, `LICENSE` (MIT, copyright line with the developer's name, which they fill in), `README.md` (one-paragraph stub + "Docs: docs/"), `.env.example`, `.pre-commit-config.yaml`
- Modify: none

**Interfaces:**
- Produces: `.env.example` keys `DATABASE_URL`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_DB` (values from Global Constraints)

- [ ] **Step 1:** Write `.gitignore` covering: `.env`, `**/.venv/`, `__pycache__/`, `.pytest_cache/`, `.ruff_cache/`, `node_modules/`, `frontend/dist/`, `*.egg-info/`, `.DS_Store`.
- [ ] **Step 2:** Write `.pre-commit-config.yaml` with hooks: `gitleaks` (secret scan), `ruff` + `ruff-format` (scoped to `backend/`), `end-of-file-fixer`, `trailing-whitespace`, `check-yaml`.
- [ ] **Step 3:** `git init -b main`, then install pre-commit (`uv tool install pre-commit`, or `pip install --user pre-commit` if uv isn't there yet) and `pre-commit install`.
- [ ] **Step 4: Verify the secret scan.** Create a throwaway file containing `OPENAI_API_KEY=sk-proj-` + 40 random alphanumerics, `git add` it, run `pre-commit run gitleaks --all-files`. Expected: **Failed**, a leak is detected. Delete the file.
- [ ] **Step 5:** First commit: `chore: bootstrap repo with docs, labs and tooling` (includes the existing `docs/`, `labs/`, `CLAUDE.md`).
- [ ] **Step 6 (the developer, in the browser):** create the public GitHub repo `corridor` (no README/licence; the repo has them). Then `git remote add origin <url>` and `git push -u origin main`. Turn on *Settings → Code security → Secret scanning + Push protection*.

### Task 2: PostGIS via docker-compose (Tier 3 · subagent)

**Files:**
- Create: `docker-compose.yml`

**Interfaces:**
- Produces: a service `db` on `localhost:5434`, with a named volume `corridor_pgdata` and a healthcheck (`pg_isready`).

- [ ] **Step 1:** Write `docker-compose.yml` with service `db`: image `postgis/postgis:17-3.5`, env from `.env` (`POSTGRES_USER/PASSWORD/DB`), ports `5434:5432`, volume, healthcheck every 5s.
- [ ] **Step 2: Verify.** `docker compose up -d db`, wait until healthy, then `docker compose exec db psql -U corridor -d corridor -c "CREATE EXTENSION IF NOT EXISTS postgis; SELECT postgis_version();"`. Expected: a row starting with `3.5`.
- [ ] **Step 3: Verify no port clash.** `docker ps` shows both `corridor-race-lab` (5433) and the compose `db` (5434) running.
- [ ] **Step 4:** Commit `chore: add PostGIS docker-compose service`.

### Task 3: Backend skeleton and tooling (Tier 3 · subagent)

**Files:**
- Create: `backend/pyproject.toml`, `backend/uv.lock`, `backend/app/__init__.py`, `backend/app/settings.py`, `backend/app/main.py` (app factory, no routes yet), `backend/alembic.ini`, `backend/alembic/env.py` (async), `backend/alembic/versions/0001_enable_postgis.py`, `backend/tests/conftest.py`, `backend/tests/test_settings.py`
- Modify: none

**Interfaces:**
- Produces:
  - `app.settings.Settings(BaseSettings)` with `database_url: str` (required, no default), loading `.env` from the repo root; and `get_settings() -> Settings` (cached).
  - `app.main.create_app() -> FastAPI` (title "Corridor", all routers mounted under `/api`), plus module-level `app = create_app()`.
  - Alembic revision `0001` running `CREATE EXTENSION IF NOT EXISTS postgis`, with a downgrade that drops it.

- [ ] **Step 0 (the developer, once):** install uv on Windows: `powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`, then reopen the terminal and run `uv --version`.
- [ ] **Step 1:** `uv init --app --python 3.12` in `backend/`. Dependencies: `fastapi`, `uvicorn[standard]`, `sqlalchemy[asyncio]>=2.0.30`, `asyncpg`, `geoalchemy2`, `alembic`, `pydantic-settings`. Dev group: `pytest`, `pytest-asyncio`, `httpx`, `ruff`, `pyright`.
- [ ] **Step 2:** Configure in `pyproject.toml`: ruff (line length 100, rules `E,F,I,B,UP,ASYNC`), pyright (`typeCheckingMode = "standard"`), pytest (`asyncio_mode = "auto"`, `testpaths = ["tests"]`).
- [ ] **Step 3: Write the failing test** `tests/test_settings.py::test_missing_database_url_fails_clearly`: with `DATABASE_URL` removed from the environment and `_env_file=None`, constructing `Settings()` raises `pydantic.ValidationError` whose message contains `database_url`.
- [ ] **Step 4:** Run `uv run pytest -v`. Expected: FAIL (`app.settings` doesn't exist).
- [ ] **Step 5:** Implement `Settings` / `get_settings`. Run again. Expected: PASS.
- [ ] **Step 6:** Set up Alembic for async (`alembic init -t async alembic`); `env.py` reads the URL from `get_settings()`; add revision `0001_enable_postgis`. Run `uv run alembic upgrade head` against the compose DB. Expected: no error; `SELECT extname FROM pg_extension` includes `postgis`.
- [ ] **Step 7:** `uv run ruff check . && uv run ruff format --check . && uv run pyright`. Expected: all clean.
- [ ] **Step 8:** Commit `chore: backend skeleton with uv, settings, alembic postgis migration`.

### Task 4: First async DB session + `/api/health` (TIER 1 · THE DEVELOPER WRITES IT)

**Files:**
- Create: `backend/app/db.py`, `backend/app/routers/health.py`, `backend/tests/test_health.py`
- Modify: `backend/app/main.py` (mount the health router)

**Interfaces:**
- Consumes: `get_settings()` (Task 3)
- Produces:
  - `app.db.engine: AsyncEngine`, `app.db.SessionLocal: async_sessionmaker[AsyncSession]` (with `expire_on_commit=False`)
  - `async def get_db() -> AsyncIterator[AsyncSession]` (FastAPI dependency)
  - `GET /api/health` → 200 `{"status": "ok", "postgis_version": "<str>"}`; if the DB is unreachable → **503** `{"status": "error", "detail": "database unavailable"}`

- [ ] **Step 1: Write the failing tests** in `tests/test_health.py` (use `httpx.AsyncClient` with `ASGITransport(app=app)`; note `AsyncClient(app=...)` was removed in httpx 0.28):
  - `test_health_ok`: status 200, `body["status"] == "ok"`, `body["postgis_version"].startswith("3.")`
  - `test_health_db_down_returns_503`: override `get_db` with a session whose engine points at `localhost:1` → status 503, `body["status"] == "error"`
- [ ] **Step 2:** `uv run pytest tests/test_health.py -v`. Expected: FAIL (404 / import error).
- [ ] **Step 3:** Implement `db.py` and the health router. Run the query `SELECT postgis_version()` through the session. Catch the DB connection error and turn it into a 503. *(Mentor hints on request: what `async with` does for the session; why `expire_on_commit=False`; which exception type to catch.)*
- [ ] **Step 4:** Run the tests. Expected: 2 passed.
- [ ] **Step 5: Teach-back (main session):** explain in your own words (a) why `get_db` is a generator with `yield`, (b) what would happen with `time.sleep(1)` inside the endpoint, (c) the SQL your query sends. Write the answers in `docs/journal.md`.
- [ ] **Step 6:** Commit `feat: async db session and health endpoint` on a branch; open a PR; review in the main session.

### Task 5: Frontend skeleton (Tier 3 · subagent)

**Files:**
- Create: `frontend/` (Vite React-TS template), `frontend/vite.config.ts` (proxy), `frontend/src/App.tsx`, `frontend/src/api/health.ts`, `frontend/src/api/health.test.ts`
- Modify: none

**Interfaces:**
- Consumes: `GET /api/health` (Task 4)
- Produces: `fetchHealth(): Promise<{status: "ok" | "error"; postgis_version?: string; detail?: string}>` in `src/api/health.ts`

- [ ] **Step 1:** `npm create vite@latest frontend -- --template react-ts`, then add Tailwind, ESLint, Prettier, Vitest. Configure `server.proxy` so `/api` → `http://localhost:8000`.
- [ ] **Step 2: Write the failing test** `health.test.ts`: with `fetch` mocked to return `{status: "ok", postgis_version: "3.5"}`, `fetchHealth()` resolves to that object; with a 503 response it resolves to `{status: "error", ...}` (it does not throw).
- [ ] **Step 3:** `npm test`. Expected: FAIL. Implement `fetchHealth`. Expected: PASS.
- [ ] **Step 4:** `App.tsx` shows a badge: green "DB ok · PostGIS 3.5" or red "DB unavailable".
- [ ] **Step 5: Verify end to end:** `docker compose up -d db`, `uv run uvicorn app.main:app --reload` (backend), `npm run dev` (frontend), open `http://localhost:5173` → green badge. Stop the DB → refresh → red badge.
- [ ] **Step 6:** `npm run lint && npm run build`. Expected: clean. Commit `feat: frontend skeleton with health badge`.

### Task 6: CI (Tier 3 · subagent)

**Files:**
- Create: `.github/workflows/ci.yml`

**Interfaces:**
- Consumes: the commands from Tasks 3–5.

- [ ] **Step 1:** Job `backend`: ubuntu-latest, service container `postgis/postgis:17-3.5` (health-checked), `astral-sh/setup-uv`, `uv sync --locked`, `alembic upgrade head`, `ruff check`, `ruff format --check`, `pyright`, `pytest -v`. `DATABASE_URL` points at the service.
- [ ] **Step 2:** Job `frontend`: `actions/setup-node` (22, npm cache), `npm ci`, `npm run lint`, `npx tsc --noEmit`, `npm test -- --run`, `npm run build`.
- [ ] **Step 3:** Trigger on `push` and `pull_request`. Push a branch, open a PR. Expected: both jobs green.
- [ ] **Step 4: Verify CI catches failures:** on a scratch branch, break one assertion in `test_health_ok` and push. Expected: the backend job is red. Delete the branch.
- [ ] **Step 5:** Commit `ci: backend and frontend checks with real PostGIS`. Update `docs/STATUS.md`: Phase 0 done, next is Phase 1.
