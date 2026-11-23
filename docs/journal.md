# Dev journal

Short dated notes: what broke, what we tried, what fixed it, and the numbers before and after.
This is the raw material for blog posts and X/LinkedIn posts. Write while it's fresh.

Format:
```
## YYYY-MM-DD — short title
- Problem:
- Tried:
- Fix:
- Numbers (before → after):
- Lesson:
```

---

## 2026-11-16 — Planning session 1 (grill-me)
- Decided: a simulated replayable world, geography as data, one global hazard source, UTC and SI units, FR/EN via the model, our own harness, a single agent. See `docs/decisions/` 0001–0007.
- Lesson: my first region design had three hazard adapters, a resolver and border merging. Checked against "Simplicity First", one global source (Open-Meteo) covered everything, *and* the border problem disappeared. Simpler designs often remove problems instead of solving them.
- Lesson: on multi-agent, knowing *when and why* beats knowing *how*. Three conditions justify a second agent (context overload, parallelism, permission isolation). None applied, so we don't build it.

## 2026-11-16 — Race lab: watching approval bugs happen
- Problem: approve-proposal can double-execute, overbook a warehouse, or execute a stale plan.
- Tried: a naive "SELECT status → if pending → act" inside a transaction.
- Fix: a conditional `UPDATE … WHERE status='pending' RETURNING` claim, `FOR UPDATE` on the dependent rows, and a precondition re-check in the same transaction.
- Numbers (naive → fixed): 50 concurrent clicks gave 50 transfer orders → 1; a 10-pallet warehouse went to −3 → never negative; a stale reroute executed → caught as "stale".
- Lesson: a transaction is not a lock. A check that isn't protected by a lock is a guess. Exactly-once does not protect against TOCTOU.

## 2026-11-20 — N+1 lab: 101 queries to show 100 employees
- Problem: listing employees with their roles (same as the PFA POS `routers/employee.py:58`) sends one hidden query per employee.
- Tried: accessing `employee.roles` in async code → `MissingGreenlet` crash. The googled fix (`await e.awaitable_attrs.roles` in a loop) works but keeps the N+1.
- Fix: `selectinload(Employee.roles)` sends 2 queries; `joinedload` sends 1.
- Numbers (localhost): 101 queries / ~100 ms → 2 queries / ~8 ms. With a cloud DB (5–50 ms per round trip) that's 0.5–5 s → 10–100 ms.
- Lesson: async SQLAlchemy's "annoying" crash is a feature. It makes hidden queries impossible to ignore.

## 2026-11-23 — Backend skeleton (Phase 0 Task 3)
- Surprise: `uv init --app` (uv 0.13) generated a packaged `src/` layout with a build backend. Replaced it with a flat `backend/app/` and `[tool.uv] package = false`: the backend is an app, not a library.
- Surprise: the `postgis/postgis` image auto-enables postgis (plus `postgis_topology`, `postgis_tiger_geocoder`) in the default DB, so `alembic upgrade` there proves nothing. Verified migration 0001 on a scratch DB created from `template0`: upgrade → postgis 3.5.2 present; downgrade → gone.
- Decision: the downgrade is a plain `DROP EXTENSION postgis`, no `CASCADE`. On the dev DB it fails (other extensions depend on postgis); that's wanted: `CASCADE` would one day silently drop every geometry column.
- Gotcha (WSL → Windows exe): env vars only cross into `uv.exe` if listed in `WSLENV`.
