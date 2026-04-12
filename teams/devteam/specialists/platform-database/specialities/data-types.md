---
name: data-types
description: Evaluates SQLite type affinity, STRICT tables, cross-database type mapping, and proper use of TEXT vs NUMERIC for portable schemas.
artifact: guidelines/database-design/data-types.md
version: 1.0.0
---

## Worker Focus
Validates SQLite type affinity and the 5-rule algorithm, ensures STRICT mode is considered for type safety, confirms TEXT is used instead of STRING (non-standard), validates NUMERIC affinity behavior for decimal precision, and checks type mapping consistency between SQLite and PostgreSQL for synced tables.

## Verify
- No `STRING` type used anywhere; all text columns use `TEXT`
- Type affinity explicitly understood for each column (INTEGER, TEXT, REAL, BLOB, NUMERIC)
- STRICT mode enabled on tables requiring strict type enforcement
- NUMERIC columns used only for decimal precision work (not boolean, not enum)
- Boolean columns use `INTEGER` or `TEXT` with CHECK constraint, never `BOOLEAN`
- Datetime columns use `TEXT` (ISO 8601) or `INTEGER` (Unix timestamp) with rationale documented
- For synced tables: cross-database type mapping documented (SQLite ↔ PostgreSQL equivalence)
- No reliance on implicit type coercion in queries
