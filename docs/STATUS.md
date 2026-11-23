# Status

_Update this at the end of every session (CLAUDE.md §11). The repo is the memory, not the chat._

**Last updated:** 2026-11-23
**Current phase:** Phase 0 (setup), Task 3 done → Task 4 next (Tier 1: the developer writes it)

## Done
- Design session (grill-me): 25 ADRs in `docs/decisions/`, M1 definition of done (`docs/milestones/M1.md`), roadmap (`docs/milestones/M1-plan.md`), Phase 0 plan (`docs/plans/phase-0-setup.md`).
- Labs: `labs/race-lab` (exactly-once, capacity race, TOCTOU, simulator vs lock + 3 pytest tests), `labs/n-plus-one-lab`.
- Learning docs: `docs/learning/concepts.md` (glossary), `docs/learning/post-ideas.md`, `docs/learning/design-session-1.md` (reading guide to the design conversation).
- CLAUDE.md: Corridor rules added below the original generic rules.

## In progress
- Phase 0 Task 1 done: repo public at github.com/MedAzizChatti/corridor, pre-commit + gitleaks verified, private files gitignored (transcript, post-ideas.md). Git runs from Windows (VS Code, Git Bash), commit email = GitHub noreply.
- Phase 0 Task 2 done: `docker-compose.yml`, PostGIS 3.5 healthy on 5434, volume `corridor_pgdata`. The image auto-enables postgis in the default DB; the Alembic migration must still create it.
- Phase 0 Task 3 done: `backend/` (uv, Python 3.12, flat `app/`, `package = false`), `Settings`/`get_settings` (+ test: missing `DATABASE_URL` fails clearly), `create_app()` with an empty `/api` router, async Alembic reading the URL from settings, migration `0001` (verified up/down on a fresh `template0` DB). ruff, format, pyright clean. Run backend commands from Windows (`cd backend; uv run ...`).

## Next
1. Developer's homework (optional, recommended): race-lab exercises; n-plus-one-lab exercises; fix the POS `add_order` race + N+1 with real-Postgres tests.
2. Phase 0 Task 4 (Tier 1, the developer writes it): `app/db.py`, `/api/health`, tests first. Mount the router on `api` in `app/main.py`.

## Open questions
- None blocking. Deferred: deployment (M2).
