# Race lab

Watch three approval bugs happen against a real Postgres, then watch the fixes hold.
Companion to [ADR 0010](../../docs/decisions/0010-durable-runs-proposals-exactly-once.md).

## Run (Windows, PowerShell)

Requirements: Docker Desktop running, and Python 3.11+ (the lab uses `asyncio.Barrier`).

**Step 0: open PowerShell in this folder**
```powershell
cd labs\race-lab
```

**Step 1: start Postgres** (the container is named `corridor-race-lab` and listens on port 5433)
```powershell
# first time only: create the container
docker run -d --name corridor-race-lab -e POSTGRES_USER=lab -e POSTGRES_PASSWORD=lab -e POSTGRES_DB=lab -p 5433:5432 postgres:17-alpine

# every later time (after a reboot or Docker restart): start it again
docker start corridor-race-lab
```
Check it's running: `docker ps` should show `corridor-race-lab` with status `Up`.

**Step 2: create the virtual environment and install the dependency** (first time only)
```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

**Step 3: run the lab**
```powershell
.venv\Scripts\python.exe race_lab.py
```
Calling `.venv\Scripts\python.exe` directly means you don't need to activate the venv, and it avoids PowerShell's script-execution-policy error with `Activate.ps1`.

**Step 4: run the tests**
```powershell
.venv\Scripts\python.exe -m pytest -v
```
Expected: `3 passed`. If you installed the requirements before pytest was added, rerun step 2's `pip install` line first.

**Cleanup** (when you're done with the lab)
```powershell
docker rm -f corridor-race-lab
```

**Troubleshooting**
- `ConnectionRefusedError` → Postgres isn't up yet. Run `docker ps`, wait a few seconds after starting it, and retry.
- `port is already allocated` → something else uses 5433. Change `-p 5433:5432` to e.g. `-p 5434:5432`, and run with `$env:DSN="postgresql://lab:lab@localhost:5434/lab"; .venv\Scripts\python.exe race_lab.py`.
- `AttributeError: module 'asyncio' has no attribute 'Barrier'` → your Python is older than 3.11. Check it with `python --version`.

## Expected output

```
=== 1. DOUBLE-APPROVE: 50 simultaneous clicks on proposal P1 ===
  naive: responses={'executed': 50}  transfer_orders=50  free_pallets=-390   -> BUG
  fixed: responses={'409': 49, 'executed': 1}  transfer_orders=1  free_pallets=2   -> OK, exactly once

=== 2. CAPACITY RACE: P1 (8 pallets) and P2 (5 pallets), WH-PHL has 10 free ===
  naive (with capacity check!): {'P1': 'executed', 'P2': 'executed'}  free_pallets=-3   -> BUG: overbooked
  fixed: {'P1': 'stale: WH-PHL has 5 free, needs 8', 'P2': 'executed'}  free_pallets=5   -> OK

=== 3. TOCTOU: drafted at km 120, simulator moves T7 to km 145, then you approve ===
  naive: executed   -> BUG: rerouted a truck that already passed the exit
  fixed: stale: T7 already passed the exit   -> OK

=== 4. SIMULATOR vs APPROVAL: the sim tries to move T7 while the approval is working ===
  without lock:
    0.11s  simulator: moving T7 25 km forward...
    0.12s  simulator: T7 moved                      <- moved while the approval was still working
    0.52s  approval: committed (executed)
  with lock:
    0.10s  simulator: moving T7 25 km forward...
    0.51s  approval: committed (executed)
    0.52s  simulator: T7 moved                      <- had to wait until the approval committed
```

In experiment 2, which proposal wins varies between runs. The invariant (never overbooked) does not.

## What to notice

1. **The naive version uses a transaction, and it's still broken.** A transaction gives atomicity (all or nothing), not mutual exclusion. In READ COMMITTED, a plain `SELECT` takes no lock, so all 50 requests read `pending`.
2. **In experiment 2 the naive code *does* check capacity, and it's still overbooked.** Both requests read "10 free" before either one writes. A check that isn't protected by a lock is just a guess.
3. **Experiment 3 has no concurrency at all,** one request and one click. Exactly-once can't save you here. Only re-checking preconditions at the moment of use can.

## Exercises (do them; this is where it sticks)

1. In `approve_fixed`, remove `FOR UPDATE` from the warehouse `SELECT`. Rerun. Which experiment breaks, and why does experiment 1 still pass?
res: the capacity race was broken it show an overbooked BUG also the expirement 1 still pass cause it is beffore the remove and python handle the code line by line

2. Set `WORK = 0`. Does the naive version become correct? (Run it several times.) What does that tell you about bugs that "never happen on my machine"?
res: it shows bug in the 3 i tried it 2 times or more and same things happens i don t get why this test and it do
3. In `approve_naive`, use `c.transaction(isolation="serializable")`. What error do the losers get now? How would your API have to handle it? (Hint: retries.)
res : it says that asyncpg.exceptions.SerializationError: could not serialize access due to concurrent update also i don t get it why this or it will do and for what so also tell me
4. Add a fourth experiment: the simulator ticks T7 forward *while* `approve_fixed` is between steps 2 and 4. Show that the simulator's `UPDATE` waits for the approval to commit.
res:  i don t understand so tell me
5. Turn experiment 1 into a pytest test. That's the concurrency test the real project will need.
res: i don t know how to create one so create and tell me how
