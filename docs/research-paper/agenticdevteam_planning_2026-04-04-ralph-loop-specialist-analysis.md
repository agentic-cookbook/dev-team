# Ralph-Loop in Specialist Execution: Pros and Cons Analysis

## Context

The dev-team plugin uses a **worker-verifier loop** to execute specialty-teams: for each team, spawn an independent worker agent, spawn an independent verifier agent, retry up to 3 times on failure. The **ralph-loop** plugin is a stop-hook-based iteration system that repeats the same prompt until a completion promise is met or max iterations are reached. This analysis evaluates whether ralph-loop could replace or augment the specialist execution loop.

## Four Integration Models Evaluated

### Model 1: Ralph-loop wraps the entire specialist run

One ralph-loop per specialist (e.g., security with 15 teams).

| Pros | Cons |
|------|------|
| Session crash recovery via file state | Destroys parallelism (ralph-loop is single-threaded, one state file) |
| Cross-team self-correction (can revisit earlier teams) | Extreme token cost (30-50 iterations re-reading full context) |
| Simple dispatch (one loop per specialist) | Loses worker-verifier independence (same agent plays both roles) |
| | Claude must reconstruct progress from files each iteration — drift risk |
| | Completion promise requires self-assessing 15 teams — fragile |

**Verdict: Poor fit.** Scope too large, parallelism lost, token cost extreme.

### Model 2: Ralph-loop wraps each worker-verifier pair

One ralph-loop per specialty-team. Claude acts as both worker and verifier.

| Pros | Cons |
|------|------|
| Eliminates subagent dispatch overhead | **Breaks the independence principle** — same agent writes and verifies |
| File-based crash recovery per team | Self-verification is weaker than independent verification (confirmation bias) |
| Simpler orchestrator logic | Combined prompt doubles in size or loses specificity |
| Flexible iteration count (not hard-coded to 3) | Parallelism constrained (one state file per session) |
| | If stuck, max-iterations fires but produces no useful output |

**Verdict: Architecturally dubious.** The independence principle is the core quality mechanism — replacing it with self-verification trades correctness for simplicity.

### Model 3: Ralph-loop replaces just the retry loop

Worker and verifier remain separate subagents. Ralph-loop manages the retry/re-dispatch.

