# Status

_Update this at the end of every session (CLAUDE.md §11). The repo is the memory, not the chat._

**Last updated:** 2026-11-23
**Current phase:** Phase 0 (setup), Task 2 done → Task 3 next

## Done
- Design session (grill-me): 25 ADRs in `docs/decisions/`, M1 definition of done (`docs/milestones/M1.md`), roadmap (`docs/milestones/M1-plan.md`), Phase 0 plan (`docs/plans/phase-0-setup.md`).
- Labs: `labs/race-lab` (exactly-once, capacity race, TOCTOU, simulator vs lock + 3 pytest tests), `labs/n-plus-one-lab`.
- Learning docs: `docs/learning/concepts.md` (glossary), `docs/learning/post-ideas.md`, `docs/learning/design-session-1.md` (reading guide to the design conversation).
- CLAUDE.md: Corridor rules added below the original generic rules.

## In progress
- Phase 0 Task 1 done: repo public at github.com/MedAzizChatti/corridor, pre-commit + gitleaks verified, private files gitignored (transcript, post-ideas.md). Git runs from Windows (VS Code, Git Bash), commit email = GitHub noreply.
- Phase 0 Task 2 done: `docker-compose.yml`, PostGIS 3.5 healthy on 5434, volume `corridor_pgdata`. The image auto-enables postgis in the default DB; the Alembic migration must still create it.

## Next
1. Developer's homework (optional, recommended): race-lab exercises; n-plus-one-lab exercises; fix the POS `add_order` race + N+1 with real-Postgres tests.
2. Phase 0 Task 3 (backend skeleton). First install uv (Step 0).

## Open questions
- None blocking. Deferred: deployment (M2).
