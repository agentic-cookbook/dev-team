---
name: sync-schema-design
description: Dual schema design, UUID keys, soft deletes, dirty tracking, versioning for offline-capable databases
artifact: guidelines/database-design/sync-schema-design.md
version: 1.0.0
---

## Worker Focus
The worker evaluates whether the database schema supports offline-first sync by using UUID primary keys for offline creation, implementing soft deletes or tombstone patterns, tracking dirty records, versioning synced tables for optimistic concurrency, and maintaining sync metadata tables.

## Verify
- UUID PKs on all synced tables (not auto-incremented server IDs)
- Soft delete strategy chosen and documented (flag column vs tombstone table)
- Dirty tracking mechanism specified (dirty flag, change log, or operation queue)
- Version column present on all synced tables for optimistic concurrency
- Sync metadata tables defined (last_synced_at per table, change cursors, device state)
