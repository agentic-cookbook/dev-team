---
name: testing
description: Evaluates test database strategy, migration testing, sync logic testing, and conflict resolution verification.
artifact: guidelines/database-design/testing.md
version: 1.0.0
---

## Worker Focus
Evaluates testing strategy for database code. Verifies test database selection (in-memory for speed and isolation, file-based for fidelity and debugging). Reviews test fixtures and seed data organization. Audits migration testing for both forward and backward compatibility. Validates sync logic testing including change detection, push/pull success criteria, and conflict resolution. Documents test isolation strategy.

## Verify
- Test database strategy chosen and justified: in-memory SQLite for speed, file-based for production-like behavior, or hybrid approach
- Migration tests cover forward (new schema) and backward (rollback) scenarios
- Sync tests verify change detection (dirty flags, timestamps); push/pull operations succeed with expected state
- Conflict resolution tests cover concurrent writes, last-write-wins, vector clocks, or custom resolution logic
- Test isolation documented: each test gets fresh database or transaction rollback strategy
- Seed data organized in fixtures with clear setup/teardown for data independence
