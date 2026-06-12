# ADR 004: Dashboard-First Navigation

**Date:** 2026-06-10
**Status:** Accepted

## Context

ESG analysts need portfolio visibility — seeing all monitored regions, their health scores, and active alerts at a glance. The map page was the only entry point, making it difficult to get this overview.

## Decision

Make the Dashboard the primary landing page (`/`), with the map as a drill-down for deep analysis.

## Consequences

### Positive
- Immediate portfolio visibility
- ESG scorecard provides at-a-glance metrics
- Alert system is prominent
- Module navigation is intuitive

### Negative
- Requires redirect from `/` to `/dashboard`
- Existing users may need to update bookmarks
- Dashboard must load quickly to be useful
