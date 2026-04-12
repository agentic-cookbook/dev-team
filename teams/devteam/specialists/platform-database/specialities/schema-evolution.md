---
name: schema-evolution
description: Evaluates migration strategies, ALTER TABLE compatibility, backwards-compatible changes, and sync-compatible schema transitions.
artifact: guidelines/database-design/schema-evolution.md
version: 1.0.0
---

## Worker Focus
Validates migration tracking via PRAGMA user_version or migration table, ensures SQLite ALTER TABLE limitations are respected, confirms changes are backwards-compatible, and assesses sync compatibility of schema migrations.

## Verify
- Migration tracking mechanism established: `PRAGMA user_version` incremented or migration table records applied migrations
- No unsupported ALTER TABLE operations used (SQLite doesn't support: DROP COLUMN, MODIFY COLUMN type, RENAME COLUMN in older versions)
- Backwards-compatible migrations: ADD COLUMN with NOT NULL requires DEFAULT, DROP COLUMN requires table recreation, RENAME uses compatibility layer
- Sync-compatible migrations are add-only: new columns have defaults, no deletions until sync strategy allows, no renames without compatibility mapping
- Migrations wrapped in transactions (`BEGIN` / `COMMIT`) with rollback strategy documented
- Column drops use `CREATE TABLE new AS SELECT * FROM old` pattern with constraint reconstruction
- Default values provided for new NOT NULL columns (schema will be readable by old code during upgrade)
- Migration scripts are idempotent: re-running migration is safe even if table already modified
- Major version changes tracked separately; deployment strategy ensures coordinated migration between client and server
