"""Concurrency tests for the approval flow, against a real Postgres.

Why a real database and not a mock: the bugs live in Postgres's locking behaviour.
A mock has no locks, so it would happily pass the naive version too.
"""

import asyncio

import asyncpg

from race_lab import DSN, approve_fixed, clicks, count_orders, free_pallets, reset


def run_with_pool(scenario):
    """Open a pool, run one async scenario, close the pool."""

    async def main():
        pool = await asyncpg.create_pool(DSN, min_size=5, max_size=60)
        try:
            await scenario(pool)
        finally:
            await pool.close()

    asyncio.run(main())


def test_50_concurrent_approvals_execute_exactly_once():
    async def scenario(pool):
        # Arrange: one pending proposal P1 (8 pallets), warehouse with 10 free
        await reset(pool)
        # Act: 50 approvals start at the same instant
        results = await clicks(50, approve_fixed, pool, "P1")
        # Assert: exactly one winner, everyone else told "already handled"
        assert results.count("executed") == 1
        assert results.count("409") == 49
        assert await count_orders(pool) == 1
        assert await free_pallets(pool) == 2

    run_with_pool(scenario)


def test_competing_proposals_never_overbook_the_warehouse():
    async def scenario(pool):
        await reset(pool)  # P1 needs 8, P2 needs 5, only 10 free: both can't fit
        results = await asyncio.gather(approve_fixed(pool, "P1"), approve_fixed(pool, "P2"))
        # Which one wins varies between runs, so assert the INVARIANT, not the winner
        assert results.count("executed") == 1
        assert sum(r.startswith("stale") for r in results) == 1
        assert await free_pallets(pool) >= 0

    run_with_pool(scenario)


def test_approval_of_outdated_plan_is_rejected_as_stale():
    async def scenario(pool):
        await reset(pool)  # drafted while T7 was at km 120, exit at km 140
        await pool.execute("UPDATE trucks SET progress_m = 145000 WHERE id = 'T7'")
        result = await approve_fixed(pool, "P1")
        assert result.startswith("stale")
        assert "passed the exit" in result
        assert await count_orders(pool) == 0  # nothing was executed

    run_with_pool(scenario)
