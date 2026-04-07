---
name: conflict-resolution
description: Last-Write-Wins, server/client-wins policies, field-level merge, CRDTs, manual resolution queues for sync conflicts
artifact: guidelines/database-design/conflict-resolution.md
version: 1.0.0
---

## Worker Focus
The worker evaluates conflict resolution strategies for replicated data, ensuring the system chooses appropriate policies (Last-Write-Wins, server-wins, client-wins, CRDT, or manual) per entity type, uses reliable timestamps for LWW, implements field-level merge with base versions for three-way comparison, and maintains conflict queues for non-automatable conflicts.

## Verify
- Conflict resolution strategy chosen and documented for each entity type
- LWW implementation uses reliable timestamps (Hybrid Logical Clocks or server-assigned monotonic versions)
- Field-level merge strategy includes base version for three-way comparison when applicable
- Manual resolution queue exists for conflicts that cannot be automatically resolved
- Policy justification documented (why this strategy fits the data semantics)
