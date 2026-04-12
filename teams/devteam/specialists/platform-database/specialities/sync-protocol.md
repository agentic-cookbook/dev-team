---
name: sync-protocol
description: Push/pull/bidirectional sync, incremental syncing, idempotent operations, outbox pattern, batching and pagination strategies
artifact: guidelines/database-design/sync-protocol.md
version: 1.0.0
---

## Worker Focus
The worker evaluates the sync protocol design, ensuring it specifies sync direction (push/pull/bidirectional), uses version cursors for incremental sync, implements idempotent operations (UPSERT or idempotency keys), applies outbox pattern for transactional consistency, and defines batch sync with pagination and retry strategy with exponential backoff.

## Verify
- Sync direction specified: push-only, pull-only, or bidirectional (with justification)
- Incremental sync uses version cursors or change tracking (not full sync every time)
- All operations are idempotent (UPSERT semantics or explicit idempotency keys)
- Outbox pattern implemented for transactional consistency between local apply and remote acknowledgment
- Batch sync defined with pagination strategy for large changesets
- Retry strategy with exponential backoff specified (initial delay, max retries, backoff multiplier)
