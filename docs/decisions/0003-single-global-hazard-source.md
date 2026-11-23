# 0003. One global hazard source (Open-Meteo derived polygons)

- **Date:** 2026-11-16
- **Status:** Accepted

## Context
The agent needs weather hazard *areas* (polygons) to check against truck routes. Official alert APIs with polygons exist only in some regions (NWS for the US, MeteoAlarm for Europe), and none is free for Tunisia.

## Decision
Use a single global source: fetch the Open-Meteo forecast grid for the operating area, apply thresholds (for example gusts above 70 km/h or rain above 20 mm/h), and merge the cells that pass into hazard polygons with Shapely. Routing uses the public OpenRouteService or OSRM API.

## Alternatives considered
- **One adapter per region plus a resolver plus cross-border merging** — rejected as speculative complexity. One global source covers every preset world, and the border problem disappears.
- **Self-hosted OSRM** — postponed until public rate limits actually hurt.

## Consequences
- Works the same in every region, and cross-border routes need no special case.
- Derived polygons are our own estimate, not official warnings. Add an official-alert adapter only if a real need appears.
