---
id: a8f3d217-9c4e-4b01-8a5f-1e7c9b2d4f60
title: "SQLite best practices"
domain: agentic-cookbook://guidelines/database/sqlite-best-practices
type: guideline
version: 1.0.0
status: draft
language: en
created: 2026-04-03
modified: 2026-04-03
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "Comprehensive SQLite reference covering schema design, performance tuning, device-to-server sync, and production operations"
platforms:
  - sqlite
tags:
  - database
  - sqlite
  - sync
  - offline-first
depends-on: []
related: []
references:
  - https://sqlite.org/docs.html
  - https://sqlite.org/queryplanner.html
  - https://sqlite.org/wal.html
  - https://sqlite.org/foreignkeys.html
  - https://sqlite.org/lang_createtrigger.html
  - https://sqlite.org/sessionintro.html
  - https://sqlite.org/intern-v-extern-blob.html
  - https://sqlite.org/stricttables.html
  - https://sqlite.org/rowidtable.html
  - https://sqlite.org/autoinc.html
  - https://sqlite.org/withoutrowid.html
  - https://sqlite.org/backup.html
  - https://sqlite.org/pragma.html
  - https://sqlite.org/datatype3.html
  - https://sqlite.org/lang_altertable.html
  - https://electric-sql.com
  - https://www.powersync.com
  - https://turso.tech
  - https://litestream.io
  - https://vlcn.io/docs/cr-sqlite
---

# SQLite Best Practices

> Comprehensive reference covering schema design, performance tuning, device-to-server sync, and production operations.
> Research compiled April 2026 from official SQLite documentation, benchmarks, and practitioner sources.

---

## Table of Contents

