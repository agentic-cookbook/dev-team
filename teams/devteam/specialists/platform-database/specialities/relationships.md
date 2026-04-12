---
name: relationships
description: Evaluates relationship patterns—one-to-many via FK, many-to-many join tables, polymorphic references, and hierarchical structures.
artifact: guidelines/database-design/relationships.md
version: 1.0.0
---

## Worker Focus
Validates one-to-many relationships via FK on child table, enforces many-to-many via join tables (never comma-separated lists), evaluates polymorphic FK patterns (discriminator column vs supertype table), assesses self-referential relationships, and reviews tree hierarchy approaches.

## Verify
- One-to-many modeled as FK on child table, never as repeating group or array
- Many-to-many always uses explicit join table (with composite PK of both FKs or own PK + unique constraint)
- Polymorphic relationships justified: discriminator column approach chosen over supertype table with rationale
- Polymorphic discriminator column has CHECK constraint listing allowed types
- If supertype table used for polymorphic: base table PK correctly referenced by all subtypes
- Self-referential FKs (e.g., `parent_id` in same table) have index on FK column and ON DELETE documented
- Tree hierarchies approach documented: adjacency list (parent pointer), closure table, or nested sets
- Adjacency list used for shallow trees; closure table for querying deep hierarchies; nested sets only if frequent hierarchical queries
