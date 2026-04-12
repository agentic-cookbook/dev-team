---
name: completeness
description: Verifies all sections have meaningful content or NEEDS REVIEW markers; edge cases and test vectors present.
artifact: guidelines/recipe-quality/completeness.md
version: 1.0.0
---

## Worker Focus
Every section has meaningful content or explicit NEEDS REVIEW with explanation. Edge Cases covers null/empty, boundaries, concurrency, errors, and offline. Conformance Test Vectors has at least one test per MUST requirement.

## Verify
No empty sections without NEEDS REVIEW marker; NEEDS REVIEW markers include explanation; edge cases cover required categories; test vector count >= MUST requirement count.
