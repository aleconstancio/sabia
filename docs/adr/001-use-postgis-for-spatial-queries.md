# ADR 001: Use PostGIS for Spatial Queries

**Date:** 2026-06-10
**Status:** Accepted

## Context

The original code loaded every image from the `images` table, parsed its coordinates JSON, converted it to a Shapely polygon, and checked `contains_properly` in Python. For 1,000 images this is ~100ms. For 100,000 (CBERS-4A catalog) it's several seconds.

## Decision

Use PostGIS with `ST_Intersects` and a GiST index for spatial queries.

## Consequences

### Positive
- ~2ms response regardless of catalog size (O(log n) via R-tree index)
- Native geometry operations in the database
- Supports complex spatial predicates (intersection, containment, distance)

### Negative
- Requires PostGIS extension installed
- Slightly more complex query syntax
- Migration from Python-based filtering required
