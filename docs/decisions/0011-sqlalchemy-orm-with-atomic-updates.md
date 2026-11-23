# 0011. SQLAlchemy 2.0 ORM, with atomic updates for state that can race

- **Date:** 2026-11-16
- **Status:** Accepted

## Context
The developer already knows SQLAlchemy ORM from previous projects. The concurrency guarantees we need (conditional claims, row locks) are database features, and the ORM can express all of them.

## Decision
Use the SQLAlchemy 2.0 ORM, with two rules:
1. **State changes that can race** (stock, statuses, claims, capacity) use `update(...).where(<condition>).returning(...)` and `select(...).with_for_update()`, so the database does the check. Never "load the object, change the attribute in Python, commit" for these.
2. **Know the SQL:** `echo=True` in development, and every explanation shows the SQL the ORM emits.

## Alternatives considered
- **Raw SQL everywhere (asyncpg)** — the clearest view of the database, but new syntax on top of new concepts, and more boilerplate.
- **ORM with attribute updates for everything** — the easy path, and it produces lost updates (the PFA POS `add_order` bug).

## Consequences
- Familiar tooling, so the learning effort goes into concepts, not syntax.
- Code review must check rule 1 explicitly. It's the bug the ORM makes easy.
