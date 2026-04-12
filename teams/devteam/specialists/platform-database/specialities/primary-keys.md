---
name: primary-keys
description: Evaluates primary key strategy—INTEGER PRIMARY KEY semantics, AUTOINCREMENT tradeoffs, UUID approaches, and sync compatibility.
artifact: guidelines/database-design/primary-keys.md
version: 1.0.0
---

## Worker Focus
Validates primary key strategy selection, ensures INTEGER PRIMARY KEY is used correctly as rowid alias, assesses AUTOINCREMENT necessity (gap-free sequences only), evaluates UUID strategies (TEXT vs BLOB, v4 vs v7), determines WITHOUT ROWID appropriateness, and confirms cross-database PK compatibility for synced tables.

## Verify
- Primary key strategy documented and justified (INTEGER PRIMARY KEY vs UUID vs composite)
- INTEGER PRIMARY KEY correctly aliases rowid; AUTOINCREMENT only used where gap-free sequence is required
- UUID format consistent across local and server databases if table is synced
- UUID storage method chosen (TEXT base64/hex vs BLOB) with rationale
- UUID generation strategy documented (v4 for randomness, v7 for sortability, application-generated or database-generated)
- WITHOUT ROWID tables only for non-integer primary keys with clustered access patterns
- Without ROWID tables use composite PK or TEXT/BLOB PK, never INTEGER
- Cross-database PK mapping documented for synced tables (e.g., SQLite UUID ↔ PostgreSQL uuid type)
