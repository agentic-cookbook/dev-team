---
name: json-columns
description: Evaluates JSON column usage, extraction patterns, indexing strategies, and when JSON is a schema smell vs legitimate.
artifact: guidelines/database-design/json-columns.md
version: 1.0.0
---

## Worker Focus
Validates JSON column usage, ensures json_each is used for array iteration, assesses indexing strategy for frequently-queried JSON fields via generated columns, and determines whether JSON is legitimate flexibility or a sign of missing normalization.

## Verify
- JSON columns justified: not used for data that should be normalized (e.g., comma-separated lists, simple key-value pairs)
- Frequently-queried JSON fields have generated column + B-tree index (e.g., `json_extract(data, '$.status')` as indexed generated column)
- No `json_extract` in WHERE clause without corresponding indexed generated column (prevents table scan)
- Array iteration uses `json_each()` or `json_array_length()`, not application-side parsing
- JSON modification (insert/update/delete) uses `json_insert()`, `json_set()`, `json_remove()` or application layer (not string concatenation)
- JSON structure documented: schema of expected keys/values included in comment
- No application logic relies on exact JSON string representation; always extract via `json_extract()`
- JSON columns optional/nullable unless default JSON object provided; NULL vs empty `{}` distinction understood
