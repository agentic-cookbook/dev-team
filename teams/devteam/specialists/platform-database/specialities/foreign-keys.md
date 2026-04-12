---
name: foreign-keys
description: Evaluates foreign key enforcement—PRAGMA foreign_keys configuration, ON DELETE/UPDATE actions, deferred constraints, and referential integrity.
artifact: guidelines/database-design/foreign-keys.md
version: 1.0.0
---

## Worker Focus
Validates that PRAGMA foreign_keys is enabled, reviews ON DELETE/UPDATE action selection (CASCADE, SET NULL, RESTRICT, NO ACTION), ensures every FK column is indexed, assesses deferred constraint necessity for batch operations, and confirms referential integrity strategy.

## Verify
- `PRAGMA foreign_keys = ON` mandatory in all connection setup code (test harness, application bootstrap)
- Every foreign key column has a B-tree index (to prevent table-scan when cascading deletes/updates)
- ON DELETE action explicitly chosen and documented (CASCADE for composition, RESTRICT for integrity, SET NULL for optional refs)
- ON UPDATE action explicitly chosen and documented
- Deferred constraints (DEFERRABLE INITIALLY DEFERRED) used only where batch insert order requires temporal FK violations
- No FK constraints declared without corresponding index on the FK column
- Bidirectional references avoided; one direction always defined, back-references via query
- Cross-table constraints use correct syntax: `REFERENCES table(column)` with explicit column name