### Part I: Schema Design
1. [Column Naming Conventions](#1-column-naming-conventions)
2. [Data Types and Type Affinity](#2-data-types-and-type-affinity)
3. [Primary Key Strategies](#3-primary-key-strategies)
4. [Foreign Keys and Referential Integrity](#4-foreign-keys-and-referential-integrity)
5. [CHECK Constraints and Data Validation](#5-check-constraints-and-data-validation)
6. [Schema Design Patterns](#6-schema-design-patterns)

### Part II: Performance and Tuning
7. [Indexes](#7-indexes)
8. [Triggers](#8-triggers)
9. [WAL Mode and Journal Modes](#9-wal-mode-and-journal-modes)
10. [Transaction Management](#10-transaction-management)
11. [Query Optimization](#11-query-optimization)
12. [PRAGMA Settings for Production](#12-pragma-settings-for-production)

### Part III: Operations and Maintenance
13. [Migration and Versioning](#13-migration-and-versioning)
14. [Backup and Recovery](#14-backup-and-recovery)
15. [Date and Time Handling](#15-date-and-time-handling)
16. [Blob and Large Data](#16-blob-and-large-data)
17. [Security](#17-security)
18. [Testing with SQLite](#18-testing-with-sqlite)
19. [Common Anti-Patterns](#19-common-anti-patterns)

### Part IV: Device-to-Server Sync
20. [Schema Design for Sync](#20-schema-design-for-sync)
21. [Conflict Resolution](#21-conflict-resolution)
22. [Sync Protocols and Patterns](#22-sync-protocols-and-patterns)
23. [Offline-First Architecture](#23-offline-first-architecture)
24. [Type Mapping Between SQLite and Server Databases](#24-type-mapping-between-sqlite-and-server-databases)
25. [SQLite Sync Tools and Extensions](#25-sqlite-sync-tools-and-extensions)
26. [Real-World Sync Architectures](#26-real-world-sync-architectures)
27. [Performance Considerations for Sync](#27-performance-considerations-for-sync)

### Part V: Appendices
28. [Collected References](#28-collected-references)
29. [Decision Frameworks](#29-decision-frameworks)

---

# Part I: Schema Design

## 1. Column Naming Conventions

### Recommended Practice: snake_case everywhere

Use `snake_case` for all identifiers -- tables, columns, indexes, constraints, triggers. This is the dominant convention in SQL and the most readable across tools and contexts.

**Rationale:** SQL is case-insensitive for identifiers. CamelCase creates ambiguity: `UnderValue` and `Undervalue` are identical to SQLite, but `under_value` and `undervalue` are visually distinct. Underscores also improve readability for non-native English speakers and people with vision difficulties.

```sql
-- Good
CREATE TABLE workflow_run (
    workflow_run_id  INTEGER PRIMARY KEY,
    workflow_name    TEXT NOT NULL,
    creation_date    TEXT NOT NULL DEFAULT (datetime('now')),
    is_active        INTEGER NOT NULL DEFAULT 1
);

-- Avoid
CREATE TABLE WorkflowRun (
    WorkflowRunID INTEGER PRIMARY KEY,
    WorkflowName  TEXT NOT NULL,
    CreatedAt     TEXT NOT NULL DEFAULT (datetime('now')),
    IsActive      INTEGER NOT NULL DEFAULT 1
);
```

### Table Naming: Plural vs. Singular

Both conventions have advocates. The key argument for **plural** is that it avoids collisions with SQL reserved words (`user` is reserved; `users` is not). The key argument for **singular** is that each row represents one entity, and singular nouns compose better in compound names (`workflow_run` vs. `workflows_runs`).

**Pick one and be consistent.** If a project already uses singular, stick with singular.

### Primary Key Column Naming

Use `table_name_id` (or at minimum a descriptive name), not bare `id`.

```sql
-- Good: self-documenting in JOINs
SELECT *
FROM audit_log al
JOIN actors a ON a.actor_id = al.changed_by_actor_id;

-- Bad: ambiguous in JOINs, easy to introduce bugs
SELECT *
FROM audit_log al
JOIN actors a ON a.id = al.changed_by;
```

When both sides of a JOIN say `id`, errors are invisible. When they say `actor_id` and `finding_id`, mismatches are obvious.

### Foreign Key Column Naming

Match the referenced column name when possible. When a table references the same parent table multiple times, add a descriptive qualifier:

```sql
-- Single reference: match the parent column name
finding_id INTEGER REFERENCES findings(finding_id)

-- Multiple references to same parent: add qualifier
source_actor_id      INTEGER REFERENCES actors(actor_id),
destination_actor_id INTEGER REFERENCES actors(actor_id)
```

### Boolean Columns

Prefix with `is_` or `has_`:

```sql
is_active    INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
has_children INTEGER NOT NULL DEFAULT 0 CHECK (has_children IN (0, 1))
```

### Date/Time Columns

Use descriptive event names, not generic suffixes:

```sql
-- Good: describes the event
creation_date    TEXT NOT NULL DEFAULT (datetime('now')),
modification_date TEXT,
completion_date  TEXT

-- Avoid: vague
created_at TEXT,
updated_at TEXT
```

### Reserved Words to Avoid

SQLite has 147 reserved keywords. Common traps for column/table names:

| Dangerous Name | Problem | Alternative |
|---|---|---|
| `order` | Reserved keyword | `sort_order`, `display_order` |
| `group` | Reserved keyword | `team`, `grouping` |
| `index` | Reserved keyword | `position`, `sort_index` |
| `key` | Reserved keyword | `lookup_key`, `api_key` |
| `value` | Reserved keyword | `setting_value`, `metric_value` |
| `action` | Reserved keyword | `operation`, `activity` |
| `check` | Reserved keyword | `validation`, `check_result` |
| `column` | Reserved keyword | `field`, `attribute` |
| `default` | Reserved keyword | `default_value`, `fallback` |
| `replace` | Reserved keyword | `substitution`, `replacement` |
| `match` | Reserved keyword | `comparison`, `match_result` |
| `plan` | Reserved keyword | `execution_plan` |
| `query` | Reserved keyword | `search_query` |
| `row` | Reserved keyword | `record`, `entry` |
| `filter` | Reserved keyword | `criterion`, `filter_expr` |

If you must use a reserved word, quote it with double quotes (`"order"`), but this adds friction to every query. Better to choose a different name.

**Future-proofing:** SQLite adds new keywords over time. The official docs recommend quoting any English word used as an identifier, even if it is not currently reserved.

### Index and Constraint Naming

```sql
-- Indexes: ix_tablename_purpose
CREATE INDEX ix_findings_workflow_run_id ON findings(workflow_run_id);
CREATE UNIQUE INDEX ux_actors_email ON actors(email);

-- Triggers: tr_tablename_event_purpose
CREATE TRIGGER tr_documents_after_update_audit ...

-- Check constraints: ck_tablename_column
CONSTRAINT ck_employees_salary CHECK (salary > 0)
```

### Sources

- [Database Naming Standards (Ovid)](https://dev.to/ovid/database-naming-standards-2061) -- snake_case rationale, plural tables, FK naming
- [SQL Naming Conventions (bbkane)](https://www.bbkane.com/blog/sql-naming-conventions/) -- PK naming, index conventions, trigger naming
- [SQLite Keywords](https://www.sqlite.org/lang_keywords.html) -- official keyword list, quoting rules
- [Baeldung SQL Naming Conventions](https://www.baeldung.com/sql/database-table-column-naming-conventions)
- [BrainStation SQL Naming Conventions](https://brainstation.io/learn/sql/naming-conventions)

---

## 2. Data Types and Type Affinity

### SQLite's Type System is Unique

Most databases use **static typing** -- the column determines the type. SQLite uses **dynamic typing** -- the value determines the type. A column's declared type is a *preference* (called "affinity"), not a constraint.

```sql
-- This is legal in SQLite (without STRICT):
CREATE TABLE demo (age INTEGER);
INSERT INTO demo VALUES ('not a number');  -- Stores as TEXT
SELECT typeof(age) FROM demo;             -- Returns 'text'
```

### The Five Storage Classes

Every value in SQLite belongs to exactly one storage class:

| Storage Class | Description | Size |
|---|---|---|
| `NULL` | Null value | 0 bytes |
| `INTEGER` | Signed integer | 0, 1, 2, 3, 4, 6, or 8 bytes (variable) |
| `REAL` | IEEE 754 float | 8 bytes |
| `TEXT` | UTF-8 string | Variable |
| `BLOB` | Raw bytes | Variable |

**Key differences from other databases:**
- No `BOOLEAN` type. Use `INTEGER` with 0/1. `TRUE` and `FALSE` keywords (since 3.23.0) are just aliases for 1 and 0.
- No `DATE`/`DATETIME` type. Store as `TEXT` (ISO 8601: `'YYYY-MM-DD HH:MM:SS'`), `REAL` (Julian day), or `INTEGER` (Unix timestamp). TEXT is recommended for readability.
- `INTEGER` storage is variable-width (0-8 bytes), not fixed. Small values use less space than large ones.

### Type Affinity: The 5-Rule Algorithm

For non-STRICT tables, SQLite determines column affinity from the declared type name using these rules **in order of precedence**:

| Rule | If declared type contains... | Affinity | Examples |
|---|---|---|---|
| 1 | `"INT"` | INTEGER | INT, INTEGER, TINYINT, SMALLINT, MEDIUMINT, BIGINT, INT2, INT8 |
| 2 | `"CHAR"`, `"CLOB"`, `"TEXT"` | TEXT | CHARACTER(20), VARCHAR(255), NCHAR, TEXT, CLOB |
| 3 | `"BLOB"` or no type | BLOB | BLOB, (no type specified) |
| 4 | `"REAL"`, `"FLOA"`, `"DOUB"` | REAL | REAL, DOUBLE, FLOAT, DOUBLE PRECISION |
| 5 | Otherwise | NUMERIC | NUMERIC, DECIMAL(10,5), BOOLEAN, DATE, DATETIME |

**Critical: order matters.** `"CHARINT"` matches both rules 1 and 2, but rule 1 wins -- affinity is INTEGER. `"FLOATING POINT"` contains `"INT"` (in "POINT"), so affinity is INTEGER, not REAL.

### The STRING Gotcha

Declaring a column as `STRING` gives it **NUMERIC** affinity (rule 5 -- "STRING" does not contain "CHAR", "CLOB", or "TEXT"). This means number-like strings get silently converted to integers:

```sql
CREATE TABLE demo (val STRING);
INSERT INTO demo VALUES ('007');
SELECT typeof(val), val FROM demo;
-- Returns: integer, 7  (leading zeros lost!)
```

**Fix:** Use `TEXT`, never `STRING`.

### NUMERIC Affinity Behavior

NUMERIC affinity aggressively converts text to numbers:

```sql
CREATE TABLE demo (val NUMERIC);
INSERT INTO demo VALUES ('3.0e+5');
SELECT typeof(val), val FROM demo;
-- Returns: integer, 300000  (converted from scientific notation to integer)
```

### Comparison Pitfalls

When comparing values of different storage classes without affinity guidance, SQLite uses this ordering: `NULL < INTEGER/REAL < TEXT < BLOB`. This produces surprising results:

```sql
CREATE TABLE t1 (
    a TEXT,     -- text affinity
    b NUMERIC,  -- numeric affinity
    c BLOB,     -- blob affinity (no type)
    d           -- blob affinity (no type)
);
INSERT INTO t1 VALUES ('500', '500', '500', 500);

-- Column c has BLOB affinity, d is integer 500.
-- Without affinity guidance: INTEGER < TEXT always
SELECT d < '40' FROM t1;
-- Returns: 1  (integer 500 is "less than" text '40')
```

The full comparison rules:
1. If one operand has INTEGER/REAL/NUMERIC affinity and the other has TEXT/BLOB/no affinity, apply NUMERIC affinity to the other operand before comparing.
2. If one operand has TEXT affinity and the other has no affinity, apply TEXT affinity to the other operand.
3. Otherwise, compare as-is using the storage class ordering.

### STRICT Tables (SQLite 3.37.0+)

STRICT tables enforce rigid typing. Declare with the `STRICT` keyword:

```sql
CREATE TABLE measurements (
    measurement_id INTEGER PRIMARY KEY,
    sensor_name    TEXT NOT NULL,
    reading        REAL NOT NULL,
    raw_data       BLOB
) STRICT;
```

**Allowed types in STRICT tables:** `INT`, `INTEGER`, `REAL`, `TEXT`, `BLOB`, `ANY`.

**Behavior:**
- Inserting a wrong type raises `SQLITE_CONSTRAINT_DATATYPE`
- SQLite attempts type coercion first (like other databases), fails if coercion fails
- `INTEGER PRIMARY KEY` still aliases rowid (but `INT PRIMARY KEY` does not)
- `ANY` type preserves values exactly as inserted, with no coercion

```sql
CREATE TABLE demo (val ANY) STRICT;
INSERT INTO demo VALUES ('007');
SELECT typeof(val), val FROM demo;
-- Returns: text, 007  (preserved exactly -- no conversion)

CREATE TABLE demo2 (val INTEGER) STRICT;
INSERT INTO demo2 VALUES ('not a number');
-- ERROR: SQLITE_CONSTRAINT_DATATYPE
```

**Combining with WITHOUT ROWID:**
```sql
CREATE TABLE lookups (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
) STRICT, WITHOUT ROWID;
```

**Compatibility:** Databases with STRICT tables cannot be opened by SQLite versions before 3.37.0.

### Practical Recommendations

1. **Declare explicit types** on every column, even in non-STRICT tables. Use `TEXT`, `INTEGER`, `REAL`, `BLOB` -- the four canonical storage classes.
2. **Never use `STRING`** -- it gives NUMERIC affinity. Use `TEXT`.
3. **Use `TEXT` for dates** in ISO 8601 format (`'YYYY-MM-DD HH:MM:SS'`). It sorts correctly and is human-readable.
4. **Use `INTEGER` for booleans** with CHECK constraints: `CHECK (col IN (0, 1))`.
5. **Consider STRICT tables** for new schemas where type safety matters. The tradeoff is losing compatibility with SQLite < 3.37.0.
6. **Be explicit about comparisons** -- don't rely on affinity coercion in WHERE clauses. Cast or quote consistently.

### Sources

- [Datatypes In SQLite](https://www.sqlite.org/datatype3.html) -- official type system docs, affinity rules, comparison behavior
- [STRICT Tables](https://www.sqlite.org/stricttables.html) -- official STRICT table docs
- [The Advantages of Flexible Typing](https://www.sqlite.org/flextypegood.html) -- official rationale for dynamic typing
- [SQLite's Flexible Typing (DEV Community)](https://dev.to/lovestaco/sqlites-flexible-typing-storage-types-and-column-affinity-4ggg)
- [Understanding Type Affinity in SQLite](https://database.guide/understanding-type-affinity-in-sqlite/)

---

## 3. Primary Key Strategies

### How SQLite's rowid Works

Every SQLite table (unless `WITHOUT ROWID`) has a hidden 64-bit signed integer `rowid`. It is:
- The actual key used by the B-tree storage engine
- Accessible via the aliases `rowid`, `_rowid_`, or `oid` (unless a real column shadows these names)
- Automatically assigned on INSERT if not specified
- **Not persistent** -- `VACUUM` may reassign rowids unless aliased by `INTEGER PRIMARY KEY`

### Option 1: INTEGER PRIMARY KEY (Recommended Default)

```sql
CREATE TABLE findings (
    finding_id INTEGER PRIMARY KEY,
    content    TEXT NOT NULL,
    severity   TEXT NOT NULL
);
```

**What happens:**
- `finding_id` becomes an **alias for rowid** -- no extra storage, no separate index
- On INSERT without a value, SQLite assigns `max(finding_id) + 1`
- If the max row is deleted, that ID *can* be reused
- This is the fastest possible primary key in SQLite

**Critical detail:** Only `INTEGER PRIMARY KEY` aliases rowid. `INT PRIMARY KEY` does NOT -- it creates a regular column with a separate unique index, doubling storage overhead.

```sql
-- These alias rowid (identical behavior):
id INTEGER PRIMARY KEY
id INTEGER PRIMARY KEY NOT NULL  -- NOT NULL is redundant but harmless

-- These do NOT alias rowid:
id INT PRIMARY KEY        -- INT != INTEGER for this purpose
id INTEGER PRIMARY KEY DESC  -- DESC prevents aliasing (since SQLite 3.45.0 this may change)
id INTEGER UNIQUE         -- UNIQUE != PRIMARY KEY for this purpose
```

### Option 2: INTEGER PRIMARY KEY AUTOINCREMENT

```sql
CREATE TABLE audit_entries (
    entry_id INTEGER PRIMARY KEY AUTOINCREMENT,
    action   TEXT NOT NULL,
    actor_id INTEGER NOT NULL
);
```

**What it adds beyond plain INTEGER PRIMARY KEY:**
- Guarantees IDs are **strictly monotonically increasing and never reused** -- even if the highest row is deleted
- Maintains a counter in the internal `sqlite_sequence` table
- If the counter reaches `2^63 - 1` (9,223,372,036,854,775,807), further inserts fail with `SQLITE_FULL`
- Without AUTOINCREMENT, SQLite would try random IDs at the max, potentially reusing old ones

**Performance cost:** Every INSERT requires an additional read/write to `sqlite_sequence`. The official SQLite docs explicitly warn: *"The AUTOINCREMENT keyword imposes extra CPU, memory, disk space, and disk I/O overhead and should be avoided if not strictly needed."*

**When to use it:** Audit logs, financial ledgers, event streams -- anywhere ID reuse would be semantically wrong or a security concern.

### Option 3: UUID

```sql
-- Text form (36 chars, human-readable but large)
CREATE TABLE sync_records (
    record_id TEXT PRIMARY KEY,
    data      TEXT NOT NULL
);

-- Blob form (16 bytes, more compact)
CREATE TABLE sync_records (
    record_id BLOB PRIMARY KEY,
    data      TEXT NOT NULL
);
```

**Advantages:**
- Globally unique across databases, servers, devices
- Generated client-side -- ID is known before INSERT
- No coordination required in distributed systems

**Significant downsides in SQLite:**
- Random UUIDs (v4) destroy B-tree locality. Sequential integer inserts append to the rightmost leaf page; random UUIDs scatter inserts across the entire tree, causing page splits and cache thrashing.
- 36-byte TEXT UUID is 9x larger than an 8-byte integer. This ripples into every foreign key and index.
- Does not alias rowid, so SQLite maintains two data structures (the rowid B-tree and a separate index).

**UUIDv7 mitigates the locality problem.** UUIDv7 (IETF-approved May 2024) encodes a Unix millisecond timestamp in the first 48 bits, making IDs time-ordered. This preserves B-tree locality while maintaining global uniqueness.

```sql
-- Store UUIDv7 as BLOB for maximum efficiency
CREATE TABLE distributed_events (
    event_id BLOB PRIMARY KEY,  -- 16-byte UUIDv7
    payload  TEXT NOT NULL
) WITHOUT ROWID;
```

**Hybrid approach:** Use `INTEGER PRIMARY KEY` for internal operations (joins, indexes, foreign keys) and a separate UUID column for external APIs:

```sql
CREATE TABLE resources (
    resource_id  INTEGER PRIMARY KEY,
    external_id  TEXT NOT NULL UNIQUE,  -- UUIDv7 for API exposure
    resource_name TEXT NOT NULL
);
```

### WITHOUT ROWID Tables

```sql
CREATE TABLE word_counts (
    word TEXT PRIMARY KEY,
    count INTEGER NOT NULL DEFAULT 0
) WITHOUT ROWID;
```

**What it does:** Uses the declared PRIMARY KEY as the clustered index key instead of a hidden rowid. The table is stored as a single B-tree keyed on the PRIMARY KEY columns.

**When to use:**
- Non-integer or composite primary keys
- Small rows (< ~1/20th of page size, roughly 50-200 bytes)
- Tables that do NOT store large strings or BLOBs

**Performance benefit:** For the `word_counts` example, a regular table stores the word text twice (once in the rowid B-tree, once in the unique index). WITHOUT ROWID stores it once -- roughly **50% less disk space and 2x faster** for simple lookups.

**Restrictions:**
- Must have an explicit PRIMARY KEY (error if omitted)
- No AUTOINCREMENT
- NOT NULL enforced on all PRIMARY KEY columns (SQL standard)
- `sqlite3_last_insert_rowid()` does not work
- No incremental BLOB I/O
- Requires SQLite 3.8.2+

### Decision Table

| Situation | Use |
|---|---|
| Default / general tables | `INTEGER PRIMARY KEY` |
| Audit log, ledger -- IDs must never reuse | `INTEGER PRIMARY KEY AUTOINCREMENT` |
| Distributed / multi-device sync | UUIDv7 as `BLOB` (prefer WITHOUT ROWID) |
| Exposing IDs in a public API | Separate UUID column + integer PK internally |
| Non-integer or composite key, small rows | `WITHOUT ROWID` |
| Maximum performance, local-only DB | `INTEGER PRIMARY KEY` |

### Sources

- [Rowid Tables](https://www.sqlite.org/rowidtable.html) -- official rowid behavior, INTEGER PRIMARY KEY aliasing
- [SQLite Autoincrement](https://www.sqlite.org/autoinc.html) -- official AUTOINCREMENT docs, sqlite_sequence, performance warnings
- [WITHOUT ROWID Tables](https://www.sqlite.org/withoutrowid.html) -- official WITHOUT ROWID docs, when to use, restrictions
- [UUID vs Auto-Increment (Bytebase)](https://www.bytebase.com/blog/choose-primary-key-uuid-or-auto-increment/) -- UUID performance analysis, UUIDv7
- [Primary Key Data Types (High Performance SQLite)](https://highperformancesqlite.com/watch/primary-key-data-types)

---

## 4. Foreign Keys and Referential Integrity

### The Critical First Step: Enable Foreign Keys

Foreign key constraints are **disabled by default** in SQLite and must be enabled for **each database connection** at runtime:

```sql
PRAGMA foreign_keys = ON;
```

This is the single most common SQLite pitfall. Developers create schemas with FOREIGN KEY declarations, test them, and find constraints are silently not enforced. The PRAGMA does not persist in the database file -- it must be set every time a connection opens.

**Verification:**
```sql
PRAGMA foreign_keys;  -- Returns 0 (off) or 1 (on)
```

**Cannot be changed mid-transaction:** Attempting to enable/disable foreign keys inside a `BEGIN...COMMIT` block silently does nothing.

**Why this design?** Foreign keys were added long after SQLite's file format was designed. There is no place in the database file to store the on/off state, and changing the default would break billions of existing applications.

### Foreign Key Declaration

```sql
-- Inline (column-level)
CREATE TABLE tracks (
    track_id     INTEGER PRIMARY KEY,
    track_name   TEXT NOT NULL,
    artist_id    INTEGER NOT NULL REFERENCES artists(artist_id)
);

-- Table-level (required for composite FKs)
CREATE TABLE songs (
    song_id     INTEGER PRIMARY KEY,
    song_artist TEXT NOT NULL,
    song_album  TEXT NOT NULL,
    FOREIGN KEY (song_artist, song_album)
        REFERENCES albums(album_artist, album_name)
);
```

**Requirement:** The referenced column(s) must be the PRIMARY KEY or have a UNIQUE index. Otherwise, the table creation fails.

### ON DELETE / ON UPDATE Actions

Actions configure what happens to child rows when a referenced parent row is deleted or its key is modified. Default is `NO ACTION`.

| Action | Behavior |
|---|---|
| `NO ACTION` | Fail if child rows exist (checked at statement end) |
| `RESTRICT` | Fail immediately, even with deferred constraints |
| `SET NULL` | Set child FK column(s) to NULL |
| `SET DEFAULT` | Set child FK column(s) to their DEFAULT value |
| `CASCADE` | Delete child rows (ON DELETE) or update child FK values (ON UPDATE) |

```sql
CREATE TABLE tracks (
    track_id   INTEGER PRIMARY KEY,
    track_name TEXT NOT NULL,
    artist_id  INTEGER REFERENCES artists(artist_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);
```

**CASCADE example:**
```sql
-- Parent table
INSERT INTO artists VALUES (1, 'Dean Martin');
INSERT INTO artists VALUES (2, 'Frank Sinatra');

-- Child rows
INSERT INTO tracks VALUES (11, 'That''s Amore', 1);
INSERT INTO tracks VALUES (12, 'Christmas Blues', 1);
INSERT INTO tracks VALUES (13, 'My Way', 2);

-- Update parent key -- cascades to all children
UPDATE artists SET artist_id = 100 WHERE artist_name = 'Dean Martin';

-- After: tracks 11 and 12 now have artist_id = 100
```

**SET DEFAULT pitfall:** If the default value does not exist in the parent table, the action fails:

```sql
CREATE TABLE tracks (
    track_id   INTEGER PRIMARY KEY,
    track_name TEXT NOT NULL,
    artist_id  INTEGER DEFAULT 0 REFERENCES artists(artist_id)
        ON DELETE SET DEFAULT
);

-- This FAILS if artist_id=0 doesn't exist in artists
DELETE FROM artists WHERE artist_id = 3;
-- Error: foreign key constraint failed

-- Fix: ensure the default value exists
INSERT INTO artists VALUES (0, 'Unknown Artist');
-- Now the delete succeeds
```

### Deferred Constraints

By default, FK constraints are checked at the end of each statement (immediate). Deferred constraints delay checking until COMMIT:

```sql
CREATE TABLE tracks (
    track_id   INTEGER PRIMARY KEY,
    track_name TEXT NOT NULL,
    artist_id  INTEGER REFERENCES artists(artist_id)
        DEFERRABLE INITIALLY DEFERRED
);

-- With deferred constraints, insert order doesn't matter within a transaction:
BEGIN;
INSERT INTO tracks VALUES (1, 'My Song', 5);  -- artist 5 doesn't exist yet
INSERT INTO artists VALUES (5, 'New Artist');  -- now it does
COMMIT;  -- constraint checked here -- passes
```

**Temporary override** for all constraints in a session:
```sql
PRAGMA defer_foreign_keys = ON;
```

This is useful for bulk data imports or schema migrations where insert order is inconvenient.

### Common Pitfalls

**1. NULL values bypass FK checks:**
```sql
-- This succeeds even if artist_id=999 doesn't exist
INSERT INTO tracks (track_id, track_name, artist_id) VALUES (1, 'Test', NULL);
-- NULL in any FK column = no parent row required
```

**2. Missing indexes on child FK columns:**
Without an index on the child's FK column, every parent DELETE/UPDATE requires a full table scan of the child table:

```sql
-- Always create indexes on FK columns
CREATE INDEX ix_tracks_artist_id ON tracks(artist_id);
```

**3. Composite FKs must match exactly:**
The child column count, types, and collation must match the parent's PRIMARY KEY or UNIQUE constraint exactly.

**4. ALTER TABLE restrictions:**
You cannot add a new column with a FK constraint and a non-NULL default:

```sql
-- Fails
ALTER TABLE tracks ADD COLUMN genre_id INTEGER NOT NULL DEFAULT 1
    REFERENCES genres(genre_id);

-- Works (NULL default)
ALTER TABLE tracks ADD COLUMN genre_id INTEGER REFERENCES genres(genre_id);
```

**5. Cross-schema FKs not supported:**
Foreign keys cannot reference tables in attached databases.

### Sources

- [SQLite Foreign Key Support](https://sqlite.org/foreignkeys.html) -- official comprehensive FK docs
- [SQLite Forum: Why is FK support per-connection?](https://sqlite.org/forum/info/c5dc50f61b88c587) -- design rationale
- [SQLite Foreign Keys: Common Pitfalls](https://runebook.dev/en/docs/sqlite/foreignkeys) -- indexed practical guide

---

## 5. CHECK Constraints and Data Validation

### Syntax

```sql
-- Inline (column-level)
CREATE TABLE products (
    product_id   INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    quantity     INTEGER NOT NULL CHECK (quantity >= 0),
    price        REAL NOT NULL CHECK (price > 0)
);

-- Table-level (can reference multiple columns)
CREATE TABLE events (
    event_id   INTEGER PRIMARY KEY,
    start_date TEXT NOT NULL,
    end_date   TEXT NOT NULL,
    CHECK (end_date >= start_date)
);

-- Named constraint
CREATE TABLE employees (
    employee_id INTEGER PRIMARY KEY,
    salary      REAL NOT NULL,
    CONSTRAINT ck_employees_salary CHECK (salary > 0)
);
```

There is no functional difference between column-level and table-level CHECK constraints. The only advantage of table-level is the ability to reference multiple columns.

### How CHECK Evaluation Works

1. The CHECK expression is evaluated on every INSERT and UPDATE
2. The result is cast to NUMERIC
3. **If result is integer 0 or real 0.0** -- constraint violation (`SQLITE_CONSTRAINT_CHECK`)
4. **If result is NULL** -- no violation (NULL is truthy for CHECK purposes)
5. **If result is any non-zero value** -- no violation

**The NULL gotcha:** `CHECK (status IN ('active', 'inactive'))` allows NULL values because `NULL IN (...)` evaluates to NULL, which is not zero. Add `NOT NULL` separately if NULL should be prohibited.

### Common Validation Patterns

#### Range Validation
```sql
age     INTEGER NOT NULL CHECK (age >= 0 AND age <= 150),
score   REAL NOT NULL CHECK (score BETWEEN 0.0 AND 100.0),
percent INTEGER NOT NULL CHECK (percent >= 0 AND percent <= 100)
```

#### Enum-Like Constraints (Restricting to Known Values)
```sql
status    TEXT NOT NULL CHECK (status IN ('pending', 'active', 'completed', 'failed')),
priority  INTEGER NOT NULL CHECK (priority IN (1, 2, 3, 4, 5)),
direction TEXT NOT NULL CHECK (direction IN ('inbound', 'outbound'))
```

#### Boolean Enforcement
```sql
is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
```

#### Pattern Matching
```sql
email TEXT NOT NULL CHECK (email LIKE '%_@_%.__%'),
phone TEXT CHECK (phone LIKE '+%' OR phone IS NULL),
code  TEXT NOT NULL CHECK (length(code) = 6 AND code GLOB '[A-Z][A-Z][0-9][0-9][0-9][0-9]')
```

#### Multi-Column Constraints
```sql
CREATE TABLE promotions (
    promotion_id INTEGER PRIMARY KEY,
    start_date   TEXT NOT NULL,
    end_date     TEXT NOT NULL,
    discount     REAL NOT NULL,
    CHECK (end_date > start_date),
    CHECK (discount > 0 AND discount <= 1.0)
);
```

#### Conditional Logic
```sql
CREATE TABLE inventory (
    product_id   INTEGER PRIMARY KEY,
    product_name TEXT NOT NULL,
    stock        INTEGER NOT NULL,
    status       TEXT NOT NULL,
    CHECK (
        (status = 'surplus' AND stock >= 500) OR
        (status != 'surplus')
    )
);
```

#### String Length Validation
```sql
username TEXT NOT NULL CHECK (length(username) >= 3 AND length(username) <= 50),
api_key  TEXT NOT NULL CHECK (length(api_key) = 32)
```

### What Is NOT Allowed in CHECK Expressions

These are explicitly prohibited and will cause errors:

| Prohibited | Reason |
|---|---|
| Subqueries (`SELECT ...`) | Cannot reference other rows or tables |
| `CURRENT_TIME` | Non-deterministic |
| `CURRENT_DATE` | Non-deterministic |
| `CURRENT_TIMESTAMP` | Non-deterministic |

**Workaround for date validation:** You cannot use `CHECK (event_date <= CURRENT_DATE)` in the schema definition. However, `DEFAULT (datetime('now'))` works for defaults because defaults are evaluated at INSERT time, not at schema creation time.

For date validation that depends on "now", use triggers or application-level validation instead.

### Conflict Resolution

The conflict resolution algorithm for CHECK constraints is always `ABORT`. The `ON CONFLICT` clause is parsed for historical compatibility but has no effect:

```sql
-- ON CONFLICT is ignored for CHECK constraints
quantity INTEGER NOT NULL CHECK (quantity >= 0) ON CONFLICT REPLACE
-- Still ABORTs on violation, does NOT replace
```

### Disabling CHECK Constraints

For data migrations or imports of potentially dirty data:

```sql
PRAGMA ignore_check_constraints = ON;
-- Import data...
PRAGMA ignore_check_constraints = OFF;
```

After import, verify data integrity:

```sql
PRAGMA integrity_check;  -- Reports CHECK violations as corruption
```

### Limitations

1. **Cannot add via ALTER TABLE.** You must recreate the table:
   ```sql
   -- 1. Create new table with constraints
   CREATE TABLE new_table (...constraints...);
   -- 2. Copy data
   INSERT INTO new_table SELECT * FROM old_table;
   -- 3. Drop old table
   DROP TABLE old_table;
   -- 4. Rename
   ALTER TABLE new_table RENAME TO old_table;
   ```

2. **Row-scoped only.** Cannot validate against other rows (use triggers for cross-row validation).

3. **Not verified on SELECT.** Corrupted data (from external file manipulation or disabled checks) can be read even if it violates constraints.

4. **Minimal performance impact.** CHECK expressions are simple comparisons evaluated in-process. Modern SQLite versions have optimized constraint evaluation. The cost is negligible compared to disk I/O.

### Sources

- [CREATE TABLE: CHECK constraints](https://www.sqlite.org/lang_createtable.html) -- official docs, evaluation rules, prohibited expressions
- [Validating Data with SQLite CHECK Constraints (Sling Academy)](https://www.slingacademy.com/article/validating-your-data-with-sqlite-check-constraints/)
- [How to Write Effective CHECK Constraints (Sling Academy)](https://www.slingacademy.com/article/how-to-write-effective-check-constraints-in-sqlite/)
- [SQLite Check Constraints (sql-easy.com)](https://www.sql-easy.com/learn/sqlite-check-constraints/)
- [SQLite Data Validation: Using CHECK and Alternatives](https://runebook.dev/en/docs/sqlite/lang_createtable/ckconst)

---

## 6. Schema Design Patterns

### Polymorphic Foreign Keys

#### The Problem

A polymorphic foreign key is a column that references one of several different tables. A common example is a `changed_by` column in an audit log where the actor could be a human, a service, or a bot.

#### Pattern 1: Generic FK with Discriminator Column

```sql
CREATE TABLE audit_log (
    audit_log_id    INTEGER PRIMARY KEY,
    changed_by_id   INTEGER NOT NULL,
    changed_by_type TEXT NOT NULL CHECK (changed_by_type IN ('human', 'service', 'bot'))
);
```

Store both the `id` and a `type` discriminator. Application code resolves the join. SQLite will not enforce FK referential integrity across multiple tables even with `PRAGMA foreign_keys = ON`, so the app layer owns that constraint.

**Pros:** Simple, works everywhere, no schema changes when adding types
**Cons:** No DB-level FK enforcement, easy to get into inconsistent state

#### Pattern 2: Supertype / Base Table (Recommended)

```sql
CREATE TABLE actors (
    actor_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    actor_type   TEXT NOT NULL CHECK (actor_type IN ('human', 'service', 'bot')),
    display_name TEXT NOT NULL  -- denormalized for fast queries
);

CREATE TABLE humans (
    actor_id INTEGER PRIMARY KEY REFERENCES actors(actor_id),
    name     TEXT NOT NULL,
    email    TEXT NOT NULL UNIQUE
);

CREATE TABLE services (
    actor_id     INTEGER PRIMARY KEY REFERENCES actors(actor_id),
    service_name TEXT NOT NULL,
    api_key_hint TEXT
);

CREATE TABLE bots (
    actor_id       INTEGER PRIMARY KEY REFERENCES actors(actor_id),
    bot_name       TEXT NOT NULL,
    owner_actor_id INTEGER REFERENCES actors(actor_id)
);

CREATE TABLE audit_log (
    audit_log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name   TEXT NOT NULL,
    row_id       INTEGER NOT NULL,
    operation    TEXT NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    changed_by   INTEGER NOT NULL REFERENCES actors(actor_id),
    change_date  TEXT NOT NULL DEFAULT (datetime('now'))
);
```

`audit_log.changed_by` is a **real, enforced FK** into `actors`. Each subtype has its own table with a 1:1 FK back to `actors`.

**Pros:** True referential integrity, clean join point, scalable query pattern
**Cons:** Extra join to get subtype-specific data, insert order matters (supertype first)

#### Pattern 3: Nullable Column Per Type

```sql
CREATE TABLE audit_log (
    audit_log_id           INTEGER PRIMARY KEY,
    changed_by_human_id    INTEGER REFERENCES humans(actor_id),
    changed_by_service_id  INTEGER REFERENCES services(actor_id),
    changed_by_bot_id      INTEGER REFERENCES bots(actor_id),
    CHECK (
        (changed_by_human_id   IS NOT NULL) +
        (changed_by_service_id IS NOT NULL) +
        (changed_by_bot_id     IS NOT NULL) = 1
    )
);
```

**Pros:** Real FK enforcement on each column, fully declarative
**Cons:** Gets unwieldy fast as types grow, adds nullable columns

#### Recommendation

**Use Pattern 2 (supertype table)** when actor types share a common identity concept. It is the most principled design and gives you real referential integrity. Denormalize `display_name` onto the supertype to avoid subtype joins for common queries (audit feeds, lists).

**Use Pattern 1** when moving fast or comfortable owning FK integrity in the application layer.

### Normalized vs Denormalized

**Recommended practice:** Start with a normalized schema (3NF), then selectively denormalize only the hotspots where joins are measurably slow. This hybrid approach gives you clean data with targeted performance boosts.

**When to normalize:** Transactional systems (banking, inventory, ERP) where accuracy, redundancy control, and storage efficiency matter most.

**When to denormalize:** Read-heavy workloads (data warehouses, dashboards, BI tools) where retrieval speed is the priority. Denormalization deliberately introduces redundancy to speed up certain queries at the cost of extra storage and increased risk of anomalies.

**SQLite-specific consideration:** Because SQLite is embedded (zero network latency), the N+1 problem is far less costly than with client/server databases. Multiple simple queries often outperform complex joins, so the pressure to denormalize is lower than in PostgreSQL or MySQL.

**Benchmark reference:** In one test with 5,000 bars and 10K wines, denormalized queries ran 16x faster for one pattern (569ms vs 9,143ms) and 104x faster for another (83ms vs 8,648ms). The denormalized database was 50% smaller.

Sources:
- [Database Schema Design Patterns for SQLite](https://sqleditor.online/blog/sqlite-schema-design-patterns)
- [Database Design Patterns Every Developer Should Know](https://www.bytebase.com/blog/database-design-patterns/)
- [ByteByteGo: Normalization vs Denormalization](https://blog.bytebytego.com/p/database-schema-design-simplified)
- [SQLite JSON and Denormalization](https://maximeblanc.fr/blog/sqlite-json-and-denormalization)

### JSON Columns

SQLite's JSON functions let you store structured data in TEXT columns while still querying into them.

**Core extraction:**

```sql
-- json_extract: returns SQL type for scalars, JSON text for objects/arrays
SELECT json_extract(data, '$.name') FROM events;
-- For {"name": "alice"} returns: 'alice'

-- ->> operator: always returns SQL type (TEXT, INTEGER, REAL, NULL)
SELECT data ->> '$.name' FROM events;

-- -> operator: always returns JSON text representation
SELECT data -> '$.tags' FROM events;
-- For {"tags": [1,2]} returns: '[1,2]'
```

**Iterating arrays with json_each:**

```sql
-- Find users with a 704 area code phone number
SELECT DISTINCT user.name
FROM user, json_each(user.phone)
WHERE json_each.value LIKE '704-%';
```

**Modifying JSON:**

```sql
-- json_set: creates or overwrites
UPDATE events SET data = json_set(data, '$.status', 'processed');

-- json_insert: creates only (won't overwrite)
UPDATE events SET data = json_insert(data, '$.new_field', 42);

-- json_replace: overwrites only (won't create)
UPDATE events SET data = json_replace(data, '$.status', 'done');

-- Append to array (use $[#] for end position)
UPDATE events SET data = json_set(data, '$.tags[#]', 'new-tag');

-- Remove a key
UPDATE events SET data = json_remove(data, '$.temp_field');
```

**Aggregating rows into JSON:**

```sql
-- Build a JSON array from rows
SELECT json_group_array(json_object('id', id, 'name', name)) FROM users;
-- Returns: [{"id":1,"name":"alice"}, {"id":2,"name":"bob"}]

-- Build a JSON object from rows
SELECT json_group_object(name, score) FROM leaderboard;
-- Returns: {"alice":100, "bob":85}
```

**Validation:**

```sql
SELECT json_valid('{"x":35}');     -- 1 (valid)
SELECT json_valid('{"x":35');      -- 0 (invalid)
SELECT json_valid('{x:35}', 6);   -- 1 (valid JSON5 or JSONB)
```

Source: [SQLite JSON Functions](https://sqlite.org/json1.html)

### Generated Columns for JSON Indexing

The most powerful pattern for JSON performance: virtual generated columns with B-tree indexes.

```sql
CREATE TABLE documents (
  id INTEGER PRIMARY KEY,
  body TEXT  -- JSON
);

-- Extract fields as virtual generated columns
ALTER TABLE documents ADD COLUMN doc_type TEXT
  GENERATED ALWAYS AS (body ->> '$.type') VIRTUAL;

ALTER TABLE documents ADD COLUMN author TEXT
  GENERATED ALWAYS AS (body ->> '$.author') VIRTUAL;

-- Index the generated columns for B-tree speed
CREATE INDEX idx_doc_type ON documents(doc_type);
CREATE INDEX idx_author ON documents(author);

-- Queries now use indexes (verify with EXPLAIN QUERY PLAN):
SELECT * FROM documents WHERE doc_type = 'report' AND author = 'alice';
-- SEARCH documents USING INDEX idx_doc_type (doc_type=?)
```

**VIRTUAL vs STORED:**
- VIRTUAL: computed on read, no disk space, can be added with ALTER TABLE
- STORED: computed on write, uses disk space, cannot be added with ALTER TABLE
- Use STORED when reads vastly outnumber writes; VIRTUAL otherwise

**Key advantages:**
- No extra write overhead (VIRTUAL columns are computed on read)
- Can be added with ALTER TABLE without rebuilding the table
- Indexes work exactly like regular column indexes
- Zero back-filling when adding new virtual columns

Sources: [SQLite Generated Columns](https://sqlite.org/gencol.html), [SQLite JSON Virtual Columns + Indexing](https://www.dbpro.app/blog/sqlite-json-virtual-columns-indexing)

### Materialized Views via Triggers

SQLite has no native materialized views. Simulate them with a table + triggers:

```sql
-- 1. Create the materialized view table
CREATE TABLE report_summary (
  report_id  INTEGER PRIMARY KEY,
  category   TEXT NOT NULL,
  item_count INTEGER NOT NULL DEFAULT 0,
  last_updated TEXT NOT NULL
);

-- 2. Populate on insert to source table
CREATE TRIGGER trg_report_insert AFTER INSERT ON items
BEGIN
  INSERT INTO report_summary (report_id, category, item_count, last_updated)
    VALUES (NEW.report_id, NEW.category, 1, datetime('now'))
    ON CONFLICT(report_id) DO UPDATE SET
      item_count = item_count + 1,
      last_updated = datetime('now');
END;

-- 3. Update on delete from source table
CREATE TRIGGER trg_report_delete AFTER DELETE ON items
BEGIN
  UPDATE report_summary
    SET item_count = item_count - 1,
        last_updated = datetime('now')
    WHERE report_id = OLD.report_id;
END;

-- 4. Full refresh when triggers are insufficient
DELETE FROM report_summary;
INSERT INTO report_summary (report_id, category, item_count, last_updated)
  SELECT report_id, category, COUNT(*), datetime('now')
  FROM items GROUP BY report_id, category;
```

**Tradeoffs:**
- Trigger-maintained: always current, adds overhead to every write on the source table
- Scheduled refresh: stale between refreshes, no write overhead
- Choose triggers for small-to-medium tables; scheduled refresh for large aggregation tables

Source: [SQLite Triggers as Materialized Views](https://madflex.de/SQLite-triggers-as-replacement-for-a-materialized-view/)

### EAV (Entity-Attribute-Value) Pattern

**What it is:** Three columns -- `entity_id`, `attribute_name`, `value` -- allowing flexible attributes per entity.

```sql
CREATE TABLE product_attributes (
    entity_id  INTEGER REFERENCES products(product_id),
    attribute  TEXT NOT NULL,
    value      TEXT,
    PRIMARY KEY (entity_id, attribute)
);
```

**When to use:** Product catalogs with hundreds of optional attributes, clinical records with thousands of possible fields, or any domain where the set of attributes is not known at schema design time.

**Why it often fails:**
- Every query retrieving multiple attributes requires self-joins or pivot operations
- Filtering is slow because `value` is always TEXT (no type enforcement)
- No foreign key constraints on values
- Query complexity grows multiplicatively with each attribute

**Modern alternative for SQLite:** Use typed columns for core fields and JSON for variable attributes (requires SQLite 3.38.0+ for `->>` operator):

```sql
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    price      REAL NOT NULL,
    attributes TEXT DEFAULT '{}'  -- JSON
);

-- Query with JSON:
SELECT product_id, name, attributes ->> '$.color' AS color
FROM products
WHERE attributes ->> '$.color' = 'red';

-- Index on JSON field:
CREATE INDEX ix_products_color ON products(attributes ->> '$.color');
```

Sources:
- [Database Design Patterns Every Developer Should Know](https://www.bytebase.com/blog/database-design-patterns/)
- [Universal Database Design Patterns](https://www.red-gate.com/blog/database-design-patterns/)

### Single-Table Inheritance

All subtypes stored in one table with a `type` discriminator column. Subtype-specific columns are NULL for rows of other types.

```sql
CREATE TABLE vehicles (
    vehicle_id    INTEGER PRIMARY KEY,
    vehicle_type  TEXT NOT NULL CHECK (vehicle_type IN ('car', 'truck', 'motorcycle')),
    make          TEXT NOT NULL,
    model         TEXT NOT NULL,
    -- car-specific
    num_doors     INTEGER,
    -- truck-specific
    payload_tons  REAL,
    -- motorcycle-specific
    engine_cc     INTEGER
);
```

**When to use:** Few subtypes (2-4), subtypes share most columns, and you query across all types frequently. Simple to implement, single-table scans, no joins needed.

**When to avoid:** Many subtypes, subtypes have few shared columns (table becomes mostly NULL), or you need strict NOT NULL constraints on subtype-specific fields.

**SQLite-specific consideration:** Without STRICT mode, SQLite will happily store any type in any column, so the CHECK constraint on `vehicle_type` is your main safety net. Consider STRICT tables (SQLite 3.37.0+) for type enforcement.

### Adjacency Lists and Tree Hierarchies

Three primary patterns for hierarchical data:

#### Adjacency List (simplest)

```sql
CREATE TABLE categories (
    category_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    parent_id   INTEGER REFERENCES categories(category_id)
);
```

Simple to implement. Finding immediate children: `WHERE parent_id = ?`. Finding all descendants requires recursive CTEs (SQLite 3.8.3+):

```sql
WITH RECURSIVE descendants AS (
    SELECT category_id, name, parent_id FROM categories WHERE category_id = ?
    UNION ALL
    SELECT c.category_id, c.name, c.parent_id
    FROM categories c
    JOIN descendants d ON c.parent_id = d.category_id
)
SELECT * FROM descendants;
```

**Trade-offs:** Minimal storage, simple writes, but recursive reads.

#### Closure Table (best for read-heavy hierarchies)

```sql
CREATE TABLE category_closure (
    ancestor_id   INTEGER NOT NULL REFERENCES categories(category_id),
    descendant_id INTEGER NOT NULL REFERENCES categories(category_id),
    depth         INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (ancestor_id, descendant_id)
);
```

Every path in the hierarchy is stored as a row. Efficient queries without recursion:

```sql
-- All descendants of node 1:
SELECT descendant_id FROM category_closure WHERE ancestor_id = 1;

-- All ancestors of node 4:
SELECT ancestor_id FROM category_closure WHERE descendant_id = 4;

-- Direct children only:
SELECT descendant_id FROM category_closure WHERE ancestor_id = 1 AND depth = 1;
```

**Trade-offs:** Excellent read performance (indexed flat queries, no recursion), but O(n^2) worst-case storage and complex insert/delete maintenance.

**SQLite-specific:** SQLite has a `transitive_closure` extension that auto-maintains the closure table from an adjacency list.

#### Nested Sets (best for static hierarchies)

```sql
CREATE TABLE categories (
    category_id    INTEGER PRIMARY KEY,
    name           TEXT NOT NULL,
    left_boundary  INTEGER NOT NULL,
    right_boundary INTEGER NOT NULL
);

-- All descendants of node with left=1, right=10:
SELECT * FROM categories
WHERE left_boundary > 1 AND right_boundary < 10;
```

**Trade-offs:** Excellent read performance without recursion, low storage, but adding/deleting/moving nodes requires renumbering boundaries -- expensive for frequently-modified trees.

#### Decision Table

| Pattern | Read Performance | Write Complexity | Storage | Best For |
|---------|-----------------|-----------------|---------|----------|
| Adjacency List | Moderate (recursive) | Simple | Minimal | Dynamic trees with few depth queries |
| Closure Table | Excellent | Moderate | High | Read-heavy, deep hierarchies |
| Nested Sets | Excellent | High (renumbering) | Low | Static/rarely-modified hierarchies |

Sources:
- [Mastering SQL Trees: Adjacency Lists to Nested Sets and Closure Tables](https://teddysmith.io/sql-trees/)
- [Querying Tree Structures in SQLite](https://charlesleifer.com/blog/querying-tree-structures-in-sqlite-using-python-and-the-transitive-closure-extension/)
- [Hierarchical Data in SQL: The Ultimate Guide](https://www.databasestar.com/hierarchical-data-sql/)

---

# Part II: Performance and Tuning

## 7. Indexes

### B-Tree Architecture

SQLite stores all data in B-trees (specifically B+ trees). Each table is a B-tree keyed by rowid; each index is a separate B-tree keyed by the indexed columns with rowid appended. A lookup in a B-tree is O(log N), versus O(N) for a full table scan.

When a query uses an index, SQLite performs two binary searches: one on the index B-tree to find the rowid, then one on the table B-tree to retrieve the row. This is why covering indexes matter -- they eliminate the second lookup.

### Single-Column Indexes

```sql
CREATE INDEX idx_fruit ON fruitsforsale(fruit);
```

Reduces lookup from O(N) to O(log N). Still requires two binary searches (index + table).

### Multi-Column Indexes

```sql
CREATE INDEX idx_fruit_state ON fruitsforsale(fruit, state);
```

Rows are ordered by first column, with subsequent columns as tie-breakers. The query planner can use a multi-column index for any left-prefix of the indexed columns.

**Column ordering rules:**
- Equality columns (`=`, `IN`, `IS`) go first
- The rightmost used column can use inequalities (`<`, `>`, `<=`, `>=`, `BETWEEN`)
- No gaps allowed -- if columns are (a, b, c), you cannot use a and c without b
- Columns to the right of an inequality constraint are not used for indexing

```sql
-- Given index on (a, b, c):
WHERE a = 1 AND b = 2 AND c > 3   -- uses all 3 columns
WHERE a = 1 AND b > 2             -- uses a and b
WHERE a = 1                        -- uses only a
WHERE b = 2                        -- CANNOT use this index (no left-prefix)
```

**Rule of thumb:** "Your database schema should never contain two indices where one index is a prefix of the other." If you have an index on (a, b, c), you do not need a separate index on (a) or (a, b).

Source: [SQLite Query Planning](https://sqlite.org/queryplanner.html)

### Covering Indexes

A covering index includes all columns needed by a query, eliminating the table lookup entirely. This cuts the number of binary searches in half, roughly doubling query speed.

```sql
-- Query needs fruit, state, and price
SELECT price FROM fruitsforsale WHERE fruit = 'Orange' AND state = 'CA';

-- Covering index: includes the output column (price)
CREATE INDEX idx_fruit_state_price ON fruitsforsale(fruit, state, price);
```

EXPLAIN QUERY PLAN shows `USING COVERING INDEX` when this optimization applies:

```
QUERY PLAN
`--SEARCH fruitsforsale USING COVERING INDEX idx_fruit_state_price (fruit=? AND state=?)
```

Source: [SQLite Query Planning](https://sqlite.org/queryplanner.html)

### Partial Indexes

Index only a subset of rows by adding a WHERE clause. Reduces index size, speeds up writes, and can enforce conditional uniqueness.

```sql
-- Only index non-NULL values (useful when most rows are NULL)
CREATE INDEX idx_parent_po ON purchaseorder(parent_po)
  WHERE parent_po IS NOT NULL;

-- Enforce "only one team leader per team"
CREATE UNIQUE INDEX idx_team_leader ON person(team_id)
  WHERE is_team_leader;
```

**Query planner usage rules:**
- The partial index WHERE clause terms must appear (exactly or by implication) in the query WHERE clause
- `IS NOT NULL` in the index is satisfied by any comparison operator (`=`, `<`, `>`, `<>`, `IN`, `LIKE`, `GLOB`) on that column
- Expression matching is literal -- `b=6` matches `6=b` but NOT `b=3+3`

```sql
CREATE INDEX idx_active ON orders(customer_id) WHERE status = 'active';

-- Uses the partial index:
SELECT * FROM orders WHERE customer_id = 42 AND status = 'active';

-- Does NOT use the partial index (status term missing):
SELECT * FROM orders WHERE customer_id = 42;
```

Available since SQLite 3.8.0. Databases with partial indexes are unreadable by older versions.

Source: [SQLite Partial Indexes](https://www.sqlite.org/partialindex.html)

### Expression Indexes

Index the result of an expression rather than a raw column value.

```sql
CREATE INDEX idx_upper_last ON employees(UPPER(last_name));
CREATE INDEX idx_abs_amount ON account_change(acct_no, abs(amt));
CREATE INDEX idx_length_company ON customers(LENGTH(company));
```

**Critical constraint: exact expression matching.** The query planner does not do algebra. The expression in the query must match the index definition exactly:

```sql
-- Given: CREATE INDEX idx_xy ON t(x + y);
WHERE x + y > 10   -- USES the index
WHERE y + x > 10   -- does NOT use the index (different operand order)
```

**Restrictions:**
- Only deterministic functions allowed (no `random()`, `sqlite_version()`)
- Can only reference columns from the indexed table
- No subqueries
- Only usable in CREATE INDEX (not UNIQUE or PRIMARY KEY constraints)

Available since SQLite 3.9.0.

Source: [SQLite Indexes on Expressions](https://sqlite.org/expridx.html)

### Generated Columns + JSON Indexing

Generated columns (3.31.0+) let you extract values from JSON and index them at B-tree speed:

```sql
CREATE TABLE events (
  id INTEGER PRIMARY KEY,
  data TEXT  -- JSON blob
);

-- Virtual generated columns (computed on read, no storage cost)
ALTER TABLE events ADD COLUMN event_type TEXT
  GENERATED ALWAYS AS (json_extract(data, '$.type')) VIRTUAL;

ALTER TABLE events ADD COLUMN event_date TEXT
  GENERATED ALWAYS AS (json_extract(data, '$.date')) VIRTUAL;

-- Index the generated columns
CREATE INDEX idx_event_type ON events(event_type);
CREATE INDEX idx_event_date ON events(event_date);

-- Now this query uses B-tree index speed:
SELECT * FROM events WHERE event_type = 'click';
```

**VIRTUAL vs STORED:**
- VIRTUAL: computed on read, no disk space, can be added with ALTER TABLE
- STORED: computed on write, uses disk space, cannot be added with ALTER TABLE
- Use STORED when reads vastly outnumber writes; VIRTUAL otherwise

Source: [SQLite Generated Columns](https://sqlite.org/gencol.html)

### EXPLAIN QUERY PLAN

The essential tool for understanding index usage.

```sql
EXPLAIN QUERY PLAN SELECT * FROM orders WHERE customer_id = 42;
```

**Key output terms:**
- `SCAN table` -- full table scan (bad for large tables)
- `SEARCH table USING INDEX idx (col=?)` -- index lookup (good)
- `SEARCH table USING COVERING INDEX idx (col=?)` -- no table lookup needed (best)
- `USE TEMP B-TREE FOR ORDER BY` -- sorting required (index could eliminate this)
- `CORRELATED SCALAR SUBQUERY` -- runs once per outer row (expensive)
- `MULTI-INDEX OR` -- separate index lookups combined for OR conditions
- `AUTOMATIC INDEX` -- SQLite created a temporary index (permanent index would help)

```sql
-- Enabling automatic EXPLAIN QUERY PLAN in the CLI:
.eqp on
-- Now every query automatically shows its plan before results
```

Source: [SQLite EXPLAIN QUERY PLAN](https://www.sqlite.org/eqp.html)

### Over-Indexing Pitfalls

Every index must be maintained on every INSERT, UPDATE, and DELETE. The number of indexes on a table is the dominant factor for insert performance.

**Guidance:**
- Before creating an index, ask: "Will queries WHERE, JOIN, or ORDER BY this column?"
- Remove indexes that EXPLAIN QUERY PLAN never references
- Never have two indexes where one is a prefix of the other
- Run `PRAGMA optimize` periodically so the query planner has current statistics
- Monitor with: `SELECT * FROM sqlite_stat1;` (populated by ANALYZE)

**Benchmark reference:** With secondary indexes present, insert performance may reduce by up to 5x compared to a table with no secondary indexes.

Sources: [Use The Index, Luke - Insert](https://use-the-index-luke.com/sql/dml/insert), [Common Indexing Mistakes](https://www.slingacademy.com/article/common-mistakes-in-indexing-and-how-to-avoid-them-in-sqlite/)

---

## 8. Triggers

### Syntax

```sql
CREATE [TEMP | TEMPORARY] TRIGGER [IF NOT EXISTS] trigger_name
    {BEFORE | AFTER | INSTEAD OF} {DELETE | INSERT | UPDATE [OF column_name, ...]}
    ON table_name
    [FOR EACH ROW]
    [WHEN expression]
BEGIN
    -- one or more statements
END;
```

### Trigger Types

| Type | Works On | When It Fires |
|---|---|---|
| `BEFORE` | Tables only | Before the row modification |
| `AFTER` | Tables only | After the row modification |
| `INSTEAD OF` | Views only | Replaces the triggering operation entirely |

SQLite supports only `FOR EACH ROW` triggers (not `FOR EACH STATEMENT` like PostgreSQL).

### NEW and OLD References

| Event | `NEW.column` | `OLD.column` |
|---|---|---|
| INSERT | Available | Not available |
| UPDATE | Available (new values) | Available (old values) |
| DELETE | Not available | Available |

### Common Use Cases

#### 1. Audit Trail

```sql
CREATE TABLE audit_log (
    audit_log_id INTEGER PRIMARY KEY,
    table_name   TEXT NOT NULL,
    record_id    INTEGER NOT NULL,
    operation    TEXT NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    old_values   TEXT,  -- JSON of old row
    new_values   TEXT,  -- JSON of new row
    change_date  TEXT NOT NULL DEFAULT (datetime('now'))
);

-- After INSERT: log the new row
CREATE TRIGGER tr_documents_after_insert_audit
AFTER INSERT ON documents
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, record_id, operation, new_values)
    VALUES (
        'documents',
        NEW.document_id,
        'INSERT',
        json_object('title', NEW.title, 'body', NEW.body)
    );
END;

-- After UPDATE: log old and new values
CREATE TRIGGER tr_documents_after_update_audit
AFTER UPDATE ON documents
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, record_id, operation, old_values, new_values)
    VALUES (
        'documents',
        NEW.document_id,
        'UPDATE',
        json_object('title', OLD.title, 'body', OLD.body),
        json_object('title', NEW.title, 'body', NEW.body)
    );
END;

-- Before DELETE: log the deleted row
CREATE TRIGGER tr_documents_before_delete_audit
BEFORE DELETE ON documents
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, record_id, operation, old_values)
    VALUES (
        'documents',
        OLD.document_id,
        'DELETE',
        json_object('title', OLD.title, 'body', OLD.body)
    );
END;
```

#### 2. Automatic Timestamp Updates

```sql
CREATE TRIGGER tr_documents_after_update_timestamp
AFTER UPDATE ON documents
FOR EACH ROW
WHEN NEW.modification_date = OLD.modification_date OR NEW.modification_date IS NULL
BEGIN
    UPDATE documents
    SET modification_date = datetime('now')
    WHERE document_id = NEW.document_id;
END;
```

The WHEN clause prevents infinite recursion -- the trigger only fires when the timestamp was not explicitly set by the UPDATE statement.

#### 3. Business Rule Validation

```sql
CREATE TRIGGER tr_sales_before_insert_validate
BEFORE INSERT ON sales
FOR EACH ROW
BEGIN
    SELECT CASE
        WHEN NEW.sale_price < NEW.purchase_price THEN
            RAISE(ABORT, 'Sale price must not be less than purchase price')
    END;
END;
```

The `RAISE()` function is trigger-specific and provides error handling:
- `RAISE(ROLLBACK, 'message')` -- rolls back the entire transaction
- `RAISE(ABORT, 'message')` -- aborts the current statement, undoes its changes, but preserves prior statements in the transaction
- `RAISE(FAIL, 'message')` -- fails the current statement but keeps changes already made by it
- `RAISE(IGNORE)` -- silently skips the rest of the trigger and the triggering statement

#### 4. Maintaining Denormalized Data

```sql
-- Keep a cached count in the parent table
CREATE TRIGGER tr_line_items_after_insert_count
AFTER INSERT ON line_items
FOR EACH ROW
BEGIN
    UPDATE orders
    SET item_count = (SELECT count(*) FROM line_items WHERE order_id = NEW.order_id)
    WHERE order_id = NEW.order_id;
END;

CREATE TRIGGER tr_line_items_after_delete_count
AFTER DELETE ON line_items
FOR EACH ROW
BEGIN
    UPDATE orders
    SET item_count = (SELECT count(*) FROM line_items WHERE order_id = OLD.order_id)
    WHERE order_id = OLD.order_id;
END;
```

#### 5. INSTEAD OF Triggers on Views

```sql
CREATE VIEW active_customers AS
    SELECT customer_id, customer_name, email
    FROM customers
    WHERE is_active = 1;

CREATE TRIGGER tr_active_customers_instead_of_update
INSTEAD OF UPDATE ON active_customers
FOR EACH ROW
BEGIN
    UPDATE customers
    SET customer_name = NEW.customer_name,
        email = NEW.email
    WHERE customer_id = NEW.customer_id;
END;

-- Now you can UPDATE the view directly:
UPDATE active_customers SET email = 'new@example.com' WHERE customer_id = 42;
```

### Performance Implications

**Overhead sources:**
- SQLite opens a **statement journal** for any statement that fires triggers, adding file I/O even for simple operations.
- Each trigger body is a separate program that gets compiled and executed per affected row.
- Triggers that perform additional writes (INSERT into audit table, UPDATE a counter) multiply the I/O.
- Using `PRAGMA temp_store = MEMORY` reduces statement journal overhead by keeping it in memory.

**Practical advice:**
- Prefer `AFTER` triggers over `BEFORE` triggers. BEFORE triggers have undefined behavior if they modify or delete the row being processed.
- Keep trigger logic simple -- complex business logic belongs in application code where it can be versioned, tested, and debugged.
- Triggers are invisible at the SQL level. Document them heavily. Developers debugging slow INSERTs may not realize triggers are firing.
- Audit triggers on high-write tables can become a bottleneck. Consider batched/async logging for high-throughput scenarios.
- Test empirically -- one trigger on a moderate-volume table is usually fine; dozens of triggers on hot tables compound overhead.

### Restrictions Within Trigger Bodies

1. Table names must be unqualified (no `schema.table` syntax)
2. Non-TEMP triggers can only reference tables in the same database
3. TEMP triggers can access any attached database
4. No `INSERT INTO table DEFAULT VALUES`
5. No `INDEXED BY` / `NOT INDEXED` clauses
6. No `ORDER BY` / `LIMIT` clauses
7. No CTEs directly (but CTEs work inside subselects)

### Sources

- [CREATE TRIGGER](https://www.sqlite.org/lang_createtrigger.html) -- official trigger docs, syntax, restrictions
- [Creating Audit Tables with SQLite Triggers (Medium)](https://medium.com/@dgramaciotti/creating-audit-tables-with-sqlite-and-sql-triggers-751f8e13cf73)
- [SQLite Triggers (sql-easy.com)](https://www.sql-easy.com/learn/sqlite-trigger/)
- [Measuring and Reducing CPU Usage in SQLite](https://sqlite.org/cpu.html) -- performance measurement
- [SQLite Optimizations for Ultra High Performance (PowerSync)](https://www.powersync.com/blog/sqlite-optimizations-for-ultra-high-performance)

---

## 9. WAL Mode and Journal Modes

### Journal Mode Comparison

| Mode | Mechanism | Concurrent Reads | Write Speed | Durability |
|------|-----------|-----------------|-------------|------------|
| DELETE (default) | Rollback journal, deleted after txn | Blocked during writes | Slow (2x write) | Full |
| TRUNCATE | Rollback journal, truncated (not deleted) | Blocked during writes | Slightly faster than DELETE | Full |
| PERSIST | Rollback journal header zeroed | Blocked during writes | Slightly faster than DELETE | Full |
| WAL | Write-ahead log | Yes, concurrent with writes | Fast (1x write, sequential) | Full with synchronous=FULL |
| MEMORY | Journal in RAM only | Blocked during writes | Fast | None (crash = corruption) |
| OFF | No journal | Blocked during writes | Fastest | None (crash = corruption) |

### WAL Mode Details

```sql
PRAGMA journal_mode = WAL;
```

**How it works:** Changes are appended to a separate WAL file instead of modifying the database directly. The original database file stays intact. A COMMIT is just appending a commit record to the WAL -- no fsync of the database file required.

**Concurrency model:**
- Unlimited simultaneous readers
- One writer at a time
- Readers do not block writers; writers do not block readers
- Each reader sees a consistent snapshot from when its transaction started

**Performance advantages:**
- Writes are sequential (append-only to WAL), not random I/O
- Fewer fsync() calls than rollback journal
- Per-transaction overhead drops from 30ms+ to <1ms (with synchronous=NORMAL)

**Limitations:**
- All processes must be on the same machine (shared memory requirement)
- Cannot change page_size after entering WAL mode
- Very large transactions (multi-GB) may perform worse than rollback mode
- Creates additional -wal and -shm files alongside the database

### Checkpointing

Checkpointing transfers WAL content back to the main database file. Types:

```sql
PRAGMA wal_checkpoint(PASSIVE);   -- Non-blocking, does what it can
PRAGMA wal_checkpoint(FULL);      -- Blocks new writers until complete
PRAGMA wal_checkpoint(RESTART);   -- Blocks writers, resets WAL to beginning
PRAGMA wal_checkpoint(TRUNCATE);  -- Blocks writers, truncates WAL to zero bytes
```

**Automatic checkpointing:** By default, SQLite checkpoints when the WAL reaches 1000 pages.

```sql
-- Increase threshold for better write throughput (at cost of slower reads):
PRAGMA wal_autocheckpoint = 2000;

-- Disable automatic checkpointing (manual control only):
PRAGMA wal_autocheckpoint = 0;
```

**WAL growth prevention:** Three causes of unbounded WAL growth:
1. Automatic checkpointing disabled without manual replacement
2. Checkpoint starvation -- long-running readers prevent checkpoint from completing
3. Very large write transactions that block checkpointing

```sql
-- Limit WAL file size on disk (bytes, reclaimed after checkpoint):
PRAGMA journal_size_limit = 6144000;  -- 6MB
```

### When to Use Each Mode

- **WAL:** Default choice for most applications. Use when you have concurrent readers, need good write performance, and all access is from the same machine.
- **DELETE:** Use for maximum compatibility, network file systems, or when WAL limitations apply.
- **TRUNCATE:** Marginal speed improvement over DELETE on some filesystems.
- **OFF/MEMORY:** Only for ephemeral/rebuildable data where crash safety does not matter.

Sources: [SQLite WAL Documentation](https://sqlite.org/wal.html), [Fly.io SQLite WAL Internals](https://fly.io/blog/sqlite-internals-wal/), [SQLite Performance Tuning (phiresky)](https://phiresky.github.io/blog/2020/sqlite-performance-tuning/)

---

## 10. Transaction Management

### Implicit vs Explicit Transactions

Every SQL statement in SQLite runs inside a transaction. Without an explicit BEGIN, each statement gets its own implicit transaction with automatic COMMIT. This means individual INSERT statements each pay the full fsync cost.

```sql
-- Slow: each INSERT is its own transaction with fsync
INSERT INTO t VALUES (1);  -- implicit BEGIN, COMMIT, fsync
INSERT INTO t VALUES (2);  -- implicit BEGIN, COMMIT, fsync
INSERT INTO t VALUES (3);  -- implicit BEGIN, COMMIT, fsync

-- Fast: one transaction, one fsync
BEGIN;
INSERT INTO t VALUES (1);
INSERT INTO t VALUES (2);
INSERT INTO t VALUES (3);
COMMIT;  -- single fsync
```

### Transaction Types

```sql
BEGIN;               -- same as BEGIN DEFERRED
BEGIN DEFERRED;      -- default: acquire locks lazily
BEGIN IMMEDIATE;     -- acquire write lock immediately
BEGIN EXCLUSIVE;     -- acquire exclusive lock immediately
```

**DEFERRED (default):**
- No lock acquired until first database access
- First SELECT acquires a read lock
- First write statement attempts to upgrade to write lock
- If upgrade fails (another writer active), returns SQLITE_BUSY immediately
- busy_timeout does NOT apply to lock upgrades in DEFERRED mode

**IMMEDIATE:**
- Acquires write lock at BEGIN time
- If another writer is active, waits up to busy_timeout, then SQLITE_BUSY
- Benchmarks show approximately 2x better performance than DEFERRED for write-heavy workloads
- Recommended for any transaction that will write

**EXCLUSIVE:**
- Same as IMMEDIATE in WAL mode
- In rollback journal mode, also blocks readers
- Use only in rollback mode when you need total isolation

**Recommendation:** Use `BEGIN IMMEDIATE` for any transaction that will write. It fails fast at BEGIN time instead of failing mid-transaction after work has been done.

Sources: [SQLite Transaction Documentation](https://sqlite.org/lang_transaction.html), [SQLite Transactions (reorchestrate)](https://reorchestrate.com/posts/sqlite-transactions/)

### Batch Insert Performance

Transaction wrapping is the single most impactful optimization for inserts.

**Benchmarks (100M rows, Rust):**

| Technique | Time | Notes |
|-----------|------|-------|
| Naive single-row inserts (autocommit) | Minutes per million | Each row = separate transaction + fsync |
| Transaction-wrapped batches + prepared stmts | 34.3 seconds (100M rows) | Single connection |
| Threaded producer + single writer | 32.37 seconds (100M rows) | 4 worker threads, 1 writer |
| In-memory database | 29 seconds (100M rows) | ~2 seconds of disk I/O overhead |

**Impact of transaction wrapping by language (100M rows):**

| Language | Batched | Naive |
|----------|---------|-------|
| Rust (prepared + batched) | 34 seconds | N/A |
| PyPy (batched) | 2.5 minutes | N/A |
| CPython (batched) | 8.5 minutes | 10 minutes |

Source: [Fast SQLite Inserts (avi.im)](https://avi.im/blag/2021/fast-sqlite-inserts/)

**Impact by optimization technique:**

| Technique | Impact |
|-----------|--------|
| WAL + synchronous=NORMAL | Per-transaction overhead from 30ms+ to <1ms |
| Transaction wrapping | Write throughput 2-20x improvement |
| Prepared statements | Per-statement throughput up to 1.5x |
| Background WAL checkpoints | Eliminates occasional 30-100ms fsync spikes |

Source: [PowerSync SQLite Optimizations](https://www.powersync.com/blog/sqlite-optimizations-for-ultra-high-performance)

**PRAGMA settings for bulk loading (maximum speed, reduced safety):**

```sql
PRAGMA journal_mode = OFF;
PRAGMA synchronous = 0;
PRAGMA cache_size = 1000000;
PRAGMA locking_mode = EXCLUSIVE;
PRAGMA temp_store = MEMORY;
```

**Safe bulk loading (maintains crash safety):**

```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -64000;  -- 64MB
PRAGMA temp_store = MEMORY;

BEGIN IMMEDIATE;
-- ... batch of inserts (100-10000 rows per transaction) ...
COMMIT;
```

**Optimal batch size:** 100-1,000 rows per transaction for general use. For bulk loading, larger batches (10K-100K) are better.

### Transaction Size Considerations

- Keep transactions as short as possible to minimize lock contention
- Very large transactions (multi-GB) can cause WAL growth and performance degradation
- In WAL mode, long-running read transactions prevent checkpointing, causing WAL bloat
- There is no hard limit on transaction size, but practical limits come from disk space for the WAL/journal

---

## 11. Query Optimization

### Reading EXPLAIN QUERY PLAN

```sql
EXPLAIN QUERY PLAN
SELECT o.id, c.name
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.status = 'active'
ORDER BY o.created_date DESC;
```

What to look for:
- `SCAN` = full table scan (often bad, check if index would help)
- `SEARCH` = index-assisted lookup (good)
- `COVERING INDEX` = all data from index, no table lookup (best)
- `USE TEMP B-TREE FOR ORDER BY` = sort step needed (index on ORDER BY columns could eliminate)
- `AUTOMATIC INDEX` = SQLite created a temporary index (permanent index would help)
- `CORRELATED SCALAR SUBQUERY` = runs for each outer row (rewrite as JOIN if possible)
- `MULTI-INDEX OR` = separate index lookups combined for OR conditions
- `CO-ROUTINE` = subquery evaluated in parallel, yielding single rows on demand
- `MATERIALIZE` = subquery result stored in temporary table

### Common Anti-Patterns

**1. Correlated subqueries instead of JOINs:**

```sql
-- BAD: subquery runs once per order row
SELECT o.id,
  (SELECT name FROM customers WHERE id = o.customer_id) AS customer_name
FROM orders o;

-- GOOD: single join operation
SELECT o.id, c.name
FROM orders o
JOIN customers c ON c.id = o.customer_id;
```

**2. UNION when UNION ALL suffices:**

```sql
-- BAD: sorts and deduplicates (unnecessary when sets are disjoint)
SELECT id, name FROM active_users
UNION
SELECT id, name FROM archived_users;

-- GOOD: just concatenates result sets
SELECT id, name FROM active_users
UNION ALL
SELECT id, name FROM archived_users;
```

UNION requires sorting all rows and comparing for duplicates. UNION ALL simply appends. For large datasets, UNION ALL can be 60%+ faster. Use UNION only when you genuinely need deduplication.

**3. Functions on indexed columns in WHERE:**

```sql
-- BAD: cannot use index on created_date
WHERE date(created_date) = '2024-01-15'

-- GOOD: preserves index usage
WHERE created_date >= '2024-01-15' AND created_date < '2024-01-16'

-- ALTERNATIVE: create an expression index
CREATE INDEX idx_date ON orders(date(created_date));
```

**4. OR conditions without supporting indexes:**

```sql
-- Potentially slow: needs indexes on BOTH columns
WHERE status = 'active' OR priority > 5

-- SQLite handles this with MULTI-INDEX OR if both columns are indexed
-- Without indexes on both, falls back to full table scan
```

**5. SELECT * when you only need specific columns:**

```sql
-- BAD: fetches all columns, prevents covering index optimization
SELECT * FROM orders WHERE status = 'active';

-- GOOD: may use covering index
SELECT id, customer_id FROM orders WHERE status = 'active';
```

**6. NOT IN with subqueries (NULL hazard):**

```sql
-- DANGEROUS: if subquery returns any NULL, entire NOT IN is NULL (returns no rows)
SELECT * FROM orders WHERE customer_id NOT IN (SELECT id FROM inactive_customers);

-- SAFE: NOT EXISTS handles NULLs correctly
SELECT * FROM orders o
WHERE NOT EXISTS (SELECT 1 FROM inactive_customers ic WHERE ic.id = o.customer_id);
```

### Query Planner Optimizations to Know

**Automatic index creation:** When no persistent index helps and the lookup will run more than log(N) times during a statement, SQLite creates a temporary index. Construction cost is O(N log N). Watch for `AUTOMATIC INDEX` in EXPLAIN QUERY PLAN -- it means a permanent index would help.

**Subquery flattening:** SQLite attempts to merge subqueries in the FROM clause into the outer query, enabling index usage on the underlying tables instead of scanning a temporary result.

**Skip-scan:** When the leftmost index column has few distinct values but a later column is constrained, SQLite can skip-scan the index. Requires ANALYZE to have been run (needs statistics showing 18+ duplicates in the leftmost column).

**MIN/MAX optimization:** `SELECT MIN(col) FROM t` or `SELECT MAX(col) FROM t` on the leftmost column of an index executes as a single index lookup, not a full scan.

**Predicate push-down:** WHERE conditions from outer queries are pushed into subqueries to reduce the size of intermediate results.

**Constant propagation:** `WHERE a = b AND b = 5` implies `a = 5`, enabling SQLite to use an index on `a`.

**OR-to-IN conversion:** Multiple equality conditions on the same column separated by OR are rewritten as IN operators for index use: `WHERE x=1 OR x=2 OR x=3` becomes `WHERE x IN (1,2,3)`.

**LIKE/GLOB optimization:** When the pattern does not start with a wildcard and the column has BINARY collation, SQLite converts `LIKE 'prefix%'` to a range scan: `col >= 'prefix' AND col < 'prefiy'`.

### Running ANALYZE

```sql
-- Collect statistics for all tables:
ANALYZE;

-- Collect for a specific table:
ANALYZE orders;

-- Limit analysis time (rows examined per index):
PRAGMA analysis_limit = 1000;
ANALYZE;

-- View collected statistics:
SELECT * FROM sqlite_stat1;
```

Statistics are stored in `sqlite_stat1` (and optionally `sqlite_stat4`). The query planner uses these to estimate row counts and choose between competing index strategies. Without ANALYZE, the planner uses rough heuristics that may choose suboptimal plans.

Sources: [SQLite EXPLAIN QUERY PLAN](https://www.sqlite.org/eqp.html), [SQLite Query Optimizer](https://sqlite.org/optoverview.html), [Deep Dive into SQLite Query Optimizer](https://micahkepe.com/blog/sqlite-query-optimizer/)

---

## 12. PRAGMA Settings for Production

### Recommended Production Configuration

Run these on every new connection:

```sql
-- Use write-ahead logging for concurrency and write speed
PRAGMA journal_mode = WAL;

-- NORMAL is safe in WAL mode; only checkpoints need fsync
PRAGMA synchronous = NORMAL;

-- 64MB page cache (negative value = kilobytes)
PRAGMA cache_size = -64000;

-- Memory-mapped I/O: let OS manage page caching (256MB)
PRAGMA mmap_size = 268435456;

-- Keep temp tables and indexes in memory
PRAGMA temp_store = MEMORY;

-- Wait 5 seconds on lock contention before returning SQLITE_BUSY
PRAGMA busy_timeout = 5000;

-- Enforce foreign key constraints (off by default)
PRAGMA foreign_keys = ON;
```

### PRAGMA Reference

**journal_mode = WAL**
- Enables concurrent readers + single writer
- Sequential writes, fewer fsync calls
- Persists across connections (set once, stored in database header)
- Cannot use on network file systems

**synchronous = NORMAL**
- Default is FULL (fsync every commit)
- NORMAL: only checkpoint fsyncs; safe in WAL mode against corruption
- Risk: committed transaction could roll back on power loss (not application crash)
- OFF: no fsync at all; corruption risk on any crash

**cache_size = -64000**
- Negative value = kilobytes; positive value = pages
- Default is -2000 (approximately 2MB)
- More cache = fewer disk reads, but may duplicate OS page cache
- Session-only; resets on each new connection

**mmap_size = 268435456**
- Enables memory-mapped I/O (fewer syscalls)
- Set to 0 to disable, or to expected database size
- On 64-bit systems, can set very large (e.g., 30GB) -- reserves virtual address space, not physical RAM
- Beneficial for read-heavy workloads

**temp_store = MEMORY**
- Temp tables, indexes, and intermediate results stored in RAM
- Faster than disk-based temp storage
- Value 2 = memory; value 1 = file; value 0 = compile-time default

**busy_timeout = 5000**
- Milliseconds to wait on lock contention before returning SQLITE_BUSY
- Without this, SQLITE_BUSY returns immediately
- Essential for any multi-connection setup

**foreign_keys = ON**
- Off by default (historical reasons)
- Negligible performance impact
- Must be set per-connection (not stored in database)

### For New Databases (SQLite 3.37.0+)

```sql
CREATE TABLE items (
    item_id INTEGER PRIMARY KEY,
    name    TEXT NOT NULL,
    price   REAL NOT NULL
) STRICT;
```

STRICT enforces column types at insert/update time, raising `SQLITE_CONSTRAINT_DATATYPE` on type mismatches.

### Maintenance PRAGMAs

```sql
-- For long-lived connections, run on open:
PRAGMA optimize = 0x10002;

-- Run periodically (hourly for long-lived connections):
PRAGMA optimize;

-- Run before closing short-lived connections:
PRAGMA optimize;
PRAGMA wal_checkpoint(PASSIVE);

-- Limit ANALYZE time (set before PRAGMA optimize):
PRAGMA analysis_limit = 400;

-- Limit WAL file size on disk:
PRAGMA journal_size_limit = 6144000;  -- 6MB
```

**PRAGMA optimize** collects statistics for tables where the query planner would have benefited from better data. The `0x10002` mask checks all tables and limits runtime. Run it:
- On connection open for long-lived apps (with `0x10002`)
- Before connection close for short-lived apps (plain `optimize`)
- After schema changes

**auto_vacuum:**

```sql
-- Must be set before creating any tables:
PRAGMA auto_vacuum = INCREMENTAL;

-- Then periodically:
PRAGMA incremental_vacuum;
```

- NONE (default): unused pages stay allocated; requires manual VACUUM
- FULL: automatic but can worsen fragmentation
- INCREMENTAL: you control when space is reclaimed

**VACUUM** rewrites the entire database. Avoid for databases over 100MB due to the time and temporary disk space required.

### Configuration Summary Table

| PRAGMA | Production Value | Default | Impact |
|--------|-----------------|---------|--------|
| journal_mode | WAL | DELETE | Concurrency, write speed |
| synchronous | NORMAL | FULL | Write speed (2-50x) |
| cache_size | -64000 | -2000 | Read speed for large DBs |
| mmap_size | 268435456 | 0 | Read speed, fewer syscalls |
| temp_store | MEMORY | DEFAULT | Temp operation speed |
| busy_timeout | 5000 | 0 | Prevents immediate BUSY errors |
| foreign_keys | ON | OFF | Data integrity |
| wal_autocheckpoint | 1000 | 1000 | WAL size vs checkpoint frequency |
| journal_size_limit | 6144000 | -1 (unlimited) | Disk space control |
| analysis_limit | 400 | 0 (unlimited) | ANALYZE/optimize runtime |

### Quick Reference: Connection Setup Template

```sql
-- Run on every new connection:
PRAGMA journal_mode = WAL;          -- persists in DB, but safe to re-set
PRAGMA synchronous = NORMAL;
PRAGMA cache_size = -64000;
PRAGMA mmap_size = 268435456;
PRAGMA temp_store = MEMORY;
PRAGMA busy_timeout = 5000;
PRAGMA foreign_keys = ON;
PRAGMA optimize = 0x10002;          -- for long-lived connections

-- Run periodically (hourly for long-lived connections):
PRAGMA optimize;

-- Run before closing short-lived connections:
PRAGMA optimize;
PRAGMA wal_checkpoint(PASSIVE);
```

Sources: [SQLite PRAGMA Documentation](https://sqlite.org/pragma.html), [SQLite PRAGMA Cheatsheet](https://cj.rs/blog/sqlite-pragma-cheatsheet-for-performance-and-consistency/), [SQLite Performance Tuning (phiresky)](https://phiresky.github.io/blog/2020/sqlite-performance-tuning/), [High Performance SQLite Recommended PRAGMAs](https://highperformancesqlite.com/articles/sqlite-recommended-pragmas), [SQLite Optimizations For Ultra High-Performance](https://www.powersync.com/blog/sqlite-optimizations-for-ultra-high-performance), [Write-Ahead Logging](https://sqlite.org/wal.html)

---

# Part III: Operations and Maintenance

## 13. Migration and Versioning

### Schema Versioning with PRAGMA user_version

Use SQLite's built-in `PRAGMA user_version` integer to track schema version. It is simpler and more efficient than maintaining a version table -- the integer is available immediately without searching the database file.

```sql
-- Read current version
PRAGMA user_version;

-- Set version after migration
PRAGMA user_version = 3;
```

**Migration file structure:**

```
migrations/
  0001_initial_schema.sql
  0002_add_indexes.sql
  0003_add_fts.sql
```

Each migration file ends with `PRAGMA user_version = N;`

**Python implementation:**

```python
current = db.execute('PRAGMA user_version').fetchone()[0]
for migration_file in sorted(migration_files):
    version = int(migration_file.split('_')[0])
    if version > current:
        db.executescript(open(migration_file).read())
```

**Shell script implementation:**

```bash
current_version=$(sqlite3 "$DB" "PRAGMA user_version;")
for migration in migrations/*.sql; do
    version=$(basename "$migration" | cut -d_ -f1 | sed 's/^0*//')
    if [ "$version" -gt "$current_version" ]; then
        sqlite3 "$DB" < "$migration"
    fi
done
```

**Best practices:**
- Keep migration SQL scripts in version control
- Wrap each migration in a transaction (BEGIN/COMMIT)
- Design scripts to be safely re-runnable (idempotent where possible)
- Number migrations sequentially to ensure ordering
- Include both the DDL changes and the `PRAGMA user_version = N` in each file

Sources:
- [SQLite DB Migrations with PRAGMA user_version](https://levlaz.org/sqlite-db-migrations-with-pragma-user_version/)
- [SQLite's user_version pragma for schema versioning](https://gluer.org/blog/sqlites-user_version-pragma-for-schema-versioning/)

### ALTER TABLE Limitations

SQLite's ALTER TABLE is severely limited. It supports:
- `ALTER TABLE x RENAME TO y`
- `ALTER TABLE x ADD COLUMN y` (column must have a default value or allow NULL)
- `ALTER TABLE x RENAME COLUMN old TO new` (SQLite 3.25.0+)
- `ALTER TABLE x DROP COLUMN y` (SQLite 3.35.0+)

It does **not** support changing column types, adding/removing constraints, changing default values, or reordering columns.

**The 12-step migration procedure** for structural changes:

```sql
-- Example: changing a column type and adding a constraint
BEGIN TRANSACTION;
PRAGMA foreign_keys = OFF;

CREATE TABLE items_new (
    item_id INTEGER PRIMARY KEY,
    name    TEXT NOT NULL,
    price   REAL NOT NULL CHECK (price >= 0)  -- was TEXT, now REAL with constraint
);

INSERT INTO items_new (item_id, name, price)
SELECT item_id, name, CAST(price AS REAL) FROM items;

DROP TABLE items;
ALTER TABLE items_new RENAME TO items;

PRAGMA foreign_key_check;  -- verify no broken references
PRAGMA foreign_keys = ON;
COMMIT;
```

**Critical:** The sequence (create new, copy, drop old, rename new) is important to avoid breaking foreign key references.

**Declarative migration approach:** Compare the actual database against a "pristine" in-memory database created from the schema definition. The migrator queries `sqlite_schema` to identify differences and applies changes automatically. Works well for adding new tables, modifying indexes, and adding nullable columns. Requires manual SQL for data migrations.

Sources:
- [Simple declarative schema migration for SQLite](https://david.rothlis.net/declarative-schema-migration-for-sqlite/)
- [SQLite ALTER TABLE documentation](https://sqlite.org/lang_altertable.html)

---

## 14. Backup and Recovery

### Backup Methods

#### .backup Command (built-in, recommended default)

```
sqlite3 mydb.db ".backup backup.db"
```

Creates a page-by-page replica. Other connections can write during the backup, but those changes will not appear in the backup.

#### VACUUM INTO (backup + optimize)

```sql
VACUUM INTO '/path/to/backup.db';
```

Creates a vacuumed (compacted) copy. More CPU-intensive than `.backup` but produces a smaller, defragmented file.

#### Online Backup API (programmatic, incremental)

The C API copies pages incrementally without locking the source for the entire duration:

- `sqlite3_backup_init()` -- creates backup object
- `sqlite3_backup_step(N)` -- copies N pages per iteration
- `sqlite3_backup_finish()` -- releases resources

The source is read-locked only while pages are being read. Progress monitored with `sqlite3_backup_remaining()` and `sqlite3_backup_pagecount()`.

#### Litestream (continuous replication to S3)

Streams WAL changes to S3-compatible storage. Provides point-in-time recovery. Requires additional software.

#### Copy-on-Write (filesystem-level)

On Btrfs/XFS, `cp --reflink=always` within a deferred transaction creates near-instant backups (~2ms for 440MB+).

### Comparison

| Method | Durability | Space | Restore Speed | Complexity |
|--------|-----------|-------|---------------|-----------|
| `.backup` | High | Moderate | Very Fast | Low |
| `VACUUM INTO` | High | Small (compacted) | Very Fast | Low |
| Online Backup API | High | Moderate | Very Fast | Medium |
| Litestream | Very High | Low (incremental) | Moderate | Medium |
| CoW `cp` | High | Very Low | Very Fast | Low |
| `.dump` (SQL) | High | Large | Slow | Low |

### Critical WAL Consideration

When restoring a backup, **always delete any existing `*-wal` and `*-shm` files** at the destination before copying. A stale/mismatched WAL file can corrupt the restored database.

### Corruption Prevention

SQLite is highly resistant to corruption -- partial transactions from crashes are automatically rolled back on next access. Corruption can occur from:

1. **Rogue process overwrites** -- other processes writing directly to the database file
2. **Broken file locking** -- especially on network filesystems (NFS, CIFS). Never use SQLite on network storage.
3. **Sync failures** -- disk drives reporting writes complete before reaching persistent media. Use `PRAGMA synchronous = FULL` (or `NORMAL` with WAL mode).
4. **Deleting journal files** -- removing `*-journal` or `*-wal` files prevents crash recovery
5. **Memory corruption** -- stray pointers, especially with memory-mapped I/O
6. **Mismatched database + journal** -- renaming or moving the database without its journal

**Integrity checking:**

```sql
PRAGMA integrity_check;       -- thorough check (slow on large DBs)
PRAGMA quick_check;           -- faster, less thorough
```

**Recovery from corruption:**

```sql
-- SQLite 3.29.0+
.recover
-- Or manually:
.mode insert
.output recovery.sql
.dump
.output stdout
```

**Configuration rules to prevent corruption:**
- Never use `PRAGMA synchronous = OFF`
- Never use `PRAGMA journal_mode = OFF` or `MEMORY`
- Never modify `PRAGMA schema_version` with active connections
- Use `PRAGMA writable_schema = ON` with extreme caution

Sources:
- [SQLite Backup API](https://sqlite.org/backup.html)
- [How To Corrupt An SQLite Database File](https://sqlite.org/howtocorrupt.html)
- [Recovering Data From A Corrupt SQLite Database](https://sqlite.org/recovery.html)
- [Backup strategies for SQLite in production](https://oldmoe.blog/2024/04/30/backup-strategies-for-sqlite-in-production/)

---

## 15. Date and Time Handling

### Storage Format Options

SQLite has no native datetime type. Three storage approaches:

#### TEXT -- ISO-8601 strings (recommended default)

```sql
CREATE TABLE events (
    event_id   INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);
-- Stores: '2026-04-03 14:30:00'
```

**Pros:** Human-readable, built-in function support (`datetime()`, `date()`, `time()`), supports timezone info, millisecond precision.
**Cons:** 20-27 bytes per timestamp (vs 8 for INTEGER), string comparison slightly slower.

#### INTEGER -- Unix timestamps

```sql
CREATE TABLE events (
    event_id   INTEGER PRIMARY KEY,
    name       TEXT NOT NULL,
    created_at INTEGER NOT NULL DEFAULT (unixepoch('now'))
);
-- Stores: 1775403000
```

**Pros:** 8 bytes, fastest comparisons, simplest arithmetic, timezone-neutral (always UTC), efficient range queries.
**Cons:** Not human-readable, requires conversion for display. **Caution:** Timestamps from the first 63 days of 1970 may be misinterpreted as Julian day numbers by the `auto` modifier.

#### REAL -- Julian day numbers

```sql
SELECT julianday('now');  -- 2460737.10417
```

**Pros:** Most precise for day-based calculations.
**Cons:** Rarely used, unfamiliar to most developers.

### Core Date Functions

```sql
-- Current UTC timestamp
SELECT datetime('now');                          -- '2026-04-03 14:30:00'
SELECT unixepoch('now');                         -- 1775403000

-- Convert between formats
SELECT datetime(1775403000, 'unixepoch');        -- INTEGER to TEXT
SELECT strftime('%s', '2026-04-03 14:30:00');    -- TEXT to INTEGER

-- Date arithmetic
SELECT datetime('now', '+7 days');               -- 7 days from now
SELECT datetime('now', '-1 month');              -- 1 month ago
SELECT date('now', 'start of month', '+1 month', '-1 day');  -- end of current month

-- Day-based calculations
SELECT julianday('now') - julianday('2026-01-01') AS days_elapsed;

-- Validation (returns NULL for invalid dates)
SELECT datetime('2026-13-45');  -- NULL
```

### Critical Best Practices

**Always store UTC.** Converting to local time is a display concern:

```sql
-- Store in UTC
INSERT INTO events (name, created_at) VALUES ('test', datetime('now'));

-- Display in local time
SELECT datetime(created_at, 'localtime') AS local_time FROM events;
```

**Never mix formats in the same column.** Pick TEXT or INTEGER and use it consistently. Mixed formats break comparisons and indexing.

**Be consistent with precision.** If you store milliseconds in some rows and seconds in others, comparisons break.

**Month arithmetic can surprise:**

```sql
SELECT date('2026-01-31', '+1 month');  -- result may vary
```

### Choosing a Format

| Criterion | TEXT (ISO-8601) | INTEGER (Unix) |
|-----------|----------------|----------------|
| Human readability | Excellent | Poor |
| Storage size | 20-27 bytes | 8 bytes |
| Comparison speed | Good | Best |
| Date arithmetic | Via functions | Simple addition |
| Range queries | Good | Best |
| Timezone clarity | Can include offset | Always UTC |
| Function support | Native | Requires 'unixepoch' modifier |

**For most applications:** TEXT ISO-8601 is the safer default -- easier to debug and works naturally with SQLite's date functions.

**For high-volume logging or time-series data:** INTEGER unix timestamps for storage efficiency and comparison speed.

Sources:
- [Handling Timestamps in SQLite](https://blog.sqlite.ai/handling-timestamps-in-sqlite)
- [SQLite Date & Time Functions](https://sqlite.org/lang_datefunc.html)
- [SQLite Date & Time Tutorial](https://www.sqlitetutorial.net/sqlite-date/)

---

## 16. Blob and Large Data

### The 100KB Threshold

SQLite's own benchmarks established a clear guideline:

- **Under 100KB:** Reading BLOBs from the database is **faster** than from separate files. At 10KB, SQLite is 35% faster than filesystem I/O and uses 20% less disk space.
- **Over 100KB:** Reading from separate files is faster. The crossover varies by hardware (between 100KB and 1MB depending on page size).

### When to Store BLOBs in the Database

**Do store internally:**
- Small files under 100KB (thumbnails, icons, small config files)
- When ACID guarantees on the data matter
- When atomic updates of both metadata and content are needed

**Store externally (file path in DB):**
- Files over 100KB (videos, PDFs, large images)
- When files are served directly via a web server
- When files are accessed independently of their metadata

**Hybrid approach:** Store small BLOBs internally, large BLOBs externally with the path in the database.

### Page Size Optimization

```sql
-- Set before creating the database (cannot change after)
PRAGMA page_size = 8192;   -- or 16384 for large BLOB I/O
```

A page size of 8192 or 16384 gives the best performance for large BLOB I/O. The default 4096 is fine for non-BLOB workloads.

### Maximum BLOB Size

- Default maximum: 1,000,000,000 bytes (1 GB)
- Absolute maximum: 2,147,483,647 bytes (~2 GB)
- Configurable via `SQLITE_MAX_LENGTH` compile-time option

### ZEROBLOB for Incremental Writing

`zeroblob()` allocates space filled with zeros, then you overwrite in chunks via the blob I/O API:

```sql
INSERT INTO files (name, content) VALUES ('large.bin', zeroblob(1048576));
-- Then use sqlite3_blob_open() / sqlite3_blob_write() to write in chunks
```

This avoids loading the entire BLOB into memory at once.

### ACID vs Performance Trade-off

Storing files in the database gives you ACID properties (atomic updates, crash recovery). External files lose ACID but gain direct filesystem access, CDN compatibility, no database size bloat, and independent backup.

Sources:
- [Internal Versus External BLOBs](https://sqlite.org/intern-v-extern-blob.html)
- [35% Faster Than The Filesystem](https://sqlite.org/fasterthanfs.html)
- [Implementation Limits For SQLite](https://sqlite.org/limits.html)

---

## 17. Security

### SQL Injection Prevention

**The rule:** Use prepared statements with bind parameters. Do not try to play games attempting to outthink your attacker. Prepared statements separate SQL code from data -- the database engine treats bound parameters as data, never as executable code.

**In Python:**

```python
# DANGEROUS -- string concatenation
cursor.execute(f"SELECT * FROM users WHERE name = '{user_input}'")

# SAFE -- parameterized query
cursor.execute("SELECT * FROM users WHERE name = ?", (user_input,))
```

**In shell scripts:** The `sqlite3` CLI does not natively support parameterized queries. This is the biggest security risk for shell script database access.

**Option 1 -- .parameter bind (sqlite3 3.38.0+):**

```bash
sqlite3 "$DB" <<EOF
.parameter set :name '$sanitized_name'
SELECT * FROM users WHERE name = :name;
EOF
```

**Option 2 -- Validate and escape in the shell script:**

```bash
# Minimal escaping: double all single quotes
safe_input="${user_input//\'/\'\'}"
sqlite3 "$DB" "SELECT * FROM users WHERE name = '${safe_input}'"
```

This is inferior to prepared statements but may be the only option in pure shell.

**Option 3 -- Delegate to a helper program:**

Write a small Python/Go/Rust wrapper that accepts arguments and uses proper parameterized queries. The shell script calls the wrapper. This is the most secure approach for shell-based architectures.

**Option 4 -- sqlite3_mprintf format specifiers (`%q`, `%Q`, `%w`):**

In C code, `%q` doubles single quotes, `%Q` wraps in quotes and handles NULL, `%w` is for identifiers.

### Database File Permissions

SQLite delegates all access control to the operating system. It does not implement GRANT/REVOKE or user authentication.

```bash
# Database file: owner read/write only
chmod 600 mydb.db

# Set umask before creating databases
umask 077
sqlite3 newdb.db "CREATE TABLE test (id INTEGER PRIMARY KEY);"
```

**Important considerations:**
- The database file, WAL file, and journal file must all have consistent permissions
- The directory containing the database must be writable (SQLite creates temporary files)
- On WAL mode, read-only connections still need write permission to the WAL and SHM files
- Never make database files world-readable if they contain sensitive data

### Additional Security Measures

- **Principle of least privilege:** Run database-accessing processes under a restricted user account
- **Encryption at rest:** SQLite has no built-in encryption. Use SQLCipher or SEE (SQLite Encryption Extension) for encrypted databases
- **Input validation:** Beyond SQL injection, validate that inputs conform to expected formats before they reach the query layer
- **LIKE clause escaping:** User input in LIKE patterns needs the ESCAPE clause:

```sql
SELECT * FROM items WHERE name LIKE '%' || :search || '%' ESCAPE '\';
```

Sources:
- [SQLite Forum: Characters to escape to prevent SQL Injection](https://sqlite.org/forum/info/53ec3a55cb9fc1d3)
- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- [Basic Security Practices for SQLite](https://dev.to/stephenc222/basic-security-practices-for-sqlite-safeguarding-your-data-23lh)

---

## 18. Testing with SQLite

### In-Memory Databases

The foundation of SQLite testing is `:memory:`, which creates a RAM-only database destroyed when the connection closes.

```python
import sqlite3
conn = sqlite3.connect(':memory:')
conn.executescript(open('schema.sql').read())
# ... run tests ...
conn.close()  # database destroyed
```

**Key advantages:** Speed (no disk I/O), isolation (each connection independent), simplicity (no files to manage), reproducibility (known blank state).

### Test Isolation Strategies

#### Strategy 1 -- Fresh Database Per Test (strongest isolation)

```python
import pytest, sqlite3

@pytest.fixture
def db():
    conn = sqlite3.connect(':memory:')
    conn.executescript(open('schema.sql').read())
    yield conn
    conn.close()

def test_insert_user(db):
    db.execute("INSERT INTO users (name) VALUES (?)", ("Alice",))
    assert db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 1

def test_empty_users(db):
    # Guaranteed empty -- no cross-test contamination
    assert db.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0
```

**Pros:** Perfect isolation, simple to reason about.
**Cons:** Schema setup cost per test (usually negligible).

#### Strategy 2 -- Transaction Rollback (faster for large schemas)

```python
@pytest.fixture
def db(shared_db):
    shared_db.execute("BEGIN")
    yield shared_db
    shared_db.execute("ROLLBACK")
```

Schema created once. Tests must not COMMIT; nested transactions need SAVEPOINTs.

#### Strategy 3 -- Template Database with Backup API

```python
@pytest.fixture(scope='session')
def template_db():
    conn = sqlite3.connect(':memory:')
    conn.executescript(open('schema.sql').read())
    conn.executescript(open('test_seeds.sql').read())
    return conn

@pytest.fixture
def db(template_db):
    conn = sqlite3.connect(':memory:')
    template_db.backup(conn)
    return conn
```

Combines pre-populated data with per-test isolation using SQLite's backup API.

### Migration Testing

```python
def test_migrations_apply_cleanly():
    conn = sqlite3.connect(':memory:')
    for migration_file in sorted(glob.glob('migrations/*.sql')):
        conn.executescript(open(migration_file).read())
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    assert ('users',) in tables

def test_migration_idempotency():
    conn = sqlite3.connect(':memory:')
    for _ in range(2):
        for migration_file in sorted(glob.glob('migrations/*.sql')):
            conn.executescript(open(migration_file).read())
```

### Cross-Database Compatibility Caveats

When SQLite substitutes for a production database in tests:

| Behavior | SQLite | PostgreSQL | MySQL |
|----------|--------|------------|-------|
| String comparison | Case-sensitive | Case-sensitive (default) | Case-insensitive |
| Type enforcement | Flexible (unless STRICT) | Strict | Strict |
| Boolean type | INTEGER 0/1 | Native BOOLEAN | TINYINT |
| LIKE | Case-sensitive for ASCII | Case-insensitive (ILIKE) | Case-insensitive |

Test against the actual production database for integration tests. Use SQLite only for unit tests where dialect differences do not matter.

### Test Performance Tips

- Use function-scoped fixtures (one database per test) for isolation
- Use module/session-scoped fixtures for performance if tests are read-only
- Use `PRAGMA journal_mode = OFF` and `PRAGMA synchronous = OFF` in test databases for maximum speed (safe because test data is disposable)
- Pre-populate fixtures with representative data rather than building it per-test

Sources:
- [How to Use SQLite in Testing](https://oneuptime.com/blog/post/2026-02-02-sqlite-testing/view)
- [How SQLite Is Tested](https://sqlite.org/testing.html)
- [How to test SQLite in-memory databases using pytest](https://woteq.com/how-to-test-sqlite-in-memory-databases-using-pytest/)

---

## 19. Common Anti-Patterns

### Storing CSV/Lists in Columns

```sql
-- ANTI-PATTERN:
CREATE TABLE posts (
    post_id INTEGER PRIMARY KEY,
    tags    TEXT  -- 'python,sqlite,database'
);
```

Cannot index individual values, cannot join, cannot enforce referential integrity, requires LIKE '%tag%' (full table scan with false positives).

**Fix -- junction table:**

```sql
CREATE TABLE tags (
    tag_id INTEGER PRIMARY KEY,
    name   TEXT NOT NULL UNIQUE
);

CREATE TABLE post_tags (
    post_id INTEGER REFERENCES posts(post_id),
    tag_id  INTEGER REFERENCES tags(tag_id),
    PRIMARY KEY (post_id, tag_id)
);
```

Or for simpler cases, use JSON:

```sql
CREATE TABLE posts (
    post_id INTEGER PRIMARY KEY,
    tags    TEXT DEFAULT '[]'  -- JSON array
);

SELECT * FROM posts, json_each(posts.tags)
WHERE json_each.value = 'python';
```

### Not Using Transactions for Batch Operations

```sql
-- ANTI-PATTERN: each statement is an implicit transaction with fsync
INSERT INTO data VALUES (1, 'a');
INSERT INTO data VALUES (2, 'b');
-- ... 10,000 more

-- FIX: explicit transaction (2-20x faster)
BEGIN TRANSACTION;
INSERT INTO data VALUES (1, 'a');
INSERT INTO data VALUES (2, 'b');
-- ... 10,000 more
COMMIT;
```

The filesystem sync happens once at COMMIT instead of per-statement. Even read performance improves (fewer lock operations).

### Ignoring EXPLAIN QUERY PLAN

```sql
-- Always check query execution:
EXPLAIN QUERY PLAN SELECT * FROM users WHERE email = 'test@example.com';
-- SCAN users              <-- full table scan! needs an index
-- SEARCH users USING INDEX idx_email (email=?)  <-- good
```

Adopt a repeatable workflow: capture the query, EXPLAIN it, test with the fix, deploy.

### Using SQLite as a Message Queue

SQLite allows only one writer at a time. Queue patterns require frequent writes (enqueue) and deletes (dequeue) from competing processes, creating lock contention. Use a purpose-built queue instead.

**Exception:** A single-process queue (one producer, one consumer in the same application) works fine because there is no write contention.

### SELECT * in Production

Returns unnecessary columns, prevents index-only scans, breaks when schema changes, wastes memory. List only the columns you need.

### Functions on Indexed Columns

```sql
-- ANTI-PATTERN: cannot use index
SELECT * FROM users WHERE LOWER(email) = 'test@example.com';

-- FIX: expression index (SQLite 3.9.0+)
CREATE INDEX ix_users_email_lower ON users(LOWER(email));
```

### N+1 Query Pattern

```sql
-- ANTI-PATTERN:
SELECT customer_id FROM customers;
-- Then for each: SELECT COUNT(*) FROM orders WHERE customer_id = ?;

-- FIX:
SELECT c.customer_id, c.name, COUNT(o.order_id) AS order_count
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
GROUP BY c.customer_id, c.name;
```

**SQLite caveat:** Because SQLite is embedded (no network hop), the N+1 penalty is smaller than with client/server databases. Sometimes N+1 with simple indexed lookups is actually faster than a complex join. Benchmark both.

### Long Transactions

In SQLite, an open write transaction blocks all other writers. A transaction held for 30 seconds blocks all writes for 30 seconds. Keep transactions short. Use `PRAGMA busy_timeout` for transient contention:

```sql
PRAGMA busy_timeout = 5000;  -- wait up to 5 seconds for locks
```

### SQLite vs Other Databases

#### What SQLite Excels At

SQLite "competes with `fopen()`" -- it is an embedded database engine, not a client/server system.

**Zero administration:** No server to install, configure, monitor, or restart. The database is a single file.

**Zero latency:** No network round-trip. Queries execute in-process.

**Ideal use cases:**
- **Application file format:** Desktop apps, mobile apps, Electron apps
- **Embedded/IoT devices:** Cellphones, cameras, drones, medical devices
- **Websites with < 100K hits/day**
- **Data analysis:** Import CSV/JSON, query with SQL, share the single file
- **Local caching and temporary databases**
- **Data transfer format:** Richer than CSV, simpler than a server

#### Where SQLite Falls Short

- **Write concurrency:** Unlimited readers but only one writer at a time
- **Network access:** Cannot connect from a different machine
- **Very large datasets:** Performance degrades above a few GB without careful tuning
- **Advanced SQL features:** No RIGHT JOIN, no FULL OUTER JOIN, limited ALTER TABLE, no stored procedures
- **Enterprise features:** No replication, no role-based access control, no audit logging

#### Decision Checklist

| Question | If Yes |
|----------|--------|
| Data on a separate server from the app? | Use client/server |
| Many concurrent writers needed? | Use client/server |
| Data exceeds a few GB? | Consider client/server |
| Multiple application servers sharing data? | Use client/server |
| Need user authentication at DB level? | Use client/server |
| Otherwise? | SQLite is likely the best choice |

#### Modern Performance Reality (2025-2026)

Recent benchmarks challenge traditional assumptions:
- A Rails app with 10 Puma workers achieved **2,730 write requests/second** using SQLite
- This supports ~1 million daily active users performing 35 writes/day each
- Key insight: match database connections to application workers, not excessive connection pools
- WAL mode with `busy_timeout` eliminates most "database locked" errors

#### Migration Away from SQLite

When migrating to PostgreSQL/MySQL:
- Tools like `sqlite3-to-mysql` handle encoding, type conversion, and bulk transfer
- SQLite's flexible typing may have allowed data that stricter databases reject -- validate data types first
- Date formats may need conversion (SQLite TEXT dates to native TIMESTAMP types)
- NULL handling differences may surface

Sources:
- [SQL Anti-Patterns and How to Fix Them](https://slicker.me/sql/antipatterns.htm)
- [SQLite Optimizations For Ultra High-Performance](https://www.powersync.com/blog/sqlite-optimizations-for-ultra-high-performance)
- [Database Design Patterns Every Developer Should Know](https://www.bytebase.com/blog/database-design-patterns/)
- [Appropriate Uses For SQLite](https://sqlite.org/whentouse.html)
- [Why you should probably be using SQLite](https://www.epicweb.dev/why-you-should-probably-be-using-sqlite)
- [SQLite vs MySQL vs PostgreSQL](https://www.digitalocean.com/community/tutorials/sqlite-vs-mysql-vs-postgresql-a-comparison-of-relational-database-management-systems)

---

# Part IV: Device-to-Server Sync

## 20. Schema Design for Sync

### 20.1 UUID vs Integer Primary Keys

**Why UUIDs are necessary for offline-first sync:**

Auto-incrementing integers are generated locally by each device. When two devices create records offline, their local databases produce identical IDs. On sync, these duplicates cause conflicts, data corruption, or sync failures. UUIDs solve this by enabling client-side ID generation without server coordination.

**SQLite-specific advantage:** Unlike MySQL or PostgreSQL where random UUIDs fragment the clustered B-tree index, SQLite uses the internal `rowid` as its clustered index. A TEXT UUID primary key creates a separate B-tree index, so UUID randomness does not cause the same page-split fragmentation problems.

**Recommended: UUIDv7 (time-ordered)**

UUIDv7 includes a timestamp prefix, making IDs roughly ordered by creation time. This preserves the insert-order performance benefits of integers while maintaining global uniqueness. UUIDv7 is supported natively in PostgreSQL 17+ via `uuid_generate_v7()`.

```sql
-- SQLite: sync-ready table with TEXT UUID primary key
CREATE TABLE tasks (
    id TEXT PRIMARY KEY NOT NULL,         -- UUIDv7, generated client-side
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TEXT NOT NULL,             -- ISO-8601 UTC
    updated_at TEXT NOT NULL,             -- ISO-8601 UTC
    version INTEGER NOT NULL DEFAULT 1,
    is_deleted INTEGER NOT NULL DEFAULT 0,
    last_synced_at TEXT                   -- NULL until first sync
);
```

```sql
-- PostgreSQL: corresponding server table
CREATE TABLE tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    version INTEGER NOT NULL DEFAULT 1,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    last_synced_at TIMESTAMPTZ
);
```

**Pitfalls to avoid:**
- Never use `INTEGER PRIMARY KEY AUTOINCREMENT` for synced tables -- IDs will collide across devices
- Never use `datetime('now')` as an ID substitute -- insufficient precision for uniqueness
- If using the sqlite-sync extension, use `cloudsync_uuid()` which generates UUIDv7 natively

**Sources:**
- [UUID vs Auto Increment for Primary Keys (Bytebase)](https://www.bytebase.com/blog/choose-primary-key-uuid-or-auto-increment/)
- [Primary Key Data Types (High Performance SQLite)](https://highperformancesqlite.com/watch/primary-key-data-types)
- [Android Room UUID Primary Key (CodeStudy)](https://www.codestudy.net/blog/using-uuid-for-primary-key-using-room-with-android/)

### 20.2 Timestamps for Change Tracking

Every synced table needs timestamps to detect what changed since the last sync.

**Required columns:**

| Column | Purpose | Format |
|--------|---------|--------|
| `created_at` | Record creation time | ISO-8601 UTC |
| `updated_at` | Last modification time | ISO-8601 UTC |
| `last_synced_at` | Last successful server sync | ISO-8601 UTC, NULL until synced |

**Detecting unsynced changes:**

```sql
-- Find all records that changed since last sync
SELECT * FROM tasks
WHERE last_synced_at IS NULL
   OR updated_at > last_synced_at;
```

**Automatic timestamp updates via triggers:**

```sql
CREATE TRIGGER tasks_update_timestamp
AFTER UPDATE ON tasks
FOR EACH ROW
WHEN NEW.updated_at = OLD.updated_at  -- prevent infinite recursion
BEGIN
    UPDATE tasks SET updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
    WHERE id = NEW.id;
END;
```

**Physical clocks vs logical clocks:**

Physical timestamps (`datetime('now')`) are simple but vulnerable to clock skew between devices. For systems where ordering correctness matters, consider:

- **Lamport timestamps:** Simple incrementing counter. Guarantees `e happened before f => L(e) < L(f)`, but the converse is not true. Low overhead but no concurrency detection.
- **Vector clocks:** Array of counters, one per device. Can distinguish "happened-before" from "concurrent" events. Space grows with O(n) where n = number of devices. Impractical for many-device scenarios.
- **Hybrid Logical Clocks (HLC):** Combine physical wall-clock time with a logical counter in a single 64-bit value. Remain close to wall-clock time while guaranteeing causal ordering. Strictly monotonic per-node. Self-stabilizing against NTP corrections. Recommended for most sync systems.

```
HLC timestamp = [48-bit physical time] + [16-bit logical counter]
```

**Sources:**
- [Handling Timestamps in SQLite (sqlite.ai)](https://blog.sqlite.ai/handling-timestamps-in-sqlite)
- [Hybrid Logical Clocks (Sergei Turukin)](https://sergeiturukin.com/2017/06/26/hybrid-logical-clocks.html)
- [Vector Clocks (Wikipedia)](https://en.wikipedia.org/wiki/Vector_clock)
- [Evolving Clock Sync in Distributed Databases (YugabyteDB)](https://www.yugabyte.com/blog/evolving-clock-sync-for-distributed-databases/)

### 20.3 Soft Deletes vs Hard Deletes (Tombstone Patterns)

Hard deleting a record on one device makes it impossible to propagate that deletion to other devices or the server -- there is no record left to sync. Sync systems require soft deletes.

**Simple soft delete:**

```sql
-- Mark as deleted instead of DELETE FROM
UPDATE tasks
SET is_deleted = 1,
    updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
WHERE id = ?;
```

```sql
-- All normal queries exclude deleted records
SELECT * FROM tasks WHERE is_deleted = 0;
```

```sql
-- Sync queries include deleted records
SELECT * FROM tasks
WHERE last_synced_at IS NULL OR updated_at > last_synced_at;
```

**Index for filtering deleted records:**

```sql
CREATE INDEX idx_tasks_is_deleted ON tasks(is_deleted);
```

**Tombstone table pattern (alternative):**

Instead of a flag column, move deleted records to a separate tombstone table. This keeps the live table clean and fast while preserving deletion history for sync.

```sql
CREATE TABLE tasks_tombstones (
    id TEXT PRIMARY KEY NOT NULL,
    table_name TEXT NOT NULL,
    deleted_at TEXT NOT NULL,
    synced INTEGER NOT NULL DEFAULT 0
);

-- Trigger to capture deletes
CREATE TRIGGER tasks_soft_delete
BEFORE DELETE ON tasks
BEGIN
    INSERT INTO tasks_tombstones (id, table_name, deleted_at)
    VALUES (OLD.id, 'tasks', strftime('%Y-%m-%dT%H:%M:%fZ', 'now'));
END;
```

**Purging tombstones:**

Tombstones accumulate forever unless pruned. Only purge after confirming all devices have synced past the deletion:

```sql
-- Purge tombstones older than 90 days that have been synced
DELETE FROM tasks_tombstones
WHERE synced = 1
  AND deleted_at < strftime('%Y-%m-%dT%H:%M:%fZ', 'now', '-90 days');
```

**Pitfalls:**
- Never hard-delete records that other devices might still reference
- Always include `is_deleted` in indexes used by sync queries
- Plan a tombstone purge strategy from the start -- unbounded tombstones degrade performance

**Sources:**
- [Soft Deletes (Brent Ozar)](https://www.brentozar.com/archive/2020/02/what-are-soft-deletes-and-how-are-they-implemented/)
- [Tombstone Design Pattern (James Tharpe)](https://www.jamestharpe.com/tombstone-pattern/)
- [Soft Deletes (DoltHub)](https://www.dolthub.com/blog/2022-11-03-soft-deletes/)

### 20.4 Schema Compatibility Between SQLite and Server DB

SQLite's dynamic type system differs fundamentally from PostgreSQL/MySQL's rigid type system. Design schemas for compatibility.

**Key differences:**

| Concept | SQLite | PostgreSQL |
|---------|--------|------------|
| Type enforcement | Column affinity (recommended, not enforced) | Strict type enforcement |
| Boolean | INTEGER (0/1) | BOOLEAN (true/false) |
| Date/Time | TEXT (ISO-8601), INTEGER (unix), or REAL (julian) | TIMESTAMP, TIMESTAMPTZ, DATE, TIME |
| UUID | TEXT | UUID (native type) |
| JSON | TEXT with json1 functions | JSONB (binary, indexed) |
| BLOB | BLOB | BYTEA |
| Auto-increment | INTEGER PRIMARY KEY (alias for rowid) | SERIAL / GENERATED ALWAYS AS IDENTITY |

**Compatibility rules for sync schemas:**

1. Store booleans as INTEGER 0/1 in SQLite; map to BOOLEAN on server
2. Store dates as ISO-8601 TEXT in SQLite; map to TIMESTAMPTZ on server
3. Store UUIDs as TEXT in SQLite; map to UUID type on server
4. Store JSON as TEXT in SQLite; map to JSONB on server
5. Always use UTC for all timestamps on both sides
6. Define column constraints identically on both sides (NOT NULL, DEFAULT, CHECK)

**Sources:**
- [SQLite Data Types (w3resource)](https://www.w3resource.com/sqlite/sqlite-data-types.php)
- [SQLite Datatypes (sqlite.org)](https://www.sqlite.org/datatype3.html)
- [SQLAlchemy Type Hierarchy](https://docs.sqlalchemy.org/en/20/core/type_basics.html)

### 20.5 Version Columns for Optimistic Concurrency

A `version` column enables detecting concurrent modifications without timestamps.

**How it works:**

1. Client reads record with `version = 3`
2. Client modifies record locally, increments to `version = 4`
3. Client sends update to server: `UPDATE tasks SET ... WHERE id = ? AND version = 3`
4. If another client already incremented to `version = 4`, the WHERE clause matches zero rows
5. Server responds with conflict; client must reconcile

```sql
-- SQLite: version-based update
UPDATE tasks
SET title = ?,
    status = ?,
    version = version + 1,
    updated_at = strftime('%Y-%m-%dT%H:%M:%fZ', 'now')
WHERE id = ? AND version = ?;
-- Check changes() == 1; if 0, conflict occurred
```

**SQLite-specific rowversion simulation:**

SQLite lacks a native auto-updating rowversion type. Simulate with a trigger:

```sql
-- Randomized version token (alternative to incrementing integer)
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    row_version BLOB NOT NULL DEFAULT (randomblob(8)),
    -- ... other columns
);

CREATE TRIGGER tasks_rowversion
AFTER UPDATE ON tasks
BEGIN
    UPDATE tasks SET row_version = randomblob(8) WHERE id = NEW.id;
END;
```

**Best practice:** Use both `version` (integer) and `updated_at` (timestamp). The version integer is authoritative for conflict detection; the timestamp is useful for debugging and human-readable ordering.

**Sources:**
- [Optimistic Concurrency (ServiceStack)](https://docs.servicestack.net/ormlite/optimistic-concurrency)
- [Handling Concurrency Conflicts (EF Core)](https://learn.microsoft.com/en-us/ef/core/saving/concurrency)
- [Entity Framework Core: SQLite Concurrency Checks](https://elanderson.net/2018/12/entity-framework-core-sqlite-concurrency-checks/)

---

## 21. Conflict Resolution

### 21.1 Last-Write-Wins (LWW)

The simplest strategy: the most recent modification (by timestamp or version) overwrites older versions.

**Implementation:**

```sql
-- Server-side: accept the newer version
INSERT INTO tasks (id, title, status, updated_at, version)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT (id) DO UPDATE SET
    title = EXCLUDED.title,
    status = EXCLUDED.status,
    updated_at = EXCLUDED.updated_at,
    version = EXCLUDED.version
WHERE EXCLUDED.updated_at > tasks.updated_at;
```

**When to use:** Low-conflict domains (analytics, logging, single-user-per-record apps), settings/preferences, any case where the latest value is "correct enough."

**When NOT to use:** Collaborative editing, inventory management, financial records, or anywhere losing a concurrent edit is unacceptable.

**Pitfalls:**
- Clock skew between devices can cause the "wrong" write to win
- Silent data loss -- the user whose write is overwritten gets no notification
- Use HLC timestamps instead of wall-clock time to mitigate ordering issues

### 21.2 Server-Wins vs Client-Wins Policies

**Server-wins:** The server's current value always takes precedence. Client changes are silently discarded on conflict.

```python
# Server-wins: ignore client version if server is newer
if server_record.version >= client_record.version:
    return server_record  # client change discarded
else:
    apply(client_record)
```

**Client-wins:** The client's value always overwrites the server. Equivalent to LWW where client timestamp always "wins."

```python
# Client-wins: always accept client change
apply(client_record)
```

**When to use:**
- Server-wins: settings pushed from admin, read-only sync (server is source of truth)
- Client-wins: draft documents, personal notes, any data "owned" by one user

**Turso's conflict strategies demonstrate the spectrum:**
- `FAIL_ON_CONFLICT` -- reject sync, require explicit handling
- `DISCARD_LOCAL` -- server-wins
- `REBASE_LOCAL` -- replay local changes on top of server state (like git rebase)
- `MANUAL_RESOLUTION` -- callback with both versions for custom logic

### 21.3 Field-Level Merge

Instead of replacing entire rows, merge individual columns. If Device A changes `title` and Device B changes `status`, both changes are preserved.

**Implementation:**

```python
def field_level_merge(client_record, server_record, base_record):
    """Merge at column level using three-way comparison."""
    merged = {}
    for field in all_fields:
        client_changed = client_record[field] != base_record[field]
        server_changed = server_record[field] != base_record[field]
        
        if client_changed and not server_changed:
            merged[field] = client_record[field]    # client wins this field
        elif server_changed and not client_changed:
            merged[field] = server_record[field]    # server wins this field
        elif client_changed and server_changed:
            if client_record[field] == server_record[field]:
                merged[field] = client_record[field]  # both agree
            else:
                # True conflict on this field -- apply policy
                merged[field] = resolve_field_conflict(
                    field, client_record, server_record
                )
        else:
            merged[field] = base_record[field]      # neither changed
    return merged
```

**cr-sqlite uses per-column CRDTs for this:** Each column is independently tracked with its own version, so conflicting edits to different columns on the same row merge automatically. Only same-column, same-row conflicts require LWW fallback.

**When to use:** Any application where concurrent users typically edit different fields of the same record (task trackers, CRMs, project management).

**Pitfalls:**
- Requires storing the "base" version (the last-synced state) to do three-way comparison
- Field-level merge can produce semantically invalid combinations (e.g., changing `quantity` and `unit_price` independently can produce wrong `total`)
- Consider which fields should merge independently vs which should be treated as an atomic group

### 21.4 Operational Transformation (OT)

OT transforms concurrent operations against each other so both can be applied in any order and converge to the same result. Used primarily for text and sequence editing.

**How it works:**
1. User A inserts "X" at position 5
2. User B inserts "Y" at position 3
3. Server receives both operations
4. Server transforms A's operation: since B inserted before position 5, A's position shifts to 6
5. Both clients apply the transformed operations, converging to the same document

**When to use:** Collaborative text editing (Google Docs uses OT), sequential data where position matters.

**When NOT to use:** Simple key-value record sync, CRUD apps, scenarios without a central server (OT requires a server for ordering).

**Trade-offs vs CRDTs:**
- OT is simpler for text editing with a central server
- CRDTs work peer-to-peer without a central server
- OT requires all operations to pass through the server
- CRDTs have higher metadata overhead but work offline indefinitely

**Sources:**
- [OT vs CRDT Comparison (thom.ee)](https://thom.ee/blog/crdt-vs-operational-transformation/)
- [Real-Time Collaboration OT vs CRDT (TinyMCE)](https://www.tiny.cloud/blog/real-time-collaboration-ot-vs-crdt/)
- [Why Fiberplane Uses OT (Fiberplane)](https://fiberplane.com/blog/why-we-at-fiberplane-use-operational-transformation-instead-of-crdt/)

### 21.5 CRDTs (Conflict-Free Replicated Data Types)

CRDTs are data structures designed to automatically converge across replicas without coordination. If no more updates are made, all replicas reach the same state -- guaranteed by mathematical properties.

**CRDT types relevant to SQLite sync:**

| Type | Behavior | Use Case |
|------|----------|----------|
| **LWW-Register** | Last write wins per field, using timestamp | Individual record fields |
| **G-Counter** | Grow-only counter, each replica tracks its own count | Page views, like counts |
| **PN-Counter** | Positive-negative counter (two G-Counters) | Inventory, resource pools |
| **G-Set** | Grow-only set (add only, no remove) | Event logs, tags |
| **OR-Set** | Observed-Remove set (add and remove, add-wins) | Shopping carts, selections |
| **LWW-Element-Set** | Add/remove with timestamps | Feature flags, preferences |
| **MV-Register** | Multi-value register (preserves all concurrent writes) | Conflict-aware fields |
| **RGA** | Replicated Growable Array | Collaborative text, lists |

**cr-sqlite CRDT usage:**

```sql
-- Load the extension
.load crsqlite

-- Create a normal table
CREATE TABLE tasks (
    id TEXT PRIMARY KEY NOT NULL,
    title TEXT,
    status TEXT
);

-- Convert to a conflict-free replicated relation (CRR)
SELECT crsql_as_crr('tasks');

-- Normal INSERT/UPDATE/DELETE operations work as usual
INSERT INTO tasks (id, title, status) VALUES ('task-1', 'Buy groceries', 'pending');
UPDATE tasks SET status = 'done' WHERE id = 'task-1';

-- Export changes since version X for sync
SELECT "table", "pk", "cid", "val", "col_version", "db_version",
       "site_id", "cl", "seq"
FROM crsql_changes
WHERE db_version > ?;

-- Import changes from another device
INSERT INTO crsql_changes
    ("table", "pk", "cid", "val", "col_version", "db_version",
     "site_id", "cl", "seq")
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);

-- Clean up before closing
SELECT crsql_finalize();
```

**Performance characteristics of cr-sqlite:**
- Inserts into CRR tables: approximately 2.5x slower than regular SQLite
- Reads: identical speed to standard SQLite
- Space overhead: additional metadata for version tracking per column

**When to use CRDTs:** Peer-to-peer sync, multi-device apps with extended offline periods, collaborative editing, any scenario where a central server cannot always be reached.

**When NOT to use CRDTs:** Simple client-server sync where the server is always authoritative, apps where business logic validation must happen before accepting writes.

**Sources:**
- [cr-sqlite (GitHub)](https://github.com/vlcn-io/cr-sqlite)
- [CRDT Dictionary (Ian Duncan)](https://www.iankduncan.com/engineering/2025-11-27-crdt-dictionary/)
- [CRDT Implementations (crdt.tech)](https://crdt.tech/implementations)
- [Conflict-Free Replicated Data Types (Wikipedia)](https://en.wikipedia.org/wiki/Conflict-free_replicated_data_type)

### 21.6 Conflict Queues for Manual Resolution

When automated resolution is insufficient, queue conflicts for human review.

**Conflict queue table:**

```sql
CREATE TABLE sync_conflicts (
    id TEXT PRIMARY KEY NOT NULL,
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    client_data TEXT NOT NULL,      -- JSON of client version
    server_data TEXT NOT NULL,      -- JSON of server version
    base_data TEXT,                 -- JSON of last-synced version (for 3-way merge)
    conflict_type TEXT NOT NULL,    -- 'update_update', 'update_delete', 'delete_update'
    detected_at TEXT NOT NULL,
    resolved_at TEXT,
    resolution TEXT,                -- 'client', 'server', 'merged', 'discarded'
    resolved_data TEXT              -- JSON of final version if merged
);

CREATE INDEX idx_conflicts_unresolved
ON sync_conflicts(resolved_at) WHERE resolved_at IS NULL;
```

**Conflict detection during sync:**

```python
def sync_record(client_record, server_record):
    if server_record.version == client_record.base_version:
        # No conflict -- server hasn't changed since client last synced
        apply_to_server(client_record)
    else:
        # Conflict -- both changed since last sync
        conflict = {
            "table_name": "tasks",
            "record_id": client_record.id,
            "client_data": json.dumps(client_record),
            "server_data": json.dumps(server_record),
            "conflict_type": "update_update",
            "detected_at": now_utc()
        }
        insert_conflict(conflict)
        # Optionally: apply server version as interim, flag for review
```

**When to use:** Medical records, legal documents, financial transactions, any domain where silent data loss is unacceptable and a human must choose the correct resolution.

---

## 22. Sync Protocols and Patterns

### 22.1 Full Sync vs Incremental/Delta Sync

**Full sync:** Transfer the entire dataset on every sync. Simple but expensive.

```sql
-- Full sync: client sends everything
SELECT * FROM tasks;

-- Server replaces all client data
DELETE FROM tasks;
INSERT INTO tasks SELECT * FROM incoming_data;
```

**Incremental (delta) sync:** Transfer only records that changed since the last sync.

```sql
-- Client tracks last successful sync timestamp
-- or last sync version number
SELECT * FROM tasks
WHERE updated_at > ?   -- last_sync_timestamp
ORDER BY updated_at ASC;
```

**Delta sync with version numbers (more reliable than timestamps):**

```sql
-- Server maintains a global sync version counter
-- Each change increments it
-- Client stores the last version it received

-- Client pull: "give me everything after version 42"
SELECT * FROM tasks WHERE sync_version > 42 ORDER BY sync_version ASC;

-- Client push: send changes with their local version
-- Server assigns sequential sync_version on acceptance
```

**Best practice:** Always use delta sync in production. Full sync only for initial bootstrap or recovery after corruption.

### 22.2 Change Tracking Approaches

**Approach 1: Flag columns on each table**

```sql
-- updated_at + last_synced_at comparison
SELECT * FROM tasks
WHERE last_synced_at IS NULL OR updated_at > last_synced_at;
```

Pros: Simple. Cons: Requires adding columns to every synced table.

**Approach 2: Change log table with triggers**

```sql
CREATE TABLE change_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    operation TEXT NOT NULL,  -- 'INSERT', 'UPDATE', 'DELETE'
    changed_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    synced INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_changelog_unsynced ON change_log(synced, changed_at);

-- INSERT trigger
CREATE TRIGGER tasks_after_insert
AFTER INSERT ON tasks
BEGIN
    INSERT INTO change_log (table_name, record_id, operation)
    VALUES ('tasks', NEW.id, 'INSERT');
END;

-- UPDATE trigger
CREATE TRIGGER tasks_after_update
AFTER UPDATE ON tasks
BEGIN
    INSERT INTO change_log (table_name, record_id, operation)
    VALUES ('tasks', NEW.id, 'UPDATE');
END;

-- DELETE trigger
CREATE TRIGGER tasks_after_delete
AFTER DELETE ON tasks
BEGIN
    INSERT INTO change_log (table_name, record_id, operation)
    VALUES ('tasks', OLD.id, 'DELETE');
END;
```

Pros: Centralized change tracking, captures operation type. Cons: Table grows continuously, needs periodic purging.

**Approach 3: SQLite Session Extension**

The SQLite Session Extension is a built-in mechanism for recording changes to rowid tables and packaging them as binary changesets.

```c
// Create a session monitoring all tables
sqlite3_session *pSession;
sqlite3session_create(db, "main", &pSession);
sqlite3session_attach(pSession, NULL);  // NULL = all tables

// ... application makes changes ...

// Generate a binary changeset
void *pChangeset;
int nChangeset;
sqlite3session_changeset(pSession, &nChangeset, &pChangeset);

// Apply changeset to another database
sqlite3changeset_apply(db2, nChangeset, pChangeset, NULL, conflict_handler, NULL);

// Clean up
sqlite3session_delete(pSession);
```

Changeset contents per operation:
- **INSERT:** Values for all columns of the new row
- **DELETE:** Primary key + original values for all columns
- **UPDATE:** Primary key + original values + new values for changed columns

Changeset vs patchset:
- **Changeset:** Full old + new values; enables complete conflict detection
- **Patchset:** Compact format; DELETE carries only PK, UPDATE carries only new values; limited conflict detection

Build requirement: compile SQLite with `-DSQLITE_ENABLE_SESSION -DSQLITE_ENABLE_PREUPDATE_HOOK`

**Sources:**
- [SQLite Session Extension (sqlite.org)](https://sqlite.org/sessionintro.html)
- [SQLiteChangesetSync (GitHub)](https://github.com/gerdemb/SQLiteChangesetSync)
- [sqlite3session changeset example (GitHub Gist)](https://gist.github.com/kroggen/8329210e5f52a0b8b60e9c7f98b059a7)

### 22.3 Push vs Pull vs Bidirectional Sync

**Pull sync (server to client):**
- Client periodically requests new data from server
- Server is source of truth
- Simple to implement; polling introduces latency
- Use for read-heavy apps (news, documentation, catalog data)

**Push sync (client to server):**
- Client sends local changes to server when connectivity returns
- Server validates and applies
- Use for write-heavy offline scenarios (field data collection, surveys)

**Bidirectional sync:**
- Both push and pull in a single sync cycle
- Most complex; requires conflict resolution
- Standard pattern for collaborative apps

**Recommended sync cycle for bidirectional:**

```
1. Push local changes to server
2. Server validates, resolves conflicts, returns results
3. Pull server changes (including changes from other devices)
4. Apply server changes to local database
5. Update last_synced_at / sync version
```

**Push-based optimization via "shoulder tap":**
Instead of polling, the server sends a lightweight notification (push notification, WebSocket message, SSE event) that new data is available. The client then pulls the actual data. This combines low latency with simple pull-based data transfer.

### 22.4 Batch Sync with Pagination

Never sync unbounded result sets. Paginate using the sync version or timestamp.

```sql
-- Server: paginated sync endpoint
-- Client requests: GET /sync?since_version=42&limit=100

SELECT id, title, status, updated_at, version, is_deleted, sync_version
FROM tasks
WHERE sync_version > :since_version
ORDER BY sync_version ASC
LIMIT :limit;

-- Response includes the max sync_version in the batch
-- Client uses that as since_version for the next page
```

**Batch size recommendations:**
- Start with 100-500 records per batch
- Adjust based on average record size and network conditions
- Mobile: smaller batches (50-100) for unreliable connections
- Desktop: larger batches (500-1000) for stable connections
- Never exceed the SQLite parameter limit (999 for older versions, 32766 for newer)

### 22.5 Idempotent Operations for Retry Safety

Network failures during sync mean the same batch may be sent multiple times. Every sync operation must be safe to replay.

**Making operations idempotent:**

```sql
-- UPSERT pattern: safe to replay
INSERT INTO tasks (id, title, status, updated_at, version)
VALUES (?, ?, ?, ?, ?)
ON CONFLICT (id) DO UPDATE SET
    title = EXCLUDED.title,
    status = EXCLUDED.status,
    updated_at = EXCLUDED.updated_at,
    version = EXCLUDED.version
WHERE EXCLUDED.version > tasks.version;
```

```sql
-- Soft delete: safe to replay
UPDATE tasks SET is_deleted = 1, updated_at = ?
WHERE id = ? AND is_deleted = 0;
-- If already deleted, this is a no-op (0 rows affected) -- safe
```

**Idempotency keys in the outbox:**

```sql
CREATE TABLE outbox (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    payload TEXT NOT NULL,
    idempotency_key TEXT NOT NULL UNIQUE,  -- critical
    status TEXT NOT NULL DEFAULT 'pending',
    attempt_count INTEGER NOT NULL DEFAULT 0,
    created_at INTEGER NOT NULL
);

-- INSERT OR IGNORE prevents duplicate entries on retry
INSERT OR IGNORE INTO outbox (id, type, payload, idempotency_key, created_at)
VALUES (?, ?, ?, ?, ?);
```

**Server-side deduplication:**

The server must also track processed idempotency keys and return success (not error) for duplicates:

```python
def process_sync_batch(changes):
    for change in changes:
        if already_processed(change.idempotency_key):
            continue  # idempotent: return success, don't reapply
        apply_change(change)
        mark_processed(change.idempotency_key)
```

### 22.6 Queue-Based Sync with Outbox Pattern

The outbox pattern ensures that local data writes and sync queue entries are always consistent -- either both happen or neither does.

**Outbox table schema:**

```sql
CREATE TABLE sync_queue (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation TEXT NOT NULL,         -- 'INSERT', 'UPDATE', 'DELETE'
    table_name TEXT NOT NULL,
    record_id TEXT NOT NULL,
    payload TEXT NOT NULL,           -- JSON of the record
    idempotency_key TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
    synced INTEGER NOT NULL DEFAULT 0,
    attempt_count INTEGER NOT NULL DEFAULT 0,
    next_attempt_at INTEGER NOT NULL DEFAULT 0
);

CREATE INDEX idx_sync_unsynced ON sync_queue(synced, next_attempt_at);
```

**Transactional dual-write (critical pattern):**

```python
# BOTH the data write and queue entry in ONE transaction
db.execute("BEGIN TRANSACTION")

db.execute("""
    INSERT INTO tasks (id, title, status, created_at, updated_at)
    VALUES (?, ?, ?, ?, ?)
""", [task_id, title, status, now, now])

db.execute("""
    INSERT INTO sync_queue (operation, table_name, record_id, payload, idempotency_key)
    VALUES ('INSERT', 'tasks', ?, ?, ?)
""", [task_id, json.dumps(task_data), f"insert:tasks:{task_id}"])

db.execute("COMMIT")
# If it's on screen, it's in the outbox.
```

**Sync worker (processes queue on reconnect):**

```python
def process_sync_queue():
    rows = db.execute("""
        SELECT id, operation, table_name, record_id, payload, attempt_count
        FROM sync_queue
        WHERE synced = 0 AND next_attempt_at <= ?
        ORDER BY id ASC
        LIMIT 50
    """, [now_ms()]).fetchall()
    
    for row in rows:
        try:
            response = send_to_server(row)
            if response.status_code in (200, 201, 204):
                db.execute("UPDATE sync_queue SET synced = 1 WHERE id = ?", [row.id])
            elif response.status_code == 409:  # conflict
                handle_conflict(row, response.json())
        except NetworkError:
            # Exponential backoff, capped at 15 minutes
            next_attempt = now_ms() + min(
                15 * 60_000,
                30_000 * (row.attempt_count + 1)
            )
            db.execute("""
                UPDATE sync_queue
                SET attempt_count = attempt_count + 1,
                    next_attempt_at = ?
                WHERE id = ?
            """, [next_attempt, row.id])
```

**Inbound sync (applying server changes locally):**

```python
def apply_server_changes(changes):
    db.execute("BEGIN TRANSACTION")
    for change in changes:
        if change["operation"] == "INSERT":
            db.execute("""
                INSERT OR REPLACE INTO tasks (id, title, status, updated_at, version)
                VALUES (?, ?, ?, ?, ?)
            """, [change["id"], change["title"], change["status"],
                  change["updated_at"], change["version"]])
        elif change["operation"] == "DELETE":
            db.execute("""
                UPDATE tasks SET is_deleted = 1, updated_at = ?
                WHERE id = ?
            """, [change["updated_at"], change["id"]])
    db.execute("COMMIT")
```

**Sources:**
- [Outbox Pattern (Milan Jovanovic)](https://www.milanjovanovic.tech/blog/implementing-the-outbox-pattern)
- [Transactional Outbox Pattern (microservices.io)](https://microservices.io/patterns/data/transactional-outbox.html)
- [React Native Offline Sync with SQLite Queue (DEV)](https://dev.to/sathish_daggula/react-native-offline-sync-with-sqlite-queue-4975)
- [Offline-First Apps with SQLite Sync Queues (SQLite Forum)](https://www.sqliteforum.com/p/building-offline-first-applications-4f4)

---

## 23. Offline-First Architecture

### 23.1 Write-Ahead Log for Offline Operations

SQLite's WAL mode is foundational for offline-first apps.

**Enable WAL mode:**

```sql
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;  -- safe for app crashes, not power loss
```

**Why WAL matters for sync:**
- Readers never block writers and writers never block readers
- Write transactions are fast (sequential log append, no fsync per commit in NORMAL mode)
- Background sync reads can proceed while the user writes data
- WAL can be replicated (Litestream, Turso use this)

**Connection strategy for sync:**
- One writer connection (serialized writes via application-level queue)
- Multiple reader connections (parallel reads for UI and sync)
- Never share a single connection between UI thread and sync thread

### 23.2 Operation Queue Pattern

Queue every mutation as a discrete operation. Replay the queue when connectivity returns.

**Queue table:**

```sql
CREATE TABLE outbox (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,               -- 'create_task', 'update_task', 'delete_task'
    payload TEXT NOT NULL,            -- JSON with all data needed to replay
    idempotency_key TEXT NOT NULL UNIQUE,
    status TEXT NOT NULL DEFAULT 'pending',  -- 'pending', 'sending', 'done', 'failed'
    attempt_count INTEGER NOT NULL DEFAULT 0,
    next_attempt_at INTEGER NOT NULL DEFAULT 0,
    created_at INTEGER NOT NULL
);

CREATE INDEX idx_outbox_pending
ON outbox(status, next_attempt_at)
WHERE status = 'pending';
```

**Critical rule:** The UI write and the outbox entry must be in the same transaction. If it is on screen, it is in the outbox.

**Event-sourcing variant:** Instead of storing record snapshots, store operations:

```json
{"type": "set_logged", "set_id": "abc", "reps": 10, "weight": 135}
{"type": "set_deleted", "set_id": "abc"}
{"type": "workout_renamed", "workout_id": "xyz", "name": "Leg Day"}
```

The server replays these events to reconstruct state. This makes sync equivalent to event replay and naturally supports undo/redo.

### 23.3 Optimistic UI Updates

The UI always reads from the local SQLite database, never from the network. Changes appear instantly.

**Pattern:**

```
User Action
    |
    v
Write to local SQLite + Enqueue to outbox (one transaction)
    |
    v
UI reads from SQLite (instant update)
    |
    v (background, asynchronous)
Sync worker sends outbox to server
    |
    v
Server confirms or rejects
    |
    v
If rejected: roll back local change, notify user
If confirmed: mark outbox entry as done
```

**Rollback on server rejection:**

```python
def handle_server_rejection(outbox_entry, server_response):
    db.execute("BEGIN TRANSACTION")
    # Revert the local change
    if outbox_entry.type == 'create_task':
        db.execute("DELETE FROM tasks WHERE id = ?", [outbox_entry.record_id])
    elif outbox_entry.type == 'update_task':
        # Restore from server's version
        apply_server_version(server_response.current_record)
    # Remove from outbox
    db.execute("UPDATE outbox SET status = 'failed' WHERE id = ?", [outbox_entry.id])
    db.execute("COMMIT")
    notify_user("Your change could not be saved: " + server_response.reason)
```

### 23.4 Schema Migrations When Device Is Offline

Devices may be offline when a new app version with schema changes is released.

**Migration strategy using user_version pragma:**

```python
def migrate_database(db):
    db.execute("PRAGMA user_version")
    current_version = db.fetchone()[0]
    
    if current_version < 1:
        db.execute("ALTER TABLE tasks ADD COLUMN priority TEXT DEFAULT 'medium'")
        db.execute("CREATE INDEX idx_tasks_priority ON tasks(priority)")
        db.execute("PRAGMA user_version = 1")
    
    if current_version < 2:
        db.execute("""
            CREATE TABLE task_tags (
                task_id TEXT NOT NULL REFERENCES tasks(id),
                tag TEXT NOT NULL,
                PRIMARY KEY (task_id, tag)
            )
        """)
        db.execute("PRAGMA user_version = 2")
    
    if current_version < 3:
        # Complex migration: rename column (SQLite < 3.25 workaround)
        db.execute("BEGIN TRANSACTION")
        db.execute("ALTER TABLE tasks RENAME TO tasks_old")
        db.execute("""
            CREATE TABLE tasks (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,  -- renamed from 'content'
                -- ... all other columns
            )
        """)
        db.execute("""
            INSERT INTO tasks (id, title, description, ...)
            SELECT id, title, content, ... FROM tasks_old
        """)
        db.execute("DROP TABLE tasks_old")
        db.execute("COMMIT")
        db.execute("PRAGMA user_version = 3")
```

**Migration tracking table (alternative to pragma):**

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    applied_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))
);
```

**Rules for sync-compatible migrations:**
1. Only add columns -- never remove or rename without a migration path
2. New columns must have DEFAULT values (CRDTs require this)
3. Migrations must be idempotent (safe to run twice)
4. Wrap each migration in a transaction
5. Always back up before migrating
6. Test migrations against databases at every previous version

**Sources:**
- [SQLite Versioning and Migration Strategies (SQLite Forum)](https://www.sqliteforum.com/p/sqlite-versioning-and-migration-strategies)
- [Android SQLite Database Migration (Medium)](https://medium.com/mobile-app-development-publication/android-sqlite-database-migration-b9ad47811d34)

### 23.5 Data Expiry and Cache Invalidation

Local SQLite databases grow unbounded without maintenance.

**Pruning synced data:**

```sql
-- Remove successfully synced outbox entries older than 30 days
DELETE FROM sync_queue
WHERE synced = 1
  AND created_at < strftime('%Y-%m-%dT%H:%M:%fZ', 'now', '-30 days');

-- Remove old change log entries
DELETE FROM change_log
WHERE synced = 1
  AND changed_at < strftime('%Y-%m-%dT%H:%M:%fZ', 'now', '-30 days');

-- Purge tombstones older than 90 days (confirmed synced)
DELETE FROM tasks WHERE is_deleted = 1
  AND updated_at < strftime('%Y-%m-%dT%H:%M:%fZ', 'now', '-90 days')
  AND last_synced_at IS NOT NULL;
```

**VACUUM after pruning:**

```sql
-- Reclaim disk space (locks database, copies and rebuilds)
VACUUM;

-- Check space usage before deciding to vacuum
SELECT page_count * page_size AS total_size,
       freelist_count * page_size AS free_space
FROM pragma_page_count(), pragma_page_size(), pragma_freelist_count();
```

**Incremental vacuum (less disruptive alternative):**

```sql
PRAGMA auto_vacuum = INCREMENTAL;
PRAGMA incremental_vacuum(100);  -- free up to 100 pages
```

**Cache invalidation strategy:**
- Track `last_full_sync` timestamp
- If `last_full_sync` is older than threshold (e.g., 7 days), do a full sync instead of delta
- If server sends a "schema changed" signal, drop and rebuild local tables
- Monitor storage quota (especially important in browsers):

```javascript
const estimate = await navigator.storage.estimate();
const percentUsed = (estimate.usage / estimate.quota) * 100;
if (percentUsed > 80) {
    // Trigger aggressive pruning
    await pruneOldSyncData();
}
```

---

## 24. Type Mapping Between SQLite and Server Databases

### 24.1 Complete Type Mapping Reference

| Data Concept | SQLite Storage | SQLite DDL | PostgreSQL | MySQL | SQL Server |
|-------------|---------------|------------|------------|-------|------------|
| UUID | TEXT | `id TEXT PRIMARY KEY` | `UUID` | `CHAR(36)` | `UNIQUEIDENTIFIER` |
| Boolean | INTEGER | `is_active INTEGER DEFAULT 0` | `BOOLEAN` | `TINYINT(1)` | `BIT` |
| Timestamp (UTC) | TEXT | `created_at TEXT` | `TIMESTAMPTZ` | `DATETIME` | `DATETIMEOFFSET` |
| Date only | TEXT | `birth_date TEXT` | `DATE` | `DATE` | `DATE` |
| Integer | INTEGER | `count INTEGER` | `INTEGER` / `BIGINT` | `INT` / `BIGINT` | `INT` / `BIGINT` |
| Decimal | TEXT or REAL | `price TEXT` | `NUMERIC(10,2)` | `DECIMAL(10,2)` | `DECIMAL(10,2)` |
| Float | REAL | `latitude REAL` | `DOUBLE PRECISION` | `DOUBLE` | `FLOAT` |
| Short text | TEXT | `name TEXT` | `VARCHAR(255)` | `VARCHAR(255)` | `NVARCHAR(255)` |
| Long text | TEXT | `description TEXT` | `TEXT` | `TEXT` | `NVARCHAR(MAX)` |
| JSON | TEXT | `metadata TEXT` | `JSONB` | `JSON` | `NVARCHAR(MAX)` |
| Binary data | BLOB | `avatar BLOB` | `BYTEA` | `LONGBLOB` | `VARBINARY(MAX)` |
| Enum | TEXT | `status TEXT CHECK(...)` | `VARCHAR` + CHECK | `ENUM(...)` | `VARCHAR` + CHECK |

### 24.2 Date/Time Format Alignment

**Critical rule: Always store and transmit dates as ISO-8601 UTC strings.**

```sql
-- SQLite: store as ISO-8601 TEXT
INSERT INTO events (id, event_date)
VALUES ('evt-1', strftime('%Y-%m-%dT%H:%M:%fZ', 'now'));
-- Result: '2026-04-03T14:30:45.123Z'

-- PostgreSQL: parse from ISO-8601
INSERT INTO events (id, event_date)
VALUES ('evt-1', '2026-04-03T14:30:45.123Z'::timestamptz);
```

**Conversion helpers:**

```sql
-- SQLite: ISO-8601 TEXT to Unix timestamp
SELECT strftime('%s', '2026-04-03T14:30:45Z');  -- 1775148645

-- SQLite: Unix timestamp to ISO-8601 TEXT
SELECT strftime('%Y-%m-%dT%H:%M:%fZ', 1775148645, 'unixepoch');

-- SQLite: Compare dates stored as TEXT (works because ISO-8601 is lexicographically sortable)
SELECT * FROM events WHERE event_date > '2026-01-01T00:00:00Z';
```

**Pitfalls:**
- SQLite has no TIMESTAMP type -- it stores dates as TEXT, REAL, or INTEGER
- ISO-8601 TEXT comparison requires consistent formatting (always use leading zeros, always include 'Z' suffix)
- Never mix timestamp formats in the same column
- Always convert to UTC before storing; convert to local time only at the display layer
- PostgreSQL `TIMESTAMP` (without time zone) and `TIMESTAMPTZ` behave differently -- always use `TIMESTAMPTZ` for synced data

### 24.3 JSON Handling Differences

```sql
-- SQLite: JSON stored as TEXT, queried with json1 functions
SELECT json_extract(metadata, '$.color') FROM tasks WHERE id = ?;
SELECT metadata ->> 'color' FROM tasks WHERE id = ?;  -- SQLite 3.38+

-- PostgreSQL: JSON stored as JSONB (binary, indexed)
SELECT metadata->>'color' FROM tasks WHERE id = ?;

-- SQLite: index on JSON field
CREATE INDEX idx_tasks_color ON tasks(json_extract(metadata, '$.color'));

-- PostgreSQL: GIN index on JSONB
CREATE INDEX idx_tasks_metadata ON tasks USING GIN (metadata);
```

**Compatibility notes:**
- SQLite's `->` and `->>` operators are designed to be compatible with both MySQL and PostgreSQL syntax
- SQLite JSONB format is NOT binary-compatible with PostgreSQL JSONB -- it is a different on-disk format
- Always validate JSON on both sides -- SQLite's json1 returns NULL for invalid JSON, PostgreSQL raises an error

### 24.4 Boolean Handling

```sql
-- SQLite: booleans are integers
INSERT INTO tasks (id, is_complete) VALUES ('task-1', 0);
SELECT * FROM tasks WHERE is_complete = 1;

-- PostgreSQL: native boolean
INSERT INTO tasks (id, is_complete) VALUES ('task-1', FALSE);
SELECT * FROM tasks WHERE is_complete = TRUE;
```

**Sync conversion layer:**

```python
def sqlite_to_postgres(record):
    """Convert SQLite record to PostgreSQL-compatible values."""
    converted = dict(record)
    for col in boolean_columns:
        converted[col] = bool(converted[col])  # 0/1 -> False/True
    for col in timestamp_columns:
        # TEXT -> datetime object (PostgreSQL driver handles conversion)
        converted[col] = datetime.fromisoformat(converted[col])
    return converted

def postgres_to_sqlite(record):
    """Convert PostgreSQL record to SQLite-compatible values."""
    converted = dict(record)
    for col in boolean_columns:
        converted[col] = int(converted[col])  # True/False -> 1/0
    for col in timestamp_columns:
        converted[col] = record[col].isoformat()  # datetime -> TEXT
    return converted
```

**Sources:**
- [SQLite Data Types (w3resource)](https://www.w3resource.com/sqlite/sqlite-data-types.php)
- [Datatypes in SQLite (sqlite.org)](https://www.sqlite.org/datatype3.html)
- [Handling Timestamps in SQLite (sqlite.ai)](https://blog.sqlite.ai/handling-timestamps-in-sqlite)
- [Drizzle ORM SQLite Column Types](https://orm.drizzle.team/docs/column-types/sqlite)
- [Drizzle ORM PostgreSQL Column Types](https://orm.drizzle.team/docs/column-types/pg)

---

## 25. SQLite Sync Tools and Extensions

### 25.1 SQLite Session Extension (sqlite3session)

Built into SQLite. Records changes to attached tables and packages them as binary changesets.

**Key capabilities:**
- Captures INSERT, UPDATE, DELETE as binary blobs
- Changesets can be applied to other databases with the same schema
- Built-in conflict handler callback
- Supports changeset inversion (undo)
- Supports changeset concatenation (batch multiple sessions)

**Conflict handler callback types:**

| Conflict Type | Trigger Condition |
|--------------|-------------------|
| SQLITE_CHANGESET_DATA | UPDATE/DELETE: row exists but non-PK values don't match |
| SQLITE_CHANGESET_NOTFOUND | UPDATE/DELETE: no row with matching PK |
| SQLITE_CHANGESET_CONFLICT | INSERT: row with matching PK already exists |
| SQLITE_CHANGESET_CONSTRAINT | Change violates UNIQUE or CHECK constraint |

**Limitations:**
- Tables must have a declared PRIMARY KEY
- Virtual tables not supported
- NULL values in PK columns are ignored (rows not captured)
- Requires compile-time flags: `-DSQLITE_ENABLE_SESSION -DSQLITE_ENABLE_PREUPDATE_HOOK`

**Source:** [SQLite Session Extension (sqlite.org)](https://sqlite.org/sessionintro.html)

### 25.2 CR-SQLite (CRDT-Based Merge)

Run-time loadable extension that adds multi-master replication via CRDTs.

**Setup:**

```sql
.load crsqlite

CREATE TABLE documents (id TEXT PRIMARY KEY NOT NULL, title TEXT, content TEXT);
SELECT crsql_as_crr('documents');
```

**Sync between two databases:**

```sql
-- On Device A: export changes
SELECT * FROM crsql_changes WHERE db_version > ?;

-- On Device B: import Device A's changes
INSERT INTO crsql_changes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);
```

**Schema changes on CRR tables:**

```sql
SELECT crsql_begin_alter('documents');
ALTER TABLE documents ADD COLUMN status TEXT;
SELECT crsql_commit_alter('documents');
```

**CRDT algorithms per column:** LWW (last-write-wins), fractional indices (list ordering), observe-remove sets (row presence). Counter and rich-text CRDTs in development.

**Source:** [cr-sqlite (GitHub)](https://github.com/vlcn-io/cr-sqlite)

### 25.3 Litestream

Streaming WAL-based replication for disaster recovery. Not a sync tool -- it replicates a single SQLite database to cloud storage (S3, Azure Blob, SFTP).

**How it works:**
1. Takes over SQLite's WAL checkpointing process
2. Starts a long-running read transaction to prevent other processes from checkpointing
3. Continuously copies new WAL pages to a "shadow WAL" directory
4. Streams shadow WAL to configured storage backends
5. Periodically takes full snapshots; prunes old WAL files

**Key configuration:**

```yaml
dbs:
  - path: /path/to/app.db
    replicas:
      - type: s3
        bucket: my-backup-bucket
        path: app.db
        retention: 72h
```

**Live read replicas:** Litestream can stream changes to read-only replicas on other servers, applying changes in a transactionally-safe manner.

**When to use:** Server-side SQLite backup and disaster recovery. Not designed for multi-writer sync or device-to-server sync.

**Source:** [Litestream (litestream.io)](https://litestream.io/how-it-works/)

### 25.4 ElectricSQL

Syncs Postgres with client-side SQLite using the Postgres logical replication WAL.

**Architecture:**
- Electric service sits between Postgres and clients
- Reads Postgres WAL via logical replication
- Streams changes to client-side SQLite (browser via WASM, mobile via native SQLite)
- Client writes go through Electric back to Postgres
- Conflict resolution via CRDTs (last-writer-wins semantics)

**Key characteristic:** "Direct-to-Postgres" -- writes bypass your application backend. Validation must happen via Postgres constraints and DDLX rules.

**Trade-offs:**
- Pro: No backend code needed for sync
- Con: Cannot inject custom business logic on the write path
- Con: Modifies Postgres schema (adds shadow tables, triggers)
- Con: Requires SUPERUSER database privileges

**Source:** [ElectricSQL Alternatives (electric-sql.com)](https://electric-sql.com/docs/reference/alternatives)

### 25.5 PowerSync

Postgres-to-SQLite sync engine with server-authoritative write path.

**Architecture:**
- PowerSync Service connects to Postgres via logical replication (read-only)
- Streams data to client-side SQLite based on configurable "Sync Rules"
- Client writes go to a local upload queue, then through YOUR backend
- Your backend applies business logic, validation, authorization
- Changes committed to Postgres flow back to all clients via PowerSync

**Key differentiator:** You control the write path. The server can reject, transform, or merge client writes with custom logic.

**Sync Rules (dynamic partial replication):**

```yaml
# Only sync tasks belonging to the current user
- table: tasks
  filter: "user_id = token_parameters.user_id"
```

**Consistency model:** Causal+ consistency via checkpoint-based synchronization. Clients update state atomically when receiving all data matching a checkpoint.

**Supported backends:** Postgres (GA), MongoDB (GA), MySQL (planned)

**Sources:**
- [PowerSync v1.0 (powersync.com)](https://www.powersync.com/blog/introducing-powersync-v1-0-postgres-sqlite-sync-layer)
- [ElectricSQL vs PowerSync (powersync.com)](https://www.powersync.com/blog/electricsql-vs-powersync)

### 25.6 Turso / libSQL

Fork of SQLite with built-in replication and embedded replicas.

**Embedded replicas architecture:**
- Source of truth is the remote Turso database
- Local SQLite copy on each device for zero-latency reads
- Sync uses frame-based WAL replication (1 frame = 4KB page)
- Guarantees read-your-writes semantics

**Sync strategies:**
- Manual sync: call `client.sync()` when desired
- Periodic sync: configure `syncInterval` for automatic polling
- Offline writes: write to local WAL, push when connected, pull to reconcile

**Conflict resolution options:**
- `FAIL_ON_CONFLICT` -- reject and require explicit handling
- `DISCARD_LOCAL` -- server-wins (discard local changes)
- `REBASE_LOCAL` -- replay local changes on top of server state
- `MANUAL_RESOLUTION` -- callback with `localData` and `remoteData`

```typescript
const client = createClient({
    url: 'local.db',
    syncUrl: 'libsql://remote.turso.io',
    authToken: '...',
});

await client.execute('INSERT INTO tasks VALUES (?)', ['task-1']);
await client.sync({ strategy: SyncStrategy.REBASE_LOCAL });
```

**Source:** [Turso Offline Writes (turso.tech)](https://turso.tech/blog/introducing-offline-writes-for-turso)

### 25.7 SQLite Sync (sqlite.ai)

CRDT-based extension that syncs SQLite with SQLite Cloud, PostgreSQL, and Supabase.

**Setup:**

```sql
.load cloudsync

-- Enable CRDT sync on a table
SELECT cloudsync_init('tasks');

-- Use UUIDv7 for primary keys
INSERT INTO tasks (id, title) VALUES (cloudsync_uuid(), 'New task');

-- Connect and sync
SELECT cloudsync_network_init('your-database-id');
SELECT cloudsync_network_set_apikey('your-api-key');
SELECT cloudsync_network_sync();
```

**CRDT algorithm options:**
- `cls` (Causal-Length Set) -- default
- `dws` (Delete-Wins Set)
- `aws` (Add-Wins Set)
- `gos` (Grow-Only Set)

**Block-level LWW for text columns:**

```sql
-- Enable per-line conflict resolution on a text column
SELECT cloudsync_set_column('notes', 'body', 'algo', 'block');
SELECT cloudsync_set_column('notes', 'body', 'delimiter', '\n');

-- After sync, materialize the merged text
SELECT cloudsync_text_materialize('notes', 'body', 'note-001');
```

**Schema requirements:**
- All NOT NULL columns must have DEFAULT values
- TEXT primary keys with UUIDv7 recommended
- Must call `cloudsync_begin_alter` / `cloudsync_commit_alter` before/after ALTER TABLE

**Source:** [sqlite-sync API (GitHub)](https://github.com/sqliteai/sqlite-sync/blob/main/API.md)

### Tool Comparison Matrix

| Feature | Session Extension | cr-sqlite | Litestream | ElectricSQL | PowerSync | Turso | sqlite-sync |
|---------|-------------------|-----------|------------|-------------|-----------|-------|-------------|
| **Sync direction** | Manual | Bidirectional | One-way (backup) | Bidirectional | Bidirectional | Bidirectional | Bidirectional |
| **Conflict resolution** | Callback | CRDT (automatic) | N/A | CRDT (LWW) | Custom (your backend) | Multiple strategies | CRDT (automatic) |
| **Server DB** | Any | Any | N/A (storage) | Postgres only | Postgres, MongoDB | Turso Cloud | SQLite Cloud, PG, Supabase |
| **Offline writes** | Yes | Yes | No | Yes | Yes | Yes | Yes |
| **Custom write logic** | Yes | No | N/A | No (PG constraints) | Yes (your backend) | Partial | No |
| **Setup complexity** | Low (C API) | Low (extension) | Low (config) | Medium | Medium | Low | Low (extension) |
| **Maturity** | Stable (part of SQLite) | Beta | Stable | Production | Production | Beta (offline) | Beta |

---

## 26. Real-World Sync Architectures

### 26.1 Notion

**Architecture:** Notion built their entire client-side data layer on SQLite compiled to WebAssembly.

**Key design decisions:**
- Uses OPFS SyncAccessHandle Pool VFS for browser persistence
- SharedWorker coordinates SQLite access across browser tabs -- only one tab writes at a time
- Web Locks API detects closed tabs
- The local SQLite database serves as a read cache; the server is source of truth
- Every server update writes to the local cache
- Navigation queries race SQLite and API requests on slower devices

**Performance results:**
- 20% improvement in page navigation times across all browsers
- 28-33% faster for users in high-latency regions (Australia, China, India)

**Notable trade-off:** Initial page load deliberately skips SQLite caching because downloading the WASM library is slower than the first API call. SQLite only accelerates subsequent navigations.

**Source:** [How We Sped Up Notion with WASM SQLite (Notion Blog)](https://www.notion.com/blog/how-we-sped-up-notion-in-the-browser-with-wasm-sqlite)

### 26.2 Linear

**Architecture:** Custom sync engine with centralized server authority.

**Key design decisions:**
- All operations pass through the server, which assigns sequential sync IDs (monotonically increasing integers)
- Sync IDs serve as the global version number of the database
- Clients send transactions to the server; server broadcasts delta packets to all clients
- Delta packets may differ from the original transaction (server can add side-effects)
- Uses MobX for reactive UI updates from local store
- IndexedDB for browser-side persistence

**Data model:**
- Models defined with TypeScript decorators (`@ClientModel`)
- Seven property types: property, ephemeralProperty, reference, referenceModel, referenceCollection, backReference, referenceArray
- Lazy loading for properties not needed at bootstrap
- Schema hash for instant detection of schema mismatches

**Offline support:**
- Transactions cached in IndexedDB during disconnection
- Automatically resent on reconnection
- Reversible transactions enable client-side rollback if server rejects

**Conflict resolution:** Last-writer-wins for simple fields; server-authoritative ordering via sync IDs eliminates most conflicts by serializing all operations.

**Sources:**
- [Reverse Engineering Linear's Sync Engine (GitHub)](https://github.com/wzhudev/reverse-linear-sync-engine)
- [Linear local-first rabbit hole (Bytemash)](https://bytemash.net/posts/i-went-down-the-linear-rabbit-hole/)

### 26.3 Figma

**Architecture:** Client/server with custom CRDT-inspired approach.

**Key design decisions:**
- Clients connect to servers via WebSockets
- Each document gets a separate server process
- Inspired by CRDTs but not a pure CRDT implementation
- Uses server authority for operation ordering (closer to OT than full CRDT)
- CRDTs provide eventual consistency guarantees: if no more updates, all clients converge

**Collaboration model:**
- Server receives operations, validates against authoritative state
- Transforms operations to resolve concurrent conflicts
- Broadcasts transformed operations to all connected clients
- Client-side operations are applied optimistically (instant UI)

**Source:** [How Figma's Multiplayer Technology Works (Figma Blog)](https://www.figma.com/blog/how-figmas-multiplayer-technology-works/)

### 26.4 Mobile Apps (iOS/Android)

**iOS pattern (Core Data + CloudKit):**
- `NSPersistentCloudKitContainer` bridges Core Data (backed by SQLite) with iCloud
- Only SQLite-type persistent stores can be synchronized
- Requires Persistent History Tracking enabled
- Supports three database tiers: private, shared, public
- Multiple SQLite stores with separate configurations control what syncs

**Android pattern (Room + Sync Adapter):**
- Room provides a type-safe abstraction over SQLite
- SyncAdapter framework handles background sync with system-managed scheduling
- ContentProvider mediates between SyncAdapter and the private SQLite database
- System batches sync operations for battery efficiency

**Cross-platform pattern (React Native / Flutter):**
- SQLite via `expo-sqlite` or `sqflite` packages
- Outbox queue table for pending mutations
- NetInfo API to detect connectivity changes
- Background sync on reconnect
- PowerSync or ElectricSQL for managed sync infrastructure

### 26.5 Desktop Apps (Electron / Tauri)

**Electron:**
- better-sqlite3 or sql.js for SQLite access
- RxDB provides reactive queries with IndexedDB or SQLite adapters
- Sync via REST APIs or WebSocket connections
- Multiple windows share one SQLite database via main process IPC

**Tauri:**
- Rust backend with `sqlx` crate for direct SQLite access
- Tauri SQL plugin for cross-platform SQLite
- Drizzle ORM: frontend computes SQL queries, sends to Rust backend for execution
- Turso embedded replicas for managed sync

**Shared desktop pattern:**
- SQLite database in the app's data directory
- WAL mode enabled for concurrent read/write
- Sync worker runs in a background thread
- Outbox pattern for offline writes
- Delta sync for efficient bandwidth usage

**Sources:**
- [Expo SQLite Guide (Expo Documentation)](https://docs.expo.dev/guides/local-first/)
- [Electron Database (RxDB)](https://rxdb.info/electron-database.html)
- [Drizzle + SQLite in Tauri (DEV)](https://dev.to/huakun/drizzle-sqlite-in-tauri-app-kif)
- [Android Room Database (Android Developers)](https://developer.android.com/training/data-storage/room)

---

## 27. Performance Considerations for Sync

### 27.1 Batch Size for Sync Operations

**Recommendations:**

| Context | Batch Size | Rationale |
|---------|------------|-----------|
| Mobile (unstable network) | 50-100 records | Smaller batches survive connection drops |
| Desktop (stable network) | 500-1000 records | Larger batches reduce HTTP overhead |
| Initial bootstrap | 1000-5000 records | Fast initial sync is critical for UX |
| Background sync | 100-500 records | Balance throughput with UI responsiveness |

**JSON bulk operations (PowerSync pattern):**

```sql
-- Bulk insert via JSON: single statement, no parameter limit issues
INSERT INTO tasks (id, title, status)
SELECT e->>'id', e->>'title', e->>'status'
FROM json_each(?) e;

-- Bulk update via JSON
WITH data AS (
    SELECT e->>'id' AS id, e->>'title' AS title, e->>'status' AS status
    FROM json_each(?) e
)
UPDATE tasks
SET title = data.title, status = data.status
FROM data
WHERE tasks.id = data.id;

-- Bulk delete via JSON
DELETE FROM tasks
WHERE id IN (SELECT e.value FROM json_each(?) e);
```

### 27.2 Transaction Management During Sync

**Rule: Wrap each sync batch in a single transaction.**

```python
def apply_sync_batch(changes):
    db.execute("BEGIN IMMEDIATE")  # IMMEDIATE to acquire write lock upfront
    try:
        for change in changes:
            apply_change(db, change)
        db.execute("COMMIT")
    except Exception:
        db.execute("ROLLBACK")
        raise
```

**Why IMMEDIATE for sync transactions:** `BEGIN IMMEDIATE` acquires the write lock at the start of the transaction, not at the first write statement. This prevents SQLITE_BUSY errors mid-transaction, which would require rolling back and retrying the entire batch.

**Connection strategy:**
- Single write connection with an application-level queue (prevents SQLITE_BUSY)
- Multiple read connections for UI queries
- Never hold a write transaction open while waiting for network I/O

**Transaction batching benchmark:**
- Without transaction: each INSERT triggers an fsync (30ms+ per operation)
- With transaction wrapping: 2-20x throughput improvement
- WAL mode + synchronous=NORMAL: reduces per-transaction overhead from 30ms+ to under 1ms

### 27.3 Index Strategy for Sync Metadata Columns

**Essential indexes for sync:**

```sql
-- Find unsynced records (most important sync query)
CREATE INDEX idx_tasks_sync_status
ON tasks(last_synced_at, updated_at)
WHERE last_synced_at IS NULL OR updated_at > last_synced_at;

-- Outbox: find pending entries
CREATE INDEX idx_outbox_pending
ON outbox(status, next_attempt_at)
WHERE status = 'pending';

-- Change log: find unsynced changes
CREATE INDEX idx_changelog_unsynced
ON change_log(synced, changed_at)
WHERE synced = 0;

-- Soft-deleted records
CREATE INDEX idx_tasks_deleted ON tasks(is_deleted);

-- Version-based sync
CREATE INDEX idx_tasks_version ON tasks(version);
```

**Partial indexes (SQLite 3.8.0+) reduce index size:** Only index the rows that matter for sync queries.

**Use EXPLAIN QUERY PLAN to verify:**

```sql
EXPLAIN QUERY PLAN
SELECT * FROM tasks
WHERE last_synced_at IS NULL OR updated_at > last_synced_at;
-- Should show "SEARCH ... USING INDEX" not "SCAN"
```

### 27.4 WAL Mode Benefits for Concurrent Sync Reads/Writes

**Essential PRAGMA configuration for sync:**

```sql
PRAGMA journal_mode = WAL;           -- enable write-ahead logging
PRAGMA synchronous = NORMAL;         -- safe for app crashes, fast commits
PRAGMA busy_timeout = 5000;          -- wait 5s instead of failing immediately
PRAGMA journal_size_limit = 6144000; -- limit WAL file to ~6MB
PRAGMA cache_size = -2000;           -- 2MB page cache (negative = KB)
PRAGMA foreign_keys = ON;            -- enforce referential integrity
```

**WAL concurrency model:**
- Multiple readers can proceed simultaneously
- One writer at a time (SQLITE_BUSY if contended)
- Readers do not block writers
- Writers do not block readers
- Readers see a consistent snapshot from when they started

**WAL checkpoint management:**

```sql
-- Default: auto-checkpoint every 1000 pages
PRAGMA wal_autocheckpoint = 1000;

-- Manual checkpoint (run periodically or after large sync batches)
PRAGMA wal_checkpoint(PASSIVE);   -- doesn't block, checkpoints what it can
PRAGMA wal_checkpoint(TRUNCATE);  -- blocks briefly, resets WAL to zero size
```

**Checkpoint strategy for sync:**
- Use PASSIVE checkpoints during normal operation
- Use TRUNCATE checkpoint after large sync batches (reduces WAL file size)
- Run checkpoints in a separate thread/connection to avoid blocking UI reads

### 27.5 Database Size Management

**Monitoring database size:**

```sql
-- Total size and free space
SELECT page_count * page_size AS total_bytes,
       freelist_count * page_size AS free_bytes
FROM pragma_page_count(), pragma_page_size(), pragma_freelist_count();
```

**Pruning strategy:**

```sql
-- 1. Purge synced outbox entries (keep 7 days for debugging)
DELETE FROM outbox WHERE status = 'done'
  AND created_at < strftime('%s', 'now', '-7 days') * 1000;

-- 2. Purge old change log entries
DELETE FROM change_log WHERE synced = 1
  AND changed_at < strftime('%Y-%m-%dT%H:%M:%fZ', 'now', '-30 days');

-- 3. Hard-delete confirmed tombstones
DELETE FROM tasks WHERE is_deleted = 1
  AND last_synced_at IS NOT NULL
  AND updated_at < strftime('%Y-%m-%dT%H:%M:%fZ', 'now', '-90 days');

-- 4. Reclaim space (only if significant free space exists)
PRAGMA incremental_vacuum(500);  -- free up to 500 pages
```

**When to VACUUM:**
- After deleting 25%+ of database content
- Run during app idle time or on app launch
- VACUUM locks the database and requires 2x the database size in free disk space
- Prefer `PRAGMA incremental_vacuum` for gradual, non-blocking reclamation

**Sources:**
- [SQLite Optimizations for Ultra High-Performance (PowerSync)](https://www.powersync.com/blog/sqlite-optimizations-for-ultra-high-performance)
- [Best Practices for SQLite Performance (Android Developers)](https://developer.android.com/topic/performance/sqlite-performance-best-practices)
- [Write-Ahead Logging (sqlite.org)](https://sqlite.org/wal.html)
- [SQLite Performance Tuning (phiresky)](https://phiresky.github.io/blog/2020/sqlite-performance-tuning/)
- [SQLite WAL Mode for Mobile Apps (DEV)](https://dev.to/software_mvp-factory/sqlite-wal-mode-and-connection-strategies-for-high-throughput-mobile-apps-beyond-the-basics-eh0)

---

# Part V: Appendices

## 28. Collected References

### Schema Design

- [Datatypes In SQLite](https://www.sqlite.org/datatype3.html)
- [STRICT Tables](https://www.sqlite.org/stricttables.html)
- [The Advantages of Flexible Typing](https://www.sqlite.org/flextypegood.html)
- [Rowid Tables](https://www.sqlite.org/rowidtable.html)
- [SQLite Autoincrement](https://www.sqlite.org/autoinc.html)
- [WITHOUT ROWID Tables](https://www.sqlite.org/withoutrowid.html)
- [SQLite Foreign Key Support](https://sqlite.org/foreignkeys.html)
- [CREATE TABLE: CHECK constraints](https://www.sqlite.org/lang_createtable.html)
- [SQLite Keywords](https://www.sqlite.org/lang_keywords.html)
- [Database Naming Standards (Ovid)](https://dev.to/ovid/database-naming-standards-2061)
- [SQL Naming Conventions (bbkane)](https://www.bbkane.com/blog/sql-naming-conventions/)
- [UUID vs Auto-Increment (Bytebase)](https://www.bytebase.com/blog/choose-primary-key-uuid-or-auto-increment/)
- [Database Design Patterns (Bytebase)](https://www.bytebase.com/blog/database-design-patterns/)
- [Database Schema Design Patterns for SQLite](https://sqleditor.online/blog/sqlite-schema-design-patterns)

### Performance

- [SQLite Query Planning](https://sqlite.org/queryplanner.html)
- [SQLite Query Optimizer](https://sqlite.org/optoverview.html)
- [SQLite EXPLAIN QUERY PLAN](https://www.sqlite.org/eqp.html)
- [SQLite Partial Indexes](https://www.sqlite.org/partialindex.html)
- [SQLite Indexes on Expressions](https://sqlite.org/expridx.html)
- [SQLite Generated Columns](https://sqlite.org/gencol.html)
- [SQLite WAL Documentation](https://sqlite.org/wal.html)
- [SQLite PRAGMA Documentation](https://sqlite.org/pragma.html)
- [SQLite Transaction Documentation](https://sqlite.org/lang_transaction.html)
- [SQLite JSON Functions](https://sqlite.org/json1.html)
- [CREATE TRIGGER](https://www.sqlite.org/lang_createtrigger.html)
- [Fast SQLite Inserts (avi.im)](https://avi.im/blag/2021/fast-sqlite-inserts/)
- [SQLite Optimizations for Ultra High-Performance (PowerSync)](https://www.powersync.com/blog/sqlite-optimizations-for-ultra-high-performance)
- [SQLite Performance Tuning (phiresky)](https://phiresky.github.io/blog/2020/sqlite-performance-tuning/)
- [SQLite PRAGMA Cheatsheet](https://cj.rs/blog/sqlite-pragma-cheatsheet-for-performance-and-consistency/)
- [High Performance SQLite Recommended PRAGMAs](https://highperformancesqlite.com/articles/sqlite-recommended-pragmas)
- [Fly.io SQLite WAL Internals](https://fly.io/blog/sqlite-internals-wal/)
- [Use The Index, Luke - Insert](https://use-the-index-luke.com/sql/dml/insert)
- [Deep Dive into SQLite Query Optimizer](https://micahkepe.com/blog/sqlite-query-optimizer/)
- [SQLite JSON and Denormalization](https://maximeblanc.fr/blog/sqlite-json-and-denormalization)
- [SQLite JSON Virtual Columns + Indexing](https://www.dbpro.app/blog/sqlite-json-virtual-columns-indexing)

### Operations

- [SQLite Backup API](https://sqlite.org/backup.html)
- [SQLite ALTER TABLE documentation](https://sqlite.org/lang_altertable.html)
- [Internal Versus External BLOBs](https://sqlite.org/intern-v-extern-blob.html)
- [35% Faster Than The Filesystem](https://sqlite.org/fasterthanfs.html)
- [How To Corrupt An SQLite Database File](https://sqlite.org/howtocorrupt.html)
- [Recovering Data From A Corrupt SQLite Database](https://sqlite.org/recovery.html)
- [SQLite Date & Time Functions](https://sqlite.org/lang_datefunc.html)
- [How SQLite Is Tested](https://sqlite.org/testing.html)
- [Appropriate Uses For SQLite](https://sqlite.org/whentouse.html)
- [Backup strategies for SQLite in production](https://oldmoe.blog/2024/04/30/backup-strategies-for-sqlite-in-production/)
- [SQLite DB Migrations with PRAGMA user_version](https://levlaz.org/sqlite-db-migrations-with-pragma-user_version/)
- [Simple declarative schema migration for SQLite](https://david.rothlis.net/declarative-schema-migration-for-sqlite/)
- [OWASP SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)

### Sync

- [SQLite Session Extension (sqlite.org)](https://sqlite.org/sessionintro.html)
- [cr-sqlite (GitHub)](https://github.com/vlcn-io/cr-sqlite)
- [Litestream (litestream.io)](https://litestream.io/how-it-works/)
- [ElectricSQL (electric-sql.com)](https://electric-sql.com/docs/reference/alternatives)
- [PowerSync v1.0 (powersync.com)](https://www.powersync.com/blog/introducing-powersync-v1-0-postgres-sqlite-sync-layer)
- [Turso Offline Writes (turso.tech)](https://turso.tech/blog/introducing-offline-writes-for-turso)
- [sqlite-sync API (GitHub)](https://github.com/sqliteai/sqlite-sync/blob/main/API.md)
- [Handling Timestamps in SQLite (sqlite.ai)](https://blog.sqlite.ai/handling-timestamps-in-sqlite)
- [Hybrid Logical Clocks (Sergei Turukin)](https://sergeiturukin.com/2017/06/26/hybrid-logical-clocks.html)
- [Outbox Pattern (Milan Jovanovic)](https://www.milanjovanovic.tech/blog/implementing-the-outbox-pattern)
- [Transactional Outbox Pattern (microservices.io)](https://microservices.io/patterns/data/transactional-outbox.html)
- [CRDT Dictionary (Ian Duncan)](https://www.iankduncan.com/engineering/2025-11-27-crdt-dictionary/)
- [CRDT Implementations (crdt.tech)](https://crdt.tech/implementations)
- [OT vs CRDT Comparison (thom.ee)](https://thom.ee/blog/crdt-vs-operational-transformation/)
- [How We Sped Up Notion with WASM SQLite (Notion Blog)](https://www.notion.com/blog/how-we-sped-up-notion-in-the-browser-with-wasm-sqlite)
- [Reverse Engineering Linear's Sync Engine (GitHub)](https://github.com/wzhudev/reverse-linear-sync-engine)
- [How Figma's Multiplayer Technology Works (Figma Blog)](https://www.figma.com/blog/how-figmas-multiplayer-technology-works/)
- [Expo SQLite Guide (Expo Documentation)](https://docs.expo.dev/guides/local-first/)
- [Electron Database (RxDB)](https://rxdb.info/electron-database.html)
- [Android Room Database (Android Developers)](https://developer.android.com/training/data-storage/room)
- [Best Practices for SQLite Performance (Android Developers)](https://developer.android.com/topic/performance/sqlite-performance-best-practices)

---

## 29. Decision Frameworks

### Choosing a Sync Strategy

```
Is the server always the source of truth?
├── YES: Pull-only sync (server-wins)
│   └── Tools: PowerSync, Turso embedded replicas
└── NO: Bidirectional sync needed
    │
    Can you tolerate silent data loss on conflict?
    ├── YES: Last-Write-Wins
    │   └── Simple timestamp-based resolution
    └── NO:
        │
        Do users edit the same fields concurrently?
        ├── RARELY: Field-level merge
        │   └── Three-way merge with base version
        ├── OFTEN: CRDTs or OT
        │   └── Tools: cr-sqlite, ElectricSQL, sqlite-sync
        └── NEVER (single-user-per-record): Version-based optimistic concurrency
            └── Conflict queue for edge cases
```

### Choosing a Sync Tool

```
Do you need custom business logic on writes?
├── YES: PowerSync (your backend handles writes)
└── NO:
    │
    Is your server database Postgres?
    ├── YES:
    │   ├── Want CRDTs? → ElectricSQL
    │   ├── Want control? → PowerSync
    │   └── Want simplicity? → Turso + embedded replicas
    └── NO / Multiple DBs:
        ├── SQLite-to-SQLite: cr-sqlite or sqlite-sync
        ├── Need backup only: Litestream
        └── Custom: SQLite Session Extension + your own sync layer
```

---

*Compiled from official SQLite documentation, benchmarks, and practitioner sources. Last updated April 2026.*
