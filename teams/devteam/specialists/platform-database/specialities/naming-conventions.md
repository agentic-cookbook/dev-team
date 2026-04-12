---
name: naming-conventions
description: Evaluates database naming conventions—snake_case identifiers, table naming patterns, PK/FK column semantics, and reserved word avoidance.
artifact: guidelines/database-design/naming-conventions.md
version: 1.0.0
---

## Worker Focus
Validates that all database identifiers follow snake_case conventions, tables use appropriate singular/plural patterns, primary and foreign key columns follow semantic naming (e.g., `table_name_id` not bare `id`), and no SQL reserved words are used as unquoted identifiers. Checks index, constraint, and trigger naming patterns.

## Verify
- All identifiers use snake_case exclusively (no camelCase, PascalCase, or mixed case)
- No bare `id` columns; all primary keys follow pattern `<table>_id` or semantic name
- Foreign key columns named as `<referenced_table>_id` for clarity
- No SQL reserved words used as unquoted identifiers
- Indexes follow `ix_<table>_<columns>` convention
- Unique constraints follow `uq_<table>_<columns>` convention
- Check constraints follow `ck_<table>_<constraint_name>` convention
- Foreign key constraints follow `fk_<table>_<referenced_table>` convention
- Triggers follow `trg_<table>_<action>_<timing>` convention (e.g., `trg_users_update_before`)