| Pros | Cons |
|------|------|
| Preserves worker-verifier independence | Architecturally redundant — the orchestrator already does this in 5 lines |
| Adds persistence for retry state | **Impedance mismatch** — stop hook fires at session-exit, not between subagent calls |
| Removes hard-coded 3-retry limit | Prompt describes orchestration procedure, not direct work (fighting ralph-loop's design) |
| | Token overhead from re-reading orchestration prompt each iteration |
| | State reconciliation fragile (prompt says "run worker" but files show it already ran twice) |

**Verdict: Impedance mismatch.** Ralph-loop operates at session-exit granularity; the retry loop operates at subagent-dispatch granularity. Different levels of abstraction.

### Model 4: Ralph-loop as an outer quality loop

Run the current flow unchanged. Ralph-loop checks the aggregated output afterward.

| Pros | Cons |
|------|------|
| Cross-specialist conflict detection (security vs accessibility suggestions) | Cannot re-run a specific specialist — can only flag problems |
| Does not interfere with existing architecture | Adds latency on top of already-long pipeline |
| Low token cost (reads summary files, not full pipeline) | Diminishing returns — 180+ inner quality checks already ran |
| Ralph-loop's strengths align (well-defined task, clear criterion) | May become a rubber stamp (fires VERIFIED on iteration 1) |
| Compatible with parallel specialist execution | |

**Verdict: Best fit of the four**, but marginal practical value given extensive inner quality controls.

## Cross-Cutting Concerns

### Token Cost
| Model | Relative to current |
|-------|-------------------|
| Current (subagent dispatch) | Baseline — each agent gets only the context it needs |
| Model 1 (whole specialist) | 10-20x — re-reads all prior results every iteration |
| Model 2 (per team) | 1.5-2x — combined prompt, no context scoping |
| Model 3 (retry wrapper) | 1.2-1.5x — orchestration prompt overhead |
| Model 4 (outer quality) | Negligible — reads small summary files |

### Parallelism
Current system runs 2-3 specialists concurrently via Agent tool. Ralph-loop uses a single state file per session — **no concurrent loops possible**. Models 1-3 break parallelism. Model 4 runs after parallelism completes, so it's compatible.

### Independence Principle
Worker and verifier are separate agents that cannot influence each other — an **architectural guarantee**. In any ralph-loop model where one Claude instance plays both roles, this degrades to a prompt instruction ("now pretend you didn't just do the worker's thinking"). Prompt-based role separation is fundamentally weaker.

### Observability
Current system: orchestrator sees every verdict, failure reason, and retry count in conversation context. Integrates with DB layer (`db-finding.sh`, `db-message.sh`). Ralph-loop: limited to iteration count in state file + whatever Claude writes to disk. No structured reporting, no DB integration.

### Recoverability
Ralph-loop's one clear advantage: crash recovery via persistent state file. Current system mitigates this through aggressive persistence (reviews written to disk after each specialist completes), so crash loses at most one specialist's in-progress work.

## Recommendation

**Do not replace the worker-verifier loop with a ralph-loop.** They solve different problems:

- **Ralph-loop**: single-agent iterative refinement with file-based persistence. Paradigm: "do work, check files, iterate."
- **Worker-verifier loop**: multi-agent quality control with architectural independence. Paradigm: "dispatch, verify, retry with feedback."

These are complementary, not competitive. The worker-verifier loop is an orchestration pattern; ralph-loop is an iteration pattern.

### Higher-value alternatives to consider
1. **Add crash recovery** to the orchestrator (persist retry state to disk, not just conversation context)
2. **Add cross-specialist conflict detection** as a post-processing subagent (achieves Model 4's goal without ralph-loop)
3. **Make retry limit configurable** per specialty-team (some teams need more iterations)

### Where ralph-loop could fit in dev-team
Best suited for a different layer — wrapping a top-level `/dev-team generate` invocation for unattended iterative improvement of an entire project. But user approval gates in the generate workflow make unattended loops impractical today.

---

## Narrowing the Gap: Crash Recovery

Ralph-loop's one genuine advantage over the current system is **crash recovery** — the ability to resume work after a session dies. This section analyzes the current vulnerability and what it would take to close the gap without adopting ralph-loop.

### What ralph-loop provides

Ralph-loop persists state in `.claude/ralph-loop.local.md` (iteration count, prompt, completion promise). When a session crashes and restarts, the stop hook reads this file and feeds the same prompt back. Claude then reads file state and git history to understand where it left off.

This is a **coarse-grained** recovery: it re-runs the entire prompt from scratch, relying on Claude to infer what's already done from files. It doesn't know which team was in progress, what the verifier said, or what retry iteration it was on — it just knows "keep going."

### What the current system has

The DB already has infrastructure that partially supports recovery:

| Table | What it tracks | Granularity |
|-------|---------------|-------------|
| `sessions` | Workflow run (project, workflow type, start/end) | Per `/dev-team generate` invocation |
| `session_state` | Agent dispatch (agent_type, specialist_domain, status, output_path) | Per specialist agent |
| `findings` | Individual findings (type, severity, status) | Per finding |
| `artifacts` | Output files (category, path, content) | Per file written |
| `messages` | Agent activity log | Per message |

The `session_state` table tracks `status = running | completed | failed` per specialist. So after a crash, you can query: "which specialists were running when we died?"

**The gap**: There's no tracking at the **specialty-team** level within a specialist. The DB knows "security specialist was running" but not "security specialist was on team 7 of 15, retry iteration 2, verifier returned FAIL with these reasons."

### The aggressive persistence mitigation

The `generate.md` workflow writes reviews to disk immediately after each specialist completes (line 248-251). So crash recovery at the specialist level already works informally:

1. Run `/dev-team generate`
2. Specialists A, B complete — reviews written to disk
3. Crash during specialist C
4. Re-run `/dev-team generate`
5. Orchestrator could check which reviews already exist and skip those specialists

But this is **not implemented** — the orchestrator doesn't check for existing reviews. It re-runs everything.

### What would close the gap

Three levels of crash recovery, from simplest to most complete:

#### Level 1: Specialist-level resume (low effort)

At the start of the specialist loop in `generate.md`, check if a review file already exists at `<project>/context/reviews/<scope-slug>-<specialist-domain>.md`. If it does and looks complete (has the expected sections), skip that specialist.

**What this covers**: Crash after specialist A completes but before specialist B starts. No work is re-done for A.

**What it misses**: Crash mid-specialist (during the team loop). The entire specialist re-runs.

**Implementation**: ~5 lines in `generate.md` workflow instructions. No DB changes. No new scripts.

#### Level 2: Team-level checkpointing (moderate effort)

Add a `team_progress` table to the DB:

```sql
CREATE TABLE team_progress (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_state_id INTEGER REFERENCES session_state(id),
  team_name TEXT NOT NULL,
  specialist_domain TEXT NOT NULL,
  status TEXT DEFAULT 'pending',  -- pending | running | passed | failed | escalated
  iteration INTEGER DEFAULT 0,
  verifier_feedback TEXT,
  worker_output_path TEXT,
  started TIMESTAMP,
  completed TIMESTAMP
);
```

The orchestrator records each team's status as it progresses through the loop. On resume, it queries `team_progress` for the current session and skips teams that already passed.

**What this covers**: Crash mid-specialist. Only the in-progress team re-runs from scratch; completed teams are skipped.

**What it misses**: Crash mid-retry (during iteration 2 of 3). The team restarts from iteration 1.

**Implementation**: New table + `db-team-progress.sh` script. Workflow changes to record progress and check on resume. ~50-100 lines total.

#### Level 3: Retry-level checkpointing (higher effort)

Extend `team_progress` to track the current retry iteration and persist the verifier's feedback between retries:

```sql
-- Same table as Level 2, but the orchestrator also:
-- 1. Updates 'iteration' after each retry
-- 2. Stores verifier_feedback so the worker can receive it on resume
-- 3. Stores worker_output_path so the verifier can re-verify on resume
```

On resume, the orchestrator can pick up mid-retry: "team 7 was on iteration 2, verifier said X. Re-run worker with that feedback."

**What this covers**: Full recovery to the exact point of failure. No work is re-done.

**What it misses**: Nothing — this is equivalent to ralph-loop's recovery, but with structured state instead of "re-read files and infer."

**Implementation**: Same DB schema as Level 2, but more workflow logic to read/write retry state. ~100-150 lines total.

### Comparison: ralph-loop recovery vs DB-based recovery

| Aspect | Ralph-loop | DB-based (Level 2-3) |
|--------|-----------|---------------------|
| **Recovery granularity** | Coarse (restart entire prompt) | Fine (resume at exact team/iteration) |
| **State format** | Unstructured (Claude infers from files) | Structured (SQL query returns exact state) |
| **Token cost on resume** | High (re-reads everything, re-infers progress) | Low (queries DB, skips completed work) |
| **Reliability** | Depends on Claude correctly inferring state | Deterministic (DB state is authoritative) |
| **Implementation effort** | Zero (ralph-loop already exists) | Moderate (new table, scripts, workflow changes) |
| **Parallelism** | Breaks it (single state file) | Preserves it (each specialist has its own DB rows) |
| **Observability** | Iteration count only | Full: which teams passed, which failed, what feedback, what iteration |

### Recommendation

**Level 2 (team-level checkpointing) is the sweet spot.** It closes the main crash recovery gap — resuming mid-specialist instead of restarting from scratch — without the complexity of tracking individual retry iterations. It uses the existing DB infrastructure, preserves parallelism, and provides structured observability that ralph-loop cannot match.

Level 1 is worth implementing immediately as a quick win (check for existing review files before re-running a specialist). Level 3 is only worth the effort if specialists routinely crash mid-retry, which in practice is rare.

Neither requires ralph-loop. The DB-based approach is more reliable (deterministic state vs. inference), more observable (structured queries vs. file scanning), and architecturally compatible (preserves parallelism and independence).
