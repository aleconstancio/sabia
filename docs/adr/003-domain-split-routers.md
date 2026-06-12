# ADR 003: Domain-Split Routers

**Date:** 2026-06-12
**Status:** Accepted

## Context

The original `router.py` was 713 lines with 25+ endpoints across multiple domains (images, processing, geocoding, overlays, downloads, PDF export). This made the file difficult to navigate and maintain.

## Decision

Split `router.py` into domain-specific router modules:
- `images.py` - Image catalog queries
- `processing.py` - Processing orchestration
- `downloads.py` - File serving
- `geocoding.py` - Geocoding proxy
- `reports.py` - PDF generation

## Consequences

### Positive
- Each module is independently maintainable
- Easier to understand and navigate
- Follows existing pattern (analyses.py, profiles.py)
- Reduces merge conflicts

### Negative
- Requires updating imports in main router
- Slightly more files to navigate
