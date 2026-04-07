---
name: access-pattern-analysis
description: Evaluates query patterns, read/write tradeoffs, index coverage, and batch sizing for sync operations.
artifact: guidelines/database-design/access-pattern-analysis.md
version: 1.0.0
---

## Worker Focus
Analyzes query patterns and maps them against schema design. Identifies hot-path queries and verifies index coverage for WHERE/JOIN/ORDER BY columns. Evaluates read-heavy vs write-heavy design tradeoffs. Specifies appropriate batch sizes for sync operations (pull, push, conflict resolution). Documents access patterns to inform normalization and denormalization decisions.

## Verify
- All hot-path queries identified and mapped to available indexes
- Every WHERE, JOIN, and ORDER BY column has index coverage or explicitly chosen denormalization justifies lack of index
- Read/write ratio documented; schema normalized for high-write or denormalized for high-read as appropriate
- Batch sizes specified for sync operations (e.g., pull 1000 rows per batch, push 500 rows per transaction)
- Access patterns documented in code comments or design documentation for future maintainers
