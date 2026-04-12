---
name: offline-first-architecture
description: WAL mode, operation queues, optimistic UI, rollback handling, offline migrations, cache invalidation, connectivity-aware scheduling
artifact: guidelines/database-design/offline-first-architecture.md
version: 1.0.0
---

## Worker Focus
The worker evaluates offline-first foundation: WAL mode enablement, operation queue pattern for mutations, optimistic UI updates with rollback paths, schema migrations while offline, data expiry and cache invalidation strategies, and connectivity-aware sync scheduling.

## Verify
- WAL mode enabled on local SQLite database for offline capability
- Local-first read/write with background sync to server
- Operation queue pattern implemented for mutations queued while offline
- Optimistic UI updates with rollback path when server rejects operation
- Schema migration strategy handles offline devices (deferred, conditional, or dual schema)
- Data expiry and cache invalidation strategy documented
- Connectivity detection implemented to trigger sync when connection restored
