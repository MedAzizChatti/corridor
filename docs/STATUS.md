# Status

_Update this at the end of every session (CLAUDE.md §11). The repo is the memory, not the chat._

**Last updated:** 2026-11-23
**Current phase:** Phase 0 (setup), Task 1 in progress

## Done
- Design session (grill-me): 25 ADRs in `docs/decisions/`, M1 definition of done (`docs/milestones/M1.md`), roadmap (`docs/milestones/M1-plan.md`), Phase 0 plan (`docs/plans/phase-0-setup.md`).
- Labs: `labs/race-lab` (exactly-once, capacity race, TOCTOU, simulator vs lock + 3 pytest tests), `labs/n-plus-one-lab`.
- Learning docs: `docs/learning/concepts.md` (glossary), `docs/learning/post-ideas.md`, `docs/learning/design-session-1.md` (reading guide to the design conversation).
- CLAUDE.md: Corridor rules added below the original generic rules.

## In progress
- Phase 0 Task 1: files written (`.gitignore`, `.gitattributes`, `LICENSE` with a `<YOUR NAME>` placeholder, `README.md`, `.env.example`, `.pre-commit-config.yaml`); `git init -b main` done with Windows Git. Remaining (developer, PowerShell): fill in LICENSE name, install pre-commit, gitleaks verification, first commit, create GitHub repo + push + push protection.
- Decisions: git and pre-commit run from Windows PowerShell, not WSL. `awel_conv_3Al_projet.md` stays local (gitignored).

## Next
1. Developer's homework (optional, recommended): race-lab exercises; n-plus-one-lab exercises; fix the POS `add_order` race + N+1 with real-Postgres tests.
2. Finish Phase 0 Task 1 (steps above), then Task 2 (docker-compose).
3. Install uv (Phase 0, Task 3, Step 0). The GitHub CLI isn't installed; create the repo in the browser.

## Open questions
- None blocking. Deferred: deployment (M2).
