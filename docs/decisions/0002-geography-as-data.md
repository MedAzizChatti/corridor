# 0002. Geography is data, not code

- **Date:** 2026-11-16
- **Status:** Accepted

## Context
The world has to fit where a company's trucks actually operate. A distributor in Sfax and one in New Jersey should both work without code changes.

## Decision
A company is defined by configuration: its operating area (polygon or bounding box), depots, fleet, timezone and display units. The simulator and every external lookup are driven by that configuration. Preset demo worlds: US East Coast, Tunisia (Tunis, Sousse, Sfax), and a cross-border world (for example France and Spain).

## Alternatives considered
- **Hard-code one region** — simpler at first, but every new region means code changes, and it can't show the system works anywhere.

## Consequences
- Switching worlds live in a demo shows the design.
- "Anywhere" means *any configured region*, limited by what the external providers cover. The README must say so honestly.
