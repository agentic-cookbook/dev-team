---
name: Key architecture docs for dev-team
description: Where the current architectural thinking and history live in this repo.
type: reference
originSessionId: 1529e1c6-c334-497e-83d0-d341413f38f4
---
**Current target architecture (conductor pivot):**
- Design spec: `docs/superpowers/specs/2026-04-11-conductor-design.md` — prescriptive; read this before making conductor-related changes.
- Research doc: `docs/planning/2026-04-11-conductor-architecture.md` — brainstorming history, alternatives considered, decision rationale.

**Predecessor (terminology still valid, outer loop superseded):**
- `docs/planning/2026-04-03-system-architecture-v2.md` — first DB-centric rearchitecture. Terminology and disposition tables still stand; the "team-lead runs in CC conversation" assumption is gone.

**Current state:**
- `docs/architecture.md` — describes the system *as it is today*, pre-conductor. Do NOT update this to describe the conductor model until the first production team is ported and stable.

**Cross-repo mirror:**
- `docs/research-paper/` contains flat-file copies of many planning/research docs across projects for cross-referencing. The conductor spec is mirrored as `agenticdevteam_sp_spec_2026-04-11-conductor-design.md`.
