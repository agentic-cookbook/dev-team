---
name: Conductor architecture pivot
description: Dev-team is pivoting from a Claude-Code-hosted team-lead to a headless conductor process. Design spec landed 2026-04-11.
type: project
originSessionId: 1529e1c6-c334-497e-83d0-d341413f38f4
---
The dev-team system is pivoting architectures: from "team-lead runs inside a Claude Code conversation" to a **headless conductor** — a long-running Python process per session that dispatches LLM work through a pluggable dispatcher, with everything coordinated through a single arbitrator over a shared DB.

**Why:** The old model burned context on long runs, couldn't parallelize specialists, had no natural home for multi-team coordination, and forced a tradeoff between observability and cost.

**Key design decisions (all captured in the spec):**
- Dispatch via `claude -p` subprocess, not the Agent SDK (billing — see user_billing_constraint).
- Dispatcher is an abstraction seam (`ClaudeCodeDispatcher` now, future `LocalDispatcher`).
- Per-agent logical model names (`high-reasoning`, `fast-cheap`, etc.) mapped to concrete models by the dispatcher.
- Single arbitrator + shared DB; inter-team comms is a query, not a message bus.
- Explicit `request` resource with typed kinds, schemas, timeouts, and an arbitrator-internal serial queue for deadlock prevention.
- Session = data scope (rows keyed by `session_id`); state = ephemeral tree-shaped cursor persisted on every push/pop for crash recovery.
- Team-playbooks authored in Python, "declarations not programs" convention.
- Host phase 1: terminal. Phase 2: `agentic-daemon` runs per-session jobs.

**Build order:** name-a-puppy walking skeleton → full name-a-puppy → cross-team flow → project-management team split → dev-team port.

**Why:** Captured so future sessions pick up the thread without re-deriving — and so they don't accidentally recommend the old architecture.

**How to apply:** When work on dev-team/specialist/specialty/team-lead code comes up, assume the conductor model is the target unless we're explicitly in maintenance mode on the current implementation. Read `docs/superpowers/specs/2026-04-11-conductor-design.md` for the prescriptive details before suggesting architecture changes.
