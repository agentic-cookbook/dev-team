---
name: query-optimization
description: Evaluates SQLite query planner behavior, query rewriting, subquery elimination, and JSON query performance.
artifact: guidelines/database-design/query-optimization.md
version: 1.0.0
---

## Worker Focus
Evaluates SQLite query execution patterns against the query planner's behavior. Identifies slow queries through EXPLAIN QUERY PLAN analysis and rewrites them to avoid full table scans. Checks for correlated subqueries that should be eliminated with JOINs, avoids functions on indexed columns in WHERE clauses, and analyzes JSON query performance. Prefers UNION ALL over UNION when deduplication is not required. Compares CTEs vs subqueries for readability and performance.

## Verify
- No correlated subqueries where a JOIN would be more efficient
- No functions applied to indexed columns in WHERE clauses (e.g., WHERE LOWER(name) = ...)
- UNION ALL preferred over UNION unless deduplication is required
- EXPLAIN QUERY PLAN checked for all hot-path queries; no unexpected full table scans
- JSON queries use index-aware extraction functions; complex JSON traversals evaluated for denormalization
- Subqueries vs CTEs choice documented and justified
