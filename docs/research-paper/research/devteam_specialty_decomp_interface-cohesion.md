---
name: interface-cohesion
description: Groups files by shared public API surfaces, exported types, shared protocols/interfaces, and barrel files.
artifact: guidelines/codebase-decomposition/interface-cohesion.md
version: 1.0.0
---

## Worker Focus
Examine public API surfaces, exported types, shared protocols/interfaces, and barrel files. Files sharing a common public interface belong together as a scope group. Trace shared types to their consumers.

## Verify
Public interfaces identified and grouped; shared types traced to their consumers; no scope group splits a cohesive public API.
