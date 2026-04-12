---
name: backup-and-recovery
description: Evaluates backup strategies, Litestream integration, integrity checks, recovery procedures, and tombstone purging.
artifact: guidelines/database-design/backup-and-recovery.md
version: 1.0.0
---

## Worker Focus
Evaluates backup strategy including SQLite backup API for online backups or Litestream for WAL streaming replication. Verifies corruption detection (PRAGMA integrity_check) is scheduled. Reviews VACUUM strategy (incremental vs full with threshold). Ensures database size monitoring is in place. Documents tombstone retention windows and purging procedures for soft-deleted records.

## Verify
- Backup strategy chosen and documented: SQLite backup API or Litestream for continuous replication
- PRAGMA integrity_check scheduled and run periodically; failures trigger alerts
- VACUUM strategy selected (incremental PRAGMA incremental_vacuum for ongoing cleanup, or full VACUUM with size threshold)
- Database size monitoring in place with alerts for growth anomalies
- Tombstone retention window defined (e.g., keep soft-deleted records for 30 days before purging)
- Recovery procedure documented and tested; recovery RTO/RPO defined
