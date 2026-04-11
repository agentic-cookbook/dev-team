---
name: cross-database-compatibility
description: Ensures every schema decision works on both SQLite and PostgreSQL, catching type incompatibilities, PK strategy conflicts, and representation mismatches
type: consulting
source:
  - docs/research/database/sync-sqlite.md
  - docs/research/database/schema-design.md
  - docs/research/database/decision-frameworks.md
version: 1.0.0
---

## Consulting Focus

Ensures every schema decision works on both SQLite and PostgreSQL. Catches type incompatibilities, PK strategy conflicts, constraint gaps, and representation mismatches between local and server databases. Reviews data type mappings, boolean/date/UUID/JSON representations, and constraint support across both engines.

## Verify

VERIFIED findings must identify specific SQLite↔PostgreSQL incompatibilities with concrete type mappings or constraint references. NOT-APPLICABLE must demonstrate the output was reviewed and explain why no cross-database concerns exist (e.g., "output covers single-database backup operations with no cross-database implications").
