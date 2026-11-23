# N+1 lab

Count the queries your ORM really sends. Same models as the PFA POS (an employee has many roles).
Companion to [ADR 0015](../../docs/decisions/0015-async-backend.md) and [ADR 0011](../../docs/decisions/0011-sqlalchemy-orm-with-atomic-updates.md).

## Run (Windows, PowerShell)

It reuses the race lab's Postgres container (`corridor-race-lab`, port 5433). Make sure Docker Desktop is running.

```powershell
cd labs\n-plus-one-lab
docker start corridor-race-lab
python -m venv .venv                                          # first time only
.venv\Scripts\python.exe -m pip install -r requirements.txt   # first time only
.venv\Scripts\python.exe n_plus_one_lab.py
```

If the container doesn't exist yet, create it with the `docker run` command in `../race-lab/README.md`.

## Expected output

```
=== A. sync habit: access employee.roles directly ===
  CRASH: MissingGreenlet

=== B. naive async fix: await e.awaitable_attrs.roles in a loop  (N+1) ===
  rows: 100 employees   queries sent: 101   time: ~100 ms
    SQL> SELECT employees.id, employees.name FROM employees LIMIT $1
    SQL> SELECT ... FROM employee_roles WHERE $1 = employee_roles.employee_id
    ... and 99 more like it

=== C. selectinload ===
  rows: 100 employees   queries sent: 2   time: ~8 ms
    SQL> SELECT employees.id, employees.name FROM employees LIMIT $1
    SQL> SELECT ... FROM employee_roles WHERE employee_roles.employee_id IN ($1, $2, ..., $100)

=== D. joinedload ===
  rows: 100 employees   queries sent: 1   time: ~8 ms
    SQL> SELECT ... FROM (SELECT ... FROM employees LIMIT $1) AS anon_1 LEFT OUTER JOIN employee_roles ...
```

## What to notice

1. **N+1 = 1 query for the list + N queries, one per row.** B sends 101 queries to show 100 employees. Your POS does exactly this in `routers/employee.py:58` (`employee.roles` inside the list comprehension), one hidden query per employee.
2. **The time difference here is ~10×, on localhost.** Postgres is on your own machine, so each round trip costs ~1 ms. With a cloud database (Neon, RDS) each round trip is 5–50 ms. Then 101 queries take **0.5–5 seconds**, and 2 queries take 10–100 ms. N+1 is invisible in development and painful in production.
3. **Async made the bug visible.** In sync code (your POS) the hidden query just happens. Async SQLAlchemy *crashes* instead (A), forcing you to choose how to load. The naive fix (B) silences the crash but keeps the N+1. The real fix is C or D.
4. **selectinload vs joinedload:**
   - `selectinload` sends 2 simple queries (`WHERE employee_id IN (...)`). Best for **one-to-many** (an employee has many roles). The default choice.
   - `joinedload` sends 1 query with a JOIN, but repeats the employee's columns once per role. Best for **many-to-one** (an order has one customer). Needs `.unique()` for collections.

## Exercises

1. **Predict, then run:** change `N_EMPLOYEES` to 500. How many queries does B send? And C? Did the time grow the same way for both?
2. In D, remove `.unique()`. What error do you get, and why does a JOIN create duplicate employees?
3. Add `echo=True` to `create_async_engine(...)` and rerun. This is the habit for Corridor (ADR 0011): always know what SQL your ORM sends.
4. **Fix your own POS:** in `PFA/POS-back/app/crud/employee.py`, add `.options(selectinload(models.Employee.roles))` to the query in `get_employees`. Count the queries before and after with `echo=True`.
5. Write a test that fails if listing employees sends more than 2 queries, using the same `before_cursor_execute` counter. That's how teams stop N+1 from coming back.
