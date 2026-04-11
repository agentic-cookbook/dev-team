---
name: cross-cutting-detection
description: Identifies logging, error handling, analytics, auth checks, caching, and retry logic that span groups; distinguishes cross-cutting from shared infrastructure.
artifact: guidelines/codebase-decomposition/cross-cutting-detection.md
version: 1.0.0
---

## Worker Focus
Find logging calls, error handling patterns, analytics instrumentation, auth checks, caching layers, and retry logic that span multiple groups. Distinguish cross-cutting concerns (should NOT be their own scope group) from shared infrastructure (SHOULD be its own scope group). Test: does removing the concern break dependent groups?

## Verify
Cross-cutting concerns identified and classified; shared infrastructure distinguished from cross-cutting; no cross-cutting concern incorrectly proposed as its own scope group.
