---
name: transactions-and-concurrency
description: Evaluates WAL mode, journal modes, transaction patterns, connection strategies, busy timeouts, and production PRAGMA tuning.
artifact: guidelines/database-design/transactions-and-concurrency.md
version: 1.0.0
---

## Worker Focus
Evaluates transaction patterns and concurrency configuration for SQLite. Verifies WAL mode is enabled for concurrent access. Checks that write transactions use BEGIN IMMEDIATE to avoid serialization errors. Reviews connection pooling strategy (single writer + multiple readers). Validates busy_timeout configuration. Audits production PRAGMAs including synchronous level, cache_size, journal_size_limit, and foreign_keys enforcement.

## Verify
- WAL mode enabled (PRAGMA journal_mode = WAL)
- Write transactions use BEGIN IMMEDIATE; read transactions use BEGIN DEFERRED
- busy_timeout set to reasonable value (e.g., 5000ms) to prevent SQLITE_BUSY errors
- Production PRAGMAs configured: synchronous=NORMAL, cache_size=-64000, journal_size_limit, foreign_keys=ON
- Connection pooling implements single-writer pattern for write transactions
- Transaction isolation levels understood and documented for concurrent read scenarios
