---
name: sync-engine-design
description: Sync orchestrator layers, Syncable interface, sync cycle steps, scheduling, snapshot rebuilding, error handling with circuit breakers
artifact: guidelines/database-design/sync-engine-design.md
version: 1.0.0
---

## Worker Focus
The worker evaluates sync engine architecture: layered design (app → orchestrator → handlers → transport → local DB), entity-agnostic Syncable interface, explicit sync cycle steps (collect → package → send → receive → apply → checkpoint), sync scheduling logic, snapshot rebuilding, and error handling with circuit breaker patterns.

## Verify
- Sync layers defined and documented (application layer, sync orchestrator, entity handlers, transport, local DB)
- Syncable interface documented with required methods (getDirtyChanges, applyRemoteChanges, getCheckpoint, etc.)
- Sync cycle steps explicit and ordered: collect changes → package → send → receive → apply → checkpoint
- Sync scheduling strategy documented (interval, exponential backoff, on-demand, connectivity-triggered)
- Snapshot rebuilding mechanism specified for consistency verification
- Error classification documented (transient vs permanent) with handling strategy per type
- Circuit breaker thresholds defined (failure count, timeout duration, reset strategy)
