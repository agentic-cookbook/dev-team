# Database Platform Specialist

## Role
Schema design, migrations, indexing, query optimization, transactions, concurrency, backup/restore, data modeling, local-remote sync architecture.

## Persona
(coming)

## Cookbook Sources
- `guidelines/database-design/naming-conventions.md`
- `guidelines/database-design/data-types.md`
- `guidelines/database-design/primary-keys.md`
- `guidelines/database-design/foreign-keys.md`
- `guidelines/database-design/constraints-and-validation.md`
- `guidelines/database-design/relationships.md`
- `guidelines/database-design/normalization-and-denormalization.md`
- `guidelines/database-design/json-columns.md`
- `guidelines/database-design/schema-evolution.md`
- `guidelines/database-design/indexing.md`
- `guidelines/database-design/query-optimization.md`
- `guidelines/database-design/transactions-and-concurrency.md`
- `guidelines/database-design/access-pattern-analysis.md`
- `guidelines/database-design/backup-and-recovery.md`
- `guidelines/database-design/testing.md`
- `guidelines/database-design/sync-schema-design.md`
- `guidelines/database-design/conflict-resolution.md`
- `guidelines/database-design/sync-protocol.md`
- `guidelines/database-design/clock-systems.md`
- `guidelines/database-design/offline-first-architecture.md`
- `guidelines/database-design/sync-engine-design.md`
- `guidelines/database-design/sync-tooling.md`

## Manifest

- specialty-teams/platform-database/naming-conventions.md
- specialty-teams/platform-database/data-types.md
- specialty-teams/platform-database/primary-keys.md
- specialty-teams/platform-database/foreign-keys.md
- specialty-teams/platform-database/constraints-and-validation.md
- specialty-teams/platform-database/relationships.md
- specialty-teams/platform-database/normalization-and-denormalization.md
- specialty-teams/platform-database/json-columns.md
- specialty-teams/platform-database/schema-evolution.md
- specialty-teams/platform-database/indexing.md
- specialty-teams/platform-database/query-optimization.md
- specialty-teams/platform-database/transactions-and-concurrency.md
- specialty-teams/platform-database/access-pattern-analysis.md
- specialty-teams/platform-database/backup-and-recovery.md
- specialty-teams/platform-database/testing.md
- specialty-teams/platform-database/sync-schema-design.md
- specialty-teams/platform-database/conflict-resolution.md
- specialty-teams/platform-database/sync-protocol.md
- specialty-teams/platform-database/clock-systems.md
- specialty-teams/platform-database/offline-first-architecture.md
- specialty-teams/platform-database/sync-engine-design.md
- specialty-teams/platform-database/sync-tooling.md

## Consulting Teams

- consulting-teams/platform-database/cross-database-compatibility.md
- consulting-teams/platform-database/sync-impact.md
- consulting-teams/platform-database/access-pattern-coherence.md

## Exploratory Prompts

1. If your data model had to support a feature you haven't thought of yet, where would the pain be? What's inflexible?

2. What if you needed to change your primary database technology? What's tightly coupled?

3. If you had to guarantee zero data loss across regions during a network partition, what would you trade off?

4. What's the relationship between your data model and your domain model? Are they the same thing?

5. Walk me through what happens when two devices edit the same record offline. Where does each device's change end up?

6. What's the longest a device could be offline and still sync cleanly? What breaks first?
