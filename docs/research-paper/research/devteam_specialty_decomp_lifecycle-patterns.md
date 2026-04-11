---
name: lifecycle-patterns
description: Traces constructor/destructor pairs, resource ownership, session management, state machines, and co-created/co-destroyed object groups.
artifact: guidelines/codebase-decomposition/lifecycle-patterns.md
version: 1.0.0
---

## Worker Focus
Find constructor/destructor pairs, setup/teardown methods, resource ownership (retain/release, connection pools), session management, state machines, and disposable/closeable patterns. Objects created and destroyed together form natural boundaries.

## Verify
Resource ownership chains traced; co-created/co-destroyed object groups identified; state machine boundaries mapped.
