---
name: purpose-classification
description: Classifies every code unit by primary purpose — UI, data transformation, orchestration, persistence, communication, config, testing, security, analytics.
artifact: guidelines/codebase-decomposition/purpose-classification.md
version: 1.0.0
---

## Worker Focus
Classify each code unit by primary purpose: UI presentation, data transformation, orchestration, persistence, communication, configuration, testing infrastructure, build tooling, security/auth, or analytics/observability. Each scope group should have one clear primary purpose.

## Verify
Every code unit assigned a primary purpose; mixed-purpose files flagged; scope groups have coherent single-purpose classification.
