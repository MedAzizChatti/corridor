# 0019. PostGIS for spatial data and queries; Shapely to build hazard polygons

- **Date:** 2026-11-22
- **Status:** Accepted

## Context
The core questions are geometric: which routes cross a hazard polygon, and has a truck passed a diversion point. Trucks, routes and hazards live in Postgres. Precondition checks run inside the approval transaction (ADR 0010).

## Decision
- **PostGIS** (Postgres extension, `postgis/postgis` image) stores geometries and answers spatial queries in SQL (`ST_Intersects`, `ST_LineLocatePoint`, `ST_DWithin`...), using **GiST spatial indexes**. Columns are mapped in the ORM with **GeoAlchemy2**.
- **Shapely** (Python) is used only to *build* hazard polygons from the Open-Meteo grid (merge cells, simplify) before storing them.
- Coordinates are stored as **SRID 4326** (latitude/longitude). Distances in metres use `geography` casts, or a projected CRS where needed (ADR 0004: SI units).

## Alternatives considered
- **Everything in Shapely** — familiar Python, but every spatial question loads all routes into memory, with no indexes, and it can't run inside the approval's SQL transaction as one query.

## Consequences
- Spatial questions are one indexed SQL query, and they can run inside the same transaction and locks as an approval.
- New concepts to learn: geometry vs geography, SRIDs, spatial indexes. A PostGIS lab comes first.
- Spatial tests need a real PostGIS database (already true for concurrency tests).
