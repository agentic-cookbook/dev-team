---
name: module-boundaries
description: Identifies independently buildable units via build manifests, directory structure, and explicit module/package declarations.
artifact: guidelines/codebase-decomposition/module-boundaries.md
version: 1.0.0
---

## Worker Focus
Examine build manifests, directory structure, and explicit module/package declarations to find each independently buildable unit. Map directory-level boundaries to declared modules and build targets. Identify where one module ends and another begins.

## Verify
Every build target has been identified; directory boundaries map to declared modules; no module spans unrelated directories.
