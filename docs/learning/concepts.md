# Concepts glossary

Every new concept from the Corridor sessions, explained in plain words, with an example from code **you already wrote** (the PFA POS) or from Corridor.
Add to this file every time a new concept appears. If you can't explain an entry in your own words, it isn't learned yet.

---

## Concurrency and databases

**Race condition**
Two requests run at the same time, and the result depends on who goes first.
*Your POS:* two cashiers sell the last chair at the same moment, and both sales succeed.

**Check-then-act**
"Read a value, decide, then write" in separate steps. Another request can slip in between the check and the act. This is the most common race.
*Your POS:* `crud/order.py` → `if product.quantity < line["quantity"]` (check) … `bulk_update_mappings` (act).

**Lost update**
Two requests read the same value, each computes a new value, and the second write erases the first.
*Your POS:* stock is 5 and two orders of 2 each read 5. Both write `5 - 2 = 3`. Stock should be 1. The update is written as an absolute value (`product.quantity - line["quantity"]`) computed in Python.
*Fix:* let the database do the maths: `SET quantity = quantity - 2`.

**Transaction**
A group of statements that succeed or fail together (all or nothing). **A transaction is not a lock**: it doesn't stop two transactions from reading the same row at once.
*Lab:* `approve_naive` uses a transaction and still executes 50 times.

**Row lock / `SELECT … FOR UPDATE`**
"I'm going to change this row; everyone else who wants to change it must wait until I commit." Readers without `FOR UPDATE` don't wait.
*Lab:* experiment 4, where the simulator waits 0.4 s for the approval.

**Atomic conditional update (the "claim")**
Check and act in **one** SQL statement, so nothing can slip in between:
`UPDATE … SET status='used' WHERE id=:id AND status='active' RETURNING *` → 0 rows means someone else got there first.
*Your POS fix:* coupons → `WHERE code=:code AND status='Active'`. Stock → `SET quantity = quantity - :q WHERE id=:id AND quantity >= :q`.

**Exactly-once**
An action runs once even if it's requested many times (double-click, retry, two tabs).
*Lab:* experiment 1, 50 clicks → 1 transfer order.

**Idempotency**
Doing something twice has the same effect as doing it once. An idempotent API is safe to retry.

**TOCTOU (Time Of Check to Time Of Use)**
What you checked was true *then*, but isn't true *now*, when you use it. It needs no concurrency, just time passing.
*Lab:* experiment 3, where the truck passed the exit while you were deciding.

**Precondition re-check**
Store the assumptions a decision relies on, and check them again at the moment of acting.

**Optimistic vs pessimistic concurrency**
Pessimistic: lock early and hold the lock ("nobody touch this while I decide"). Optimistic: don't lock, but verify just before acting and abort if something changed. We never hold a lock while a *human* decides.

**Isolation levels (READ COMMITTED, SERIALIZABLE)**
How much a transaction is protected from others. Postgres's default is READ COMMITTED, where you only see committed data but plain reads take no locks. SERIALIZABLE means Postgres aborts transactions that would give a result impossible if they had run one after another, and you must retry them.
*Lab:* exercise 3, the `SerializationError`.

**Invariant**
A rule that must *always* be true, whatever happens. "Stock is never negative." "A coupon is used at most once." Good tests assert invariants.

---

## Agents and LLMs

**The LLM is stateless**
The model remembers nothing between calls. Its whole "memory" is the list of messages you send each time. That's why pausing a run means saving the messages, and resuming means sending them again.

**Tool calling**
The model answers "call function X with arguments Y" instead of text. Your code runs the function and sends the result back as a message.

**Agent loop / harness**
The code around the model: call model → run the requested tools → append results → repeat, until it answers or hits a limit (max steps, budget).

**Structured output**
Forcing the model's answer to match a schema (Pydantic or JSON Schema) so code can rely on it.

**Human-in-the-loop (HITL) / proposal**
The agent may only *propose* write actions. A human approves, and deterministic code executes.

**Durable run / state machine**
A run's status lives in the database (`running → awaiting_approval → …`), not in a waiting process. It survives restarts.

**Event log (append-only)**
Every step is added as a new row and never edited. You can replay or audit everything that happened.

**Reference, don't copy**
Tools store data on the backend with an ID. The model refers to IDs instead of copying data, so it can't make up data, and it uses fewer tokens.

---

## Architecture and process

**ADR (Architecture Decision Record)**
Half a page per decision: context, decision, rejected alternatives, consequences. Never edited; a newer ADR supersedes an older one.

**Ports and adapters (interfaces for external services)**
Your code depends on a small interface ("get hazards for this area"), not on a specific API. The real API and a test fake both implement it.

**Deterministic simulation / seed**
Same seed and scenario give exactly the same world, every time. Required to test agents reproducibly.

