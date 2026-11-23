"""Race lab: see the approval bugs happen, then see the fixes hold.

Three experiments, each run NAIVE then FIXED against a real Postgres:
  1. Double-approve   — 50 concurrent clicks on the same proposal (exactly-once)
  2. Capacity race    — two different proposals fight over the same warehouse spots
  3. TOCTOU           — the world moves between "draft" and "approve"

Run:  python race_lab.py   (see README.md for the Postgres container)
"""

import asyncio
import os
import time

import asyncpg

DSN = os.getenv("DSN", "postgresql://lab:lab@localhost:5433/lab")
WORK = 0.02  # seconds of "work" while executing (calling routing API, writing docs...).
# Real work also takes time; the sleep just makes the race window reproducible.

SCHEMA = """
DROP TABLE IF EXISTS transfer_orders, proposals, trucks, warehouses;
CREATE TABLE warehouses (id text PRIMARY KEY, free_pallets int NOT NULL);
CREATE TABLE trucks (id text PRIMARY KEY, status text NOT NULL, progress_m int NOT NULL);
CREATE TABLE proposals (
    id text PRIMARY KEY,
    status text NOT NULL,              -- pending | approved | executed | stale
    truck_id text NOT NULL,
    warehouse_id text NOT NULL,
    pallets int NOT NULL,
    max_progress_m int NOT NULL        -- precondition: truck must not be past the exit
);
CREATE TABLE transfer_orders (id serial PRIMARY KEY, proposal_id text NOT NULL);
"""


async def reset(pool, *, free_pallets=10, t7_progress=120_000):
    async with pool.acquire() as c:
        await c.execute(SCHEMA)
        await c.execute("INSERT INTO warehouses VALUES ('WH-PHL', $1)", free_pallets)
        await c.execute("INSERT INTO trucks VALUES ('T7','in_transit',$1), ('T9','in_transit',100000)",
                        t7_progress)
        await c.execute("""INSERT INTO proposals VALUES
            ('P1','pending','T7','WH-PHL',8,140000),
            ('P2','pending','T9','WH-PHL',5,140000)""")


async def count_orders(pool):
    return await pool.fetchval("SELECT count(*) FROM transfer_orders")


async def free_pallets(pool):
    return await pool.fetchval("SELECT free_pallets FROM warehouses WHERE id='WH-PHL'")


async def clicks(n, fn, *args):
    """Fire n requests that all start at the same instant."""
    barrier = asyncio.Barrier(n)

    async def one():
        await barrier.wait()
        return await fn(*args)

    return await asyncio.gather(*(one() for _ in range(n)))


# ---------------------------------------------------------------- approve: NAIVE
async def approve_naive(pool, pid, check_preconditions=False):
    async with pool.acquire() as c, c.transaction():  # yes, a transaction. Still broken.
        p = await c.fetchrow("SELECT * FROM proposals WHERE id=$1", pid)
        if p["status"] != "pending":                                      # ① CHECK
            return "409"
        wh = await c.fetchrow("SELECT * FROM warehouses WHERE id=$1", p["warehouse_id"])
        if check_preconditions and wh["free_pallets"] < p["pallets"]:
            return "stale"
        await asyncio.sleep(WORK)                                         # ...the gap...
        await c.execute("INSERT INTO transfer_orders (proposal_id) VALUES ($1)", pid)  # ② ACT
        await c.execute("UPDATE warehouses SET free_pallets = free_pallets - $1 WHERE id=$2",
                        p["pallets"], p["warehouse_id"])
        await c.execute("UPDATE proposals SET status='executed' WHERE id=$1", pid)
        return "executed"


