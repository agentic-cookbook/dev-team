---
name: constraints-and-validation
description: Evaluates CHECK constraints, boolean/enum enforcement patterns, and NULL truthiness in constraint expressions.
artifact: guidelines/database-design/constraints-and-validation.md
version: 1.0.0
---

## Worker Focus
Validates CHECK constraint syntax and evaluation semantics, ensures boolean columns use `INTEGER CHECK(col IN (0,1))` pattern, enforces enum-like constraints via `CHECK(col IN (...))` with documented values, and confirms NULL truthiness is never relied upon in constraint logic.

## Verify
- Boolean columns use `INTEGER` type with `CHECK(col IN (0,1))` constraint
- Enum-like columns use `TEXT` or `INTEGER` with `CHECK(col IN (...))` constraint
- All CHECK constraints have documented enumeration of allowed values (in comment or constraint name)
- No CHECK expressions that evaluate NULL as truthy (NULL in any constraint expression prevents row from failing check)
- Range constraints (e.g., `CHECK(age >= 0 AND age <= 150)`) explicitly bounded
- Pattern validation via `CHECK(col LIKE pattern)` only for simple patterns; regex deferred to application layer
- CHECK constraints exclude domain validation that might be partially applied (validate in application or use NOT NULL + other constraints)
- No negation logic that silently accepts NULL: `CHECK(status != 'deleted')` will accept NULL (use explicit whitelist instead)
