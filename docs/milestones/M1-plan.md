# Milestone 1 — Roadmap

Goal: everything in [`M1.md`](M1.md) checked. Design: [`docs/decisions/`](../decisions/README.md) (ADRs 0001–0025).

**How this works**
- Each phase ends with something that **works and is tested** (vertical slices).
- Each phase gets its own **detailed task plan** in `docs/plans/`, written when the phase starts, against the code that exists by then. Only Phase 0's is written now.
- **Executor** (ADR 0012 + the session decision of 2026-11-23):
  - **You** = the developer writes it, the main session mentors and reviews (Tier 1)
  - **Sub+review** = a subagent implements after the developer writes the tests, then review + teach-back in the main session (Tier 2)
  - **Sub** = a subagent implements, the main session verifies (Tier 3)
- One fresh session per phase. Update `docs/STATUS.md` at the end of each session.

---

## Phase 0: Workshop setup
**Plan:** [`docs/plans/phase-0-setup.md`](../plans/phase-0-setup.md)
| Task | Executor |
|---|---|
| Repo bootstrap: git, .gitignore, LICENSE, README stub, pre-commit with secret scanning, GitHub public repo `corridor` | Sub (repo creation by you, in the browser) |
| docker-compose with PostGIS | Sub |
| Backend skeleton: uv, pyproject, ruff, pyright, pytest, Alembic with the PostGIS migration | Sub |
| **First async DB session + `/api/health`** | **You** |
| Frontend skeleton: Vite + React + TS + Tailwind, `/api` proxy, health badge | Sub |
| CI: backend (ruff, pyright, pytest on PostGIS) + frontend (lint, typecheck, build) | Sub |

**Done when:** `docker compose up` + backend + frontend show "DB ok, PostGIS 3.x" in the browser; CI is green on GitHub.

## Phase 1: PostGIS lab
| Task | Executor |
|---|---|
| `labs/postgis-lab`: points, lines, polygons; `ST_Intersects`, `ST_LineInterpolatePoint`, `ST_LineLocatePoint`; geometry vs geography distances; GiST index with and without (EXPLAIN) | Sub builds the lab, **you** do the exercises |

**Done when:** you can explain each function in `concepts.md` → Geospatial in your own words.

## Phase 2: World + simulator (S0: trucks move)
| Task | Executor |
|---|---|
| Models + migrations: companies, depots/warehouses, trucks, routes (LineString), orders, shipments | Sub+review |
| Scenario YAML loader + seeded world builder (US East Coast) | Sub+review |
| Routing adapter (ORS/OSRM) + `routes` cache | Sub+review |
| **SimClock + tick loop + advisory-lock leader** | **You** |
| SSE stream of positions + MapLibre map with moving trucks | Sub |

**Done when:** trucks move on real roads on the map; the same seed gives the same positions at the same sim time (test).

## Phase 3: Hazards
| Task | Executor |
|---|---|
| Open-Meteo adapter + record/replay files | Sub+review |
| Grid → hazard polygons (Shapely), stored in PostGIS; scenario event fires the hazard | Sub+review |
| Polygon layer on the map | Sub |

**Done when:** the recorded storm appears at its scheduled sim time; a unit test checks the thresholding on a tiny fixed grid.

## Phase 4: Agent harness core
| Task | Executor |
|---|---|
| LLM adapter (OpenAI-compatible, config-switched) + `ScriptedModel` | Sub+review |
| **Tool registry (Pydantic schemas, validation errors fed back to the model)** | **You** |
| **Harness loop + run state + `run_steps` (max steps, guardrails)** | **You** |
| **Context builder (compact thread memory)** | **You** |
| Harness tests (layer 2) with `ScriptedModel` | You write them |

**Done when:** a scripted run calls 2 tools and finishes; malformed args get corrected; max steps stops a loop; all in CI with no network.

## Phase 5: S1 (ask → map + table), first evals
| Task | Executor |
|---|---|
| Read tools: `get_hazards`, `find_affected_shipments`, `get_fleet_status`, `list_warehouses` + artifacts | Sub+review |
| Structured final answer `{message, views[]}` + validation + default views (ADR 0009) | Sub+review |
| Agent stream over SSE + chat panel + view registry (map, table) | Sub+review |
| **Eval runner (YAML cases, code graders, 3 runs, pass^3, results JSON)** | **You** |
| First 8 eval cases (EN + FR) + day-1 checks: real free-tier limits and model choice | You |

**Done when:** S1 works in the browser in EN and FR; the evals run and the numbers are in the journal.

## Phase 6: S2 + S3 (act → approve → exactly-once → stale)
| Task | Executor |
|---|---|
| `plan_reroute` (compute only) + `draft_transfer_order` (proposal, idempotency key) | Sub+review |
| Run pause/resume on proposals | You |
| **Approval: claim + locks + precondition re-check, in one transaction** | **You** |
| Race-lab tests moved into the real suite (exactly-once, capacity, stale) | You |
| Document view (transfer order card) + Approve/Reject buttons | Sub |

**Done when:** S2 and S3 work end to end; the concurrency tests are green in CI.

## Phase 7: Auth + S6 (permissions)
| Task | Executor |
|---|---|
| Users, JWT in an httpOnly cookie, CSRF header, roles, demo login, single origin | Sub+review |
| Tool permission checks + `approved_by` | Sub+review |
| Confused-deputy eval trap | You |

**Done when:** a dispatcher can't approve through the UI or through the agent; the trap passes^3.

## Phase 8: S4 + S5 (chart, Gantt), observability, reliability
| Task | Executor |
|---|---|
| `query_metrics` + chart view | Sub+review |
| Schedule artifact + Gantt view (planned vs revised) | Sub+review |
| Reliability layer: timeouts, backoff + jitter, fallback model (tests with `ScriptedModel`) | You write the tests, Sub+review implements |
| structlog + `run_id` contextvar; Run Inspector page | Sub+review |

**Done when:** S4 and S5 work; a simulated 429 is retried and visible in the Run Inspector.

## Phase 9: Injection lab, Spain world, evals to 25+
| Task | Executor |
|---|---|
| **Injection lab + walkthrough** (exfiltration, fencing, poisoned-data traps), as promised | Main session teaches, you do it |
| Safe Markdown rendering; `<untrusted_data>` fencing | Sub+review |
| Spain/Valencia world + recorded DANA weather (check the polygon visually first) | Sub+review |
| Eval set to ≥ 25 cases; model comparison; pass^3 ≥ 80%, 0 unapproved writes | You |

## Phase 10: Ship it
| Task | Executor |
|---|---|
| README: architecture diagram, eval table, latency/token numbers, limitations | Sub drafts, you rewrite in your own words |
| 2-minute demo video (S1–S6 + Run Inspector) | You |
| ADRs and journal up to date; final M1 checklist | You |
