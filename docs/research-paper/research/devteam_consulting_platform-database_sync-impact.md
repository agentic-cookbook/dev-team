---
name: sync-impact
description: Ensures non-sync teams account for synchronization implications — catches decisions that would break sync or create merge conflicts
type: consulting
source:
  - docs/research/database/sync-strategies.md
  - docs/research/database/decision-frameworks.md
version: 1.0.0
---

## Consulting Focus

Ensures non-sync specialty teams account for synchronization implications. Catches schema or performance decisions that would break sync, create unresolvable merge conflicts, or make offline operation difficult. Reviews denormalization choices, column drops, constraint changes, and index modifications for their sync-layer consequences.

## Verify

VERIFIED findings must cite the specific sync implication (e.g., "denormalized column requires sync-time propagation") with a concrete recommendation. NOT-APPLICABLE must demonstrate the output was reviewed and explain why no sync impact exists (e.g., "naming conventions have no effect on sync behavior").
