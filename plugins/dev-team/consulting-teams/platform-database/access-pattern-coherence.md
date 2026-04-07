---
name: access-pattern-coherence
description: Ensures structural decisions serve actual query patterns — catches schemas that look correct but perform poorly under real-world access
type: consulting
source:
  - docs/research/database/performance-and-tuning.md
  - docs/research/database/decision-frameworks.md
version: 1.0.0
---

## Consulting Focus

Ensures structural decisions serve actual query patterns. Catches schemas that look correct in isolation but perform poorly under real-world access patterns. Reviews join table indexes against hot-path queries, JSON column extraction patterns, denormalization choices against read/write ratios, and relationship structures against actual traversal patterns.

## Verify

VERIFIED findings must identify a specific query pattern and explain how the structural decision affects it (e.g., "join table missing index on the column used in the hot-path filter query"). NOT-APPLICABLE must demonstrate the output was reviewed and explain why no access pattern concerns exist (e.g., "clock system selection is a sync protocol decision, not a query pattern decision").
