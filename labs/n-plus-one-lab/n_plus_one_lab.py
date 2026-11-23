"""N+1 lab: count the queries your ORM really sends.

Same models as the PFA POS: Employee has many EmployeeRole.
The "list employees with their roles" page, written 4 ways:
  A. sync habit in async code  -> MissingGreenlet crash
  B. the naive async "fix"     -> works, but N+1 queries
  C. selectinload              -> 2 queries
  D. joinedload                -> 1 query

Run:  .venv\\Scripts\\python.exe n_plus_one_lab.py   (see README.md)
"""

import asyncio
import os
import time

from sqlalchemy import ForeignKey, event, select
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, joinedload, mapped_column, relationship, selectinload

DSN = os.getenv("DSN", "postgresql+asyncpg://lab:lab@localhost:5433/lab")
N_EMPLOYEES = 100


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Employee(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    roles: Mapped[list["EmployeeRole"]] = relationship()  # lazy by default, like your POS


class EmployeeRole(Base):
    __tablename__ = "employee_roles"
    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id"))
    role: Mapped[str]


engine = create_async_engine(DSN)
Session = async_sessionmaker(engine, expire_on_commit=False)

# ---- query counter: every SQL statement sent to Postgres goes through here
queries: list[str] = []


@event.listens_for(engine.sync_engine, "before_cursor_execute")
def count_query(conn, cursor, statement, params, context, executemany):
    queries.append(" ".join(statement.split()))


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    async with Session() as db:
        for i in range(1, N_EMPLOYEES + 1):
            roles = ["Vendor"] if i % 3 else ["Vendor", "Admin"]
            db.add(Employee(id=i, name=f"Employee {i}", roles=[EmployeeRole(role=r) for r in roles]))
        await db.commit()


def report(title, rows, started):
    ms = (time.perf_counter() - started) * 1000
    print(f"\n=== {title} ===")
    print(f"  rows: {len(rows)} employees   queries sent: {len(queries)}   time: {ms:.0f} ms")
    for q in queries[:3]:
        print(f"    SQL> {q[:230]}")
    if len(queries) > 3:
        print(f"    ... and {len(queries) - 3} more queries like the last one")


async def a_sync_habit():
    """What your POS does: touch employee.roles and let the ORM fetch it silently."""
    async with Session() as db:
        employees = (await db.execute(select(Employee).limit(N_EMPLOYEES))).scalars().all()
        try:
            return [(e.name, [r.role for r in e.roles]) for e in employees]
        except Exception as exc:
            print("\n=== A. sync habit: access employee.roles directly ===")
            print(f"  CRASH: {type(exc).__name__}")
            print("  Async SQLAlchemy refuses to run a hidden query inside a plain attribute access.")


async def b_naive_fix():
    """The 'fix' people google: await each relationship. Works... one query per employee."""
    queries.clear()
    started = time.perf_counter()
    async with Session() as db:
        employees = (await db.execute(select(Employee).limit(N_EMPLOYEES))).scalars().all()
        rows = [(e.name, [r.role for r in await e.awaitable_attrs.roles]) for e in employees]
    report("B. naive async fix: await e.awaitable_attrs.roles in a loop  (N+1)", rows, started)


async def c_selectinload():
    queries.clear()
    started = time.perf_counter()
    async with Session() as db:
        stmt = select(Employee).options(selectinload(Employee.roles)).limit(N_EMPLOYEES)
        employees = (await db.execute(stmt)).scalars().all()
        rows = [(e.name, [r.role for r in e.roles]) for e in employees]
    report("C. selectinload: employees, then ALL their roles in one IN (...) query", rows, started)


async def d_joinedload():
    queries.clear()
    started = time.perf_counter()
    async with Session() as db:
        stmt = select(Employee).options(joinedload(Employee.roles)).limit(N_EMPLOYEES)
        employees = (await db.execute(stmt)).unique().scalars().all()
        rows = [(e.name, [r.role for r in e.roles]) for e in employees]
    report("D. joinedload: one query with a JOIN", rows, started)


async def main():
    await seed()
    await a_sync_habit()
    await b_naive_fix()
    await c_selectinload()
    await d_joinedload()
    await engine.dispose()
    print()


if __name__ == "__main__":
    asyncio.run(main())
