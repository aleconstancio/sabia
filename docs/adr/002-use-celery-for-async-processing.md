# ADR 002: Use Celery for Async Processing

**Date:** 2026-06-10
**Status:** Accepted

## Context

Downloading 4 spectral bands at ~200MB each takes 30-120 seconds. In the old code, Flask's single thread was blocked for the entire duration, meaning one user could block all others.

## Decision

Use Celery workers with Redis broker for async task processing.

## Consequences

### Positive
- HTTP endpoint returns task ID immediately
- Frontend polls for progress (or WebSocket)
- Multiple users can process images concurrently
- Worker pool limits resource usage
- Task result persistence for later download

### Negative
- Requires Redis as broker
- Additional complexity in task state management
- Need to handle task failures and retries