**Vertical slice**
Build one feature through *every* layer (DB → API → agent → UI) before widening. Avoids "90% of 10 features, 0 working".

---

## Evals

**Eval (evaluation)**
A test for non-deterministic AI behaviour: run the real model on a fixed case, grade the result, and repeat it to get a *rate*, not a yes or no.

**Eval case**
One input plus a known world plus expected properties (tools, IDs, view, language, write or no write). In Corridor, one YAML file.

**Grader**
The code that decides pass or fail for one expectation. Code graders (set equality, "was tool X called?") are exact and free. Prefer them.

**LLM-as-judge**
Another LLM grades the answer. Use it only for things code can't check (clarity, tone), and only after checking it against human grades.

**Trajectory / trace**
The full sequence of steps in a run: model call → tool call → result → … Reading traces is how you find *why* a case failed.

**pass@k vs pass^k**
pass@k: passed at least once in k tries (fine for "can it ever do it?"). pass^k: passed **all** k tries (what you need for reliability, and for write actions).

**Regression**
Something that used to pass now fails, after a prompt, model or code change. Evals exist mainly to catch these.

---

## Security

**Confused deputy**
A program with more power than the person using it gets tricked into using that power for them. With agents: a dispatcher asks the agent "approve this", and the agent's tools have full database rights. *Fix:* every tool checks the **user's** role in code. The prompt is never a security boundary.
*Your POS:* `get_curr_employee` with `allowed_roles` is the same idea, applied to routes instead of agent tools.

**Authentication vs authorization**
Authentication = *who are you?* (login, JWT). Authorization = *what are you allowed to do?* (roles, permission checks).

---

## Async and ORM loading

**async / await, the event loop**
One thread runs many requests. At every `await` (waiting on the network or DB), Python pauses that request and runs another one. Great when the backend mostly *waits* (LLMs, APIs, DB).
*Race lab:* why `WORK = 0` still gave 50 duplicates: Python switched requests at every `await`.

**Blocking the event loop**
A sync call inside async code (`time.sleep`, `requests.get`, a sync DB driver, heavy CPU work) stops the *one* thread, and every user freezes. Use `await asyncio.sleep`, `httpx.AsyncClient`, and `asyncio.to_thread` for CPU work.

**Lazy loading vs eager loading**
Lazy: the ORM fetches a relationship the first time you touch it, with a hidden query. Eager: you say up front what to load (`selectinload`, `joinedload`).

**N+1 query problem**
1 query for a list, then 1 more query **per row** for its related data. 100 rows = 101 queries.
*Your POS:* `routers/employee.py:58` → `employee.roles` inside the list comprehension.
*Lab:* `labs/n-plus-one-lab`: 101 queries → 2 with `selectinload`.

**MissingGreenlet**
The error async SQLAlchemy raises when code triggers a lazy load. It looks annoying, but it's a guard against hidden queries.

**selectinload vs joinedload**
`selectinload`: 2 queries, the second with `WHERE id IN (...)`. Default for one-to-many. `joinedload`: 1 query with a JOIN. Good for many-to-one, and needs `.unique()` for collections.

---

## Real-time and web security

**SSE (Server-Sent Events)**
A normal HTTP response that never ends: the server keeps writing `event:` / `data:` / `id:` text blocks into it. One direction only (server → browser). The browser's built-in client is `EventSource`.

**Last-Event-ID**
When an SSE connection drops, the browser reconnects automatically and tells the server the last `id` it received. The server replays what was missed. In Corridor that's a query on the append-only `run_steps` table.

**WebSocket vs SSE vs polling**
WebSocket: a permanent two-way pipe. More power, more code. SSE: server → browser, plain HTTP, reconnects by itself. Polling: "anything new?" every N seconds. Simple, laggy, wasteful.

**`EventSource` can't send headers**
So a JWT in an `Authorization` header can't go along with it. Fixes: a cookie (sent automatically) or fetch-based SSE. **Never** put a token in the URL.

**Token in URL (anti-pattern)**
`?token=...` ends up in server logs, browser history, proxies and the `Referer` header, so anyone who reads them can log in as that user.

**XSS (Cross-Site Scripting)**
An attacker gets their JavaScript to run on your page (for example through unescaped user input). That script can read `localStorage`, so a token stored there can be stolen. *Your POS* stores the JWT in `localStorage`.

**httpOnly cookie**
A cookie that JavaScript can't read. The browser still sends it automatically. An XSS bug can no longer steal the token.

