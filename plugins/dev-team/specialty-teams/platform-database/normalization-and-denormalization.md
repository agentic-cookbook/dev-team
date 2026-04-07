---
name: normalization-and-denormalization
description: Evaluates schema normalization (3NF baseline), selective denormalization with measured justification, and sync impact.
artifact: guidelines/database-design/normalization-and-denormalization.md
version: 1.0.0
---

## Worker Focus
Ensures schema starts at 3NF (no transitive dependencies, no update anomalies), allows selective denormalization only for measured hotspots, documents SQLite-specific embedded tradeoff (zero network latency), and assesses denormalization interaction with table sync.

## Verify
- Schema design starts from 3NF baseline; normalization violations documented if intentional
- Any denormalized data justified by measured query performance bottleneck (benchmark provided, not assumed)
- Denormalization maintenance strategy documented: triggers for automatic sync, or explicit application logic for batch updates
- Denormalized data never used for primary filtering (query logic doesn't depend on correctness of denormalized values)
- If column is denormalized, single source of truth identified (original table where it can be reconstructed)
- For synced tables: denormalization strategy compatible with sync direction and frequency
- Triggers used to maintain denormalized data are wrapped in transaction and tested
- No "just in case" denormalization; measure the query before denormalizing
