---
name: indexing
description: Evaluates B-tree fundamentals, partial/expression/composite indexes, covering indexes, EXPLAIN QUERY PLAN, and sync metadata index strategy.
artifact: guidelines/database-design/indexing.md
version: 1.0.0
---

## Worker Focus
Evaluates index design choices including B-tree fundamentals, partial indexes for filtered queries, expression indexes for computed columns, composite index column ordering (equality-first), and covering indexes. Analyzes EXPLAIN QUERY PLAN output to verify index usage and identifies when indexes should NOT be created (low-selectivity columns, small tables). Ensures sync metadata columns (isDirty, sync_version) are properly indexed.

## Verify
- Composite indexes ordered with equality columns first, range/inequality columns second
- Partial indexes used for filtered queries (e.g., WHERE deleted = 0)
- No indexes on low-selectivity columns (booleans, status fields with few values) or tables under 10K rows
- Sync metadata columns (isDirty, sync_version) indexed for hot-path queries
- EXPLAIN QUERY PLAN shows index usage for all hot-path queries; no full table scans on large tables
- Covering indexes reduce disk seeks for queries selecting multiple columns
