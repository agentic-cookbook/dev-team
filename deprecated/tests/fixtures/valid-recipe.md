---
id: 00000000-0000-0000-0000-000000000003
title: "Test Recipe"
domain: agentic-cookbook://recipes/infrastructure/test-recipe
type: recipe
version: 1.0.0
status: accepted
language: en
created: 2026-04-04
modified: 2026-04-04
author: Mike Fullerton
copyright: 2026 Mike Fullerton
license: MIT
summary: "A test recipe used by the skill test harness to verify lint and approve behavior."
platforms: []
tags:
  - test
depends-on: []
related: []
references: []
approved-by: ""
approved-date: ""
---

# Test Recipe

## Overview

A minimal infrastructure recipe for testing the lint and approve skills.

## Behavioral Requirements

- **data-persistence**: The service MUST persist data to disk on every write operation.
- **graceful-shutdown**: The service MUST complete all pending writes before shutting down.

## Appearance

Not applicable — infrastructure recipe with no visual UI.

## States

Not applicable — infrastructure recipe.

## Accessibility

Not applicable — infrastructure recipe with no user-facing interface.

## Conformance Test Vectors

| ID | Requirements | Input | Expected |
|----|-------------|-------|----------|
| tr-001 | data-persistence | Write 1 record | Record exists on disk |
| tr-002 | graceful-shutdown | Send shutdown signal during write | Write completes before exit |

## Edge Cases

- Empty write: zero-byte payload MUST be accepted without error
- Concurrent writes: two simultaneous writes MUST NOT corrupt data

## Logging

Subsystem: `{{bundle_id}}` | Category: `TestRecipe`

| Event | Level | Message |
|-------|-------|---------|
| Write completed | debug | `TestRecipe: wrote {{bytes}} bytes` |

## Platform Notes

- **Swift**: Use `FileManager` for atomic writes.
- **TypeScript**: Use `fs.writeFileSync` with a temp file and rename.

## Design Decisions

**Decision**: Use atomic file writes. **Rationale**: Prevents partial writes on crash. **Approved**: yes

## Compliance

| Check | Status | Category |
|-------|--------|----------|
| [explicit-error-handling](agentic-cookbook://compliance/best-practices#explicit-error-handling) | passed | Best Practices |

## Change History

| Version | Date | Author | Summary |
|---------|------|--------|---------|
| 1.0.0 | 2026-04-04 | Mike Fullerton | Initial creation |