# ---------------------------------------------------------------- approve: FIXED
async def approve_fixed(pool, pid, work=WORK, lock=True):
    for_update = " FOR UPDATE" if lock else ""  # lock=False only exists for experiment 4
    async with pool.acquire() as c, c.transaction():
        # 1. CLAIM: check + claim in ONE atomic statement -> exactly-once
        p = await c.fetchrow("""UPDATE proposals SET status='approved'
                                WHERE id=$1 AND status='pending' RETURNING *""", pid)
        if p is None:
            return "409"
        # 2. LOCK the rows our decision depends on (blocks other approvers + the simulator)
        truck = await c.fetchrow("SELECT * FROM trucks WHERE id=$1" + for_update, p["truck_id"])
        wh = await c.fetchrow("SELECT * FROM warehouses WHERE id=$1" + for_update, p["warehouse_id"])
        # 3. RE-CHECK preconditions against the CURRENT world (TOCTOU)
        problems = []
        if truck["progress_m"] > p["max_progress_m"]:
            problems.append(f"{truck['id']} already passed the exit")
        if wh["free_pallets"] < p["pallets"]:
            problems.append(f"{wh['id']} has {wh['free_pallets']} free, needs {p['pallets']}")
        if problems:
            await c.execute("UPDATE proposals SET status='stale' WHERE id=$1", pid)
            return "stale: " + "; ".join(problems)
        # 4. ACT
        await asyncio.sleep(work)
        await c.execute("INSERT INTO transfer_orders (proposal_id) VALUES ($1)", pid)
        await c.execute("UPDATE warehouses SET free_pallets = free_pallets - $1 WHERE id=$2",
                        p["pallets"], p["warehouse_id"])
        await c.execute("UPDATE proposals SET status='executed' WHERE id=$1", pid)
        return "executed"


def tally(results):
    out = {}
    for r in results:
        key = r.split(":")[0]
        out[key] = out.get(key, 0) + 1
    return out


async def main():
    pool = await asyncpg.create_pool(DSN, min_size=5, max_size=60)

    print("\n=== 1. DOUBLE-APPROVE: 50 simultaneous clicks on proposal P1 ===")
    for name, fn in [("naive", approve_naive), ("fixed", approve_fixed)]:
        await reset(pool)
        results = await clicks(50, fn, pool, "P1")
        n = await count_orders(pool)
        verdict = "OK, exactly once" if n == 1 else "BUG"
        print(f"  {name}: responses={tally(results)}  transfer_orders={n}  "
              f"free_pallets={await free_pallets(pool)}   -> {verdict}")

    print("\n=== 2. CAPACITY RACE: P1 (8 pallets) and P2 (5 pallets), WH-PHL has 10 free ===")
    for name, fn in [("naive (with capacity check!)", lambda p, pid: approve_naive(p, pid, True)),
                     ("fixed", approve_fixed)]:
        await reset(pool)
        barrier = asyncio.Barrier(2)

        async def go(pid, fn=fn, barrier=barrier):
            await barrier.wait()
            return pid, await fn(pool, pid)

        results = await asyncio.gather(go("P1"), go("P2"))
        left = await free_pallets(pool)
        verdict = "BUG: overbooked" if left < 0 else "OK"
        print(f"  {name}: {dict(results)}  free_pallets={left}   -> {verdict}")

    print("\n=== 3. TOCTOU: drafted at km 120, simulator moves T7 to km 145, then you approve ===")
    for name, fn in [("naive", approve_naive), ("fixed", approve_fixed)]:
        await reset(pool)  # 14:00 - agent drafts P1 while T7 is at km 120 (exit at km 140)
        await pool.execute("UPDATE trucks SET progress_m=145000 WHERE id='T7'")  # 14:12 sim tick
        result = await fn(pool, "P1")  # 14:15 - you click Approve
        verdict = "BUG: rerouted a truck that already passed the exit" if result == "executed" else "OK"
        print(f"  {name}: {result}   -> {verdict}")

    print("\n=== 4. SIMULATOR vs APPROVAL: the sim tries to move T7 while the approval is working ===")
    for name, lock in [("without lock", False), ("with lock", True)]:
        await reset(pool)
        t0 = time.perf_counter()

        def now():
            return f"{time.perf_counter() - t0:4.2f}s"

        async def approval(lock=lock):
            result = await approve_fixed(pool, "P1", work=0.5, lock=lock)  # 0.5s of "work"
            print(f"    {now()}  approval: committed ({result})")

        async def sim_tick():
            await asyncio.sleep(0.1)  # by now the approval has checked T7 and is "working"
            print(f"    {now()}  simulator: moving T7 25 km forward...")
            await pool.execute("UPDATE trucks SET progress_m = progress_m + 25000 WHERE id='T7'")
            print(f"    {now()}  simulator: T7 moved")

        print(f"  {name}:")
        await asyncio.gather(approval(), sim_tick())

    await pool.close()
    print()


if __name__ == "__main__":
    asyncio.run(main())
