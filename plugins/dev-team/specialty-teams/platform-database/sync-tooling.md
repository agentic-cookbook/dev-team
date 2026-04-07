---
name: sync-tooling
description: Evaluating sync tools — SQLite Session Extension, cr-sqlite, Litestream, ElectricSQL, PowerSync, Turso, sqlite-sync
artifact: guidelines/database-design/sync-tooling.md
version: 1.0.0
---

## Worker Focus
The worker evaluates sync tools and frameworks against project requirements: SQLite Session Extension, cr-sqlite, Litestream, ElectricSQL, PowerSync, Turso/libSQL, sqlite-sync. Analyzes selection criteria including offline support, conflict resolution model, server requirements, maturity, and community.

## Verify
- Tool evaluation performed against explicit requirements (offline support, conflict model, server type, maturity level)
- Selection criteria documented for comparison (e.g., CRDT vs LWW, built-in conflict UI, schema migration support)
- Chosen tool justified with acknowledged tradeoffs (what it solves, what it requires, what it doesn't handle)
- Server requirements documented (PostgreSQL, custom backend, cloud-hosted, self-hosted options)
- License compatibility verified
- Migration path or escape hatch documented if tool becomes unsuitable