**CSRF (Cross-Site Request Forgery)**
Because cookies are sent automatically, an evil site can make the user's browser send a request to your API *with the user's cookie*. Defences: `SameSite` cookies, plus requiring a custom header (browsers won't add one cross-site without permission).

**SameSite (Strict / Lax / None)**
A cookie flag that controls whether the cookie is sent on requests coming from other sites. `Lax` blocks it on cross-site POSTs, which covers most CSRF.

**Same-origin policy and CORS**
Origin = scheme + host + port. Browsers isolate origins from each other. CORS is how a server *allows* another origin in. If frontend and API share one origin, CORS isn't needed at all.

---

## Dependencies and repositories

**Direct vs transitive dependency**
Direct: what you asked for (`fastapi`). Transitive: what *your* dependencies need (`starlette`, `pydantic`, `anyio`...). Most of the code you run comes from packages you never chose.

**Version ranges (semver)**
`fastapi>=0.115,<1` or `^16.2.0` means "any compatible version". Flexible, but two installs on different days can get different versions.

**Lockfile**
A generated file listing the *exact* version (and hash) of **every** package, direct and transitive, after resolution. Same lockfile = same install everywhere. Examples: `uv.lock`, `package-lock.json` (your POS frontend has one).
*Two files, two jobs:* `pyproject.toml` / `package.json` = what you want; the lockfile = exactly what you got.

**pip freeze is not a real lockfile**
Your POS `requirements.txt` pins everything (good), but mixes direct and indirect packages (you can't tell what you actually use), captures Windows-only packages like `colorama`, has no hashes, and lists both `psycopg2` and `psycopg2-binary`.

**Hashes / supply-chain attack**
An attacker publishes a malicious version of a real package, or a look-alike name. A lockfile with hashes refuses any file whose content doesn't match what you locked.

**Monorepo**
Several parts of a system (frontend, backend) in one repository. One PR can change both sides at once. Split repos only for separate teams or release cycles.

**Secret scanning / key rotation**
Bots scan public GitHub for API keys within minutes. If a key is ever pushed, deleting the commit isn't enough: revoke it and generate a new one (rotate).

**License**
Public code with no license is legally "all rights reserved": others can read it but not reuse it. MIT = "do what you want, keep the notice".

---

## Geospatial

**PostGIS**
A Postgres extension that adds geometry types (points, lines, polygons) and spatial functions in SQL. The industry standard for geo-backends.

**Spatial query (`ST_Intersects` and friends)**
SQL functions on shapes: `ST_Intersects(route, storm)` (do they touch?), `ST_DWithin(a, b, 5000)` (within 5 km?), `ST_LineLocatePoint(route, truck)` (how far along the route is the truck, 0 → 1).

**Spatial index (GiST)**
Like a normal index, but for shapes. It stores each shape's bounding box, so the database can skip every route that's nowhere near the storm without doing the exact maths on it.

**SRID / CRS**
The coordinate system a geometry uses. **4326** = GPS latitude/longitude (WGS 84). Mixing SRIDs gives wrong answers silently.

**geometry vs geography**
`geometry` does flat-plane maths (fast, but in degrees for 4326, so "distance 0.1" means nothing useful). `geography` does maths on the curved Earth and returns metres. Use geography (or a projected CRS) for real distances.

**Shapely**
A Python library for geometry operations in memory. In Corridor it only *builds* hazard polygons from the weather grid. Querying happens in PostGIS.

---

## Simulation

**Simulated clock (injected clock)**
Code never asks the real time (`datetime.now()`). It asks a clock object it was given. The simulator controls that clock (speed, pause), and tests can freeze it. Same idea as injecting a DB session.

**Fixed time step vs event-driven simulation**
Fixed step: every tick advances time by the same amount and updates everything (good for continuous movement). Event-driven: jump straight to the next scheduled event (good for sparse events like queues).

**Determinism / pure function of inputs**
Same seed + same scenario + same time = exactly the same world. That's what makes replays, tests and evals possible.

**Seeded random number generator**
"Random" numbers that are the same sequence every run for the same seed. Realistic variation, fully reproducible.

**Caching external calls**
Store an external API's answer and reuse it. It protects you from rate limits, makes runs work offline, and gives deterministic results.

**Advisory lock / leader election**
`pg_try_advisory_lock(42)`: a named lock Postgres gives to exactly one session. Used to elect a single "leader" (here, the one worker that runs the simulator). If the leader crashes, the lock frees up and another worker can take over.

---

## Context engineering

**Context window**
Everything the model sees in one call: system prompt, tool schemas, history, current messages. It has a maximum size, and every token costs latency and rate limit.

**Context engineering**
Deciding *what* goes into the context on each call, and what stays out. Often matters more than prompt wording.

**Token budget**
A planned breakdown of how many tokens each part of the context may use (system ~800, tools ~1,500, memory ≤ 1,500...). It keeps calls predictable and inside free-tier limits.

**Thread vs run**
A thread is the whole conversation. A run is one agent execution for one user message. A thread contains many runs.

**Compact memory**
Instead of replaying full histories, keep only user messages, final answers and references to artifacts. The model can resolve "them" → `a_17` without seeing old raw data.

**Stale context**
Old tool results left in the context describe a world that has moved on. The model may treat them as current. TOCTOU, inside the prompt. *Fix:* tools always read the current state.

**Truncation vs summarization**
Truncation: drop the oldest turns (deterministic, free, testable). Summarization: ask an LLM to compress them (costs a call, can lose or invent details). Start with truncation.

---

## Reliability

**Temporary vs permanent errors**
Temporary (429, 500, 503, timeout): the same request may succeed later, so retry. Permanent (400 bad request, 401 bad key): it will fail identically forever, so don't retry; fix it.

**Timeout**
A maximum wait. Without one, a single stuck call can hang a run (or a server thread) forever.

**Exponential backoff**
Wait 1 s, then 2, 4, 8... between retries. It gives an overloaded service time to recover instead of hammering it.

**Jitter**
A small random extra delay added to each retry, so many clients that failed together don't all retry at the same instant.

**Thundering herd**
Many clients hitting a service at the same moment (for example all retrying after the same error), causing it to fail again. Jitter prevents it.

**Retry-After**
A header where the server says how long to wait. Obey it when present.

**Self-correction (error feedback to the model)**
Send the exact validation error back to the model as the tool result; models usually fix their call on the next step.

**Fallback model**
A second model used when the primary keeps failing. Always record which model produced each step.

**Idempotency key**
A unique key per logical action (here `(run_id, tool_call_id)`), enforced by a unique constraint. `INSERT ... ON CONFLICT DO NOTHING` makes a replay of the same action a no-op.

**Crash recovery**
Persist each step before moving on. After a crash, resume from the last saved step. That's only safe if repeated steps are idempotent.

---

## Observability

**Observability**
Being able to understand what a system did, and why, from the data it leaves behind, without adding print statements after the fact.

**Traces, logs, metrics**
Trace: the step-by-step story of one request or run. Log: one event ("retrying after 429"). Metric: a number over time (median latency, tokens per day).

**Span**
One timed step inside a trace (a model call, a tool call). A trace is a tree or sequence of spans. In Corridor, one `run_steps` row ≈ one span.

**Structured logging**
Log lines as JSON key-value pairs instead of free text, so they can be filtered and queried (`run_id = r_812 AND level = warning`).

**Correlation ID**
An ID (here `run_id`) attached to every log line belonging to the same run or request, so you can follow one story across the whole codebase.

**contextvar**
Python's way to store a value "for the current async task", like `run_id`, without passing it through every function. Each concurrent run sees its own value.

---

## AI security (prompt injection)

**Prompt injection**
Text that makes the model follow instructions it shouldn't. It works because instructions and data share one channel (text). There is no complete fix. *(Full walkthrough and lab when we implement it.)*

**Direct vs indirect injection**
Direct: the user types the malicious instruction. Indirect: the instruction hides inside *data* the agent reads later (an order note, an email, a web page), so the attacker never talks to the agent.

**Blast radius**
How much damage is possible if something is compromised. Strategy: assume the model is hijacked, and make sure it *can't* do harm (proposals plus approval, permissions in code).

**Data exfiltration via rendered output**
A hijacked model writes a Markdown image whose URL contains secret data. When the chat renders it, the browser sends that data to the attacker's server. *Fix:* no remote images and no raw HTML in rendered model output.

**Fencing untrusted data (spotlighting)**
Wrapping external text in clear markers (`<untrusted_data>...</untrusted_data>`) and telling the model it's data. It lowers the success rate but is not a guarantee.

**Git hook / pre-commit**
A script Git runs at a fixed moment, e.g. just before a commit is created. If it exits non-zero, the commit is refused. The `pre-commit` tool manages these scripts from `.pre-commit-config.yaml`. Corridor uses it to run gitleaks, so a staged `sk-proj-...` key blocks the commit *before* it reaches history. The hook is installed per clone and points at one Python, so install it on the side (Windows or WSL) you commit from.

**Secret scanning vs rotation**
Scanning (gitleaks locally, GitHub push protection remotely) stops a key from being published. Once a key is public, deleting the commit is not enough: bots scrape GitHub within minutes, so the key must be **revoked and replaced** (ADR 0018).

**Line endings (CRLF vs LF) and `.gitattributes`**
Windows ends lines with `\r\n`, Linux/macOS with `\n`. Without a rule, the same file flips between the two depending on who saved it, and every line shows as changed in diffs. `* text=auto eol=lf` in `.gitattributes` makes Git store and check out LF everywhere.
